---
name: geoserver
description: "Use when deploying GeoServer 3.0.x to publish WMS/WFS/WMTS/WCS/MVT, or configuring SLD/CSS styles, RBAC security, and GeoWebCache seeding. Covers geoserver-3.0.2-bin.zip, docker.osgeo.org/geoserver:3.0.2 on Java 17/21, /rest/about/version.json, blank GetMap from wrong native bounds, and Shapefile charset mojibake."
tags:
  - java
  - server
  - wms
  - wfs
  - wmts
  - wcs
  - wps
  - ogc
  - map
  - web
---

> **项目地址：** <https://github.com/geoserver/geoserver>
>
> **官方文档：** <https://docs.geoserver.org/latest/en/user/>
>
> **下载：** <https://geoserver.org/release/stable/>
>
> **最新版本：** 3.0.2（2026-10-19，安全修复版，生产应优先升级；[官方下载](https://geoserver.org/release/stable/)）
>
> **运行环境：** Java 17 或 21；3.0.2 内含 GeoTools 35.2、GeoWebCache 2.0.2
>
> **许可证：** GPL-2.0

> 该 SKILL 关注 GeoServer 服务端运维与配置；REST API 自动化管理资源请配合 `gis/geoserver-rest-api`。

## 概述

GeoServer 提供：

- **OGC 服务**：WMS、WMTS、WFS、WCS、WPS、CSW
- **矢量瓦片**：Mapbox Vector Tiles（pbf）
- **样式**：SLD、CSS、YSLD、MBStyle
- **数据源**：PostGIS、Shapefile、GeoPackage、Oracle、SQL Server、ArcSDE、GeoTIFF、ImageMosaic、JP2、NetCDF
- **安全**：基于角色的访问控制（RBAC）
- **管理**：Web UI（端口 8080） + REST API

---

## 安装部署

### 前置：JDK

3.0.x 需要 **Java 17 或 21**；先 `java -version` 确认（低于 17 的 JVM 无法启动 3.x 分发包）。

### 二进制

```bash
curl -fLO https://sourceforge.net/projects/geoserver/files/GeoServer/3.0.2/geoserver-3.0.2-bin.zip
unzip geoserver-3.0.2-bin.zip && cd geoserver-3.0.2
sh bin/startup.sh         # http://localhost:8080/geoserver  (admin/geoserver)
```

### Docker

```bash
docker run --name gs -p 8080:8080 \
  -e SKIP_DEMO_DATA=true \
  -e EXTRA_JAVA_OPTS="-Xms512m -Xmx2g" \
  -v $PWD/data:/opt/geoserver_data \
  docker.osgeo.org/geoserver:3.0.2
```

### 数据目录

```text
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

```text
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

## 典型工作流

1. **部署 GeoServer**：优先使用 Docker 镜像 `docker.osgeo.org/geoserver:3.0.2`（安全修复版；从旧版本升级前先备份数据目录）
2. **创建 Workspace**：为每个项目创建独立工作空间实现命名隔离
3. **添加数据存储**：根据数据类型选择 PostGIS（矢量）、Shapefile（文件矢量）、GeoTIFF（栅格）
4. **发布图层**：设置 SRS（坐标参考系）、计算 Native Bounds、配置样式
5. **验证服务**：通过 Layer Preview 或直接构造 WMS/WFS 请求测试
6. **优化性能**：启用 GeoWebCache 预切片、PostGIS 建空间索引、调整 JVM 参数

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

## DeepSeek Harness 使用建议

- **加载与引用**：`skill("geoserver")` 加载；技能目录只读，SLD、脚本、日志等产物写到会话工作区。
- **执行环境**：命令交给 dsh 的 shell 工具（Windows 用 `pwsh`）；`wget`/`unzip` 换成 `curl.exe -LO` 与 `Expand-Archive`，`$PWD` 换成 `(Get-Location)`。
- **先探测版本**：`curl -s -u admin:geoserver http://localhost:8080/geoserver/rest/about/version.json`（无 jq 时管道给 `python -m json.tool`），核对 GeoServer、GeoWebCache 与 JVM；`java -version` 必须是 17 或 21，否则 3.0.2 包直接启动失败。
- **验证产物**：发布后用 `curl -s -o out.png -w "%{http_code} %{size_download}\n" "http://localhost:8080/geoserver/my_ws/wms?service=WMS&version=1.1.0&request=GetMap&layers=my_ws:poi&srs=EPSG:4326&bbox=...&width=512&height=512&format=image/png"`，要 200 且字节数大于 0；再拉一次 `GetCapabilities` 确认图层已注册，不要只凭 UI 回显。
- **写后回读**：REST 建 workspace/store/layer 或上传 SLD 后，用同路径 GET 回读；`?recurse=true` 删除后再 GET 应得 404。
- **安全与权限**：`admin:geoserver` 凭据不要回显到命令输出或报告里（用环境变量传入）；重启容器、改 `-Xmx`、删除 workspace、清 GWC 缓存前先征得用户同意。
- **常见误操作**：WMS 返回空白图先查 native bounds 与 SRS 是否对不上；Shapefile 中文乱码改 Store 的 `charset`；seed 大范围瓦片会撑爆磁盘，先小 zoom 范围试。

## 相关技能

- **geoserver-rest-api** — REST API 自动化管理：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **geoserver-cloud** — 云原生微服务版本：[../geoserver-cloud/SKILL.md](../geoserver-cloud/SKILL.md)
- **postgis** — 空间数据库（GeoServer 最常见数据源）：[../postgis/SKILL.md](../postgis/SKILL.md)
- **geotools** — GeoServer 底层 Java GIS 库：[../geotools/SKILL.md](../geotools/SKILL.md)

## 参考资源

- 文档：<https://docs.geoserver.org/latest/en/user/>
- SLD Cookbook：<https://docs.geoserver.org/latest/en/user/styling/sld/cookbook/>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/geoserver/>
