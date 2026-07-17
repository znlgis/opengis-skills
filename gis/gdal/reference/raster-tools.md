# GDAL Raster Tools Reference

Detailed parameter reference and examples for GDAL raster tools.

---

## gdalinfo — Raster Info Query

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

## gdal_translate — Format Conversion and Resampling

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

## gdalwarp — Reprojection and Mosaicking

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

## gdal_merge.py — Raster Mosaic

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

## gdal_calc.py — Raster Calculator

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

## gdal_contour — Contour Line Extraction

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
| `-off <offset>` | 间隔偏移量 |
| `-p` | 生成多边形而非线 |
| `-3d` | 输出 3D 矢量 |
| `-f <format>` | 输出格式 |
| `-b <band>` | 源波段号 |

---

## gdal_grid — Grid Creation from Scattered Points

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
- `average` — 平均值（最简单）
- `invdist` — 反距离加权（常用）
- `invdistnn` — 反距离加权（最近邻）
- `kriging` — 克里金插值（高级）
- `linear` — 线性内插（TIN）

---

## gdal_polygonize.py — Raster to Vector Polygon

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

## gdaltindex — Raster Tile Index

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

## gdal_edit.py — Edit Raster Metadata

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

## nearblack — Clean Black/White Borders

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
