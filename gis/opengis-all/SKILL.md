---
name: opengis-all
description: "Use when navigating end-to-end GIS workflows — discover the full toolchain from GDAL data processing through GeoServer publishing to CesiumJS/OpenLayers visualization. One-stop index covering the complete open-source GIS data pipeline."

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

```
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
docker run -d -p 8080:8080 docker.osgeo.org/geoserver:3.0.0

# 验证
curl -u admin:geoserver "http://localhost:8080/geoserver/rest/about/version.json"
```

**默认认证：** 用户名 `admin`，密码 `geoserver`（HTTP Basic Auth）

---

> 阶段一（数据获取与信息查询）与阶段二（数据处理与转换）的完整操作手册见 [reference/data-stages.md](reference/data-stages.md)

## 阶段三：空间分析

### 3.1 缓冲区分析

```bash
# qgis_process
qgis_process run native:buffer -- \
  INPUT=points.shp DISTANCE=1000 SEGMENTS=16 OUTPUT=buffered.gpkg
```

```python
# PyQGIS (processing)
result = processing.run("native:buffer", {
    'INPUT': '/data/roads.shp',
    'DISTANCE': 50,
    'SEGMENTS': 10,
    'DISSOLVE': False,
    'OUTPUT': '/data/roads_buffer.shp'
})
```

```python
# PyQGIS (几何操作)
buffered = geom.buffer(100, 16)
```

```python
# GDAL Python API (OGR 几何)
from osgeo import ogr
pt = ogr.Geometry(ogr.wkbPoint)
pt.SetPoint_2D(0, 116.4, 39.9)
buffer = pt.Buffer(1.0)
```

### 3.2 叠加分析（交集/联合/差集）

```bash
# qgis_process — 交集
qgis_process run native:intersection -- \
  INPUT=layer1.shp OVERLAY=layer2.shp OUTPUT=intersection.shp

# qgis_process — 联合
qgis_process run native:union -- \
  INPUT=layer1.shp OVERLAY=layer2.shp OUTPUT=union.shp

# qgis_process — 差集
qgis_process run native:difference -- \
  INPUT=layer1.shp OVERLAY=layer2.shp OUTPUT=difference.shp
```

```python
# PyQGIS
result = processing.run("native:intersection", {
    'INPUT': layer1, 'OVERLAY': layer2, 'OUTPUT': 'memory:intersected'
})
```

```python
# PyQGIS 几何级别操作
intersection = geom1.intersection(geom2)
union = geom1.combine(geom2)
difference = geom1.difference(geom2)
sym_diff = geom1.symDifference(geom2)
```

```python
# GDAL OGR 几何级别操作
inter   = polygon.Intersection(pt)
united  = polygon.Union(pt)
diff    = polygon.Difference(pt)
```

### 3.3 融合（Dissolve）

```bash
# qgis_process
qgis_process run native:dissolve -- \
  INPUT=polygons.shp FIELD=type OUTPUT=dissolved.gpkg
```

```python
# PyQGIS
result = processing.run("native:dissolve", {
    'INPUT': '/data/polygons.shp',
    'FIELD': ['type'],
    'OUTPUT': '/data/dissolved.gpkg'
})
```

### 3.4 空间连接

```bash
# qgis_process — 按位置连接属性
qgis_process run native:joinattributesbylocation -- \
  INPUT=points.shp JOIN=polygons.shp PREDICATE=0 OUTPUT=joined.shp
```

```python
# PyQGIS
result = processing.run("native:joinattributesbylocation", {
    'INPUT': points_layer,
    'JOIN': polygons_layer,
    'PREDICATE': [0],  # 0=相交
    'METHOD': 0,       # 0=一对一
    'OUTPUT': 'memory:joined'
})
```

### 3.5 栅格计算（波段运算）

```bash
# NDVI 计算
gdal_calc.py -A nir.tif -B red.tif \
  --calc="(A-B)/(A+B)" --outfile=ndvi.tif

# 栅格掩膜
gdal_calc.py -A input.tif --calc="A*(A>100)" \
  --outfile=masked.tif --NoDataValue=0

# 两个栅格平均
gdal_calc.py -A input1.tif -B input2.tif \
  --calc="(A+B)/2" --outfile=mean.tif
```

### 3.6 DEM 分析

```bash
# 等值线提取
gdal_contour -a elevation dem.tif contours.shp -i 10

# qgis_process — 坡度分析
qgis_process run gdal:slope -- INPUT=dem.tif OUTPUT=slope.tif

# qgis_process — 坡向分析
qgis_process run gdal:aspect -- INPUT=dem.tif OUTPUT=aspect.tif

# qgis_process — 山体阴影
qgis_process run gdal:hillshade -- INPUT=dem.tif OUTPUT=hillshade.tif
```

```python
# PyQGIS — 坡度分析
result = processing.run("gdal:slope", {
    'INPUT': '/data/dem.tif',
    'OUTPUT': '/data/slope.tif'
})
```

### 3.7 散点插值（创建 DEM）

```bash
# 反距离加权（IDW）插值
gdal_grid -a invdist:power=2:smoothing=0 \
  -zfield Z input_points.shp output_dem.tif

# 指定输出范围和分辨率
gdal_grid -outsize 512 512 -tr 10 10 \
  -a average input_points.shp output_dem.tif
```

### 3.8 栅格矢量互转

```bash
# 栅格转矢量（多边形化）
gdal_polygonize.py input.tif output.shp

# qgis_process
qgis_process run gdal:polygonize -- INPUT=input.tif OUTPUT=output.shp

# 矢量转栅格
qgis_process run gdal:rasterize -- \
  INPUT=input.shp FIELD=value OUTPUT=output.tif
```

### 3.9 空间查询与过滤

```bash
# ogr2ogr — 属性过滤
ogr2ogr output.shp input.shp -where "population > 1000000"

# ogr2ogr — 空间过滤
ogr2ogr output.shp input.shp -spat 116.0 39.5 117.0 40.5

# qgis_process — 按属性提取
qgis_process run native:extractbyattribute -- \
  INPUT=input.shp FIELD=type OPERATOR=0 VALUE=road OUTPUT=roads.shp

# qgis_process — 按位置提取
qgis_process run native:extractbylocation -- \
  INPUT=points.shp INTERSECT=boundary.shp PREDICATE=0 OUTPUT=extracted.shp
```

```python
# PyQGIS — 要素查询
from qgis.core import QgsFeatureRequest, QgsRectangle

# 属性过滤
request = QgsFeatureRequest().setFilterExpression('"population" > 10000')
for feature in layer.getFeatures(request):
    print(feature["name"])

# 空间范围过滤
rect = QgsRectangle(116.0, 39.0, 117.0, 40.0)
request = QgsFeatureRequest().setFilterRect(rect)
for feature in layer.getFeatures(request):
    print(feature.id())
```

```python
# GDAL Python API — 空间过滤 + 属性过滤
from osgeo import ogr

ds = ogr.Open("input.shp")
layer = ds.GetLayer(0)
layer.SetSpatialFilterRect(116.0, 39.5, 117.0, 40.5)
layer.SetAttributeFilter("POPULATION > 1000000")

for feature in layer:
    print(feature.GetField("NAME"))
ds = None
```

### 3.10 地图渲染与导出

```python
# PyQGIS — 渲染为 PNG
from qgis.core import QgsMapSettings, QgsMapRendererSequentialJob
from qgis.PyQt.QtCore import QSize

settings = QgsMapSettings()
settings.setLayers([layer])
settings.setDestinationCrs(layer.crs())
settings.setExtent(layer.extent())
settings.setOutputSize(QSize(1920, 1080))

job = QgsMapRendererSequentialJob(settings)
job.start()
job.waitForFinished()
job.renderedImage().save("/data/map_output.png")
```

```python
# PyQGIS — 导出 PDF
from qgis.core import QgsProject, QgsPrintLayout, QgsLayoutItemMap, QgsLayoutExporter

project = QgsProject.instance()
layout = QgsPrintLayout(project)
layout.initializeDefaults()

map_item = QgsLayoutItemMap(layout)
map_item.setRect(20, 20, 200, 150)
map_item.setExtent(layer.extent())
map_item.setLayers([layer])
layout.addLayoutItem(map_item)

exporter = QgsLayoutExporter(layout)
exporter.exportToPdf("/data/output.pdf", QgsLayoutExporter.PdfExportSettings())
```

---

> 阶段四（发布 GIS 地图服务）的完整 GeoServer REST 操作见 [reference/data-stages.md](reference/data-stages.md)
> 端到端工作流示例、内置算法速查、GDAL 命令速查、数据格式与环境变量见 [reference/workflow-cheatsheets.md](reference/workflow-cheatsheets.md)

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

## AI 使用建议

### 工具选择指南

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 快速格式转换 | GDAL 命令行（ogr2ogr / gdal_translate） | 最简洁，适合脚本 |
| 复杂空间分析 | qgis_process 或 PyQGIS | 算法丰富，参数统一 |
| 编程集成 | GDAL API 或 PyQGIS | 灵活控制，适合程序嵌入 |
| 栅格波段运算 | gdal_calc.py | NumPy 语法，简单直观 |
| DEM 分析 | qgis_process (gdal:slope 等) | 一行命令完成 |
| 几何级别操作 | GDAL OGR API 或 PyQGIS QgsGeometry | 精确控制每个几何操作 |
| 服务发布 | GeoServer REST API | 唯一选择，HTTP 接口标准 |
| CI/CD 自动化 | qgis_process + GDAL CLI + curl | 命令行驱动，JSON 输出 |

### 推荐完整工作流

1. **探索数据**：`ogrinfo -json` / `gdalinfo -json` — 获取结构化元数据
2. **格式转换**：`ogr2ogr` / `gdal_translate` — 统一数据格式
3. **坐标统一**：`ogr2ogr -t_srs` / `gdalwarp -t_srs` — 统一坐标系
4. **空间分析**：`qgis_process run` / `processing.run()` — 执行分析算法
5. **结果验证**：`ogrinfo -json` / `gdalinfo -json` — 验证输出
6. **发布服务**：GeoServer REST API — 上传并发布地图服务

### 关键注意事项

1. **始终使用绝对路径**：避免工作目录不确定导致文件找不到。
2. **始终使用 `--json` 选项**：JSON 输出结构化、易解析，是 AI 最友好的交互方式。
3. **先查 help 再构造参数**：`qgis_process help <id> --json` 确认参数定义。
4. **Headless 环境设置 `QT_QPA_PLATFORM=offscreen`**：在无显示器的服务器上必须设置。
5. **坐标系一致性**：空间运算前确保所有数据使用相同 CRS。
6. **文件上传格式**：GeoServer 上传 Shapefile 时需打包为 ZIP，且 ZIP 内须含 `.shp`、`.shx`、`.dbf`、`.prj`。
7. **GeoServer JSON 包装**：REST API 的 JSON 请求/响应均使用单层包装（如 `{"workspace":{...}}`）。
8. **recurse 参数**：删除 GeoServer 工作空间/数据存储时，添加 `?recurse=true` 级联删除。
9. **大数据优化**：启用 `GDAL_NUM_THREADS=ALL_CPUS`，增大 `GDAL_CACHEMAX`；PyQGIS 中使用 `QgsSpatialIndex`。
10. **始终备份**：GDAL 可就地修改文件（如 `gdal_edit.py`），操作前做好备份。

---

## 相关技能

- **gdal** — GDAL 命令行工具：[../gdal/SKILL.md](../gdal/SKILL.md)
- **gdal-api** — GDAL 编程 API：[../gdal-api/SKILL.md](../gdal-api/SKILL.md)
- **pyqgis** — QGIS Python 开发：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **qgis-process** — QGIS 命令行批处理：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **geoserver-rest-api** — GeoServer REST API：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **geopipe-agent** — AI 驱动的 GIS 流水线：[../geopipe-agent/SKILL.md](../geopipe-agent/SKILL.md)

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
