---
name: gis-skills
description: GIS（地理信息系统）技能分类索引，覆盖空间数据处理、地图服务、几何运算、Web 可视化等领域共 23 个开源工具，按需加载即可获得 GDAL、QGIS、GeoServer、PostGIS、JTS 等工具的精准 AI 辅助。
tags:
  - gis
  - geospatial
  - mapping
  - spatial-analysis
  - vector
  - raster
  - server
  - webmapping
---

> **父级入口：** [../SKILL.md](../SKILL.md) — 全仓 56 技能总索引

## 概述

本分类涵盖 **23 个 GIS 开源项目**的技能文件，覆盖从底层数据处理到上层地图服务的完整链路：

```
数据源 → 命令行处理 → 编程分析 → 空间数据库 → 地图服务 → 前端可视化
 (GDAL)   (GDAL CLI)   (JTS/PyQGIS)  (PostGIS)  (GeoServer) (OpenLayers/Cesium)
```

### 何时加载此索引？

- 用户问题涉及「地图」「空间数据」「坐标」「GIS」等关键词
- 不确定具体该用 GDAL、QGIS 还是 PostGIS
- 需要了解 GIS 领域有哪些可选开源工具

---

## 技能列表

### 🧰 数据处理与命令行

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [gdal](./gdal/SKILL.md) | GDAL 命令行：栅格/矢量处理事实标准 | `cli` `raster` `vector` `conversion` |
| [gdal-api](./gdal-api/SKILL.md) | GDAL/OGR 编程 API（C/C++/Python/.NET） | `api` `python` `cpp` `dotnet` |
| [qgis-process](./qgis-process/SKILL.md) | QGIS 命令行批处理 | `cli` `processing` `headless` |
| [geopipe-agent](./geopipe-agent/SKILL.md) | AI 原生 GIS 数据流水线（YAML 驱动） | `agent` `pipeline` `yaml` `qc` |

### 🗄️ 空间数据库

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [postgis](./postgis/SKILL.md) | PostgreSQL 空间数据库扩展 | `database` `sql` `spatial` `postgresql` |

### 🔧 几何运算库

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [jts](./jts/SKILL.md) | Java Topology Suite 几何引擎 | `java` `geometry` `spatial` |
| [nettopologysuite](./nettopologysuite/SKILL.md) | JTS 的 .NET 移植 | `dotnet` `geometry` `nuget` |
| [geometry-api-java](./geometry-api-java/SKILL.md) | Esri Geometry API for Java | `java` `esri` `geometry` |
| [geometry-api-net](./geometry-api-net/SKILL.md) | Esri Geometry API for .NET | `dotnet` `esri` `geometry` |
| [shapely](./shapely/SKILL.md) | Python 几何对象与运算 | `python` `geometry` `analysis` |
| [geopandas](./geopandas/SKILL.md) | Python 矢量空间数据处理 | `python` `pandas` `vector` |

### 🌐 地图服务器

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [geoserver](./geoserver/SKILL.md) | 开源地图服务器（WMS/WFS/WMTS/WCS） | `server` `wms` `wfs` `ogc` |
| [geoserver-rest-api](./geoserver-rest-api/SKILL.md) | GeoServer REST API 自动化管理 | `rest` `automation` `publish` |
| [geoserver-cloud](./geoserver-cloud/SKILL.md) | GeoServer 云原生微服务架构 | `cloud` `kubernetes` `docker` |

### 🖥️ QGIS 生态

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [pyqgis](./pyqgis/SKILL.md) | QGIS Python 二次开发 | `python` `qgis` `plugin` |

### 🗺️ Web 地图可视化

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [cesiumjs](./cesiumjs/SKILL.md) | 高性能 3D 地球可视化 | `javascript` `3d` `webgl` |
| [openlayers](./openlayers/SKILL.md) | 高性能 Web 2D 地图库 | `javascript` `webmapping` `2d` |

### 📦 .NET GIS 组件

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [nettopologysuite](./nettopologysuite/SKILL.md) | JTS 的 .NET 移植 | `dotnet` `geometry` |
| [geometry-api-net](./geometry-api-net/SKILL.md) | Esri Geometry API for .NET | `dotnet` `esri` `geometry` |
| [sharpmap](./sharpmap/SKILL.md) | .NET WinForms/Web 地图渲染库 | `dotnet` `legacy` `winforms` |
| [mapsui](./mapsui/SKILL.md) | .NET 跨平台地图控件 | `dotnet` `crossplatform` `maui` |

### 🧩 综合/工具集

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [opengis-all](./opengis-all/SKILL.md) | **一站式 GIS 全流程索引** | `entrypoint` `workflow` `fullstack` |
| [geotools](./geotools/SKILL.md) | Java GIS 工具集 | `java` `geotools` `feature` |
| [opengis-utils-for-java](./opengis-utils-for-java/SKILL.md) | OpenGIS Java 实用工具集 | `java` `utils` `toolkit` |
| [opengis-utils-for-net](./opengis-utils-for-net/SKILL.md) | OpenGIS .NET 实用工具集 | `dotnet` `utils` `toolkit` |

---

## 快速导航

| 用户需求 | 推荐加载 |
|---------|---------|
| "Shapefile 转 GeoJSON" | `gdal/SKILL.md` |
| "Python 空间分析" | `geopandas/SKILL.md` + `shapely/SKILL.md` |
| "发布 WMS 地图服务" | `geoserver/SKILL.md` + `geoserver-rest-api/SKILL.md` |
| "QGIS 批处理" | `qgis-process/SKILL.md` |
| "Java 几何运算" | `jts/SKILL.md` |
| ".NET 地图控件" | `mapsui/SKILL.md` |
| "PostgreSQL 空间查询" | `postgis/SKILL.md` |
| "前端 3D 地球" | `cesiumjs/SKILL.md` |
| "前端 2D 地图" | `openlayers/SKILL.md` |
| "AI 驱动的 GIS 流水线" | `geopipe-agent/SKILL.md` |
| "完整 GIS 处理链路" | `opengis-all/SKILL.md` |

---

## 相关分类

- **[cad/](../cad/SKILL.md)** — CAD 参数化建模、几何运算、BIM/PCB
- **[csharp/](../csharp/SKILL.md)** — .NET 框架、ORM、Office 操作
- **[ai/](../ai/SKILL.md)** — LLM 应用、Agent 框架
- **[iot/](../iot/SKILL.md)** — 物联网与嵌入式
