---
name: openlayers
description: "Use when adding interactive 2D maps to web apps with npm ol 10.11.0 — Map/View, fromLonLat to EPSG:3857, WMS/WMTS/XYZ sources, MVT with featureClass, Draw/Modify/Snap interactions, or debugging blank layers (missing setStyle), offset centers and ol/... module-not-found errors."
tags:
  - javascript
  - web
  - 2d
  - map
  - wms
  - wmts
  - vector-tiles
  - geojson
  - drawing
---

> **项目地址：** <https://github.com/openlayers/openlayers>
>
> **官方文档：** <https://openlayers.org/doc/>
>
> **API 参考：** <https://openlayers.org/en/latest/apidoc/>
>
> **示例：** <https://openlayers.org/en/latest/examples/>
>
> **最新版本：** 10.11.0（截至2026-10，npm `ol`）
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

1. **创建 Map**：`new Map({ target, layers, view })` → 设置投影和初始中心
2. **添加底图**：`TileLayer` + `OSM`/`XYZ`/`TileWMS` Source
3. **加载矢量数据**：`VectorLayer` + `VectorSource` + `GeoJSON`/`MVT` Format
4. **应用样式**：使用 `Style` 函数按属性动态渲染
5. **添加交互**：`Draw`/`Modify`/`Select`/`Snap` Interaction
6. **性能优化**：`declutter` 避让标注、`renderMode: 'image'` 静态图层

---

## 性能优化

1. 大量要素 → `WebGLPointsLayer` 或 MVT
2. 不要每帧重新创建 Style，缓存样式实例
3. 添加要素用 `addFeatures([])` 而非循环 `addFeature`
4. `declutter: true` 自动避让标注
5. `renderMode: 'image'` 用于不变的矢量图层

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 中心点偏移 | 投影未对齐：`fromLonLat()` 转换 |
| WMS 不显示 | 检查 CORS、`LAYERS` 名、`SRS` 参数 |
| 字体未生效 | 加载字体后再创建 Text 样式 |
| MVT 字段缺失 | 使用 `MVT({ featureClass: Feature })` |
| 矢量图层完全不显示 | 图层未设置样式时默认不渲染，需为图层 `setStyle()` |
| 点击拾取不到要素 | `map.forEachFeatureAtPixel` 设置 `hitTolerance`（触摸设备/细小要素场景） |
| 运行时报 `ol/...` 模块找不到 | 确认使用 npm 包 `ol` 并配置打包器（或改用官方全量构建 `dist/ol.js`） |

---

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("openlayers")` 加载（用户也可输入 `/openlayers`）；本技能无 reference 子目录，示例代码直接写进会话工作区工程，技能目录只读。
- **执行环境**：`npm install`、`npm run build` 交给 `pwsh`；Windows 下 `npm` 是 `npm.cmd`，长构建用后台作业并把输出落盘再读。
- **先探测版本**：`npm ls ol`（未装则 `npm view ol version`）；本技能按 10.11.0 编写，只使用 `ol/Map.js`、`ol/layer/Tile.js` 等 ESM 子路径，旧版 `ol.source.*` 全量命名空间写法不要混用。
- **验证产物**：`npm run build` 后用 `npx serve dist`（或 `python -m http.server 5173 -d dist`）起静态服务，`curl.exe -I http://localhost:5173/` 与打包出的 `assets/*.js` 应为 200；DSH 不打开浏览器，请用户看页面与控制台，有截图再用 `read_image`。
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
