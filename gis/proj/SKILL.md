---
name: proj
description: "Use when transforming coordinates or inspecting CRS definitions from the command line — cs2cs, projinfo -s/-t, proj projection math, cct, EPSG lookup, datum shift with grid files, WKT/PROJJSON export, or debugging \"Cannot find proj.db\" and latitude-first axis order. PROJ 9.9.0: the OSGeo engine behind GDAL/QGIS, with the proj.db SQLite database."
tags:
  - proj
  - crs
  - coordinate-transformation
  - reprojection
  - epsg
  - projinfo
  - cs2cs
  - geodesy
  - wkt
  - gis
---

> **项目地址：** <https://github.com/OSGeo/PROJ>
>
> **官方文档：** <https://proj.org/>
>
> **命令行文档：** <https://proj.org/en/stable/apps/index.html>
>
> **最新版本：** 9.9.0（截至 2026-10，PROJ 版本号即其数据版本）
>
> **许可证：** MIT

## 概述

PROJ 是 OSGeo 维护的坐标转换与投影库，也是 GDAL、QGIS、PostGIS 等软件坐标运算的底层引擎。它将坐标系与转换参数存储于 SQLite 数据库 `proj.db`，并通过命令行工具暴露查询与转换能力：

- **`projinfo`** — 查询 CRS 定义、查找两坐标系之间的转换操作、导出 WKT/PROJJSON
- **`cs2cs`** — 在任意两个可定义的坐标系之间做坐标转换（含基准面转换）
- **`proj`** — 在同一基准面内做地理坐标与投影坐标的正反算
- **`cct`** — 4D（含时间）坐标转换，输入为点列表
- **`projsync`** — 从 PROJ CDN 下载基准面转换所需的网格文件
- **`proj.db`** — SQLite 数据库，内含 EPSG 数据集与坐标转换记录

---

## 环境准备

### 验证安装

```bash
projinfo --version          # 输出版本与 proj.db 路径，推荐用于验证
projinfo --searchpaths      # 列出资源搜索路径
```

`proj` 直接执行会进入交互模式，不作为版本检查命令。

### 安装方法

#### Linux (Debian/Ubuntu)

```bash
apt-get update
apt-get install proj-bin proj-data
```

#### Linux (CentOS/RHEL/Fedora)

```bash
yum install proj proj-devel      # 或 dnf install proj proj-devel
```

#### macOS (Homebrew)

```bash
brew install proj
```

#### Conda（跨平台）

```bash
conda install -c conda-forge proj
```

#### Docker

```bash
docker run -it osgeo/proj:latest bash
```

#### Windows

安装 OSGeo4W 或 conda 发行版；GDAL/QGIS 的 Windows 安装包已内置 PROJ，无需单独安装。

### 数据与网络配置

```bash
# PROJ 9.1 起使用 PROJ_DATA（旧名为 PROJ_LIB，9.1 仍兼容）
export PROJ_DATA=/usr/share/proj

# 允许按需从 CDN 下载转换网格
export PROJ_NETWORK=ON
```

`proj.db` 必须可读，库才能正常工作；若报 `Cannot find proj.db`，请核对 `PROJ_DATA` 指向的目录。

---

## 核心 API/命令

### projinfo — CRS 与转换操作查询

查询单个对象（默认按 CRS 解释，`-k` 可指定 `crs|operation|datum|ensemble|ellipsoid`）：

```bash
# 查询 CRS，输出 PROJ 字符串与 WKT2:2019
projinfo EPSG:4326

# 以 PROJJSON 输出（-q 仅输出字符串本体）
projinfo GDA94 -o PROJJSON -q

# WKT1:GDAL 单行输出
projinfo -o WKT1:GDAL --single-line EPSG:25832

# 按名称识别，给出最接近数据库对象的概率
projinfo --identify EPSG:4326

# 将 2D CRS 提升为 3D
projinfo EPSG:4326 --3d
```

查找两坐标系之间的坐标转换操作：

```bash
# -s 源 CRS，-t 目标 CRS
projinfo -s EPSG:4326 -t EPSG:32650

# 限定作用范围与输出摘要
projinfo -s NAD27 -t EPSG:4269 --area "USA - Missouri" --summary
```

列表与数据库结构：

```bash
# 列出符合条件的 CRS
projinfo --list-crs --area Taiwan

# 转储数据库结构（可交给 sqlite3 导入）
projinfo --dump-db-structure
```

`-o` 支持 `all`、`default`、`PROJ`、`WKT_ALL`、`WKT2:2015`、`WKT2:2019`、`WKT1:GDAL`、`WKT1:ESRI`、`PROJJSON`、`SQL`，格式前加 `-` 表示禁用。输入可为 proj 字符串、WKT、`AUTHORITY:CODE`、对象名称、PROJJSON 或 OGC URN。

### cs2cs — 坐标系转换

```bash
# EPSG 代码：WGS 84 经纬度 → UTM 31N（EPSG 轴序为纬度在前）
echo 56 12 | cs2cs EPSG:4326 EPSG:25832

# 多行输入
cs2cs EPSG:4326 EPSG:32631 <<EOF
45N 2E
EOF
```

PROJ 字符串写法（`+to` 分隔源与目标）：

```bash
cs2cs +proj=latlong +datum=NAD83 +to +proj=utm +zone=10 +datum=NAD27 -r <<EOF
45d15.551666667N -111d30
+45.25919444444 111d30'000w
EOF
```

常用选项：

| 选项 | 作用 |
|------|------|
| `-I` | 反向转换（目标 CRS → 源 CRS） |
| `-r` / `-s` | 反转输入 / 输出的前两位轴顺序（第三位高度不变） |
| `-f <fmt>` | printf 风格输出格式，默认 `%.2f`（逆算输出度） |
| `-d <n>` | 输出保留小数位数 |
| `-E` | 输出行前附加原始输入坐标 |
| `--3d` | 启用三维转换 |
| `--only-best` | 只使用精度最高的转换，网格缺失时报错而非退回 |

### proj — 单基准面投影正反算

```bash
# 墨卡托投影（纬度 56.5° 为真比例）
echo 55.2 12.2 | proj +proj=merc +lat_ts=56.5 +ellps=GRS80

# UTM 12 带，输入纬度在前
proj +proj=utm +zone=12 -r <<EOF
45d15.551666667N -111d30
EOF

# 逆算（投影 → 地理），-V 输出带注释的详细参数
proj -I +proj=merc +lat_ts=56.5 +ellps=GRS80

# PROJ 9.3 起可直接接受 CRS（须为投影 CRS）
proj EPSG:6421 -V <<EOF
-120 35.8
EOF

# 列出可用投影标识
proj -l
proj -l=merc
```

### proj.db — SQLite 数据库

`proj.db` 存储 CRS、基准面、坐标转换与网格信息，可直接用 `sqlite3` 查询。视图 `crs_view` 保存 CRS 定义，`coordinate_operation_view` 保存转换记录：

```sql
-- 查询 NAD27 → NAD83 的可用转换及其精度
SELECT auth_name, code, name, method_name, accuracy
FROM coordinate_operation_view
WHERE source_crs_auth_name = 'EPSG' AND source_crs_code = '4267'
  AND target_crs_auth_name   = 'EPSG' AND target_crs_code   = '4269';
```

```bash
sqlite3 "$PROJ_DATA/proj.db" \
  "SELECT auth_name, code, name FROM crs_view WHERE auth_name='EPSG' LIMIT 5;"
```

### 其他工具

```bash
# 4D 坐标转换（含时间维），输入为点列表
cct +proj=pipeline +step +proj=cart +ellps=GRS80

# 大地线（大圆）计算
geod +ellps=WGS84 -I <<EOF
-120 35 0 120 35
EOF

# 从 CDN 下载全部转换网格，或按机构/范围筛选
projsync --all
projsync --source-id fr_ign --bbox 2,49,2,49
projsync --list-files
```

---

## 典型工作流

### 模式 1：WGS 84 经纬度 → UTM / Web Mercator

```bash
echo 116.391 39.907 | cs2cs EPSG:4326 EPSG:32650   # 北京 → UTM 50N
echo 116.391 39.907 | cs2cs EPSG:4326 EPSG:3857    # → Web Mercator
```

### 模式 2：CGCS2000 中国坐标系操作

```bash
# 查询 CGCS2000 地理坐标系
projinfo EPSG:4490

# 查询 3 度带高斯-克吕格投影（114E 中央经线，即 38 带）
projinfo EPSG:4547

# WGS 84 经纬度 → CGCS2000 3 度带投影
echo 114.0 30.5 | cs2cs EPSG:4326 EPSG:4547
```

### 模式 3：查找并确认转换路径

```bash
# 先列出可用转换与精度
projinfo -s EPSG:4326 -t EPSG:4547 --summary

# 再用 cs2cs 执行，必要时强制使用最佳转换
echo 114.0 30.5 | cs2cs EPSG:4326 EPSG:4547 --only-best
```

### 模式 4：批量转换坐标文本

```bash
#!/bin/bash
# 输入文件每行 "lon lat"，批量转为目标 CRS
while read -r lon lat; do
  echo "$lat $lon" | cs2cs EPSG:4326 EPSG:3857
done < points.txt > points_3857.txt
```

### 模式 5：为缺失网格下载数据

```bash
# 按目标区域下载转换网格后执行高精度转换
projsync --bbox 73,18,135,54
export PROJ_NETWORK=ON
echo 116.391 39.907 | cs2cs EPSG:4326 EPSG:4547 --only-best
```

---

## 最佳实践

- **优先使用权威代码而非 proj 字符串**：`EPSG:4326` 等代码由 `proj.db` 完整描述基准面与轴序，proj 字符串会丢失精度信息（如 `+datum=` 的隐含假设）。
- **注意轴序**：`AUTHORITY:CODE` 或 WKT 会强制其定义轴序，`EPSG:4326` 为纬度在前；`proj` 命令内部期望经度在前，需用 `-r` 调整。
- **转换前先验证**：用 `projinfo <code>` 确认 CRS 名称与轴序，用 `projinfo -s A -t B` 确认转换路径与精度。
- **显式指定 `PROJ_DATA`**：多套 PROJ 共存时（如系统、conda、PostGIS 自带），指向错误目录会报 `proj.db` 版本不匹配。
- **高精度转换需网格**：涉及基准面平移的转换依赖网格文件，用 `projsync` 预取或设 `PROJ_NETWORK=ON`，并用 `--only-best` 避免静默降级。
- **区分 PROJ 与 GDAL**：重投影栅格/矢量文件用 GDAL（`gdalwarp`/`ogr2ogr`），纯坐标点转换用 `cs2cs`；两者共享 `PROJ_DATA`。

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `Cannot find proj.db` | 检查 `PROJ_DATA`（PROJ 9.1 前为 `PROJ_LIB`）是否指向含 `proj.db` 的目录，用 `projinfo --searchpaths` 查看搜索路径 |
| `DATABASE.LAYOUT.VERSION` 不匹配 | 多个 PROJ 副本（系统 / conda / PostGIS）混用，统一 `PROJ_DATA` 指向与所用库版本一致的 `proj.db` |
| `The EPSG code is unknown` | 该代码不在本地 `proj.db`，升级 PROJ 或改用等效 WKT/PROJJSON；可先 `projinfo --list-crs` 确认是否存在 |
| `cs2cs` 输出与预期轴序相反 | `EPSG:4326` 等按定义轴序（纬度在前），用 `-r` 反转输入或 `-s` 反转输出 |
| 转换精度不足或结果偏差大 | 缺少高精度网格导致退回近似转换，用 `projsync` 下载网格、设 `PROJ_NETWORK=ON`，并加 `--only-best` 校验 |
| `proj` 报参数错误或进入交互无输出 | `proj` 需投影参数（如 `+proj=...`）或投影 CRS；直接运行会进入交互模式，请用管道或文件输入 |
| 查询 CRS 输出过多难以解析 | 加 `-q` 只输出字符串本体，或 `-o PROJJSON -q` 获取结构化结果，配合 `jq` 解析 |
| 命令找不到 / 版本过旧 | 用 `projinfo --version` 核对版本，安装 `proj-bin`、conda-forge `proj` 或使用 `osgeo/proj` 镜像 |

---

## 参考资源

- **官方文档：** <https://proj.org/> | [命令行工具](https://proj.org/en/stable/apps/index.html) | [快速上手](https://proj.org/en/stable/usage/quickstart.html) | [资源文件与 proj.db](https://proj.org/en/stable/resource_files.html)
- **工具手册：** [projinfo](https://proj.org/en/stable/apps/projinfo.html) | [cs2cs](https://proj.org/en/stable/apps/cs2cs.html) | [proj](https://proj.org/en/stable/apps/proj.html) | [projsync](https://proj.org/en/stable/apps/projsync.html)
- **转换原理：** <https://proj.org/en/stable/operations/operations_computation.html>
- **EPSG 代码查询：** <https://epsg.io/>
- **源码仓库：** <https://github.com/OSGeo/PROJ>

---

## 相关技能

- **gdal** — 栅格/矢量数据命令行处理，内部使用 PROJ 做坐标转换：[../gdal/SKILL.md](../gdal/SKILL.md)
- **gdal-api** — GDAL 编程 API（C/C++/Python/.NET）：[../gdal-api/SKILL.md](../gdal-api/SKILL.md)
- **postgis** — PostgreSQL 空间数据库，`ST_Transform` 依赖 PROJ 数据：[../postgis/SKILL.md](../postgis/SKILL.md)
- **pyqgis** — QGIS Python 二次开发，坐标系处理底层为 PROJ：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)

---

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("proj")` 加载（用户也可输入 `/proj`）；本技能没有 reference 子目录，正文即全部内容，更细的参数用 `projinfo --help`、`cs2cs --help`、`projinfo --list-crs` 现场查；技能目录只读，脚本与结果写到会话工作区。
- **执行环境**：命令交给 dsh 的 shell 工具（Windows 用 `pwsh`；仅暴露 `run_code` 的会话在 `tools.pwsh` 中执行）。正文的 `export PROJ_DATA=...` 在 PowerShell 写作 `$env:PROJ_DATA = "C:\OSGeo4W\share\proj"`；heredoc（`<<EOF`）在 pwsh 不可用，改用管道 `"56 12" | cs2cs EPSG:4326 EPSG:25832` 或先把输入写成文件再重定向。
- **先探测版本**：`projinfo --version`（同时打印 `proj.db` 路径）、`projinfo --searchpaths`；本技能按 PROJ 9.9.0 编写，低于 9.1 用 `PROJ_LIB` 而非 `PROJ_DATA`，低于 9.3 的 `proj` 不能直接接受 `EPSG:xxxx`。
- **验证转换**：用已知点对拍——`echo "116.391 39.907" | cs2cs EPSG:4326 EPSG:32650` 应得到东坐标约 45 万、北坐标约 442 万，量级不对通常是轴序或单位问题；结构化核对用 `projinfo -o PROJJSON -q EPSG:4326`，转换路径用 `projinfo -s A -t B --summary` 看候选操作与精度。
- **轴序与降级**：`EPSG:4326` 纬度在前（输入先 lat 后 lon），`proj` 命令内部经度在前要用 `-r`；高精度转换加 `--only-best`，否则缺网格时会静默退回精度更低的操作。
- **大输出处理**：`projinfo EPSG:4326` 的 WKT 有上百行，重定向到文件再分段 `read`；批量转换把 `cs2cs EPSG:4326 EPSG:3857 points.txt` 一次跑完，不要逐行起进程。
- **安全与权限**：`projsync --all` 会从 CDN 下载数 GB 网格、`PROJ_NETWORK=ON` 也会联网，先确认网络与磁盘；`sqlite3 proj.db` 只做只读查询，不要写库；改 `PROJ_DATA` 会影响同机 GDAL/PostGIS，先征得用户同意。
