---
name: design-drawing-svg-md
description: "Use when converting vector PDF engineering drawings (steel-structure shop drawings, A0 drawings, linework-only PDFs without a text layer) into LLM-consumable dual-carrier records — semantic Markdown reading thread plus layered SVG geometry archive linked by shared IDs and crosswalk."
tags:
  - cad
  - svg
  - markdown
  - pdf
  - steel-structure
  - drawing
  - llm
  - workflow
---

> **技能定位：** 设计图 SVG+MD 双载体记录方法论——把"会画不懂"的矢量 PDF 工程图，转化为大模型能准确理解、指认与复刻的交付物。
>
> **方法来源：** 一套钢结构施工图数字化执行方案的固化与泛化；文中数字为示例值或多图实测值，执行时以实际图纸实测为准。
>
> **适用输入：** 矢量线画 + 无文字层的 PDF 工程图（彩色分层或单色均可）。
>
> **脚本资产：** 本仓库 `scripts/` 目录附带可直接复跑的泛化脚本——共用库 [scripts/common.py](scripts/common.py)、入口配置 [scripts/config.example.json](scripts/config.example.json)、十一阶段脚本 `01_extract.py` … `09_verify_deliverables.py`（执行顺序与门禁见 [reference/pipeline.md](reference/pipeline.md)）。

---

## 概述

**MD 是"大模型阅读主线"，SVG 是"高精度几何档案 + 按需切片源"，两者用统一 ID 体系互联，用校验闭环保证一致。**

### 何时使用

- 需要让大模型/Agent 理解一份工程图纸（几何、尺寸、语义、工艺、管理信息）
- 源图为 PDF，且是矢量线画、无文字层（尺寸数字只是 glyph 轮廓路径，直接渲染"会画不会读"）
- 需要对图纸做问答、复刻重绘、改图、核量、生成 BOM 等下游任务
- 图纸会换版（R00→R01），需要可 diff、可追溯的数字化档案

### 何时不使用

- 源图已有文字层且无需精确几何 → 直接 PDF 文本提取即可
- 只需一张渲染图给人看，无下游智能任务 → 不必建双载体
- 栅格扫描件 → 本技能不覆盖矢量化（OCR/矢量化另案处理）

### 适用对象

A0 钢结构施工图（无文字层的矢量线画）为典型用例；任何"矢量线画 + 无文字层"的 PDF 工程图均可套用。

---

## 核心概念

### 双载体定位

```
原图 PDF（矢量线画 / 无文字层 / 彩色分层）
   │  提取（fitz.get_drawings + 分层：OCG 语义优先 + 颜色兜底）
   ▼
MD（魂·阅读主线） ◄── ID 互联（view/dim/balloon/prim-id + crosswalk） ──► SVG（骨·几何档案）
语义/参数/值/工艺/BOM                                       原生坐标/图层/视图分组/文本
   │                                                                    │
   └──────── 校验闭环（MD 重绘 ⇄ SVG 叠合 ⇄ 原图）──────────────────────┘
   └──────── 消费（MD 全文分块 + SVG 按视图切片）────────────────────────┘
```

### 三条设计原则

1. **单一事实源**：每类信息只在一处为"真"，另一处只引用不复制（分工矩阵见下），避免双份漂移。
2. **ID 互联而非坐标复制**：MD 保留局部 mm 参数坐标（可编辑），SVG 保留页面 pt 原生坐标（精确），换算关系写入 crosswalk。
3. **token 可行**：MB 级 SVG 不整份进上下文；MD 为索引，SVG 按 `data-view` 切片按需取。

### 为什么不只用单一载体

| 载体 | 优势 | 短板 |
|---|---|---|
| 仅 SVG | 像素级可复刻 | 对模型是坐标流——"会画不懂"（无文字层时尺寸数字只是轮廓路径） |
| 仅 MD | 结构语义可读、可编辑 | "看懂画不准"（细节图元易被省略、无法精确指认） |

### 理解准确性的四个分量

大模型"准确理解" = **几何精度 × 语义完整 × 可指认 × token 可行**，缺一不可：

| 分量 | 含义 | 落点 |
|---|---|---|
| 几何精度 | 每条线的位置/类型/参数可复现 | SVG 原生坐标 + MD 参数图元互校 |
| 语义完整 | 每根线"是什么"、每个视图"看的是什么"、工艺与管理要求 | MD 语义层 + SVG `data-*` 属性 |
| 可指认 | 文档里每句话能定位到原图确切位置 | ID + crosswalk + 布局表 |
| token 可行 | 装得进上下文 | MD 分块读、SVG 按视图切片读 |

---

## 载体分工矩阵（单一事实源）

| 信息项 | 事实源 | 另一载体 |
|---|---|---|
| 页面级精确坐标、线宽、图层归属 | **SVG** | MD 不复制页面坐标 |
| 参数化几何（局部 mm、可改图） | **MD** | SVG 不存参数，仅存形状 |
| 尺寸/半径/角度/厚度的值 | **MD**（dims 表） | SVG `<text data-value>` 作显示层 |
| 视图划分、归属、比例、投影/剖切关系 | **MD** | SVG `data-view` 镜像 |
| 弧/长圆孔的参数（R、len、w、orient） | **MD** | SVG 以 `data-params` 旁注，不依赖折线近似 |
| 气球↔零件↔BOM、重量/材质 | **MD** | — |
| 标题栏、技术要求（逐字） | **MD** | SVG `<metadata>` 镜像 |
| 功能语义自然语言注解 | **MD** | — |
| 不清/待确认项 | **MD** | — |
| 换算关系（旋转/比例/平移） | **crosswalk**（MD 附录 + SVG metadata 各存一份，脚本同源生成） | — |
| 渲染兼容性约束（不用 crispEdges、剔除纯白背景矩形、OCG 语义优先 + 颜色兜底的分层映射） | **SVG**（生成时内建） | MD 不复制 |

**冲突仲裁：** 几何坐标以 SVG 为准；值与语义以 MD 为准；不一致时由校验闭环（流水线步骤 8）产出修正单，人工确认后回写。

---

## ID 体系与 crosswalk 换算链

### ID 体系

| ID | 对象 | 出现位置 |
|---|---|---|
| `V{nn}` | 视图 | SVG `data-view` / MD 章节标题 |
| `V{nn}-P{mm}` | 几何图元 | SVG `data-prim-id` / MD 图元 JSON |
| `V{nn}-D{mm}` | 尺寸标注 | SVG `data-dim-id`（线与 text 同号）/ MD dims 表 |
| `V{nn}-B{mm}` | 气球（零件编号） | MD 标注章 |

### 换算链

MD 参数坐标（x, y）= 视图局部 mm，原点 = 视图 bbox 左下角，X 右 Y 上；s = 2.83465 / 比例分母（pt/mm）：

```
X_L = x·s + tx          Y_L = −y·s + ty
页面 pt（竖放）：x_p = W − Y_L          y_p = X_L
```

- **回正规则（唯一结论）：** 页面内容回正 = 逆时针 90°（ccw90）；fitz 调用 `page.set_rotation(270)`。
- **自检（self_check）：** 局部原点 (0,0) 换算后必须落在该视图 bbox 左下角（x_p = bbox 左界、y_p = bbox 下界）。
- s、tx/ty 与各坐标值均为示例值（如 1:20 → s≈0.14173）；实际图纸以配准（流水线步骤 5）实测为准。
- crosswalk 条目 JSON 全文见 [reference/md-spec.md](reference/md-spec.md)。

---

## 生产与校验流水线（11 步）

完整职责、脚本执行顺序、关键依赖与门禁矩阵见 [reference/pipeline.md](reference/pipeline.md)；本节只留步骤索引 + 门禁矩阵。文中数字均为多图实测值。**语义步骤号 ≠ 执行顺序**（如 06 SVG 生成在 04 MD 增补之前执行），执行顺序以 [reference/pipeline.md](reference/pipeline.md) §2 为准。

1. **矢量提取 + 分层**（`01_extract.py`）：`fitz.get_drawings()` 按 **OCG 语义优先 + 颜色兜底** 归六层（颜色→层硬映射对部分图失效）；title-block 靠 OCG `layer==PDM_Title` 独立成层，否则退化为五层不合规。
2. **视图聚类归属**（`02_cluster_views.py`）：outline + dimension + centerline 空间聚类（排除 thin 层）；**视图数是聚类输出、非可预设目标**（实测区间 [8,26]）。
3. **跨图字形字典**（`03`/`03c`/`03d`）：模板聚类 → 自监督解码 → 视觉逐行对账，跨图合并；**视觉识读过双闸门**（图号真值 + 转录字符数核对）才入字典。
4. **文本恢复**（`03b_text_recover.py`）：按视图 bbox 高清竖正裁切识读 → `<text>` + dim-id 绑定；竖排归一化必须用 `(x,y) → (1−y, x)`（旧式 `(y, 1−x)` 缺平移校正、静默降质）。
5. **配准**（`05_crosswalk.py`）：逐视图定尺度/旋转/平移 → crosswalk 的 tx/ty + `self_check`；比例三档 read/inferred/fallback（实测 read 档全 0，inferred score=0 归 fallback）；V00 整页图框区用 `frame_scale()` 页面几何自证 1:1。
6. **SVG 生成**（`06_enhance_svg.py`）：按六层 + 视图分组生成增强版 SVG（骨）——`data-*` 属性、`<text>` 尺寸绑定、弧/圆参数旁注、metadata 同源镜像（见 [reference/svg-spec.md](reference/svg-spec.md)）。
7. **MD 增补**（`04_build_md.py`）：补 ID / 语义注解段 / crosswalk → 重建 MD（三条硬约束见 [reference/md-spec.md](reference/md-spec.md)）。
8. **三方互校**（`07_validate.py`）：MD 重绘 ⇄ SVG 叠合（**2px 膨胀容差度量，recall≥0.99 门禁**）；绿层值集合 ⇄ dims（**绑定率非门禁**，未绑定值只入 MD §6）；BOM ⇄ 气球。
9. **LLM 验收**（`08_qa.py`）：题库 ≥20 题 + 盲测子代理只读交付物作答，准确率 ≥95% 方交付。
10. **独立审计**（`spec_audit`/`final_audit` 探针）：不复用生成器判定，从交付物 + 源 PDF 重算方案条款。
11. **交付物齐套**（`09_verify_deliverables.py`）：六件套齐套 + 门禁汇总 + 基线对账（见交付物与命名章）。

### 关键实测结论（多图验证）

- **分层**：OCG 语义优先 + 颜色兜底；纠偏只在主色占比 >50% 时触发，逐图落盘 `meta.triggers` + 分层审计表。
- **竖排归正式**：`(x,y) → (1−y, x)`；写错是静默降质（模板虚增 1010→1031、竖排已解行 129→1）。
- **视图数不可预设**：是聚类输出（实测 [8,26]），不得为对齐基线数字调参或加机制。
- **绿层绑定率非门禁**：上限是字典标签覆盖率（31/1010），未绑定值只入 MD §6 不清项。
- **比例三档** read/inferred/fallback；实测 read 档全 0，`score=0` 仍叫 `inferred` 有误导 → 归 `fallback`。
- **视觉识读双闸门**：图号真值（单行转录最长公共子串）+ 转录字符数核对（容差 0）；第一道未过整图不采信。
- **三方互校容差度量**：2px 膨胀 + recall/precision/F1，门禁 recall≥0.99；严格 IoU 假性偏低仅参考；precision 不作门禁。
- **V00 比例**：`frame_scale()` 页面几何自证 1:1，不打分。
- **MD 三条硬约束**：单文件 ≤80000 字符、总量类问题须有明文句子可逐字核对、§3 须给 prim-id 区间 + 计数且区间求和 == kept。

### 门禁矩阵（硬门禁 12 项 vs 基线对账）

| 类别 | 含义 | 项 | 不达标动作 |
|---|---|---|---|
| **硬门禁** | 交付物自洽性与合规性，**必须全过** | 计数链四相等、六层齐全（含独立 title-block）、无 `UNASSIGNED`、recall≥0.99、rms≤0.1pt、载体一致性、`self_check` 全过、QA≥20 题、五类齐全、QA 自检 100%、盲测≥95%、MD≤80000 字符 | 回相应阶段修正后重跑，不得放行 |
| **基线对账** | 与参照数值比较，**只记录并解释** | 逐层图元数、视图数、绑定率、recall/rms 具体数值 | 写清机制差异；**禁止为对齐数字调参或加机制** |

---

## 验收题库

每图 ≥20 题、覆盖五类；题库与答案单独成 JSON 交付物。验收时仅把交付物（MD + SVG 切片）喂给模型，不喂本技能与方案文档。

| 类别 | 考察点 | 示例题（示例值） |
|---|---|---|
| 结构类 | 总量/材质（BOM） | 本图共几件？总重？件11 数量/材质？ |
| 几何类 | 参数值（dims） | 件11 圆头半径、起吊孔径、斜边角？ |
| 关系类 | 视图关系 | A-A 剖切经过哪些件？V16 是哪个位置的放大？ |
| 工艺类 | 技术要求 | 吊耳底部焊缝高度与无损等级？未注焊缝？ |
| 指认类 | ID→语义定位 | V15-D03 标注的是哪个视图的哪个零件的哪个方向？ |

**验收标准：** 结构/几何/关系/工艺类准确率 ≥95%，指认类 100%，方视为"大模型已准确理解本图"。

---

## 大模型消费策略（token 可行）

- **默认只读 MD**：语义、值、关系全在（示例：某 A0 图全文约 7.7 万字符，示例值）；按视图章节分块读，单章约 3–10KB。
- **需要精确坐标时按视图切 SVG**：以 `data-view="Vxx"` 抽取该组（单视图通常 10–40KB，示例值），连同 MD 对应章节一起喂。
- **永不整份喂 MB 级 SVG**；glyph 路径段（dimension 层数字轮廓）切片时剔除，只留 `<text>`。
- 重绘/改图任务：以 MD 参数为输入；校验/测量任务：以 SVG 切片为输入。
- 回答"图上一共有几个零件/多重"类总量问题：先读 MD 的 BOM 章，再按需用 SVG 切片核对气球位置。

---

## 交付物与命名

| 文件 | 内容 | 事实源角色 |
|---|---|---|
| `<图号> R<x>.svg`（增强版） | 骨：分层 + 视图分组 + 文本恢复 + 参数旁注 + metadata | 几何/图层/页面坐标 |
| `<图号> R<x>-可复现图纸描述.md` | 魂：六层 schema + ID + 语义注解 + crosswalk 附录 | 值/语义/工艺/BOM |
| `<图号> R<x>_crosswalk.json` | view↔svg 组↔换算（MD 附录同份，脚本同源生成） | 换算 |
| `<图号> R<x>_QA题库.json` | 验收题库及答案（≥20 题五类） | — |
| `<图号> R<x>_修正单.md` | 三方互校差异仲裁记录（随版归档） | — |
| `反向重绘验证.png` | 校验产物，随版更新；必须与源渲染同分辨率（示例：scale=2.0≈144DPI），降采样会糊、无法叠合校验 | — |

---

## 范围分级（按工期取舍）

| 能力 | 最小版 | 完整版 |
|---|---|---|
| 六层 SVG + MD 六层 schema | ✔ | ✔ |
| ID 体系 + crosswalk | ✔（bbox 级对齐，不做锚点吸附） | ✔（含锚点吸附校正） |
| data-view 视图分组 | ✔ | ✔ |
| `<text>` 文本恢复 | 仅尺寸值 + 视图标签 | + 标题栏/焊缝符号/剖切标记 |
| 弧/长圆 data-params 旁注 | — | ✔ |
| 语义注解段 | 每视图 1 句 | 每视图 1–3 句 + 关系句 |
| 三方互校 + LLM 验收 | 值集合核对 | + 叠合差集 + 题库 ≥95% |
| data-view 无 UNASSIGNED（标题栏/图框归 V00） | ✔ | ✔ |
| crosswalk 记 scale_source + self_check | self_check | + scale_source 三档分级 |
| 叠合用容差度量（recall/precision/F1） | — | ✔（recall≥0.99 门禁） |
| 独立于生成器的审计 | — | ✔（09 + spec_audit + final_audit，三者互不复用判定） |

估算（实测修正）：最小版 ≈0.5 人日/图；完整版 ≈**1.5–2 人日/图**（首图含字典冷启动更高，后续图因字典跨图复用递减）。原估「≈1 人日/图」未计入跨图字形字典、多轮盲测答卷维护、独立审计三处增量。

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| 视图聚类错分/粘连 | 与 MD 布局表互认；粘连视图人工指定 bbox |
| 文本复读误（162°/163° 类，示例） | 双源独立读 + 仲裁；冲突值入 unclear 不臆造 |
| 曲线折线化丢参数 | MD 参数为真 + SVG data-params 双轨 |
| 双载体漂移 | crosswalk/metadata 由脚本从 MD 同源生成，禁手改 |
| 渲染器兼容性（crispEdges 吞细线；无描边纯白填充矩形覆盖全图） | 交付 SVG 不带 shape-rendering=crispEdges；提取时剔除无描边纯白背景矩形；校验与消费固定同一渲染器及版本 |
| 版本变更（R00→R01） | ID 与版本号绑定；换版重跑流水线，diff 出变更单 |
| 反向重绘糊化（降采样） | 重绘固定原分辨率；与叠合校验共用同一渲染器 |
| 渲染库缺 cairo（svglib/reportlab） | 重绘脚本用 PIL 直读 get_drawings() 数据，不走 svglib→PNG 链路 |
| 视图聚类串簇（thin 层横跨全页） | 聚类排除 thin(黄)层，仅用 outline+dimension+centerline |
| BOM 缺失 | 源图标题栏可能不含可填写明细表；降级为记录"BOM 未提供"并列出已识别零件编号，不得臆造材料/重量 |
| 颜色→层硬映射对个别图失效（黄既是 thin 又是 title-block） | OCG 语义优先、颜色兜底；任一色占比 >50% 时触发复核并落 `meta.triggers` + 分层审计表 |
| 竖排归正式写错（静默降质：所有 `rotate(90)` 文本坐标错位，计数类门禁却全过） | 用 `self_check` 双界断言逐视图验；竖排归一化固定用 `(x,y)→(1−y,x)` |
| 发丝线严格 IoU 假性偏低（0.12pt 抗锯齿） | 叠合用容差度量（2px 膨胀 + recall/precision/F1）；严格 IoU 仅参考，precision 不作门禁 |
| 为对齐基线数字而调参/加机制 | 基线不吻合先做参数扫描取证，证不可弥合后按「记录并解释」登记，不改机制凑数 |
| 校验由生成器自判（「自己说自己通过」） | 官方 09 之外另立不复用其判定的审计（spec_audit + final_audit）；FAIL 先定性（口径错 / 真缺陷）再动手 |
| metadata 裸 JSON 含中文/特殊字符破坏 XML | 用 `<![CDATA[...]]>` 包裹 |

---

## 参考资源

- **SVG 规范（骨）：** [reference/svg-spec.md](reference/svg-spec.md) — 完整 XML 示例、四项增强、data-* 属性速查、渲染兼容性约束
- **MD 规范（魂）：** [reference/md-spec.md](reference/md-spec.md) — 六层 schema、逐视图章节模板、crosswalk JSON 全文、BOM 降级规则、三条硬约束
- **流水线（十一步）：** [reference/pipeline.md](reference/pipeline.md) — 每步职责、脚本执行顺序与覆写防护、门禁矩阵、范围分级
