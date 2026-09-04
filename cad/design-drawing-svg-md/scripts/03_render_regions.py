# -*- coding: utf-8 -*-
"""03 回正裁切图 + 跨图字形模板接触表（方案 §6 步骤 3 视觉识读来源 / 决策 D3）

PDF + views.json → work/regions/*.png          （逐视图回正高清紧裁切、整页总览、
                                                 标题栏专切、技术要求区专切）
     glyph_templates.json → output/_glyph_dict/templates/<sid>.png + tpl_<sheet>.json
     --contact-sheets     → output/_glyph_dict/templates.json + contact_sheet_*.png/.json

回正：page.set_rotation(270)（ROTATION="ccw90"），横向坐标 (X_L, Y_L) = (y_p, W − x_p)，
故竖放 bbox [x0,y0,x1,y1] 的横向裁切框 = Rect(y0, W−x1, y1, W−x0)。
门禁：每张 png 尺寸 == 裁切框×scale（四舍五入）、视图数覆盖齐全。
"""
from __future__ import annotations

import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

REGION_PX = 1800.0        # 视图裁切图长边目标像素
OVERVIEW_SCALE = 1.5      # 整页总览（≈108DPI；反向重绘另按 scale=2.0 于 07 内渲染）
PATCH_PX = 112            # 单字形贴片边长（px），矢量约 10pt → scale≈11（≈4× 高清的再放大）
SHEET_COLS = 12           # 接触表列数
SHEET_ROWS = 12           # 接触表行数（每张 144 模板）
CELL_LABEL = 28           # 接触表每格下方标签高度（px）


def _cfg() -> dict:
    """config 运行时快照（common.init 后可用）；未 init 时为空 dict。"""
    return getattr(C, "_CFG", None) or {}


def _latin_font(size: int):
    """config fonts.latin 加载拉丁字体；未配置或加载失败回退默认位图字体。"""
    from PIL import ImageFont
    p = (_cfg().get("fonts") or {}).get("latin")
    if not p:
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()


def land_rect(bbox):
    """竖放 bbox → 横向(回正) fitz.Rect 参数。"""
    x0, y0, x1, y1 = bbox
    return (y0, C.W_PT - x1, y1, C.W_PT - x0)


def render_regions(base: str) -> dict:
    import pymupdf
    vdoc = C.read_json(C.work_path(base, "views.json"))
    if not vdoc:
        sys.exit("缺少 views.json，请先跑 02 --sheet %s" % base)
    C.ensure_dirs(base)
    rdir = os.path.join(C.work_dir(base), "regions")
    doc = pymupdf.open(C.pdf_path(base))
    page = doc[0]
    page.set_rotation(270)

    made = []
    # 整页总览
    pm = page.get_pixmap(matrix=pymupdf.Matrix(OVERVIEW_SCALE, OVERVIEW_SCALE), alpha=False)
    p = os.path.join(rdir, "_overview.png")
    pm.save(p)
    made.append({"file": "_overview.png", "kind": "overview", "px": [pm.width, pm.height],
                 "scale": OVERVIEW_SCALE, "clip": [0, 0, round(page.rect.width, 2),
                                                   round(page.rect.height, 2)]})

    def crop(name, bbox, kind, extra=None, target_px=REGION_PX):
        r = land_rect(bbox)
        w, h = r[2] - r[0], r[3] - r[1]
        if w <= 0.5 or h <= 0.5:
            return None
        k = max(0.6, min(24.0, target_px / max(w, h)))
        clip = pymupdf.Rect(*r)
        pm = page.get_pixmap(matrix=pymupdf.Matrix(k, k), clip=clip, alpha=False)
        fn = "%s.png" % name
        pm.save(os.path.join(rdir, fn))
        rec = {"file": fn, "kind": kind, "px": [pm.width, pm.height], "scale": round(k, 4),
               "bbox_portrait": [round(v, 3) for v in bbox],
               "clip_landscape": [round(v, 3) for v in r],
               "expect_px": [int(round(w * k)), int(round(h * k))]}
        if extra:
            rec.update(extra)
        made.append(rec)
        return rec

    for v in vdoc["views"]:
        nm = v["id"] if v["id"] != "V00" else "V00_title"
        crop(nm, v["bbox_all"], "view", {"view": v["id"], "name": v["name"],
                                         "n": v["n"], "by_layer": v["by_layer"]})
    # 标题栏专切（tb_bbox）
    if vdoc.get("tb_bbox"):
        crop("_title_block", vdoc["tb_bbox"], "title_block", {"px_target": 2000.0}, 2000.0)

    # 技术要求/注释区专切：注释类 OCG 的字形簇 bbox。
    # 实测（基线图）注释文字被尺寸线/剖面线切碎，单簇常 <8 字，故分级取框：
    #   ① 取**字数最多**的簇（≥4 字）；② 否则退回全部注释字形的合并 bbox
    #      （多列并排时框会偏大，但保证不漏字，交给 vision 识读）。
    by_i = {p["i"]: p for p in C.read_json(C.work_path(base, "prims.json"))["prims"]}
    notes = [by_i[i] for i, p in by_i.items()
             if p["g"]["type"] == "GLYPH" and (p["ocg"] or "") in C.OCG_NOTES]
    notes_box, notes_how = None, "无注释字形"
    if notes:
        rects = [p["r"] for p in notes]
        grp = defaultdict(list)
        for k, c in enumerate(C.cluster_bbox(rects, 30.0)):
            grp[c].append(k)
        big = max(grp.values(), key=len)
        if len(big) >= 4:
            b = list(C.merge_rects([rects[k] for k in big]))
            notes_how = "最大注释簇(%d字/共%d簇)" % (len(big), len(grp))
        else:
            b = list(C.merge_rects(rects))
            notes_how = "全部注释字形合并(%d字,最大簇仅%d)" % (len(rects), len(big))
        b = [b[0] - 20, b[1] - 20, b[2] + 20, b[3] + 20]
        notes_box = crop("_tech_notes", b, "tech_notes", {"n_glyphs": len(notes),
                                                          "how": notes_how})
    doc.close()

    bad = [m for m in made if "expect_px" in m
           and (abs(m["px"][0] - m["expect_px"][0]) > 2 or abs(m["px"][1] - m["expect_px"][1]) > 2)]
    n_views = len(vdoc["views"])
    # PyMuPDF 的位图边长对 pt×scale 一律**向上取整**，故容差取 +2px（而非相等）。
    ow, oh = made[0]["px"]
    ew, eh = page_w() * OVERVIEW_SCALE, page_h() * OVERVIEW_SCALE
    gate = C.Gate(base)
    gate.add("整页总览尺寸正确", 0 <= ow - ew <= 2 and 0 <= oh - eh <= 2,
             "实得%s 期望[%d,%d]±2 scale=%s"
             % (made[0]["px"], int(ew), int(eh), OVERVIEW_SCALE))
    gate.add("视图裁切图齐全", sum(1 for m in made if m["kind"] == "view") == n_views,
             "%d/%d" % (sum(1 for m in made if m["kind"] == "view"), n_views))
    gate.add("png 尺寸==裁切框×scale", not bad,
             "异常=%s" % ([m["file"] for m in bad] or "无"))
    gate.add("标题栏专切存在", bool(vdoc.get("tb_bbox")) is
             any(m["kind"] == "title_block" for m in made),
             "tb_bbox=%s" % (vdoc.get("tb_bbox"),))
    gate.add("技术要求区专切", notes_box is not None,
             "注释字形=%d 取框=%s 专切=%s"
             % (len(notes), notes_how, notes_box["file"] if notes_box else "未定位"),
             required=False)
    gate.dump(C.work_path(base, "gate_03.json"))
    C.write_json(C.work_path(base, "regions.json"),
                 {"base_name": base, "rotation": C.ROTATION, "region_px": REGION_PX,
                  "overview_scale": OVERVIEW_SCALE, "regions": made})
    C.log("=" * 78)
    C.log(gate.report())
    for m in made:
        C.log("  %-18s %-12s px=%-14s scale=%-7s %s"
              % (m["file"], m["kind"], m["px"], m["scale"], m.get("view", "")))
    return {"made": made, "gate": gate.dump()}


def page_w():
    return C.H_PT


def page_h():
    return C.W_PT


# ---------------------------------------------------------------- 字形贴片与接触表


PATCH_PADS = [0.18, 0.6, 1.5]   # 贴片外扩系数逐级重试（墨迹自检）
INK_MIN = 1e-5                  # 归一化墨迹下限（低于此视为空白贴片）


def _ink(pm) -> float:
    """灰度位图的归一化墨迹（1=全黑）；用于贴片空白自检。"""
    import numpy as np
    a = np.frombuffer(pm.samples, dtype=np.uint8)
    return float(1.0 - a.mean() / 255.0)


def render_glyph_patches(base: str) -> dict:
    """逐图渲染字形模板贴片（按 sid 跨图去重），并落 tpl_<sheet>.json 供合并。

    贴片一律**重渲不跳过已存在**（旧版本裁切逻辑遗留的空白 png 会被覆盖），
    并对每张做墨迹自检：空白则按 PATCH_PADS 逐级放大外扩重试，仍空则计入
    blank 并报门禁（贴片非空白率）。不空白才能保证 vision 标注有依据。
    """
    import pymupdf
    gt = C.read_json(C.work_path(base, "glyph_templates.json"))
    if not gt:
        sys.exit("缺少 glyph_templates.json，请先跑 01 --sheet %s" % base)
    prims = {p["i"]: p for p in C.read_json(C.work_path(base, "prims.json"))["prims"]}
    pdir = os.path.join(C.GLYPH_DIR, "templates")
    os.makedirs(pdir, exist_ok=True)
    doc = pymupdf.open(C.pdf_path(base))
    page = doc[0]
    page.set_rotation(270)
    tpl_out, n_new, blank, retries = {}, 0, [], Counter()
    for tid, t in gt["templates"].items():
        p = prims.get(t["sample"])
        if not p or not t["kept"]:
            continue
        sid = t["sid"]
        fn = os.path.join(pdir, sid + ".png")
        r = land_rect(p["r"])
        w, h = max(r[2] - r[0], 0.5), max(r[3] - r[1], 0.5)
        mx = max(w, h)
        cx0, cy0 = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        ink, pad = 0.0, PATCH_PADS[0]
        for pi, pad in enumerate(PATCH_PADS):
            half = mx / 2 + pad * mx + 0.6     # 方形贴片：字形居中、保持长宽比
            clip = pymupdf.Rect(cx0 - half, cy0 - half, cx0 + half, cy0 + half)
            k = PATCH_PX / (2 * half)
            pm = page.get_pixmap(matrix=pymupdf.Matrix(k, k), clip=clip, alpha=False)
            ink = _ink(pm)
            if ink >= INK_MIN:
                retries[pi] += 1
                break
            retries["blank"] += 1
        pm.save(fn)
        if ink < INK_MIN:
            blank.append({"sid": sid, "tid": tid, "sample": t["sample"],
                          "bbox": p["r"], "ocg": t["ocg"]})
        tpl_out[tid] = {"sid": sid, "n": t["n"], "gh": t["gh"], "vert": t["vert"],
                        "ocg": t["ocg"], "n_items": t["n_items"], "sample": t["sample"],
                        "sample_bbox": p["r"], "sheet": base,
                        "ink": round(ink, 5), "pad": pad}
        n_new += 1
    doc.close()
    C.write_json(os.path.join(C.GLYPH_DIR, "tpl_%s.json" % C.sanitize(base)),
                 {"sheet": base, "stats": gt["stats"], "templates": tpl_out})
    rate = (n_new - len(blank)) / n_new if n_new else 1.0
    gate = C.Gate(base)
    gate.add("贴片非空白率≥95%", rate >= 0.95,
             "%d/%d 非空白（rate=%.4f）pad重试=%s 空白=%s"
             % (n_new - len(blank), n_new, rate, dict(retries),
                [b["sid"] for b in blank[:5]] or "无"))
    gate.dump(C.work_path(base, "gate_03b_patch.json"))
    C.log("[%s] 字形模板 kept=%d 渲染贴片=%d 非空白=%.1f%% pad重试=%s → %s"
          % (base, len(tpl_out), n_new, rate * 100, dict(retries), pdir))
    C.log(gate.report())
    return {"kept": len(tpl_out), "new": n_new, "blank": blank, "rate": rate}


def build_contact_sheets(per_sheet: int = SHEET_COLS * SHEET_ROWS) -> dict:
    """合并各图模板（按 sid 去重）→ templates.json + 接触表分片 + 清单。"""
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(C.GLYPH_DIR, exist_ok=True)
    merged = {}
    for fn in sorted(os.listdir(C.GLYPH_DIR)):
        if not (fn.startswith("tpl_") and fn.endswith(".json")):
            continue
        d = C.read_json(os.path.join(C.GLYPH_DIR, fn))
        for tid, t in d["templates"].items():
            m = merged.setdefault(t["sid"], {
                "sid": t["sid"], "gh": t["gh"], "vert": t["vert"], "ocg": t["ocg"],
                "n_items": t["n_items"], "n": 0, "sheets": Counter(), "sample": None,
                "sample_sheet": None, "tids": {}})
            m["n"] += t["n"]
            m["sheets"][t["sheet"]] += t["n"]
            m["tids"][t["sheet"]] = tid
            if m["sample"] is None:
                m["sample"], m["sample_sheet"] = t["sample"], t["sheet"]
    for m in merged.values():
        m["sheets"] = dict(m["sheets"])
        m["n_sheets"] = len(m["sheets"])
    # 排序：跨图复现优先（sheet 数、总次数），再按字高
    order = sorted(merged.values(), key=lambda m: (-m["n_sheets"], -m["n"], m["gh"], m["sid"]))
    for k, m in enumerate(order):
        m["gid"] = "G%04d" % (k + 1)
    font = _latin_font(13)

    pdir = os.path.join(C.GLYPH_DIR, "templates")
    # 幂等清理孤儿贴片：签名口径一旦变化（如竖排归正式修正），部分旧 sid 不再产生，
    # 遗留 png 会使 templates/*.png 数与 templates.json 的模板数不符（齐套门禁误判）。
    live = {m["sid"] for m in order}
    stale = [f for f in (os.listdir(pdir) if os.path.isdir(pdir) else [])
             if f.endswith(".png") and f[:-4] not in live]
    for f in stale:
        os.remove(os.path.join(pdir, f))
    n_sheets = int(math.ceil(len(order) / per_sheet))
    made = []
    for si in range(n_sheets):
        chunk = order[si * per_sheet:(si + 1) * per_sheet]
        cw, ch = PATCH_PX, PATCH_PX + CELL_LABEL
        img = Image.new("RGB", (cw * SHEET_COLS, ch * SHEET_ROWS), "white")
        dr = ImageDraw.Draw(img)
        man = []
        for j, m in enumerate(chunk):
            cx, cy = (j % SHEET_COLS) * cw, (j // SHEET_COLS) * ch
            fp = os.path.join(pdir, m["sid"] + ".png")
            if os.path.exists(fp):
                t = Image.open(fp).convert("RGB")
                t = t.resize((PATCH_PX - 8, PATCH_PX - 8), Image.LANCZOS)
                img.paste(t, (cx + 4, cy + 4))
            dr.rectangle([cx, cy, cx + cw - 1, cy + ch - 1], outline="#cccccc")
            lab = "%s n=%d h=%.1f %s %s" % (m["gid"], m["n"], m["gh"],
                                            "V" if m["vert"] else "H", m["ocg"][:6])
            dr.text((cx + 3, cy + PATCH_PX + 1), lab, fill="black", font=font)
            dr.text((cx + 3, cy + PATCH_PX + 14), "sheets=%d %s"
                    % (m["n_sheets"], m["sid"][:8]), fill="#555555", font=font)
            man.append({"cell": j, "row": j // SHEET_COLS, "col": j % SHEET_COLS,
                        "gid": m["gid"], "sid": m["sid"], "n": m["n"],
                        "n_sheets": m["n_sheets"], "gh": m["gh"], "vert": m["vert"],
                        "ocg": m["ocg"], "sheets": m["sheets"],
                        "bbox_px": [cx + 4, cy + 4, cx + PATCH_PX - 4, cy + PATCH_PX - 4]})
        fn = "contact_sheet_%02d.png" % (si + 1)
        img.save(os.path.join(C.GLYPH_DIR, fn))
        C.write_json(os.path.join(C.GLYPH_DIR, fn.replace(".png", ".json")),
                     {"sheet_file": fn, "index": si + 1, "of": n_sheets,
                      "cell_px": [PATCH_PX, PATCH_PX + CELL_LABEL],
                      "cols": SHEET_COLS, "rows": SHEET_ROWS,
                      "n_cells": len(chunk), "cells": man,
                      "ask": "请逐格给出该字符（数字/字母/汉字/符号）；不确定写 UNK。"
                             "输出严格 JSON：{\"gid\":\"字符\"}"})
        made.append({"file": fn, "n": len(chunk), "px": [img.width, img.height]})
    stats = {
        "templates_total": len(order),
        "by_nsheets": dict(Counter(m["n_sheets"] for m in order)),
        "ge2_sheets": sum(1 for m in order if m["n_sheets"] >= 2),
        "n_total_instances": sum(m["n"] for m in order),
        "heights": dict(Counter(round(m["gh"], 1) for m in order).most_common(12)),
        "contact_sheets": n_sheets,
        "patch_px": PATCH_PX, "cell_px": [PATCH_PX, PATCH_PX + CELL_LABEL],
    }
    C.write_json(os.path.join(C.GLYPH_DIR, "templates.json"),
                 {"stats": stats, "templates": {m["gid"]: m for m in order}})
    C.write_json(os.path.join(C.GLYPH_DIR, "dict_stats.json"),
                 {"stats": stats, "sheets": made,
                  "labels_file": "glyph_labels.json",
                  "label_policy": "只标 n_sheets≥2 的模板 + 单例中落在标题栏/技术要求区者；"
                                  "其余标 UNK 入 unclear，不臆造"})
    C.log("=" * 78)
    C.log("字形字典：合并模板=%d（跨图≥2 图=%d）实例=%d 接触表=%d 张（每张%d格）"
          % (stats["templates_total"], stats["ge2_sheets"], stats["n_total_instances"],
             n_sheets, per_sheet))
    C.log("按跨图数分布:", stats["by_nsheets"])
    C.log("清理孤儿贴片=%d（当前 sid=%d，贴片 png=%d）"
          % (len(stale), len(live), len([f for f in os.listdir(pdir) if f.endswith('.png')])))
    for m in made:
        C.log("  %-24s n=%-4d px=%s" % (m["file"], m["n"], m["px"]))
    return stats


LABEL_COLS, LABEL_ROWS = 5, 4        # 标注用大字接触表：每张 20 格
LABEL_CELL, LABEL_LAB = 220, 58      # 格边长与下方标签高度（px）
LABEL_MIN_N, LABEL_MIN_GH = 2, 5.0   # 只标复现≥2 且字高≥5pt 的模板（D3 策略）


def build_label_sheets(limit: int = 180) -> dict:
    """为人工/视觉标注产出**大格高对比**分片表（D3：只标复现≥2 的模板）。

    与 contact_sheet_* 的区别：每格 220px（而非 112）、每张 20 格（而非 144）、
    统一灰度化 + 自动对比拉伸使笔画一律为黑（原 PDF 里黄/青字在白底上对比极低），
    并按**复现次数降序**取前 limit 个，使标注预算优先花在覆盖实例最多的字符上。
    """
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    tdoc = C.read_json(os.path.join(C.GLYPH_DIR, "templates.json"), {"templates": {}})
    if not tdoc.get("templates"):
        sys.exit("缺少 templates.json，请先跑 03 --contact-sheets")
    cand = [m for m in tdoc["templates"].values()
            if m["n"] >= LABEL_MIN_N and m["gh"] >= LABEL_MIN_GH]
    cand.sort(key=lambda m: (-m["n"], m["gh"], m["sid"]))
    cand = cand[:limit]
    font = _latin_font(20)
    pdir = os.path.join(C.GLYPH_DIR, "templates")
    per = LABEL_COLS * LABEL_ROWS
    n_sheets = int(math.ceil(len(cand) / per))
    made, covered = [], 0
    for si in range(n_sheets):
        chunk = cand[si * per:(si + 1) * per]
        covered += sum(m["n"] for m in chunk)
        cw, chh = LABEL_CELL, LABEL_CELL + LABEL_LAB
        img = Image.new("RGB", (cw * LABEL_COLS, chh * LABEL_ROWS), "white")
        dr = ImageDraw.Draw(img)
        man = []
        for j, m in enumerate(chunk):
            cx, cy = (j % LABEL_COLS) * cw, (j // LABEL_COLS) * chh
            fp = os.path.join(pdir, m["sid"] + ".png")
            if os.path.exists(fp):
                t = Image.open(fp).convert("L")
                t = ImageOps.autocontrast(t, cutoff=1)          # 笔画→黑、底→白
                t = t.resize((LABEL_CELL - 12, LABEL_CELL - 12), Image.LANCZOS)
                img.paste(t, (cx + 6, cy + 6))
            dr.rectangle([cx, cy, cx + cw - 1, cy + chh - 1], outline="#999999")
            dr.text((cx + 6, cy + LABEL_CELL + 2), "%s" % m["gid"], fill="black", font=font)
            dr.text((cx + 6, cy + LABEL_CELL + 26), "n=%d h=%.1f %s"
                    % (m["n"], m["gh"], "WIDE" if m["vert"] else "TALL"),
                    fill="black", font=font)
            man.append({"cell": j, "row": j // LABEL_COLS, "col": j % LABEL_COLS,
                        "gid": m["gid"], "sid": m["sid"], "n": m["n"], "gh": m["gh"],
                        "vert": m["vert"], "ocg": m["ocg"],
                        "n_sheets": m["n_sheets"], "sheets": m["sheets"],
                        "bbox_px": [cx + 6, cy + 6, cx + LABEL_CELL - 6,
                                    cy + LABEL_CELL - 6]})
        fn = "label_sheet_%02d.png" % (si + 1)
        img.save(os.path.join(C.GLYPH_DIR, fn))
        C.write_json(os.path.join(C.GLYPH_DIR, fn.replace(".png", ".json")),
                     {"sheet_file": fn, "index": si + 1, "of": n_sheets,
                      "cols": LABEL_COLS, "rows": LABEL_ROWS, "cell_px": [cw, chh],
                      "n_cells": len(chunk), "cells": man,
                      "ask": "逐格给出字符（数字/字母/汉字/符号）；几何碎片或不确定写 UNK。"
                             "输出严格 JSON {\"gid\":\"字符\"}"})
        made.append({"file": fn, "n": len(chunk), "px": [img.width, img.height]})
    stats = {"candidates": len(cand), "selected": len(cand), "sheets": n_sheets,
             "per_sheet": per, "instances_covered": covered,
             "instances_total": sum(m["n"] for m in tdoc["templates"].values()),
             "coverage": round(covered / max(1, sum(
                 m["n"] for m in tdoc["templates"].values())), 4),
             "policy": "n≥%d 且字高≥%gpt，按复现次数降序取前 %d 个；其余入 UNK/unclear"
                       % (LABEL_MIN_N, LABEL_MIN_GH, limit)}
    C.write_json(os.path.join(C.GLYPH_DIR, "label_sheets.json"),
                 {"stats": stats, "sheets": made})
    C.log("标注表：%d 张（每张%d格）选中模板=%d 覆盖实例=%d/%d(%.1f%%)"
          % (n_sheets, per, len(cand), covered, stats["instances_total"],
             stats["coverage"] * 100))
    for m in made:
        C.log("  %-22s n=%-3d px=%s" % (m["file"], m["n"], m["px"]))
    return stats


def main(argv):
    C.init(argv)
    if "--contact-sheets" in argv:
        build_contact_sheets()
        return
    if "--label-sheets" in argv:
        lim = 180
        if "--limit" in argv:
            lim = int(argv[argv.index("--limit") + 1])
        build_label_sheets(lim)
        return
    for base in C.parse_sheet_arg(argv):
        render_regions(base)
        render_glyph_patches(base)


if __name__ == "__main__":
    main(sys.argv[1:])
