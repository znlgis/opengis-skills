---
name: mapserver
description: "Use when publishing spatial data as OGC web services (WMS, WFS, WCS) from a mapfile, styling layers with SLD, or deploying the mapserv CGI/FastCGI. MapServer: the C-based OSGeo open-source map server for the web."
tags:
  - c
  - server
  - wms
  - wfs
  - wcs
  - ogc
  - mapfile
  - cgi
  - web
---

> **项目地址：** <https://github.com/MapServer/MapServer>
>
> **官方文档：** <https://mapserver.org/>
>
> **最新版本：** 8.6.6（rel-8-6-6，[发布记录](https://github.com/MapServer/MapServer/releases)）
>
> **许可证：** MIT

> 该 SKILL 关注 MapServer 服务端发布与 mapfile 配置；数据源准备配合 `gis/gdal`（ogr2ogr）、空间数据库配合 `gis/postgis`。

## 概述

MapServer 是 OSGeo 维护的开源平台，用于把空间数据发布为 Web 地图与 OGC 服务。它以 C 语言实现，核心是一个读取 mapfile 的 `mapserv` CGI 可执行程序。它定位为"地图服务引擎"而非完整 GIS，侧重高效渲染与标准协议输出。

- **OGC 服务**：WMS、WFS、WCS、OGC API Features、SOS
- **渲染**：地图合成、图层叠加、要素标注、栅格与矢量混合
- **样式**：CLASS/STYLE 内置符号体系，外部 SLD 绑定
- **数据源**：Shapefile、PostGIS、GeoPackage、OGR 支持的格式、GeoTIFF 等栅格
- **扩展**：MapScript（Python/PHP/Java/.NET）脚本化、MapCache 瓦片缓存、TinyOWS WFS-T

---

## 环境准备

### 方式一：Debian/Ubuntu 软件包

```bash
sudo apt update
sudo apt install -y cgi-mapserver mapserver-bin
# 可选：Apache 集成
sudo apt install -y apache2 libapache2-mod-fcgid
sudo a2enmod authnz_fcgi cgi
sudo systemctl restart apache2
```

`cgi-mapserver` 提供 CGI 可执行程序，`mapserver-bin` 提供 `mapserv`、`map2img`、`shp2img`、`legend` 等命令行工具。

### 方式二：源码编译（CMake）

MapServer 8.x 需要支持 C++11/C99 的编译器，8.4.0 起要求 CMake 3.16+。先装依赖（GDAL、PROJ、libpng、FreeType、zlib、libcurl 为常用项）：

```bash
sudo apt install -y build-essential cmake libgdal-dev libproj-dev \
  libpng-dev libfreetype6-dev zlib1g-dev libcurl4-openssl-dev

tar -zxvf mapserver-8.6.6.tar.gz
cd mapserver-8.6.6 && mkdir build && cd build
cmake -DCMAKE_INSTALL_PREFIX=/opt \
      -DWITH_CURL=ON -DWITH_CLIENT_WFS=ON -DWITH_CLIENT_WMS=ON \
      -DWITH_PYTHON=ON ..
make
sudo make install
```

### 方式三：Windows（OSGeo4W）

使用 OSGeo4W 安装器，勾选 `mapserver` 组件即可获得 `mapserv.exe` 与全部依赖。

### 验证

```bash
mapserv -v
# 输出应包含 MapServer version 8.6.6 与 SUPPORTS=WMS_SERVER,WMS_CLIENT,WFS_SERVER...
```

若缺少某个服务，对应 `SUPPORTS=` 字段不会出现，说明编译时未启用该库。

---

## 核心 API / 命令

### mapfile 对象层次

mapfile 必须以 `MAP` 开头，扩展名为 `.map`，不区分大小写，从顶部到底部依次读取（越靠上的图层越先绘制）。字符串含特殊字符或关键字时必须加引号。

| 对象 | 作用 |
|------|------|
| `MAP` | 根对象，定义名称、尺寸、范围、颜色、输出格式 |
| `LAYER` | 数据 + 样式的组合，按 `TYPE`（POINT/LINE/POLYGON/RASTER）区分 |
| `CLASS` | 图层内的一类要素及其样式与过滤条件 |
| `STYLE` | 具体绘制样式（颜色、线宽、符号、填充） |
| `LABEL` | 要素注记的文字与排版 |
| `WEB` | 服务元数据与模板，承载 `wms_*`/`wfs_*` 关键字 |
| `PROJECTION` | 定义对象坐标参考系 |
| `SYMBOL`/`OUTPUTFORMAT`/`LEGEND` | 符号库、输出格式、图例 |

### 最小 mapfile 示例

```mapfile
MAP
  NAME "demo"
  SIZE 600 400
  EXTENT -180 -90 180 90
  UNITS dd
  IMAGECOLOR 255 255 255
  SHAPEPATH "/data/shp"
  WEB
    METADATA
      "wms_title"          "Demo WMS"
      "wms_onlineresource" "http://localhost/cgi-bin/mapserv?"
      "wms_srs"            "EPSG:4326 EPSG:3857"
      "wms_enable_request" "*"
    END
  END
  LAYER
    NAME "countries"
    TYPE POLYGON
    STATUS ON
    DATA "countries"
    PROJECTION
      "init=epsg:4326"
    END
    CLASS
      NAME "default"
      STYLE
        COLOR 200 220 240
        OUTLINECOLOR 60 60 60
        WIDTH 1
      END
    END
  END
END
```

### mapserv CGI 请求参数

服务通过 URL 访问 `mapserv` 并传入 `map=` 指向 mapfile：

```text
http://my.host.com/cgi-bin/mapserv?map=/path/to/demo.map&SERVICE=WMS&...
```

| 参数 | 说明 |
|------|------|
| `map=` | mapfile 绝对路径（生产环境建议用 `MS_MAP_PATTERN` 或包装脚本隐藏） |
| `SERVICE` | `WMS` / `WFS` / `WCS`，必填 |
| `VERSION` | 如 `1.1.1`、`1.3.0`（WMS）、`2.0.0`（WFS） |
| `REQUEST` | `GetCapabilities` / `GetMap` / `GetFeature` / `GetFeatureInfo` |
| `LAYERS` / `TYPENAMES` | 请求的图层（WMS 用 `LAYERS`，WFS 2.0 用 `TYPENAMES`） |

### WMS 请求示例

```text
# GetCapabilities
http://my.host.com/cgi-bin/mapserv?map=/path/demo.map&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetCapabilities

# GetMap
http://my.host.com/cgi-bin/mapserv?map=/path/demo.map&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=countries&STYLES=&SRS=EPSG:4326&BBOX=-180,-90,180,90&WIDTH=600&HEIGHT=400&FORMAT=image/png
```

WMS 1.3.0 使用 `CRS` 取代 `SRS`，并对 EPSG 4000–5000 区段采用轴序调整。

### WFS 请求示例

```text
# WFS 2.0 GetFeature
http://my.host.com/cgi-bin/mapserv?map=/path/demo.map&SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=countries&COUNT=100&OUTPUTFORMAT=application/json
```

WFS 需要图层 `TYPE` 为 POINT/LINE/POLYGON 且 `NAME` 以字母开头。MapServer 提供只读 WFS，不支持事务（WFS-T），需要写入时使用 TinyOWS 或 GeoServer。

### SLD 绑定

在 LAYER 中通过 `SLD` 关键字绑定样式文档；服务端也可通过 `SLD=` 请求参数在运行时传入：

```mapfile
LAYER
  NAME "countries"
  TYPE POLYGON
  DATA "countries"
  CLASSITEM "pop_est"
  SLD "file:///data/sld/countries.sld"
END
```

```text
# 运行时传入 SLD
http://my.host.com/cgi-bin/mapserv?map=/path/demo.map&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=countries&STYLES=&SLD=http://my.host.com/sld/countries.sld&...
```

### 数据准备（ogr2ogr）

Shapefile、GeoPackage 等矢量数据可用 GDAL 的 `ogr2ogr` 转换与裁剪，再由 LAYER 的 `DATA` 引用：

```bash
# 转 GeoPackage 并指定目标坐标系
ogr2ogr -f GPKG countries.gpkg source.shp -t_srs EPSG:4326

# 按范围裁剪
ogr2ogr -f GPKG clip.gpkg countries.gpkg -clipsrc 100 20 130 50
```

---

## 典型工作流

### 工作流一：发布 WMS 服务

1. 准备数据：用 `ogr2ogr` 把数据转为 GeoPackage 或放入 PostGIS。
2. 编写 mapfile：定义 `MAP`（`SIZE`/`EXTENT`/`IMAGECOLOR`）与 `LAYER`。
3. 在 `WEB/METADATA` 写入 `wms_title`、`wms_onlineresource`、`wms_srs`、`wms_enable_request`。
4. 部署 `mapserv` 到 CGI 目录，或用 FastCGI 常驻进程。
5. 验证 `GetCapabilities` 能返回 XML，再用 `GetMap` 检查图像输出。

### 工作流二：WFS 要素查询

1. 确认图层 `NAME` 以字母开头且 `TYPE` 为矢量类型。
2. 在 `WEB/METADATA` 写入 `wfs_title`、`wfs_onlineresource`、`wfs_enable_request`、`wfs_srs`。
3. 图层级补充 `wfs_title`、`wfs_srs`、`gml_featureid`；如需输出属性，设置 `gml_include_items`（8.x 默认不暴露任何属性）。
4. 用 `GetFeature` 请求并指定 `OUTPUTFORMAT`（如 `application/json`）取回要素。
5. 用 `GetCapabilities` 核对服务声明的图层与格式是否与预期一致。

### 工作流三：SLD 样式绑定

1. 从 SLD 规范或样式库编写 SLD 文档，`NamedLayer/Name` 与图层 `NAME` 对应。
2. 在 LAYER 中设置 `CLASSITEM`（SLD 过滤所依赖的字段）与 `SLD` 指向样式文件。
3. 或用请求参数 `SLD=` 在运行时覆盖样式，便于调试。
4. 通过 `GetMap` 或 `GetLegendGraphic` 检查渲染与图例效果。
5. 确认无误后将 SLD 固化到 mapfile 或作为受控资源发布。

---

## 最佳实践

- **用 FastCGI 而非纯 CGI**：FastCGI 常驻进程避免每次请求重复初始化，显著降低延迟。
- **锁定 mapfile 路径**：设置 `MS_MAP_PATTERN`、`MS_MAP_NO_PATH` 或包装脚本，避免任意 `map=` 路径被利用。
- **显式声明 `wms_enable_request` / `wfs_enable_request`**：不设置时不会启用任何请求，用 `!` 前缀可禁用单个请求。
- **显式设置 `gml_include_items`**：MapServer 8.x 默认不输出要素属性，需按需开放字段。
- **PostGIS 图层建空间索引**，并在 mapfile 中正确设置 `PROJECTION` 与 `EXTENT`。
- **图像格式按需选择**：`image/png` 适合线面，`image/jpeg` 适合影像，`image/png; mode=8bit` 可减小体积。
- **配合 MapCache** 缓存瓦片，或在前端做预切片以承接高并发。
- **mapfile 保持 UTF-8 编码**，中文注记需指定支持中文的字体。

---

## 常见问题

| 问题 | 排查与解决 |
|------|-----------|
| 访问 mapserv 返回 "No query information to decode" | 属正常提示，说明 CGI 可执行；缺少请求参数，补上 `SERVICE`/`REQUEST` 等 |
| 浏览器 403 Forbidden | Web 用户无执行权限，执行 `chmod o+x mapserv`，确认 CGI 目录已启用 |
| 500 Internal Server Error | 查看 Apache `error.log`；多为 mapfile 语法错误或 `DATA` 路径不可读 |
| GetMap 返回空白图像 | 检查 `EXTENT` 与请求 `BBOX` 是否匹配、`PROJECTION` 是否与数据一致、图层 `STATUS` 是否为 `ON` |
| WMS 提示未启用请求 | `wms_enable_request` 未设置或未包含该请求类型；设为 `*` 或列出具体请求 |
| GetFeatureInfo 无返回 | 图层缺少 `TEMPLATE`（如 `empty`）或 `wms_include_items` 未配置 |
| WFS 返回结果不含属性字段 | 8.x 默认不暴露属性，设置 `gml_include_items "all"` 或列出字段名 |
| 中文注记显示为方框 | mapfile 需 UTF-8 编码，且 `FONT` 指向包含中文字形的字体集 |
| 图层名不符合 WFS 发布要求 | `NAME` 必须以字母开头，且 `TYPE` 为 POINT/LINE/POLYGON |
| SLD 未生效 | `NamedLayer/Name` 与图层 `NAME` 不匹配，或 `CLASSITEM` 字段名错误 |

---

## 参考资源

- 官方文档：<https://mapserver.org/>
- Unix 编译安装：<https://mapserver.org/installation/unix.html>
- Mapfile 参考：<https://mapserver.org/mapfile/index.html>
- WMS Server：<https://mapserver.org/ogc/wms_server.html>
- WFS Server：<https://mapserver.org/ogc/wfs_server.html>
- 在线示例服务：<https://demo.mapserver.org/>

---

## 相关技能

- **geoserver** — 功能更全的 Java 地图服务器，支持 WFS-T：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **geoserver-rest-api** — GeoServer 资源自动化管理：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **gdal** — ogr2ogr 数据转换与栅格处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **postgis** — 常用矢量数据源：[../postgis/SKILL.md](../postgis/SKILL.md)

---

## AI 使用建议

- **优先用 `mapserv -v` 判断能力**：输出中的 `SUPPORTS=` 列表决定该实例能否提供 WMS/WFS/WCS，遇到服务不生效先查此项。
- **改动前先验证 mapfile 语法**：可用 `map2img` 或 `shp2img` 离线渲染，快速定位语法与数据路径问题，无需经过 Web 服务器。
- **区分"渲染问题"与"协议问题"**：图像空白多属渲染（EXTENT/PROJECTION/STATUS），能力文档缺失多属 `wms_*`/`wfs_*` 元数据配置。
- **不要编造 OGC 参数**：WMS/WFS 请求参数以官方文档为准，WFS 2.0 用 `TYPENAMES`，WMS 1.3.0 用 `CRS`。
- **生产部署优先 FastCGI**，并配置 `MS_MAP_PATTERN` 限制可访问的 mapfile 路径。
