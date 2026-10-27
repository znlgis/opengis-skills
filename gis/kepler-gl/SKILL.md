---
name: kepler-gl
description: "Use when building React/Redux web apps or Jupyter notebooks for large-scale geospatial visual exploration with Kepler.gl 3.3.0-alpha.16 — @kepler.gl/components KeplerGl, @kepler.gl/actions addDataToMap, @kepler.gl/processors processGeojson/processCsvData, and the Python keplergl widget. Also for fixing blank maps from a missing reducer or wrong getState (react-redux 'Could not find ... in the context of Connect(...)'), Mapbox token basemap errors, and oversized addDataToMap payloads."
tags:
  - javascript
  - react
  - redux
  - webgl
  - geospatial
  - data-visualization
  - map-layers
  - jupyter
  - python
  - maplibre
---

> **项目地址：** <https://github.com/keplergl/kepler.gl>
>
> **官方文档：** <https://docs.kepler.gl/>
>
> **npm：** `kepler.gl`（npm `latest` 标签 3.3.0-alpha.16；GitHub Release v3.3.0-alpha.18 尚未回填 `latest`，截至 2026-10）
>
> **PyPI：** `keplergl` 0.4.0（Jupyter 小组件，版本节奏落后于前端，截至 2026-10）
>
> **许可证：** MIT

## 概述

Kepler.gl 是 Uber 开源（现由社区维护）的地理数据可视化应用，同时也是可嵌入 React 应用的组件库。它把数据抽象成「字段 + 行」的表格模型，通过图层、过滤器、交互配置渲染基于 MapLibre GL 与 deck.gl 的地图，百万级点位可直接在浏览器中做过场动画与空间聚合。核心是一个 Redux 应用：组件、reducer、action、处理器相互解耦，业务方只需把数据整理成 Kepler.gl 的数据集结构即可。

- **数据无关**：CSV、GeoJSON、Pandas DataFrame、GeoPandas GeoDataFrame、Arrow 表统一转为 fields/rows
- **图层体系**：点、弧线、线、多边形、Hexbin、网格、热力、3D 建筑、H3、S2、瓦片（含 MVT）
- **交互能力**：过滤器（时间、范围、选择）、tooltip、图层可见性、时间轴动画、分屏对比
- **配置可序列化**：整张地图的 `mapState` / `visState` / `mapStyle` 可导出 JSON，再通过 `addDataToMap` 还原
- **双形态**：React 组件库（npm）与 Jupyter 小组件（PyPI），共享同一套数据与配置格式

---

## 环境准备

### 前端（npm）

Kepler.gl 3.x 的 peer 依赖由主包 `kepler.gl` 声明：`react` / `react-dom` >= 18.2，`styled-components` ^6.1.0。默认底图使用 MapLibre 与 CARTO 样式，不需要 Mapbox token。

```bash
# 方式一：整包（含 UMD、全部子包，适合 demo 与不开包优化的项目）
npm install kepler.gl

# 方式二：按需子包（生产项目推荐，体积更小）
npm install @kepler.gl/components @kepler.gl/actions @kepler.gl/reducers \
            @kepler.gl/processors @kepler.gl/schemas @kepler.gl/styles

# 若使用 Mapbox 官方样式（非 CARTO/MapLibre 样式）
npm install mapbox-gl
```

子包版本必须与主包一致，Kepler.gl 各包之间存在内部耦合，混版会出现难以定位的运行时错误：

```bash
npm ls kepler.gl @kepler.gl/components @kepler.gl/actions
python -c "import keplergl; print(keplergl.__version__)"
```

### 免打包（UMD）

```html
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@^4/dist/maplibre-gl.css" />
<script src="https://unpkg.com/kepler.gl/umd/keplergl.min.js"></script>
```

UMD 构建的库名为 `KeplerGl`，AMD 加载时同样以 `KeplerGl` 注册；页面可直接通过全局变量获取组件与 action，适合无构建环境的演示页。

### Python（Jupyter）

```bash
pip install keplergl==0.4.0

# 或使用 conda
conda install -c conda-forge keplergl
```

`keplergl` 0.4.0 要求 Python >= 3.9、JupyterLab >= 4.0 或 Notebook >= 7.0，依赖 `anywidget`、`geopandas`、`pyarrow`、`geoarrow-pandas`。验证：

```python
import keplergl
from keplergl import KeplerGl

print(keplergl.__version__)   # 0.4.0
m = KeplerGl(height=300)      # 无数据也能创建空地图
print(type(m).__name__)       # KeplerGl
```

---

## 核心 API

### 数据模型：dataset 与 fields/rows

所有数据最终都归一化为下面两种形态之一，`addDataToMap` 只认这个结构：

| 形态 | 结构 | 说明 |
|------|------|------|
| 表格 | `{fields: [{name, type, format}], rows: [[...]]}` | CSV / DataFrame / Arrow，行列索引对齐 |
| GeoJSON | `{type, features}` | 单要素或 FeatureCollection；属性进 fields |

`type` 取值包括 `string`、`integer`、`real`、`boolean`、`timestamp`、`date`、`geojson`；经纬度字段需为数值型且列名为 `latitude` / `longitude`（或手动指定图层当前列），`timestamp` 需配 `format`，否则时间轴与时间过滤器不生效。

```javascript
import {processGeojson, processCsvData} from '@kepler.gl/processors';

const {fields, rows} = processCsvData(csvText);
const geo = processGeojson(geojsonObject);   // 返回同样含 fields / rows 的对象
```

### Redux 接入

Kepler.gl 不是自治组件，它依赖挂载在 store 的 `keplerGl` 键下的 reducer，以及处理异步任务的 middleware。

```javascript
import {createStore, combineReducers, applyMiddleware, compose} from 'redux';
import keplerGlReducer, {enhanceReduxMiddleware} from '@kepler.gl/reducers';

const reducers = combineReducers({
  keplerGl: keplerGlReducer,
  // ...其余 reducer
});

const middlewares = enhanceReduxMiddleware([
  // ...其余 middleware
]);

export const store = createStore(reducers, {}, compose(applyMiddleware(...middlewares)));
```

若把 reducer 挂在别的键（例如 `state.maps`），挂载组件时必须同时传入 `getState={state => state.maps}`，否则组件取不到实例状态而渲染空白。

### KeplerGl 组件

```javascript
import KeplerGl from '@kepler.gl/components';

export default function MapPanel() {
  return (
    <KeplerGl
      id="demo"
      mapboxApiAccessToken=""   // 仅 Mapbox 样式需要；CARTO/MapLibre 样式留空
      width={window.innerWidth}
      height={window.innerHeight}
      appName="Traffic Explorer"
      sidePanelWidth={420}
      getState={state => state.keplerGl}
      onViewStateChange={({longitude, latitude, zoom}) => console.log(longitude, latitude, zoom)}
    />
  );
}
```

| Prop | 默认值 | 说明 |
|------|--------|------|
| `id` | `map` | 实例标识，对应 `state.keplerGl[id]`；多地图实例必须唯一 |
| `getState` | `state => state.keplerGl` | 从 store 取 Kepler.gl 子树的函数 |
| `mapboxApiAccessToken` | 无（类型上必填） | Mapbox 样式所需 token；只用 CARTO/MapLibre 样式时传空串 |
| `width` / `height` | `800` / `800` | 画布尺寸，常配合容器尺寸动态计算 |
| `appName` / `version` | `Kepler.Gl` / `v1.0` | 侧栏标题文字 |
| `sidePanelWidth` | `300` | 侧栏像素宽度 |
| `theme` | `{}` | 主题对象（覆盖默认主题变量），不是字符串；字符串 `'dark'`/`'light'` 只用于 Python 小组件 |
| `mapStyles` | 内置列表 | 自定义底图样式数组，配合 `mapStylesReplaceDefault` 替换默认列表 |
| `readOnly` | `false` | 隐藏侧栏，只读展示 |
| `onViewStateChange` | 无 | 视口变化回调，用于外部联动 |
| `getMapboxRef` | 无 | 拿到内部地图实例引用（分屏时按 index 区分） |

### addDataToMap

```javascript
import {addDataToMap, removeDataset} from '@kepler.gl/actions';

dispatch(addDataToMap({
  datasets: {
    info: {id: 'roads', label: '道路'},
    data: {fields, rows}
  },
  options: {
    centerMap: true,
    padding: {left: 300, top: 24, right: 24, bottom: 24},
    readOnly: false,
    keepExistingConfig: false
  },
  config: savedConfig,          // 可选：之前导出的整图配置
  info: {title: '路网概览', description: '2026-10 快照'}
}));
```

- `datasets` 可传单个 dataset 或数组；配置里的 `dataId` 必须与 `datasets.info.id` 对应
- `options.centerMap` 会覆盖 `config.mapState` 中的视口，需要保留原视口时设为 `false`
- `options.keepExistingConfig` 为 `false` 时清空旧图层与过滤器，做「换图」用；追加数据集改用数组形式并设为 `true`
- 增量更新行数据用 `addToDataset` / `removeFromDataset`，不必重建整图；Arrow/DuckDB 表暂不支持这两个 action

### 配置导出与还原

```javascript
import KeplerGlSchema from '@kepler.gl/schemas';

const saved = KeplerGlSchema.getConfigToSave(store.getState().keplerGl.demo);
const meta = KeplerGlSchema.getMapInfo(store.getState().keplerGl.demo);
localStorage.setItem('kepler-config', JSON.stringify(saved));
```

还原时把 `saved` 作为 `config` 传回 `addDataToMap`，并重新提供 `datasets`；配置中只保存图层与样式，不保存数据本身。

### Python 小组件

```python
from keplergl import KeplerGl
import geopandas as gpd

gdf = gpd.read_file("data/roads.gpkg")

m = KeplerGl(height=500, theme="dark", app_name="路网概览")
m.add_data(data=gdf, name="roads")
m

# 导出为独立 HTML（从 unpkg 加载 kepler.gl，无需本地构建）
m.save_to_html(file_name="roads_map.html", read_only=True, center_map=True)
```

`KeplerGl.__init__` 关键参数：`data`（名称到数据的字典）、`config`（整图配置）、`height`、`mapbox_token`、`use_arrow`（DataFrame 用 Arrow IPC 序列化，大数据更快）、`theme`、`app_name`。`add_data(data, name="data", use_arrow=None)` 追加数据集，`save_to_html(...)` 支持 `read_only`、`center_map`、`json_encoder` 等参数。

---

## 典型工作流

以「GeoPandas 预处理路网 → 发布为可分享的独立 HTML」为例：

1. 用 GeoPandas 读取并裁剪数据，保持 WGS84（EPSG:4326），Kepler.gl 只认经纬度
2. 在 Notebook 中创建 `KeplerGl` 实例并 `add_data`，检查字段类型是否被正确识别
3. 在界面里调好图层颜色、半径、tooltip 字段
4. 通过 `m.config` 取出配置，与数据一起 `save_to_html`，得到单文件地图

```python
import geopandas as gpd
from keplergl import KeplerGl

roads = gpd.read_file("data/roads.gpkg").to_crs(4326)
roads = roads[roads["class"].isin(["motorway", "primary", "secondary"])]
roads["length_km"] = roads.length * 111.32   # 粗略换算，正式分析请用投影坐标系

m = KeplerGl(height=520, theme="dark", app_name="路网概览")
m.add_data(data=roads[["class", "length_km", "geometry"]], name="roads")

# 在 Notebook 中交互配置完成后，导出配置
config = m.config
m.save_to_html(file_name="roads_map.html", config=config, read_only=True)
print("written:", "roads_map.html")
```

输出是一个独立 HTML：内嵌数据与配置，从 unpkg 拉取 kepler.gl 运行时，可直接发给同事查看。

React 侧的等价流程是：`processGeojson` / `processCsvData` 解析 → `dispatch(addDataToMap(...))` → 用户交互 → `KeplerGlSchema.getConfigToSave` 落库 → 下次用同一 `config` 还原。

---

## 最佳实践

1. **坐标系只保留 WGS84**：Kepler.gl 不做投影，其他坐标系先用 GeoPandas `to_crs(4326)` 或 GDAL 转换
2. **规范字段类型**：数字列不要混入空字符串，时间列统一转 `datetime` 并设置 `format`，否则过滤器表现为「无数据」
3. **大数据走 Arrow**：Python 侧 `use_arrow=True`，前端可先转 Arrow 表再 `processArrowTable`，比 JSON 行数组更省内存
4. **控制单次 payload**：一次 `addDataToMap` 传入几十万行以上时应先做聚合或后端分页，浏览器主线程会卡在数据展开
5. **配置与数据分离存储**：`getConfigToSave` 只存样式，数据另存；版本升级后旧配置可能引用不存在的字段，需要做字段名兜底
6. **多实例用 id 隔离**：一个页面放两张地图时给不同 `id`，并确认 `getState` 指向同一个根
7. **底图选型**：CARTO/MapLibre 样式免 token，适合内网与演示；Mapbox 官方样式需 token 且有计费风险

---

## 常见问题

| 问题 | 原因与解决 |
|------|------------|
| 组件渲染为空白，控制台提示 `Could not find ... in the context of Connect(...)` | reducer 未挂载或挂载键名不对：按 `combineReducers({keplerGl: keplerGlReducer})` 挂载，或给 `KeplerGl` 传正确的 `getState` |
| 数据已传入但地图没有图层 | `datasets.info.id` 与 `config` 里的 `dataId` 不匹配，或字段类型不是数值：先不传 `config`（`addDataToMap` 的 config 置空）确认能否自动建层 |
| 时间过滤器/时间轴不可用 | 时间字段未标记为 `timestamp` 或缺少 `format`：在 `fields` 中补 `{name, type: 'timestamp', format: 'YYYY-MM-DD HH:mm:ss'}` |
| 点位错位或全部堆在 (0,0) | 坐标不是经纬度，或列名不是 `latitude`/`longitude`：先转 EPSG:4326，并在图层里手动指定经纬度字段 |
| 底图不显示，提示需要 Mapbox token | 当前样式是 `mapbox://` 样式：换成默认的 CARTO/MapLibre 样式，或给 `mapboxApiAccessToken` 配置有效 token（有计费） |
| 导入时报 `Cannot find module '@kepler.gl/components'` | 只装了 `kepler.gl` 整包却按子包路径 import：整包用 `kepler.gl` 入口，或按需安装子包并保证版本一致 |
| `addDataToMap` 后页面卡死数秒 | 单次数据量过大：先聚合或抽样，或改走 Arrow 表；同时关闭不需要的图层（如六边形聚合） |
| Jupyter 中地图不显示 | 内核与前端版本不匹配：确认 JupyterLab >= 4 / Notebook >= 7，重启内核后重装 `keplergl==0.4.0` |
| `save_to_html` 报 JSON 序列化错误 | 数据中有 datetime 等非原生类型：保留默认 `json_encoder=str`，或自行传入可序列化编码函数 |

---

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("kepler-gl")` 加载（也可输入 `/kepler-gl`）；示例工程写到会话工作区，技能目录只读。
- **执行环境**：`npm install` / `pnpm install`、`pip install keplergl` 交给 `pwsh` 或 `ops_bash`，长输出重定向到文件再分段读。
- **先探测版本**：`npm ls kepler.gl @kepler.gl/components @kepler.gl/actions`，子包必须与主包同为 3.3.0-alpha.16；Python 侧 `python -c "import keplergl; print(keplergl.__version__)"` 应为 0.4.0。
- **验证产物**：前端用 `npm run build` 确认编译，再用 `npx serve dist` 起本地静态服务；是否真出图只能由浏览器确认，DSH 不打开浏览器，请用户看画面与控制台，有截图再用 `read_image`。
- **无 GPU 环境**：无头环境无法验证 WebGL 渲染，构建通过不等于地图可用，此时不要报告「已渲染」。
- **常见症状**：空白组件先查 reducer 与 `getState`；无图层查 `dataId` 与字段类型；token 报错查底图样式。
- **安全与权限**：装包、起服务、把数据写入 HTML 前先征得用户同意；配置里不要硬编码 Mapbox token。

## 相关技能

- **deck-gl** — Kepler.gl 的渲染底座，自定义图层与拾取需直接操作 deck.gl：[../deck-gl/SKILL.md](../deck-gl/SKILL.md)
- **mapbox-gl-js** — 使用 Mapbox 官方样式与 token 时的对应技能：[../mapbox-gl-js/SKILL.md](../mapbox-gl-js/SKILL.md)
- **openlayers** — 传统 2D WebGIS 方案，适合与 Kepler.gl 做能力对比：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **geopandas** — Python 侧数据预处理与投影转换：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **gdal** — 大体量数据的格式转换与切片，为前端准备输入：[../gdal/SKILL.md](../gdal/SKILL.md)

## 参考资源

- 官方文档与示例：<https://docs.kepler.gl/>
- 4.x 之前的旧版文档（API 名称有变化，注意甄别）：<https://github.com/keplergl/kepler.gl/tree/master/docs>
- Jupyter 小组件指南：<https://docs.kepler.gl/docs/keplergl-jupyter>
- 示例工程目录：<https://github.com/keplergl/kepler.gl/tree/master/examples>
- 数据格式与处理函数：<https://docs.kepler.gl/docs/api-reference/processors/processors>
