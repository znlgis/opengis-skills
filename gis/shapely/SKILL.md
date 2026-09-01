---
name: shapely
description: "Use when performing computational geometry in Python — intersection, union, buffer, convex hull, simplification. Shapely: Python bindings for GEOS, the C++ geometry engine that powers PostGIS."
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

**环境要求：** Python 3.9+，Shapely 2.0+

---

## Geometry Types

| Type | Class | Description |
|------|-------|-------------|
| Point | `shapely.Point` | Single coordinate (x, y [, z [, m]]) |
| LineString | `shapely.LineString` | Ordered sequence of 2+ points |
| LinearRing | `shapely.LinearRing` | Closed, simple LineString |
| Polygon | `shapely.Polygon` | Exterior ring + optional holes |
| MultiPoint | `shapely.MultiPoint` | Collection of Points |
| MultiLineString | `shapely.MultiLineString` | Collection of LineStrings |
| MultiPolygon | `shapely.MultiPolygon` | Collection of Polygons |
| GeometryCollection | `shapely.GeometryCollection` | Heterogeneous collection |

Z coordinates are **ignored for all spatial analysis** — operations are performed in the x-y plane only.

## Dual API Pattern

Shapely provides two APIs. Prefer the **function-based API** for arrays and performance; use the **OOP API** for scalar convenience.

### Function-based (vectorized, NumPy ufunc)

All functions release the GIL during GEOS execution, support NumPy broadcasting, and handle arrays natively.

```python
import shapely
import numpy as np

geoms = np.array([shapely.Point(0, 0), shapely.Point(1, 1)])
shapely.area(geoms)                    # array of floats
shapely.contains(polygon, geoms)       # array of bools
shapely.buffer(geoms, 1.0)            # array of polygons
shapely.distance(geoms, other)        # array of distances
```

### OOP (method-based, scalar)

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

### Operator overloading

```python
geom1 & geom2    # intersection
geom1 | geom2    # union
geom1 - geom2    # difference
geom1 ^ geom2    # symmetric_difference
```

## Geometry Creation

### From coordinates (OOP)

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

### From coordinates (vectorized)

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

### From serialization formats

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

### From/to GeoJSON-like dict (`__geo_interface__`)

```python
from shapely.geometry import shape, mapping

geom = shape({"type": "Point", "coordinates": [0, 0]})
d = mapping(geom)  # {"type": "Point", "coordinates": (0.0, 0.0)}
```

> 构造操作、空间谓词、集合运算、测量、空间索引、仿射与坐标变换及线性参考的完整 API 见 [reference/operations-reference.md](reference/operations-reference.md)

## Validation

```python
shapely.is_valid(geom)
shapely.is_valid_reason(geom)
shapely.make_valid(geom, method="linework")   # or "structure"
```

## Prepared Geometry

Caches spatial index for repeated predicate tests against the same geometry.

```python
shapely.prepare(geom)            # in-place, returns True if newly prepared
shapely.destroy_prepared(geom)   # free cache
shapely.is_prepared(geom)
```

## Missing Values

`None` represents missing geometries. Consistent behavior:
- Predicates return `False`
- Measurements return `nan`
- Constructive operations return `None`

Use `shapely.is_missing(obj)` to check, distinct from `shapely.is_empty(geom)`.

## Important Caveats

1. **Z ignored in analysis**: All spatial operations work in x-y plane only. Geometries with different z values may still intersect or be equal.

2. **`contains` excludes boundary**: `contains(line, endpoint)` is `False`. Use `covers()` or `intersects()` if you need boundary inclusion.

3. **`set_coordinates` modifies in-place**: Copy geometry first with `.copy()` if originals must be preserved.

4. **`clip_by_rect` may produce invalid output**: The fast clip is not guaranteed to yield valid topology.

5. **WKB drops LinearRing**: LinearRings become LineStrings during WKB serialization.

6. **`to_geojson` drops Z**: Third dimension is silently discarded; LinearRing outputs as `null`.

7. **OOP vs function `buffer` defaults differ**: `Point(0,0).buffer(1)` uses `quad_segs=16`; `shapely.buffer(Point(0,0), 1)` uses `quad_segs=8`.

8. **`set_precision` changes vertex order**: Returned geometry is in "mild canonical form" — vertex order should not be relied upon.

9. **NaN coordinates**: Creating geometries with NaN/Inf is allowed by default. Use `handle_nan='error'` or `handle_nan='skip'` in creation functions to control this.

10. **Prepared state not preserved**: After any operation producing a new geometry, `prepare()` must be called again.

11. **GEOS version gates**: `concave_hull`, `constrained_delaunay_triangles`, `remove_repeated_points` require GEOS >= 3.11. `coverage_simplify`, `has_m`, `get_m` require GEOS >= 3.12.

## Common Patterns

### Point-in-polygon test for many points
```python
from shapely import STRtree, points

pts = points(np.random.rand(10000, 2))
tree = STRtree(pts)
idx = tree.query(polygon, predicate="intersects")
inside_points = pts[idx]
```

### Batch union of many polygons
```python
result = shapely.union_all(polygon_array)
```

### Coordinate projection (e.g., with pyproj)
```python
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

def project(coords):
    x, y = transformer.transform(coords[:, 0], coords[:, 1])
    return np.column_stack([x, y])

projected = shapely.transform(geom, project)
```

### Extract all coordinates from mixed geometries
```python
coords = shapely.get_coordinates(geom_array, include_z=False)
# coords shape: (N, 2)
```

### Spatial join pattern
```python
tree = STRtree(right_geoms)
left_idx, right_idx = tree.query(left_geoms, predicate="intersects")
# left_idx[i] and right_idx[i] are paired matches
```

## AI 使用建议

### 推荐工作流

1. **创建几何**：使用 `shapely.points()` / `shapely.linestrings()` / `shapely.polygons()` 向量化创建，或 `Point()` / `LineString()` / `Polygon()` OOP 方式
2. **空间运算**：使用向量化函数（`shapely.intersection()` / `shapely.buffer()`）批量处理，比逐个 OOP 调用快 10-100 倍
3. **空间谓词**：使用 `shapely.contains()` / `shapely.intersects()` 等函数式 API，返回 bool 数组
4. **空间索引**：`STRtree` 查询 + `predicate="intersects"` 加速批量空间关系判断
5. **序列化**：`shapely.from_wkt()` / `shapely.to_geojson()` 等进行格式互转

### 关键注意事项

- **Z 坐标在分析中被忽略**：所有空间运算仅在 x-y 平面进行
- **`contains` 不包含边界**：如需边界判断使用 `covers()` 或 `intersects()`
- **向量化函数 vs OOP 方法**：函数式 API（`shapely.area(geoms)`）释放 GIL，支持 NumPy 广播，性能远优于 OOP（`geom.area`）
- **`set_precision` 改变顶点顺序**：返回的几何为"温和规范形式"，不应依赖顶点顺序
- **Prepared 状态不持久**：任何操作产生新几何后需重新 `prepare()`
- **WKB 会丢弃 LinearRing**：WKB 序列化时 LinearRing 变为 LineString

---

$h$faq`

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

---

## 相关技能

- **geopandas** — 基于 Shapely 的矢量数据分析库：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **pyqgis** — QGIS Python 绑定（也使用 GEOS/QgsGeometry）：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **jts** — Java 几何计算（Shapely 的 GEOS 底层是 JTS 的 C++ 移植）：[../jts/SKILL.md](../jts/SKILL.md)
- **gdal** — 命令行数据处理：[../gdal/SKILL.md](../gdal/SKILL.md)

## Package Structure

```
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

## 参考资源

- **GitHub 仓库：** <https://github.com/shapely/shapely>
- **官方文档：** <https://shapely.readthedocs.io/>
- **API 参考：** <https://shapely.readthedocs.io/en/stable/reference.html>
- **PyPI：** <https://pypi.org/project/shapely/>
- **GEOS（底层 C++ 引擎）：** <https://libgeos.org/>
- **上游中文教程：** <https://znlgis.github.io/gis/tutorial/shapely/>
