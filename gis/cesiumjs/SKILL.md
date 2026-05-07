---
name: cesiumjs
description: CesiumJS 是开源的 JavaScript 三维地球与地图库，基于 WebGL，无插件即可在浏览器中呈现高精度的 3D 全球地形、影像、3D Tiles、glTF 模型与时序动画，是 Web 端三维 GIS 的事实标准。
tags:
  - javascript
  - webgl
  - 3d
  - 3d-tiles
  - gltf
  - earth
  - map
  - web
  - visualization
---

> **项目地址：** <https://github.com/CesiumGS/cesium>
>
> **官方文档：** <https://cesium.com/learn/cesiumjs-learn/>
>
> **API 参考：** <https://cesium.com/learn/cesiumjs/ref-doc/>
>
> **Sandcastle：** <https://sandcastle.cesium.com/>
>
> **许可证：** Apache-2.0

## 概述

CesiumJS 提供：

- **三维全球**：WGS84 椭球体、地形（Quantized-Mesh）、卫星影像
- **3D Tiles**：海量三维流式（倾斜摄影、BIM、点云、城市模型）
- **glTF / GLB 模型**：标准 PBR 渲染
- **CZML / Entity API**：高层声明式数据模型，时序动画
- **Primitive API**：底层高性能 API
- **可视化分析**：通视/剖面/缓冲/裁剪/视频投影/光影

---

## 安装

```bash
npm install cesium
```

```html
<link href="https://cdn.jsdelivr.net/npm/cesium/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/cesium/Build/Cesium/Cesium.js"></script>
```

### Vite 集成

```js
import { defineConfig } from 'vite';
import cesium from 'vite-plugin-cesium';
export default defineConfig({ plugins: [cesium()] });
```

### Webpack 集成

需将 `node_modules/cesium/Build/Cesium/{Workers,Assets,Widgets}` 拷贝到输出目录，并设置 `window.CESIUM_BASE_URL`。

---

## 快速上手

```html
<div id="cesiumContainer" style="width:100%;height:100vh"></div>
<script type="module">
  import * as Cesium from 'cesium';
  import 'cesium/Build/Cesium/Widgets/widgets.css';

  Cesium.Ion.defaultAccessToken = 'YOUR_ION_TOKEN';

  const viewer = new Cesium.Viewer('cesiumContainer', {
    terrainProvider: await Cesium.createWorldTerrainAsync(),
    timeline: false, animation: false
  });

  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(116.397, 39.908, 5000)
  });
</script>
```

---

## 核心概念

| 概念 | 说明 |
|------|------|
| `Viewer` | 顶层容器 |
| `Scene` | 渲染场景，含 globe/camera/primitives |
| `Entity` | 高层数据对象，时序、属性、可视化封装 |
| `DataSource` | Entity 集合（CZML/GeoJSON/KML） |
| `Primitive` | 低层渲染单元，性能最优 |
| `Cesium3DTileset` | 3D Tiles 数据集 |

---

## 影像与地形

```js
viewer.imageryLayers.addImageryProvider(new Cesium.UrlTemplateImageryProvider({
  url: 'https://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}'
}));

viewer.terrainProvider = await Cesium.createWorldTerrainAsync({
  requestVertexNormals: true,
  requestWaterMask: true
});
```

---

## Entity 数据驱动

```js
const ds = await Cesium.GeoJsonDataSource.load('/data/poi.geojson', {
  stroke: Cesium.Color.RED, fill: Cesium.Color.RED.withAlpha(0.3),
  strokeWidth: 2, clampToGround: true
});
viewer.dataSources.add(ds);
viewer.flyTo(ds);

viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(116.397, 39.908),
  point: { pixelSize: 10, color: Cesium.Color.YELLOW },
  label: { text: '天安门', font: '14px sans-serif',
           verticalOrigin: Cesium.VerticalOrigin.BOTTOM }
});

viewer.entities.add({
  polyline: {
    positions: Cesium.Cartesian3.fromDegreesArray([116, 39, 121, 31]),
    width: 3, material: Cesium.Color.CYAN, clampToGround: true
  }
});

viewer.entities.add({
  polygon: {
    hierarchy: Cesium.Cartesian3.fromDegreesArray([116,39, 117,39, 117,40, 116,40]),
    material: Cesium.Color.RED.withAlpha(0.5),
    extrudedHeight: 1000
  }
});
```

---

## 3D Tiles

```js
const tileset = await Cesium.Cesium3DTileset.fromUrl('https://server/tileset.json', {
  maximumScreenSpaceError: 16
});
viewer.scene.primitives.add(tileset);
viewer.flyTo(tileset);

tileset.style = new Cesium.Cesium3DTileStyle({
  color: { conditions: [
    ['${height} >= 100', 'rgba(255,0,0,0.8)'],
    ['true', 'rgb(180,180,180)']
  ]}
});
```

---

## glTF 模型

```js
viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 0),
  model: { uri: '/models/airplane.glb', minimumPixelSize: 64, maximumScale: 200 }
});
```

---

## 时序动画（CZML）

```js
const czml = [
  { id: 'document', name: 'demo', version: '1.0',
    clock: { interval: '2024-01-01/2024-01-02', currentTime: '2024-01-01' } },
  { id: 'plane',
    position: { epoch: '2024-01-01T00:00:00Z',
      cartographicDegrees: [0, 116, 39, 1000, 3600, 117, 40, 1000] },
    point: { color: { rgba: [255, 0, 0, 255] }, pixelSize: 10 } }
];
viewer.dataSources.add(Cesium.CzmlDataSource.load(czml));
```

---

## 交互与拾取

```js
const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
handler.setInputAction(e => {
  const picked = viewer.scene.pick(e.position);
  if (Cesium.defined(picked)) console.log(picked.id);

  const c3 = viewer.camera.pickEllipsoid(e.position);
  if (c3) {
    const c = Cesium.Cartographic.fromCartesian(c3);
    console.log(Cesium.Math.toDegrees(c.longitude),
                Cesium.Math.toDegrees(c.latitude));
  }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);
```

---

## 摄像机

```js
viewer.camera.flyTo({
  destination: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 5000),
  orientation: { heading: 0, pitch: -Cesium.Math.PI_OVER_FOUR, roll: 0 },
  duration: 2
});
viewer.trackedEntity = entity;
```

---

## 性能优化

1. 大量静态要素优先用 Primitive 而非 Entity
2. 3D Tiles 启用 `dynamicScreenSpaceError`、`skipLevelOfDetail`
3. 影像图层数量 ≤ 4
4. 启用 `requestRenderMode = true`（按需渲染）
5. `clampToGround` 适度使用
6. 释放：`viewer.entities.removeAll()`、`tileset.destroy()`
7. 监听 `webglcontextlost`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 黑屏 | 检查 `CESIUM_BASE_URL` 与静态资源 |
| 模型贴地不准 | `HeightReference.CLAMP_TO_GROUND` 或地形采样 |
| 性能卡顿 | 启用 `requestRenderMode`，降低 `maximumScreenSpaceError` |
| 国内瓦片偏移 | 使用 GCJ02→WGS84 纠偏 |
| Token 过期 | 不需要 ion 时不设置 token；或自托管 |

---

## AI 使用建议

### 推荐工作流

1. **初始化 Viewer**：使用 `Cesium.Viewer` 创建三维地球，设置地形和影像提供者
2. **加载数据**：根据数据类型选择合适 API——GeoJSON/CZML 用 `DataSource`，3D 瓦片用 `Cesium3DTileset`，单模型用 `Entity.model`
3. **设置相机**：使用 `camera.flyTo()` 定位到目标区域
4. **添加交互**：通过 `ScreenSpaceEventHandler` 处理点击拾取
5. **性能优化**：根据场景复杂度启用 `requestRenderMode`、调整 `maximumScreenSpaceError`

### 关键注意事项

- **Ion Token**：使用 Cesium ion 服务需要设置 `Cesium.Ion.defaultAccessToken`；自托管数据则无需
- **坐标转换**：Cesium 内部使用 Cartesian3（地心地固坐标），通过 `Cesium.Cartesian3.fromDegrees(lon, lat, height)` 将经纬度转为内部坐标
- **Entity vs Primitive**：少量动态要素用 Entity API（简洁），大量静态要素用 Primitive API（高性能）
- **贴地（clampToGround）**：在三维地形上，需要明确设置 `clampToGround: true` 或 `HeightReference.CLAMP_TO_GROUND`
- **资源释放**：不再使用的 `DataSource` 调用 `viewer.dataSources.remove(ds)`，3D Tileset 调用 `tileset.destroy()`
- **静态资源部署**：使用 Webpack/Vite 时，确保 `Assets`、`Workers`、`Widgets` 目录正确复制到输出目录

## 相关技能

- **openlayers** — 二维 Web 地图库：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **geoserver** — 地图服务发布：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **geoserver-rest-api** — REST 自动化管理：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)
- **mapsui** — .NET 跨平台地图组件：[../mapsui/SKILL.md](../mapsui/SKILL.md)

## 参考资源

- 学习中心：<https://cesium.com/learn/>
- API：<https://cesium.com/learn/cesiumjs/ref-doc/>
- Sandcastle：<https://sandcastle.cesium.com/>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/cesiumjs/>
