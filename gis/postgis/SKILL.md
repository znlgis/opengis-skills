---
name: postgis
description: PostGIS 是 PostgreSQL 数据库的空间扩展，为关系型数据库添加地理对象支持，提供完整的空间数据类型、空间索引（GiST/SP-GiST/BRIN）、空间关系判断和 1000+ 空间函数，是事实上的开源空间数据库标准。
tags:
  - postgresql
  - database
  - sql
  - spatial
  - geometry
  - geography
  - raster
  - vector
  - wkt
  - wkb
---

> **项目地址：** <https://github.com/postgis/postgis>
>
> **官方文档：** <https://postgis.net/docs/>
>
> **许可证：** GPL-2.0+

## 概述

PostGIS 是基于 PostgreSQL 的开源空间数据库扩展，遵循 OGC Simple Features for SQL 规范。核心能力：

- **空间数据类型**：`geometry`（平面）、`geography`（球面）、`raster`、`topology`、`3DZ/4DZM`
- **空间索引**：基于 R-Tree-over-GiST，亿级要素仍保持毫秒级查询
- **1000+ 空间函数**：覆盖度量、关系、构造、聚合、栅格代数
- **坐标参考系**：内置 6000+ EPSG 投影，自动 ST_Transform
- **数据导入导出**：与 GDAL/ogr2ogr/shp2pgsql 无缝集成

**版本要求：** PostgreSQL 12+ 配合 PostGIS 3.0+

---

## 环境准备

### 安装

```bash
# Debian/Ubuntu
sudo apt install postgresql-15-postgis-3 postgresql-15-postgis-3-scripts

# CentOS/RHEL
sudo yum install postgis33_15

# macOS
brew install postgis

# Docker（推荐）
docker run --name pg -e POSTGRES_PASSWORD=pg -p 5432:5432 -d postgis/postgis:16-3.4
```

### 启用扩展

```sql
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;     -- 拓扑（可选）
CREATE EXTENSION postgis_raster;       -- 栅格（可选）
CREATE EXTENSION postgis_sfcgal;       -- 3D 高级运算（可选）
SELECT PostGIS_Full_Version();         -- 验证
```

---

## 核心数据类型

| 类型 | 说明 | 适用场景 |
|------|------|---------|
| `geometry(Point, 4326)` | 平面几何，速度快 | 投影坐标系下的常规分析 |
| `geography(Point, 4326)` | 球面几何，距离按米 | 全球范围、跨经线计算 |
| `raster` | 栅格 | DEM、影像 |

---

## 建表与索引

```sql
CREATE TABLE poi (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom geometry(Point, 4326)
);

CREATE INDEX poi_geom_idx ON poi USING GIST (geom);

INSERT INTO poi(name, geom) VALUES
    ('天安门', ST_GeomFromText('POINT(116.397 39.908)', 4326)),
    ('外滩',   ST_SetSRID(ST_MakePoint(121.490, 31.241), 4326));

ANALYZE poi;
```

---

## 常用空间 SQL

### 1. 空间关系

```sql
-- 范围查询：&& 走 GiST 索引
SELECT id, name FROM poi
WHERE geom && ST_MakeEnvelope(116, 39, 117, 40, 4326)
  AND ST_Within(geom, ST_MakeEnvelope(116, 39, 117, 40, 4326));

-- KNN：<-> 走索引
SELECT id, name, geom <-> ST_MakePoint(116.4, 39.9)::geometry AS d
FROM poi ORDER BY d LIMIT 10;

-- 5 公里缓冲区内
SELECT * FROM poi
WHERE ST_DWithin(geom::geography, ST_MakePoint(116.4, 39.9)::geography, 5000);
```

### 2. 几何变换

```sql
SELECT ST_Buffer(geom::geography, 100)::geometry FROM poi;       -- 100 米
SELECT ST_Transform(geom, 3857) FROM poi;                        -- WGS84→Mercator
SELECT ST_SimplifyPreserveTopology(geom, 0.001) FROM province;
SELECT ST_Centroid(geom), ST_ConvexHull(geom), ST_Envelope(geom) FROM province;
```

### 3. 集合运算

```sql
SELECT ST_Union(geom)        FROM city WHERE province_id = 31;
SELECT ST_Intersection(a.geom, b.geom) FROM a, b WHERE a.id=1 AND b.id=2;
SELECT ST_Difference(a.geom, b.geom)   FROM a, b;
```

### 4. 度量

```sql
SELECT ST_Area(geom::geography), ST_Length(geom::geography),
       ST_Distance(a.geom::geography, b.geom::geography);
```

### 5. 输出格式

```sql
SELECT ST_AsText(geom), ST_AsGeoJSON(geom), ST_AsBinary(geom) FROM poi;
```

---

## 数据导入导出

```bash
# Shapefile → PostGIS
shp2pgsql -s 4326 -I -W UTF-8 china.shp public.china | psql -d gisdb

# 反向
pgsql2shp -f out.shp -h localhost -u postgres gisdb "SELECT * FROM poi"

# 通用（GDAL）
ogr2ogr -f PostgreSQL "PG:host=localhost user=postgres dbname=gisdb password=pg" \
        -nln poi -nlt PROMOTE_TO_MULTI -lco GEOMETRY_NAME=geom \
        -t_srs EPSG:4326 input.gpkg
```

---

## 矢量瓦片（ST_AsMVT）

```sql
WITH mvtgeom AS (
    SELECT ST_AsMVTGeom(
             ST_Transform(geom, 3857),
             ST_TileEnvelope(:z, :x, :y)) AS geom,
           id, name
    FROM poi
    WHERE geom && ST_Transform(ST_TileEnvelope(:z, :x, :y), 4326)
)
SELECT ST_AsMVT(mvtgeom.*, 'poi', 4096, 'geom') FROM mvtgeom;
```

---

## 栅格

```sql
-- 导入（命令行）
raster2pgsql -s 4326 -I -C -M dem.tif -F -t 256x256 public.dem | psql -d gisdb

SELECT ST_Value(rast, ST_MakePoint(116.4, 39.9)) FROM dem;
SELECT (ST_SummaryStats(rast)).* FROM dem;
SELECT ST_Clip(rast, geom, true) FROM dem, region WHERE region.id=1;
```

---

## 性能优化

1. **必建空间索引**：`USING GIST(geom)`
2. 用 `&&` 让查询走索引，再用 `ST_Within/Intersects` 精筛
3. 大批量导入后 `VACUUM ANALYZE`
4. SRID 必须一致，跨 SRID 必须 `ST_Transform`
5. 距离排序用 KNN `<->` 替代 `ST_Distance`
6. 几何简化：前端展示用 `ST_SimplifyPreserveTopology`
7. 大表按行政区分区
8. `ST_Subdivide` 切分大几何加速空间连接

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 查询慢 | 建索引 + `ANALYZE` + 检查 `EXPLAIN` |
| `Operation on mixed SRID` | 统一 SRID：`ST_SetSRID/ST_Transform` |
| 距离单位不对 | 投影下是度，需转 `geography` 或投到米制 |
| 跨经线 180° 异常 | 改用 `geography` |
| 多边形无效 | `ST_MakeValid` 修复，`ST_IsValidReason` 诊断 |

---

## AI 使用建议

### 推荐工作流

1. **安装扩展**：`CREATE EXTENSION postgis;` 启用空间功能
2. **建表**：包含 `geometry(Point, 4326)` 或 `geography(Point, 4326)` 类型的几何列
3. **建索引**：`CREATE INDEX ON table USING GIST(geom)` —— 必建空间索引
4. **导入数据**：使用 `shp2pgsql`（Shapefile）、`ogr2ogr`（通用）、`raster2pgsql`（栅格）
5. **空间查询**：用 `&&` 先做包围盒粗筛（走 GiST 索引），再用 `ST_Within`/`ST_Intersects` 精筛
6. **验证结果**：`EXPLAIN ANALYZE` 查看查询计划，确认索引被使用

### 关键注意事项

- **geometry vs geography**：`geometry`（平面计算，速度快）vs `geography`（球面计算，距离单位为米）
- **SRID 必须一致**：跨 SRID 运算必须先 `ST_Transform`，否则报 `Operation on mixed SRID`
- **用 `&&` 让查询走索引**：`WHERE geom && ST_MakeEnvelope(...)` 粗筛 + `ST_Within` 精筛
- **KNN 用 `<->`**：`ORDER BY geom <-> point LIMIT 10` 走 GiST 索引，比 `ST_Distance` 快几个数量级
- **大几何优化**：使用 `ST_Subdivide` 切分大面几何加速空间连接
- **导入后 ANALYZE**：大批量数据导入后执行 `VACUUM ANALYZE` 更新统计信息

## 相关技能

- **geoserver** — 地图服务发布（PostGIS 是最常见数据源）：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **geotools** — Java GIS 工具库：[../geotools/SKILL.md](../geotools/SKILL.md)
- **geopandas** — Python 矢量数据处理：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **gdal** — 命令行数据导入导出：[../gdal/SKILL.md](../gdal/SKILL.md)

## 参考资源

- 文档：<https://postgis.net/docs/>
- 函数速查：<https://postgis.net/docs/reference.html>
- Workshop：<https://postgis.net/workshops/postgis-intro/>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/postgis/>
