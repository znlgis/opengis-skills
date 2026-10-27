---
name: whitebox-tools
description: "Use when doing advanced raster, terrain or LiDAR geoprocessing with WhiteboxTools v2.4.0 — whitebox_tools --run=Slope/FillDepressions/BreachDepressions/FlowAccumulationFullWorkflow/Watershed/ExtractStreams, lidar_* tools for LAS point clouds, or the whitebox (whitebox-python 2.3.6) WhiteboxTools wrapper in Python. Also for 'whitebox_tools: command not found', mismatched Python frontend versions, and missing DEM/flow-accumulation intermediate outputs."
tags:
  - geospatial
  - raster
  - terrain-analysis
  - hydrology
  - lidar
  - dem
  - command-line
  - python
  - rust
  - geoprocessing
---

> **项目地址：** <https://github.com/jblindsay/whitebox-tools>
>
> **官方文档：** 用户手册站 <https://www.whiteboxgeo.com/manual/wbt_book/preface.html>（2026-10 实测返回 404，暂以仓库 README 与 `UserManual.txt` 为可访问入口）
>
> **最新版本：** 2.4.0（GitHub Release，截至 2026-10）
>
> **PyPI 前端：** `whitebox` 2.3.6（whitebox-python 封装，仅负责下载与调用二进制，版本号落后于核心库）
>
> **许可证：** MIT
>
> **注意：** 上游仓库 README 已标记为 legacy，新开发转向 <https://github.com/jblindsay/whitebox_next_gen>；但 2.4.0 仍是当前稳定可用的开源版本，本文以其为基准。

## 概述

WhiteboxTools 是圭尔夫大学 GHRG 实验室（John Lindsay）用 Rust 编写的独立地理空间分析引擎，面向「分析后端」而非制图：它不渲染地图，只接收栅格/矢量/LAS 输入并产出分析结果。相比通用 GIS 桌面软件，它的优势在于命令行与脚本化，几百个工具都能通过统一参数形式批量执行，适合 DEM 地形分析、水文建模与 LiDAR 处理流水线。

- **地形分析**：坡度、坡向、曲率、山体阴影、相对高程、地形位置指数（TPI）、多尺度位置分析
- **水文分析**：洼地填充/决口、D8/DInf/FD8 流向与流量累积、河网提取、Strahler 分级、流域划分
- **LiDAR**：点云信息与直方图、按类别过滤、去噪、地面点分类、插值成 DEM、密度与强度栅格
- **栅格与矢量工具**：栅格计算器、重分类、分区统计、矢量栅格互转、要素裁剪与合并
- **统一接口**：`whitebox_tools --run=<ToolName> [参数]`，另有 `--toolhelp`、`--toolparameters` 查询元数据

---

## 环境准备

### 方式一：下载预编译二进制（推荐）

到 <https://github.com/jblindsay/whitebox-tools/releases> 下载对应平台的预编译压缩包，解压后目录内含 `whitebox_tools`（Windows 为 `whitebox_tools.exe`）与 `WBT` 插件目录。

```bash
cd /opt/WBT          # 解压后的 WBT 目录
./whitebox_tools --version
./whitebox_tools --listtools slope | head -5
```

```powershell
# Windows PowerShell
cd C:\Tools\WBT
.\whitebox_tools.exe --version
```

### 方式二：源码编译（适合无预编译包的平台）

需要 Rust 工具链；Windows 上还需 MSVC 或 GNU 链接器。仓库根目录的 `build.py` 会调用 `cargo` 并把产物整理到 `WBT/`。

```bash
git clone https://github.com/jblindsay/whitebox-tools.git
cd whitebox-tools
python build.py
./WBT/whitebox_tools --version
```

### 方式三：Python 前端（`whitebox` 包）

`whitebox-python` 是社区维护的封装，首次运行会下载 / 复用 WBT 二进制；它不提升核心工具版本，因此工具能力以二进制实际版本为准。

```bash
pip install whitebox==2.3.6

# 或 conda
conda install -c conda-forge whitebox
```

```python
import whitebox
print(whitebox.__version__)          # 2.3.6 —— 这是 Python 封装版本

wbt = whitebox.WhiteboxTools()
wbt.set_verbose_mode(False)
print(wbt.version())                 # 打印底层 WhiteboxTools 二进制版本
```

**验证要点**：`--version` 输出的是核心库版本；Python 包版本号与核心库不一致属正常现象，排错时以 `--version` 为准。

---

## 核心命令

### 命令行骨架

```bash
whitebox_tools --wd="data/" --run=Slope --dem=input.tif --output=slope.tif --units=degrees -v
```

| 参数 | 作用 |
|------|------|
| `--wd` / `--cd` | 切换工作目录；与 `--run` 连用，之后的相对路径都基于它 |
| `-r` / `--run` | 指定工具名（CamelCase），如 `Slope`、`FillDepressions` |
| `-v` | 详细模式，打印进度与耗时；`-v=false` 关闭 |
| `--listtools [关键词]` | 列出工具及描述，可按关键词过滤 |
| `--toolhelp=<Tool>` | 打印某工具的使用帮助 |
| `--toolparameters=<Tool>` | 以 JSON 输出参数定义，适合脚本动态组装参数 |
| `--version` | 版本信息 |

**不要凭记忆写参数名**：不同工具的参数差异很大（例如坡度用 `--units`，流量累积工作流用五个 `--out_*` 参数）。写脚本前先 `--toolparameters` 取 JSON，再据此拼参数。

### 常用工具速查

| 工具名 | 作用 | 关键参数 |
|--------|------|----------|
| `Slope` | 坡度栅格 | `--dem`、`--output`、`--units`（degrees/radians/percent）、`--zfactor` |
| `Aspect` | 坡向 | `--dem`、`--output` |
| `Hillshade` | 山体阴影 | `--dem`、`--output`、`--azimuth`、`--altitude`、`--zfactor` |
| `FillDepressions` | 填洼 | `--dem`、`--output`、`--fix_flats`、`--flat_increment` |
| `BreachDepressions` | 洼地决口（保留更多地形细节） | `--dem`、`--output`、`--max_depth`、`--max_length`、`--fill_pits` |
| `D8Pointer` | D8 流向 | `--dem`、`--output`、`--esri_pntr` |
| `D8FlowAccumulation` | D8 流量累积 | `--input`、`--output`、`--out_type` |
| `FlowAccumulationFullWorkflow` | 一键：决口 + 流向 + 累积 | `--dem`、`--out_dem`、`--out_pntr`、`--out_accum`、`--out_type` |
| `ExtractStreams` | 阈值法提取河网 | `--flow_accum`、`--output`、`--threshold` |
| `StrahlerStreamOrder` | 河网 Strahler 分级 | `--streams`、`--d8_pntr`、`--output` |
| `Watershed` | 由流向与倾泻点划分流域 | `--d8_pntr`、`--pour_pts`、`--output` |
| `LidarInfo` | LAS/LAZ 基本信息 | `--input` |
| `LidarPointDensity` | 点密度栅格 | `--input`、`--output`、`--cell_size` |
| `LidarHillshade` | 点云生成山体阴影 | `--input`、`--output`、`--azimuth`、`--altitude` |
| `Mosaic` | 多栅格拼接 | `--inputs`、`--output` |
| `Clip` | 按矢量范围裁剪栅格 | `--input`、`--clip`、`--output` |

完整列表用 `whitebox_tools --listtools`；以下为常用子集，参数以 `--toolparameters` 输出为准。

### Python 调用

```python
from whitebox import WhiteboxTools

wbt = WhiteboxTools()
wbt.set_working_dir("data")
wbt.set_verbose_mode(False)

# 方法名是工具名的 snake_case 形式，参数名与 CLI 的路由一致
wbt.slope(dem="dem.tif", output="slope.tif", units="degrees")
wbt.hillshade(dem="dem.tif", output="hillshade.tif", azimuth=315.0, altitude=30.0)

# 任何工具都能用 run_tool 统一调用
wbt.run_tool("FillDepressions", ["--dem=dem.tif", "--output=dem_filled.tif", "--fix_flats=true"])
```

`run_tool(tool_name, args)` 的 `args` 是 `--flag=value` 字符串列表，适合官方封装尚未覆盖的新工具；两种方式可混用。

---

## 典型工作流

从原始 DEM 到河网与流域的完整水文分析：

**输入**：`data/dem.tif`（投影坐标系 DEM，水平与垂直单位一致）
**输出**：`watershed.tif`、`streams.tif`、`accum.tif`

1. 先检查 DEM 是否有异常值与坐标系单位
2. 用 `FlowAccumulationFullWorkflow` 一次完成决口、流向与流量累积，避免中间文件散落
3. 用流量累积的阈值提取河网
4. 按倾泻点划分流域（倾泻点可先用 `SnapPourPoints` 吸附到河网）
5. 如需河网矢量，用 `RasterStreamsToVector`

```bash
cd /opt/WBT

# 1) 决口 + D8 流向 + 流量累积
./whitebox_tools --wd="D:/work/hydro" --run=FlowAccumulationFullWorkflow \
  --dem=dem.tif --out_dem=dem_breached.tif \
  --out_pntr=flow_pntr.tif --out_accum=accum.tif --out_type=cells -v

# 2) 阈值提取河网（阈值随分辨率与气候区调整，先看累积值分布）
./whitebox_tools --wd="D:/work/hydro" --run=ExtractStreams \
  --flow_accum=accum.tif --output=streams.tif --threshold=1000 -v

# 3) 倾泻点吸附后划分流域
./whitebox_tools --wd="D:/work/hydro" --run=SnapPourPoints \
  --pour_pts=pour_pts.shp --flow_accum=accum.tif --snap_dist=3 --output=pour_pts_snapped.shp -v
./whitebox_tools --wd="D:/work/hydro" --run=Watershed \
  --d8_pntr=flow_pntr.tif --pour_pts=pour_pts_snapped.shp --output=watershed.tif -v

# 4) 河网转矢量（可选）
./whitebox_tools --wd="D:/work/hydro" --run=RasterStreamsToVector \
  --streams=streams.tif --d8_pntr=flow_pntr.tif --output=streams.shp -v
```

Python 等价写法：

```python
from whitebox import WhiteboxTools

wbt = WhiteboxTools()
wbt.set_working_dir("D:/work/hydro")

wbt.flow_accumulation_full_workflow(
    dem="dem.tif",
    out_dem="dem_breached.tif",
    out_pntr="flow_pntr.tif",
    out_accum="accum.tif",
    out_type="cells",
)
wbt.extract_streams(flow_accum="accum.tif", output="streams.tif", threshold=1000)
wbt.watershed(d8_pntr="flow_pntr.tif", pour_pts="pour_pts_snapped.shp", output="watershed.tif")
```

**检查点**：`accum.tif` 的极值应与流域面积量级相符；若所有像元值都是 1，通常是 DEM 单位不一致或流向计算被平坦区阻断。

---

## 最佳实践

1. **统一单位与坐标系**：DEM 用投影坐标系，水平/垂直单位不同时显式传 `--zfactor`，否则坡度与累积结果会有系统性偏差
2. **决口优先于填洼**：`BreachDepressions` 保留更多真实地形细节，平坦区多时才回退 `FillDepressions`
3. **阈值要试算**：`ExtractStreams` 的 `--threshold` 与分辨率强相关，先统计累积栅格分布，再取值对比
4. **用 `--toolparameters` 驱动脚本**：自动化流水线里先取 JSON 参数定义，避免版本升级后参数改名导致静默失败
5. **中间文件显式命名**：把 `dem_breached`、`flow_pntr`、`accum` 分开存，便于复算与排错
6. **LiDAR 先探测再处理**：`LidarInfo` 确认点数、范围与坐标系，再做分类与插值；大文件先 `LidarTile` 分块
7. **批量任务按 CPU 数并行**：多个独立工具调用可并行，同一 DEM 的上下游步骤必须串行

---

## 常见问题

| 问题 | 原因与解决 |
|------|------------|
| `whitebox_tools: command not found` | 二进制目录未加入 PATH：`cd` 到 WBT 目录执行，或把该目录加进 PATH；Windows 注意加 `.exe` |
| 运行后没有任何输出文件，也没有报错 | 相对路径基于 `--wd`：确认 `--wd` 指向数据目录，或全部改用绝对路径 |
| `--run` 后提示工具不存在 | 工具名必须是 CamelCase（如 `FillDepressions`）；用 `--listtools` 确认真实名称 |
| 参数名报错或参数被忽略 | 参数名随工具而异：用 `--toolparameters=<Tool>` 取 JSON 定义，不要照抄别的工具的参数 |
| Python 里 `wbt.version()` 与 pip 版本不一致 | 正常现象：pip 版本是 Python 封装版本，二进制版本由下载器决定；能力差异以二进制为准 |
| 水系的流量累积结果异常（全为 1 或极大值） | DEM 未决口/填洼，或单位不一致；先跑 `BreachDepressions` 并检查 `--zfactor` |
| 平坦区出现大片无流向像元 | 填洼时未处理平坦区：`FillDepressions` 打开 `--fix_flats=true`，或改用 `BreachDepressions` |
| LiDAR 工具报格式不支持 | 输入需为 LAS/LAZ；若为其他点云格式，先用 PDAL 转换 |
| 处理大 DEM 时内存占用过高 | 先 `Clip` 到研究区，或分块处理后再 `Mosaic` 合并 |

---

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("whitebox-tools")` 加载（也可输入 `/whitebox-tools`）；脚本与数据写到会话工作区，技能目录只读。
- **执行环境**：`python build.py` 编译耗时可达数分钟，放后台任务；`pip install whitebox` 首次调用会联网下载二进制，离线环境需先手动放置 WBT。
- **先探测版本**：`whitebox_tools --version` 确认核心版本（本文基准 2.4.0）；`python -c "import whitebox; print(whitebox.__version__)"` 确认前端（2.3.6）。两者不一致时以二进制为准并明确告知用户。
- **验证产物**：用 `ls -l` 检查输出文件是否生成，再用 GDAL（`gdalinfo` / `python -c "import rasterio..."`）读取数值范围做断言；只看命令退出码不足以证明分析正确。
- **失败信号**：无输出且无报错几乎都是工作目录或路径问题；参数被忽略多为参数名拼错，用 `--toolparameters` 核对。
- **常见症状**：累积值异常先查决口与单位；平坦区无流向查 `--fix_flats`；LiDAR 报错先查 LAS/LAZ 格式。
- **安全与权限**：编译、安装、下载二进制前先征得用户同意；批量处理前确认磁盘占用。

## 相关技能

- **gdal** — 栅格/矢量格式转换与重投影，常作为 WBT 前后处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **pdal** — LiDAR 点云格式转换与滤波，与 WBT 的 LiDAR 工具互补：[../pdal/SKILL.md](../pdal/SKILL.md)
- **grass-gis** — 另一套水文与地形分析工具链，可交叉验证结果：[../grass-gis/SKILL.md](../grass-gis/SKILL.md)
- **qgis-process** — 通过 qgis_process 调用 QGIS 原生算法，做流程编排与出图：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **proj** — 坐标系定义与转换，处理 DEM CRS 时常用：[../proj/SKILL.md](../proj/SKILL.md)

## 参考资源

- 用户手册（上游 README 标注的地址，2026-10 实测 404）：<https://www.whiteboxgeo.com/manual/wbt_book/preface.html>
- 可访问的用法说明：仓库 README 与 `UserManual.txt` <https://github.com/jblindsay/whitebox-tools>
- 源码与 Issue：<https://github.com/jblindsay/whitebox-tools>
- 后继项目：<https://github.com/jblindsay/whitebox_next_gen>
- Python 封装：<https://github.com/opengeos/whitebox-python>
- 预编译二进制：<https://github.com/jblindsay/whitebox-tools/releases>
