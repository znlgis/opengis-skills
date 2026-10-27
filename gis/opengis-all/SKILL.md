---
name: opengis-all
description: "Use when navigating end-to-end GIS workflows — GDAL CLI/API (ogr2ogr, gdalwarp, gdal_calc.py), qgis_process and PyQGIS analysis, GeoServer REST publishing, and OpenLayers/CesiumJS visualization. One-stop index covering the complete open-source GIS data pipeline."

tags:
  - gis
  - entrypoint
  - workflow
  - fullstack
  - gdal
  - qgis
  - geoserver
  - pyqgis
  - tutorial
---

> **涵盖工具与项目：**
>
> | 工具/接口 | 项目地址 | 文档 | 许可证 |
> |-----------|----------|------|--------|
> | GDAL 命令行 | <https://github.com/OSGeo/gdal> | <https://gdal.org/en/latest/programs/> | MIT |
> | GDAL API (C++/Python/Java/C#) | <https://github.com/OSGeo/gdal> | <https://gdal.org/en/stable/api/index.html> | MIT |
> | qgis_process | <https://github.com/qgis/QGIS> | <https://docs.qgis.org/3.44/en/docs/user_manual/processing/standalone.html> | GPL-2.0+ |
> | PyQGIS | <https://github.com/qgis/QGIS> | <https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/> | GPL-2.0+ |
> | GeoServer REST API | <https://github.com/geoserver/geoserver> | <https://docs.geoserver.org/latest/en/user/rest/index.html> | GPL-2.0+ |

## 概述

本文件将五个独立的 GIS 技能模块整合为一个**端到端的 GIS 数据处理流程**，涵盖以下阶段：

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  阶段一       │    │  阶段二       │    │  阶段三       │    │  阶段四       │
│  数据获取     │ →  │  数据处理     │ →  │  空间分析     │ →  │  服务发布     │
│  与生成       │    │  与转换       │    │              │    │              │
│              │    │              │    │              │    │              │
│ · 读取各类    │    │ · 格式转换    │    │ · 缓冲区分析  │    │ · 创建工作空间 │
│   矢量/栅格  │    │ · 坐标系转换  │    │ · 叠加分析    │    │ · 上传数据    │
│ · 创建新数据  │    │ · 裁剪/合并   │    │ · 栅格计算    │    │ · 发布图层    │
│ · 查询元数据  │    │ · 元数据编辑  │    │ · DEM分析     │    │ · 配置样式    │
│              │    │              │    │ · 统计分析    │    │ · 图层组/缓存 │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘

工具映射：
  阶段一：GDAL CLI (ogrinfo/gdalinfo) · GDAL API · PyQGIS
  阶段二：GDAL CLI (ogr2ogr/gdalwarp/gdal_translate) · GDAL API · qgis_process · PyQGIS
  阶段三：qgis_process · PyQGIS · GDAL CLI (gdal_calc/gdal_contour) · GDAL API
  阶段四：GeoServer REST API
```

---

## 环境准备

### GDAL（命令行 + API）

```bash
# Linux (Debian/Ubuntu)
apt-get update && apt-get install gdal-bin python3-gdal libgdal-dev

# macOS
brew install gdal

# Conda（推荐，自动处理 C 库依赖）
conda install -c conda-forge gdal

# Docker
docker run -it osgeo/gdal:latest bash

# 验证
gdalinfo --version
ogrinfo --version
python3 -c "from osgeo import gdal; print(gdal.VersionInfo())"
```

### QGIS（qgis_process + PyQGIS）

```bash
# 安装 QGIS 3.44 LTR 或 4.x（qgis_process 从 3.16 开始可用）
# Ubuntu
apt-get install qgis qgis-plugin-grass

# 验证
qgis_process --version

# Headless 服务器环境（无窗口系统）
export QT_QPA_PLATFORM=offscreen
```

### GeoServer

```bash
# Docker 方式（推荐）
docker run -d -p 8080:8080 docker.osgeo.org/geoserver:3.0.2

# 验证
curl -u admin:geoserver "http://localhost:8080/geoserver/rest/about/version.json"
```

**默认认证：** 用户名 `admin`，密码 `geoserver`（HTTP Basic Auth）

---

> 阶段一（数据获取与信息查询）、阶段二（数据处理与转换）、阶段三（空间分析）的完整操作手册见 [reference/data-stages.md](reference/data-stages.md)

## 核心 API 与命令速查

| 阶段 | 工具 | 入口 |
|------|------|------|
| 数据获取/元数据 | GDAL CLI | `ogrinfo -json`（矢量）、`gdalinfo -json`（栅格） |
| 格式转换 | GDAL CLI | `ogr2ogr`（矢量）、`gdal_translate`（栅格） |
| 坐标统一 | GDAL CLI | `ogr2ogr -t_srs` / `gdalwarp -t_srs` |
| 空间分析 | qgis_process / PyQGIS | `qgis_process run <alg> --json` / `processing.run(...)` |
| 栅格波段运算 | GDAL CLI | `gdal_calc.py`（NumPy 语法） |
| 编程集成 | GDAL API / PyQGIS | `osgeo.ogr`/`osgeo.gdal`、`QgsApplication` + `QgisInterface` |
| 服务发布 | GeoServer REST API | HTTP + JSON（工作空间 → 数据存储 → 图层 → 样式） |

> 各阶段完整示例见 [reference/data-stages.md](reference/data-stages.md) 与 [reference/workflow-cheatsheets.md](reference/workflow-cheatsheets.md)。

---

## 阶段三：空间分析（速查）

| 任务 | 命令入口 |
|------|----------|
| 缓冲区 | `qgis_process run native:buffer -- INPUT=... DISTANCE=... OUTPUT=...` |
| 交集/联合/差集 | `native:intersection / native:union / native:difference` |
| 融合 | `native:dissolve -- FIELD=...` |
| 空间连接 | `native:joinattributesbylocation -- PREDICATE=0` |
| 按属性/位置提取 | `native:extractbyattribute / native:extractbylocation` |
| 栅格波段运算 | `gdal_calc.py -A nir.tif -B red.tif --calc="(A-B)/(A+B)"` |
| DEM 分析 | `gdal_contour -i 10 / qgis_process run gdal:slope|aspect|hillshade` |
| 插值成 DEM | `gdal_grid -a invdist:power=2:zfield=Z` |
| 栅格矢量互转 | `gdal_polygonize.py / qgis_process run gdal:rasterize` |
| 地图渲染导出 | `PyQGIS QgsMapRendererSequentialJob / QgsLayoutExporter` |

> 完整的 3.1-3.10 逐项示例（qgis_process、PyQGIS、GDAL Python API 三种写法）见 [reference/data-stages.md](reference/data-stages.md)。

> 阶段四（发布 GIS 地图服务）的完整 GeoServer REST 操作见 [reference/data-stages.md](reference/data-stages.md)
> 端到端工作流示例、内置算法速查、GDAL 命令速查、数据格式与环境变量见 [reference/workflow-cheatsheets.md](reference/workflow-cheatsheets.md)

## 典型工作流

### 端到端：Shapefile → 缓冲分析 → GeoServer 发布 → Web 预览

输入 `data/roads.shp`（EPSG:4326），输出 `http://localhost:8080/geoserver/wms` 上可用的图层 `demo:roads_buffer`。

1. **探索数据**：`ogrinfo -so -al data/roads.shp` 确认要素数与 CRS
2. **统一格式与坐标系**：`ogr2ogr -t_srs EPSG:3857 roads_3857.gpkg data/roads.shp`
3. **空间分析**：`qgis_process run native:buffer -- INPUT=roads_3857.gpkg DISTANCE=500 OUTPUT=roads_buffer.gpkg`
4. **验证结果**：`ogrinfo -so roads_buffer.gpkg roads_buffer` 核对方框与要素数
5. **发布服务**：GeoServer REST 建工作空间 → 上传 GeoPackage → 发布图层
6. **前端预览**：OpenLayers `TileWMS` 指向 `/geoserver/wms`，`LAYERS: 'demo:roads_buffer'`

```bash
# 1~4：本地分析与验证
ogrinfo -so -al data/roads.shp
ogr2ogr -t_srs EPSG:3857 roads_3857.gpkg data/roads.shp
QT_QPA_PLATFORM=offscreen qgis_process run native:buffer -- \
  INPUT=roads_3857.gpkg DISTANCE=500 SEGMENTS=8 OUTPUT=roads_buffer.gpkg
ogrinfo -so roads_buffer.gpkg roads_buffer

# 5：发布（GeoServer 3.0.2，默认 admin/geoserver）
BASE=http://localhost:8080/geoserver/rest
curl -u admin:geoserver -X POST "$BASE/workspaces" \
  -H 'Content-Type: application/json' \
  -d '{"workspace":{"name":"demo"}}'

curl -u admin:geoserver -X PUT "$BASE/workspaces/demo/datastores/roads/file.gpkg?configure=all" \
  -H 'Content-Type: application/geopackage+sqlite3' \
  --data-binary @roads_buffer.gpkg

# 6：回读确认图层已发布
curl -u admin:geoserver "$BASE/layers/demo:roads_buffer.json"
```

```js
// 6：OpenLayers 前端预览
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import TileLayer from 'ol/layer/Tile.js';
import TileWMS from 'ol/source/TileWMS.js';

new Map({
  target: 'map',
  layers: [new TileLayer({
    source: new TileWMS({
      url: 'http://localhost:8080/geoserver/wms',
      params: { LAYERS: 'demo:roads_buffer', TILED: true }
    })
  })],
  view: new View({ center: [12968000, 4863000], zoom: 12 })
});
```

**验收**：`curl -u admin:geoserver .../layers/demo:roads_buffer.json` 返回 200 且含 `"enabled": true`；前端地图能看到缓冲区图形。任一步失败都不要继续后续阶段——先修当前阶段的产物。


---

## 常用环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `QT_QPA_PLATFORM` | Qt 平台插件（Headless 必需） | `offscreen` |
| `GDAL_DATA` | GDAL 数据文件目录 | `/usr/share/gdal/` |
| `PROJ_LIB` | PROJ 数据文件目录 | `/usr/share/proj/` |
| `GDAL_NUM_THREADS` | GDAL 处理线程数 | `ALL_CPUS` |
| `GDAL_CACHEMAX` | 块缓存大小（MB） | `512` |
| `CPL_DEBUG` | 调试日志级别 | `ON` |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 无显示器服务器上 qgis_process 崩溃 | 设置 `QT_QPA_PLATFORM=offscreen` |
| GeoServer 上传 Shapefile 失败 | 打包为 ZIP，且 ZIP 根目录须含 `.shp`、`.shx`、`.dbf`、`.prj` |
| 分析结果坐标错位 | 全链路统一 CRS：`ogr2ogr -t_srs` / `gdalwarp -t_srs` / `qgis_process run native:reprojectlayer` |
| 找不到 `gdal_calc.py` | 安装 GDAL Python 绑定（`python3-gdal` 或 conda 的 `gdal`），或改用 `qgis_process run gdal:rastercalculator` |
| 大栅格/大矢量导致内存不足 | 先裁剪或分块（`gdal_translate -srcwin`/`-outsize`），并调大 `GDAL_CACHEMAX`、启用 `GDAL_NUM_THREADS` |
| GeoServer REST 返回 401/403 | 检查 HTTP Basic Auth（默认 `admin/geoserver`）与用户权限 |
| PyQGIS 导入 `qgis.core` 失败 | 需在 QGIS 自带 Python 环境运行，或正确配置 `PYTHONPATH`/`QGIS_PREFIX_PATH` |

---

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("opengis-all")` 加载（用户也可输入 `/opengis-all`）；本页是阶段索引，详细步骤在 `reference/data-stages.md` 与 `reference/workflow-cheatsheets.md`，按当前阶段 `read`，不要一次全读。
- **执行环境**：命令交给 dsh 的 shell 工具（Windows 用 `pwsh`；仅暴露 `run_code` 的会话在 `tools.pwsh` 中执行）。示例是 Linux/bash 写法，按平台改写 `apt`、`/tmp`、`export` 与反引号；Windows 路径加引号。
- **先探测工具链**：`gdalinfo --version`、`qgis_process --version`、`python3 -c "from osgeo import gdal; print(gdal.VersionInfo())"`、`curl -u admin:geoserver "http://localhost:8080/geoserver/rest/about/version.json"`；缺哪个阶段就加载相邻技能（如 `skill("gdal")`、`skill("qgis-process")`）。
- **分阶段交付**：每阶段产物落盘到工作区（GeoPackage/COG/GeoJSON），下一阶段只读取产物；先用 `ogrinfo -so`、`gdalinfo -json` 看摘要，不要把大文件或大段输出贴进上下文。
- **验证**：转换后重新打开结果核对 CRS、范围、要素数；发布后用 `curl` 回读 REST 资源或 `GetCapabilities`；无显示器环境设置 `QT_QPA_PLATFORM=offscreen`；`qgis_process` 参数先用 `qgis_process help <id> --json` 确认。
- **安全**：`gdal_edit.py`、覆盖输出、GeoServer `?recurse=true` 删除均不可逆；先备份并确认路径，安装 GDAL/QGIS、启动服务或使用数据库凭据前先征得用户同意。

---

## 相关技能

- **gdal** — GDAL 命令行工具：[../gdal/SKILL.md](../gdal/SKILL.md)
- **gdal-api** — GDAL 编程 API：[../gdal-api/SKILL.md](../gdal-api/SKILL.md)
- **pyqgis** — QGIS Python 开发：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **qgis-process** — QGIS 命令行批处理：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **geoserver-rest-api** — GeoServer REST API：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **geopipe-agent** — AI 驱动的 GIS 流水线：[../geopipe-agent/SKILL.md](../geopipe-agent/SKILL.md)
- **openlayers** — 前端 2D 地图可视化：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **cesiumjs** — 前端 3D 地球可视化：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)
- **duckdb-spatial** — 用 SQL 直接分析 Shapefile/GeoParquet：[../duckdb-spatial/SKILL.md](../duckdb-spatial/SKILL.md)
- **geolibre** — 浏览器/桌面里做 GIS，无需服务端：[../geolibre/SKILL.md](../geolibre/SKILL.md)
- **whitebox-tools** — 地形/水文/LiDAR 批量分析：[../whitebox-tools/SKILL.md](../whitebox-tools/SKILL.md)
- **pdal** — 点云 LAS/LAZ 处理与 DEM 生成：[../pdal/SKILL.md](../pdal/SKILL.md)

## 参考资源

- **GDAL 源码：** <https://github.com/OSGeo/gdal>
- **GDAL 官方文档：** <https://gdal.org/en/latest/>
- **GDAL 命令行工具：** <https://gdal.org/en/latest/programs/>
- **GDAL API 总览：** <https://gdal.org/en/stable/api/index.html>
- **GDAL Python API：** <https://gdal.org/en/stable/api/python/index.html>
- **QGIS 源码：** <https://github.com/qgis/QGIS>
- **qgis_process 文档：** <https://docs.qgis.org/3.44/en/docs/user_manual/processing/standalone.html>
- **PyQGIS 开发者手册：** <https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/>
- **PyQGIS API 参考：** <https://qgis.org/pyqgis/3.44/>
- **GeoServer 源码：** <https://github.com/geoserver/geoserver>
- **GeoServer REST API：** <https://docs.geoserver.org/latest/en/user/rest/index.html>
- **GeoServer API 参考：** <https://docs.geoserver.org/stable/en/user/rest/api/index.html>
