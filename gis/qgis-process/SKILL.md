---
name: qgis-process
description: "Use when running QGIS geoprocessing tools headless from command line or CI/CD — buffer, clip, reproject, raster analysis without GUI. QGIS Processing: batch spatial analysis via qgis_process CLI."
tags:
  - cli
  - qgis
  - processing
  - raster
  - automation
  - batch
  - ci-cd
  - json
  - shell
---

> **项目地址：** <https://github.com/qgis/QGIS>
>
> **文档地址：** <https://github.com/qgis/QGIS-Documentation>
>
> **在线文档：** <https://docs.qgis.org/3.44/en/docs/user_manual/processing/standalone.html>
>
> **许可证：** GPL-2.0+

## 概述

`qgis_process` 是 QGIS 自带的命令行工具（QGIS Processing Executor），允许在**不启动 QGIS 桌面应用**的情况下，直接从命令行运行 Processing 算法和模型（内置算法或由插件提供）。它适用于服务器端批量处理、CI/CD 自动化流水线、脚本化 GIS 工作流等场景。

源码位置：`src/process/` 目录下的 `main.cpp`、`qgsprocess.cpp`、`qgsprocess.h`。

---

## 环境准备

### 前置条件

- 安装 QGIS 3.16+（`qgis_process` 从 QGIS 3.16 开始可用）
- 确保 `qgis_process` 可执行文件在 `PATH` 中

### 无窗口系统（Headless 服务器）

在没有窗口管理器的系统上运行前，需设置环境变量：

```bash
export QT_QPA_PLATFORM=offscreen
```

### 验证安装

```bash
qgis_process --version
```

---

## 命令行语法

```
qgis_process [--help] [--version] [--json] [--verbose] [--no-python] [--skip-loading-plugins] [command] [algorithm id | model path | script path] [parameters]
```

### 全局选项

| 选项 | 说明 |
|------|------|
| `--help` 或 `-h` | 输出帮助信息 |
| `--version` 或 `-v` | 输出 QGIS Process 相关的所有版本信息 |
| `--json` | 以 JSON 格式输出结果（AI/脚本友好） |
| `--verbose` | 输出详细日志 |
| `--no-python` | 禁用 Python 支持（启动更快） |
| `--skip-loading-plugins` | 跳过加载已启用的插件（启动更快） |

### 可用命令

| 命令 | 说明 |
|------|------|
| `plugins` | 列出可用和已激活的插件 |
| `plugins enable <name>` | 启用已安装的插件 |
| `plugins disable <name>` | 禁用已安装的插件 |
| `list` | 列出所有可用的 Processing 算法 |
| `help <algorithm_id>` | 显示指定算法的帮助信息 |
| `run <algorithm_id> [-- PARAM=VALUE ...]` | 运行指定算法 |

> **注意：** 只有在 `metadata.txt` 中声明了 `hasProcessingProvider=yes` 的已安装插件才能被 `qgis_process` 识别和加载。

---

## 核心用法

### 1. 列出所有算法

```bash
qgis_process list
```

输出所有已注册 Provider 及其提供的算法 ID。

### 2. 查看算法帮助

```bash
qgis_process help qgis:regularpoints
```

输出算法的描述、参数列表（名称、类型、默认值、是否可选）和输出定义。

#### JSON 格式帮助（推荐 AI 使用）

```bash
qgis_process help native:buffer --json
```

JSON 输出结构：

```json
{
  "qgis_version": "...",
  "algorithm_details": {
    "id": "native:buffer",
    "name": "Buffer",
    "tags": ["..."]
  },
  "provider_details": {
    "id": "native",
    "name": "QGIS (native c++)"
  },
  "parameters": {
    "INPUT": {
      "name": "INPUT",
      "description": "Input layer",
      "type": {
        "id": "source",
        "name": "Vector Features",
        "acceptable_values": ["Path to a vector layer"]
      },
      "optional": false,
      "default_value": null
    },
    "DISTANCE": {
      "name": "DISTANCE",
      "description": "Distance",
      "type": {
        "id": "distance",
        "name": "Distance"
      },
      "optional": false,
      "default_value": 10
    },
    "OUTPUT": {
      "name": "OUTPUT",
      "description": "Buffered",
      "type": {
        "id": "sink",
        "name": "Vector Layer Destination"
      },
      "is_destination": true,
      "optional": false
    }
  },
  "outputs": {
    "OUTPUT": {
      "description": "Buffered",
      "type": "outputVector"
    }
  }
}
```

### 3. 运行算法

#### 基本语法

```bash
qgis_process run <algorithm_id> -- PARAM1=VALUE1 PARAM2=VALUE2 ...
```

#### 示例：缓冲区分析

```bash
qgis_process run native:buffer -- INPUT=source.shp DISTANCE=2 OUTPUT=buffered.shp
```

#### 示例：合并图层（多值参数）

同一参数多次指定即可传入列表值：

```bash
qgis_process run native:mergevectorlayers -- LAYERS=input1.shp LAYERS=input2.shp OUTPUT=merged.shp
```

#### `run` 命令附加选项

| 选项 | 说明 |
|------|------|
| `--json` | 以 JSON 格式输出执行结果 |
| `--ellipsoid=<name>` | 指定椭球体，用于距离和面积计算 |
| `--distance_units=<unit>` | 指定距离单位 |
| `--area_units=<unit>` | 指定面积单位 |
| `--project_path=<path>` | 加载已有 QGIS 项目文件供算法执行时使用 |

#### JSON 格式运行结果

```bash
qgis_process run native:buffer --json -- INPUT=source.shp DISTANCE=2 OUTPUT=buffered.shp
```

JSON 输出结构：

```json
{
  "qgis_version": "...",
  "algorithm_details": { "id": "native:buffer" },
  "inputs": {
    "INPUT": "source.shp",
    "DISTANCE": "2",
    "OUTPUT": "buffered.shp"
  },
  "results": {
    "OUTPUT": "/full/path/to/buffered.shp"
  },
  "log": ["..."]
}
```

### 4. 通过 STDIN 传入 JSON 参数（复杂参数）

当参数本身是复杂对象（如字典类型）时，可通过 STDIN 传入 JSON：

```bash
qgis_process run <algorithm_id> -
```

末尾的 `-` 表示从 STDIN 读取参数。JSON 必须包含 `"inputs"` 键：

```bash
echo '{"inputs": {"INPUT": "my_shape.shp", "DISTANCE": 5}}' | qgis_process run native:buffer -
```

完整 JSON 结构（含可选配置）：

```json
{
  "ellipsoid": "EPSG:7019",
  "distance_units": "feet",
  "area_units": "ha",
  "project_path": "/path/to/project.qgs",
  "inputs": {
    "INPUT": "my_shape.shp",
    "DISTANCE": 5,
    "SEGMENTS": 8,
    "OUTPUT": "output.shp"
  }
}
```

> **注意：** 通过 STDIN 传入 JSON 时，输出自动使用 JSON 格式。

### 5. 插件管理

```bash
# 列出插件
qgis_process plugins

# 启用插件
qgis_process plugins enable cartography_tools

# 禁用插件
qgis_process plugins disable cartography_tools
```

### 6. 运行模型文件

```bash
qgis_process run /path/to/my_model.model3 -- INPUT=data.shp OUTPUT=result.shp
```

### 7. 运行 Python 脚本

```bash
qgis_process run /path/to/my_script.py -- INPUT=data.shp OUTPUT=result.shp
```

---

> 常用内置算法速查、参数类型参考与典型工作流示例见 [reference/algorithm-cheatsheet.md](reference/algorithm-cheatsheet.md)

## AI 使用建议

### 推荐工作流

1. **发现算法**：`qgis_process list` → 获取所有可用算法 ID
2. **查看帮助**：`qgis_process help <algorithm_id> --json` → 获取参数定义的 JSON
3. **构造参数**：根据 JSON 帮助信息构造参数
4. **执行算法**：`qgis_process run <algorithm_id> --json -- PARAM=VALUE ...` 或通过 STDIN 传入 JSON
5. **解析结果**：解析 JSON 输出获取结果路径和日志信息

### 关键注意事项

1. **始终使用 `--json` 选项**：JSON 输出结构化、易解析，是 AI 最友好的交互方式。
2. **先查 help 再构造参数**：每个算法的参数名和类型不同，先用 `help --json` 确认参数定义。
3. **枚举类型传数字索引**：枚举参数用数字（如 `0`、`1`）而非文字。help 输出的 `available_options` 提供了索引到含义的映射。
4. **多值参数多次指定**：如 `LAYERS=a.shp LAYERS=b.shp`（在 `--` 之后，参数不带前导 `--`）。
5. **复杂参数用 STDIN JSON**：字典类型的参数值适合通过 STDIN JSON 方式传入。
6. **文件路径使用绝对路径**：避免工作目录不确定导致的文件找不到。
7. **Headless 环境设置 `QT_QPA_PLATFORM=offscreen`**：在无显示器的服务器上必须设置。
8. **需要项目文件的算法**：某些算法（如打印布局导出）需要通过 `--project_path` 指定项目文件。
9. **取消正在运行的算法**：使用 `CTRL+C` 可取消执行中的算法。
10. **`--no-python` 和 `--skip-loading-plugins` 可加速启动**：如果不需要第三方插件提供的算法，使用这两个选项可显著缩短启动时间。

### 错误处理

- 算法不存在：`Algorithm <id> not found!`
- 缺少必填参数：`The following mandatory parameters were not specified`
- 模型文件无效：`File <path> is not a valid Processing model!`
- Python 脚本无效：`File <path> is not a valid Processing script!`
- 算法不可在命令行使用：`The "<id>" algorithm is not available for use outside of the QGIS desktop application`
- 需要项目文件：`The "<id>" algorithm requires a QGIS project to execute`

---

## 算法 Provider 分类

| Provider ID | 说明 | 来源 |
|-------------|------|------|
| `native` | QGIS 原生 C++ 算法 | QGIS 内置 |
| `qgis` | QGIS Python 算法 | QGIS 内置 |
| `gdal` | GDAL/OGR 工具封装 | QGIS 内置 |
| `grass` | GRASS GIS 算法 | QGIS 内置（需 GRASS 安装） |
| `saga` | SAGA GIS 算法 | 插件提供 |
| `pdal` | 点云处理算法 | QGIS 内置（需 PDAL） |
| `3d` | 3D 分析算法 | QGIS 内置 |
| 其他 | 第三方插件 Provider | 各插件提供 |

---

## 相关技能

- **pyqgis** — QGIS Python 绑定：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **gdal** — 命令行数据处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **geopipe-agent** — AI 原生分析流水线：[../geopipe-agent/SKILL.md](../geopipe-agent/SKILL.md)
- **geoserver-rest-api** — REST API 自动化：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)

## 源码结构参考

源码位于 QGIS 仓库 `src/process/` 目录：

| 文件 | 说明 |
|------|------|
| `main.cpp` | 程序入口 |
| `qgsprocess.h` | `QgsProcessingExec` 类定义，包含命令分发、插件加载、算法执行等 |
| `qgsprocess.cpp` | 核心实现：`showUsage()`（帮助）、`listAlgorithms()`（列表）、`showAlgorithmHelp()`（算法帮助）、`execute()`（执行算法） |
| `CMakeLists.txt` | 构建配置 |

### 核心类

- **`QgsProcessingExec`**：命令行执行器，负责解析命令和参数、加载插件、执行算法
- **`ConsoleFeedback`**：继承自 `QgsProcessingFeedback`，处理控制台输出和进度显示，支持文本和 JSON 两种输出模式
- **`QgsProcessingExec::Flags`**：执行标志（`UseJson`、`SkipPython`、`SkipLoadingPlugins`）

### 关键方法

| 方法 | 说明 |
|------|------|
| `run(args, logLevel, flags)` | 主入口，解析命令行参数并分发到对应子命令 |
| `showUsage(appName)` | 输出使用帮助 |
| `showVersionInformation()` | 输出版本信息 |
| `listAlgorithms()` | 列出所有 Provider 和算法 |
| `listPlugins(useJson, showLoaded)` | 列出插件信息 |
| `enablePlugin(name, enabled)` | 启用/禁用插件 |
| `showAlgorithmHelp(id)` | 显示算法帮助（支持文本和 JSON 输出） |
| `execute(algId, parameters, ...)` | 执行算法核心逻辑 |
| `loadPlugins()` | 加载 Python 插件 |
