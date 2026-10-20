---
name: deck-gl
description: "Use when visualizing large geospatial datasets in the browser with deck.gl 9.4.0 — ScatterplotLayer/GeoJsonLayer, HexagonLayer/ScreenGridLayer aggregation, MVTLayer/TileLayer, @deck.gl/mapbox MapboxOverlay over MapLibre, or debugging blank canvases, stale data props and mismatched @deck.gl/* subpackage versions."
tags:
  - javascript
  - web
  - webgl
  - webgpu
  - data-visualization
  - geospatial
  - map-layers
  - aggregation
  - maplibre
  - mapbox
---

> **项目地址：** <https://github.com/visgl/deck.gl>
>
> **官方文档：** <https://deck.gl/>
>
> **最新版本：** 9.4.0（截至 2026-10，npm `deck.gl` 与 GitHub Release 一致）
>
> **许可证：** MIT（`gh api repos/visgl/deck.gl --jq '.license.spdx_id'` 核实）

## 概述

deck.gl 是 vis.gl 项目（OpenJS Foundation 托管）推出的 Web 数据可视化框架，基于 WebGL2/WebGPU（底层 luma.gl）把数据映射为 GPU 图层，再通过视图（view）渲染。它面向大规模数据：百万级点位、海量 GeoJSON 面、矢量瓦片均可交互式渲染，是 WebGIS 前端在数据量超过常规 DOM/SVG 方案时的首选。核心架构是「图层（Layer）+ 视图（View）」组合式设计，并与 MapLibre / Mapbox / Google Maps / ArcGIS 底图集成。

- **GPU 渲染**：数据以属性缓冲上传显存，顶点/片元着色器完成绘制，CPU 只负责一次性数据展开
- **图层目录**：基础图层（Scatterplot、GeoJson、Path、Polygon、Icon、Text）、地理图层（Tile、MVT、Terrain、H3）、聚合图层（Hexagon、Grid、ScreenGrid、Heatmap、Contour）
- **多视图**：`MapView`、`OrthographicView`、`FirstPersonView`、`GlobeView`，一个 `Deck` 实例可同时承载多个视图
- **底图集成**：`@deck.gl/mapbox` 提供 `MapboxOverlay`，支持叠加（overlaid）与交错（interleaved）两种模式
- **交互内置**：GPU 拾取（picking）、悬停/点击回调、tooltip、高亮与过滤

---

## 环境准备

### 安装

按需选择整包或子包：整包 `deck.gl` 含全部子模块且可 tree-shaking；子包体积更小，但**各子包版本需手动保持一致**。

```bash
npm install deck.gl                 # 整包（含全部功能）
npm install @deck.gl/core @deck.gl/layers   # 最小组合：核心 + 基础图层
npm install @deck.gl/core @deck.gl/layers @deck.gl/aggregation-layers @deck.gl/geo-layers @deck.gl/react
npm install @deck.gl/mapbox maplibre-gl     # 与 MapLibre / Mapbox 底图集成
```

| 子包 | 作用 |
|------|------|
| `@deck.gl/core` / `@deck.gl/layers` | `Deck`、视图、控制器、图层基类与基础图层 |
| `@deck.gl/aggregation-layers` / `@deck.gl/geo-layers` | 聚合图层；地理图层（Tile、MVT、Terrain、H3、S2） |
| `@deck.gl/mesh-layers` | 3D 网格与场景图（SimpleMesh、Scene） |
| `@deck.gl/mapbox` / `@deck.gl/maplibre` | Mapbox / MapLibre GL JS 集成入口 |
| `@deck.gl/react` / `@deck.gl/json` | React 封装组件 `DeckGL`；JSON 声明式图层配置 |

### CDN 快速试用

```html
<script src="https://unpkg.com/deck.gl@9.4.0/dist.min.js"></script>
```

### 验证

独立渲染一个 `ScatterplotLayer`，页面出现可拖拽缩放的散点即环境正常。`Deck` 创建的 canvas 是透明覆盖层，独立使用时通常需自行放置底图或设置页面背景。

```javascript
import {Deck} from '@deck.gl/core';
import {ScatterplotLayer} from '@deck.gl/layers';

new Deck({
  initialViewState: {longitude: -122.45, latitude: 37.8, zoom: 11},
  controller: true,
  layers: [
    new ScatterplotLayer({
      data: [{position: [-122.45, 37.8], radius: 100, color: [255, 0, 0]}],
      getPosition: d => d.position,
      getRadius: d => d.radius,
      getFillColor: d => d.color,
      pickable: true
    })
  ],
  getTooltip: ({object}) => object && '命中散点'
});
```

---

## 核心 API

### Deck 初始化（独立模式）

```javascript
import {Deck} from '@deck.gl/core';

const deck = new Deck({
  initialViewState: {longitude: -122.4, latitude: 37.74, zoom: 11},
  controller: true,          // 设为 true 启用拖拽/缩放/旋转
  layers: [],
  getTooltip: ({object}) => object,
  useDevicePixels: true      // 关闭可显著降低高分屏下的像素开销
});

deck.setProps({layers: []}); // 后续增量更新，勿重建 Deck 实例
```

| 选项 | 说明 |
|------|------|
| `canvas` | 目标 canvas（HTMLCanvasElement 或 id）；未提供时自动创建 |
| `initialViewState` / `viewState` | 非受控 / 受控视口；受控模式下由外部框架驱动相机 |
| `controller` | 交互控制器，`true` 启用默认平移缩放 |
| `views` | 视图定义，缺省为单个 `MapView` |
| `layers` | 图层数组，顺序即绘制顺序（后者在上） |
| `getTooltip` | 返回字符串/对象生成 tooltip，返回 `null` 不显示 |
| `useDevicePixels` / `pickingRadius` | 是否按设备像素比渲染；拾取容差（像素） |

### 图层通用属性

| 属性 | 说明 |
|------|------|
| `id` | 图层唯一标识，用于匹配前后两次渲染、定位 picking 结果 |
| `data` | 数据源：数组、URL、Promise、异步可迭代对象或二进制列 |
| `pickable` | 是否参与拾取，默认 `false`；仅在需要 tooltip/点击时开启 |
| `visible` / `opacity` | 显隐开关（优于增删图层）与整体透明度 0-1 |
| `updateTriggers` | 指定访问器失效条件，只重建受影响属性而非全部缓冲 |
| `get*` 访问器 | 函数或常量；常量在更新时开销极低 |

### ScatterplotLayer（散点）

```javascript
import {ScatterplotLayer} from '@deck.gl/layers';

new ScatterplotLayer({
  id: 'stations',
  data: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/bart-stations.json',
  getPosition: d => d.coordinates,     // [经度, 纬度]
  getRadius: d => Math.sqrt(d.exits),  // 半径，默认单位米
  getFillColor: [255, 140, 0],
  stroked: true,
  getLineColor: [0, 0, 0],
  getLineWidth: 10,
  radiusScale: 6,
  radiusMinPixels: 1,   // 缩小后不消失
  radiusMaxPixels: 20,  // 放大后不过分膨胀
  pickable: true
});
```

`radiusUnits` 默认 `'meters'`，需固定像素半径时设为 `'pixels'`；`getFillColor` / `getLineColor` 优先于通用的 `getColor`。

### GeoJsonLayer（GeoJSON 复合图层）

一个 `GeoJsonLayer` 会按几何类型自动拆成面、线、点、文字等子图层，渲染顺序在内部已处理。

```javascript
import {GeoJsonLayer} from '@deck.gl/layers';

new GeoJsonLayer({
  id: 'geojson',
  data: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/bart.geo.json',
  filled: true,             // 默认 true
  stroked: true,            // 默认 true
  extruded: false,          // 按 getElevation 沿 z 轴拉伸
  pointType: 'circle+text', // circle / icon / text，可用 + 组合
  pickable: true,
  getFillColor: [160, 160, 180, 200],
  getLineColor: f => f.properties.color
    ? f.properties.color.match(/[0-9a-f]{2}/g).map(x => parseInt(x, 16))
    : [0, 0, 0],
  getLineWidth: 20,
  getPointRadius: 4,
  getText: f => f.properties.name,
  getTextSize: 12
});
```

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `getFillColor` / `getLineColor` | `[0, 0, 0, 255]` | 面与圆的填充色 / 轮廓色，RGBA 0-255 |
| `getPointRadius` | `1` | 点半径，透传给内部 ScatterplotLayer 的 `getRadius` |
| `getElevation` | `1000` | 仅 `extruded: true` 时生效 |
| `pointType` | `'circle'` | 点渲染方式 |

### TileLayer 与 MVTLayer（瓦片）

`TileLayer` 按当前视口动态加载切片，只保留可见瓦片；`MVTLayer` 继承自 `TileLayer`，专门加载 Mapbox Vector Tiles。

```javascript
import {TileLayer} from '@deck.gl/geo-layers';
import {BitmapLayer} from '@deck.gl/layers';

new TileLayer({
  id: 'osm-tiles',
  data: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  minZoom: 0,
  maxZoom: 19,
  tileSize: 512,
  renderSubLayers: props => {
    const {boundingBox} = props.tile;
    return new BitmapLayer(props, {
      data: null,
      image: props.data,
      bounds: [boundingBox[0][0], boundingBox[0][1], boundingBox[1][0], boundingBox[1][1]]
    });
  },
  pickable: true
});
```

`renderSubLayers` 缺省返回 `GeoJsonLayer`；`getTileData` 自定义加载逻辑，其 `tile` 参数含 `index`、`id`、`url`、`bbox` 与 `signal`（AbortSignal，应透传给 `fetch`，并在 `aborted` 时返回空值以免污染缓存）。`refinementStrategy` 可取 `'best-available'`（默认）、`'no-overlap'`、`'never'`。

```javascript
import {MVTLayer} from '@deck.gl/geo-layers';

new MVTLayer({
  id: 'carto-streets',
  data: ['https://tiles-a.basemaps.cartocdn.com/vectortiles/carto.streets/v1/{z}/{x}/{y}.mvt'],
  minZoom: 0,
  maxZoom: 14,
  binary: true,            // 默认 true，二进制解析快 2-3 倍
  getFillColor: f => [240, 240, 240],
  getLineColor: [192, 192, 192],
  getPointRadius: 2,
  pointRadiusUnits: 'pixels',
  stroked: false,
  pickable: true
});
```

`data` 也接受 TileJSON URL 或对象；`getRenderedFeatures()` 可取出当前可见要素的 GeoJSON，但开销较大，应按需防抖调用。

### 聚合图层

聚合图层在 GPU 上把大量点归并为可读的视觉单元；`gpuAggregation`（默认 `true`）在设备不支持时自动回退到 CPU。

```javascript
import {HexagonLayer} from '@deck.gl/aggregation-layers';

new HexagonLayer({
  id: 'hexagon',
  data: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/sf-bike-parking.json',
  getPosition: d => d.COORDINATES,
  getColorWeight: d => d.SPACES,
  getElevationWeight: d => d.SPACES,
  radius: 200,            // 六边形边长（米）
  extruded: true,         // 渲染为 3D 柱体
  elevationScale: 4,
  coverage: 1,            // 半径系数 0-1，控制间隙
  elevationRange: [0, 1000],
  colorRange: [[255, 255, 178], [254, 204, 92], [253, 141, 60], [240, 59, 32], [189, 0, 38], [128, 0, 38]],
  pickable: true          // PickingInfo.object 含 count / elevationValue / colorValue
});
```

```javascript
import {ScreenGridLayer, HeatmapLayer} from '@deck.gl/aggregation-layers';

new ScreenGridLayer({
  id: 'screen-grid',
  data: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/sf-bike-parking.json',
  getPosition: d => d.COORDINATES,
  getWeight: d => d.SPACES,
  cellSizePixels: 50,     // 屏幕像素网格边长，默认 100
  gpuAggregation: true,
  aggregation: 'SUM',     // SUM / MEAN / MIN / MAX / COUNT
  colorDomain: null,      // 留空则运行时按实际最值自动设定
  opacity: 0.8
});

new HeatmapLayer({
  id: 'heatmap',
  data: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/sf-bike-parking.json',
  getPosition: d => d.COORDINATES,
  getWeight: d => d.SPACES,
  radiusPixels: 25,        // 默认 30
  aggregation: 'SUM',      // SUM / MEAN
  intensity: 1,
  threshold: 0.05,         // 低权重像素按 alpha 淡出
  weightsTextureSize: 2048 // 调小可提速但有像素化
});
```

### 与 MapLibre / Mapbox 底图集成

两种模式：**叠加（overlaid）** 是两块独立 canvas 上下叠放、相机同步，各库独立渲染，兼容性最好；**交错（interleaved）** 是 deck.gl 直接渲染进底图的 WebGL2 上下文，deck 图层可被底图标注、3D 建筑遮挡，但要求底图暴露相应开发接口，且**底图必须是 WebGL2 上下文**。

```javascript
import {MapboxOverlay} from '@deck.gl/mapbox';
import {ScatterplotLayer} from '@deck.gl/layers';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://demotiles.maplibre.org/style.json',
  center: [0.45, 51.47],
  zoom: 11
});

map.once('load', () => {
  const overlay = new MapboxOverlay({
    interleaved: true,   // false 即为叠加模式
    layers: [
      new ScatterplotLayer({
        id: 'deck-point',
        data: [{position: [0.45, 51.47]}],
        getPosition: d => d.position,
        getFillColor: [255, 0, 0, 100],
        getRadius: 1000,
        beforeId: 'waterway-label' // 交错模式插入位置；Mapbox v3 Standard 样式用 slot: 'bottom'
      })
    ],
    getTooltip: ({object}) => object && '命中'
  });
  map.addControl(overlay);

  overlay.setProps({layers: [/* 更新后的图层 */]}); // 后续更新
});
```

`MapboxOverlay` 接受与 `Deck` 相同的 props，但 `viewState` / `initialViewState` / `controller` / `canvas` / `parent` / `device` 由内部托管；交错模式下 `useDevicePixels` 被忽略。使用 Mapbox 时把 `maplibregl` 换成 `mapbox-gl` 并配置 `accessToken`。React 场景推荐用 react-map-gl 的 `useControl` 挂载：

```javascript
import {Map, useControl} from 'react-map-gl/maplibre';
import {MapboxOverlay} from '@deck.gl/mapbox';

function DeckGLOverlay(props) {
  const overlay = useControl(() => new MapboxOverlay(props));
  overlay.setProps(props);
  return null;
}
```

### 交互与拾取

拾取由 GPU 离屏渲染实现，回调中的 `info` 含 `object`（原始数据项）、`index`、`layer`、`coordinate`、`x` / `y`（屏幕坐标）。聚合图层的 `object` 是聚合单元而非原始点，含 `count`、`elevationValue`、`colorValue` 等字段。

```javascript
const deck = new Deck({
  initialViewState: {longitude: -122.4, latitude: 37.74, zoom: 11},
  controller: true,
  layers: [layer],
  onClick: ({object, coordinate}) => console.log(object, coordinate),
  onHover: ({object}) => { hoveredId = object ? object.id : null; }
});

deck.pickObject({x: 100, y: 100, radius: 4, layerIds: ['stations']}); // 程序化拾取
```

---

## 典型工作流

以「MapLibre 底图 + 百万级点位聚合 + 矢量瓦片底图数据 + 点击查看详情」为例：

1. 安装 `@deck.gl/core`、`@deck.gl/layers`、`@deck.gl/aggregation-layers`、`@deck.gl/geo-layers`、`@deck.gl/mapbox` 与 `maplibre-gl`
2. 初始化 `maplibregl.Map`，在 `load` 事件后创建 `MapboxOverlay`
3. 概览用聚合图层（`HexagonLayer` / `ScreenGridLayer`），细节用 `ScatterplotLayer`
4. 需要矢量瓦片数据时叠加 `MVTLayer`
5. 绑定 `getTooltip` 与 `onClick` 实现悬停与点击反馈
6. 数据刷新时调用 `overlay.setProps({layers: [...]})`，保持 `data` 引用稳定
7. 组件卸载时调用 `overlay.finalize()` 释放 GPU 资源

```javascript
import {MapboxOverlay} from '@deck.gl/mapbox';
import {HexagonLayer} from '@deck.gl/aggregation-layers';

// map：已初始化并触发过 load 的 maplibregl.Map 实例
const data = await fetch('/api/bike-parking').then(r => r.json());

const overlay = new MapboxOverlay({
  interleaved: true,
  layers: [
    new HexagonLayer({
      id: 'density',
      data,
      getPosition: d => d.coordinates,
      getColorWeight: d => d.count,
      getElevationWeight: d => d.count,
      radius: 200,
      extruded: true,
      elevationScale: 4,
      pickable: true
    })
  ],
  getTooltip: ({object}) => object && `数量：${object.elevationValue ?? object.count}`
});

map.addControl(overlay);
```

---

## 最佳实践

1. **保持 `data` 引用稳定**：图层通过浅比较判断数据是否变化，若每次渲染都用 `.filter()` / `.map()` 生成新数组，会每帧重建 GPU 缓冲；确需比较内容时用 `dataComparator`
2. **访问器尽量用常量**：常量 props 的更新成本远低于函数，能预计算就预计算，避免在访问器里创建新数组
3. **按需开启 `pickable`**：拾取要额外做一次离屏渲染，不需要 tooltip/点击的图层保持默认 `false`；每帧可拾取图层上限约 256 个
4. **用 `visible` 替代增删图层**：移除图层会丢弃已上传的 GPU 状态，重新显示时需重新构建
5. **用 `updateTriggers` 精准失效**：只让依赖某个字段的属性重建，而非整层重建
6. **大数据量走二进制**：提供带 `length` 字段的非迭代对象，或在 `data.attributes` 中直接给出类型化数组，可绕过 CPU 属性展开（仅限非复合图层）
7. **注意 overdraw 与像素比**：片元着色成本随屏幕像素增长，高分屏下可关闭 `useDevicePixels`；单图层数据量上限约 1600 万项
8. **图层数量控制在百级以内**：deck.gl 并非为数千图层设计，图层过多会拖慢拾取与排序
9. **交错模式留意抗锯齿**：底图上下文 `antialias` 为 false，需要时在相关图层上开 `antialiasing: true`；生产环境也不要开启 luma.gl 的 debug 模式

---

## 常见问题

| 问题 | 原因与解决 |
|------|------------|
| 页面空白，无任何图层 | 容器未设置高度或 canvas 被遮挡：为容器设置显式 `height`；独立模式记得 canvas 是透明层，需要背景或底图 |
| 报错 `Cannot read properties of undefined` 或图层不生效 | 子包版本不一致：整包安装，或保证 `@deck.gl/*` 各子包版本号完全一致（子包版本需手动同步） |
| 图层数据更新了但画面不变 | `data` 引用未变化，或访问器依赖的外部变量未触发失效：改用新数组引用，或用 `updateTriggers` 声明依赖 |
| tooltip / 点击无反应 | 图层 `pickable` 为默认的 `false`：显式设为 `true`；点太小可调大 `pickingRadius`，或确认 `layerIds` 过滤条件正确 |
| 交错模式渲染异常或图层被底图遮挡 | 底图非 WebGL2 上下文时 deck 无法插入（WebGL1 不支持）；检查 `beforeId` 是否指向底图存在的图层 id，Mapbox v3 Standard 样式改用 `slot: 'bottom'` |
| Mapbox 底图报 401 / 提示需要 access token | Mapbox GL JS v2+ 需配置 `accessToken`：改用 MapLibre 则无需 token，或正确设置 `mapbox-gl` 的 token |
| 悬停时卡顿、掉帧 | 拾取成本过高：关闭非必要图层的 `pickable`，减少可拾取图层数量，或在高分屏上关闭 `useDevicePixels` |
| 百万级点位渲染慢或内存高 | 未启用 GPU 聚合或访问器过重：改用 `HexagonLayer` / `ScreenGridLayer`（`gpuAggregation: true`），并让访问器保持轻量 |
| 聚合图层颜色全是同一档 | `colorDomain` 未按数据设定：留空让其自动取实际最值，或显式传入 `[min, max]`；权重字段需通过 `getColorWeight` 提供 |

---

## 参考资源

- 官方文档与示例：<https://deck.gl/>
- 独立模式快速上手：<https://deck.gl/docs/get-started/using-standalone>
- 与底图集成：<https://deck.gl/docs/get-started/using-with-map>
- 图层目录：<https://deck.gl/docs/api-reference/layers>
- `MapboxOverlay` API：<https://deck.gl/docs/api-reference/mapbox/mapbox-overlay>
- 性能调优指南：<https://deck.gl/docs/developer-guide/performance>
- 源码与发布记录：<https://github.com/visgl/deck.gl>

## 相关技能

- **mapbox-gl-js** — 矢量瓦片底图与 Style Spec，deck.gl 的常见底图搭档：[../mapbox-gl-js/SKILL.md](../mapbox-gl-js/SKILL.md)
- **openlayers** — 开源 2D WebGIS 库，投影、MVT 与高级交互：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **leaflet** — 轻量 2D 瓦片地图，适合中小数据量与简单场景：[../leaflet/SKILL.md](../leaflet/SKILL.md)
- **cesiumjs** — 三维地球与 3D Tiles 可视化：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("deck-gl")` 加载（用户也可输入 `/deck-gl`）；本技能无 reference 子目录，示例代码写入会话工作区工程，技能目录只读。
- **执行环境**：`npm install`、`npm run build` 交给 `pwsh`；子包多、安装输出长，重定向到文件再分段读。
- **先探测版本**：`npm ls deck.gl @deck.gl/core @deck.gl/layers @deck.gl/geo-layers`；所有 `@deck.gl/*` 必须是同一版本 9.4.0，混版会报 `Cannot read properties of undefined`。本技能按 9.4.0 编写。
- **验证产物**：`npm run build` 后 `npx serve dist`，`curl.exe -I http://localhost:5173/` 确认入口；WebGL 是否真出图只能由浏览器确认，DSH 不打开浏览器，请用户看画面和控制台，有截图再用 `read_image`。
- **无 GPU 环境**：无头/CI 环境无法验证 WebGL，构建通过不等于渲染正确，不要据此报告“已渲染”。
- **数据与坐标**：位置一律 `[经度, 纬度]`；保持 `data` 引用稳定，不要在渲染路径里 `filter`/`map` 生成新数组，否则 GPU 缓冲反复重建。
- **常见症状**：空白画布先查容器高度与底图；数据变了画面不变用 `updateTriggers`；tooltip 无反应是 `pickable` 默认 false。
- **安全与权限**：装包、起 dev server 前先征得用户同意；用 Mapbox 底图时提醒 token 与计费。
