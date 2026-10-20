---
name: grass-gis
description: "Use when doing GIS geoprocessing with GRASS GIS headlessly — grass --exec and --tmp-project for servers and CI, g.region computational region management, r.* raster, v.* vector, r3.* 3D raster and t.* temporal modules, r.import/v.import data import, or Python scripting with grass.script, grass.script.array and grass.tools."
tags:
  - gis
  - raster
  - vector
  - python
  - cli
  - headless
  - temporal
  - automation
  - qgis
---

> **项目地址：** <https://github.com/OSGeo/grass>
>
> **官方文档：** <https://grass.osgeo.org/>
>
> **手册入口：** <https://grass.osgeo.org/grass-stable/manuals/>
>
> **最新版本：** 8.5.0（截至 2026-10，GitHub Releases；8.4 系列最新补丁 8.4.2）
>
> **许可证：** GPL-2.0

## 概述

GRASS GIS（Geographic Resources Analysis and Support System）是 OSGeo 创始项目之一，提供栅格、拓扑矢量、三维栅格、影像与时序数据的分析能力。它以模块化命令体系为核心：每个功能是一个独立命令（模块），既可交互使用，也可通过 `grass --exec` 在无头会话中执行。计算区域（computational region）与地图数据范围分离管理，是理解其行为的关键概念。Python 生态（`grass.script`、PyGRASS、`grass.jupyter`）使其适合脚本化与自动化。

核心特点：

- **模块化命令体系**：`g.*`（通用）、`r.*`（二维栅格）、`r3.*`（三维栅格）、`v.*`（矢量）、`i.*`（影像）、`db.*`（数据库）、`t.*`（时空）、`d.*`/`ps.*`（显示，仅交互会话）。
- **计算区域独立管理**：栅格模块在 `g.region` 定义的窗口上运算，与地图本身范围解耦。
- **无头执行**：`grass --exec` / `--tmp-project` / `--tmp-mapset` 支持服务器与 CI 场景。
- **时空框架**：`t.*` 模块管理 strds / str3ds / stvds 时空数据集。
- **Python 接口**：`grass.script`（命令封装）、`grass.script.array`（NumPy 读写栅格）、`grass.tools`（8.4+ 面向对象工具调用）、`grass.jupyter`（笔记本集成）。

## 环境准备

### 安装方式

```bash
# Ubuntu / Debian（发行版仓库版本可能滞后，可用 ubuntugis PPA 获取新版）
sudo apt update && sudo apt install grass

# Conda / mamba / pixi（conda-forge 提供 Linux、macOS、Windows 64 位包）
conda install -c conda-forge grass

# Docker（官方镜像；下载页同时以 osgeo/grass-gis 名称与 releasebranch_8_5-* 标签发布）
docker pull osgeo/grass
docker run --rm osgeo/grass grass --version
```

Windows 可通过 OSGeo4W 安装器安装，之后在 "OSGeo4W Shell" 中使用 `grass` 命令。

### 验证安装

```bash
grass --version

# 在临时 XY 项目中打印完整版本与依赖库信息（Docker 镜像自检常用）
grass --tmp-project XY --exec g.version -rge
```

### 官方示例数据

下载 North Carolina 示例项目用于练习：

```bash
curl -LO https://grass.osgeo.org/sampledata/north_carolina/nc_basic_spm_grass7.zip
unzip nc_basic_spm_grass7.zip -d $HOME/grassdata/
```

## 核心 API/命令

### 模块命名体系

| 前缀 | 类别 | 常用模块 |
|------|------|----------|
| `g.*` | 通用（项目/地图集/区域/元数据） | g.region、g.list、g.remove、g.copy、g.rename、g.proj、g.version、g.extension |
| `r.*` | 二维栅格 | r.import、r.mapcalc、r.univar、r.slope.aspect、r.watershed、r.neighbors、r.series、r.out.gdal |
| `r3.*` | 三维栅格 | r3.in.xyz、r3.mapcalc、r3.stats、r3.univar |
| `v.*` | 矢量 | v.import、v.buffer、v.overlay、v.clean、v.clip、v.what.rast、v.rast.stats、v.out.ogr |
| `i.*` | 影像 | i.vi、i.segment、i.pca |
| `db.*` | 数据库 | db.select、db.in.ogr |
| `t.*` | 时空 | t.create、t.register、t.rast.aggregate、t.rast.series |
| `d.*` / `ps.*` | 显示 / PostScript（需要显示环境） | d.rast、d.vect |

### grass 启动器与无头执行

```bash
# 创建项目（-c 指定 CRS 或从数据文件推断；-e 表示创建后立即退出）
grass -c EPSG:4326 $HOME/grassdata/myproject
grass -c dem.tif -e $HOME/grassdata/dem_project

# 无头执行：在已有项目中运行单个模块
grass $HOME/grassdata/nc_basic_spm_grass7/PERMANENT --exec r.univar map=elevation

# 无头执行：运行 shell / Python 脚本
grass $HOME/grassdata/nc_basic_spm_grass7/PERMANENT --exec sh test.sh
grass $HOME/grassdata/nc_basic_spm_grass7/PERMANENT --exec python3 analyze.py

# 临时项目：按指定 CRS 创建，运行结束自动删除（适合 CI）
grass --tmp-project EPSG:3358 --exec g.proj -p

# 临时地图集：复用已有项目数据，运行结束自动删除
grass --tmp-mapset $HOME/grassdata/nc_basic_spm_grass7/ --exec g.region -p

# 文本界面（无 GUI 环境）
grass --text $HOME/grassdata/nc_basic_spm_grass7/PERMANENT
```

> **注意：** `--exec` 的脚本需要 shebang（如 `#!/bin/sh`、`#!/usr/bin/env python3`）；临时项目/地图集在结束时删除，脚本内需先通过 `r.out.gdal` / `v.out.ogr` 导出结果。

### g.region 计算区域管理

栅格模块只在当前计算区域内运算，分析前应先设置区域：

```bash
# 打印当前区域（人类可读 / shell 变量 / JSON）
g.region -p
g.region -p format=shell
g.region -p format=json

# 按栅格或矢量地图对齐区域
g.region raster=elevation
g.region vector=roads align=elevation

# 指定范围与分辨率
g.region n=220750 s=220000 w=638300 e=639000 res=10

# 缩放到非 NULL 数据范围
g.region raster=elevation zoom=elevation

# 保存 / 恢复命名区域
g.region raster=elevation save=dem_region
g.region region=dem_region
```

### 数据导入导出

```bash
# 导入（r.import / v.import 会重投影到项目 CRS）
r.import input=dem.tif output=dem
v.import input=roads.gpkg output=roads layer=roads

# 导出
r.out.gdal input=slope output=slope.tif format=GTiff
v.out.ogr input=roads output=roads.gpkg format=GPKG
```

`r.in.gdal` / `v.in.ogr` 不重投影，适合 CRS 已一致的场景。

### 常用分析模块

```bash
# 栅格计算与统计
r.mapcalc "ndvi = (nir - red) / (nir + red)"
r.univar map=elevation
r.series input=ndvi_202601,ndvi_202602,ndvi_202603 output=ndvi_max method=maximum

# 地形分析
r.slope.aspect elevation=dem slope=slope aspect=aspect
r.watershed elevation=dem accumulation=flowacc basin=basins
r.neighbors input=dem output=dem_smooth size=5 method=average

# 矢量分析
v.buffer input=roads output=roads_buf distance=100
v.overlay a=zones b=landuse operator=and output=zones_landuse
v.rast.stats vector=zones raster=elevation column_prefix=elev method=average
```

### 时空数据集（t.*）

时空框架把带时间戳的栅格/矢量地图组织为数据集：strds（时空栅格）、str3ds（时空三维栅格）、stvds（时空矢量）。时空数据库按地图集（mapset）独立，首次运行 `t.*` 命令时自动创建，默认使用 SQLite3（`tgis.sqlite`），也支持 PostgreSQL 后端。

```bash
# 创建 strds 并注册地图（-i 表示由起始时间与增量推导各时间区间）
t.create type=strds temporaltype=absolute output=ndvi_monthly title="月度 NDVI" description="示例数据集"
t.register -i type=strds input=ndvi_monthly \
    maps=ndvi_202601,ndvi_202602,ndvi_202603 start=2026-01-01 increment="1 month"

# 查询
t.list type=strds
t.info type=strds input=ndvi_monthly
t.rast.list input=ndvi_monthly columns=name,start_time,end_time

# 分析：按时间粒度聚合、时间序列统计、表达式计算
t.rast.aggregate input=ndvi_monthly output=ndvi_quarterly granularity="3 months" method=average
t.rast.series input=ndvi_monthly output=ndvi_mean method=average
t.rast.mapcalc inputs=ndvi_monthly output=ndvi_scaled basename=scaled expression="ndvi * 0.0001"
```

### Python 脚本化

`grass.script`（惯用别名 `gs`）把模块调用映射为函数：第一个参数是模块名，选项为关键字参数，标志位放入 `flags`。

```python
import grass.script as gs

# 在 GRASS 会话之外启动会话（脚本未经 grass --exec 运行时）
session = gs.setup.init("/home/user/grassdata/nc_basic_spm_grass7/PERMANENT")

gs.run_command("g.region", raster="elevation")
stats = gs.parse_command("r.univar", map="elevation", flags="g")  # 返回 dict
print(stats["mean"])
text = gs.read_command("r.info", map="elevation", flags="g")      # 返回字符串

# mapcalc 专用包装函数
gs.mapcalc("slope_high = slope > 10")

session.finish()
```

`gs.setup.init(...)` 返回的会话对象可作上下文管理器使用：`with gs.setup.init(path) as session: ...`。

NumPy 互操作使用 `grass.script.array`：

```python
import grass.script as gs
from grass.script import array as garray

gs.use_temp_region()  # 临时区域仅当前 Python 会话有效，不影响地图集
gs.run_command("g.region", raster="elevation")

elev = garray.array(mapname="elevation")   # 按当前区域读入二维数组
elev_ft = elev * 3.28084
elev_ft.write(mapname="elev_ft", overwrite=True)

# 三维栅格用 array3d，索引顺序为 [depth][row][column]
elev3d = garray.array3d(mapname="elev3d")
```

8.4+ 提供面向对象的工具调用接口 `grass.tools`（模块名中的点替换为下划线，支持 numpy 输入输出）：

```python
from grass.tools import Tools

tools = Tools(session=session)
tools.g_region(rows=100, cols=100)
tools.r_random_surface(output="surface", seed=42)
print(tools.g_region(flags="p", format="json")["cells"])
```

`grass.jupyter` 提供 Jupyter 集成（`init`、`Map`、`Map3D`、`InteractiveMap`、`SeriesMap`、`TimeSeriesMap` 等）。

### 与 QGIS 集成

QGIS Processing 工具箱内置 GRASS provider：在系统已安装 GRASS GIS 的前提下，可直接在 GUI 或通过 `qgis_process` 命令行调用 GRASS 算法（算法 ID 前缀为 `grass:`，QGIS 3.x 时代为 `grass7:`），QGIS 会自动完成数据转换与临时地图集管理。详见 [qgis-process](../qgis-process/SKILL.md)。

## 典型工作流

### 工作流 1：无头栅格地形分析

```bash
# 1. 创建项目（CRS 从 DEM 文件推断）并退出
grass -c dem.tif -e $HOME/grassdata/dem_project

# 2. 无头执行完整分析链，结果导出为 GeoTIFF
grass $HOME/grassdata/dem_project/PERMANENT --exec sh -c '
  r.import input='"$(pwd)"'/dem.tif output=dem --overwrite
  g.region raster=dem
  r.slope.aspect elevation=dem slope=slope aspect=aspect
  r.out.gdal input=slope output='"$(pwd)"'/slope.tif format=GTiff --overwrite
'
```

### 工作流 2：CI 中的临时项目

```bash
# 无需预先建库，EPSG 已知时直接运行脚本；结果必须在脚本内导出
grass --tmp-project EPSG:32633 --exec python3 analysis.py
```

### 工作流 3：时空数据集聚合

```bash
grass $HOME/grassdata/ndvi_project/PERMANENT --exec sh -c '
  t.create type=strds temporaltype=absolute output=ndvi_monthly title="月度 NDVI" description=""
  t.register -i type=strds input=ndvi_monthly \
      maps=ndvi_202601,ndvi_202602,ndvi_202603 start=2026-01-01 increment="1 month"
  t.rast.series input=ndvi_monthly output=ndvi_mean method=average
  r.out.gdal input=ndvi_mean output='"$(pwd)"'/ndvi_mean.tif format=GTiff --overwrite
'
```

## 最佳实践

1. **分析前先 `g.region`**：按目标地图设置区域（`g.region raster=...`），否则结果范围可能不是预期值。
2. **无头场景用 `--exec` 单行执行**：避免交互式会话依赖；CI 优先使用 `--tmp-project` 保持幂等。
3. **临时项目内先导出结果**：`--tmp-project` / `--tmp-mapset` 结束时目录被删除。
4. **覆盖已有地图加 `--overwrite`**：否则模块报地图已存在并退出非零。
5. **Python 中结构化解析**：用 `gs.parse_command(..., format="json")` 或 `flags="g"` 获取 dict，不要手工解析人类可读输出。
6. **Python 会话内改动区域用 `gs.use_temp_region()`**：临时区域随会话结束自动还原。
7. **导入优先用 `r.import` / `v.import`**：自动重投影到项目 CRS，避免 CRS 不一致导致的分析错误。
8. **`--exec` 脚本加 shebang**：缺失 shebang 会报 `Exec format error`。

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `grass: command not found` | 确认安装并把 `grass` 加入 `PATH`；Windows 在 OSGeo4W Shell 中运行 |
| 模块报地图不存在（`Raster map <x> not found`） | 用 `g.list type=raster` 确认地图名与当前地图集；跨地图集访问用 `map@mapset` |
| 分析结果范围或分辨率不对 | 先用 `g.region -p` 检查当前区域，再用 `g.region raster=<map>` 对齐 |
| 无头服务器上启动失败 | 使用 `--text` / `--exec`，不要启动 GUI（`--gui` 需要显示环境） |
| `--exec` 报 `Exec format error` | 脚本首行添加 shebang 并赋予可执行权限，或显式 `--exec python3 script.py` |
| 模块报输出地图已存在 | 添加 `--overwrite` 覆盖，或先用 `g.remove` 删除 |
| Python 报 `GISBASE not defined` / 找不到模块 | 通过 `grass --exec python3 script.py` 运行，或先调用 `gs.setup.init(path)` |
| 临时项目/地图集运行后数据丢失 | 临时目录结束即删除，需在脚本内用 `r.out.gdal` / `v.out.ogr` 先导出 |
| Docker 中结果文件属主为 root | 运行时加 `--user=$(id -u):$(id -g)` 与 `--env HOME=/data/` |
| `t.*` 报时空数据库错误 | 时空数据库按地图集独立且自动创建；确认在正确地图集内运行并检查 `t.connect -p` 状态 |

## 参考资源

- **GRASS GIS 源码：** <https://github.com/OSGeo/grass>
- **官方文档：** <https://grass.osgeo.org/>
- **模块手册（grass-stable）：** <https://grass.osgeo.org/grass-stable/manuals/>
- **grass 启动器说明：** <https://grass.osgeo.org/grass-stable/manuals/grass.html>
- **Python 脚本 API：** <https://grass.osgeo.org/grass-stable/manuals/libpython/>
- **时空框架介绍：** <https://grass.osgeo.org/grass-stable/manuals/temporalintro.html>
- **Docker 镜像说明：** <https://grass.osgeo.org/download/docker/>
- **官方示例数据：** <https://grass.osgeo.org/sampledata/north_carolina/nc_basic_spm_grass7.zip>

## 相关技能

- **qgis-process** — QGIS Processing 命令行（含 GRASS provider 调用）：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **gdal** — 栅格/矢量格式转换与命令行工具：[../gdal/SKILL.md](../gdal/SKILL.md)
- **geopandas** — Python 矢量数据分析：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **pyqgis** — QGIS Python 绑定：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("grass-gis")` 加载（用户也可输入 `/grass-gis`）；本技能没有 reference 子目录，模块参数用 `r.univar --help` 或官网手册核对；技能目录只读，脚本与导出结果写到会话工作区。
- **执行环境**：命令交给 dsh 的 shell 工具（Windows 用 `pwsh`；仅暴露 `run_code` 的会话在 `tools.pwsh` 中执行）。正文里 `grass ... --exec sh -c '...'` 的多行引用在 pwsh 下不可靠，改为把模块序列写进 `.py` 脚本（首行 `#!/usr/bin/env python3`），再 `grass --tmp-project EPSG:3857 --exec python3 analysis.py`。
- **先探测版本**：`grass --version`（应为 8.5.0，LTR 8.4.2）、`grass --tmp-project EPSG:3857 --exec g.region -p`；8.4 之前没有 `grass.tools`，Python 脚本改用 `gs.run_command`。
- **验证产物**：`--tmp-project` 内的地图最后必须导出——`r.out.gdal input=slope output=/work/slope.tif format=GTiff`，随后 `gdalinfo -json slope.tif` 核对 CRS 与范围；会话内核对用 `g.region -p format=json`、`g.list type=raster`。
- **区域语义优先**：栅格模块只处理计算区域内的像元，结果范围不对先看 `g.region -p`；重复运行加 `--overwrite`，否则模块报地图已存在并非零退出。
- **错误识别**：GRASS 模块的失败以 `ERROR:` 开头并返回非零码（如 `Raster map <x> not found`），据此区分地图名、区域为空还是输出已存在问题，不要只读最后一行日志。
- **安全与权限**：`g.remove`、`--overwrite`、`t.connect` 会改/删地图集数据；`--tmp-project`/`--tmp-mapset` 结束即删除目录，结果必须先导出；启动 Docker 或改文件属主（`--user=$(id -u):$(id -g)`）前先确认写入路径。
