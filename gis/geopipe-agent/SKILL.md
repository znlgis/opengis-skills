---
name: geopipe-agent
description: "Use when building YAML GIS pipelines with GeoPipeAgent — geopipe-agent validate/run, io.read_vector → vector.buffer → io.write_vector chains, 33 built-in steps, qc.geometry_validity/attribute_completeness/topology, native_python|qgis_process|gdal_cli backends, $step.output refs; also for validate \"not registered\" errors, silent when-condition skips, and resolve/knowledge capability gaps. 0.1.0, source install only (not on PyPI)."
tags:
  - gis
  - agent
  - pipeline
  - yaml
  - qc
  - spatial-analysis
  - vector
  - raster
  - geoprocessing
  - python
---

> **项目地址：** <https://github.com/znlgis/GeoPipeAgent>
>
> **最新版本：** 0.1.0（截至2026-10，源码 `pyproject.toml`；发布包名 `geopipe-agent` 尚未上传 PyPI，需从源码安装）
>
> **许可证：** MIT

## 概述

GeoPipeAgent 是一个 **AI 原生的 GIS 分析流水线引擎**。核心理念是：你（AI）生成 YAML 管道配置，框架负责执行并返回结构化结果。

**核心能力：**

- **声明式流水线**：YAML 定义分析步骤，AI 友好
- **丰富步骤库**：33 个内置步骤，覆盖矢量分析、栅格分析、网络分析、空间聚类、数据质检
- **多后端支持**：7 种后端可切换（native_python / gdal_cli / gdal_python / qgis_process / pyqgis / generic_cli / curl_api），按环境自动检测可用性
- **质检框架**：10 种 QC 检查，支持错误/警告/信息三级
- **结构化报告**：JSON 输出，含统计信息和 QC 汇总
- **步骤引用**：`$step_id.output` 语法实现步骤间数据传递

---

## 快速开始

### 安装

```bash
git clone https://github.com/znlgis/GeoPipeAgent.git
cd GeoPipeAgent
pip install -e ".[analysis,network]"   # 按需启用分析/网络分析可选依赖
```

### 基本用法

```bash
# 列出所有可用步骤（可按类别过滤）
geopipe-agent list-steps --category qc

# 查看步骤详情
geopipe-agent describe vector.buffer

# 校验 YAML 流水线（不执行）
geopipe-agent validate pipeline.yaml

# 执行流水线
geopipe-agent run pipeline.yaml

# 查看可用后端
geopipe-agent backends

# 查看 GIS 数据文件摘要
geopipe-agent info data/roads.shp

# 覆盖流水线变量 / 输出 JSON 步骤清单 / 生成 AI 技能包
geopipe-agent run pipeline.yaml --var input_path=roads.shp
geopipe-agent list-steps --format json
geopipe-agent generate-skill --output-dir skills/geopipe-agent

# 能力缺口：查候选能力与回退路径（自我扩展闭环入口）
geopipe-agent resolve "把 Shapefile 落库到 PostGIS"
geopipe-agent knowledge search "坐标转换" --tags crs
```

### 最小示例

```yaml
pipeline:
  name: "快速缓冲区"
  steps:
    - id: read
      use: io.read_vector
      params:
        path: "data/roads.shp"
    - id: buffer
      use: vector.buffer
      params:
        input: "$read"
        distance: 500
    - id: save
      use: io.write_vector
      params:
        input: "$buffer"
        path: "output/result.geojson"
  outputs:
    result: "$save"
```

---

## 核心概念

### 步骤引用语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `$step_id` | 等同于 `$step_id.output` | `$buffer` |
| `$step_id.output` | 引用步骤输出 | `$buffer.output` |
| `$step_id.stats` | 引用步骤统计信息 | `$buffer.stats` |
| `$step_id.issues` | 引用 QC 步骤问题列表 | `$check.issues` |
| `$step_id.issues_count` | QC 问题数量 | `$check.issues_count` |
| `${var_name}` | 变量替换 | `${input_path}` |

### 条件执行 (`when`)

```yaml
- id: fix-geometries
  use: qc.geometry_validity
  params:
    input: "$data"
    auto_fix: true
  when: "$check.issues_count > 0"
```

支持比较运算符（`==`, `!=`, `>`, `<`, `>=`, `<=`）、布尔运算符（`and`, `or`, `not`）。

> 注意：上例中的 `$data` 与 `$check` 必须由**更早定义的步骤**提供；`when` 引用了不存在的步骤属性时，条件会按 false 处理，条件步骤会静默不执行。

### 错误处理 (`on_error`)

| 值 | 行为 |
|----|------|
| `fail`（默认） | 停止管道执行 |
| `skip` | 跳过当前步骤，继续下一步 |
| `retry` | 重试最多 3 次，延迟 0.5s → 1.0s（线性递增，非指数退避） |

---

## 能力缺口与自我扩展

需要的能力尚未实现时（`validate` 报 `not registered`）不要猜参数，按 **探测 → 检索 → 取得能力 → 验证 → 沉淀** 五步走：

| 阶段 | 命令 |
|------|------|
| 探测 | `geopipe-agent resolve "<需求或步骤 ID>"` |
| 检索 | `geopipe-agent knowledge search "<关键词>"`、`geopipe-agent knowledge show <技能>` |
| 取得能力 | 零代码：`gdal.cli` / `qgis.algorithm` / `http.request` 直通步骤；生成代码：`geopipe-agent scaffold step <id> --capability <key>` |
| 验证 | `geopipe-agent validate <pipeline.yaml>` + `geopipe-agent run <pipeline.yaml>` |
| 沉淀 | 登记 `knowledge/capabilities.yaml` 与 `knowledge/recipes/<key>.md` |

完整说明、示例与安全边界：[reference/self-extension.md](reference/self-extension.md)

---

## 步骤分类

### IO 步骤（io.*）

| 步骤 | 说明 | 关键参数 |
|------|------|---------|
| `io.read_vector` | 读取矢量数据（SHP/GeoJSON/GPKG） | `path`, `layer`, `encoding` |
| `io.read_raster` | 读取栅格数据（GeoTIFF 等） | `path` |
| `io.write_vector` | 写入矢量数据 | `input`, `path`, `format`, `encoding` |
| `io.write_raster` | 写入栅格数据 | `input`, `path` |

### 矢量分析步骤（vector.*）

| 步骤 | 说明 | 关键参数 | 后端 |
|------|------|---------|------|
| `vector.buffer` | 缓冲区分析 | `input`, `distance`, `cap_style` | native_python, qgis_process |
| `vector.clip` | 矢量裁剪 | `input`, `clip_geometry` | native_python, qgis_process |
| `vector.reproject` | 投影转换 | `input`, `target_crs` | native_python, qgis_process |
| `vector.dissolve` | 按字段融合 | `input`, `by`, `aggfunc` | native_python |
| `vector.overlay` | 叠加分析 | `input`, `overlay_layer`, `how` | native_python |
| `vector.query` | 属性查询 | `input`, `expression` | — |
| `vector.simplify` | 几何简化 | `input`, `tolerance`, `preserve_topology` | native_python |

**叠加方式** (`vector.overlay` 的 `how` 参数)：`intersection`、`union`、`difference`、`symmetric_difference`、`identity`

### 栅格分析步骤（raster.*）

| 步骤 | 说明 | 关键参数 |
|------|------|---------|
| `raster.reproject` | 栅格投影转换 | `input`, `target_crs`, `resampling` |
| `raster.clip` | 栅格裁剪 | `input`, `mask`, `crop`, `nodata` |
| `raster.calc` | 栅格波段计算 | `input`, `expression`（如 `'(B4-B3)/(B4+B3)'`） |
| `raster.contour` | 等值线提取 | `input`, `interval`, `band`, `base` |
| `raster.stats` | 栅格统计 | `input`, `band` |

**重采样方法** (`raster.reproject` 的 `resampling`)：`nearest`、`bilinear`、`cubic`、`lanczos`

### 高级分析步骤（analysis.*）

| 步骤 | 说明 | 关键参数 |
|------|------|---------|
| `analysis.voronoi` | 泰森多边形 | `input`, `envelope` |
| `analysis.heatmap` | 热力图（KDE） | `input`, `resolution`, `bandwidth` |
| `analysis.interpolate` | 空间插值 | `input`, `value_field`, `method`, `resolution` |
| `analysis.cluster` | 空间聚类 | `input`, `method`（dbscan/kmeans）, `eps`, `n_clusters` |

**插值方法** (`analysis.interpolate` 的 `method`)：`linear`、`nearest`、`cubic`、`idw`

### 网络分析步骤（network.*）

| 步骤 | 说明 | 关键参数 |
|------|------|---------|
| `network.shortest_path` | 最短路径 | `input`, `origin`, `destination`, `weight` |
| `network.service_area` | 服务区分析 | `input`, `center`, `cost_limit`, `weight` |
| `network.geocode` | 地理编码 | `addresses`, `provider`, `user_agent` |

### 质检步骤（qc.*）

QC 步骤遵循 **「检查即透传」** 模式：输入数据原样通过为 `output`，问题单独收集在 `$step.issues` 和 `$step.issues_gdf` 中。

| 步骤 | 检查内容 | 关键参数 |
|------|---------|---------|
| `qc.geometry_validity` | 几何有效性（自相交、空几何等） | `input`, `auto_fix`, `severity` |
| `qc.topology` | 拓扑关系（重叠、缝隙、悬挂线） | `input`, `rules`, `tolerance`, `severity` |
| `qc.attribute_completeness` | 必填字段完整性 | `input`, `required_fields`, `allow_empty`, `severity` |
| `qc.attribute_domain` | 属性值域合规性 | `input`, `field`, `allowed_values`, `pattern`, `severity` |
| `qc.value_range` | 数值字段范围 | `input`, `field`, `min`, `max`, `severity` |
| `qc.duplicate_check` | 重复要素检测 | `input`, `check_geometry`, `check_fields`, `tolerance`, `severity` |
| `qc.crs_check` | 坐标参考系验证 | `input`, `expected_crs`, `severity` |
| `qc.raster_nodata` | NoData 一致性 | `input`, `expected_nodata`, `max_nodata_ratio`, `severity` |
| `qc.raster_value_range` | 栅格值域检查 | `input`, `min`, `max`, `band`, `severity` |
| `qc.raster_resolution` | 分辨率一致性 | `input`, `expected_x`, `expected_y`, `tolerance`, `severity` |

**严重级别** (`severity`)：`error`、`warning`、`info`

**拓扑规则** (`qc.topology` 的 `rules`)：`no_overlaps`、`no_gaps`、`no_dangles`

---

## 典型工作流

五个可直接套用的工作流（完整 YAML 见 [reference/workflows.md](reference/workflows.md)）：

| 工作流 | 步骤链 |
|--------|--------|
| 数据质检 + 修复 | `io.read_vector → qc.geometry_validity → （when 命中才修复）→ qc.attribute_completeness → io.write_vector` |
| 缓冲区 + 叠加分析 | `io.read_vector ×2 → vector.buffer → vector.overlay(intersection) → io.write_vector` |
| DEM 分析 + 等值线 | `io.read_raster → qc.raster_nodata → qc.raster_resolution → raster.contour → io.write_vector` |
| 网络分析 | `io.read_vector → network.shortest_path → network.service_area → io.write_vector ×2` |
| 空间聚类 + 热力图 | `io.read_vector → analysis.cluster(dbscan) → analysis.heatmap → io.write_vector + io.write_raster` |

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("geopipe-agent")` 加载（用户也可输入 `/geopipe-agent`）；`reference/steps-reference.md`、`pipeline-schema.md`、`workflows.md`、`self-extension.md` 按需 `read`，路径相对加载结果中的 Base directory；技能目录只读，YAML 与输出写到会话工作区。
- **执行环境**：命令交给 dsh 的 shell 工具（Windows 用 `pwsh`）；`python` 可能指向 QGIS/GDAL 自带解释器，建议在工作区建独立 venv 后 `pip install -e .`，避免污染系统环境。
- **源码安装（未上 PyPI）**：`git clone https://github.com/znlgis/GeoPipeAgent.git && pip install -e ".[analysis,network]"`；验证 `geopipe-agent --help`、`geopipe-agent list-steps --category qc`、`pip show geopipe-agent | Select-String Version`。不要写 `pip install geopipe-agent`——PyPI 上还没有这个包。
- **先探测能力**：`geopipe-agent backends` 看当前环境可用后端（默认 `native_python`），`geopipe-agent list-steps --format json` 拿真实步骤 ID；`validate` 报 `not registered` 时先用 `geopipe-agent resolve "<需求>"` 与 `knowledge search`，不要猜参数。
- **验证产物**：`geopipe-agent validate pipeline.yaml` 通过后再 `run pipeline.yaml`，检查 JSON 报告里的 `qc_summary` 与各步骤统计，随后重开输出文件核对（`geopipe-agent info output/result.geojson`，装了 GDAL 时也可 `ogrinfo -so output/result.geojson result`），确认要素数与 CRS 而不是只看“执行成功”。
- **典型误操**：步骤 ID 不能含点号，`$step_id` 必须由更早步骤提供，`when` 引用不存在的属性会按 false **静默跳过**；`backend:` 只有声明了 backends 的 6 个矢量步骤会读取，其余步骤写了也被忽略。
- **性能与内存**：管道全程在内存中运行，超大栅格先 `raster.clip` 或 `io.read_raster` 只读所需波段；QC 步骤是“检查即透传”，`output` 就是输入，问题在 `$step.issues` / `issues_gdf`。
- **安全与权限**：`network.geocode` 与 `curl_api`、`http.request` 会把数据发到外部服务，执行前确认是否允许出网并检查 `user_agent`/凭据；`pip install`、覆盖已有输出文件、批量改写数据前先征得用户同意。

---

## 与其它工具对比

| 工具 | 适用场景 | GeoPipeAgent 优势 |
|------|---------|------------------|
| GDAL CLI | 手动命令行操作 | AI 可编程，结构化输出 |
| qgis_process | 复杂空间分析 | 多步流水线编排，条件执行 |
| PyQGIS 脚本 | Python 编程 | 声明式配置，无需写 Python |
| Python 脚本 | 自定义分析 | 模板化，AI 直接生成配置 |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 步骤引用解析失败 | 检查步骤 ID 是否含点号，引用目标是否在当前步骤之前定义 |
| 管线执行超时 | 对大范围栅格先裁剪，减少数据量 |
| QC 步骤无输出 | QC 步骤透传输入数据，问题在 `$step.issues` 中，`output` 即输入 |
| 条件步骤未触发 | 检查 `when` 表达式语法，确保引用的 `$step.attr` 存在 |
| 后端不兼容 | `native_python` 和 `qgis_process` 后端参数可能不同，查阅 `list-steps` 确认 |

---

## 相关技能

- **gdal** — 命令行数据处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **qgis-process** — QGIS 命令行处理工具：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **pyqgis** — QGIS Python 绑定：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **geopandas** — Python 矢量数据处理：[../geopandas/SKILL.md](../geopandas/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)
- **opengis-daf** — .NET 方案驱动的分析/质检框架（同类流水线工具）：[../opengis-daf/SKILL.md](../opengis-daf/SKILL.md)

## 参考资源

- 步骤参考：[reference/steps-reference.md](reference/steps-reference.md)
- 管道 Schema：[reference/pipeline-schema.md](reference/pipeline-schema.md)
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/GeoPipeAgent/>
