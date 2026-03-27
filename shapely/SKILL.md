---
name: shapely
description: Shapely 是 Python 平台上广泛使用的开源二维平面几何操作与分析库，基于 GEOS 引擎，提供几何对象创建、空间关系判断、集合运算、几何分析以及多种格式序列化能力，并支持 NumPy 向量化批量操作与多线程并行计算。
---

> **项目地址：** <https://github.com/shapely/shapely>
>
> **PyPI：** <https://pypi.org/project/shapely/>
>
> **文档：** <https://shapely.readthedocs.io/>
>
> **许可证：** BSD 3-Clause License

## 概述

Shapely 是一个基于 [GEOS](https://libgeos.org/)（PostGIS 的几何引擎、JTS 的 C/C++ 移植版）的 Python 二维平面几何操作库。它提供：

- **几何对象模型**：Point、LineString、LinearRing、Polygon、MultiPoint、MultiLineString、MultiPolygon、GeometryCollection
- **空间关系判断**：equals、contains、within、intersects、touches、crosses、overlaps、disjoint、covers、covered_by、relate（DE-9IM）
- **集合运算**：intersection、union、difference、symmetric_difference、buffer
- **几何分析**：convex_hull、centroid、area、length、distance、bounds、envelope、simplify、is_valid
- **向量化操作**：通过 NumPy ufunc 接口对几何数组进行高性能批量运算
- **多线程支持**：运算时自动释放 GIL，允许多线程并行计算
- **格式读写**：WKT、WKB、GeoJSON

**环境要求：** Python ≥ 3.11、GEOS ≥ 3.10、NumPy ≥ 1.23（Shapely 2.x）

---

## 安装

```bash
# pip
pip install shapely

# conda
conda install shapely --channel conda-forge
```

---

## 核心模块一览

| 模块 / 包 | 用途 |
|---|---|
| `shapely.geometry` | ★ **推荐入口**——Point、LineString、Polygon 等几何类 |
| `shapely` | 顶层模块，提供向量化 ufunc 函数（`shapely.intersects()`、`shapely.buffer()` 等） |
| `shapely.ops` | 高级操作——unary_union、polygonize、linemerge、split、snap、nearest_points、transform |
| `shapely.affinity` | 仿射变换——translate、rotate、scale、skew |
| `shapely.wkt` | WKT 格式的序列化 / 反序列化 |
| `shapely.wkb` | WKB 格式的序列化 / 反序列化 |
| `shapely.validation` | 几何有效性验证与修复 |
| `shapely.prepared` | PreparedGeometry——加速重复空间关系判断 |
| `shapely.strtree` | STRtree 空间索引——加速批量空间查询 |

---

## 几何对象创建

```python
from shapely.geometry import Point, LineString, LinearRing, Polygon
from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon, GeometryCollection
from shapely import box

# 点
point = Point(116.4, 39.9)

# 带 Z 值的点
point3d = Point(116.4, 39.9, 50.0)

# 线串
line = LineString([(0, 0), (10, 10), (20, 0)])

# 线环（自动闭合）
ring = LinearRing([(0, 0), (10, 0), (10, 10), (0, 10)])

# 面（无洞）
polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])

# 面（带洞）
polygon_with_hole = Polygon(
    [(0, 0), (20, 0), (20, 20), (0, 20)],       # 外环
    [[(5, 5), (15, 5), (15, 15), (5, 15)]]       # 内环列表
)

# 矩形（通过 box 快速创建）
rect = box(0, 0, 10, 10)  # box(minx, miny, maxx, maxy)

# 多点
multi_point = MultiPoint([(1, 2), (3, 4), (5, 6)])

# 多线
multi_line = MultiLineString([[(0, 0), (1, 1)], [(2, 2), (3, 3)]])

# 多面
multi_polygon = MultiPolygon([polygon, Polygon([(30, 30), (40, 30), (40, 40), (30, 40)])])

# 几何集合
gc = GeometryCollection([point, line, polygon])
```

---

## 几何属性

```python
# 几何类型
point.geom_type          # 'Point'
polygon.geom_type        # 'Polygon'

# 坐标维度
point.has_z              # False / True

# 坐标访问
list(point.coords)       # [(116.4, 39.9)]
list(line.coords)        # [(0.0, 0.0), (10.0, 10.0), (20.0, 0.0)]
polygon.exterior.coords  # 外环坐标
list(polygon.interiors)  # 内环列表

# 度量属性
polygon.area             # 面积
line.length              # 长度
polygon.bounds           # (minx, miny, maxx, maxy)

# 几何中心
polygon.centroid         # 质心（Point）
polygon.representative_point()  # 保证在几何内部的点

# 空/有效判断
point.is_empty           # False
polygon.is_valid         # True
line.is_ring             # False
line.is_simple           # True（无自交）
```

---

## 空间关系判断

```python
from shapely.geometry import Point, Polygon

point = Point(5, 5)
polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
other = Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])

# 基本空间谓词
point.within(polygon)              # True —— 点在面内
polygon.contains(point)            # True —— 面包含点
polygon.intersects(other)          # True —— 相交
polygon.disjoint(other)            # False —— 不相离
polygon.touches(other)             # False —— 不接触
polygon.crosses(other)             # False
polygon.overlaps(other)            # True —— 重叠
polygon.covers(point)              # True —— 覆盖
polygon.equals(other)              # False

# DE-9IM 关系矩阵
polygon.relate(other)              # 返回如 '212101212'
polygon.relate_pattern(other, 'T*T***T**')  # 按模式匹配

# 距离
point.distance(other)              # 最短距离
point.hausdorff_distance(other)    # Hausdorff 距离
```

---

## 集合运算

```python
a = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
b = Polygon([(5, 0), (15, 0), (15, 10), (5, 10)])

# 交集
a.intersection(b)

# 并集
a.union(b)

# 差集
a.difference(b)          # a 减去 b
b.difference(a)          # b 减去 a

# 对称差
a.symmetric_difference(b)

# 缓冲区
a.buffer(1.0)                           # 默认圆角缓冲
a.buffer(1.0, join_style='mitre')       # 直角缓冲
a.buffer(-0.5)                          # 负缓冲（内缩）
point.buffer(10.0, resolution=64)       # 高精度圆形缓冲
```

---

## 几何分析与构造

```python
from shapely.geometry import LineString, Polygon, MultiPoint

line = LineString([(0, 0), (5, 5), (10, 0)])
polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
points = MultiPoint([(0, 0), (1, 1), (2, 0), (3, 2)])

# 凸包
points.convex_hull

# 外接矩形
polygon.envelope                   # 最小外接矩形（与坐标轴对齐）
polygon.minimum_rotated_rectangle  # 最小面积外接矩形

# 简化
polygon.simplify(1.0, preserve_topology=True)   # 保拓扑简化
polygon.simplify(1.0, preserve_topology=False)  # Douglas-Peucker 简化

# 几何有效性
polygon.is_valid
from shapely.validation import explain_validity, make_valid
explain_validity(polygon)          # 无效原因描述
make_valid(polygon)                # 修复无效几何

# 线性参考
line.interpolate(0.5, normalized=True)    # 沿线 50% 处的点
line.project(Point(5, 5))                 # 点在线上的投影距离
line.project(Point(5, 5), normalized=True)  # 归一化投影距离
```

---

## 高级操作（shapely.ops）

```python
from shapely.ops import (
    unary_union, polygonize, linemerge, split,
    snap, nearest_points, transform, voronoi_diagram
)
from shapely.geometry import LineString, Point, MultiPoint, Polygon

# 批量合并（比逐个 union 高效）
from shapely.ops import unary_union
polygons = [Polygon([(i, 0), (i+1, 0), (i+1, 1), (i, 1)]) for i in range(5)]
merged = unary_union(polygons)

# 线合并
lines = [LineString([(0, 0), (1, 1)]), LineString([(1, 1), (2, 2)])]
merged_line = linemerge(lines)

# 从线构建面
polygonized = list(polygonize(lines))

# 分割几何
blade = LineString([(5, -1), (5, 11)])
result = split(Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]), blade)
list(result.geoms)  # 分割后的几何列表

# 吸附（Snap）
snapped = snap(Point(0.1, 0.1), Point(0, 0), tolerance=0.5)

# 最近点对
p1, p2 = nearest_points(Point(0, 0), LineString([(1, 1), (2, 2)]))

# 坐标变换（配合 pyproj 使用）
from pyproj import Transformer
transformer = Transformer.from_crs('EPSG:4326', 'EPSG:3857', always_xy=True)
transformed = transform(transformer.transform, Point(116.4, 39.9))

# Voronoi 图
points = MultiPoint([(0, 0), (1, 1), (2, 0)])
voronoi_diagram(points)
```

---

## 仿射变换（shapely.affinity）

```python
from shapely.affinity import translate, rotate, scale, skew
from shapely.geometry import Polygon

polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])

# 平移
translated = translate(polygon, xoff=10, yoff=20)

# 旋转（默认绕质心）
rotated = rotate(polygon, angle=45)                    # 逆时针 45°
rotated2 = rotate(polygon, angle=45, origin='centroid') # 绕质心
rotated3 = rotate(polygon, angle=45, origin=(0, 0))     # 绕指定点

# 缩放
scaled = scale(polygon, xfact=2.0, yfact=3.0, origin='center')

# 倾斜
skewed = skew(polygon, xs=10, ys=0)
```

---

## 格式读写

```python
from shapely.geometry import shape, mapping, Point
from shapely import wkt, wkb
import json

geom = Point(116.4, 39.9)

# ---- WKT ----
wkt_str = wkt.dumps(geom)                  # 'POINT (116.4 39.9)'
geom2 = wkt.loads('POINT (116.4 39.9)')

# 也可使用对象方法
wkt_str = geom.wkt                          # 'POINT (116.4 39.9)'

# ---- WKB ----
wkb_bytes = wkb.dumps(geom)                # bytes
geom3 = wkb.loads(wkb_bytes)

wkb_hex = wkb.dumps(geom, hex=True)        # 十六进制字符串
geom4 = wkb.loads(wkb_hex, hex=True)

# 也可使用对象方法
wkb_bytes = geom.wkb                        # bytes
wkb_hex = geom.wkb_hex                      # 十六进制字符串

# ---- GeoJSON ----
geojson_dict = mapping(geom)                # {'type': 'Point', 'coordinates': (116.4, 39.9)}
geom5 = shape(geojson_dict)

geojson_str = json.dumps(mapping(geom))
geom6 = shape(json.loads(geojson_str))
```

---

## 向量化操作（NumPy ufunc）

Shapely 2.x 提供顶层 ufunc 函数，对几何数组进行高性能批量运算：

```python
import shapely
import numpy as np
from shapely.geometry import Point

# 创建几何数组
points = np.array([Point(i, i) for i in range(5)])
polygon = shapely.box(1, 1, 3, 3)

# 批量空间关系判断
shapely.contains(polygon, points)       # array([False, True, True, True, False])
shapely.intersects(polygon, points)     # array([...]
shapely.within(points, polygon)         # array([...])
shapely.distance(points, polygon)       # array([...])

# 批量缓冲
buffered = shapely.buffer(points, 0.5)  # 返回几何数组

# 批量集合运算
shapely.intersection(buffered, polygon)
shapely.union_all(buffered)             # 全部合并
```

---

## 空间索引（STRtree）

```python
from shapely.strtree import STRtree
from shapely.geometry import Point, box

# 构建索引
geoms = [Point(i, i).buffer(0.5) for i in range(100)]
tree = STRtree(geoms)

# 查询与目标相交的几何索引
query_geom = box(10, 10, 20, 20)
indices = tree.query(query_geom)               # 返回索引数组
results = [geoms[i] for i in indices]

# 指定谓词查询
indices = tree.query(query_geom, predicate='intersects')
indices = tree.query(query_geom, predicate='contains')
indices = tree.query(query_geom, predicate='within')

# 最近邻查询
nearest_idx = tree.nearest(Point(5.5, 5.5))   # 返回最近几何的索引

# 批量查询（向量化）
query_geoms = np.array([Point(5, 5), Point(15, 15)])
result_idx_pairs = tree.query(query_geoms, predicate='intersects')
```

---

## PreparedGeometry（加速重复查询）

```python
from shapely.prepared import prep
from shapely.geometry import Point, Polygon

polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
prepared = prep(polygon)

# 使用 prepared 版本进行大量判断（比直接调用快数倍）
points = [Point(i, j) for i in range(12) for j in range(12)]
inside = [p for p in points if prepared.contains(p)]
touching = [p for p in points if prepared.intersects(p)]
```

---

## 与其他 GIS 库集成

### 与 GeoPandas 集成

```python
import geopandas as gpd
from shapely.geometry import Point

# GeoPandas 的 geometry 列即为 Shapely 几何对象
gdf = gpd.GeoDataFrame({
    'name': ['A', 'B'],
    'geometry': [Point(116.4, 39.9), Point(121.5, 31.2)]
}, crs='EPSG:4326')

# 可直接对 geometry 列使用 Shapely 方法
gdf['buffered'] = gdf.geometry.buffer(0.1)
```

### 与 Fiona 集成（读写文件）

```python
import fiona
from shapely.geometry import shape, mapping

# 读取
with fiona.open('data.shp') as src:
    for feature in src:
        geom = shape(feature['geometry'])  # Fiona dict → Shapely
        print(geom.area)

# 写入
with fiona.open('output.shp', 'w', driver='ESRI Shapefile',
                schema={'geometry': 'Polygon', 'properties': {'id': 'int'}}) as dst:
    dst.write({
        'geometry': mapping(polygon),      # Shapely → Fiona dict
        'properties': {'id': 1}
    })
```

### 与 pyproj 集成（坐标变换）

```python
from shapely.ops import transform
from pyproj import Transformer

transformer = Transformer.from_crs('EPSG:4326', 'EPSG:3857', always_xy=True)
projected = transform(transformer.transform, Point(116.4, 39.9))
```

---

## 常见注意事项

1. **坐标顺序**：Shapely 始终使用 `(x, y)` 即 `(经度, 纬度)` 的顺序。
2. **坐标系**：Shapely **不处理坐标系**，所有运算均在笛卡尔平面上进行。如需坐标变换或大地测量计算，请配合 `pyproj` 使用。
3. **几何有效性**：执行空间运算前应检查 `is_valid`，无效几何可能导致错误结果。可使用 `shapely.validation.make_valid()` 修复。
4. **Polygon 环方向**：Shapely 2.x 遵循 GeoJSON 规范，外环逆时针、内环顺时针。可使用 `shapely.ops.orient(polygon, sign=1.0)` 统一方向。
5. **线程安全**：Shapely 2.x 的 ufunc 函数在执行时释放 GIL，支持多线程并行；但单个几何对象不应在多线程中同时修改。
6. **不可变性**：Shapely 几何对象是不可变的（immutable），所有操作返回新对象。
7. **性能优化**：
   - 批量操作优先使用顶层 ufunc（`shapely.buffer()`、`shapely.intersects()`）而非逐个调用对象方法
   - 大量空间查询使用 `STRtree` 空间索引
   - 重复判断同一几何使用 `PreparedGeometry`
   - 批量合并使用 `unary_union` 而非循环 `union`
