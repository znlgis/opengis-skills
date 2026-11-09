---
name: openlayers
description: "Use when adding interactive 2D maps to web apps with npm ol 10.11.0 — Map/View, fromLonLat to EPSG:3857, WMS/WMTS/XYZ sources, MVT with featureClass, Draw/Modify/Snap interactions, or debugging blank layers (missing setStyle), offset centers and ol/... module-not-found errors."
license: MIT
metadata:
  category: gis
  tags: "javascript, web, 2d, map, wms, wmts, vector-tiles, geojson, drawing"
---

> **项目地址：** <https://github.com/openlayers/openlayers>
>
> **官方文档：** <https://openlayers.org/doc/>
>
> **API 参考：** <https://openlayers.org/en/latest/apidoc/>
>
> **示例：** <https://openlayers.org/en/latest/examples/>
>
> **最新版本：** 10.11.0（截至 2026-11，[npm `ol`](https://www.npmjs.com/package/ol) 与 [GitHub Release](https://github.com/openlayers/openlayers/releases) 一致）
>
> **许可证：** BSD-2-Clause

## 概述

OpenLayers（OL）特性：

- 多源底图：OSM、Bing、XYZ、WMS、WMTS、ArcGIS REST
- 矢量数据：GeoJSON、KML、GPX、TopoJSON、GML、MVT
- 投影：内置 EPSG:3857/4326，与 proj4 集成支持任意投影
- 矢量瓦片（MVT）原生支持
- 强大的样式与交互（Draw/Modify/Select/Snap）
- WebGL 渲染（点云、海量点）

---

## 安装

```bash
npm install ol
```

```js
import 'ol/ol.css';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import TileLayer from 'ol/layer/Tile.js';
import OSM from 'ol/source/OSM.js';

const map = new Map({
  target: 'map',
  layers: [new TileLayer({ source: new OSM() })],
  view: new View({ center: [12968000, 4863000], zoom: 10 })  // EPSG:3857
});
```

---

## 核心概念

| 类 | 作用 |
|----|------|
| `Map` | 顶层容器 |
| `View` | 视图（投影、中心、缩放、旋转） |
| `Layer` | 图层 |
| `Source` | 数据源 |
| `Feature` / `Geometry` | 矢量要素与几何 |
| `Style` | 样式 |
| `Interaction` | 交互 |

---

## 图层与数据源

### 栅格底图

```js
import XYZ from 'ol/source/XYZ.js';
import TileWMS from 'ol/source/TileWMS.js';

new TileLayer({ source: new XYZ({
  url: 'https://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}'
}) });

new TileLayer({ source: new TileWMS({
  url: 'http://localhost:8080/geoserver/wms',
  params: { LAYERS: 'topp:states', TILED: true }
}) });
```

### 矢量图层（GeoJSON）

```js
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import GeoJSON from 'ol/format/GeoJSON.js';

map.addLayer(new VectorLayer({
  source: new VectorSource({
    url: '/data/poi.geojson',
    format: new GeoJSON()
  })
}));
```

### 矢量瓦片（MVT）

```js
import VectorTileLayer from 'ol/layer/VectorTile.js';
import VectorTileSource from 'ol/source/VectorTile.js';
import MVT from 'ol/format/MVT.js';

new VectorTileLayer({
  declutter: true,
  source: new VectorTileSource({
    format: new MVT(),
    url: 'https://server/tiles/{z}/{x}/{y}.pbf'
  })
});
```

---

## 样式

```js
import { Style, Fill, Stroke, Circle, Text } from 'ol/style.js';

const style = new Style({
  fill: new Fill({ color: 'rgba(255,0,0,0.3)' }),
  stroke: new Stroke({ color: '#f00', width: 2 }),
  image: new Circle({ radius: 6, fill: new Fill({ color: '#f00' }) })
});

layer.setStyle(feature => new Style({
  fill: new Fill({ color: feature.get('pop') > 1e7 ? '#f00' : '#0a0' }),
  text: new Text({ text: feature.get('name'), font: '12px sans-serif' })
}));
```

---

## 投影

```js
import { fromLonLat, toLonLat, transform } from 'ol/proj.js';
import proj4 from 'proj4';
import { register } from 'ol/proj/proj4.js';

map.getView().setCenter(fromLonLat([116.397, 39.908]));

proj4.defs('EPSG:4490', '+proj=longlat +ellps=GRS80 +no_defs');
register(proj4);
```

---

## 交互（Draw / Modify / Select / Snap）

```js
import Draw from 'ol/interaction/Draw.js';
import Modify from 'ol/interaction/Modify.js';
import Select from 'ol/interaction/Select.js';
import Snap from 'ol/interaction/Snap.js';

const source = new VectorSource();
map.addLayer(new VectorLayer({ source }));

const draw = new Draw({ source, type: 'Polygon' });
map.addInteraction(draw);
draw.on('drawend', e => console.log(e.feature.getGeometry().getCoordinates()));

map.addInteraction(new Modify({ source }));
map.addInteraction(new Snap({ source }));

const select = new Select();
map.addInteraction(select);
select.on('select', e => console.log(e.selected));
```

---

## 量测

```js
import { getLength, getArea } from 'ol/sphere.js';
draw.on('drawend', e => console.log(getLength(e.feature.getGeometry())));
```

---

## Overlay 弹窗

```js
import Overlay from 'ol/Overlay.js';

const popup = new Overlay({
  element: document.getElementById('popup'),
  positioning: 'bottom-center', offset: [0, -10]
});
map.addOverlay(popup);

map.on('singleclick', e => {
  map.forEachFeatureAtPixel(e.pixel, f => {
    popup.setPosition(e.coordinate);
    document.getElementById('popup').innerText = f.get('name');
  });
});
```

---

## 集群

```js
import Cluster from 'ol/source/Cluster.js';
const clusterSource = new Cluster({ distance: 40, source: pointSource });
new VectorLayer({ source: clusterSource, style: clusterStyleFn });
```

---

## 典型工作流

以「底图 + GeoJSON 行政区 + 绘制编辑」为例，输入 `public/data/districts.geojson`，输出可浏览、可勾绘的面图层页面。

1. **创建 Map**：`new Map({ target, layers, view })` → `new View({ center: fromLonLat([116.39, 39.9]), zoom: 10 })`
2. **添加底图**：`TileLayer` + `OSM`/`XYZ`/`TileWMS` Source
3. **加载矢量数据**：`VectorLayer` + `VectorSource` + `GeoJSON` Format
4. **应用样式**：`layer.setStyle(fn)` 按属性动态渲染（不设样式矢量图层不渲染）
5. **添加交互**：`Draw`/`Modify`/`Select`/`Snap` Interaction
6. **导出结果**：`geojson.writeFeatures(source.getFeatures())` 落盘
7. **性能优化**：`declutter` 避让标注、`renderMode: 'image'` 静态图层

```js
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import TileLayer from 'ol/layer/Tile.js';
import OSM from 'ol/source/OSM.js';
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import { fromLonLat } from 'ol/proj.js';
import { Style, Fill, Stroke, Text } from 'ol/style.js';
import Draw from 'ol/interaction/Draw.js';

// 显式 dataProjection / featureProjection，避免 4326 数据直接落在 3857 视图上偏移
const geojson = new GeoJSON({
  dataProjection: 'EPSG:4326',
  featureProjection: 'EPSG:3857'
});

const vectorLayer = new VectorLayer({
  source: new VectorSource({
    url: '/data/districts.geojson',
    format: geojson
  }),
  style: (feature) => new Style({
    fill: new Fill({ color: 'rgba(70,130,180,0.25)' }),
    stroke: new Stroke({ color: '#4682b4', width: 1.5 }),
    text: new Text({
      text: feature.get('name'),
      font: '12px sans-serif',
      overflow: true
    })
  })
});

const map = new Map({
  target: 'map',
  layers: [new TileLayer({ source: new OSM() }), vectorLayer],
  view: new View({ center: fromLonLat([116.39, 39.9]), zoom: 9 })
});

// 直接在同一个矢量图层上绘制；画完把全部要素序列化回 EPSG:4326
const drawSource = vectorLayer.getSource();
map.addInteraction(new Draw({ source: drawSource, type: 'Polygon' }));

drawSource.on('addfeature', () => {
  const text = geojson.writeFeatures(drawSource.getFeatures(), {
    dataProjection: 'EPSG:4326',
    featureProjection: 'EPSG:3857'
  });
  console.log(text);           // 可直接提交给后端保存
});
```

**验证产物**：`npm run build` 后打开页面，底图与行政区面同时显示；再画一个多边形，控制台应输出对应 GeoJSON（坐标已转回 EPSG:4326）。

---

## 性能优化

1. 大量要素 → `WebGLPointsLayer` 或 MVT
2. 不要每帧重新创建 Style，缓存样式实例
3. 添加要素用 `addFeatures([])` 而非循环 `addFeature`
4. `declutter: true` 自动避让标注
5. `renderMode: 'image'` 用于不变的矢量图层

---

## 常见问题

| 报错 / 现象 | 原因 | 处置 |
|------|------|------|
| 报错 `Uncaught AssertionError: Assertion failed: The view center is not defined` | `new View()` 未给 `center`，或给的是 `undefined`（坐标变量还没算出来） | 构造 View 时显式传 `center: fromLonLat([lng, lat])` 与 `zoom`；异步取数时等数据到了再 `view.setCenter()` |
| 报错 `Assertion failed: Expected a list of style instances` | `setStyle()` 收到单个 `Style` 之外的非法值（数组里混入 `null`/`undefined`，或传了函数却返回非 Style） | 传 `new Style({...})` 或其数组；用样式函数时确保每个分支都返回 Style |
| 中心点偏移 / 图层跑到别处 | 经纬度直接当投影坐标用，未做 `EPSG:4326 → EPSG:3857` 转换 | 所有经纬度经 `fromLonLat()` 转换；自定义投影先 `register(proj4)`；用 `map.getView().getCenter()` 回读核对 |
| 矢量图层完全不显示 | 矢量图层未设置样式时默认不渲染 | 为图层 `setStyle(new Style({...}))`，或在构造时传 `style` |
| WMS 返回空白或 404 | `LAYERS` 用了图层短名而非全名、`SRS`/`CRS` 与请求版本不匹配，或服务端未放行 CORS | 用 `GetCapabilities` 里的全名填 `LAYERS`；WMS 1.3.0 用 `CRS`、1.1.1 用 `SRS`；服务端补 CORS 头 |
| MVT 要素取不到属性 | MVT 源未指定要素类，属性被丢弃 | 用 `new MVT({ featureClass: Feature })`，再通过 `feature.getProperties()` 读取 |
| 文字标注不显示 / 字体不生效 | 字体尚未加载就创建了 Text 样式，或字体族名与服务端不一致 | 先用 `document.fonts.load()`/CSS 加载字体再建样式；确认 `font` 字符串里的字体族名可用 |
| 点击拾取不到要素 | 要素过小或触摸设备命中容差不足 | `map.forEachFeatureAtPixel(evt.pixel, cb, { hitTolerance: 5 })` 加大容差 |
| 运行时报 `ol/...` 模块找不到（如 `Failed to resolve module specifier "ol/Map.js"`） | 直接用 `<script>` 引 ESM 源码，或打包器未按 ESM 解析 | 用 npm 的 `ol` 包并配置打包器；不想打包就用官方全量构建 `dist/ol.js` |

---

## AI 使用建议

- **执行环境**：`npm install`、`npm run build` 在终端中执行；Windows 下 `npm` 是 `npm.cmd`，长构建放后台运行并把输出落盘再读。
- **先探测版本**：`npm ls ol`（未装则 `npm view ol version`）；本技能按 10.11.0 编写，只使用 `ol/Map.js`、`ol/layer/Tile.js` 等 ESM 子路径，旧版 `ol.source.*` 全量命名空间写法不要混用。
- **验证产物**：`npm run build` 后用 `npx serve dist`（或 `python -m http.server 5173 -d dist`）起静态服务，`curl.exe -I http://localhost:5173/` 与打包出的 `assets/*.js` 应为 200；AI 助手通常看不到浏览器画面，请用户看页面与控制台，环境支持读图时用截图核对。
- **投影**：经纬度必须 `fromLonLat()` 转 EPSG:3857，自定义投影先 `register(proj4)`；否则中心点偏移或图层不显示。
- **图层样式**：矢量图层不设样式默认不渲染，务必 `setStyle()`；MVT 源要用 `MVT({ featureClass: Feature })` 才能保留属性。
- **常见症状**：WMS 空白先查 CORS、`LAYERS` 全名与 `SRS`；`ol/...` 模块找不到说明打包器没按 ESM 解析；容器尺寸变化后调用 `map.updateSize()`。
- **安全与权限**：装包、起 dev server、对外暴露端口前先征得用户同意；内网 WMS 地址与凭据不要写进示例。

## 相关技能

- **cesiumjs** — 三维地球与地图库：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)
- **geoserver** — 地图服务发布：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **postgis** — 空间数据库（MVT 数据源）：[../postgis/SKILL.md](../postgis/SKILL.md)
- **mapsui** — .NET 跨平台地图组件：[../mapsui/SKILL.md](../mapsui/SKILL.md)

## 参考资源

- 文档：<https://openlayers.org/doc/>
- 示例：<https://openlayers.org/en/latest/examples/>
- API：<https://openlayers.org/en/latest/apidoc/>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/openlayers/>
