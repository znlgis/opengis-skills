---
name: duckdb-spatial
description: "Use when doing spatial analysis inside a DuckDB database or SQL pipeline — INSTALL spatial / LOAD spatial, ST_Read over Shapefile/GeoPackage/GeoJSON, ST_Point/ST_GeomFromText, ST_Intersects/ST_Contains/ST_Buffer joins, ST_Area_Spheroid, ST_AsMVT tiles, DuckDB-WASM in the browser; also for 'Extension spatial is not installed' or spatial function does not exist, GEOMETRY vs WKB_BLOB friction, and exporting query results to GeoParquet. DuckDB 2.0 built-in spatial extension."
tags:
  - duckdb
  - sql
  - python
  - spatial
  - geospatial
  - extension
  - vector
  - geoparquet
  - analysis
  - cli
---

> **项目地址：** <https://github.com/duckdb/duckdb-spatial>
>
> **官方文档：** <https://duckdb.org/docs/stable/core_extensions/spatial/overview>
>
> **函数参考：** <https://duckdb.org/docs/stable/core_extensions/spatial/functions>
>
> **DuckDB 包（PyPI）：** 2.0.0（截至 2026-10）
>
> **扩展分发：** 随 DuckDB 版本自动匹配，INSTALL spatial 从 extensions.duckdb.org 拉取（无独立版本号）
>
> **许可证：** MIT

## 概述

DuckDB Spatial 是 DuckDB 官方的核心扩展，把列式分析数据库变成可读写地理数据的空间分析工具。它基于 OGC Simple Features 模型增加 GEOMETRY 类型，底层用 GEOS 做拓扑运算、用 PROJ 做坐标转换、用 GDAL 读文件。

- **零服务依赖**：进程内运行，扩展按需安装，无需 PostGIS 或服务器
- **轻量几何类型**：POINT_2D / LINESTRING_2D / POLYGON_2D / BOX_2D 有原生函数重载，比通用 GEOMETRY 路径快
- **ST_Read 表函数**：通过 GDAL 直接查询 Shapefile、GeoPackage、GeoJSON、FlatGeoBuf 等
- **SQL 即分析**：空间谓词、聚合（ST_Union_Agg、ST_Extent_Agg）、瓦片编码（ST_AsMVT）
- **与 Parquet/CSV/JSON 同库联查**：空间表可直接 JOIN 普通表，无须导入导出
- **WASM 可用**：同一扩展编译为 WebAssembly，GeoLibre 与 DuckDB-WASM 前端都靠它

扩展自带 GEOS/PROJ/GDAL 静态链接版本，机器上不需要另外安装 GDAL。

## 环境准备

### 安装 DuckDB

```bash
# 1) Python（推荐用于脚本与 Notebook）
pip install duckdb==2.0.0

# 2) conda / mamba
conda install -c conda-forge duckdb

# 3) 官方 CLI（单文件可执行）
#    Windows: 下载 duckdb_cli-windows-amd64.zip 后解压
#    macOS:   brew install duckdb
```

### 安装 spatial 扩展

```sql
INSTALL spatial;
LOAD spatial;
```

INSTALL 会把扩展写入用户目录（~/.duckdb/extensions/<version>/<platform>/），只需一次；之后每次会话 LOAD spatial 即可。spatial 不属于 autoloadable 扩展，忘记 LOAD 时所有 ST_* 函数都会报"不存在"。

### 验证

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")
print(con.execute("SELECT duckdb_version()").fetchone())
print(con.execute("SELECT ST_AsText(ST_Point(116.39, 39.90))").fetchone())
print(con.execute("SELECT extension_version FROM duckdb_extensions() WHERE extension_name='spatial'").fetchone())
print(con.execute("SELECT duckdb_proj_version()").fetchone())
```

预期能打印 POINT (116.39 39.9) 与 PROJ 版本号；任一失败即扩展未正确加载。

## 核心 API

### 几何构造与序列化

| 函数 | 作用 | 返回 |
|------|------|------|
| ST_Point(x, y) / ST_MakePoint(x, y) | 构造点（两者等价，后者为 PostGIS 兼容名） | GEOMETRY |
| ST_GeomFromText(wkt [, ignore_invalid]) | 从 WKT 解析 | GEOMETRY |
| ST_GeomFromGeoJSON(json) / ST_AsGeoJSON(geom) | GeoJSON fragment 互转 | GEOMETRY / JSON |
| ST_GeomFromWKB(blob) / ST_AsWKB(geom) | WKB 互转 | GEOMETRY / WKB_BLOB |
| ST_MakeEnvelope(minx, miny, maxx, maxy) | 矩形面 | GEOMETRY |
| ST_MakeLine(list_of_points) / ST_MakePolygon(ring) | 线/面构造 | GEOMETRY |
| ST_AsText(geom) | 输出 WKT | VARCHAR |

```sql
SELECT ST_AsText(ST_Point(116.39, 39.90))                          AS pt,
       ST_AsText('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'::GEOMETRY)   AS poly,
       ST_AsWKB('POINT(1 2)'::GEOMETRY)::BLOB                      AS wkb;
```

字符串可以直接带类型转换写成 'POINT(...)'::GEOMETRY，这是最短路径。DuckDB Spatial 的 GEOMETRY 不保存 SRID，因此没有 ST_SetSRID 这类函数。

### 空间关系谓词

| 函数 | 说明 |
|------|------|
| ST_Intersects(a, b) | 相交（含接触） |
| ST_Contains(a, b) / ST_Within(a, b) | 包含 / 被包含 |
| ST_Covers(a, b) / ST_CoveredBy(a, b) | 覆盖（边界计入，比 Contains 宽松） |
| ST_Disjoint(a, b) | 不相交 |
| ST_Touches(a, b) / ST_Crosses(a, b) | 接触 / 穿越 |
| ST_DWithin(a, b, dist) | 距离小于阈值 |
| ST_Intersects_Extent(a, b) | 仅比较包围盒，最快的粗筛 |

```sql
-- 点落在面内：用 EXISTS 半连接，避免笛卡尔积
SELECT c.name
FROM cities c
WHERE EXISTS (
  SELECT 1 FROM countries k
  WHERE ST_Intersects(k.geom, c.geom)
);
```

### 度量与构造

| 函数 | 说明 | 单位 |
|------|------|------|
| ST_Area(geom) | 平面面积（非面返回 0） | 与坐标系一致 |
| ST_Area_Spheroid(geom) | 椭球面积，假定输入为 EPSG:4326 | 平方米 |
| ST_Length(geom) | 平面长度 | 与坐标系一致 |
| ST_Length_Spheroid(geom) | 椭球长度 | 米 |
| ST_Distance(a, b) | 平面距离（忽略 Z） | 与坐标系一致 |
| ST_Distance_Sphere(a, b) | 大圆距离 | 米 |
| ST_Centroid(geom) | 质心 | GEOMETRY |
| ST_Buffer(geom, dist [, num_triangles]) | 缓冲，num_triangles 默认 8 | 与坐标系一致 |
| ST_Simplify / ST_SimplifyPreserveTopology | 简化 | — |
| ST_MakeValid / ST_IsValid | 修复 / 校验 | — |

```sql
-- 经纬度下 ST_Area 的单位是"平方度"，要米制面积就用椭球版本
SELECT name,
       ST_Area(geom)           AS planar_deg2,
       ST_Area_Spheroid(geom)  AS spheroid_m2
FROM countries
ORDER BY spheroid_m2 DESC
LIMIT 5;
```

### 坐标转换

```sql
-- 显式给出源与目标 CRS；always_xy 决定是否强制 x=经度
SELECT ST_AsText(
         ST_Transform(ST_Point(116.39, 39.90), 'EPSG:4326', 'EPSG:3857')
       );

-- 包围盒同样可以转换
SELECT ST_Transform({min_x: -180, min_y: -85, max_x: 180, max_y: 85}::BOX_2D,
                    'EPSG:4326', 'EPSG:3857');
```

CRS 字符串支持 PROJ 认得的写法（'EPSG:4326'、'+proj=longlat +datum=WGS84'、WKT）。ST_Transform 不会替你猜坐标系，源 CRS 必须由你给出。

### 聚合与瓦片

| 函数 | 说明 |
|------|------|
| ST_Union_Agg(geom) | 合并要素（GEOS union） |
| ST_Extent_Agg(geom) | 最小包围盒多边形 |
| ST_Intersection_Agg(geom) | 批量求交 |
| ST_CoverageUnion_Agg(geom) | 覆盖合并（共享边界时更快） |
| ST_AsMVT(row, layer_name, extent, geom_col, id_col) | 生成 Mapbox Vector Tile |
| ST_AsMVTGeom(geom, bounds, extent, buffer, clip) | 裁剪到瓦片边界 |

```sql
-- 按省合并成一条 MultiPolygon，并给出总包围盒
SELECT province,
       ST_AsText(ST_Union_Agg(geom))  AS merged,
       ST_AsText(ST_Extent_Agg(geom)) AS bbox
FROM counties
GROUP BY province;
```

### 文件读写（GDAL 表函数）

| 函数 | 说明 |
|------|------|
| ST_Read(path, ...) | 读矢量文件，参数见下表 |
| ST_Read_Meta(path) | 只读元数据（图层、CRS、字段） |
| ST_ReadSHP(path, encoding) | 不依赖 GDAL 的 Shapefile 读取（快，基础类型） |
| ST_ReadOSM(path) | 直接解析 .osm.pbf，输出原始 Nodes/Ways/Relations |
| ST_Drivers() | 列出编译进来的 GDAL 驱动 |

常用 ST_Read 参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| layer | VARCHAR | 图层名或索引（0 起）；多图层文件必给 |
| spatial_filter_box | BOX_2D | 按包围盒过滤（部分驱动可下推） |
| spatial_filter | WKB_BLOB | 按任意几何过滤 |
| open_options | VARCHAR[] | 透传 GDAL 打开选项，如 FLATTEN_NESTED_ATTRIBUTES=YES |
| allowed_drivers | VARCHAR[] | 限制可用驱动 |
| keep_wkb | BOOLEAN | 返回 wkb_geometry（WKB_BLOB）而非 GEOMETRY |

```sql
-- 单图层文件
CREATE TABLE roads AS SELECT * FROM ST_Read('data/roads.shp');

-- 指定图层 + 包围盒过滤
SELECT * FROM ST_Read('data/city.gpkg',
                      layer := 'buildings',
                      spatial_filter_box := {min_x: 116.0, min_y: 39.5,
                                             max_x: 116.6, max_y: 40.1}::BOX_2D);

-- 先看元数据，再决定读哪个图层
SELECT unnest(layers).name FROM ST_Read_Meta('data/city.gpkg');
```

替换扫描（replacement scan）：.shp、.gpkg、.fgb 三种扩展名可以直接当表名查，无需 ST_Read：

```sql
SELECT * FROM 'data/roads.shp' LIMIT 5;
```

这只是 ST_Read 的语法糖，性能一致；要传参数时仍应显式调用 ST_Read。

## 典型工作流：Shapefile → 空间分析 → GeoParquet

输入 data/roads.shp（线）与 data/districts.shp（面），目标是从每条道路提取落在各区的长度并输出 Parquet。

```python
import duckdb

con = duckdb.connect("analysis.duckdb")
con.execute("INSTALL spatial; LOAD spatial;")

# 1) 读入并落到持久表（避免每次查询重复解析 Shapefile）
con.execute("CREATE OR REPLACE TABLE roads AS SELECT * FROM ST_Read('data/roads.shp');")
con.execute("CREATE OR REPLACE TABLE districts AS SELECT * FROM ST_Read('data/districts.shp');")

# 2) 探明列名与 CRS
print(con.execute("DESCRIBE roads").fetchall())
print(con.execute("""
    SELECT layers[1].geometry_fields[1].crs.auth_name,
           layers[1].geometry_fields[1].crs.auth_code
    FROM ST_Read_Meta('data/roads.shp')
""").fetchone())

# 3) 统一到投影坐标系后再算长度（米），避免把"度"当"米"
con.execute("""
    CREATE OR REPLACE TABLE roads_m AS
    SELECT *, ST_Transform(geom, 'EPSG:4326', 'EPSG:3857') AS geom_m,
              ST_Length(ST_Transform(geom, 'EPSG:4326', 'EPSG:3857')) AS length_m
    FROM roads;
""")
con.execute("""
    CREATE OR REPLACE TABLE districts_m AS
    SELECT *, ST_Transform(geom, 'EPSG:4326', 'EPSG:3857') AS geom_m
    FROM districts;
""")

# 4) 叠加：相交取交线，按区汇总长度
con.execute("""
    CREATE OR REPLACE TABLE road_length_by_district AS
    SELECT d.name AS district,
           SUM(ST_Length(ST_Intersection(r.geom_m, d.geom_m))) AS length_m
    FROM roads_m r
    JOIN districts_m d
      ON ST_Intersects(r.geom_m, d.geom_m)
    GROUP BY d.name
    ORDER BY length_m DESC;
""")

# 5) 输出：几何列写成 WKB
con.execute("""
    COPY (SELECT ST_AsWKB(geom_m) AS geometry, name, length_m FROM roads_m)
    TO 'out/roads_m.parquet' (FORMAT parquet);
""")

print(con.execute("SELECT * FROM road_length_by_district LIMIT 10").fetchall())
```

输出 out/roads_m.parquet 与一张按区汇总的长度表。要点：先把 Shapefile 落到持久表（重复 ST_Read 很慢）、先投影再算长度、按区名分组而不是逐行比较。

## 与 Python / pandas 协作

```python
import duckdb, geopandas as gpd

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

# 查询结果直接转 DataFrame
rows = con.execute("SELECT name, ST_AsText(geom) FROM ST_Read('data/cities.shp')").fetchdf()

# GeoDataFrame 注册成视图后即可用 SQL 查询
districts = gpd.read_file("data/districts.gpkg")
con.register("districts", districts)
print(con.execute("SELECT name, ST_Area(geom) AS area FROM districts ORDER BY area DESC LIMIT 5").fetchall())
```

register 只在当前会话有效；跨进程请建表或直接读文件。

## 输出 GeoParquet 与矢量瓦片

```sql
-- GeoParquet：几何列写成 WKB，字段名用 geometry 便于下游识别
COPY (SELECT ST_AsWKB(geom) AS geometry, name, pop FROM cities)
TO 'out/cities.parquet' (FORMAT parquet);

-- MVT：先裁剪到瓦片，再聚合
WITH tile AS (
  SELECT ST_AsMVTGeom(
           ST_Transform(geom, 'EPSG:4326', 'EPSG:3857'),
           ST_TileEnvelope(12, 3423, 1586)
         ) AS geom,
         name
  FROM cities
  WHERE ST_Intersects_Extent(
          ST_Transform(geom, 'EPSG:4326', 'EPSG:3857'),
          ST_TileEnvelope(12, 3423, 1586))
)
SELECT ST_AsMVT(tile, 'cities', 4096, 'geom') FROM tile;
```

## 性能优化

1. **落表再查**：对同一文件重复 ST_Read 会反复走 GDAL 解析，先 CREATE TABLE AS 物化。GDAL 是单线程的，ST_Read 无法并行。
2. **没有空间索引，先做包围盒粗筛**：DuckDB Spatial 不提供 R-Tree 索引，join 前用 ST_Intersects_Extent 缩小候选集，再用 ST_Intersects 精确判断。
3. **优先用轻量类型**：能落成 POINT_2D / POLYGON_2D 的列走原生实现，必要时用 ST_Force2D 去掉 Z/M。
4. **面积/长度单位要有依据**：经纬度下 ST_Area 的单位是平方度，应改用 ST_Area_Spheroid 或先投影。
5. **投影一次即可**：ST_Transform 是 CPU 热点，放在建表阶段，不要写在 WHERE 里逐行算。
6. **减少字符串往返**：几何尽量保持二进制形态，只在最终输出时 ST_AsText / ST_AsWKB。
7. **大文件用列裁剪**：SELECT name, geom 比 SELECT * 少读属性列。

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Extension spatial is not installed | 只写了 LOAD 没写 INSTALL，或离线环境拉不到扩展 | 先执行 INSTALL spatial；离线时复用扩展目录，或下载官方 unsigned 构建后 INSTALL '<path>'（需 -unsigned 启动） |
| Catalog Error: Scalar Function with name ST_Intersects does not exist | 当前连接没 LOAD spatial | 每个新连接都要 LOAD spatial；Python 里可在建连后立即执行 |
| ST_Area 返回 0 或很小的数 | 输入是经纬度，单位是平方度 | 用 ST_Area_Spheroid，或先 ST_Transform 到米制投影 |
| ST_Transform 报 CRS 解析失败 | 源/目标 CRS 字符串拼错或 PROJ 未识别 | 用 'EPSG:4326' 这类标准写法；SELECT duckdb_proj_version() 确认 PROJ 可用 |
| 读 GeoPackage 只拿到第一个图层 | 多图层文件未指定 layer | 用 ST_Read_Meta 先看 layers，再 ST_Read(..., layer := '...') |
| Shapefile 中文属性乱码 | DBF 编码与默认 UTF-8 不一致 | 用 ST_ReadSHP(path, encoding := 'GBK')，或在 open_options 里给驱动指定编码 |
| 空间 join 极慢 | 没有空间索引，也没做包围盒粗筛 | 先 ST_Intersects_Extent 粗筛，再 ST_Intersects 精筛 |
| 写出的 Parquet 没有 CRS | ST_AsWKB 只写几何，不写 CRS 元数据 | 落盘后用 GeoPandas/GDAL 补写 crs，或用 ogr2ogr 转出 |
| ST_ReadOSM 只返回 node/way 原始表 | 该函数不做几何装配 | 需要成品几何时改用 ST_Read 的 OSM 驱动 |

## DeepSeek Harness 使用建议

- **加载技能**：skill("duckdb-spatial")；技能目录只读，SQL 脚本与输出数据写到会话工作区。
- **先验扩展再写 SQL**：执行前跑 SELECT extension_name, loaded FROM duckdb_extensions() WHERE extension_name='spatial'; 确认 loaded=true；未加载就先 LOAD，不要把"函数不存在"当语法错误去改。
- **版本敏感**：2.0.0 与旧版函数集合有差异（ST_Area_Spheroid、ST_CoverageUnion_Agg 属较新函数）。写示例前用 SELECT function_name FROM duckdb_functions() WHERE function_name LIKE 'ST_%'; 探测实际可用函数。
- **大文件不要整读进内存**：优先用 ST_Read 的 spatial_filter_box / layer 参数与 Parquet 列裁剪；反复查询时先落表。
- **验证产物**：写完 Parquet/MVT 后回读核对 count、ST_IsValid、ST_GeometryType 分布，以及坐标范围是否落在预期 CRS 内。
- **写操作确认**：COPY ... TO、CREATE OR REPLACE TABLE、DROP TABLE 会覆盖文件或表；执行前确认目标路径已被授权覆盖。

## 相关技能

- **postgis** — 服务端空间数据库，DuckDB 的常见替代：[../postgis/SKILL.md](../postgis/SKILL.md)
- **geopandas** — Python 矢量分析，可与 DuckDB 互转：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **gdal** — ST_Read 背后的读写引擎与格式转换：[../gdal/SKILL.md](../gdal/SKILL.md)
- **proj** — CRS 定义与 ST_Transform 的底层库：[../proj/SKILL.md](../proj/SKILL.md)
- **geolibre** — 浏览器里用 DuckDB-WASM Spatial 做 SQL 分析：[../geolibre/SKILL.md](../geolibre/SKILL.md)

## 参考资源
- 扩展仓库：<https://github.com/duckdb/duckdb-spatial>
- 函数总表：<https://duckdb.org/docs/stable/core_extensions/spatial/functions>
- DuckDB 文档：<https://duckdb.org/docs/stable/>
