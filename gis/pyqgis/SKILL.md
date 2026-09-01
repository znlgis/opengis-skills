---
name: pyqgis
description: "Use when extending QGIS with Python plugins, automating map composition, or scripting QGIS processing algorithms. PyQGIS: QGIS Python API for custom tools, processing scripts, and plugin development."
tags:
  - python
  - qgis
  - gis
  - processing
  - vector
  - raster
  - rendering
  - plugin
---

> **项目地址：** <https://github.com/qgis/QGIS>
>
> **开发者手册：** <https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/>
>
> **Python API 参考：** <https://qgis.org/pyqgis/3.44/>
>
> **许可证：** GPL-2.0+

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

- 安装 QGIS 3.16+（[查看 QGIS LTR/最新版](https://qgis.org/download/)）
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

> 矢量图层与栅格图层操作的完整 API 与示例见 [reference/vector-raster-layers.md](reference/vector-raster-layers.md)

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

> Processing 算法调用、地图渲染与导出、典型工作流示例见 [reference/processing-rendering.md](reference/processing-rendering.md)

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
10. **QGIS 版本兼容**：部分 API 在不同版本间有变化，建议使用 LTR 版本（[查看当前 LTR](https://qgis.org/download/)）以获得稳定接口；QGIS 4.2.0 已于 2026-07 发布为稳定版，3.44 LTR 仍受支持。

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

## 相关技能

- **qgis-process** — QGIS 命令行处理工具：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **gdal** — 命令行数据处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **geopandas** — Python 矢量数据处理：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **shapely** — Python 几何计算核心：[../shapely/SKILL.md](../shapely/SKILL.md)
- **geopipe-agent** — AI 原生分析流水线：[../geopipe-agent/SKILL.md](../geopipe-agent/SKILL.md)

## 参考资源

- **QGIS 源码仓库：** <https://github.com/qgis/QGIS>
- **PyQGIS 开发者手册（3.44）：** <https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/>
- **PyQGIS API 参考（3.44）：** <https://qgis.org/pyqgis/3.44/>
- **QGIS 文档仓库：** <https://github.com/qgis/QGIS-Documentation>
- **QGIS 用户手册：** <https://docs.qgis.org/3.44/en/docs/user_manual/>
- **PyQGIS 速查表：** <https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/cheat_sheet.html>
