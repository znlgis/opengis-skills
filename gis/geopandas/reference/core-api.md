# GeoPandas Core API Reference

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

```
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

```
difference(other, align=None)          intersection(other, align=None)
symmetric_difference(other, align=None) union(other, align=None)
shortest_line(other, align=None)       snap(other, tolerance, align=None)
shared_paths(other, align=None)
```

#### 距离方法 → Series[float]

```
distance(other, align=None)
hausdorff_distance(other, align=None)
frechet_distance(other, align=None)
```

#### 线性参考

```
interpolate(distance, normalized=False)  → GeoSeries (线上的点)
project(other, normalized=False)         → Series[float] (沿线距离)
```

#### 聚合方法

```
union_all(method="unary", grid_size=None)  → 单个 Shapely geometry
intersection_all()                         → 单个 Shapely geometry
```

#### 仿射变换 → GeoSeries

```
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

