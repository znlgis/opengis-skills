---
name: blender
description: "Use when building or batch-processing 3D scenes with Blender's Python bpy API: constructing meshes and objects, Geometry Nodes procedural modeling, converting GIS data (GeoJSON/Shapefile) into building massing, developing add-ons, and exporting glTF/OBJ/STL in headless mode. Blender is the leading open-source 3D creation suite."
tags:
  - 3d
  - blender
  - python
  - bpy
  - geometry-nodes
  - gltf
  - headless
  - addon
  - gis
  - procedural
---

> **项目地址：** <https://github.com/blender/blender>
>
> **官方文档：** <https://docs.blender.org/>
>
> **Python API：** <https://docs.blender.org/api/current/>
>
> **许可证：** GPL-2.0-or-later
>
> **最新稳定版：** 5.2.2 LTS（2026-09-15 发布，见 [GitHub Tags](https://github.com/blender/blender/tags)；上一 LTS 系列为 4.5）

## 概述

Blender 是开源 3D 创作套件，通过内置 Python 解释器暴露完整的 `bpy` API：脚本可读写全部场景数据、调用几乎全部界面功能，适合程序化建模、GIS 数据三维化与无头批处理。Python API 随 Blender 版本发布（当前 5.2.2 LTS），无需单独安装。

核心模块：

| 模块 | 用途 |
|------|------|
| `bpy.data` | 数据块访问（objects、meshes、materials、node_groups…） |
| `bpy.context` | 当前上下文（场景、视图层、选中对象、模式） |
| `bpy.ops` | 操作符（建模、导入导出、渲染、文件管理） |
| `bpy.types` | 类型定义（Object、Mesh、Operator、NodeTree…） |
| `bpy.msgbus` | 消息总线（订阅数据块属性变更） |
| `mathutils` | Vector / Matrix / Quaternion / Euler 数学库 |
| `bpy_extras` | 辅助工具（io_utils、object_utils、view3d_utils） |

常用交换格式：.blend、glTF 2.0（.gltf/.glb）、OBJ、STL、FBX、PLY、USD、Alembic、SVG。

---

## 环境准备

**桌面安装**

```bash
# Windows：官网安装包或 winget
winget install BlenderFoundation.Blender

# macOS
brew install --cask blender

# Linux（Ubuntu 官方推荐 snap）
sudo snap install blender --classic
# 或使用官网 tar.xz（免 root）：<https://www.blender.org/download/>
# 发行版仓库的 blender 包通常滞后于官网版本，建议 snap 或官网包
```

**无头（headless）运行**

- `blender -b`（`--background`）不创建窗口，渲染、导入导出、脚本执行均可用，适合服务器与 CI。
- 无头环境不需要显示器；Linux 服务器建议使用官网 tar.xz 并补齐基础运行库。
- Blender 内置独立 Python，不依赖系统 Python；脚本中直接 `import bpy` 即可。

**验证**

```bash
blender --version
blender -b --python-expr "import bpy; print(bpy.app.version_string)"
```

---

## 核心 API/命令

### 命令行运行脚本

```bash
blender -b scene.blend -P build.py                 # 打开文件并执行脚本
blender -b -P gen.py -- --count 100 --out out.glb  # 脚本参数置于 -- 之后，脚本内用 sys.argv 读取
blender -b --python-expr "import bpy; print(len(bpy.data.objects))"
blender -b --python-exit-code 1 -P pipeline.py     # 脚本异常时以非零码退出，便于 CI 判断
```

`-P` 等价于 `--python <filepath>`；另有 `--python-text <name>`（执行文本块）与 `--python-console`（交互控制台）。

### 数据访问与对象创建

```python
import bpy
from mathutils import Vector

# 无头场景：清空为工厂空设置
bpy.ops.wm.read_factory_settings(use_empty=True)

# 由顶点/面创建网格数据块
mesh = bpy.data.meshes.new("Facade")
mesh.from_pydata([(0, 0, 0), (10, 0, 0), (10, 6, 0), (0, 6, 0)], [], [(0, 1, 2, 3)])
mesh.validate()

# 创建对象并链接到当前集合
obj = bpy.data.objects.new("Building", mesh)
bpy.context.collection.objects.link(obj)

obj.location = Vector((100.0, 50.0, 0.0))
obj.scale = (1.0, 1.0, 3.0)   # 简易拉高
```

`bpy.data` 集合既可按名称索引（`bpy.data.objects["Cube"]`）也可按序号索引；序号可能随运行变化，脚本中优先用名称或变量引用。

### 网格与几何操作

```python
mesh = obj.data
mesh.validate()             # 检查并修复非法几何
mesh.calc_loop_triangles()  # 计算三角剖分（导出前需要）

# 变换优先改对象属性，避免依赖上下文的 bpy.ops
obj.rotation_euler = (0.0, 0.0, 1.5708)  # 绕 Z 轴 90 度
bpy.context.view_layer.update()          # 属性改动后刷新依赖图
```

### 导出 glTF / OBJ / STL

```python
# glTF 2.0（.glb 单文件，Web 首选）
bpy.ops.export_scene.gltf(filepath="out.glb", export_format='GLB', use_selection=False)

# OBJ（4.0 起为新的导入导出器）
bpy.ops.wm.obj_export(filepath="out.obj", export_selected_objects=False)

# STL（4.1 起为新的导入导出器）
bpy.ops.wm.stl_export(filepath="out.stl", export_selected_objects=False)

# 保存 .blend
bpy.ops.wm.save_as_mainfile(filepath="scene.blend")
```

### Geometry Nodes 基础（脚本创建节点组）

```python
# 新建几何节点组（GeometryNodeTree）
group = bpy.data.node_groups.new("GN_Extrude", 'GeometryNodeTree')

# 4.0 起用 interface.new_socket 定义输入/输出接口
group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

node_in = group.nodes.new("NodeGroupInput")
node_out = group.nodes.new("NodeGroupOutput")
cube = group.nodes.new("GeometryNodeMeshCube")        # 立方体节点
extrude = group.nodes.new("GeometryNodeExtrudeMesh")  # 挤出网格节点

group.links.new(node_in.outputs["Geometry"], extrude.inputs["Mesh"])
group.links.new(extrude.outputs["Mesh"], node_out.inputs["Geometry"])
```

```python
# 将节点组挂到对象修饰器上
obj = bpy.data.objects.new("GN_Object", None)
bpy.context.collection.objects.link(obj)
mod = obj.modifiers.new("GeometryNodes", 'NODES')
mod.node_group = group

# 取评估后网格（应用修饰器结果，用于导出/统计）
depsgraph = bpy.context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(depsgraph)
mesh_eval = bpy.data.meshes.new_from_object(obj_eval)
```

### 插件开发框架

```python
bl_info = {
    "name": "My GIS Tool",
    "author": "you",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "category": "Object",
}

import bpy

class OBJECT_OT_build_from_footprint(bpy.types.Operator):
    bl_idname = "object.build_from_footprint"
    bl_label = "Build from Footprint"

    def execute(self, context):
        self.report({'INFO'}, "done")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_build_from_footprint)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_build_from_footprint)

if __name__ == "__main__":
    register()
```

传统插件用 `bl_info` + `register()/unregister()`（结构取自官方 Add-on Tutorial）；4.2 起新式扩展（Extensions）改用 `blender_manifest.toml` 声明元数据，`register/unregister` 约定不变。

### GIS 数据结合（GeoJSON 生成建筑体块）

```python
import json
import bpy

# 解析 GeoJSON（标准库 json 即可）
with open("footprints.geojson", encoding="utf-8") as f:
    gj = json.load(f)

def add_building(ring, height, name):
    """ring: [[lon, lat], ...] 外环；按等距近似投影为米"""
    verts = [(x * 111320.0, y * 110540.0, 0.0) for x, y in ring[:-1]]  # 去掉闭合点
    n = len(verts)
    verts += [(x, y, height) for x, y, _ in verts]
    faces = [[i, (i + 1) % n, (i + 1) % n + n, i + n] for i in range(n)]
    faces.append([i + n for i in range(n)])  # 顶面
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

for i, feat in enumerate(gj["features"]):
    geom = feat["geometry"]
    if geom["type"] == "Polygon":
        add_building(geom["coordinates"][0], feat["properties"].get("height", 10.0), f"B_{i}")

bpy.ops.export_scene.gltf(filepath="city.glb", export_format='GLB')
```

- 上述经纬度转米为等距近似，跨区域或高精度场景应先用 pyproj/GDAL 做投影（UTM/Web Mercator）再写入 `verts`。
- Shapefile 可用 [BlenderGIS](https://github.com/domlysz/BlenderGIS) 插件导入：`bpy.ops.importgis.shapefile(filepath="districts.shp")`（bl_idname 为 `importgis.shapefile`），该插件同时支持 GeoTIFF 与 OSM。
- 大数据量建议先在 GDAL/QGIS 中裁剪、简化、转 GeoJSON，再交给 Blender 生成体块。

---

## 典型工作流

1. **准备环境**：无头服务器用官网包安装，`blender -b --python-expr "import bpy"` 验证可用。
2. **编写脚本**：以 `bpy.ops.wm.read_factory_settings(use_empty=True)` 开始，用 `bpy.data` 创建网格/对象并 `link` 到集合。
3. **建模**：简单体块直接 `from_pydata`；参数化或迭代规则用 Geometry Nodes 节点组 + 修饰器。
4. **材质与变换**：设置 `obj.location/rotation_euler/scale` 与材质槽，`view_layer.update()` 刷新。
5. **导出**：按目标平台选择 `export_scene.gltf` / `wm.obj_export` / `wm.stl_export`，显式指定格式与选择参数。
6. **批处理**：`blender -b -P pipeline.py -- <args>` 循环处理数据集，配合 `--python-exit-code` 接入 CI。

---

## 最佳实践

1. **脚本优先 `bpy.data`，而非 `bpy.ops`**：`bpy.ops` 依赖上下文（模式、选中、区域），无头环境下易报 `context is incorrect`；必须用操作符时通过 `bpy.context.temp_override(...)` 显式提供上下文。
2. **导出参数写全**：glTF 用 `export_format='GLB'` 控制单文件；OBJ/STL 用 `export_selected_objects` 控制范围；导出前确认对象已链接到场景集合。
3. **Geometry Nodes 结果需评估**：修饰器不修改原始网格，导出或统计前经 `evaluated_depsgraph_get()` + `new_from_object()` 取评估网格。
4. **单位与坐标**：Blender 内部为米、Z 轴向上；glTF 导出默认转 Y 轴向上，写入 GIS 数据（东-北-高）时保持 Z-up 约定。
5. **无头稳定性**：CI 中加 `--python-exit-code 1`；批处理循环用 `try/except` 包装，单个要素失败不中断整批。
6. **第三方库**：Blender 使用内置 Python，不加载系统 site-packages；纯数据解析优先标准库（json、csv），复杂投影/几何处理可调用外部 GDAL 生成中间文件。

---

## 常见问题

| 问题 | 解决 |
|------|------|
| snap 安装后 `blender: command not found` | snap 版路径为 `/snap/bin/blender`，确认 PATH 或使用绝对路径 |
| 无头下 `bpy.ops` 报 `context is incorrect` | 改用 `bpy.data` 直接操作，或用 `bpy.context.temp_override(...)` 提供所需上下文 |
| 脚本报 `ModuleNotFoundError`（第三方包） | Blender 使用内置 Python，不加载系统 site-packages；改用标准库或外部工具生成中间数据 |
| `-P` 脚本执行完但没有输出文件 | 后台模式不自动保存；需显式调用 `wm.save_as_mainfile` 或导出操作符 |
| 导出的 glTF 没有材质 | 材质需使用 Principled BSDF 节点；检查导出参数 `export_materials` 未被关闭 |
| Geometry Nodes 修饰器无效果 | 确认节点组输出已连接 `Group Output`，且对象有输入几何；用 depsgraph 取评估网格验证 |
| 脚本参数没有传入 | 参数须放在 `--` 之后（`blender -b -P s.py -- a b`），脚本内从 `sys.argv` 读取 |
| 4.x 旧脚本在 5.x 报错 | 节点组接口：旧式 `inputs/outputs` 改为 `interface.new_socket`；导入导出核对 `wm.obj_export`/`wm.stl_export` 名称 |

---

## 参考资源

- 官方手册（脚本与扩展章节）：<https://docs.blender.org/manual/en/latest/advanced/scripting/index.html>
- Python API 文档：<https://docs.blender.org/api/current/>
- API Quickstart：<https://docs.blender.org/api/current/info_quickstart.html>
- 命令行参数：<https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html>
- Add-on 教程：<https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html>
- 扩展（Extensions）指南：<https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html>
- 下载与版本：<https://www.blender.org/download/>

---

## 相关技能

- **freecad** — 参数化 CAD 与 BIM（精确实体建模，与 Blender 网格流程互补）：[../freecad/SKILL.md](../freecad/SKILL.md)
- **openscad** — 声明式 CSG 建模（快速生成体块后导入 Blender 渲染）：[../openscad/SKILL.md](../openscad/SKILL.md)
- **cadquery** — Python 参数化 CAD（精确 B-Rep，可与 Blender 交换 glTF/OBJ）：[../cadquery/SKILL.md](../cadquery/SKILL.md)
- **occt** — 底层 OCCT 几何内核（精确几何运算）：[../occt/SKILL.md](../occt/SKILL.md)

---

## AI 使用建议

- **推荐工作流模式**：AI 生成 Blender 脚本时先确定运行模式（GUI 交互或 `blender -b -P` 无头），无头脚本一律从 `bpy.data` 出发；GIS 类任务先输出 GeoJSON 中间文件再生成体块脚本，避免在 Blender 内做重投影。
- **关键注意事项**：① `bpy.ops` 依赖上下文，无头环境优先 `bpy.data`；② 修改属性后调用 `bpy.context.view_layer.update()` 或重新获取 depsgraph；③ 导出操作符参数（`export_format`、`export_selected_objects`）必须显式给出；④ Blender 内置 Python 不加载系统第三方包；⑤ 版本差异集中在节点组接口（`interface.new_socket`）与导入导出操作符名称（`wm.obj_export`/`wm.stl_export`），生成代码前确认目标版本。
- **常用代码模式**：`read_factory_settings(use_empty=True)` → `bpy.data.meshes.new` + `from_pydata` → `objects.new` + `collection.objects.link` → 设置变换/修饰器 → `export_scene.gltf` / `wm.stl_export`；批处理外壳 `blender -b --python-exit-code 1 -P pipeline.py -- <args>`。
