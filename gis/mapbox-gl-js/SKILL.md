---
name: mapbox-gl-js
description: "Use when building vector web maps with mapbox-gl 3.33.0 — WebGL rendering, Style Spec layers, data-driven expressions, setTerrain raster-dem, fill-extrusion, or debugging 401 'A valid Mapbox access token is required', 'Style is not done loading', and pk./sk. token handling. Note: v2+ is proprietary under Mapbox TOS and requires a token; MapLibre GL JS is the open-source fork."
tags:
  - javascript
  - web
  - map
  - vector-tiles
  - webgl
  - 3d-terrain
  - data-driven-styling
  - style-spec
  - access-token
---

> **项目地址：** <https://github.com/mapbox/mapbox-gl-js>
>
> **官方文档：** <https://docs.mapbox.com/mapbox-gl-js/>
>
> **API 参考：** <https://docs.mapbox.com/mapbox-gl-js/api/>
>
> **最新版本：** 3.33.0（截至2026-10，npm `mapbox-gl` 与 GitHub Release 一致）
>
> **许可证：** v2+ 为 Mapbox 专有许可（v1.x 为 BSD-3-Clause；需 Mapbox 账号 access token）

## 概述

Mapbox GL JS 是基于 WebGL 的 JavaScript 地图库，用矢量瓦片在浏览器端实时渲染样式。2020 年 v2.0 起许可证由 BSD-3-Clause 变更为 Mapbox 专有许可（TOS），运行时需要 Mapbox 账号 access token 并受配额计费约束；API 兼容的开源分支 MapLibre GL JS（<https://github.com/maplibre/maplibre-gl-js>）可免 token 使用。主要特性：

- **矢量瓦片渲染**：GPU 加速，任意缩放级别平滑显示，样式由客户端 Style Spec 驱动
- **Style Spec 样式规范**：图层、数据源、字体、精灵图均以 JSON 描述，可在 Mapbox Studio 可视化编辑
- **数据驱动样式（Expressions）**：按要素属性、缩放级别、feature-state 动态计算颜色、半径、透明度
- **3D 能力**：`raster-dem` 地形源配合 `setTerrain` 实现 3D 地形，`fill-extrusion` 渲染 3D 建筑
- **图层级交互**：事件绑定到具体图层 id，支持点击、悬停查询要素并配合 Popup 展示

---

## 环境准备

### 获取 access token

1. 注册并登录 <https://account.mapbox.com>，在 Tokens 页面创建 access token
2. 浏览器端必须使用以 `pk.` 开头的 public token；`sk.` 开头的 secret token 禁止出现在前端代码
3. 生产环境建议在 token 上配置 URL restrictions（限定可用域名），避免被他人盗用配额
4. 不要将 token 硬编码提交到仓库，使用构建时注入的环境变量

### 方式一：npm

```bash
npm install mapbox-gl
```

```javascript
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN'; // 或用环境变量注入
```

v3 提供更小的 ESM 入口：`import * as mapboxgl from 'mapbox-gl/esm'`。

### 方式二：CDN

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://api.mapbox.com/mapbox-gl-js/v3.33.0/mapbox-gl.css" rel="stylesheet" />
  <script src="https://api.mapbox.com/mapbox-gl-js/v3.33.0/mapbox-gl.js"></script>
  <style>
    /* 容器必须显式设置高度，否则地图不可见 */
    #map { height: 400px; }
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';
    const map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [116.3975, 39.9087], // [经度, 纬度]
      zoom: 12
    });
  </script>
</body>
</html>
```

### 验证

页面出现可拖拽缩放的 streets 底图即成功；也可在控制台检查加载状态。

```javascript
map.on('load', () => console.log('style loaded', map.isStyleLoaded()));
```

### 开源替代：MapLibre GL JS

MapLibre GL JS 从 v1.13 分叉，API 与 Mapbox GL JS 高度兼容（`mapboxgl` 改为 `maplibregl`，`mapbox://` 样式 URL 需替换为自建/第三方瓦片），无需 token、采用 BSD-3-Clause。若项目要求开源许可或零配额成本，应优先评估 MapLibre。

---

## 核心 API

### Map 初始化

```javascript
const map = new mapboxgl.Map({
  container: 'map',                       // 容器 id 或 HTMLElement（必须无子元素）
  style: 'mapbox://styles/mapbox/streets-v12', // 样式 URL；缺省为 Mapbox Standard 样式
  center: [116.3975, 39.9087],            // [经度, 纬度]
  zoom: 12,
  pitch: 0,
  bearing: 0,
  maxZoom: 22,
  minZoom: 0
});
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `container` | HTMLElement \| string | 必填 | 地图容器，元素必须无子节点 |
| `style` | Object \| string | `mapbox://styles/mapbox/standard` | 样式 URL 或 Style Spec 对象 |
| `center` | LngLatLike | `[0, 0]` | 初始中心，顺序为 `[lng, lat]` |
| `zoom` / `minZoom` / `maxZoom` | number | `0` / `0` / `22` | 缩放级别及范围 |
| `pitch` / `bearing` | number | `0` | 俯仰角（0-85）与方位角 |
| `projection` | string \| Object | `'mercator'` | 投影，可设为 `'globe'` |

### 矢量瓦片源（addSource）

Style Spec 的数据源类型：`vector`（矢量瓦片）、`raster`、`raster-dem`（地形高程）、`geojson`、`image`、`video`。Mapbox 托管的瓦片集用 `mapbox://tilesetid` 引用。

```javascript
map.addSource('countries', {
  type: 'vector',
  url: 'mapbox://mapbox.country-boundaries-v1'
});

map.addSource('ports', {
  type: 'geojson',
  data: 'https://example.com/ports.geojson',
  cluster: true,
  clusterRadius: 50,
  clusterMaxZoom: 14
});

map.addSource('dem', {
  type: 'raster-dem',
  url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
  tileSize: 512,
  maxzoom: 14
});
```

| 源类型 | 关键字段 | 说明 |
|--------|----------|------|
| `vector` | `url`、`tiles`、`promoteId` | `promoteId` 指定用哪个属性作为要素 id（feature-state 依赖） |
| `geojson` | `data`、`cluster`、`clusterRadius`、`clusterProperties` | 适合中小数据量；聚合生成 `point_count` 等属性 |
| `raster-dem` | `url`、`tileSize`（默认 512）、`encoding`（`mapbox` 默认 / `terrarium`） | 高程编码瓦片，用于 3D 地形与 hillshade |
| `raster` | `url`、`tiles`、`tileSize` | 栅格底图（卫星影像等） |

### 添加图层与数据驱动样式

`addLayer` 必须指定 `id`、`type`、`source`；矢量瓦片源还要指定 `source-layer`（瓦片集内的图层名）。`paint` / `layout` 属性可写常量或表达式。

```javascript
map.addLayer({
  id: 'countries-fill',
  type: 'fill',
  source: 'countries',
  'source-layer': 'country_boundaries',
  paint: {
    'fill-color': '#088',
    'fill-opacity': 0.4
  }
});
```

Expressions 是 JSON 数组，第一个元素是运算符名，参数可以是字面量或嵌套表达式。

| 运算符 | 语法 | 用途 |
|--------|------|------|
| `get` | `["get", "property_name"]` | 取要素属性值 |
| `zoom` | `["zoom"]` | 当前缩放级别（只能作为顶层 `step`/`interpolate` 的输入） |
| `interpolate` | `["interpolate", ["linear"], ["zoom"], 0, v0, 10, v1]` | 连续插值（linear / exponential / cubic-bezier） |
| `step` | `["step", input, out0, stop1, out1, ...]` | 分段常量取值 |
| `match` | `["match", input, label, output, ..., fallback]` | 按值匹配（label 可为单值或数组） |
| `case` | `["case", cond, output, ..., fallback]` | 条件分支 |
| `coalesce` | `["coalesce", expr1, expr2, ...]` | 取第一个非空值 |
| `feature-state` | `["feature-state", "hover"]` | 取运行时要素状态（悬停高亮等） |
| `format` | `["format", "text", { "font-scale": 1.2 }]` | `text-field` 内混排样式文本 |

```javascript
map.addLayer({
  id: 'ports-circle',
  type: 'circle',
  source: 'ports',
  paint: {
    // 半径随缩放插值，并乘以属性值
    'circle-radius': ['interpolate', ['linear'], ['zoom'], 0, 1, 10, ['*', 4, ['get', 'scalerank']]],
    // 按类别匹配颜色
    'circle-color': ['match', ['get', 'type'], 'port', '#f28cb1', 'airport', '#51bbd6', '#888888']
  }
});
```

运行时更新样式，无需重建图层：

```javascript
map.setPaintProperty('countries-fill', 'fill-opacity', 0.7);
map.setLayoutProperty('ports-circle', 'visibility', 'none');
map.setFilter('ports-circle', ['==', ['get', 'type'], 'port']);
```

### 3D 地形与 3D 建筑

```javascript
map.on('load', () => {
  map.addSource('mapbox-dem', {
    type: 'raster-dem',
    url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
    tileSize: 512,
    maxzoom: 14
  });
  map.setTerrain({ source: 'mapbox-dem', exaggeration: 1.5 });
});

map.setTerrain(null); // 关闭地形
```

3D 建筑用 `fill-extrusion` 图层，高度来自属性表达式（需样式含 building 图层数据）：

```javascript
map.addLayer({
  id: '3d-buildings',
  source: 'composite',
  'source-layer': 'building',
  filter: ['==', ['get', 'extrude'], 'true'],
  type: 'fill-extrusion',
  minzoom: 15,
  paint: {
    'fill-extrusion-color': '#dddddd',
    'fill-extrusion-height': ['get', 'height'],
    'fill-extrusion-base': ['get', 'min_height'],
    'fill-extrusion-opacity': 0.6
  }
});
```

### 相机与视图控制

```javascript
map.flyTo({ center: [121.4737, 31.2304], zoom: 14, pitch: 60, bearing: 30 });
map.easeTo({ center: [116.3975, 39.9087], zoom: 10, duration: 1000 });
map.fitBounds([[116.0, 39.6], [116.8, 40.2]], { padding: 40 });
map.getBounds(); // 当前视口范围
```

### 交互事件

事件可绑定到整张地图或指定图层 id；图层事件回调中的 `e.features` 是当前光标下的要素集合。要素对象只在回调内有效，需长期保存时应拷贝属性。

```javascript
map.on('click', 'countries-fill', (e) => {
  const feature = e.features[0];
  new mapboxgl.Popup()
    .setLngLat(e.lngLat)
    .setHTML(`<strong>${feature.properties.name}</strong>`)
    .addTo(map);
});

map.on('mouseenter', 'countries-fill', () => {
  map.getCanvas().style.cursor = 'pointer';
});
map.on('mouseleave', 'countries-fill', () => {
  map.getCanvas().style.cursor = '';
});
```

feature-state 悬停高亮（要素必须有 id，矢量瓦片源可用 `promoteId` 指定）：

```javascript
let hoveredId = null;

map.on('mousemove', 'states-fill', (e) => {
  if (e.features.length === 0) return;
  if (hoveredId !== null) {
    map.setFeatureState({ source: 'states', id: hoveredId }, { hover: false });
  }
  hoveredId = e.features[0].id;
  map.setFeatureState({ source: 'states', id: hoveredId }, { hover: true });
});

map.on('mouseleave', 'states-fill', () => {
  if (hoveredId !== null) {
    map.setFeatureState({ source: 'states', id: hoveredId }, { hover: false });
  }
  hoveredId = null;
});
```

对应图层的 paint 中使用 `['case', ['boolean', ['feature-state', 'hover'], false], 1, 0.5]` 控制高亮。

常用事件：`load`、`click`、`dblclick`、`mousemove`、`mouseenter`、`mouseleave`、`moveend`、`zoomend`、`sourcedata`、`idle`、`error`。用 `map.on` / `map.once` / `map.off` 注册与注销。

### 控件、标记与销毁

```javascript
map.addControl(new mapboxgl.NavigationControl(), 'top-right');
map.addControl(new mapboxgl.ScaleControl());

new mapboxgl.Marker()
  .setLngLat([116.3975, 39.9087])
  .setPopup(new mapboxgl.Popup().setHTML('北京'))
  .addTo(map);

map.remove(); // 销毁地图，释放 WebGL 资源与事件
```

---

## 典型工作流

以「矢量瓦片分区着色 + 点击弹窗 + 3D 地形」为例：

1. 初始化地图并等待 `load` 事件
2. `addSource` 添加矢量瓦片源
3. `addLayer` 添加图层，`paint` 中使用 expressions 按属性着色
4. 绑定 `click` / `mouseenter` 图层事件，展示 Popup
5. `addSource` 添加 `raster-dem` 源并 `setTerrain` 开启动态地形
6. 组件卸载时 `map.remove()`

```javascript
mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';

const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v12',
  center: [116.3975, 39.9087],
  zoom: 3,
  pitch: 45
});

map.on('load', () => {
  map.addSource('countries', { type: 'vector', url: 'mapbox://mapbox.country-boundaries-v1' });

  map.addLayer({
    id: 'countries-fill',
    type: 'fill',
    source: 'countries',
    'source-layer': 'country_boundaries',
    paint: {
      'fill-color': ['case', ['==', ['get', 'worldview'], 'CN'], '#e6a23c', '#4a90d9'],
      'fill-opacity': 0.5
    }
  });

  map.on('click', 'countries-fill', (e) => {
    new mapboxgl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(e.features[0].properties.name_zh || e.features[0].properties.name)
      .addTo(map);
  });

  map.addSource('mapbox-dem', {
    type: 'raster-dem',
    url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
    tileSize: 512,
    maxzoom: 14
  });
  map.setTerrain({ source: 'mapbox-dem', exaggeration: 1.2 });
});
```

---

## 最佳实践

1. **token 安全**：前端只用 `pk.` public token，配置 URL restrictions；`sk.` secret token 仅限服务端
2. **许可与费用**：v2+ 受 Mapbox TOS 约束，免费层每月 50,000 次地图加载（map loads），超出按量计费，额度与价格以 <https://www.mapbox.com/pricing> 为准；开源或零成本场景评估 MapLibre GL JS
3. **等待样式加载**：`addSource` / `addLayer` / `setTerrain` 必须在 `load` 事件之后调用
4. **固定版本**：CDN 引用固定版本号（如 `v3.33.0`），JS 与 CSS 版本保持一致
5. **坐标顺序**：Mapbox GL JS 使用 `[经度, 纬度]`，与 GeoJSON 一致，与 Leaflet 的 `[lat, lng]` 相反
6. **大数据量**：优先矢量瓦片而非大量 GeoJSON；GeoJSON 点数据开启 `cluster` 聚合
7. **资源清理**：SPA 卸载组件时调用 `map.remove()`，注销自定义事件监听
8. **事件内取要素**：`e.features` 仅在回调内有效，需要持久化时用 `e.features[0].properties` 拷贝

---

## 常见问题

| 问题 | 原因与解决 |
|------|------------|
| 控制台报 401 / `A valid Mapbox access token is required` | token 未设置、失效或超出配额：检查 `mapboxgl.accessToken`（或构造选项 `accessToken`）是否为 `pk.` 开头且在 account 页面未被撤销；确认账号额度与 URL restrictions |
| 地图区域空白 | 容器缺少显式高度：为 `#map` 设置 `height`；或容器尺寸变化后调用 `map.resize()` |
| 报错 `Style is not done loading` | 在 `load` 事件触发前调用了 `addSource`/`addLayer`，移入 `map.on('load', ...)` 回调 |
| `mapboxgl is not defined` 或样式失效 | CDN 脚本未加载或 JS/CSS 版本不一致：先引 `mapbox-gl.js` 与 `mapbox-gl.css` 再执行代码，两者使用同一版本号 |
| 点击图层无反应 / `e.features` 为空 | 图层 id 拼写错误或事件注册早于 `addLayer`；确认 `source-layer` 与瓦片集内图层名一致；查询时可用 `queryRenderedFeatures` 指定 `layers` |
| 标记点位置偏移 | 坐标顺序错误：应为 `[经度, 纬度]`，检查是否误用了 `[纬度, 经度]` |
| `setTerrain` 无效果 | `raster-dem` 源 url 无效或未在 `load` 后调用；自定义 DEM 需确认 `encoding`（`mapbox` / `terrarium`）与数据一致 |
| feature-state 悬停不生效 | 要素缺少 id：矢量瓦片源设置 `promoteId`，GeoJSON 要素提供顶层 `id`；且该属性需支持 data-driven styling |
| 想免 token 或使用开源许可 | v2+ 为专有许可，需改用 MapLibre GL JS（`mapboxgl` 替换为 `maplibregl`，替换 `mapbox://` 样式与瓦片 URL） |

---

## 参考资源

- 官方文档：<https://docs.mapbox.com/mapbox-gl-js/>
- API 参考：<https://docs.mapbox.com/mapbox-gl-js/api/>
- 官方示例：<https://docs.mapbox.com/mapbox-gl-js/examples/>
- Style Spec 样式规范：<https://docs.mapbox.com/style-spec/>
- Expressions 表达式参考：<https://docs.mapbox.com/style-spec/reference/expressions/>
- 源码仓库与发布记录：<https://github.com/mapbox/mapbox-gl-js>
- 开源替代 MapLibre GL JS：<https://github.com/maplibre/maplibre-gl-js>
- 价格说明：<https://www.mapbox.com/pricing>

## 相关技能

- **leaflet** — 轻量 2D 瓦片地图，无需 token，适合简单场景：[../leaflet/SKILL.md](../leaflet/SKILL.md)
- **openlayers** — 功能全面的开源 2D WebGIS 库（投影、MVT、高级交互）：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **cesiumjs** — 三维地球与 3D Tiles 可视化：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)
- **geoserver** — 发布 WMS/WFS/MVT 服务作为矢量瓦片数据源：[../geoserver/SKILL.md](../geoserver/SKILL.md)

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("mapbox-gl-js")` 加载（用户也可输入 `/mapbox-gl-js`）；本技能无 reference 子目录，示例代码写入会话工作区工程，技能目录只读。
- **执行环境**：`npm install`、`npm run build` 交给 `pwsh`；Windows 下用 `npm.cmd`，长构建用后台作业。
- **先探测版本**：`npm ls mapbox-gl`（未装则 `npm view mapbox-gl version`）；本技能按 3.33.0 编写，CDN 的 JS 与 CSS 必须同为 `v3.33.0`，联网时 `curl.exe -I https://api.mapbox.com/mapbox-gl-js/v3.33.0/mapbox-gl.js` 应为 200。
- **验证产物**：`npm run build` 后 `npx serve dist`，`curl.exe -I http://localhost:5173/` 确认入口；地图是否真加载、有没有 401 只能看浏览器 Network（`api.mapbox.com`），DSH 不打开浏览器，请用户确认或提供截图后再 `read_image`。
- **token 安全**：前端只允许 `pk.` 公开 token，`sk.` 绝不能进构建产物；用 `VITE_MAPBOX_TOKEN` 等环境变量注入，提交前用 dsh 的 `grep` 搜 `sk.` 与硬编码 `pk.`，回答和日志里不要回显 token。
- **许可提醒**：v2+ 是 Mapbox 专有许可并受配额计费约束；用户要求开源或免 token 时改写为 MapLibre（`maplibregl` 替代 `mapboxgl`，`mapbox://` 样式换成自建瓦片）。
- **常见症状**：`Style is not done loading` 是 `load` 事件前调了 `addSource`/`addLayer`；空白先查容器高度和 `map.resize()`；`e.features` 只在回调内有效。
- **安全与权限**：装包、起 dev server、调用计费接口前先征得用户同意，并说明可能产生费用。
