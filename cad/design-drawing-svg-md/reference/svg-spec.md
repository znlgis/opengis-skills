# SVG 规范（骨）

> 本文件是 [../SKILL.md](../SKILL.md) 的参考拆分：SVG 载体的完整 XML 示例与生成约束。
> 定位：高精度几何档案 + 按需切片源。文中所有数字均为示例值。

---

## 1. 完整 XML 示例

基础六层 SVG（按颜色分层、`data-layer` 组）之上做四项增强，其余不动：

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2383.654 3370.11">
  <!-- 增强4：metadata 同源镜像（与 MD 附录同份，脚本生成，禁手改） -->
  <metadata id="sheet-meta">{ 与 MD 元信息同源的 JSON，含 crosswalk }</metadata>

  <!-- 增强1：层内二级视图分组 -->
  <g data-layer="outline" data-semantic="主轮廓线层(可见实体线)">
    <g data-view="V15" data-view-name="吊耳分解详图" data-scale="1:20"
       data-bbox="1890.1,1420.5,2310.7,2260.9">
      <path data-prim="outline" data-prim-id="V15-P01" d="M..."/>
      <!-- 增强2：弧参数旁注（参数坐标=视图局部 mm、与 MD 同源；d 折线仍为页面 pt，仅用于显示） -->
      <path data-prim="arc" data-prim-id="V15-P05"
            data-params='{"cx":1140,"cy":2850,"r":150,"a1":0,"a2":180}'
            d="M...(页面pt折线近似,仅用于显示)"/>
    </g>
  </g>

  <!-- 增强3：文本恢复——尺寸值/标签/标题栏写真实 <text>，glyph 路径保留 -->
  <g data-layer="dimension" data-semantic="尺寸标注层">
    <g data-view="V15">
      <path data-prim="dim-line" data-dim-id="V15-D03" d="M..."/>
      <text data-dim-id="V15-D03" data-value="930" x="1980" y="1700"
            transform="rotate(90 1980 1700)">930</text>
    </g>
  </g>
</svg>
```

（示例值：viewBox、data-bbox、坐标、参数等；实际以提取脚本输出为准。）

---

## 2. 四项增强要点

### 增强 1：视图分组（data-view）

- 层内二级分组：`<g data-layer=...>` 内嵌 `<g data-view="Vxx" ...>`。
- 携带 `data-view-name`（视图名）、`data-scale`（比例）、`data-bbox`（竖放页面 pt 包围盒）。
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
| `data-layer` | 一级 `<g>` | outline/centerline/thin/dimension/red | 颜色图层 |
| `data-semantic` | 一级 `<g>` | 中文语义名 | 图层语义（给模型读） |
| `data-view` | 二级 `<g>` | V{nn} | 视图 ID，切片键 |
| `data-view-name` | 二级 `<g>` | 视图名 | 视图语义 |
| `data-scale` | 二级 `<g>` | 1:20 等 | 视图比例 |
| `data-bbox` | 二级 `<g>` | x0,y0,x1,y1 | 竖放页面 pt 包围盒 |
| `data-prim` | `<path>` | outline/arc/dim-line/... | 图元类型 |
| `data-prim-id` | `<path>` | V{nn}-P{mm} | 图元 ID |
| `data-dim-id` | `<path>`/`<text>` | V{nn}-D{mm} | 尺寸 ID（线与文本同号） |
| `data-value` | `<text>` | 930 / R150 / t=30 | 机器值 |
| `data-params` | `<path>` | JSON 字符串 | 弧/长圆参数旁注 |

---

## 4. 渲染兼容性约束（生成时内建）

| 约束 | 规则 |
|---|---|
| 形状渲染 | 交付 SVG 不得出现 `shape-rendering="crispEdges"`（会吞 0.12pt 级细线） |
| 白底甄别 | 提取时剔除无描边（color=None）的整页纯白填充矩形（f 类型图元），再按五色归层 |
| 颜色→图层语义 | 黑=主轮廓、青=中心线、黄=细轮廓/标题栏（thin）、绿=尺寸、红=特殊；其余颜色入不清项 |
| 页面方向 | 保持原页面方向（竖放）不旋转；旋转换算只写在 crosswalk，避免二次几何误差 |
| 渲染器锁定 | 校验与消费固定同一渲染器及版本；渲染库缺 cairo（svglib/reportlab）时，重绘脚本用 PIL 直读 get_drawings() 数据，不走 svglib→PNG 链路 |

---

## 5. 口径提醒

- "drawing 元素数"与"path 数"是两个口径（示例：某图 9257 个 drawing 元素 / 9223 个 path，示例值），提取统计时勿混用。
- 单色图纸同样适用：图层语义退化为单层，其余规范不变。

---

## 6. 生成顺序（脚本执行顺序）

执行者编写的提取/增强脚本按以下顺序运行，产出最终 SVG：

1. 剔除白底：删掉无描边（color=None）的整页纯白填充矩形
2. 按颜色归层：五色 → 六个 `data-layer` 组 + `data-semantic`
3. 视图聚类分组：outline+dimension+centerline 聚类 → `data-view` 组与 bbox
4. 文本恢复：视觉识读 + 绿层核对 → `<text data-value>`，与 dim-id 绑定
5. 参数旁注：弧/长圆孔补 `data-params`（与 MD 图元 JSON 同源）
6. metadata 同源生成：从 MD 附录生成 `<metadata id="sheet-meta">`

提取参数（DPI、渲染器及版本、fitz 版本）固化进 MD 元信息层，保证换版/复跑可复现。

