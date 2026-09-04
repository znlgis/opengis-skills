# -*- coding: utf-8 -*-
"""07 反向重绘 + 三方互校（方案 §6 步骤 6 / 决策 D7）

交付物 SVG + MD + crosswalk + 源 PDF →
    work/validate.json + <base>_反向重绘验证.png

D7：解析交付 SVG 的 `d` 折线 → PIL 按 scale=2.0（≈144DPI，4767×6740）绘制 →
与 `fitz` 同分辨率渲染叠合 → 2px 膨胀后算 recall/precision/F1（门禁 recall≥0.99），
严格 IoU 仅记录不作门禁；不走 svglib/reportlab（缺 cairo）。
三方互校：PDF 原图 ↔ prims.json 几何 ↔ SVG data-params（换算回页面 pt 后比对），
弧/圆残差 rms 门禁 ≤0.1pt；载体一致性 = SVG `<text>` 的 (dim-id,data-value) 集合
== MD 绑定 dims 集合。
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

SCALE = 2.0            # 反向重绘分辨率（≈144DPI）
DILATE_PX = 2          # 容差膨胀半径
INK_TH = 250           # 灰度 < 该值视为有墨
RECALL_MIN = 0.99
RMS_MAX = 0.1          # pt

PATH_RE = re.compile(r"<path\b([^>]*?)/>", re.S)
ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')
ATTR_JSON_RE = re.compile(r"([\w:-]+)='([^']*)'")
TEXT_RE = re.compile(r"<text\b([^>]*?)>([^<]*)</text>", re.S)
NUM_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
MD_DIM_RE = re.compile(r"^\|\s*`(V\d+-D\d+)`\s*\|\s*([-\d.]+)\s*\|", re.M)


def parse_svg(txt: str) -> tuple:
    """从交付 SVG 读回 path 列表与 <text> 集合（不回读中间产物，真「反向」）。"""
    paths, texts = [], []
    for m in PATH_RE.finditer(txt):
        a = dict(ATTR_RE.findall(m.group(1)))
        a.update(ATTR_JSON_RE.findall(m.group(1)))
        d = a.get("d", "")
        pts, cur = [], None
        for tok in re.split(r"([MLZ])", d):
            if tok in ("M", "L"):
                cur = tok
            elif tok == "Z":
                cur = None
            elif tok.strip() and cur:
                ns = [float(x) for x in NUM_RE.findall(tok)]
                for k in range(0, len(ns) - 1, 2):
                    pts.append((ns[k], ns[k + 1]))
        paths.append({"attrs": a, "pts": pts,
                      "w": float(a.get("stroke-width", 0) or 0),
                      "stroke": a.get("stroke", "none"),
                      "fill": a.get("fill", "none")})
    for m in TEXT_RE.finditer(txt):
        a = dict(ATTR_RE.findall(m.group(1)))
        texts.append({"dim-id": a.get("data-dim-id"), "value": a.get("data-value"),
                      "kind": a.get("data-kind"), "x": float(a.get("x", 0)),
                      "y": float(a.get("y", 0)), "content": m.group(2)})
    return paths, texts


def redraw(paths: list, size_px: tuple):
    """按交付 SVG 的 d 与线宽在 PIL 上重绘（scale=2.0，竖放不旋转，与源同坐标系）。"""
    from PIL import Image, ImageDraw
    img = Image.new("L", size_px, 255)
    dr = ImageDraw.Draw(img)
    n_seg = 0
    for p in paths:
        pts = p["pts"]
        if not pts:
            continue
        sc = [(x * SCALE, y * SCALE) for x, y in pts]
        w = max(1, int(round(p["w"] * SCALE))) if p["stroke"] != "none" else 0
        if w:
            if len(sc) == 1:
                dr.point(sc[0], fill=0)
            else:
                dr.line(sc, fill=0, width=w, joint="curve")
            n_seg += len(sc) - 1
        if p["fill"] not in ("none", ""):
            if len(sc) >= 3:
                dr.polygon(sc, fill=0)
    return img, n_seg


def dilate(img, r: int = DILATE_PX):
    from PIL import ImageFilter
    return img.filter(ImageFilter.MaxFilter(2 * r + 1))


def metrics(orig, svg) -> dict:
    import numpy as np
    a = np.asarray(orig, dtype=np.uint8) < INK_TH      # 源有墨
    b = np.asarray(svg, dtype=np.uint8) < INK_TH       # 重绘有墨
    from PIL import Image
    ad = np.asarray(dilate(Image.fromarray((a * 255).astype(np.uint8))),
                    dtype=np.uint8) > 127
    bd = np.asarray(dilate(Image.fromarray((b * 255).astype(np.uint8))),
                    dtype=np.uint8) > 127
    n_a, n_b = int(a.sum()), int(b.sum())
    rec = int((a & bd).sum()) / n_a if n_a else 1.0
    pre = int((b & ad).sum()) / n_b if n_b else 1.0
    f1 = 2 * rec * pre / (rec + pre) if (rec + pre) else 0.0
    iou = int((a & b).sum()) / int((a | b).sum()) if int((a | b).sum()) else 0.0
    return {"recall": round(rec, 6), "precision": round(pre, 6), "f1": round(f1, 6),
            "iou_strict": round(iou, 6), "orig_ink_px": n_a, "redraw_ink_px": n_b,
            "missed_px": n_a - int((a & bd).sum()), "extra_px": n_b - int((b & ad).sum()),
            "tolerance": {"dilate_px": DILATE_PX, "ink_threshold": INK_TH,
                          "note": "recall/precision 用 2px 膨胀容差；iou_strict 仅记录"}}, a, b, ad, bd


def save_proof(a, b, ad, bd, out_png: str) -> dict:
    """验证图：R=漏画(源有墨而重绘容差内无)、G=多画、B=双方命中；scale=2.0 原分辨率。"""
    import numpy as np
    from PIL import Image
    h, w = a.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    both = a & b
    rgb[..., 0] = np.where(a & ~bd, 255, 0)
    rgb[..., 1] = np.where(b & ~ad, 255, 0)
    rgb[..., 2] = np.where(both, 255, 0)
    orange = (a & ~b) & bd                 # 源有墨、重绘未直接命中但在 2px 容差内
    rgb[orange] = [255, 128, 0]
    Image.fromarray(rgb, "RGB").save(out_png)
    return {"file": os.path.basename(out_png), "px": [w, h], "scale": SCALE,
            "legend": "R=漏画 G=多画 B=双方命中 橙=容差内补齐",
            "n_both": int(both.sum()), "n_orange": int(orange.sum())}


def params_roundtrip(base: str, paths: list) -> dict:
    """三方互校：SVG data-params(视图局部 mm) → 页面 pt ↔ prims.json 几何。"""
    pdoc = C.read_json(C.work_path(base, "prims.json"))
    cwd = C.read_json(C.deliverables(base)["crosswalk"])
    by_i = {p["i"]: p for p in pdoc["prims"]}
    cwv = {v["id"]: v for v in cwd["views"]}
    errs_c, errs_r, errs_a, n = [], [], [], 0
    n_params = 0
    # 逐 path 解析：所属视图由 data-prim-id 前缀得到
    for p in paths:
        a = p["attrs"]
        if "data-params" not in a:
            continue
        n_params += 1
        pid = a.get("data-prim-id", "")
        vid = pid.split("-P")[0]
        cw = cwv.get(vid)
        i = int(a.get("data-prim-i", -1))
        g = by_i.get(i, {}).get("g")
        if not cw or not g:
            continue
        try:
            prm = json.loads(a["data-params"])
        except Exception:
            continue
        x0, y0, s = cw["x0"], cw["y0"], cw["s_pt_per_mm"]

        def to_pt(lx, ly):        # 局部 mm(x右y下) → 页面 pt
            return (x0 + ly * s, y0 + lx * s)
        n += 1
        if prm["type"] in ("circle", "arc"):
            cx, cy = to_pt(prm["cx"], prm["cy"])
            errs_c.append(math.hypot(cx - g["cx"], cy - g["cy"]))
            errs_r.append(abs(prm["r"] * s - g["r"]))
            if prm["type"] == "arc":
                a1 = (90 - prm["a1"]) % 360
                sw = -prm["sweep"]
                d1 = abs((a1 - g["a1"] + 180) % 360 - 180)
                d2 = abs((sw - g["sweep"] + 180) % 360 - 180)
                errs_a.append(max(d1, d2) * math.pi / 180 * g["r"])   # 角度差折算弧长 pt
        elif prm["type"] == "obround":
            c1 = to_pt(*prm["c1"])
            c2 = to_pt(*prm["c2"])
            errs_c.append(max(math.hypot(c1[0] - g["c1"][0], c1[1] - g["c1"][1]),
                              math.hypot(c2[0] - g["c2"][0], c2[1] - g["c2"][1])))
            errs_r.append(abs(prm["r"] * s - g["r"]))

    def rms(v):
        return round(math.sqrt(sum(x * x for x in v) / len(v)), 6) if v else 0.0
    allerr = errs_c + errs_r + errs_a
    return {"n_data_params": n_params, "n_checked": n,
            "rms_center_pt": rms(errs_c), "rms_radius_pt": rms(errs_r),
            "rms_angle_as_arc_pt": rms(errs_a), "rms_all_pt": rms(allerr),
            "max_all_pt": round(max(allerr), 6) if allerr else 0.0,
            "fit_rms_from_01": C.read_json(C.work_path(base, "extract_audit.json"), {})
            .get("arc_rms")}


def build(base: str) -> dict:
    import pymupdf
    import numpy as np
    from PIL import Image
    sd = C.sheet_dir(base)
    svg_p = C.deliverables(base).get("svg") or os.path.join(sd, base + ".svg")
    md_p = C.deliverables(base).get("md") or os.path.join(sd, base + "-可复现图纸描述.md")
    proof_p = C.deliverables(base).get("redraw") or os.path.join(sd, base + "_反向重绘验证.png")
    if not (os.path.exists(svg_p) and os.path.exists(md_p)):
        sys.exit("缺少 SVG/MD 交付物，请先跑 06/04 --sheet %s" % base)
    svg_txt = C.read_text(svg_p)
    md_txt = C.read_text(md_p)
    paths, texts = parse_svg(svg_txt)
    pdoc = C.read_json(C.work_path(base, "prims.json"))
    cwd = C.read_json(C.deliverables(base)["crosswalk"])
    idx = C.read_json(C.work_path(base, "md_prims_index.json"), {"index": {}})
    meta = pdoc["meta"]
    kept = meta["counts"]["kept"]

    # ---- 计数对账链
    chain = {"drawings": meta["counts"]["drawings"], "bg": meta["counts"]["bg"],
             "kept": kept, "svg_path": len(paths), "md_index": len(idx["index"]),
             "svg_data_prim_id_unique": len({p["attrs"].get("data-prim-id") for p in paths})}
    chain["ok"] = (chain["drawings"] - chain["bg"] == kept == chain["svg_path"]
                   == chain["md_index"] == chain["svg_data_prim_id_unique"])

    # ---- 反向重绘
    doc = pymupdf.open(C.pdf_path(base))
    page = doc[0]
    W, H = page.rect.width, page.rect.height
    size_px = (int(math.ceil(W * SCALE)), int(math.ceil(H * SCALE)))
    # 必须显式要灰度：PyMuPDF 默认 colorspace=DeviceRGB（pm.n==3），
    # 若把 RGB samples 当作 "L" 解码会得到乱图（recall 假降至 ~0.06）。
    pm = page.get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), alpha=False,
                         colorspace=pymupdf.csGRAY)
    assert pm.n == 1, "pixmap 非单通道(n=%d)，不能按 L 解码" % pm.n
    orig = Image.frombytes("L", (pm.width, pm.height), pm.samples)
    doc.close()
    svg_img, n_seg = redraw(paths, (pm.width, pm.height))
    m, a, b, ad, bd = metrics(orig, svg_img)
    proof = save_proof(a, b, ad, bd, proof_p)

    # ---- 三方互校
    rt = params_roundtrip(base, paths)

    # ---- 载体一致性：SVG <text> 集合 == MD 绑定 dims 集合
    svg_set = {(t["dim-id"], float(t["value"])) for t in texts if t["dim-id"]}
    md_set = {(m2.group(1), float(m2.group(2))) for m2 in MD_DIM_RE.finditer(md_txt)}
    cw_set = {(d["dim-id"], float(d["value"])) for v in cwd["views"] for d in (v.get("dims") or [])}
    consist = {"svg_n": len(svg_set), "md_n": len(md_set), "crosswalk_n": len(cw_set),
               "svg_eq_md": svg_set == md_set, "svg_eq_crosswalk": svg_set == cw_set,
               "md_eq_crosswalk": md_set == cw_set,
               "only_svg": sorted(svg_set - md_set)[:10],
               "only_md": sorted(md_set - svg_set)[:10],
               "consistent": bool(svg_set == md_set == cw_set)}

    # ---- 绿层值集合 vs MD dims 集合（记录，非门禁）
    tdoc = C.read_json(C.work_path(base, "text.json"), {})
    green_vals = {float(t["value"]) for t in (tdoc.get("texts") or [])
                  if t.get("value") is not None and t.get("conf") != "low"}
    dim_vals = {v for _, v in md_set}
    green = {"n_recovered_numeric": len(green_vals), "n_bound": len(dim_vals),
             "bound_subset_of_recovered": bool(dim_vals <= green_vals),
             "unbound_numeric": len(green_vals - dim_vals),
             "bind_rate": round(len(dim_vals) / len(green_vals), 4) if green_vals else None,
             "note": "绑定率仅记录，非门禁（守方案 §1「41–43% 非门禁、不臆造定位」）"}

    out = {"base_name": base, "scale": SCALE, "size_px": [pm.width, pm.height],
           "page_rect_pt": [round(W, 3), round(H, 3)],
           "n_svg_segments": n_seg, "chain": chain, "redraw": m, "proof": proof,
           "roundtrip": rt, "carrier_consistency": consist, "green_layer": green,
           "pymupdf": meta["pymupdf"], "pil": __import__("PIL").__version__}
    C.write_json(C.work_path(base, "validate.json"), out)

    gate = C.Gate(base)
    gate.add("计数对账链 drawings−bg==kept==SVG path==MD 索引", chain["ok"], str(chain))
    gate.add("反向重绘 recall≥%.2f" % RECALL_MIN, m["recall"] >= RECALL_MIN,
             "recall=%.6f precision=%.6f f1=%.6f（2px 膨胀容差）漏画=%dpx/%dpx"
             % (m["recall"], m["precision"], m["f1"], m["missed_px"], m["orig_ink_px"]))
    gate.add("弧/圆三方互校 rms≤%.1fpt" % RMS_MAX, rt["rms_all_pt"] <= RMS_MAX,
             "rms_all=%.6fpt max=%.6fpt（center=%.6f radius=%.6f 角度折算=%.6f，n=%d/%d）"
             % (rt["rms_all_pt"], rt["max_all_pt"], rt["rms_center_pt"], rt["rms_radius_pt"],
                rt["rms_angle_as_arc_pt"], rt["n_checked"], rt["n_data_params"]))
    gate.add("载体一致性 SVG text == MD dims == crosswalk", consist["consistent"],
             "svg=%d md=%d crosswalk=%d 仅svg=%s 仅md=%s"
             % (consist["svg_n"], consist["md_n"], consist["crosswalk_n"],
                consist["only_svg"] or "无", consist["only_md"] or "无"))
    gate.add("交付 SVG 无占位符文本(<text> 必带 data-dim-id)",
             all(t["dim-id"] for t in texts) and "??" not in svg_txt
             and svg_txt.count("?") == 2,
             "<text>=%d 个均为已绑定尺寸（仅已绑定者）；未解出字形"
             "不写假字符，SVG 内 '?' 总数=%d（仅 <?xml …?> 声明的 2 个）"
             % (len(texts), svg_txt.count("?")))
    gate.add("严格 IoU（仅记录，非门禁）", True,
             "iou_strict=%.6f（细线抗锯齿差异所致，不作门禁）" % m["iou_strict"],
             required=False)
    gate.add("绿层绑定率（仅记录，非门禁）", True, str(green), required=False)
    gate.add("验证图已产出", os.path.exists(proof_p),
             "%s %s" % (proof["file"], proof["px"]))
    gate.dump(C.work_path(base, "gate_07.json"))
    C.log("=" * 78)
    C.log(gate.report())
    C.log("chain:", chain)
    C.log("redraw:", {k: v for k, v in m.items() if k != "tolerance"})
    C.log("roundtrip:", rt)
    C.log("→", proof_p)
    return out


def main(argv):
    C.init(argv)
    for base in C.parse_sheet_arg(argv):
        build(base)


if __name__ == "__main__":
    main(sys.argv[1:])
