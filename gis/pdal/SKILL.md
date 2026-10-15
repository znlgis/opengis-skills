---
name: pdal
description: "Use when processing point cloud data (LAS/LAZ/BPF/EPT/COPC) via CLI or Python — pipeline JSON workflows, format conversion, reprojection, cropping, outlier removal, ground classification (SMRF), and DEM generation from LiDAR. PDAL (Point Data Abstraction Library) is the point cloud equivalent of GDAL: pdal info/translate/pipeline commands plus pdal.Pipeline Python bindings."
tags:
  - pdal
  - point-cloud
  - lidar
  - las
  - laz
  - pipeline
  - dem
  - gis
  - geospatial
---

> **项目地址：** <https://github.com/PDAL/PDAL>
>
> **官方文档：** <https://pdal.io/>
>
> **最新版本：** 2.10.2（2026-06 发布，[发布页](https://github.com/PDAL/PDAL/releases)）
>
> **许可证：** BSD-3-Clause

## 概述

PDAL（Point Data Abstraction Library）是处理点云数据的开源库与命令行工具集，常被称作“点云界的 GDAL”。它把点云读取、过滤、写入抽象为统一的 stage 模型，用 JSON pipeline 描述整条处理链。支持 LAS/LAZ、BPF、EPT、COPC、文本等多种格式。既提供 `pdal` 命令行（info/translate/pipeline 等），也提供 Python、C++ 绑定，常与 GDAL 配合完成地面分类与 DEM 生成。

- **Stage 模型**：reader → filter → writer 串联，每个 stage 由 `type` 与参数描述
- **流式优先**：默认尽量使用 stream mode，大文件不必整体载入
- **格式广泛**：内置 LazPerf，LAZ 压缩读写开箱即用
- **生态衔接**：writers.gdal 直接输出 GeoTIFF DEM，Python 绑定返回 NumPy 数组

## 环境准备

### 安装方法一：apt（Debian/Ubuntu）

```bash
sudo apt update
sudo apt install pdal libpdal-dev python3-pdal
```

### 安装方法二：conda（推荐，跨平台）

```bash
conda install -c conda-forge pdal python-pdal
# 或先建环境再安装
conda create -n pdal -c conda-forge pdal python-pdal
conda activate pdal
```

### 安装方法三：Docker

```bash
docker pull pdal/pdal:latest
docker run --rm pdal/pdal pdal --version
# 交互式使用，将当前目录挂载到 /data
docker run --rm -it -v "$PWD":/data -w /data pdal/pdal
```

### Python 绑定（pip）

```bash
pip install PDAL   # 依赖系统已安装 PDAL 库（提供 pdal-config）
```

### 验证安装

```bash
pdal --version                  # 输出如 pdal 2.10.2
pdal --drivers                  # 列出可用的 readers/filters/writers
pdal --options filters.smrf     # 查看某个 stage 的全部参数与默认值
```

## 核心 API/命令

### pdal info — 查看点云信息

```bash
pdal info input.las                     # 不带参数时默认等价 --stats（读取全部点统计）
pdal info input.las --summary           # 概要（点数、范围、坐标系）
pdal info input.las --metadata          # 元数据（含 LAS 头信息）
pdal info input.las --schema            # 维度 schema
pdal info input.las --all               # stats + schema + metadata
pdal info input.las -p 0-10             # 输出第 0-10 个点（0 起始）
pdal info input.las --query "636601.87, 849018.59, 425.10"   # 按到该点的距离排序输出
```

输出默认为 JSON，可直接用 `jq` 解析。

### pdal translate — 转换与简单过滤

```bash
# 基本语法：pdal translate [options] input output [filter...]
pdal translate input.las output.laz

# 重投影
pdal translate input.las output.las -f reprojection --filters.reprojection.out_srs="EPSG:4326"

# 多级过滤按顺序串联
pdal translate input.las output.las smrf expression --filters.expression.expression="Classification == 2"

# 指定 writer 参数（LAZ 压缩）
pdal translate input.las output.laz --writers.las.compression=true
```

### pdal pipeline — 运行 JSON pipeline

```bash
pdal pipeline pipeline.json
pdal pipeline --stdin < pipeline.json
pdal pipeline pipeline.json --validate       # 只校验并报告是否可流式处理
pdal pipeline pipeline.json --metadata meta.json
pdal pipeline pipeline.json --writers.las.filename=out.laz   # 命令行覆盖参数
pdal pipeline pipeline.json --stage.points.filename=data.laz # 按 tag 覆盖
```

### Pipeline JSON 结构

```json
[
  "input.las",
  { "type": "filters.crop", "bounds": "([0,100],[0,100])" },
  "output.laz"
]
```

- 顶层为 stage 数组；旧式 `{"pipeline": [...]}` 对象写法仍兼容
- 每个 stage 可含：`type`（reader/filter/writer 类型）、`filename`、`tag`（唯一标识）、`inputs`（上游 tag 数组）及专有参数
- 字符串 stage 等价于只含 filename 的 stage，驱动按扩展名推断
- stage 按列出顺序执行；未写 `inputs` 时沿用默认输入链；`inputs` 引用的 tag 必须先定义

### 常用 filters

#### filters.crop — 裁剪

```json
{ "type": "filters.crop", "bounds": "([0,1000000],[0,1000000])" }
```

- `bounds` 支持 PDAL 风格 `([xmin,xmax],[ymin,ymax])`（3D 时加第三段）、GeoJSON BBOX、JSON 对象
- `polygon` 接受 WKT 字符串（如 `"POLYGON((0 0, 5000 10000, 10000 0, 0 0))"`）
- `point` + `distance` 按半径裁剪；`outside` 取反，只保留区域外的点

#### filters.range — 按维度取值过滤

```json
{ "type": "filters.range", "limits": "Z[0:100],Classification[2:2]" }
```

- 范围语法：`Z[10:]`（Z ≥ 10）、`Classification[2:2]`（等于 2）、`Blue[:255)`（开区间）、`Intensity![25:25]`（取反）
- 同维度多段取并集，不同维度取交集
- 2.5 起推荐新代码改用 filters.expression；filters.range 将在 3.0 弃用

#### filters.expression — 表达式过滤

```json
{ "type": "filters.expression", "expression": "Classification == 2" }
```

#### filters.reprojection — 重投影

```json
{ "type": "filters.reprojection", "in_srs": "EPSG:26916", "out_srs": "EPSG:4326" }
```

- `out_srs` 必需；`in_srs` 仅在数据自身缺少坐标系时给出
- 重投影会改变坐标精度，writer 侧用 `scale_x/y/z` 与 `offset_x/y/z: "auto"` 保持精度

#### filters.outlier — 去噪

```json
{ "type": "filters.outlier", "method": "statistical", "mean_k": 12, "multiplier": 2.2 }
```

- `method` 可选 `statistical`（`mean_k` 默认 8，`multiplier` 默认 2.0）或 `radius`（`radius` 默认 1.0，`min_k` 默认 2）
- 命中点标记为 `Classification=7`（LAS 噪点），再用 filters.expression 删除

#### filters.smrf — 地面分类

```json
{ "type": "filters.smrf", "cell": 1.0, "slope": 0.15, "threshold": 0.5, "window": 18.0, "scalar": 1.25 }
```

- Simple Morphological Filter：地面点标 `Classification=2`（`ground_class`），非地面标 `1`（`other_class`）
- 常用参数：`cell`（格网大小，默认 1.0）、`window`（最大窗口，默认 18.0）、`slope`（默认 0.15）、`threshold`（默认 0.5）、`scalar`（高程缩放，默认 1.25）
- 之后用 filters.expression（`"Classification == 2"`）只保留地面点

### 常用 writers

#### writers.las

```json
{ "type": "writers.las", "filename": "output.laz", "compression": "true", "minor_version": 4 }
```

- `compression` 设为 `true` 输出 LAZ（LazPerf 压缩）
- `scale_x/y/z` 与 `offset_x/y/z` 可设 `"auto"` 防止精度损失
- `a_srs` 指定输出坐标系；`forward` 可继承源 LAS 头字段

#### writers.gdal — DEM 栅格化

```json
{
  "type": "writers.gdal",
  "filename": "dem.tif",
  "resolution": 1.0,
  "output_type": "idw",
  "gdaldriver": "GTiff"
}
```

- `resolution` 必需（格网边长）；`dimension` 默认 `Z`
- `output_type` 可选 `min/max/mean/idw/count/stdev/all`（默认 `all`，输出多波段）
- `gdalopts` 透传 GDAL 驱动参数；`override_srs` 指定输出栅格坐标系

### Python 绑定

```python
import json
import pdal

stages = [
    "input.las",
    {"type": "filters.smrf"},
    {"type": "filters.expression", "expression": "Classification == 2"},
    {"type": "writers.gdal", "filename": "dem.tif", "resolution": 1.0, "output_type": "idw"}
]

pipeline = pdal.Pipeline(json.dumps(stages))
count = pipeline.execute()    # 返回处理的点数
arrays = pipeline.arrays      # NumPy 结构化数组列表
metadata = pipeline.metadata  # 元数据
log = pipeline.log            # 执行日志

points = arrays[0]
x = points["X"]               # 按维度名取列
```

## 典型工作流

### 工作流 1：批量格式转换（LAS → LAZ）

```bash
for f in *.las; do
  pdal translate "$f" "${f%.las}.laz"
done
```

### 工作流 2：裁剪 + 重投影

pipeline 文件 `clip_reproject.json`：

```json
[
  "input.las",
  { "type": "filters.crop", "bounds": "([500000,500500],[4000000,4000500])" },
  { "type": "filters.reprojection", "in_srs": "EPSG:32650", "out_srs": "EPSG:4326" },
  { "type": "writers.las", "filename": "output_4326.laz", "compression": "true",
    "scale_x": "auto", "scale_y": "auto", "scale_z": "auto" }
]
```

```bash
pdal pipeline clip_reproject.json
```

### 工作流 3：地面分类与 DEM 生成（与 GDAL 配合）

```json
[
  "input.las",
  { "type": "filters.outlier", "method": "statistical", "mean_k": 8, "multiplier": 2.0 },
  { "type": "filters.smrf", "cell": 1.0, "slope": 0.15, "threshold": 0.5, "window": 18.0 },
  { "type": "filters.expression", "expression": "Classification == 2" },
  { "type": "writers.gdal", "filename": "dem.tif", "resolution": 1.0, "output_type": "idw", "window_size": 3 }
]
```

```bash
pdal pipeline ground_dem.json
gdalinfo dem.tif
gdal_translate -of COG dem.tif dem_cog.tif   # 后续处理交给 GDAL
```

### 工作流 4：Python 批处理去噪

```python
import glob
import json
import pdal

for las_file in glob.glob("tiles/*.las"):
    stages = [
        las_file,
        {"type": "filters.outlier", "method": "statistical", "mean_k": 8, "multiplier": 2.0},
        {"type": "filters.expression", "expression": "Classification != 7"},
        las_file.replace(".las", "_denoised.laz"),
    ]
    count = pdal.Pipeline(json.dumps(stages)).execute()
    print(las_file, count)
```

## 最佳实践

- 先探测再处理：`pdal info --summary` 检查点数、范围与坐标系，`--metadata` 查看 LAS 头信息
- 复杂处理写成 pipeline JSON 文件：可复用、可版本化，用 `pdal pipeline --validate` 预校验
- 处理顺序影响结果：去噪（outlier）→ 地面分类（smrf）→ 提取（expression）→ 输出（writer）
- 优先流式处理：stream mode 是默认策略；outlier、smrf 等需要全局计算的 stage 会回退标准模式，内存受限时按块拆分数据
- 重投影后用 writer 的 `scale_*/offset_* = "auto"`，防止坐标精度截断
- 输出统一用 LAZ（`compression: "true"`）减小体积，GDAL/QGIS 可直接读取
- 用 `tag` + `inputs` 构建分支与合并（filters.merge），tag 必须先定义
- `pdal ground` 命令自 2.6.0 起弃用，改用 filters.smrf 的 pipeline 写法
- SMRF 参数需按数据调整：window 参考最大建筑物尺寸，slope/threshold 可参考 SMRF 论文的参数组合

## 常见问题

| 问题 | 解决 |
|------|------|
| `pdal: command not found` | 按环境准备安装（apt/conda/Docker）；Windows 推荐 conda 或 OSGeo4W |
| `pip install PDAL` 报错找不到 pdal-config | 需先安装 PDAL 库（apt 的 libpdal-dev 或 conda 的 pdal），推荐直接用 conda 安装 python-pdal |
| pipeline 报解析失败 | 用 `pdal pipeline --validate` 定位 JSON 语法错误；确认顶层是 stage 数组 |
| filters.reprojection 报缺少 SRS | 设置 `out_srs`；数据无坐标系时补充 `in_srs` |
| 处理大文件内存不足 | 尽量使用支持流式的 stage；outlier/smrf 等全局 filter 按数据分块处理 |
| writers.gdal 输出了多波段 | 默认 `output_type: "all"`，指定 `mean` 或 `idw` 等单值即可输出单波段 |
| 重投影后坐标精度变差 | 在 writer 中设置 `scale_x/y/z` 与 `offset_x/y/z: "auto"` |
| 地面分类效果不佳 | 调整 smrf 的 window/slope/threshold/scalar，先检查数据坐标系与高程单位 |

## 参考资源

- **官方文档：** <https://pdal.io/> | [Pipeline](https://pdal.io/en/latest/pipeline.html) | [命令行应用](https://pdal.io/en/latest/apps/index.html) | [Stage 参考](https://pdal.io/en/latest/stages/index.html) | [Python 绑定](https://pdal.io/en/latest/python.html)
- **GitHub：** <https://github.com/PDAL/PDAL>
- **Docker 镜像：** <https://hub.docker.com/r/pdal/pdal>
- **示例数据：** <https://github.com/PDAL/data>

## 相关技能

- **gdal** — 栅格/矢量处理，DEM 后处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **qgis-process** — QGIS 命令行批处理：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **geopandas** — Python 矢量数据处理：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **shapely** — 几何对象计算，与裁剪范围构造相关：[../shapely/SKILL.md](../shapely/SKILL.md)

## AI 使用建议

1. 探索数据先跑 `pdal info input.las --summary`，确认坐标系与范围后再设计 pipeline
2. 生成 pipeline 后先用 `pdal pipeline --validate` 校验，再实际运行
3. 大文件避免一次性标准模式处理，优先流式 stage 或分块
4. 需要修改参数时优先在 pipeline JSON 中修改，而不是堆叠长命令行
5. Python 场景用 `json.dumps` 构造 stage 列表，便于程序化生成与复用
