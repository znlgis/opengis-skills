# OpenGIS Data Pipeline Stages Reference

Stage 1 (data acquisition/query), stage 2 (processing/conversion) and stage 4 (GeoServer publishing) split from SKILL.md.

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

