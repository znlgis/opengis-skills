# OpenGIS Workflow Examples and Cheatsheets

End-to-end workflow examples, built-in algorithm cheatsheet, GDAL CLI cheatsheet, data formats and env vars split from SKILL.md.

---

## 端到端工作流示例

### 示例 1：从 Shapefile 到地图服务（全自动）

完整流程：数据检查 → 重投影 → 缓冲区分析 → 发布到 GeoServer

```bash
#!/bin/bash
# === 阶段一：数据检查 ===
echo "=== 检查输入数据 ==="
ogrinfo -json buildings.shp | jq '.layers[0].featureCount'

# === 阶段二：数据处理 ===
echo "=== 重投影到 EPSG:4326 ==="
ogr2ogr -t_srs EPSG:4326 -f GPKG buildings_4326.gpkg buildings.shp

# === 阶段三：空间分析 ===
echo "=== 缓冲区分析（50米） ==="
qgis_process run native:buffer --json -- \
  INPUT=buildings_4326.gpkg DISTANCE=50 SEGMENTS=16 OUTPUT=buildings_buffer.gpkg

echo "=== 融合 ==="
qgis_process run native:dissolve --json -- \
  INPUT=buildings_buffer.gpkg OUTPUT=buildings_dissolved.gpkg

# === 阶段四：发布到 GeoServer ===
GEOSERVER="http://localhost:8080/geoserver"
AUTH="admin:geoserver"

echo "=== 创建工作空间 ==="
curl -u $AUTH -XPOST \
  -H "Content-Type: application/json" \
  -d '{"workspace":{"name":"analysis"}}' \
  "$GEOSERVER/rest/workspaces"

echo "=== 上传并发布图层 ==="
# 将 GeoPackage 转换为 Shapefile ZIP 以便上传
ogr2ogr buildings_result.shp buildings_dissolved.gpkg
zip buildings_result.zip buildings_result.*

curl -u $AUTH -XPUT \
  -H "Content-Type: application/zip" \
  --data-binary @buildings_result.zip \
  "$GEOSERVER/rest/workspaces/analysis/datastores/buildings/file.shp"

echo "=== 完成！==="
echo "WMS 地址: $GEOSERVER/wms?service=WMS&version=1.1.1&request=GetMap&layers=analysis:buildings_result&bbox=..."
```

### 示例 2：DEM 处理到坡度图服务（Python 全流程）

```python
"""从 DEM 生成坡度分析并发布到 GeoServer"""
import subprocess
import requests
from requests.auth import HTTPBasicAuth

GEOSERVER = "http://localhost:8080/geoserver"
AUTH = HTTPBasicAuth("admin", "geoserver")

# === 阶段一：数据检查 ===
subprocess.run(["gdalinfo", "dem.tif"], check=True)

# === 阶段二：数据处理 — 裁剪并重投影 ===
subprocess.run([
    "gdalwarp", "-t_srs", "EPSG:4326",
    "-cutline", "boundary.shp", "-crop_to_cutline",
    "dem.tif", "dem_clipped.tif"
], check=True)

# === 阶段三：空间分析 — 坡度分析 ===
subprocess.run([
    "qgis_process", "run", "gdal:slope", "--",
    "INPUT=dem_clipped.tif", "OUTPUT=slope.tif"
], check=True)

# === 阶段四：发布到 GeoServer ===
# 创建工作空间
requests.post(
    f"{GEOSERVER}/rest/workspaces",
    json={"workspace": {"name": "terrain"}},
    auth=AUTH
)

# 上传坡度栅格
with open("slope.tif", "rb") as f:
    requests.put(
        f"{GEOSERVER}/rest/workspaces/terrain/coveragestores/slope/file.geotiff",
        data=f,
        headers={"Content-Type": "image/tiff"},
        auth=AUTH
    )

print("坡度图层已发布！")
print(f"WMS: {GEOSERVER}/wms?service=WMS&version=1.1.1&request=GetMap&layers=terrain:slope")
```

### 示例 3：PyQGIS 完整分析流程

```python
"""PyQGIS 独立脚本：加载数据 → 分析 → 导出 → 发布"""
import sys
import requests
from requests.auth import HTTPBasicAuth
from qgis.core import QgsApplication, QgsVectorLayer, QgsProject
import processing
from processing.core.Processing import Processing

# 初始化 QGIS
qgs = QgsApplication([], False)
qgs.setPrefixPath("/usr", True)
qgs.initQgis()
Processing.initialize()

# === 阶段一：加载数据 ===
layer = QgsVectorLayer("/data/buildings.shp", "buildings", "ogr")
assert layer.isValid(), "图层加载失败"
print(f"加载完成: {layer.featureCount()} 个要素")

# === 阶段二：重投影 ===
result1 = processing.run("native:reprojectlayer", {
    'INPUT': layer,
    'TARGET_CRS': 'EPSG:4326',
    'OUTPUT': 'memory:reprojected'
})

# === 阶段三：缓冲区 + 融合 ===
result2 = processing.run("native:buffer", {
    'INPUT': result1['OUTPUT'],
    'DISTANCE': 100,
    'SEGMENTS': 16,
    'OUTPUT': 'memory:buffered'
})

result3 = processing.run("native:dissolve", {
    'INPUT': result2['OUTPUT'],
    'OUTPUT': '/data/buildings_analysis.gpkg'
})
print(f"分析完成: {result3['OUTPUT']}")

# === 阶段四：发布到 GeoServer ===
GEOSERVER = "http://localhost:8080/geoserver"
AUTH = HTTPBasicAuth("admin", "geoserver")

# 转换为 Shapefile ZIP 以上传
processing.run("native:reprojectlayer", {
    'INPUT': result3['OUTPUT'],
    'TARGET_CRS': 'EPSG:4326',
    'OUTPUT': '/data/for_upload.shp'
})

import zipfile, glob
with zipfile.ZipFile("/data/for_upload.zip", "w") as zf:
    for f in glob.glob("/data/for_upload.*"):
        zf.write(f, f.split("/")[-1])

requests.post(f"{GEOSERVER}/rest/workspaces",
              json={"workspace": {"name": "analysis"}}, auth=AUTH)

with open("/data/for_upload.zip", "rb") as f:
    requests.put(
        f"{GEOSERVER}/rest/workspaces/analysis/datastores/buildings/file.shp",
        data=f, headers={"Content-Type": "application/zip"}, auth=AUTH
    )

print("图层已发布到 GeoServer！")

qgs.exitQgis()
```

### 示例 4：使用 qgis_process JSON 模式的自动化流水线

```bash
#!/bin/bash
# 适用于 CI/CD 自动化流水线
export QT_QPA_PLATFORM=offscreen

# 步骤 1：缓冲区分析（JSON 输入）
echo '{
  "inputs": {
    "INPUT": "/data/roads.shp",
    "DISTANCE": 50,
    "SEGMENTS": 10,
    "OUTPUT": "/data/roads_buffer.gpkg"
  }
}' | qgis_process run native:buffer -

# 步骤 2：解析输出路径
BUFFER_OUTPUT=$(echo '{
  "inputs": {
    "INPUT": "/data/roads.shp",
    "DISTANCE": 50,
    "SEGMENTS": 10,
    "OUTPUT": "/data/roads_buffer.gpkg"
  }
}' | qgis_process run native:buffer - | jq -r '.results.OUTPUT')

# 步骤 3：融合
qgis_process run native:dissolve --json -- \
  INPUT="$BUFFER_OUTPUT" OUTPUT=/data/roads_dissolved.gpkg

# 步骤 4：发布到 GeoServer
ogr2ogr roads_final.shp /data/roads_dissolved.gpkg
zip roads_final.zip roads_final.*

curl -u admin:geoserver -XPUT \
  -H "Content-Type: application/zip" \
  --data-binary @roads_final.zip \
  "http://localhost:8080/geoserver/rest/workspaces/myws/datastores/roads/file.shp"
```

---

## 常用内置算法速查（qgis_process / PyQGIS）

### 矢量分析

| 算法 ID | 说明 | 关键参数 |
|---------|------|---------|
| `native:buffer` | 缓冲区分析 | INPUT, DISTANCE, SEGMENTS, DISSOLVE |
| `native:clip` | 矢量裁剪 | INPUT, OVERLAY |
| `native:dissolve` | 融合 | INPUT, FIELD |
| `native:intersection` | 交集 | INPUT, OVERLAY |
| `native:union` | 联合 | INPUT, OVERLAY |
| `native:difference` | 差集 | INPUT, OVERLAY |
| `native:symmetricaldifference` | 对称差 | INPUT, OVERLAY |
| `native:centroids` | 质心 | INPUT |
| `native:convexhull` | 凸包 | INPUT |
| `native:simplifygeometries` | 简化几何 | INPUT, TOLERANCE |
| `native:reprojectlayer` | 重投影 | INPUT, TARGET_CRS |
| `native:mergevectorlayers` | 合并图层 | LAYERS |
| `native:splitvectorlayer` | 拆分图层 | INPUT, FIELD |
| `native:extractbyattribute` | 按属性提取 | INPUT, FIELD, OPERATOR, VALUE |
| `native:extractbylocation` | 按位置提取 | INPUT, INTERSECT, PREDICATE |
| `native:joinattributesbylocation` | 按位置连接属性 | INPUT, JOIN, PREDICATE |
| `native:fixgeometries` | 修复几何 | INPUT |
| `native:countpointsinpolygon` | 多边形内点计数 | POLYGONS, POINTS |
| `native:voronoipolygons` | 泰森多边形 | INPUT |
| `native:creategrid` | 创建网格 | TYPE, EXTENT, HSPACING, VSPACING |
| `native:fieldcalculator` | 字段计算器 | INPUT, FIELD_NAME, FORMULA |

### 栅格分析

| 算法 ID | 说明 | 关键参数 |
|---------|------|---------|
| `native:rasterlayerstatistics` | 栅格统计 | INPUT |
| `gdal:cliprasterbyextent` | 按范围裁剪栅格 | INPUT, EXTENT |
| `gdal:cliprasterbymask` | 按掩膜裁剪栅格 | INPUT, MASK |
| `gdal:merge` | 栅格合并 | INPUT |
| `gdal:warpreproject` | 栅格重投影 | INPUT, TARGET_CRS |
| `gdal:contour` | 等值线提取 | INPUT, INTERVAL |
| `gdal:polygonize` | 栅格转矢量 | INPUT |
| `gdal:rasterize` | 矢量转栅格 | INPUT, FIELD |
| `gdal:hillshade` | 山体阴影 | INPUT |
| `gdal:slope` | 坡度分析 | INPUT |
| `gdal:aspect` | 坡向分析 | INPUT |
| `gdal:roughness` | 粗糙度 | INPUT |
| `gdal:buildvirtualraster` | 构建虚拟栅格 | INPUT |

---

## GDAL 命令行工具速查

### 矢量工具

| 命令 | 说明 |
|------|------|
| `ogrinfo` | 矢量数据信息查询 |
| `ogr2ogr` | 矢量格式转换和处理 |

### 栅格工具

| 命令 | 说明 |
|------|------|
| `gdalinfo` | 栅格数据信息查询 |
| `gdal_translate` | 栅格格式转换和重采样 |
| `gdalwarp` | 栅格重投影和镶嵌 |
| `gdal_merge.py` | 栅格镶嵌融合 |
| `gdal_calc.py` | 栅格计算器（NumPy 语法） |
| `gdal_contour` | 等值线提取 |
| `gdal_grid` | 散点数据插值创建网格 |
| `gdal_polygonize.py` | 栅格转矢量 |
| `gdaltindex` | 创建栅格瓦片索引 |
| `gdal_edit.py` | 编辑栅格元数据 |
| `nearblack` | 清理黑白边界 |

---

## 数据格式支持

### 矢量格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| Shapefile | .shp | ESRI 标准格式 |
| GeoJSON | .geojson | Web 标准 JSON |
| GeoPackage | .gpkg | SQLite 基础，推荐 |
| KML | .kml | Google Maps 格式 |
| PostGIS | N/A | 数据库矢量存储 |
| GML | .gml | ISO 标准 XML |
| CSV | .csv | 点数据 |
| FlatGeobuf | .fgb | 高性能流式二进制格式 |

### 栅格格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| GeoTIFF | .tif | 标准地理栅格（推荐） |
| COG | .tif | 云优化 GeoTIFF |
| PNG | .png | Web 图像 |
| JPEG | .jpg | 有损压缩 |
| NetCDF | .nc | 科学数据 |
| HDF5 | .h5 | 多维数据 |
| JPEG2000 | .jp2 | 高质量压缩 |
| ASCII Grid | .asc | 简单栅格 |

---

