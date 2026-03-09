# SKILL.md — QGIS Processing Executor (`qgis_process`)

> **项目地址：** <https://github.com/qgis/QGIS>
>
> **文档地址：** <https://github.com/qgis/QGIS-Documentation>
>
> **在线文档：** <https://docs.qgis.org/3.40/en/docs/user_manual/processing/standalone.html>
>
> **许可证：** GNU General Public License v2.0+

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

## 常用内置算法速查

以下列出常用的内置算法分类及代表性 ID：

### 矢量通用（native）

| 算法 ID | 说明 |
|---------|------|
| `native:buffer` | 缓冲区分析 |
| `native:clip` | 裁剪 |
| `native:dissolve` | 融合 |
| `native:intersection` | 交集 |
| `native:union` | 联合 |
| `native:difference` | 差集 |
| `native:symmetricaldifference` | 对称差 |
| `native:centroids` | 质心 |
| `native:convexhull` | 凸包 |
| `native:simplifygeometries` | 简化几何 |
| `native:reprojectlayer` | 重投影 |
| `native:mergevectorlayers` | 合并矢量图层 |
| `native:splitvectorlayer` | 拆分矢量图层 |
| `native:extractbyattribute` | 按属性提取 |
| `native:extractbylocation` | 按位置提取 |
| `native:joinattributesbylocation` | 按位置连接属性 |
| `native:fixgeometries` | 修复几何 |
| `native:countpointsinpolygon` | 多边形内点计数 |
| `native:voronoipolygons` | 泰森多边形 |
| `native:delaunaytriangulation` | Delaunay 三角剖分 |
| `native:creategrid` | 创建网格 |
| `native:randomextract` | 随机抽样 |
| `native:addautoincrementalfield` | 添加自增字段 |
| `native:fieldcalculator` | 字段计算器 |

### 栅格分析（native / gdal）

| 算法 ID | 说明 |
|---------|------|
| `native:rasterlayerstatistics` | 栅格统计 |
| `native:rastersurfacevolume` | 栅格曲面体积 |
| `gdal:cliprasterbyextent` | 按范围裁剪栅格 |
| `gdal:cliprasterbymask` | 按掩膜裁剪栅格 |
| `gdal:merge` | 栅格合并 |
| `gdal:warpreproject` | 栅格重投影 |
| `gdal:contour` | 等值线提取 |
| `gdal:polygonize` | 栅格转矢量 |
| `gdal:rasterize` | 矢量转栅格 |
| `gdal:hillshade` | 山体阴影 |
| `gdal:slope` | 坡度分析 |
| `gdal:aspect` | 坡向分析 |
| `gdal:roughness` | 粗糙度 |
| `gdal:buildvirtualraster` | 构建虚拟栅格（VRT） |

### 坐标参考系

| 算法 ID | 说明 |
|---------|------|
| `native:reprojectlayer` | 矢量重投影 |
| `gdal:warpreproject` | 栅格重投影 |
| `native:assignprojection` | 指定投影（不变换坐标） |

### 点云（pdal）

| 算法 ID | 说明 |
|---------|------|
| `pdal:info` | 点云信息 |
| `pdal:clip` | 点云裁剪 |
| `pdal:merge` | 点云合并 |
| `pdal:thin` | 点云抽稀 |
| `pdal:tile` | 点云瓦片化 |
| `pdal:boundary` | 点云边界 |
| `pdal:density` | 点云密度 |
| `pdal:exportraster` | 点云转栅格 |
| `pdal:exportvector` | 点云转矢量 |

---

## 参数类型参考

`qgis_process` 支持的常见参数类型及命令行传值方式：

| 参数类型 | 说明 | 命令行值示例 |
|----------|------|-------------|
| `source` / `vector` | 矢量数据源 | 文件路径 `input.shp`、`input.geojson` |
| `raster` | 栅格图层 | 文件路径 `dem.tif` |
| `sink` | 矢量输出目标 | 文件路径 `output.shp`、`output.gpkg` |
| `rasterDestination` | 栅格输出目标 | 文件路径 `output.tif` |
| `number` / `distance` / `area` | 数值 | `10`、`2.5` |
| `string` | 字符串 | `"my_value"` |
| `boolean` | 布尔值 | `true` / `false` |
| `enum` | 枚举 | 数字索引 `0`、`1`、`2` |
| `crs` | 坐标参考系 | `EPSG:4326`、`EPSG:3857` |
| `extent` | 空间范围 | `xmin,xmax,ymin,ymax [EPSG:code]` |
| `point` | 点坐标 | `x,y [EPSG:code]` |
| `field` | 字段名 | 字段名字符串 |
| `expression` | QGIS 表达式 | `"field_name * 2"` |
| `multilayer` | 多图层 | 多次指定同一参数 |
| `file` | 文件路径 | `/path/to/file` |
| `folder` | 文件夹路径 | `/path/to/folder` |

---

## 典型工作流示例

### 示例 1：矢量数据格式转换（SHP → GeoJSON）

```bash
# 使用 ogr2ogr 风格的转换，利用 QGIS 重投影能力
qgis_process run native:reprojectlayer -- \
  INPUT=input.shp \
  TARGET_CRS=EPSG:4326 \
  OUTPUT=output.geojson
```

### 示例 2：批量缓冲区 + 融合

```bash
# 第一步：缓冲区分析
qgis_process run native:buffer -- \
  INPUT=points.shp \
  DISTANCE=1000 \
  SEGMENTS=16 \
  OUTPUT=/tmp/buffered.gpkg

# 第二步：融合
qgis_process run native:dissolve -- \
  INPUT=/tmp/buffered.gpkg \
  OUTPUT=dissolved.gpkg
```

### 示例 3：栅格裁剪 + 坡度分析

```bash
# 裁剪 DEM
qgis_process run gdal:cliprasterbymask -- \
  INPUT=dem.tif \
  MASK=boundary.shp \
  OUTPUT=/tmp/clipped_dem.tif

# 坡度分析
qgis_process run gdal:slope -- \
  INPUT=/tmp/clipped_dem.tif \
  OUTPUT=slope.tif
```

### 示例 4：使用 JSON 传参（适合 AI 自动化）

```bash
cat <<'EOF' | qgis_process run native:buffer -
{
  "ellipsoid": "EPSG:7030",
  "distance_units": "meters",
  "inputs": {
    "INPUT": "/data/roads.shp",
    "DISTANCE": 50,
    "SEGMENTS": 10,
    "END_CAP_STYLE": 0,
    "JOIN_STYLE": 0,
    "MITER_LIMIT": 2,
    "DISSOLVE": false,
    "OUTPUT": "/data/roads_buffer_50m.gpkg"
  }
}
EOF
```

### 示例 5：在脚本中解析 JSON 输出

```bash
# 运行算法并捕获 JSON 输出
RESULT=$(qgis_process run native:buffer --json -- \
  INPUT=source.shp DISTANCE=100 OUTPUT=buffered.shp)

# 使用 jq 提取输出文件路径
OUTPUT_PATH=$(echo "$RESULT" | jq -r '.results.OUTPUT')
echo "输出文件: $OUTPUT_PATH"
```

### 示例 6：需要 QGIS 项目文件的算法

```bash
qgis_process run native:printlayouttopdf -- \
  --PROJECT_PATH=/path/to/project.qgs \
  LAYOUT="My Layout" \
  OUTPUT=/output/map.pdf
```

---

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
4. **多值参数多次指定**：如 `--LAYERS=a.shp --LAYERS=b.shp`。
5. **复杂参数用 STDIN JSON**：字典类型的参数值适合通过 STDIN JSON 方式传入。
6. **文件路径使用绝对路径**：避免工作目录不确定导致的文件找不到。
7. **Headless 环境设置 `QT_QPA_PLATFORM=offscreen`**：在无显示器的服务器上必须设置。
8. **需要项目文件的算法**：某些算法（如打印布局导出）需要通过 `--PROJECT_PATH` 指定项目文件。
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
