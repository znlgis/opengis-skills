---
name: pyqgis
description: PyQGIS 是 QGIS 的 Python 绑定，提供对 QGIS 核心 C++ 库的完整 Python 访问能力。通过 PyQGIS，可在 Python 脚本、QGIS 控制台、独立应用或插件中执行矢量/栅格图层管理、几何操作、坐标变换、空间分析、Processing 算法调用、地图渲染与导出等 GIS 任务。
---

> **项目地址：** <https://github.com/qgis/QGIS>
>
> **开发者手册：** <https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/>
>
> **Python API 参考：** <https://qgis.org/pyqgis/3.44/>
>
> **许可证：** GNU General Public License v2.0+

## 概述

PyQGIS 是 QGIS 桌面 GIS 软件的 Python 绑定层，对应 QGIS 源码中 `python/` 目录下的绑定代码。它将 QGIS 核心 C++ 类库完整暴露给 Python，使得开发者可以：

- 在 **QGIS Python 控制台**中交互式操作
- 编写 **独立 Python 脚本**（无需启动 QGIS 桌面）
- 开发 **QGIS 插件**扩展桌面功能
- 调用 **Processing 框架**执行 100+ 种空间分析算法
- 进行 **地图渲染与导出**（PNG / PDF / SVG）

PyQGIS 主要包含以下模块：

| 模块 | 说明 |
|------|------|
| `qgis.core` | 核心类——图层、要素、几何、坐标系、项目、Processing 等 |
| `qgis.gui` | GUI 组件——地图画布、地图工具、符号选择器等 |
| `qgis.analysis` | 空间分析——插值、网络分析、栅格计算等 |
| `qgis.processing` | Processing 算法调用入口（`processing.run()`） |
| `qgis.server` | QGIS Server Python 插件接口 |
| `qgis.3d` | 3D 地图视图相关类 |
| `qgis.PyQt` | PyQt5/PyQt6 兼容层 |

---

## 环境准备

### 前置条件

- 安装 QGIS 3.16+（推荐 3.44 LTR）
- Python 3.9+（QGIS 自带 Python 环境）

### 在 QGIS Python 控制台中使用

打开 QGIS 桌面 → 菜单「Plugins → Python Console」，即可直接使用 PyQGIS：

```python
# QGIS 控制台中无需初始化，直接使用
layer = iface.activeLayer()
print(layer.name(), layer.featureCount())
```

### 独立脚本（Standalone Script）

在 QGIS 外部运行 Python 脚本时，需要先初始化 QGIS 应用：

```python
import sys
from qgis.core import QgsApplication

# 初始化 QGIS（False 表示不使用 GUI）
qgs = QgsApplication([], False)
qgs.setPrefixPath("/usr", True)  # Linux; Windows 示例："C:/OSGeo4W/apps/qgis"
qgs.initQgis()

# ===== 在此处编写 PyQGIS 代码 =====

# 退出
qgs.exitQgis()
```

### 独立脚本中使用 Processing

```python
import sys
from qgis.core import QgsApplication
import processing
from processing.core.Processing import Processing

qgs = QgsApplication([], False)
qgs.setPrefixPath("/usr", True)
qgs.initQgis()

# 初始化 Processing 框架
Processing.initialize()

# 现在可以使用 processing.run()
result = processing.run("native:buffer", {
    'INPUT': '/data/points.shp',
    'DISTANCE': 100,
    'OUTPUT': '/data/buffered.shp'
})

qgs.exitQgis()
```

### Headless 服务器环境

```bash
export QT_QPA_PLATFORM=offscreen
python3 my_pyqgis_script.py
```

---

## 核心类一览

### 项目与应用

| 类 | 模块 | 用途 |
|---|---|---|
| `QgsApplication` | `qgis.core` | QGIS 应用实例，初始化/退出 |
| `QgsProject` | `qgis.core` | 项目管理（单例），加载/保存项目、管理图层 |

### 矢量图层与要素

| 类 | 模块 | 用途 |
|---|---|---|
| `QgsVectorLayer` | `qgis.core` | 矢量图层（Shapefile、GeoJSON、PostGIS、内存等） |
| `QgsFeature` | `qgis.core` | 单个要素（几何 + 属性） |
| `QgsField` / `QgsFields` | `qgis.core` | 属性字段定义与集合 |
| `QgsFeatureRequest` | `qgis.core` | 要素查询过滤器（空间/属性条件） |
| `QgsVectorFileWriter` | `qgis.core` | 矢量数据写出（SHP、GPKG、GeoJSON 等） |
| `QgsVectorLayerUtils` | `qgis.core` | 矢量图层工具方法集 |
| `QgsSpatialIndex` | `qgis.core` | 空间索引，加速空间查询 |

### 栅格图层

| 类 | 模块 | 用途 |
|---|---|---|
| `QgsRasterLayer` | `qgis.core` | 栅格图层（GeoTIFF、VRT、WMS 等） |
| `QgsRasterPipe` | `qgis.core` | 栅格渲染管线 |
| `QgsRasterFileWriter` | `qgis.core` | 栅格数据写出 |

### 几何

| 类 | 模块 | 用途 |
|---|---|---|
| `QgsGeometry` | `qgis.core` | 几何对象封装（含空间操作方法） |
| `QgsPointXY` | `qgis.core` | 二维点坐标 |
| `QgsPoint` | `qgis.core` | 三维点坐标（含 Z / M） |
| `QgsRectangle` | `qgis.core` | 矩形范围（Bounding Box） |
| `QgsWkbTypes` | `qgis.core` | WKB 几何类型枚举 |
| `QgsDistanceArea` | `qgis.core` | 距离和面积计算（支持椭球面） |

### 坐标参考系与变换

| 类 | 模块 | 用途 |
|---|---|---|
| `QgsCoordinateReferenceSystem` | `qgis.core` | 坐标参考系（CRS）对象 |
| `QgsCoordinateTransform` | `qgis.core` | 坐标变换器 |
| `QgsCoordinateTransformContext` | `qgis.core` | 坐标变换上下文 |

### 表达式

| 类 | 模块 | 用途 |
|---|---|---|
| `QgsExpression` | `qgis.core` | QGIS 表达式解析与求值 |
| `QgsExpressionContext` | `qgis.core` | 表达式计算上下文 |
| `QgsExpressionContextUtils` | `qgis.core` | 创建预设表达式上下文的工具方法 |

### Processing 框架

| 类 | 模块 | 用途 |
|---|---|---|
| `processing.run()` | `qgis.processing` | **执行 Processing 算法的核心入口** |
| `QgsProcessingFeedback` | `qgis.core` | 算法执行反馈（进度、日志） |
| `QgsProcessingContext` | `qgis.core` | 算法执行上下文 |
| `QgsProcessingAlgorithm` | `qgis.core` | 自定义算法基类 |
| `QgsProcessingParameterDefinition` | `qgis.core` | 算法参数定义基类 |

### 地图渲染

| 类 | 模块 | 用途 |
|---|---|---|
| `QgsMapSettings` | `qgis.core` | 地图渲染设置（范围、CRS、图层、尺寸） |
| `QgsMapRendererSequentialJob` | `qgis.core` | 顺序渲染任务 |
| `QgsMapRendererParallelJob` | `qgis.core` | 并行渲染任务 |
| `QgsLayoutExporter` | `qgis.core` | 打印布局导出（PDF、PNG、SVG） |
| `QgsPrintLayout` | `qgis.core` | 打印布局对象 |

### 数据提供者

| Provider 名称 | 说明 | 示例 URI |
|---|---|---|
| `ogr` | OGR 矢量（SHP、GeoJSON、GPKG、FileGDB 等） | `/path/to/file.shp` |
| `gdal` | GDAL 栅格（GeoTIFF、VRT、ECW 等） | `/path/to/dem.tif` |
| `postgres` | PostgreSQL / PostGIS | `dbname='gis' host=localhost port=5432 table="public"."layer" (geom)` |
| `memory` | 内存图层 | `Point?crs=epsg:4326&field=id:integer&field=name:string(50)` |
| `wms` | WMS / WMTS 服务 | `url=https://example.com/wms&layers=dem&crs=EPSG:4326` |
| `wfs` | WFS 服务 | `url=https://example.com/wfs&typename=buildings` |
| `delimitedtext` | CSV / 分隔文本 | `file:///path/to/data.csv?delimiter=,&xField=lon&yField=lat&crs=epsg:4326` |
| `spatialite` | SpatiaLite 数据库 | `dbname='/path/to/db.sqlite' table="layer" (geometry)` |
| `virtual` | 虚拟图层（SQL 查询） | SQL 表达式 |

---

## 项目管理

### 加载与保存项目

```python
from qgis.core import QgsProject

project = QgsProject.instance()

# 读取项目
project.read("/path/to/project.qgs")

# 获取所有图层
layers = project.mapLayers()  # 返回 dict {layer_id: layer}

# 保存项目
project.write("/path/to/output.qgs")
```

### 添加/移除图层

```python
from qgis.core import QgsProject, QgsVectorLayer

project = QgsProject.instance()

layer = QgsVectorLayer("/data/roads.shp", "roads", "ogr")
if layer.isValid():
    project.addMapLayer(layer)

# 移除图层
project.removeMapLayer(layer.id())
```

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

## 坐标参考系与变换

### 创建 CRS

```python
from qgis.core import QgsCoordinateReferenceSystem

# 从 EPSG 代码
crs = QgsCoordinateReferenceSystem("EPSG:4326")

# 从 WKT
crs = QgsCoordinateReferenceSystem.fromWkt(wkt_string)

# 从 Proj 字符串
crs = QgsCoordinateReferenceSystem.fromProj4(proj4_string)

# 获取图层 CRS
crs = layer.crs()
print(crs.authid())       # "EPSG:4326"
print(crs.description())  # "WGS 84"
```

### 坐标变换

```python
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject

src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
dst_crs = QgsCoordinateReferenceSystem("EPSG:3857")

transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

# 变换单个点
point = transform.transform(QgsPointXY(116.4, 39.9))

# 变换几何
geom.transform(transform)

# 反向变换
point_back = transform.transform(point, QgsCoordinateTransform.ReverseTransform)
```

---

## 表达式

### 基本表达式求值

```python
from qgis.core import QgsExpression, QgsExpressionContext, QgsExpressionContextUtils

# 简单计算
exp = QgsExpression("1 + 2 * 3")
result = exp.evaluate()  # 7

# 基于要素的表达式
exp = QgsExpression('"population" / "area"')
context = QgsExpressionContext()
context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

for feature in layer.getFeatures():
    context.setFeature(feature)
    value = exp.evaluate(context)
    print(feature["name"], value)
```

### 过滤要素

```python
# 表达式过滤
exp = QgsExpression('"type" = \'residential\' AND "area" > 1000')
request = QgsFeatureRequest(exp)

for feature in layer.getFeatures(request):
    print(feature.attributes())
```

### 字段计算器

```python
from qgis.core import QgsExpression

layer.startEditing()

# 使用表达式批量更新字段
expression = QgsExpression('"length" * "width"')
context = QgsExpressionContext()
context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

field_index = layer.fields().indexOf("area")
for feature in layer.getFeatures():
    context.setFeature(feature)
    value = expression.evaluate(context)
    layer.changeAttributeValue(feature.id(), field_index, value)

layer.commitChanges()
```

---

## Processing 算法调用

### 基本调用

```python
import processing

# 运行缓冲区分析
result = processing.run("native:buffer", {
    'INPUT': '/data/roads.shp',
    'DISTANCE': 50,
    'SEGMENTS': 10,
    'END_CAP_STYLE': 0,      # 0=圆形, 1=平头, 2=方形
    'JOIN_STYLE': 0,          # 0=圆形, 1=斜角, 2=斜切
    'MITER_LIMIT': 2,
    'DISSOLVE': False,
    'OUTPUT': '/data/roads_buffer.shp'
})
print(result['OUTPUT'])  # 输出文件路径
```

### 带反馈对象

```python
from qgis.core import QgsProcessingFeedback

feedback = QgsProcessingFeedback()

result = processing.run("native:dissolve", {
    'INPUT': '/data/polygons.shp',
    'FIELD': ['type'],
    'OUTPUT': '/data/dissolved.gpkg'
}, feedback=feedback)
```

### 使用内存输出

```python
# OUTPUT 设为 'memory:' 前缀可得到内存图层
result = processing.run("native:buffer", {
    'INPUT': layer,
    'DISTANCE': 100,
    'OUTPUT': 'memory:buffered'
})
buffered_layer = result['OUTPUT']  # QgsVectorLayer（内存）
```

### 图层对象作为输入

```python
# 可以直接传入 QgsVectorLayer / QgsRasterLayer 对象
result = processing.run("native:clip", {
    'INPUT': input_layer,       # QgsVectorLayer 对象
    'OVERLAY': clip_layer,      # QgsVectorLayer 对象
    'OUTPUT': 'memory:clipped'
})
```

### 常用 Processing 算法

| 算法 ID | 说明 | 关键参数 |
|---------|------|---------|
| `native:buffer` | 缓冲区 | INPUT, DISTANCE, SEGMENTS, DISSOLVE |
| `native:clip` | 矢量裁剪 | INPUT, OVERLAY |
| `native:dissolve` | 融合 | INPUT, FIELD |
| `native:intersection` | 交集 | INPUT, OVERLAY |
| `native:union` | 联合 | INPUT, OVERLAY |
| `native:difference` | 差集 | INPUT, OVERLAY |
| `native:centroids` | 质心 | INPUT |
| `native:reprojectlayer` | 重投影 | INPUT, TARGET_CRS |
| `native:mergevectorlayers` | 合并图层 | LAYERS |
| `native:fixgeometries` | 修复几何 | INPUT |
| `native:extractbyattribute` | 按属性提取 | INPUT, FIELD, OPERATOR, VALUE |
| `native:extractbylocation` | 按位置提取 | INPUT, INTERSECT, PREDICATE |
| `native:joinattributesbylocation` | 空间连接 | INPUT, JOIN, PREDICATE, METHOD |
| `native:fieldcalculator` | 字段计算器 | INPUT, FIELD_NAME, FORMULA |
| `gdal:cliprasterbyextent` | 栅格按范围裁剪 | INPUT, EXTENT |
| `gdal:cliprasterbymask` | 栅格按掩膜裁剪 | INPUT, MASK |
| `gdal:warpreproject` | 栅格重投影 | INPUT, TARGET_CRS |
| `gdal:merge` | 栅格合并 | INPUT |
| `gdal:contour` | 等值线提取 | INPUT, INTERVAL |
| `gdal:polygonize` | 栅格转矢量 | INPUT |
| `gdal:rasterize` | 矢量转栅格 | INPUT, FIELD |

### 查询可用算法

```python
# 在 QGIS 控制台中列出所有算法
for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id(), "-", alg.displayName())

# 搜索算法
for alg in QgsApplication.processingRegistry().algorithms():
    if 'buffer' in alg.id().lower():
        print(alg.id(), alg.displayName())
```

---

## 地图渲染与导出

### 渲染为图片

```python
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

image = job.renderedImage()
image.save("/data/map_output.png")
```

### 使用打印布局导出 PDF

```python
from qgis.core import (
    QgsProject, QgsPrintLayout, QgsLayoutItemMap,
    QgsLayoutExporter, QgsLayoutSize, QgsUnitTypes
)

project = QgsProject.instance()
layout = QgsPrintLayout(project)
layout.initializeDefaults()

# 添加地图项
map_item = QgsLayoutItemMap(layout)
map_item.setRect(20, 20, 200, 150)
map_item.setExtent(layer.extent())
map_item.setLayers([layer])
layout.addLayoutItem(map_item)

# 导出 PDF
exporter = QgsLayoutExporter(layout)
pdf_settings = QgsLayoutExporter.PdfExportSettings()
exporter.exportToPdf("/data/output.pdf", pdf_settings)
```

---

## 典型工作流示例

### 示例 1：矢量格式转换（SHP → GeoPackage）

```python
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsProject

layer = QgsVectorLayer("/data/input.shp", "input", "ogr")

options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "GPKG"
options.fileEncoding = "UTF-8"

QgsVectorFileWriter.writeAsVectorFormatV3(
    layer,
    "/data/output.gpkg",
    QgsProject.instance().transformContext(),
    options
)
```

### 示例 2：批量缓冲区 + 融合

```python
import processing

# 缓冲区
result1 = processing.run("native:buffer", {
    'INPUT': '/data/points.shp',
    'DISTANCE': 500,
    'SEGMENTS': 16,
    'OUTPUT': 'memory:buffered'
})

# 融合
result2 = processing.run("native:dissolve", {
    'INPUT': result1['OUTPUT'],
    'OUTPUT': '/data/dissolved.gpkg'
})
```

### 示例 3：坐标系转换 + 属性过滤

```python
import processing

# 重投影到 CGCS2000
result1 = processing.run("native:reprojectlayer", {
    'INPUT': '/data/input_wgs84.shp',
    'TARGET_CRS': 'EPSG:4490',
    'OUTPUT': 'memory:reprojected'
})

# 按属性提取
result2 = processing.run("native:extractbyattribute", {
    'INPUT': result1['OUTPUT'],
    'FIELD': 'type',
    'OPERATOR': 0,  # 0=等于
    'VALUE': 'road',
    'OUTPUT': '/data/roads_cgcs2000.gpkg'
})
```

### 示例 4：栅格裁剪 + 坡度分析

```python
import processing

# 按掩膜裁剪 DEM（栅格算法使用 TEMPORARY_OUTPUT 生成临时文件）
result1 = processing.run("gdal:cliprasterbymask", {
    'INPUT': '/data/dem.tif',
    'MASK': '/data/boundary.shp',
    'OUTPUT': 'TEMPORARY_OUTPUT'  # 栅格输出不支持 memory:，使用 TEMPORARY_OUTPUT 创建临时文件
})

# 坡度分析
result2 = processing.run("gdal:slope", {
    'INPUT': result1['OUTPUT'],
    'OUTPUT': '/data/slope.tif'
})
```

### 示例 5：从 CSV 创建矢量图层并导出

```python
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsProject

# 从 CSV 加载（指定经纬度字段）
uri = "file:///data/stations.csv?delimiter=,&xField=longitude&yField=latitude&crs=epsg:4326"
layer = QgsVectorLayer(uri, "stations", "delimitedtext")

if layer.isValid():
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GeoJSON"
    QgsVectorFileWriter.writeAsVectorFormatV3(
        layer,
        "/data/stations.geojson",
        QgsProject.instance().transformContext(),
        options
    )
```

### 示例 6：独立脚本完整示例

```python
"""独立 PyQGIS 脚本：加载 SHP、缓冲区分析、导出 GeoJSON"""
import sys
from qgis.core import (
    QgsApplication, QgsVectorLayer, QgsProject
)
import processing
from processing.core.Processing import Processing

# 初始化
qgs = QgsApplication([], False)
qgs.setPrefixPath("/usr", True)
qgs.initQgis()
Processing.initialize()

# 加载数据
layer = QgsVectorLayer("/data/buildings.shp", "buildings", "ogr")
assert layer.isValid(), "图层加载失败"

# 缓冲区分析
result = processing.run("native:buffer", {
    'INPUT': layer,
    'DISTANCE': 200,
    'OUTPUT': '/data/buildings_buffer.geojson'
})

print(f"输出文件: {result['OUTPUT']}")

# 退出
qgs.exitQgis()
```

---

## AI 使用建议

### 推荐工作流

1. **初始化环境**：独立脚本需 `QgsApplication` 初始化；QGIS 控制台中可直接使用
2. **加载数据**：使用 `QgsVectorLayer` / `QgsRasterLayer` 加载数据源
3. **执行分析**：优先使用 `processing.run()` 调用算法（参数统一、算法丰富）；精细操作使用 `QgsGeometry` 方法
4. **导出结果**：使用 `QgsVectorFileWriter` 写出矢量，`QgsRasterFileWriter` 写出栅格
5. **清理退出**：独立脚本调用 `qgs.exitQgis()`

### 关键注意事项

1. **始终检查图层有效性**：加载图层后必须检查 `layer.isValid()`，无效时检查路径和 Provider。
2. **坐标系一致性**：空间运算前确保所有图层使用相同 CRS；使用 `native:reprojectlayer` 或 `QgsCoordinateTransform` 进行转换。
3. **编辑模式**：修改图层数据需 `startEditing()` → 操作 → `commitChanges()`；失败可 `rollBack()`。
4. **Processing 内存输出**：将 OUTPUT 设为 `'memory:name'` 可得到内存图层，避免创建临时文件。
5. **椭球面计算**：对地理坐标（经纬度）计算距离/面积时，使用 `QgsDistanceArea` 并设置椭球体，或使用 Processing 算法指定椭球体。
6. **Headless 环境**：无显示器的服务器上必须设置 `QT_QPA_PLATFORM=offscreen`。
7. **文件路径使用绝对路径**：避免工作目录不确定导致文件找不到。
8. **大数据量优化**：使用 `QgsSpatialIndex` 加速空间查询；使用 `QgsFeatureRequest` 限制返回字段和范围。
9. **表达式语法**：字段名用双引号 `"field"`，字符串值用单引号 `'value'`。
10. **QGIS 版本兼容**：部分 API 在不同版本间有变化，建议使用 3.44 LTR 以获得稳定接口。

### 错误处理

```python
# 图层加载失败
layer = QgsVectorLayer(path, name, provider)
if not layer.isValid():
    print(f"图层加载失败: {layer.error().message()}")

# Processing 算法错误
try:
    result = processing.run("native:buffer", params, feedback=feedback)
except Exception as e:
    print(f"算法执行失败: {e}")

# 编辑提交失败
if not layer.commitChanges():
    errors = layer.commitErrors()
    print(f"提交失败: {errors}")
    layer.rollBack()
```

---

## 参考链接

- **QGIS 源码仓库：** <https://github.com/qgis/QGIS>
- **PyQGIS 开发者手册（3.44）：** <https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/>
- **PyQGIS API 参考（3.44）：** <https://qgis.org/pyqgis/3.44/>
- **QGIS 文档仓库：** <https://github.com/qgis/QGIS-Documentation>
- **QGIS 用户手册：** <https://docs.qgis.org/3.44/en/docs/user_manual/>
- **PyQGIS 速查表：** <https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/cheat_sheet.html>
