---
name: geopandas
description: GeoPandas 是基于 pandas 的开源 Python 地理空间数据处理库，扩展了 pandas 的 DataFrame 和 Series 类型以支持几何对象，提供空间数据读写、坐标参考系管理、几何操作、空间连接、叠加分析和地图可视化等功能，是 Python 地理空间数据科学的核心工具。
---

> **项目地址：** <https://github.com/geopandas/geopandas>
>
> **官方文档：** <https://geopandas.org/en/stable/>
>
> **API 参考：** <https://geopandas.org/en/stable/docs/reference.html>
>
> **用户指南：** <https://geopandas.org/en/stable/docs/user_guide.html>
>
> **许可证：** BSD 3-Clause License

## 概述

GeoPandas 是 Python 生态系统中处理地理空间矢量数据的核心库，由社区维护并托管于 <https://github.com/geopandas/geopandas>。它在 pandas 之上构建，提供：

- **GeoDataFrame / GeoSeries**：扩展 pandas 数据结构，原生支持几何列（Point、LineString、Polygon 等）
- **空间数据 I/O**：通过 pyogrio/fiona 读写 Shapefile、GeoJSON、GeoPackage、FlatGeobuf、Parquet 等 50+ 种矢量格式
- **坐标参考系（CRS）管理**：基于 pyproj 的投影定义、查询与重投影
- **几何操作**：基于 Shapely 2 的缓冲区、质心、凸包、简化、布尔运算等
- **空间关系与查询**：intersects、within、contains、crosses 等谓词判断
- **空间连接（sjoin）与叠加分析（overlay）**：按空间关系合并数据集
- **聚合与融合（dissolve）**：按属性分组聚合几何
- **地图可视化**：基于 matplotlib 的 `.plot()` 方法，支持分级色彩图（choropleth）

GeoPandas 的核心依赖栈：

| 依赖库 | 作用 |
|--------|------|
| `pandas` | 表格数据结构与操作 |
| `shapely` (≥ 2.0) | 几何对象创建与操作（基于 GEOS） |
| `pyproj` | 坐标参考系定义与变换（基于 PROJ） |
| `pyogrio` | 矢量数据 I/O（基于 GDAL/OGR，默认后端） |
| `matplotlib` | 地图可视化（可选） |

---

## 环境准备

### 安装方法

#### pip 安装

```bash
pip install geopandas
```

#### Conda 安装（推荐，自动处理 C 库依赖）

```bash
conda install -c conda-forge geopandas
```

#### 验证安装

```python
import geopandas as gpd
print(gpd.__version__)
# 预期输出：1.1.3 或更高版本
```

### 最低依赖要求（1.1+）

| 依赖 | 最低版本 |
|------|---------|
| Python | 3.10+ |
| pandas | 2.0+ |
| numpy | 1.24+ |
| shapely | 2.0+ |
| pyproj | 3.5+ |
| pyogrio | 0.7+ |

---

## 核心类一览

| 类 / 函数 | 说明 |
|-----------|------|
| `GeoDataFrame` | 带有几何列的 DataFrame，核心数据结构 |
| `GeoSeries` | 几何对象序列，支持逐元素空间操作 |
| `gpd.read_file()` | 读取矢量文件为 GeoDataFrame |
| `gpd.read_parquet()` | 读取 GeoParquet 文件 |
| `gpd.read_feather()` | 读取 Feather 格式文件 |
| `gpd.read_postgis()` | 从 PostGIS 数据库读取 |
| `GeoDataFrame.to_file()` | 写出矢量文件（Shapefile、GeoJSON、GPKG 等） |
| `GeoDataFrame.to_parquet()` | 写出 GeoParquet 文件 |
| `GeoDataFrame.to_postgis()` | 写入 PostGIS 数据库 |
| `gpd.sjoin()` | 空间连接（基于空间谓词合并两个 GeoDataFrame） |
| `gpd.overlay()` | 叠加分析（intersection、union、difference 等集合运算） |
| `GeoDataFrame.dissolve()` | 按属性分组聚合几何 |
| `GeoDataFrame.clip()` | 按边界裁剪 |
| `GeoDataFrame.plot()` | 地图可视化 |
| `gpd.tools.geocode()` | 地理编码（地址 → 坐标） |

---

## 数据读写

### 读取矢量文件

```python
import geopandas as gpd

# 读取 Shapefile
gdf = gpd.read_file("data/boundaries.shp")

# 读取 GeoJSON
gdf = gpd.read_file("data/points.geojson")

# 读取 GeoPackage（指定图层）
gdf = gpd.read_file("data/city.gpkg", layer="buildings")

# 读取 GeoPackage（空间过滤，只读取指定范围内的要素）
from shapely.geometry import box
bbox = box(116.0, 39.0, 117.0, 40.0)
gdf = gpd.read_file("data/city.gpkg", mask=bbox)

# 读取 GeoParquet（高性能列式格式）
gdf = gpd.read_parquet("data/parcels.parquet")

# 从 URL 读取
gdf = gpd.read_file("https://example.com/data.geojson")

# 从 PostGIS 读取
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:password@host:5432/dbname")
gdf = gpd.read_postgis("SELECT * FROM buildings", engine, geom_col="geom")
```

### 写出矢量文件

```python
# 写出 GeoJSON
gdf.to_file("output/result.geojson", driver="GeoJSON")

# 写出 Shapefile
gdf.to_file("output/result.shp")

# 写出 GeoPackage
gdf.to_file("output/result.gpkg", driver="GPKG", layer="result")

# 写出 GeoParquet
gdf.to_parquet("output/result.parquet")

# 写入 PostGIS
gdf.to_postgis("table_name", engine, if_exists="replace")
```

### 支持的常见矢量格式

| 格式 | 驱动名 | 扩展名 | 说明 |
|------|--------|--------|------|
| Shapefile | `ESRI Shapefile` | `.shp` | 经典 GIS 矢量格式 |
| GeoJSON | `GeoJSON` | `.geojson` | Web 友好的 JSON 格式 |
| GeoPackage | `GPKG` | `.gpkg` | OGC 标准轻量数据库 |
| FlatGeobuf | `FlatGeobuf` | `.fgb` | 高性能流式二进制格式 |
| GeoParquet | — | `.parquet` | 列式存储，大数据场景高效 |
| KML | `KML` | `.kml` | Google Earth 格式 |
| CSV（含 WKT） | `CSV` | `.csv` | 需配合几何列 |
| PostGIS | — | — | PostgreSQL 空间数据库 |

---

## 坐标参考系（CRS）

### 查看与设置 CRS

```python
# 查看当前 CRS
print(gdf.crs)           # 例如：EPSG:4326
print(gdf.crs.to_epsg()) # 4326

# 为无 CRS 的数据设置 CRS（不改变坐标值）
gdf = gdf.set_crs("EPSG:4326")

# 重投影到新 CRS（改变坐标值）
gdf_projected = gdf.to_crs("EPSG:3857")   # Web Mercator
gdf_utm = gdf.to_crs("EPSG:32650")        # UTM Zone 50N
```

### 常用坐标系

| EPSG 代码 | 名称 | 说明 |
|-----------|------|------|
| 4326 | WGS 84 | 经纬度，GPS 默认坐标系 |
| 3857 | Web Mercator | Web 地图（Google Maps、OpenStreetMap） |
| 4490 | CGCS2000 | 中国国家大地坐标系 |
| 32650 | WGS 84 / UTM 50N | 通用横轴墨卡托投影（中国东部） |

### 注意事项

- **面积/距离计算前应投影**：`EPSG:4326` 是地理坐标系（单位为度），计算面积/距离前应先投影到适当的投影坐标系（单位为米）
- **set_crs 与 to_crs 的区别**：`set_crs()` 仅设置元数据，不改变坐标值；`to_crs()` 执行实际坐标变换

---

## 几何操作

### GeoSeries 几何属性

```python
# 面积（投影坐标系下，单位与 CRS 一致）
gdf_projected.geometry.area

# 长度（线要素）
gdf_projected.geometry.length

# 边界矩形
gdf.geometry.bounds          # 返回 DataFrame (minx, miny, maxx, maxy)
gdf.geometry.total_bounds    # 整个 GeoDataFrame 的边界

# 质心
gdf.geometry.centroid

# 凸包
gdf.geometry.convex_hull

# 包络矩形
gdf.geometry.envelope

# 几何类型
gdf.geometry.geom_type       # 返回 Series: 'Point', 'Polygon', ...

# 坐标数量
gdf.geometry.count_coordinates()
```

### 几何变换

```python
# 缓冲区
buffered = gdf.geometry.buffer(distance=100)   # 投影坐标系下，单位为米

# 简化
simplified = gdf.geometry.simplify(tolerance=50)

# 仿射变换
from shapely import affinity
rotated = gdf.geometry.apply(lambda g: affinity.rotate(g, angle=45))
```

### 集合运算（逐元素）

```python
# 两个 GeoSeries 逐元素交集
result = gdf1.geometry.intersection(gdf2.geometry)

# 逐元素合并
result = gdf1.geometry.union(gdf2.geometry)

# 逐元素差集
result = gdf1.geometry.difference(gdf2.geometry)

# 逐元素对称差
result = gdf1.geometry.symmetric_difference(gdf2.geometry)
```

### 空间谓词

```python
# 逐元素空间关系判断（返回 bool Series）
gdf1.geometry.intersects(gdf2.geometry)
gdf1.geometry.within(gdf2.geometry)
gdf1.geometry.contains(gdf2.geometry)
gdf1.geometry.touches(gdf2.geometry)
gdf1.geometry.crosses(gdf2.geometry)
gdf1.geometry.overlaps(gdf2.geometry)
gdf1.geometry.disjoint(gdf2.geometry)
```

### 常用几何操作速查

| 操作 | 方法 | 返回类型 |
|------|------|---------|
| 缓冲区 | `.buffer(distance)` | GeoSeries |
| 质心 | `.centroid` | GeoSeries |
| 凸包 | `.convex_hull` | GeoSeries |
| 简化 | `.simplify(tolerance)` | GeoSeries |
| 包络矩形 | `.envelope` | GeoSeries |
| 边界 | `.boundary` | GeoSeries |
| 全部合并 | `.union_all()` | 单个 Geometry |
| 面积 | `.area` | Series (float) |
| 长度 | `.length` | Series (float) |
| 距离 | `.distance(other)` | Series (float) |
| 相交判断 | `.intersects(other)` | Series (bool) |
| 包含判断 | `.contains(other)` | Series (bool) |
| 位于内部 | `.within(other)` | Series (bool) |

---

## 空间连接与叠加分析

### 空间连接（sjoin）

```python
# 空间连接：将 points 中的点与 polygons 中包含该点的面匹配
result = gpd.sjoin(points_gdf, polygons_gdf, how="inner", predicate="within")

# 支持的 predicate 值：
# "intersects"（默认）、"within"、"contains"、"crosses"、"touches"、"overlaps"

# 支持的 how 值：
# "inner"（默认）、"left"、"right"

# 最近邻空间连接
result = gpd.sjoin_nearest(points_gdf, lines_gdf, how="inner", max_distance=100)
```

### 叠加分析（overlay）

```python
# 叠加分析：两个面图层的几何集合运算
# 交集
result = gpd.overlay(gdf1, gdf2, how="intersection")

# 合并
result = gpd.overlay(gdf1, gdf2, how="union")

# 差集
result = gpd.overlay(gdf1, gdf2, how="difference")

# 对称差
result = gpd.overlay(gdf1, gdf2, how="symmetric_difference")

# 裁剪（identity）
result = gpd.overlay(gdf1, gdf2, how="identity")
```

### 融合（dissolve）

```python
# 按属性分组聚合几何
dissolved = gdf.dissolve(by="province", aggfunc="sum")

# 全部融合为一个几何
dissolved_all = gdf.dissolve()
```

### 裁剪（clip）

```python
# 按 mask 裁剪
clipped = gpd.clip(gdf, mask_gdf)
```

---

## 属性操作与数据处理

GeoPandas 继承 pandas 的全部数据操作能力：

```python
# 筛选
subset = gdf[gdf["population"] > 100000]

# 新增列
gdf["area_km2"] = gdf.geometry.area / 1e6

# 分组聚合
stats = gdf.groupby("province")["population"].sum()

# 合并（基于属性）
merged = gdf.merge(df, on="city_code")

# 排序
gdf_sorted = gdf.sort_values("population", ascending=False)

# 缺失值处理
gdf = gdf.dropna(subset=["geometry"])
```

---

## 地图可视化

### 基础绑图

```python
import matplotlib.pyplot as plt

# 基础绘图
gdf.plot()
plt.show()

# 按属性着色（分级色彩图）
gdf.plot(column="population", cmap="YlOrRd", legend=True)
plt.title("Population Distribution")
plt.show()

# 自定义样式
gdf.plot(
    color="lightblue",
    edgecolor="black",
    linewidth=0.5,
    figsize=(12, 8)
)
plt.show()
```

### 多图层叠加

```python
fig, ax = plt.subplots(figsize=(12, 8))

# 底图：行政区划面
polygons_gdf.plot(ax=ax, color="lightyellow", edgecolor="gray")

# 叠加：道路线
roads_gdf.plot(ax=ax, color="red", linewidth=0.5)

# 叠加：兴趣点
poi_gdf.plot(ax=ax, color="blue", markersize=5)

ax.set_title("Map Overlay")
plt.show()
```

### 分级色彩图（Choropleth）

```python
# 自然断点分级
gdf.plot(
    column="gdp",
    scheme="NaturalBreaks",
    k=5,
    cmap="Blues",
    legend=True,
    legend_kwds={"title": "GDP", "loc": "lower right"}
)
plt.show()

# 分位数分级
gdf.plot(column="density", scheme="Quantiles", k=5, cmap="Reds", legend=True)
plt.show()
```

### 交互式地图（配合 folium）

```python
# 导出为交互式 HTML 地图
m = gdf.explore(column="population", cmap="YlOrRd", tooltip=["name", "population"])
m.save("map.html")
```

---

## 空间索引

GeoPandas 内置 R-tree 空间索引，可加速空间查询：

```python
# 自动创建空间索引
sindex = gdf.sindex

# 查询与给定几何相交的要素索引
from shapely.geometry import box
query_geom = box(116.0, 39.0, 117.0, 40.0)
candidate_idx = list(sindex.query(query_geom))

# 在 sjoin 中自动使用空间索引（无需手动调用）
```

---

## 从其他数据构造 GeoDataFrame

### 从 pandas DataFrame 构造

```python
import pandas as pd
from shapely.geometry import Point

df = pd.DataFrame({
    "name": ["Beijing", "Shanghai", "Guangzhou"],
    "lat": [39.9, 31.2, 23.1],
    "lon": [116.4, 121.5, 113.3]
})

# 方法 1：从经纬度列创建
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["lon"], df["lat"]),
    crs="EPSG:4326"
)

# 方法 2：从 WKT 字符串创建
df["wkt"] = ["POINT(116.4 39.9)", "POINT(121.5 31.2)", "POINT(113.3 23.1)"]
from shapely import wkt
df["geometry"] = df["wkt"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
```

### 从 GeoJSON 字典构造

```python
from shapely.geometry import shape

geojson = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [116.4, 39.9]}, "properties": {"name": "Beijing"}}
    ]
}
gdf = gpd.GeoDataFrame.from_features(geojson["features"], crs="EPSG:4326")
```

---

## 典型工作流示例

### 示例 1：读取 → 投影 → 缓冲区分析 → 导出

```python
import geopandas as gpd

# 读取学校点位数据
schools = gpd.read_file("data/schools.geojson")

# 重投影到 UTM（单位为米）
schools_utm = schools.to_crs("EPSG:32650")

# 500 米缓冲区
buffer_500m = schools_utm.copy()
buffer_500m["geometry"] = schools_utm.geometry.buffer(500)

# 导出结果
buffer_500m.to_file("output/school_buffers.gpkg", driver="GPKG")
```

### 示例 2：空间连接（点落入哪个行政区）

```python
import geopandas as gpd

# 读取数据
poi = gpd.read_file("data/poi.geojson")
districts = gpd.read_file("data/districts.gpkg")

# 确保 CRS 一致
poi = poi.to_crs(districts.crs)

# 空间连接：每个 POI 关联所在行政区
result = gpd.sjoin(poi, districts, how="left", predicate="within")

# 统计每个行政区的 POI 数量
poi_count = result.groupby("district_name").size().reset_index(name="poi_count")
print(poi_count)
```

### 示例 3：叠加分析（两个面图层求交集）

```python
import geopandas as gpd

# 读取两个面图层
landuse = gpd.read_file("data/landuse.gpkg")
flood_zone = gpd.read_file("data/flood_zone.gpkg")

# 确保 CRS 一致
flood_zone = flood_zone.to_crs(landuse.crs)

# 交集叠加
at_risk = gpd.overlay(landuse, flood_zone, how="intersection")

# 计算受影响面积
at_risk_projected = at_risk.to_crs("EPSG:32650")
at_risk_projected["area_m2"] = at_risk_projected.geometry.area
at_risk_projected["area_km2"] = at_risk_projected["area_m2"] / 1e6

print(at_risk_projected[["land_type", "area_km2"]].groupby("land_type").sum())
```

### 示例 4：融合行政区 → 分级色彩图

```python
import geopandas as gpd
import matplotlib.pyplot as plt

# 读取数据
gdf = gpd.read_file("data/counties.gpkg")

# 按省份融合
provinces = gdf.dissolve(by="province", aggfunc={"population": "sum", "area_km2": "sum"})

# 计算人口密度
provinces["density"] = provinces["population"] / provinces["area_km2"]

# 绘制分级色彩图
fig, ax = plt.subplots(figsize=(12, 8))
provinces.plot(
    column="density",
    cmap="YlOrRd",
    scheme="NaturalBreaks",
    k=5,
    legend=True,
    ax=ax
)
ax.set_title("Population Density by Province")
plt.tight_layout()
plt.savefig("output/density_map.png", dpi=150)
plt.show()
```

### 示例 5：CSV → GeoDataFrame → GeoJSON

```python
import pandas as pd
import geopandas as gpd

# 读取 CSV（含经纬度列）
df = pd.read_csv("data/stations.csv")

# 创建 GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:4326"
)

# 导出 GeoJSON
gdf.to_file("output/stations.geojson", driver="GeoJSON")
```

### 示例 6：GeoParquet 高性能读写

```python
import geopandas as gpd

# 读取大型 Parquet 数据（比 Shapefile 快数倍）
gdf = gpd.read_parquet("data/buildings.parquet")

# 处理
gdf_projected = gdf.to_crs("EPSG:32650")
gdf_projected["area_m2"] = gdf_projected.geometry.area

# 写出 Parquet
gdf_projected.to_parquet("output/buildings_with_area.parquet")
```

---

## AI 使用建议

### 推荐工作流

1. **读取数据**：使用 `gpd.read_file()` 或 `gpd.read_parquet()` 加载空间数据
2. **检查数据**：查看 `gdf.head()`、`gdf.crs`、`gdf.geometry.geom_type`、`gdf.shape`
3. **统一 CRS**：在空间操作前确保所有数据使用相同坐标参考系（`to_crs()`）
4. **执行分析**：使用 `sjoin()` / `overlay()` / `dissolve()` / `buffer()` 等方法
5. **导出结果**：使用 `to_file()` / `to_parquet()` 保存

### 关键注意事项

1. **CRS 一致性**：空间连接、叠加分析等操作前，必须确保所有 GeoDataFrame 使用相同 CRS。使用 `gdf.to_crs(target_gdf.crs)` 统一。
2. **投影后再算面积/距离**：`EPSG:4326`（经纬度）下 `.area` 返回的是「平方度」而非面积单位，需先 `to_crs()` 到投影坐标系（如 UTM）。
3. **set_crs 不等于 to_crs**：`set_crs()` 仅声明坐标系而不变换坐标；`to_crs()` 执行实际坐标变换。弄反会导致数据错位。
4. **大数据量优化**：
   - 使用 GeoParquet 替代 Shapefile 以获得更快的 I/O 性能
   - 使用 `read_file()` 的 `bbox` 或 `mask` 参数进行空间过滤读取
   - 使用 `sindex`（空间索引）加速空间查询
5. **几何有效性**：操作前可检查 `gdf.geometry.is_valid`，使用 `gdf.geometry.make_valid()` 修复无效几何。
6. **内存管理**：处理大型数据集时，尽早筛选不需要的列和行，减少内存占用。
7. **文件路径使用绝对路径**：避免工作目录不确定导致文件找不到。
8. **GeoJSON 精度**：写出 GeoJSON 时可能丢失浮点精度，对精度敏感的场景推荐 GeoPackage 或 GeoParquet。
9. **Shapefile 限制**：Shapefile 字段名最长 10 字符、文件大小限制 2GB、不支持 NULL 值。推荐使用 GeoPackage 或 GeoParquet 替代。
10. **版本兼容**：GeoPandas 1.0+ 要求 Shapely 2.0+，不再支持旧版 Shapely 1.x 或 PyGEOS。

### 错误处理

```python
import geopandas as gpd

# 文件读取失败
try:
    gdf = gpd.read_file("data/missing.shp")
except Exception as e:
    print(f"文件读取失败: {e}")

# CRS 缺失
if gdf.crs is None:
    print("警告：数据缺少 CRS 信息，请使用 set_crs() 设置")
    gdf = gdf.set_crs("EPSG:4326")

# 几何无效
invalid = gdf[~gdf.geometry.is_valid]
if len(invalid) > 0:
    print(f"发现 {len(invalid)} 个无效几何，正在修复...")
    gdf["geometry"] = gdf.geometry.make_valid()

# 空间连接 CRS 不一致
if poi.crs != districts.crs:
    poi = poi.to_crs(districts.crs)
result = gpd.sjoin(poi, districts, how="left", predicate="within")
```

---

## 参考链接

- **项目地址：** <https://github.com/geopandas/geopandas>
- **官方文档：** <https://geopandas.org/en/stable/>
- **API 参考：** <https://geopandas.org/en/stable/docs/reference.html>
- **用户指南：** <https://geopandas.org/en/stable/docs/user_guide.html>
- **安装指南：** <https://geopandas.org/en/stable/getting_started/install.html>
- **示例集：** <https://geopandas.org/en/stable/gallery/index.html>
- **更新日志：** <https://geopandas.org/en/stable/docs/changelog.html>
- **PyPI：** <https://pypi.org/project/geopandas/>
- **问题追踪：** <https://github.com/geopandas/geopandas/issues>
