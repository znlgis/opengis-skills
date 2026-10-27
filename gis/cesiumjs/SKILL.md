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
> **最新版本：** 1.146.0（截至 2026-10，npm `cesium`）
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

### 方式一：npm

```bash
npm install cesium
npm ls cesium            # 验证：应显示 cesium@1.146.0
```

```js
import { defineConfig } from 'vite';
import cesium from 'vite-plugin-cesium';

export default defineConfig({ plugins: [cesium()] });
```

### 方式二：CDN

```html
<link href="https://cdn.jsdelivr.net/npm/cesium@1.146.0/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/cesium@1.146.0/Build/Cesium/Cesium.js"></script>
```

```bash
# 验证 CDN 版本可达
curl.exe -I https://cdn.jsdelivr.net/npm/cesium@1.146.0/Build/Cesium/Cesium.js   # 期望 200
```

### 打包器接入

- **Vite**：用 `vite-plugin-cesium`，按上面的 `vite.config.js` 注册，插件负责拷贝静态资源
- **Webpack**：将 `node_modules/cesium/Build/Cesium/{Workers,Assets,Widgets}` 拷到输出目录，并在入口最早处设置 `window.CESIUM_BASE_URL`

> **1.146 变更：** 数学/几何/时间/工具类被拆分为新包 `@cesium/core`（`cesium@1.146.0` 依赖 `@cesium/core@^0.1.0`）。从 `cesium` 主包导入的代码不受影响；直接按子路径引用 `@cesium/engine` 的代码需改从 `@cesium/core` 导入（旧导出计划在后续版本移除，1.146 仍可用）。

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

以「GeoJSON 点位 + 倾斜摄影 3D Tiles」为例，输入 `data/poi.geojson` 与 `/tiles/tileset.json`，输出可点击拾取的三维场景。

1. **初始化 Viewer**：`new Cesium.Viewer('cesiumContainer', { terrainProvider: await Cesium.createWorldTerrainAsync() })`
2. **加载矢量数据**：`GeoJsonDataSource.load()` → `viewer.dataSources.add(ds)` → `viewer.flyTo(ds)`
3. **加载 3D Tiles**：`Cesium3DTileset.fromUrl()` → `scene.primitives.add(tileset)` → `viewer.zoomTo(tileset)`
4. **添加交互**：`ScreenSpaceEventHandler` + `scene.pick()` 取 `picked.id`，`camera.pickEllipsoid()` 取经纬度
5. **性能与释放**：静态要素用 Primitive，`requestRenderMode = true`，卸载时 `tileset.destroy()` / `viewer.destroy()`

```js
import * as Cesium from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';

Cesium.Ion.defaultAccessToken = import.meta.env.VITE_CESIUM_ION_TOKEN;

const viewer = new Cesium.Viewer('cesiumContainer', {
  terrainProvider: await Cesium.createWorldTerrainAsync(),
  timeline: false,
  animation: false
});

// 1) GeoJSON 点位：统一改成扁平圆点，避免默认图钉遮挡
const ds = await Cesium.GeoJsonDataSource.load('/data/poi.geojson', { clampToGround: true });
viewer.dataSources.add(ds);
for (const entity of ds.entities.values) {
  entity.billboard = undefined;
  entity.point = new Cesium.PointGraphics({ pixelSize: 8, color: Cesium.Color.ORANGE });
}
await viewer.flyTo(ds);

// 2) 3D Tiles：加载倾斜摄影并飞到数据范围
const tileset = await Cesium.Cesium3DTileset.fromUrl('/tiles/tileset.json', {
  maximumScreenSpaceError: 16
});
viewer.scene.primitives.add(tileset);
await viewer.zoomTo(tileset);

// 3) 点击拾取：先试 3D Tiles / 点要素，再回退到椭球面坐标
const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
handler.setInputAction((e) => {
  const picked = viewer.scene.pick(e.position);
  console.log('picked:', Cesium.defined(picked) ? picked.id : null);
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);
```

**验证产物**：`npm run build` 后 `python -m http.server 5173 -d dist`，`curl.exe -I http://localhost:5173/Cesium/Workers/createVerticesFromHeightmap.js` 返回 200 才说明 Workers 已随产物发布。

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
| 黑屏 / 资源 404 | 控制台报 `Unable to determine Cesium base URL automatically, try defining a global variable called CESIUM_BASE_URL.` 时，在入口最早处设 `window.CESIUM_BASE_URL = '/Cesium'`，并确认 `Workers/Assets/Widgets` 已随构建产物发布 |
| 模型贴地不准 | `HeightReference.CLAMP_TO_GROUND` 或地形采样 |
| 性能卡顿 | 启用 `requestRenderMode`，降低 `maximumScreenSpaceError`；静态要素改 Primitive |
| 报 `WebGL 2 context is required` | 浏览器/环境未提供 WebGL2（无头浏览器、远程桌面软件渲染）；开启硬件加速或改用支持 WebGL2 的环境 |
| 国内瓦片偏移 | 使用 GCJ02→WGS84 纠偏 |
| Token 过期 | 不需要 ion 时不设置 token；或自托管 |

---

## AI 使用建议

- **执行环境**：`npm install`、`npm run build` 在终端中执行；Windows 下 `npm` 实为 `npm.cmd`，脚本里写 `cmd /c npm run build` 更稳；装包和大构建放后台运行，输出重定向到文件再分段读。
- **先探测版本**：`npm ls cesium`（未安装时 `npm view cesium version`）。本技能按 1.146.0 编写：该版本依赖 `@cesium/core@^0.1.0`，数学/几何/时间/工具类已拆到 `@cesium/core`，低于 1.146 的工程不要照搬这条迁移建议。
- **验证产物**：`npm run build` 通过后用 `npx serve dist` 或 `python -m http.server 5173 -d dist` 起静态服务，用 `curl.exe -I` 检查 `http://localhost:5173/Cesium.js` 与 `.../Cesium/Widgets/widgets.css` 返回 200（404 或 text/html 说明资源没拷贝）；AI 助手通常看不到浏览器画面，把 URL 和预期画面交给用户，环境支持读图时用截图核对。
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
