# -*- coding: utf-8 -*-
"""02 视图聚类与归属（方案 §6 步骤 2 / 决策 D2）

work/prims.json → work/views.json
门禁：无 UNASSIGNED（每个 kept 图元都有视图）、Σmembers==kept、V00 必存在、
     每视图≥1 prim、无重复归属；基线图视图数对账 §11 基线（V00+V01–Vnn）为记录项。

算法（实测校准）：方案原文指定「outline+centerline 并查集聚类(eps=25) → 投影间隙
切分过合并簇 → 小簇(<15 prim)就近归并」。实测该口径下 eps=25 得 54 簇、最大仅 576 条
（「最大 1647 条」的记载只在**全 kept 层**口径下复现，即把 dimension/thin 一并
聚类），故不存在待切的过合并巨簇；而递归投影间隙切分作用于全部种子会把基线图从 26 推到
43（各图一致过分裂），按方案原样流程扫遍「过合并簇」判据只能得 13–16 —— 两条路径都
比现行机制离基线 27 更远（探针 output/_probe/cmp_specviews.py、cmp_gapsplit.py，落盘
spec_views.json、gap_split.json；09 的修正单 §3.3 读回并叙述）。故改用**墨迹占用栅格
连通域**，并把长骨架线排除出连通核以消除桥接：
  1. V00   = title-block 层全部 + 整页跨度的图框/分区线
  2. 骨架   = outline+centerline 且非 GLYPH、非整页跨度、非 V00
  3. 连通核 = 骨架中 max_side ≤ CORE_MAX_SIDE 的**局部短线**（长线是桥接元凶，
             先排除出连通性，事后按就近归属）→ CELL 栅格化 → 膨胀 DIL → 连通域
  4. 种子   = 连通核数 ≥ MIN_SEED 的连通域；小碎片就近并入种子，否则 V00
  5. 长骨架 = 就近归属种子（≤FAR_DIST），否则 V00
  6. 其余层 = dimension/special/thin/字形按种子 bbox 扩张包含 → 唯一命中该视图；
             多命中取最近中心；无命中取 ≤FAR_DIST 的最近种子；仍无则 V00
  7. 覆盖   = work/views_override.json 人工 bbox 优先级最高（absorb=true 强制吸收）
  8. 编号   = 回正横向(X_L=y_p, Y_L=W−x_p) 先行后列阅读序 → V01…Vnn，V00 固定
"""
from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

# ---- 聚类参数（基线图对账校准，逐图通用；实测 min_side=8 → 25 种子 + V00 = 26 视图）
CELL = 6.0            # 墨迹栅格边长（pt）
DIL = 2               # 膨胀迭代次数（≈12pt 容差，弥合笔画间断）
CORE_MAX_SIDE = 200.0  # 连通核的图元长边上限（pt）：超过者视为跨视图长线
MIN_SEED = 8          # 独立视图种子的最小连通核图元数
SEED_MERGE_DIST = 120.0  # 小碎片就近并入种子的 bbox 距离上限（pt）
CONTAIN_TOL = 40.0    # 归属判定的视图 bbox 扩张（pt）
FAR_DIST = 400.0      # 无包含时就近归属的距离上限（pt）
TB_EPS = 15.0         # 标题栏密聚半径（pt）
TB_ABSORB = 40.0      # 标题栏邻簇吸收半径（pt）；实测 20/40/60 同结果，100 起气球化

# 方案 §11 基线视图数（记录项，非硬门禁）：从 config.baseline.views 读取
def _cfg() -> dict:
    """config 运行时快照（common.init 后可用）；未 init 时为空 dict。"""
    return getattr(C, "_CFG", None) or {}


def ink_grid(prims: list, cell: float = CELL) -> "object":
    """把图元栅格化为墨迹占用网格（折线采样点 + bbox 填充）。"""
    import numpy as np
    gw = int(np.ceil(C.W_PT / cell)) + 1
    gh = int(np.ceil(C.H_PT / cell)) + 1
    g = np.zeros((gw, gh), dtype=bool)
    for p in prims:
        x0, y0, x1, y1 = p["r"]
        g[max(0, int(x0 // cell)):min(gw, int(x1 // cell) + 1),
          max(0, int(y0 // cell)):min(gh, int(y1 // cell) + 1)] = True
        for q in C.flatten_prim(p):
            g[min(gw - 1, max(0, int(q[0] // cell))),
              min(gh - 1, max(0, int(q[1] // cell)))] = True
    return g


def label_prims(prims: list, lab, cell: float = CELL) -> list:
    """每个图元取其 bbox 内出现最多的连通域标号（无墨迹则 -1）。"""
    import numpy as np
    out = []
    for p in prims:
        x0, y0, x1, y1 = p["r"]
        sub = lab[max(0, int(x0 // cell)):int(x1 // cell) + 1,
                  max(0, int(y0 // cell)):int(y1 // cell) + 1]
        v = sub[sub > 0]
        out.append(int(np.bincount(v).argmax()) if len(v) else -1)
    return out


def rowcol_layout(views: list) -> None:
    """回正横向阅读序：先按 Y_L 分行（自上而下），行内按 X_L 升序。"""
    lb = []
    for v in views:
        b = v["bbox"]
        x0, y0 = C.to_landscape(b[0], b[3])
        x1, y1 = C.to_landscape(b[2], b[1])
        lb.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    n = len(views)
    uf = C.UnionFind(n)
    for a in range(n):
        for b in range(a + 1, n):
            if lb[a][1] <= lb[b][3] and lb[b][1] <= lb[a][3]:
                uf.union(a, b)
    rows = list(uf.groups().values())
    if len(rows) == 1 and n > 4:            # 区间重叠链化 → 退化为中心距单链
        hs = sorted((lb[k][3] - lb[k][1]) for k in range(n))
        t = 0.5 * hs[len(hs) // 2]
        uf = C.UnionFind(n)
        order = sorted(range(n), key=lambda k: (lb[k][1] + lb[k][3]) / 2)
        for a, b in zip(order, order[1:]):
            if abs((lb[a][1] + lb[a][3]) / 2 - (lb[b][1] + lb[b][3]) / 2) <= t:
                uf.union(a, b)
        rows = list(uf.groups().values())
    rows.sort(key=lambda g: -sum((lb[k][1] + lb[k][3]) / 2 for k in g) / len(g))
    for ri, g in enumerate(rows):
        g.sort(key=lambda k: (lb[k][0] + lb[k][2]) / 2)
        for ci, k in enumerate(g):
            views[k]["layout"] = {"row": ri + 1, "col": ci + 1}
            views[k]["center_L"] = [round((lb[k][0] + lb[k][2]) / 2, 2),
                                    round((lb[k][1] + lb[k][3]) / 2, 2)]
            views[k]["bbox_L"] = [round(x, 2) for x in lb[k]]


def build(base: str) -> dict:
    import numpy as np
    from scipy import ndimage

    doc = C.read_json(C.work_path(base, "prims.json"))
    if not doc:
        sys.exit("缺少 prims.json，请先跑 01_extract.py --sheet %s" % base)
    prims = doc["prims"]
    by_i = {p["i"]: p for p in prims}
    kept = [p for p in prims if p["sem"] != "bg"]
    C.ensure_dirs(base)
    ovs = (C.read_json(C.work_path(base, "views_override.json"), {"overrides": []})
           or {}).get("overrides") or []

    def max_side(p):
        x0, y0, x1, y1 = p["r"]
        return max(x1 - x0, y1 - y0)

    # ---------------- 1) V00
    v00 = [p["i"] for p in kept if p["sem"] == "title-block" or C.spans_page(p["r"], 0.9)]
    v00set = set(v00)
    frame_n = sum(1 for i in v00 if by_i[i]["sem"] != "title-block")

    tb = [by_i[i] for i in v00 if by_i[i]["sem"] == "title-block"
          and not C.spans_page(by_i[i]["r"], 0.9)]
    tb_bbox = None
    tb_absorb_n, tb_absorb_ok = 0, True
    if tb:
        rects = [p["r"] for p in tb]
        grp = defaultdict(list)
        for k, c in enumerate(C.cluster_bbox(rects, TB_EPS)):
            grp[c].append(k)
        big = max(grp.values(), key=len)
        main_bb = C.merge_rects([rects[k] for k in big])
        boxes = [C.merge_rects([rects[k] for k in ks]) for ks in grp.values()]
        # 只取最大簇会**切掉图号段**：TB_EPS=15 把标题栏切成上千簇（基线图实测 1760），
        # 最大簇 y 止于 3163.0，而图号行在 y 3192–3314（另一簇 n=83、与主簇共边），
        # 于是 03d 的 V1「图号真值」核对永远无法命中。改为从主簇出发按 bbox
        # 距离迭代吸收邻簇，半径须远小于「标题栏→图框分区标记」的间距。
        acc = main_bb
        changed = True
        while changed:
            changed = False
            for bb in boxes:
                if (C.rect_dist(acc, bb) <= TB_ABSORB
                        and not C.rect_contains(acc, bb, 0.01)):
                    acc = C.merge_rects([acc, bb])
                    tb_absorb_n += 1
                    changed = True
        # 气球化守卫：吸收后跨过页面六成即视为该图半径失效，退回主簇并如实记录
        if ((acc[2] - acc[0]) >= 0.6 * C.W_PT or (acc[3] - acc[1]) >= 0.6 * C.H_PT):
            acc, tb_absorb_ok = main_bb, False
        tb_bbox = [round(v, 3) for v in acc]

    # ---------------- 2)-4) 墨迹连通域 → 种子
    skel = [p for p in kept if p["sem"] in ("outline", "centerline")
            and p["g"]["type"] != "GLYPH" and p["i"] not in v00set]
    core = [p for p in skel if max_side(p) <= CORE_MAX_SIDE]
    long_sk = [p for p in skel if max_side(p) > CORE_MAX_SIDE]

    g = ink_grid(core)
    gm = ndimage.binary_dilation(g, iterations=DIL) if DIL else g
    lab, ncomp = ndimage.label(gm, structure=np.ones((3, 3)))
    clab = label_prims(core, lab)

    comp = defaultdict(list)
    for p, c in zip(core, clab):
        if c > 0:
            comp[c].append(p["i"])
    seeds = []
    scraps = []
    for _, ids in sorted(comp.items(), key=lambda kv: -len(kv[1])):
        (seeds if len(ids) >= MIN_SEED else scraps).append(sorted(ids))
    seeds = [{"core": s, "bbox": [round(v, 3) for v in C.merge_rects([by_i[i]["r"] for i in s])]}
             for s in seeds]
    for s in scraps:
        b = C.merge_rects([by_i[i]["r"] for i in s])
        if seeds:
            d = [C.rect_dist(b, sd["bbox"]) for sd in seeds]
            j = min(range(len(seeds)), key=lambda t: d[t])
            if d[j] <= SEED_MERGE_DIST:
                seeds[j]["core"].extend(s)
                seeds[j]["bbox"] = [round(v, 3)
                                    for v in C.merge_rects([by_i[i]["r"] for i in seeds[j]["core"]])]
                continue
        v00.extend(s)

    # ---------------- 7) 人工覆盖（优先级最高）
    for n, ov in enumerate(ovs):
        seeds.append({"core": [], "bbox": [float(v) for v in ov["bbox"]], "override": True,
                      "absorb": bool(ov.get("absorb")),
                      "name": ov.get("name") or ("人工视图%d" % (n + 1))})

    # ---------------- 5)-6) 就近/包含归属
    def boxes():
        return [s["bbox"] for s in seeds]

    def assign_extra(pool):
        bx = boxes()
        cen = [((b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for b in bx]
        orphan = []
        for p in pool:
            r = p["r"]
            hit = []
            for k, b in enumerate(bx):
                if seeds[k].get("absorb") and C.rect_contains(b, r, CONTAIN_TOL):
                    hit = [k]
                    break
                if C.rect_contains(b, r, CONTAIN_TOL):
                    hit.append(k)
            if len(hit) == 1:
                seeds[hit[0]].setdefault("extra", []).append(p["i"])
            elif len(hit) > 1:
                cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
                k = min(hit, key=lambda t: (cen[t][0] - cx) ** 2 + (cen[t][1] - cy) ** 2)
                seeds[k].setdefault("extra", []).append(p["i"])
            elif bx:
                d = [C.rect_dist(r, b) for b in bx]
                j = min(range(len(bx)), key=lambda t: d[t])
                if d[j] <= FAR_DIST:
                    seeds[j].setdefault("extra", []).append(p["i"])
                else:
                    orphan.append(p["i"])
            else:
                orphan.append(p["i"])
        return orphan

    skel_ids = set(i for s in seeds for i in s["core"])
    long_ids = set(p["i"] for p in long_sk)
    v00.extend(assign_extra(long_sk))
    done = skel_ids | long_ids | set(v00)
    rest = [p for p in kept if p["i"] not in done]
    v00.extend(assign_extra(rest))

    # ---------------- 汇总
    for s in seeds:
        s["members"] = sorted(set(s["core"]) | set(s.pop("extra", [])))
        rects = [by_i[i]["r"] for i in s["members"]]
        s["bbox_all"] = [round(v, 3) for v in C.merge_rects(rects)] if rects else list(s["bbox"])
        s["n"] = len(s["members"])
        s["n_core"] = len(set(s["core"]))
        s["by_layer"] = dict(Counter(by_i[i]["sem"] for i in s["members"]))
        s["by_geom"] = dict(Counter(by_i[i]["g"]["type"] for i in s["members"]))

    v00 = sorted(set(v00))
    v00r = [by_i[i]["r"] for i in v00]
    head = {"id": "V00", "name": "TITLE/图框(标题栏·图框·分区网格·整页跨度线)", "kind": "title",
            "bbox": tb_bbox or ([round(v, 3) for v in C.merge_rects(v00r)] if v00r else None),
            "bbox_all": [round(v, 3) for v in C.merge_rects(v00r)] if v00r else None,
            "n": len(v00), "n_core": 0, "members": v00,
            "by_layer": dict(Counter(by_i[i]["sem"] for i in v00)),
            "by_geom": dict(Counter(by_i[i]["g"]["type"] for i in v00)),
            "frame_lines": frame_n, "layout": {"row": 0, "col": 0},
            "center_L": [round(v, 2) for v in C.to_landscape(
                *( (tb_bbox[0] + tb_bbox[2]) / 2, (tb_bbox[1] + tb_bbox[3]) / 2 ))]
            if tb_bbox else None}

    body = [s for s in seeds if s["members"]]
    rowcol_layout(body)
    body.sort(key=lambda v: (v["layout"]["row"], v["layout"]["col"]))
    out_views = [head]
    for k, v in enumerate(body):
        v["id"] = "V%02d" % (k + 1)
        v["kind"] = "part"
        v.setdefault("name", "零件视图%s" % v["id"][1:])
        out_views.append(v)

    # ---------------- 校验
    seen = Counter()
    for v in out_views:
        seen.update(v["members"])
    dup = sorted(i for i, n in seen.items() if n > 1)
    for i in dup:
        for v in reversed(out_views):
            if i in v["members"] and v["id"] != "V00":
                v["members"].remove(i)
                v["n"] = len(v["members"])
                break
    unassigned = [p["i"] for p in kept if seen[p["i"]] == 0]
    out_views = [v for v in out_views if v["members"]]

    stats = {
        "kept": len(kept), "assigned": sum(len(v["members"]) for v in out_views),
        "n_views": len(out_views), "n_part_views": len(out_views) - 1,
        "skel": len(skel), "core": len(core), "long_skel": len(long_sk),
        "components": int(ncomp), "seeds": len(seeds), "scraps": len(scraps),
        # 各连通核的**核心图元数**降序：零件视图数 == 其中 ≥MIN_SEED 的个数，故这列
        # 是「视图数与方案基线差 ±1」唯一可核查的依据（阈值边界簇一眼可见）。09 的
        # 修正单 §3.3 直接引用它解释偏差，不把结论数字写死在报告生成器里。
        "comp_core_sizes": sorted((len(ids) for ids in comp.values()), reverse=True),
        "v00": len(v00), "v00_frame_lines": frame_n, "overrides": len(ovs),
        "duplicates": len(dup), "unassigned": len(unassigned),
        "rows": max((v["layout"]["row"] for v in out_views), default=0),
        "cluster_sizes": sorted((v["n"] for v in out_views), reverse=True)[:14],
        "params": {"cell": CELL, "dil": DIL, "core_max_side": CORE_MAX_SIDE,
                   "min_seed": MIN_SEED, "seed_merge_dist": SEED_MERGE_DIST,
                   "contain_tol": CONTAIN_TOL, "far_dist": FAR_DIST, "tb_eps": TB_EPS,
                   "tb_absorb": TB_ABSORB},
        "tb_bbox_absorbed": tb_absorb_n, "tb_bbox_absorb_ok": tb_absorb_ok,
    }

    C.write_json(C.work_path(base, "views.json"),
                 {"meta": {"base_name": base, "page_rect_pt": doc["meta"]["page_rect_pt"],
                           "rotation": C.ROTATION, "id_system": doc["meta"]["id_system"],
                           "counts": doc["meta"]["counts"]},
                  "tb_bbox": tb_bbox, "stats": stats, "views": out_views}, indent=None)

    gate = C.Gate(base)
    gate.add("无 UNASSIGNED 图元", stats["unassigned"] == 0,
             "unassigned=%d assigned=%d kept=%d" % (stats["unassigned"], stats["assigned"],
                                                    stats["kept"]))
    gate.add("计数对账 Σmembers==kept", stats["assigned"] == len(kept),
             "%d == %d" % (stats["assigned"], len(kept)))
    gate.add("V00 存在", any(v["id"] == "V00" for v in out_views),
             "V00 n=%d（title-block+整页线%d）tb_bbox=%s（吸收邻簇%d%s）"
             % (head["n"], frame_n, tb_bbox, tb_absorb_n,
                "" if tb_absorb_ok else "，触发气球化守卫已退回主簇"))
    gate.add("每视图≥1 prim", all(v["members"] for v in out_views), "n_views=%d" % len(out_views))
    gate.add("无重复归属", len(dup) == 0, "dup=%d%s" % (len(dup), dup[:6] or ""))
    if base == C.baseline_sheet():
        bv = (_cfg().get("baseline") or {}).get("views")
        if bv is not None:
            gate.add("方案 §11 基线视图数(%s)" % base, stats["n_views"] == bv,
                     "n_views=%d 零件视图=%d 行数=%d（基线 V00+V01–V%02d=%d）簇top=%s"
                     % (stats["n_views"], stats["n_part_views"], stats["rows"],
                        bv - 1, bv, stats["cluster_sizes"]), required=False)
    gate.dump(C.work_path(base, "gate_02.json"))

    C.log("=" * 78)
    C.log(gate.report())
    C.log("骨架=%d 连通核=%d 长骨架=%d 连通域=%d 种子=%d 碎片=%d 覆盖=%d"
          % (stats["skel"], stats["core"], stats["long_skel"], stats["components"],
             stats["seeds"], stats["scraps"], stats["overrides"]))
    for v in out_views:
        C.log("  %-4s n=%-5d core=%-4d r/c=%d/%-2d bbox_L=%s layers=%s"
              % (v["id"], v["n"], v.get("n_core", 0), v["layout"]["row"], v["layout"]["col"],
                 v.get("bbox_L"), dict(sorted(v["by_layer"].items(), key=lambda kv: -kv[1]))))
    C.log("→", C.work_path(base, "views.json"))
    return {"stats": stats, "views": out_views, "gate": gate.dump()}


def main(argv):
    C.init(argv)
    for base in C.parse_sheet_arg(argv):
        build(base)


if __name__ == "__main__":
    main(sys.argv[1:])
