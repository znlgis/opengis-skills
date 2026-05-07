---
name: clipper2
description: Clipper2 是 Angus Johnson 编写的高性能开源多边形裁剪/偏移库的最新一代实现（C++/C#/Delphi 三语言），支持布尔运算（并/交/差/异或）、多边形偏移（Inflate/Outset/Mitre/Square/Round）、最小封闭矩形等，是 CAD/GIS/CNC/3D 打印领域的核心几何算法库。
---

> **项目地址：** <https://github.com/AngusJohnson/Clipper2>
>
> **官方文档：** <http://www.angusj.com/clipper2/Docs/Overview.htm>
>
> **NuGet：** `Clipper2`
>
> **许可证：** Boost Software License 1.0

## 概述

Clipper2 相对 Clipper1 的提升：

- 全新算法，速度更快、内存更省
- 支持浮点（`PathsD`）与整数（`Paths64`）双模式
- 全新偏移引擎：更鲁棒的 mitre/square/round 端帽与连接
- 简洁 API：`Union/Intersect/Difference/Xor` 顶级函数
- 多语言：C++、C#、Delphi、JS（Clipper2.js 移植）

---

## 安装

### C#

```bash
dotnet add package Clipper2     # 提供 Clipper2Lib 命名空间
```

### C++

```bash
# vcpkg
vcpkg install clipper2
# 或直接 add subdirectory CPP/Clipper2Lib 到 CMake
```

### JavaScript

```bash
npm install clipper2-js
```

---

## 核心数据结构（C#）

```csharp
using Clipper2Lib;

PointD pd = new(10.5, 20.7);            // 浮点点
PathD  path = new() { new(0,0), new(10,0), new(10,10), new(0,10) };
PathsD subj = new() { path };           // 多个 path
PathsD clip = new() { /* ... */ };
```

整数版本：`Point64` / `Path64` / `Paths64`，避免浮点误差。

---

## 布尔运算

```csharp
using Clipper2Lib;

PathsD a = new() { Clipper.MakePath(new[] { 0d,0, 100,0, 100,100, 0,100 }) };
PathsD b = new() { Clipper.MakePath(new[] { 50d,50, 150,50, 150,150, 50,150 }) };

PathsD u = Clipper.Union(a, b, FillRule.NonZero);
PathsD i = Clipper.Intersect(a, b, FillRule.NonZero);
PathsD d = Clipper.Difference(a, b, FillRule.NonZero);
PathsD x = Clipper.Xor(a, b, FillRule.NonZero);
```

`FillRule`：

- `EvenOdd`（奇偶）
- `NonZero`（非零）
- `Positive`（正向缠绕）
- `Negative`（负向缠绕）

---

## 多边形偏移（Inflate / 缩进）

```csharp
PathsD outline = new() {
    Clipper.MakePath(new[] { 0d,0, 100,0, 100,100, 0,100 })
};

// 向外偏移 10 单位
PathsD outer = Clipper.InflatePaths(outline, 10,
    JoinType.Round,        // Square / Miter / Round
    EndType.Polygon);       // Polygon / Joined / Butt / Square / Round

// 向内偏移：负数
PathsD inner = Clipper.InflatePaths(outline, -10,
    JoinType.Miter, EndType.Polygon);
```

**EndType：**

- `Polygon` 闭合多边形
- `Joined` 开放多线段，端点首尾相连
- `Butt` / `Square` / `Round` 开放线段端帽

---

## 高级用法（ClipperD/Clipper64 类）

需要更精细控制（PolyTree、ZFill 回调等）：

```csharp
ClipperD clipper = new(2);   // 2 = 浮点保留 2 位小数精度

clipper.AddSubject(subj);
clipper.AddClip(clip);

PolyTreeD tree = new();
clipper.Execute(ClipType.Union, FillRule.NonZero, tree);
PathsD result = Clipper.PolyTreeToPathsD(tree);
```

`PolyTree` 保留外环/内孔的层级关系，对于带孔多边形非常重要。

---

## 实用工具

```csharp
double area = Clipper.Area(path);                       // 有符号面积
PointD c    = Clipper.Centroid(path);                   // 形心
RectD bbox  = Clipper.GetBounds(paths);                 // 包围盒

PathsD simp = Clipper.SimplifyPaths(paths, 0.5);        // 简化（容差）
PathsD ramer = Clipper.RamerDouglasPeucker(paths, 0.5); // RDP 简化

PathsD trim = Clipper.TrimCollinear(paths);             // 去共线点

// 多边形矩形最小封闭
PathD minRect = Clipper.MinkowskiSum(...);
```

---

## C++ 用法

```cpp
#include "clipper2/clipper.h"
using namespace Clipper2Lib;

PathsD subj{ MakePathD({0,0, 100,0, 100,100, 0,100}) };
PathsD clip{ MakePathD({50,50, 150,50, 150,150, 50,150}) };

auto u = Union(subj, clip, FillRule::NonZero);
auto inflated = InflatePaths(u, 10.0, JoinType::Round, EndType::Polygon);
```

---

## 性能要点

1. **优先 Path64 + 适当 scale**：浮点版内部仍用整数实现，避免精度问题
2. **SimplifyPaths** 在大量数据布尔前预处理，减少顶点
3. **避免共线点**：`TrimCollinear`
4. **大对象用 PolyTree**：避免重新计算外/内环关系
5. **Inflate 注意 miter limit**：尖角处可能产生超大顶点
6. **多线程**：Clipper2 单实例非线程安全，多线程需独立实例

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 输出空集 | 检查 FillRule、方向（逆时针 vs 顺时针）、闭合性 |
| 偏移变形 | 调整 `JoinType` 与 `MiterLimit` |
| 浮点精度异常 | 改用 `Path64` 或 `ClipperD(precision)` |
| 与 Clipper1 不兼容 | API 已变化，参考迁移指南 |

---

## 与其它库对比

| 库 | 语言 | 主要特性 |
|----|------|---------|
| **Clipper2** | C++/C#/Delphi/JS | 高性能布尔+偏移，AGG 兼容 |
| **CGAL Boolean** | C++ | 精确算术，复杂但慢 |
| **JTS / NTS** | Java/.NET | 完整空间分析，速度中等 |
| **Boost.Polygon** | C++ | 仅整数，高性能 |

---

## 参考资源

- 仓库：<https://github.com/AngusJohnson/Clipper2>
- 文档：<http://www.angusj.com/clipper2/Docs/Overview.htm>
- 在线示例：<https://github.com/AngusJohnson/Clipper2/tree/main/CSharp/Clipper2Lib.Examples>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/clipper2/>
