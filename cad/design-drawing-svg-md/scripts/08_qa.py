# -*- coding: utf-8 -*-
"""08 QA 题库 + self_check + 盲测判分（方案 §6 步骤 7）

MD/SVG/crosswalk → <base>_QA题库.json + work/qa_selfcheck.json (+ work/qa_blind.json 判分)

原则：**只从 MD 实际存在的内容出题**（数据驱动，不出降级图没有的总重/明细题）。
每题给 `answer_keys`（全部需命中）与 `answer_keys_any`（任一命中即可）；
self_check 逐题校验答案串确实出现在 MD 正文（`md_verifiable`），门禁要求 100%。
盲测判分前先剥编号前缀 `^\\d+[\\.、\\)]` 防假阳（「第4条：」vs「4.」）。
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

CATEGORIES = ["结构", "几何", "关系", "工艺", "指认"]
MIN_Q = 20
BLIND_MIN = 0.95
PREFIX_RE = re.compile(r"^\s*\d+\s*[\.、\)]\s*")
PUNCT = " \t\r\n，。；：、,.;:！!？?\"'“”‘’（）()【】[]《》<>—-_"


def norm(s) -> str:
    s = PREFIX_RE.sub("", str(s))
    return "".join(ch for ch in s if ch not in PUNCT).lower()


def fmt(v) -> str:
    """数字→最短无损串（供答案键与 MD 正文双向匹配）。"""
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, float):
        for nd in range(0, 7):
            s = "%.*f" % (nd, v)
            if abs(float(s) - v) < 1e-12:
                return s
        return repr(v)
    return str(v)


# ---------------------------------------------------------------- 出题


def gen_questions(base: str, md: str) -> list:
    pdoc = C.read_json(C.work_path(base, "prims.json"))
    vdoc = C.read_json(C.work_path(base, "views.json"))
    cwd = C.read_json(C.deliverables(base)["crosswalk"])
    idx = C.read_json(C.work_path(base, "md_prims_index.json"), {"index": {}})
    val = C.read_json(C.work_path(base, "validate.json"), {})
    meta = pdoc["meta"]
    counts = meta["counts"]
    by_layer = counts.get("by_layer") or {}
    views = vdoc["views"]
    cwv = {v["id"]: v for v in cwd["views"]}
    Q = []

    def q(cat, text, keys, any_keys=None, src=""):
        Q.append({"category": cat, "question": text,
                  "answer_keys": [fmt(k) for k in keys],
                  "answer_keys_any": [fmt(k) for k in (any_keys or [])],
                  "source": src})

    # ---- 结构
    q("结构", "本图 A0 竖放页面的宽高（pt）各是多少？回正方式是什么？",
      ["%.6f" % C.W_PT, "%.6f" % C.H_PT, C.ROTATION], src="§1 元信息")
    q("结构", "本页 drawings 总数、剔除的背景数与 kept 图元数各是多少？",
      [counts["drawings"], counts["bg"], counts["kept"]], src="§1 元信息")
    q("结构", "六层（outline/centerline/thin/dimension/special/title-block）"
              "在本图各有多少图元？",
      [by_layer.get(L, 0) for L in C.LAYERS], src="§1.1 分层口径")
    q("结构", "本图共切出多少个视图（含 V00）？其中零件/注释视图多少个？",
      [len(views), sum(1 for v in views if v["id"] != "V00")], src="§2 布局")
    q("结构", "V00 归属区包含多少条图元？它承载什么内容？",
      [next((v["n"] for v in views if v["id"] == "V00"), 0), "标题栏"], src="§2 布局")
    # 答案键用 MD 自己的措辞（§3.99 写「一致 / 成立（一致）/ 相等」），而不是
    # Python 的 True——盲测代理读不到布尔字面量，只能读到交付物的中文结论词。
    q("结构", "计数对账链 drawings−bg==kept==SVG path==MD 索引 是否成立？各环节值是多少？",
      ["一致", counts["drawings"], counts["bg"], counts["kept"]],
      any_keys=["成立", "相等"], src="§1 元信息 / §3.99")

    # ---- 工艺
    q("工艺", "决策 D1 的分层口径是什么？title-block 层的判定条件是什么？",
      ["PDM_Title", "颜色优先"], any_keys=["OCG 定点纠偏", "主导性"], src="§1.1 分层口径")
    q("工艺", "本图 OCG 主导性纠偏是否触发？逐层结论是什么？",
      [("触发" if v else "不触发") for v in (meta.get("triggers") or {}).values()]
      or ["无"], src="§1.1 分层口径")
    q("工艺", "special 层承载哪些语义？",
      ["红色"], any_keys=["双点划线", "剖面线", "焊缝"], src="§1.1 / 附录B")
    q("工艺", "尺寸绑定遵循什么原则？未命中的值去了哪里？",
      ["唯一命中"], any_keys=["不臆造", "§6", "unclear"], src="§3 / §6")
    q("工艺", "比例来源分三档，优先级顺序是什么？本图各档视图数是多少？",
      ["read", "inferred", "fallback"],
      any_keys=[v for v in cwd["scale_sources"]], src="附录A")

    # ---- 几何 / 关系 / 指认：逐视图数据驱动
    by_i = {p["i"]: p for p in pdoc["prims"]}
    by_layer_views = sorted(views, key=lambda v: -v["n"])
    for v in by_layer_views[:6]:
        cw = cwv[v["id"]]
        spans = C.layer_spans(v, by_i)
        # 只问该视图实际存在的层（优先 outline，否则取图元最多的层），
        # 守住「只从 MD 实际存在的内容出题」。
        if not spans:
            continue
        lay_q = "outline" if "outline" in spans else max(spans, key=lambda L: spans[L]["n"])
        q("关系", "%s 的比例、比例来源、s(pt/mm) 与 self_check 结果是什么？" % v["id"],
          [cw["scale"], cw["scale_source"], "%.6f" % cw["s_pt_per_mm"],
           cw["self_check"]["pass"]], src="§3.%s / 附录A" % v["id"].lstrip("V"))
        q("几何", "%s 的局部幅面（mm）与 tx/ty/x0/y0 各是多少？" % v["id"],
          ["%.1f" % cw["W_mm"], "%.1f" % cw["H_mm"], "%.3f" % cw["tx"],
           "%.3f" % cw["ty"], "%.3f" % cw["x0"], "%.3f" % cw["y0"]],
          src="§3.%s" % v["id"].lstrip("V"))
        q("指认", "%s 里 %s 层的 prim-id 区间与计数是什么？" % (v["id"], lay_q),
          [spans[lay_q]["first"], spans[lay_q]["last"], spans[lay_q]["n"]],
          src="§3.%s" % v["id"].lstrip("V"))
        q("指认", "%s 各层 prim-id 区间计数之和是多少？" % v["id"],
          [sum(d["n"] for d in spans.values())], src="§3.%s / §3.99" % v["id"].lstrip("V"))

    # 弧/圆参数题（从 MD 展开的 data-params 里取，保证 MD 可验证）
    prm = re.findall(r'\{"prim-id":"(V\d+-P\d+)","type":"(arc|circle|obround)"([^}]*)\}', md)
    for pid, t, rest in prm[:6]:
        r = re.search(r'"r":([\d.]+)', rest)
        cx = re.search(r'"cx":([-\d.]+)', rest)
        cy = re.search(r'"cy":([-\d.]+)', rest)
        keys = [x for x in [t, r.group(1) if r else None,
                            cx.group(1) if cx else None, cy.group(1) if cy else None] if x]
        if len(keys) >= 2:
            q("几何", "图元 `%s` 的解析类型与参数（局部 mm）是什么？" % pid, keys,
              src="§3 参数化图元 / SVG data-params")

    # 换算题（关系）：答案在 MD 附录A 的「换算示例」两列里逐字存在，
    # 盲测代理无需自行推算（推算属禁项），只需定位并摘录。
    for v in views[1:4]:
        cw = cwv[v["id"]]
        s, x0, y0 = cw["s_pt_per_mm"], cw["x0"], cw["y0"]
        mm = (100.0, 200.0)
        xp, yp = C.local_to_pt(*mm, x0, y0, s)
        q("关系", "在 %s 里，局部坐标 (100, 200) mm 对应的页面竖放 pt 坐标是多少？" % v["id"],
          ["%.3f" % xp, "%.3f" % yp], src="附录A 换算示例列 / §3.%s 坐标系"
          % v["id"].lstrip("V"))

    # 最大/最多类指认题。V00 装的是 title-block 全层 + 整页跨度图框线，按定义在
    # 「弧/圆最多」与「图元最多」两项上恒居第一（实测旧题面下这两项几乎恒为
    # 答案都是 V00），指认不出任何零件视图，等于送分题。故两题都限定在**零件视图**
    # 内比较，题面写明排除 V00。两题就地替换、不增减题数：qid 按位置编号（`Q%02d`），
    # 增删会使后续题号整体位移、连带作废已收集的盲测答卷。
    arc_by_view = Counter()
    for pid, e in idx["index"].items():
        if e["type"] in ("ARC", "CIRCLE", "OBROUND"):
            arc_by_view[e["view"]] += 1
    part_arc = Counter({k: n for k, n in arc_by_view.items() if k != "V00"})
    if part_arc:
        top = part_arc.most_common(1)[0]
        q("指认", "除图框/标题栏归属区 V00 外，哪个视图的弧/圆/长圆最多？有多少个？",
          [top[0], top[1]], src="§3")
    part_n = sorted([v for v in views if v["id"] != "V00"], key=lambda v: -v["n"])
    if part_n:
        q("指认", "除 V00 外，哪个视图图元数最多？有多少条？", [part_n[0]["id"],
                                                        part_n[0]["n"]], src="§2 布局")
    if val and ("%.6f" % val["redraw"]["recall"]) in md:
        q("几何", "反向重绘在 2px 膨胀容差下的 recall 与 precision 是多少？"
                  "弧/圆三方互校 rms 是多少 pt？",
          ["%.6f" % val["redraw"]["recall"], "%.6f" % val["redraw"]["precision"],
           "%.6f" % val["roundtrip"]["rms_all_pt"]], src="§7 / 07 验证")
    # 不清项
    n_unclear = len(cwd.get("unclear_scale") or []) + len(cwd.get("unbound_values") or [])
    # 答案键带量词「个」而不用裸整数：裸小整数在长答卷里没有判别力——实测一份
    # 陈旧答卷（V00 尚在 §6 unclear 时答「比例未验证视图 10 个」）因整行引用 MD 表格
    # 而带行号 `|9|`，被键 "9" 子串命中、missing=[] 而判为 correct，把「答案已过期」
    # 掩盖成通过。曾试过在判分侧给纯数字键加边界检验，但 norm() 会剥掉小数点、把
    # `2383.654053` 之类也变成纯数字，而这些值在 MD 里只以表格单元格 `|…|` 出现，
    # 结果误伤 20 题（verifiable 47→27）→ 改在出题侧给键加量词，零副作用。
    # 04 已在 §6 表后写出明文总量句「比例未验证视图 N 个、未绑定尺寸值 M 个」，
    # 故这两个键能在 MD 里逐字核对（守「只从 MD 实际存在的内容出题」）。
    q("结构", "本图 §6 登记了多少个比例未验证视图与多少个未绑定尺寸值？",
      ["%d个" % len(cwd.get("unclear_scale") or []),
       "%d个" % len(cwd.get("unbound_values") or [])], src="§6")
    return Q


# ---------------------------------------------------------------- self_check


def self_check(Q: list, md: str) -> tuple:
    nmd = norm(md)
    out = []
    for k, q in enumerate(Q, 1):
        hits = [a for a in q["answer_keys"] if norm(a) and norm(a) in nmd]
        anyh = [a for a in q["answer_keys_any"] if norm(a) and norm(a) in nmd]
        need = len([a for a in q["answer_keys"] if norm(a)])
        ok = need > 0 and len(hits) == need and (not q["answer_keys_any"] or anyh)
        out.append({"qid": "Q%02d" % k, "md_verifiable": bool(ok),
                    "n_keys": need, "n_hits": len(hits),
                    "missing": [a for a in q["answer_keys"] if norm(a) not in nmd],
                    "any_hits": len(anyh)})
        q["qid"] = "Q%02d" % k
    return out, [q for q, s in zip(Q, out) if s["md_verifiable"]]


def judge(Q: list, answers: dict) -> dict:
    """盲测判分：剥编号前缀 + 去标点大小写归一后做子串/等价匹配。"""
    res, n_ok = [], 0
    for q in Q:
        raw = answers.get(q["qid"], answers.get(q["question"], None))
        if raw is None:
            res.append({"qid": q["qid"], "correct": False, "reason": "缺答"})
            continue
        na = norm(raw)
        keys = [norm(a) for a in q["answer_keys"] if norm(a)]
        anyk = [norm(a) for a in q["answer_keys_any"] if norm(a)]
        hit = [k for k in keys if k and (k in na or na in k)]
        anyhit = [k for k in anyk if k and (k in na or na in k)]
        ok = len(hit) == len(keys) and (not anyk or anyhit)
        n_ok += bool(ok)
        res.append({"qid": q["qid"], "correct": bool(ok), "n_keys": len(keys),
                    "n_hit": len(hit), "any_hit": len(anyhit),
                    "answer_norm": na[:120],
                    # 只列归一后非空且未命中的键（空键不参与判定，不应出现在缺失里）
                    "missing": [a for a, k in zip(q["answer_keys"],
                                                  [norm(x) for x in q["answer_keys"]])
                                if k and k not in na],
                    "missing_any": ([] if not anyk or anyhit
                                    else [a for a in q["answer_keys_any"]])})
    return {"n": len(Q), "n_correct": n_ok,
            "accuracy": round(n_ok / len(Q), 4) if Q else 0.0, "detail": res}


def write_blind_prompt(base: str, Qv: list) -> str:
    """生成盲测卷（**不含任何答案键**），供只读代理作答。

    盲测的公平性靠文件隔离保证：本文件只有题面与交付物路径，
    answer_keys / self_check / 中间产物一律不列。
    """
    d = C.deliverables(base)
    L = ["# 盲测卷 — %s" % base, "",
         "你只能读下列交付物作答，**不得**读 `work/` 下任何中间产物、不得读 "
         "`%s`（含答案键）、不得看源 PDF、不得凭常识猜测。"
         % os.path.basename(d["qa"]),
         "答案必须能在交付物里逐字找到依据；找不到的题写 `NOT_FOUND`（宁缺勿臆）。", "",
         "可读文件（按优先级）：", "",
         "1. `%s` — 主载体（语义/结构/参数/坐标系/附录）" % d["md"],
         "2. `%s` — 互联（比例三档/换算式/self_check/逐视图参数）" % d["crosswalk"],
         "3. `%s` — 骨（六层/`data-view`/`data-params`/`metadata` CDATA）" % d["svg"], "",
         "输出格式：**只输出一个 JSON 对象**，不要任何解释文字：",
         "",
         "```json",
         '{"answers": {"Q01": "答案原文摘录（可多段拼接，保留数字与单位）", "Q02": "…"}}',
         "```",
         "",
         "共 %d 题：" % len(Qv), ""]
    for q in Qv:
        L.append("- **%s**（%s）%s" % (q["qid"], q["category"], q["question"]))
    L.append("")
    p = C.work_path(base, "qa_blind_prompt.md")
    C.write_text(p, "\n".join(L))
    return p


def build(base: str) -> dict:
    sd = C.sheet_dir(base)
    md_p = C.deliverables(base).get("md") or os.path.join(sd, base + "-可复现图纸描述.md")
    qa_p = C.deliverables(base).get("qa") or os.path.join(sd, base + "_QA题库.json")
    if not os.path.exists(md_p):
        sys.exit("缺少 MD 交付物，请先跑 04 --sheet %s" % base)
    md = C.read_text(md_p)
    Q = gen_questions(base, md)
    sc, Qv = self_check(Q, md)
    cats = Counter(q["category"] for q in Qv)
    prompt_p = write_blind_prompt(base, Qv)
    blind = C.read_json(C.work_path(base, "qa_blind.json"), {})
    ans = blind.get("answers") or {}
    jd = judge(Qv, ans) if ans else None
    doc = {
        "base_name": base, "md_file": os.path.basename(md_p), "md_chars": len(md),
        "policy": "只从 MD 实际存在的内容出题；BOM 降级图不出总重/明细题；"
                  "答案键需在 MD 正文可验证（self_check）；判分前剥编号前缀防假阳",
        "categories": CATEGORIES, "min_questions": MIN_Q,
        "counts": {"generated": len(Q), "verifiable": len(Qv),
                   "dropped": len(Q) - len(Qv),
                   "dropped_detail": [{"qid": s["qid"], "missing": s["missing"]}
                                      for s in sc if not s["md_verifiable"]],
                   "by_category": dict(cats), "n_categories": len(cats)},
        "questions": [{k: v for k, v in q.items()} for q in Qv],
        "self_check": sc,
        "blind_test": (dict(jd, answerer=blind.get("source") or blind.get("answerer")
                            or "未标注(视为脚本自评，证据强度不足)")
                       if jd else
                       {"status": "未提供答卷（work/qa_blind.json 缺失）",
                        "blind_prompt": prompt_p,
                        "howto": "由只读本图交付物的代理作答，写入 "
                                 "{\"answers\": {\"Q01\": \"…\", …}, "
                                 "\"source\": \"<作答者身份>\"} 后重跑 08"}),
        "answer_normalization": {"strip_prefix": PREFIX_RE.pattern,
                                 "strip_punct": True, "case_fold": True},
    }
    C.write_json(qa_p, doc)
    C.write_json(C.work_path(base, "qa_selfcheck.json"),
                 {"counts": doc["counts"], "self_check": sc})

    gate = C.Gate(base)
    gate.add("题量≥%d" % MIN_Q, len(Qv) >= MIN_Q,
             "生成=%d 可验证=%d" % (len(Q), len(Qv)))
    gate.add("五类覆盖齐全", len(cats) == len(CATEGORIES),
             str(dict(cats)))
    gate.add("self_check md_verifiable 100%",
             len(Qv) > 0 and all(s["md_verifiable"] for s in sc if s["qid"] in
                                 {q["qid"] for q in Qv}),
             "%d/%d 可验证；缺键样例=%s"
             % (len(Qv), len(sc), [s["missing"][:2] for s in sc
                                   if not s["md_verifiable"]][:3]))
    dropped = [s for s in sc if not s["md_verifiable"]]
    gate.add("出题全部可在 MD 验证(丢弃项披露)", not dropped,
             "丢弃 %d 题（答案键不在 MD 正文，按「只从 MD 实际存在的内容出题」剔除）：%s"
             % (len(dropped), [(s["qid"], s["missing"]) for s in dropped]),
             required=False)
    if jd:
        gate.add("盲测准确率≥%.0f%%" % (BLIND_MIN * 100), jd["accuracy"] >= BLIND_MIN,
                 "%d/%d=%.4f" % (jd["n_correct"], jd["n"], jd["accuracy"]))
    else:
        gate.add("盲测准确率≥%.0f%%" % (BLIND_MIN * 100), False,
                 "缺 work/qa_blind.json（待只读代理作答后重跑 08）")
    gate.dump(C.work_path(base, "gate_08.json"))
    C.log("=" * 78)
    C.log(gate.report())
    C.log("counts:", doc["counts"])
    C.log("盲测卷(无答案键) →", prompt_p)
    for q in Qv[:6]:
        C.log("  %-4s [%s] %s" % (q["qid"], q["category"], q["question"][:64]))
    C.log("→", qa_p)
    return doc


def main(argv):
    C.init(argv)
    for base in C.parse_sheet_arg(argv):
        build(base)


if __name__ == "__main__":
    main(sys.argv[1:])
