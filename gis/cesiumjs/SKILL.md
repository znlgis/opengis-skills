---
name: cesiumjs
description: "Use when building browser-based 3D globes, 3D Tiles, CZML/time-dynamic data, or glTF models with npm cesium 1.146.0 — Viewer, Cesium3DTileset, Ion token (Cesium.Ion.defaultAccessToken), CESIUM_BASE_URL for Workers/Assets/Widgets, GCJ-02 tile offset, or debugging a black screen after a Vite/Webpack build."
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
> **最新版本：** 1.146.0（截至2026-10，npm `cesium`）
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

> **1.146 变更：** 数学/几何/时间/工具类被拆分为新包 `@cesium/core`（`cesium@1.146.0` 依赖 `@cesium/core@^0.1.0`）。从 `cesium` 主包导入的代码不受影响；直接按子路径引用 `@cesium/engine` 的代码需改从 `@cesium/core` 导入（旧导出计划在后续版本移除，1.146 仍可用）。

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

## 典型工作流

1. **初始化 Viewer**：使用 `Cesium.Viewer` 创建三维地球，设置地形和影像提供者
2. **加载数据**：根据数据类型选择合适 API——GeoJSON/CZML 用 `DataSource`，3D 瓦片用 `Cesium3DTileset`，单模型用 `Entity.model`
3. **设置相机**：使用 `camera.flyTo()` 定位到目标区域
4. **添加交互**：通过 `ScreenSpaceEventHandler` 处理点击拾取
5. **性能优化**：根据场景复杂度启用 `requestRenderMode`、调整 `maximumScreenSpaceError`

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

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("cesiumjs")` 加载（用户也可输入 `/cesiumjs`）；本技能无 reference 子目录，示例代码直接落到会话工作区的工程里，技能目录只读。
- **执行环境**：`npm install`、`npm run build` 交给 `pwsh`；Windows 下 `npm` 实为 `npm.cmd`，脚本里写 `cmd /c npm run build` 更稳；装包和大构建用后台作业，输出重定向到文件再分段读。
- **先探测版本**：`npm ls cesium`（未安装时 `npm view cesium version`）。本技能按 1.146.0 编写：该版本依赖 `@cesium/core@^0.1.0`，数学/几何/时间/工具类已拆到 `@cesium/core`，低于 1.146 的工程不要照搬这条迁移建议。
- **验证产物**：`npm run build` 通过后用 `npx serve dist` 或 `python -m http.server 5173 -d dist` 起静态服务，用 `curl.exe -I` 检查 `http://localhost:5173/Cesium.js` 与 `.../Cesium/Widgets/widgets.css` 返回 200（404 或 text/html 说明资源没拷贝）；DSH 不打开浏览器，把 URL 和预期画面交给用户，有截图再用 `read_image` 核对。
- **Ion 与部署**：`Cesium.Ion.defaultAccessToken` 从环境变量注入（Vite 用 `import.meta.env.VITE_CESIUM_ION_TOKEN`），不要写进源码或提交；黑屏先查 `window.CESIUM_BASE_URL` 与 `Workers/Assets/Widgets` 是否随构建产物发布。
- **坐标与性能**：定位一律 `Cesium.Cartesian3.fromDegrees(lon, lat, height)`；大量静态要素用 Primitive，少量动态要素才用 Entity；`clampToGround` 只在需要贴地时开启。
- **常见症状**：瓦片整体错位是国内底图的 GCJ-02 偏移，需先纠偏；ion 服务 401/403 多为 token 未设置或失效；`tileset.destroy()`、`viewer.dataSources.remove()` 不调用会持续占用显存。
- **安全与权限**：安装依赖、启动 dev server、改端口前先征得用户同意；日志和回答中不要回显 Ion token。

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
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/cesium/>
