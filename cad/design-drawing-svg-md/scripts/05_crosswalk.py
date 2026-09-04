# -*- coding: utf-8 -*-
"""05 crosswalk：比例三档 + 坐标换算 + 每视图 self_check + 尺寸绑定（决策 D4/D5）

prims.json + views.json (+ text.json 可选) → <base>_crosswalk.json

换算式（方案 §5，已用 V15 例逐字校验：bbox=[1890.1,1420.5,2310.7,2260.9]、1:20
→ s=0.14173、tx=1420.5、ty=493.55、(1140,2850)→(y_p=1582.07, x_p=2294.05)）：
    rotation   = "ccw90"（回正=逆时针90°；渲染 page.set_rotation(270)）
    x0 = W − ty ; y0 = tx            （即 tx = bbox.y0, ty = W − bbox.x0）
    local_to_portrait :  x_p = x0 + y_mm·s ;  y_p = y0 + x_mm·s
    portrait_to_local :  x_mm = (y_p − y0)/s ;  y_mm = (x_p − x0)/s
    portrait_to_landscape : (X_L, Y_L) = (y_p, W − x_p) = (tx + x_mm·s, ty − y_mm·s)
    self_check : (0,0) → x_p == bbox.x0 且 y_p == bbox.y0

比例三档：read(文本恢复读到「1:xx」) ＞ inferred(候选分母打分，记 score) ＞ fallback(1:10)。
尺寸绑定：唯一命中才绑（守方案 §1「不臆造定位」），多命中/零命中只入 unclear。
"""
from __future__ import annotations

import math
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def _cfg() -> dict:
    """config 运行时快照（common.init 后可用）；未 init 时为空 dict。"""
    return getattr(C, "_CFG", None) or {}


DEN_CANDIDATES = [1, 2, 5, 10, 20, 25, 50, 100, 200]
FALLBACK_DEN = 10
NICE_STEP = 10.0         # mm，尺寸值网格（钢结构图多为 10mm 倍数）
NICE_TOL = 1.0           # mm，网格命中容差（容纳导出器的比例系数偏差）
MIN_DIM_LEN = 15.0       # pt，参与打分的尺寸线最短长度（滤除箭头/短划/斜线）
K_STEPS = [1.0 + 0.0005 * i for i in range(-40, 41)]   # 仅用于分母选择的放宽启发式搜索域 ±2%
MM_MIN, MM_MAX = 5.0, 30000.0
HIT_FRAC = 0.55          # inferred 命中率达到该值即采纳（取最小分母）
BIND_TOL_PT = 0.6        # pt，尺寸线长度与 value·s 的绑定容差下限
SCALE_RE = re.compile(r"1\s*[:：]\s*(\d+(?:\.\d+)?)")
# 整页图框归属区（V00）的比例自证用参数：
ISO_A_MM = [(1189.0, 841.0), (841.0, 594.0), (594.0, 420.0),
            (420.0, 297.0), (297.0, 210.0)]      # A0..A4 的 (长边, 短边) mm
PAPER_PPM_TOL = 0.05      # pt/mm，纸型反查容差（A0 实测 2.8344 vs 标准 2.83465）
FRAME_COVER = 0.90        # bbox 两轴均覆盖页面 ≥90%（与 02 的「整页跨度线」同阈值）
FRAME_TOL_MM = 25.0       # mm，图框内缩于纸边的容差（实测 A0 长边内缩 7.2mm）


def nice_err(v: float, step: float = NICE_STEP) -> float:
    """v 到最近 step 倍数的距离（mm）。"""
    return abs(v - round(v / step) * step)


def infer_scale(dim_lens: list) -> dict:
    """对候选分母打分：命中（长度换算成 mm 后落在 NICE_STEP 网格上）最多者胜。

    **交付尺度一律用方案 D5 的标准公式 s_pt_per_mm = 2.83465 / 分母（k=1.0）**：
    方案 §5 已验证例 V15 的 s=0.14173 正是 2.83465/20，公式里没有修正系数。

    曾经在此处把一个拟合出的 k 直接乘进交付尺度，实测后已撤销，原因有两条硬证据：
    1. k 的搜索目标是「±NICE_TOL(1mm) 窗口命中 NICE_STEP(10mm) 网格」，其
       **随机命中率就有 ~20%**；在 81 个 k 里取命中最多者，是在拟合噪声。
       实测各视图 k 散布 0.981~1.0195（±2%，恰在搜索域边界），而同为 1:5
       的视图 k 分别是 1.0030/0.9905/0.9965/0.9910 —— 同一比例不应有四个 k。
    2. 残差审计（scripts/_diag_scale.py，已归档结论到 03c 的 plaintext_audit）：
       对全部 8 个候选分母，跨度换算值到最近整数的残差 med|r|≈0.15~0.42mm、
       p90|r|≈0.45mm（均匀分布上限 0.5），即 **mod 1 近似均匀 = 无信号**；
       换标准 s 与拟合 s 结论相同。没有任何证据支持某个特定 k。

    k 的放宽搜索仍**只用于挑分母**（「命中尺寸线数最多者胜」的启发式），
    拟合值作诊断量记录在 k_fit/k_fit_frac，不进入任何交付 mm 值。
    大分母是小分母的超集，故按分母升序取**第一个**命中率≥HIT_FRAC 者。
    """
    lens = [L for L in dim_lens if L >= MIN_DIM_LEN]
    if len(lens) < 3:
        return {"den": FALLBACK_DEN, "k": 1.0, "s": C.scale_s(FALLBACK_DEN),
                "source": "fallback", "score": 0, "hits": 0, "n": len(lens),
                "frac": 0.0, "reason": "视图内可用尺寸线<3 条（已滤除<%gpt 短划）" % MIN_DIM_LEN}
    table = []
    for den in DEN_CANDIDATES:
        s0 = C.scale_s(den)
        best = None
        for k in K_STEPS:
            s = s0 * k
            hits = 0
            for L in lens:
                v = L / s
                if MM_MIN <= v <= MM_MAX and nice_err(v) <= NICE_TOL:
                    hits += 1
            if best is None or hits > best[1]:
                best = (k, hits)
        k_fit, hits = best
        # 交付尺度用标准 s（k=1.0）；k_fit 只作诊断量随 crosswalk 落盘。
        hits0 = sum(1 for L in lens
                    if MM_MIN <= L / s0 <= MM_MAX and nice_err(L / s0) <= NICE_TOL)
        frac = hits / len(lens)
        table.append({"den": den, "k_fit": k_fit, "hits": hits, "hits_at_k1": hits0,
                      "n": len(lens), "frac": round(frac, 4),
                      "frac_at_k1": round(hits0 / len(lens), 4)})
        if frac >= HIT_FRAC:
            return {"den": den, "k": 1.0, "s": round(s0, 8), "source": "inferred",
                    "score": hits, "hits": hits, "n": len(lens), "frac": round(frac, 4),
                    "k_fit": k_fit, "k_fit_frac": round(frac, 4),
                    "frac_at_k1": round(hits0 / len(lens), 4),
                    "reason": "分母升序首个命中率≥%.2f；交付尺度用方案 D5 标准式 "
                              "s=2.83465/%d=%.7f（k=1.0），拟合 k=%.4f 仅诊断不入尺度"
                              % (HIT_FRAC, den, s0, k_fit),
                    "table": table}
    best = max(table, key=lambda t: (t["frac"], -t["den"]))
    if best["frac"] <= 0:
        return {"den": FALLBACK_DEN, "k": 1.0, "s": C.scale_s(FALLBACK_DEN),
                "source": "fallback", "score": 0, "hits": 0, "n": len(lens), "frac": 0.0,
                "reason": "所有候选分母命中数为 0", "table": table}
    return {"den": best["den"], "k": 1.0,
            "s": round(C.scale_s(best["den"]), 8), "source": "inferred",
            "score": 0, "hits": best["hits"], "n": best["n"], "frac": best["frac"],
            "k_fit": best["k_fit"], "k_fit_frac": best["frac"],
            "frac_at_k1": best.get("frac_at_k1", 0.0),
            "reason": "无分母达命中率阈值，取最高者(frac=%s)；score=0 → mm 值并入 unclear；"
                      "交付尺度仍用标准式 s=2.83465/%d（k=1.0）"
                      % (best["frac"], best["den"]), "table": table}


def paper_mm(page_pt: tuple):
    """由页面 pt 幅面反查 ISO A 系列纸型，返回 (长边mm, 短边mm) 或 None。

    page_pt = (短边pt, 长边pt)。长短边各自除以纸型对应边长，**两个商都得落在
    标准 PT_PER_MM 附近**才算命中；只看长宽比会把相邻纸型全部匹中（A 系列
    长宽比同为 √2）。
    """
    lo, hi = page_pt
    for L, S in ISO_A_MM:
        if (abs(hi / L - C.PT_PER_MM) <= PAPER_PPM_TOL
                and abs(lo / S - C.PT_PER_MM) <= PAPER_PPM_TOL):
            return (L, S)
    return None


def frame_scale(v: dict, paper: tuple, page_pt: tuple):
    """整页图框归属区（V00）的比例由**页面几何自证**，不走尺寸线打分。

    为何必须特判：V00 装的是 title-block 全层 + 整页跨度的图框/分区线
    （02 的归属定义），它的 bbox 就是纸本身。图框边框按定义是 1:1 画在纸上的，
    故其 mm 跨度必然等于纸张幅面 —— 这是**几何恒等式**，不需要拿尺寸线网格
    命中去猜。而打分在这个区里跑的是图框分区标记/引出线，长度与任何比例都不
    自洽：实测同一类整页区在各图里被打成 1:1/1:2/1:10/1:20 四种答案（某图得
    W_mm=23635mm，是 A0 长边的 20 倍），即把噪声当结论交付。

    自证：den=1 时 W_mm/H_mm 必须落在纸型幅面的 FRAME_TOL_MM 内，否则返回
    None 退回打分结果（宁缺勿臆）。坐标轴对应：竖放页 x 轴=纸短边、y 轴=纸长边，
    与 view_geometry 的 W_mm=(y1−y0)/s、H_mm=(x1−x0)/s 一致。
    """
    if not paper:
        return None
    x0, y0, x1, y1 = v["bbox_all"]
    span_x, span_y = x1 - x0, y1 - y0
    pg_x, pg_y = page_pt
    if span_x < FRAME_COVER * pg_x or span_y < FRAME_COVER * pg_y:
        return None
    s1 = C.scale_s(1)
    W_mm, H_mm = span_y / s1, span_x / s1
    L, S = paper
    if abs(W_mm - L) > FRAME_TOL_MM or abs(H_mm - S) > FRAME_TOL_MM:
        return None
    return {"den": 1, "k": 1.0, "s": round(s1, 8), "source": "inferred",
            "score": 0, "hits": 0, "n": 0, "frac": 0.0,
            "verified": True, "evidence": "page-geometry",
            "paper_mm": [L, S], "frame_mm": [round(W_mm, 3), round(H_mm, 3)],
            "reason": "整页图框归属区：bbox 覆盖页面 %.1f%%×%.1f%%，图框边框按定义以 "
                      "1:1 画在纸上，故 den=1 由页面几何自证（非文本识读、非尺寸线打分）。"
                      "自证：W_mm=%.1f / H_mm=%.1f 落在 %g×%gmm 纸型幅面 ±%gmm 内（内缩 "
                      "%.1f/%.1fmm = 图框距纸边）。score=0 仅表示未用尺寸线命中，**不代表"
                      "未验证**（scale_verified=true）。"
                      % (100.0 * span_x / pg_x, 100.0 * span_y / pg_y, W_mm, H_mm,
                         L, S, FRAME_TOL_MM, L - W_mm, S - H_mm)}


def view_geometry(v: dict, by_i: dict, s: float) -> dict:
    """视图局部 mm 几何量：尺寸线长度、弧/圆半径、外框角点、对称轴。"""
    x0, y0, x1, y1 = v["bbox_all"]
    dim_lens, radii, axes = [], [], []
    for i in v["members"]:
        p = by_i[i]
        g = p["g"]
        if p["sem"] == "dimension" and g["type"] == "LINE":
            dim_lens.append((i, C.seg_len(g["p1"], g["p2"])))
        elif p["sem"] == "dimension" and g["type"] == "POLYLINE":
            pts = C.flatten_prim(p)
            if len(pts) == 2:
                dim_lens.append((i, C.seg_len(pts[0], pts[1])))
        if g["type"] in ("CIRCLE", "ARC", "OBROUND"):
            radii.append((i, g["r"]))
        if p["sem"] == "centerline" and g["type"] == "LINE":
            axes.append((i, g["p1"], g["p2"]))
    # 对称轴交点（长中心线两两求交，落在 bbox 内者）
    inter = []
    for a in range(len(axes)):
        for b in range(a + 1, len(axes)):
            q = seg_intersect(axes[a][1], axes[a][2], axes[b][1], axes[b][2])
            if q and x0 - 1 <= q[0] <= x1 + 1 and y0 - 1 <= q[1] <= y1 + 1:
                inter.append(q)
    corners = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
    anchors = [{"name": "bbox角点", "pt": [round(a, 3) for a in c],
                "local_mm": [round(u, 3) for u in C.pt_to_local(c[0], c[1], x0, y0, s)]}
               for c in corners]
    if inter:
        c = (sum(q[0] for q in inter) / len(inter), sum(q[1] for q in inter) / len(inter))
        anchors.append({"name": "对称轴交点(均值,n=%d)" % len(inter),
                        "pt": [round(c[0], 3), round(c[1], 3)],
                        "local_mm": [round(u, 3) for u in C.pt_to_local(c[0], c[1], x0, y0, s)]})
    return {"dim_lens": dim_lens, "radii": radii, "anchors": anchors,
            "W_mm": round((y1 - y0) / s, 3), "H_mm": round((x1 - x0) / s, 3)}


def seg_intersect(p1, p2, p3, p4):
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return None
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den
    u = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / den
    if -0.02 <= t <= 1.02 and -0.02 <= u <= 1.02:
        return (p1[0] + t * d1[0], p1[1] + t * d1[1])
    return None


def bind_dims(v: dict, by_i: dict, s: float, texts: list) -> tuple:
    """唯一命中才绑定：数值文本 ↔ 等长尺寸线 / 等径圆弧。

    返回 (dims, unbound, geo)。dims 项含 dim-id、value、kind、prim_i、len_pt、
    matched_pt、match_delta_pt、tol_pt。**两个长度字段的语义不同**：
    `len_pt` 是图元自己的几何长（对圆弧/长圆是**弧长**），`matched_pt` 是命中判据
    实际参与比较的量（length=尺寸线长、radius=半径、diameter=直径）。自洽性只能看
    后者：拿弧长去比直径会得出假矛盾（实测各图 9 条，全为 diameter）。
    """
    geo = view_geometry(v, by_i, s)
    x0, y0 = v["bbox_all"][0], v["bbox_all"][1]
    cands = [(i, L) for i, L in geo["dim_lens"]]
    rad_c = [(i, r) for i, r in geo["radii"]]
    _rad_by_i = dict(rad_c)          # 供命中后回取半径，算 matched_pt
    dims, unbound = [], []
    nums = [t for t in texts if t.get("value") is not None and t.get("view") == v["id"]]
    nums.sort(key=lambda t: (t.get("y_pt", 0), t.get("x_pt", 0)))
    for k, t in enumerate(nums):
        val = float(t["value"])
        prefix = (t.get("prefix") or "").upper()
        tol = max(BIND_TOL_PT, 0.02 * val * s)
        hit, kind = [], None
        if prefix in ("R", "SR"):
            hit = [i for i, r in rad_c if abs(r - val * s) <= tol]
            kind = "radius"
        elif prefix in ("Φ", "%%C", "C", "D"):
            hit = [i for i, r in rad_c if abs(2 * r - val * s) <= tol]
            kind = "diameter"
        else:
            hit = [i for i, L in cands if abs(L - val * s) <= tol]
            kind = "length"
            if not hit:                    # 数值也可能是直径/半径标注
                h2 = [i for i, r in rad_c if abs(2 * r - val * s) <= tol]
                if h2:
                    hit, kind = h2, "diameter"
        if len(hit) == 1:
            p = by_i[hit[0]]
            loc = C.pt_to_local((p["r"][0] + p["r"][2]) / 2, (p["r"][1] + p["r"][3]) / 2,
                                x0, y0, s)
            # 命中判据用的几何量随 kind 而变：length 比尺寸线长、radius 比半径、
            # diameter 比直径。而 g["len_pt"] 对圆弧是**弧长**，与直径/半径不可比，
            # 故额外落盘 matched_pt / match_delta_pt，使「绑定是否自洽」可审计。
            # 命中本身就是用 tol 筛的，故 match_delta_pt ≤ tol_pt 恒成立。
            _r = _rad_by_i.get(hit[0])
            matched_pt = (p["g"].get("len_pt", 0.0) if kind == "length"
                          else (_r if kind == "radius" else
                                (2 * _r if _r is not None else None)))
            dims.append({
                "dim-id": C.dim_id(v["id"], len(dims) + 1), "value": val,
                "text": t.get("text"), "kind": kind, "prefix": prefix or None,
                "prim_i": hit[0], "len_pt": round(p["g"].get("len_pt", 0.0), 3),
                "matched_pt": (round(matched_pt, 3)
                               if matched_pt is not None else None),
                "match_delta_pt": (round(abs(matched_pt - val * s), 3)
                                   if matched_pt is not None else None),
                "expected_pt": round(val * s, 3), "tol_pt": round(tol, 3),
                "local_mm": [round(loc[0], 2), round(loc[1], 2)],
                "pos_pt": [round(t.get("x_pt", 0.0), 2), round(t.get("y_pt", 0.0), 2)],
                "vert": bool(t.get("vert")), "tpl_conf": t.get("conf"),
            })
        else:
            unbound.append({"text": t.get("text"), "value": val, "kind": kind,
                            "n_candidates": len(hit), "pos_pt":
                                [round(t.get("x_pt", 0.0), 2), round(t.get("y_pt", 0.0), 2)],
                            "reason": "多命中" if len(hit) > 1 else "零命中"})
    # 上面的唯一性只在**文本侧**成立：两个不同文本可各自唯一命中**同一条**
    # 尺寸线（实测某图：图框左右边缘的分区标记「11」各唯一命中 prim_i=4802），
    # 对该尺寸线而言仍是多命中、无法判定谁对。按 D4「多命中只入 unclear、
    # 不写 <text>」一并撤绑，不保留任何一个，并重排 dim-id 保持连续。
    cnt = Counter(d["prim_i"] for d in dims)
    amb = {k for k, n in cnt.items() if n > 1}
    if amb:
        keep = []
        for d in dims:
            if d["prim_i"] in amb:
                unbound.append({"text": d["text"], "value": d["value"], "kind": d["kind"],
                                "n_candidates": cnt[d["prim_i"]], "pos_pt": d["pos_pt"],
                                "prim_i": d["prim_i"],
                                "reason": "同一尺寸线被多个数值文本命中"})
            else:
                keep.append(d)
        dims = keep
        for k, d in enumerate(dims):
            d["dim-id"] = C.dim_id(v["id"], k + 1)
    return dims, unbound, geo


def self_check(v: dict, cw: dict) -> dict:
    """换算闭环自检：原点落 bbox 左下角 + 四角往返 + 横向一致性。"""
    x0, y0, x1, y1 = v["bbox_all"]
    s, tx, ty = cw["s_pt_per_mm"], cw["tx"], cw["ty"]
    p = C.local_to_pt(0.0, 0.0, x0, y0, s)
    d_origin = max(abs(p[0] - x0), abs(p[1] - y0))
    worst_rt = 0.0
    for q in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        mm = C.pt_to_local(q[0], q[1], x0, y0, s)
        b = C.local_to_pt(mm[0], mm[1], x0, y0, s)
        worst_rt = max(worst_rt, abs(b[0] - q[0]), abs(b[1] - q[1]))
    worst_L = 0.0
    for mm in ((0.0, 0.0), (100.0, 50.0), (cw["W_mm"], cw["H_mm"])):
        q = C.local_to_pt(mm[0], mm[1], x0, y0, s)
        xl, yl = C.to_landscape(*q)
        worst_L = max(worst_L, abs(xl - (tx + mm[0] * s)), abs(yl - (ty - mm[1] * s)))
    # tx/ty 以 6 位小数落盘，故横向一致性容差取 1e-5pt（约 3.5nm，远小于图元精度）
    ok = d_origin <= 1e-9 and worst_rt <= 1e-9 and worst_L <= 1e-5
    return {"pass": bool(ok), "origin_err_pt": d_origin,
            "roundtrip_err_pt": worst_rt, "landscape_err_pt": worst_L,
            "tol": {"origin": 1e-9, "roundtrip": 1e-9, "landscape": 1e-5},
            "expr": "x=0,y=0 → x_p==bbox.x0(%.3f) 且 y_p==bbox.y0(%.3f)" % (x0, y0)}


def build(base: str) -> dict:
    pdoc = C.read_json(C.work_path(base, "prims.json"))
    vdoc = C.read_json(C.work_path(base, "views.json"))
    if not pdoc or not vdoc:
        sys.exit("缺少 prims.json/views.json，请先跑 01/02 --sheet %s" % base)
    by_i = {p["i"]: p for p in pdoc["prims"]}
    pr = pdoc["meta"]["page_rect_pt"]
    if len(pr) == 4:
        _pw, _ph = abs(pr[2] - pr[0]), abs(pr[3] - pr[1])
    else:
        _pw, _ph = abs(pr[0]), abs(pr[1])
    page_pt = (min(_pw, _ph), max(_pw, _ph))   # 竖放：(短边pt=x轴, 长边pt=y轴)
    paper = paper_mm(page_pt)
    tdoc = C.read_json(C.work_path(base, "text.json"), {"texts": []})
    texts = tdoc.get("texts") or []
    texts_by_view = defaultdict(list)
    for t in texts:
        texts_by_view[t.get("view") or "V00"].append(t)

    views_out, unclear_scale, all_dims, all_unbound = [], [], [], []
    dims_by_view = {}
    for v in vdoc["views"]:
        x0, y0, x1, y1 = v["bbox_all"]
        geo_pre = view_geometry(v, by_i, C.scale_s(FALLBACK_DEN))
        sc = (frame_scale(v, paper, page_pt)
              or infer_scale([L for _, L in geo_pre["dim_lens"]]))
        # read 档：文本恢复读到「1:xx」。已被页面几何自证的视图不吃这一档——V00
        # 里的文本是标题栏比例字段，它描述的是其它视图而不是图框本身，用它覆盖
        # V00 会把本已消除的跨图不一致重新引回来。
        if not sc.get("verified"):
            for t in texts_by_view.get(v["id"], []):
                m = SCALE_RE.search(t.get("text") or "")
                if m:
                    den = float(m.group(1))
                    sc = {"den": den, "k": 1.0, "s": round(C.scale_s(den), 8),
                          "source": "read", "score": -1, "hits": -1,
                          "n": sc["n"], "frac": sc["frac"],
                          "reason": "视图内文本识读到「%s」" % t["text"],
                          "from_text": t.get("text")}
                    break
        s = sc["s"]
        geo = view_geometry(v, by_i, s)
        cw = {
            "id": v["id"], "name": v["name"], "kind": v["kind"],
            "layout": v["layout"], "bbox": v["bbox_all"], "bbox_L": v.get("bbox_L"),
            "n_members": v["n"], "by_layer": v["by_layer"],
            "scale": "1:%g" % sc["den"], "scale_den": sc["den"],
            "scale_source": sc["source"], "scale_score": sc["score"],
            "scale_k": sc["k"], "scale_frac": sc["frac"],
            "scale_reason": sc["reason"],
            "scale_verified": bool(sc.get("verified")),
            "scale_evidence": sc.get("evidence") or "dim-grid",
            "s_pt_per_mm": s,
            "tx": round(y0, 6), "ty": round(C.W_PT - x0, 6),
            "x0": round(x0, 6), "y0": round(y0, 6),
            "W_mm": geo["W_mm"], "H_mm": geo["H_mm"],
            "anchors": geo["anchors"],
            "n_dim_lines": len(geo["dim_lens"]), "n_arcs": len(geo["radii"]),
        }
        if sc.get("table"):
            cw["scale_table"] = sc["table"]
        if sc.get("verified"):
            cw["paper_mm"] = sc["paper_mm"]
            cw["frame_mm"] = sc["frame_mm"]
        cw["self_check"] = self_check(v, cw)
        dims, unbound, _ = bind_dims(v, by_i, s, texts_by_view.get(v["id"], []))
        cw["dims"] = dims
        cw["n_dims_bound"] = len(dims)
        cw["n_dims_unbound"] = len(unbound)
        if not sc.get("verified") and (
                sc["source"] == "fallback"
                or (sc["source"] == "inferred" and sc["score"] == 0)):
            unclear_scale.append({"view": v["id"], "scale": cw["scale"],
                                  "source": sc["source"], "reason": sc["reason"],
                                  "note": "该视图局部 mm 值未验证，全部并入 §6 不清项"})
        views_out.append(cw)
        dims_by_view[v["id"]] = dims
        all_dims.extend(dims)
        all_unbound.extend(dict(u, view=v["id"]) for u in unbound)

    n_dim_texts = sum(1 for t in texts if t.get("value") is not None)
    cw_doc = {
        "base_name": base,
        "page": 1,
        "page_rect_pt": pdoc["meta"]["page_rect_pt"],
        "rotation": C.ROTATION,
        "W_pt": C.W_PT, "H_pt": C.H_PT, "pt_per_mm": C.PT_PER_MM,
        "page_pt": list(page_pt), "paper_mm": list(paper) if paper else None,
        "formula": {
            "x0": "W − ty", "y0": "tx", "tx": "bbox.y0", "ty": "W − bbox.x0",
            "local_to_portrait": "x_p = x0 + y_mm·s ; y_p = y0 + x_mm·s",
            "portrait_to_local": "x_mm = (y_p − y0)/s ; y_mm = (x_p − x0)/s",
            "portrait_to_landscape": "(X_L, Y_L) = (y_p, W − x_p)",
            "landscape_from_local": "X_L = tx + x_mm·s ; Y_L = ty − y_mm·s",
            "s_pt_per_mm": "2.83465 / 比例分母",
            "self_check": "(0,0) → x_p == bbox.x0 且 y_p == bbox.y0",
            "verified_against": "方案 §5 V15 例：bbox=[1890.1,1420.5,2310.7,2260.9] 1:20 "
                                "→ tx=1420.5 ty=493.55；(1140,2850)→(y_p=1582.07,x_p=2294.05)",
        },
        "id_system": pdoc["meta"]["id_system"],
        "scale_sources": dict(Counter(v["scale_source"] for v in views_out)),
        "counts": {"views": len(views_out), "dims_bound": len(all_dims),
                   "dims_unbound": len(all_unbound), "numeric_texts": n_dim_texts,
                   "bind_rate": round(len(all_dims) / n_dim_texts, 4) if n_dim_texts else None},
        "views": views_out,
        "unclear_scale": unclear_scale,
        "unbound_values": all_unbound,
    }
    C.write_json(C.deliverables(base)["crosswalk"], cw_doc)
    C.write_json(C.work_path(base, "crosswalk_stats.json"),
                 {"counts": cw_doc["counts"], "scale_sources": cw_doc["scale_sources"],
                  "scales": {v["id"]: [v["scale"], v["scale_source"], v["scale_score"]]
                             for v in views_out}})

    gate = C.Gate(base)
    bad = [v["id"] for v in views_out if not v["self_check"]["pass"]]
    gate.add("每视图 self_check 通过", not bad,
             "%d/%d 通过%s" % (len(views_out) - len(bad), len(views_out),
                              ("失败=%s" % bad) if bad else ""))
    gate.add("换算式与方案 §5 例一致", verify_plan_example(), "V15 例逐字复算")
    gate.add("比例来源分档齐全", all(v["scale_source"] in ("read", "inferred", "fallback")
                                    for v in views_out),
             str(cw_doc["scale_sources"]))
    gate.add("score=0/fallback 已入 unclear",
             len(unclear_scale) == sum(1 for v in views_out
                                       if not v.get("scale_verified")
                                       and (v["scale_source"] == "fallback"
                                            or (v["scale_source"] == "inferred"
                                                and v["scale_score"] == 0))),
             "unclear_scale=%d；另有 %d 个视图由页面几何自证(scale_verified)，不入 unclear"
             % (len(unclear_scale),
                sum(1 for v in views_out if v.get("scale_verified"))))
    fr = [v for v in views_out if v.get("scale_verified")]
    gate.add("整页图框区比例由页面几何自证为 1:1",
             bool(fr) and all(v["scale_den"] == 1 for v in fr),
             "verified=%s 纸型=%s 图框幅面(mm)=%s"
             % ([v["id"] for v in fr] or "无", list(paper) if paper else "未识别",
                [v.get("frame_mm") for v in fr]),
             required=bool(paper))
    dup_bind = [vid for vid, ds in dims_by_view.items()
                if len({d["prim_i"] for d in ds}) != len(ds)]
    gate.add("尺寸绑定唯一命中(不臆造)", not dup_bind,
             "一条尺寸线至多绑一个值；重复绑定视图=%s | bound=%d unbound=%d 数值文本=%d 绑定率=%s"
             % (dup_bind or "无", len(all_dims), len(all_unbound), n_dim_texts,
                cw_doc["counts"]["bind_rate"]),
             required=bool(texts))
    if base == C.baseline_sheet():
        br = (_cfg().get("baseline") or {}).get("bind_rate")
        if br is not None:
            gate.add("方案 §11 基线绑定率(%s) %.1f%%" % (base, br * 100),
                     cw_doc["counts"]["bind_rate"] is None
                     or abs(cw_doc["counts"]["bind_rate"] - br) <= 0.15,
                     "本次=%s（文本恢复前为 None，属预期）" % cw_doc["counts"]["bind_rate"],
                     required=False)
    gate.dump(C.work_path(base, "gate_05.json"))

    C.log("=" * 78)
    C.log(gate.report())
    for v in views_out:
        C.log("  %-4s %-7s %-9s score=%-5s k=%.4f frac=%.2f s=%.6f tx=%.2f ty=%.2f "
              "mm=%.0f×%.0f dim线=%-4d 绑定=%d/%d self_check=%s"
              % (v["id"], v["scale"], v["scale_source"], v["scale_score"], v["scale_k"],
                 v["scale_frac"], v["s_pt_per_mm"], v["tx"], v["ty"], v["W_mm"], v["H_mm"],
                 v["n_dim_lines"], v["n_dims_bound"],
                 v["n_dims_bound"] + v["n_dims_unbound"], v["self_check"]["pass"]))
    C.log("→", C.deliverables(base)["crosswalk"])
    return cw_doc


def verify_plan_example() -> bool:
    """用方案 §5 的 V15 例逐字复算换算式（数值取方案给出的 1582.1/2294.0）。"""
    bbox = (1890.1, 1420.5, 2310.7, 2260.9)
    s = C.scale_s(20)
    x0, y0 = bbox[0], bbox[1]
    tx, ty = y0, C.W_PT - x0
    if abs(tx - 1420.5) > 0.01 or abs(ty - 493.55) > 0.01 or abs(s - 0.14173) > 1e-4:
        return False
    xp, yp = C.local_to_pt(1140, 2850, x0, y0, s)
    return abs(yp - 1582.1) <= 0.05 and abs(xp - 2294.0) <= 0.05


def main(argv):
    C.init(argv)
    for base in C.parse_sheet_arg(argv):
        build(base)


if __name__ == "__main__":
    main(sys.argv[1:])
