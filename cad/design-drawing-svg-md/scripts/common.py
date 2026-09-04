# -*- coding: utf-8 -*-
"""公共库：路径与命名、分层映射(方案 D1)、并查集/网格索引、几何工具、IO 与门禁助手。

分层口径（决策 D1）：颜色优先（复现方案 §11 基线）+ PDM_Title 拆标题栏 + 逐图 OCG 主导性审计纠偏。
每条图元同时保留 ocg 与 color 原值，使归层成为可重跑的纯函数。
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

# ---------------------------------------------------------------- 配置加载（阶段 1 泛化）
# _CFG 在 init() 前为 None，模块级常量保持下方默认值（等价旧硬编码）；init() 读 config.json
# 覆盖这些常量，实现 config 驱动。脚本在 import 期只直接引用 GLYPH_DIR（09 模块级
# GLYPH_GATE），故 OUT/GLYPH_DIR 保留由 ROOT 推导的默认值；其余易变常量（PDF_DIR/W_PT/…）
# 均在运行期读取，init() 覆盖后即生效。init/_find_config_path/all_sheets/baseline_sheet
# 定义在文末「命令行入口」段，紧邻 parse_sheet_arg。

_CFG = None

# ---------------------------------------------------------------- 路径与命名

PDF_DIR = r"<源PDF目录>"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
GLYPH_DIR = os.path.join(OUT, "_glyph_dict")

# 图号清单（示例占位，实际以 config.json 覆盖；config.example.json 可作模板）
SHEETS = [
    "示例图号A 1-1 R00",
    "示例图号B 2-1 R00",
]
BASELINE_SHEET = None

W_PT = 2383.654052734375      # A0 竖放页宽（pt）
H_PT = 3370.110107421875      # A0 竖放页高（pt）
PT_PER_MM = 2.83465           # 1:1 时 pt/mm
ROTATION = "ccw90"            # 回正=逆时针90°；fitz 渲染用 page.set_rotation(270)


def sanitize(base: str) -> str:
    """目录名转写：去空格，保留中文与连字符。"""
    return re.sub(r"\s+", "_", base).strip("_")


def pdf_path(base: str) -> str:
    return os.path.join(PDF_DIR, base + ".pdf")


def sheet_dir(base: str) -> str:
    return os.path.join(OUT, sanitize(base))


def work_dir(base: str) -> str:
    return os.path.join(sheet_dir(base), "work")


def ensure_dirs(base: str) -> None:
    os.makedirs(work_dir(base), exist_ok=True)
    os.makedirs(os.path.join(work_dir(base), "regions"), exist_ok=True)


def work_path(base: str, name: str) -> str:
    return os.path.join(work_dir(base), name)


# 方案 §8 交付六件套（文件名保留原始空格与中文）
def deliverables(base: str) -> dict:
    d = sheet_dir(base)
    return {
        "svg": os.path.join(d, base + ".svg"),
        "md": os.path.join(d, base + "-可复现图纸描述.md"),
        "crosswalk": os.path.join(d, base + "_crosswalk.json"),
        "qa": os.path.join(d, base + "_QA题库.json"),
        "fixlist": os.path.join(d, base + "_修正单.md"),
        "redraw": os.path.join(d, base + "_反向重绘验证.png"),
    }


# ---------------------------------------------------------------- 颜色与 OCG 语义

RGB = {
    "black": (0.0, 0.0, 0.0),
    "yellow": (1.0, 1.0, 0.0),
    "green": (0.0, 1.0, 0.0),
    "cyan": (0.0, 1.0, 1.0),
    "red": (1.0, 0.0, 0.0),
    "magenta": (1.0, 0.0, 1.0),
    "blue": (0.0, 0.0, 1.0),
    "white": (1.0, 1.0, 1.0),
}
COLOR_NAME = {v: k for k, v in RGB.items()}

# 方案 §1：黑=主轮廓、青=中心线、黄=细轮廓、绿=尺寸、红=特殊
COLOR_LAYER = {
    "black": "outline",
    "cyan": "centerline",
    "yellow": "thin",
    "green": "dimension",
    "red": "special",
}
# 五色之外（洋红/蓝等）按 OCG 语义归层，仍无解则 thin 并标 UNMAPPED
OCG_STRONG = {
    "outline": {"粗实线", "产品轮廓线", "产品线", "粗线"},
    "centerline": {"中心线", "细点划线"},
    "dimension": {"标注尺寸线"},
    "special": {"双点划线", "剖面线"},
}
OCG_TO_LAYER = {ocg: lay for lay, s in OCG_STRONG.items() for ocg in s}
# 各层的基线色（用于主导性审计判定是否失真）
LAYER_BASE_COLOR = {
    "outline": "black",
    "centerline": "cyan",
    "dimension": "green",
    "special": "red",
}
# 通用/标注类 OCG：不参与纠偏，一律走颜色兜底
OCG_GENERIC = {
    "0", "01", "02", "05", "7", "8", "DIM", "DEFPOINTS", "THIN", "hsl",
    "文字", "标注 文字线", "标注\u3000文字线", "7标注层",
}
# 字形候选所在的 OCG（无文字层，字符=单线笔画矢量）
OCG_TEXT = {
    "8", "文字", "标注 文字线", "标注\u3000文字线", "7标注层", "标注尺寸线", "DIM", "PDM_Title",
}

LAYERS = ["outline", "thin", "centerline", "dimension", "special", "title-block"]
LAYER_SEMANTIC = {
    "outline": "主轮廓线层(可见实体线)",
    "thin": "细轮廓线层(细实线/虚线/隐藏线/图框分区)",
    "centerline": "中心线层(中心线/细点划线/对称轴)",
    "dimension": "尺寸标注层(尺寸线/界线/箭头/尺寸数字glyph)",
    "special": "特殊层(红色特殊要求/剖面线/双点划线)",
    "title-block": "标题栏层(OCG=PDM_Title 的标题栏与栏内线)",
}


def rgb_key(color) -> tuple | None:
    if color is None:
        return None
    k = tuple(round(float(x), 2) for x in color)
    for name, ref in RGB.items():
        if all(abs(a - b) <= 0.02 for a, b in zip(k, ref)):
            return ref
    return k


def color_name(color) -> str:
    k = rgb_key(color)
    if k is None:
        return "none"
    return COLOR_NAME.get(k, "rgb%s" % (k,))


# ---------------------------------------------------------------- 图元归一化


def norm_item(it) -> list:
    """把 fitz drawing item 归一为 [op, [coords...]]，坐标保留 3 位小数。"""
    op = it[0]
    if op == "re":
        r = it[1]
        return ["re", [round(r.x0, 3), round(r.y0, 3), round(r.x1, 3), round(r.y1, 3)]]
    if op == "qu":
        q = it[1]
        pts = [q.ul, q.ur, q.ll, q.lr]
        return ["qu", [c for p in pts for c in (round(p.x, 3), round(p.y, 3))]]
    pts = [round(v.x, 3) if hasattr(v, "x") else round(float(v), 3)
           for p in it[1:] for v in (p.x, p.y)]
    return [op, pts]


def item_points(rec_it: list) -> list:
    """从归一 item 取端点序列 [(x,y), ...]。

    `qu` 存的是 ul,ur,ll,lr（非周界序），返回时重排为周界 ul→ur→lr→ll，
    与 flatten_prim 保持一致，否则矩形 quad 会丢掉两条侧边。
    """
    op, c = rec_it
    if op == "re":
        x0, y0, x1, y1 = c
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    if op == "qu":
        q = list(zip(c[0::2], c[1::2]))
        return [q[0], q[1], q[3], q[2]]
    return list(zip(c[0::2], c[1::2]))


def prim_points(prim: dict) -> list:
    pts = []
    for it in prim["it"]:
        pts.extend(item_points(it))
    return pts


def prim_bbox(prim: dict) -> tuple:
    return tuple(prim["r"])


def is_page_bg(prim: dict) -> bool:
    """整页纯白/无色背景填充矩形：color=None 且覆盖 >=99% 页面。"""
    if prim["c"] is not None:
        return False
    x0, y0, x1, y1 = prim["r"]
    return (x1 - x0) >= 0.99 * W_PT and (y1 - y0) >= 0.99 * H_PT


# ---------------------------------------------------------------- D1 分层


def audit_layers(prims: list) -> dict:
    """逐图主导性审计：统计 OCG×color 交叉计数、强语义 OCG 的主色占比与纠偏触发。"""
    cross = Counter()
    for p in prims:
        cross[(p["ocg"] or "", color_name(p["c"]))] += 1
    triggers, detail = {}, {}
    for layer, ocgs in OCG_STRONG.items():
        cnt = Counter()
        for (ocg, cname), n in cross.items():
            if ocg in ocgs:
                cnt[cname] += n
        total = sum(cnt.values())
        if total == 0:
            detail[layer] = {"total": 0, "dominant": None, "ratio": 0.0,
                             "baseline": LAYER_BASE_COLOR[layer], "trigger": False}
            triggers[layer] = False
            continue
        dom, domn = cnt.most_common(1)[0]
        ratio = domn / total
        trig = dom != LAYER_BASE_COLOR[layer] and ratio > 0.5
        detail[layer] = {"total": total, "dominant": dom, "ratio": round(ratio, 4),
                         "baseline": LAYER_BASE_COLOR[layer], "trigger": bool(trig),
                         "colors": dict(cnt.most_common())}
        triggers[layer] = bool(trig)
    # 整页跨度长线的 OCG 归属（PDM_Title 条数偏少的图据此扩定 V00 范围）
    frame = Counter()
    for p in prims:
        x0, y0, x1, y1 = p["r"]
        if (x1 - x0) >= 0.9 * W_PT or (y1 - y0) >= 0.9 * H_PT:
            frame[(p["ocg"] or "", color_name(p["c"]))] += 1
    return {
        "cross": {f"{o}|{c}": n for (o, c), n in sorted(cross.items(), key=lambda kv: -kv[1])},
        "strong": detail,
        "triggers": triggers,
        "frame_lines": {f"{o}|{c}": n for (o, c), n in frame.most_common()},
    }


def assign_layer(prim: dict, triggers: dict) -> tuple:
    """返回 (六层名, 备注)。颜色优先 + PDM_Title 拆标题栏 + 强语义 OCG 纠偏。"""
    ocg = prim["ocg"] or ""
    cname = color_name(prim["c"])
    note = ""
    if ocg == "PDM_Title" and cname in ("yellow", "none"):
        return "title-block", note
    if is_page_bg(prim):
        return "bg", "整页无描边背景填充矩形(剔除)"
    sem = COLOR_LAYER.get(cname)
    if sem is None:
        sem = OCG_TO_LAYER.get(ocg)
        if sem is None:
            sem = "thin"
            note = "UNMAPPED:color=%s,ocg=%s" % (cname, ocg)
        else:
            note = "off-palette color=%s→OCG %s" % (cname, ocg)
    # 纠偏：仅当该图该层主导性审计判定颜色口径失真时生效
    for layer, on in triggers.items():
        if on and ocg in OCG_STRONG[layer] and sem != layer:
            note = (note + ";" if note else "") + "OCG纠偏:%s(%s)→%s" % (ocg, cname, layer)
            sem = layer
            break
    return sem, note


# ---------------------------------------------------------------- 并查集与网格索引


class UnionFind:
    def __init__(self, n: int):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, a: int) -> int:
        p = self.p
        while p[a] != a:
            p[a] = p[p[a]]
            a = p[a]
        return a

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1

    def groups(self) -> dict:
        g = defaultdict(list)
        for i in range(len(self.p)):
            g[self.find(i)].append(i)
        return dict(g)


def cluster_bbox(rects: list, eps: float, cell: float = 80.0,
                 max_pair_per_cell: int = 200000) -> list:
    """bbox 扩张 eps 后相交的并查集聚类，网格索引避免 O(n^2)。返回每元素的簇 id。"""
    n = len(rects)
    uf = UnionFind(n)
    grid = defaultdict(list)
    for k, r in enumerate(rects):
        gx0, gx1 = int((r[0] - eps) // cell), int((r[2] + eps) // cell)
        gy0, gy1 = int((r[1] - eps) // cell), int((r[3] + eps) // cell)
        for gx in range(gx0, gx1 + 1):
            for gy in range(gy0, gy1 + 1):
                grid[(gx, gy)].append(k)
    for ks in grid.values():
        m = len(ks)
        if m * (m - 1) // 2 > max_pair_per_cell:
            continue
        for a in range(m):
            ra = rects[ks[a]]
            for b in range(a + 1, m):
                rb = rects[ks[b]]
                if (ra[0] - eps <= rb[2] and rb[0] - eps <= ra[2]
                        and ra[1] - eps <= rb[3] and rb[1] - eps <= ra[3]):
                    uf.union(ks[a], ks[b])
    roots = uf.groups()
    labels = [0] * n
    for cid, (_, members) in enumerate(sorted(roots.items(), key=lambda kv: -len(kv[1]))):
        for k in members:
            labels[k] = cid
    return labels


def merge_rects(rects) -> tuple:
    return (min(r[0] for r in rects), min(r[1] for r in rects),
            max(r[2] for r in rects), max(r[3] for r in rects))


def rect_dist(a, b) -> float:
    """两 bbox 间距离（相交为 0）。"""
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)


def rect_contains(outer, inner, tol: float = 0.0) -> bool:
    return (outer[0] - tol <= inner[0] and outer[1] - tol <= inner[1]
            and outer[2] + tol >= inner[2] and outer[3] + tol >= inner[3])


# ---------------------------------------------------------------- 几何工具


def flatten_bezier(p0, p1, p2, p3, tol: float = 0.05) -> list:
    """自适应折线化三次贝塞尔（不含起点 p0，含终点 p3）。"""
    out = []

    def sub(a, b, c, d, depth):
        chord = math.hypot(d[0] - a[0], d[1] - a[1])
        dev = max(math.hypot(b[0] - (2 * a[0] + d[0]) / 3, b[1] - (2 * a[1] + d[1]) / 3),
                  math.hypot(c[0] - (a[0] + 2 * d[0]) / 3, c[1] - (a[1] + 2 * d[1]) / 3))
        if depth >= 8 or (chord > 1e-9 and dev / chord <= tol) or dev <= tol:
            out.append(d)
            return
        ab = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        bc = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
        cd = ((c[0] + d[0]) / 2, (c[1] + d[1]) / 2)
        abc = ((ab[0] + bc[0]) / 2, (ab[1] + bc[1]) / 2)
        bcd = ((bc[0] + cd[0]) / 2, (bc[1] + cd[1]) / 2)
        m = ((abc[0] + bcd[0]) / 2, (abc[1] + bcd[1]) / 2)
        sub(a, ab, abc, m, depth + 1)
        sub(m, bcd, cd, d, depth + 1)

    sub(tuple(p0), tuple(p1), tuple(p2), tuple(p3), 0)
    return out


def flatten_prim(prim: dict, tol: float = 0.05) -> list:
    """图元折线化：返回 [(x,y), ...]（页面 pt，起点含、按 item 顺序）。"""
    pts = []
    cur = None
    for op, c in prim["it"]:
        if op == "re":
            x0, y0, x1, y1 = c
            pts.extend([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
            cur = None
            continue
        if op == "qu":
            # PyMuPDF 的 quad 顶点序列是 ul, ur, ll, lr（**非**周界顺序）；
            # 直接顺序连会画成 ul→ur→ll→lr（两条对角线），丢掉两条侧边。
            # 正确周界：ul → ur → lr → ll → ul。
            q = list(zip(c[0::2], c[1::2]))
            pts.extend([q[0], q[1], q[3], q[2], q[0]])
            cur = None
            continue
        seq = list(zip(c[0::2], c[1::2]))
        if op == "l":
            if cur is None:
                pts.append(seq[0])
            pts.append(seq[1])
            cur = seq[1]
        elif op == "c":
            if cur is None:
                pts.append(seq[0])
            pts.extend(flatten_bezier(seq[0], seq[1], seq[2], seq[3], tol))
            cur = seq[3]
        else:                       # 未知 op：按折线兜底
            if cur is None:
                pts.append(seq[0])
            pts.extend(seq[1:])
            cur = seq[-1]
    return pts


def path_d(pts: list) -> str:
    if not pts:
        return ""
    s = ["M%.3f %.3f" % pts[0]]
    s += ["L%.3f %.3f" % p for p in pts[1:]]
    return "".join(s)


def fit_circle(pts: list) -> tuple:
    """代数最小二乘拟合圆（Kåsa），返回 (cx, cy, r, rms)。仅作几何拟合的初值。"""
    n = len(pts)
    if n < 3:
        return None, None, None, float("inf")
    sx = sum(p[0] for p in pts); sy = sum(p[1] for p in pts)
    sxx = sum(p[0] * p[0] for p in pts); syy = sum(p[1] * p[1] for p in pts)
    sxy = sum(p[0] * p[1] for p in pts)
    sxxx = sum(p[0] ** 3 for p in pts); syyy = sum(p[1] ** 3 for p in pts)
    sxyy = sum(p[0] * p[1] * p[1] for p in pts); syxx = sum(p[1] * p[0] * p[0] for p in pts)
    a = n * sxx - sx * sx
    b = n * sxy - sx * sy
    c = n * syy - sy * sy
    d = 0.5 * (n * (sxyy + syyy) - sy * (sxx + syy))
    e = 0.5 * (n * (sxxx + syxx) - sx * (sxx + syy))
    det = a * c - b * b
    if abs(det) < 1e-12:
        return None, None, None, float("inf")
    cy = (a * d - b * e) / det
    cx = (c * e - b * d) / det
    r2 = (sxx - 2 * cx * sx + n * cx * cx + syy - 2 * cy * sy + n * cy * cy) / n
    if r2 <= 0:
        return None, None, None, float("inf")
    r = math.sqrt(r2)
    rms = math.sqrt(sum((math.hypot(p[0] - cx, p[1] - cy) - r) ** 2 for p in pts) / n)
    return cx, cy, r, rms


def fit_circle_geom(pts: list) -> tuple | None:
    """几何最小二乘拟合圆（径向残差最小），返回 (cx, cy, r, rms)；失败 None。

    源 PDF 无贝塞尔（op 仅 l/re/qu，closePath 全 False），弧/圆均为多段线近似，
    代数拟合在弧段上病态（实测给出 r≈1e8），必须用几何拟合。"""
    if len(pts) < 4:
        return None
    import numpy as np
    from scipy.optimize import least_squares
    a = np.asarray(pts, dtype=float)
    c0 = a.mean(axis=0)
    rad = np.hypot(a[:, 0] - c0[0], a[:, 1] - c0[1])
    r0 = float(rad.mean())
    if r0 <= 1e-9:
        return None

    def res(p):
        return np.hypot(a[:, 0] - p[0], a[:, 1] - p[1]) - p[2]

    try:
        s = least_squares(res, [c0[0], c0[1], r0], method="lm",
                          xtol=1e-12, ftol=1e-12, max_nfev=400)
    except Exception:
        return None
    rms = float(math.sqrt(float(np.mean(s.fun ** 2))))
    return float(s.x[0]), float(s.x[1]), abs(float(s.x[2])), rms


def seg_len(a, b) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def polyline_len(pts: list) -> float:
    return sum(seg_len(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def turn_angles(pts: list) -> list:
    """各内点转角（度，带符号）。"""
    out = []
    for i in range(1, len(pts) - 1):
        a1 = math.atan2(pts[i][1] - pts[i - 1][1], pts[i][0] - pts[i - 1][0])
        a2 = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
        d = math.degrees(a2 - a1)
        while d > 180:
            d -= 360
        while d < -180:
            d += 360
        out.append(d)
    return out


def split_runs(pts: list, straight_tol_deg: float = 4.0) -> list:
    """按转角把折线切成 [('s'|'c', [点索引...]), ...]（直线段/弯曲段交替）。"""
    if len(pts) < 3:
        return [("s", list(range(len(pts))))]
    kinds = []
    for d in turn_angles(pts):
        kinds.append("s" if abs(d) <= straight_tol_deg else "c")
    # kinds[i] 描述顶点 i+1；把顶点归到相邻段的种类
    runs, cur, curk = [], [0], kinds[0]
    for i, k in enumerate(kinds):
        vi = i + 1
        if k == curk:
            cur.append(vi)
        else:
            cur.append(vi)
            runs.append((curk, cur))
            cur, curk = [vi], k
    cur.append(len(pts) - 1)
    runs.append((curk, cur))
    # 合并相邻同类
    merged = []
    for k, idx in runs:
        if merged and merged[-1][0] == k:
            merged[-1][1].extend(idx[1:])
        else:
            merged.append((k, list(idx)))
    return merged


def detect_obround(pts: list, closed: bool, rms_tol: float = 0.1) -> dict | None:
    """长圆（OBROUND）：闭合折线 = 2 直线 + 2 等半径半圆端。参数为页面 pt。"""
    if not closed or len(pts) < 8:
        return None
    runs = split_runs(pts)
    if len(runs) > 1 and runs[0][0] == runs[-1][0]:          # 跨首尾的同类型段合并
        runs = [(runs[0][0], runs[-1][1] + runs[0][1][1:])] + runs[1:-1]
    straights = [r for r in runs if r[0] == "s"]
    curves = [r for r in runs if r[0] == "c"]
    if len(straights) != 2 or len(curves) != 2:
        return None
    fits = []
    for _, idx in curves:
        if len(idx) < 3:
            return None
        f = fit_circle_geom([pts[i] for i in idx])
        if not f or f[3] > rms_tol or not f[2]:
            return None
        fits.append(f)
    (c1x, c1y, r1, m1), (c2x, c2y, r2, m2) = fits
    if abs(r1 - r2) > max(0.05, 0.02 * r1):
        return None
    rad = (r1 + r2) / 2
    cen = math.hypot(c2x - c1x, c2y - c1y)
    if cen <= rad * 0.5:
        return None
    return {"r": round(rad, 3), "c1": [round(c1x, 3), round(c1y, 3)],
            "c2": [round(c2x, 3), round(c2y, 3)], "center_dist": round(cen, 3),
            "w": round(2 * rad, 3), "total_len": round(cen + 2 * rad, 3),
            "orient": round(math.degrees(math.atan2(c2y - c1y, c2x - c1x)) % 360, 2),
            "rms": round(max(m1, m2), 4)}


def _sweep_signed(pts: list, cx: float, cy: float) -> tuple:
    """沿折线累计带符号转角，返回 (a1, sweep)（度）。"""
    ang = [math.atan2(p[1] - cy, p[0] - cx) for p in pts]
    tot = 0.0
    for i in range(len(ang) - 1):
        d = ang[i + 1] - ang[i]
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        tot += d
    return math.degrees(ang[0]) % 360, math.degrees(tot)


def classify_geom(prim: dict, glyph: bool = False, tol_flat: float = 0.05,
                  circle_rms: float = 0.1) -> dict:
    """判定几何类型与参数：GLYPH/RECT/QUAD/LINE/CIRCLE/ARC/OBROUND/POLYLINE/CURVE。

    字形优先：字符"0"等本身即圆，必须先按 D3 判字形再判几何，否则会被误当 CIRCLE。
    """
    items = prim["it"]
    ops = [op for op, _ in items]
    pts = flatten_prim(prim, tol_flat)
    x0, y0, x1, y1 = prim["r"]
    diag = math.hypot(x1 - x0, y1 - y0)
    closed = math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 0.6 if len(pts) > 1 else False
    base = {"closed": closed, "n_items": len(items), "n_pts": len(pts),
            "len_pt": round(polyline_len(pts), 3) if len(pts) > 1 else 0.0}
    if glyph:
        return dict(base, type="GLYPH")
    if len(items) == 1 and ops[0] == "re":
        return dict(base, type="RECT", bbox=[x0, y0, x1, y1])
    if ops and set(ops) == {"qu"}:
        return dict(base, type="QUAD", bbox=[x0, y0, x1, y1])
    if set(ops) == {"l"} and len(pts) == 2:
        return dict(base, type="LINE", p1=[round(pts[0][0], 3), round(pts[0][1], 3)],
                    p2=[round(pts[1][0], 3), round(pts[1][1], 3)])
    if len(pts) >= 4:
        ob = detect_obround(pts, closed, circle_rms)
        if ob:
            return dict(base, type="OBROUND", **ob)
        f = fit_circle_geom(pts)
        if f:
            cx, cy, r, rms = f
            # 排除"直线被拟合成超大半径圆"的假阳
            if rms <= circle_rms and r <= 4 * diag + 10:
                a1, sweep = _sweep_signed(pts, cx, cy)
                if closed and abs(abs(sweep) - 360) <= 2.0:
                    return dict(base, type="CIRCLE", cx=round(cx, 3), cy=round(cy, 3),
                                r=round(r, 3), rms=round(rms, 4))
                if abs(sweep) >= 8.0:
                    return dict(base, type="ARC", cx=round(cx, 3), cy=round(cy, 3),
                                r=round(r, 3), a1=round(a1, 2),
                                a2=round((a1 + sweep) % 360, 2),
                                sweep=round(sweep, 2), rms=round(rms, 4))
    if set(ops) == {"l"}:
        return dict(base, type="POLYLINE")
    return dict(base, type="CURVE")


# ---------------------------------------------------------------- 字形候选（决策 D3）

GLYPH_MIN_SIDE = 0.6      # pt，笔画短边下限
GLYPH_MAX_DIM = 30.0      # pt，字符长边上限
GLYPH_SIG_ND = 1          # 归一化签名的坐标小数位（以字高为单位）
# 方案 §D3 原文写「32×32 归一栅格化取位图哈希」，此处按 §D3 开头允许的「等价降本
# 实现」改用 nd=1 的量化矢量点集（精度≈0.1 字高，与 32×32 同量级），实测**更优**：
# 全量 10987 字形下，栅格哈希得 2399 个 sid、单例 1161 个、13 个已知字符碎成 109
# 个 sid 且出现 1 处同 sid 多字符冲突（C 3 票 / S 12 票，会直接污染字典）；量化矢量
# 点集得 1012 个 sid、单例 198 个、同样 13 字符仍聚成 31 个 sid、零冲突，前 31 大模板
# 的实例覆盖率 40.5% vs 30.0%。原因是 CAD 字形为解析矢量、同字符同字号的点集
# bit-exact（与 §D4「CAD 矢量无采样噪声，不用 RANSAC」同理），栅格化反而引入量化误差。
# 模板复现次数阈值：标题栏文字多为孤字（阀值 1），注释文字次之，
# 尺寸层同时承载箭头/短划等小几何，靠复现次数去噪（阀值 3）
GLYPH_MIN_COUNT_TITLE = 1
GLYPH_MIN_COUNT_NOTES = 2
GLYPH_MIN_COUNT_DIM = 3
OCG_NOTES = {"文字", "标注 文字线", "标注\u3000文字线", "7标注层"}


def glyph_pool(prims: list) -> list:
    """宽松字形候选池：纯描边 + 文本/标注 OCG + 子路径≥2 + 尺寸约束。"""
    out = []
    for p in prims:
        if p["t"] != "s" or (p["ocg"] or "") not in OCG_TEXT or len(p["it"]) < 2:
            continue
        x0, y0, x1, y1 = p["r"]
        w, h = x1 - x0, y1 - y0
        if min(w, h) < GLYPH_MIN_SIDE or max(w, h) > GLYPH_MAX_DIM:
            continue
        out.append(p)
    return out


def glyph_signature(prim: dict, nd: int = GLYPH_SIG_ND) -> tuple:
    """归一化形状签名：以字高 max(w,h) 为单位、保持长宽比、竖排归正。

    同一字符在不同字号下得到相同签名（尺度不变），而"1"(窄)与"—"(扁)
    因保持长宽比而可区分。实测某图：1006 个唯一签名，复现≥3 的 151 个
    模板覆盖 1240 实例，而箭头/短划类噪声几乎全为单例。

    竖排归正的旋转式必须是 `(x, y) -> (1 - y, x)`，**不是** `(y, 1 - x)`。
    窄高字形（h>w，如正立的 "1"）归一化后 x∈[0, w/h]、y∈[0, 1]，而同一字符
    躺倒时（w>h）走不旋转分支、得 x∈[0, 1]、y∈[0, h/w]=[0, w_orig/h_orig]。
    两式的 x 区间一致，但 `(y, 1-x)` 的 y 落在 [1-w/h, 1] 而非 [0, w/h]，与躺倒态
    相差一个随长宽比变化的常量平移，只有 w/h=0.5 时才偶然重合 → 正立与躺倒的
    同一字符被劈成两个模板。多图实测（10987 字形）：改正前竖形/横形共享 sid
    仅 4 个、覆盖实例 竖14/横33；改正后共享 26 个、覆盖 竖566/横2644，而总 sid
    由 1031 降到 1012（去重生效）、13 个已知字符仍各聚成同样 31 个 sid、同 sid
    多字符冲突仍为 0、前 31 大模板的实例覆盖率由 37.2% 升到 40.5%。
    """
    x0, y0, x1, y1 = prim["r"]
    w, h = x1 - x0, y1 - y0
    s = 1.0 / max(w, h, 1e-6)
    vert = h > w
    pts = []
    for q in flatten_prim(prim):
        x, y = (q[0] - x0) * s, (q[1] - y0) * s
        if vert:
            x, y = 1.0 - y, x
        pts.append((round(x, nd), round(y, nd)))
    return (len(prim["it"]), tuple(sorted(pts)))


def sig_id(sig) -> str:
    """形状签名的跨图稳定 id（用于跨图合并同一字形模板）。"""
    import hashlib
    return hashlib.sha1(repr(sig).encode("utf-8")).hexdigest()[:16]


def glyph_templates(pool: list) -> dict:
    """对候选池做模板聚类，返回 {sig: {"n", "gh", "vert", "members"}}。"""
    tpls = {}
    for p in pool:
        sig = glyph_signature(p)
        x0, y0, x1, y1 = p["r"]
        w, h = x1 - x0, y1 - y0
        t = tpls.setdefault(sig, {"n": 0, "gh": [], "vert": [], "members": []})
        t["n"] += 1
        t["gh"].append(round(max(w, h), 2))
        t["vert"].append(bool(h > w))
        t["members"].append(p["i"])
    for sig, t in tpls.items():
        gh = Counter(t["gh"]).most_common(1)[0][0]
        t["gh"] = gh
        t["vert"] = Counter(t["vert"]).most_common(1)[0][0]
        t["hgt"] = round(gh, 2)
    return tpls


def glyph_flags(prims: list) -> tuple:
    """标记字形：返回 ({prim_i: {"gh","vert","tpl","tid"}}, stats, table)。

    字形优先于几何判定（字符"0"本身即圆）；低复现的孤字（如标题栏汉字）
    按 OCG 分级阀值保留，其余单例留给 03b 的文本行对齐促升。
    table = {tid: {"n","gh","vert","ocg","members","sample"}}，供接触表与字典共用。
    """
    pool = glyph_pool(prims)
    tpls = glyph_templates(pool)
    by_i = {p["i"]: p for p in pool}
    out, table = {}, {}
    n_flag = 0
    for sig, t in sorted(tpls.items(), key=lambda kv: (-kv[1]["n"], kv[1]["gh"], kv[0][0])):
        tid = "T%04d" % (len(table) + 1)
        ocgs = Counter((by_i[i]["ocg"] or "") for i in t["members"])
        dom = ocgs.most_common(1)[0][0]
        if dom == "PDM_Title":
            need = GLYPH_MIN_COUNT_TITLE
        elif dom in OCG_NOTES:
            need = GLYPH_MIN_COUNT_NOTES
        else:
            need = GLYPH_MIN_COUNT_DIM
        table[tid] = {"n": t["n"], "gh": t["gh"], "vert": t["vert"], "ocg": dom,
                      "members": t["members"], "sample": t["members"][0],
                      "n_items": sig[0], "kept": t["n"] >= need, "sid": sig_id(sig)}
        if t["n"] < need:
            continue
        n_flag += 1
        for i in t["members"]:
            out[i] = {"gh": 0.0, "vert": t["vert"], "tpl": t["n"],
                      "ocg": dom, "tid": tid, "sid": table[tid]["sid"]}
    for i, v in out.items():
        x0, y0, x1, y1 = by_i[i]["r"]
        v["gh"] = round(max(x1 - x0, y1 - y0), 2)
    stats = {
        "pool": len(pool),
        "templates": len(tpls),
        "templates_kept": n_flag,
        "templates_ge3": sum(1 for t in tpls.values() if t["n"] >= 3),
        "flagged": len(out),
        "heights": sorted(Counter(v["gh"] for v in out.values()).most_common(8)),
        "vert": sum(1 for v in out.values() if v["vert"]),
        "tpl_top": sorted((t["n"] for t in tpls.values()), reverse=True)[:12],
    }
    return out, stats, table


def arc_points(cx, cy, r, a1, sweep, n: int = 0) -> list:
    """按解析弧生成折线（用于 rms 校验）。a1 起角(度)，sweep 带符号扫角(度)。"""
    if n <= 0:
        n = max(8, int(math.ceil(abs(sweep) / 3.0)))
    return [(cx + r * math.cos(math.radians(a1 + sweep * i / n)),
             cy + r * math.sin(math.radians(a1 + sweep * i / n))) for i in range(n + 1)]


def circle_points(cx, cy, r, n: int = 0) -> list:
    if n <= 0:
        n = max(16, int(math.ceil(2 * math.pi * r / 1.5)))
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n + 1)]


def pt_to_local(x_p, y_p, x0, y0, s) -> tuple:
    """页面 pt(竖放) → 视图局部 mm：local_x=(y_p-y0)/s, local_y=(x_p-x0)/s。"""
    return ((y_p - y0) / s, (x_p - x0) / s)


def local_to_pt(x_mm, y_mm, x0, y0, s) -> tuple:
    """视图局部 mm → 页面 pt(竖放)：x_p=x0+y·s, y_p=y0+x·s。"""
    return (x0 + y_mm * s, y0 + x_mm * s)


def scale_s(denominator: float) -> float:
    return PT_PER_MM / denominator


# ---------------------------------------------------------------- ID 体系（方案 §5）


def pid_width(n: int) -> int:
    """图元编号位宽：至少 3 位，容纳大视图。"""
    return max(3, len(str(max(n, 1))))


def prim_id(vid: str, k: int, w: int = 3) -> str:
    return "%s-P%s" % (vid, str(k).zfill(w))


def dim_id(vid: str, k: int) -> str:
    return "%s-D%s" % (vid, str(k).zfill(2))


def balloon_id(vid: str, k: int) -> str:
    return "%s-B%s" % (vid, str(k).zfill(2))


def to_landscape(x_p: float, y_p: float) -> tuple:
    """页面竖放 pt → 回正横向 pt：(X_L, Y_L) = (y_p, W − x_p)，Y_L 向上为正。"""
    return (y_p, W_PT - x_p)


def spans_page(r, frac: float = 0.9) -> bool:
    return (r[2] - r[0]) >= frac * W_PT or (r[3] - r[1]) >= frac * H_PT


LAYER_ORDER = {L: n for n, L in enumerate(LAYERS)}


def view_prim_ids(view: dict, by_i: dict) -> list:
    """视图内图元的**唯一权威排序**与 prim-id（MD 与 SVG 必须同源）。

    排序键 = (六层次序, 图元原序 i)，使 MD 的分层 prim-id 区间天然连续。
    返回 [(prim_i, prim_id, 层内序号, 层内总数)]。
    """
    ids = sorted(view["members"], key=lambda i: (LAYER_ORDER.get(by_i[i]["sem"], 99), i))
    w = pid_width(len(ids))
    per = Counter(by_i[i]["sem"] for i in ids)
    seen = Counter()
    out = []
    for k, i in enumerate(ids):
        sem = by_i[i]["sem"]
        seen[sem] += 1
        out.append((i, prim_id(view["id"], k + 1, w), seen[sem], per[sem]))
    return out


def layer_spans(view: dict, by_i: dict) -> dict:
    """每层的 prim-id 区间与计数（MD §3 门禁：区间求和==kept）。"""
    out = {}
    for i, pid, k, n in view_prim_ids(view, by_i):
        sem = by_i[i]["sem"]
        d = out.setdefault(sem, {"layer": sem, "n": 0, "first": pid, "last": pid,
                                 "first_i": i, "last_i": i, "width": len(pid.split("-P")[1])})
        d["n"] += 1
        d["last"] = pid
        d["last_i"] = i
    return out


# ---------------------------------------------------------------- IO 与门禁


def read_json(path: str, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, obj, indent: int = 1) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)


def write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def esc(s) -> str:
    """SVG/XML 属性转义。"""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


class Gate:
    """门禁收集器：add(name, ok, detail)，可 dump 为 JSON / 打印。"""

    def __init__(self, sheet: str = ""):
        self.sheet = sheet
        self.rows = []

    def add(self, name: str, ok, detail: str = "", required: bool = True) -> bool:
        self.rows.append({"gate": name, "ok": bool(ok), "detail": str(detail),
                          "required": required})
        return bool(ok)

    def metric(self, name: str, value, threshold: str, ok: bool, required: bool = True):
        return self.add(name, ok, "%s (门禁 %s)" % (value, threshold), required)

    @property
    def failed(self) -> list:
        return [r for r in self.rows if r["required"] and not r["ok"]]

    @property
    def passed(self) -> bool:
        return not self.failed

    def dump(self, path: str = None) -> dict:
        obj = {"sheet": self.sheet, "passed": self.passed,
               "n": len(self.rows), "n_failed": len(self.failed), "gates": self.rows}
        if path:
            write_json(path, obj)
        return obj

    def report(self) -> str:
        lines = ["门禁 [%s] %s (%d/%d)" % (self.sheet, "PASS" if self.passed else "FAIL",
                                           len(self.rows) - len(self.failed), len(self.rows))]
        for r in self.rows:
            flag = "ok  " if r["ok"] else ("FAIL" if r["required"] else "warn")
            lines.append("  %s %s :: %s" % (flag, r["gate"], r["detail"]))
        return "\n".join(lines)


# ---------------------------------------------------------------- 命令行入口


def _find_config_path(argv) -> str | None:
    """从 argv 找 `--config <path>` / `--config=<path>`；缺省回退脚本同目录 config.json。找不到返回 None。"""
    if argv:
        for i, a in enumerate(argv):
            if a == "--config" and i + 1 < len(argv):
                return argv[i + 1]
            if a.startswith("--config="):
                return a.split("=", 1)[1]
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    return here if os.path.exists(here) else None


def init(argv=None) -> dict:
    """加载配置 JSON 并覆盖模块级常量（config 驱动，阶段 1 泛化）。

    找不到配置（既无 --config、脚本同目录也无 config.json）时报错退出并提示 --config。
    未 init 时模块级常量保持默认值，故脚本 import 期引用的 GLYPH_DIR 仍可用，旧 11 个
    脚本不改动也能以默认值运行。返回 _CFG。
    """
    global _CFG, PDF_DIR, OUT, GLYPH_DIR, SHEETS, BASELINE_SHEET, \
        W_PT, H_PT, PT_PER_MM, ROTATION, RGB, COLOR_NAME, COLOR_LAYER, \
        OCG_STRONG, OCG_TO_LAYER, LAYER_BASE_COLOR, OCG_GENERIC, OCG_TEXT, \
        OCG_NOTES, LAYERS, LAYER_SEMANTIC, LAYER_ORDER, \
        GLYPH_MIN_SIDE, GLYPH_MAX_DIM, GLYPH_SIG_ND, \
        GLYPH_MIN_COUNT_TITLE, GLYPH_MIN_COUNT_NOTES, GLYPH_MIN_COUNT_DIM

    cfg_path = _find_config_path(argv)
    if cfg_path is None:
        sys.exit("common.init: 未找到配置（未给 --config 且脚本同目录无 config.json）。"
                 "请用 `--config <path>` 指定，或复制 config.example.json 为 config.json")
    if not os.path.exists(cfg_path):
        sys.exit("common.init: 配置文件不存在: %s" % cfg_path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        _CFG = json.load(f)

    paths = _CFG.get("paths") or {}
    if paths.get("pdf_dir"):
        PDF_DIR = paths["pdf_dir"]
    if paths.get("out"):
        OUT = paths["out"]
    GLYPH_DIR = paths.get("glyph_dir") or os.path.join(OUT, "_glyph_dict")

    page = _CFG.get("page") or {}
    W_PT = page.get("w_pt", W_PT)
    H_PT = page.get("h_pt", H_PT)
    PT_PER_MM = page.get("pt_per_mm", PT_PER_MM)
    ROTATION = page.get("rotation", ROTATION)

    if _CFG.get("sheets") is not None:
        SHEETS = list(_CFG["sheets"])
    b = _CFG.get("baseline") or {}
    if "sheet" in b:
        BASELINE_SHEET = b["sheet"]

    # 方法论/物理常量：保留默认值，允许 config 覆盖
    if _CFG.get("rgb"):
        RGB = {k: tuple(v) for k, v in _CFG["rgb"].items()}
        COLOR_NAME = {v: k for k, v in RGB.items()}
    layering = _CFG.get("layering") or {}
    if layering.get("color_layer"):
        COLOR_LAYER = dict(layering["color_layer"])
    if layering.get("layer_base_color"):
        LAYER_BASE_COLOR = dict(layering["layer_base_color"])
    if layering.get("ocg_strong"):
        OCG_STRONG = {k: set(v) for k, v in layering["ocg_strong"].items()}
        OCG_TO_LAYER = {ocg: lay for lay, s in OCG_STRONG.items() for ocg in s}
    if layering.get("ocg_generic") is not None:
        OCG_GENERIC = set(layering["ocg_generic"])
    if layering.get("ocg_text") is not None:
        OCG_TEXT = set(layering["ocg_text"])
    if layering.get("ocg_notes") is not None:
        OCG_NOTES = set(layering["ocg_notes"])
    if _CFG.get("layers"):
        LAYERS = list(_CFG["layers"])
        LAYER_ORDER = {L: n for n, L in enumerate(LAYERS)}
    if _CFG.get("layer_semantic"):
        LAYER_SEMANTIC = dict(_CFG["layer_semantic"])

    glyph = _CFG.get("glyph") or {}
    GLYPH_MIN_SIDE = glyph.get("min_side", GLYPH_MIN_SIDE)
    GLYPH_MAX_DIM = glyph.get("max_dim", GLYPH_MAX_DIM)
    GLYPH_SIG_ND = glyph.get("sig_nd", GLYPH_SIG_ND)
    GLYPH_MIN_COUNT_TITLE = glyph.get("min_count_title", GLYPH_MIN_COUNT_TITLE)
    GLYPH_MIN_COUNT_NOTES = glyph.get("min_count_notes", GLYPH_MIN_COUNT_NOTES)
    GLYPH_MIN_COUNT_DIM = glyph.get("min_count_dim", GLYPH_MIN_COUNT_DIM)
    return _CFG


def all_sheets() -> list:
    """config 驱动的图号清单；未 init 时回退模块级默认 SHEETS。"""
    return list((_CFG or {}).get("sheets") or SHEETS)


def baseline_sheet():
    """config 驱动的基线图号；未 init 时回退默认 BASELINE_SHEET。可为 None。"""
    b = (_CFG or {}).get("baseline") or {}
    return b.get("sheet", BASELINE_SHEET)


def parse_sheet_arg(argv: list) -> list:
    """解析 --sheet <base|序号> / --all，返回 base_name 列表。"""
    sheets = all_sheets()
    baseline = baseline_sheet()
    if "--all" in argv:
        return list(sheets)
    out = []
    for i, a in enumerate(argv):
        if a == "--sheet" and i + 1 < len(argv):
            v = argv[i + 1]
            if v.isdigit() and 1 <= int(v) <= len(sheets):
                out.append(sheets[int(v) - 1])
            elif v in sheets:
                out.append(v)
            else:                       # 容错：去空格匹配
                m = [s for s in sheets if sanitize(s) == sanitize(v)]
                if not m:
                    sys.exit("未知图号: %s（可选 --all 或 1..%d）" % (v, len(sheets)))
                out.append(m[0])
    if not out:
        if baseline:
            out = [baseline]
        else:
            sys.exit("未指定图号：请用 `--all` 处理全部图，或 `--sheet <序号|图号>` 指定单图"
                     "（config 未配置 baseline.sheet，无法回退基线图）。")
    seen, res = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); res.append(s)
    return res


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def log(*a) -> None:
    try:
        print(*a, flush=True)
    except UnicodeEncodeError:
        # 控制台编码覆盖不到部分符号时，一条日志就能把整条流水线打断（实测
        # Windows 管道下 stdout 为 GBK，08 打印题面时崩在 `drawings−bg` 的
        # U+2212 上）。降级为按控制台编码 replace，保证日志不致命。
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(*[str(x).encode(enc, "replace").decode(enc, "replace") for x in a],
              flush=True)
