---
name: gdal
description: "Use when processing geospatial raster/vector data via command line — format conversion (Shapefile to GeoJSON), reprojection, DEM analysis, NDVI calculation, mosaicking. GDAL/OGR CLI: the industry standard for batch geospatial data processing with 50+ command-line tools (ogr2ogr, gdalwarp, gdal_translate, gdal_calc)."

tags:
  - gdal
  - ogr
  - cli
  - raster
  - vector
  - conversion
  - reprojection
  - gis
  - geospatial
---

> **项目地址：** <https://github.com/OSGeo/gdal>
>
> **官方文档：** <https://gdal.org/en/latest/>
>
> **源码命令文档：** <https://gdal.org/en/latest/programs/>
>
> **许可证：** MIT

## 概述

GDAL 是地理空间数据处理的事实标准库。它提供了 **50+ 个命令行工具**，分为两大类：

- **OGR 工具**（开放地理数据模型）：处理矢量数据（点、线、面）
- **GDAL 工具**：处理栅格数据（卫星影像、DEM、栅格地图）

---

## 环境准备

### 前置条件

GDAL 3.0+ 已预装在大多数 Linux 发行版的地理信息处理环境中。确保工具在 `PATH` 中：

```bash
gdalinfo --version   # 验证 GDAL 版本
ogrinfo --version    # 验证 OGR 版本
```

### 安装方法

#### Linux (Debian/Ubuntu)

```bash
apt-get update
apt-get install gdal-bin python3-gdal
```

#### Linux (CentOS/RHEL)

```bash
yum install gdal gdal-devel
```

#### macOS (Homebrew)

```bash
brew install gdal
```

#### Conda

```bash
conda install -c conda-forge gdal
```

#### Docker

```bash
docker run -it osgeo/gdal:latest bash
```

### Python 绑定（可选）

某些 GDAL 工具（如 `gdal_calc`, `gdal_merge`, `gdal_grid`, `gdal_polygonize`）是 Python 脚本，需要安装 Python 绑定：

```bash
pip install GDAL
# 或
conda install -c conda-forge gdal
```

---

## 核心命令结构

### 新式 CLI (GDAL 3.9+)

GDAL 3.9 引入了统一的 CLI 接口（[查看最新稳定版](https://gdal.org/download.html)），并在后续版本持续完善，新增 `gdal vector concave-hull/convex-hull/dissolve/sort`、`gdal dataset check` 等子命令：

```bash
gdal <command> <subcommand> [options] <inputs>
```

主要命令：
- `gdal info` — 获取数据信息（自动检测栅格或矢量）
- `gdal vector` — 矢量操作入口
- `gdal raster` — 栅格操作入口
- `gdal dataset` — 数据集管理

### 传统 CLI（广泛使用）

```bash
ogrinfo <datasource> [layer]
ogr2ogr <output> <input> [options]
gdalinfo <raster_file>
gdal_translate <input> <output> [options]
gdalwarp <input> <output> [options]
```

---

## 矢量数据工具（OGR）

> 完整参数表和高级示例见 [reference/vector-tools.md](reference/vector-tools.md)

### ogrinfo — 矢量数据信息查询

```bash
# 列出所有图层
ogrinfo mydata.shp

# 获取特定图层摘要
ogrinfo mydata.shp layername -so

# JSON 格式输出（GDAL 3.7+）
ogrinfo -json mydata.shp

# 显示所有要素及其属性
ogrinfo -al -geom=YES mydata.shp

# 按属性过滤
ogrinfo mydata.shp -where "AREA > 1000"
```

### ogr2ogr — 矢量数据格式转换和处理

```bash
# 格式转换（Shapefile → GeoJSON）
ogr2ogr output.geojson input.shp

# 指定输出格式（Shapefile → GeoPackage）
ogr2ogr -f GPKG output.gpkg input.shp

# 重投影（WGS84 → Web Mercator）
ogr2ogr -t_srs EPSG:3857 output.shp input.shp

# 属性过滤
ogr2ogr output.shp input.shp -where "area > 1000"

# 选择特定字段
ogr2ogr output.shp input.shp -select "id,name,geometry"
```

---

## 栅格数据工具（GDAL）

> 完整参数表和高级用法见 [reference/raster-tools.md](reference/raster-tools.md)

### gdalinfo — 栅格数据信息查询

```bash
# 基本信息
gdalinfo dem.tif

# JSON 输出
gdalinfo -json dem.tif

# 显示统计信息
gdalinfo -stats dem.tif
```

### gdal_translate — 栅格格式转换和重采样

```bash
# 格式转换（GeoTIFF → PNG）
gdal_translate input.tif output.png

# 格式转换（带压缩）
gdal_translate -co COMPRESS=DEFLATE input.tif output.tif

# 重采样（降低分辨率）
gdal_translate -outsize 50% 50% input.tif output.tif

# 裁剪到范围
gdal_translate -projwin -180 90 -170 80 input.tif output.tif
```

### gdalwarp — 栅格重投影和镶嵌

```bash
# 重投影（UTM 50N → WGS84）
gdalwarp -t_srs EPSG:4326 input_utm.tif output_wgs84.tif

# 镶嵌多个文件
gdalwarp input1.tif input2.tif input3.tif output_mosaic.tif

# 重采样并重投影
gdalwarp -tr 30 30 -t_srs EPSG:4326 input.tif output.tif

# 用矢量边界裁剪
gdalwarp -cutline clip_boundary.shp -crop_to_cutline input.tif output.tif
```

### gdal_merge.py — 栅格镶嵌融合

```bash
# 基本合并
gdal_merge.py -o output.tif input1.tif input2.tif input3.tif

# 分离波段（创建多波段文件）
gdal_merge.py -separate -o rgb.tif r.tif g.tif b.tif
```

### gdal_calc.py — 栅格计算器

```bash
# 两个栅格平均
gdal_calc.py -A input1.tif -B input2.tif --calc="(A+B)/2" --outfile=mean.tif

# 计算 NDVI（植被指数）
gdal_calc.py -A nir.tif -B red.tif \
  --calc="(A-B)/(A+B)" --outfile=ndvi.tif
```

### gdal_contour — 等值线提取

```bash
# 提取等高线（10 米间隔）
gdal_contour -a elevation dem.tif contours.shp -i 10

# 输出为 GeoJSON
gdal_contour -f GeoJSON dem.tif contours.geojson -i 50
```

### gdal_grid — 从散点数据创建网格

```bash
# 基本网格化（使用平均值）
gdal_grid -a average input_points.shp output_dem.tif

# 反距离加权（IDW）插值
gdal_grid -a invdist:power=2:smoothing=0 input_points.shp output_dem.tif
```

### gdal_polygonize.py — 栅格转矢量

```bash
# 基本转换
gdal_polygonize.py input.tif output.shp

# 指定输出格式
gdal_polygonize.py input.tif -f GeoJSON output.geojson
```

### gdaltindex — 创建栅格瓦片索引

```bash
# 基本索引
gdaltindex index.shp *.tif

# 输出为 GeoPackage
gdaltindex -of GPKG index.gpkg *.tif
```

### gdal_edit.py — 编辑栅格元数据

```bash
# 设置坐标参考系
gdal_edit.py -a_srs EPSG:4326 input.tif

# 设置 NoData 值
gdal_edit.py -a_nodata 0 input.tif
```

### nearblack — 清理黑白边界

```bash
# 清理黑色边界（默认）
nearblack input.tif -o output.tif

# 搜索白色边界
nearblack -white input.tif -o output.tif
```

---

## 常用环境变量和配置

### GDAL 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `GDAL_DATA` | GDAL 数据文件目录 | `/usr/share/gdal/` |
| `PROJ_LIB` | PROJ 数据文件目录 | `/usr/share/proj/` |
| `CPL_DEBUG` | 调试日志级别 | `ON` / `OFF` |
| `GDAL_CACHEMAX` | 块缓存大小（MB） | `512` |
| `GDAL_NUM_THREADS` | 线程数 | `4` / `ALL_CPUS` |
| `GDAL_DISABLE_READDIR_ON_OPEN` | 禁用目录读取 | `YES` |
| `GDAL_HTTP_TIMEOUT` | HTTP 超时（秒） | `30` |
| `GDAL_HTTP_MAX_RETRY` | HTTP 重试次数 | `3` |
| `GDAL_VSI_CURL_ALLOWED_EXTENSIONS` | 允许的远程文件扩展名 | `.tif,.tiff,.vrt` |
| `AWS_ACCESS_KEY_ID` | AWS 密钥 ID | 用于 S3 访问 |
| `AWS_SECRET_ACCESS_KEY` | AWS 密钥 | 用于 S3 访问 |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud 凭证文件 | `/path/to/credentials.json` |

### 使用环境变量

```bash
# 启用多线程处理
export GDAL_NUM_THREADS=ALL_CPUS

# 增加块缓存
export GDAL_CACHEMAX=1024

# 启用调试
export CPL_DEBUG=ON

# 访问 S3 上的栅格
export AWS_ACCESS_KEY_ID=xxxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
gdalinfo /vsis3/bucket/key.tif

# 运行命令
gdalwarp input.tif output.tif
```

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
| DXF | .dxf | CAD 格式 |
| MapInfo | .tab | MapInfo 格式 |

### 栅格格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| GeoTIFF | .tif, .tiff | 标准地理栅格（推荐） |
| PNG | .png | Web 图像 |
| JPEG | .jpg, .jpeg | 有损压缩 |
| COG | .tif | 云优化 GeoTIFF |
| NetCDF | .nc | 科学数据 |
| HDF5 | .h5, .he5 | 多维数据 |
| ASCII Grid | .asc | 简单栅格（DEM） |
| JPEG2000 | .jp2 | 高质量压缩 |
| ECW | .ecw | MrSID 格式 |

---

## 常见使用模式

### 模式 1: 批量格式转换

```bash
#!/bin/bash
# 将目录内所有 Shapefile 转换为 GeoJSON

for shp in *.shp; do
  base="${shp%.shp}"
  ogr2ogr -f GeoJSON "$base.geojson" "$shp"
done
```

### 模式 2: 批量重投影

```bash
#!/bin/bash
# 重投影所有 GeoTIFF 为 Web Mercator (EPSG:3857)

for tif in *.tif; do
  base="${tif%.tif}"
  gdalwarp -t_srs EPSG:3857 "$tif" "${base}_3857.tif"
done
```

### 模式 3: 创建 DEM 等值线

```bash
#!/bin/bash
# 从 DEM 提取等高线（10 米间隔）

gdal_contour -a elev dem.tif -i 10 contours.shp

# 转换为 GeoJSON
ogr2ogr -f GeoJSON contours.geojson contours.shp
```

### 模式 4: 计算 NDVI

```bash
#!/bin/bash
# 从多光谱影像计算 NDVI

gdal_calc.py \
  -A nir_band.tif \
  -B red_band.tif \
  --calc="(A-B)/(A+B)" \
  --outfile=ndvi.tif
```

### 模式 5: 镶嵌和重投影

```bash
#!/bin/bash
# 合并多个影像并重投影到 WGS84

gdalwarp -t_srs EPSG:4326 \
  image1.tif image2.tif image3.tif \
  output_mosaic_wgs84.tif
```

### 模式 6: 创建栅格瓦片索引

```bash
#!/bin/bash
# 为目录内所有 GeoTIFF 创建索引

gdaltindex -recursive -of GPKG \
  tile_index.gpkg /path/to/rasters/
```

---

## AI 使用建议

### 推荐工作流

1. **探索数据**：
   ```bash
   gdalinfo input.tif  # 栅格信息
   ogrinfo input.shp   # 矢量信息
   ```

2. **检查支持的格式和驱动**：
   ```bash
   gdalinfo --formats
   ogrinfo --formats
   ```

3. **分步处理**（避免大内存操作）：
   ```bash
   # 不要直接镶嵌所有文件
   # 改为逐个处理和合并
   ```

4. **使用 JSON 输出**（便于解析）：
   ```bash
   gdalinfo -json input.tif | jq '.coordinateSystem'
   ogrinfo -json input.shp | jq '.layers[0].featureCount'
   ```

5. **优化性能**：
   ```bash
   # 启用多线程、内存缓存、COG 格式
   export GDAL_NUM_THREADS=ALL_CPUS
   export GDAL_CACHEMAX=2048
   ```

### 关键注意事项

- **始终备份**：GDAL 可以就地修改文件（如 `gdal_edit.py`）
- **使用绝对路径**：避免工作目录问题
- **验证坐标系**：重投影前确认源和目标坐标系
- **测试小数据**：在大数据集上运行前，用小样本测试
- **使用 VRT（虚拟数据集）**：避免创建多个副本
- **环境变量**：设置适当的 `GDAL_CACHEMAX` 和 `GDAL_NUM_THREADS`

---

## 相关技能

- **gdal-api** — GDAL 编程 API（C/C++/Python/.NET）：[../gdal-api/SKILL.md](../gdal-api/SKILL.md)
- **qgis-process** — QGIS 命令行批处理：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **pyqgis** — QGIS Python 二次开发：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **postgis** — PostgreSQL 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)
- **opengis-all** — 一站式 GIS 全流程：[../opengis-all/SKILL.md](../opengis-all/SKILL.md)

## 相关资源

- **官方文档与资源：** <https://gdal.org/> | [命令行工具](https://gdal.org/en/latest/programs/) | [API](https://gdal.org/api/) | [GitHub](https://github.com/OSGeo/gdal)
- **矢量工具详细参考：** [reference/vector-tools.md](reference/vector-tools.md)
- **栅格工具详细参考：** [reference/raster-tools.md](reference/raster-tools.md)
