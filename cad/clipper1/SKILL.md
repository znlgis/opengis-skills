---
name: clipper1
description: Clipper（一代）是 Angus Johnson 的开源整数多边形裁剪/偏移库，遵循 Vatti 算法，提供布尔运算（并/交/差/异或）、多边形偏移与简化能力，长期作为 CAD/GIS/CNC 行业的事实标准；目前已被 Clipper2 取代但仍在大量遗留代码中使用。
---

> **项目地址：** <https://github.com/AngusJohnson/Clipper>
>
> **官方文档：** <http://www.angusj.com/delphi/clipper.php>
>
> **NuGet：** `Clipper`（多个第三方移植版）
>
> **许可证：** Boost Software License 1.0

## 概述

Clipper1 主要特征：

- **整数算法**（`IntPoint`），通过 `scale` 系数模拟浮点
- **核心 API**：`Clipper`、`ClipperOffset`、`ClipperBase`
- **支持**：布尔运算 + 偏移 + 多边形简化
- **多语言移植**：C++（含 Header-only）、C#、Delphi/Pascal、JS、Python

> **新项目优先使用 [Clipper2](../clipper2/SKILL.md)**，其性能与 API 均优于 Clipper1。本 SKILL 主要用于维护遗留代码。

---

## 安装

```bash
# C#
dotnet add package Clipper

# JavaScript
npm install js-clipper          # 或 clipper-lib

# Python
pip install pyclipper
```

C++ 通常直接拷贝 `clipper.hpp/.cpp` 到工程。

---

## 核心数据结构

```csharp
using ClipperLib;
using IntPoint = ClipperLib.IntPoint;

const long Scale = 1000000;     // 浮点 → 整数缩放因子

List<IntPoint> path = new() {
    new IntPoint(0, 0),
    new IntPoint(100 * Scale, 0),
    new IntPoint(100 * Scale, 100 * Scale),
    new IntPoint(0, 100 * Scale),
};
List<List<IntPoint>> paths = new() { path };
```

---

## 布尔运算

```csharp
var clipper = new Clipper();
clipper.AddPath(subject, PolyType.ptSubject, true);   // true = 闭合
clipper.AddPath(clip,    PolyType.ptClip,    true);

var solution = new List<List<IntPoint>>();
clipper.Execute(ClipType.ctUnion, solution,
    PolyFillType.pftNonZero, PolyFillType.pftNonZero);
```

`ClipType`：`ctIntersection`、`ctUnion`、`ctDifference`、`ctXor`
`PolyFillType`：`pftEvenOdd`、`pftNonZero`、`pftPositive`、`pftNegative`

---

## 多边形偏移（ClipperOffset）

```csharp
var co = new ClipperOffset();
co.AddPaths(paths, JoinType.jtRound, EndType.etClosedPolygon);

var solution = new List<List<IntPoint>>();
co.Execute(ref solution, 10 * Scale);     // 正：外扩；负：内缩
```

`JoinType`：`jtSquare`、`jtMiter`、`jtRound`
`EndType`：`etClosedPolygon`、`etClosedLine`、`etOpenButt`、`etOpenSquare`、`etOpenRound`

---

## PolyTree（保留环层级）

```csharp
var tree = new PolyTree();
clipper.Execute(ClipType.ctUnion, tree,
    PolyFillType.pftNonZero, PolyFillType.pftNonZero);

foreach (var node in tree.Childs)        // 顶层是外环
    foreach (var hole in node.Childs)    // 子节点是孔
        Console.WriteLine(hole.Contour.Count);
```

---

## 实用方法

```csharp
double area    = Clipper.Area(path);
bool   ccw     = Clipper.Orientation(path);
var    cleaned = Clipper.CleanPolygon(path, 1.415);    // 去重/共线
var    simp    = Clipper.SimplifyPolygon(path, PolyFillType.pftNonZero);
var    reverse = Clipper.ReversePath(path);
```

---

## Python（pyclipper）

```python
import pyclipper

scale = 1_000_000
subj  = [[(0,0),(100,0),(100,100),(0,100)]]
clip  = [[(50,50),(150,50),(150,150),(50,150)]]

pc = pyclipper.Pyclipper()
pc.AddPaths(pyclipper.scale_to_clipper(subj, scale),
            pyclipper.PT_SUBJECT, True)
pc.AddPaths(pyclipper.scale_to_clipper(clip, scale),
            pyclipper.PT_CLIP, True)
sol = pc.Execute(pyclipper.CT_UNION,
                 pyclipper.PFT_NONZERO,
                 pyclipper.PFT_NONZERO)
sol = pyclipper.scale_from_clipper(sol, scale)

# 偏移
pco = pyclipper.PyclipperOffset()
pco.AddPaths(pyclipper.scale_to_clipper(subj, scale),
             pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
sol = pco.Execute(10 * scale)
```

---

## C++ 用法

```cpp
#include "clipper.hpp"
using namespace ClipperLib;

Paths subj{{ {0,0},{1000,0},{1000,1000},{0,1000} }};
Paths clip{{ {500,500},{1500,500},{1500,1500},{500,1500} }};
Clipper c;
c.AddPaths(subj, ptSubject, true);
c.AddPaths(clip, ptClip, true);
Paths solution;
c.Execute(ctUnion, solution, pftNonZero, pftNonZero);
```

---

## 与 Clipper2 主要差异

| 维度 | Clipper1 | Clipper2 |
|------|----------|----------|
| 数值类型 | 整数 + scale | 整数 / 浮点双模式 |
| 性能 | 较慢 | 显著更快 |
| API | `Clipper` 类 | 顶层 `Union/Intersect/...` |
| 简化 | `SimplifyPolygon` | `SimplifyPaths` 更准确 |
| 维护 | 已停止新功能 | 活跃维护 |

迁移要点：

- `IntPoint` → `Point64`
- 移除 scale，使用 `PathsD` 或保留 `Paths64`
- API 改为静态函数

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 浮点 → 整数舍入失真 | 增大 `scale` |
| 偏移产生自相交 | 偏移前 `SimplifyPolygon` |
| 闭合 path 多余首尾点 | Clipper 不需要重复首点 |
| Mac/Linux 编译失败 | 启用 `use_int32`/`use_xyz` 对应宏 |

---

## 参考资源

- 仓库：<https://github.com/AngusJohnson/Clipper>
- 文档：<http://www.angusj.com/delphi/clipper.php>
- pyclipper：<https://github.com/fonttools/pyclipper>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/clipper1/>
