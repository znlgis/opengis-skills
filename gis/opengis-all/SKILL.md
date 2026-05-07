---
name: opengis-all
description: 整合 GDAL 命令行、GDAL API、qgis_process、PyQGIS、GeoServer REST API 五大工具/接口，覆盖 GIS 数据生成、格式转换、空间分析、地图服务发布全流程。通过本文件即可一站式解决从原始数据到地图服务的完整 GIS 数据处理链路。
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
# 安装 QGIS 3.16+（qgis_process 从 3.16 开始可用）
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
docker run -d -p 8080:8080 kartoza/geoserver:latest

# 验证
curl -u admin:geoserver "http://localhost:8080/geoserver/rest/about/version.json"
```

**默认认证：** 用户名 `admin`，密码 `geoserver`（HTTP Basic Auth）

---

## 阶段一：数据获取与信息查询

### 1.1 矢量数据信息查询

#### GDAL 命令行

```bash
# 列出所有图层
ogrinfo mydata.shp

# 获取图层摘要信息
ogrinfo mydata.shp layername -so

# JSON 格式输出（GDAL 3.7+，AI 友好）
ogrinfo -json mydata.shp

# 按属性过滤查看
ogrinfo mydata.shp -where "AREA > 1000"

# SQL 查询
ogrinfo mydata.shp -sql "SELECT * FROM mydata WHERE population > 10000"

# 空间范围过滤
ogrinfo mydata.shp -spat -10 40 10 50
```

#### GDAL Python API

```python
from osgeo import ogr

ds = ogr.Open("cities.shp", 0)  # 0 = 只读
layer = ds.GetLayer(0)

print(f"要素数量: {layer.GetFeatureCount()}")
print(f"空间范围: {layer.GetExtent()}")
print(f"坐标系: {layer.GetSpatialRef().ExportToWkt()}")

for feature in layer:
    name = feature.GetField("NAME")
    geom = feature.GetGeometryRef()
    if geom is not None:
        print(f"{name}: {geom.ExportToWkt()}")
ds = None
```

#### PyQGIS

```python
from qgis.core import QgsVectorLayer

layer = QgsVectorLayer("/data/buildings.shp", "buildings", "ogr")
if layer.isValid():
    print(f"要素数量: {layer.featureCount()}")
    print(f"坐标系: {layer.crs().authid()}")
    print(f"范围: {layer.extent().toString()}")

    for feature in layer.getFeatures():
        print(feature.id(), feature.geometry().asWkt(), feature.attributes())
```

### 1.2 栅格数据信息查询

#### GDAL 命令行

```bash
# 基本信息
gdalinfo dem.tif

# JSON 格式输出（便于解析）
gdalinfo -json dem.tif

# 显示统计信息
gdalinfo -stats dem.tif
```

#### GDAL Python API

```python
from osgeo import gdal

ds = gdal.Open("dem.tif", gdal.GA_ReadOnly)
print(f"尺寸: {ds.RasterXSize} x {ds.RasterYSize}")
print(f"波段数: {ds.RasterCount}")
print(f"仿射变换: {ds.GetGeoTransform()}")
print(f"投影: {ds.GetProjection()}")

band = ds.GetRasterBand(1)
data = band.ReadAsArray()  # numpy.ndarray
print(f"数据类型: {data.dtype}, 最小值: {data.min()}, 最大值: {data.max()}")
ds = None
```

#### PyQGIS

```python
from qgis.core import QgsRasterLayer, QgsRasterBandStats

layer = QgsRasterLayer("/data/dem.tif", "DEM")
if layer.isValid():
    print(f"尺寸: {layer.width()} x {layer.height()}")
    stats = layer.dataProvider().bandStatistics(1, QgsRasterBandStats.All)
    print(f"最小值: {stats.minimumValue}, 最大值: {stats.maximumValue}")
    print(f"平均值: {stats.mean}, 标准差: {stats.stdDev}")
```

### 1.3 创建新的矢量数据

#### GDAL Python API

```python
from osgeo import ogr, osr

driver = ogr.GetDriverByName("ESRI Shapefile")
ds = driver.CreateDataSource("output.shp")

srs = osr.SpatialReference()
srs.SetWellKnownGeogCS("WGS84")
layer = ds.CreateLayer("output", srs, ogr.wkbPoint)

layer.CreateField(ogr.FieldDefn("NAME", ogr.OFTString))
layer.CreateField(ogr.FieldDefn("POPULATION", ogr.OFTInteger))

feature = ogr.Feature(layer.GetLayerDefn())
feature.SetField("NAME", "Beijing")
feature.SetField("POPULATION", 21540000)
pt = ogr.Geometry(ogr.wkbPoint)
pt.SetPoint_2D(0, 116.4, 39.9)
feature.SetGeometry(pt)
layer.CreateFeature(feature)

feature = None
ds = None
```

#### PyQGIS

```python
from qgis.core import (
    QgsVectorFileWriter, QgsFields, QgsField,
    QgsFeature, QgsGeometry, QgsPointXY,
    QgsCoordinateReferenceSystem, QgsWkbTypes
)
from qgis.PyQt.QtCore import QVariant

fields = QgsFields()
fields.append(QgsField("id", QVariant.Int))
fields.append(QgsField("name", QVariant.String))

crs = QgsCoordinateReferenceSystem("EPSG:4326")
writer = QgsVectorFileWriter("/data/output.shp", "UTF-8", fields, QgsWkbTypes.Point, crs, "ESRI Shapefile")

feat = QgsFeature()
feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(116.4, 39.9)))
feat.setAttributes([1, "北京"])
writer.addFeature(feat)
del writer
```

### 1.4 创建新的栅格数据

#### GDAL Python API

```python
from osgeo import gdal, osr
import numpy as np

driver = gdal.GetDriverByName("GTiff")
ds = driver.Create("output.tif", 256, 256, 1, gdal.GDT_Float32)

ds.SetGeoTransform([116.0, 0.01, 0, 40.0, 0, -0.01])
srs = osr.SpatialReference()
srs.SetWellKnownGeogCS("WGS84")
ds.SetProjection(srs.ExportToWkt())

band = ds.GetRasterBand(1)
data = np.arange(256 * 256, dtype=np.float32).reshape(256, 256)
band.WriteArray(data)
band.SetNoDataValue(-9999.0)

ds.FlushCache()
ds = None
```

---

## 阶段二：数据处理与转换

### 2.1 矢量格式转换

#### GDAL 命令行（ogr2ogr）

```bash
# Shapefile → GeoJSON
ogr2ogr output.geojson input.shp

# Shapefile → GeoPackage
ogr2ogr -f GPKG output.gpkg input.shp

# 转换到 CSV（含 WKT 几何）
ogr2ogr -f CSV output.csv input.shp -lco GEOMETRY=AS_WKT

# PostGIS 导入
ogr2ogr -f PostgreSQL "PG:dbname=mydb user=postgres" input.shp -nln mytable

# 批量格式转换
for shp in *.shp; do
  ogr2ogr -f GeoJSON "${shp%.shp}.geojson" "$shp"
done
```

#### GDAL Python API

```python
from osgeo import gdal

gdal.VectorTranslate("output.geojson", "input.shp", format="GeoJSON")
```

#### qgis_process

```bash
qgis_process run native:reprojectlayer -- \
  INPUT=input.shp TARGET_CRS=EPSG:4326 OUTPUT=output.geojson
```

#### PyQGIS

```python
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsProject

layer = QgsVectorLayer("/data/input.shp", "input", "ogr")
options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "GPKG"
options.fileEncoding = "UTF-8"

QgsVectorFileWriter.writeAsVectorFormatV3(
    layer, "/data/output.gpkg",
    QgsProject.instance().transformContext(), options
)
```

### 2.2 栅格格式转换

#### GDAL 命令行（gdal_translate）

```bash
# GeoTIFF → PNG
gdal_translate input.tif output.png

# 带压缩的 GeoTIFF
gdal_translate -co COMPRESS=DEFLATE input.tif output.tif

# 重采样到指定分辨率
gdal_translate -tr 10 10 input.tif output.tif

# 裁剪到指定范围
gdal_translate -projwin -180 90 -170 80 input.tif output.tif

# 提取特定波段
gdal_translate -b 1 rgb.tif red.tif

# 转换数据类型
gdal_translate -ot Byte input.tif output.tif
```

#### GDAL Python API

```python
from osgeo import gdal

# 格式转换
src = gdal.Open("input.tif")
gdal.GetDriverByName("PNG").CreateCopy("output.png", src)
src = None

# 带选项的转换
gdal.Translate("output.tif", "input.tif",
               creationOptions=["COMPRESS=LZW", "TILED=YES"])
```

### 2.3 坐标系转换（重投影）

#### 矢量重投影

```bash
# GDAL 命令行
ogr2ogr -t_srs EPSG:3857 output.shp input.shp
```

```bash
# qgis_process
qgis_process run native:reprojectlayer -- \
  INPUT=input.shp TARGET_CRS=EPSG:3857 OUTPUT=reprojected.shp
```

```python
# PyQGIS
import processing
result = processing.run("native:reprojectlayer", {
    'INPUT': '/data/input_wgs84.shp',
    'TARGET_CRS': 'EPSG:3857',
    'OUTPUT': '/data/reprojected.shp'
})
```

```python
# GDAL Python API — 坐标变换
from osgeo import osr

src_srs = osr.SpatialReference()
src_srs.SetWellKnownGeogCS("WGS84")
dst_srs = osr.SpatialReference()
dst_srs.ImportFromEPSG(3857)

transform = osr.CoordinateTransformation(src_srs, dst_srs)
x, y, z = transform.TransformPoint(116.4, 39.9)
```

#### 栅格重投影

```bash
# GDAL 命令行（gdalwarp）
gdalwarp -t_srs EPSG:4326 input_utm.tif output_wgs84.tif

# 带重采样和目标分辨率
gdalwarp -tr 30 30 -t_srs EPSG:4326 -r bilinear input.tif output.tif
```

```bash
# qgis_process
qgis_process run gdal:warpreproject -- \
  INPUT=input.tif TARGET_CRS=EPSG:4326 OUTPUT=reprojected.tif
```

```python
# GDAL Python API
from osgeo import gdal

gdal.Warp("reprojected.tif", "input.tif",
          dstSRS="EPSG:3857", resampleAlg="bilinear")
```

### 2.4 数据裁剪

#### 矢量裁剪

```bash
# ogr2ogr — 矩形范围裁剪
ogr2ogr output.shp input.shp -spat -10 40 10 50

# ogr2ogr — 多边形裁剪
ogr2ogr -clipsrc clip_polygon.shp output.shp input.shp
```

```bash
# qgis_process
qgis_process run native:clip -- \
  INPUT=input.shp OVERLAY=clip_boundary.shp OUTPUT=clipped.shp
```

```python
# PyQGIS
result = processing.run("native:clip", {
    'INPUT': input_layer,
    'OVERLAY': clip_layer,
    'OUTPUT': 'memory:clipped'
})
```

#### 栅格裁剪

```bash
# gdalwarp — 用矢量边界裁剪
gdalwarp -cutline boundary.shp -crop_to_cutline input.tif output.tif

# gdalwarp — 指定范围裁剪
gdalwarp -te -10 40 10 50 input.tif output.tif
```

```bash
# qgis_process
qgis_process run gdal:cliprasterbymask -- \
  INPUT=dem.tif MASK=boundary.shp OUTPUT=clipped_dem.tif
```

```python
# PyQGIS
result = processing.run("gdal:cliprasterbymask", {
    'INPUT': '/data/dem.tif',
    'MASK': '/data/boundary.shp',
    'OUTPUT': 'TEMPORARY_OUTPUT'
})
```

### 2.5 数据合并

```bash
# 合并多个矢量文件
ogr2ogr -append merged.shp input1.shp
ogr2ogr -append merged.shp input2.shp

# qgis_process 合并矢量
qgis_process run native:mergevectorlayers -- \
  LAYERS=input1.shp LAYERS=input2.shp OUTPUT=merged.shp

# 合并多个栅格（gdalwarp 镶嵌）
gdalwarp input1.tif input2.tif input3.tif output_mosaic.tif

# gdal_merge.py 合并栅格
gdal_merge.py -o output.tif input1.tif input2.tif input3.tif
```

### 2.6 栅格元数据编辑

```bash
# 设置坐标参考系
gdal_edit.py -a_srs EPSG:4326 input.tif

# 设置地理范围
gdal_edit.py -a_ullr -180 90 180 -90 input.tif

# 设置 NoData 值
gdal_edit.py -a_nodata 0 input.tif

# 添加元数据
gdal_edit.py -mo DATUM=WGS84 -mo SOURCE=USGS input.tif
```

---

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

## 阶段四：发布 GIS 地图服务（GeoServer REST API）

**基础 URL：** `http://{host}:{port}/geoserver/rest`

**认证：** HTTP Basic Auth（默认 `admin:geoserver`）

**数据格式：** 支持 JSON 和 XML，可通过 `Accept` 头或 URL 后缀（`.json` / `.xml`）指定。

### 4.1 创建工作空间

```bash
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{"workspace":{"name":"myws"}}' \
  "http://localhost:8080/geoserver/rest/workspaces"
```

### 4.2 上传矢量数据并发布图层

#### 方式一：上传 Shapefile（自动创建数据存储和图层）

```bash
# Shapefile 需打包为 ZIP（包含 .shp、.shx、.dbf、.prj）
curl -u admin:geoserver -XPUT \
  -H "Content-Type: application/zip" \
  --data-binary @roads.zip \
  "http://localhost:8080/geoserver/rest/workspaces/myws/datastores/roads/file.shp"
```

#### 方式二：连接 PostGIS 并发布

```bash
# 创建 PostGIS 数据存储
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{
    "dataStore": {
      "name": "pgstore",
      "connectionParameters": {
        "entry": [
          {"@key": "host", "$": "localhost"},
          {"@key": "port", "$": "5432"},
          {"@key": "database", "$": "geodata"},
          {"@key": "user", "$": "postgres"},
          {"@key": "passwd", "$": "postgres"},
          {"@key": "dbtype", "$": "postgis"},
          {"@key": "schema", "$": "public"}
        ]
      }
    }
  }' \
  "http://localhost:8080/geoserver/rest/workspaces/myws/datastores"

# 发布数据库表为图层
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{"featureType":{"name":"buildings","nativeName":"buildings"}}' \
  "http://localhost:8080/geoserver/rest/workspaces/myws/datastores/pgstore/featuretypes"
```

### 4.3 上传栅格数据并发布图层

```bash
curl -u admin:geoserver -XPUT \
  -H "Content-Type: image/tiff" \
  --data-binary @dem.tif \
  "http://localhost:8080/geoserver/rest/workspaces/myws/coveragestores/dem/file.geotiff"
```

### 4.4 创建和应用样式

```bash
# 步骤 1：创建样式定义
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{"style":{"name":"mystyle","filename":"mystyle.sld"}}' \
  "http://localhost:8080/geoserver/rest/workspaces/myws/styles"

# 步骤 2：上传 SLD 文件
curl -u admin:geoserver -XPUT \
  -H "Content-Type: application/vnd.ogc.sld+xml" \
  --data-binary @mystyle.sld \
  "http://localhost:8080/geoserver/rest/workspaces/myws/styles/mystyle"

# 步骤 3：为图层设置默认样式
curl -u admin:geoserver -XPUT \
  -H "Content-Type: application/json" \
  -d '{"layer":{"defaultStyle":{"name":"mystyle","workspace":"myws"}}}' \
  "http://localhost:8080/geoserver/rest/layers/myws:roads"
```

### 4.5 创建图层组

```bash
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{
    "layerGroup": {
      "name": "basemap",
      "layers": {
        "layer": [
          {"name": "myws:roads"},
          {"name": "myws:buildings"}
        ]
      },
      "styles": {
        "style": [
          {"name": "line"},
          {"name": "polygon"}
        ]
      }
    }
  }' \
  "http://localhost:8080/geoserver/rest/workspaces/myws/layergroups"
```

### 4.6 GeoServer REST API 端点速查

#### 系统管理

| 操作 | 方法 | 端点 |
|------|------|------|
| 获取版本信息 | GET | `/rest/about/version.json` |
| 获取系统状态 | GET | `/rest/about/system-status.json` |
| 重新加载配置 | POST | `/rest/reload` |
| 重置缓存 | POST | `/rest/reset` |

#### 工作空间与数据存储

| 操作 | 方法 | 端点 |
|------|------|------|
| 列出工作空间 | GET | `/rest/workspaces.json` |
| 创建工作空间 | POST | `/rest/workspaces` |
| 删除工作空间 | DELETE | `/rest/workspaces/{ws}?recurse=true` |
| 列出数据存储 | GET | `/rest/workspaces/{ws}/datastores.json` |
| 创建数据存储 | POST | `/rest/workspaces/{ws}/datastores` |
| 上传矢量文件 | PUT | `/rest/workspaces/{ws}/datastores/{ds}/file.{ext}` |

#### 图层与样式

| 操作 | 方法 | 端点 |
|------|------|------|
| 列出所有图层 | GET | `/rest/layers.json` |
| 发布要素类型 | POST | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes` |
| 上传栅格文件 | PUT | `/rest/workspaces/{ws}/coveragestores/{cs}/file.{ext}` |
| 列出样式 | GET | `/rest/styles.json` |
| 创建样式 | POST | `/rest/styles` |
| 更新样式 | PUT | `/rest/styles/{style}` |
| 修改图层 | PUT | `/rest/layers/{layer}` |

#### 图层组与 OGC 服务

| 操作 | 方法 | 端点 |
|------|------|------|
| 列出图层组 | GET | `/rest/layergroups.json` |
| 创建图层组 | POST | `/rest/layergroups` |
| 获取 WMS 设置 | GET | `/rest/services/wms/settings.json` |
| 修改 WMS 设置 | PUT | `/rest/services/wms/settings` |
| 获取 WFS 设置 | GET | `/rest/services/wfs/settings.json` |
| 修改 WFS 设置 | PUT | `/rest/services/wfs/settings` |

#### GeoWebCache

| 操作 | 方法 | 端点 |
|------|------|------|
| 清空图层缓存 | POST | `/gwc/rest/seed/{layer}.json` |
| 查看缓存任务 | GET | `/gwc/rest/seed/{layer}.json` |
| 批量截断 | POST | `/gwc/rest/masstruncate` |

---

## 端到端工作流示例

### 示例 1：从 Shapefile 到地图服务（全自动）

完整流程：数据检查 → 重投影 → 缓冲区分析 → 发布到 GeoServer

```bash
#!/bin/bash
# === 阶段一：数据检查 ===
echo "=== 检查输入数据 ==="
ogrinfo -json buildings.shp | jq '.layers[0].featureCount'

# === 阶段二：数据处理 ===
echo "=== 重投影到 EPSG:4326 ==="
ogr2ogr -t_srs EPSG:4326 -f GPKG buildings_4326.gpkg buildings.shp

# === 阶段三：空间分析 ===
echo "=== 缓冲区分析（50米） ==="
qgis_process run native:buffer --json -- \
  INPUT=buildings_4326.gpkg DISTANCE=50 SEGMENTS=16 OUTPUT=buildings_buffer.gpkg

echo "=== 融合 ==="
qgis_process run native:dissolve --json -- \
  INPUT=buildings_buffer.gpkg OUTPUT=buildings_dissolved.gpkg

# === 阶段四：发布到 GeoServer ===
GEOSERVER="http://localhost:8080/geoserver"
AUTH="admin:geoserver"

echo "=== 创建工作空间 ==="
curl -u $AUTH -XPOST \
  -H "Content-Type: application/json" \
  -d '{"workspace":{"name":"analysis"}}' \
  "$GEOSERVER/rest/workspaces"

echo "=== 上传并发布图层 ==="
# 将 GeoPackage 转换为 Shapefile ZIP 以便上传
ogr2ogr buildings_result.shp buildings_dissolved.gpkg
zip buildings_result.zip buildings_result.*

curl -u $AUTH -XPUT \
  -H "Content-Type: application/zip" \
  --data-binary @buildings_result.zip \
  "$GEOSERVER/rest/workspaces/analysis/datastores/buildings/file.shp"

echo "=== 完成！==="
echo "WMS 地址: $GEOSERVER/wms?service=WMS&version=1.1.1&request=GetMap&layers=analysis:buildings_result&bbox=..."
```

### 示例 2：DEM 处理到坡度图服务（Python 全流程）

```python
"""从 DEM 生成坡度分析并发布到 GeoServer"""
import subprocess
import requests
from requests.auth import HTTPBasicAuth

GEOSERVER = "http://localhost:8080/geoserver"
AUTH = HTTPBasicAuth("admin", "geoserver")

# === 阶段一：数据检查 ===
subprocess.run(["gdalinfo", "dem.tif"], check=True)

# === 阶段二：数据处理 — 裁剪并重投影 ===
subprocess.run([
    "gdalwarp", "-t_srs", "EPSG:4326",
    "-cutline", "boundary.shp", "-crop_to_cutline",
    "dem.tif", "dem_clipped.tif"
], check=True)

# === 阶段三：空间分析 — 坡度分析 ===
subprocess.run([
    "qgis_process", "run", "gdal:slope", "--",
    "INPUT=dem_clipped.tif", "OUTPUT=slope.tif"
], check=True)

# === 阶段四：发布到 GeoServer ===
# 创建工作空间
requests.post(
    f"{GEOSERVER}/rest/workspaces",
    json={"workspace": {"name": "terrain"}},
    auth=AUTH
)

# 上传坡度栅格
with open("slope.tif", "rb") as f:
    requests.put(
        f"{GEOSERVER}/rest/workspaces/terrain/coveragestores/slope/file.geotiff",
        data=f,
        headers={"Content-Type": "image/tiff"},
        auth=AUTH
    )

print("坡度图层已发布！")
print(f"WMS: {GEOSERVER}/wms?service=WMS&version=1.1.1&request=GetMap&layers=terrain:slope")
```

### 示例 3：PyQGIS 完整分析流程

```python
"""PyQGIS 独立脚本：加载数据 → 分析 → 导出 → 发布"""
import sys
import requests
from requests.auth import HTTPBasicAuth
from qgis.core import QgsApplication, QgsVectorLayer, QgsProject
import processing
from processing.core.Processing import Processing

# 初始化 QGIS
qgs = QgsApplication([], False)
qgs.setPrefixPath("/usr", True)
qgs.initQgis()
Processing.initialize()

# === 阶段一：加载数据 ===
layer = QgsVectorLayer("/data/buildings.shp", "buildings", "ogr")
assert layer.isValid(), "图层加载失败"
print(f"加载完成: {layer.featureCount()} 个要素")

# === 阶段二：重投影 ===
result1 = processing.run("native:reprojectlayer", {
    'INPUT': layer,
    'TARGET_CRS': 'EPSG:4326',
    'OUTPUT': 'memory:reprojected'
})

# === 阶段三：缓冲区 + 融合 ===
result2 = processing.run("native:buffer", {
    'INPUT': result1['OUTPUT'],
    'DISTANCE': 100,
    'SEGMENTS': 16,
    'OUTPUT': 'memory:buffered'
})

result3 = processing.run("native:dissolve", {
    'INPUT': result2['OUTPUT'],
    'OUTPUT': '/data/buildings_analysis.gpkg'
})
print(f"分析完成: {result3['OUTPUT']}")

# === 阶段四：发布到 GeoServer ===
GEOSERVER = "http://localhost:8080/geoserver"
AUTH = HTTPBasicAuth("admin", "geoserver")

# 转换为 Shapefile ZIP 以上传
processing.run("native:reprojectlayer", {
    'INPUT': result3['OUTPUT'],
    'TARGET_CRS': 'EPSG:4326',
    'OUTPUT': '/data/for_upload.shp'
})

import zipfile, glob
with zipfile.ZipFile("/data/for_upload.zip", "w") as zf:
    for f in glob.glob("/data/for_upload.*"):
        zf.write(f, f.split("/")[-1])

requests.post(f"{GEOSERVER}/rest/workspaces",
              json={"workspace": {"name": "analysis"}}, auth=AUTH)

with open("/data/for_upload.zip", "rb") as f:
    requests.put(
        f"{GEOSERVER}/rest/workspaces/analysis/datastores/buildings/file.shp",
        data=f, headers={"Content-Type": "application/zip"}, auth=AUTH
    )

print("图层已发布到 GeoServer！")

qgs.exitQgis()
```

### 示例 4：使用 qgis_process JSON 模式的自动化流水线

```bash
#!/bin/bash
# 适用于 CI/CD 自动化流水线
export QT_QPA_PLATFORM=offscreen

# 步骤 1：缓冲区分析（JSON 输入）
echo '{
  "inputs": {
    "INPUT": "/data/roads.shp",
    "DISTANCE": 50,
    "SEGMENTS": 10,
    "OUTPUT": "/data/roads_buffer.gpkg"
  }
}' | qgis_process run native:buffer -

# 步骤 2：解析输出路径
BUFFER_OUTPUT=$(echo '{
  "inputs": {
    "INPUT": "/data/roads.shp",
    "DISTANCE": 50,
    "SEGMENTS": 10,
    "OUTPUT": "/data/roads_buffer.gpkg"
  }
}' | qgis_process run native:buffer - | jq -r '.results.OUTPUT')

# 步骤 3：融合
qgis_process run native:dissolve --json -- \
  INPUT="$BUFFER_OUTPUT" OUTPUT=/data/roads_dissolved.gpkg

# 步骤 4：发布到 GeoServer
ogr2ogr roads_final.shp /data/roads_dissolved.gpkg
zip roads_final.zip roads_final.*

curl -u admin:geoserver -XPUT \
  -H "Content-Type: application/zip" \
  --data-binary @roads_final.zip \
  "http://localhost:8080/geoserver/rest/workspaces/myws/datastores/roads/file.shp"
```

---

## 常用内置算法速查（qgis_process / PyQGIS）

### 矢量分析

| 算法 ID | 说明 | 关键参数 |
|---------|------|---------|
| `native:buffer` | 缓冲区分析 | INPUT, DISTANCE, SEGMENTS, DISSOLVE |
| `native:clip` | 矢量裁剪 | INPUT, OVERLAY |
| `native:dissolve` | 融合 | INPUT, FIELD |
| `native:intersection` | 交集 | INPUT, OVERLAY |
| `native:union` | 联合 | INPUT, OVERLAY |
| `native:difference` | 差集 | INPUT, OVERLAY |
| `native:symmetricaldifference` | 对称差 | INPUT, OVERLAY |
| `native:centroids` | 质心 | INPUT |
| `native:convexhull` | 凸包 | INPUT |
| `native:simplifygeometries` | 简化几何 | INPUT, TOLERANCE |
| `native:reprojectlayer` | 重投影 | INPUT, TARGET_CRS |
| `native:mergevectorlayers` | 合并图层 | LAYERS |
| `native:splitvectorlayer` | 拆分图层 | INPUT, FIELD |
| `native:extractbyattribute` | 按属性提取 | INPUT, FIELD, OPERATOR, VALUE |
| `native:extractbylocation` | 按位置提取 | INPUT, INTERSECT, PREDICATE |
| `native:joinattributesbylocation` | 按位置连接属性 | INPUT, JOIN, PREDICATE |
| `native:fixgeometries` | 修复几何 | INPUT |
| `native:countpointsinpolygon` | 多边形内点计数 | POLYGONS, POINTS |
| `native:voronoipolygons` | 泰森多边形 | INPUT |
| `native:creategrid` | 创建网格 | TYPE, EXTENT, HSPACING, VSPACING |
| `native:fieldcalculator` | 字段计算器 | INPUT, FIELD_NAME, FORMULA |

### 栅格分析

| 算法 ID | 说明 | 关键参数 |
|---------|------|---------|
| `native:rasterlayerstatistics` | 栅格统计 | INPUT |
| `gdal:cliprasterbyextent` | 按范围裁剪栅格 | INPUT, EXTENT |
| `gdal:cliprasterbymask` | 按掩膜裁剪栅格 | INPUT, MASK |
| `gdal:merge` | 栅格合并 | INPUT |
| `gdal:warpreproject` | 栅格重投影 | INPUT, TARGET_CRS |
| `gdal:contour` | 等值线提取 | INPUT, INTERVAL |
| `gdal:polygonize` | 栅格转矢量 | INPUT |
| `gdal:rasterize` | 矢量转栅格 | INPUT, FIELD |
| `gdal:hillshade` | 山体阴影 | INPUT |
| `gdal:slope` | 坡度分析 | INPUT |
| `gdal:aspect` | 坡向分析 | INPUT |
| `gdal:roughness` | 粗糙度 | INPUT |
| `gdal:buildvirtualraster` | 构建虚拟栅格 | INPUT |

---

## GDAL 命令行工具速查

### 矢量工具

| 命令 | 说明 |
|------|------|
| `ogrinfo` | 矢量数据信息查询 |
| `ogr2ogr` | 矢量格式转换和处理 |

### 栅格工具

| 命令 | 说明 |
|------|------|
| `gdalinfo` | 栅格数据信息查询 |
| `gdal_translate` | 栅格格式转换和重采样 |
| `gdalwarp` | 栅格重投影和镶嵌 |
| `gdal_merge.py` | 栅格镶嵌融合 |
| `gdal_calc.py` | 栅格计算器（NumPy 语法） |
| `gdal_contour` | 等值线提取 |
| `gdal_grid` | 散点数据插值创建网格 |
| `gdal_polygonize.py` | 栅格转矢量 |
| `gdaltindex` | 创建栅格瓦片索引 |
| `gdal_edit.py` | 编辑栅格元数据 |
| `nearblack` | 清理黑白边界 |

---

## 数据格式支持

### 矢量格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| Shapefile | .shp | ESRI 标准格式 |
| GeoJSON | .geojson | Web 标准 JSON |
| GeoPackage | .gpkg | SQLite 基础，推荐 |
| KML | .kml | Google Maps 格式 |
| PostGIS | N/A | 数据库矢量存储 |
| GML | .gml | ISO 标准 XML |
| CSV | .csv | 点数据 |
| FlatGeobuf | .fgb | 高性能流式二进制格式 |

### 栅格格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| GeoTIFF | .tif | 标准地理栅格（推荐） |
| COG | .tif | 云优化 GeoTIFF |
| PNG | .png | Web 图像 |
| JPEG | .jpg | 有损压缩 |
| NetCDF | .nc | 科学数据 |
| HDF5 | .h5 | 多维数据 |
| JPEG2000 | .jp2 | 高质量压缩 |
| ASCII Grid | .asc | 简单栅格 |

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

## 参考链接

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
