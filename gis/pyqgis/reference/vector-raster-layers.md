# PyQGIS Vector and Raster Layer Operations Reference

Vector and raster layer operation APIs and examples split from SKILL.md.

---

## 矢量图层操作

### 加载矢量图层

```python
from qgis.core import QgsVectorLayer

# 从文件加载
layer = QgsVectorLayer("/data/buildings.shp", "buildings", "ogr")

# 从 GeoPackage 加载指定图层
layer = QgsVectorLayer("/data/data.gpkg|layername=rivers", "rivers", "ogr")

# 从 PostGIS 加载
uri = 'dbname=\'gis\' host=localhost port=5432 user=\'postgres\' table="public"."parcels" (geom)'
layer = QgsVectorLayer(uri, "parcels", "postgres")

# 内存图层
layer = QgsVectorLayer("Point?crs=epsg:4326&field=id:integer&field=name:string(50)", "temp", "memory")

# 验证
if not layer.isValid():
    print("图层加载失败！")
```

### 遍历要素

```python
for feature in layer.getFeatures():
    geom = feature.geometry()
    attrs = feature.attributes()
    print(feature.id(), geom.asWkt(), attrs)
```

### 按条件查询要素

```python
from qgis.core import QgsFeatureRequest

# 按属性过滤
request = QgsFeatureRequest().setFilterExpression('"population" > 10000')
for feature in layer.getFeatures(request):
    print(feature["name"], feature["population"])

# 按空间范围过滤
from qgis.core import QgsRectangle
rect = QgsRectangle(116.0, 39.0, 117.0, 40.0)
request = QgsFeatureRequest().setFilterRect(rect)
for feature in layer.getFeatures(request):
    print(feature.id())

# 限制返回字段（提升性能）
request = QgsFeatureRequest().setSubsetOfAttributes(["name", "area"], layer.fields())
```

### 编辑要素

```python
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY

# 开启编辑
layer.startEditing()

# 添加要素
feat = QgsFeature(layer.fields())
feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(116.4, 39.9)))
feat.setAttributes([1, "北京"])
layer.addFeature(feat)

# 修改已有要素属性
layer.changeAttributeValue(feature_id, field_index, new_value)

# 修改几何
layer.changeGeometry(feature_id, new_geometry)

# 删除要素
layer.deleteFeature(feature_id)

# 提交修改
layer.commitChanges()
# 或回滚
# layer.rollBack()
```

### 创建矢量文件

```python
from qgis.core import (
    QgsVectorFileWriter, QgsVectorLayer, QgsFeature,
    QgsGeometry, QgsPointXY, QgsField, QgsFields,
    QgsCoordinateReferenceSystem, QgsWkbTypes
)
from qgis.PyQt.QtCore import QVariant

# 定义字段
fields = QgsFields()
fields.append(QgsField("id", QVariant.Int))
fields.append(QgsField("name", QVariant.String))

# 创建写入器
crs = QgsCoordinateReferenceSystem("EPSG:4326")
writer = QgsVectorFileWriter(
    "/data/output.shp",
    "UTF-8",
    fields,
    QgsWkbTypes.Point,
    crs,
    "ESRI Shapefile"
)

# 写入要素
feat = QgsFeature()
feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(116.4, 39.9)))
feat.setAttributes([1, "北京"])
writer.addFeature(feat)

del writer  # 关闭文件
```

### 使用 SaveVectorOptions 写出（推荐）

```python
from qgis.core import QgsVectorFileWriter

options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "GPKG"
options.fileEncoding = "UTF-8"

error = QgsVectorFileWriter.writeAsVectorFormatV3(
    layer,
    "/data/output.gpkg",
    QgsProject.instance().transformContext(),
    options
)
```

### 空间索引

```python
from qgis.core import QgsSpatialIndex

# 构建索引
index = QgsSpatialIndex(layer.getFeatures())

# 最近邻查询（返回要素 ID 列表）
nearest_ids = index.nearestNeighbor(QgsPointXY(116.4, 39.9), 5)

# 矩形范围查询
ids_in_rect = index.intersects(QgsRectangle(116.0, 39.0, 117.0, 40.0))
```

---

## 栅格图层操作

### 加载栅格图层

```python
from qgis.core import QgsRasterLayer

# 从文件加载
layer = QgsRasterLayer("/data/dem.tif", "DEM")

# WMS 服务
uri = "url=https://example.com/wms&layers=elevation&crs=EPSG:4326&format=image/png"
layer = QgsRasterLayer(uri, "WMS Layer", "wms")

if not layer.isValid():
    print("栅格加载失败！")
```

### 查询栅格值

```python
from qgis.core import QgsPointXY, QgsRaster

# 在指定坐标获取栅格值
point = QgsPointXY(116.4, 39.9)
result = layer.dataProvider().identify(point, QgsRaster.IdentifyFormatValue)
if result.isValid():
    values = result.results()  # {band_number: value}
    print(values)
```

### 栅格统计

```python
from qgis.core import QgsRasterBandStats

stats = layer.dataProvider().bandStatistics(1, QgsRasterBandStats.All)
print(f"最小值: {stats.minimumValue}")
print(f"最大值: {stats.maximumValue}")
print(f"平均值: {stats.mean}")
print(f"标准差: {stats.stdDev}")
```

---

## 几何操作

### 创建几何

```python
from qgis.core import QgsGeometry, QgsPointXY, QgsPoint

# 点
geom_pt = QgsGeometry.fromPointXY(QgsPointXY(116.4, 39.9))

# 折线
geom_line = QgsGeometry.fromPolylineXY([
    QgsPointXY(0, 0), QgsPointXY(10, 10), QgsPointXY(20, 0)
])

# 面
geom_poly = QgsGeometry.fromPolygonXY([[
    QgsPointXY(0, 0), QgsPointXY(10, 0),
    QgsPointXY(10, 10), QgsPointXY(0, 10),
    QgsPointXY(0, 0)
]])

# 从 WKT 创建
geom = QgsGeometry.fromWkt("POINT(116.4 39.9)")

# 从 WKB 创建
geom = QgsGeometry()
geom.fromWkb(wkb_bytes)

# 从 GeoJSON 创建（通过 QgsJsonUtils）
from qgis.core import QgsJsonUtils
features = QgsJsonUtils.stringToFeatureList(geojson_string)
if features:
    geom = features[0].geometry()
```

### 格式导出

```python
wkt = geom.asWkt()        # WKT 字符串
wkb = geom.asWkb()        # WKB bytes
json_str = geom.asJson()  # GeoJSON 字符串
```

### 空间运算

```python
# 缓冲区
buffered = geom.buffer(100, 16)

# 交集
intersection = geom1.intersection(geom2)

# 合并
union = geom1.combine(geom2)

# 差集
difference = geom1.difference(geom2)

# 对称差
sym_diff = geom1.symDifference(geom2)

# 凸包
hull = geom.convexHull()

# 质心
centroid = geom.centroid()

# 包围盒
bbox = geom.boundingBox()  # 返回 QgsRectangle

# 简化
simplified = geom.simplify(tolerance)

# 有效性检查
is_valid = geom.isGeosValid()
```

### 空间关系判断

```python
geom1.intersects(geom2)   # 是否相交
geom1.contains(geom2)     # 是否包含
geom1.within(geom2)       # 是否在内部
geom1.overlaps(geom2)     # 是否重叠
geom1.touches(geom2)      # 是否相切
geom1.crosses(geom2)      # 是否交叉
geom1.disjoint(geom2)     # 是否不相交
geom1.equals(geom2)       # 是否相等
```

### 距离与面积计算

```python
# 平面距离
dist = geom1.distance(geom2)

# 椭球面距离和面积（精确计算）
from qgis.core import QgsDistanceArea, QgsCoordinateReferenceSystem

da = QgsDistanceArea()
da.setSourceCrs(QgsCoordinateReferenceSystem("EPSG:4326"),
                QgsProject.instance().transformContext())
da.setEllipsoid("WGS84")

length = da.measureLength(line_geom)
area = da.measureArea(polygon_geom)

# 两点间大地测量距离
d = da.measureLine(QgsPointXY(116.4, 39.9), QgsPointXY(121.5, 31.2))
```

---

