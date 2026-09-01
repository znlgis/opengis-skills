---
name: geopandas
description: "Use when performing vector spatial data analysis in Python — reading/writing shapefiles, spatial joins, overlay operations, choropleth maps. GeoPandas: extends pandas DataFrames with geometry columns for Pythonic spatial analysis."
tags:
  - python
  - pandas
  - vector
  - geometry
  - geodataframe
  - spatial-analysis
  - io
  - visualization
---

> **项目地址：** <https://github.com/geopandas/geopandas>
>
> **官方文档：** <https://geopandas.readthedocs.io>
>
> **官网：** <https://geopandas.org>
>
> **许可证：** BSD-3-Clause

## 概述

GeoPandas 是 Python 地理空间矢量数据处理的核心库，在 pandas DataFrame 基础上扩展了几何列支持。核心类 `GeoDataFrame`（继承 `pandas.DataFrame`）和 `GeoSeries`（继承 `pandas.Series`）通过 Shapely 提供几何运算、通过 pyproj 提供坐标系管理、通过 pyogrio/fiona 提供文件 IO。

## 依赖关系

| 核心依赖 | 最低版本 | 用途 |
|----------|---------|------|
| `pandas` | >= 2.0.0 | DataFrame 基类 |
| `shapely` | >= 2.0.0 | 几何对象与运算 (GEOS) |
| `pyproj` | >= 3.5.0 | CRS 处理与坐标变换 |
| `pyogrio` | >= 0.7.2 | 默认文件 IO 引擎 (GDAL/OGR) |
| `numpy` | >= 1.24 | 数组运算 |

| 可选依赖 | 用途 |
|----------|------|
| `matplotlib` >= 3.5 | 静态地图绘制 `.plot()` |
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

> 核心类（GeoSeries/GeoDataFrame）完整 API 参考见 [reference/core-api.md](reference/core-api.md)

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

$h$faq`

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

## AI 使用建议

### 推荐工作流

1. **读取数据**：使用 `gpd.read_file()` 读取矢量文件，或 `gpd.read_parquet()` 读取 GeoParquet
2. **检查 CRS**：始终先检查 `gdf.crs`，需要在投影坐标系（非地理坐标系）下进行面积/距离计算
3. **空间分析**：使用 `gpd.sjoin()` 进行空间连接，`gpd.overlay()` 进行叠加分析，`gpd.clip()` 进行裁剪
4. **可视化**：使用 `.plot()` 快速静态出图，`.explore()` 生成交互式地图
5. **输出**：使用 `gdf.to_file()` 或 `gdf.to_parquet()` 保存结果，优先使用 GeoPackage 或 GeoParquet 格式

### 关键注意事项

- **`set_crs()` vs `to_crs()`**：`set_crs()` 仅标记坐标系不转换坐标，`to_crs()` 执行实际坐标变换——切勿混用
- **面积/距离计算前投影**：地理坐标系（EPSG:4326）下面积单位为度²无意义，应使用 `gdf.to_crs(gdf.estimate_utm_crs())` 投影后再计算
- **空间操作前统一 CRS**：确保参与 `sjoin`、`overlay`、`clip` 的所有 GeoDataFrame 使用相同 CRS
- **优先使用 GeoParquet**：比 Shapefile/GeoJSON 读写快 5-10 倍，且无字段名长度限制
- **向量化操作**：避免逐行循环，使用 GeoSeries 的向量化方法（`buffer()`、`intersection()` 等）批量处理
- **空间索引自动构建**：`.sindex` 自动维护 STRtree，`query()` 和 `nearest()` 可大幅加速空间查询

## 相关技能

- **shapely** — 底层几何计算库：[../shapely/SKILL.md](../shapely/SKILL.md)
- **gdal** — 命令行数据处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **pyqgis** — QGIS Python 绑定：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)
- **geopipe-agent** — AI 原生分析流水线：[../geopipe-agent/SKILL.md](../geopipe-agent/SKILL.md)

## 性能提示

- **GeoParquet** 比 Shapefile/GeoJSON 读写快 5-10 倍，优先使用
- **空间索引** `.sindex` 自动构建 STRtree，`query()` 和 `nearest()` 可大幅加速空间查询
- **矩形裁剪** `clip_by_rect()` 或 `clip(gdf, (xmin,ymin,xmax,ymax))` 比多边形裁剪快
- **`pyogrio` 引擎**（默认）比 `fiona` 快 2-5 倍
- 大数据集用 `read_file(rows=slice(0, 1000))` 先预览
- `dissolve()` 使用 `method="coverage"` 对已知不重叠的多边形更快
- 避免逐行循环几何操作，使用向量化方法（如 `buffer()`, `intersection()` 等）

---

## 参考资源

- **GitHub 仓库：** <https://github.com/geopandas/geopandas>
- **官方文档：** <https://geopandas.readthedocs.io>
- **官网：** <https://geopandas.org>
- **GeoParquet 规范：** <https://geoparquet.org/>
- **中文教程（znlgis）：** <https://znlgis.github.io/gis/tutorial/geopandas/>
