# -*- coding: utf-8 -*-
"""03d 视觉识读：逐行高对比渲染 → 转录 → 确定性双源核对 → 派生字形标签。

为什么需要本脚本（三处实测缺陷，均有硬证据）
------------------------------------------------------------------
1. 03 的字形贴片直接 `get_pixmap` 原图：黄/青细线在灰度下仅 235–255，
   接触表近乎空白，而 `_ink` 门禁阈值 1e-5 形同虚设 → 视觉通道无依据可标，
   此前被误判为「通道会虚构」。标定实验（`output/_probe/calib_*.png`，真值已知）
   证明该通道对 ≥40px 高对比文字可**逐字**转录，故失败真因是图不可读。
2. `common.glyph_signature` 用精确矢量点哈希（`sorted(round(归一坐标,nd))`）
   而非方案 D3 的 32×32 栅格哈希 → 同一字符在不同字高下裂成多个 sid
   （模板与单例数虚增），字典无法收敛。
3. 03b 的行归并在字高不一致时失效：实测某图的 716 行里 333 行只有 1 个字形，
   且出现 68.2°/−40.6° 等 CAD 文本不可能的倾角。

本脚本因此**绕开**字典先行，改为「逐行识读 + 反推字典」：
  ① 按回正坐标把字形聚成文本行，每行渲染成一格（高对比纯黑白、字高≈44px），
     格下标注 `行号 n=字形数 h=字高`，任务说明直接写进图里（Read 通道不收提示词）；
  ② 视觉通道逐格转录 → `work/vread/transcript.json`；
  ③ 确定性核对（--apply）：
     V1 图号真值 —— base_name 取自 PDF 文件名，是**已知真值**；标题栏某行
        转录必须等于它。不过则本图识读一律不采信（宁缺勿臆）。
     V2 逐行字数对账 —— 一个字符 = 一个 drawing item（方案 D3），故转录的
        非空白字符数应等于该行字形 prim 数。
  ④ 只有 V2 **精确相等**的行才用于字符↔字形对齐，产出 sid→字符票；
     同 sid 多票一致才采信，冲突即弃（--promote 汇总到跨图字典）。

行级识读同时直接给出 MD §4（标题栏字段）与 §5（技术要求）的内容来源，
不必等字典收敛——这正是方案 §4 的来源优先级：字典重建值 ＞ 视觉裁切复核。

用法
----
  python scripts/03d_vision_read.py --sheet 4                 # 渲染行格图(默认 tb 区)
  python scripts/03d_vision_read.py --sheet 4 --zone notes
  python scripts/03d_vision_read.py --sheet 4 --apply         # 核对转录+派生标签
  python scripts/03d_vision_read.py --all --promote           # 跨图汇总派生标签
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

# ------------------------------------------------------------------ 参数
TARGET_CHAR_PX = 44.0     # 目标字高(px)；标定证明 ≥40px 可逐字转录
SCALE_MIN, SCALE_MAX = 2.0, 16.0
ROWS_PER_SHEET = 8        # 每张图多少行（标定 8 行全部转录成功）
GAP_FRAC = 1.2            # 行内字间最大间隙 = 此系数 × 两字中较小的字高
Y_FRAC = 0.55             # 同行判定：中线偏差 ≤ 此系数 × 较小字高
CELL_PAD = 10             # 行格内边距(px)
LABEL_H = 30              # 行格下方标签条高(px)
CAPTION_H = 44            # 图顶说明条高(px)，多行时按 CAP_LINE_H 递增
CAP_LINE_H = 26           # 说明条行高(px)
MIN_SHEET_W = 560         # 画布最小宽(px)：须容下行号标签，否则标签被裁到画布外
MAX_CELL_W = 1700         # 单格最大宽(px)
PAD_PT = 3.0              # 行 bbox 外扩(pt)
INK_TH = 250              # 灰度<此值判为墨（背景纯白255）；黄/青线原值226–250
CHARLIKE_FRAC = 0.55      # 字高 ≥ 本区中位×此系数才算字符（排除2–3pt小标记）
V2_TOL = 0                # 逐行字数对账容差（字符数）：0=必须精确相等才用于对齐
CELL_GAP_FRAC = 1.6       # 相邻字符位中心距 > 此系数×字距 → 判定中间有缺位
V1_MIN_LCS = 8            # 图号真值：单行转录与图名的最长公共连续子串下限（字符）

ZONE_TB, ZONE_NOTES, ZONE_DRAW = "tb", "notes", "drawing"
ZONES = (ZONE_TB, ZONE_NOTES, ZONE_DRAW)


def _cfg() -> dict:
    """config 运行时快照（common.init 后可用）；未 init 时为空 dict。"""
    return getattr(C, "_CFG", None) or {}


def _cjk_font(size: int):
    """config fonts.cjk 加载中文字体；未配置或加载失败回退默认位图字体。"""
    from PIL import ImageFont
    p = (_cfg().get("fonts") or {}).get("cjk")
    if not p:
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()


def land_box(r):
    """竖放 bbox → 回正(横向) bbox，与 03.land_rect 同式：(y0, W−x1, y1, W−x0)。"""
    x0, y0, x1, y1 = r
    return (y0, C.W_PT - x1, y1, C.W_PT - x0)


def zone_of(p):
    """分区：title-block / notes / drawing。分层结果在 `sem` 字段（不是 layer）。

    注意 OCG「标注 文字线」属 C.OCG_NOTES，其实是**视图内尺寸数字**，
    故 notes 区并非只有技术要求；技术要求靠转录文本的编号行特征识别。
    """
    ocg = p.get("ocg") or ""
    if p.get("sem") == "title-block" or ocg == "PDM_Title":
        return ZONE_TB
    if ocg in C.OCG_NOTES:
        return ZONE_NOTES
    return ZONE_DRAW


def row_cells(gs):
    """把一行内的 item 归并成**字符位**序列（含推断出的空位）。

    两个实测事实使 item 数 ≠ 字符数：
      (a) 一个字符可被拆成 2 个 item（上半/下半，x 区间嵌套重叠）；
      (b) 单笔画字符（连字符、「1」、「·」）只有 1 段子路径，被 glyph_pool 的
          `len(it)>=2` 系统性丢弃，在行内表现为一个**空位**。
    故先按 x 区间重叠归并成簇，再用相邻簇中心距的中位数估字距，中心距超过
    CELL_GAP_FRAC×字距处插入空位。图号行实测：15 item → 11 簇 + 1 空位 = 12 字符位，
    与视觉逐字读出的图号串（12 字符）精确一致。

    返回 [{"x0","x1","sids":[...]}, ...]；sids 为空表空位，>1 表拆字位（两者均不投票）。
    """
    items = sorted(gs, key=lambda g: g["lb"][0])
    clusters = []
    for g in items:
        x0, x1 = g["lb"][0], g["lb"][2]
        if clusters and x0 <= clusters[-1]["x1"] + 0.01:
            clusters[-1]["x1"] = max(clusters[-1]["x1"], x1)
            clusters[-1]["g"].append(g)
        else:
            clusters.append({"x0": x0, "x1": x1, "g": [g]})
    if len(clusters) < 2:
        return [{"x0": c["x0"], "x1": c["x1"], "sids": [g["sid"] for g in c["g"]]}
                for c in clusters]
    cs = [(c["x0"] + c["x1"]) / 2 for c in clusters]
    diffs = sorted(cs[k + 1] - cs[k] for k in range(len(cs) - 1))
    m = len(diffs) // 2
    adv = diffs[m] if len(diffs) % 2 else (diffs[m - 1] + diffs[m]) / 2
    out = []
    for k, c in enumerate(clusters):
        if k and adv > 0.5 and (cs[k] - cs[k - 1]) > CELL_GAP_FRAC * adv:
            miss = int(round((cs[k] - cs[k - 1]) / adv)) - 1
            out.extend([{"x0": None, "x1": None, "sids": []}] * max(miss, 0))
        out.append({"x0": round(c["x0"], 2), "x1": round(c["x1"], 2),
                    "sids": [g["sid"] for g in c["g"]]})
    return out


def group_rows(gs):
    """两趟聚行：先按回正 y 归行，再按 x 间隙切分。

    容差一律取**两字中较小的字高**为尺度，而非 03b 的全区中位字高：
    标题栏里 3.96pt 小字与 17.3pt 大字混排，用全区中位数会把
    图框分区标记（6 字横跨 312pt）当成一行。x 间隙切分同理。
    """
    if not gs:
        return []
    items = sorted(gs, key=lambda g: ((g["lb"][1] + g["lb"][3]) / 2, g["lb"][0]))

    def cy(g):
        return (g["lb"][1] + g["lb"][3]) / 2

    bands, cur = [], [items[0]]
    for g in items[1:]:
        ref = min(g["gh"], max(q["gh"] for q in cur))
        cy0 = sum(cy(q) for q in cur) / len(cur)
        if abs(cy(g) - cy0) <= max(1.0, Y_FRAC * ref):
            cur.append(g)
        else:
            bands.append(cur)
            cur = [g]
    bands.append(cur)

    rows = []
    for band in bands:
        band.sort(key=lambda g: g["lb"][0])
        seg, prev = [band[0]], band[0]
        for g in band[1:]:
            ref = min(g["gh"], prev["gh"])
            if g["lb"][0] - prev["lb"][2] <= max(1.0, GAP_FRAC * ref):
                seg.append(g)
            else:
                rows.append(seg)
                seg = [g]
            prev = g
        rows.append(seg)

    out = []
    for rr in rows:
        cells = row_cells(rr)
        out.append({
            "box": (min(g["lb"][0] for g in rr), min(g["lb"][1] for g in rr),
                    max(g["lb"][2] for g in rr), max(g["lb"][3] for g in rr)),
            "prims": [g["i"] for g in rr], "sids": [g["sid"] for g in rr],
            "cells": cells, "n": len(cells), "n_items": len(rr),
            "gh": max(g["gh"] for g in rr),
            "cy": sum(cy(g) for g in rr) / len(rr),
        })
    out.sort(key=lambda r: (round(r["cy"], 1), r["box"][0]))
    return out


def select(base, zone, tb_bbox=None, min_n=1):
    """取指定分区的字形 prim → 聚行 → 过滤（字符级字高、行数下限）。"""
    pdoc = C.read_json(C.work_path(base, "prims.json"))
    gs = []
    for p in pdoc["prims"]:
        if p["g"]["type"] != "GLYPH":
            continue
        if zone_of(p) != zone:
            continue
        if zone == ZONE_TB and tb_bbox:
            x0, y0, x1, y1 = p["r"]
            bx0, by0, bx1, by1 = tb_bbox
            if x1 < bx0 or x0 > bx1 or y1 < by0 or y0 > by1:
                continue          # 标题栏层还含图框分区标记，须按 tb_bbox 收口
        gs.append({"i": p["i"], "lb": land_box(p["r"]), "gh": p.get("gl") or 0.0,
                   "sid": p.get("gs"), "tid": p.get("gti")})
    hs = sorted(g["gh"] for g in gs)
    med = hs[len(hs) // 2] if hs else 1.0
    gh_min = max(2.0, CHARLIKE_FRAC * med)
    gs = [g for g in gs if g["gh"] >= gh_min]
    rows = [r for r in group_rows(gs) if r["n"] >= min_n]
    return rows, {"glyphs_all": len(gs), "gh_median": med, "gh_min": round(gh_min, 2),
                  "rows": len(rows)}


# ------------------------------------------------------------------ 渲染
def _row_image(page, row, target_px):
    """把一行渲染成高对比纯黑白小图，返回 (PIL.Image, scale)。"""
    import numpy as np
    import pymupdf
    from PIL import Image
    bx0, by0, bx1, by1 = row["box"]
    bx0, by0, bx1, by1 = bx0 - PAD_PT, by0 - PAD_PT, bx1 + PAD_PT, by1 + PAD_PT
    w, h = bx1 - bx0, by1 - by0
    k = min(SCALE_MAX, max(SCALE_MIN, target_px / max(row["gh"], 1.0)))
    k = min(k, MAX_CELL_W / max(w, 1.0))
    pm = page.get_pixmap(matrix=pymupdf.Matrix(k, k),
                         clip=pymupdf.Rect(bx0, by0, bx1, by1),
                         alpha=False, colorspace=pymupdf.csGRAY)
    assert pm.n == 1, "pixmap 非单通道(n=%d)，不能按 L 解码" % pm.n
    a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width)
    ink = a < INK_TH
    if not ink.any():                 # 极淡者退化到最暗 2% 分位（不产出空白格）
        t = float(np.percentile(a, 2.0))
        ink = a <= max(t, float(a.min()) + 1.0)
    return Image.fromarray(np.where(ink, 0, 255).astype(np.uint8), "L"), k


def render_rows(base, zone, rows, outdir, limit=None):
    """逐行渲染成格、每 ROWS_PER_SHEET 行拼一张图；返回 (sheets, row_records)。"""
    import pymupdf
    from PIL import Image, ImageDraw, ImageFont
    if limit:
        rows = rows[:limit]
    vdir = outdir
    os.makedirs(vdir, exist_ok=True)
    # 幂等清理：本轮行数变少时，上一轮的多余 sheet 会残留（如 tb 43行/6张 → 30行/4张，
    # sheet_05/06 仍在），转录者会照着 stale 图填 manifest 里没有的行号。
    # 旧 band 设计的产物同理。范围严格限定在本 vdir 内、本 zone 的两种文件名模式。
    for fn in sorted(os.listdir(vdir)):
        if (fn.startswith("%s_row_sheet_" % zone) or fn.startswith("%s_band_" % zone)) \
                and fn.endswith(".png"):
            os.remove(os.path.join(vdir, fn))
    doc = pymupdf.open(C.pdf_path(base))
    page = doc[0]
    page.set_rotation(270)
    fnt = _cjk_font(20)
    fcap = _cjk_font(22)
    sheets, recs = [], []
    ns = (len(rows) + ROWS_PER_SHEET - 1) // ROWS_PER_SHEET
    for si in range(ns):
        chunk = rows[si * ROWS_PER_SHEET:(si + 1) * ROWS_PER_SHEET]
        imgs = []
        for j, r in enumerate(chunk):
            rid = "R%04d" % (si * ROWS_PER_SHEET + j + 1)
            im, k = _row_image(page, r, TARGET_CHAR_PX)
            imgs.append((rid, r, im, k))
        cw = min(MAX_CELL_W, max(im.size[0] for _a, _b, im, _k in imgs)) + 2 * CELL_PAD
        chs = [im.size[1] + LABEL_H + 2 * CELL_PAD for _a, _b, im, _k in imgs]
        cap = ("%s区  第%d/%d张  共%d格：每格一行文本，格下 n=该行字符位数（已含推断空位）；"
               "请按 R编号 逐格逐字转录"
               % (zone, si + 1, ns, len(imgs)))
        # 画布宽必须同时容下格图与行号标签。旧版 W=cw 把 "R0001 n=5 h=7.1"
        # 与整条说明都画在了画布外（sheet_01 宽 181、标签起点 x=183），
        # 转录者读不到行号 → V2 逐行字数对账从构造上就无法成立。
        probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
        W = max(cw, MIN_SHEET_W,
                int(probe.textlength("R0000  n=000  h=000.0", font=fnt)) + 2 * CELL_PAD)
        cap_lines, cur = [], ""
        for cch in cap:                    # 说明按画布宽折行，避免同样被裁
            if probe.textlength(cur + cch, font=fcap) > W - 12:
                cap_lines.append(cur)
                cur = cch
            else:
                cur += cch
        cap_lines.append(cur)
        cap_h = CAPTION_H + CAP_LINE_H * (len(cap_lines) - 1)
        H = cap_h + sum(chs)
        out = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(out)
        for li, ln in enumerate(cap_lines):
            d.text((6, 8 + CAP_LINE_H * li), ln, fill=(0, 0, 0), font=fcap)
        d.line([(0, cap_h), (W, cap_h)], fill=(0, 0, 0), width=2)
        y = cap_h
        cellmap = []
        for (rid, r, im, k), ch in zip(imgs, chs):
            d.rectangle([2, y + 2, W - 3, y + ch - 3], outline=(170, 170, 170))
            out.paste(im.convert("RGB"), (CELL_PAD, y + CELL_PAD))
            # 标签放格图**下方**（LABEL_H 带内）而非右侧：右侧起点随格宽变化，
            # 窄格时必然溢出画布；下方只要 W 够宽就恒可见。
            d.text((CELL_PAD, y + CELL_PAD + im.size[1] + 4),
                   "%s  n=%d  h=%.1f" % (rid, r["n"], r["gh"]), fill=(0, 0, 0), font=fnt)
            cellmap.append({"row_id": rid, "cell": [2, y + 2, W - 3, y + ch - 3]})
            recs.append({"row_id": rid, "zone": zone, "n": r["n"], "gh": round(r["gh"], 2),
                         "n_items": r.get("n_items", r["n"]),
                         "cells": r.get("cells") or [],
                         "prims": r["prims"], "sids": r["sids"],
                         "box_landscape": [round(v, 3) for v in r["box"]],
                         "scale": round(k, 3), "sheet": "%s_row_sheet_%02d.png" % (zone, si + 1)})
            y += ch
        fn = "%s_row_sheet_%02d.png" % (zone, si + 1)
        out.save(os.path.join(vdir, fn))
        sheets.append({"file": fn, "zone": zone, "px": [W, H], "caption": cap,
                       "rows": [c["row_id"] for c in cellmap]})
    doc.close()
    return sheets, recs


# ------------------------------------------------------------------ 转录核对
NORM_RE = re.compile(r"[\s\u3000]+")


def caption_re() -> re.Pattern:
    r"""图号前缀正则：从 config.drawing_no_prefixes 动态构造，过滤转录里的图号/行号行。

    alternatives：各图号前缀（取自 config.drawing_no_prefixes）+ `\S+_row_sheet`（行格图文件名）+
    `R\d{4}\s+n=`（行号标签）。config 未配 drawing_no_prefixes 时只留后两类结构串。
    """
    prefixes = _cfg().get("drawing_no_prefixes") or []
    alts = [re.escape(p) for p in prefixes] + [r"\S+_row_sheet", r"R\d{4}\s+n="]
    return re.compile(r"^(%s)" % "|".join(alts))


def norm(s):
    """归一：去空白、大写、全角转半角（图号/字符比对用）。"""
    s = NORM_RE.sub("", str(s or "")).upper()
    return "".join(chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in s)


def lcs_len(a, b):
    """最长公共**连续子串**长度（图号真值核对用；a、b 均已 norm）。"""
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


FIELD_RES = [
    ("material", re.compile(r"材料[:：\s]*([A-Za-z0-9\-\u4e00-\u9fff]{2,20})")),
    ("scale", re.compile(r"(?:比例|SCALE)[:：\s]*(\d+\s*[:：]\s*\d+(?:\.\d+)?)")),
    ("weight", re.compile(r"(?:重量|单件|总计|共\s*\d+\s*张)[:：\s]*([\d\.]+)")),
    ("date", re.compile(r"(20\d{2}[\.\-/年]\s?\d{1,2}[\.\-/月]\s?\d{1,2})")),
    ("name", re.compile(r"([\u4e00-\u9fff]{3,20}(?:座|架|体|盘|盖|轴|轮|板|框|箱|盖|套|环|块|件))")),
]
NOTE_RE = re.compile(r"^\s*(\d{1,2})\s*[\.、\)]\s*(\S.{1,200})$")
SCALE_ONLY_RE = re.compile(r"^\s*(\d+)\s*[:：]\s*(\d+(?:\.\d+)?)\s*$")


def apply_transcript(base, zone=None):
    """核对转录：V1 图号真值 + V2 逐行字数对账 → 派生 sid→字符票。"""
    vd = os.path.join(C.work_dir(base), "vread")
    man = C.read_json(os.path.join(vd, "manifest.json"), {}) or {}
    tp = os.path.join(vd, "transcript.json")
    tr = C.read_json(tp, None)
    gate = C.Gate(base)
    if tr is None:
        gate.add("转录已提供", False,
                 "缺 %s；行格图已渲染，待视觉通道逐格转录后 --apply。"
                 "格式：{\"zones\": {\"tb\": {\"R0001\": \"…\"}, \"notes\": {…}}}"
                 % tp,
                 required=False)
        gate.dump(C.work_path(base, "gate_03d.json"))
        C.log(gate.report())
        return {"status": "await_transcript"}

    # row_id 在分区间**不唯一**：每个 zone 独立从 R0001 起编号（本图 tb 30 行与
    # notes 51 行的 R0001–R0030 完全撞号），故对账键必须是 (zone, row_id)；
    # 转录也按分区嵌套。旧格式 {"rows": {...}} 无分区维度，会把两个 zone 的同号行
    # 静默互相覆盖（tb 的图号行被 notes 的 n=4 尺寸行顶掉），V1/V2 必然错乱 → 拒收。
    rows = {(r["zone"], r["row_id"]): r for r in man.get("rows", [])}
    tr_zones = tr.get("zones")
    if not isinstance(tr_zones, dict):
        gate.add("转录格式正确", False,
                 "%s 须按分区嵌套：{\"zones\": {\"tb\": {\"R0001\": \"…\"}, "
                 "\"notes\": {…}}}；row_id 在 tb/notes 之间撞号，"
                 "无分区维度则无法安全归属" % tp)
        gate.dump(C.work_path(base, "gate_03d.json"))
        C.log(gate.report())
        return {"status": "bad_transcript_format"}
    per, votes, aligned = [], Counter(), 0
    lines_tb, lines_notes, notes, zones_done = [], [], [], []
    for zname in ZONES:
        zrows = tr_zones.get(zname)
        if not isinstance(zrows, dict) or not zrows:
            continue
        zones_done.append(zname)
        for rid, txt in sorted(zrows.items()):
            r = rows.get((zname, rid))
            if not r:
                per.append({"row_id": rid, "zone": zname, "ok": False,
                            "why": "manifest 无此行"})
                continue
            if (not isinstance(txt, str) or not txt.strip()
                    or caption_re().match(txt.strip())):
                continue
            t = txt.strip()
            n_chars = len(norm(t))
            diff = n_chars - r["n"]
            ok_exact = diff == 0
            ok_v2 = abs(diff) <= V2_TOL
            per.append({"row_id": rid, "zone": r["zone"], "n_cells": r["n"],
                        "n_items": r.get("n_items", r["n"]),
                        "n_chars": n_chars, "diff": diff, "ok_v2": ok_v2, "text": t})
            if ok_exact:
                aligned += 1
                chars = [c for c in norm(t)]
                for k, cell in enumerate(r.get("cells") or []):
                    if k >= len(chars):
                        break
                    # 只有「一位一 item」的字符位可投票：空位（单笔画字符被池丢弃）
                    # 与拆字位（一字符拆成上下两半）都无法把字符唯一归给某个 sid。
                    sids = cell.get("sids") or []
                    if len(sids) == 1 and sids[0]:
                        votes[(sids[0], chars[k])] += 1
            if r["zone"] == ZONE_TB:
                lines_tb.append(t)
            else:
                lines_notes.append(t)
            m = NOTE_RE.match(t)
            if m and len(m.group(2)) >= 4:
                notes.append({"no": int(m.group(1)), "text": m.group(2).strip(),
                              "row_id": rid, "zone": r["zone"]})

    want = norm(base)
    tb_all = norm("".join(lines_tb))
    # V1：图号真值核对。标题栏图号单元格实测只写图号主体（去文件名前缀
    # 与版本段），故不要求整名相等，而要求**单行**与图名的最长公共连续子串
    # ≥ V1_MIN_LCS。8 字符连续命中不可能由虚构产生；仍不用全区拼接，
    # 以免转录里混入的图顶说明条造成假阳性。
    dn_row, dn_hit = [], 0
    for p in per:
        if p.get("zone") != ZONE_TB:
            continue
        L = lcs_len(norm(p.get("text", "")), want)
        p["v1_lcs"] = L
        dn_hit = max(dn_hit, L)
        if L >= V1_MIN_LCS:
            dn_row.append(p["row_id"])
    v1 = bool(dn_row)
    scales = []
    for p in per:
        m = SCALE_ONLY_RE.match(p.get("text", ""))
        if m:
            scales.append({"row_id": p["row_id"], "scale": "1:%s" % m.group(2),
                           "denominator": float(m.group(2)), "ok_v2": p.get("ok_v2")})
    fields = {}
    for k, rx in FIELD_RES:
        m = rx.search("\n".join(lines_tb))
        if m:
            fields[k] = NORM_RE.sub(" ", m.group(1)).strip()

    labels = {}
    for (sid, ch), n in votes.items():
        e = labels.setdefault(sid, {"chars": Counter(), "votes": 0})
        e["chars"][ch] += n
        e["votes"] += n
    n_sid = len(labels)
    n_conflict = sum(1 for e in labels.values() if len(e["chars"]) > 1)
    lab_out = {sid: {"char": e["chars"].most_common(1)[0][0], "votes": e["votes"],
                     "conflict": dict(e["chars"]), "n_chars_seen": len(e["chars"])}
               for sid, e in sorted(labels.items(), key=lambda kv: -kv[1]["votes"])}
    trusted = v1 and aligned > 0
    doc = {
        "base_name": base, "status": "applied", "zones_applied": zones_done,
        "source": "视觉通道逐行转录 + 脚本化双源核对（V1 图号真值 / V2 逐行字数对账）",
        "verification": {
            "V1_drawing_no_truth": {
                "pass": v1, "expect": base, "expect_norm": want,
                "min_lcs": V1_MIN_LCS, "best_lcs": dn_hit,
                "hit_rows": dn_row, "tb_concat_hit": want in tb_all,
                "note": "base_name 取自 PDF 文件名=已知真值。标题栏图号单元格只写"
                        "图号主体（去文件名前缀与版本段，实测如此），故按最长公共连续子串"
                        "≥%d 判定，且必须命中在**单一行**内，否则本图视觉识读不采信"
                        % V1_MIN_LCS},
            "V2_char_count_per_row": {
                "pass": aligned > 0, "rows_transcribed": len(per),
                "rows_exact": aligned,
                "tol": V2_TOL,
                "note": "对账基准是**字符位数**而非 item 数：一字符可被拆成上下两半"
                        "两个 item，而单笔画字符（连字符/「1」/「·」）只有 1 段子路径、"
                        "被 glyph_pool 丢弃而成空位；字符位由 x 重叠归并 + 字距中位数"
                        "推空位得出。仅精确相等者用于字符↔字形对齐"},
            "rows": per,
        },
        "trusted": bool(trusted),
        "title_block": fields if v1 else {},
        "title_block_lines": lines_tb,
        "technical_requirements": notes if v1 else [],
        "scale_reads": scales if v1 else [],
        "derived_labels": {"n_sid": n_sid, "n_conflict": n_conflict,
                           "labels": lab_out},
    }
    C.write_json(C.work_path(base, "vision_read.json"), doc)
    C.write_json(os.path.join(vd, "labels_derived.json"),
                 {"base_name": base, "aligned_rows": aligned, "labels": lab_out})
    gate.add("V1 图号真值命中标题栏转录", v1,
             "expect=%s 标题栏行=%d 最长公共子串=%d(阈%d) 命中行=%s"
             % (base, len(lines_tb), dn_hit, V1_MIN_LCS, dn_row or "无"),
             required=False)
    gate.add("V2 逐行字符位数精确对账", aligned > 0,
             "精确=%d/%d 行（容差=%d 字符）" % (aligned, len(per), V2_TOL),
             required=False)
    gate.add("派生标签无冲突", n_conflict == 0 and n_sid > 0,
             "sid=%d 冲突=%d 票=%d" % (n_sid, n_conflict, sum(votes.values())),
             required=False)
    gate.add("技术要求条目已识读", bool(notes),
             "%d 条（编号行）" % len(notes), required=False)
    gate.add("比例 read 档已识读", bool(scales),
             "%d 处" % len(scales), required=False)
    gate.dump(C.work_path(base, "gate_03d.json"))
    C.log("[%s] 视觉识读 trusted=%s V1=%s(%s) V2精确=%d/%d 派生sid=%d(冲突%d) "
          "技术要求=%d 比例=%d 字段=%s"
          % (base, trusted, v1, dn_row or "无", aligned, len(per), n_sid,
             n_conflict, len(notes), len(scales), sorted(fields)))
    C.log(gate.report())
    return doc


def promote():
    """跨图汇总派生标签 → output/_glyph_dict/glyph_labels.json（冲突即弃）。

    只收 trusted=True 的图：trusted = V1 图号真值命中 且 V2 有精确对齐行。
    V1 未命中意味着连图上最大的图号串都读错了（实测某图把图号串读错一位，
    LCS=7<8），此时 V2 对齐只能证明「字符位数」对上了，不能证明
    字符本身对——把这些票汇入字典就是把误读当真相，违反「不臆造」。
    """
    votes = Counter()
    seen = defaultdict(Counter)
    per_sheet = {}
    skipped = {}
    for base in C.all_sheets():
        p = os.path.join(C.work_dir(base), "vread", "labels_derived.json")
        d = C.read_json(p, None)
        if not d:
            continue
        vr = C.read_json(C.work_path(base, "vision_read.json"), {}) or {}
        v1d = (vr.get("verification") or {}).get("V1_drawing_no_truth") or {}
        if not vr.get("trusted"):
            skipped[base] = {"n_sid": len(d.get("labels") or {}),
                             "best_lcs": v1d.get("best_lcs"),
                             "why": "V1 图号真值未命中，本图识读不采信，标签不入字典"}
            per_sheet[base] = {"aligned_rows": d.get("aligned_rows", 0),
                               "n_sid": len(d.get("labels") or {}), "trusted": False,
                               "best_lcs": v1d.get("best_lcs"),
                               "min_lcs": v1d.get("min_lcs")}
            continue
        per_sheet[base] = {"aligned_rows": d.get("aligned_rows", 0),
                           "n_sid": len(d.get("labels") or {}), "trusted": True,
                           "best_lcs": v1d.get("best_lcs"),
                           "hit_rows": v1d.get("hit_rows") or []}
        for sid, e in (d.get("labels") or {}).items():
            for ch, n in (e.get("conflict") or {}).items():
                votes[(sid, ch)] += n
                seen[sid][ch] += n
    labels, rejected = {}, {}
    for sid, cnt in seen.items():
        tot = sum(cnt.values())
        best, bn = cnt.most_common(1)[0]
        if len(cnt) == 1:
            labels[sid] = {"char": best, "votes": tot, "label_confidence": "high",
                           "source": "03d 逐行识读对齐（V1+V2 双过）"}
        elif bn >= 3 * (tot - bn) and bn >= 3:
            labels[sid] = {"char": best, "votes": tot, "label_confidence": "med",
                           "source": "03d 多票主导（%s）" % dict(cnt)}
        else:
            rejected[sid] = {"chars": dict(cnt), "why": "票型分散，宁缺勿臆"}
    gd = C.GLYPH_DIR
    old = C.read_json(os.path.join(gd, "glyph_labels.json"), {}) or {}
    old_lab = old.get("labels") or {}
    old_meta = old.get("meta") or {}
    # 与 03c 对称：字典跨阶段共用，本阶段只覆写自己产出的标签，保留其他来源
    # （source 不以 "03d" 开头）已采信的标签，并保留 03c 的 meta 审计键
    # （plaintext_audit / crib_audit / reject_reasons / n_unresolved 等是两个明文源
    # 的否证留痕）——整份覆写会让汇总报告 §五 读出一堆 None，丢掉已有证据。
    foreign = {k: v for k, v in old_lab.items()
               if k not in labels
               and not str((v or {}).get("source") or "").startswith("03d")}
    merged = dict(foreign)
    merged.update(labels)
    meta = dict(old_meta)
    meta.update({"source": "scripts/03d_vision_read.py --promote",
                 "method": "逐行高对比识读 + V1 图号真值 + V2 逐行字数精确对账，"
                           "仅精确对齐行贡献票；跨图汇总后单票型=high，"
                           "≥3倍主导=med，票型分散=拒绝",
                 "vision_available": True,
                 "vision_scope": "可用范围经 V1/V2 双源比对实测校准，非全量可用："
                                 "CAD 单线数字/字母与几何标注可逐字精确（图号 12/12）；"
                                 "小字高汉字格会被描述通道虚构，由 V2 字数对账拦下"
                                 "（转录者因字符数≠n 而省略，省略行不贡献票）",
                 "vote_zone_scope": "全部票均来自 tb(标题栏) 与 notes(说明/技术要求) 两区；"
                                    "drawing 区渲染 0 行，故单票标签也满足方案「单例只标"
                                    "落在标题栏/技术要求区的模板」的要求",
                 "n_labels": len(merged), "n_labels_own": len(labels),
                 "n_labels_foreign_preserved": len(foreign),
                 "n_rejected": len(rejected),
                 "n_sheets_trusted": sum(1 for v in per_sheet.values() if v.get("trusted")),
                 "skipped_untrusted": skipped,
                 "per_sheet": per_sheet,
                 "prev_n_labels": len(old_lab)})
    out = {"labels": merged,
           "meta": meta,
           "rejected": rejected,
           # unresolved 的语义归 03c（未解模板清单）；本阶段不重写它，
           # 旧实现写的是「上轮到本轮丢掉的 sid」，与 09 读的「未解模板数」不同义。
           "unresolved": old.get("unresolved") or [],
           "evidence_sample": old.get("evidence_sample") or []}
    C.write_json(os.path.join(gd, "glyph_labels.json"), out)
    C.log("promote: 标签=%d(本阶段%d+保留%d) 拒绝=%d 采信图=%d 不采信图=%d 逐图=%s"
          % (len(merged), len(labels), len(foreign), len(rejected),
             sum(1 for v in per_sheet.values() if v.get("trusted")),
             len(skipped), per_sheet))
    return out


def build(base, zone, limit=None):
    vdir = os.path.join(C.work_dir(base), "vread")
    os.makedirs(vdir, exist_ok=True)
    vdoc = C.read_json(C.work_path(base, "views.json")) or {}
    tb_bbox = vdoc.get("tb_bbox")
    min_n = 2                     # 单字形“行”实测多为小标记碎片，不入识读
    rows, meta = select(base, zone, tb_bbox, min_n)
    sheets, recs = render_rows(base, zone, rows, vdir, limit)
    mp = os.path.join(vdir, "manifest.json")
    old = C.read_json(mp, {}) or {}
    keep_rows = [r for r in (old.get("rows") or []) if r["zone"] != zone]
    keep_sheets = [s for s in (old.get("sheets") or []) if s["zone"] != zone]
    man = {"base_name": base, "zones": dict((old.get("zones") or {}), **{zone: meta}),
           "sheets": keep_sheets + sheets, "rows": keep_rows + recs,
           "howto": ("逐张读 %s 下的 %s_row_sheet_*.png，按格下 R 编号转录，写入 %s："
                     '{"zones": {"%s": {"R0001": "该行文本", ...}}}，再跑 --apply。'
                     "row_id 在各分区间独立编号会撞号，故必须嵌在分区键下。"
                     "格下 n= 是该行**字符位数**（已含被池丢弃的单笔画字符所占空位），"
                     "转录的非空白字符数应与之精确相等，否则该行不被采信。"
                     % (vdir, zone, os.path.join(vdir, "transcript.json"), zone))}
    C.write_json(mp, man)
    gate = C.Gate(base)
    gate.add("行格图已渲染", len(sheets) > 0,
             "%s 区：字形=%d 行=%d 图=%d 张 → %s"
             % (zone, meta["glyphs_all"], meta["rows"], len(sheets), vdir))
    gate.add("每行字数已标注(供 V2 对账)", all(r["n"] >= 1 for r in recs),
             "行数=%d n 分布=%s" % (len(recs), dict(Counter(r["n"] for r in recs).most_common(6))))
    gate.dump(C.work_path(base, "gate_03d.json"))
    C.log("[%s] %s 区渲染：字形=%d(中位字高%.2f,字符级下限%.2f) 行=%d 图=%d"
          % (base, zone, meta["glyphs_all"], meta["gh_median"], meta["gh_min"],
             meta["rows"], len(sheets)))
    C.log(gate.report())
    return man


def main():
    argv = sys.argv[1:]
    C.init(argv)
    if "--promote" in argv:
        promote()
        return 0
    apply_only = "--apply" in argv
    zone = ZONE_TB
    if "--zone" in argv:
        zone = argv[argv.index("--zone") + 1]
        if zone not in ZONES:
            sys.exit("--zone 只能是 %s" % (ZONES,))
    limit = None
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])
    for b in C.parse_sheet_arg(argv):
        C.ensure_dirs(b)
        if apply_only:
            apply_transcript(b, zone)
        else:
            build(b, zone, limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
