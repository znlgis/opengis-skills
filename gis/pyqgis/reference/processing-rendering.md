# PyQGIS Processing, Rendering and Workflows Reference

Processing algorithm invocation, map rendering/export and typical workflow examples split from SKILL.md.

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

