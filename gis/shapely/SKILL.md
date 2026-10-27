---
name: shapely
description: "Use when doing computational geometry in Python — shapely.intersection/union/buffer/convex_hull/simplify, STRtree queries, from_wkt/to_wkt/to_geojson, make_valid, GEOS-gated ops (coverage_clean, split); also for TopologyException on self-intersecting polygons or OOP vs function buffer quad_segs mismatch. Shapely 2.2.0 binds GEOS."
tags:
  - python
  - geometry
  - geos
  - wkt
  - wkb
  - geojson
  - spatial
  - numpy
---

> **项目地址：** <https://github.com/shapely/shapely>
>
> **官方文档：** <https://shapely.readthedocs.io/>
>
> **PyPI：** <https://pypi.org/project/shapely/>
>
> **包管理器：** `shapely`（最新 2.2.0，截至 2026-10，PyPI）
>
> **许可证：** BSD-3-Clause

## 概述

Shapely 是 Python 计算几何的核心库，基于 GEOS（Geometry Engine - Open Source）的 C++ 几何引擎。它为 PostGIS、GeoPandas、PyQGIS 等众多开源 GIS 项目提供几何计算底层支持。核心能力：

- **几何对象模型**：Point、LineString、Polygon、Multi*、GeometryCollection
- **空间关系判断**：contains、intersects、within、touches、covers、disjoint、relate（DE-9IM）
- **集合运算**：intersection、union、difference、symmetric_difference
- **构造操作**：buffer、simplify、convex_hull、delaunay_triangles、voronoi_polygons、make_valid
- **几何度量**：area、length、distance、hausdorff_distance、frechet_distance
- **空间索引**：STRtree，加速批量空间查询
- **格式读写**：WKT、WKB、GeoJSON
- **双重 API**：函数式（向量化，支持 NumPy 广播）+ OOP（标量便捷）

**环境要求：** Python 3.11+（Shapely 2.2 起；2.1 为 3.10+），NumPy >= 1.26，GEOS >= 3.10。PyPI 二进制 wheel 内含 GEOS 3.14。

---

## 环境准备

```bash
# pip（含预编译 GEOS 的 wheel）
pip install shapely

# Conda / Mamba
# 推荐使用 conda-forge/miniforge 发行版（比 Anaconda 轻量）
conda install -c conda-forge shapely

# 验证
python -c "import shapely; print(shapely.__version__, shapely.geos_version)"
```

---

## 几何类型

| 类型 | 类 | 说明 |
|------|-------|-------------|
| Point | `shapely.Point` | 单个坐标 (x, y [, z [, m]]) |
| LineString | `shapely.LineString` | 由 2 个以上点组成的有序序列 |
| LinearRing | `shapely.LinearRing` | 闭合的简单 LineString |
| Polygon | `shapely.Polygon` | 外环 + 可选内环（洞） |
| MultiPoint | `shapely.MultiPoint` | 点集合 |
| MultiLineString | `shapely.MultiLineString` | 线集合 |
| MultiPolygon | `shapely.MultiPolygon` | 面集合 |
| GeometryCollection | `shapely.GeometryCollection` | 异构几何集合 |

**所有空间分析都忽略 Z 值** —— 运算只在 x-y 平面进行。

## 双 API 模式

Shapely 提供两套 API：处理数组、追求性能时优先用**函数式 API**，只做单个几何的便捷操作时用**面向对象 API**。

### 函数式 API（向量化，NumPy ufunc）

这些函数在 GEOS 运算期间释放 GIL，支持 NumPy 广播，并原生处理数组。

```python
import shapely
import numpy as np

geoms = np.array([shapely.Point(0, 0), shapely.Point(1, 1)])
shapely.area(geoms)                    # array of floats
shapely.contains(polygon, geoms)       # array of bools
shapely.buffer(geoms, 1.0)            # array of polygons
shapely.distance(geoms, other)        # array of distances
```

### 面向对象 API（方法式，标量）

```python
from shapely import Point, Polygon

p = Point(0, 0)
poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
p.buffer(10)
p.distance(Point(1, 1))
poly.area                  # property
poly.contains(p)
poly.intersection(other)
```

### 运算符重载

```python
geom1 & geom2    # intersection
geom1 | geom2    # union
geom1 - geom2    # difference
geom1 ^ geom2    # symmetric_difference
```

## 几何对象创建

### 从坐标创建（面向对象）

```python
from shapely import Point, LineString, LinearRing, Polygon
from shapely import MultiPoint, MultiLineString, MultiPolygon, GeometryCollection

Point(0, 0)
Point(0, 0, 5)                                    # 3D
LineString([(0, 0), (1, 1), (2, 0)])
LinearRing([(0, 0), (1, 0), (1, 1), (0, 0)])      # must be closed
Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])         # auto-closes shell
Polygon(shell_coords, [hole1_coords, hole2_coords])
MultiPoint([(0, 0), (1, 1)])
MultiLineString([[(0, 0), (1, 1)], [(2, 2), (3, 3)]])
MultiPolygon([poly1, poly2])
GeometryCollection([point, line, poly])
```

### 从坐标创建（向量化）

```python
import shapely

shapely.points([[0, 1], [2, 3]])                  # array of Points
shapely.points(0, 1)                               # scalar Point
shapely.linestrings([[[0, 0], [1, 1]], [[2, 2], [3, 3]]])
shapely.linearrings([[0, 0], [1, 0], [1, 1]])     # auto-closes
shapely.polygons(shell, holes=[hole1, hole2])
shapely.box(xmin, ymin, xmax, ymax)               # rectangle(s)
shapely.multipoints([pt1, pt2])
shapely.multilinestrings(...)
shapely.multipolygons(...)
shapely.geometrycollections(...)
```

### 从序列化格式创建

```python
# WKT
shapely.from_wkt("POINT (0 0)")
shapely.to_wkt(geom, rounding_precision=6, trim=True)

# WKB
shapely.from_wkb(b'\x01\x01...')
shapely.to_wkb(geom, hex=False, flavor="extended")

# GeoJSON
shapely.from_geojson('{"type":"Point","coordinates":[0,0]}')
shapely.to_geojson(geom, indent=None)

# GeoArrow ragged arrays
shapely.from_ragged_array(geometry_type, coords, offsets)
shapely.to_ragged_array(geometries)
```

### 与 GeoJSON 字典互转（`__geo_interface__`）

```python
from shapely.geometry import shape, mapping

geom = shape({"type": "Point", "coordinates": [0, 0]})
d = mapping(geom)  # {"type": "Point", "coordinates": (0.0, 0.0)}
```

> 构造操作、空间谓词、集合运算、测量、空间索引、仿射与坐标变换及线性参考的完整 API 见 [reference/operations-reference.md](reference/operations-reference.md)

## 有效性校验

```python
shapely.is_valid(geom)
shapely.is_valid_reason(geom)
shapely.make_valid(geom, method="linework")   # or "structure"
```

## 预处理几何（Prepared Geometry）

为同一几何的重复谓词判断缓存空间索引。

```python
shapely.prepare(geom)            # in-place, returns True if newly prepared
shapely.destroy_prepared(geom)   # free cache
shapely.is_prepared(geom)
```

## 缺失值

`None` 表示缺失几何，各函数行为保持一致：
- 谓词返回 `False`
- 度量返回 `nan`
- 构造类操作返回 `None`

用 `shapely.is_missing(obj)` 判断，注意它与 `shapely.is_empty(geom)`（空几何）不同。

## 重要注意事项

1. **分析中忽略 Z 值**：所有空间运算只在 x-y 平面进行，Z 值不同的几何仍可能相交或相等。

2. **`contains` 不含边界**：`contains(line, endpoint)` 为 `False`；需要把边界算在内时用 `covers()` 或 `intersects()`。

3. **`set_coordinates` 原地修改**：需保留原几何时，先 `.copy()`。

4. **`clip_by_rect` 可能产出无效几何**：这个快速裁剪不保证拓扑有效。

5. **WKB 丢失 LinearRing**：LinearRing 在 WKB 序列化时变成 LineString。

6. **`to_geojson` 丢弃 Z**：第三维被静默丢弃，LinearRing 输出为 `null`。

7. **面向对象与函数式 `buffer` 默认值不同**：`Point(0,0).buffer(1)` 用 `quad_segs=16`，`shapely.buffer(Point(0,0), 1)` 用 `quad_segs=8`。

8. **`set_precision` 改变顶点顺序**：返回几何处于"轻度规范化"形式，不要依赖其顶点顺序。

9. **NaN 坐标**：默认允许用 NaN/Inf 构造几何；需要控制时在创建函数里传 `handle_nan='error'` 或 `handle_nan='skip'`。

10. **预处理状态不保留**：任何产生新几何的运算之后，都要重新调用 `prepare()`。

11. **GEOS 版本门槛**：`concave_hull`、`constrained_delaunay_triangles`、`remove_repeated_points` 需 GEOS >= 3.11；`coverage_simplify`、`has_m`、`get_m` 需 GEOS >= 3.12；`coverage_clean` 需 GEOS >= 3.14；顶层 `split` 需 GEOS >= 3.15（低版本自动回退到 `shapely.ops.split`）。

12. **`shapely.ops.transform` 已弃用**：2.2 起改用 `shapely.transform`（按坐标逐点）或 `shapely.transform_coordseq`（按坐标序列）；`multithreading_enabled` 装饰器同样已弃用。

## 典型工作流

端到端：WKT 读入 → 有效性修复 → 裁剪/缓冲 → 写回 GeoJSON，全程用函数式 API。

```python
import json
import numpy as np
import shapely

# 1. 读入输入几何（WKT 或 WKB）
parcels = shapely.from_wkt([
    "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))",
    "POLYGON ((20 20, 30 30, 30 20, 20 30, 20 20))",   # 自相交的"蝴蝶结"，无效
])
clip_poly = shapely.from_wkt("POLYGON ((5 5, 25 5, 25 25, 5 25, 5 5))")

# 2. 先查有效性，无效的再修复（不要盲目 buffer(0)）
print(shapely.is_valid(parcels))                       # [True False]
print(shapely.is_valid_reason(parcels[1]))             # Self-intersection[25 25]
parcels = np.where(shapely.is_valid(parcels), parcels,
                   shapely.make_valid(parcels))        # 无效的那个变成 MultiPolygon

# 3. 空间运算：裁剪 + 缓冲区
clipped = shapely.intersection(parcels, clip_poly)
buffered = shapely.buffer(clipped, 1.0, quad_segs=8)   # 显式指定 quad_segs

# 4. 度量（示例坐标无投影，面积即平面面积）
print(shapely.area(clipped))                            # 每个几何的面积数组

# 5. 写出 GeoJSON（FeatureCollection）
features = [
    {"type": "Feature", "properties": {"id": int(i)},
     "geometry": json.loads(shapely.to_geojson(g))}
    for i, g in enumerate(buffered) if not shapely.is_empty(g)
]
with open("clipped.geojson", "w", encoding="utf-8") as fh:
    json.dump({"type": "FeatureCollection", "features": features}, fh)
```

**输出与验收**：`clipped.geojson` 中每个 Feature 都能被 `shapely.from_geojson()` 重新读入；`shapely.is_valid()` 全为 `True`；面积量级应与输入量级同阶（若用经纬度坐标，先投影再算，见下）。

## 常用模式

### 大批量点落在面内判断
```python
import numpy as np
import shapely
from shapely import STRtree, points

rng = np.random.default_rng(0)
pts = points(rng.random((10000, 2)))
polygon = shapely.box(0.2, 0.2, 0.6, 0.6)      # 待查询的面

tree = STRtree(pts)                             # 索引点集
idx = tree.query(polygon, predicate="intersects")
inside_points = pts[idx]                        # 落面内的点
```

### 批量合并大量多边形
```python
import shapely

result = shapely.union_all(polygon_array)
```

### 坐标投影（配合 pyproj）
```python
import numpy as np
import shapely
from pyproj import Transformer

transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

def project(coords):
    x, y = transformer.transform(coords[:, 0], coords[:, 1])
    return np.column_stack([x, y])

projected = shapely.transform(geom, project)
```

### 从混合几何中提取全部坐标
```python
import shapely

coords = shapely.get_coordinates(geom_array, include_z=False)
# coords shape: (N, 2)
```

### 空间连接模式
```python
from shapely import STRtree

tree = STRtree(right_geoms)
left_idx, right_idx = tree.query(left_geoms, predicate="intersects")
# left_idx[i] and right_idx[i] are paired matches
```

## 常见问题

| 问题 | 解决 |
|------|------|
| 面积/距离为 0 或极小 | CRS 为地理坐标系（度），需要投影到投影坐标系再计算 |
| `contains` 对边界上的点返回 False | 使用 `covers()` 或 `intersects()` 代替 |
| 几何操作产生 TopologyException | 几何无效，用 `make_valid()` 修复后再操作 |
| OOP 和函数式 API 结果不一致 | `buffer` 默认 `quad_segs` 不同（OOP=16，函数式=8），显式指定即可 |
| `None` 参与运算报错 | 使用 `shapely.is_missing()` 先检查，或过滤掉 `None` 再运算 |
| STRtree 查询返回空数组 | 检查几何是否 `None`/`Empty`；确认查询几何与索引几何的 CRS 一致 |
| WKB 序列化丢失 LinearRing | WKB 规范不支持 LinearRing，会自动转为 LineString |
| `to_geojson` 丢失 Z 坐标 | GeoJSON 标准不支持 Z，改用 WKB 或自定义序列化 |
| `shapely.ops.transform` 弃用警告 | 2.2 起弃用，改用 `shapely.transform` 或 `shapely.transform_coordseq` |

---

## AI 使用建议

- **本技能的组织**：主文件给高频用法，完整参数表与高级示例在 `reference/operations-reference.md`，需要时再展开；示例工程与生成的数据写到工作目录，不要改动技能目录本身。
- **执行环境**：命令在终端 / shell 中执行（Windows 用 PowerShell）；`python` 不一定是 QGIS/GDAL 自带环境，先 `python -c "import sys; print(sys.executable, sys.version)"`。
- **先探测版本**：`python -c "import shapely; print(shapely.__version__, shapely.geos_version)"`；本技能按 2.2.0 编写，PyPI wheel 内含 GEOS 3.14。GEOS 低版本请按第 11 条降级（如 `coverage_clean` 需 3.14、`shapely.split` 需 3.15）。
- **验证产物（必做）**：`print(shapely.is_valid(g), shapely.is_valid_reason(g))` 报无效原因；面积/长度做量级断言；序列化回读 `shapely.from_wkt(shapely.to_wkt(g, rounding_precision=-1)).equals(g)`，改过几何后再核对一次 `geom_type` 与 `get_num_geometries()`。
- **报错先查有效性**：`TopologyException: side location conflict` 基本都是输入几何自相交，先 `shapely.make_valid(g)`（可指定 `method="structure"`）再算，不要直接加 `buffer(0)`。
- **性能与内存**：批量操作走向量化函数（`shapely.union_all`、`shapely.buffer(geoms, r)`），别逐条 OOP 循环；十万级以上几何先 `STRtree(geoms)` 过滤，再对小集合做精确谓词。
- **典型误操**：`set_coordinates()`/`shapely.prepare()` 都是原地修改，先 `.copy()`；`shapely.buffer` 默认 `quad_segs=8` 与 `Point.buffer()` 的 16 不同，比较结果前显式传参。
- **安全**：`pip install shapely` 前先征得用户同意；输出 WKT/坐标前确认数据是否敏感（精确坐标可反推位置），大几何 dump 到文件再分段读，别刷屏。

---

## 包结构

```text
shapely/
├── __init__.py              # Top-level re-exports
├── geometry/                # OOP geometry classes
│   ├── base.py              # BaseGeometry (all methods/properties)
│   ├── point.py, linestring.py, polygon.py
│   ├── multipoint.py, multilinestring.py, multipolygon.py
│   ├── collection.py        # GeometryCollection
│   └── geo.py               # shape(), mapping(), box()
├── constructive.py          # buffer, simplify, hull, etc.
├── predicates.py            # contains, intersects, etc.
├── set_operations.py        # union, intersection, difference, etc.
├── measurement.py           # area, length, distance, bounds
├── creation.py              # points(), linestrings(), polygons(), box()
├── coordinates.py           # transform, get/set_coordinates
├── io.py                    # from/to WKT, WKB, GeoJSON
├── strtree.py               # STRtree spatial index
├── linear.py                # line_interpolate_point, line_merge, etc.
├── affinity.py              # rotate, scale, skew, translate
├── validation.py            # make_valid
├── prepared.py              # PreparedGeometry
├── ops.py                   # Legacy: split, nearest_points, etc.
├── algorithms/              # polylabel, oriented_envelope fallback
└── plotting.py              # Matplotlib helpers (experimental)
```

---

## 相关技能

- **geopandas** — 基于 Shapely 的矢量数据分析库：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **pyqgis** — QGIS Python 绑定（也使用 GEOS/QgsGeometry）：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **jts** — Java 几何计算（Shapely 的 GEOS 底层是 JTS 的 C++ 移植）：[../jts/SKILL.md](../jts/SKILL.md)
- **gdal** — 命令行数据处理：[../gdal/SKILL.md](../gdal/SKILL.md)

---

## 参考资源

- **GitHub 仓库：** <https://github.com/shapely/shapely>
- **官方文档：** <https://shapely.readthedocs.io/>
- **API 参考：** <https://shapely.readthedocs.io/en/stable/manual.html>
- **PyPI：** <https://pypi.org/project/shapely/>
- **GEOS（底层 C++ 引擎）：** <https://libgeos.org/>
- **上游中文教程：** <https://znlgis.github.io/gis/tutorial/shapely/>
