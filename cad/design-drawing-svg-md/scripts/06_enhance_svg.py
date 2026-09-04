# -*- coding: utf-8 -*-
"""06 六层 SVG 生成（六层 schema 与四项增强见 reference/svg-spec.md / 决策 D6-D7）

prims.json + views.json + crosswalk.json (+ text.json 可选) → <base>.svg

要点（守 §4）：保持竖放不旋转；不加 shape-rendering=crispEdges；曲线「折线显示 +
data-params 参数旁注」双轨；glyph 路径保留但可被消费者按 §7 剔除；每 path 带
data-prim / data-prim-id / data-ocg / data-color，使分层与归视图可追溯。
门禁：SVG path 数 == kept（计数对账链 drawings→kept→SVG path）。
"""
from __future__ import annotations

import math
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

GENERATOR = "scripts/06_enhance_svg.py"
# 占位符不冒充内容：未解出字形的掩码（'?'/'??'…）一律降为 None，
# 即使上游 text.json 是旧版（用 '?' 填充）也不会让假字符流进交付 SVG。
PLACEHOLDER_RE = re.compile(r"^\?+$")
PLACEHOLDER_TEXT_RE = re.compile(r">\s*\?+\s*<")


def strip_placeholders(o):
    """递归把 '?' 掩码降为 None（只作用于 metadata 镜像，不触碰几何）。"""
    if isinstance(o, str):
        return None if PLACEHOLDER_RE.match(o.strip()) else o
    if isinstance(o, dict):
        return {k: strip_placeholders(v) for k, v in o.items()}
    if isinstance(o, list):
        return [strip_placeholders(v) for v in o]
    return o

# data-prim 取值：几何类型优先，直线类按层语义细化（与 MD §3 用词一致）
DIM_PRIM = {"dimension": "dim-line", "centerline": "centerline", "outline": "outline",
            "thin": "thin-line", "special": "special-line", "title-block": "title-line"}


def hexcolor(c) -> str:
    if c is None:
        return "none"
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v * 255)))) for v in c[:3])


def sub_d(prim: dict, tol: float = 0.05) -> str:
    """按 item 逐子路径生成 d（每个 item 一个 M，其后 L；贝塞尔折线化）。"""
    out = []
    for op, c in prim["it"]:
        pts = C.item_points([op, c])
        if op == "c":
            seq = list(zip(c[0::2], c[1::2]))
            pts = [seq[0]] + C.flatten_bezier(seq[0], seq[1], seq[2], seq[3], tol)
        elif op == "qu":
            # item_points 已给周界序 ul→ur→lr→ll，再回首点闭合（下方补 Z）
            pts = pts + [pts[0]]
        elif op == "re":
            pass
        else:
            seq = list(zip(c[0::2], c[1::2]))
            pts = seq
        if not pts:
            continue
        out.append("M%.3f %.3f" % pts[0])
        out.extend("L%.3f %.3f" % p for p in pts[1:])
        if op in ("re", "qu") or (prim["cp"] and len(pts) > 2):
            out.append("Z")
    return "".join(out)


def local_params(g: dict, x0: float, y0: float, s: float) -> dict:
    """弧/圆/长圆的参数换算到视图局部 mm（x 右、y 下；页角 θ → 局部角 90−θ）。"""
    def lm(px, py):
        return [round((py - y0) / s, 3), round((px - x0) / s, 3)]

    t = g["type"]
    if t == "CIRCLE":
        return {"type": "circle", "cx": lm(g["cx"], g["cy"])[0], "cy": lm(g["cx"], g["cy"])[1],
                "r": round(g["r"] / s, 3), "rms_pt": g["rms"], "frame": "local_mm(x右y下)"}
    if t == "ARC":
        c = lm(g["cx"], g["cy"])
        return {"type": "arc", "cx": c[0], "cy": c[1], "r": round(g["r"] / s, 3),
                "a1": round((90 - g["a1"]) % 360, 2), "a2": round((90 - g["a2"]) % 360, 2),
                "sweep": round(-g["sweep"], 2), "rms_pt": g["rms"],
                "frame": "local_mm(x右y下,角度自+x顺时针)"}
    if t == "OBROUND":
        c1, c2 = lm(*g["c1"]), lm(*g["c2"])
        return {"type": "obround", "r": round(g["r"] / s, 3), "c1": c1, "c2": c2,
                "center_dist": round(g["center_dist"] / s, 3), "w": round(g["w"] / s, 3),
                "total_len": round(g["total_len"] / s, 3),
                "orient": round((90 - g["orient"]) % 360, 2), "rms_pt": g["rms"],
                "frame": "local_mm(x右y下)"}
    return {}


def build(base: str) -> dict:
    pdoc = C.read_json(C.work_path(base, "prims.json"))
    vdoc = C.read_json(C.work_path(base, "views.json"))
    cwd = C.read_json(C.deliverables(base)["crosswalk"])
    if not pdoc or not vdoc or not cwd:
        sys.exit("缺少 prims/views/crosswalk，请先跑 01/02/05 --sheet %s" % base)
    by_i = {p["i"]: p for p in pdoc["prims"]}
    cwv = {v["id"]: v for v in cwd["views"]}
    tdoc = C.read_json(C.work_path(base, "text.json"), {"texts": []})
    texts = tdoc.get("texts") or []
    bound_dim_ids = {d["dim-id"] for v in cwd["views"] for d in v.get("dims") or []}

    meta = pdoc["meta"]
    kept = meta["counts"]["kept"]
    L = []
    L.append('<?xml version="1.0" encoding="UTF-8"?>')
    L.append('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
             'viewBox="0 0 %.3f %.3f" width="%.3f" height="%.3f" '
             'data-base-name="%s" data-page="%d" data-rotation="%s" '
             'data-kept-prims="%d" data-generator="%s">'
             % (C.W_PT, C.H_PT, C.W_PT, C.H_PT, C.esc(base), meta["page"], C.ROTATION,
                kept, C.esc(GENERATOR)))

    # ---- 增强4：metadata 同源镜像（与 MD §1 / 附录A 同份，脚本生成，禁手改）
    import json
    sheet_meta = {
        "base_name": base, "page": meta["page"], "page_rect_pt": meta["page_rect_pt"],
        "rotation": C.ROTATION, "W_pt": C.W_PT, "H_pt": C.H_PT, "pt_per_mm": C.PT_PER_MM,
        "counts": meta["counts"], "layer_semantic": C.LAYER_SEMANTIC,
        "id_system": meta["id_system"], "layering": {
            "policy": "颜色优先 + PDM_Title 拆标题栏 + 逐图 OCG 主导性审计纠偏(D1)",
            "triggers": meta["triggers"],
            "off_palette_note": "五色之外按 OCG 语义归层，无解则 thin 并标 UNMAPPED"},
        "views": [{"id": v["id"], "name": v["name"], "kind": v["kind"],
                   "layout": v["layout"], "n": v["n"], "bbox": v["bbox_all"],
                   "bbox_L": v.get("bbox_L")} for v in vdoc["views"]],
        "title_block": {"bbox_pt": cwd["views"][0]["bbox"] if cwd["views"] else None,
                        "fields": strip_placeholders(tdoc.get("title_block") or {}),
                        "source": tdoc.get("title_block_source") or "待文本恢复/vision 识读"},
        "technical_requirements": strip_placeholders(tdoc.get("technical_requirements") or []),
        "text_recovery": {
            "method": tdoc.get("method"),
            "lines": len(texts),
            "resolved_lines": sum(1 for t in texts if t.get("resolved")),
            "unresolved_lines": sum(1 for t in texts if not t.get("resolved")),
            "labeled_glyphs": (tdoc.get("counts") or {}).get("labeled_glyphs", 0),
            "unk_glyphs": (tdoc.get("counts") or {}).get("unk_glyphs", 0),
            "by_zone": (tdoc.get("counts") or {}).get("by_zone", {}),
            "policy": "SVG 只写**已绑定尺寸**的 <text data-dim-id data-value>（仅"
                      "已绑定者）；未解出的字形不发布字符串、不以占位符冒充内容，其位置由 "
                      "<path data-prim=\"glyph\"> 原样保留，全量行几何见 work/text.json。"},
        "crosswalk": {"formula": cwd["formula"], "scale_sources": cwd["scale_sources"],
                      "views": [{"id": v["id"], "scale": v["scale"],
                                 "scale_source": v["scale_source"], "scale_k": v["scale_k"],
                                 "s_pt_per_mm": v["s_pt_per_mm"], "tx": v["tx"], "ty": v["ty"],
                                 "x0": v["x0"], "y0": v["y0"],
                                 "W_mm": v["W_mm"], "H_mm": v["H_mm"],
                                 "self_check": v["self_check"]["pass"],
                                 "n_dims_bound": v["n_dims_bound"]}
                                for v in cwd["views"]]},
        "pymupdf": meta["pymupdf"], "generator": GENERATOR,
    }
    L.append('<metadata id="sheet-meta"><![CDATA[%s]]></metadata>'
             % json.dumps(sheet_meta, ensure_ascii=False, separators=(",", ":")))

    # ---- 逐层 → 逐视图 → path
    n_path = 0
    n_params = 0
    n_text = 0
    # 已定位但**未发布**为 <text> 的文本行（未解出者），只计数、只进 metadata 摘要
    n_unpublished = sum(1 for t in texts if not t.get("resolved"))
    bound_by_view = defaultdict(list)
    for v in cwd["views"]:
        bound_by_view[v["id"]] = v.get("dims") or []

    for layer in C.LAYERS:
        groups = [(v, [i for i in C.view_prim_ids(v, by_i) if by_i[i[0]]["sem"] == layer])
                  for v in vdoc["views"]]
        groups = [(v, g) for v, g in groups if g]
        if not groups:
            # 该层本图无图元（如某图无红/无双点划线 → special=0）：仍输出空组，
            # 保证「六层齐全含独立 title-block」为可判定的结构事实而非计数巧合。
            L.append('<g data-layer="%s" data-semantic="%s" data-count="0" '
                     'data-empty="true"><!-- 本图该层无图元 --></g>'
                     % (layer, C.esc(C.LAYER_SEMANTIC[layer])))
            continue
        L.append('<g data-layer="%s" data-semantic="%s" data-count="%d">'
                 % (layer, C.esc(C.LAYER_SEMANTIC[layer]),
                    sum(len(g) for _, g in groups)))
        for v, g in groups:
            cw = cwv[v["id"]]
            x0, y0 = cw["x0"], cw["y0"]
            s = cw["s_pt_per_mm"]
            L.append('<g data-view="%s" data-view-name="%s" data-scale="%s" '
                     'data-scale-source="%s" data-bbox="%s" data-bbox-L="%s" '
                     'data-tx="%.3f" data-ty="%.3f" data-s-pt-per-mm="%.6f" data-count="%d">'
                     % (v["id"], C.esc(v["name"]), cw["scale"], cw["scale_source"],
                        ",".join("%.3f" % q for q in v["bbox_all"]),
                        ",".join("%.2f" % q for q in v["bbox_L"]) if v.get("bbox_L") else "",
                        cw["tx"], cw["ty"], s, len(g)))
            for i, pid, _, _ in g:
                p = by_i[i]
                gt = p["g"]["type"]
                dprim = "glyph" if gt == "GLYPH" else (
                    DIM_PRIM.get(p["sem"], p["sem"]) if gt in ("LINE", "POLYLINE")
                    else gt.lower())
                attrs = ['data-prim="%s"' % dprim, 'data-prim-id="%s"' % pid,
                         'data-prim-i="%d"' % i,
                         'data-ocg="%s"' % C.esc(p["ocg"] or ""),
                         'data-color="%s"' % hexcolor(p["c"]),
                         'data-type="%s"' % p["t"]]
                if p.get("note"):
                    attrs.append('data-note="%s"' % C.esc(p["note"]))
                if gt == "GLYPH":
                    attrs.append('data-glyph-tpl="%s"' % p.get("gti", ""))
                    attrs.append('data-glyph-sid="%s"' % p.get("gs", ""))
                    attrs.append('data-glyph-h="%.2f"' % p.get("gl", 0.0))
                if gt in ("ARC", "CIRCLE", "OBROUND"):
                    lp = local_params(p["g"], x0, y0, s)
                    if lp:
                        attrs.append("data-params='%s'"
                                     % json.dumps(lp, ensure_ascii=False,
                                                  separators=(",", ":")))
                        n_params += 1
                style = []
                if p["t"] in ("s", "fs"):
                    style.append('stroke="%s"' % hexcolor(p["c"]))
                    style.append('stroke-width="%.4f"' % p["w"])
                    if p["so"] < 1:
                        style.append('stroke-opacity="%.3f"' % p["so"])
                else:
                    style.append('stroke="none"')
                if p["t"] in ("f", "fs"):
                    style.append('fill="%s"' % hexcolor(p["fl"]))
                    if p["fo"] < 1:
                        style.append('fill-opacity="%.3f"' % p["fo"])
                    if p["eo"]:
                        style.append('fill-rule="evenodd"')
                else:
                    style.append('fill="none"')
                style.append('stroke-linecap="butt"')
                L.append('<path %s d="%s" %s/>' % (" ".join(attrs), sub_d(p), " ".join(style)))
                n_path += 1
            # ---- 增强3：文本恢复 → **只**写已绑定尺寸的 <text>（仅已绑定者）。
            # 未解出的字形不发布字符串：其位置已由 <path data-prim="glyph"> 原样保留，
            # 全量行几何在 work/text.json，故绝不用 '?' 占位符冒充内容污染骨载体。
            for d in bound_by_view[v["id"]]:
                if layer != "dimension":
                    continue
                x, y = d["pos_pt"]
                tr = ' transform="rotate(90 %.2f %.2f)"' % (x, y) if d.get("vert") else ""
                L.append('<text data-dim-id="%s" data-value="%s" data-kind="%s" '
                         'data-conf="%s" x="%.2f" y="%.2f" font-size="%.2f" '
                         'font-family="sans-serif" fill="#00ff00"%s>%s</text>'
                         % (d["dim-id"], C.esc(d["value"]), C.esc(d["kind"]),
                            C.esc(d.get("tpl_conf") or ""), x, y, d.get("h_pt") or 9.9,
                            tr, C.esc(d.get("text") or d["value"])))
                n_text += 1
            L.append('</g>')
        L.append('</g>')
    L.append('</svg>')

    svg = "\n".join(L)
    C.write_text(C.deliverables(base)["svg"], svg)

    gate = C.Gate(base)
    gate.add("SVG path 数 == kept", n_path == kept, "%d == %d" % (n_path, kept))
    gate.add("六层 <g data-layer> 齐全",
             svg.count('data-layer="') == len(C.LAYERS),
             "%d 层：%s" % (svg.count('data-layer="'), C.LAYERS))
    gate.add("无 UNASSIGNED data-view", 'data-view="UNASSIGNED"' not in svg,
             "data-view 组数=%d" % svg.count("<g data-view="))
    gate.add("保持竖放不旋转", 'viewBox="0 0 %.3f %.3f"' % (C.W_PT, C.H_PT) in svg
             and "transform=" not in L[1],
             "根 <svg> 无 transform，viewBox=0 0 %.3f %.3f（页面竖放原样）"
             % (C.W_PT, C.H_PT))
    gate.add("不用 crispEdges", "crispEdges" not in svg, "无 shape-rendering=crispEdges")
    gate.add("metadata CDATA 同源镜像", '<metadata id="sheet-meta"><![CDATA[' in svg,
             "含 counts/layer_semantic/id_system/views/crosswalk/title_block")
    gate.add("弧/圆/长圆 data-params 旁注",
             n_params == sum(1 for p in pdoc["prims"]
                             if p["sem"] != "bg" and p["g"]["type"] in ("ARC", "CIRCLE",
                                                                        "OBROUND")),
             "data-params=%d 个（弧/圆/长圆图元数）" % n_params, required=False)
    gate.add("载体一致性预备：<text> 仅来自 crosswalk 绑定",
             n_text == len(bound_dim_ids),
             "<text>=%d == 绑定 dims=%d；未发布文本行=%d（仅已绑定者，"
             "未解出行不写 <text>）" % (n_text, len(bound_dim_ids), n_unpublished))
    gate.add("占位符不冒充内容(交付 SVG 无 '?' 掩码)",
             svg.count("?") == 2 and "??" not in svg
             and not PLACEHOLDER_TEXT_RE.search(svg),
             "SVG 内 '?' 总数=%d（仅 <?xml …?> 声明的 2 个）；未解出字形位置由 "
             "<path data-prim=\"glyph\"> 保留，不渲染假字符" % svg.count("?"))
    gate.dump(C.work_path(base, "gate_06.json"))

    C.log("=" * 78)
    C.log(gate.report())
    C.log("path=%d data-params=%d text=%d 未发布文本行=%d 层组=%d 视图组=%d 字节=%.1fKB"
          % (n_path, n_params, n_text, n_unpublished, svg.count('data-layer="'),
             svg.count("<g data-view="), len(svg.encode("utf-8")) / 1024))
    C.log("→", C.deliverables(base)["svg"])
    return {"n_path": n_path, "n_params": n_params, "n_text": n_text,
            "n_unpublished_text": n_unpublished, "bytes": len(svg)}


def main(argv):
    C.init(argv)
    for base in C.parse_sheet_arg(argv):
        build(base)


if __name__ == "__main__":
    main(sys.argv[1:])
