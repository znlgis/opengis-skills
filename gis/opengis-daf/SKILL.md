---
name: opengis-daf
description: "Use when building plan-driven GIS data analysis or data quality-check pipelines with OpenGisDAF (.NET 10 / C# 14): define buffer, clip, intersect/containment checks, coordinate transform, field calculator, attribute/geometry QC rules purely in JSON plans, run the daf CLI, chain operators via DAG upstream bindings, output to GeoJSON/Shapefile/PostGIS, or extend with plugin operators loaded via AssemblyLoadContext."

tags:
  - gis
  - csharp
  - dotnet
  - spatial-analysis
  - data-quality
  - geojson
  - shapefile
  - postgis
  - plugin
---

> **项目地址：** <https://github.com/znlgis/opengis-daf>
>
> **许可证：** MIT License
>
> **文档：** <https://github.com/znlgis/opengis-daf/tree/main/docs>（快速入门、方案配置指南、算子参考、CLI 参考）
>
> **底层依赖：** GDAL/OGR 3.x、NetTopologySuite 2.6、Npgsql 10、Serilog 4.3

## 概述

OpenGIS Data Analysis Framework（简称 OpenGisDAF / `daf`）是一个**方案驱动、纯配置定义**的 GIS 数据分析与数据质检框架：用一个 JSON 方案（AnalysisPlan）描述"输入数据 → 算子处理 → 输出目标"的完整流程，可复用、可版本化。核心能力：

- **方案驱动**：纯 JSON 定义分析流程，内置 21 条方案校验规则（参数存在性/类型/范围、绑定完整性、DAG 环检测）
- **空间分析**：缓冲区、裁剪、相交检查、包含检查、坐标系转换（CRS 全链路传播，Z 值保留）
- **属性操作**：字段计算器（表达式 + 算术解析器）、空值填充
- **数据质检**：几何有效性、属性完整性检查，QC 模式自动生成质量评分报告
- **DAG 调度**：Kahn 拓扑排序，`upstream` 绑定串联算子，超时/重试/失败策略控制
- **多数据源/多输出**：`IFeatureSource`（GeoJSON、Shapefile、PostGIS、内存）× `IFeatureSink`（控制台、GeoJSON、Shapefile、PostGIS）
- **插件扩展**：`AssemblyLoadContext` 动态加载算子 DLL，插件算子与内置算子在同一 DAG 中无区别
- **方案管理**：list/create/copy/export、版本回退、跨版本 Diff、原子写入

**环境要求：** .NET SDK 10.0（仓库 `global.json` 已锁定版本）、Git（克隆时需 `--recurse-submodules`，子模块 `opengis-utils-for-net` 提供 GDAL 绑定）。Windows x64 / Linux x64 / macOS。

---

## 快速上手

```bash
# 克隆（必须带子模块）
git clone --recurse-submodules https://github.com/znlgis/opengis-daf.git
cd opengis-daf
dotnet build            # 或 .\build.ps1 / ./build.sh

# 验证安装
dotnet run --project src/OpenGisDAF.Cli -- help

# 校验方案（不执行）
daf validate --plan plans/my-analysis.json
# 执行分析/质检
daf run --plan plans/my-analysis.json
```

测试须分两步（.NET 10 SDK + xunit.v3 工具链下 `dotnet test` 同命令构建会报"运行了零个测试"并退出码 5）：

```bash
dotnet build OpenGisDAF.slnx --configuration Release
dotnet test OpenGisDAF.slnx --configuration Release --no-build
```

仓库自带**完全自包含的学习 Demo**（`demo/`，虚构"新星市"合成数据，一键脚本 `demo/run-demo.ps1` / `run-demo.sh` 依次执行构建 → 算子清单 → 校验 → 4 个方案 → 插件演示，并对退出码断言）。

---

## 方案配置（核心）

### 顶层结构

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 方案唯一标识 |
| `name` | string | 是 | 方案名称 |
| `version` | string | 是 | 语义化版本（如 `"1.0.0"`） |
| `group` | string | 否 | 分组名（方案管理分类用） |
| `items` | array | 是 | 分析项列表（至少 1 个） |
| `executionPolicy` | object | 否 | `failurePolicy`: `stopOnAny`（默认，遇错即停）/ `continueIndependent`（继续独立项）；`maxParallelism` 默认 4 |

### 分析项（items[]）

每个 item 一次算子调用：`id`（方案内唯一）、`operatorId`、`inputs`（绑定名 → InputBinding）、`parameters`（算子参数）、`output`（OutputBinding）、可选 `executionPolicy`（item 级：`qcMode`、`maxRetries`、`retryInterval` 默认 `"00:00:05"`、`timeout` 默认 `"00:30:00"`、`exponentialBackoff`）。

**InputBinding**：

```json
{ "type": "external", "sourceId": "data/roads.shp" }
{ "type": "upstream", "sourceId": "step-clip", "outputKey": "output" }
```

`type` 取 `external`（文件路径）或 `upstream`（引用上游 item 的输出，`outputKey` 默认 `"output"`）。

**OutputBinding**：

```json
{ "adapterType": "geojson", "targetPath": "output/result.geojson", "isIntermediate": false }
```

`adapterType` 推荐短名 `console` / `geojson` / `shapefile` / `postgis`（也接受枚举名 `ConsoleWriter` 等，大小写不敏感）；`isIntermediate: true` 标记中间结果可被缓存复用；PostGIS 需另加 `connectionConfig`。

### 最小示例（两步串联：裁剪 → 字段计算）

```json
{
  "id": "serial-demo", "name": "串联分析", "version": "1.0.0",
  "items": [
    { "id": "step-clip", "operatorId": "clip",
      "inputs": { "source": { "type": "external", "sourceId": "data/polygons.geojson" },
                  "clip":   { "type": "external", "sourceId": "data/boundary.geojson" } },
      "output": { "adapterType": "geojson", "targetPath": "output/clipped.geojson" } },
    { "id": "step-field", "operatorId": "field_calculator",
      "inputs": { "source": { "type": "upstream", "sourceId": "step-clip" } },
      "parameters": { "target_field": "area_sqkm", "expression": "area * 0.000001", "field_type": "Double" },
      "output": { "adapterType": "geojson", "targetPath": "output/final.geojson" } }
  ],
  "executionPolicy": { "failurePolicy": "stopOnAny" }
}
```

---

## 内置算子（9 个）

| 算子 ID | 分类 | 参数 | 输入绑定 | 说明 |
|---------|------|------|---------|------|
| `buffer` | 空间运算 | `distance`（double，必填） | `source` | 缓冲区多边形；单位与数据坐标系一致（先转米制投影再算距离） |
| `clip` | 空间运算 | 无 | `source` + `clip` | 裁剪；**逐面求交**，一个源要素与多个裁剪面相交会输出多条（可能要素分裂） |
| `intersect_check` | 空间关系 | `use_second_input`（bool，默认 true） | `source`（+ `target`） | true=两集合交叉检查；false=集合内要素两两相交检查 |
| `containment_check` | 空间关系 | `relationship`（`contains`/`within`） | `source` + `target` | 包含关系检查 |
| `coordinate_transform` | 格式转换 | `source_epsg` + `target_epsg`（int，必填） | `source` | 坐标系转换，CRS 随数据流传播 |
| `field_calculator` | 属性操作 | `target_field` + `expression` + `field_type` | `source` | 表达式：字符串字面量 `"Hello"`、字段引用 `{field_name}`、算术 `+ - * /` 与括号 |
| `null_value_filler` | 属性操作 | `target_field` + `default_value` + `field_type` | `source` | 空值填充 |
| `attribute_completeness_checker` | 质检 | `required_fields`（逗号分隔） | `source` | QC 模式产出 `ATTR_MISSING`（Error，null）/ `ATTR_EMPTY`（Warning，空串） |
| `geometry_validity_checker` | 质检 | 无 | `source` | QC 模式产出 `GEOM_EMPTY` / `GEOM_INVALID`（Error）、`GEOM_NOT_SIMPLE`（Warning） |

`field_type` 取值：`String` / `Integer` / `Double` / `Boolean` / `DateTime`。

---

## 数据源与输出适配器

| 输入 `IFeatureSource` | 说明 |
|----------------------|------|
| `GeoJsonFeatureSource` | `.geojson` / `.json`，支持属性过滤 |
| `ShapefileFeatureSource` | `.shp`，自动读取 `.prj` 投影 |
| `PostgisFeatureSource` | GDAL `PG:` 驱动，密码加密（DPAPI / AES-256-GCM） |
| `InMemoryFeatureSource` | 算子间传递中间结果 |

| 输出 `IFeatureSink` | 说明 |
|--------------------|------|
| `ConsoleFeatureSink` | 调试查看 |
| `GeoJsonFeatureSink` | 含属性、几何与 `crs` 字段 |
| `ShapefileFeatureSink` | `.shp/.shx/.dbf/.prj/.cpg` 五件套 |
| `PostgisFeatureSink` | 自动建表写入；**目标表已存在时报错，绝不静默覆盖** |

---

## CLI 命令

| 命令 | 说明 |
|------|------|
| `daf run --plan <path>` | 加载 → 校验 → 执行；Ctrl+C 可取消；QC 模式自动生成 `{plan}.qc-report.json` |
| `daf validate --plan <path>` | 仅校验 21 条规则，不执行 |
| `daf operator list [--category <名>]` | 列出已注册算子（**导入仅当前进程有效**） |
| `daf operator import --dll <path>` | 动态导入算子 DLL |
| `daf plan list / create / copy / export` | 方案管理，操作用户数据目录（Windows 为 `%APPDATA%\opengis-daf\plans`），ID 格式 `group/name` |

退出码：`0` 成功；`1` 任何错误（参数错误、校验失败、执行失败）——**只要有失败或跳过即返回 1**，便于 CI 判断。

---

## 插件算子开发

插件只引用 `OpenGisDAF.Core` 的公共契约（`IOperator` / `IFeature` / `IFeatureSource`），通过 `AssemblyLoadContext` 动态加载。三个关键点：

1. **最小依赖面**：自带 `PluginFeature` / `PluginFeatureSource` 简单实现，不引用任何实现层程序集。
2. **不要复制宿主程序集**（最常见的坑）：csproj 中 `ProjectReference` 必须 `Private="false" ExcludeAssets="runtime"`——若把 `OpenGisDAF.Core.dll` 复制进插件目录，插件的 `IOperator` 与宿主不是同一 Type，算子被静默跳过（日志 "No IOperator implementations found"）。
3. **schema 可选**：输出源不实现 `IFeatureSchemaProvider` 也能工作，框架写输出时自动推断字段并集、几何类型与 CRS。

CLI 的 `operator import` 只在当前进程生效，`daf run` 是新进程——要让插件参与方案执行需**同进程编程宿主**（参考 `demo/plugin/OpenGisDAF.PluginHostDemo`）：

```bash
dotnet build demo/plugin/OpenGisDAF.SamplePlugin/OpenGisDAF.SamplePlugin.csproj -c Release
dotnet build demo/plugin/OpenGisDAF.PluginHostDemo/OpenGisDAF.PluginHostDemo.csproj -c Release
dotnet demo/plugin/OpenGisDAF.PluginHostDemo/bin/Release/net10.0/OpenGisDAF.PluginHostDemo.dll \
    --plugin demo/plugin/OpenGisDAF.SamplePlugin/bin/Release/net10.0/OpenGisDAF.SamplePlugin.dll \
    --plan   demo/plugin/plans/road-length.json
```

---

## 常见工作流

### 先质检、后分析（推荐）

无效几何（蝴蝶结多边形等）参与 clip 求交会抛 `TopologyException`、该要素被跳过。正确顺序：

1. 跑质检方案（各 QC 算子 `executionPolicy.qcMode: true`），生成 `{plan}.qc-report.json`——含每条规则 `totalChecked/failed/passed/passRate`、汇总质量评分、完整 issue 清单（含 WKT 违规几何）；
2. 按 issue 修复数据；
3. 再跑分析方案。

### 容错策略

`failurePolicy: "continueIndependent"` 下：失败项的下游跳过、与其无依赖的项照常执行（demo 方案 04）。默认 `stopOnAny` 遇错即停。注意 `maxRetries` **仅对执行期运行时错误（`ERR_RT_*`，如超时）生效**；输入文件不存在这类调度层错误（`SCH_*`）直接失败、不重试。

### PostGIS 输出

`output.adapterType: "postgis"` + `connectionConfig`。`encryptedPassword` 必须是当前用户上下文生成的 DPAPI（Windows）/ AES-256-GCM（Linux/macOS，密钥文件权限 0600）密文，**不能填明文**；密文无效立即失败且错误信息不回显密文。

---

## 常见问题

| 问题 | 处理 |
|------|------|
| Shapefile 字段名被截断（`landuse_type` → `landuse_ty`） | DBF 规范 10 字符限制，GDAL 自动 launder；跨数据源方案优先引用短字段名，截断无法自动恢复 |
| 字段引用找不到 | `field_calculator` 的 `{字段}` 匹配按 OrdinalIgnoreCase，但不同数据源返回大小写不同（SHP 大写、PostGIS 折叠小写）；跨源串联时用与目标源实际一致的名字 |
| clip 结果要素比预期多 | 逐面求交语义，一个源要素与多个裁剪面各输出一条；需先 union 裁剪面 |
| 质检报告 `FeatureId` 当主键用 | 它是底层驱动 FID（GDAL 通常从 0 起），不保证跨驱动/跨版本稳定；业务标识请数据自带 id 字段 |
| 插件算子不出现 | 检查是否复制了 `OpenGisDAF.Core.dll` 到插件目录（Type 不同源被静默跳过）；`operator import` 对后续 `daf run` 进程无效，需同进程宿主 |
| 距离计算结果离谱 | `buffer` 单位与数据坐标系一致，度数坐标系下 800 = 800 度；先 `coordinate_transform` 转米制投影（如 3857） |
| PostGIS 写入报 `Layer already exists` | 有意的防误覆盖设计：先删目标表或换表名 |

---

## 参考资源

- 仓库与文档：<https://github.com/znlgis/opengis-daf>（`docs/quickstart.md`、`docs/plan-config-guide.md`、`docs/operator-reference.md`、`docs/cli-reference.md`）
- 自包含教程 Demo：<https://github.com/znlgis/opengis-daf/tree/main/demo>（"新星市"规划分析：6 步 DAG 主线、QC 评分、SHP 闭环、失败策略、插件开发）
- 底层几何库：本仓库 [NetTopologySuite SKILL](../nettopologysuite/SKILL.md)、[GDAL 元技能](../opengis-all/SKILL.md)
- 配套工具库：<https://github.com/znlgis/opengis-utils-for-net>（Git 子模块，GDAL C# 绑定）
