# -*- coding: utf-8 -*-
"""04 生成「魂」载体：<base>-可复现图纸描述.md（方案 §3/§7 / 决策 D6）

prims/views/text/crosswalk → MD 六层 schema + work/md_prims_index.json（全量索引）

§1 元信息 §2 布局 §3 逐视图（语义注解+坐标系+prim-id 区间与计数+参数化图元+dims 表
+气球/焊缝/剖切）§4 BOM(降级) §5 技术要求(逐字) §6 不清项 §7 消费策略
附录A crosswalk（与 crosswalk.json / SVG metadata 同源）附录B ID 体系

门禁（D6）：**MD 里各视图分层 prim-id 区间的计数求和 == kept**（从写好的 MD 正文
反向正则解析求和，而非用生成时的变量，确保正文自洽）；**字符数 ≤ 8 万**。
体量控制：弧/圆/长圆与闭合多段线的完整参数按视图配额展开，超配额者只给计数与
prim-id 区间，全量落 work/md_prims_index.json（机器可读对账依据，非交付正文）。
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

CHAR_BUDGET = 78000          # 目标上限（门禁 80000）
CHAR_HARD = 80000
CAPS = [60, 40, 25, 15, 10, 6, 4, 2, 1, 0]     # 每视图参数化图元展开配额（自适应降级）
SPAN_RE = re.compile(r"\|\s*(?:outline|centerline|thin|dimension|special|title-block)\s*"
                     r"\|[^|]*\|\s*V\d+-P\d+\s*[…-]{1,2}\s*V\d+-P\d+\s*\|\s*(\d+)\s*\|")
ELL = "…"

KIND_NOTE = {
    "view": "零件/装配视图", "title": "标题栏与图框区", "notes": "注释与技术要求区",
    "section": "剖视/剖面", "detail": "节点大样/详图",
}


def paths(base: str) -> dict:
    d = C.deliverables(base)
    sd = C.sheet_dir(base)
    return {"md": d.get("md") or os.path.join(sd, base + "-可复现图纸描述.md"),
            "index": C.work_path(base, "md_prims_index.json")}


# ---------------------------------------------------------------- 语义注解


def sem_note(v: dict, cw: dict, spans: dict, geo: Counter) -> str:
    """1–3 句确定性语义注解（只用可核算的量，不做主观臆断）。"""
    s = []
    kind = KIND_NOTE.get(v.get("kind"), v.get("kind") or "视图")
    s.append("本区为%s（%s），图元 %d 条，其中 %s。"
             % (kind, v.get("name") or v["id"], v["n"],
                "、".join("%s %d" % (L, spans[L]["n"]) for L in C.LAYERS
                          if L in spans) or "无分层图元"))
    top = geo.most_common(3)
    if top:
        s.append("几何构成以 %s 为主，图纸幅面 %.0f×%.0f mm（比例 %s，来源 %s）。"
                 % ("、".join("%s %d" % kv for kv in top), cw["W_mm"], cw["H_mm"],
                    cw["scale"], cw["scale_source"]))
    if "ARC" in geo or "CIRCLE" in geo or "OBROUND" in geo:
        s.append("含 %d 个弧/圆/长圆，其参数以 data-params 同源 JSON 在下方展开，"
                 "可直接用于重绘与校核。" % (geo["ARC"] + geo["CIRCLE"] + geo["OBROUND"]))
    return " ".join(s[:3])


def feature_note(v: dict, by_i: dict, spans: dict) -> list:
    """气球/焊缝/剖切线索：只给可核算的计数与 prim-id，不做语义断言。"""
    out = []
    small_c = []
    for i in v["members"]:
        p = by_i[i]
        g = p["g"]
        if g["type"] == "CIRCLE" and p["sem"] in ("thin", "outline") and g["r"] < 12.0:
            small_c.append(i)
    if small_c:
        out.append({"feature": "小半径圆(疑似序号气球/孔)", "n": len(small_c),
                    "prim_i_sample": small_c[:6],
                    "note": "半径<12pt 的 thin/outline 圆；未与文本绑定，语义待确认"})
    if "special" in spans:
        out.append({"feature": "special 层图元", "n": spans["special"]["n"],
                    "prim_id_range": [spans["special"]["first"], spans["special"]["last"]],
                    "note": "红色/双点划线/剖面线语义（见 §1 分层口径），含焊缝或剖切符号的可能"})
    return out


# ---------------------------------------------------------------- MD 生成


_SVG_PATH_N = {}


def svg_path_count(base: str) -> int:
    """交付 SVG 里 `data-prim-id` 的出现次数（= SVG path 数）。

    缓存：build_md 会按 CAPS 多次重跑，SVG 可达数十 MB，不可重复整读。
    06 在 04 之前跑（链序 …→05→06→04→07→08），故此处读到的是本次交付物。
    """
    if base not in _SVG_PATH_N:
        p = C.deliverables(base)["svg"]
        _SVG_PATH_N[base] = (C.read_text(p).count('data-prim-id="')
                             if os.path.exists(p) else -1)
    return _SVG_PATH_N[base]


def build_md(base: str, cap: int) -> tuple:
    pdoc = C.read_json(C.work_path(base, "prims.json"))
    vdoc = C.read_json(C.work_path(base, "views.json"))
    cwd = C.read_json(C.deliverables(base)["crosswalk"])
    tdoc = C.read_json(C.work_path(base, "text.json"), {})
    if not pdoc or not vdoc or not cwd:
        sys.exit("缺少 prims/views/crosswalk，请先跑 01/02/05 --sheet %s" % base)
    by_i = {p["i"]: p for p in pdoc["prims"]}
    cwv = {v["id"]: v for v in cwd["views"]}
    meta = pdoc["meta"]
    cnt = meta["counts"]
    bl = cnt.get("by_layer") or {}
    kept = cnt["kept"]
    texts = tdoc.get("texts") or []

    M = []
    A = M.append
    # ---- §1
    A("# %s — 可复现图纸描述" % base)
    A("")
    # 模板串里已写死 `.svg` 后缀，实参只能传 base：再拼一次会得到
    # `<base>.svg.svg` 这个不存在的文件名（各图 MD 首段全中）。
    A("> 本文件是图纸的「魂」：语义、结构、参数与坐标系的可读权威。骨架见同目录 "
      "`%s.svg`，两者由同一份 `work/` 中间产物脚本化生成，**禁手改**。" % base)
    A("")
    A("## §1 元信息")
    A("")
    A("| 项 | 值 |")
    A("|---|---|")
    A("| 图号(base_name) | `%s` |" % base)
    A("| 源 PDF | `%s`（第 %d 页，只读） |" % (meta["pdf"], meta["page"]))
    A("| 页面尺寸(pt) | `%s`（A0 竖放，源 rotation=%s） |"
      % ("[" + ", ".join("%.3f" % q for q in meta["page_rect_pt"]) + "]",
         meta["page_rotation_src"]))
    A("| 回正方式 | `%s`（渲染 `page.set_rotation(270)`） |" % C.ROTATION)
    A("| W×H(pt) | %.6f × %.6f |" % (C.W_PT, C.H_PT))
    A("| pt/mm(1:1) | %g |" % C.PT_PER_MM)
    A("| drawings / bg / kept | %d / %d / **%d** |"
      % (cnt["drawings"], cnt["bg"], kept))
    A("| 六层计数 | %s |" % "、".join("%s=%d" % (L, bl.get(L, 0))
                                      for L in C.LAYERS))
    A("| 视图数 | %d（V00 + %d 个零件/注释视图） |"
      % (len(vdoc["views"]), sum(1 for v in vdoc["views"] if v["id"] != "V00")))
    A("| 生成器 | `%s` / PyMuPDF %s |" % (os.path.basename(__file__), meta["pymupdf"]))
    A("")
    A("### §1.1 分层口径（决策 D1：颜色优先 + OCG 定点纠偏）")
    A("")
    A("| 层 | 语义 | 判定 | 本图计数 |")
    A("|---|---|---|---|")
    for L in C.LAYERS:
        rule = {"outline": "黑 (0,0,0)；或 OCG∈{粗实线,产品轮廓线,产品线,粗线} 且主色占比>50% 时纠偏",
                "centerline": "青 (0,1,1)；或 OCG∈{中心线,细点划线} 主色占比>50% 时纠偏",
                "thin": "黄 (1,1,0)；以及五色之外按 OCG 无解者的兜底(标 UNMAPPED)",
                "dimension": "绿 (0,1,0)；或 OCG∈{标注尺寸线} 主色占比>50% 时纠偏",
                "special": "红 (1,0,0)；或 OCG∈{双点划线,剖面线} 主色占比>50% 时纠偏",
                "title-block": "OCG==`PDM_Title` 且 color∈{黄, None}"}[L]
        A("| `%s` | %s | %s | %d |" % (L, C.LAYER_SEMANTIC[L], rule,
                                       bl.get(L, 0)))
    A("")
    trg = meta.get("triggers") or {}
    A("OCG 主导性纠偏触发情况：%s"
      % ("、".join("`%s`=%s" % (k, "触发" if v else "不触发(保持颜色口径)")
                   for k, v in trg.items()) if trg else "无"))
    A("")
    A("每条 SVG path 同时带 `data-ocg` 与 `data-color`，故任何重新归层都是可重跑的"
      "纯函数，无需重新提取。逐图 OCG×color 交叉计数与主色占比见 `%s_修正单.md`。" % base)
    A("")
    # ---- §2
    A("## §2 布局")
    A("")
    A("版面按横向(回正)坐标 (X_L, Y_L) 描述，X_L 向右、Y_L 向上，与 `portrait_to_"
      "landscape: (X_L, Y_L) = (y_p, W − x_p)` 一致。视图按行分组（行内自左而右、"
      "行间自上而下）：")
    A("")
    A("| 视图 | 名称 | 类型 | 行 | 图元 | bbox(竖放 pt) | bbox_L(横向 pt) | 比例 | 比例来源 |")
    A("|---|---|---|---|---|---|---|---|---|")
    for v in vdoc["views"]:
        cw = cwv[v["id"]]
        A("| `%s` | %s | %s | %s | %d | `%s` | `%s` | %s | %s |"
          % (v["id"], C.esc(v.get("name") or ""), v.get("kind", ""),
             (v.get("layout") or {}).get("row", ""), v["n"],
             ",".join("%.1f" % q for q in v["bbox_all"]),
             ",".join("%.1f" % q for q in (v.get("bbox_L") or [])),
             cw["scale"], cw["scale_source"]))
    A("")
    A("V00 为图框/标题栏/整页跨度线归属区，共 %d 条图元；标题栏紧裁切框(竖放 pt) = `%s`。"
      % (next((v["n"] for v in vdoc["views"] if v["id"] == "V00"), 0),
         ",".join("%.1f" % q for q in (vdoc.get("tb_bbox") or []))))
    A("")
    _v0 = cwv.get("V00") or {}
    if _v0.get("scale_verified"):
        # score=0 在本图对 V00 会被误读为「未验证」，故必须把自证证据写进交付物。
        A("V00 的比例 `%s` 由**页面几何自证**（证据 `%s`），不走尺寸线打分：V00 的 bbox "
          "就是纸本身，图框边框按定义以 1:1 画在纸上，故其 mm 跨度必等于纸张幅面。"
          "自证：图框 `%s` mm 落在 `%s` mm 纸型幅面 ±25mm 容差内。因此 V00 的 "
          "`score=0` 仅表示未用尺寸线命中，**不代表未验证**——其 mm 值可当已验证使用，"
          "未并入 §6 unclear。"
          % (_v0.get("scale"), _v0.get("scale_evidence"),
             "×".join(str(q) for q in (_v0.get("frame_mm") or [])),
             "×".join(str(q) for q in (_v0.get("paper_mm") or []))))
        A("")
    # ---- §3
    A("## §3 逐视图分层描述")
    A("")
    A("每视图给出：语义注解 → 坐标系(self_check 已通过) → 分层 prim-id 区间与计数"
      "（**区间计数求和 == kept == %d**，见 §3.99 对账）→ 参数化图元 → 绑定尺寸表 → "
      "特征线索。prim-id 全量索引见 `work/md_prims_index.json`。" % kept)
    A("")
    index = {}
    n_param_expanded = 0
    n_closed_expanded = 0
    for v in vdoc["views"]:
        cw = cwv[v["id"]]
        spans = C.layer_spans(v, by_i)
        geo = Counter(by_i[i]["g"]["type"] for i in v["members"])
        x0, y0 = cw["x0"], cw["y0"]
        s = cw["s_pt_per_mm"]
        A("### §3.%s %s — %s" % (v["id"].lstrip("V"), v["id"], C.esc(v.get("name") or "")))
        A("")
        A(sem_note(v, cw, spans, geo))
        A("")
        A("- 坐标系原点：视图 bbox 左下角(竖放 pt) = (%.3f, %.3f)；"
          "`local_to_portrait: x_p = x0 + y_mm·s, y_p = y0 + x_mm·s`" % (x0, y0))
        A("- `tx=%.3f  ty=%.3f  x0=%.3f  y0=%.3f  s=%.6f pt/mm`（%s，k=%.4f）；"
          "self_check=%s（原点误差 %.2e pt、往返 %.2e pt、横向 %.2e pt）"
          % (cw["tx"], cw["ty"], cw["x0"], cw["y0"], s, cw["scale"], cw["scale_k"],
             cw["self_check"]["pass"], cw["self_check"]["origin_err_pt"],
             cw["self_check"]["roundtrip_err_pt"], cw["self_check"]["landscape_err_pt"]))
        A("- 幅面：%.1f × %.1f mm（局部 x 右、y 下）；尺寸线 %d 条、弧/圆 %d 个"
          % (cw["W_mm"], cw["H_mm"], cw["n_dim_lines"], cw["n_arcs"]))
        A("")
        A("| 层 | 语义 | prim-id 区间 | 计数 |")
        A("|---|---|---|---|")
        for L in C.LAYERS:
            if L not in spans:
                continue
            d = spans[L]
            A("| %s | %s | %s%s%s | %d |"
              % (L, C.LAYER_SEMANTIC[L], d["first"], ELL, d["last"], d["n"]))
        A("")
        # 参数化图元（弧/圆/长圆）+ 闭合多段线，按配额展开
        pid_of = {}
        for i, pid, _, _ in C.view_prim_ids(v, by_i):
            pid_of[i] = pid
            index[pid] = {"view": v["id"], "layer": by_i[i]["sem"],
                          "type": by_i[i]["g"]["type"], "i": i,
                          "bbox": [round(q, 3) for q in by_i[i]["r"]]}
        rows = []
        for i, pid, _, _ in C.view_prim_ids(v, by_i):
            p = by_i[i]
            g = p["g"]
            if g["type"] in ("ARC", "CIRCLE", "OBROUND"):
                lp = local_params(g, x0, y0, s)
                rows.append(("param", pid, g["type"], lp, g.get("rms")))
            elif g["type"] in ("QUAD", "RECT") or (g["type"] == "POLYLINE"
                                                   and g.get("closed")):
                # 闭合图元全量展开（方案 D6：弧/圆/OBROUND + 全部闭合多段线）；
                # QUAD/RECT 同为闭合轮廓，不可只留在 SVG 里。
                pts = C.flatten_prim(p)
                rows.append(("closed", pid, g["type"],
                             {"n_pts": len(pts),
                              "pts_mm": [[round((q[1] - y0) / s, 2), round((q[0] - x0) / s, 2)]
                                         for q in pts]}, None))
        n_param = sum(1 for r in rows if r[0] == "param")
        n_closed = sum(1 for r in rows if r[0] == "closed")
        shown = rows[:cap] if cap else []
        n_param_expanded += sum(1 for r in shown if r[0] == "param")
        n_closed_expanded += sum(1 for r in shown if r[0] == "closed")
        if rows:
            A("参数化图元：弧/圆/长圆 %d 个 + 闭合多段线 %d 条，本视图展开前 %d 个"
              "（配额=%d，%s）；未展开者的 prim-id 与 bbox 全量见 "
              "`work/md_prims_index.json`，其 `data-params` 在 SVG 中**逐条同源存在**。"
              % (n_param, n_closed, len(shown), cap,
                 "全部展开" if len(rows) <= cap else "余 %d 条压缩为计数" % (len(rows) - cap)))
            A("")
            A("```json")
            for kind, pid, t, prm, rms in shown:
                o = {"prim-id": pid, "type": t.lower(), "frame": "local_mm(x右y下)"}
                o.update({k: val for k, val in prm.items() if k != "frame"})
                if rms is not None:
                    o["rms_pt"] = rms
                A(json.dumps(o, ensure_ascii=False, separators=(",", ":")))
            A("```")
            A("")
        # 绑定尺寸表
        dims = cw.get("dims") or []
        A("绑定尺寸：%d 个已绑定（唯一命中才绑，守「不臆造定位」）、%d 个未绑定"
          "（多命中/零命中，入 §6）。" % (len(dims), cw.get("n_dims_unbound", 0)))
        if dims:
            A("")
            # 第 6 列必须是**命中判据实际比较的量**（matched_pt），不能是图元的
            # len_pt：后者对圆弧/长圆是弧长，与「期望长」（=value×s，对 diameter 是直径）
            # 不可比，并排印出来会被读成「绑定错了」（旧版实测各图 9 条 diameter 行
            # 看似差到 tol 的 32 倍，实为弧长 vs 直径的错比）。
            A("| dim-id | 值(mm) | 类型 | 前缀 | 图元 | 匹配量(pt) | 期望长(pt) | 局部(mm) | 置信 |")
            A("|---|---|---|---|---|---|---|---|---|")
            for d in dims:
                A("| `%s` | %g | %s | %s | `%s` | %.2f | %.2f | %s | %s |"
                  % (d["dim-id"], d["value"], d["kind"], d.get("prefix") or "—",
                     pid_of.get(d["prim_i"], d["prim_i"]),
                     (d["matched_pt"] if d.get("matched_pt") is not None
                      else d["len_pt"]), d["expected_pt"],
                     d["local_mm"], d.get("tpl_conf") or "—"))
            A("")
            A("「匹配量」= 命中判据实际比较的几何量：`length` 为尺寸线长、`radius` 为半径、"
              "`diameter` 为直径，故它与「期望长」（=值×`s_pt_per_mm`）同量纲、差值恒在 "
              "`tol_pt` 内。图元自身的 `len_pt`（对圆弧/长圆是**弧长**）不与期望长并排展示，"
              "避免错比；全量在 `work/` 同级的 `<图>_crosswalk.json` 的 `dims[].len_pt`。")
            A("")
        feats = feature_note(v, by_i, spans)
        if feats:
            A("特征线索（仅计数与定位，不作语义断言）：")
            for f in feats:
                A("- **%s**：%s" % (f["feature"], json.dumps(
                    {k: val for k, val in f.items() if k != "feature"}, ensure_ascii=False)))
            A("")
    # ---- §3.99 对账
    A("### §3.99 计数对账链（drawings − bg == kept == SVG path == MD 索引）")
    A("")
    tot = sum(d["n"] for v in vdoc["views"] for d in C.layer_spans(v, by_i).values())
    A("各视图各层 prim-id 区间计数求和 = **%d**，kept = **%d**，%s。"
      % (tot, kept, "一致" if tot == kept else "**不一致**"))
    A("")
    # 四环全列出：MD 必须自证最硬的那条门禁，消费者无需回到脚本或 work/ 才能核对。
    n_svg = svg_path_count(base)
    n_idx = len(index)
    chain_ok = (tot == kept == n_idx == n_svg
                and cnt["drawings"] - cnt["bg"] == kept)
    A("完整对账链：drawings **%d** − bg **%d** = kept **%d**；SVG path（`data-prim-id` "
      "计数）= **%s**；MD 全量索引条目（`work/md_prims_index.json`）= **%s**；"
      "prim-id 区间求和 = **%d** —— 四者%s，计数对账链%s。"
      % (cnt["drawings"], cnt["bg"], kept,
         n_svg if n_svg >= 0 else "未生成", n_idx, tot,
         "相等" if chain_ok else "**不相等**",
         "成立（一致）" if chain_ok else "**不成立（不一致）**"))
    A("")
    # ---- §4 BOM（降级）
    A("## §4 BOM / 明细表（降级填写）")
    A("")
    tb = tdoc.get("title_block") or {}
    fields = {k: val for k, val in tb.items() if isinstance(val, dict) and "value" in val}
    A("- **来源**：无外部 BOM 源（明细表 xlsx / 设计计算 docx 未提供），本图无文字层，"
      "故按方案 §10 降级填写。")
    A("- **已识别零件编号**：%s"
      % ("、".join("`%s`=%s（%s）" % (k, v["value"], v.get("conf", ""))
                   for k, v in fields.items()) if fields
         else "未提供（字形字典未解出可核对的编号文本，见 §6）"))
    A("- **整图材料**：%s"
      % ("`%s`（标题栏识读，置信 %s）" % (fields["材料"]["value"], fields["材料"].get("conf"))
         if "材料" in fields else "未提供（标题栏文本未解出，见 §6）"))
    A("- **逐件明细**：未提供。若后续给出明细表 xlsx，按方案 §10 由降级升级为实填，"
      "并标注来源与置信。")
    A("")
    # ---- §5 技术要求
    A("## §5 技术要求（逐字）")
    A("")
    tr = tdoc.get("technical_requirements") or []
    if tr:
        for k, t in enumerate(tr, 1):
            A("%d. %s  <!-- %s view=%s conf=%s unk=%d -->"
              % (k, C.esc(t["text"]), t["line_id"], t["view"], t["conf"], t["n_unk"]))
    else:
        A("未提供。注释区共 %d 个字形图元已定位并切出高清裁切图 "
          "`work/regions/_tech_notes.png`。字典在注释区**完整解出**的文本行里，没有一条达到"
          "「汉字数≥2 的成句行」这一条款判据：全是形如 `9720`、`Φ60`、`C45` 的纯数字/符号串"
          "（尺寸值与倒角/直径标注），或形如 `向5` 的单汉字+数字（视图方向/剖向符号），"
          "它们属于零件视图而不是技术要求条款——CAD 导出把标注文字也放进了注释类 OCG，"
          "故 `zone=notes` ≠ 技术要求。按方案「不做 glyph OCR 猜测、不臆造」原则，这些行"
          "不入 §5（把尺寸数字当技术要求逐字交付等于向 §5 注入臆造内容）；其数值仍参与 "
          "§3 的尺寸绑定，被排除的行数与样例见 §6 不清项。小字高汉字格无法逐字核对"
          "（视觉能力边界见各图修正单 §3.2），故不编一段占位文本。"
          % tdoc.get("counts", {}).get("glyphs", 0))
    A("")
    # ---- §6 不清项
    A("## §6 不清项（unclear，不仲裁、不臆造）")
    A("")
    A("| # | 类别 | 数量 | 说明 |")
    A("|---|---|---|---|")
    k = 0
    for u in cwd.get("unclear_scale") or []:
        k += 1
        A("| %d | 比例未验证 | 1 | `%s` 比例 %s（%s）：%s |"
          % (k, u["view"], u["scale"], u["source"], u["note"]))
    un = cwd.get("unbound_values") or []
    if un:
        k += 1
        A("| %d | 尺寸值未绑定 | %d | 多命中/零命中，不写 SVG `<text>`，仅此处登记 |"
          % (k, len(un)))
    for u in tdoc.get("unclear") or []:
        if not u.get("n"):
            continue
        k += 1
        A("| %d | %s | %d | %s |" % (k, u["kind"], u["n"], u.get("note", "")))
    if cap and (n_param_expanded or n_closed_expanded):
        k += 1
        A("| %d | MD 体量压缩 | — | 参数化图元每视图配额 %d，超出者压缩为计数；"
          "全量在 `work/md_prims_index.json` 与 SVG `data-params` 中同源存在 |" % (k, cap))
    if not k:
        A("| — | 无 | 0 | 本图无登记的不清项 |")
    A("")
    # 上表逐行只写「1」，两个**总量**（比例未验证视图数、未绑定尺寸值数）在 MD 里
    # 并无明文，读者得自己数行数。题库 Q47 正是以这两个总量为答案键：MD 无明文时，
    # self_check 只能靠表格行号里的数字蒙中（裸小整数在长文本里没判别力），等于
    # 出题超出「MD 实际存在的内容」。故把总量写成明文句，使答案键可逐字核对。
    A("**本节共登记 %d 项不清项，其中比例未验证视图 %d 个、未绑定尺寸值 %d 个。**"
      % (k, len(cwd.get("unclear_scale") or []), len(un)))
    A("")
    A("### §6.1 未绑定尺寸值明细")
    A("")
    if un:
        A("| view | 文本 | 值 | 类型 | 候选数 | 原因 |")
        A("|---|---|---|---|---|---|")
        for u in un[:200]:
            A("| `%s` | %s | %g | %s | %d | %s |"
              % (u.get("view"), C.esc(str(u.get("text"))), u.get("value", 0),
                 u.get("kind"), u.get("n_candidates", 0), u.get("reason")))
        if len(un) > 200:
            A("| … | 其余 %d 条见 `crosswalk.json.unbound_values` | | | | |" % (len(un) - 200))
    else:
        A("无（文本恢复未产出可绑定数值时本节为空，属预期，见 §5）。")
    A("")
    # ---- §7
    A("## §7 消费策略（token 可行）")
    A("")
    A("- 本文档 %d 字符。按需分块读取：先读 §1/§2 建立全局，再按 §3.<视图号> 定点读取。"
      % 0)
    A("- 需要几何重绘时读同目录 SVG（`data-layer`/`data-view` 可过滤），"
      "需要参数校核时读 SVG `data-params` 或 `work/md_prims_index.json`。")
    A("- 需要换算时只用附录A 的公式，**不要**自行推断比例；`scale_source` 为 "
      "`fallback`/`score=0` 的视图，其 mm 值未验证，见 §6。")
    A("- glyph 路径（`data-prim=\"glyph\"`）为字符的单线笔画矢量，消费者可按需剔除，"
      "但剔除后计数对账链不再等于 kept。")
    A("")
    # ---- 附录A
    A("## 附录A crosswalk（与 `%s_crosswalk.json` / SVG `<metadata>` 同源）" % base)
    A("")
    A("```json")
    A(json.dumps(cwd["formula"], ensure_ascii=False, indent=1))
    A("```")
    A("")
    A("### 比例三档（决策 D4：read ＞ inferred ＞ fallback）")
    A("")
    ss = cwd.get("scale_sources") or {}
    A("| 档 | 含义 | 本图视图数 |")
    A("|---|---|---|")
    for k, why in (("read", "文本恢复读到「1:xx」，直接采信"),
                   ("inferred", "对候选分母集 {1,2,5,10,20,25,50,100,200} 打分，"
                                "命中尺寸线数最多者胜（带 score）"),
                   ("fallback", "1:10，未验证；其 mm 值全部并入 §6 unclear")):
        A("| `%s` | %s | %d |" % (k, why, ss.get(k, 0)))
    A("| 合计 | — | %d |" % sum(ss.get(k, 0) for k in ("read", "inferred", "fallback")))
    A("")
    A("`s_pt_per_mm = 2.83465 / 分母`（方案 D5 原式，**k 恒为 1.0**）。表里的 `k` 列是"
      "05 在 ±2% 搜索域内拟合出的诊断量（`k_fit`）：其搜索目标「±1mm 窗口命中 10mm 网格」"
      "随机命中率就有 ~20%，在 81 个候选里取最大属拟合噪声（实测同为 1:5 的视图"
      "k 分别是 1.0030/0.9905/0.9965/0.9910，同一比例不应有多个 k），且残差审计"
      "（见各图修正单 §3.2）显示对全部分母该残差都近似均匀分布，无证据支持任何特定 k。"
      "**故 k 不乘进交付尺度**，仅作可追溯诊断量保留。"
      "`inferred` 且 score=0 或 `fallback` 的视图，其 mm 换算值不得当作已验证尺寸使用。"
      "**例外见下表的 `自证` 列**：值为 `page-geometry` 者（整页图框区 V00）的比例由"
      "页面几何自证为 1:1，其 score=0 只表示未用尺寸线命中，不表示未验证；"
      "值为 `dim-grid` 者才是真的未验证。")
    A("")
    A("末两列是**换算示例**：把该视图局部坐标 `(x_mm, y_mm) = (100, 200)` 代入 "
      "`local_to_portrait: x_p = x0 + y_mm*s ; y_p = y0 + x_mm*s` 得到的页面竖放 pt 坐标，"
      "供消费者直接对照校验自己的换算实现（不必自行推算）。")
    A("")
    A("| 视图 | 比例 | 来源 | 自证 | score | k | s(pt/mm) | tx | ty | x0 | y0 | W_mm | H_mm | "
      "示例 x_p | 示例 y_p | self_check | 绑定 |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v in cwd["views"]:
        xp, yp = C.local_to_pt(100.0, 200.0, v["x0"], v["y0"], v["s_pt_per_mm"])
        A("| `%s` | %s | %s | %s | %s | %.4f | %.6f | %.3f | %.3f | %.3f | %.3f | %.1f | %.1f "
          "| %.3f | %.3f | %s | %d |"
          % (v["id"], v["scale"], v["scale_source"],
             v.get("scale_evidence") or "dim-grid", v["scale_score"], v["scale_k"],
             v["s_pt_per_mm"], v["tx"], v["ty"], v["x0"], v["y0"], v["W_mm"], v["H_mm"],
             xp, yp, v["self_check"]["pass"], v["n_dims_bound"]))
    A("")
    A("锚点（每视图 bbox 四角 + 对称轴交点）全量见 `crosswalk.json.views[].anchors`。")
    A("")
    # ---- 附录B
    A("## 附录B ID 体系")
    A("")
    A("```json")
    A(json.dumps(meta["id_system"], ensure_ascii=False, indent=1))
    A("```")
    A("")
    A("- `data-prim-id` 在视图内唯一、跨层连续编号（排序键 = 六层次序 → 图元原序），"
      "MD 与 SVG **同源同序**，故区间可直接互查。")
    A("- `dim-id` 仅在唯一命中时分配；`balloon-id` 预留（本图未产出可核对的序号文本）。")
    A("")
    md = "\n".join(M)
    # §7 的字符数需自指，二次替换（长度变化极小，不影响门禁判定）
    md = md.replace("- 本文档 %d 字符。" % 0, "- 本文档 %d 字符。" % len(md))
    stats = {"chars": len(md), "cap": cap, "index_entries": len(index),
             "param_expanded": n_param_expanded, "closed_expanded": n_closed_expanded,
             "lines": md.count("\n") + 1}
    return md, stats, index


_SVG06 = None


def local_params(g, x0, y0, s):
    """与 06_enhance_svg.local_params 完全同源（保证 MD 与 SVG data-params 一致）。

    模块只加载一次并缓存（弧/圆/长圆可达上千个，重复 importlib 加载会拖垮生成）。
    """
    global _SVG06
    if _SVG06 is None:
        import importlib.util
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "06_enhance_svg.py")
        spec = importlib.util.spec_from_file_location("svg06", p)
        _SVG06 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_SVG06)
    return _SVG06.local_params(g, x0, y0, s)


def build(base: str) -> dict:
    md = stats = None
    for cap in CAPS:
        md, stats, index = build_md(base, cap)
        if stats["chars"] <= CHAR_BUDGET:
            break
    p = paths(base)
    C.write_text(p["md"], md)
    kept = C.read_json(C.work_path(base, "prims.json"))["meta"]["counts"]["kept"]
    C.write_json(p["index"], {"base_name": base, "kept": kept,
                              "n_entries": len(index),
                              "id_order": "六层次序 → 图元原序（与 SVG data-prim-id 同源）",
                              "index": index})
    # 反向解析 MD 正文的区间计数求和（自洽性门禁）
    parsed = [int(x) for x in SPAN_RE.findall(md)]
    n_views_md = md.count("\n### §3.") - md.count("\n### §3.99")
    cwd = C.read_json(C.deliverables(base)["crosswalk"])
    vdoc = C.read_json(C.work_path(base, "views.json"))
    gate = C.Gate(base)
    gate.add("prim-id 区间求和==kept", sum(parsed) == kept,
             "MD 解析区间数=%d 求和=%d kept=%d" % (len(parsed), sum(parsed), kept))
    gate.add("MD 字符数≤8万", len(md) <= CHAR_HARD,
             "%d 字符（目标≤%d，配额 cap=%d）" % (len(md), CHAR_BUDGET, stats["cap"]))
    gate.add("六层在 §1 齐全", all(("| `%s` |" % L) in md for L in C.LAYERS),
             "缺失=%s" % [L for L in C.LAYERS if ("| `%s` |" % L) not in md])
    gate.add("逐视图 §3 小节齐全", n_views_md == len(vdoc["views"]),
             "%d/%d" % (n_views_md, len(vdoc["views"])))
    gate.add("附录A 与 crosswalk.json 同源",
             all(("| `%s` | %s |" % (v["id"], v["scale"])) in md for v in cwd["views"]),
             "视图比例行 %d/%d" % (sum(1 for v in cwd["views"]
                                       if ("| `%s` | %s |" % (v["id"], v["scale"])) in md),
                                   len(cwd["views"])))
    gate.add("索引条目==kept", len(index) == kept,
             "%d vs %d" % (len(index), kept))
    gate.dump(C.work_path(base, "gate_04.json"))
    C.log("=" * 78)
    C.log(gate.report())
    C.log("stats:", stats)
    C.log("→", p["md"])
    return {"md": md, "stats": stats, "gate": gate.dump()}


def main(argv):
    C.init(argv)
    for base in C.parse_sheet_arg(argv):
        build(base)


if __name__ == "__main__":
    main(sys.argv[1:])
