---
name: freecad
description: FreeCAD 是开源参数化 3D CAD 建模软件，基于 OCCT 几何内核与 Coin3D 显示引擎，提供 Sketcher、Part、PartDesign、Assembly、Draft、Arch（BIM）、CAM、FEM 等专业模块，支持 Python 脚本与插件扩展，适合机械设计、建筑 BIM、产品原型与教学。
tags: [3d, parametric, cad, python, brep, step, cam, bim, ifc, freecad]
---

> **项目地址：** <https://github.com/FreeCAD/FreeCAD>
>
> **官网：** <https://www.freecad.org/>
>
> **官方文档：** <https://wiki.freecad.org/Main_Page>
>
> **Python API：** <https://wiki.freecad.org/FreeCAD_Scripting_Basics>
>
> **许可证：** LGPL-2.0+

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

最新稳定 1.x 起合并了大量长期分支（如 PartDesign Toponaming 修复）。

---

## 工作流（GUI）

1. **新建文档** → 选择「Part Design」工作台
2. **新建 Body** → 进入 Sketcher，绘制带约束的 2D 草图
3. **特征建模**：Pad（拉伸）、Pocket（开槽）、Revolution（旋转）、Loft、Sweep
4. **修饰**：圆角、倒角、抽壳、镜像、阵列
5. **导出**：File → Export → STEP/STL

---

## Python 脚本（FreeCAD 控制台 / 宏）

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

## 通过 OCCT/Part 直接构造几何

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

## Sketcher 脚本约束

```python
import Sketcher
sk = doc.addObject('Sketcher::SketchObject', 'Sketch')
sk.Support = (doc.XY_Plane, [''])
sk.addGeometry(Part.LineSegment(Vector(0,0,0), Vector(50,0,0)))
sk.addConstraint(Sketcher.Constraint('Distance', 0, 50))
doc.recompute()
```

---

## 装配（自带 Assembly）

1. 切换到 Assembly 工作台
2. New Assembly → Insert Components（插入零件）
3. 添加 Joint：Fixed/Revolute/Slider/Planar/Cylindrical/Ball/Distance/Angle
4. Run Solver 自动定位
5. 干涉检查：Part → Check Geometry / Section

---

## CAM（Path）流程

1. Path Job → 选择目标体
2. 设置原点、坐标系、刀具库（Tool Bit）
3. 添加操作：Profile / Pocket / Drilling / Surface
4. Stock 模型与限位
5. Post Processor → 输出 G-code

---

## 工程图（TechDraw）

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

## BIM / IFC

- Arch / BIM 工作台支持墙、梁、柱、楼板、屋顶、门窗、设备
- 支持 IFC2x3 / IFC4 导入导出（基于 IfcOpenShell）
- 与 Blender BIM、IfcConvert 协同

---

## 命令行（无界面）

```bash
freecadcmd /tmp/script.py    # 后台运行 Python
freecad   --console <<<'doc=App.newDocument(); ...'
```

---

## 性能优化

1. **关闭工具栏图标动画**与不必要的工作台
2. **大装配**：使用 Lightweight Part / Linked Document
3. **Recompute** 仅在必要时调用，使用 `doc.recompute(returnStringList=True)` 检查错误
4. **Sketcher**：减少自由度，避免过约束求解失败
5. **导出 STL**：减面后再导出，控制 LinearDeflection

---

## 常见问题

| 问题 | 解决 |
|------|------|
| Toponaming 在编辑后特征丢失 | 升级到 1.x（含拓扑命名修复） |
| 中文文件名编码 | 使用 UTF-8；Windows 下避免 GBK 路径 |
| 导出 STEP 缺少颜色 | 用 STEP AP242 或在 ImportSettings 启用颜色 |
| Sketcher 求解失败 | 删除冗余约束、检查 DoF |
| Mesh 转 Solid 不闭合 | 用 Part → Convert to solid 前先 Mesh Repair |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应根据场景选择工作台——机械零件用 PartDesign（草图+特征），简单几何用 Part（CSG），建筑用 Arch/BIM。脚本自动化优先使用 `FreeCAD Python Console` 或 `freecadcmd` 无头模式。
- **关键注意事项**：① Sketcher 草图需完全约束（黑色），欠约束（蓝色）在后续编辑中可能偏移；② Python 操作几何对象后需调用 `doc.recompute()` 才能更新显示与关联；③ 导出 STEP 前确认模型无错误（`Part → Check Geometry`）；④ Toponaming 问题在 1.x 版基本解决，旧版注意避免引用面/边编号。
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
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/freecad/>
