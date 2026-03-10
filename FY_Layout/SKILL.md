---
name: FY_Layout
description: FY_Layout 是飞扬集成设计平台的场地布置二次开发插件示例，基于 LightCAD 框架和 C# 语言，提供围栏、草坪、基坑、道路、板房、场地、硬化地面、土方回填等建筑工程场布元素的二维绘制与三维建模能力。
---

> **项目地址：** <https://github.com/znlgis/FY_Layout>
>
> **所属平台：** 飞扬集成设计平台（LightCAD / LightBIM）
>
> **许可证：** CC-BY-NC 4.0

## 概述

FY_Layout 是飞扬集成设计平台（LightCAD）的 **场地布置二次开发插件示例**，面向建筑工程设计行业，提供二维绘制与三维建模的完整插件示例源代码。该项目演示了如何基于飞扬平台 SDK 进行 C# 插件开发，涵盖元素定义、命令注册、2D/3D Action 编写及形状/实体 Provider 实现等核心流程。

项目包含两个核心模块：

| 模块 | 项目名 | 说明 |
|------|--------|------|
| 插件主体 | `QdLayout` | 场布插件——元素类型定义、命令注册、UI 菜单、2D/3D Action 实现 |
| 形状提供者 | `QdLayoutProvider` | 元素的二维形状（Shape）和三维实体（Solid）生成逻辑 |

**技术栈：**

- 开发语言：C#
- 目标框架：.NET 8.0（net8.0-windows）
- 开发环境：Visual Studio 2022 社区版（17.5.5+）
- UI 框架：WinForms
- 图形引擎：SkiaSharp（2D）、ThreeJs4Net / OpenTK（3D）
- 数据格式：兼容 DWG/DXF

---

## 开发环境准备

### 前置条件

- Visual Studio 2022 社区版（17.5.5 以上）
- .NET 8.0 SDK
- 飞扬主程序（`飞扬主程序/lightcad.EXE`，项目仓库内已包含）

### 克隆与编译

```bash
git clone https://github.com/znlgis/FY_Layout.git
cd FY_Layout
# 使用 VS2022 打开 LightBIM.sln
```

### 调试方式

飞扬最新组件和启动程序为 `飞扬主程序/lightcad.EXE`。编译后使用 VS2022 **附加进程** 的方式进行断点调试。

---

## 项目结构

```
FY_Layout/
├── LightBIM.sln                  # 解决方案文件
├── Libs/                         # 飞扬平台 SDK DLL（LightCAD.Core、LightCAD.Drawing 等）
├── 飞扬主程序/                    # 飞扬主程序 lightcad.EXE
├── Build/                        # 编译输出目录
├── QdLayout/                     # ★ 插件主体项目
│   ├── QdLayout.csproj
│   ├── GlobalUsing.cs            # 全局 using 声明
│   ├── LayoutPlugin.cs           # ★ 插件入口（ILcPlugin 实现）
│   ├── LayoutCmds.cs             # ★ 命令注册（[CommandClass] / [CommandMethod]）
│   ├── LayoutElementType.cs      # ★ 场布元素类型定义
│   ├── LcCurveChangeLoop.cs      # 曲线转换为闭合环工具类
│   ├── Barrier/                  # 防护栏杆
│   ├── Berm/                     # 出土道路
│   ├── Earthwork/                # 土方回填
│   ├── Equipment/                # 场布设备
│   ├── Fence/                    # 围栏（围墙）
│   ├── FoundationPit/            # 基坑
│   ├── Ground/                   # 硬化地面
│   ├── Harden/                   # 路面硬化
│   ├── Lawn/                     # 草坪
│   ├── OpenLine/                 # 开门边线
│   ├── PlanBuild/                # 拟建建筑
│   ├── PlateHouse/               # 板房 / 板房楼栋
│   ├── PropertyLine/             # 用地红线
│   ├── Road/                     # 城市道路 / 交叉路口
│   ├── Site/                     # 场地
│   └── TemplateArrange/          # 模板排布方案
└── QdLayoutProvider/             # ★ 形状/实体提供者项目
    ├── QdLayoutProvider.csproj
    ├── GlobalUsing.cs
    ├── QdLayoutProviderRegist.cs # Provider 注册入口（IDllProviderImporter）
    ├── QdLayoutProviderUtils.cs  # Provider 工具方法
    ├── QdBermProvider.cs         # 出土道路 Shape/Solid
    ├── QdFoundationPitProvider.cs# 基坑 Shape/Solid
    ├── QdGroundProvider.cs       # 硬化地面 Shape/Solid
    ├── QdEarthworkProvider.cs    # 土方回填 Shape/Solid
    ├── QdHardenProvider.cs       # 路面硬化 Shape/Solid
    ├── QdLawnProvider.cs         # 草坪 Shape/Solid
    ├── QdFenceProvider.cs        # 围栏 Shape/Solid
    ├── QdSiteProvider.cs         # 场地 Shape
    ├── QdBarrierProvider.cs      # 防护栏杆 Shape/Solid
    └── QdIntersectionProvider.cs # 交叉路口 Shape/Solid
```

---

## NuGet 包体系

FY_Layout 将飞扬平台 SDK 封装为 NuGet 包，每个包对应一个架构层，通过分层依赖向上组合。所有 SDK 程序集均放置在包内的 `ref/{tfm}/` 目录下，属于 **编译期引用**（compile-time only）——NuGet 不会将其复制到消费者的输出目录，因此插件开发者无需配置 `Private=false` 或 `ExcludeAssets="runtime"`，飞扬主程序在运行时自动提供这些 DLL。

### NuGet 包一览

| NuGet 包 ID | 架构层 | 包含程序集 | 依赖包 |
|------------|--------|-----------|--------|
| `Fs.FY.LightCAD.Core` | 核心层 | `LightCAD.Core`、`LightCAD.MathLib`、`LightCAD.Runtime` | — |
| `Fs.FY.LightCAD.Render` | 渲染层 | `LightCAD.RenderUtils`、`ThreeJs4Net` | Core |
| `Fs.FY.LightCAD.Drawing` | 绘图层 | `LightCAD.Drawing`、`LightCAD.Drawing.Actions`、`LightCAD.Component.Actions` | Core |
| `Fs.FY.LightCAD.Data` | 数据层 | `LightCAD.Model`、`LightCAD.DBUtility`、`LightCAD.DBHelper`、`Dapper`、`System.Data.SQLite` | Core |
| `Fs.FY.LightCAD.IO` | I/O 层 | `netDxf`、`Newtonsoft.Json`、`Svg`、`LightCAD.ImpExpDwg` | Core |
| `Fs.FY.LightCAD.UI` | UI/OpenGL 层 | `OpenTK`、`OpenTK.WinForms`、`WinFormsUI`、`Flee` | Core、Render |
| `Fs.FY.Layout` | 场布插件 | QdLayout 插件主体 | Core、Render、Drawing、Data、IO、UI |
| `Fs.FY.Layout.Provider` | 场布 Provider | QdLayoutProvider 形状/实体提供者 | Core、Render |

### 包依赖关系

```
Fs.FY.LightCAD.Core
├── Fs.FY.LightCAD.Render  (→ Core)
│   └── Fs.FY.LightCAD.UI  (→ Core + Render)
├── Fs.FY.LightCAD.Drawing (→ Core)
├── Fs.FY.LightCAD.Data    (→ Core)
├── Fs.FY.LightCAD.IO      (→ Core)
│
├── Fs.FY.Layout           (→ Core + Render + Drawing + Data + IO + UI)
└── Fs.FY.Layout.Provider  (→ Core + Render)
```

### 各包程序集与命名空间

| NuGet 包 | 程序集 / DLL | 命名空间 | 主要用途 |
|---------|------------|---------|---------|
| `Fs.FY.LightCAD.Core` | `LightCAD.Core.dll` | `LightCAD.Core` | 元素类型 `ElementType`、文档 `LcDocument`、运行时 `LcRuntime`、组件定义 |
| `Fs.FY.LightCAD.Core` | `LightCAD.MathLib.dll` | `LightCAD.MathLib` | `Vector2/3`、`Line2d`、`Arc2d`、`Polyline2d`、`Curve2dGroup`、`Curve2dGroupCollection` 等 |
| `Fs.FY.LightCAD.Core` | `LightCAD.Runtime.dll` | `LightCAD.Runtime` | `CommandClass`、`CommandMethod`、`TabItem`、`TabButton` 等特性和 UI 类 |
| `Fs.FY.LightCAD.Render` | `LightCAD.RenderUtils.dll` | `LightCAD.RenderUtils` | 渲染工具 |
| `Fs.FY.LightCAD.Render` | `ThreeJs4Net.dll` | `ThreeJs4Net` | 三维引擎——`Shape`、`Solid3d`、`Surface3d`、`GeometryData` 等 |
| `Fs.FY.LightCAD.Drawing` | `LightCAD.Drawing.dll` | `LightCAD.Drawing` | 绘图文档——图层、图纸、绘制管理 |
| `Fs.FY.LightCAD.Drawing` | `LightCAD.Drawing.Actions.dll` | `LightCAD.Drawing.Actions` | 绘图交互动作基类——`IDocumentEditor`、点拾取、线拾取 |
| `Fs.FY.LightCAD.Drawing` | `LightCAD.Component.Actions.dll` | `LightCAD.Component.Actions` | 通用组件动作 |
| `Fs.FY.LightCAD.Data` | `LightCAD.Model.dll` | `LightCAD.Model` | 模型管理 |
| `Fs.FY.LightCAD.Data` | `LightCAD.DBUtility.dll` / `LightCAD.DBHelper.dll` | `LightCAD.DBUtility` | 数据库工具与 SQLite 访问 |
| `Fs.FY.LightCAD.Data` | `Dapper.dll` | `Dapper` | 轻量 ORM |
| `Fs.FY.LightCAD.Data` | `System.Data.SQLite.dll` | `System.Data.SQLite` | SQLite 驱动 |
| `Fs.FY.LightCAD.IO` | `netDxf.dll` | `netDxf` | DXF 格式支持 |
| `Fs.FY.LightCAD.IO` | `Newtonsoft.Json.dll` | `Newtonsoft.Json` | JSON 序列化 |
| `Fs.FY.LightCAD.IO` | `Svg.dll` / `LightCAD.ImpExpDwg.dll` | — | SVG 及 DWG 导入导出 |
| `Fs.FY.LightCAD.UI` | `OpenTK.dll` / `OpenTK.WinForms.dll` | `OpenTK` | OpenGL 绑定与 WinForms 集成 |
| `Fs.FY.LightCAD.UI` | `WinFormsUI.dll` | — | UI 扩展控件 |
| `Fs.FY.LightCAD.UI` | `Flee.dll` | `Flee` | 表达式求值器 |

### 在新插件中引用 NuGet 包

以开发一个与 QdLayout 同级的新插件为例（仅需绘图和核心能力）：

```xml
<!-- MyPlugin/MyPlugin.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWindowsForms>true</UseWindowsForms>

    <!-- NuGet 包元数据 -->
    <PackageId>Fs.FY.MyPlugin</PackageId>
    <Description>我的飞扬插件</Description>
    <IsPackable>true</IsPackable>
  </PropertyGroup>

  <!--
    引用飞扬平台 NuGet 包（编译期引用，运行时由主程序提供 DLL）。
    按需选择所需架构层，未用到的层不必引用。
  -->
  <ItemGroup>
    <!-- 必选：核心层（元素类型、数学库、运行时） -->
    <PackageReference Include="Fs.FY.LightCAD.Core" Version="1.0.0" />
    <!-- 按需：二维绘图交互层 -->
    <PackageReference Include="Fs.FY.LightCAD.Drawing" Version="1.0.0" />
    <!-- 按需：三维渲染层 -->
    <PackageReference Include="Fs.FY.LightCAD.Render" Version="1.0.0" />
    <!-- 按需：UI/OpenGL 层 -->
    <PackageReference Include="Fs.FY.LightCAD.UI" Version="1.0.0" />
  </ItemGroup>
</Project>
```

如果开发 Provider（形状/实体提供者）插件，只需引用 Core 和 Render：

```xml
<!-- MyProvider/MyProvider.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <PackageId>Fs.FY.MyPlugin.Provider</PackageId>
    <IsPackable>true</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Fs.FY.LightCAD.Core" Version="1.0.0" />
    <PackageReference Include="Fs.FY.LightCAD.Render" Version="1.0.0" />
  </ItemGroup>
</Project>
```

> **注意：** 因为所有 SDK DLL 都放置在包的 `ref/{tfm}/` 目录中，NuGet 只将其作为编译时引用，**不会**将 DLL 复制到插件输出目录。飞扬主程序（`lightcad.EXE`）在运行时负责提供这些程序集，因此插件 DLL 保持轻量。

### 打包与发布

在仓库根目录使用 `dotnet pack` 生成 NuGet 包：

```bash
# 构建并打包所有层包（输出到 Build/Packages/）
dotnet pack Fs.FY.LightCAD.Core/Fs.FY.LightCAD.Core.csproj -c Release
dotnet pack Fs.FY.LightCAD.Render/Fs.FY.LightCAD.Render.csproj -c Release
dotnet pack Fs.FY.LightCAD.Drawing/Fs.FY.LightCAD.Drawing.csproj -c Release
dotnet pack Fs.FY.LightCAD.Data/Fs.FY.LightCAD.Data.csproj -c Release
dotnet pack Fs.FY.LightCAD.IO/Fs.FY.LightCAD.IO.csproj -c Release
dotnet pack Fs.FY.LightCAD.UI/Fs.FY.LightCAD.UI.csproj -c Release

# 打包场布插件主体（输出到 Build/）
dotnet pack QdLayout/QdLayout.csproj -c Release

# 打包场布 Provider（输出到 Build/Providers/）
dotnet pack QdLayoutProvider/QdLayoutProvider.csproj -c Release
```

全局版本号在 `Directory.Build.props` 中统一维护：

```xml
<!-- Directory.Build.props -->
<PropertyGroup>
  <Version>1.0.0</Version>
  <Authors>znlgis</Authors>
  <Company>飞扬集成设计平台</Company>
  <PackageProjectUrl>https://github.com/znlgis/FY_Layout</PackageProjectUrl>
  <PackageTags>FeiYang;LightCAD;BIM;CAD;Layout;Construction;Architecture</PackageTags>
</PropertyGroup>
```

---

## 核心 SDK 引用一览

| DLL | 所在 NuGet 包 | 命名空间 | 用途 |
|-----|-------------|---------|------|
| `LightCAD.Core.dll` | `Fs.FY.LightCAD.Core` | `LightCAD.Core` | ★ 核心——元素类型 `ElementType`、文档 `LcDocument`、运行时 `LcRuntime`、组件定义等 |
| `LightCAD.Drawing.dll` | `Fs.FY.LightCAD.Drawing` | `LightCAD.Drawing` | 绘图文档——图层、图纸、绘制管理 |
| `LightCAD.Drawing.Actions.dll` | `Fs.FY.LightCAD.Drawing` | `LightCAD.Drawing.Actions` | 绘图交互动作基类——`IDocumentEditor`、点拾取、线拾取等 |
| `LightCAD.MathLib.dll` | `Fs.FY.LightCAD.Core` | `LightCAD.MathLib` | 数学库——`Vector2`、`Vector3`、`Line2d`、`Arc2d`、`Polyline2d`、`Color` 等 |
| `LightCAD.Model.dll` | `Fs.FY.LightCAD.Data` | `LightCAD.Model` | 模型管理 |
| `LightCAD.Runtime.dll` | `Fs.FY.LightCAD.Core` | `LightCAD.Runtime` | 运行时框架——`CommandClass`、`CommandMethod`、`TabItem`、`TabButton` 等特性和 UI 类 |
| `LightCAD.RenderUtils.dll` | `Fs.FY.LightCAD.Render` | `LightCAD.RenderUtils` | 渲染工具 |
| `ThreeJs4Net.dll` | `Fs.FY.LightCAD.Render` | `ThreeJs4Net` | 三维引擎——`Shape`、`Solid3d`、`Surface3d`、`GeometryData` 等 |
| `OpenTK.dll` | `Fs.FY.LightCAD.UI` | `OpenTK` | OpenGL 绑定 |
| `Newtonsoft.Json.dll` | `Fs.FY.LightCAD.IO` | `Newtonsoft.Json` | JSON 序列化 |

---

## 插件开发核心概念

### 1. 插件入口（ILcPlugin）

每个飞扬插件必须实现 `ILcPlugin` 接口，在 `Loaded()` 中注册元素类型和 Action，在 `Completed()` 中初始化 UI。

```csharp
using LightCAD.Runtime;
using LightCAD.Core;

namespace QdLayout
{
    public class LayoutPlugin : ILcPlugin
    {
        // 定义 UI 菜单 Tab
        public static TabItem LayoutItem = new TabItem
        {
            Name = "LayoutMajor",
            Text = "场布",
            ShortcutKey = "ALT-L",
            ButtonGroups = new List<TabButtonGroup> { /* ... */ }
        };

        public void InitUI() { }

        public void Loaded()
        {
            // 注册元素类型
            LcDocument.RegistElementTypes(LayoutElementType.All);
            // 注册程序集
            LcRuntime.RegistAssemblies.Add("QdLayout");
            // 注册 2D Action
            LcDocument.ElementActions.Add(LayoutElementType.Lawn, new LawnAction());
            // 注册 3D Action
            LcDocument.Element3dActions.Add(LayoutElementType.Lawn, new Lawn3dAction());
            // ... 其他元素注册
        }

        public void Completed()
        {
            // 将 TabItem 添加到 UI
            AppRuntime.UISystem.AddInitTabItems([LayoutItem]);
        }

        public void OnInitializeDocRt(DocumentRuntime docRt) { }
        public void OnDisposeDocRt(DocumentRuntime docRt) { }
    }
}
```

### 2. 元素类型定义（ElementType）

通过静态字段定义场布元素，每个元素包含唯一 GUID、名称、显示名和实体类型：

```csharp
using LightCAD.Core;

namespace QdLayout
{
    public static class LayoutElementType
    {
        public static ElementType Lawn = new ElementType
        {
            Guid = Guid.ParseExact("{63A566EA-3702-A98C-7A6B-8DBEA6B3F41A}", "B").ToLcGuid(),
            Name = "Lawn",
            DispalyName = "草坪",
            ClassType = typeof(QdLawn)
        };

        public static ElementType FoundationPit = new ElementType
        {
            Guid = Guid.ParseExact("{C082E6EA-E099-94AB-50FA-50DF72D286D4}", "B").ToLcGuid(),
            Name = "FoundationPit",
            DispalyName = "基坑",
            ClassType = typeof(QdFoundationPit)
        };

        // ... 其他元素类型

        public static ElementType[] All = new ElementType[]
        {
            Lawn, FoundationPit, Road, Earthwork, Berm, Harden,
            Site, PropertyLine, Fence, PlateBuilding, PlateBuildGroup, OpenLine
        };
    }
}
```

### 3. 命令注册（CommandClass / CommandMethod）

使用 `[CommandClass]` 和 `[CommandMethod]` 特性注册绘图命令：

```csharp
using LightCAD.Runtime.Interface;

namespace QdLayout
{
    [CommandClass]
    public class LayoutCmds
    {
        [CommandMethod(Name = "Fence", ShortCuts = "W")]
        public CommandResult DrawWall(IDocumentEditor docEditor, string[] args)
        {
            var fenceAction = new FenceAction(docEditor);
            fenceAction.ExecCreate(args);
            return CommandResult.Succ();
        }

        [CommandMethod(Name = "Lawn", ShortCuts = "LW")]
        public CommandResult DrawLawn(IDocumentEditor docEditor, string[] args)
        {
            var lawnAction = new LawnAction(docEditor);
            lawnAction.ExecCreatePoly(args);
            return CommandResult.Succ();
        }

        [CommandMethod(Name = "FoundationPit", ShortCuts = "FDP")]
        public CommandResult DrawFoundationPit(IDocumentEditor docEditor, string[] args)
        {
            var fdpAction = new FoundationPitAction(docEditor);
            fdpAction.ExecCreatePoly(args);
            return CommandResult.Succ();
        }
    }
}
```

### 4. UI 菜单定义（TabItem / TabButton）

通过 `TabItem`、`TabButtonGroup`、`TabButton` 构建插件工具栏菜单：

```csharp
public static TabItem LayoutItem = new TabItem
{
    Name = "LayoutMajor",
    Text = "场布",
    ShortcutKey = "ALT-L",
    ButtonGroups = new List<TabButtonGroup>
    {
        new TabButtonGroup
        {
            Buttons = new List<TabButton>
            {
                new TabButton
                {
                    Name = "Lawn",
                    Text = "草坪",
                    Icon = Properties.Resources.草地,
                    IsCommand = true,
                    DropDowns = new List<TabButton>
                    {
                        new TabButton { Name = "Lawn", Text = "任意绘制", IsCommand = true },
                        new TabButton { Name = "LawnRec", Text = "矩形绘制", IsCommand = true },
                        new TabButton { Name = "LawnChange", Text = "转换多段线", IsCommand = true },
                    }
                },
                // ... 更多按钮
            }
        }
    }
};
```

---

## 场布元素一览

| 元素名称 | ElementType 名 | 实体类 | 2D Action | 3D Action | 说明 |
|---------|---------------|--------|-----------|-----------|------|
| 草坪 | `Lawn` | `QdLawn` | `LawnAction` | `Lawn3dAction` | 支持任意绘制、矩形绘制、多段线转换 |
| 围栏 | `Fence` | `QdFence` | `FenceAction` | `Fence3dAction` | 围墙绘制 |
| 拟建建筑 | `PlanBuild` | `QdPlanBuild` | `PlanBuildAction` | `PlanBuild3dAction` | 支持多段线拾取创建 |
| 基坑 | `FoundationPit` | `QdFoundationPit` | `FoundationPitAction` | `FoundationPit3dAction` | 支持任意绘制、矩形绘制、多段线转换 |
| 硬化地面 | `Ground` | `QdGround` | `GroundAction` | `Ground3dAction` | 支持任意绘制、矩形绘制、多段线转换 |
| 土方回填 | `Earthwork` | `QdEarthwork` | `EarthworkAction` | `Earthwork3dAction` | 支持任意绘制、矩形绘制、多段线转换 |
| 出土道路 | `Berm` | `QdBerm` | `BermAction` | `Berm3dAction` | 基线+宽度绘制 |
| 防护栏杆 | `Barrier` | `QdBarrier` | `BarrierAction` | `Barrier3dAction` | 线性防护构件 |
| 路面硬化 | `Harden` | `QdHarden` | `HardenAction` | `Harden3dAction` | 支持任意绘制、矩形绘制、多段线转换 |
| 城市道路 | `Road` | `QdRoad` | `RoadAction` | `Road3dAction` | 道路绘制 |
| 场地 | `Site` | `QdSite` | `SiteAction` | `Site3dAction` | 支持任意绘制、矩形绘制、多段线转换 |
| 用地红线 | `PropertyLine` | `QdPropertyLine` | `PropertyLineAction` | — | 支持任意绘制、矩形绘制、多段线转换 |
| 板房 | `PlateBuilding` | `PlateBuilding` | `PlateBuildingAction` | — | 板房设置 |
| 板房楼栋 | `PlateBuildGroup` | `PlateBuildGroup` | `PlateBuildGroupAction` | `PlateBuild3dAction` | 板房楼栋编组 |
| 开门边线 | `OpenLine` | `QdOpenLine` | `OpenLineAction` | — | 出入口边线 |
| 场布设备 | `LayoutEquipment` | `QdLayoutEquipment` | `LayoutEquipmentAction` | `LayoutEquipment3dAction` | 施工设备放置 |

---

## 已注册命令一览

| 命令名 | 快捷键 | Action 类 | 方法 | 说明 |
|--------|--------|----------|------|------|
| `Fence` | W | `FenceAction` | `ExecCreate` | 绘制围栏 |
| `Lawn` | LW | `LawnAction` | `ExecCreatePoly` | 绘制草坪（任意多边形） |
| `LawnRec` | LWRC | `LawnAction` | `ExecCreateRec` | 绘制草坪（矩形） |
| `LawnChange` | LWCH | `LawnAction` | `ExecCreate` | 转换多段线为草坪 |
| `Site` | Site | `SiteAction` | `ExecCreatePoly` | 绘制场地 |
| `SiteRec` | STRC | `SiteAction` | `ExecCreateRec` | 绘制场地（矩形） |
| `SiteChange` | STCH | `SiteAction` | `ExecCreate` | 转换多段线为场地 |
| `PropertyLine` | PropertyLine | `PropertyLineAction` | `ExecCreatePoly` | 绘制用地红线 |
| `PropertyLineRec` | PLRC | `PropertyLineAction` | `ExecCreateRec` | 绘制红线（矩形） |
| `PropertyLineChange` | PLCH | `PropertyLineAction` | `ExecCreate` | 转换多段线为红线 |
| `PlanBuild` | PB | `PlanBuildAction` | `ExecCreatePlanBuild` | 绘制拟建建筑 |
| `PickLinePlanBuild` | PLPB | `PlanBuildAction` | `ExecPickLineCreatePlanBuild` | 拾取线创建拟建建筑 |
| `FoundationPit` | FDP | `FoundationPitAction` | `ExecCreatePoly` | 绘制基坑 |
| `FoundationPitRec` | FDPRE | `FoundationPitAction` | `ExecCreateRec` | 绘制基坑（矩形） |
| `FoundationPitChange` | FDPCH | `FoundationPitAction` | `ExecCreate` | 转换多段线为基坑 |
| `Road` | ROD | `RoadAction` | `ExecCreate` | 绘制城市道路 |
| `Ground` | GOD | `GroundAction` | `ExecCreatePoly` | 绘制硬化地面 |
| `GroundRec` | GDRC | `GroundAction` | `ExecCreateRec` | 绘制硬化地面（矩形） |
| `GroundChange` | GODCH | `GroundAction` | `ExecCreate` | 转换多段线为硬化地面 |
| `Earthwork` | EWK | `EarthworkAction` | `ExecCreatePoly` | 绘制土方回填 |
| `EarthworkRec` | EWRC | `EarthworkAction` | `ExecCreateRec` | 绘制土方（矩形） |
| `EarthworkChange` | EWCH | `EarthworkAction` | `ExecCreate` | 转换多段线为土方 |
| `Berm` | BRM | `BermAction` | `ExecCreatePoly` | 绘制出土道路 |
| `Barrier` | BRR | `BarrierAction` | `ExecCreate` | 绘制防护栏杆 |
| `Harden` | HDR | `HardenAction` | `ExecCreatePoly` | 绘制路面硬化 |
| `HardenRec` | HDRC | `HardenAction` | `ExecCreateRec` | 绘制硬化（矩形） |
| `HardenChange` | HDCH | `HardenAction` | `ExecCreate` | 转换多段线为硬化 |
| `OpenOuterLine` | OPL | `OpenLineAction` | `ExecCreateOpenLine` | 绘制开门边线 |
| `PlateBuilding` | W | `PlateBuildingAction` | `ExecCreate` | 编辑板房布置 |
| `SetBuildGroup` | W | `PlateBuildGroupAction` | `SetGroup` | 设置板房楼栋分组 |
| `PlateUBuild` | W | `PlateBuildGroupAction` | `ExecCreate` | 创建板房楼栋 |
| `SelRedLinesForArrange` | SRFA | `TemComAttriAction` | `ExecCreate` | 选择红线生成排布方案 |
| `DrawOrAdjust` | DRAD | `DrawOrAdjustAction` | `ExecCreate` | 绘制或调整 |

---

## Action 模式说明

每个场布元素通常包含以下文件：

| 文件 | 说明 |
|------|------|
| `Qd{Element}.cs` | 元素实体类，继承自 LightCAD 基类，定义元素属性和序列化 |
| `Qd{Element}Def.cs` | 元素定义类 |
| `{Element}Action.cs` | ★ 2D Action——处理用户交互、参数输入、元素创建和编辑 |
| `{Element}3dAction.cs` | 3D Action——生成元素的三维模型 |
| `{Element}Set.cs` / `.Designer.cs` | 可选的属性设置面板（WinForms） |

Action 类常用方法模式：

| 方法 | 说明 |
|------|------|
| `ExecCreatePoly(args)` | 任意多边形方式创建元素（交互式点拾取） |
| `ExecCreateRec(args)` | 矩形方式创建元素 |
| `ExecCreate(args)` | 选择已有多段线转换为元素 |

---

## Provider 模式说明（QdLayoutProvider）

Provider 项目负责元素的二维形状生成（Shape）和三维实体生成（Solid），通过 `IDllProviderImporter` 接口注册。

### Provider 注册入口

```csharp
using LightCAD.Core;

namespace QdLayoutProvider
{
    public class QdLayoutDllProviderImporter : IDllProviderImporter
    {
        internal static ShapeProviderCollection ShapeProviders = new ShapeProviderCollection();
        internal static SolidProviderCollection SolidProviders = new SolidProviderCollection();

        public (ShapeProviderCollection shapeProviders, SolidProviderCollection solidProviders) GetImportProviders()
        {
            QdFenceProvider.RegistProviders();
            QdLawnProvider.RegistProviders();
            QdFoundationPitProvider.RegistProviders();
            QdGroundProvider.RegistProviders();
            QdEarthworkProvider.RegistProviders();
            QdBermProvider.RegistProviders();
            QdHardenProvider.RegistProviders();
            QdSiteProvider.RegistProviders();
            QdIntersectionProvider.RegistProviders();
            return (ShapeProviders, SolidProviders);
        }
    }
}
```

### 编写自定义 Provider 示例

以场地（Site）Provider 为例，展示如何注册一个二维形状 Provider：

```csharp
using LightCAD.Core.Component;
using LightCAD.MathLib.Csg;
using ThreeJs4Net;

namespace QdArchProvider
{
    internal static class QdSiteProvider
    {
        internal static void RegistProviders()
        {
            // 注册二维形状 Provider
            ConvertToProviders(new List<(string uuid, string name, CreateShape creator)>
            {
                ("61C3A847-E445-83E6-DEB7-724A1248B04D", "场地", 场地)
            });
        }

        // 二维形状生成方法
        internal static Curve2dGroupCollection 场地(LcParameterSet pset, ShapeCreator creator)
        {
            var curves = new List<Curve2d>();
            var outline = pset.GetValue<Polyline2d>("Outline");
            curves = outline.Curve2ds.Clone();
            var baseCurveGrp = new Curve2dGroup { Curve2ds = curves.ToListEx() };
            return new Curve2dGroupCollection { baseCurveGrp };
        }
    }
}
```

### 包含三维实体的 Provider 示例（出土道路）

```csharp
namespace QdArchProvider
{
    internal static class QdBermProvider
    {
        internal static void RegistProviders()
        {
            // 注册二维形状
            ConvertToProviders(new List<(string uuid, string name, CreateShape creator)>
            {
                ("A2802FC8-94B2-ABFD-8AA2-5CABD9CC8FAB", "出土道路", 出土道路)
            });
            // 注册三维实体
            ConvertToProvider(
                "C55AD616-A858-F513-48D9-A577B2696D94",
                nameof(GetSolid_出土道路),
                GetSolid_出土道路,
                GetSolidMats
            );
        }

        // 二维形状：基线 + 左右偏移线 + 端线
        internal static Curve2dGroupCollection 出土道路(LcParameterSet pset, ShapeCreator creator)
        {
            var width = pset.GetValue<double>("Width");
            var baseline = pset.GetValue<Line2d>("Baseline");
            var normal = baseline.Dir.Clone().RotateAround(new Vector2(), Math.PI / 2);
            var leftL = baseline.Clone().Translate(normal.Clone().MultiplyScalar(width / 2)) as Line2d;
            var rightL = baseline.Clone().Translate(normal.Clone().MultiplyScalar(-width / 2)) as Line2d;
            var curves = new List<Curve2d> { baseline.Clone(), leftL, rightL,
                new Line2d(leftL.Start.Clone(), rightL.Start.Clone()),
                new Line2d(leftL.End.Clone(), rightL.End.Clone()) };
            return new Curve2dGroupCollection { new Curve2dGroup { Curve2ds = curves.ToListEx() } };
        }

        // 三维实体：根据标高和放坡系数生成立体
        private static Solid3dCollection GetSolid_出土道路(
            LcComponentDefinition definition, LcParameterSet pset, SolidCreator creator)
        {
            var line = pset.GetValue<Line2d>("Baseline");
            var bottom = pset.GetValue<double>("Bottom");
            var factor = pset.GetValue<double>("Factor");
            var width = pset.GetValue<double>("Width");
            var eleStart = pset.GetValue<double>("ElevationStart");
            var eleEnd = pset.GetValue<double>("ElevationEnd");
            // ... 通过顶面、底面、侧面构造 Solid3d
            // 返回 Solid3dCollection
        }

        // 材质回调
        private static MaterialInfo[] GetSolidMats(
            LcComponentDefinition definition, LcParameterSet pset,
            SolidCreator creator, Solid3d solid)
        {
            return new MaterialInfo[] { pset.GetValue<MaterialInfo>("Material") };
        }
    }
}
```

---

## 典型二次开发场景

| 场景 | 涉及类/模式 | 说明 |
|------|-----------|------|
| 添加新的场布元素类型 | `LayoutElementType` + `ILcPlugin.Loaded()` | 定义新的 `ElementType`（含唯一 GUID），在插件 `Loaded()` 中注册 |
| 注册新命令 | `[CommandClass]` + `[CommandMethod]` | 在命令类中添加新方法，指定 Name 和 ShortCuts |
| 实现 2D 绘制交互 | `{Element}Action` + `IDocumentEditor` | 实现 `ExecCreatePoly` / `ExecCreateRec` / `ExecCreate` 方法 |
| 实现 3D 建模 | `{Element}3dAction` + Provider | 在 Provider 中用 `Curve2dGroupCollection` 和 `Solid3dCollection` 生成模型 |
| 添加属性设置面板 | `{Element}Set` (WinForms Form) | 创建 WinForms 面板供用户编辑元素参数 |
| 自定义 UI 菜单按钮 | `TabItem` / `TabButtonGroup` / `TabButton` | 在 `LayoutPlugin` 中添加新的按钮定义 |
| 注册形状/实体 Provider | `IDllProviderImporter` + `ConvertToProviders` | 在 Provider 项目中实现 `CreateShape` 和 `CreateSolid` 委托 |
| 曲线转换为闭合环 | `LcCurveChangeLoop.CheckLoops()` | 将多条线段/弧线拼接为闭合多段线 |

---

## 常用数学库 API

| 类 | 命名空间 | 说明 |
|----|---------|------|
| `Vector2` | `LightCAD.MathLib` | 二维向量，支持加减、缩放、旋转、距离计算 |
| `Vector3` | `LightCAD.MathLib` | 三维向量 |
| `Line2d` | `LightCAD.MathLib` | 二维线段（Start / End / Dir） |
| `Line3d` | `LightCAD.MathLib` | 三维线段 |
| `Arc2d` | `LightCAD.MathLib` | 二维弧线（Center / Radius / StartAngle / EndAngle） |
| `Polyline2d` | `LightCAD.MathLib` | 二维多段线（Curve2ds / IsClosed） |
| `Circle2d` | `LightCAD.MathLib` | 二维圆 |
| `Plane` | `LightCAD.MathLib` | 平面（法向量定义） |
| `Curve2dGroup` | `LightCAD.MathLib` | 二维曲线组 |
| `Curve2dGroupCollection` | `LightCAD.MathLib` | 二维曲线组集合（Shape 返回类型） |
| `Solid3d` | `LightCAD.MathLib` | 三维实体（Name / Geometry） |
| `Solid3dCollection` | `LightCAD.MathLib` | 三维实体集合（Solid 返回类型） |
| `PlanarSurface3d` | `LightCAD.MathLib.Csg` | 平面表面，支持三角化 `Trianglate()` |
| `GeometryData` | `LightCAD.MathLib` | 几何数据（Verteics / Indics / Groups） |
| `Intersect2d` | `LightCAD.MathLib` | 二维相交计算（线线、线圆、圆圆） |

常用向量操作：

```csharp
// 向量旋转 90°
var normal = line.Dir.Clone().RotateAround(new Vector2(), Math.PI / 2);

// 向量平移
line.Clone().Translate(normal.Clone().MultiplyScalar(width / 2));

// 二维转三维
var point3d = point2d.ToVector3(elevation);

// 叉积计算法向量
var faceNormal = new Vector3().CrossVectors(dir1, dir2);

// 点相似性判断（闭合检测）
startPoint.Similarity(endPoint, 0);
```

---

## 常见注意事项

1. **GUID 唯一性**：每个 `ElementType` 和 Provider 的 UUID 必须全局唯一，使用 `Guid.ParseExact(..., "B")` 格式。
2. **多段线方向**：闭合多段线需检查绕行方向，使用 `ShapeUtils.isClockWise()` 判断并在必要时调用 `Reverse()`。
3. **Clone 习惯**：几何对象（`Vector2`、`Line2d`、`Polyline2d` 等）在变换前务必 `Clone()`，避免修改原始数据。
4. **Provider 项目独立**：`QdLayoutProvider` 输出到 `Build/Providers` 目录，与插件主体分离部署。
5. **调试方式**：编译后通过 VS2022 附加进程到 `lightcad.EXE` 进行断点调试。
6. **UI 注册时机**：`TabItem` 应在 `Completed()` 中通过 `AppRuntime.UISystem.AddInitTabItems()` 注册，不要在 `Loaded()` 中操作 UI。

---

## 参考链接

- **FY_Layout 项目地址：** <https://github.com/znlgis/FY_Layout>
- **飞扬集成设计平台：** 面向建筑设计行业的开源 BIM 正向设计软件
- **技术服务：** 微信 qishou003
