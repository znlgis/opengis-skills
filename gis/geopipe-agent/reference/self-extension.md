# 能力缺口与自我扩展（完整说明）

当流水线需要的能力尚未实现时（`validate` 会直接报 `not registered`），不要猜测参数——按下面五步获得能力：

| 步骤 | 命令 | 作用 |
|------|------|------|
| 1 探测 | `geopipe-agent resolve "<需求或步骤 ID>"` | 返回候选能力（kind/status/可用性/依赖）、回退路径与落地建议 |
| 2 检索 | `geopipe-agent knowledge search "<关键词>" [--tags crs]`、`knowledge show <技能> [--section 概述]` | 离线按需加载内置 GIS 知识（11 个上游技能语料） |
| 3 取得能力 | 零代码：`gdal.cli` / `qgis.algorithm` / `http.request` 直通步骤；生成代码：`geopipe-agent scaffold step <category.action> --capability <key>` | 直通步骤以白名单可执行 + 参数列表立即获得新能力；scaffold 默认 dry-run，`--allow-author` 才写盘 |
| 4 验证 | `geopipe-agent validate <pipeline.yaml>` + `geopipe-agent run <pipeline.yaml>` | 校验并执行 |
| 5 沉淀 | 登记 `knowledge/capabilities.yaml` 与 `knowledge/recipes/<key>.md` | 之后同类需求会被 `resolve` 直接命中 |

示例：OGR SQL 聚合没有内置步骤，用直通步骤即可实现——

```yaml
pipeline:
  name: "OGR SQL 聚合"
  steps:
    - id: sql-agg
      use: gdal.cli
      params:
        tool: ogr2ogr
        args: ["-f", "GeoJSON", "agg.geojson", "input.geojson", "-dialect", "SQLITE",
               "-sql", "SELECT category, SUM(area) AS total_area FROM input GROUP BY category"]
        output_path: agg.geojson
```

维护者须知：

- `gdal.cli` 参数以列表传入且 `shell=False`，可执行文件走白名单（ogr2ogr / ogrinfo / gdalinfo / gdal_translate / gdalwarp / gdal_rasterize / gdalbuildvrt），`output_path` 必须位于 workspace 内；args 中的相对路径以进程工作目录为基准，建议使用绝对路径。
- `geopipe-agent knowledge doctor` 校验能力登记与语料的一致性；`geopipe-agent knowledge sync --source <上游 gis 目录>` 用于从 opengis-skills 重新同步语料。
- 直通步骤返回文本输出，报告中的摘要字段是 `output_chars`（不是 `feature_count`）。

---
