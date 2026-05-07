---
name: geoserver
description: GeoServer 是基于 Java 的开源地图服务器，遵循 OGC 标准（WMS/WMTS/WFS/WCS/WPS），用于发布矢量、栅格、瓦片地图服务，支持 Shapefile、PostGIS、Oracle、GeoTIFF 等数据源，是开源 SDI 的核心组件之一。
---

> **项目地址：** <https://github.com/geoserver/geoserver>
>
> **官方文档：** <https://docs.geoserver.org/latest/en/user/>
>
> **下载：** <https://geoserver.org/release/stable/>
>
> **许可证：** GPL-2.0

> 该 SKILL 关注 GeoServer 服务端运维与配置；REST 自动化管理资源请配合 `gis/geoserver-rest-api`。

## 概述

GeoServer 提供：

- **OGC 服务**：WMS、WMTS、WFS、WCS、WPS、CSW
- **矢量瓦片**：Mapbox Vector Tiles（pbf）
- **样式**：SLD、CSS、YSLD、MBStyle
- **数据源**：PostGIS、Shapefile、GeoPackage、Oracle、SQL Server、ArcSDE、GeoTIFF、ImageMosaic、JP2、NetCDF
- **安全**：基于角色的访问控制（RBAC）
- **管理**：Web UI（端口 8080） + REST API

---

## 部署

### 二进制

```bash
wget https://sourceforge.net/projects/geoserver/files/GeoServer/2.25.0/geoserver-2.25.0-bin.zip
unzip geoserver-2.25.0-bin.zip && cd geoserver-2.25.0
sh bin/startup.sh         # http://localhost:8080/geoserver  (admin/geoserver)
```

### Docker

```bash
docker run --name gs -p 8080:8080 \
  -e SKIP_DEMO_DATA=true \
  -e EXTRA_JAVA_OPTS="-Xms512m -Xmx2g" \
  -v $PWD/data:/opt/geoserver_data \
  docker.osgeo.org/geoserver:2.25.0
```

### 数据目录

```
GEOSERVER_DATA_DIR/
├── workspaces/<ws>/<store>/...
├── styles/
├── layergroups/
├── gwc/
└── security/
```

---

## 核心概念

| 概念 | 说明 |
|------|------|
| Workspace | 命名空间 |
| Store | 数据存储 |
| Layer | 图层（Store 资源 + 样式） |
| Style | 渲染规则（SLD/CSS） |
| LayerGroup | 图层组 |
| GeoWebCache (GWC) | 内置瓦片缓存 |

---

## 发布矢量图层（PostGIS）

1. 创建 Workspace `my_ws`
2. 添加 Store：选 PostGIS，填 host/db/user/pass
3. 发布图层：选表 → 计算原始范围 → 设置 SRS
4. 配置样式（默认 / SLD）
5. Layer Preview

访问 URL：

```
WMS  : /geoserver/my_ws/wms?service=WMS&version=1.1.0&request=GetMap&layers=my_ws:poi&srs=EPSG:4326&bbox=...&width=512&height=512&format=image/png
WMTS : /geoserver/gwc/service/wmts?...&LAYER=my_ws:poi&...
WFS  : /geoserver/my_ws/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=my_ws:poi&outputFormat=application/json
MVT  : /geoserver/gwc/service/wmts?...&FORMAT=application/vnd.mapbox-vector-tile
```

---

## SLD 样式示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
    xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc">
  <NamedLayer>
    <Name>poi</Name>
    <UserStyle><FeatureTypeStyle>
      <Rule>
        <ogc:Filter><ogc:PropertyIsGreaterThan>
          <ogc:PropertyName>pop</ogc:PropertyName>
          <ogc:Literal>1000000</ogc:Literal>
        </ogc:PropertyIsGreaterThan></ogc:Filter>
        <PointSymbolizer>
          <Graphic><Mark><WellKnownName>circle</WellKnownName>
            <Fill><CssParameter name="fill">#ff0000</CssParameter></Fill>
          </Mark><Size>10</Size></Graphic>
        </PointSymbolizer>
      </Rule>
    </FeatureTypeStyle></UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
```

---

## 栅格

- **GeoTIFF**：UI → Coverage Store → Add new → GeoTIFF
- **ImageMosaic**：目录中放多个 GeoTIFF（同投影），创建 Mosaic store；推荐配合 `gdaladdo` 建金字塔

---

## GeoWebCache

UI：Tile Caching → Tile Layers → Seed/Truncate

```bash
curl -u admin:geoserver -XPOST \
  "http://localhost:8080/geoserver/gwc/rest/seed/my_ws:poi.json" \
  -H "Content-Type: application/json" \
  -d '{"seedRequest":{"name":"my_ws:poi","srs":{"number":4326},"zoomStart":0,"zoomStop":10,"format":"image/png","type":"seed","threadCount":4}}'
```

---

## 常用扩展

| 扩展 | 用途 |
|------|------|
| `vector-tiles` | MVT 输出 |
| `css` | CSS 样式 |
| `wps` | 处理服务 |
| `monitor` | 请求监控 |
| `control-flow` | 限流 |
| `printing` | 打印 |
| `csw` | 元数据 |

放入 `webapps/geoserver/WEB-INF/lib/` 重启即可。

---

## 性能优化

1. JVM：`-Xms2g -Xmx4g -XX:+UseG1GC`
2. PostGIS 必建空间索引
3. 启用 GeoWebCache 预切片
4. `control-flow` 限流：`ows.global=10`
5. 正确设置图层 native bbox
6. 关闭未用服务
7. ImageMosaic 用金字塔与索引

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 启动慢 / OOM | 增加 `-Xmx`，关闭 demo 数据 |
| Shapefile 中文乱码 | Store 设 `charset=UTF-8` 或 `GBK` |
| 图层范围空白 | 重新计算 native bounds |
| WFS-T 403 | Data 规则允许 `w` 权限 |
| 跨域 | 配置 CORS 过滤器 |

---

## 参考资源

- 文档：<https://docs.geoserver.org/latest/en/user/>
- SLD Cookbook：<https://docs.geoserver.org/latest/en/user/styling/sld/cookbook/>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/geoserver/>
