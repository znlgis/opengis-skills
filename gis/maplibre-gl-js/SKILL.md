---
name: maplibre-gl-js
description: "Use when building open-source vector web maps with maplibre-gl 6.17.0 — Map/addSource/addLayer, Style Spec v25 layers, data-driven expressions, raster-dem terrain with setTerrain, setSky, setMissingStyleImageResolver, addProtocol for PMTiles, or debugging v6 ESM-only import errors, 'WebGL2 is required', blank maps after setStyle and style-spec expression warnings. MapLibre GL JS is the BSD-3-Clause fork of Mapbox GL JS and needs no access token."
license: MIT
metadata:
  category: gis
  tags: "javascript, web, map, vector-tiles, webgl, style-spec, expressions, pmtiles, terrain, open-source"
---

> **项目地址：** <https://github.com/maplibre/maplibre-gl-js>
>
> **官方文档：** <https://maplibre.org/maplibre-gl-js/docs/>
>
> **API 参考：** <https://maplibre.org/maplibre-gl-js/docs/API/>
>
> **样式规范：** <https://maplibre.org/maplibre-style-spec/>
>
> **最新版本：** 6.17.0（截至 2026-11，[npm `maplibre-gl`](https://registry.npmjs.org/maplibre-gl/latest) dist-tag `latest`；[GitHub Releases](https://github.com/maplibre/maplibre-gl-js/releases) 同步）
>
> **许可证：** BSD-3-Clause（v6 起的发行物为 ESM-only，UMD 构建已移除）

## 概述

MapLibre GL JS 是基于 WebGL2 的矢量瓦片地图渲染库，源自 Mapbox GL JS v1 的 BSD 分支，现由 MapLibre 社区独立维护。样式由 Style Spec JSON 驱动，客户端按需请求矢量瓦片、字体与精灵图，再用 GPU 逐帧绘制，因此缩放平滑、样式可运行时改动，且不需要任何商业 token。

- **矢量瓦片渲染**：MVT 瓦片 + 客户端样式，任意缩放级别清晰；同时支持栅格瓦片与 GeoJSON 源
- **Style Spec 样式规范**：sources / layers / expressions 全部 JSON 化，可版本化、可服务端下发
- **数据驱动样式**：表达式按要素属性、`zoom`、`feature-state` 动态计算颜色、宽度、透明度
- **三维能力**：`raster-dem` 地形源 + `setTerrain`，配 `setSky` 做天空与大气；globe 投影可直接切换
- **可扩展协议**：`addProtocol` 注册自定义加载器，PMTiles、COG 等单文件瓦片方案由此接入
- **开源免 token**：底图可用公共 demotiles、自建 tile server 或 PMTiles，不受 Mapbox 配额与 TOS 约束

与相邻技术的差异：Mapbox GL JS 是同一血统的闭源商业版本（v2 起专有许可、必须 token）；OpenLayers 偏全能型二维 GIS（投影、WMS/WMTS 更强）；deck.gl 负责大规模数据图层，通常叠在 MapLibre 底图之上。

---

## 环境准备

### npm 安装

v6 是 **ESM-only** 发行方式，包内只有 `dist/maplibre-gl.mjs`，不再提供 `maplibre-gl.js` 这类 UMD 文件：

```bash
npm install maplibre-gl
npm ls maplibre-gl          # 验证：应显示 maplibre-gl@6.17.0
```

```javascript
// v6：用命名空间导入或具名导入，没有 default export
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://demotiles.maplibre.org/style.json',
  center: [116.39, 39.91],
  zoom: 4
});
```

```html
<!-- 容器必须有显式高度，否则地图不可见 -->
<style>#map { height: 500px; }</style>
<div id="map"></div>
```

### CDN（无构建步骤）

由于 UMD 已移除，CDN 场景也必须走 ES module：

```html
<link href="https://cdn.jsdelivr.net/npm/maplibre-gl@6.17.0/dist/maplibre-gl.css" rel="stylesheet">
<script type="module">
  import * as maplibregl from 'https://cdn.jsdelivr.net/npm/maplibre-gl@6.17.0/dist/maplibre-gl.mjs';
  const map = new maplibregl.Map({
    container: 'map',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [0, 20],
    zoom: 1
  });
  window.__map = map;   // 便于控制台调试
</script>
```

### 验证

```bash
# 包与入口存在性（v6 只有 .mjs，查 .js 得到 404 是正常的）
npm ls maplibre-gl
curl -s -o /dev/null -w '%{http_code}\n' https://cdn.jsdelivr.net/npm/maplibre-gl@6.17.0/dist/maplibre-gl.mjs
```

页面能显示 demotiles 世界地图、拖拽缩放正常，即环境就绪。浏览器控制台出现 `WebGL2 is required` 说明运行环境不支持 WebGL2，换浏览器或开启硬件加速。

### v5 升 v6 的破坏性变更

| 变更 | 影响与改法 |
|------|-----------|
| ESM-only，UMD 构建移除 | `<script src=".../maplibre-gl.js">` 改为 `<script type="module">`；`import maplibregl from 'maplibre-gl'` 改为 `import * as maplibregl from 'maplibre-gl'` 或具名导入 |
| 只支持 WebGL2 | WebGL1 路径删除；失败信息可通过 `map.on('error')` 捕获 |
| `Map` 改为组合 `Camera` 而非继承 | 相机 API 仍由 Map 转发；内部 `map.transform` 已移除，不要再访问 |
| `styleimagemissing` 变为只通知 | 不能再在该事件里同步补图，改用 `map.setMissingStyleImageResolver(fn)`（支持 async） |
| `GeoJSONSource#setData` 去掉第二个参数与返回值 | `setData(data)` 只传数据，不要再用 `waitForCompletion` |
| Style Spec 升到 v25 | 遗留表达式写法会以 warning 级错误抛出，需按新版表达式改写 |
| 事件改为真实类，`MapDataEvent` 移除 | 源码数据事件是 `MapSourceDataEvent` 或 `MapStyleDataEvent`；`MapLibreZoomEvent` 更名 `MapBoxZoomEvent` |
| 着色器指令 `#pragma mapbox` 改为 `#pragma maplibre` | 自定义图层若依赖该指令需同步改 |
| `zoomLevelsToOverscale` 默认改为 4 | 高缩放密集标注更自然，但 `queryRenderedFeatures` 结果可能变化；要还原设为 `undefined` |
| TypeScript 目标升到 ES2022 | 需要转译 MapLibre 或升级构建链的旧工程会报语法错误 |

---

## 核心 API

### Map 与生命周期

```javascript
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://demotiles.maplibre.org/style.json',
  center: [116.39, 39.91],
  zoom: 5,
  pitch: 0,
  bearing: 0,
  minZoom: 0,
  maxZoom: 18,
  attributionControl: { compact: true },
  hash: true                 // 把视图同步到 URL #zoom/lat/lng
});

map.on('load', () => { /* 样式与初始瓦片就绪后再加图层 */ });
map.on('error', (e) => console.error(e.error));
```

| 阶段 | 判断方式 | 可做什么 |
|------|---------|---------|
| 构造完成 | `new Map()` 返回 | 绑定事件、加控件 |
| 样式就绪 | `map.isStyleLoaded()` / `load` / `style.load` | `addSource` / `addLayer` |
| 瓦片渲染完 | `map.areTilesLoaded()` / `idle` | 截图、批量查询 |
| 销毁 | `map.remove()` | 释放 WebGL 上下文与 Worker |

### 数据源 Source

| `type` | 用途 | 关键字段 |
|--------|------|---------|
| `geojson` | 要素集合，可运行时 `setData` | `data`、`cluster`、`generateId` |
| `vector` | MVT 矢量瓦片 | `tiles` / `url`、`minzoom`、`maxzoom` |
| `raster` | 栅格瓦片底图 | `tiles`、`tileSize`、`attribution` |
| `raster-dem` | 地形高程（Terrarium/Mapbox DEM） | `encoding`、`tileSize` |
| `image` | 单张地理配准图片 | `url`、`coordinates` |

```javascript
map.addSource('pois', { type: 'geojson', data: '/data/poi.geojson' });
map.addSource('dem', {
  type: 'raster-dem',
  url: 'https://demotiles.maplibre.org/terrain-tiles/tiles.json',
  tileSize: 256
});

const src = map.getSource('pois');
src.setData(newGeoJson);          // v6：只传数据，无第二参数
```

### 图层 Layer

图层按 `type` 分类，通过 `filter`、`paint`、`layout` 控制外观。绘制顺序即数组顺序，后加的在上。

```javascript
map.addLayer({
  id: 'pois-circle',
  type: 'circle',
  source: 'pois',
  filter: ['==', ['get', 'kind'], 'station'],
  paint: {
    'circle-radius': ['interpolate', ['linear'], ['zoom'], 6, 3, 14, 12],
    'circle-color': ['match', ['get', 'level'], 'high', '#d7301f', 'mid', '#fc8d59', '#fee08b'],
    'circle-stroke-width': 1,
    'circle-stroke-color': '#ffffff'
  }
});

map.addLayer({
  id: 'pois-label',
  type: 'symbol',
  source: 'pois',
  layout: {
    'text-field': ['get', 'name'],
    'text-size': 12,
    'text-offset': [0, 1.2]
  },
  paint: { 'text-halo-color': '#fff', 'text-halo-width': 1 }
});
```

常用图层类型：`background`、`fill`、`line`、`symbol`、`circle`、`heatmap`、`fill-extrusion`（3D 建筑）、`raster`、`hillshade`、`clip`。

### 表达式与数据驱动样式

表达式是 JSON 数组，第一个元素是操作符。它是 Style Spec 的核心，替换了早期的 `stops` 写法。

```javascript
// 缩放插值
['interpolate', ['linear'], ['zoom'], 4, 1, 10, 6]

// 属性分支
['case', ['>', ['get', 'pop'], 1000000], '#800026', '#feb24c']

// 算术与颜色
map.setPaintProperty('buildings', 'fill-extrusion-height',
  ['*', ['coalesce', ['get', 'height'], 10], 1.0]);

// feature-state 联动（悬停高亮）
map.setPaintProperty('pois-circle', 'circle-opacity',
  ['case', ['boolean', ['feature-state', 'hover'], false], 1, 0.5]);
```

### 控件、Marker 与 Popup

```javascript
map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');
map.addControl(new maplibregl.GeolocateControl({ trackUserLocation: true }));
map.addControl(new maplibregl.FullscreenControl());

const marker = new maplibregl.Marker({ color: '#d7301f' })
  .setLngLat([116.39, 39.91])
  .setPopup(new maplibregl.Popup().setHTML('<b>北京</b>'))
  .addTo(map);

marker.togglePopup();
```

### 三维地形与天空

```javascript
map.addSource('dem', {
  type: 'raster-dem',
  url: 'https://demotiles.maplibre.org/terrain-tiles/tiles.json',
  tileSize: 256
});
map.setTerrain({ source: 'dem', exaggeration: 1.5 });
map.setSky({
  'sky-color': '#88c6fc',
  'horizon-color': '#ffffff',
  'fog-color': '#ffffff',
  'sky-horizon-blend': 0.5
});

// 三维建筑
map.addLayer({
  id: 'buildings-3d',
  type: 'fill-extrusion',
  source: 'buildings',
  paint: {
    'fill-extrusion-height': ['get', 'height'],
    'fill-extrusion-base': ['get', 'min_height'],
    'fill-extrusion-color': '#a0a0a0',
    'fill-extrusion-opacity': 0.85
  }
});
```

### 投影切换（含 globe）

样式里写 `projection` 即可切换，无需插件：

```javascript
map.setProjection({ type: 'globe' });
map.setProjection({ type: 'mercator' });

// 实验能力：注册自定义 CRS 平面投影（6.15 起）
maplibregl.addProjection({
  name: 'EPSG:2193',
  projection: /* proj4 转换函数 */ customProjection
});
```

自定义 CRS 属于实验 API，生产环境优先用 Mercator 或 globe。

### 自定义协议与 PMTiles

`addProtocol` 让 `sources` 里的伪协议 URL 由自定义函数加载，PMTiles 就靠它把单文件瓦片包当作任意 z/x/y 请求的源：

```javascript
import { Protocol } from 'pmtiles';

const protocol = new Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);

map.addSource('basemap', {
  type: 'vector',
  url: 'pmtiles://https://example.com/tiles.pmtiles',
  attribution: 'PMTiles'
});
```

同理可接入 COG 栅格源。协议注册是全局的，同一页面多个 Map 共享；不再使用时 `maplibregl.removeProtocol('pmtiles')`。

### 交互查询与要素状态

```javascript
map.on('click', 'pois-circle', (e) => {
  const feature = e.features[0];
  new maplibregl.Popup()
    .setLngLat(e.lngLat)
    .setHTML(`<b>${feature.properties.name}</b>`)
    .addTo(map);
});

map.on('mousemove', 'pois-circle', (e) => {
  map.getCanvas().style.cursor = 'pointer';
  if (e.features.length) {
    map.setFeatureState(
      { source: 'pois', id: e.features[0].id },
      { hover: true }
    );
  }
});

// 屏幕坐标查要素
const hits = map.queryRenderedFeatures({ layers: ['pois-circle'] });
```

---

## 典型工作流

### 链路一：自建矢量瓦片 + 属性联动样式

输入：tile server 上的 `{z}/{x}/{y}.mvt` 与属性字段 `level`；输出：按等级着色的可点击地图。

1. 加载空样式骨架：`new maplibregl.Map({ style: { version: 8, sources: {}, layers: [] } })`
2. `map.addSource('base', { type: 'vector', tiles: ['https://tiles.example.com/{z}/{x}/{y}.mvt'], minzoom: 0, maxzoom: 14 })`
3. 用 `source-layer` 指定 MVT 内的图层名，加 `fill` + `line` 两个图层
4. 用 `match` 表达式按 `level` 着色，用 `filter` 拆不同业务图层
5. 绑定 `click` / `mousemove` 事件，配合 `setFeatureState` 做悬停高亮
6. 校验：缩放各级别瓦片正常、控制台无 404、`map.areTilesLoaded()` 为 true

```javascript
map.addSource('base', {
  type: 'vector',
  tiles: ['https://tiles.example.com/{z}/{x}/{y}.mvt'],
  minzoom: 0,
  maxzoom: 14
});

map.addLayer({
  id: 'parcel-fill',
  type: 'fill',
  source: 'base',
  'source-layer': 'parcel',
  paint: {
    'fill-color': ['match', ['get', 'level'], 'A', '#2b8cbe', 'B', '#a6bddb', '#ece7f2'],
    'fill-opacity': 0.75
  }
});
```

### 链路二：GeoJSON 热力 + 地形 + 点击详情

输入：`/data/events.geojson`；输出：带地形与热力的分析视图。

1. 加 `raster-dem` 源并 `setTerrain`，再做 `setSky` 补天空
2. 加载 GeoJSON 源，加 `heatmap` 图层（`heatmap-weight` 用属性字段）
3. 叠加 `circle` 图层用于精确点击，`filter` 限定可点要素
4. `click` 回调里用 `Popup` 展示属性，`closeOnClick` 默认 true
5. 校验：地形起伏可见、热力随缩放变化、点击有弹窗

```javascript
map.addSource('events', { type: 'geojson', data: '/data/events.geojson' });

map.addLayer({
  id: 'events-heat',
  type: 'heatmap',
  source: 'events',
  paint: {
    'heatmap-weight': ['get', 'count'],
    'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 5, 8, 13, 40],
    'heatmap-opacity': 0.7
  }
});

map.addLayer({
  id: 'events-point',
  type: 'circle',
  source: 'events',
  paint: { 'circle-radius': 3, 'circle-color': '#ffffff', 'circle-opacity': 0 }
});
```

### 链路三：样式热切换与图片按需补全

输入：用户切换主题；输出：不重建地图、仅替换样式，且缺失图标自动补。

1. 用 `map.setStyle(nextStyle)` 整体换样式，不要销毁重建 Map
2. 用 `transformStyle` 在构造或 `setStyle` 时注入通用改动（如统一字体、加业务图层）
3. 缺失图标不再靠 `styleimagemissing` 补，改用 `setMissingStyleImageResolver` 异步取图
4. 监听 `style.load` 后再补加自定义图层与数据源
5. 校验：切换后业务图层仍在、图标不缺、无重复图层报错

```javascript
map.setMissingStyleImageResolver(async (id) => {
  const response = await fetch(`/icons/${id}.png`);
  if (!response.ok) return;
  const image = await createImageBitmap(await response.blob());
  map.addImage(id, image, { pixelRatio: 2 });
});

map.on('style.load', () => {
  map.addSource('pois', { type: 'geojson', data: geojson });
  map.addLayer({ id: 'pois', type: 'circle', source: 'pois' });
});
```

---

## 性能优化与最佳实践

1. **GeoJSON 源走瓦片化**：超过约 10 万要素改用 `vector` 源或服务端切片，GeoJSON 源在浏览器内做 `geojson-vt` 索引会占用主线程
2. **保持数据引用稳定**：`setData` 传新对象才触发重绘，但要避免每帧调用，节流到重绘帧率
3. **用 `feature-state` 而非改 paint**：悬停/选中用 feature-state，避免整层 `setPaintProperty` 造成全量重绘
4. **控制同时可见图层数**：图层越多每帧绘制开销越大，非当前视野的图层用 `layout.visibility = 'none'`
5. **合理设 `maxzoom`**：源声明真实 `maxzoom`，让客户端复用父级瓦片过度缩放，而不是请求不存在的瓦片
6. **关闭不必要的开销**：`canvasContextAttributes` 里默认 `antialias: false`、`preserveDrawingBuffer: false`，只有截图需求才开
7. **预初始化 Worker**：多地图页面可用 `prewarm()` 提前创建共享 Worker（需在 `setWorkerUrl()` 之后调用）
8. **及时销毁**：`map.remove()` 释放上下文；SPA 路由切换务必调用，否则 WebGL 上下文会累积到浏览器上限

---

## 常见问题

| 问题 | 原因 | 处置 |
|------|------|------|
| 报 `WebGL2 is required` 或地图不渲染 | v6 移除了 WebGL1 支持，运行环境（无头浏览器、远程桌面软件渲染、旧驱动）没有 WebGL2 | 开启浏览器硬件加速；无头环境改用带 GPU 的容器或接受无法渲染；用 `map.on('error')` 捕获具体原因 |
| `import maplibregl from 'maplibre-gl'` 后 `new maplibregl.Map` 报 undefined | v6 无 default export（ESM-only 改造的一部分） | 改为 `import * as maplibregl from 'maplibre-gl'` 或 `import { Map } from 'maplibre-gl'` |
| 引入 CDN 后报 `Unexpected token 'export'` | v6 不再发布 UMD，旧的 `<script src>` 方式加载了 ESM 文件 | 改用 `<script type="module">`，并直接从 CDN 导入 `.mjs` |
| 地图空白但无报错 | 容器没有高度，或 `addLayer` 早于样式就绪 | 给容器设显式高度；在 `load` 或 `isStyleLoaded()` 之后再 `addSource`/`addLayer` |
| 升级后控制台出现表达式 warning | Style Spec v25 把遗留表达式从静默失败改为 warning 级错误 | 按新版表达式重写；确认自定义样式里没有旧 `stops` 残留写法 |
| `styleimagemissing` 里补图不生效 | v6 起该事件只通知，不再允许同步提供图片 | 改用 `map.setMissingStyleImageResolver(async (id) => { ... })` |
| `setData(data, true)` 行为异常 | v6 移除了第二参数与返回值 | 只调用 `setData(data)`；需要等渲染用 `idle` 事件 |
| 自定义图层 shader 编译失败 | v6 把 `#pragma mapbox` 改为 `#pragma maplibre` | 同步修改自定义图层的着色器指令 |
| 截图空白 | `preserveDrawingBuffer` 默认 false，WebGL 缓冲在呈现后丢弃 | 构造时设 `canvasContextAttributes: { preserveDrawingBuffer: true }`，或改用 `map.triggerRepaint()` 后立即抓取 |
| 切换路由后地图越来越多内存 | 未调用 `map.remove()`，WebGL 上下文不断累积 | 组件卸载时 `map.remove()`，并移除 `addProtocol` 注册的全局协议 |

---

## AI 使用建议

- **执行环境**：`npm install`、`npm run build` 在终端执行；Windows 下 npm 实际是 `npm.cmd`，脚本里写 `cmd /c npm run build` 更稳；装包与大构建放后台，输出重定向到文件再分段读。
- **先探测版本**：`npm ls maplibre-gl`（未安装时 `npm view maplibre-gl version`），本技能按 6.17.0 编写。遇到 `new maplibregl.Map is not a constructor` 先怀疑是否还在用 v5 的 default import 写法。
- **验证产物**：`npm run build` 后 `npx serve dist`，用 `curl -s -o /dev/null -w '%{http_code}'` 检查入口与 `maplibre-gl.css` 返回 200；WebGL 是否真出图只能由浏览器确认，AI 助手通常看不到画面，请用户看画面与控制台，环境支持读图时用截图核对。
- **无 GPU 环境**：无头/CI 无法验证 WebGL2，构建通过不等于渲染正确，不要据此报告"已渲染"。
- **坐标顺序**：所有经纬度都是 `[lng, lat]`（经度在前），与 Leaflet 相反；`LngLatBounds` 用 `[[west, south], [east, north]]`。
- **样式调试顺序**：先确认 `style` 可访问（404 会导致整图空白且只有 error 事件），再确认 `source-layer` 与 MVT 内的图层名一致，最后才怀疑表达式。
- **常见症状**：空白图先查容器高度与样式 URL；瓦片 404 查 `minzoom/maxzoom` 与 tile URL 模板；点击无反应查图层 `id` 是否与事件绑定的一致。
- **安全与权限**：装包、起 dev server、改端口前先征得用户同意；`addProtocol` 与第三方瓦片 URL 要确认来源可信，避免把内网地址写进样式。

## 相关技能

- **mapbox-gl-js** — 同源商业版本，API 高度相似，迁移时对照：[../mapbox-gl-js/SKILL.md](../mapbox-gl-js/SKILL.md)
- **maplibre-native** — 同一体系的 C++ 原生渲染引擎（Android/iOS/Node）：[../maplibre-native/SKILL.md](../maplibre-native/SKILL.md)
- **openlayers** — 全能型二维 WebGIS，WMS/WMTS 与投影能力更强：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **deck-gl** — 大规模数据图层，常叠加在 MapLibre 底图之上：[../deck-gl/SKILL.md](../deck-gl/SKILL.md)
- **leaflet** — 更轻量的二维瓦片地图方案：[../leaflet/SKILL.md](../leaflet/SKILL.md)
- **stac-cog-titiler** — 为地图提供动态影像瓦片的后端链路：[../stac-cog-titiler/SKILL.md](../stac-cog-titiler/SKILL.md)

## 参考资源

- 官方文档：<https://maplibre.org/maplibre-gl-js/docs/>
- API 参考：<https://maplibre.org/maplibre-gl-js/docs/API/>
- 样式规范：<https://maplibre.org/maplibre-style-spec/>
- 示例集：<https://maplibre.org/maplibre-gl-js/docs/examples/>
- v5 到 v6 迁移指南：<https://github.com/maplibre/maplibre-gl-js/blob/main/docs/guides/v5-to-v6-migration-guide.md>
- 发布记录：<https://github.com/maplibre/maplibre-gl-js/releases>
- 演示样式（demotiles）：<https://demotiles.maplibre.org/style.json>
- 中文教程：<https://znlgis.github.io/gis/tutorial/maplibre-gl-js/>
