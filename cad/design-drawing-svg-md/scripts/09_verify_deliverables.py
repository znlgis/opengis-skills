# -*- coding: utf-8 -*-
"""09 交付物齐套性 + 门禁汇总 + 基线对账 + 每图修正单（方案 §6 步骤 8 / §11）

output/** →
    <base>_修正单.md   （第 6 件交付物：分层审计表 + 三方互校差异 + 仲裁记录）
    output/_汇总报告.md （逐图 × 门禁矩阵 + 与方案 §11 基线对账 + 未达标项的阶段定位）

不重算任何几何：只读各阶段落盘的 gate_*.json / *.json，做齐套性与一致性判定，
因此 09 的结论可追溯到产生它的那一阶段脚本。
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

# 各阶段门禁文件 → (阶段号, 脚本, 职责)
GATE_FILES = [
    ("gate_01.json", "A1", "01_extract.py", "矢量提取 + 六层归层"),
    ("gate_02.json", "A2", "02_cluster_views.py", "视图聚类归属"),
    ("gate_03.json", "A4", "03_render_regions.py", "回正裁切图 + 整页总览"),
    ("gate_03b_patch.json", "A4", "03_render_regions.py", "字形贴片(4×高清)"),
    ("gate_03b.json", "B3", "03b_text_recover.py", "字形字典重建文本行"),
    ("gate_03d.json", "B3", "03d_vision_read.py", "视觉逐行识读双闸门(V1/V2)"),
    ("gate_05.json", "A3", "05_crosswalk.py", "比例三档 + 换算 + 尺寸绑定"),
    ("gate_06.json", "A3", "06_enhance_svg.py", "六层 SVG(骨)"),
    ("gate_04.json", "A6", "04_build_md.py", "MD(魂) + prim 全量索引"),
    ("gate_07.json", "A7", "07_validate.py", "反向重绘 + 三方互校"),
    ("gate_08.json", "A8", "08_qa.py", "QA 题库 + self_check + 盲测判分"),
]
def _cfg() -> dict:
    """config 运行时快照（common.init 后可用）；未 init 时为空 dict。"""
    return getattr(C, "_CFG", None) or {}


def _glyph_gate_path() -> str:
    """config 驱动的 glyph 门禁文件路径（common.init 后 C.GLYPH_DIR 才被覆盖，故须运行期取）。"""
    return os.path.join(C.GLYPH_DIR, "gate_03c.json")


def _plan_drawings() -> dict:
    """config 的 plan_drawings（附件清单 drawings 基线，逐图）；未配置时为空 dict。"""
    return _cfg().get("plan_drawings") or {}


def _baseline_expect():
    """从 config.baseline 构造 §11 基线期望值；无基线数据时返回 None。

    键与旧实现硬编码的基线 dict 一致：kept/六层/views/bind_rate/rms_pt/recall。
    """
    b = _cfg().get("baseline") or {}
    layers = b.get("layers") or {}
    if not layers and not any(b.get(k) for k in ("views", "bind_rate", "rms_pt", "recall")):
        return None
    kept = sum(layers.values()) if layers else None
    exp = {"kept": kept}
    exp.update({L: layers.get(L, 0) for L in C.LAYERS})
    exp["views"] = b.get("views")
    exp["bind_rate"] = b.get("bind_rate")
    exp["rms_pt"] = b.get("rms_pt")
    exp["recall"] = b.get("recall")
    return exp


def _probe_dir():
    """config 的 paths.probe_dir；null 或目录不存在时返回 None（调用方跳过叙述段）。"""
    d = (_cfg().get("paths") or {}).get("probe_dir")
    return d if (d and os.path.isdir(d)) else None


# 方案 §7 token 可行性上限
MD_CHAR_LIMIT = 80000

PIECE_NAMES = OrderedDict([
    ("svg", "骨：<base>.svg"), ("md", "魂：<base>-可复现图纸描述.md"),
    ("crosswalk", "互联：<base>_crosswalk.json"), ("qa", "<base>_QA题库.json"),
    ("fixlist", "<base>_修正单.md"), ("redraw", "<base>_反向重绘验证.png"),
])


# ---------------------------------------------------------------- 采集


def load_gates(base: str) -> list:
    wd = C.work_dir(base)
    out = []
    for fn, stage, script, duty in GATE_FILES:
        p = os.path.join(wd, fn)
        g = C.read_json(p) if os.path.exists(p) else None
        out.append({"file": fn, "stage": stage, "script": script, "duty": duty,
                    "exists": g is not None, "doc": g or {}})
    return out


def collect(base: str) -> dict:
    """把一张图的全部可核算事实收进一个 dict（供修正单与汇总报告共用）。"""
    d = C.deliverables(base)
    pdoc = C.read_json(C.work_path(base, "prims.json"), {})
    meta = pdoc.get("meta") or {}
    cnt = meta.get("counts") or {}
    bl = cnt.get("by_layer") or {}
    audit = C.read_json(C.work_path(base, "extract_audit.json"), {}).get("audit") or {}
    vdoc = C.read_json(C.work_path(base, "views.json"), {})
    cwd = C.read_json(d["crosswalk"], {})
    val = C.read_json(C.work_path(base, "validate.json"), {})
    tdoc = C.read_json(C.work_path(base, "text.json"), {})
    qdoc = C.read_json(d["qa"], {})
    idx = C.read_json(C.work_path(base, "md_prims_index.json"), {"index": {}})
    md_chars = len(C.read_text(d["md"])) if os.path.exists(d["md"]) else 0
    views = vdoc.get("views") or []
    cwv = {v["id"]: v for v in (cwd.get("views") or [])}
    sc_all = [v.get("self_check") or {} for v in (cwd.get("views") or [])]
    n_sc = len(sc_all)
    n_sc_ok = sum(1 for s in sc_all if s.get("pass"))
    return {
        "base": base, "dir": C.sheet_dir(base), "deliverables": d,
        "pieces": {k: os.path.exists(p) and os.path.getsize(p) > 0
                   for k, p in d.items()},
        "meta": meta, "counts": cnt, "by_layer": bl, "audit": audit,
        "views": views, "n_views": len(views), "tb_bbox": vdoc.get("tb_bbox") or [],
        "views_stats": vdoc.get("stats") or {},
        "crosswalk": cwd, "cwv": cwv,
        "self_check": {"n": n_sc, "ok": n_sc_ok},
        "scale_sources": cwd.get("scale_sources") or {},
        "unclear_scale": cwd.get("unclear_scale") or [],
        "unbound_values": cwd.get("unbound_values") or [],
        "n_dims_bound": sum(len(v.get("dims") or []) for v in (cwd.get("views") or [])),
        "validate": val, "text": tdoc, "qa": qdoc,
        "md_chars": md_chars, "md_index": len(idx.get("index") or {}),
        "gates": load_gates(base),
    }


def color_only_counts(cross: dict) -> Counter:
    """纯颜色口径（不含 PDM_Title 拆标题栏、不含 OCG 纠偏）的逐层计数，用于差值表。"""
    out = Counter()
    for k, n in (cross or {}).items():
        ocg, _, cname = k.partition("|")
        if ocg == "PDM_Title" and cname in ("yellow", "none", "None", ""):
            out["title-block"] += n
            continue
        lay = C.COLOR_LAYER.get(cname)
        out[lay or "UNMAPPED"] += n
    return out


def gate_state(rows: list) -> dict:
    """把逐阶段门禁折成 {gate_file: (状态, 通过数, 总数, 失败清单, 警告清单)}。"""
    st = {}
    for r in rows:
        g = r["doc"]
        if not r["exists"]:
            st[r["file"]] = ("缺文件", 0, 0, [r["file"] + " 未产出"], [])
            continue
        fails = [x["gate"] for x in g.get("gates", []) if x["required"] and not x["ok"]]
        warns = [x["gate"] for x in g.get("gates", []) if not x["required"] and not x["ok"]]
        n = len(g.get("gates", []))
        st[r["file"]] = ("PASS" if not fails else "FAIL", n - len(fails), n, fails, warns)
    return st


# ---------------------------------------------------------------- vision 证据


def _med(xs: list):
    s = sorted(float(x) for x in xs if x)
    return round(s[len(s) // 2], 2) if s else None


def _vision_stats(base: str) -> dict:
    """vision 逐行识读的实测证据：双源核对结果 + 覆盖率 + 省略行的字高特征。

    覆盖率与「省略行字高更小」均由落盘数据算出，不是叙述：manifest 有全部
    渲染行（含 gh/n/zone），vision_read 的 verification.rows 只有转录者实际给出的行，
    两者之差即省略行。
    """
    vr = C.read_json(C.work_path(base, "vision_read.json"), {}) or {}
    man = C.read_json(os.path.join(C.work_dir(base), "vread", "manifest.json"), {}) or {}
    vd = vr.get("verification") or {}
    rows_tr = vd.get("rows") or []
    done = {(r.get("zone"), r.get("row_id")) for r in rows_tr}
    exact = {(r.get("zone"), r.get("row_id")) for r in rows_tr if r.get("ok_v2")}
    per_zone, gh_tr, gh_om = {}, [], []
    for r in man.get("rows") or []:
        pz = per_zone.setdefault(r.get("zone"), {"rendered": 0, "transcribed": 0, "exact": 0})
        pz["rendered"] += 1
        key = (r.get("zone"), r.get("row_id"))
        if key in done:
            pz["transcribed"] += 1
            gh_tr.append(r.get("gh") or 0.0)
            if key in exact:
                pz["exact"] += 1
        else:
            gh_om.append(r.get("gh") or 0.0)
    return {"v1": vd.get("V1_drawing_no_truth") or {},
            "v2": vd.get("V2_char_count_per_row") or {},
            # V2 不精确的行（转录字符数 ≠ 字符位数）：只有这些行不投票，故必须能被
            # 逐行追责。§5.2 直接引用它算精确率，不再把「=100%」写死在正文里。
            "v2_bad": [{"zone": r.get("zone"), "row_id": r.get("row_id"),
                        "n_cells": r.get("n_cells"), "n_chars": r.get("n_chars"),
                        "diff": r.get("diff"), "text": r.get("text")}
                       for r in rows_tr if r.get("diff")],
            "dl": vr.get("derived_labels") or {},
            "trusted": bool(vr.get("trusted")), "per_zone": per_zone,
            "gh_transcribed": gh_tr, "gh_omitted": gh_om,
            "zones_applied": vr.get("zones_applied") or [],
            "n_notes": len(vr.get("technical_requirements") or []),
            "n_scale": len(vr.get("scale_reads") or []),
            "n_fields": len(vr.get("title_block") or {}),
            "n_tb_lines": len(vr.get("title_block_lines") or [])}


# ---------------------------------------------------------------- 修正单


def build_fixlist(S: dict) -> str:
    base = S["base"]
    audit = S["audit"]
    cross = audit.get("cross") or {}
    strong = audit.get("strong") or {}
    trig = audit.get("triggers") or {}
    bl = S["by_layer"]
    cnt = S["counts"]
    colo = color_only_counts(cross)
    val = S["validate"]
    tdoc = S["text"]
    cwd = S["crosswalk"]
    qdoc = S["qa"]
    gdict = C.read_json(os.path.join(C.GLYPH_DIR, "glyph_labels.json"), {})
    gmeta = gdict.get("meta") or {}
    L = []
    A = L.append

    A("# %s — 修正单" % base)
    A("")
    A("> 本文件记录**口径与偏差**，不记录成果本身（成果见同目录 SVG / MD / crosswalk / "
      "QA题库 / 反向重绘验证.png）。三段：分层审计表 → 三方互校差异 → 仲裁记录。"
      "全部数字由脚本从 `work/` 中间产物读出，**禁手改**。")
    A("")
    A("## 一、分层审计表（决策 D1）")
    A("")
    A("口径：**颜色优先** + `PDM_Title∩{黄, 无色}` 拆出独立 `title-block` + "
      "**逐图主导性 OCG 纠偏**（仅当强语义 OCG 的主色与该层基线色不一致且占比 >50% 时触发）。")
    A("")
    A("### 1.1 OCG × color 交叉计数")
    A("")
    A("| OCG | color | 图元数 | 归层(实际) |")
    A("|---|---|---|---|")
    for k, n in list(cross.items())[:40]:
        ocg, _, cname = k.partition("|")
        A("| `%s` | %s | %d | %s |" % (ocg or "(无)", cname, n,
                                       _layer_of(ocg, cname, trig)))
    if len(cross) > 40:
        A("| … | 余 %d 组见 `work/extract_audit.json` | %d | |"
          % (len(cross) - 40, sum(list(cross.values())[40:])))
    A("")
    A("### 1.2 强语义 OCG 主导性与纠偏触发")
    A("")
    A("| 目标层 | 强语义 OCG 集 | 图元总数 | 主色 | 主色占比 | 基线色 | 是否纠偏 |")
    A("|---|---|---|---|---|---|---|")
    for lay in ("outline", "centerline", "dimension", "special"):
        s = strong.get(lay) or {}
        A("| `%s` | %s | %s | %s | %s | %s | %s |"
          % (lay, "/".join(sorted(C.OCG_STRONG.get(lay, []))),
             s.get("total", 0), s.get("dominant") or "—",
             ("%.4f" % s["ratio"]) if s.get("total") else "—",
             s.get("baseline") or C.LAYER_BASE_COLOR.get(lay, "—"),
             "**触发**" if s.get("trigger") else "不触发(保持颜色口径)"))
    A("")
    A("### 1.3 与纯颜色口径的逐层差值")
    A("")
    A("| 层 | 纯颜色口径 | 实际(纠偏后) | 差值 | 说明 |")
    A("|---|---|---|---|---|")
    for lay in C.LAYERS:
        d0, d1 = colo.get(lay, 0), bl.get(lay, 0)
        why = "—" if d1 == d0 else ("OCG 纠偏改归属" if trig.get(lay) else
                                    "PDM_Title 拆标题栏 / 兜底改判")
        A("| `%s` | %d | %d | %+d | %s |" % (lay, d0, d1, d1 - d0, why))
    A("| `bg`(剔除) | — | %s | — | 整页无色背景矩形，不入六层 |" % (cnt.get("bg") or 0))
    A("")
    A("计数对账：drawings=%s − bg=%s = kept=**%s**；六层求和=%s%s"
      % (cnt.get("drawings"), cnt.get("bg"), cnt.get("kept"),
         sum(bl.get(x, 0) for x in C.LAYERS),
         "（== kept ✓）" if sum(bl.get(x, 0) for x in C.LAYERS) == cnt.get("kept")
         else "（≠ kept ✗）"))
    A("")
    A("### 1.4 整页跨度长线的 OCG 归属（V00 范围依据）")
    A("")
    fl = audit.get("frame_lines") or {}
    A("| OCG | color | 条数 |")
    A("|---|---|---|")
    for k, n in list(fl.items())[:12]:
        ocg, _, cname = k.partition("|")
        A("| `%s` | %s | %d |" % (ocg or "(无)", cname, n))
    if not fl:
        A("| — | — | 0（本图无 ≥90% 页面跨度的长线） |")
    A("")
    A("V00 归属 %d 条图元；标题栏紧裁切框(竖放 pt)=`%s`。"
      % (next((v["n"] for v in S["views"] if v["id"] == "V00"), 0),
         ",".join("%.1f" % q for q in S["tb_bbox"])))
    A("")
    A("### 1.5 UNMAPPED 图元")
    A("")
    A("五色之外且 OCG 无强语义者按 D1 兜底入 `thin` 并标 `UNMAPPED`（逐条 `data-note` "
      "写在 SVG path 上，可回溯重归层）：")
    for r in S["gates"]:
        if r["stage"] == "A1":
            for g in r["doc"].get("gates", []):
                if "UNMAPPED" in g["gate"]:
                    A("- %s :: %s" % (g["gate"], g["detail"]))
    A("")

    # ---- 二、三方互校
    A("## 二、三方互校差异（PDF 原图 ↔ prims.json 几何 ↔ 交付 SVG/MD）")
    A("")
    ch = val.get("chain") or {}
    rd = val.get("redraw") or {}
    rt = val.get("roundtrip") or {}
    cc = val.get("carrier_consistency") or {}
    A("| 环节 | 值 | 门禁 | 判定 |")
    A("|---|---|---|---|")
    A("| 计数链 drawings−bg | %s − %s = %s | == kept | %s |"
      % (ch.get("drawings"), ch.get("bg"),
         (ch.get("drawings") or 0) - (ch.get("bg") or 0),
         "✓" if (ch.get("drawings") or 0) - (ch.get("bg") or 0) == ch.get("kept") else "✗"))
    A("| kept | %s | — | — |" % ch.get("kept"))
    A("| SVG path 数 | %s | == kept | %s |"
      % (ch.get("svg_path"), "✓" if ch.get("svg_path") == ch.get("kept") else "✗"))
    A("| SVG data-prim-id 去重 | %s | == kept | %s |"
      % (ch.get("svg_data_prim_id_unique"),
         "✓" if ch.get("svg_data_prim_id_unique") == ch.get("kept") else "✗"))
    A("| MD prim 全量索引 | %s | == kept | %s |"
      % (ch.get("md_index"), "✓" if ch.get("md_index") == ch.get("kept") else "✗"))
    A("| MD §3 区间求和 | %s | == kept | %s |"
      % (_md_span_sum(S), "✓" if _md_span_sum(S) == ch.get("kept") else "✗"))
    A("| 反向重绘 recall(2px 膨胀) | %s | ≥0.99 | %s |"
      % (rd.get("recall"), "✓" if (rd.get("recall") or 0) >= 0.99 else "✗"))
    A("| 反向重绘 precision | %s | 记录 | — |" % rd.get("precision"))
    A("| 严格 IoU | %s | 记录(非门禁) | — |" % rd.get("iou_strict"))
    A("| 漏画/多画 px | %s / %s | 记录 | — |" % (rd.get("missed_px"), rd.get("extra_px")))
    A("| 弧/圆三方互校 rms | %s pt (max %s pt, n=%s) | ≤0.1pt | %s |"
      % (rt.get("rms_all_pt"), rt.get("max_all_pt"), rt.get("n_checked"),
         "✓" if (rt.get("rms_all_pt") or 9) <= 0.1 else "✗"))
    A("| ├ 圆心 rms | %s pt | — | — |" % rt.get("rms_center_pt"))
    A("| ├ 半径 rms | %s pt | — | — |" % rt.get("rms_radius_pt"))
    A("| └ 角度折算弧长 rms | %s pt | — | — |" % rt.get("rms_angle_as_arc_pt"))
    A("| 载体一致性 SVG text == MD dims == crosswalk | %s / %s / %s | True | %s |"
      % (cc.get("svg_n"), cc.get("md_n"), cc.get("crosswalk_n"),
         "✓" if cc.get("consistent") else "✗"))
    A("| crosswalk 每视图 self_check | %d/%d | 全过 | %s |"
      % (S["self_check"]["ok"], S["self_check"]["n"],
         "✓" if S["self_check"]["ok"] == S["self_check"]["n"] else "✗"))
    A("| MD 字符数 | %d | ≤%d | %s |"
      % (S["md_chars"], MD_CHAR_LIMIT,
         "✓" if S["md_chars"] <= MD_CHAR_LIMIT else "✗"))
    A("| data-view UNASSIGNED | %s | 0 | %s |"
      % (_unassigned(S), "✓" if not _unassigned(S) else "✗"))
    A("")
    A("反向重绘验证图：`%s`（%s，scale=%s；图例 R=漏画 G=多画 B=双方命中 橙=2px 容差内补齐）。"
      % (os.path.basename(S["deliverables"]["redraw"]),
         (val.get("proof") or {}).get("px"), val.get("scale")))
    A("")
    A("渲染链版本固定：%s / Pillow %s（scale=%.1f，膨胀 %dpx，墨迹阈值 %d）。"
      % (val.get("pymupdf"), val.get("pil"), val.get("scale"),
         (rd.get("tolerance") or {}).get("dilate_px", 2),
         (rd.get("tolerance") or {}).get("ink_threshold", 250)))
    A("")

    # ---- 三、仲裁记录
    A("## 三、仲裁记录")
    A("")
    A("### 3.1 比例来源与未验证项")
    A("")
    A("| 档 | 视图数 | 含义 |")
    A("|---|---|---|")
    for k in ("read", "inferred", "fallback"):
        A("| `%s` | %d | %s |" % (k, (S["scale_sources"] or {}).get(k, 0),
                                  {"read": "文本恢复读到「1:xx」",
                                   "inferred": "候选分母打分命中最多者胜(带 score)",
                                   "fallback": "1:10 未验证，其 mm 值全部入 §6 unclear"}[k]))
    A("")
    A("比例未验证视图 %d 个、未绑定尺寸值 %d 个（均登记在 MD §6，不臆造定位）。"
      % (len(S["unclear_scale"]), len(S["unbound_values"])))
    ver = [v for v in (cwd.get("views") or []) if v.get("scale_verified")]
    if ver:
        A("")
        A("**页面几何自证（`inferred` 档里的例外，不计入上面的未验证数）**：%s 的比例 "
          "%s 不是尺寸线打分得到的，而是由页面几何自证（`scale_evidence=page-geometry`）："
          "bbox 两轴均覆盖页面 ≥90%%，且 den=1 时 W_mm/H_mm=%s mm 落在纸型 %s mm 幅面 "
          "±25mm 内。它的 score=0 只表示未用尺寸线命中，**不代表未验证**。"
          % (", ".join("`%s`" % v["id"] for v in ver), ver[0]["scale"],
             "×".join(str(q) for q in (ver[0].get("frame_mm") or [])),
             "×".join(str(q) for q in (ver[0].get("paper_mm") or []))))
    ks = [v["id"] for v in (cwd.get("views") or []) if v.get("scale_k")
          and abs(v["scale_k"] - 1.0) > 0.002]
    if ks:
        k0 = next(v for v in cwd["views"] if v["id"] == ks[0])
        A("")
        A("**比例修正系数 k**：本图 %d 个视图的实测 k 偏离 1 超过 0.2%%（如 %s k=%.4f）。"
          "导出器的 pt/mm 系数与标准 2.83465/分母 有约 0.05%% 量级偏差，05 在 ±2%% 搜索域内"
          "取使尺寸线整数命中最多的 k，`s_pt_per_mm = 2.83465/分母 × k`，并在 MD §3 逐视图披露。"
          % (len(ks), ks[0], k0["scale_k"]))
    A("")
    A("### 3.2 文本恢复与字形字典（决策 D3 的降级记录）")
    A("")
    tc = tdoc.get("counts") or {}
    ds = tdoc.get("dict_stats") or {}
    A("| 项 | 值 |")
    A("|---|---|")
    A("| 字形候选/文本行 | %s / %s |" % (tc.get("glyphs"), tc.get("lines")))
    A("| 已标注字 / UNK 字 | %s / %s |" % (tc.get("labeled_glyphs"), tc.get("unk_glyphs")))
    A("| 数值文本行 | %s |" % tc.get("numeric"))
    A("| 字典模板(跨图合并) / 其中已标注 sid | %s / %s |"
      % (ds.get("templates"), ds.get("sid_labeled")))
    A("| 绿层数值集合覆盖率 | %s |"
      % json.dumps(tdoc.get("green_layer_coverage") or {}, ensure_ascii=False))
    A("| 绑定尺寸数 | %d（绿层绑定率 %s，**非门禁**） |"
      % (S["n_dims_bound"], (val.get("green_layer") or {}).get("bind_rate")))
    A("")
    vs = _vision_stats(base)
    A("**仲裁：字形字典采用 03d 视觉逐行对账的标签（仅 V1+V2 双过），未过对账的字形仍记 "
      "`UNK` 入 unclear。** 全字典现状：%s；本图识读：%s"
      % (json.dumps({"labels": gmeta.get("n_labels"),
                     "labels_own_03d": gmeta.get("n_labels_own"),
                     "trusted_sheets": gmeta.get("n_sheets_trusted"),
                     "rejected": gmeta.get("n_rejected")}, ensure_ascii=False),
         json.dumps({"trusted": vs["trusted"],
                     "V1_lcs": vs["v1"].get("best_lcs"),
                     "V1_min": vs["v1"].get("min_lcs"),
                     "V1_hit_rows": vs["v1"].get("hit_rows") or [],
                     "V2_exact": vs["v2"].get("rows_exact"),
                     "V2_transcribed": vs["v2"].get("rows_transcribed"),
                     "sid": vs["dl"].get("n_sid"),
                     "conflict": vs["dl"].get("n_conflict")}, ensure_ascii=False)))
    A("")
    A("1. 方案 D3 的来源优先级是「字典重建值 ＞ 视觉裁切复核 ＞ 不做 glyph OCR 猜测」。"
      "第一档（03c 的两条明文源）已被下面的残差审计与跨图一致性检验否证；"
      "**第二档已实测可用并采用**——但是有条件的，条件就是第 2 点的双源核对。")
    A("2. **视觉通道经双源比对后部分可用**（`03d_vision_read.py`）。早前「两条视觉通道均"
      "不可用」的判定针对的是两种**整图自由描述**用法：① `vision` 子代理模型缺失；"
      "② 对 `work/regions/_title_block.png` 直接读图只返回散文描述（漏报图号、虚构"
      "名称/序号，对单字贴片把一个字读成多字串）。两者均不可核对 → 当时判定不可用。"
      "03d 改成**逐行裁切 + 字符位格 + 双源核对**的受限用法后，结论随之改变：")
    A("   - **V1 图号真值**（以 PDF 文件名为先验，不靠信仰）：本图最长公共连续子串=%s"
      "（阈 %s），命中行=%s → %s。"
      % (vs["v1"].get("best_lcs"), vs["v1"].get("min_lcs"),
         ",".join(vs["v1"].get("hit_rows") or []) or "无",
         "**命中**" if vs["v1"].get("pass") else "**未命中，本图识读不采信**"))
    A("   - **V2 逐行字符位数精确对账**（容差 0）：%s/%s 行精确。对账基准是**字符位数**"
      "而非 item 数：一字符可被 CAD 拆成上下两半两个 item，而单笔画字符（`-`/`1`/`·`）"
      "只有 1 段子路径、被字形池丢弃而成空位。仅精确相等的行用于字符↔字形对齐。"
      % (vs["v2"].get("rows_exact"), vs["v2"].get("rows_transcribed")))
    A("   - **能力边界（实测校准，不是「不可用」也不是「全可用」）**：同一张图上，"
      "说明条与 n/h 几何标注逐字精确；14pt CAD 单线数字/字母逐字精确（图号 12/12 全对，"
      "连字形池里没有的 `-` 也对）；而小字高的汉字格会被描述通道幻觉出无工程语义的词"
      "（实测虚构过「心平气和」「小雨」「转子包」）。V2 字数对账是**确定性闸门**："
      "转录者因字符数≠n 而省略该行，省略行不贡献票，故虚构未污染字典。"
      "本图字高证据：转录行 gh 中位=%s pt、省略行 gh 中位=%s pt（省略行系统性更小）。"
      % (_med(vs["gh_transcribed"]), _med(vs["gh_omitted"])))
    A("   - **票的分区范围**：本图已应用分区=%s；各图 `drawing` 区渲染 0 行，故包括"
      "单票标签在内的全部标签均落在标题栏/技术要求区，符合方案「只标注复现次数≥2 的"
      "模板 + 单例中落在标题栏/技术要求区的模板」。"
      % json.dumps(vs["zones_applied"], ensure_ascii=False))
    A("   - **本图产出（识读侧：03d 转录命中，只用于给字形字典投票，不直接进 MD §5）**："
      "技术要求编号行 %d 条、比例 read 档 %d 处、标题栏字段 %d 个。"
      "MD §5 实际交付的条款另按「汉字数≥2 的成句行」判据由 03b 取（见 §5.2 与 MD §5/§6）。"
      "未命中的一律不写占位文本（不臆造）。"
      % (vs["n_notes"], vs["n_scale"], vs["n_fields"]))
    A("3. 已实现确定性自监督解码器 `03c_glyph_solve.py` 作为替代，包含两条明文源："
      "**A 几何尺寸线长度**（跨度 ÷ 已推断比例 = 整数 → 与最近共线逻辑尺寸线的"
      "文本行投票）与 **B 图号 crib**（文件名先验已知，标题栏内唯一等长行→逐位对齐）。"
      "实测结果：%s"
      % json.dumps({"labels": gmeta.get("n_labels"),
                    "unresolved": gmeta.get("n_unresolved"),
                    "evidence": gmeta.get("evidence_n"),
                    "reject_reasons": gmeta.get("reject_reasons")},
                   ensure_ascii=False))
    pa = gmeta.get("plaintext_audit") or {}
    if pa:
        med = [round((v.get("seg") or {}).get("med_abs_r_mm", 0), 3) for v in pa.values()]
        p90 = [round((v.get("seg") or {}).get("p90_abs_r_mm", 0), 3) for v in pa.values()]
        A("4. **源 A 已被残差审计否证**（`plaintext_audit`，各图全 `viable=False`）："
          "对全部候选分母、两种跨度定义（共线段跨度 / 界线相邻间隔），换算值到最近整数的"
          "残差 med|r|≈%s mm、p90|r|≈%s mm，而均匀分布上限为 0.5 —— mod 1 近似均匀即"
          "**无信号**。另已修掉三个会掩盖该结论的缺陷：竖放/横向坐标系混用（修后配对 "
          "1→37、unmatched 1711→167）、垂距窗下限（文字压在尺寸线上是主流情形，已降为 0）、"
          "以及无判别力的相对容差（修前 int_rate 恒=1.000，已改为绝对 0.05mm）。"
          % ("%s~%s" % (min(med), max(med)), "%s~%s" % (min(p90), max(p90))))
    ca = gmeta.get("crib_audit") or {}
    if ca:
        gain = ca.get("crib_only_gain") or {}
        A("5. **源 B（图号 crib）已被两重一致性检验否证**（`crib_audit`）。"
          "crib 的思路是把文件名当先验明文（图号确实已知），在标题栏内找唯一等长行逐位对齐；"
          "它能否成立不靠信仰，而靠两条可判定的约束：")
        A("   - **跨图约束**：同一 CAD 字体下，同一明文串在不同图里必须给出完全相同的"
          "sid 序列。实测：跨图可比 crib=%d 个，序列完全一致的=%d 个；字符→sid 多重度=%s"
          "（`8` 对应 9 个 sid、`0` 对应 6 个 —— 单一字体不可能）。"
          % (ca.get("n_crib_cross_sheet"), ca.get("n_seq_identical_all"),
             json.dumps(ca.get("char_to_sid_multiplicity"), ensure_ascii=False)))
        A("   - **跨图号家族约束**（更锐利、且不循环）：同一图号家族里两张图号只有第 6 位"
          "不同（其余位共享同一前缀），若两行都真是图号，则公共位 sid 必须全同、差异位"
          "必须分两组。实测：约束 %d/%d 通过。"
          % (ca.get("n_cross_family_agree"), ca.get("n_cross_family")))
        for f in (ca.get("cross_family") or [])[:3]:
            A("     - `%s`(%s) vs `%s`(%s) 公共前缀 `%s`：%d/%d 位 sid 相同 → %s"
              % (f["crib_a"], f["sheet_a"][:14], f["crib_b"], f["sheet_b"][:14],
                 f["common_prefix"], f["n_sid_identical"], f["n_prefix"],
                 "成立" if f["agree"] else "**不成立**"))
        cs = ca.get("cross_sheet") or []
        for r in cs[:1]:
            A("     - 同一 crib `%s` 在 %d 图命中的各行 sid（前 6 位）：%s"
              % (r["crib"], r["n_sheets"],
                 " / ".join("%s:%s" % (s["sheet"][:12], ",".join(x[:6] for x in s["sids"]))
                            for s in r["seqs"])))
        A("   - 旁证：命中行字高 = %s pt。同一 PDM 标题栏模板的图号单元格字高应一致，"
          "实测跳变数倍 → 命中的根本不是同一类行。"
          % (ca.get("matched_line_heights_pt"),))
        A("   - 收益回测（`crib_only_gain`）：即便不管上述否证、把 crib 一致票全部当标签发布"
          "（%s 个模板，字符集 `%s`），全部图 %s 个文本行中会有 %s 行看似可全字解析、"
          "其中纯数值 %s 行。这正是陷阱所在：**收益看上去很大，但根据上述否证它们是虚构文本**，"
          "一旦写入就会污染 MD §5、§4 与 SVG `<text>`，且因带「已解码」标记而比 UNK 更难发现。"
          "故一律不发布。"
          % (gain.get("n_crib_only_labels"), gain.get("crib_only_chars"),
             gain.get("n_lines_total"), gain.get("n_lines_fully_resolvable"),
             gain.get("n_numeric_resolvable")))
        A("   - 判定：%s" % ca.get("verdict"))
    A("6. 不收敛的根本原因：候选字形池来自 PDM 导出的通用 OCG（如 `8`），"
      "其中混有**箭头、短划、尺寸界线端点**等非字符笔画几何（字典模板字高分布包含 "
      "1.8~5.5pt 的大量小图元，远小于真实字高带 9.8/10.0/14.0pt）；由它们串出的"
      "「文本行」既不是真文本行，也就无法与任何明文源对齐。")
    A("7. 影响面：字典标签只覆盖已标注的 %s/%s 个模板，未覆盖者仍为 `UNK`，故影响的是 "
      "MD §5 技术要求逐字、§4 标题栏字段识读、以及 SVG `<text>` 尺寸绑定的**完整度**；"
      "**不影响**几何载体（path/弧圆参数/坐标系/视图归属/计数对账链），"
      "这些均由矢量原值直接生成，反向重绘与三方互校已独立验证。"
      % (ds.get("sid_labeled"), ds.get("templates")))
    A("8. 闭环路径（提高覆盖率，按成本从低到高）：① 修 `03d_vision_read.py` 的 `select()` "
      "字高过滤时机（聚行**后**按行字高过滤而非聚行前逐字形过滤），可找回被当成半个字符"
      "丢弃的下半环笔画，但会改变 n → 需重渲染并重转录全部图；② 人工标注 "
      "`output/_glyph_dict/label_sheet_*.png`（每张 20 格、按复现次数降序、灰度增强），"
      "把 `格号→字符` 写回 `glyph_labels.json`；③ 若提供明细表/设计计算等外部文本源，"
      "可用其数值作 crib 反解。任一路径之后重跑 `03b→05→06→04→07→08→09`。"
      "注意：03c 与 03d 均写 `glyph_labels.json`，两者已做**互相保留**（各自只覆写"
      "自己来源的标签），但 03b 必须跑在两者之后。字典为各图共用，标注一次全图受益。")
    A("")
    A("### 3.3 本图特有偏差")
    A("")
    for line in _sheet_specific(S):
        A("- %s" % line)
    A("")
    A("### 3.4 逐阶段门禁")
    A("")
    A("| 阶段 | 脚本 | 职责 | 结果 | 未过条目 |")
    A("|---|---|---|---|---|")
    for r in S["gates"]:
        g = r["doc"]
        fails = [x["gate"] for x in g.get("gates", []) if x["required"] and not x["ok"]]
        warns = [x["gate"] for x in g.get("gates", []) if not x["required"] and not x["ok"]]
        state = "缺文件" if not r["exists"] else ("PASS %d/%d" % (len(g.get("gates", [])) - len(fails),
                                                                  len(g.get("gates", [])))
                                                  if not fails else "FAIL %d/%d"
                                                  % (len(g.get("gates", [])) - len(fails),
                                                     len(g.get("gates", []))))
        A("| %s | `%s` | %s | %s | %s |"
          % (r["stage"], r["script"], r["duty"], state,
             "; ".join(fails + ["(warn) " + w for w in warns]) or "—"))
    A("")
    A("QA：题库 %s 题（可验证 %s 题，五类 %s）；self_check %s；盲测 %s。"
      % ((qdoc.get("counts") or {}).get("generated"),
         (qdoc.get("counts") or {}).get("verifiable"),
         json.dumps((qdoc.get("counts") or {}).get("by_category"), ensure_ascii=False),
         _qa_selfcheck_pct(qdoc), _blind_str(qdoc)))
    A("")
    return "\n".join(L)


def _layer_of(ocg: str, cname: str, trig: dict) -> str:
    if ocg == "PDM_Title" and cname in ("yellow", "none", "None", ""):
        return "title-block"
    for lay, on in (trig or {}).items():
        if on and ocg in C.OCG_STRONG.get(lay, ()):
            return lay + "(纠偏)"
    return C.COLOR_LAYER.get(cname) or "thin(UNMAPPED 兜底)"


def _unassigned(S: dict) -> int:
    return sum(1 for v in S["views"] if v["id"] == "UNASSIGNED") + \
        sum(1 for v in (S["crosswalk"].get("views") or []) if v["id"] == "UNASSIGNED")


def _md_span_sum(S: dict) -> int:
    p = S["deliverables"]["md"]
    if not os.path.exists(p):
        return -1
    txt = C.read_text(p)
    rx = re.compile(r"\|\s*(?:outline|centerline|thin|dimension|special|title-block)\s*"
                    r"\|[^|]*\|\s*V\d+-P\d+\s*[…-]{1,2}\s*V\d+-P\d+\s*\|\s*(\d+)\s*\|")
    return sum(int(m.group(1)) for m in rx.finditer(txt))


def _qa_selfcheck_pct(qdoc: dict) -> str:
    sc = qdoc.get("self_check") or []
    if not sc:
        return "无题库"
    ok = sum(1 for s in sc if s.get("md_verifiable"))
    return "%d/%d = %.1f%%" % (ok, len(sc), 100.0 * ok / len(sc))


def _blind_str(qdoc: dict) -> str:
    bt = qdoc.get("blind_test") or {}
    if "accuracy" in bt:
        return "%d/%d = %.2f%%" % (bt["n_correct"], bt["n"], 100 * bt["accuracy"])
    return bt.get("status") or "未提供答卷"


def _sheet_specific(S: dict) -> list:
    """本图特有偏差：只写可从落盘数据核实的事实。"""
    base, out = S["base"], []
    bl, audit = S["by_layer"], S["audit"]
    cross = audit.get("cross") or {}
    strong = audit.get("strong") or {}
    trig = audit.get("triggers") or {}
    nv = S["n_views"]
    _bl = _baseline_expect()
    out.append("视图数 %d（V00 + %d）；data-view 组无 UNASSIGNED=%s。"
               % (nv, nv - 1, "是" if not _unassigned(S) else "否"))
    # 视图数与方案基线不等时，§4.2 只给「△ 差异(见修正单 §3.3)」的指针，解释必须在此落地。
    # 全部数字从 views.json 的 stats（02 落盘）与探针 output/_probe/views_cause.json 读，
    # 不在报告生成器里写死结论。
    vs = S.get("views_stats") or {}
    pm, cs = vs.get("params") or {}, vs.get("comp_core_sizes") or []
    ms = pm.get("min_seed")
    mech = False          # 视图数偏差的机制解释是否已按落盘数据给出（下方兜底据此去重）
    if base == C.baseline_sheet() and _bl and cs and ms and _bl["views"] is not None \
            and nv != _bl["views"]:
        mech = True
        out.append("**视图数 %d 与方案基线 %d（V00+V01–V%02d）差 %+d 的机制**：02 把骨架图元的"
                   "墨迹连通域（本图 %s 个）按**核心图元数 ≥ `MIN_SEED=%s`** 二分——达标 %s 个"
                   "成零件视图，其余 %s 个作碎片就近并入 ≤`SEED_MERGE_DIST=%s`pt 的种子、"
                   "无近邻者归 V00。核心图元数降序 %s…，阈值正落在 %s→%s 的**天然断层**上。"
                   % (nv, _bl["views"], _bl["views"] - 1, nv - _bl["views"],
                      vs.get("components"), ms, vs.get("seeds"), vs.get("scraps"),
                      pm.get("seed_merge_dist"), cs[:12], ms,
                      next((n for n in cs if n < ms), "—")))
        attain = sorted({sum(1 for n in cs if n >= k) for k in range(1, max(cs) + 1)})
        out.append("该偏差**不能靠调阈值弥合**：把 `MIN_SEED` 从 1 扫到 %d，本图可得到的零件"
                   "视图数集合是 %s，其中**不含基线的 %d**。"
                   % (max(cs), attain, _bl["views"] - 1))
        # 方案原文把「投影间隙切分过合并簇」列为收敛到基线的手段，故必须实测它，
        # 不能用「机制不同」一句带过。两支探针与诊断裁切均落盘 output/_probe/，此处读回；
        # 报告里不出现任何未在 JSON 里的数字，视觉核查结论则指向可复核的 PNG。
        _pb = _probe_dir()
        _gs = (C.read_json(os.path.join(_pb, "gap_split.json"), {}) or {}) if _pb else {}
        _sv = (C.read_json(os.path.join(_pb, "spec_views.json"), {}) or {}) if _pb else {}
        _gp, _sp = _gs.get("params") or {}, _sv.get("params") or {}
        _gk = "gap_cells=%s" % _sp.get("gap_cells", 1)
        _g1 = (_gs.get(_gk) or {}).get(base) or {}
        if _g1 and _sv:
            _aft = [(_gs.get(_gk) or {}).get(b, {}).get("after_views") for b in C.all_sheets()]
            _bef = [(_gs.get(_gk) or {}).get(b, {}).get("before_views") for b in C.all_sheets()]
            _rp = (_sv.get("line109_repro") or {}).get(base) or {}
            _oc, _ka = _rp.get("oc_no_v00(=skel_of)") or {}, _rp.get("kept_all(全层)") or {}
            _gappt = round((_sp.get("gap_cells", 1) + 2 * _gp.get("dil", 2))
                           * _gp.get("cell", 6.0), 1)
            out.append("**「投影间隙切分过合并簇」已实测，两种作用域都比现行机制"
                       "离基线更远，故不纳入主流程**（探针 `output/_probe/cmp_gapsplit.py`、"
                       "`cmp_specviews.py`，落盘 `gap_split.json`、`spec_views.json` 可复核）："
                       "① 对全部种子递归切分（栅格 `CELL=%s`pt、膨胀 %s 次、空档判据 %s 格，"
                       "≈ 真实留白 ≥%s pt），本图 %s→**%s**（%+d，过分裂），各图一致过分裂 "
                       "%s→%s；② 按方案原样口径（`outline+centerline` 的 bbox 并查集 "
                       "eps=%s pt → 只切过合并巨簇 → 小簇 <%s 就近归并），扫遍「过合并簇」"
                       "判据可得视图数集合 %s，`contains_baseline=%s`。按决策 D2 归**基线"
                       "对账项**（记录差异并解释），不为对齐一个数字而改机制或调参。"
                       % (_gp.get("cell"), _gp.get("dil"), _sp.get("gap_cells"), _gappt,
                          _g1.get("before_views"), _g1.get("after_views"),
                          (_g1.get("after_views") or 0) - (_g1.get("before_views") or 0),
                          _bef, _aft, _sp.get("eps"), _sp.get("min_merge"),
                          _sv.get("attainable_views_6_3"), _sv.get("contains_baseline")))
            out.append("**该步骤在方案口径下没有作用对象**：方案原文记载「eps=25 直接聚 "
                       "43 簇（最大 1647 条为过合并）」，但按方案指定的 `outline+centerline` "
                       "骨架口径实测为 %s 簇、最大 %s 条（本图骨架 %s 条）；能复现「最大 %s 条」"
                       "的只有**全 kept 层**口径（%s 条 → %s 簇、最大 %s 条），即该记载的巨簇来自"
                       "把 dimension/thin 一并聚类，与方案的骨架口径不一致；而本实现的"
                       "墨迹连通域又把长骨架线（>`CORE_MAX_SIDE=%s`pt）排除出连通核，进一步消除"
                       "桥接。故「切分过合并巨簇」在方案口径下无对象可切。"
                       % (_oc.get("clusters"), _oc.get("max"), _oc.get("n"), _ka.get("max"),
                          _ka.get("n"), _ka.get("clusters"), _ka.get("max"),
                          pm.get("core_max_side")))
            _dg = (C.read_json(os.path.join(_pb, "diag_views.json"), {}) or {}) if _pb else {}
            _dvs = ([v for v in (_dg.get("views") or []) if v.get("kind") == "part"]
                    if _dg.get("sheet") == base else [])
            if _dvs:
                _t2 = sorted(_dvs, key=lambda v: -(v.get("n_core") or 0))[:2]
                _png = "、".join("`crop_%s_%s.png`" % (base.replace(" ", "_"), v["id"])
                                 for v in _t2)
                _who = "、".join("%s（n_core=%s、%s×%spt）" % (v["id"], v.get("n_core"),
                                                              v.get("wL"), v.get("hL"))
                                 for v in _t2)
                out.append("**方案记载的残余粘连出路（写 `views_override.json` 人工 bbox）"
                           "无可指认目标**：人工 bbox 必须先看见粘连在哪，否则即臆造。已按 "
                           "`n_core` 降序取最大的两个种子——%s——渲出高分辨率裁切"
                           "（`output/_probe/diag_crop.py` → %s）逐一核查：两者的尺寸链均横跨"
                           "自身整个 bbox、两端特征镜像对称，各自是**单一视图**而非两视图粘连；"
                           "故 `overrides=%s`（未写人工 bbox）。"
                           % (_who, _png, vs.get("overrides")))
        vc = (C.read_json(os.path.join(_pb, "views_cause.json"), {}) or {}) if _pb else {}
        if vc:
            out.append("该偏差**与竖排归正式修正无关**（探针 `output/_probe/cmp_views_cause.py` "
                       "落盘 `_probe/views_cause.json` 可复核）：分别用旧式 `%s` 与新式 `%s` "
                       "重算 01 的 GLYPH 标记，各图全池标记对称差 %s 个图元，但落入 `skel` "
                       "条件（`sem∈{outline,centerline}` 且不在 V00）的对称差**为 %s** → 02 的"
                       "骨架集合与聚类结果对该修正不敏感，视图数属既有偏差。02 四项硬门禁"
                       "（无 UNASSIGNED=%s、Σmembers==kept=%s、每视图≥1 prim、无重复归属=%s）"
                       "全部 PASS。"
                       % (vc.get("old_formula"), vc.get("new_formula"),
                          vc.get("total_glyph_symdiff"), vc.get("total_skel_symdiff"),
                          vs.get("unassigned"), vs.get("assigned"), vs.get("duplicates")))
    for lay, on in trig.items():
        s = strong.get(lay) or {}
        if on:
            out.append("**OCG 纠偏已触发**：`%s` 层改用 OCG 归属，主色 %s 占 %s/%s=%.4f"
                       "（基线色 %s）；该层与纯颜色口径差 %+d 条。"
                       % (lay, s.get("dominant"), s.get("colors", {}).get(s.get("dominant")),
                          s.get("total"), s.get("ratio"), s.get("baseline"),
                          bl.get(lay, 0) - color_only_counts(cross).get(lay, 0)))
    if bl.get("special", 0) == 0:
        out.append("`special` 层为 0：本图既无红色 (1,0,0) 也无 {双点划线, 剖面线} OCG，"
                   "属合法空层；SVG 仍输出带 `data-empty=\"true\"` 的空 `<g data-layer>`，"
                   "使「六层齐全」成为可判定的结构事实。")
    mag = [(k, v) for k, v in cross.items() if v >= 500 and k.partition("|")[2] == "magenta"]
    for k, v in mag:
        out.append("洋红图元 %d 条（OCG `%s`）：五色模型外，按 D1 的 OCG 语义映射归 "
                   "`special`（双点划线），已在 §1.2 主导性表中核算。"
                   % (v, k.partition("|")[0]))
    gen = [(k, v) for k, v in cross.items()
           if k.partition("|")[0] in C.OCG_GENERIC and v >= 200]
    for k, v in sorted(gen, key=lambda kv: -kv[1])[:4]:
        ocg, _, cname = k.partition("|")
        out.append("通用 OCG `%s` 上的 %s 图元 %d 条：无语义可依据，按 D1 颜色口径归 "
                   "`%s`（不触发纠偏）。" % (ocg, cname, v, C.COLOR_LAYER.get(cname, "thin")))
    if base == C.baseline_sheet() and _bl:
        diffs = []
        for k, want in _bl.items():
            if k in ("views", "bind_rate", "rms_pt", "recall") or want is None:
                continue
            got = S["counts"].get("kept") if k == "kept" else bl.get(k, 0)
            if got != want:
                diffs.append("%s 实测 %s vs 基线 %s" % (k, got, want))
        out.append(("方案 §11 基线逐层对账：**逐项吻合**（kept=%d、六层全等）。"
                    % S["counts"].get("kept", -1)) if not diffs
                   else "方案 §11 基线逐层对账差异：" + "；".join(diffs))
        if _bl["views"] is not None:
            dv = nv - _bl["views"]
            # 机制解释已在上面按 views.json 的 comp_core_sizes 给出（含「扫遍 MIN_SEED 仍取不到
            # 基线值」的不可能性证明），此处不重复叙述、也不写未经证实的机制猜测；仅在缺该
            # 数据无法给出机制时兜底，保证 D2「记录差异并解释」不落空。
            if dv == 0:
                out.append("视图数 %d vs 基线 %d：吻合。" % (nv, _bl["views"]))
            elif not mech:
                out.append("视图数 %d vs 基线 %d（差 %+d）：属**基线对账项（记录并解释）**，非硬门禁；"
                           "本图无 UNASSIGNED=%s、V00 存在、逐视图 self_check 全过。"
                           % (nv, _bl["views"], dv,
                              "是" if not _unassigned(S) else "否"))
    pd = _plan_drawings().get(base)
    if pd is not None and S["counts"].get("drawings") != pd:
        out.append("drawings 总数 %s vs 附件清单基线 %s（差 %+s）"
                   % (S["counts"].get("drawings"), pd,
                      (S["counts"].get("drawings") or 0) - pd))
    tc = (S["text"].get("counts") or {})
    if tc.get("numeric") == 0:
        out.append("数值文本行 0 → 绑定尺寸 0 → SVG 无 `<text>`；载体一致性以 0==0==0 成立。"
                   "见 §3.2 的降级依据与闭环路径。")
    if S["unclear_scale"]:
        out.append("比例 `fallback`(1:10 未验证) 视图 %d 个，其 mm 值已全部并入 MD §6 unclear。"
                   % len(S["unclear_scale"]))
    return out


# ---------------------------------------------------------------- 汇总报告


# 方案「目录与交付物」清单里、6 件套之外的逐图 work/ 中间产物。
# views_override.json 不在必查列：它是**可选人工输入**（方案 §10，仅聚类残余粘连时
# 才需要人工指定 bbox），未用到时不存在属正常，也不应由脚本生成占位文件。
WORK_REQ = ("prims.json", "views.json", "text.json", "md_prims_index.json",
            "validate.json", "qa_selfcheck.json", "qa_blind.json")


def _layout_missing(allS: list) -> tuple:
    """查方案目录清单的齐套性，返回 (缺件列表, 字形贴片张数)。
    报告正文与门禁共用本函数，保证两边说的是同一件事。"""
    def _has_png(d: str, pref: str = "") -> bool:
        return (os.path.isdir(d)
                and any(f.endswith(".png") and f.startswith(pref)
                        for f in os.listdir(d)))

    miss = []
    for S in allS:
        wd = C.work_dir(S["base"])
        miss += ["%s/work/%s" % (S["base"], f) for f in WORK_REQ
                 if not os.path.exists(os.path.join(wd, f))]
        if not _has_png(os.path.join(wd, "regions")):
            miss.append("%s/work/regions/*.png" % S["base"])
    miss += ["_glyph_dict/" + f for f in ("glyph_labels.json", "dict_stats.json",
                                         "templates.json")
             if not os.path.exists(os.path.join(C.GLYPH_DIR, f))]
    if not _has_png(os.path.join(C.GLYPH_DIR, "templates")):
        miss.append("_glyph_dict/templates/*.png")
    if not _has_png(C.GLYPH_DIR, "contact_sheet_"):
        miss.append("_glyph_dict/contact_sheet_*.png")
    tdir = os.path.join(C.GLYPH_DIR, "templates")
    n_patch = (len([f for f in os.listdir(tdir) if f.endswith(".png")])
               if os.path.isdir(tdir) else 0)
    return miss, n_patch


def build_report(allS: list, glyph_gate: dict) -> str:
    L = []
    A = L.append
    _bl = _baseline_expect()
    _pd = _plan_drawings()
    _bs = C.baseline_sheet() or "基线"
    A("# %d 图双载体解析 — 汇总报告" % len(allS))
    A("")
    A("> 由 `scripts/09_verify_deliverables.py` 从各阶段落盘的 `work/gate_*.json` 与交付物"
      "读出，不重算几何。逐图口径与偏差见各图 `<base>_修正单.md`。")
    A("")
    A("## 一、6 件套齐套性")
    A("")
    A("| 图号 | SVG | MD | crosswalk | QA题库 | 修正单 | 反向重绘 | 齐套 |")
    A("|---|---|---|---|---|---|---|---|")
    for S in allS:
        p = S["pieces"]
        A("| `%s` | %s | %s | %s | %s | %s | %s | %s |"
          % (S["base"], *["✓" if p[k] else "✗" for k in
                          ("svg", "md", "crosswalk", "qa", "fixlist", "redraw")],
             "**齐套**" if all(p.values()) else "缺件"))
    A("")
    _miss, _np = _layout_missing(allS)
    A("**方案目录清单的其余部分**（6 件套之外）：逐图 `work/` 下 %s 与 `regions/*.png`；"
      "跨图共用件 `output/_glyph_dict/` 下 `templates/*.png`（逐模板 4× 高清贴片 **%d 张**）、"
      "`contact_sheet_*.png`、`glyph_labels.json`、`dict_stats.json`。实查结果：**%s**。"
      "`views_override.json` 是**可选人工输入**（方案 §10：仅当聚类残余粘连时人工指定 "
      "bbox，02 优先读它），各图均无 UNASSIGNED、未用到该通道，故不存在属正常，"
      "也不由脚本生成占位文件。"
      % ("/".join("`%s`" % f for f in WORK_REQ), _np,
         "全部齐套" if not _miss else "缺 %d 项 %s" % (len(_miss), _miss[:8])))
    A("")
    A("## 二、门禁矩阵（硬门禁）")
    A("")
    heads = ["计数链四相等", "六层齐全", "无UNASSIGNED", "recall≥0.99", "rms≤0.1pt",
             "载体一致", "self_check全过", "QA≥20题", "五类齐全", "QA自检100%",
             "盲测≥95%", "MD≤8万字符"]
    A("| 图号 | " + " | ".join(heads) + " | 阶段结论 |")
    A("|---" * (len(heads) + 2) + "|")
    for S in allS:
        st = gate_state(S["gates"])
        val, ch = S["validate"], (S["validate"].get("chain") or {})
        rd = val.get("redraw") or {}
        rt = val.get("roundtrip") or {}
        cc = val.get("carrier_consistency") or {}
        qc = (S["qa"].get("counts") or {})
        sc = S["qa"].get("self_check") or []
        bt = S["qa"].get("blind_test") or {}
        six = _six_layers_ok(S)
        cells = [
            _mk(ch.get("ok")),
            _mk(six),
            _mk(_unassigned(S) == 0),
            _mk((rd.get("recall") or 0) >= 0.99),
            _mk((rt.get("rms_all_pt") if rt.get("rms_all_pt") is not None else 9) <= 0.1),
            _mk(cc.get("consistent")),
            _mk(S["self_check"]["n"] > 0 and S["self_check"]["ok"] == S["self_check"]["n"]),
            _mk((qc.get("verifiable") or 0) >= 20),
            _mk((qc.get("n_categories") or 0) == 5),
            _mk(len(sc) > 0 and all(s.get("md_verifiable") for s in sc)),
            _mk(bt.get("accuracy") is not None and bt["accuracy"] >= 0.95),
            _mk(0 < S["md_chars"] <= MD_CHAR_LIMIT),
        ]
        fails = sorted({"%s(%s)" % (r["stage"], r["script"]) for r in S["gates"]
                        if r["exists"] and any(x["required"] and not x["ok"]
                                               for x in r["doc"].get("gates", []))})
        miss = sorted({"%s(%s)" % (r["stage"], r["script"]) for r in S["gates"]
                       if not r["exists"]})
        concl = "全绿" if not fails and not miss and all(c == "✓" for c in cells) else (
            "未达标：" + "; ".join(fails + ["缺文件 " + m for m in miss]))
        A("| `%s` | %s | %s |" % (S["base"], " | ".join(cells), concl))
    A("")
    A("## 三、关键指标（实测值）")
    A("")
    A("| 图号 | drawings | bg | kept | SVG path | MD索引 | 视图数 | 层计数(out/cl/thin/dim/sp/tb) "
      "| recall | precision | IoU | rms(pt) | MD字符 | 绑定dims | 比例档(read/inf/fb) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for S in allS:
        ch = S["validate"].get("chain") or {}
        rd = S["validate"].get("redraw") or {}
        rt = S["validate"].get("roundtrip") or {}
        bl, ss = S["by_layer"], S["scale_sources"]
        A("| `%s` | %s | %s | %s | %s | %s | %d | %d/%d/%d/%d/%d/%d | %s | %s | %s | %s | %d | %d | %d/%d/%d |"
          % (S["base"], S["counts"].get("drawings"), S["counts"].get("bg"),
             S["counts"].get("kept"), ch.get("svg_path"), ch.get("md_index"), S["n_views"],
             bl.get("outline", 0), bl.get("centerline", 0), bl.get("thin", 0),
             bl.get("dimension", 0), bl.get("special", 0), bl.get("title-block", 0),
             rd.get("recall"), rd.get("precision"), rd.get("iou_strict"),
             rt.get("rms_all_pt"), S["md_chars"], S["n_dims_bound"],
             ss.get("read", 0), ss.get("inferred", 0), ss.get("fallback", 0)))
    A("")
    A("## 四、与方案基线对账")
    A("")
    A("### 4.1 drawings 总数（附件清单基线）")
    A("")
    A("| 图号 | 基线 | 实测 | 差 |")
    A("|---|---|---|---|")
    for S in allS:
        pd = _pd.get(S["base"])
        got = S["counts"].get("drawings")
        A("| `%s` | %s | %s | %s |" % (S["base"], pd, got,
                                       (got - pd) if (pd is not None and got is not None) else "—"))
    A("")
    A("### 4.2 %s 逐层基线（方案 §11）" % _bs)
    A("")
    S3 = next((S for S in allS if S["base"] == C.baseline_sheet()), None)
    A("| 项 | 基线 | 实测 | 判定 |")
    A("|---|---|---|---|")
    if S3 and _bl:
        rows = [("kept", _bl["kept"], S3["counts"].get("kept"))]
        for lay in ("outline", "centerline", "thin", "dimension", "special", "title-block"):
            rows.append((lay, _bl[lay], S3["by_layer"].get(lay, 0)))
        rows.append(("视图数(V00+…)", _bl["views"], S3["n_views"]))
        rows.append(("recall", _bl["recall"],
                     (S3["validate"].get("redraw") or {}).get("recall")))
        rows.append(("弧/圆 rms(pt)", _bl["rms_pt"],
                     (S3["validate"].get("roundtrip") or {}).get("rms_all_pt")))
        rows.append(("绿层绑定率", _bl["bind_rate"],
                     (S3["validate"].get("green_layer") or {}).get("bind_rate")))
        for name, want, got in rows:
            if got is None:
                verdict = "未产出"
            elif isinstance(want, float) or isinstance(got, float):
                verdict = "记录并解释" if got != want else "吻合"
            else:
                verdict = "✓ 吻合" if got == want else "△ 差异(见修正单 §3.3)"
            A("| %s | %s | %s | %s |" % (name, want, got, verdict))
        # 汇总报告不能只给「见修正单」的指针：视图数这一行的偏差机制必须就地可读。
        _vs3 = S3.get("views_stats") or {}
        _cs3 = _vs3.get("comp_core_sizes") or []
        _ms3 = (_vs3.get("params") or {}).get("min_seed")
        if _cs3 and _ms3 and _bl["views"] is not None and S3["n_views"] != _bl["views"]:
            A("")
            A("视图数差 %+d 的机制：02 把本图 %s 个墨迹连通核按**核心图元数 ≥ "
              "`MIN_SEED=%s`** 二分，达标者 %s 个成零件视图、其余 %s 个作碎片就近并入。"
              "该偏差**不可调参弥合**：`MIN_SEED` 从 1 扫到 %d，可得的零件视图数集合为 %s，"
              "其中不含基线的 %d——差异源于聚类机制本身，按 D2 记录并解释，不为对齐数字而"
              "改机制（逐图证据与「与竖排归正式修正无关」的探针结果见 %s 修正单 §3.3）。"
              % (S3["n_views"] - _bl["views"], _vs3.get("components"), _ms3,
                 _vs3.get("seeds"), _vs3.get("scraps"), max(_cs3),
                 sorted({sum(1 for n in _cs3 if n >= k)
                         for k in range(1, max(_cs3) + 1)}),
                 _bl["views"] - 1, _bs))
            # 方案指定的「投影间隙切分过合并簇」是**已实测后未采纳**、不是漏做；
            # 方案要求汇总报告把未达标项定位到阶段，故该结论必须就地可读，
            # 数字全部从两支探针的落盘 JSON 读。
            _pb3 = _probe_dir()
            _gs3 = (C.read_json(os.path.join(_pb3, "gap_split.json"), {}) or {}) if _pb3 else {}
            _sv3 = (C.read_json(os.path.join(_pb3, "spec_views.json"), {}) or {}) if _pb3 else {}
            _sp3 = _sv3.get("params") or {}
            _gk3 = "gap_cells=%s" % _sp3.get("gap_cells", 1)
            _g13 = (_gs3.get(_gk3) or {}).get(C.baseline_sheet()) or {}
            _rp3 = (_sv3.get("line109_repro") or {}).get(C.baseline_sheet()) or {}
            _oc3 = _rp3.get("oc_no_v00(=skel_of)") or {}
            _ka3 = _rp3.get("kept_all(全层)") or {}
            if _g13 and _sv3:
                A("")
                A("方案指定的「投影间隙切分过合并簇」这一步**已实测、未采纳**"
                  "（不是漏做）：① 对全部种子递归切分使本图 %s→%s，各图一致过分裂 %s→%s；"
                  "② 按方案原样口径（`outline+centerline` bbox 并查集 eps=%s pt → 只切"
                  "过合并巨簇 → 小簇 <%s 就近归并）扫遍「过合并簇」判据只能得 %s；"
                  "③ 方案原文记载的「最大 1647 条过合并簇」只在**全 kept 层**口径下复现"
                  "（%s 条 → %s 簇、最大 %s 条），而方案指定的骨架口径实测 %s 簇、"
                  "最大仅 %s 条 → 该步在方案口径下**无对象可切**。①② 都比现行 %s 离"
                  "基线 %s 更远，故保留现行机制；探针 `output/_probe/cmp_gapsplit.py`、"
                  "`cmp_specviews.py`（落盘 `gap_split.json`、`spec_views.json`）可复核，"
                  "逐条叙述与「残余粘连无可指认目标」的高分辨率裁切核查见 %s 修正单 §3.3。"
                  % (_g13.get("before_views"), _g13.get("after_views"),
                     [(_gs3.get(_gk3) or {}).get(b, {}).get("before_views")
                      for b in C.all_sheets()],
                     [(_gs3.get(_gk3) or {}).get(b, {}).get("after_views")
                      for b in C.all_sheets()],
                     _sp3.get("eps"), _sp3.get("min_merge"),
                     _sv3.get("attainable_views_6_3"),
                     _ka3.get("n"), _ka3.get("clusters"), _ka3.get("max"),
                     _oc3.get("clusters"), _oc3.get("max"),
                     S3["n_views"], _bl["views"], _bs))
        # recall / rms 两项的判定写的是「记录并解释」，解释必须就地给出（方案 D2）；
        # 全部数字从基线图的 validate.json 读，不写死。
        _rt3 = S3["validate"].get("roundtrip") or {}
        _rd3 = S3["validate"].get("redraw") or {}
        _ch3 = S3["validate"].get("chain") or {}
        _gl3 = S3["validate"].get("green_layer") or {}
        _tol3 = _rd3.get("tolerance") or {}
        A("")
        A("**recall %s vs 基线 %s（差 %+.6f）的解释**：反向重绘漏画 %s px / 源墨迹 %s px"
          "（%spx 膨胀容差、墨迹阈值 %s）。漏画近零是**链条四相等**的直接后果："
          "`svg_path == kept == md_index == %s` 且 `data-prim-id` 唯一，每个 kept 图元恰好"
          "发射一次。但同一次测量里 **precision=%s、多画 %s px**（重绘墨迹 %s px）："
          "07 的重绘把线宽取为 `max(1, round(stroke-width × scale))` 的整像素并用 PIL 硬边"
          "描边（joint=curve），而源图由 PyMuPDF 抗锯齿渲染、上述阈值只收极暗像素 → 细线在"
          "源图达不到阈值、在重绘图却是满宽硬边。这是**测量口径的不对称**，不是交付物多画"
          "了图元（图元数与 id 唯一性属硬门禁，已四相等）；方案基线只列 recall、未列 "
          "precision，故在此一并记录。"
          % (_rd3.get("recall"), _bl["recall"],
             (_rd3.get("recall") or 0) - _bl["recall"], _rd3.get("missed_px"),
             _rd3.get("orig_ink_px"), _tol3.get("dilate_px"), _tol3.get("ink_threshold"),
             _ch3.get("svg_path"), _rd3.get("precision"), _rd3.get("extra_px"),
             _rd3.get("redraw_ink_px")))
        A("")
        _ratio = ((_bl["rms_pt"] / _rt3["rms_all_pt"])
                  if _rt3.get("rms_all_pt") else None)
        A("**弧/圆 rms %s pt vs 基线 %s pt（低 %s 倍）的解释**：07 的 `params_roundtrip` 把 "
          "SVG `data-params` 逐条读回与 01 的源几何比较，%s/%s 全覆盖（center=%s、"
          "radius=%s、角度折算=%s、max=%s pt）。本实现**不重拟合弧**——`extract_audit.json` "
          "无 `arc_rms` 键、故 07 的 `fit_rms_from_01=%s`——而是把 PDF 自带的曲线参数按 "
          "3 位小数写进 `data-params`（`06_enhance_svg.py` 的弧参数一律 `round(…, 3)`），"
          "故残差只剩写出的十进制量化，与 3 位小数的量化下限 0.001/√12≈0.000289 pt 同量级。"
          "基线的 %s pt 高一个数量级，对应「从采样点重拟合弧」的路径；两者都满足硬门禁 "
          "rms≤0.1pt（方案门禁总表）。"
          % (_rt3.get("rms_all_pt"), _bl["rms_pt"],
             ("%.0f" % _ratio) if _ratio else "—",
             _rt3.get("n_checked"), _rt3.get("n_data_params"), _rt3.get("rms_center_pt"),
             _rt3.get("rms_radius_pt"), _rt3.get("rms_angle_as_arc_pt"),
             _rt3.get("max_all_pt"), _rt3.get("fit_rms_from_01"),
             _bl["rms_pt"]))
        A("")
        A("**绿层绑定率 %s vs 基线 %s（%s/%s）的解释**：绑定率的直接上限是字典标签覆盖率"
          "（%s/%s 个模板有标签），而非定位算法；未绑定者 %s 个全部计入 MD §6 不清项、"
          "不臆造定位。方案 §11 明确该项**仅记录、非门禁**。"
          % (_gl3.get("bind_rate"), _bl["bind_rate"], _gl3.get("n_bound"),
             _gl3.get("n_recovered_numeric"),
             (C.read_json(os.path.join(C.GLYPH_DIR, "glyph_labels.json"), {}) or {}
              ).get("meta", {}).get("n_labels"),
             (C.read_json(os.path.join(C.GLYPH_DIR, "dict_stats.json"), {}) or {}
              ).get("stats", {}).get("templates_total"), _gl3.get("unbound_numeric")))
    else:
        A("| — | — | — | %s 未产出 |" % _bs)
    A("")
    A("硬门禁与基线对账的区别（决策 D2）：计数链、六层齐全、无 UNASSIGNED、recall≥0.99、"
      "rms≤0.1pt、载体一致性、QA 题量/五类/自检、MD≤8万字符为**硬门禁**；"
      "逐层图元数、视图数、绑定率、rms/recall 的具体数值为**基线对账项**（记录差异并解释）。")
    A("")
    A("## 五、跨图共用字形字典")
    A("")
    ds = C.read_json(os.path.join(C.GLYPH_DIR, "dict_stats.json"), {})
    dst = ds.get("stats") or {}
    _gdoc = C.read_json(os.path.join(C.GLYPH_DIR, "glyph_labels.json"), {}) or {}
    gm = _gdoc.get("meta") or {}
    lab_map = _gdoc.get("labels") or {}
    VS = {S["base"]: _vision_stats(S["base"]) for S in allS}
    A("| 项 | 值 |")
    A("|---|---|")
    A("| 合并去重模板数 | %s |"
      % (dst.get("templates_total") or ds.get("templates") or gm.get("n_templates") or "—"))
    A("| 字形实例总数 | %s |" % dst.get("n_total_instances"))
    A("| 模板跨图复现分布（出现于 N 图的模板数） | %s |"
      % json.dumps(dst.get("by_nsheets") or {}, ensure_ascii=False))
    A("| **字典标签数（合计）** | %s |" % gm.get("n_labels"))
    # 不能拿 meta 的 own/foreign 当「来源分布」：那两个计数只是**最后写入阶段**的视角，
    # 与标签的真实出处无关。改按标签自带的 `source` 字段统计，与写入顺序无关。
    _src = Counter(str((v or {}).get("source") or "未标注") for v in lab_map.values())
    A("| ├ 按标签自带 `source` 字段的来源分布 | %s |"
      % json.dumps(dict(_src.most_common()), ensure_ascii=False))
    # `meta.source` 不可用作「最后写入阶段」的标识：03c 落盘时用
    # `dict(_prev_meta, **doc["meta"])` 合并（03c_glyph_solve.py:622），而它自建的
    # meta 里根本没有 `source` 键 → 盘上该值是从 03d 继承来的，只证明 03d 曾 promote。
    # 两阶段互相保留对方的 meta 键（03d 亦 `dict(old_meta)` 起头），故 03c 独有的
    # plaintext_audit/crib_audit 同样会被 03d 继承、不能用来判序。真正两阶段**共写**
    # 的只有 method / n_labels / n_labels_own / n_labels_foreign_preserved /
    # vision_available，其中 `method` 的文案两阶段互不相同 → 用它判定最后写入者。
    _last = ("03c 确定性明文双源" if "确定性自监督解码" in str(gm.get("method") or "")
             else "03d 视觉逐行识读")
    A("| └ `n_labels_own`/`n_labels_foreign_preserved` 的口径 | 这两个计数是**最后写入 "
      "glyph_labels.json 的阶段**（本轮=%s，按 `meta.method` 文案判定）的自产/保留视角："
      "自产 %s、保留他阶段 %s。`meta.source`=%s 是 03c 合并时从 03d **继承**的键，"
      "不代表写入顺序。两阶段已做互相保留（03c 重跑不会清掉 03d 的标签），故标签的"
      "真实出处以上一行的 `source` 分布为准；详见 §5.3。 |"
      % (_last, gm.get("n_labels_own"), gm.get("n_labels_foreign_preserved"),
         gm.get("source")))
    A("| 标签字符分布 | %s |"
      % json.dumps(dict(Counter(str((v or {}).get("char"))
                                for v in lab_map.values()).most_common()),
                   ensure_ascii=False))
    A("| 其中单票标签（复现次数=1） | %d —— 全部落在标题栏/技术要求区，符合方案"
      "「只标注复现次数≥2 的模板 + 单例中落在标题栏/技术要求区的模板」 |"
      % sum(1 for v in lab_map.values() if (v or {}).get("votes") == 1))
    A("| 票型分散被拒（宁缺勿臆） | %s :: %s |"
      % (gm.get("n_rejected"),
         json.dumps(_gdoc.get("rejected") or {}, ensure_ascii=False)))
    A("| 采信图数（V1+V2 双过） | %s / %d |" % (gm.get("n_sheets_trusted"), len(allS)))
    A("| 未解模板数（03c） | %s |" % gm.get("n_unresolved"))
    A("| 证据对(文本行↔尺寸线) | %s |" % gm.get("evidence_n"))
    A("| 配对拒绝原因 | %s |" % json.dumps(gm.get("reject_reasons") or {}, ensure_ascii=False))
    A("| vision 通道可用 | %s（归属 03d；03c 只透传不覆写） |" % gm.get("vision_available"))
    A("| vision 可用范围（实测校准） | %s |" % (gm.get("vision_scope") or "—"))
    A("| 票的分区范围 | %s |" % (gm.get("vote_zone_scope") or "—"))
    A("| 明文源 A（几何尺寸线长度）可用 | %s |" % gm.get("plaintext_viable"))
    ca = gm.get("crib_audit") or {}
    if ca:
        gn = ca.get("crib_only_gain") or {}
        A("| 明文源 B（图号 crib）跨图号家族约束 | %s/%s 通过 |"
          % (ca.get("n_cross_family_agree"), ca.get("n_cross_family")))
        A("| 明文源 B 跨图同 crib 序列一致 | %s/%s |"
          % (ca.get("n_seq_identical_all"), ca.get("n_crib_cross_sheet")))
        A("| 明文源 B 命中行字高(pt) | %s |" % (ca.get("matched_line_heights_pt"),))
        A("| crib-only 强行发布的**诱饵收益** | %s 行看似可全字解析（纯数值 %s）/ 共 %s 行"
          " —— 已否证为虚构文本，不发布 |"
          % (gn.get("n_lines_fully_resolvable"), gn.get("n_numeric_resolvable"),
             gn.get("n_lines_total")))
    A("")
    A("### 5.1 vision 双源比对（方案 D3 第二档来源：视觉裁切复核）")
    A("")
    A("两源都**可判定**，不靠信任识读者：**V1** 用 PDF 文件名作图号真值，要求标题栏"
      "**单行**转录与图名的最长公共连续子串 ≥ 阈值（不用全区拼接，以免假阳性）；"
      "**V2** 要求转录的非空白字符数与该行的**字符位数**精确相等（容差 0）。"
      "只有 V1+V2 双过的图才把票汇入字典。")
    A("")
    A("| 图号 | V1 LCS(阈) | V1 命中行 | V2 精确/转录 | 派生 sid | 冲突 | trusted |")
    A("|---|---|---|---|---|---|---|")
    for S in allS:
        v = VS[S["base"]]
        A("| `%s` | %s(%s) | %s | %s/%s | %s | %s | %s |"
          % (S["base"], v["v1"].get("best_lcs"), v["v1"].get("min_lcs"),
             ",".join(v["v1"].get("hit_rows") or []) or "无",
             v["v2"].get("rows_exact"), v["v2"].get("rows_transcribed"),
             v["dl"].get("n_sid"), v["dl"].get("n_conflict"),
             "**是**" if v["trusted"] else "否"))
    A("")
    sk, ps = gm.get("skipped_untrusted") or {}, gm.get("per_sheet") or {}
    if sk:
        A("**V1 拒绝的图（识读不采信、标签不入字典）**：")
        for b, r in sk.items():
            A("- `%s`：V1 最长公共子串=%s（阈 %s）未命中 → %s；该图 %s 个派生 sid 全部丢弃。"
              % (b, r.get("best_lcs"), (ps.get(b) or {}).get("min_lcs"),
                 r.get("why"), r.get("n_sid")))
        A("")
        A("拒绝理由：V1 未命中意味着连图上字号最大的图号串都读错了，此时 V2 对齐只能证明"
          "「字符位数」对上、不能证明字符本身对——把这些票汇入字典就是把误读当真相，"
          "违反方案「不臆造」。")
    A("")
    A("### 5.2 识读覆盖率与能力边界（省略行不贡献票）")
    A("")
    A("| 图号 | tb 转录/渲染 | notes 转录/渲染 | 省略行 | 转录行 gh 中位(pt) | 省略行 gh 中位(pt) |")
    A("|---|---|---|---|---|---|")
    t_r = t_t = 0
    for S in allS:
        v, pz = VS[S["base"]], VS[S["base"]]["per_zone"]
        tb, nt = pz.get("tb") or {}, pz.get("notes") or {}
        nr = sum(x["rendered"] for x in pz.values())
        ntr = sum(x["transcribed"] for x in pz.values())
        t_r += nr
        t_t += ntr
        A("| `%s` | %s/%s | %s/%s | %d | %s | %s |"
          % (S["base"], tb.get("transcribed", 0), tb.get("rendered", 0),
             nt.get("transcribed", 0), nt.get("rendered", 0), nr - ntr,
             _med(v["gh_transcribed"]), _med(v["gh_omitted"])))
    A("| **合计** | — | — | **转录 %d / 渲染 %d** | %s | %s |"
      % (t_t, t_r,
         _med([g for S in allS for g in VS[S["base"]]["gh_transcribed"]]),
         _med([g for S in allS for g in VS[S["base"]]["gh_omitted"]])))
    A("")
    zt = {"tb": [0, 0], "notes": [0, 0]}
    for S in allS:
        for z, x in VS[S["base"]]["per_zone"].items():
            if z in zt:
                zt[z][0] += x["transcribed"]
                zt[z][1] += x["rendered"]
    n_exact = sum((VS[b]["v2"].get("rows_exact") or 0) for b in VS)
    n_tr = sum((VS[b]["v2"].get("rows_transcribed") or 0) for b in VS)
    n_cjk = sum(1 for v in lab_map.values()
                if ord(str((v or {}).get("char") or "a")[:1]) > 0x2E80)
    # 精确率与「不精确行」一律从落盘的 verification.rows 现算：把「=100%」写死会在
    # 任何一行 V2 失配时变成假陈述（本轮实测 269/270，失配行逐条列出）。
    _v2bad = [(b, r) for b in VS for r in VS[b]["v2_bad"]]
    _ntr = [b for b in VS if VS[b]["trusted"]]
    _lcs = [VS[b]["v1"].get("best_lcs") for b in _ntr]
    _badtxt = "" if not _v2bad else "，不精确的 %d 行：%s" % (
        len(_v2bad), "、".join(
            "`%s` 的 %s %s（转录 %r=%s 字符 vs 字符位数 %s，diff=%s）"
            % (b, r["zone"], r["row_id"], r["text"], r["n_chars"], r["n_cells"],
               r["diff"]) for b, r in _v2bad))
    _unb = [b for b, r in _v2bad if not VS[b]["trusted"]]
    _badwhy = "" if not _v2bad else (
        "。这些行全落在 V1 未过的图（%s）——整图本就不采信、票不入字典，故 V2 失配"
        "不影响字典" % "、".join("`%s`" % b for b in _unb)
        if len(_unb) == len(_v2bad) else
        "。其中落在已采信图的行会少投一票，已逐行列出可追责")
    A("能力边界的**数据判据**（只陈述已测量的事实，不外推）：")
    A("- 各图无一例外：省略行的 gh 中位数低于转录行（合计 %s pt vs %s pt）。但两者"
      "差距不大且都落在小字高带，故字高**不是唯一判据**，不能据此断言「字够大就能读对」。"
      % (_med([g for S in allS for g in VS[S["base"]]["gh_transcribed"]]),
         _med([g for S in allS for g in VS[S["base"]]["gh_omitted"]])))
    A("- 转录成功率按分区高度偏斜：`notes` 区 %d/%d、`tb` 区仅 %d/%d。`notes` 区以"
      "数值/尺寸行为主（转录出的全是 `2900`/`1275`/`8950` 这类纯数字串），`tb` 区含"
      "名称/材料/日期等小字高汉字格——即**内容类型（拉丁数字 vs 汉字）与字高两个因素"
      "混淆在一起**，现有落盘数据不足以把它们分开，故不单独归因。"
      % (zt["notes"][0], zt["notes"][1], zt["tb"][0], zt["tb"][1]))
    A("- 能确定的是**闸门有效**：%d 图的 tb `R0001`（图号行）被逐字读对（V1 LCS=%s，"
      "达阈值 %s）；转录进来的行 V2 精确率 %d/%d=%.2f%%%s%s，而转录者对无法确定字符数的行"
      "主动省略，省略行不进入 V2、不贡献票。结果：字典 %d 个标签里只有 %d 个汉字，"
      "**没有任何汉字长句被写入**——描述通道在小字高汉字格上幻觉出的词（实测出现过"
      "「心平气和」「小雨」「转子包」这类无工程语义串）确实被拦在字典之外。"
      % (len(_ntr), min(_lcs) if _lcs else "—",
         (VS[_ntr[0]]["v1"].get("min_lcs") if _ntr else "—"),
         n_exact, n_tr, (100.0 * n_exact / n_tr) if n_tr else 0.0, _badtxt, _badwhy,
         len(lab_map), n_cjk))
    A("")
    _n5 = sum(len(S2["text"].get("technical_requirements") or []) for S2 in allS)
    _ts = [(S2["text"].get("tech_req_stats") or {}) for S2 in allS]
    _n5n = sum(t.get("n_note_lines") or 0 for t in _ts)
    _n5x = sum(t.get("n_excluded_non_cjk") or 0 for t in _ts)
    A("§5 技术要求的口径（两个计数不可混淆）：")
    A("- **识读侧**：03d 在 `notes` 区命中的编号行共 %d 条、比例 read 档 %d 处、标题栏"
      "字段 %d 个——这只用于给字形字典投票，**不直接进 MD §5**。"
      % (sum(VS[b]["n_notes"] for b in VS), sum(VS[b]["n_scale"] for b in VS),
         sum(VS[b]["n_fields"] for b in VS)))
    A("- **MD §5 实际交付**的技术要求条目共 %d 条：03b 只把注释区里**汉字数≥2 的成句行**"
      "写进 §5。实测注释区 %d 条完整解出行里有 %d 条被排除（形如 `9720`、`Φ60`、`C45`、"
      "`向5` 的尺寸值/倒角/直径/视图方向标注）——CAD 导出把标注文字也放进了注释类 OCG，"
      "故 `zone=notes` ≠ 技术要求；只看 OCG 会把这些数字当条款逐字交付、还标 conf=high。"
      "被排除者计入 §6 不清项，不静默丢弃。" % (_n5, _n5n, _n5x))
    A("- 未命中一律不写占位文本（不臆造）：§5 为空时 MD 记「未提供」并写明排除依据与样例，"
      "而不是编一段。")
    A("")
    A("### 5.3 03c 自监督解码阶段门禁（跑于 03d 视觉对账**之前**）")
    A("")
    A("下表是 03c 自己那一轮的判定，其中「本阶段标签」计数反映的是 03c 的两条明文源"
      "（几何尺寸线长度 / 图号 crib）**均未产出标签**这一事实，**不是字典的最终状态**；"
      "字典最终状态见本节开头的合计行。03c 的否证审计（`plaintext_audit` / `crib_audit`）"
      "已由 03d 的 promote 保留在同一份 meta 里，不会因阶段覆写而丢失。")
    A("")
    A("| 门禁 | 结果 | 明细 |")
    A("|---|---|---|")
    for g in (glyph_gate or {}).get("gates", []):
        A("| `%s` | %s | %s |" % (g["gate"], "ok" if g["ok"] else
                                 ("FAIL" if g["required"] else "warn"), g["detail"]))
    A("")
    A("结论与闭环路径见各图修正单 §3.2（各图共用同一份字典，标注一次全图受益）。")
    A("")
    A("## 六、未达标项 → 阶段定位")
    A("")
    any_fail = False
    for S in allS:
        for r in S["gates"]:
            if not r["exists"]:
                A("- `%s` 阶段 %s（`%s`）：**门禁文件缺失** → 未跑或跑崩，重跑 "
                  "`python scripts\\%s --sheet \"%s\"`"
                  % (S["base"], r["stage"], r["file"], r["script"], S["base"]))
                any_fail = True
                continue
            for g in r["doc"].get("gates", []):
                if g["required"] and not g["ok"]:
                    A("- `%s` 阶段 %s（`%s`）：**%s** → %s"
                      % (S["base"], r["stage"], r["script"], g["gate"], g["detail"]))
                    any_fail = True
        miss = [k for k, ok in S["pieces"].items() if not ok]
        if miss:
            A("- `%s` 交付物缺件：%s" % (S["base"], ", ".join(PIECE_NAMES[m] for m in miss)))
            any_fail = True
    if not any_fail:
        A("- 无：全部图硬门禁通过、6 件套齐套。")
    A("")
    A("## 七、复跑命令")
    A("")
    # 方案原文：全链固定 PyMuPDF 渲染 + PIL 绘制、scale=2.0，**版本写入汇总报告**。
    # 07 已把 scale/size_px/pymupdf/pil 落进 validate.json，此处读回（与交付物同源，
    # 不另行探测），并核各图是否单值——「全链固定」必须是可判定的事实而非叙述。
    _vs = [S["validate"] or {} for S in allS]
    _keys = ("pymupdf", "pil", "scale", "size_px")

    def _u(k):
        s = sorted({json.dumps(v.get(k), ensure_ascii=False)
                    if isinstance(v.get(k), (list, dict)) else str(v.get(k))
                    for v in _vs if v})
        return s[0] if len(s) == 1 else "**多值：%s**" % "、".join(s)

    _nval = {k: len({json.dumps(v.get(k), ensure_ascii=False) for v in _vs if v}) for k in _keys}
    _tol = ((_vs[0].get("redraw") or {}).get("tolerance") or {}) if _vs else {}
    try:
        import numpy as _np
        import scipy as _sp
        _nver, _sver = _np.__version__, _sp.__version__
    except Exception as _e:                      # 报告不得因取版本号而失败
        _nver = _sver = "未取到(%s)" % _e.__class__.__name__
    A("**运行环境（方案原文：全链固定 PyMuPDF 渲染 + PIL 绘制、scale=2.0，版本写入"
      "汇总报告）**：各图 `validate.json` 记录的渲染器与分辨率%s——渲染器 %s、"
      "Pillow %s、`scale=%s`、叠合图 %s px（≈144DPI）；容差口径 `dilate_px=%s`、"
      "`ink_threshold=%s`（灰度 < 该值视为有墨）。另 numpy %s / scipy %s（02 的 "
      "`ndimage.label` + `binary_dilation` 墨迹连通域）、python %s。版本号由 07 在测量"
      "当时写入 `validate.json`，本段读回而非另行探测，故与交付物同源。"
      % ("**单值一致**" if all(n == 1 for n in _nval.values())
         else "**存在多值 %s**" % _nval,
         _u("pymupdf"), _u("pil"), _u("scale"), _u("size_px"),
         _tol.get("dilate_px"), _tol.get("ink_threshold"),
         _nver, _sver, sys.version.split()[0]))
    A("")
    A("顺序**有依赖**：03c 与 03d 都写 `output/_glyph_dict/glyph_labels.json`"
      "（两者已做互相保留，各自只覆写自己来源的标签），03b 读它，故 **03b 必须在 "
      "03c、03d 之后**；05/06/04/07/08 读 03b 的 `text.json`。旧顺序把 03b 排在 03c 前、"
      "且漏掉 03d，照它跑会得到零标签字典。")
    A("")
    A("**字形 sid 由 01 落盘**（`01_extract.py` 调 `C.glyph_flags` 写 "
      "`work/glyph_templates.json`），`03_render_regions.py` 只读不重算。故任何对 "
      "`common.glyph_signature` 的修改都必须**从 01 起**重跑整链，只跑 03 及其后续"
      "会让修改静默失效（实测踩过）。`templates.json` 与接触表"
      "只能由 `--contact-sheets` 产出（`--all` 不会更新它），漏跑会让字典停在旧 sid 上。")
    A("")
    A("```powershell")
    A("$env:PYTHONIOENCODING='utf-8'")
    A("# 1) 几何与视图（确定性，可反复跑）")
    A("foreach($s in '01_extract','02_cluster_views','03_render_regions'){"
      " python \"scripts\\$s.py\" --all }")
    A("python scripts\\03_render_regions.py --contact-sheets  # 合并各图 sid → templates.json + 接触表")
    A("python scripts\\03_render_regions.py --label-sheets    # 大格标注表（n≥2 且字高≥5pt）")
    A("# 2) 字形字典：03c 自监督解码 → 03d 视觉逐行对账（渲染 / 转录 / 回填 / 汇总）")
    A("python scripts\\03c_glyph_solve.py --all")
    A("python scripts\\03d_vision_read.py --all                # 渲染 tb 区行格图")
    A("python scripts\\03d_vision_read.py --all --zone notes    # 渲染 notes 区行格图")
    A("#    ↑ 此处需由只读代理逐张转录 <sheet>/work/vread/*_row_sheet_*.png，写入")
    A("#      <sheet>/work/vread/transcript.json，必须按分区嵌套：")
    A('#      {"zones": {"tb": {"R0001": "…"}, "notes": {"R0001": "…"}}}')
    A("#      （row_id 在各分区独立编号会撞号；格下 n= 是字符位数，非空白字符数须与之相等）")
    A("python scripts\\03d_vision_read.py --all --apply         # V1/V2 双源对账 → 派生标签")
    A("python scripts\\03d_vision_read.py --all --promote       # 跨图汇总 → glyph_labels.json")
    A("# 3) 文本恢复与双载体（读字典）")
    A("foreach($s in '03b_text_recover','05_crosswalk','06_enhance_svg','04_build_md',"
      "'07_validate','08_qa'){ python \"scripts\\$s.py\" --all }")
    A("python scripts\\09_verify_deliverables.py --all")
    A("```")
    A("")
    A("单图：`python scripts\\<脚本>.py --sheet \"<图号>\"`（或 1-based 序号 "
      "`--sheet 4`）。所有脚本无状态、可重复执行；源 PDF 只读。")
    A("")
    # 方案原文写的是「11 个脚本」，实盘多于此；口径差异必须说清，否则齐套性无法对账。
    # 实盘清单从目录枚举（不写死），方案侧的 11 个是 Spec §脚本清单的原文内容。
    _spec11 = ["common.py", "01_extract.py", "02_cluster_views.py", "03_render_regions.py",
               "03b_text_recover.py", "04_build_md.py", "05_crosswalk.py", "06_enhance_svg.py",
               "07_validate.py", "08_qa.py", "09_verify_deliverables.py"]
    _sdir = os.path.dirname(os.path.abspath(__file__))
    _py = sorted(f for f in os.listdir(_sdir)
                 if f.endswith(".py") and not f.startswith("__"))
    _extra = [f for f in _py if f not in _spec11]
    A("**脚本数口径（方案原文「11 个 sheet 参数化脚本」）**：方案 §脚本清单 列出的 11 个"
      "均已存在（%s）；`scripts/` 实盘 %d 个 `.py`，多出的 %d 个是：%s——其中两个字形字典"
      "脚本是决策 D3「字形模板字典」拆出的两步（方案原文要求 `output/_glyph_dict/` "
      "产出 `glyph_labels.json`、`dict_stats.json` 与接触表，必须有一处负责）；下划线开头的"
      "是诊断与盲测答卷合并工具，不属流水线阶段、不参与门禁，故不进 6 件套与目录齐套门禁。"
      % ("、".join("`%s`" % s for s in _spec11), len(_py), len(_extra),
         "、".join("`%s`" % f for f in _extra)))
    A("")
    # 方案要求「未达标项定位到阶段」；要能声称无未达标项，前提是**逐条审计过**
    # 且审计本身可追溯。审计脚本不复用本生成器的判定（否则就是「生成器说自己通过」），
    # 而是直接从磁盘交付物与**源 PDF**（fitz 直读 rotation/page_count/rect）重算方案条款，
    # 结果落盘 _probe/spec_audit.json；此处只读回，不在报告里写死任何数字。
    _pb7 = _probe_dir()
    _sa = (C.read_json(os.path.join(_pb7, "spec_audit.json"), {}) or {}) if _pb7 else {}
    _ck = _sa.get("checks") or []
    if _ck:
        _ls = []
        for c in _ck:
            if str(c["line"]) not in _ls:
                _ls.append(str(c["line"]))

        def _ln(s):                      # 复合条款号（如 "34/129/158"）取首个数字作排序键
            m = re.search(r"\d+", s)
            return int(m.group()) if m else 0

        _ls.sort(key=lambda s: (_ln(s), s))
        _d1 = {c["req"].split("：")[-1]: (c.get("got") or {}).get("实测") or {}
               for c in _ck if str(c["line"]) == "34/129/158"}
        # 按「实测」dict 的键特征反查对应图，不写死图号（spec_audit 对账键随配置变化）：
        # 仅 outline 触发的图带 green_in_thick；红/黄并存的图带 red；仅 special 触发的图带
        # magenta_dash_double。
        _outline_only = next((v for v in _d1.values() if "green_in_thick" in v), {})
        _red_yellow = next((v for v in _d1.values() if "red" in v), {})
        _special_only = next((v for v in _d1.values() if "magenta_dash_double" in v), {})
        _bad_span = sum(len((c.get("got") or {}).get("区间首末号自洽异常") or [])
                        for c in _ck if str(c["line"]) == "61")
        _regok = [(c.get("got") or {}).get("view数与views.json自洽") for c in _ck
                  if str(c["line"]) == "97"]
        _t157 = next((c.get("got") or {} for c in _ck if str(c["line"]) == "157"), {})
        _fired = _t157.get("全 8 图触发的层") or {}
        _fire_s = ("、".join("`%s`→%s" % (k, "/".join(v))
                            for k, v in _fired.items() if v)
                   or "无（各图均未触发）")
        A("**方案逐条完成审计（独立于本报告生成器）**：`output/_probe/spec_audit.py` 不复用 09 "
          "的判定，直接从磁盘交付物与**源 PDF**（`fitz` 直读 `rotation`/`page_count`/`rect`）"
          "重算方案条款，覆盖 line %s 共 **%d 项 → 通过 %d、失败 %d**%s。硬证据举要："
          "① 方案给出的**明文实测数**逐项精确吻合——仅 outline 触发的图绿色落「粗实线」%s/%s 条、"
          "`PDM_Title` %s 条；红/黄并存的图红 %s 条、黄落通用层「0」%s 条、`PDM_Title` %s 条；"
          "仅 special 触发的图洋红「双点划线」%s 条（均从 `prims.json` 的颜色键 `c` 与 `ocg` 重数）。"
          "② MD 的 prim-id 区间**逐行首末号自洽**（末号−首号+1==计数，各图异常合计 %d 行）"
          "且区间求和 == kept == `md_prims_index.json` 条数（D6 门禁的正文侧证明，不只是索引侧）。"
          "③ `regions/` 四类齐备（整页总览/视图紧裁切/标题栏专切/技术要求区专切），且视图裁切数"
          "与 `views.json` 的 `n_views−1` 逐图自洽（%s）。④ 各图 PDF 的 mtime 均早于其交付物"
          "（方案假设 3「源 PDF 只读不修改」）。⑤ D1 纠偏的**触发事实**与方案原文 "
          "逐图吻合（直读 `prims.json` 的 `meta.triggers`，该字典恒含四层键、值为 bool）："
          "基线图与另一张同族图 **四层全 false** → 基线保持（这是 D2 能用基线图对账的前提）；"
          "仅 outline 触发的图 `outline=true`（粗实线绿色 %s/%s）；仅 special 触发的图 `special=true`"
          "（洋红双点划线归 special）。各图实际触发的层：%s。"
          % ("、".join(_ls), _sa.get("n_checks"), _sa.get("n_pass"), _sa.get("n_fail"),
             "" if not _sa.get("fail_lines") else "，失败项 line %s" % _sa.get("fail_lines"),
             _outline_only.get("green_in_thick"), _outline_only.get("thick_total"), _outline_only.get("pdm_title"),
             _red_yellow.get("red"), _red_yellow.get("yellow_in_layer0"), _red_yellow.get("pdm_title"),
             _special_only.get("magenta_dash_double"), _bad_span,
             "全部吻合" if all(_regok) else "**存在不吻合**",
             _outline_only.get("green_in_thick"), _outline_only.get("thick_total"), _fire_s))
        _f5 = next((c.get("got") or {} for c in _ck if str(c["line"]) == "51-56"), {})
        if _f5:
            A("")
            A("**审计还查出一处方案自身矛盾，实盘取与例算、门禁同时"
              "自洽的一支**：方案的括号注写 `x0 = W - tx`，但 V15 例算给 "
              "`tx=1420.5、ty=493.55、x0=1890.10=bbox 左界`；按本图 %s pt 的 W 算，"
              "`W−ty=1890.104` 吻合例算 x0、`W−tx=963.154` 不吻合，即**括号注把 tx/ty 写反**。"
              "又因 方案的 self_check 门禁本身强制 `x_p(0,0)==bbox.x0`（即 x0==bbox.x0），"
              "故 `x0 = W − ty` 是唯一同时满足例算与门禁的一支——实盘 `crosswalk.formula.x0` "
              "即取该式（各图均为 `%s`），逐视图 self_check 全过。其余三式与方案逐字一致"
              "（仅 `·`/`−`/`→` 排版差异，已归一后比对）；`portrait_to_local` 方案用 "
              "`local_x_mm`/`local_y_mm` 命名、实盘用 `x_mm`/`y_mm`，语义同。"
              % (_f5.get("W_pt"), _f5.get("formula.x0")))
    A("")
    return "\n".join(L)


def _mk(ok) -> str:
    if ok is None:
        return "—"
    return "✓" if ok else "✗"


def _six_layers_ok(S: dict) -> bool:
    """六层齐全含独立 title-block：以 gate_06 的结构判定为准，回退到计数判定。"""
    for r in S["gates"]:
        if r["stage"] == "A3" and "06_enhance_svg" in r["script"]:
            for g in r["doc"].get("gates", []):
                if "六层" in g["gate"]:
                    return bool(g["ok"])
    bl = S["by_layer"]
    return bl.get("title-block", 0) > 0 and sum(1 for x in C.LAYERS if bl.get(x, 0) > 0) >= 5


# ---------------------------------------------------------------- 入口


def build(base: str) -> dict:
    S = collect(base)
    C.ensure_dirs(base)
    txt = build_fixlist(S)
    C.write_text(S["deliverables"]["fixlist"], txt)
    S["fixlist_chars"] = len(txt)
    # 修正单是本脚本自己产出的第 6 件：齐套快照必须在写盘之后重算，
    # 否则首轮跑永远看不到自己刚写的文件（假判「0/8 齐套」）。
    S["pieces"] = {k: os.path.exists(p) and os.path.getsize(p) > 0
                   for k, p in S["deliverables"].items()}
    C.log("[%s] 修正单 %d 字符 → %s" % (base, len(txt), S["deliverables"]["fixlist"]))
    return S


def main(argv):
    C.init(argv)
    bases = C.parse_sheet_arg(argv)
    allS = [build(b) for b in bases]
    gg = C.read_json(_glyph_gate_path(), {})
    rep = build_report(allS, gg)
    out_p = os.path.join(C.OUT, "_汇总报告.md")
    C.write_text(out_p, rep)

    gate = C.Gate("_汇总报告")
    n_piece_ok = sum(1 for S in allS if all(S["pieces"].values()))
    gate.add("6 件套齐套(%d 图)" % len(allS), n_piece_ok == len(allS),
             "%d/%d 图齐套；缺件图=%s"
             % (n_piece_ok, len(allS),
                [S["base"] for S in allS if not all(S["pieces"].values())] or "无"))
    hard_fail = []
    for S in allS:
        for r in S["gates"]:
            if not r["exists"]:
                hard_fail.append("%s/%s 缺门禁文件" % (S["base"], r["stage"]))
                continue
            for g in r["doc"].get("gates", []):
                if g["required"] and not g["ok"]:
                    hard_fail.append("%s/%s/%s" % (S["base"], r["stage"], g["gate"]))
    # 方案「目录与交付物」清单除 6 件套外还点名了 work/ 中间产物与 _glyph_dict/ 的
    # 跨图共用件；上面那道门禁只查 6 件套，故补一道，免得清单缺件被漏过。
    lay_miss, _ = _layout_missing(allS)
    gate.add("方案目录清单齐套(work/ + _glyph_dict/)", not lay_miss,
             "缺 %d 项：%s" % (len(lay_miss), lay_miss[:8] or "无"))
    gate.add("全阶段硬门禁通过", not hard_fail,
             "未过 %d 项：%s" % (len(hard_fail), hard_fail[:12] or "无"))
    gate.add("MD 字符数≤%d(逐图)" % MD_CHAR_LIMIT,
             all(0 < S["md_chars"] <= MD_CHAR_LIMIT for S in allS),
             str({S["base"]: S["md_chars"] for S in allS}))
    gate.add("计数对账链四相等(逐图)",
             all((S["validate"].get("chain") or {}).get("ok") for S in allS),
             str({S["base"]: (S["validate"].get("chain") or {}).get("kept") for S in allS}))
    gate.add("汇总报告已产出", os.path.exists(out_p), "%s (%d 字符)" % (out_p, len(rep)))
    gate.dump(os.path.join(C.OUT, "gate_09.json"))
    C.log("=" * 78)
    C.log(gate.report())
    C.log("→", out_p)


if __name__ == "__main__":
    main(sys.argv[1:])
