---
name: xbim
description: "Use when processing BIM/IFC data in .NET/C# �?IFC reading/writing, model validation, quantity takeoff, geometry extraction. xBIM: .NET BIM/IFC toolkit for building information modeling workflows."
tags: [bim, ifc, dotnet, csharp, geometry, occ]
---

> **项目地址�?* <https://github.com/xBimTeam/XbimEssentials>
>
> **几何引擎�?* <https://github.com/xBimTeam/XbimGeometry>
>
> **Web 查看器：** <https://github.com/xBimTeam/XbimWebUI>
>
> **官方文档�?* <https://docs.xbim.net/>
>
> **许可证：** CDDL-1.0

## 概述

xBIM 模块矩阵�?

| �?| 用�?|
|----|------|
| `Xbim.Common` | 基础接口 |
| `Xbim.Ifc` / `Xbim.Ifc2x3` / `Xbim.Ifc4` / `Xbim.Ifc4x3` | IFC 实体类与读写（最�?Essentials v6.0.x 支持 IFC4x3_ADD2�?|
| `Xbim.IO.Esent` / `Xbim.IO.MemoryModel` | 磁盘 / 内存模型 |
| `Xbim.Geometry.Engine` | 基于 OCCT 的几何引擎（C++/CLI�?|
| `Xbim.ModelGeometry.Scene` | 几何场景生成（用于可视化�?|
| `Xbim.WeXplorer` (`WexBIM` 文件) | WebGL 查看器格�?|
| `Xbim.CobieLiteUk` | COBie 数据交换 |
| `Xbim.Presentation` | WPF 三维展示 |

---

## 安装

```bash
dotnet add package Xbim.Essentials
dotnet add package Xbim.Geometry           # �?C++/CLI，仅 Windows x64 直接可用
dotnet add package Xbim.WindowsUI          # WPF 控件（可选）
```

> Linux/macOS：使�?`Xbim.Geometry` 受限；可改用 `Xbim.Essentials` 仅做模型解析。`Xbim.Essentials`（当�?v6.0.x）多目标 **.NET 6 / .NET 8**�?

---

## 打开 IFC

```csharp
using Xbim.Ifc;
using Xbim.Ifc4.Interfaces;

using var model = IfcStore.Open("project.ifc");
foreach (var w in model.Instances.OfType<IIfcWall>())
    Console.WriteLine($"{w.GlobalId} {w.Name}");
```

`IfcStore` 同时支持 .ifc/.ifczip/.ifcxml；亦可保�?`.xbim`（Esent 数据库）作为高速缓存�?

---

## 修改并保�?

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

## 创建�?IFC 模型

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
ctx.CreateContext();      // 解析几何（耗时，建议缓存为 .xbim�?

foreach (var inst in model.Instances.OfType<IIfcProduct>())
{
    var rep = ctx.ShapeInstancesOf(inst);
    foreach (var si in rep)
    {
        // si.BoundingBox / si.Transformation / si.ShapeGeometryLabel
    }
}
```

输出 WexBIM（用�?Web 查看器）�?

```csharp
using var s = File.OpenWrite("a.wexbim");
using var bw = new BinaryWriter(s);
ctx.Write(bw);
```

前端�?[`xbim-viewer`](https://github.com/xBimTeam/XbimWebUI) 加载�?

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
facility.WriteXls("out.xlsx", out _);     // Excel 格式（COBie 标准�?
```

---

## 性能优化

1. 大文件先缓存�?`.xbim`（Esent）：
   ```csharp
   IfcStore.Open("big.ifc", null, ifcDatabaseSizeThreshHold: 0)  // 强制 Esent
   ```
2. 几何解析昂贵，构�?`Xbim3DModelContext` 后缓�?
3. 关闭不需要的实体类型：在 `CreateContext` 中过�?
4. 多线程：`Xbim3DModelContext.MaxThreads = N`
5. WPF 展示�?`Xbim.Presentation` 控件，不要直接绑定大模型

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `Xbim.Geometry.Engine.Interop.dll` 加载失败 | �?VC++ 运行时；目标平台必须�?x64 |
| 几何精度异常 | 设置 `ModelFactors`；用 OCCT `ShapeFix` |
| Linux 上几�?| 使用 .NET 几何引擎（受限），或迁移�?`Xbim.WebUI` |
| 模型大于 2GB | 切换�?Esent 后端，分批处�?|

---

## AI 使用建议

- **推荐工作流模�?*：AI 助手应遵�?xBIM 的核心流程——`IfcStore.Open("project.ifc")` 读取 �?`model.BeginTransaction("name")` 修改 �?`txn.Commit()` �?`model.SaveAs("out.ifc")` 保存。大文件先缓存为 `.xbim`（Esent 数据库）加速后续操作。几何处理仅�?Windows x64 上可用�?
- **关键注意事项**：① `Xbim.Geometry.Engine` 依赖 VC++ 运行时，�?Windows x64 可用，Linux 仅做模型解析；② 模型大于 2GB 应使�?Esent 后端（`IfcStore.Open(file, null, ifcDatabaseSizeThreshHold: 0)`）；�?`Xbim3DModelContext` 几何解析昂贵，构建后应缓存；�?事务修改需�?`BeginTransaction`/`Commit` 内完成�?
- **常用代码模式**：读�?IFC：`IfcStore.Open("project.ifc")` �?遍历 `model.Instances.OfType<IIfcWall>()` �?修改属�?�?保存。创建模型：`IfcStore.Create(ed, IfcSchemaVersion.Ifc4, XbimStoreType.InMemoryModel)` �?`model.BeginTransaction()` �?`model.Instances.New<T>()` �?`txn.Commit()` �?`model.SaveAs("new.ifc")`�?

---

## 相关技�?

- **freecad** �?桌面参数�?CAD，BIM 工作台与 IFC 支持：[../freecad/SKILL.md](../freecad/SKILL.md)
- **ifoxcad** �?.NET CAD 二次开发框架（�?.NET 生态）：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)
- **occt** �?OCCT 几何内核（xBIM 几何引擎的底层）：[../occt/SKILL.md](../occt/SKILL.md)

---

## 典型工作�?

### 工作流一：IFC 模型读取与属性提�?

1. `IfcStore.Open("building.ifc")` 打开 IFC 文件
2. 按类型遍历实体：`model.Instances.OfType<IIfcWall>()` / `<IIfcDoor>()` / `<IIfcSpace>()`
3. 提取属性集：`model.Instances.OfType<IIfcPropertySet>()` �?`pset.HasProperties.OfType<IIfcPropertySingleValue>()`
4. 遍历空间结构：`IIfcProject �?IsDecomposedBy �?IIfcSite �?IIfcBuilding �?IIfcBuildingStorey`
5. 生成 COBie 数据：`model.ToCobieLiteUkAsync().Result.WriteXls("out.xlsx")`
6. 导出 Web 可视化：`Xbim3DModelContext` �?`ctx.Write(bw)` 生成 `.wexbim` 文件

### 工作流二：程序化创建 IFC 模型

1. 创建 `XbimEditorCredentials` 设置作者信�?
2. `IfcStore.Create(ed, IfcSchemaVersion.Ifc4, XbimStoreType.InMemoryModel)` 创建空模�?
3. `model.BeginTransaction("init")` 开始事�?
4. 使用 `model.Instances.New<IfcProject>()` / `New<IfcSite>()` / `New<IfcBuilding>()` 构建空间结构
5. 添加�?�?�?板等建筑元素，设置属�?
6. `txn.Commit()` �?`model.SaveAs("new.ifc")` 保存

---

## 参考资�?

- 文档�?https://docs.xbim.net/>
- 示例�?https://github.com/xBimTeam/XbimEssentials/tree/master/Tests>
- WebUI�?https://github.com/xBimTeam/XbimWebUI>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/xbim/>