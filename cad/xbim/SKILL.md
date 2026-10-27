---
name: xbim
description: "Use when working with IFC models in .NET/C# via xBIM 6.1 — IfcStore.Open/Create, Instances.OfType<IIfcWall>(), BeginTransaction edits, Xbim3DModelContext geometry to .wexbim, COBie export, or IFC4x3_ADD2 input; also when Xbim.Geometry.Engine.Interop.dll fails to load (x64 + VC++ runtime), geometry is empty because CreateContext was never called, or ToCobieLiteUkAsync is missing since Xbim.Essentials does not ship COBie. xBIM: IFC toolkit with an OCCT-based geometry engine."
tags:
  - bim
  - ifc
  - dotnet
  - csharp
  - geometry
  - occ
  - cobie
---

> **项目地址：** <https://github.com/xBimTeam/XbimEssentials>
>
> **几何引擎：** <https://github.com/xBimTeam/XbimGeometry>
>
> **Web 查看器：** <https://github.com/xBimTeam/XbimWebUI>
>
> **官方文档：** <https://docs.xbim.net/>
>
> **许可证：** CDDL-1.0
>
> **最新稳定版：** Xbim.Essentials 6.1.605（NuGet 当前稳定版，截至 2026-10）；Xbim.Geometry 6.x 只有带 `-netcore` 后缀的包（如 6.3.891-netcore），不加版本时 `dotnet add package` 会装稳定通道最高版 5.1.820

## 概述

xBIM 模块矩阵：

| 包 | 用途 |
|----|------|
| `Xbim.Common` | 基础接口 |
| `Xbim.Ifc` / `Xbim.Ifc2x3` / `Xbim.Ifc4` / `Xbim.Ifc4x3` | IFC 实体类与读写（Essentials 6.x 支持 IFC4x3_ADD2） |
| `Xbim.IO.Esent` / `Xbim.IO.MemoryModel` | 磁盘 / 内存模型 |
| `Xbim.Geometry.Engine` | 基于 OCCT 的几何引擎（C++/CLI） |
| `Xbim.ModelGeometry.Scene` | 几何场景生成（用于可视化） |
| `Xbim.WeXplorer` (`WexBIM` 文件) | WebGL 查看器格式 |
| `Xbim.CobieLiteUk` | COBie 数据交换 |
| `Xbim.Presentation` | WPF 三维展示 |

### 生态家族包

xBIM 由多个独立仓库组成生态家族，常用包如下：

| 包 | 说明 |
|----|------|
| [XbimEssentials](https://github.com/xBimTeam/XbimEssentials) | 核心库：IFC 实体模型、读写与事务 |
| [XbimGeometry](https://github.com/xBimTeam/XbimGeometry) | 基于 OCCT 的几何引擎 |
| [XbimWindowsUI](https://github.com/xBimTeam/XbimWindowsUI) | WPF 桌面三维查看器与控件 |
| [XbimWebUI](https://github.com/xBimTeam/XbimWebUI) | WebGL 浏览器查看器（`xbim-viewer`） |
| [XbimSamples](https://github.com/xBimTeam/XbimSamples) | 官方示例代码 |
| [Xbim.IDS.Validator](https://github.com/xBimTeam/Xbim.IDS.Validator) | IDS（信息交付规范）校验 |
| [XbimCobieExpress](https://github.com/xBimTeam/XbimCobieExpress) | COBie 数据交换 |
| [XbimBCF](https://github.com/xBimTeam/XbimBCF) | BCF（BIM 协同问题）读写 |

---

## 环境准备与安装

### 方式一：NuGet 包（推荐）

```bash
dotnet add package Xbim.Essentials                                   # 6.1.605
dotnet add package Xbim.Geometry                                     # 稳定通道 → 5.1.820
dotnet add package Xbim.Geometry --version 6.3.891-netcore           # 6.x 需显式指定（仅 -netcore 后缀版本）
dotnet add package Xbim.WindowsUI                                    # WPF 控件（可选）

dotnet build                                                         # 验证还原成功
```

### 方式二：源码构建（需要改内核或跟进未发布修复时）

```bash
git clone https://github.com/xBimTeam/XbimEssentials.git
cd XbimEssentials
dotnet build Xbim.Essentials.sln -c Release        # 解决方案文件名以仓库实际为准
dotnet pack -c Release -o ./artifacts              # 产出本地方案包
```

随后把 `artifacts/` 配成本地 NuGet 源（`dotnet nuget add source ./artifacts -n local-xbim`）再引用。

验证安装：

```bash
dotnet build                                       # 还原 + 编译通过即基础链路可用
```

> `Xbim.Geometry` 含 C++/CLI 原生交互层，只有 Windows x64 可直接用；Linux/macOS 上只能用 `Xbim.Essentials` 做模型解析（无几何）。`Xbim.Essentials` 6.1.605 的 nuspec 声明了 .NET Standard 2.0/2.1 与 net8.0/net10.0 目标（release notes 写明 "Support for Net10 added"）；6.0.x 线是 .NET 6 / 8。

---

## 核心 API

xBIM 的核心 API 集中在 `IfcStore`、`Instances` 与几何上下文三处：

| API | 用途 |
|-----|------|
| `IfcStore.Open(path)` | 打开 .ifc/.ifczip/.ifcxml 模型 |
| `IfcStore.Create(creds, schema, storeType)` | 新建 IFC 模型 |
| `model.Instances` | 按类型查询 / 创建实体（`OfType<T>()` / `New<T>()`） |
| `model.BeginTransaction(name)` / `txn.Commit()` | 事务化修改 |
| `model.SaveAs(path)` | 另存为 ifc / ifczip / xbim |
| `Xbim3DModelContext` | 解析几何、导出 WexBIM |

各 API 的完整示例见下文各节。

---

## 打开 IFC

```csharp
using Xbim.Ifc;
using Xbim.Ifc4.Interfaces;

using var model = IfcStore.Open("project.ifc");
foreach (var w in model.Instances.OfType<IIfcWall>())
    Console.WriteLine($"{w.GlobalId} {w.Name}");
```

`IfcStore` 同时支持 .ifc/.ifczip/.ifcxml；亦可保存 `.xbim`（Esent 数据库）作为高速缓存。

---

## 修改并保存

```csharp
using var model = IfcStore.Open("a.ifc", null, null);
using (var txn = model.BeginTransaction("rename walls"))
{
    foreach (var w in model.Instances.OfType<IIfcWall>())
        w.Name = "WALL_" + w.GlobalId;
    txn.Commit();
}
model.SaveAs("b.ifc");
model.SaveAs("b.ifczip");
model.SaveAs("b.xbim");
```

---

## 创建新 IFC 模型

```csharp
using Xbim.Ifc;
using Xbim.Ifc4.MeasureResource;
using Xbim.IO;

var ed = new XbimEditorCredentials {
    ApplicationFullName = "MyApp", ApplicationIdentifier = "MyApp",
    EditorsOrganisationName = "Org", EditorsFamilyName = "Doe",
    EditorsGivenName = "John"
};

using var model = IfcStore.Create(ed, IfcSchemaVersion.Ifc4, XbimStoreType.InMemoryModel);
using (var txn = model.BeginTransaction("init"))
{
    var project = model.Instances.New<Xbim.Ifc4.Kernel.IfcProject>(p => p.Name = "Project");
    // 单位、上下文 / 站点 / 楼宇 / 楼层 ...
    txn.Commit();
}
model.SaveAs("new.ifc");
```

---

## 几何处理与可视化

```csharp
using Xbim.Ifc;
using Xbim.ModelGeometry.Scene;

using var model = IfcStore.Open("a.ifc");
var ctx = new Xbim3DModelContext(model);
ctx.CreateContext();      // 解析几何（耗时，建议缓存为 .xbim）

foreach (var inst in model.Instances.OfType<IIfcProduct>())
{
    var rep = ctx.ShapeInstancesOf(inst);
    foreach (var si in rep)
    {
        // si.BoundingBox / si.Transformation / si.ShapeGeometryLabel
    }
}
```

输出 WexBIM（用于 Web 查看器）：

```csharp
using var s = File.OpenWrite("a.wexbim");
using var bw = new BinaryWriter(s);
ctx.Write(bw);
```

前端用 [`xbim-viewer`](https://github.com/xBimTeam/XbimWebUI) 加载。

---

## 查询常用 IFC 实体

```csharp
foreach (var b in model.Instances.OfType<IIfcBuilding>())   { }
foreach (var s in model.Instances.OfType<IIfcBuildingStorey>()) { }
foreach (var w in model.Instances.OfType<IIfcWall>())       { }
foreach (var d in model.Instances.OfType<IIfcDoor>())       { }
foreach (var p in model.Instances.OfType<IIfcSpace>())      { }

// 属性集
foreach (var pset in model.Instances.OfType<IIfcPropertySet>())
    foreach (var p in pset.HasProperties.OfType<IIfcPropertySingleValue>())
        Console.WriteLine($"{pset.Name}.{p.Name} = {p.NominalValue}");
```

---

## 空间结构遍历

```csharp
var project = model.Instances.OfType<IIfcProject>().FirstOrDefault();
foreach (var rel in project.IsDecomposedBy)
    foreach (var site in rel.RelatedObjects.OfType<IIfcSite>())
        foreach (var br in site.IsDecomposedBy)
            foreach (var bld in br.RelatedObjects.OfType<IIfcBuilding>())
                Console.WriteLine(bld.Name);
```

---

## COBie 输出（资产数据）

```csharp
using Xbim.CobieLiteUk;
using Xbim.IO.CobieLiteUk;

var facility = model.ToCobieLiteUkAsync().Result;
facility.WriteJson("out.json");
facility.WriteXml("out.xml");
facility.WriteXls("out.xlsx", out _);     // Excel 格式（COBie 标准）
```

---

## 性能优化

1. 大文件先缓存为 `.xbim`（Esent）：
   ```csharp
   IfcStore.Open("big.ifc", null, ifcDatabaseSizeThreshHold: 0)  // 强制 Esent
   ```
2. 几何解析昂贵，构建 `Xbim3DModelContext` 后缓存
3. 关闭不需要的实体类型：在 `CreateContext` 中过滤
4. 多线程：`Xbim3DModelContext.MaxThreads = N`
5. WPF 展示用 `Xbim.Presentation` 控件，不要直接绑定大模型

---

## 典型工作流

### 工作流一：IFC 模型读取与属性提取

1. `IfcStore.Open("building.ifc")` 打开 IFC 文件
2. 按类型遍历实体：`model.Instances.OfType<IIfcWall>()` / `<IIfcDoor>()` / `<IIfcSpace>()`
3. 提取属性集：`model.Instances.OfType<IIfcPropertySet>()` → `pset.HasProperties.OfType<IIfcPropertySingleValue>()`
4. 遍历空间结构：`IIfcProject → IsDecomposedBy → IIfcSite → IIfcBuilding → IIfcBuildingStorey`
5. 生成 COBie 数据：`model.ToCobieLiteUkAsync().Result.WriteXls("out.xlsx")`
6. 导出 Web 可视化：`Xbim3DModelContext` → `ctx.Write(bw)` 生成 `.wexbim` 文件

### 工作流二：程序化创建 IFC 模型

1. 创建 `XbimEditorCredentials` 设置作者信息
2. `IfcStore.Create(ed, IfcSchemaVersion.Ifc4, XbimStoreType.InMemoryModel)` 创建空模型
3. `model.BeginTransaction("init")` 开始事务
4. 使用 `model.Instances.New<IfcProject>()` / `New<IfcSite>()` / `New<IfcBuilding>()` 构建空间结构
5. 添加墙/梁/柱/板等建筑元素，设置属性
6. `txn.Commit()` → `model.SaveAs("new.ifc")` 保存

### 工作流三：IFC → 网页可视化（端到端）

输入：`building.ifc`；输出：`building.wexbim` + 一个能加载它的网页。

1. 在 Windows x64 工程里引用 `Xbim.Essentials` 与 `Xbim.Geometry`
2. `var model = IfcStore.Open("building.ifc");`（几何必须基于已打开模型）
3. `var ctx = new Xbim3DModelContext(model); ctx.CreateContext();` 解析几何（耗时，建议把中间结果缓存为 `.xbim`）
4. `using var s = File.Create("building.wexbim"); using var bw = new BinaryWriter(s); ctx.Write(bw);`
5. 前端用 [`xbim-viewer`](https://github.com/xBimTeam/XbimWebUI) 加载该 `.wexbim`，浏览器里检查构件可见、可选中
6. 若页面空白，先回查第 3 步是否真的执行过（未 `CreateContext` 时 `.wexbim` 里没有几何）

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `Xbim.Geometry.Engine.Interop.dll` 加载失败 | 缺 VC++ 运行时；目标平台必须是 x64 |
| 几何精度异常 | 设置 `ModelFactors`；用 OCCT `ShapeFix` |
| Linux 上要几何 | `Xbim.Geometry` 只有 Windows x64 原生库；Linux/macOS 只能做模型解析，或改走 Web 侧 `XbimWebUI` |
| 模型大于 2GB | 切换为 Esent 后端，分批处理 |
| `.wexbim` 里看不到构件 | 几何要先构建：`new Xbim3DModelContext(model).CreateContext()`，再 `Write`；几何引擎仅 Windows x64 可用 |
| 调不到 `ToCobieLiteUkAsync()` | COBie 支持在 `Xbim.CobieLiteUk` 包里，`Xbim.Essentials` 不含，需单独安装 |
| 打开 IFC4x3 文件不识别 | 用 6.x 的 `Xbim.Ifc4x3`（6.x 已支持 IFC4x3_ADD2），5.x 及更早不支持 |
| 另存的 IFC 缺少应用与作者信息 | `IfcStore.Create` / `Open` 时传 `XbimEditorCredentials`（应用名、标识、作者） |
| `dotnet add package Xbim.Geometry` 装到 5.1.820，与 Essentials 6.1 不匹配 | 6.x 线只有 `-netcore` 后缀版本，必须 `--version 6.3.891-netcore` 显式指定 |
| 用 IFC4 接口读 IFC4x3 模型报类型不匹配 | 引用 `Xbim.Ifc4x3` 并用对应命名空间的接口；不要混用 `Xbim.Ifc4.Interfaces` |
| `Instances.New<T>()` 抛异常或实体落不到正确 owner | 新建后要把实体挂到正确的聚合关系（如 `IfcRelContainedInSpatialStructure`），光 `New<T>()` 不会自动建立空间归属 |
| 几何构建后内存持续增长 | `Xbim3DModelContext` 与 `IfcStore` 都要 `Dispose`/`using`；批量处理时逐个模型释放，别在循环里累积 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应遵循 xBIM 的核心流程——`IfcStore.Open("project.ifc")` 读取 → `model.BeginTransaction("name")` 修改 → `txn.Commit()` → `model.SaveAs("out.ifc")` 保存。大文件先缓存为 `.xbim`（Esent 数据库）加速后续操作。几何处理仅在 Windows x64 上可用。
- **关键注意事项**：① `Xbim.Geometry.Engine` 依赖 VC++ 运行时，仅 Windows x64 可用，Linux 仅做模型解析；② 模型大于 2GB 应使用 Esent 后端（`IfcStore.Open(file, null, ifcDatabaseSizeThreshHold: 0)`）；③ `Xbim3DModelContext` 几何解析昂贵，构建后应缓存；④ 事务修改需在 `BeginTransaction`/`Commit` 内完成；⑤ `Xbim.Geometry` 6.x 必须显式指定带 `-netcore` 后缀的版本号。
- **常用代码模式**：读取 IFC：`IfcStore.Open("project.ifc")` → 遍历 `model.Instances.OfType<IIfcWall>()` → 修改属性 → 保存。创建模型：`IfcStore.Create(ed, IfcSchemaVersion.Ifc4, XbimStoreType.InMemoryModel)` → `model.BeginTransaction()` → `model.Instances.New<T>()` → `txn.Commit()` → `model.SaveAs("new.ifc")`。
- **不要臆造**：没有 `Xbim.Geometry.Engine.Performance` 之类可选性能包；COBie 相关 API 来自 `Xbim.CobieLiteUk`，不在 `Xbim.Essentials` 里；Linux/macOS 上没有可用的托管几何引擎替代品。

---

## 相关技能

- **freecad** — 桌面参数化 CAD，BIM 工作台与 IFC 支持：[../freecad/SKILL.md](../freecad/SKILL.md)
- **ifoxcad** — .NET CAD 二次开发框架（同 .NET 生态）：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)
- **occt** — OCCT 几何内核（xBIM 几何引擎的底层）：[../occt/SKILL.md](../occt/SKILL.md)
- **lightcad** — .NET CAD/BIM 平台与插件开发（C# 生态互补）：[../lightcad/SKILL.md](../lightcad/SKILL.md)

---

## 参考资源

- 文档：<https://docs.xbim.net/>
- 示例：<https://github.com/xBimTeam/XbimEssentials/tree/master/Tests>
- WebUI：<https://github.com/xBimTeam/XbimWebUI>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/Xbim/>
