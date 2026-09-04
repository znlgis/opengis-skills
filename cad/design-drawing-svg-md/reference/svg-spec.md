# SVG 规范（骨）

> 本文件是 [../SKILL.md](../SKILL.md) 的参考拆分：SVG 载体的完整 XML 示例与生成约束。
> 定位：高精度几何档案 + 按需切片源。文中数字为示例值或多图实测值。

---

## 1. 完整 XML 示例

基础六层 SVG（`data-layer` 组、OCG 语义优先 + 颜色兜底分层）之上做四项增强，其余不动：

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2383.654 3370.11">
  <!-- 增强4：metadata 同源镜像（与 MD 附录同份，脚本生成，禁手改）；JSON 用 CDATA 包裹，避免裸中文/特殊字符破坏 XML -->
  <metadata id="sheet-meta"><![CDATA[{ 与 MD §1 同源 JSON：base_name/page/counts/layer_semantic/id_system/title_block/technical_requirements/crosswalk }]]></metadata>

  <!-- 增强1：层内二级视图分组。层 <g> 属性顺序固定：data-layer → data-semantic → data-count -->
  <g data-layer="outline" data-semantic="主轮廓线层(可见实体线)" data-count="920">
    <!-- 视图 <g> 属性顺序固定：data-view → data-view-name → data-scale → data-scale-source → data-bbox → data-tx → data-ty → data-s-pt-per-mm -->
    <g data-view="V15" data-view-name="吊耳分解详图" data-scale="1:20" data-scale-source="inferred"
       data-bbox="1890.1,1420.5,2310.7,2260.9" data-tx="1420.5" data-ty="493.55" data-s-pt-per-mm="0.14173">
      <path data-prim="outline" data-prim-id="V15-P01" d="M..."/>
      <!-- 增强2：弧参数旁注（参数坐标=视图局部 mm、与 MD 同源；d 折线仍为页面 pt，仅用于显示） -->
      <path data-prim="arc" data-prim-id="V15-P05"
            data-params='{"cx":1140,"cy":2850,"r":150,"a1":0,"a2":180}'
            d="M...(页面pt折线近似,仅用于显示)"/>
    </g>
  </g>

  <!-- 增强3：文本恢复——尺寸值/标签/标题栏写真实 <text>，glyph 路径保留 -->
  <g data-layer="dimension" data-semantic="尺寸标注层" data-count="3607">
    <g data-view="V15" data-view-name="吊耳分解详图" data-scale="1:20" data-scale-source="inferred"
       data-bbox="1890.1,1420.5,2310.7,2260.9" data-tx="1420.5" data-ty="493.55" data-s-pt-per-mm="0.14173">
      <path data-prim="dim-line" data-dim-id="V15-D03" d="M..."/>
      <text data-dim-id="V15-D03" data-value="930" x="1980" y="1700"
            transform="rotate(90 1980 1700)">930</text>
    </g>
  </g>

  <!-- 六层必须含独立 title-block：黄色按 OCG PDM_Title 拆出标题栏层、其余黄归 thin。标题栏/图框统一归 data-view="V00"（prim-id 前缀 V00-），不留 UNASSIGNED -->
  <g data-layer="title-block" data-semantic="标题栏层(OCG PDM_Title)" data-count="2298">
    <g data-view="V00" data-view-name="标题栏/图框" data-scale="1:1" data-scale-source="page-geometry"
       data-bbox="..." data-tx="..." data-ty="..." data-s-pt-per-mm="2.83465">
      <path data-prim="frame" data-prim-id="V00-P01" d="M..."/>
    </g>
  </g>
</svg>
```

（示例值：viewBox、data-bbox、坐标、参数等；实际以提取脚本输出为准。）

---

## 2. 四项增强要点

### 增强 1：视图分组（data-view）

- 层内二级分组：`<g data-layer=...>` 内嵌 `<g data-view="Vxx" ...>`。
- **层 `<g>` 属性必须写全且顺序固定**：`data-layer` 后紧跟 `data-semantic`、`data-count`。
- **视图 `<g>` 属性必须写全且顺序固定**：`data-view` 后紧跟 `data-view-name`、`data-scale`、`data-scale-source`、`data-bbox`、`data-tx`、`data-ty`、`data-s-pt-per-mm`。实测全部图视图 `<g>` 三属性（name/scale/bbox）齐备数 == 视图 `<g>` 总数；校验时须捕获**完整** `<g …>` 标签再筛，用 `<g\b([^>]*?)data-layer=` 只会拿到该属性**之前**的空串而误报为 0。
- **不留 `UNASSIGNED`**：标题栏/图框/分区网格统一归 `data-view="V00"`（TITLE 区，prim-id 前缀 `V00-`），其余图元必归某零件视图。
- 分组由流水线步骤 2（空间聚类 + MD 布局表互认）产生，禁手编。

### 增强 2：弧参数旁注（data-params）

- 曲线一律"折线显示 + 参数旁注"双轨：`d` 为页面 pt 折线近似（仅显示），`data-params` 为 JSON 参数字符串。
- `data-params` 坐标 = 视图局部 mm、与 MD 图元 JSON 同源；LLM 取参数，渲染器取折线。
- 长圆孔（OBROUND）用 `{len, w, orient}` 类参数表达，防止被近似成矩形/六边形。

### 增强 3：文本恢复（text / data-value）

- 尺寸值、标签、标题栏逐字写入真实 `<text>`；`data-value` 为机器值（`930`、`R150`、`t=30`、`71°`），显示文本同值。
- 竖排阅读方向用 `transform="rotate(90 x y)"`。
- 文本恢复来源优先级：MD 已有值 > 绿层 300DPI 裁切复读 > glyph OCR（不推荐，细线 glyph 易碎）。
- 恢复后与绿层值集合做集合核对。
- glyph 路径（dimension 层数字轮廓）保留仅为与原图视觉一致；大模型消费时剔除、只留 `<text>`。

### 增强 4：metadata 同源镜像

- `<metadata id="sheet-meta">` 与 MD 附录（元信息 + crosswalk）同份，由脚本从 MD 同源生成，禁手改。
- 任一载体改动后必须重跑生成脚本，保证两处一致。

---

## 3. data-* 属性速查

| 属性 | 挂载元素 | 值 | 说明 |
|---|---|---|---|
| `data-layer` | 一级 `<g>` | outline/centerline/thin/dimension/special/title-block | 六层语义（OCG 语义优先 + 颜色兜底） |
| `data-semantic` | 一级 `<g>` | 中文语义名 | 图层语义（给模型读） |
| `data-count` | 一级 `<g>` | 整数 | 该层图元计数 |
| `data-view` | 二级 `<g>` | V{nn}（V00=TITLE 区） | 视图 ID，切片键 |
| `data-view-name` | 二级 `<g>` | 视图名 | 视图语义 |
| `data-scale` | 二级 `<g>` | 1:20 等 | 视图比例 |
| `data-scale-source` | 二级 `<g>` | read / inferred / fallback（V00=page-geometry） | 比例来源三档 |
| `data-bbox` | 二级 `<g>` | x0,y0,x1,y1 | 竖放页面 pt 包围盒 |
| `data-tx` / `data-ty` | 二级 `<g>` | pt 值 | 配准平移量 |
| `data-s-pt-per-mm` | 二级 `<g>` | pt/mm 值 | 比例换算系数 |
| `data-prim` | `<path>` | outline/arc/dim-line/frame/... | 图元类型 |
| `data-prim-id` | `<path>` | V{nn}-P{mm}（V00 前缀 V00-） | 图元 ID |
| `data-dim-id` | `<path>`/`<text>` | V{nn}-D{mm} | 尺寸 ID（线与文本同号） |
| `data-value` | `<text>` | 930 / R150 / t=30 | 机器值 |
| `data-params` | `<path>` | JSON 字符串 | 弧/长圆参数旁注 |

---

## 4. 渲染兼容性约束（生成时内建）

| 约束 | 规则 |
|---|---|
| 形状渲染 | 交付 SVG 不得出现 `shape-rendering="crispEdges"`（会吞 0.12pt 级细线） |
| 白底甄别 | 提取时剔除无描边（color=None）的整页纯白填充矩形（f 类型图元），再按 OCG 语义优先 + 颜色兜底归层 |
| 分层口径（OCG 语义优先 + 颜色兜底） | 先按 OCG 名归层，颜色只在 OCG 不可用时兜底；六层 = outline/centerline/thin/dimension/special + 独立 title-block（黄色按 OCG `PDM_Title` 拆出标题栏、其余黄归 thin，只靠颜色无法拆）；纠偏只在主色占比 >50% 时触发并逐图落 `meta.triggers` |
| 页面方向 | 保持原页面方向（竖放）不旋转；旋转换算只写在 crosswalk，避免二次几何误差 |
| 渲染器锁定 | 校验与消费固定同一渲染器及版本；渲染库缺 cairo（svglib/reportlab）时，重绘脚本用 PIL 直读 get_drawings() 数据，不走 svglib→PNG 链路 |

---

## 5. 口径提醒

- "drawing 元素数"与"path 数"是两个口径，提取统计时勿混用；计数链须逐一对账 `drawings→bg→kept→SVG path→MD prim_ids`（实测各差 1，即整页纯白背景矩形）。
- **六层必须含独立 `title-block`**：黄色按 OCG `PDM_Title` 拆出标题栏层、其余黄归 `thin`；只有五层（title-block 并入 thin）不合规。
- **两个不可混用的绑定计数口径**：`green_layer.n_bound` 是 MD 绑定尺寸的**去重数值**个数（同值可重复出现），**不等于** `<text>` 元素数，只成立 `n_bound ≤ 元素数`（实测多图元素数合计 46、n_bound 合计 41）；元素数的同源判据是 `carrier_consistency.svg_n`（(dim-id,data-value) 去重对，dim-id 唯一 → 等于元素数）。拿前者去比元素数会得到**假 FAIL**。
- **校验脚本的计数口径**：`<metadata>` 的 CDATA 里含**字面量示例标签串**（如 `<path data-prim="glyph">`、`<text data-dim-id data-value>`），裸 `count("<path ")` 或不要求闭合的正则各会**多算 1**。数真元素必须要求自闭合 `/>` 与配对 `</text>`（实测两项假 FAIL 均源于此）。
- 单色图纸同样适用：图层语义退化为单层，其余规范不变。

---

## 6. 生成顺序（脚本执行顺序）

完整脚本执行顺序（含依赖与覆写防护）见 [pipeline.md](pipeline.md)；以下为产出最终 SVG 的六步：

1. 剔除白底：删掉无描边（color=None）的整页纯白填充矩形
2. 分层：OCG 语义优先 + 颜色兜底 → 六个 `data-layer` 组 + `data-semantic` + `data-count`（含独立 title-block）
3. 视图聚类分组：outline+dimension+centerline 聚类 → `data-view` 组与 bbox（标题栏/图框归 V00）
4. 文本恢复：视觉识读 + 绿层核对 → `<text data-value>`，与 dim-id 绑定
5. 参数旁注：弧/长圆孔补 `data-params`（与 MD 图元 JSON 同源）
6. metadata 同源生成：从 MD 附录生成 `<metadata id="sheet-meta">`（JSON 用 CDATA 包裹）

提取参数（DPI、渲染器及版本、fitz 版本）固化进 MD 元信息层，保证换版/复跑可复现。

