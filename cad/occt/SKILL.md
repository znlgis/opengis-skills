---
name: occt
description: Open CASCADE Technology (OCCT) 是工业级开源 3D CAD 几何内核，提供 BRep 建模、几何表示、布尔运算、参数曲线/曲面、装配、网格化、显示、数据交换（STEP/IGES/STL/OBJ/glTF）等能力，是 FreeCAD、KiCAD 3D、SolveSpace 等众多开源 CAD 项目的底层。
---

> **项目地址：** <https://github.com/Open-Cascade-SAS/OCCT>
>
> **官网：** <https://dev.opencascade.org/>
>
> **官方文档：** <https://dev.opencascade.org/doc/refman/html/>
>
> **教程：** <https://dev.opencascade.org/doc/overview/html/>
>
> **许可证：** LGPL-2.1（带例外条款）

## 概述

OCCT 提供：

- **几何与拓扑**：`gp_*` 几何基元、`Geom_*` 解析曲线/曲面、`TopoDS_Shape`（Vertex/Edge/Wire/Face/Shell/Solid/Compound）
- **建模算法**：拉伸/旋转/扫掠/放样/圆角/倒角/抽壳/布尔（BOPAlgo）
- **STEP / IGES / STL / OBJ / glTF / VRML / BREP** 数据交换
- **显示**：基于 OpenGL（OCAF + AIS 应用框架）
- **网格**：BRepMesh / Triangulation
- **OCAF**：CAD 数据应用框架（属性、版本、引用）
- **跨语言绑定**：OCC.js（WebAssembly）、PythonOCC、occt-rs

---

## 安装

```bash
# Linux
sudo apt install libocct-foundation-dev libocct-modeling-data-dev \
    libocct-modeling-algorithms-dev libocct-data-exchange-dev \
    libocct-visualization-dev occt-misc

# macOS
brew install opencascade

# Conda（含 PythonOCC）
conda install -c conda-forge pythonocc-core

# 源码：CMake 构建
```

---

## 核心命名空间

| 包 | 内容 |
|----|------|
| `gp_*` | 数学几何基元（Pnt、Vec、Dir、Ax2、Trsf） |
| `Geom_*` | 参数曲线/曲面 |
| `TopoDS_*` | 拓扑（Vertex/Edge/Wire/Face/Shell/Solid/Compound） |
| `BRep*` | 拓扑 + 几何接口（BRepBuilderAPI_*、BRepPrimAPI_*、BRepAlgoAPI_*） |
| `BOPAlgo_*` | 高级布尔运算 |
| `STEPControl_*` / `IGESControl_*` | 数据交换 |
| `AIS_*` / `V3d_*` | 显示 |
| `TDocStd_*` / `TDF_*` | OCAF 数据框架 |

---

## C++ 入门：构造立方体并布尔差集

```cpp
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepFilletAPI_MakeFillet.hxx>
#include <STEPControl_Writer.hxx>
#include <TopExp_Explorer.hxx>
#include <gp_Ax2.hxx>

TopoDS_Shape box = BRepPrimAPI_MakeBox(100, 60, 30).Shape();

gp_Ax2 ax(gp_Pnt(50,30,0), gp_Dir(0,0,1));
TopoDS_Shape cyl = BRepPrimAPI_MakeCylinder(ax, 10, 50).Shape();

TopoDS_Shape result = BRepAlgoAPI_Cut(box, cyl).Shape();

// 圆角
BRepFilletAPI_MakeFillet fil(result);
for (TopExp_Explorer ex(result, TopAbs_EDGE); ex.More(); ex.Next())
    fil.Add(2.0, TopoDS::Edge(ex.Current()));
result = fil.Shape();

// STEP 导出
STEPControl_Writer w;
w.Transfer(result, STEPControl_AsIs);
w.Write("out.step");
```

---

## PythonOCC

```python
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs

box = BRepPrimAPI_MakeBox(100, 60, 30).Shape()
ax  = gp_Ax2(gp_Pnt(50,30,0), gp_Dir(0,0,1))
cyl = BRepPrimAPI_MakeCylinder(ax, 10, 50).Shape()
res = BRepAlgoAPI_Cut(box, cyl).Shape()

w = STEPControl_Writer()
w.Transfer(res, STEPControl_AsIs)
w.Write("out.step")
```

---

## 草图 → 拉伸（Wire → Face → Prism）

```cpp
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepPrimAPI_MakePrism.hxx>

BRepBuilderAPI_MakePolygon poly;
poly.Add(gp_Pnt(0,0,0));
poly.Add(gp_Pnt(50,0,0));
poly.Add(gp_Pnt(50,30,0));
poly.Add(gp_Pnt(0,30,0));
poly.Close();

TopoDS_Face face = BRepBuilderAPI_MakeFace(poly.Wire()).Face();
TopoDS_Shape solid = BRepPrimAPI_MakePrism(face, gp_Vec(0,0,20)).Shape();
```

---

## 数据交换

```cpp
// STEP 读取
#include <STEPControl_Reader.hxx>
STEPControl_Reader r;
r.ReadFile("input.step");
r.TransferRoots();
TopoDS_Shape s = r.OneShape();

// IGES
#include <IGESControl_Reader.hxx>
IGESControl_Reader ir; ir.ReadFile("a.iges"); ir.TransferRoots();

// STL 写入
#include <StlAPI_Writer.hxx>
#include <BRepMesh_IncrementalMesh.hxx>
BRepMesh_IncrementalMesh(shape, 0.1);   // 网格化容差
StlAPI_Writer sw; sw.Write(shape, "out.stl");

// glTF
#include <RWGltf_CafWriter.hxx>
```

---

## 网格化

```cpp
#include <BRepMesh_IncrementalMesh.hxx>
#include <TopLoc_Location.hxx>
#include <BRep_Tool.hxx>
#include <Poly_Triangulation.hxx>

BRepMesh_IncrementalMesh(shape, 0.1, false, 0.5);

for (TopExp_Explorer ex(shape, TopAbs_FACE); ex.More(); ex.Next()) {
    TopLoc_Location loc;
    auto tri = BRep_Tool::Triangulation(TopoDS::Face(ex.Current()), loc);
    if (tri.IsNull()) continue;
    for (int i = 1; i <= tri->NbTriangles(); ++i) {
        Standard_Integer n1, n2, n3;
        tri->Triangle(i).Get(n1, n2, n3);
        gp_Pnt p1 = tri->Node(n1).Transformed(loc);
        // ...
    }
}
```

---

## OCC.js（Web）

```js
import opencascade from 'opencascade.js';
const oc = await opencascade();
const box = new oc.BRepPrimAPI_MakeBox_2(100, 60, 30).Shape();
```

---

## 性能与稳定性

1. **小数容差一致**：使用 `BRep_Builder.UpdateVertex(_, tol)`，避免布尔失败
2. **`ShapeFix_Shape`**：导入外部 STEP 后修复
3. **`BRepBuilderAPI_Sewing`**：缝合多张面成 Shell
4. **使用 BOPAlgo_BOP** 替代旧 BRepAlgoAPI 处理多输入并行布尔
5. **共享内核**：`OSD_Parallel` 启用多线程网格化
6. **`Precision::Confusion()` / `Precision::Angular()`** 统一容差

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 布尔运算失败 | `ShapeFix_Shape` 修复输入；调整容差 |
| STEP 中文乱码 | OCCT 7.6+ 设置 `STEPControl_Reader::SetReadProgress` 与 UTF-8 |
| 拷贝 Shape 后位置错乱 | 注意 `TopoDS_Shape` 是引用，深拷贝用 `BRepBuilderAPI_Copy` |
| 显示无图 | AIS 上下文未启动 OpenGL；检查 `OCC.Display.SimpleGui` |

---

## 参考资源

- 文档：<https://dev.opencascade.org/doc/overview/html/>
- API：<https://dev.opencascade.org/doc/refman/html/>
- PythonOCC：<https://github.com/tpaviot/pythonocc-core>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/occt/>
