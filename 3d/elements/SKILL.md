---
name: elements
description: "Use when generating building information models (BIM) programmatically in C#/.NET — wall, beam, column, floor creation, geometry kernel (BREP/CSG), glTF/IFC/JSON serialization, MEP systems, spatial grids. Hypar Elements: the smallest useful BIM — a cross-platform C# library for creating building elements without Revit/Rhino dependencies."
license: MIT
metadata:
  category: 3d
  tags: "dotnet, csharp, 3d, bim, aec, geometry, ifc, gltf, building-elements, parametric"
---

> **项目地址：** <https://github.com/hypar-io/Elements>
>
> **官方文档：** <https://hypar.io/Elements/>
>
> **NuGet：** <https://www.nuget.org/packages/Hypar.Elements>
>
> **许可证：** MIT ｜ **最新版本：** `2.3.0`（截至 2026-11，[NuGet Hypar.Elements](https://www.nuget.org/packages/Hypar.Elements) 最高非预发布版；2.4.0 系列仍为 `-alpha.*` 预发布）

## 概述

Elements 是 Hypar 公司开源的 **建筑信息模型（BIM）编程生成库**，专为 AEC（建筑、结构、机电、施工）领域设计。它以纯 C# 代码创建建筑模型——墙、梁、柱、楼板、空间、机电管道等——**无需启动任何商业 BIM 软件**。

### 核心特性

| 特性 | 说明 |
|------|------|
| 跨平台 | netstandard2.0，支持 Linux/macOS/Windows 微服务 |
| 零商业依赖 | 不依赖 Revit、Rhino 或任何商业几何内核 |
| 混合几何内核 | 简洁的 BREP/CSG 混合内核，擅长"平面带孔"类建模 |
| 多格式序列化 | JSON / glTF / GLB / IFC / DXF / SVG |
| Schema 驱动 | JSON Schema 定义自定义元素类型 + 代码生成 |
| 建筑元素 | Wall / Beam / Column / Floor / Panel / Space / Topography |
| MEP 系统 | Fitting 管件体系（弯头/三通/变径）、流路分析 |
| 空间数据结构 | Grid1d/Grid2d 轴网、HalfEdgeGraph2d、CellComplex、AdaptiveGrid |

---

## 环境准备

### 安装

```bash
# NuGet（推荐）
dotnet add package Hypar.Elements

# 可选包
dotnet add package Hypar.Elements.Serialization.IFC    # IFC 导入导出
dotnet add package Hypar.Elements.Serialization.DXF   # DXF 导入导出
dotnet add package Hypar.Elements.Components           # 组件化生成
dotnet add package Hypar.Elements.CodeGeneration       # JSON Schema → C# 代码生成
```

### 前置条件

- .NET 6.0+ SDK（推荐 .NET 8）
- 无需安装 Revit / Rhino / AutoCAD

---

## 核心 API

### 元素与模型

```csharp
using Elements;
using Elements.Geometry;
using Elements.Serialization.glTF;

// 创建模型
var model = new Model();

// 创建墙
var wall = new Wall(
    line: new Line(new Vector3(0, 0, 0), new Vector3(5, 0, 0)),
    height: 3.0,
    thickness: 0.2
);
model.AddElement(wall);

// 创建柱
var column = new Column(
    location: new Vector3(2.5, 0, 0),
    height: 3.0,
    profile: Profiles.WideFlangeProfile(width: 0.2, depth: 0.3)
);
model.AddElement(column);

// 导出 glTF
model.ToGlTF("output.glb");
```

### 几何系统

```csharp
using Elements.Geometry;

// 向量运算
var a = new Vector3(1, 0, 0);
var b = new Vector3(0, 1, 0);
var cross = a.Cross(b);        // 叉积
var dot = a.Dot(b);            // 点积
var dist = a.DistanceTo(b);    // 距离

// 多边形
var polygon = Polygon.Rectangle(4, 3);
var hole = Polygon.Circle(0.5, 8);
var profile = new Profile(polygon, new[] { hole }); // 带洞轮廓

// 变换
var transform = new Transform(new Vector3(5, 0, 0));
var transformedPolygon = polygon.TransformedPolygon(transform);
```

### 实体操作

```csharp
// 拉伸
var extrude = new Extrude(profile, 3.0, Vector3.ZAxis);

// 扫掠：需要先给出扫掠路径
var path = new Line(new Vector3(0, 0, 0), new Vector3(0, 0, 3));
var sweep = new Sweep(profile, path, angle);

// CSG 布尔运算
var a = new Cube(2, 2, 2);
var b = new Sphere(1.5);
var result = a.Union(b);         // 并集
var diff = a.Subtract(b);        // 差集
var intersect = a.Intersect(b);  // 交集
```

### 序列化

```csharp
// JSON
var json = model.ToJson();
var model2 = Model.FromJson(json);

// glTF/GLB
model.ToGlTF("model.glb");
var model3 = Model.FromGlTF("model.glb");

// IFC（需 Hypar.Elements.Serialization.IFC）
model.ToIFC("model.ifc");
var model4 = Model.FromIFC("model.ifc");
```

---

## 典型工作流

### 创建完整房间模型

```csharp
using Elements;
using Elements.Geometry;

var model = new Model();

// 地板
var floor = Floor.Create(
    profile: Polygon.Rectangle(6, 4),
    thickness: 0.3
);
model.AddElement(floor);

// 四面墙
var roomProfile = Polygon.Rectangle(6, 4);
foreach (var segment in roomProfile.Segments())
{
    var wall = new Wall(segment, height: 3.0, thickness: 0.15);
    model.AddElement(wall);
}

// 柱
for (int x = -2; x <= 2; x += 4)
{
    for (int y = -1; y <= 1; y += 2)
    {
        var col = new Column(
            location: new Vector3(x, y, 0),
            height: 3.0,
            profile: Profiles.WideFlangeProfile(0.15, 0.25)
        );
        model.AddElement(col);
    }
}

// 导出
model.ToGlTF("room.glb");
```

---

## 最佳实践

1. **精度控制**：使用 `Vector3.Epsilon = 1e-05` 进行浮点比较，使用 `IsAlmostEqualTo()` 等辅助方法
2. **坐标系**：右手坐标系，+Z 朝上，无量纲（除非方法明确要求）
3. **实例化**：使用 Element Instance 模式复用定义，避免重复创建相同构件
4. **Schema 扩展**：通过 JSON Schema + CodeGeneration 定义自定义元素类型

---

## 常见问题

| 问题 / 报错 | 原因 | 处置 |
|------|------|------|
| `NU1102: Unable to find package Hypar.Elements with version (>= 2.4.0)` | 2.4.x 只有 `-alpha.*` 预发布版，默认还原不拉预发布 | 生产项目锁 `2.3.0`；确需尝鲜加 `--prerelease` 或显式写 `2.4.0-alpha.*` |
| 跨平台几何比较结果不一致 | 浮点累计误差，且不同 CPU/运行时 FMA 行为不同 | 用 `Vector3.Epsilon` 与 `IsAlmostEqualTo()`，不要用 `==` 比坐标 |
| 导出的 glTF 在 Revit/其他工具里没有构件 | 只导出了几何，或导出前没把元素 `Add` 进 `Model` | 先 `model.AddElement(...)` 再 `model.ToGlTF()`；要进 Revit 走 IFC 中转，并装 `Hypar.Elements.Serialization.IFC` |
| Linux 容器里加载失败 / 找不到原生库 | 用了依赖 Windows 原生库的包路径 | 核心库是 `netstandard2.0`，可跑 Linux Docker；避免引入 Windows-only 依赖 |
| 自定义元素反序列化后属性丢失 | JSON Schema 与 C# 属性名不一致，或没生成对应 code | 检查 Schema 的属性名与类型定义，再跑 CodeGeneration 重新生成 |
| 升级后 `Wall` / `Floor` 等 API 编译不过 | 跨大版本 API 签名有调整 | 对照 [CHANGELOG](https://github.com/hypar-io/Elements/blob/master/CHANGELOG.md) 改调用；不确定时先锁回上一稳定版 |

---

## AI 使用建议

### 推荐工作流

1. **创建 Model**：`new Model()` → 添加建筑元素（Wall/Column/Floor/Beam）
2. **几何构建**：使用 `Polygon.Rectangle()`、`Vector3`、`Line` 构建几何轮廓
3. **实体操作**：`Extrude`（拉伸）、`Sweep`（扫掠）、CSG 布尔运算（Union/Subtract/Intersect）
4. **序列化导出**：`model.ToGlTF()`（推荐 glTF/GLB）、`model.ToJson()`、`model.ToIFC()`（需额外包）
5. **自定义元素**：继承 `Element`，用 JSON Schema 定义属性，通过 CodeGeneration 生成代码

### 关键注意事项

- **坐标系**：右手坐标系，+Z 朝上，无量纲
- **浮点比较**：使用 `Vector3.Epsilon` 和 `IsAlmostEqualTo()`，不要直接用 `==`
- **零依赖**：不依赖 Revit/Rhino，可完全在 Linux Docker 中运行
- **IFC 导出**：需额外安装 `Hypar.Elements.Serialization.IFC` 包
- **实例化复用**：相同构件使用 Element Instance 模式，避免重复创建

---

## 相关技能

- **opencsg-net** — .NET CSG 建模库：[../opencsg-net/SKILL.md](../opencsg-net/SKILL.md)
- **ara3d-sdk** — .NET 高性能三维/BIM 库：[../ara3d-sdk/SKILL.md](../ara3d-sdk/SKILL.md)
- **xbim** — .NET BIM/IFC 工具集：[../../cad/xbim/SKILL.md](../../cad/xbim/SKILL.md)
- **freecad** — 开源参数化 3D CAD/BIM：[../../cad/freecad/SKILL.md](../../cad/freecad/SKILL.md)

---

## 参考资源

- [Elements 官方文档](https://hypar.io/Elements/)
- [Elements 测试代码](https://github.com/hypar-io/Elements/tree/master/Elements/test) — 官方推荐的用法示例
- [Elements Playground](https://hypar.io/Elements/Playground/) — 浏览器端实时代码编辑
- [CHANGELOG](https://github.com/hypar-io/Elements/blob/master/CHANGELOG.md) — 版本更新记录
