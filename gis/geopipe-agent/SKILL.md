---
name: geopipe-agent
description: GeoPipeAgent 是 AI 原生的 GIS 数据分析流水线框架，支持通过 YAML 声明式定义 GIS 分析流程（数据读取、矢量/栅格分析、网络分析、空间聚类、数据质检），由 AI 生成管道配置后自动执行并返回结构化 JSON 报告。
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

> **项目地址：** <https://github.com/znlgis/geopipe-agent>
>
> **许可证：** MIT

## 概述

GeoPipeAgent 是一个 **AI 原生的 GIS 分析流水线引擎**。核心理念是：你（AI）生成 YAML 管道配置，框架负责执行并返回结构化结果。

**核心能力：**

- **声明式流水线**：YAML 定义分析步骤，AI 友好
- **丰富步骤库**：矢量分析、栅格分析、网络分析、空间聚类、数据质检
- **多后端支持**：native_python（基于 geopandas/shapely/rasterio）和 qgis_process
- **质检框架**：10 种 QC 检查，支持错误/警告/信息三级
- **结构化报告**：JSON 输出，含统计信息和 QC 汇总
- **步骤引用**：`$step_id.output` 语法实现步骤间数据传递

---

## 快速开始

### 安装

```bash
pip install geopipe-agent
```

### 基本用法

```bash
# 生成管道模板
geopipe-agent template buffer > pipeline.yaml

# 编辑管道配置后执行
geopipe-agent run pipeline.yaml

# 列出所有可用步骤
geopipe-agent list-steps

# 查看步骤帮助
geopipe-agent help-step vector.buffer
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

### 错误处理 (`on_error`)

| 值 | 行为 |
|----|------|
| `fail`（默认） | 停止管道执行 |
| `skip` | 跳过当前步骤，继续下一步 |
| `retry` | 重试最多 3 次（带退避） |

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

### 工作流 1：数据质检 + 修复流水线

```yaml
pipeline:
  name: "数据质检修复"
  steps:
    - id: read
      use: io.read_vector
      params:
        path: "data/buildings.shp"

    # 第一步：检查几何有效性
    - id: check_valid
      use: qc.geometry_validity
      params:
        input: "$read"
        severity: error

    # 第二步：条件修复（仅当发现问题时执行）
    - id: fix_valid
      use: qc.geometry_validity
      params:
        input: "$check_valid"
        auto_fix: true
      when: "$check_valid.issues_count > 0"

    # 第三步：属性完整性检查
    - id: check_attr
      use: qc.attribute_completeness
      params:
        input: "$fix_valid"
        required_fields: ["name", "height", "type"]
        severity: warning

    # 第四步：写入结果
    - id: save
      use: io.write_vector
      params:
        input: "$check_attr"
        path: "output/buildings_checked.gpkg"
        format: GPKG

  outputs:
    result: "$save"
    issues: "$check_attr.issues"
```

### 工作流 2：缓冲区 + 叠加分析

```yaml
pipeline:
  name: "道路影响范围分析"
  steps:
    - id: roads
      use: io.read_vector
      params:
        path: "data/roads.shp"
    - id: parcels
      use: io.read_vector
      params:
        path: "data/parcels.shp"

    # 500 米道路缓冲区
    - id: buffer
      use: vector.buffer
      params:
        input: "$roads"
        distance: 500

    # 缓冲区与地块求交集
    - id: overlay
      use: vector.overlay
      params:
        input: "$parcels"
        overlay_layer: "$buffer"
        how: intersection

    - id: save
      use: io.write_vector
      params:
        input: "$overlay"
        path: "output/affected_parcels.geojson"

  outputs:
    result: "$save"
```

### 工作流 3：DEM 分析 + 等值线

```yaml
pipeline:
  name: "DEM 地形分析"
  steps:
    - id: read_dem
      use: io.read_raster
      params:
        path: "data/dem.tif"

    # 栅格 QC：检查 NoData 和分辨率
    - id: check_nodata
      use: qc.raster_nodata
      params:
        input: "$read_dem"
        max_nodata_ratio: 0.1

    - id: check_resolution
      use: qc.raster_resolution
      params:
        input: "$check_nodata"
        expected_x: 30
        expected_y: 30

    # 生成等高线（50 米间距）
    - id: contour
      use: raster.contour
      params:
        input: "$check_resolution"
        interval: 50

    # 输出矢量等值线
    - id: save_contour
      use: io.write_vector
      params:
        input: "$contour"
        path: "output/contours_50m.gpkg"
        format: GPKG

  outputs:
    contour: "$save_contour"
```

### 工作流 4：网络分析

```yaml
pipeline:
  name: "紧急响应路径分析"
  steps:
    - id: roads
      use: io.read_vector
      params:
        path: "data/road_network.shp"

    # 最短路径
    - id: route
      use: network.shortest_path
      params:
        input: "$roads"
        origin: [116.3, 39.9]
        destination: [116.5, 40.0]

    # 服务区（5000 米）
    - id: service
      use: network.service_area
      params:
        input: "$roads"
        center: [116.4, 39.95]
        cost_limit: 5000

    - id: save_route
      use: io.write_vector
      params:
        input: "$route"
        path: "output/route.geojson"

    - id: save_service
      use: io.write_vector
      params:
        input: "$service"
        path: "output/service_area.geojson"

  outputs:
    route: "$save_route"
    service_area: "$save_service"
```

### 工作流 5：空间聚类 + 热力图

```yaml
pipeline:
  name: "犯罪热点分析"
  steps:
    - id: points
      use: io.read_vector
      params:
        path: "data/crime_points.shp"

    # DBSCAN 聚类
    - id: cluster
      use: analysis.cluster
      params:
        input: "$points"
        method: dbscan
        eps: 0.01
        min_samples: 3

    # 热力图
    - id: heatmap
      use: analysis.heatmap
      params:
        input: "$points"
        resolution: 200

    - id: save_clusters
      use: io.write_vector
      params:
        input: "$cluster"
        path: "output/clusters.geojson"

    - id: save_heatmap
      use: io.write_raster
      params:
        input: "$heatmap"
        path: "output/heatmap.tif"

  outputs:
    clusters: "$save_clusters"
    heatmap: "$save_heatmap"
```

---

## AI 使用建议

### 推荐工作流

1. **理解需求**：用户要做什么 GIS 分析？
2. **列出可用步骤**：`geopipe-agent list-steps` 或查阅步骤表
3. **编写 YAML**：按 `io.read → analysis → io.write` 模式编排
4. **加入 QC**：在关键步骤前后插入质检步骤
5. **执行**：`geopipe-agent run pipeline.yaml`
6. **解读结果**：检查 JSON 报告中的 `qc_summary` 和统计信息

### 关键注意事项

- **步骤 ID 规则**：只能用小写字母、数字、下划线和连字符，不能含点号（`.` 保留用于属性引用）
- **引用链完整性**：确保每个 `$step_id` 引用的步骤在当前步骤之前定义
- **QC 链式调用**：QC 步骤可串联（`qc.check1 → qc.check2 → qc.check3`），问题汇总到管道报告的 `qc_summary` 中
- **后端选择**：简单分析用 `native_python`（无外部依赖），复杂分析使用 `qgis_process` 后端
- **路径使用绝对路径**：避免工作目录问题
- **大数据注意**：管道在内存中运行，超大栅格建议先裁剪

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

## 参考资源

- 步骤参考：`reference/steps-reference.md`
- 管道 Schema：`reference/pipeline-schema.md`
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/geopipe-agent/>
