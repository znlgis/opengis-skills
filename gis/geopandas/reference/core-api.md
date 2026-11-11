# GeoPandas Core API Reference

## Contents

- 核心类 API
- 1.2 新增接口（make_grid、read_file_info、grid_size）

GeoSeries and GeoDataFrame core API details split from SKILL.md.

---

## 核心类 API

### GeoDataFrame

```python
gpd.GeoDataFrame(data=None, *args, geometry=None, crs=None, **kwargs)
```

#### 备选构造器

| 方法 | 签名 |
|------|------|
| `GeoDataFrame.from_dict()` | `(data, geometry=None, crs=None, **kwargs)` |
| `GeoDataFrame.from_file()` | `(filename, **kwargs)` |
| `GeoDataFrame.from_features()` | `(features, crs=None, columns=None)` |
| `GeoDataFrame.from_postgis()` | `(sql, con, geom_col="geom", crs=None, ...)` |
| `GeoDataFrame.from_arrow()` | `(table, geometry=None, to_pandas_kwargs=None)` |

#### 核心属性

| 属性 | 说明 |
|------|------|
| `.geometry` | 活跃几何列 (GeoSeries) |
| `.crs` | 坐标参考系 (pyproj.CRS) |
| `.active_geometry_name` | 活跃几何列名 |
| `.total_bounds` | 整体边界 `[minx, miny, maxx, maxy]` |
| `.sindex` | 空间索引 (STRtree) |

#### 几何管理

| 方法 | 签名 |
|------|------|
| `set_geometry()` | `(col, drop=None, inplace=False, crs=None)` |
| `rename_geometry()` | `(col, inplace=False)` |
| `set_crs()` | `(crs=None, epsg=None, inplace=False, allow_override=False)` |
| `to_crs()` | `(crs=None, epsg=None, inplace=False)` |
| `estimate_utm_crs()` | `(datum_name="WGS 84")` → pyproj.CRS |

#### 空间操作（GeoDataFrame 级别）

| 方法 | 签名 |
|------|------|
| `dissolve()` | `(by=None, aggfunc="first", as_index=True, sort=True, method="unary", grid_size=None)` |
| `explode()` | `(column=None, ignore_index=False, index_parts=False)` |
| `sjoin()` | `(df, how="inner", predicate="intersects", lsuffix="left", rsuffix="right")` |
| `sjoin_nearest()` | `(right, how="inner", max_distance=None, distance_col=None, exclusive=False)` |
| `clip()` | `(mask, keep_geom_type=False, sort=False)` |
| `overlay()` | `(right, how="intersection", keep_geom_type=None, make_valid=True)` |

#### 序列化输出

| 方法 | 说明 |
|------|------|
| `to_file(filename, driver=None, ...)` | Shapefile/GPKG/GeoJSON 等 |
| `to_parquet(path, compression="snappy", geometry_encoding="WKB", ...)` | GeoParquet |
| `to_feather(path, ...)` | Feather |
| `to_json(na="null", show_bbox=False, to_wgs84=False, ...)` | GeoJSON 字符串 |
| `to_geo_dict(...)` | Python dict (FeatureCollection) |
| `to_wkb(hex=False)` | DataFrame (WKB) |
| `to_wkt()` | DataFrame (WKT) |
| `to_postgis(name, con, schema=None, if_exists="fail", ...)` | PostGIS |
| `to_arrow(geometry_encoding="WKB", ...)` | Arrow Table |

---

### GeoSeries

```python
gpd.GeoSeries(data=None, index=None, crs=None, **kwargs)
```

#### 备选构造器

| 方法 | 签名 |
|------|------|
| `GeoSeries.from_wkb()` | `(data, index=None, crs=None, on_invalid="raise")` |
| `GeoSeries.from_wkt()` | `(data, index=None, crs=None, on_invalid="raise")` |
| `GeoSeries.from_xy()` | `(x, y, z=None, index=None, crs=None)` |
| `GeoSeries.from_file()` | `(filename, **kwargs)` |
| `GeoSeries.from_arrow()` | `(arr, **kwargs)` |

#### 坐标访问器（仅限 Point）

`.x`, `.y`, `.z`, `.m` → pandas.Series

---

### 共享几何属性与方法（GeoDataFrame.geometry / GeoSeries）

#### 标量属性 → pandas.Series

| 属性 | 返回类型 | 说明 |
|------|---------|------|
| `.area` | float | 面积（CRS 单位） |
| `.length` | float | 长度/周长 |
| `.geom_type` | str | 几何类型名称 |
| `.is_valid` | bool | 几何有效性 |
| `.is_empty` | bool | 空几何检查 |
| `.is_simple` | bool | 不自相交 |
| `.has_z` | bool | 含 z 坐标 |
| `.bounds` | DataFrame | 每几何体 (minx, miny, maxx, maxy) |
| `.total_bounds` | array | 整体 (minx, miny, maxx, maxy) |

#### 几何属性 → GeoSeries

`.boundary`, `.centroid`, `.convex_hull`, `.envelope`, `.exterior`

#### 一元几何方法 → GeoSeries

| 方法 | 签名 |
|------|------|
| `buffer()` | `(distance, quad_segs=None, **kwargs)` |
| `simplify()` | `(tolerance, preserve_topology=True)` |
| `representative_point()` | `()` |
| `make_valid()` | `(method="linework", keep_collapsed=True)` |
| `normalize()` | `()` |
| `reverse()` | `()` |
| `segmentize()` | `(max_segment_length)` |
| `force_2d()` | `()` |
| `force_3d()` | `(z=0)` |
| `offset_curve()` | `(distance, quad_segs=8, join_style="round", mitre_limit=5.0)` |
| `minimum_rotated_rectangle()` | `()` |
| `minimum_bounding_circle()` | `()` |
| `maximum_inscribed_circle()` | `(tolerance)` |
| `concave_hull()` | `(ratio, allow_holes)` |
| `extract_unique_points()` | `()` |
| `remove_repeated_points()` | `(tolerance=0.0)` |
| `line_merge()` | `(directed=False)` |
| `set_precision()` | `(grid_size, mode="valid_output")` |
| `orient_polygons()` | `(exterior_cw=False)` |
| `constrained_delaunay_triangles()` | `()` |

#### 二元谓词 → Series[bool]

```text
contains(other, align=None)          covers(other, align=None)
covered_by(other, align=None)        crosses(other, align=None)
disjoint(other, align=None)          intersects(other, align=None)
overlaps(other, align=None)          touches(other, align=None)
within(other, align=None)            contains_properly(other, align=None)
dwithin(other, distance, align=None)
geom_equals(other, align=None)       geom_equals_exact(other, tolerance, align=None)
geom_equals_identical(other, align=None)
relate_pattern(other, pattern)
```

#### 二元几何运算 → GeoSeries

```text
difference(other, align=None)          intersection(other, align=None)
symmetric_difference(other, align=None) union(other, align=None)
shortest_line(other, align=None)       snap(other, tolerance, align=None)
shared_paths(other, align=None)
```

#### 距离方法 → Series[float]

```text
distance(other, align=None)
hausdorff_distance(other, align=None)
frechet_distance(other, align=None)
```

#### 线性参考

```text
interpolate(distance, normalized=False)  → GeoSeries (线上的点)
project(other, normalized=False)         → Series[float] (沿线距离)
```

#### 聚合方法

```text
union_all(method="unary", grid_size=None)  → 单个 Shapely geometry
intersection_all()                         → 单个 Shapely geometry
```

#### 仿射变换 → GeoSeries

```text
affine_transform(matrix)
translate(xoff=0.0, yoff=0.0, zoff=0.0)
rotate(angle, origin="center", use_radians=False)
scale(xfact=1.0, yfact=1.0, zfact=1.0, origin="center")
skew(xs=0.0, ys=0.0, origin="center", use_radians=False)
transform(transformation, include_z=False)
```

#### 其他方法

| 方法 | 返回 | 说明 |
|------|------|------|
| `clip_by_rect(xmin, ymin, xmax, ymax)` | GeoSeries | 矩形裁剪 |
| `relate(other, align=None)` | Series[str] | DE-9IM 矩阵 |
| `count_coordinates()` | Series[int] | 坐标对数量 |
| `count_geometries()` | Series[int] | 多部件几何体部件数 |
| `get_coordinates()` | DataFrame | 提取所有坐标 |
| `hilbert_distance()` | Series | Hilbert 曲线距离 |
| `is_valid_reason()` | Series[str] | 无效原因 |

---

### 空间索引 (SpatialIndex)

```python
sindex = gdf.sindex
sindex.query(geometry, predicate=None, sort=False, distance=None)
sindex.nearest(geometry, max_distance=None, return_distance=False, return_all=True, exclusive=False)
sindex.valid_query_predicates  # 有效谓词集合
sindex.size                    # 几何体数量
sindex.is_empty                # 是否为空
```

---

---

## 1.2 新增接口（make_grid、read_file_info、grid_size）

以上内容以 GeoPandas 1.2.0 为基准。1.2 新增或变更的接口如下。

### gpd.read_file_info()

```python
gpd.read_file_info(filename, layer=None)  # -> dict，1.2 新增
```

返回单个图层的元数据字典（pyogrio.read_info 的别名，需装 pyogrio）。与 `gpd.list_layers()` 的分工：`list_layers()` 列出所有图层（name/geometry_type），`read_file_info()` 给某一层的完整信息（CRS、字段、要素数等）。

### gpd.make_grid()

```python
gpd.make_grid(input_geometry, /, cell_size, grid_type="square",
              feature_type="polygons", offset=None, intersect=True, flat_topped=False)
GeoSeries.make_grid(...)   # 同名方法
```

| 参数 | 取值 | 说明 |
|------|------|------|
| `cell_size` | float | 正方形边长；六边形时为对边距离（边长 = cell_size / sqrt(3)） |
| `grid_type` | `"square"` / `"hexagon"` | 平面网格，不是 H3/S2 那种球面网格 |
| `feature_type` | `"polygons"` / `"centers"` / `"corners"` | 返回面、中心点或顶点 |
| `offset` | (x, y) | 网格左下角，默认取输入范围左下角 |
| `intersect` | bool | True 只保留与输入几何相交的单元；False 返回覆盖外接矩形的完整网格 |
| `flat_topped` | bool | 六边形是否平顶（默认尖顶朝上） |

返回 GeoSeries（1.2 新增）。

### 集合运算的 grid_size

1.2 起以下 GeoSeries 方法新增 `grid_size` 参数，用于固定精度栅格（顶点吸附到指定格网，可改善拓扑鲁棒性）：

```text
union(other, align=None, grid_size=None)
intersection(other, align=None, grid_size=None)
difference(other, align=None, grid_size=None)
symmetric_difference(other, align=None, grid_size=None)
union_all(method="unary", grid_size=None)
```

`gpd.overlay()` 没有 `grid_size` 参数，需要固定精度时先对各 GeoSeries 做 `set_precision()` 或用上述方法。

### GeoParquet 规范版本

`to_parquet(schema_version=...)` 支持 `"0.1.0"`、`"0.4.0"`、`"1.0.0"`、`"1.1.0"`、`"2.0.0"`；不传时默认写 1.1.0。1.2 起 GeoParquet 2.0 可读写。
