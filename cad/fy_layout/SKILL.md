---
name: fy_layout
description: "Use when doing construction site layout planning with the FeiYang LightCAD platform — fence, lawn, foundation pit, road, prefab house 2D/3D modeling. FY_Layout: construction site layout secondary development plugin for LightCAD/LightBIM."
tags:
  - 2d
  - 3d
  - cad
  - dotnet
  - csharp
  - bim
  - construction
  - dwg
  - dxf
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

## 核心 SDK 引用一览

| DLL | 命名空间 | 用途 |
|-----|---------|------|
| `LightCAD.Core.dll` | `LightCAD.Core` | ★ 核心——元素类型 `ElementType`、文档 `LcDocument`、运行时 `LcRuntime`、组件定义等 |
| `LightCAD.Drawing.dll` | `LightCAD.Drawing` | 绘图文档——图层、图纸、绘制管理 |
| `LightCAD.Drawing.Actions.dll` | `LightCAD.Drawing.Actions` | 绘图交互动作基类——`IDocumentEditor`、点拾取、线拾取等 |
| `LightCAD.MathLib.dll` | `LightCAD.MathLib` | 数学库——`Vector2`、`Vector3`、`Line2d`、`Arc2d`、`Polyline2d`、`Color` 等 |
| `LightCAD.Model.dll` | `LightCAD.Model` | 模型管理 |
| `LightCAD.Runtime.dll` | `LightCAD.Runtime` | 运行时框架——`CommandClass`、`CommandMethod`、`TabItem`、`TabButton` 等特性和 UI 类 |
| `LightCAD.RenderUtils.dll` | `LightCAD.RenderUtils` | 渲染工具 |
| `ThreeJs4Net.dll` | `ThreeJs4Net` | 三维引擎——`Shape`、`Solid3d`、`Surface3d`、`GeometryData` 等 |
| `OpenTK.dll` | `OpenTK` | OpenGL 绑定 |
| `Newtonsoft.Json.dll` | `Newtonsoft.Json` | JSON 序列化 |

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
            // 注意：SDK属性名本身为 DispalyName（非 DisplayName），此为飞扬SDK的拼写错误，使用时须按此名称
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
| `PlateUBuild` | W | `PlateBuildGroupAction` | `ExecCreate` | 创建板房楼栋 ⚠ 快捷键 W 与 Fence/PlateBuilding/SetBuildGroup 冲突 |
| `SelRedLinesForArrange` | SRFA | `TemComAttriAction` | `ExecCreate` | 选择红线生成排布方案 |
| `DrawOrAdjust` | DRAD | `DrawOrAdjustAction` | `ExecCreate` | 绘制或调整 |

---

> Action 模式、Provider 模式与典型二次开发场景的完整说明见 [reference/action-provider.md](reference/action-provider.md)
> 常用数学库 API 完整参考见 [reference/math-api.md](reference/math-api.md)

## AI 使用建议

- **推荐工作流模式**：AI 助手开发飞扬插件应遵循「ElementType 定义 → ILcPlugin 注册 → Command 声明 → Action 实现 → Provider 生成」的五步模式。新元素先参考 `Lawn`/`Fence` 的完整实现作为模板。
- **关键注意事项**：① 每个 `ElementType` 和 Provider UUID 必须全局唯一，使用 `Guid.ParseExact(..., "B")` 格式；② 几何对象变换前必须 `Clone()`，避免修改原始数据；③ `TabItem` 在 `Completed()` 中注册，不可在 `Loaded()` 中操作 UI；④ Provider 项目与插件主体分离部署，输出到 `Build/Providers`。
- **常用代码模式**：插件骨架 = `ILcPlugin.Loaded()` 注册元素类型和 Action + `Completed()` 注册 UI 菜单。2D Action 模式 = `ExecCreatePoly`（交互式点拾取）/ `ExecCreateRec`（矩形）/ `ExecCreate`（多段线转换）。Provider 模式 = `ConvertToProviders` 注册 Shape → `ConvertToProvider` 注册 Solid → 几何生成方法返回 `Curve2dGroupCollection`/`Solid3dCollection`。

---

## 相关技能

- **lightcad** — 飞扬基础平台（LightCAD）的 Web 2D CAD 框架：[../lightcad/SKILL.md](../lightcad/SKILL.md)
- **ifoxcad** — AutoCAD .NET 二次开发框架（类似的 CAD 插件开发模式）：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)
- **xbim** — .NET BIM/IFC 框架（与建筑场布互补）：[../xbim/SKILL.md](../xbim/SKILL.md)

---

## 参考资源

- **FY_Layout 项目地址：** <https://github.com/znlgis/FY_Layout>
- **飞扬集成设计平台：** 面向建筑设计行业的开源 BIM 正向设计软件
- **技术服务：** 微信 qishou003
