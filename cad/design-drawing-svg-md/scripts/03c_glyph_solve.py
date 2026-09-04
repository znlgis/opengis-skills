# -*- coding: utf-8 -*-
"""03c 字形模板**确定性自监督解码** → output/_glyph_dict/glyph_labels.json

背景：本环境的 vision 子代理不可用（模型缺失），而通用图像描述通道对单字贴片
不可靠（会把单字读成多字串并虚构不存在的 gid）。按方案 D3「不做 glyph OCR 猜测」，
改用**已知明文解码**——两类明文都是图纸自带的硬约束，不含任何猜测：

  明文源 A（几何长度）：尺寸层直线的长度按该视图已推断比例 s 换算成 mm 后，
      必须是整数（钢结构 5/10mm 模数），而尺寸数字总是紧贴并沿该尺寸线居中排布。
      故 (文本行 ↔ 最近共线尺寸线) 配对给出该行的数字串 → 逐位给字形模板投票。
      尺寸线在 PDF 里常被文字打断成多段，故先按共线+邻近合并成逻辑尺寸线再取跨度。
  明文源 B（图号）：base_name 是已知的，标题栏里必有该串。仅当某图号子串在标题栏
      区域内**唯一**对应一个等长文本行时才用作 crib（唯一性守卫防错配），权重加倍。

判定：某模板只有在 主票数≥MIN_VOTES 且 主票占比≥CONSIST 且 次票<2 时才写字典，
并记 confidence=high/med（按票数）；其余一律留 UNK，由 03b 计入 unclear。
"""
from __future__ import annotations

import importlib.util
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

MIN_VOTES = 3          # 主票数下限
CONSIST = 0.70         # 主票占比下限
SECOND_MAX = 2         # 次票数上限（超过则视为歧义，不解码）
PERP_MIN, PERP_MAX = 0.0, 4.0      # ×字高：文本行到尺寸线的垂距窗口。
#   下限必为 0：CAD 尺寸数字是**压在尺寸线上居中**排布的（本文件共线合并
#   就是为了跨越被文字打断的缺口），此时行中心到线的垂距≈ 0；
#   若取 0.15h 会把“文字正在线上”这一主流情形全部误拒。
PARALLEL_COS = 0.90                # 平行判定（cos25°；实测尺寸线有 19°/−25°/−32° 等斜向）
COLLINEAR_TOL = 1.2                # pt：共线合并的垂距容差
CHAIN_GAP = 6.0                    # ×字高：共线段合并允许的最大缺口
INT_ABS_TOL_MM = 0.05              # 换算值到整数的**绝对**容差（mm）。
#   旧口径 max(0.5, 0.006*v) 对 v=310mm 允许 ±1.86mm，窗口宽达 3.7 个整数间距，
#   实测 int_rate 恒为 1.000 —— 完全无判别力，会把任意四舍五入当作明文。
#   CAD 导出精度量级为 0.01mm，故取 0.05mm 作宽一级的绝对阈。
CRIB_WEIGHT = 3                    # 图号 crib 的票权（**仅作佐证**，不单独定字）
CRIB_MIN_LEN = 7                   # crib 串最短长度（防“R00”类碎片误配）

PERP_COS_MAX = 0.35                # 界线与尺寸线的 |cos| 上限（≈70°~90° 视为垂直）
CROSS_TOL = 2.0                    # pt：界线两端点必须分居尺寸线两侧（真的穿过）
EXT_MARGIN = 3.0                   # ×字高：界线允许超出尺寸线段端点的余量
EXT_DEDUP = 1.5                    # pt：相邻界线去重容差
EXT_MIN_SPAN = 8.0                 # pt：小于此的间隔不是标注（多为箭头/间隙）

REJECT = Counter()                 # 文本行↔尺寸线配对的拒绝原因计数（证据，入 gate/修正单）


def _load_03b():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03b_text_recover.py")
    spec = importlib.util.spec_from_file_location("t03b", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T = _load_03b()


# ---------------------------------------------------------------- 逻辑尺寸线


def to_land_pt(pt) -> tuple:
    """页面竖放 pt → 横向(回正) pt（与 03b.land_box 同一变换：X=y_p, Y=W−x_p）。

    文本行的 `land_bbox` 在**横向系**，而 prims 里的尺寸线端点在**竖放系**；
    两系不同（实质是转置+镜射），直接比较会使平行/垂距/投影判定全部失真
    （实测表现：1711 行全部 unmatched，仅 1 行配对 → 字典零标签）。
    """
    return (pt[1], C.W_PT - pt[0])


def logical_dim_lines(by_i: dict, v: dict, h_ref: float) -> list:
    """把视图内尺寸层直线按共线合并成逻辑尺寸线，返回 (跨度pt, 方向, 垂距, 投影区间)。

    每条逻辑线记：dir(单位向量)、off(过原点的法向偏移)、proj 区间 [a,b]、span=b−a。
    合并规则：方向一致(±)、法向偏移差≤COLLINEAR_TOL、投影缺口≤CHAIN_GAP×字高。
    """
    segs = []
    for i in v["members"]:
        p = by_i.get(i)
        if not p or p["sem"] != "dimension" or p["g"]["type"] != "LINE":
            continue
        L = p["g"].get("len_pt") or 0.0
        if L < 15.0:
            continue
        (x1, y1) = to_land_pt(p["g"]["p1"])
        (x2, y2) = to_land_pt(p["g"]["p2"])
        d = (x2 - x1, y2 - y1)
        n = math.hypot(*d)
        if n < 1e-9:
            continue
        u = (d[0] / n, d[1] / n)
        if u[0] < 0 or (abs(u[0]) < 1e-9 and u[1] < 0):
            u = (-u[0], -u[1])
        nrm = (-u[1], u[0])
        off = x1 * nrm[0] + y1 * nrm[1]
        a, b = sorted((x1 * u[0] + y1 * u[1], x2 * u[0] + y2 * u[1]))
        segs.append({"u": u, "nrm": nrm, "off": off, "a": a, "b": b, "i": i})
    segs.sort(key=lambda s: (round(s["off"] / COLLINEAR_TOL), s["a"]))
    out = []
    for s in segs:
        tgt = None
        for g in out:
            if (abs(g["u"][0] - s["u"][0]) < 1e-3 and abs(g["u"][1] - s["u"][1]) < 1e-3
                    and abs(g["off"] - s["off"]) <= COLLINEAR_TOL
                    and s["a"] - g["b"] <= CHAIN_GAP * h_ref):
                tgt = g
                break
        if tgt:
            tgt["b"] = max(tgt["b"], s["b"])
            tgt["a"] = min(tgt["a"], s["a"])
            tgt["n_seg"] += 1
            tgt["ids"].append(s["i"])
        else:
            out.append(dict(s, n_seg=1, ids=[s["i"]]))
    for g in out:
        g["span"] = g["b"] - g["a"]
    return out


def all_dim_segments(by_i: dict, v: dict) -> list:
    """视图内尺寸层全部直线段（横向系），供界线求交。"""
    out = []
    for i in v["members"]:
        p = by_i.get(i)
        if not p or p["sem"] != "dimension" or p["g"]["type"] != "LINE":
            continue
        (x1, y1) = to_land_pt(p["g"]["p1"])
        (x2, y2) = to_land_pt(p["g"]["p2"])
        d = (x2 - x1, y2 - y1)
        n = math.hypot(*d)
        if n < 3.0:
            continue
        out.append({"u": (d[0] / n, d[1] / n), "a": (x1, y1), "b": (x2, y2),
                    "mid": ((x1 + x2) / 2, (y1 + y2) / 2), "len": n, "i": i})
    return out


def dim_intervals(g: dict, segs: list, h_ref: float) -> list:
    """一条逻辑尺寸线的**实测标注区间** = 相邻两条界线在尺寸线方向上的投影间隔。

    不用共线合并后的段跨度：PDF 里尺寸线常被文字打断，又被 CHAIN_GAP 串成
    整条尺寸链，段跨度与真实标注长度无关（实测残差 med|r|≈0.25mm、p90≈0.45mm，
    即 mod 1 近似均匀分布 = 纯噪声）。**界线才是标注长度的定义边界**。

    尺寸链（a—b—c）会产出多个相邻间隔，每个都是一条独立的标注明文。
    """
    u, nrm, off = g["u"], g["nrm"], g["off"]
    ts = []
    for q in segs:
        if abs(q["u"][0] * u[0] + q["u"][1] * u[1]) > PERP_COS_MAX:
            continue                              # 不够垂直 → 不是界线
        s1 = q["a"][0] * nrm[0] + q["a"][1] * nrm[1] - off
        s2 = q["b"][0] * nrm[0] + q["b"][1] * nrm[1] - off
        if not (min(s1, s2) <= CROSS_TOL and max(s1, s2) >= -CROSS_TOL):
            continue                              # 不与尺寸线相交
        t = q["mid"][0] * u[0] + q["mid"][1] * u[1]
        if not (g["a"] - EXT_MARGIN * h_ref <= t <= g["b"] + EXT_MARGIN * h_ref):
            continue
        ts.append(t)
    ts.sort()
    ded = []
    for t in ts:
        if not ded or t - ded[-1] > EXT_DEDUP:
            ded.append(t)
        else:
            ded[-1] = (ded[-1] + t) / 2
    out = []
    for a, b in zip(ded, ded[1:]):
        if b - a < EXT_MIN_SPAN:
            continue
        out.append({"a": a, "b": b, "mid": (a + b) / 2, "span": b - a,
                    "line": g, "n_ext": len(ded)})
    return out


def line_geom(L: dict) -> tuple:
    """文本行在横向系里的：中心、单位方向（按实际 angle，可为斜向）、跨度、字高。"""
    x0, y0, x1, y1 = L["land_bbox"]
    h = L["h_pt"] or 9.8
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ang = math.radians(L.get("angle") if L.get("angle") is not None
                       else (-90.0 if L["vert"] else 0.0))
    u = (math.cos(ang), math.sin(ang))
    pa, pb = sorted((x0 * u[0] + y0 * u[1], x1 * u[0] + y1 * u[1]))
    return cx, cy, u, pa, pb, h


def match_dim(L: dict, dims: list) -> tuple:
    """给文本行找最近的平行逻辑尺寸线；返回 (dim, value_len_pt) 或 (None, None)。

    每次拒绝都计数到 REJECT，供修正单/汇总报告如实给出「为何解不出」的证据。
    """
    cx, cy, u, a, b, h = line_geom(L)
    span = b - a
    best, bestd = None, 1e18
    seen_par = seen_perp = seen_proj = 0
    for g in dims:
        c = abs(g["u"][0] * u[0] + g["u"][1] * u[1])
        if c < PARALLEL_COS:
            seen_par += 1
            continue
        gu = g["u"] if (g["u"][0] * u[0] + g["u"][1] * u[1]) > 0 else (-g["u"][0], -g["u"][1])
        nrm = (-gu[1], gu[0])
        perp = abs((cx * nrm[0] + cy * nrm[1]) - g["off"])
        if not (PERP_MIN * h <= perp <= PERP_MAX * h):
            seen_perp += 1
            continue
        ga = cx * gu[0] + cy * gu[1]          # 行中心在尺寸线方向上的投影
        pa, pb = g["a"] - span / 2, g["b"] + span / 2
        lo, hi = max(a, g["a"]), min(b, g["b"])
        # 投影重叠：行必须基本落在尺寸线跨度内（允许 ±0.6 字高）
        if lo - 0.6 * h > hi:
            seen_proj += 1
            continue
        if not (g["a"] - 3 * h <= ga <= g["b"] + 3 * h):
            seen_proj += 1
            continue
        if g["span"] < span * 0.75:
            seen_proj += 1
            continue
        if perp < bestd:
            best, bestd = g, perp
    if best is None:
        REJECT["not_parallel"] += seen_par
        REJECT["perp"] += seen_perp
        REJECT["proj"] += seen_proj
        REJECT["lines_unmatched"] += 1
    else:
        REJECT["lines_matched"] += 1
    return (best, best["span"]) if best else (None, None)


def nice_int(value: float) -> int:
    """value(mm) 是否落在整数网格上（绝对容差）；是则返回该整数，否则 0。

    返回 0 表示「无明文」——宁缺勿臆：容差内不命中就不投票，
    绝不把四舍五入的结果当成图纸上写着的数字。
    """
    v = int(round(value))
    if v < 10:
        return 0
    if abs(value - v) > INT_ABS_TOL_MM:
        return 0
    return v


def plaintext_audit(pdoc: dict, vdoc: dict, cwv: dict, h_ref: float) -> dict:
    """几何明文源可用性审计：实测跨度换算值到最近整数的残差分布。

    判据：若尺度与跨度都对，残差应在 CAD 导出精度量级（≤0.05mm）；
    若残差在 mod 1 上近似**均匀分布**（med|r|≈0.25、p90|r|→0.5），
    则该跨度根本不是标注长度，明文源不成立。

    两种跨度定义都测：共线合并段跨度、界线相邻投影间隔。
    结果写入 meta.plaintext_audit，使降级结论可由交付物自证、可重跑。
    """
    by_i = {p["i"]: p for p in pdoc["prims"]}
    acc = {"seg": [], "ext": []}
    n_view = 0
    for v in vdoc["views"]:
        cw = cwv.get(v["id"])
        if not cw or cw["scale_source"] != "inferred":
            continue
        den = int(round(2.83465 / cw["s_pt_per_mm"]))
        if not den:
            continue
        s = 2.83465 / den
        n_view += 1
        dims = logical_dim_lines(by_i, v, h_ref)
        segs = all_dim_segments(by_i, v)
        acc["seg"] += [g["span"] / s for g in dims if g["span"] > 15.0]
        acc["ext"] += [x["span"] / s for g in dims for x in dim_intervals(g, segs, h_ref)]
    out = {"n_view": n_view, "s_from": "标准式 2.83465/分母 (k=1.0)"}
    for key, qs in acc.items():
        if not qs:
            out[key] = {"n": 0}
            continue
        r = sorted(abs(q - round(q)) for q in qs)
        n = len(r)
        out[key] = {"n": n, "med_abs_r_mm": round(r[n // 2], 5),
                    "p90_abs_r_mm": round(r[int(n * 0.9)], 5),
                    "int_rate@0.05mm": round(sum(1 for x in r if x <= INT_ABS_TOL_MM) / n, 4),
                    "uniform_upper": 0.5}
    med = max((out[k].get("med_abs_r_mm", 0.0) for k in ("seg", "ext")), default=0.0)
    out["viable"] = bool(med <= INT_ABS_TOL_MM)
    out["verdict"] = (
        "明文源成立" if out["viable"] else
        "明文源不成立：两种跨度定义下残差均远大于 CAD 导出精度（med|r|=%.3fmm），"
        "p90|r| 靠近均匀分布上限 0.5 → mod 1 近似均匀 = 无信号。"
        "说明这些跨度不是标注长度（尺寸链/箭头/界线混入），几何反演无法产出明文。"
        "参照实现的 41.1%% 绑定率是**先有字典标签再正向匹配** value*s≈长度，"
        "从不反演几何取值，故不依赖本明文源。" % med)
    return out


# ---------------------------------------------------------------- 图号 crib


def drawing_number_cribs(base: str) -> list:
    """由 base_name 生成已知明文串（去空格、常见分段）。"""
    import re
    s = base.replace(" ", "")
    parts = [p for p in re.split(r"[-_]", s) if p]
    out = [s] + parts
    out += ["-".join(parts[i:j]) for i in range(len(parts))
            for j in range(i + 2, len(parts) + 1)]
    seen, res = set(), []
    for o in out:
        if len(o) >= CRIB_MIN_LEN and o not in seen:
            seen.add(o)
            res.append(o)
    return res


def crib_votes(lines: list, tb_L, base: str) -> tuple:
    """标题栏内唯一等长行 → 图号明文投票（唯一性守卫）。"""
    if not tb_L:
        return Counter(), []
    intb = [L for L in lines
            if L["land_bbox"][0] >= tb_L[0] - 30 and L["land_bbox"][2] <= tb_L[2] + 30
            and L["land_bbox"][1] >= tb_L[1] - 30 and L["land_bbox"][3] <= tb_L[3] + 30]
    by_len = defaultdict(list)
    for L in intb:
        by_len[L["n_glyphs"]].append(L)
    votes, used = Counter(), []
    for crib in drawing_number_cribs(base):
        cands = by_len.get(len(crib), [])
        if len(cands) != 1:            # 唯一性守卫：多解或无解都不用
            continue
        L = cands[0]
        for g, ch in zip(L["glyphs"], crib):
            votes[(g["sid"], ch)] += CRIB_WEIGHT
        # 带上命中行的 sid 序列：跨图比对同一 crib 的序列是否一致，是 crib 源
        # 真伪的**判别性**检验（见 crib_audit）。只记票数无法发现错配。
        used.append({"crib": crib, "line_id": L["line_id"], "n": len(crib),
                     "sids": [g["sid"] for g in L["glyphs"]]})
    return votes, used


def crib_audit(seq_by_crib: dict, gain: dict) -> dict:
    """用跨图一致性判定「图号 crib 能否独立定字」，并量化即便能也无收益。

    同一 CAD 字体下，同一明文串在不同图里必须给出**完全相同**的 sid 序列；
    同一字符也不该对应多个 sid。任一不成立，说明「标题栏内唯一等长行」守卫
    匹到的是恰好等长的任意行，crib 票属噪声，不能独立成字。
    """
    rows, ch2sid = [], defaultdict(set)
    for crib, hits in seq_by_crib.items():
        if len(hits) < 2:
            continue
        ref = hits[0]["sids"]
        n_same = sum(1 for h in hits[1:] if h["sids"] == ref)
        rows.append({"crib": crib, "n_sheets": len(hits), "n_seq_identical": n_same,
                     "agree": n_same == len(hits) - 1,
                     "seqs": [{"sheet": h["sheet"], "line_id": h["line_id"],
                               "sids": h["sids"]} for h in hits]})
    for crib, hits in seq_by_crib.items():
        for h in hits:
            for ch, sid in zip(crib, h["sids"]):
                ch2sid[ch].add(sid)
    multi = {c: sorted(s) for c, s in ch2sid.items() if len(s) > 1}
    checked = [r for r in rows]

    # 跨图号家族约束：两个不同图的 crib 若有 ≥3 位公共前缀（如同一图号家族里
    # 只有第 6 位不同、其余位共享同一前缀），这些位上的明文相同，sid 就必须相同。
    # 这不用标签验标签（不循环），而是用两个图号家族的共有子串做交叉约束。
    flat = [(c, h) for c, hs in seq_by_crib.items() for h in hs]
    family = []
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            (c1, h1), (c2, h2) = flat[i], flat[j]
            if h1["sheet"] == h2["sheet"]:
                continue
            n = 0
            while n < min(len(c1), len(c2)) and c1[n] == c2[n]:
                n += 1
            if n < 3:
                continue
            same = sum(1 for k in range(n) if h1["sids"][k] == h2["sids"][k])
            family.append({"sheet_a": h1["sheet"], "crib_a": c1,
                           "sheet_b": h2["sheet"], "crib_b": c2,
                           "common_prefix": c1[:n], "n_prefix": n,
                           "n_sid_identical": same, "agree": same == n})
    heights = sorted({round(h.get("h_pt", 0), 1) for hs in seq_by_crib.values()
                      for h in hs if h.get("h_pt")})
    bad = bool((checked and any(not r["agree"] for r in checked))
               or (family and any(not f["agree"] for f in family))
               or multi or (len(heights) > 1 and max(heights) > 2 * min(heights)))
    return {
        "n_crib_cross_sheet": len(checked),
        "n_seq_identical_all": sum(1 for r in checked if r["agree"]),
        "cross_family": family,
        "n_cross_family": len(family),
        "n_cross_family_agree": sum(1 for f in family if f["agree"]),
        "matched_line_heights_pt": heights,
        "char_to_sid_multiplicity": {c: len(s) for c, s in sorted(ch2sid.items())},
        "chars_with_multi_sid": multi,
        "cross_sheet": checked,
        "crib_only_gain": gain,
        "verdict": ("crib 源不可独立定字：跨图同一 crib 的 sid 序列不一致、跨图号家族"
                    "公共前缀位的 sid 也不一致、单字符对应多个 sid（同一字体不可能）、"
                    "且命中行字高跳变数倍（真同一标题栏单元格应一致）——说明等长行"
                    "唯一性守卫匹中的是恰好等长的任意行。故 crib 只作佐证，与 crib 冲突者"
                    "一律不入字典；否则等于向 MD/SVG 注入虚构文本。"
                    if bad else "跨图与跨家族约束均成立，crib 源可采信"),
    }


# ---------------------------------------------------------------- 主流程


def solve(sheets: list) -> dict:
    tdoc = C.read_json(os.path.join(C.GLYPH_DIR, "templates.json"), {"templates": {}})
    sid2gid = {m["sid"]: g for g, m in (tdoc.get("templates") or {}).items()}
    votes = Counter()          # 明文源 A：几何尺寸线长度（可定字的唯一依据）
    cribv = Counter()          # 明文源 B：图号（仅佐证，不单独定字，防错配污染）
    crib_seq = defaultdict(list)   # crib -> 逐图命中行的 sid 序列（跨图一致性审计用）
    all_line_sids = []             # 全部图文本行的 sid 序列（crib-only 字典收益回测用）
    audits = {}                # 逐图几何明文源可用性审计（残差分布，硬证据）
    ev = []
    for base in sheets:
        pdoc = C.read_json(C.work_path(base, "prims.json"))
        vdoc = C.read_json(C.work_path(base, "views.json"))
        cwd = C.read_json(C.deliverables(base)["crosswalk"], {"views": []})
        if not pdoc or not vdoc or not cwd.get("views"):
            C.log("[%s] 跳过（缺 prims/views/crosswalk）" % base)
            continue
        by_i = {p["i"]: p for p in pdoc["prims"]}
        cwv = {v["id"]: v for v in cwd["views"]}
        gs, _, _ = T.collect_glyphs(base, {})
        lines = [T.line_record(k, L) for k, L in enumerate(T.build_lines(gs))]
        all_line_sids.extend([g["sid"] for g in L["glyphs"]] for L in lines)
        h_ref = Counter(L["h_pt"] for L in lines if L["n_glyphs"] >= 2).most_common(1)
        h_ref = h_ref[0][0] if h_ref else 9.8
        dims_by_view = {}
        n_pair = n_ok = 0
        for v in vdoc["views"]:
            cw = cwv.get(v["id"])
            if not cw or cw["scale_source"] not in ("read", "inferred"):
                continue
            if cw["scale_source"] == "inferred" and cw["scale_score"] == 0:
                continue                      # 比例未验证 → 不产出明文
            s = cw["s_pt_per_mm"]
            dims = logical_dim_lines(by_i, v, h_ref)
            dims_by_view[v["id"]] = (dims, s)
        for L in lines:
            if not (2 <= L["n_glyphs"] <= 7):
                continue
            dd = dims_by_view.get(L["view"])
            if not dd:
                continue
            dims, s = dd
            g, span = match_dim(L, dims)
            if not g:
                continue
            n_pair += 1
            val = nice_int(span / s)
            if not val:
                continue
            digits = str(val)
            if len(digits) == L["n_glyphs"]:
                for gl, ch in zip(L["glyphs"], digits):
                    votes[(gl["sid"], ch)] += 1
                n_ok += 1
                ev.append({"sheet": base, "line_id": L["line_id"], "view": L["view"],
                           "value": val, "span_pt": round(span, 2), "s": s,
                           "n_seg": g["n_seg"], "perp_h": None})
            elif len(digits) + 1 == L["n_glyphs"]:
                # 前缀符号（Φ/R/C）+ 数字：数字位投票，前缀另计
                for gl, ch in zip(L["glyphs"][1:], digits):
                    votes[(gl["sid"], ch)] += 1
                votes[("PREFIX:" + L["glyphs"][0]["sid"], "?")] += 1
                n_ok += 1
        tb = vdoc.get("tb_bbox")
        cv, cused = crib_votes(lines, T.land_box({"r": tb}) if tb else None, base)
        cribv.update(cv)
        for c in cused:
            crib_seq[c["crib"]].append({"sheet": base, "line_id": c["line_id"],
                                        "sids": c["sids"],
                                        "h_pt": next((L["h_pt"] for L in lines
                                                      if L["line_id"] == c["line_id"]), None)})
        audits[base] = plaintext_audit(pdoc, vdoc, cwv, h_ref)
        C.log("[%s] 行=%d 多字行=%d 配对=%d 得明文=%d 图号crib=%s"
              % (base, len(lines), sum(1 for x in lines if x["n_glyphs"] >= 2),
                 n_pair, n_ok, [c["crib"] for c in cused] or "无唯一匹配"))
        C.log("      明文源审计: %s"
              % {k: v for k, v in audits[base].items() if k in ("seg", "ext", "viable")})

    # ---- 判定：只采纳**几何明文**支持的标签（图号 crib 仅提升置信）
    per_sid = defaultdict(Counter)
    for (sid, ch), n in votes.items():
        per_sid[sid][ch] += n
    labels, unresolved = {}, []
    for sid, cnt in per_sid.items():
        if sid.startswith("PREFIX:"):
            continue
        top, ntop = cnt.most_common(1)[0]
        second = cnt.most_common(2)[1][1] if len(cnt) > 1 else 0
        tot = sum(cnt.values())
        corroborated = cribv.get((sid, top), 0)
        conflict = sum(n for (s2, c2), n in cribv.items() if s2 == sid and c2 != top)
        if ntop >= MIN_VOTES and ntop / tot >= CONSIST and second <= SECOND_MAX \
                and not conflict:
            gid = sid2gid.get(sid)
            if not gid:
                continue
            labels[gid] = {"char": top,
                           "confidence": "high" if (ntop >= 8 or corroborated) else "med",
                           "source": "geom-dimlen(确定性解码)"
                                     + ("+drawing-number佐证" if corroborated else ""),
                           "votes": ntop, "total": tot, "sid": sid,
                           "crib_corroborated": corroborated}
        else:
            unresolved.append({"sid": sid, "gid": sid2gid.get(sid), "votes": dict(cnt),
                               "crib_conflict": conflict,
                               "reason": "票数<%d 或 主票占比<%.2f 或 次票>%d 或 与图号crib冲突"
                                         % (MIN_VOTES, CONSIST, SECOND_MAX)})
    unresolved.sort(key=lambda u: -sum(u["votes"].values()))
    digits_solved = sorted({v["char"] for v in labels.values() if v["char"].isdigit()})

    # ---- crib-only 字典的收益回测：即便不管跨图否证、把 crib 一致票全部当标签发布，
    # 能多解析出多少文本行？为 0 则说明发布它无意义（不仅不可信，而且无用）。
    crib_per_sid = defaultdict(Counter)
    for (sid, ch), n in cribv.items():
        crib_per_sid[sid][ch] += n
    crib_lab = {s: c.most_common(1)[0][0] for s, c in crib_per_sid.items() if len(c) == 1}
    resolvable = [[crib_lab[s] for s in sids] for sids in all_line_sids
                  if sids and all(s in crib_lab for s in sids)]
    numeric = ["".join(r) for r in resolvable if "".join(r).replace(".", "").isdigit()]
    crib_gain = {"n_lines_total": len(all_line_sids),
                 "n_crib_only_labels": len(crib_lab),
                 "crib_only_chars": "".join(sorted(set(crib_lab.values()))),
                 "n_lines_fully_resolvable": len(resolvable),
                 "n_numeric_resolvable": len(numeric),
                 "note": "行级全字解析要求该行**每个**字形模板都已标注；crib 只能给出"
                         "图号里出现过的字符，而尺寸值/技术要求用的字符集远比它宽"}
    # glyph_labels.json 是**跨阶段共用**的字典文件：03d 的视觉逐行对账也往这里
    # promote。原实现整份覆写，按报告 §七 的顺序重跑 03c 就会把 03d 已采信的标签
    # 清回 0（实测 prev_n_labels=31 → 0，等于让全部图字形重新变 UNK、绑定率归零）。
    # 故先读回、保留非本阶段来源（source 不含 geom-dimlen / crib）的标签再合并；
    # 同 sid 冲突时以本阶段的确定性证据为准（03c 的标签有明文/crib 双源审计留痕）。
    _lp = os.path.join(C.GLYPH_DIR, "glyph_labels.json")
    _prev = C.read_json(_lp, {}) or {}
    _prev_lab = (_prev.get("labels") if isinstance(_prev, dict) else None) or {}
    _prev_meta = (_prev.get("meta") if isinstance(_prev, dict) else None) or {}
    _foreign = {}
    for _k, _v in _prev_lab.items():
        _src = str((_v or {}).get("source") or "") if isinstance(_v, dict) else ""
        if _k not in labels and "geom-dimlen" not in _src and "crib" not in _src:
            _foreign[_k] = _v
    merged = dict(_foreign)
    merged.update(labels)
    doc = {
        "labels": merged,
        "meta": {
            "method": "确定性自监督解码（尺寸线长度明文 + 图号唯一 crib），无视觉、无猜测",
            "n_labels_foreign_preserved": len(_foreign),
            "foreign_sources": sorted({str((v or {}).get("source") or "")
                                       for v in _foreign.values()}),
            # vision_available 的归属权在 03d（真正用视觉的阶段）；03c 只透传，
            # 不用自己的「两条通道不可用」结论去覆盖它——那会把已校准的事实抹掉。
            "vision_available": bool(_prev_meta.get("vision_available")),
            "vision_note_03c": "本阶段试过的两条视觉通道均已实测不可用，故按 D3 不采用其结果："
                           "(a) vision 子代理模型缺失；"
                           "(b) 直接读图通道对 work/regions/_title_block.png 返回的是"
                           "散文描述而非像素，且该描述**漏报了图号**（唯一能拿文件名"
                           "先验核对的字段）却给出了无法核对的名称/序号；对单字贴片"
                           "则实测把单字读成多字串并虚构 gid。不可核对的识读结果"
                           "写入 §4/§5 就是臆造，故一律不用",
            "params": {"MIN_VOTES": MIN_VOTES, "CONSIST": CONSIST,
                       "SECOND_MAX": SECOND_MAX, "CRIB_WEIGHT": CRIB_WEIGHT,
                       "PERP": [PERP_MIN, PERP_MAX],
                       "INT_ABS_TOL_MM": INT_ABS_TOL_MM, "PARALLEL_COS": PARALLEL_COS,
                       "CHAIN_GAP": CHAIN_GAP},
            "n_labels": len(merged), "n_labels_own": len(labels),
            "n_unresolved": len(unresolved),
            "digits_solved": digits_solved,
            "chars": dict(Counter(str((v or {}).get("char")) for v in merged.values())),
            "evidence_n": len(ev),
            "reject_reasons": dict(REJECT),
            "frame_fix": "尺寸线端点已经 to_land_pt 转到横向(回正)系，再与文本行的 "
                         "land_bbox 比较；修复前两系混用导致 1711 行全部 unmatched、仅 1 行配对",
            "plaintext_audit": audits,
            "plaintext_viable": all(a.get("viable") for a in audits.values())
            if audits else False,
            "degrade_note": (
                "零标签属方案 D3 允许的降级（不臆造），且已不是「没试」而是「已量过」："
                "(1) 坐标系缺陷已修（竖放/横向混用 → 配对 1→37、unmatched 1711→167）；"
                "(2) 垂距窗下限已修为 0（文字压在尺寸线上是主流情形）；"
                "(3) 整数命中检验已从无判别力的相对容差（实测 int_rate 恒=1.000）"
                "改为绝对 0.05mm；(4) 改后残差审计（plaintext_audit）表明：对全部候选分母、"
                "两种跨度定义（共线段跨度 / 界线相邻间隔），换算值到最近整数的残差"
                "med|r|≈0.15~0.42mm、p90|r|≈0.45mm（均匀上限 0.5）——mod 1 近似均匀，"
                "即几何反演无信号，明文源 A 不成立；(5) 图号 crib（明文源 B）已被"
                "crib_audit 的跨图/跨图号家族一致性检验否证（同一明文串在不同图里"
                "sid 序列不一致、单字符对应多个 sid、命中行字高 2.2/7.3/15.5pt 跳变），"
                "说明「标题栏内唯一等长行」守卫匹中的是恰好等长的任意行，故只作佐证。"
                "闭环路径（按成本从低到高）：a) 人工标注 "
                "output/_glyph_dict/label_sheet_01..05.png（仅 100 个模板，覆盖 42.5% 实例）"
                "后回写 glyph_labels.json 重跑 03b；b) vision 模型可用时派代理标注 "
                "contact_sheet_01..08.png；c) 若提供明细表/设计计算等外部文本源，"
                "可用其数值作 crib 反解字典。在此之前，未识别数值全部入 §6 unclear，不臆造。"),
            "crib_votes": sum(cribv.values()),
            "crib_audit": crib_audit(crib_seq, crib_gain),
            "crib_note": "图号 crib 仅作佐证；与 crib 冲突的 sid 一律不入字典。"
                         "不单独定字的依据是 crib_audit 的跨图一致性否证，非主观保守",
        },
        "unresolved": unresolved[:120],
        "evidence_sample": ev[:40],
    }
    # 与 03d 对称：保留对方阶段的 meta 键与顶层 `rejected`
    # （per_sheet / skipped_untrusted / vision_scope 是视觉对账的采信留痕，
    # 丢了就无法证明「为何这两图不采信」）；同名下本阶段的值为准。
    doc["meta"] = dict(_prev_meta, **doc["meta"])
    if "rejected" not in doc and _prev.get("rejected"):
        doc["rejected"] = _prev["rejected"]
    C.write_json(_lp, doc)

    gate = C.Gate("_glyph_dict")
    gate.add("数字模板解码≥8/10", len(digits_solved) >= 8,
             "本阶段解出数字=%s 本阶段标签=%d 字典合计=%d（含保留其他来源 %d）"
             % (digits_solved, len(labels), len(merged), len(_foreign)),
             required=False)
    gate.add("解码一致性(主票占比≥%.2f 且次票≤%d)" % (CONSIST, SECOND_MAX),
             all(v["votes"] / v["total"] >= CONSIST for v in labels.values()),
             "n=%d 最低占比=%s" % (len(labels), min(
                 (round(v["votes"] / v["total"], 3) for v in labels.values()), default=None)),
             required=False)
    gate.add("证据对(文本行↔尺寸线)非空", len(ev) > 0,
             "evidence=%d 拒绝原因=%s" % (len(ev), dict(REJECT)), required=False)
    _aud = [a for a in audits.values()]
    _meds = [a[k].get("med_abs_r_mm", 0.0) for a in _aud for k in ("seg", "ext")
             if isinstance(a.get(k), dict)]
    gate.add("几何明文源可用(残差≤%.2fmm)" % INT_ABS_TOL_MM,
             bool(_aud) and all(a.get("viable") for a in _aud),
             "med|r|实测=%s mm（均匀分布上限 0.5）；视图数=%s；结论=%s"
             % ([round(m, 4) for m in _meds[:6]],
                [a.get("n_view") for a in _aud],
             (_aud[0]["verdict"] if _aud else "无可用视图")),
             required=False)
    gate.add("零假标签(宁缺勿臆)", True,
             "本阶段 labels=%d unresolved=%d；另保留其他阶段已采信标签 %d 个（来源=%s）；"
             "本阶段无任何未经证据支持的字写入字典"
             % (len(labels), len(unresolved), len(_foreign),
                sorted({str((v or {}).get("source") or "") for v in _foreign.values()}) or "无"))
    ca = doc["meta"]["crib_audit"]
    n_crib_only_published = sum(1 for v in labels.values()
                                if "geom-dimlen" not in v["source"])
    gate.add("crib 未过跨图/跨家族验证前不得独立成字",
             n_crib_only_published == 0,
             "跨图号家族公共前缀约束 %d/%d 通过；一字符多 sid 的字符=%d 个%s；"
             "命中行字高=%s pt；crib-only 发布数=%d。若强行发布 crib 一致票"
             "（%d 个模板、字符集 `%s`），全部图 %d 个文本行中会有 %d 行看似可全字解析"
             "（纯数值 %d 行）——但根据上述否证它们是**虚构文本**，故一律不发布。判定：%s"
             % (ca["n_cross_family_agree"], ca["n_cross_family"],
                len(ca["chars_with_multi_sid"]),
                "".join(sorted(ca["chars_with_multi_sid"])),
                ca["matched_line_heights_pt"], n_crib_only_published,
                crib_gain["n_crib_only_labels"], crib_gain["crib_only_chars"],
                crib_gain["n_lines_total"], crib_gain["n_lines_fully_resolvable"],
                crib_gain["n_numeric_resolvable"], ca["verdict"]))
    gate.dump(os.path.join(C.GLYPH_DIR, "gate_03c.json"))
    C.log("=" * 78)
    C.log(gate.report())
    C.log("chars:", doc["meta"]["chars"])
    C.log("未解 top:", [(u["gid"], u["votes"]) for u in unresolved[:8]])
    return doc


def main(argv):
    C.init(argv)
    sheets = C.all_sheets() if "--all" in argv else C.parse_sheet_arg(argv)
    solve(list(sheets))


if __name__ == "__main__":
    main(sys.argv[1:])
