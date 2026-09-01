# QGIS Process Algorithm Cheatsheet Reference

Built-in algorithm cheatsheet, parameter types and typical workflow examples split from SKILL.md.

---

## 常用内置算法速查

以下列出常用的内置算法分类及代表性 ID：

### 矢量通用（native）

| 算法 ID | 说明 |
|---------|------|
| `native:buffer` | 缓冲区分析 |
| `native:clip` | 裁剪 |
| `native:dissolve` | 融合 |
| `native:intersection` | 交集 |
| `native:union` | 联合 |
| `native:difference` | 差集 |
| `native:symmetricaldifference` | 对称差 |
| `native:centroids` | 质心 |
| `native:convexhull` | 凸包 |
| `native:simplifygeometries` | 简化几何 |
| `native:reprojectlayer` | 重投影 |
| `native:mergevectorlayers` | 合并矢量图层 |
| `native:splitvectorlayer` | 拆分矢量图层 |
| `native:extractbyattribute` | 按属性提取 |
| `native:extractbylocation` | 按位置提取 |
| `native:joinattributesbylocation` | 按位置连接属性 |
| `native:fixgeometries` | 修复几何 |
| `native:countpointsinpolygon` | 多边形内点计数 |
| `native:voronoipolygons` | 泰森多边形 |
| `native:delaunaytriangulation` | Delaunay 三角剖分 |
| `native:creategrid` | 创建网格 |
| `native:randomextract` | 随机抽样 |
| `native:addautoincrementalfield` | 添加自增字段 |
| `native:fieldcalculator` | 字段计算器 |

### 栅格分析（native / gdal）

| 算法 ID | 说明 |
|---------|------|
| `native:rasterlayerstatistics` | 栅格统计 |
| `native:rastersurfacevolume` | 栅格曲面体积 |
| `gdal:cliprasterbyextent` | 按范围裁剪栅格 |
| `gdal:cliprasterbymask` | 按掩膜裁剪栅格 |
| `gdal:merge` | 栅格合并 |
| `gdal:warpreproject` | 栅格重投影 |
| `gdal:contour` | 等值线提取 |
| `gdal:polygonize` | 栅格转矢量 |
| `gdal:rasterize` | 矢量转栅格 |
| `gdal:hillshade` | 山体阴影 |
| `gdal:slope` | 坡度分析 |
| `gdal:aspect` | 坡向分析 |
| `gdal:roughness` | 粗糙度 |
| `gdal:buildvirtualraster` | 构建虚拟栅格（VRT） |

### 坐标参考系

| 算法 ID | 说明 |
|---------|------|
| `native:reprojectlayer` | 矢量重投影 |
| `gdal:warpreproject` | 栅格重投影 |
| `native:assignprojection` | 指定投影（不变换坐标） |

### 点云（pdal）

| 算法 ID | 说明 |
|---------|------|
| `pdal:info` | 点云信息 |
| `pdal:clip` | 点云裁剪 |
| `pdal:merge` | 点云合并 |
| `pdal:thin` | 点云抽稀 |
| `pdal:tile` | 点云瓦片化 |
| `pdal:boundary` | 点云边界 |
| `pdal:density` | 点云密度 |
| `pdal:exportraster` | 点云转栅格 |
| `pdal:exportvector` | 点云转矢量 |

---

## 参数类型参考

`qgis_process` 支持的常见参数类型及命令行传值方式：

| 参数类型 | 说明 | 命令行值示例 |
|----------|------|-------------|
| `source` / `vector` | 矢量数据源 | 文件路径 `input.shp`、`input.geojson` |
| `raster` | 栅格图层 | 文件路径 `dem.tif` |
| `sink` | 矢量输出目标 | 文件路径 `output.shp`、`output.gpkg` |
| `rasterDestination` | 栅格输出目标 | 文件路径 `output.tif` |
| `number` / `distance` / `area` | 数值 | `10`、`2.5` |
| `string` | 字符串 | `"my_value"` |
| `boolean` | 布尔值 | `true` / `false` |
| `enum` | 枚举 | 数字索引 `0`、`1`、`2` |
| `crs` | 坐标参考系 | `EPSG:4326`、`EPSG:3857` |
| `extent` | 空间范围 | `xmin,xmax,ymin,ymax [EPSG:code]` |
| `point` | 点坐标 | `x,y [EPSG:code]` |
| `field` | 字段名 | 字段名字符串 |
| `expression` | QGIS 表达式 | `"field_name * 2"` |
| `multilayer` | 多图层 | 多次指定同一参数 |
| `file` | 文件路径 | `/path/to/file` |
| `folder` | 文件夹路径 | `/path/to/folder` |

---

## 典型工作流示例

### 示例 1：矢量数据格式转换（SHP → GeoJSON）

```bash
# 使用 ogr2ogr 风格的转换，利用 QGIS 重投影能力
qgis_process run native:reprojectlayer -- \
  INPUT=input.shp \
  TARGET_CRS=EPSG:4326 \
  OUTPUT=output.geojson
```

### 示例 2：批量缓冲区 + 融合

```bash
# 第一步：缓冲区分析
qgis_process run native:buffer -- \
  INPUT=points.shp \
  DISTANCE=1000 \
  SEGMENTS=16 \
  OUTPUT=/tmp/buffered.gpkg

# 第二步：融合
qgis_process run native:dissolve -- \
  INPUT=/tmp/buffered.gpkg \
  OUTPUT=dissolved.gpkg
```

### 示例 3：栅格裁剪 + 坡度分析

```bash
# 裁剪 DEM
qgis_process run gdal:cliprasterbymask -- \
  INPUT=dem.tif \
  MASK=boundary.shp \
  OUTPUT=/tmp/clipped_dem.tif

# 坡度分析
qgis_process run gdal:slope -- \
  INPUT=/tmp/clipped_dem.tif \
  OUTPUT=slope.tif
```

### 示例 4：使用 JSON 传参（适合 AI 自动化）

```bash
cat <<'EOF' | qgis_process run native:buffer -
{
  "ellipsoid": "EPSG:7030",
  "distance_units": "meters",
  "inputs": {
    "INPUT": "/data/roads.shp",
    "DISTANCE": 50,
    "SEGMENTS": 10,
    "END_CAP_STYLE": 0,
    "JOIN_STYLE": 0,
    "MITER_LIMIT": 2,
    "DISSOLVE": false,
    "OUTPUT": "/data/roads_buffer_50m.gpkg"
  }
}
EOF
```

### 示例 5：在脚本中解析 JSON 输出

```bash
# 运行算法并捕获 JSON 输出
RESULT=$(qgis_process run native:buffer --json -- \
  INPUT=source.shp DISTANCE=100 OUTPUT=buffered.shp)

# 使用 jq 提取输出文件路径
OUTPUT_PATH=$(echo "$RESULT" | jq -r '.results.OUTPUT')
echo "输出文件: $OUTPUT_PATH"
```

### 示例 6：需要 QGIS 项目文件的算法

```bash
qgis_process run native:printlayouttopdf \
  --project_path=/path/to/project.qgs -- \
  LAYOUT="My Layout" \
  OUTPUT=/output/map.pdf
```

---

