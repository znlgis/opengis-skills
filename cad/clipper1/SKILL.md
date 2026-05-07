---
name: clipper1
description: Clipper（一代）是 Angus Johnson 的开源整数多边形裁剪/偏移库，遵循 Vatti 算法，提供布尔运算（并/交/差/异或）、多边形偏移与简化能力，长期作为 CAD/GIS/CNC 行业的事实标准；目前已被 Clipper2 取代但仍在大量遗留代码中使用。
tags: [2d, geometry, boolean, offset, polygon, csharp, python, cpp]
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

## 典型工作流

### 工作流一：CAD/GIS 中多边形布尔运算

1. 确定浮点精度需求，选定 `scale` 系数（如 1,000,000 表示微米精度）
2. 将输入几何（Polygon/MultiLine 等）转换为 `List<IntPoint>` 格式，乘以 scale 取整
3. 创建 `Clipper` 实例，`AddPath` 添加 Subject 和 Clip
4. 调用 `Execute` 执行布尔运算（Union/Intersect/Difference/Xor）
5. 将结果坐标除以 scale 还原为浮点坐标
6. 如需保留孔洞关系，使用 `PolyTree` 替代 `List<List<IntPoint>>`

### 工作流二：多边形轮廓偏移（生成安全区/缓冲区）

1. 构建多边形路径（闭合路径用 `etClosedPolygon`，开放用 `etOpenButt` 等）
2. 创建 `ClipperOffset`，通过 `AddPaths` 添加输入
3. 调用 `Execute`，正值为外扩（膨胀），负值为内缩（侵蚀）
4. 检查结果是否自交——偏移前可先用 `SimplifyPolygon` 清理输入
5. 输出偏移后的多边形用于刀路生成、安全距离计算等

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

## AI 使用建议

- **推荐工作流模式**：AI 助手应将几何数据统一转换为 Clipper 的整数坐标格式（选择恰当的 scale），然后按「创建 Clipper → 添加路径 → 执行运算 → 还原坐标」的流程处理。对于带孔多边形，优先使用 `PolyTree` 保留层级关系。
- **关键注意事项**：① scale 选择需权衡精度与整数溢出——常用 1e6（微米级）；② Clipper1 的闭合路径不需要重复首点；③ `PolyFillType` 需 Subject 和 Clip 各指定一次，非零环绕（NonZero）是最常用的填充规则；④ Clipper1 为非线程安全，多线程需各自持有实例。
- **常用代码模式**：`new Clipper() → AddPath(subject, ptSubject, true) → AddPath(clip, ptClip, true) → Execute(ctUnion, solution, pftNonZero, pftNonZero)`。

---

## 相关技能

- **clipper2** — 新一代多边形裁剪/偏移库（推荐新项目使用）：[../clipper2/SKILL.md](../clipper2/SKILL.md)
- **qcad** — 2D CAD 软件，内置 DXF 多边形编辑能力：[../qcad/SKILL.md](../qcad/SKILL.md)
- **librecad** — 开源 2D CAD，可用于可视化 Clipper 结果：[../librecad/SKILL.md](../librecad/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/AngusJohnson/Clipper>
- 文档：<http://www.angusj.com/delphi/clipper.php>
- pyclipper：<https://github.com/fonttools/pyclipper>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/clipper1/>
