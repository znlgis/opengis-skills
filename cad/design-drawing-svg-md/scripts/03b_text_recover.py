# -*- coding: utf-8 -*-
"""03b 字形字典重建文本行（方案 §6 步骤 3 / 决策 D3）

prims.json + views.json + output/_glyph_dict/{templates.json,glyph_labels.json}
    → work/text.json

来源优先级（守方案 §4）：字典重建值 ＞ 视觉裁切复核 ＞ 不做 glyph OCR 猜测。
未标注模板一律给 UNK，只入 unclear，不臆造字符。

行重建在**横向(回正)坐标系**做：X_L = y_p、Y_L = W − x_p（X_L 右、Y_L 上）。
故横排文本行 = Y_L 近似恒定、沿 +X_L 前进；竖排文本行 = X_L 近似恒定、
沿 −Y_L（自上而下）前进。行内按基线对齐容差 0.5×字高、字距上限 1.6×字高聚合。
"""
from __future__ import annotations

import math
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

LINE_GAP_MIN = 0.30       # ×字高：相邻字**中心距**下限（小于此为重叠/噪声）
LINE_GAP_MAX = 1.50       # ×字高：相邻字中心距上限（超过即断行）
TURN_COS = 0.883          # cos(28°)：行内转向角上限（允许沿斜向尺寸线排布）
GRID_CELL = 40.0          # pt：串链用的空间网格边长
UNK = "UNK"

# 尺寸前缀：Φ 在 CAD 单线字体里常写成 %%C；C 亦用于倒角
PREFIX_RE = re.compile(r"^([RrSsDdCc]?[Rr]?|%%[Cc]|[Φφ⌀Ø]|SR|CR|n\s*[×xX]|\d+\s*[×xX])")
NUM_RE = re.compile(r"(\d+(?:[.,]\d+)?)")
SCALE_RE = re.compile(r"1\s*[:：]\s*(\d+(?:\.\d+)?)")


# ---------------------------------------------------------------- 字典


def load_dict() -> tuple:
    """读跨图字形字典 → (sid→{ch,gid,conf}, 统计)。"""
    tdoc = C.read_json(os.path.join(C.GLYPH_DIR, "templates.json"), {"templates": {}})
    ldoc = C.read_json(os.path.join(C.GLYPH_DIR, "glyph_labels.json"), {})
    raw = ldoc.get("labels") if isinstance(ldoc, dict) and "labels" in ldoc else ldoc
    raw = raw or {}
    lab = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            lab[str(k).strip()] = {"ch": (v.get("char") or v.get("label") or UNK).strip(),
                                   "conf": v.get("confidence") or v.get("conf") or "high"}
        else:
            lab[str(k).strip()] = {"ch": str(v).strip() or UNK, "conf": "high"}
    d, gids = {}, {}
    for gid, m in (tdoc.get("templates") or {}).items():
        gids[m["sid"]] = gid
        if gid in lab:
            d[m["sid"]] = dict(lab[gid], gid=gid)
    # 03d 派生的标签以 **sid** 为键（不是 gid）。旧条件 `k not in gids` 意为
    # 「只收字典里没见过的 sid」，但那恰好排除了真正能查表的那些——已知 sid
    # 两个分支都不收，导致 labels_in=31 而 sid_labeled=0、全图 1461 字形全为 UNK。
    for k, v in lab.items():
        if k not in d:
            d[k] = dict(v, gid=gids.get(k))
    stats = {"templates": len(tdoc.get("templates") or {}), "labels_in": len(lab),
             "sid_labeled": len(d),
             "unk_labels": sum(1 for v in d.values() if v["ch"] in (UNK, "", "?")),
             "label_source": "output/_glyph_dict/glyph_labels.json"}
    return d, stats


# ---------------------------------------------------------------- 行重建


def land_box(p: dict) -> tuple:
    """竖放 prim bbox → 横向(回正) bbox (X0, Y0, X1, Y1)，Y 轴向上。"""
    x0, y0, x1, y1 = p["r"]
    return (y0, C.W_PT - x1, y1, C.W_PT - x0)


def collect_glyphs(base: str, gd: dict) -> tuple:
    """取全部已标记字形，附字符与横向几何量。"""
    pdoc = C.read_json(C.work_path(base, "prims.json"))
    vdoc = C.read_json(C.work_path(base, "views.json"))
    view_of = {}
    for v in vdoc["views"]:
        for i in v["members"]:
            view_of[i] = v["id"]
    out = []
    for p in pdoc["prims"]:
        if p["g"]["type"] != "GLYPH":
            continue
        sid = p.get("gs")
        e = gd.get(sid)
        ch = e["ch"] if e else UNK
        X0, Y0, X1, Y1 = land_box(p)
        # 横向系里 Y1−Y0 才是**字高**（=竖放 bbox 的宽）；X1−X0 是字宽。
        h = max(Y1 - Y0, 1e-6)
        out.append({"i": p["i"], "sid": sid, "gid": e["gid"] if e else None,
                    "ch": ch, "conf": e["conf"] if e else None,
                    "gl": p.get("gl", h), "ocg": p["ocg"] or "",
                    "vert_p": bool(p.get("gv")),
                    "view": view_of.get(p["i"], "V00"),
                    "x_pt": round((p["r"][0] + p["r"][2]) / 2, 3),
                    "y_pt": round((p["r"][1] + p["r"][3]) / 2, 3),
                    "X0": X0, "Y0": Y0, "X1": X1, "Y1": Y1,
                    "Xc": (X0 + X1) / 2, "Yc": (Y0 + Y1) / 2, "h": h})
    return out, vdoc, pdoc


def build_runs(gs: list) -> list:
    """**任意方向**贪婪串链（实测：尺寸文字常沿斜向尺寸线排布，19°/−25°/−32° 等，
    仅按轴对齐分组会漏掉它们）。规则：中心距在 [LINE_GAP_MIN, LINE_GAP_MAX]×字高
    之间、且与当前行方向夹角≤28°者接为同一行；先向前长、再向后长。
    """
    unused = set(range(len(gs)))
    grid = defaultdict(list)
    for k, g in enumerate(gs):
        grid[(int(g["Xc"] // GRID_CELL), int(g["Yc"] // GRID_CELL))].append(k)

    def cand(last: int, h: float):
        g = gs[last]
        bx, by = int(g["Xc"] // GRID_CELL), int(g["Yc"] // GRID_CELL)
        r = int(LINE_GAP_MAX * h // GRID_CELL) + 1
        out = []
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                for j in grid.get((bx + dx, by + dy), ()):
                    if j == last or j not in unused:
                        continue
                    hh = max(g["h"], gs[j]["h"])
                    d = math.hypot(gs[j]["Xc"] - g["Xc"], gs[j]["Yc"] - g["Yc"])
                    if LINE_GAP_MIN * hh <= d <= LINE_GAP_MAX * hh:
                        out.append((d, j))
        out.sort()
        return out

    def grow(start: int, direc):
        run = [start]
        unused.discard(start)
        while True:
            last = run[-1]
            h = max(gs[x]["h"] for x in run)
            pick = None
            for d, j in cand(last, h):
                v = (gs[j]["Xc"] - gs[last]["Xc"], gs[j]["Yc"] - gs[last]["Yc"])
                n = math.hypot(*v)
                if n < 1e-9:
                    continue
                u = (v[0] / n, v[1] / n)
                if direc is None or abs(u[0] * direc[0] + u[1] * direc[1]) >= TURN_COS:
                    pick = (j, u)
                    break
            if not pick:
                break
            j, u = pick
            run.append(j)
            unused.discard(j)
            direc = u if direc is None else (direc[0] + u[0], direc[1] + u[1])
            nn = math.hypot(*direc)
            if nn < 1e-9:                 # 回头相加抵消 → 保留本次方向
                direc = u
            else:
                direc = (direc[0] / nn, direc[1] / nn)
        return run, direc

    runs = []
    while unused:
        k0 = min(unused)
        fwd, direc = grow(k0, None)
        if len(fwd) >= 2 and direc:
            back, _ = grow(fwd[0], (-direc[0], -direc[1]))
            fwd = back[::-1][:-1] + fwd      # back 首元即 fwd[0]，去重
        runs.append(fwd)
    return runs


def run_angle(gs: list, run: list) -> tuple:
    """行的阅读方向角（度，规范到 (−90,90]）与是否竖排。"""
    if len(run) < 2:
        g = gs[run[0]]
        return (90.0 if g["vert_p"] else 0.0), bool(g["vert_p"])
    a = gs[run[0]]
    b = gs[run[-1]]
    ang = math.degrees(math.atan2(b["Yc"] - a["Yc"], b["Xc"] - a["Xc"]))
    if ang > 90:
        ang -= 180
    elif ang <= -90:
        ang += 180
    return round(ang, 2), abs(ang) > 60


def build_lines(gs: list) -> list:
    """串链 → 按阅读方向排序 → 按版面阅读序（自上而下、自左而右）输出。"""
    lines = []
    for run in build_runs(gs):
        ang, vert = run_angle(gs, run)
        r = [gs[k] for k in run]
        u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        r.sort(key=lambda x: x["Xc"] * u[0] + x["Yc"] * u[1])
        lines.append({"vert": vert, "angle": ang, "g": r})
    lines.sort(key=lambda L: (-max(x["Y1"] for x in L["g"]), min(x["X0"] for x in L["g"])))
    return lines


# ---------------------------------------------------------------- 语义解析


def parse_value(s: str) -> tuple:
    """从文本行取 (value, prefix, kind)；非数值行 value=None。"""
    t = s.strip()
    m = PREFIX_RE.match(t)
    prefix = m.group(1) if m else ""
    pu = prefix.upper().replace("%%C", "Φ")
    body = t[m.end():] if m else t
    nums = NUM_RE.findall(body.replace(",", ""))
    if not nums:
        return None, pu or None, None
    try:
        val = float(nums[0].replace(",", ""))
    except ValueError:
        return None, pu or None, None
    if pu in ("R", "SR"):
        kind = "radius"
    elif pu in ("Φ", "D", "C"):
        kind = "diameter" if pu in ("Φ", "D") else "chamfer"
    elif "×" in pu.upper():
        kind = "count"
    else:
        kind = "length"
    return val, pu or None, kind


def line_record(k: int, L: dict) -> dict:
    r = L["g"]
    n_unk = sum(1 for x in r if x["ch"] == UNK)
    resolved = n_unk == 0
    # 未解出的字形**不发布字符串**：绝不用 '?' 之类占位符冒充内容（方案 D3「不做
    # glyph OCR 猜测」）。text=None 时几何、字高、方向与模板 id 仍全量保留，
    # 字典补齐后可原地重建，无需重新提取。
    chars = "".join(x["ch"] for x in r) if resolved else None
    confs = {x["conf"] for x in r if x["conf"]}
    if not resolved:
        conf = "low"                     # 含 UNK：不发布字符串，也不参与尺寸绑定
    elif not confs or confs == {"high"}:
        conf = "high"
    else:
        conf = "med"
    val, prefix, kind = parse_value(chars) if resolved else (None, None, None)
    views = Counter(x["view"] for x in r)
    vid = views.most_common(1)[0][0]
    hs = Counter(round(x["gl"], 1) for x in r)
    # 页面 pt 位置：取阅读起点（已按阅读方向排好序）的首字
    first = r[0]
    return {
        "line_id": "L%04d" % (k + 1), "text": chars, "resolved": resolved,
        "n_glyphs": len(r), "n_unk": n_unk,
        "value": val, "prefix": prefix, "kind": kind, "view": vid,
        "view_share": round(views[vid] / len(r), 3),
        "vert": L["vert"], "angle": L.get("angle"), "conf": conf,
        "h_pt": hs.most_common(1)[0][0],
        "x_pt": first["x_pt"], "y_pt": first["y_pt"],
        "x_pt_center": round(sum(x["x_pt"] for x in r) / len(r), 3),
        "y_pt_center": round(sum(x["y_pt"] for x in r) / len(r), 3),
        # 横向(回正)包围盒：用字形**实际边界**而非中心，使跨度/字距可量
        "land_bbox": [round(min(x["X0"] for x in r), 3), round(min(x["Y0"] for x in r), 3),
                      round(max(x["X1"] for x in r), 3), round(max(x["Y1"] for x in r), 3)],
        "ocg": Counter(x["ocg"] for x in r).most_common(1)[0][0],
        "glyphs": [{"i": x["i"], "sid": x["sid"], "gid": x["gid"], "ch": x["ch"],
                    "conf": x["conf"], "prim_id_i": x["i"]} for x in r],
    }


# ---------------------------------------------------------------- 标题栏 / 技术要求

TITLE_KEYS = [
    ("图号", r"(X\d{3}S[-－]\d{6}[A-Za-z]?)"),
    ("比例", r"(1\s*[:：]\s*\d+(?:\.\d+)?)"),
    ("材料", r"(Q235[A-D]?|Q345[A-D]?|Q355[A-D]?|45#?|40Cr|20CrMnTi|304|316L?"
             r"|HT\d{3}|ZG\d+|H62|T[12]|65Mn|20#?|A3|不锈钢|铸钢|铸铁|尼龙|橡胶)"),
    ("重量", r"(\d+(?:\.\d+)?)\s*(kg|KG|Kg|千克)"),
    ("日期", r"(20\d{2})[年\-/.](\d{1,2})[月\-/.](\d{1,2})"),
    ("版次", r"\b(R\d{2})\b"),
    ("数量", r"(共?\s*\d+\s*(件|套|个|张))"),
]
CN_HINT = re.compile(r"[\u4e00-\u9fff]")


def title_block_fields(tb_lines: list) -> dict:
    """从标题栏区文本行抽字段（正则命中即取，标注来源与置信）。

    未解出的行 text=None，只保留几何与字形计数：占位符不进 blob，
    既避免 '?' 被正则误命中，也避免假字符随 metadata 流进交付 SVG。
    """
    blob = "\n".join(L["text"] for L in tb_lines if L["text"])
    out = {"raw_lines": [{"text": L["text"], "n_glyphs": L["n_glyphs"],
                          "n_unk": L["n_unk"], "land_bbox": L["land_bbox"],
                          "conf": L["conf"]} for L in tb_lines],
           "n_resolved_lines": sum(1 for L in tb_lines if L["resolved"])}
    for name, pat in TITLE_KEYS:
        m = re.search(pat, blob)
        if m:
            out[name] = {"value": m.group(1).strip(), "source": "字典重建(正则命中)",
                         "conf": "med"}
    out["n_lines"] = len(tb_lines)
    out["n_cn_lines"] = sum(1 for L in tb_lines if L["text"] and CN_HINT.search(L["text"]))
    return out


# 技术要求条款的判据：行内必须含汉字。不复用 CN_HINT（那个还包含中文标点，
# 而标点可以出现在尺寸标注里，例如 `4-Φ20，均布` 的逗号），此处只要表意文字。
TR_CJK = re.compile(r"[\u4e00-\u9fff]")
TR_MIN_CJK = 2      # 条款至少 2 个汉字：实测某图的 `向5`（h_pt=14.5、竖排、
                    # land_bbox 12.4×45pt、value=5.0、OCG=「标注 文字线」）是视图方向/
                    # 剖向符号一类标注，单汉字+数字不成句，不得当条款交付。


def tech_requirements(note_lines: list) -> tuple:
    """技术要求：注释区文本行里**含汉字的散文句**按阅读顺序逐字输出。

    返回 (条目, 被排除行的文本列表)。只输出**完整解出**的行；未解出的行不输出
    （宁缺勿臆），其数量由 §6 不清项承载。

    为何不能只看 OCG：实测多图注释区的完整解出行**无一条含汉字**——全是
    `9720`/`120`/`Φ60`/`C45` 这类尺寸值与倒角/直径标注，它们属于零件视图而不是技术
    要求条款（CAD 导出把标注文字也放进了注释类 OCG）。只按「长度≥2」过滤会把这
    这些尺寸数字当技术要求逐字交付、还标 conf=high，即向 §5 注入臆造内容。

    判据取「至少 TR_MIN_CJK 个汉字」而不是「含汉字」：后者会把 `向5` 这种单汉字+数字的
    视图方向标注放进来（实测确有一例）。汉字是中文图纸技术要求句的必要条件，
    不成句者一律排除（宁缺勿臆）。
    """
    out, skipped = [], []
    for L in note_lines:
        if not L["text"] or len(L["text"].strip()) < 2:
            continue
        if len(TR_CJK.findall(L["text"])) < TR_MIN_CJK:
            skipped.append(L["text"])
            continue
        out.append({"text": L["text"], "line_id": L["line_id"], "view": L["view"],
                    "land_bbox": L["land_bbox"], "conf": L["conf"],
                    "n_unk": L["n_unk"], "h_pt": L["h_pt"]})
    return out, skipped


# ---------------------------------------------------------------- 主流程


def build(base: str) -> dict:
    gd, dstats = load_dict()
    gs, vdoc, pdoc = collect_glyphs(base, gd)
    if not gs:
        sys.exit("[%s] 无字形图元，无法重建文本" % base)
    lines = [line_record(k, L) for k, L in enumerate(build_lines(gs))]

    tb = vdoc.get("tb_bbox")
    tb_L = land_box({"r": tb}) if tb else None
    tb_lines, note_lines = [], []
    for L in lines:
        bx = L["land_bbox"]
        if tb_L and bx[0] >= tb_L[0] - 30 and bx[1] >= tb_L[1] - 30 \
                and bx[2] <= tb_L[2] + 30 and bx[3] <= tb_L[3] + 30:
            L["zone"] = "title-block"
            tb_lines.append(L)
        elif L["ocg"] in C.OCG_NOTES:
            L["zone"] = "notes"
            note_lines.append(L)
        else:
            L["zone"] = "drawing"

    tr, tr_skip = tech_requirements(note_lines)
    numeric = [L for L in lines if L["value"] is not None]
    scale_reads = [{"view": L["view"], "text": L["text"], "line_id": L["line_id"]}
                   for L in lines if L["text"] and SCALE_RE.search(L["text"])]

    # 绿层对账：重建数值集合 vs 尺寸层图元按推断比例换算的 mm 值集合
    cwd = C.read_json(C.deliverables(base)["crosswalk"], {"views": []})
    dimvals = defaultdict(list)
    for v in cwd.get("views", []):
        s = v.get("s_pt_per_mm") or 1.0
        for L in dimvals_list(v, pdoc, s):
            dimvals[v["id"]].append(L)
    cov = coverage(numeric, dimvals)

    doc = {
        "base_name": base, "method": "字形模板字典重建（决策 D3；非 glyph OCR 猜测）",
        "dict_stats": dstats,
        "counts": {"glyphs": len(gs), "lines": len(lines), "numeric": len(numeric),
                   "unk_glyphs": sum(1 for g in gs if g["ch"] == UNK),
                   "labeled_glyphs": sum(1 for g in gs if g["ch"] != UNK),
                   "by_conf": dict(Counter(L["conf"] for L in lines)),
                   "resolved_lines": sum(1 for L in lines if L["resolved"]),
                   "by_zone": dict(Counter(L.get("zone") for L in lines)),
                   "vert_lines": sum(1 for L in lines if L["vert"] is True and L["n_glyphs"] > 1),
                   "horiz_lines": sum(1 for L in lines if L["vert"] is False and L["n_glyphs"] > 1),
                   "single_lines": sum(1 for L in lines if L["n_glyphs"] == 1),
                   "angles": dict(Counter(round(L["angle"] or 0) for L in lines
                                          if L["n_glyphs"] > 1).most_common(8)),
                   "scale_reads": len(scale_reads)},
        "green_layer_coverage": cov,
        "title_block": title_block_fields(tb_lines),
        "title_block_source": "字典重建(正则命中) + 待 vision 高清裁切复核",
        "technical_requirements": tr,
        "tech_req_stats": {"n_note_lines": len(note_lines),
                           "n_excluded_non_cjk": len(tr_skip),
                           "min_cjk": TR_MIN_CJK,
                           "excluded_samples": tr_skip[:6],
                           "why": "zone=notes 但汉字数<%d → 属零件视图的尺寸/倒角/直径/"
                                  "视图方向标注，不是技术要求条款，不入 §5" % TR_MIN_CJK},
        "scale_reads": scale_reads,
        "unclear": [{"kind": "UNK 字形", "n": dstats["templates"] - dstats["sid_labeled"],
                     "note": "未标注模板一律 UNK，不臆造字符；含 UNK 的数值不参与尺寸绑定"},
                    {"kind": "含 UNK 的文本行", "n": sum(1 for L in lines if L["n_unk"])},
                    {"kind": "数值零/多命中", "n": 0,
                     "note": "由 05_crosswalk 的 unbound_values 承载"},
                    {"kind": "注释区不成句行(尺寸值/倒角/方向标注)", "n": len(tr_skip),
                     "note": "zone=notes 但汉字数<%d → 属零件视图的尺寸/倒角/直径/视图方向标注，"
                             "不是技术要求条款，故不入 §5（不臆造）；其数值仍参与 §3 尺寸绑定。"
                             "样例=%s" % (TR_MIN_CJK, tr_skip[:6] or "无")}],
        "texts": lines,
    }
    C.write_json(C.work_path(base, "text.json"), doc)

    gate = C.Gate(base)
    gate.add("文本行重建非空", len(lines) > 0, "行数=%d 字数=%d" % (len(lines), len(gs)))
    gate.add("行 view 归属无 UNASSIGNED",
             all(L["view"] != "UNASSIGNED" for L in lines),
             "视图分布 top=%s" % Counter(L["view"] for L in lines).most_common(6))
    gate.add("数值文本行非空", len(numeric) > 0,
             "数值行=%d（含 UNK 者 conf=low 不绑定）" % len(numeric),
             required=False)
    gate.add("UNK 不臆造(未标注模板一律 UNK)",
             all(g["ch"] != "" for g in gs),
             "已标注字=%d/%d（%.1f%%）字典模板=%d 标注=%d"
             % (doc["counts"]["labeled_glyphs"], len(gs),
                100.0 * doc["counts"]["labeled_glyphs"] / max(1, len(gs)),
                dstats["templates"], dstats["sid_labeled"]))
    gate.add("占位符不冒充内容(未解出行 text=null)",
             all((L["text"] is None) == (not L["resolved"]) for L in lines)
             and not any("?" in (L["text"] or "") for L in lines),
             "完整解出行=%d/%d；未解出行 text=null（不写 '?'、不进 SVG <text>），"
             "几何与模板 id 全量保留可原地重建"
             % (doc["counts"]["resolved_lines"], len(lines)))
    # 方案阶段B 步骤3 的交叉核对原只要求在基线图上做；这里对每图都算，
    # 但门禁名不得写死具体图号，否则在非基线图上会误报为“已核对基线图”。
    gate.add("重建数值集合覆盖绿层%s"
             % ("（基线图，方案B-3 指定核对项）" if base == C.baseline_sheet() else ""),
             cov["hit_frac"] >= 0.30,
             "命中=%d/%d=%.3f 绿层候选=%d 冲突=%d"
             % (cov["hits"], cov["n_numeric"], cov["hit_frac"], cov["n_dim"],
                len(cov["conflicts"])),
             required=False)
    gate.dump(C.work_path(base, "gate_03b.json"))
    C.log("=" * 78)
    C.log(gate.report())
    C.log("字典:", dstats)
    C.log("counts:", doc["counts"])
    C.log("绿层对账:", {k: v for k, v in cov.items() if k != "conflicts"},
          "冲突top=%s" % cov["conflicts"][:6])
    C.log("标题栏字段:", {k: v for k, v in doc["title_block"].items() if k != "raw_lines"})
    C.log("技术要求行:", len(doc["technical_requirements"]),
          "比例识读:", doc["scale_reads"][:6])
    for L in lines[:14]:
        C.log("  %-7s %-3s %-12s %-5s %-22s v=%-8s a=%-6s conf=%s unk=%d"
              % (L["line_id"], L["view"], L.get("zone"), L["n_glyphs"],
                 (L["text"] or "<未解出:null>")[:22],
                 L["value"], L["angle"], L["conf"], L["n_unk"]))
    return doc


def dimvals_list(v: dict, pdoc: dict, s: float) -> list:
    """视图内尺寸层直线按 s 换算的 mm 长度（绿层对账用）。"""
    by_i = {p["i"]: p for p in pdoc["prims"]}
    out = []
    for i in v.get("members", []):
        p = by_i.get(i)
        if not p or p["sem"] != "dimension":
            continue
        L = p["g"].get("len_pt")
        if L and L >= 15.0:
            out.append(round(L / s, 2))
    return out


def coverage(numeric: list, dimvals: dict, tol: float = 1.5) -> dict:
    """重建数值 vs 绿层换算长度：同视图内 |Δ|≤tol(mm) 视为命中；记录冲突值。"""
    hits, conf = 0, []
    n = 0
    for L in numeric:
        if L["conf"] == "low" or L["value"] is None:
            continue
        n += 1
        cands = dimvals.get(L["view"], [])
        near = [c for c in cands if abs(c - L["value"]) <= tol]
        if near:
            hits += 1
        else:
            conf.append({"line_id": L["line_id"], "view": L["view"], "text": L["text"],
                         "value": L["value"]})
    return {"n_numeric": n, "hits": hits, "hit_frac": round(hits / n, 4) if n else 0.0,
            "n_dim": sum(len(v) for v in dimvals.values()), "conflicts": conf}


def main(argv):
    C.init(argv)
    for base in C.parse_sheet_arg(argv):
        build(base)


if __name__ == "__main__":
    main(sys.argv[1:])
