---
name: freecad
description: "Use when scripting FreeCAD 1.1.4 in Python or driving it headless — Part/PartDesign BREP modeling, Sketcher constraints, Arch/BIM and IFC, TechDraw, CAM, FEM, freecadcmd batch runs, Import.export to STEP. Also for ModuleNotFoundError when importing Part from system Python, Toponaming breakage after changing a sketch dimension, and character-encoding problems on Chinese file paths."
tags:
  - 3d
  - parametric
  - cad
  - python
  - brep
  - step
  - cam
  - bim
  - ifc
  - freecad
---

> **项目地址：** <https://github.com/FreeCAD/FreeCAD>
>
> **官网：** <https://www.freecad.org/>
>
> **官方文档：** <https://wiki.freecad.org/Main_Page>
>
> **Python API：** <https://wiki.freecad.org/FreeCAD_Scripting_Basics>
>
> **许可证：** LGPL-2.1-or-later
>
> **包管理器：** `freecad`（conda-forge）/ 各发行版仓库 / 官网安装包与 AppImage（最新 1.1.4，截至 2026-10）
>
> **版本：** 1.1.4（2026-09-28，1.1.x 系列最后一个维护版本，见 [GitHub Releases](https://github.com/FreeCAD/FreeCAD/releases)）

## 概述

FreeCAD 核心模块：

| 模块 | 用途 |
|------|------|
| Sketcher | 二维参数化草图（约束求解） |
| Part | 显式 BREP 建模（基于 OCCT） |
| PartDesign | 参数化特征建模 |
| Assembly（A2plus / Assembly3 / 自带） | 装配 |
| Draft | 二维绘图 |
| Arch / BIM | 建筑 / IFC |
| TechDraw | 工程图 |
| CAM (Path) | 数控编程 |
| FEM | 有限元仿真 |
| Spreadsheet | 电子表格驱动参数 |
| Mesh / Points | 网格与点云 |
| Surface | 曲面建模 |
| Robot | 机器人路径 |

支持文件：FCStd、STEP、IGES、BREP、STL、OBJ、PLY、DXF、DWG、SVG、IFC、PDF（导入）、AMF、3MF…

---

## 安装

```bash
# Linux
sudo apt install freecad
# 或 AppImage：<https://github.com/FreeCAD/FreeCAD/releases>

# macOS
brew install --cask freecad

# Windows：安装包 / Conda
conda install -c conda-forge freecad
```

FreeCAD 1.x 起合并了大量长期分支（如 PartDesign Toponaming 修复）。当前稳定版 **1.1.4**（2026-09-28 发布，官方说明这是 1.1.x 系列最后一个维护版本；该版包含两处「打开恶意构造的 FCStd 文件」相关的文件处理安全修复，旧版均受影响，建议升级，参见 [FreeCAD Releases](https://github.com/FreeCAD/FreeCAD/releases)）。

---

## 核心 API

### Python 脚本（FreeCAD 控制台 / 宏）

```python
import FreeCAD as App
import Part

doc = App.newDocument("demo")

# 创建立方体
box = doc.addObject("Part::Box", "MyBox")
box.Length = 100; box.Width = 60; box.Height = 30

# 创建圆柱
cyl = doc.addObject("Part::Cylinder", "MyCyl")
cyl.Radius = 10; cyl.Height = 50
cyl.Placement = App.Placement(App.Vector(50, 30, 0), App.Rotation(0,0,0,1))

# 布尔差集
cut = doc.addObject("Part::Cut", "Cut")
cut.Base = box; cut.Tool = cyl

doc.recompute()
Part.export([cut], "/tmp/out.step")
```

---

### 通过 OCCT/Part 直接构造几何

```python
import Part
from FreeCAD import Vector

# 多边形 → 拉伸
poly = Part.makePolygon([Vector(0,0,0), Vector(50,0,0),
                         Vector(50,30,0), Vector(0,30,0), Vector(0,0,0)])
face = Part.Face(Part.Wire(poly.Edges))
solid = face.extrude(Vector(0, 0, 20))

# 圆角
solid = solid.makeFillet(2, solid.Edges)

Part.show(solid)
```

---

### Sketcher 脚本约束

```python
import Sketcher
sk = doc.addObject('Sketcher::SketchObject', 'Sketch')
sk.Support = (doc.XY_Plane, [''])
sk.addGeometry(Part.LineSegment(Vector(0,0,0), Vector(50,0,0)))
sk.addConstraint(Sketcher.Constraint('Distance', 0, 50))
doc.recompute()
```

---

### 装配（自带 Assembly）

1. 切换到 Assembly 工作台
2. New Assembly → Insert Components（插入零件）
3. 添加 Joint：Fixed/Revolute/Slider/Planar/Cylindrical/Ball/Distance/Angle
4. Run Solver 自动定位
5. 干涉检查：Part → Check Geometry / Section

---

### CAM（Path）流程

1. Path Job → 选择目标体
2. 设置原点、坐标系、刀具库（Tool Bit）
3. 添加操作：Profile / Pocket / Drilling / Surface
4. Stock 模型与限位
5. Post Processor → 输出 G-code

---

### 工程图（TechDraw）

```python
page = doc.addObject('TechDraw::DrawPage', 'Page')
template = doc.addObject('TechDraw::DrawSVGTemplate', 'Template')
template.Template = '/usr/share/freecad/Mod/TechDraw/Templates/A4_LandscapeTD.svg'
page.Template = template
view = doc.addObject('TechDraw::DrawViewPart', 'View')
view.Source = [solid]
page.addView(view)
doc.recompute()
```

---

### BIM / IFC

- Arch / BIM 工作台支持墙、梁、柱、楼板、屋顶、门窗、设备
- 支持 IFC2x3 / IFC4 导入导出（基于 IfcOpenShell）
- 与 Blender BIM、IfcConvert 协同

---

### 命令行（无界面）

```bash
freecadcmd /tmp/script.py     # 无界面执行脚本（不启动 GUI）
freecad /tmp/script.py        # GUI 启动后立即执行脚本
freecad --console             # 打开 GUI 并显示 Python 控制台，交互输入
```

`freecadcmd` 不初始化 GUI，适合 CI 与无显示器的服务器；需要 TechDraw 出图等依赖图形栈的模块时，改用 `xvfb-run freecadcmd script.py` 之类的虚拟显示方案。

---

## 典型工作流

### 工作流一：无头脚本批量建模并导出 STEP（CI 可用）

输入：一份尺寸 CSV（`parts.csv`，含 `name,length,width,height,hole`）→ 输出：每行一个 `out/<name>.step`。

1. 把草稿逻辑写成普通 Python 函数 `build(length, width, height, hole)`，内部只用 `doc.addObject("Part::Box")` 之类的显式对象，不依赖当前选中的工作台或 GUI 交互
2. 循环读 CSV，每个零件单独 `App.newDocument()` / `App.closeDocument()`，避免对象名冲突
3. 每次改完属性调 `doc.recompute()`，并用 `shape.isValid()` 判非法几何
4. 用 `Import.export([obj], f"out/{name}.step")` 落盘（比 `Part.export` 更贴近 GUI 的导出行为）
5. 用 `freecadcmd build_parts.py` 在 CI 里无头运行，退出码非 0 即失败

```python
import csv
import FreeCAD as App
import Part  # noqa: F401  (确保 Part 模块加载)
import Import

with open("parts.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        doc = App.newDocument(row["name"])
        box = doc.addObject("Part::Box", "Base")
        box.Length, box.Width, box.Height = (
            float(row["length"]), float(row["width"]), float(row["height"])
        )
        doc.recompute()
        obj = doc.getObject("Base")
        if not obj.Shape.isValid():
            raise SystemExit(f"invalid shape: {row['name']}")
        Import.export([obj], f"out/{row['name']}.step")
        App.closeDocument(doc.Name)
```

### 工作流二：GUI 内从草图到出图

1. **新建文档** → 选择「Part Design」工作台
2. **新建 Body** → 进入 Sketcher，绘制带约束的 2D 草图
3. **特征建模**：Pad（拉伸）、Pocket（开槽）、Revolution（旋转）、Loft、Sweep
4. **修饰**：圆角、倒角、抽壳、镜像、阵列
5. **导出**：File → Export → STEP/STL

---

## 性能优化

1. **关闭工具栏图标动画**与不必要的工作台
2. **大装配**：使用 Lightweight Part / Linked Document
3. **Recompute** 仅在必要时调用；`doc.recompute()` 之后检查 `doc.RecomputesFrozen` 与对象 `State`（含 `Invalid`/`Error` 即失败）
4. **Sketcher**：减少自由度，避免过约束求解失败
5. **导出 STL**：减面后再导出，控制 LinearDeflection

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 改参数后后续特征丢失/报错（Toponaming） | 1.0 起引入 ElementMap 缓解，但仍非完全解决：尽量用 `PartDesign::Body` 内的草图基准与 Datum 定位，避免跨对象引用面/边编号；升级到 1.1.4 可拿到后续修复 |
| 中文文件名编码 | 使用 UTF-8；Windows 下避免 GBK 路径 |
| 导出 STEP 缺少颜色 | 用 STEP AP242 或在 ImportSettings 启用颜色 |
| Sketcher 求解失败 | 删除冗余约束、检查 DoF |
| Mesh 转 Solid 不闭合 | 用 Part → Convert to solid 前先 Mesh Repair |
| `freecadcmd: command not found` | 发行版可能只装了 GUI 入口；用 `which freecad` 反查安装前缀并在同目录找 `freecadcmd`，或改用 AppImage（解包后取同名入口），也可 `conda install -c conda-forge freecad` 拿到完整命令行 |
| 脚本里 `import Part` 报 `ModuleNotFoundError` | `Part` 等模块只存在于 FreeCAD 自带解释器：必须在 `freecadcmd` / 宏 / GUI 控制台里跑。系统 Python 想用类型检查可装 `freecad-stubs`（PyPI），但它只有 `.pyi` 存根、不能运行几何代码 |
| `Part.export` 导出的 STEP 下游读不出 | 优先 `Import.export([obj], "out.step")`（FreeCAD 自带导入导出模块，走偏好设置）；导出前 `doc.recompute()` 并确认 `Shape.isValid()` |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应根据场景选择工作台——机械零件用 PartDesign（草图+特征），简单几何用 Part（CSG），建筑用 Arch/BIM。脚本自动化优先使用 `FreeCAD Python Console` 或 `freecadcmd` 无头模式。
- **关键注意事项**：① Sketcher 草图需完全约束（黑色），欠约束（蓝色）在后续编辑中可能偏移；② Python 操作几何对象后需调用 `doc.recompute()` 才能更新显示与关联；③ 导出 STEP 前确认模型无错误（`Part → Check Geometry`）；④ Toponaming 问题自 1.0 起有 ElementMap 缓解但未彻底解决，脚本中避免用面/边序号做长期引用（改用 Datum 与命名选择）；
- **常用代码模式**：`doc.addObject("Part::Box", ...)` 创建参数化体 → 设置属性 → `doc.recompute()` → `Part.export([shape], "out.step")`。对于脚本化建模，也可直接用 `Part.make*` 系列函数构造几何。

---

## 相关技能

- **occt** — 底层 OCCT 几何内核（FreeCAD 的几何引擎基础）：[../occt/SKILL.md](../occt/SKILL.md)
- **cadquery** — Python 参数化 CAD 库（同基于 OCCT，更适合纯脚本）：[../cadquery/SKILL.md](../cadquery/SKILL.md)
- **openscad** — 声明式 CSG 建模（与 FreeCAD 互补，适合编程型用户）：[../openscad/SKILL.md](../openscad/SKILL.md)
- **xbim** — .NET BIM/IFC 框架（与 FreeCAD BIM 工作台互补）：[../xbim/SKILL.md](../xbim/SKILL.md)
- **solvespace** — 轻量约束求解器建模（快速概念设计）：[../solvespace/SKILL.md](../solvespace/SKILL.md)

---

## 参考资源

- Wiki：<https://wiki.freecad.org/Main_Page>
- Python 入门：<https://wiki.freecad.org/FreeCAD_Scripting_Basics>
- 论坛：<https://forum.freecad.org/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/FreeCAD/>
