---
name: geopandas
description: Use when writing Python code that involves geospatial vector data — reading/writing shapefiles, GeoJSON, GeoPackage, GeoParquet; spatial joins, overlays, clipping, buffering, CRS transformations; or plotting maps with matplotlib/folium. Covers GeoDataFrame, GeoSeries, and all geopandas IO/tools APIs.
---

# GeoPandas

- **项目地址**: https://github.com/geopandas/geopandas
- **官方文档**: https://geopandas.readthedocs.io
- **官网**: https://geopandas.org
- **许可证**: BSD-3-Clause

## 概述

GeoPandas 是 Python 地理空间矢量数据处理的核心库，在 pandas DataFrame 基础上扩展了几何列支持。核心类 `GeoDataFrame`（继承 `pandas.DataFrame`）和 `GeoSeries`（继承 `pandas.Series`）通过 Shapely 提供几何运算、通过 pyproj 提供坐标系管理、通过 pyogrio/fiona 提供文件 IO。

## 依赖关系

| 核心依赖 | 最低版本 | 用途 |
|----------|---------|------|
| `pandas` | >= 2.2.0 | DataFrame 基类 |
| `shapely` | >= 2.1.0 | 几何对象与运算 (GEOS) |
| `pyproj` | >= 3.7.0 | CRS 处理与坐标变换 |
| `pyogrio` | >= 0.8 | 默认文件 IO 引擎 (GDAL/OGR) |
| `numpy` | >= 2 | 数组运算 |

| 可选依赖 | 用途 |
|----------|------|
| `matplotlib` >= 3.9 | 静态地图绑制 `.plot()` |
| `folium` | 交互式地图 `.explore()` |
| `mapclassify` >= 2.7 | 分级设色分类方案 |
| `fiona` >= 1.8.21 | 备选文件 IO 引擎 |
| `pyarrow` >= 15.0.0 | Parquet/Feather/Arrow 支持 |
| `geopy` | 地理编码 |
| `SQLAlchemy` >= 2.0 + `GeoAlchemy2` | PostGIS 读写 |
| `xyzservices` | 瓦片底图服务 |

## 全局配置

```python
import geopandas as gpd
gpd.options.display_precision  # int|None, WKT 小数位数 (0-16)
gpd.options.io_engine          # None|"pyogrio"|"fiona"
```

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

## IO 模块

### 文件读写

```python
gpd.read_file(filename, bbox=None, mask=None, columns=None, rows=None, engine=None, **kwargs)
gdf.to_file(filename, driver=None, schema=None, index=None, **kwargs)
gpd.list_layers(filename)  # → DataFrame (layer_name, geometry_type)
```

**支持的文件格式（扩展名 → 驱动）：**

| 扩展名 | 驱动 |
|--------|------|
| `.shp` | ESRI Shapefile |
| `.json`, `.geojson` | GeoJSON |
| `.geojsonl`, `.geojsons` | GeoJSONSeq |
| `.gpkg` | GPKG (GeoPackage) |
| `.gml`, `.xml` | GML |
| `.gpx` | GPX |
| `.csv` | CSV |
| `.fgb` | FlatGeobuf |
| `.dxf` | DXF |
| `.tab`, `.mif`, `.mid` | MapInfo File |

引擎选项：`"pyogrio"`（默认）或 `"fiona"`。支持所有 GDAL/OGR 驱动。

### GeoParquet / Feather

```python
gpd.read_parquet(path, columns=None, storage_options=None, bbox=None, **kwargs)
gpd.read_feather(path, columns=None, **kwargs)
gdf.to_parquet(path, compression="snappy", geometry_encoding="WKB",
               write_covering_bbox=False, schema_version=None, **kwargs)
gdf.to_feather(path, compression=None, schema_version=None, **kwargs)
```

GeoParquet 规范版本：`"1.0.0"`, `"1.1.0"` 等。几何编码：`"WKB"`（默认）、`"geoarrow"`。

### Arrow (GeoArrow)

```python
gdf.to_arrow(geometry_encoding="WKB", interleaved=True, include_z=None)
GeoDataFrame.from_arrow(table, geometry=None, to_pandas_kwargs=None)
gs.to_arrow(geometry_encoding="WKB", interleaved=True, include_z=None)
GeoSeries.from_arrow(arr, **kwargs)
```

### PostGIS

```python
gpd.read_postgis(sql, con, geom_col="geom", crs=None, index_col=None, ...)
gdf.to_postgis(name, con, schema=None, if_exists="fail", index=False, ...)
```

需要：`SQLAlchemy` + `GeoAlchemy2` + `psycopg`/`psycopg2`。

### WKB/WKT 与坐标构造

```python
gpd.points_from_xy(x, y, z=None, crs=None)  # → GeometryArray
GeoSeries.from_wkb(data, crs=None, on_invalid="raise")
GeoSeries.from_wkt(data, crs=None, on_invalid="raise")
GeoSeries.from_xy(x, y, z=None, crs=None)
```

---

## 工具模块 (tools)

### 空间连接

```python
gpd.sjoin(left_df, right_df, how="inner", predicate="intersects",
          lsuffix="left", rsuffix="right", distance=None, on_attribute=None)
```

- `how`: `"inner"`, `"left"`, `"right"`
- `predicate`: `"intersects"`, `"within"`, `"contains"`, `"contains_properly"`, `"overlaps"`, `"crosses"`, `"touches"`, `"covers"`, `"covered_by"`, `"dwithin"`
- `on_attribute`: 附加非空间连接过滤列名

### 最近邻空间连接

```python
gpd.sjoin_nearest(left_df, right_df, how="inner", max_distance=None,
                  distance_col=None, exclusive=False)
```

### 空间叠加

```python
gpd.overlay(df1, df2, how="intersection", keep_geom_type=None, make_valid=True)
```

- `how`: `"intersection"`, `"union"`, `"identity"`, `"symmetric_difference"`, `"difference"`

### 裁剪

```python
gpd.clip(gdf, mask, keep_geom_type=False, sort=False)
```

- `mask`: GeoDataFrame、GeoSeries、(Multi)Polygon 或 `(minx, miny, maxx, maxy)` 元组

### 地理编码

```python
gpd.tools.geocode(strings, provider=None, **kwargs)          # → GeoDataFrame
gpd.tools.reverse_geocode(points, provider=None, **kwargs)   # → GeoDataFrame
```

需要 `geopy`。默认 provider: `"photon"`。返回含 `geometry` 和 `address` 列的 GeoDataFrame。

### 其他工具

```python
gpd.tools.collect(x, multi=False)  # 收集几何体为多部件
gpd.show_versions()                # 打印依赖版本信息
```

---

## 可视化

### 静态绑图 (matplotlib)

```python
# GeoSeries
gs.plot(cmap=None, color=None, ax=None, figsize=None, aspect="auto")

# GeoDataFrame — 支持分级设色
gdf.plot(column=None, cmap=None, color=None, ax=None, figsize=None,
         legend=False, scheme=None, k=5, vmin=None, vmax=None,
         markersize=None, categories=None, classification_kwds=None,
         missing_kwds=None, legend_kwds=None, **style_kwds)
```

`scheme` 参数需要 `mapclassify`，支持 `"quantiles"`, `"equal_interval"`, `"fisher_jenks"` 等分类方案。

### 交互式地图 (folium/leaflet)

```python
gdf.explore(column=None, cmap=None, color=None, m=None,
            tiles="OpenStreetMap", tooltip=True, popup=False,
            categorical=False, legend=True, scheme=None, k=5,
            marker_type=None, marker_kwds={}, style_kwds={},
            tooltip_kwds={}, popup_kwds={}, legend_kwds={}, **kwargs)
```

---

## 常用模式速查

### 创建 GeoDataFrame

```python
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString

# 从文件读取
gdf = gpd.read_file("data.shp")
gdf = gpd.read_file("data.gpkg", layer="my_layer")
gdf = gpd.read_parquet("data.parquet")

# 从字典创建
gdf = gpd.GeoDataFrame(
    {"name": ["A", "B"], "value": [1, 2],
     "geometry": [Point(0, 0), Point(1, 1)]},
    crs="EPSG:4326"
)

# 从 pandas DataFrame + 坐标列
import pandas as pd
df = pd.DataFrame({"lon": [116.4, 121.5], "lat": [39.9, 31.2], "city": ["北京", "上海"]})
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")

# 从 WKT/WKB
gs = gpd.GeoSeries.from_wkt(["POINT (0 0)", "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"], crs=4326)

# 从 GeoJSON FeatureCollection
gdf = gpd.GeoDataFrame.from_features(feature_collection["features"], crs="EPSG:4326")
```

### CRS 操作

```python
gdf = gdf.set_crs("EPSG:4326")          # 赋值 CRS（数据本身不变）
gdf = gdf.to_crs("EPSG:3857")           # 投影变换（坐标重算）
gdf = gdf.to_crs(epsg=32650)            # 按 EPSG 代码投影
utm = gdf.estimate_utm_crs()            # 自动检测 UTM 分区
```

**注意**：`set_crs()` 仅标记 CRS 不转换坐标；`to_crs()` 实际执行坐标变换。面积/距离计算前务必投影到适当的投影坐标系（如 UTM）。

### 空间分析

```python
# 空间连接
joined = gpd.sjoin(points_gdf, polygons_gdf, how="inner", predicate="within")

# 最近邻连接
nearest = gpd.sjoin_nearest(gdf1, gdf2, max_distance=1000, distance_col="dist_m")

# 空间叠加
result = gpd.overlay(gdf1, gdf2, how="intersection")

# 裁剪
clipped = gpd.clip(gdf, mask_polygon)
clipped = gpd.clip(gdf, (xmin, ymin, xmax, ymax))  # 矩形快速裁剪

# 按属性融合
dissolved = gdf.dissolve(by="province", aggfunc="sum")

# 多部件炸开
exploded = gdf.explode(index_parts=False)

# 缓冲区、简化
gdf["buffer_100m"] = gdf.geometry.buffer(100)
gdf["simplified"] = gdf.geometry.simplify(tolerance=50)
```

### 几何谓词与度量

```python
gdf.geometry.intersects(other_geom)    # Series[bool]
gdf.geometry.contains(other_geom)      # Series[bool]
gdf.geometry.within(other_geom)        # Series[bool]
gdf.geometry.distance(other_geom)      # Series[float]
gdf.geometry.area                      # Series[float]
gdf.geometry.length                    # Series[float]
gdf.geometry.centroid                  # GeoSeries
gdf.geometry.bounds                    # DataFrame
gdf.total_bounds                       # array [minx, miny, maxx, maxy]
```

### 数据输出

```python
gdf.to_file("output.gpkg", driver="GPKG", layer="result")
gdf.to_file("output.geojson", driver="GeoJSON")
gdf.to_parquet("output.parquet")
geojson_str = gdf.to_json()
gdf.to_postgis("table_name", engine, if_exists="replace")
```

### 可视化

```python
# 静态地图
ax = gdf.plot(column="population", cmap="YlOrRd", legend=True, figsize=(12, 8))

# 多图层叠加
ax = base_gdf.plot(color="lightgrey", figsize=(12, 8))
points_gdf.plot(ax=ax, color="red", markersize=5)

# 交互式地图
m = gdf.explore(column="population", cmap="viridis",
                tooltip=["name", "population"], tiles="CartoDB positron")
```

---

## 常见错误与解决

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 面积/距离为 0 或极小 | CRS 为地理坐标系 (度) | `gdf.to_crs(gdf.estimate_utm_crs())` 后计算 |
| `sjoin` 无结果 | 两个 GDF 的 CRS 不一致 | 统一 CRS：`gdf2 = gdf2.to_crs(gdf1.crs)` |
| `ValueError: GeoDataFrame does not support multiple columns using the geometry column name 'geometry'` | 多个列名为 `geometry` | 重命名冲突列或使用 `set_geometry()` 指定 |
| `to_file` 属性被截断 | Shapefile 字段名限制 10 字符 | 使用 GeoPackage (`.gpkg`) 或 GeoJSON |
| `set_crs` vs `to_crs` 混淆 | `set_crs` 仅赋值不转换 | 已有 CRS 需要转换用 `to_crs()`；无 CRS 标记用 `set_crs()` |
| Shapefile 不支持空值/日期时间 | Shapefile 格式限制 | 使用 GeoPackage 格式 |
| `DriverError` 无法写入 | 驱动不支持或文件被占用 | 检查驱动名拼写、关闭已打开的文件 |
| `align=True` 导致意外 NaN | 二元操作默认按索引对齐 | 传入 `align=False` 或重置索引 |

## 性能提示

- **GeoParquet** 比 Shapefile/GeoJSON 读写快 5-10 倍，优先使用
- **空间索引** `.sindex` 自动构建 STRtree，`query()` 和 `nearest()` 可大幅加速空间查询
- **矩形裁剪** `clip_by_rect()` 或 `clip(gdf, (xmin,ymin,xmax,ymax))` 比多边形裁剪快
- **`pyogrio` 引擎**（默认）比 `fiona` 快 2-5 倍
- 大数据集用 `read_file(rows=slice(0, 1000))` 先预览
- `dissolve()` 使用 `method="coverage"` 对已知不重叠的多边形更快
- 避免逐行循环几何操作，使用向量化方法（如 `buffer()`, `intersection()` 等）
