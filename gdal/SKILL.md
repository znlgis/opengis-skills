---
name: GDAL
description: GDAL (Geospatial Data Abstraction Library) 是 OSGeo 的开源地理数据处理库，提供了功能强大的命令行工具，用于处理和转换栅格数据（DEM、影像、栅格地图）和矢量数据（点、线、面、GIS 格式文件）。GDAL 工具集适用于批量数据处理、格式转换、地理信息系统分析等场景。
---

> **项目地址：** <https://github.com/OSGeo/gdal>
>
> **官方文档：** <https://gdal.org/en/latest/>
>
> **源码命令文档：** <https://gdal.org/en/latest/programs/>
>
> **许可证：** MIT License

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
pip install gdal
# 或
conda install -c conda-forge gdal
```

---

## 核心命令结构

### 新式 CLI (GDAL 3.11+)

GDAL 3.11 引入了统一的 CLI 接口：

```bash
gdal <command> <subcommand> [options] <inputs>
```

主要命令：
- `gdal info` - 获取数据信息（自动检测栅格或矢量）
- `gdal vector` - 矢量操作入口
- `gdal raster` - 栅格操作入口
- `gdal dataset` - 数据集管理

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

### 1. ogrinfo - 矢量数据信息查询

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

### 2. ogr2ogr - 矢量数据格式转换和转换

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

# SQL 转换
ogr2ogr -sql "SELECT ST_Buffer(geometry, 100) as geom, name FROM input" output.shp

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

---

## 栅格数据工具（GDAL）

### 3. gdalinfo - 栅格数据信息查询

**描述**: 显示栅格数据的元数据、地理信息、波段信息、统计值。

**基本用法**：

```bash
# 基本信息
gdalinfo dem.tif

# JSON 输出（GDAL 3.1+）
gdalinfo -json dem.tif

# 仅显示摘要（不显示统计值）
gdalinfo -checksum dem.tif

# 显示统计信息
gdalinfo -stats dem.tif

# 显示色表
gdalinfo -checksum terrain.tif | grep -A5 "Color Table"

# 计算直方图
gdalinfo -hist image.tif
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-json` | JSON 格式输出 |
| `-stats` | 计算并显示统计信息 |
| `-approx_stats` | 近似统计（快速） |
| `-checksum` | 显示校验和 |
| `-hist` | 显示直方图 |
| `-mm` | 显示最小/最大值 |
| `-noct` | 不显示色表 |

**示例**：

```bash
# 获取 DEM 范围和分辨率
gdalinfo dem.tif | grep -E "^Size|^Upper Left|Corner|Pixel Size"

# 获取 JSON 格式地理信息
gdalinfo -json image.tif | jq '.coordinateSystem'

# 检查数据类型和波段数
gdalinfo image.tif | grep "Type:\|Band"
```

---

### 4. gdal_translate - 栅格格式转换和重采样

**描述**: 将栅格文件转换为不同格式、调整分辨率、裁剪、创建缩放图等。

**基本用法**：

```bash
# 格式转换（GeoTIFF → PNG）
gdal_translate input.tif output.png

# 格式转换（带压缩）
gdal_translate -co COMPRESS=DEFLATE input.tif output.tif

# 重采样（降低分辨率）
gdal_translate -outsize 50% 50% input.tif output.tif

# 重采样到指定分辨率
gdal_translate -tr 10 10 input.tif output.tif

# 裁剪到范围
gdal_translate -projwin -180 90 -170 80 input.tif output.tif

# 创建缩放版本（1/4 大小）
gdal_translate -outsize 25% 25% input.tif thumbnail.tif

# 转换数据类型
gdal_translate -ot Byte input.tif output.tif

# 设置 NoData 值
gdal_translate -a_nodata 0 input.tif output.tif

# 只提取特定波段
gdal_translate -b 1 rgb.tif red.tif
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-of <format>` | 输出格式 |
| `-outsize <xsize> <ysize>` | 输出大小（像素或百分比） |
| `-tr <xres> <yres>` | 目标分辨率 |
| `-projwin <ulx> <uly> <lrx> <lry>` | 裁剪范围 |
| `-ot <datatype>` | 输出数据类型 |
| `-b <band>` | 选择波段 |
| `-a_nodata <value>` | 设置 NoData 值 |
| `-co <NAME>=<VALUE>` | 创建选项（如压缩） |

---

### 5. gdalwarp - 栅格重投影和镶嵌

**描述**: 重投影栅格、裁剪、融合多个栅格（镶嵌）、重新采样。

**基本用法**：

```bash
# 重投影（UTM 50N → WGS84）
gdalwarp -t_srs EPSG:4326 input_utm.tif output_wgs84.tif

# 镶嵌多个文件
gdalwarp input1.tif input2.tif input3.tif output_mosaic.tif

# 重采样并重投影
gdalwarp -tr 30 30 -t_srs EPSG:4326 input.tif output.tif

# 裁剪（指定范围）
gdalwarp -te -10 40 10 50 input.tif output.tif

# 用矢量边界裁剪
gdalwarp -cutline clip_boundary.shp -crop_to_cutline input.tif output.tif

# 最近邻重采样（用于分类数据）
gdalwarp -r near input.tif output.tif

# 双线性插值（用于连续数据）
gdalwarp -r bilinear input.tif output.tif

# 立方卷积插值（高质量）
gdalwarp -r cubic input.tif output.tif

# 多线程处理
gdalwarp -wm 512 -co COMPRESS=DEFLATE input.tif output.tif
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-t_srs <EPSG>` | 目标坐标参考系 |
| `-s_srs <EPSG>` | 源坐标参考系 |
| `-tr <xres> <yres>` | 目标分辨率 |
| `-te <xmin> <ymin> <xmax> <ymax>` | 目标范围 |
| `-cutline <file>` | 用矢量边界裁剪 |
| `-crop_to_cutline` | 自动裁剪到边界 |
| `-r {near\|bilinear\|cubic\|cubicspline\|lanczos}` | 重采样算法 |
| `-wm <megabytes>` | 工作内存大小 |
| `-co <NAME>=<VALUE>` | 创建选项 |
| `-multi` | 多线程处理 |

---

### 6. gdal_merge.py - 栅格镶嵌融合

**描述**: 合并多个栅格为单一文件。与 `gdalwarp` 类似，但更简单，不支持重投影。

**基本用法**：

```bash
# 基本合并
gdal_merge.py -o output.tif input1.tif input2.tif input3.tif

# 指定输出格式
gdal_merge.py -of JPEG -o output.jpg *.tif

# 设置像素大小
gdal_merge.py -ps 30 30 -o output.tif *.tif

# 分离波段（创建多波段文件）
gdal_merge.py -separate -o rgb.tif r.tif g.tif b.tif

# 设置 NoData 值
gdal_merge.py -n 0 -o output.tif *.tif

# 指定输出范围
gdal_merge.py -ul_lr -180 90 180 -90 -o output.tif *.tif

# 初始化像素值
gdal_merge.py -init 255 -o output.tif input1.tif input2.tif
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-o <filename>` | 输出文件名 |
| `-of <format>` | 输出格式 |
| `-ps <pixelsize_x> <pixelsize_y>` | 像素大小 |
| `-tap` | 目标对齐像素 |
| `-separate` | 分离波段到不同输出波段 |
| `-n <nodata>` | 输入 NoData 值 |
| `-a_nodata <value>` | 输出 NoData 值 |
| `-ul_lr <ulx> <uly> <lrx> <lry>` | 输出范围 |
| `-init <value>` | 初始化像素值 |

---

### 7. gdal_calc.py - 栅格计算器

**描述**: 使用 NumPy 语法进行栅格数学运算。支持逻辑和算术操作。

**基本用法**：

```bash
# 两个栅格平均
gdal_calc.py -A input1.tif -B input2.tif --calc="(A+B)/2" --outfile=mean.tif

# 计算 NDVI（植被指数）
gdal_calc.py -A nir.tif -B red.tif \
  --calc="(A-B)/(A+B)" --outfile=ndvi.tif

# 三个栅格相加
gdal_calc.py -A band1.tif -B band2.tif -C band3.tif \
  --calc="A+B+C" --outfile=sum.tif

# 逻辑操作（掩膜）
gdal_calc.py -A input.tif --calc="A*(A>100)" \
  --outfile=masked.tif --NoDataValue=0

# 范围选择
gdal_calc.py -A input.tif --calc="A*logical_and(A>50,A<150)" \
  --outfile=filtered.tif

# 多个表达式创建多波段输出
gdal_calc.py -A input.tif --A_band=1 -B input.tif --B_band=2 \
  --calc="(A+B)/2" --calc="B-A" --outfile=result.tif

# 处理 NoData 值
gdal_calc.py -A input.tif --hideNoData \
  --calc="A*2" --outfile=output.tif

# 转换数据类型
gdal_calc.py -A input.tif --type=Int16 \
  --calc="A.astype(numpy.int16)" --outfile=output.tif
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-A, -B, ..., -Z <filename>` | 输入栅格（字母标识） |
| `--A_band=<n>` | 指定输入波段号 |
| `--calc=<expression>` | 计算表达式（NumPy 语法） |
| `--outfile=<filename>` | 输出文件 |
| `--NoDataValue=<value>` | 输出 NoData 值 |
| `--type=<datatype>` | 输出数据类型 |
| `--format=<format>` | 输出格式 |
| `--hideNoData` | 忽略输入 NoData（参与计算） |
| `--extent=union\|intersect` | 处理不同范围的栅格 |

---

### 8. gdal_contour - 等值线提取

**描述**: 从 DEM 提取等高线，生成矢量线或多边形。

**基本用法**：

```bash
# 提取等高线（10 米间隔）
gdal_contour -a elevation dem.tif contours.shp -i 10

# 添加属性字段
gdal_contour -a elev dem.tif contours.shp -i 10

# 输出为 GeoJSON
gdal_contour -f GeoJSON dem.tif contours.geojson -i 50

# 生成多边形等值区域
gdal_contour -p -amin min -amax max dem.tif contour_polygons.shp -i 20

# 指定特定等高线值
gdal_contour -fl 100 200 300 dem.tif fixed_contours.shp

# 指数间隔（如 2^n）
gdal_contour -e 2 dem.tif exponential_contours.shp

# 从特定波段提取
gdal_contour -b 1 dem.tif contours.shp -i 10
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-a <name>` | 属性字段名（存储高度值） |
| `-amin <name>` | 多边形最小值字段 |
| `-amax <name>` | 多边形最大值字段 |
| `-i <interval>` | 等高线间隔 |
| `-fl <level>` | 固定高度值（可多个） |
| `-e <base>` | 指数基数（如 2）生成指数间隔 |
| `-off <offset>` | 间隔偏移量 |
| `-p` | 生成多边形而非线 |
| `-3d` | 输出 3D 矢量 |
| `-f <format>` | 输出格式 |
| `-b <band>` | 源波段号 |

---

### 9. gdal_grid - 从散点数据创建网格

**描述**: 从矢量点数据（如 LiDAR、采样点）创建规则网格 DEM，支持多种插值算法。

**基本用法**：

```bash
# 基本网格化（使用平均值）
gdal_grid -a average input_points.shp output_dem.tif

# 反距离加权（IDW）插值
gdal_grid -a invdist:power=2:smoothing=0 input_points.shp output_dem.tif

# 克里金插值
gdal_grid -a kriging:variogram=spherical input_points.shp output_dem.tif

# 指定输出范围和分辨率
gdal_grid -outsize 512 512 -tr 10 10 \
  -a average input_points.shp output_dem.tif

# 只使用 Z 属性字段
gdal_grid -zfield Z -a invdist input_points.shp output_dem.tif

# 设置 NoData 值
gdal_grid -a_nodata -9999 -a average input_points.shp output_dem.tif

# 指定空间范围
gdal_grid -te 0 0 1000 1000 -a average input_points.shp output_dem.tif
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-a <algorithm>` | 插值算法（average, invdist, kriging 等） |
| `-zfield <name>` | 用于 Z 值的属性字段 |
| `-outsize <xsize> <ysize>` | 输出栅格大小 |
| `-tr <xres> <yres>` | 输出分辨率 |
| `-te <xmin> <ymin> <xmax> <ymax>` | 输出范围 |
| `-ot <datatype>` | 输出数据类型 |
| `-a_srs <srs>` | 输出坐标参考系 |
| `-a_nodata <value>` | NoData 值 |

**支持的算法**：
- `average` - 平均值（最简单）
- `invdist` - 反距离加权（常用）
- `invdistnn` - 反距离加权（最近邻）
- `kriging` - 克里金插值（高级）
- `linear` - 线性内插（TIN）

---

### 10. gdal_polygonize.py - 栅格转矢量

**描述**: 将栅格转换为矢量多边形，每个像素值对应一个多边形。

**基本用法**：

```bash
# 基本转换
gdal_polygonize.py input.tif output.shp

# 指定输出格式
gdal_polygonize.py input.tif -f GeoJSON output.geojson

# 转换特定波段
gdal_polygonize.py -b 1 input.tif output.shp

# 使用 8 连通性（默认 4 连通）
gdal_polygonize.py -8 input.tif output.shp

# 使用掩膜过滤
gdal_polygonize.py -mask mask.tif input.tif output.shp

# 输出到数据库
gdal_polygonize.py input.tif -f PostgreSQL \
  "PG:dbname=mydb" -nln polygons

# 自定义字段名
gdal_polygonize.py input.tif output.shp output_layer value_field
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-b <band>` | 源波段号 |
| `-8` | 使用 8 连通性（默认 4） |
| `-mask <file>` | 掩膜文件 |
| `-nomask` | 不使用掩膜 |
| `-f <format>` | 输出格式 |
| `-nln <name>` | 输出图层名 |

---

### 11. gdaltindex - 创建栅格瓦片索引

**描述**: 为多个栅格文件创建索引，生成矢量文件列出每个瓦片的范围。用于 MapServer 等。

**基本用法**：

```bash
# 基本索引
gdaltindex index.shp *.tif

# 输出为 GeoPackage
gdaltindex -of GPKG index.gpkg *.tif

# 绝对路径
gdaltindex -write_absolute_path index.shp *.tif

# 重投影索引
gdaltindex -t_srs EPSG:4326 index.shp *.tif

# 递归搜索目录
gdaltindex -recursive -of GPKG index.gpkg /path/to/rasters/

# 使用通配符过滤
gdaltindex -filename_filter "*.tif" index.shp /data/

# 跳过不同投影的文件
gdaltindex -skip_different_projection index.shp *.tif

# 存储源 SRS 信息
gdaltindex -src_srs_name src_srs -src_srs_format EPSG index.shp *.tif
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-of <format>` | 输出格式 |
| `-write_absolute_path` | 存储绝对路径 |
| `-skip_different_projection` | 跳过异投影文件 |
| `-t_srs <srs>` | 目标投影（统一所有瓦片） |
| `-src_srs_name <name>` | SRS 字段名 |
| `-recursive` | 递归搜索目录 |
| `-filename_filter <pattern>` | 文件名过滤 |
| `-tileindex <name>` | 索引字段名（默认 location） |

---

### 12. gdal_edit.py - 编辑栅格元数据

**描述**: 修改现有栅格的地理参考信息、坐标系、NoData 值等。

**基本用法**：

```bash
# 设置坐标参考系
gdal_edit.py -a_srs EPSG:4326 input.tif

# 设置地理范围
gdal_edit.py -a_ullr -180 90 180 -90 input.tif

# 设置分辨率
gdal_edit.py -tr 30 30 input.tif

# 设置 NoData 值
gdal_edit.py -a_nodata 0 input.tif

# 添加地面控制点（GCP）
gdal_edit.py -gcp 0 0 -74.0 40.0 input.tif

# 添加元数据
gdal_edit.py -mo DATUM=WGS84 -mo SOURCE=USGS input.tif

# 计算并设置统计信息
gdal_edit.py -stats input.tif

# 清除地理参考
gdal_edit.py -unsetgt input.tif

# 删除 NoData 值
gdal_edit.py -unsetnodata input.tif
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-a_srs <srs>` | 设置坐标参考系 |
| `-a_ullr <ulx> <uly> <lrx> <lry>` | 设置地理范围 |
| `-tr <xres> <yres>` | 设置分辨率 |
| `-unsetgt` | 删除地理参考 |
| `-a_nodata <value>` | 设置 NoData 值 |
| `-unsetnodata` | 删除 NoData 值 |
| `-stats` | 计算统计信息 |
| `-mo <KEY>=<VALUE>` | 添加元数据 |
| `-gcp <pixel> <line> <x> <y>` | 添加地面控制点 |

---

### 13. nearblack - 清理黑白边界

**描述**: 将接近黑色或白色的边界像素设置为纯黑或白，用于清理空照片的角落。

**基本用法**：

```bash
# 清理黑色边界（默认）
nearblack input.tif -o output.tif

# 搜索白色边界
nearblack -white input.tif -o output.tif

# 自定义颜色
nearblack -color 100,100,100 input.tif -o output.tif

# 设置容差
nearblack -near 20 input.tif -o output.tif

# 添加 Alpha 通道
nearblack -setalpha input.tif -o output.tif

# 添加掩膜波段
nearblack -setmask input.tif -o output.tif

# 指定输出格式
nearblack -of JPEG input.tif -o output.jpg
```

**关键参数**：

| 参数 | 说明 |
|------|------|
| `-o <file>` | 输出文件 |
| `-of <format>` | 输出格式 |
| `-white` | 搜索白色而非黑色 |
| `-color <c1>,<c2>,...` | 搜索特定颜色 |
| `-near <dist>` | 颜色容差（0-255，默认 15） |
| `-nb <pixels>` | 连续非黑像素数（默认 2） |
| `-setalpha` | 添加 Alpha 通道 |
| `-setmask` | 添加掩膜波段 |

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

## 参考资源

- **官方文档**：https://gdal.org/
- **开发者指南**：https://gdal.org/development/dev_practices.html
- **API 文档**：https://gdal.org/api/
- **问题追踪**：https://github.com/OSGeo/gdal/issues
- **GDAL 社区**：https://lists.osgeo.org/pipermail/gdal-dev/

