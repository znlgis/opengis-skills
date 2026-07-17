# GDAL Vector Tools Reference

Detailed parameter reference and examples for OGR vector tools (`ogrinfo`, `ogr2ogr`).

---

## ogrinfo — Vector Data Query

**描述**: 列出和查询 OGR 支持的矢量数据源（Shapefile、GeoJSON、GeoPackage、PostGIS 等）。

**基本用法**：

```bash
# 列出所有图层
ogrinfo mydata.shp

# 获取特定图层信息
ogrinfo mydata.shp layername -so

# JSON 格式输出（GDAL 3.7+）
ogrinfo -json mydata.shp

# 显示所有要素及其属性
ogrinfo -al -geom=YES mydata.shp

# 限制显示的要素数量
ogrinfo -al -limit 10 mydata.shp

# 按属性过滤
ogrinfo mydata.shp -where "AREA > 1000"

# SQL 查询
ogrinfo mydata.shp -sql "SELECT * FROM mydata WHERE population > 10000"

# 空间范围过滤
ogrinfo mydata.shp -spat -10 40 10 50
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-json` | JSON 格式输出（GDAL 3.7+） |
| `-al` | 列出所有图层及其要素 |
| `-so` | 仅摘要（不显示单个要素） |
| `-ro` | 只读模式 |
| `-where <expr>` | SQL WHERE 表达式过滤 |
| `-sql <statement>` | 执行 SQL 语句 |
| `-spat <xmin> <ymin> <xmax> <ymax>` | 空间范围过滤 |
| `-limit <n>` | 限制要素数量 |
| `-geom=YES\|NO\|SUMMARY\|WKT` | 几何输出格式 |
| `-fields=YES\|NO` | 是否输出字段值 |

**示例**：

```bash
# 查看 GeoPackage 所有图层及要素数
ogrinfo -al -so buildings.gpkg

# 获取 PostGIS 表的 JSON 信息
ogrinfo -json "PG:dbname=mydb user=postgres" public.buildings

# 查询人口超过 100 万的城市
ogrinfo cities.shp -where "population > 1000000" -fields=YES

# 导出为 GeoJSON 字符串（用于脚本）
ogrinfo -json cities.shp | jq '.layers[0].features[0]'
```

---

## ogr2ogr — Vector Format Conversion and Processing

**描述**: GDAL 最强大的矢量工具。可在各种格式间转换、重投影、过滤、合并矢量数据。

**基本用法**：

```bash
# 格式转换（Shapefile → GeoJSON）
ogr2ogr output.geojson input.shp

# 格式转换（Shapefile → GeoPackage）
ogr2ogr -f GPKG output.gpkg input.shp

# 重投影（WGS84 → Web Mercator）
ogr2ogr -t_srs EPSG:3857 output.shp input.shp

# 属性过滤
ogr2ogr output.shp input.shp -where "area > 1000"

# 选择特定字段
ogr2ogr output.shp input.shp -select "id,name,geometry"

# 创建空间索引
ogr2ogr output.gpkg input.shp -of GPKG

# 合并多个文件
ogr2ogr -append output.shp input1.shp
ogr2ogr -append output.shp input2.shp

# 裁剪到矩形范围
ogr2ogr output.shp input.shp -spat -10 40 10 50

# 裁剪到多边形
ogr2ogr -clipsrc clip_polygon.shp output.shp input.shp

# SQL 转换（图层名通常为文件名去除扩展名）
ogr2ogr -f GeoJSON output.geojson input.shp -sql "SELECT ST_Buffer(geometry, 100) as geom, name FROM input"

# 添加字段
ogr2ogr output.shp input.shp -sql "SELECT *, 'value' as new_field FROM input"
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-f <format>` | 输出格式（GeoJSON, GPKG, KML, CSV 等） |
| `-t_srs <EPSG>` | 目标坐标参考系 |
| `-s_srs <EPSG>` | 源坐标参考系 |
| `-where <expr>` | WHERE 表达式过滤 |
| `-select <cols>` | 选择特定字段 |
| `-append` | 追加到现有数据集 |
| `-overwrite` | 覆盖现有输出文件 |
| `-spat <xmin> <ymin> <xmax> <ymax>` | 矩形范围裁剪 |
| `-clipsrc <file>` | 用多边形裁剪 |
| `-sql <statement>` | SQL 查询 |
| `-nln <name>` | 输出图层名 |

**高级示例**：

```bash
# 合并多个 Shapefile（同时重投影）
for file in *.shp; do
  ogr2ogr -append -t_srs EPSG:4326 merged.shp "$file"
done

# 分割大文件（按行政区划）
ogr2ogr filtered.shp input.shp -where "county='New York'"

# 添加自增 ID 字段
ogr2ogr output.shp input.shp -sql "SELECT *, FID as id FROM input"

# 转换到 CSV（用于分析）
ogr2ogr -f CSV output.csv input.shp -lco GEOMETRY=AS_WKT

# PostGIS 导入
ogr2ogr -f PostgreSQL "PG:dbname=mydb user=postgres" input.shp -nln mytable
```
