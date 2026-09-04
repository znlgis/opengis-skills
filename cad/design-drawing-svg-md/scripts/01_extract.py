# -*- coding: utf-8 -*-
"""01 矢量提取 + 分层（方案 §6 步骤 1 / 决策 D1）

PDF → work/prims.json + work/extract_audit.json
门禁：drawings − bg == kept；六层齐全含独立 title-block；基线图逐层对账方案 §11 基线。
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

def _cfg() -> dict:
    """config 运行时快照（common.init 后可用）；未 init 时为空 dict。"""
    return getattr(C, "_CFG", None) or {}


def _baseline_layers() -> dict | None:
    """从 config.baseline 构造逐层基线期望值（阶段 2 泛化）。

    口径：total=baseline.drawings、逐层=baseline.layers、kept=Σlayers、bg=total−kept。
    config 无 baseline.drawings/layers 时返回 None，调用方跳过基线对账。
    缺 baseline.drawings 时只对账 layers，不臆测 bg（bg 置 None 跳过）。
    """
    b = _cfg().get("baseline") or {}
    layers = b.get("layers") or {}
    drawings = b.get("drawings")
    if drawings is None and not layers:
        return None
    kept = sum(layers.values()) if layers else None
    total = drawings
    exp = {"total": total, "kept": kept,
           "bg": (total - kept) if (total is not None and kept is not None) else None}
    exp.update({L: layers.get(L, 0) for L in C.LAYERS})
    return exp


def extract(base: str) -> dict:
    import pymupdf
    C.ensure_dirs(base)
    doc = pymupdf.open(C.pdf_path(base))
    page = doc[0]
    raw = page.get_drawings()
    ocgs = {str(k): (v or {}).get("name", "") for k, v in (doc.get_ocgs() or {}).items()}

    prims = []
    for i, it in enumerate(raw):
        prim = {
            "i": i,
            "t": it.get("type"),
            "w": round(float(it.get("width") or 0.0), 4),
            "c": list(it["color"]) if it.get("color") is not None else None,
            "fl": list(it["fill"]) if it.get("fill") is not None else None,
            "fo": round(float(it.get("fill_opacity") if it.get("fill_opacity") is not None else 1.0), 3),
            "so": round(float(it.get("stroke_opacity") if it.get("stroke_opacity") is not None else 1.0), 3),
            "ocg": it.get("layer") or "",
            "cp": bool(it.get("closePath")),
            "eo": bool(it.get("even_odd")),
            "r": [round(v, 3) for v in (it["rect"].x0, it["rect"].y0,
                                        it["rect"].x1, it["rect"].y1)],
            "it": [C.norm_item(x) for x in it.get("items") or []],
        }
        prim["c"] = list(C.rgb_key(prim["c"])) if prim["c"] is not None else None
        prim["fl"] = list(C.rgb_key(prim["fl"])) if prim["fl"] is not None else None
        prims.append(prim)

    # 字形优先判定（D3）：字符"0"等本身即圆，必须先判字形再判几何
    glyphs, gstats, gtable = C.glyph_flags(prims)
    for p in prims:
        gl = glyphs.get(p["i"])
        if gl:
            p["gl"] = gl["gh"]
            p["gv"] = 1 if gl["vert"] else 0
            p["gt"] = gl["tpl"]
            p["gti"] = gl["tid"]
            p["gs"] = gl["sid"]
        p["g"] = C.classify_geom(p, glyph=bool(gl))

    audit = C.audit_layers(prims)
    triggers = audit["triggers"]
    counts = Counter()
    for p in prims:
        sem, note = C.assign_layer(p, triggers)
        p["sem"] = sem
        if note:
            p["note"] = note
        counts[sem] += 1

    kept = sum(v for k, v in counts.items() if k != "bg")
    page_rect = [round(v, 3) for v in (page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1)]

    meta = {
        "base_name": base,
        "pdf": C.pdf_path(base),
        "page": 1,
        "page_rect_pt": page_rect,
        "page_rotation_src": page.rotation,
        "counts": {
            "drawings": len(prims),
            "bg": counts.get("bg", 0),
            "kept": kept,
            "by_layer": {L: counts.get(L, 0) for L in C.LAYERS},
        },
        "line_widths_pt": sorted({p["w"] for p in prims}),
        "ocg_names": sorted({n for n in ocgs.values() if n}),
        "layer_semantic": C.LAYER_SEMANTIC,
        "id_system": {"view": "V{nn}", "prim": "V{nn}-P{kkk}", "dim": "V{nn}-D{kk}",
                      "balloon": "V{nn}-B{kk}"},
        "rotation": C.ROTATION,
        "triggers": triggers,
        "glyph_stats": gstats,
        "pymupdf": pymupdf.__doc__.split(":")[0].strip() if pymupdf.__doc__ else "",
    }

    C.write_json(C.work_path(base, "prims.json"),
                 {"meta": meta, "audit": audit, "prims": prims}, indent=None)
    C.write_json(C.work_path(base, "extract_audit.json"), {"meta": meta, "audit": audit})
    C.write_json(C.work_path(base, "glyph_templates.json"),
                 {"base_name": base, "stats": gstats, "templates": gtable})

    # ---- 门禁
    gate = C.Gate(base)
    gate.add("计数对账 drawings−bg==kept",
             len(prims) - counts.get("bg", 0) == kept,
             "%d − %d == %d" % (len(prims), counts.get("bg", 0), kept))
    # 六层齐全：只要求**该图实际存在源**的层非空（如某图无红色也无双点划线/剖面线
    # OCG → special 合法为 0）；title-block 必须有源且非空（PDM_Title 在各图均存在）。
    have_color = {k.split("|")[1] for k in audit["cross"]}
    have_ocg = {k.split("|")[0] for k in audit["cross"]}
    src_layer = {C.COLOR_LAYER[c] for c in have_color if c in C.COLOR_LAYER}
    for lay, ocgs in C.OCG_STRONG.items():
        if have_ocg & ocgs:
            src_layer.add(lay)
    src_layer.add("title-block")
    missing = [L for L in sorted(src_layer) if counts.get(L, 0) == 0]
    absent = [L for L in C.LAYERS if L not in src_layer]
    gate.add("六层齐全(含独立 title-block)", not missing,
             "源存在的层缺空=%s | 无源而不存在的层=%s | %s"
             % (missing or "无", absent or "无", {L: counts.get(L, 0) for L in C.LAYERS}))
    unmapped = sum(1 for p in prims if "UNMAPPED" in (p.get("note") or ""))
    gate.add("无 UNMAPPED 图元", unmapped == 0, "UNMAPPED=%d" % unmapped, required=False)
    if base == C.baseline_sheet():
        exp = _baseline_layers()
        if exp:
            diffs = []
            for k, v in exp.items():
                if v is None:
                    continue  # 基线未提供该值（如缺 drawings 时 bg/total），不对账不臆测
                got = len(prims) if k == "total" else (counts.get("bg", 0) if k == "bg"
                                                       else (kept if k == "kept" else counts.get(k, 0)))
                if got != v:
                    diffs.append("%s:%s!=%s" % (k, got, v))
            gate.add("方案 §11 基线对账(%s)" % base, not diffs, "; ".join(diffs) or "逐项吻合")
    for layer, on in triggers.items():
        if on:
            gate.add("OCG 纠偏触发:%s" % layer, True,
                     json.dumps(audit["strong"][layer], ensure_ascii=False), required=False)
    gate.dump(C.work_path(base, "gate_01.json"))

    C.log("=" * 78)
    C.log(gate.report())
    C.log("layer counts:", {L: counts.get(L, 0) for L in C.LAYERS}, "| bg", counts.get("bg", 0))
    C.log("triggers:", triggers)
    C.log("line widths(pt):", meta["line_widths_pt"][:8], "…共", len(meta["line_widths_pt"]))
    gt = Counter(p["g"]["type"] for p in prims)
    C.log("geom types:", dict(gt.most_common()))
    rms = [p["g"]["rms"] for p in prims if p["g"]["type"] in ("ARC", "CIRCLE", "OBROUND")]
    if rms:
        C.log("弧/圆拟合 rms: n=%d 均方根=%.4fpt max=%.4fpt"
              % (len(rms), math.sqrt(sum(v * v for v in rms) / len(rms)), max(rms)))
    C.log("字高分布(pt):", gstats["heights"], "| 竖排", gstats["vert"])
    C.log("字形: 候选池=%d 模板=%d(保留%d, ≥3:%d) 已标记=%d | 模板复现top=%s"
          % (gstats["pool"], gstats["templates"], gstats["templates_kept"],
             gstats["templates_ge3"], gstats["flagged"], gstats["tpl_top"]))
    C.log("→", C.work_path(base, "prims.json"))
    doc.close()
    return {"meta": meta, "audit": audit, "gate": gate.dump()}


def main(argv):
    C.init(argv)
    for base in C.parse_sheet_arg(argv):
        if not os.path.exists(C.pdf_path(base)):
            sys.exit("找不到 PDF: %s" % C.pdf_path(base))
        extract(base)


if __name__ == "__main__":
    main(sys.argv[1:])
