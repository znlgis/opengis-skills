---
name: openlayers
description: OpenLayers 是高性能、功能丰富的开源 Web 地图 JavaScript 库，支持几乎所有主流地图服务（XYZ/WMS/WMTS/WFS/Vector Tiles/GeoJSON），提供完整的矢量绘制、样式与交互能力，是 Web 二维 GIS 的事实标准之一。
tags:
  - javascript
  - web
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

---

## AI 使用建议

### 推荐工作流

1. **创建 Map**：`new Map({ target, layers, view })` → 设置投影和初始中心
2. **添加底图**：`TileLayer` + `OSM`/`XYZ`/`TileWMS` Source
3. **加载矢量数据**：`VectorLayer` + `VectorSource` + `GeoJSON`/`MVT` Format
4. **应用样式**：使用 `Style` 函数按属性动态渲染
5. **添加交互**：`Draw`/`Modify`/`Select`/`Snap` Interaction
6. **性能优化**：`declutter` 避让标注、`renderMode: 'image'` 静态图层

### 关键注意事项

- **投影一致**：经纬度需 `fromLonLat()` 转为 EPSG:3857；自定义投影需注册 proj4
- **WMS 参数**：`LAYERS` 参数需使用完整名称（如 `workspace:layer`），检查 CORS
- **矢量瓦片字段**：MVT 格式需设置 `featureClass: Feature` 保留属性
- **样式缓存**：使用函数式 Style 时，缓存 Style 实例避免重复创建
- **批量添加**：使用 `addFeatures([])` 而非循环 `addFeature`，显著提升性能

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
