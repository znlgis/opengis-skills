---
name: leaflet
description: "Use when adding lightweight interactive 2D maps to web pages — tile layers, markers, GeoJSON overlays, layer control, popups. Leaflet: compact, mobile-friendly open-source JavaScript web mapping library."
tags:
  - javascript
  - web
  - 2d
  - map
  - geojson
  - tile-layer
  - markers
  - plugins
  - vue
  - react
---

> **项目地址：** <https://github.com/Leaflet/Leaflet>
>
> **官方文档：** <https://leafletjs.com/>
>
> **API 参考：** <https://leafletjs.com/reference.html>
>
> **示例：** <https://leafletjs.com/examples.html>
>
> **最新版本：** 1.9.4（截至2026-10，npm `leaflet`）
>
> **许可证：** BSD-2-Clause

## 概述

Leaflet 是面向移动端与桌面端的开源 2D 地图库，核心构建体积约 42 KB，提供命令式的类 jQuery API。特性：

- **瓦片图层**：支持 OSM、XYZ、WMS、WMTS、ArcGIS 等栅格底图
- **矢量叠加**：Marker、Popup、Tooltip、Circle、Polygon、Polyline、GeoJSON
- **图层管理**：LayerGroup、FeatureGroup、`L.control.layers` 切换底图与叠加层
- **事件系统**：Map / Layer / Marker 均继承 `Evented`，统一 `on` / `off` / `once`
- **插件生态**：绘制、聚合、热力图、矢量瓦片等均有成熟第三方插件
- **框架无关**：可在原生 JS、Vue、React、Svelte 中直接使用

---

## 环境准备

### 方式一：CDN

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
          integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <style>
    /* 容器必须显式设置高度，否则地图不可见 */
    #map { height: 400px; }
  </style>
</head>
<body>
  <div id="map"></div>
</body>
</html>
```

### 方式二：npm

```bash
npm install leaflet
```

```javascript
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
```

### 验证

打开页面应看到可拖拽、可缩放的 OSM 底图；控制台执行 `L.version` 返回 `"1.9.4"`。

```javascript
console.log(L.version); // "1.9.4"
```

---

## 核心 API

### L.map

```javascript
const map = L.map('map', {
  center: [39.9087, 116.3975], // [纬度, 经度]
  zoom: 12,
  zoomControl: true,
  attributionControl: true
});
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `center` | LatLng | 无 | 初始中心点 `[lat, lng]` |
| `zoom` | Number | 无 | 初始缩放级别 |
| `zoomControl` | Boolean | `true` | 是否添加缩放控件 |
| `attributionControl` | Boolean | `true` | 是否添加版权控件 |
| `minZoom` / `maxZoom` | Number | 无 | 缩放范围限制 |

### L.tileLayer

```javascript
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  subdomains: 'abc',
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
```

URL 模板占位符：`{s}` 子域、`{z}` 层级、`{x}`/`{y}` 瓦片坐标、`{r}` 高清后缀（`@2x`）。

### L.marker

```javascript
const marker = L.marker([39.9087, 116.3975], {
  draggable: true,
  title: '天安门'
}).addTo(map);

marker.bindPopup('天安门广场').openPopup();
```

### L.geoJSON

```javascript
L.geoJSON(geojsonData, {
  style: (feature) => ({ color: '#ff7800', weight: 2 }),
  pointToLayer: (feature, latlng) => L.circleMarker(latlng, { radius: 6 }),
  onEachFeature: (feature, layer) => {
    layer.bindPopup(feature.properties.name);
  },
  filter: (feature) => feature.properties.show !== false
}).addTo(map);
```

| 选项 | 签名 | 用途 |
|------|------|------|
| `style` | `(feature) => Path options` | 面/线样式，可传对象或函数 |
| `pointToLayer` | `(feature, latlng) => Layer` | 自定义点渲染（如圆点替代默认图标） |
| `onEachFeature` | `(feature, layer) => void` | 为每个要素绑定弹窗、事件 |
| `filter` | `(feature) => Boolean` | 返回 `false` 的要素不渲染 |
| `coordsToLatLng` | `(coords) => LatLng` | 自定义坐标转换 |

### L.layerGroup 与图层控制

```javascript
const baseLayers = {
  'OSM': L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
  '高德影像': L.tileLayer('https://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}')
};

const points = L.layerGroup([marker]);
const overlays = { '标注点': points };

L.control.layers(baseLayers, overlays).addTo(map);
baseLayers['OSM'].addTo(map); // 默认底图需手动添加
```

### 事件系统

`Map`、`Layer`、`Marker` 均继承 `Evented`，使用 `on` / `off` / `once` / `fire`。

```javascript
map.on('click', (e) => console.log(e.latlng));
map.on('zoomend moveend', () => console.log(map.getZoom()));

marker.on('click', () => console.log('marker clicked'));
marker.on('dragend', () => console.log(marker.getLatLng()));

const handler = (e) => console.log(e);
map.on('mousemove', handler);
map.off('mousemove', handler); // 显式移除，避免内存泄漏
```

常用 Map 事件：`click`、`dblclick`、`mousemove`、`zoomend`、`moveend`、`layeradd`、`layerremove`、`resize`、`popupopen`。

---

## 典型工作流

1. **初始化地图**：`L.map('map', { center, zoom })`，容器须有确定高度
2. **添加底图**：`L.tileLayer(urlTemplate, { attribution }).addTo(map)`
3. **叠加数据**：`L.marker` 或 `L.geoJSON(data, { style, onEachFeature })`
4. **绑定交互**：`layer.bindPopup()` / `map.on('click', fn)`
5. **图层管理**：`L.control.layers(baseLayers, overlays).addTo(map)`
6. **自适应视图**：`map.fitBounds(layer.getBounds())`
7. **销毁清理**：组件卸载时调用 `map.remove()`

```javascript
const layer = L.geoJSON(data).addTo(map);
map.fitBounds(layer.getBounds(), { padding: [20, 20] });
```

---

## 插件生态

插件通过 `L.xxx` 扩展，使用时先引入其 CSS/JS，再调用扩展 API。

| 插件 | npm 包名 | 用途 |
|------|----------|------|
| Leaflet.draw | `leaflet-draw` | 交互式绘制/编辑几何（点、线、面、矩形、圆） |
| Leaflet.markercluster | `leaflet.markercluster` | 大量点标记的聚合与展开动画 |
| Leaflet.heat | `leaflet.heat` | 基于点数据的热力图图层 |

```javascript
// 绘制控件
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';

const drawnItems = new L.FeatureGroup().addTo(map);
map.addControl(new L.Control.Draw({ edit: { featureGroup: drawnItems } }));
map.on(L.Draw.Event.CREATED, (e) => drawnItems.addLayer(e.layer));
```

```javascript
// 点聚合
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';

const cluster = L.markerClusterGroup();
cluster.addLayer(L.marker([39.9, 116.4]));
map.addLayer(cluster);
```

```javascript
// 热力图
import 'leaflet.heat';

const heat = L.heatLayer([[39.9, 116.4, 0.5], [39.91, 116.41, 0.8]], { radius: 25 });
heat.addTo(map);
```

---

## 与 Vue / React 集成

核心原则：**用 ref / state 持有 map 实例，在挂载时创建、卸载时 `map.remove()`**，避免重复初始化和内存泄漏。

### Vue 3

```vue
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const mapEl = ref(null);
let map = null;

onMounted(() => {
  map = L.map(mapEl.value).setView([39.9087, 116.3975], 12);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
});

onBeforeUnmount(() => {
  map?.remove();
  map = null;
});
</script>

<template>
  <div ref="mapEl" style="height: 400px"></div>
</template>
```

### React

```jsx
import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export default function MapView() {
  const containerRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    const map = L.map(containerRef.current).setView([39.9087, 116.3975], 12);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  return <div ref={containerRef} style={{ height: 400 }} />;
}
```

---

## 最佳实践

1. **容器高度**：`#map` 必须有显式高度（如 `height: 400px`），否则渲染为 0 高度不可见
2. **及时销毁**：单页应用卸载组件时调用 `map.remove()`，清除事件与 DOM
3. **事件解绑**：自定义监听器用具名函数并通过 `map.off(type, handler)` 移除
4. **大数据量**：数千点以上使用 `leaflet.markercluster` 聚合，避免逐点渲染卡顿
5. **避免重复初始化**：同一容器仅调用一次 `L.map()`，重复调用需先 `remove()`
6. **正确坐标顺序**：Leaflet 使用 `[纬度, 经度]`，与 GeoJSON 的 `[经度, 纬度]` 相反
7. **版权声明**：使用 OSM 等底图时在 `attribution` 中保留版权信息

---

## 常见问题

| 问题 | 原因与解决 |
|------|------------|
| 地图区域空白 / 不显示 | 容器缺少高度：为 `#map` 设置 `height`（如 `400px`），或地图初始化后调用 `map.invalidateSize()` |
| 标记图标 404 / 显示为破图 | npm + 打包器下 `leaflet.css` 引用的默认图标路径失效，需手动设置 `L.Icon.Default` 的 `iconUrl`/`iconRetinaUrl`/`shadowUrl` 或改用 CDN 引入 CSS |
| 地图在弹窗/隐藏容器中显示错乱 | 容器尺寸变化后调用 `map.invalidateSize()` 重算 |
| `L is not defined` | CDN 脚本未加载或引入顺序错误：先加载 `leaflet.js` 再执行代码；npm 下确认 `import L from 'leaflet'` |
| 经纬度颠倒导致点跑到别处 | 参数顺序为 `[lat, lng]`；GeoJSON 坐标是 `[lng, lat]`，必要时用 `coordsToLatLng` 转换 |
| 组件切换后内存持续增长 | 卸载时未调用 `map.remove()`，或事件监听器未 `off` 解绑 |
| 瓦片加载失败 / 跨域 | 检查瓦片服务 URL 模板与 CORS 头；WMS 需确认服务端允许跨域 |
| 与 Vue/React 响应式冲突 | 不要把 `L.map` 实例放进 `reactive`/`useState`（会代理内部对象），用普通变量或 `useRef` 持有 |

---

## 参考资源

- 官方文档：<https://leafletjs.com/>
- API 参考：<https://leafletjs.com/reference.html>
- 官方示例：<https://leafletjs.com/examples.html>
- 插件列表：<https://leafletjs.com/plugins.html>
- 源码仓库：<https://github.com/Leaflet/Leaflet>

## 相关技能

- **openlayers** — 功能更全的 2D WebGIS 库（投影、MVT、高级交互）：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **cesiumjs** — 三维地球与 3D Tiles 可视化：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)
- **geoserver** — 发布 WMS/WFS/瓦片服务作为 Leaflet 数据源：[../geoserver/SKILL.md](../geoserver/SKILL.md)

## AI 使用建议

- **坐标顺序**：生成代码时严格区分 `[lat, lng]`（Leaflet）与 `[lng, lat]`（GeoJSON）
- **生命周期**：框架集成务必成对生成创建与 `map.remove()` 清理逻辑
- **图标修复**：npm 场景下主动补充默认图标路径配置，避免破图
- **插件引入**：先引 CSS 再引 JS，绘制/聚合/热力图分别对应 `leaflet-draw`、`leaflet.markercluster`、`leaflet.heat`
- **大数据量**：点数超过约 1000 时优先建议 `markercluster` 或改用 `circleMarker` 降低开销
