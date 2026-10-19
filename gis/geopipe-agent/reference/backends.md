
# Backend Selection Guide（后端选择指南）

GeoPipeAgent 的步骤通过 `StepInfo.backends` 声明可选后端；引擎在运行期按声明顺序挑第一个可用后端。查看当前环境：`geopipe-agent backends`。

## 内置后端

| 后端 | 实现 | 可用性判定 | 适用场景 |
|------|------|------------|----------|
| `native_python` | GeoPandas + Shapely（进程内） | 可 import geopandas 与 shapely | 默认后端；中小矢量数据、需要细粒度控制 |
| `gdal_cli` | ogr2ogr / gdal_translate 等 CLI | PATH 中有 `ogr2ogr` | 大数据量转换；临时 GeoJSON 中转 |
| `gdal_python` | osgeo.ogr / osr / gdal 绑定 | 可 import osgeo | 需要 GDAL/OGR 精细 API 与驱动选项 |
| `qgis_process` | `qgis_process run <algorithm>` | PATH 中有 `qgis_process` | 任意 QGIS Processing 算法 |
| `pyqgis` | `qgis.core` Python API | 可 import qgis.core | 进程内使用 QGIS 图层与渲染 |
| `generic_cli` | 通用子进程执行 | 恒可用 | 集成自有脚本/工具（默认 `shell=False`） |
| `curl_api` | `curl` 子进程 | PATH 中有 `curl` | HTTP 取数/调 API（host 白名单、10 MiB、30 s、TLS 校验） |

## 选择顺序

1. 步骤已声明 `backends=[...]`：按声明顺序探测，第一个可用者胜出；YAML 中可用 `backend: <name>` 显式指定。
2. `StepInfo.backends` 为空：引擎不注入后端，步骤自己实现全部逻辑（导入期仍不得读盘、不得联网）。
3. 目标能力还没有对应步骤：先 `geopipe-agent resolve <need>` 拿到候选与回退，再决定
   - 零代码：改写为直通步骤 `gdal.cli` / `qgis.algorithm` / `http.request`；
   - 生成代码：`geopipe-agent scaffold step <category.action> --capability <key>`（默认 dry-run）。
4. 新增后端：实现 `GeoBackend` 子类，并登记进 `src/geopipe_agent/backends/__init__.py` 的 `_BACKEND_CLASSES`（硬编码列表，必须改代码）。

## 排错

- 后端不可用时错误信息会给出安装提示与可用后端列表；`qgis_process` / `pyqgis` 通常只在 OSGeo4W、QGIS 自带 Python 或 conda 环境可用。
- 直通步骤的参数一律以列表传递、`shell=False`、带超时；`http.request` 继承 `curl_api` 的 host 白名单与体积/超时限制。
- 步骤声明的 `backends` 必须与实现一致：`geopipe-agent knowledge doctor` 与 `resolve` 的 `available` 字段都会核对注册表。
