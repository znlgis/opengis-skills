---
name: spatialite
description: "Use when adding spatial SQL to a single-file SQLite database with SpatiaLite — mod_spatialite loading, InitSpatialMetaData, AddGeometryColumn, CreateSpatialIndex/MbrWithin, ST_Transform and GEOS predicates, spatialite_tool or ogr2ogr import of Shapefile, and GPKG fallback; also for 'no such module: mod_spatialite', 'no such function: InitSpatialMetaData', and 'the SPATIALITE_SECURITY environment variable' errors. libspatialite 5.1.0."
tags:
  - spatialite
  - sqlite
  - sql
  - gis
  - spatial
  - geospatial
  - python
  - vector
  - gpkg
  - command-line
---

> **项目地址：** <https://www.gaia-gis.it/fossil/libspatialite/index>
>
> **官方文档：** <https://www.gaia-gis.it/gaia-sins/spatialite-sql-latest.html>
>
> **当前版本：** libspatialite 5.1.0（2023-08-04）；spatialite-tools 5.1.0a（2023-08-13），截至 2026-10 仍为最新
>
> **安装包：** Debian/Ubuntu `libsqlite3-mod-spatialite` 5.1.0-3、`spatialite-bin` 5.1.0a-2；conda-forge `libspatialite` 5.1.0
>
> **许可证：** MPL-1.1 / GPL-2.0+ / LGPL-2.1+ 三许可（libspatialite）；spatialite-tools 为 GPL-3.0+

## 概述

SpatiaLite 是 SQLite 的空间扩展库。它把完整的空间 SQL 能力加进 SQLite：几何类型、空间索引、坐标转换与 OGC 关系谓词，而数据库仍然是**单个普通文件**，不需要任何服务端进程。官方把它定位为"SQLite 上的 PostGIS 替代品"，适合嵌入式、桌面应用与只读发布场景。

核心组件：

- **libspatialite**：扩展库本体，以 `mod_spatialite` 模块形式加载进 SQLite，提供 SQL 函数
- **spatialite-tools**：命令行工具集（`spatialite` shell、`spatialite_tool` 导入导出等）
- **元数据表**：`geometry_columns` 与 `spatial_ref_sys`，由 `InitSpatialMetaData` 创建
- **RTree 空间索引**：`CreateSpatialIndex` 建立并与主表触发器保持同步
- **GPKG 兼容**：同一套函数能读写 OGC GeoPackage

**与 GeoPackage 的关系：** GeoPackage 是 SQLite 表格结构的标准封装；SpatiaLite 是功能更全的扩展实现。要跨工具交换数据时优先 GPKG，要完整空间 SQL 能力时用 SpatiaLite。

## 环境准备

### 方式一：系统包（Debian / Ubuntu）

```bash
# 扩展模块（Python 与 sqlite3 CLI 都用它）
sudo apt install libsqlite3-mod-spatialite

# 命令行工具（spatialite shell、spatialite_tool 等）
sudo apt install spatialite-bin

# 开发头文件（自己编译或链接 libspatialite 时需要）
sudo apt install libspatialite-dev
```

Debian trixie 上的版本为 5.1.0，与上游一致；更老的发行版（如 bookworm 的 5.0.1）会落后一个小版本。

### 方式二：conda / mamba

```bash
conda install -c conda-forge libspatialite
```

conda-forge 的 `libspatialite` 为 5.1.0，Windows / macOS / Linux 均有构建，是跨平台最省事的方式。

### 方式三：Windows 预编译包

官方站点提供 Windows 二进制（`mod_spatialite-x.y.z-win-x86_64.zip` 一类命名），解压后把目录加入 `PATH`，或把 `mod_spatialite.dll` 放到与 sqlite3.exe 同级的目录。用 conda 装则无需手工放置 DLL。

### 方式四：源码编译

```bash
curl -LO https://www.gaia-gis.it/gaia-sins/libspatialite-5.1.0-RC0.tar.gz
tar xzf libspatialite-5.1.0-RC0.tar.gz
cd libspatialite-5.1.0
./configure --disable-rttopo      # 按需启用 GEOS/PROJ/RTTOPO 等依赖
make -j"$(nproc)"
sudo make install
sudo ldconfig
```

依赖链较长（SQLite、GEOS、PROJ、FreeXL、libxml2 等），没有特殊需求时优先用包管理器。

### 验证

```bash
# 1) 库文件是否存在
ls /usr/lib/x86_64-linux-gnu/mod_spatialite.so     # Linux
# Windows 下为 mod_spatialite.dll，macOS 下为 mod_spatialite.dylib

# 2) CLI 能否加载扩展并报出版本
spatialite :memory: "SELECT spatialite_version();"

# 3) Python 侧能否加载
python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.enable_load_extension(True); c.load_extension('mod_spatialite'); print(c.execute('SELECT spatialite_version()').fetchone())"
```

三条任一失败，先解决加载问题再写 SQL。

## 核心 API

### 加载扩展

```bash
# CLI：进入 shell 后加载
spatialite mydb.sqlite
spatialite> .load mod_spatialite

# CLI：一次性执行（把扩展加载与 SQL 放在同一次调用里）
spatialite mydb.sqlite -cmd ".load mod_spatialite" "SELECT spatialite_version();"
```

```python
import sqlite3

con = sqlite3.connect("mydb.sqlite")
con.enable_load_extension(True)          # Python 3.10+ 需要显式开启
con.load_extension("mod_spatialite")     # 找不到时传绝对路径
con.enable_load_extension(False)

print(con.execute("SELECT spatialite_version()").fetchone())
```

### 初始化空间元数据

每个数据库**只需执行一次**：

```sql
-- 创建 geometry_columns 与 spatial_ref_sys（1 = 成功）
SELECT InitSpatialMetaData(1);

-- 只要 WGS84 相关 SRID，体积更小
SELECT InitSpatialMetaData(1, 'WGS84');

-- 完全不插入 EPSG 定义（自己管理 SRID）
SELECT InitSpatialMetaData(1, 'NONE');
```

返回 1 表示创建成功；对已初始化的库重复调用会返回 0，不会破坏数据。

### 建表并声明几何列

先建普通表，再用 `AddGeometryColumn` 注册几何列（不要手写 geometry 列）：

```sql
CREATE TABLE poi (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT
);

SELECT AddGeometryColumn('poi', 'geom', 4326, 'POINT', 'XY');

INSERT INTO poi (name, geom)
VALUES ('tiananmen', MakePoint(116.397, 39.908, 4326)),
       ('waitan',    MakePoint(121.490, 31.241, 4326));
```

`AddGeometryColumn` 会同时建触发器，保证写入的几何类型与 SRID 与声明一致。

### 空间索引

```sql
-- 建 RTree 索引（自动创建同步触发器）
SELECT CreateSpatialIndex('poi', 'geom');

-- 校验索引一致性；参数省略时检查全部
SELECT CheckSpatialIndex('poi', 'geom');

-- 更新图层统计信息（要素数与总范围）
SELECT UpdateLayerStatistics('poi', 'geom');

-- 需要停用时
-- SELECT DisableSpatialIndex('poi', 'geom');
```

### 常用空间函数

| 类别 | 函数 | 说明 |
|------|------|------|
| 构造 | MakePoint(x, y [, srid]) | 构造点 |
| 构造 | GeomFromText(wkt [, srid]) / ST_GeomFromText | WKT 转几何 |
| 输出 | AsText(geom) / ST_AsText | 几何转 WKT |
| 输出 | AsBinary(geom) / AsGeoJSON(geom) | WKB / GeoJSON |
| 谓词 | ST_Intersects / ST_Contains / ST_Within / ST_Touches / ST_Crosses / ST_Disjoint | OGC 关系 |
| 谓词 | MbrWithin / MbrIntersects / MbrDisjoint | 仅比较包围盒，最快 |
| 度量 | ST_Area / ST_Length / ST_Distance / ST_Perimeter | 平面度量（单位随 SRID） |
| 运算 | ST_Buffer / ST_Intersection / ST_Union / ST_Difference / ST_ConvexHull | GEOS 运算 |
| 转换 | ST_Transform(geom, srid) | 坐标转换（需 PROJ） |
| 修复 | ST_MakeValid / GeosMakeValid / ST_IsValid | 无效几何处理 |

```sql
-- 5 公里内的点（先用 MBR 粗筛走索引，再精算距离）
SELECT a.name, b.name, ST_Distance(a.geom, b.geom) AS deg
FROM poi a, poi b
WHERE a.id < b.id
  AND MbrWithin(b.geom, ST_Buffer(a.geom, 0.05))
  AND ST_Distance(a.geom, b.geom) < 0.05;

-- 投影到米制后再算距离，避免"度"当"米"
SELECT ST_Distance(ST_Transform(a.geom, 3857), ST_Transform(b.geom, 3857)) AS meters
FROM poi a, poi b
WHERE a.id = 1 AND b.id = 2;
```

### 元数据与图层信息

```sql
-- 库里有哪些几何列
SELECT f_table_name, f_geometry_column, geometry_type, srid, spatial_index_enabled
FROM geometry_columns;

-- 某图层的包围盒
SELECT ST_AsText(ST_Envelope(ST_Collect(geom))) FROM poi;
```

## 典型工作流：Shapefile → SpatiaLite → 空间查询 → 导出

输入 `data/roads.shp` 与 `data/cities.shp`，目标是找出每条道路 2 公里内的城市并导出结果表。

**步骤 1：导入（两种方式任选）**

```bash
# 方式 A：spatialite_tool（参数随版本略有差异，先跑 --help 确认）
spatialite_tool --help

# 方式 B：ogr2ogr（GDAL，最稳定，强烈推荐）
ogr2ogr -f SQLite -dsco SPATIALITE=YES out.gis.sqlite data/roads.shp -nln roads
ogr2ogr -f SQLite -dsco SPATIALITE=YES -append out.gis.sqlite data/cities.shp -nln cities
```

`-dsco SPATIALITE=YES` 让 GDAL 按 SpatiaLite 格式写库（而不是纯 SQLite 表）；导入后 GDAL 会建好元数据与索引。

**步骤 2：初始化并核对**

```python
import sqlite3

con = sqlite3.connect("out.gis.sqlite")
con.enable_load_extension(True)
con.load_extension("mod_spatialite")
con.enable_load_extension(False)

# 若库是新建的空库，先执行一次
# con.execute("SELECT InitSpatialMetaData(1)")

for row in con.execute("""
    SELECT f_table_name, f_geometry_column, geometry_type, srid, spatial_index_enabled
    FROM geometry_columns
"""):
    print(row)
```

**步骤 3：空间查询**

```python
rows = con.execute("""
    SELECT r.name AS road, c.name AS city,
           ST_Distance(ST_Transform(r.geom, 3857),
                       ST_Transform(c.geom, 3857)) AS meters
    FROM roads r
    JOIN cities c
      ON MbrWithin(c.geom, ST_Buffer(r.geom, 0.02))
     AND ST_Distance(r.geom, c.geom) < 0.02
    ORDER BY meters
""").fetchall()
print(len(rows), "pairs")
```

**步骤 4：导出结果**

```python
con.execute("""
    CREATE TABLE road_city AS
    SELECT r.name AS road, c.name AS city,
           ST_Distance(ST_Transform(r.geom, 3857),
                       ST_Transform(c.geom, 3857)) AS meters
    FROM roads r
    JOIN cities c
      ON MbrWithin(c.geom, ST_Buffer(r.geom, 0.02))
     AND ST_Distance(r.geom, c.geom) < 0.02
""")
con.commit()
print(con.execute("SELECT count(*) FROM road_city").fetchone())
```

```bash
# 用 GDAL 把结果导成 GeoPackage / GeoJSON
ogr2ogr -f GPKG out/road_city.gpkg out.gis.sqlite road_city
```

**步骤 5：验收**

```bash
ogrinfo -so out/road_city.gpkg road_city | head -20
```

确认要素数、几何类型与 SRID 与预期一致。

## 与 Python 生态配合

```python
import sqlite3
import geopandas as gpd

con = sqlite3.connect("out.gis.sqlite")
con.enable_load_extension(True)
con.load_extension("mod_spatialite")
con.enable_load_extension(False)

# 读成 GeoDataFrame（GeoPandas 走 pyogrio/GDAL，会自动识别 SpatiaLite）
gdf = gpd.read_file("out.gis.sqlite", layer="cities")

# 用 SQL 结果再构造 GeoDataFrame
rows = con.execute("SELECT name, AsText(geom) FROM cities").fetchall()
print(rows[:3])
```

注意：GeoPandas 读 SpatiaLite 依赖 GDAL 的 SQLite 驱动；写回时用 `gdf.to_file("out.gis.sqlite", layer="new_layer", driver="SQLite")` 即可。

## 最佳实践

1. **几何列一定用 AddGeometryColumn 建**：手写 geometry 列会绕过元数据与触发器，后续空间函数找不到列。
2. **InitSpatialMetaData 只跑一次**：新库初始化后不要重复执行；用 `'WGS84'` 模式可以显著缩小 spatial_ref_sys。
3. **先 MBR 粗筛再精算**：`MbrWithin` / `MbrIntersects` 能吃到 RTree 索引，直接对全部行跑 ST_Distance 会很慢。
4. **SRID 必须一致**：不同 SRID 的几何不能直接比较，先 `ST_Transform` 统一。
5. **单位意识**：4326 下 ST_Distance 返回"度"、ST_Area 返回"平方度"；要米就投到米制投影（如 3857）。
6. **空间索引用 CheckSpatialIndex 体检**：批量导入或大量 UPDATE 之后跑一次，确认索引与主表同步。
7. **交换数据优先 GPKG**：SpatiaLite 专有函数多，跨工具可移植性不如 GeoPackage。
8. **写事务要提交**：Python 里 `con.commit()`，否则 `CreateSpatialIndex` 的触发器与数据都不落盘。

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| no such function: InitSpatialMetaData | 扩展未加载，或加载的是空壳库 | 先 `.load mod_spatialite`（CLI）或 `load_extension("mod_spatialite")`（Python），用 `spatialite_version()` 验证 |
| no such module: mod_spatialite | 动态库不在搜索路径 | 指定绝对路径加载；Linux 装 `libsqlite3-mod-spatialite`，Windows 把 DLL 放同目录或加 PATH |
| Python 报 "not authorized" / 无法 enable_load_extension | 解释器禁用了扩展加载 | 用系统 Python 或开启 `--enable-loadable-sqlite-extensions` 的构建；PyPI 的 `pysqlite3-binary` 可用于替换 |
| CLI 里 `.load` 报加载失败 | 动态库路径不对，或 shell 与库的位数/构建不匹配 | 先用 `python -c` 那条验证库本身可加载，再在 CLI 里给绝对路径；仍失败时改用 Python 或 GDAL 路径 |
| CreateSpatialIndex 返回 -1 | 表里存在名为 rowid 的物理列，遮蔽了真实 ROWID | 重命名该列后再建索引 |
| ST_Intersects 报 "geometry has invalid SRID" | 混入了 SRID 为 -1 或 0 的几何 | 用 `GeomFromText(wkt, 4326)` 或 `ST_Transform` 赋上正确 SRID |
| 空间查询依旧很慢 | 只用了 ST_Distance，没有 MBR 前置条件 | 先加 `MbrWithin` 或 `MbrIntersects` 条件让 RTree 生效，再精确判断 |
| apt 装的版本比官网旧 | 发行版冻结版本 | 需要 5.1.0 特性时用 conda-forge，或从源码编译 |
| 用 GDAL 打开 SQLite 库看不到图层 | 库不是 SpatiaLite 格式 | 导入时加 `-dsco SPATIALITE=YES`；已存在的库可用 GDAL 的 `SQLite` 驱动按层读取 |

## AI 使用建议

- **先确认库能被加载**：任何排查都从 `python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.enable_load_extension(True); c.load_extension('mod_spatialite')"` 开始；库加载不了时，SQL 报错没有诊断价值。
- **版本差异**：SpatiaLite 5.x 的函数集与 4.x 不同（如 `GeosMakeValid`、`InitSpatialMetaData` 的重载）。动手前查 `spatialite_version()`，并按官方函数参考核对函数名与参数。
- **优先用 ogr2ogr 导入**：命令行工具的参数在不同构建间不一致，GDAL 的 `-dsco SPATIALITE=YES` 路径最稳定；确需 `spatialite_tool` 时先跑 `--help` 核对参数。
- **验证产物**：导入或建索引后回读 `geometry_columns`（几何列、SRID、spatial_index_enabled）与 `CheckSpatialIndex(`…`)`，确认索引真的生效，再宣称"查询已优化"。
- **写操作确认**：`DROP TABLE`、`DisableSpatialIndex`、批量 `DELETE` 不可回滚到旧状态（SQLite 事务只保护单次会话）；执行前备份 .sqlite 文件。

## 相关技能

- **postgis** — 服务端空间数据库，能力更完整：[../postgis/SKILL.md](../postgis/SKILL.md)
- **gdal** — ogr2ogr 导入导出，事实上的稳定路径：[../gdal/SKILL.md](../gdal/SKILL.md)
- **geopandas** — Python 侧读写 SpatiaLite/GPKG：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **duckdb-spatial** — 另一种嵌入式空间分析方案：[../duckdb-spatial/SKILL.md](../duckdb-spatial/SKILL.md)
- **proj** — ST_Transform 依赖的坐标转换库：[../proj/SKILL.md](../proj/SKILL.md)

## 参考资源
- 官方主页（fossil 仓库）：<https://www.gaia-gis.it/fossil/libspatialite/index>
- SQL 函数参考：<https://www.gaia-gis.it/gaia-sins/spatialite-sql-latest.html>
- spatialite-tools：<https://www.gaia-gis.it/fossil/spatialite-tools/index>
- GeoPackage 标准：<https://www.geopackage.org/>
