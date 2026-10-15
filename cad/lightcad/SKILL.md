---
name: lightcad
description: "Use when building or extending a desktop CAD/BIM application with the open-source FeiYang LightCAD platform — plugin development, custom elements, DWG/DXF I/O, 2D drafting and 3D/BIM modeling on C#/.NET. LightCAD (FeiYang Integrated Design Platform) is a C# CAD system integrating 2D design, 3D design, and BIM."
tags:
  - csharp
  - dotnet
  - cad
  - bim
  - 2d
  - 3d
  - dwg
  - plugin
  - architecture
---

> **项目地址：** <https://github.com/znlgis/lightcad1>
>
> **所属平台：** 飞扬集成设计平台（LightCAD，启道软件 Qidao Soft 开源）
>
> **许可证：** CC-BY-SA-4.0（见仓库 LICENSE）
>
> **中文教程：** <https://znlgis.github.io/cad/LightCAD/>（20 章，从架构到插件实战）
>
> **版本：** 仓库暂无公开 Release/Tag，以 master 分支为准（截至2026-10）

## 概述

LightCAD（飞扬集成设计平台）是一套基于 .NET 8 / C# 开发的开源建筑工程设计软件，目标是把二维设计、三维设计、BIM 设计、智能设计与协同设计融合为一体，为建筑设计行业提供 BIM 正向设计支撑能力。项目采用严格的分层架构（MathLib → Core → RenderUtils → Drawing → Runtime → UI），既可作为完整 CAD 平台使用，也可作为二次开发底座。核心特性：

- **完整 2D/3D 能力**：直线、圆弧、多段线、样条等二维图元；拉伸、旋转、放样、融合等参数化实体建模
- **多渲染后端**：Three.js4Net（WebGL）与 OpenTK（OpenGL）
- **DWG/DXF 兼容**：通过 ODA SDK 与内置 netDxf 处理 AutoCAD 文件格式，另支持 SketchUp 导入
- **插件体系**：基于 Weikio Plugin Framework 运行时加载；预置建筑（QdArch）、电气（QdElectric）、暖通（QdHvac）、结构（QdStruct）、给排水（QdWater）五大行业插件
- **视图构建**：正交投影、截面视图、详图生成

---

## 环境准备

### 前置条件

| 项 | 要求 |
|----|------|
| 操作系统 | Windows 10（1909+）/ Windows 11 64 位 |
| 开发工具 | Visual Studio 2022（17.5.5+，.NET 桌面开发工作负载）或 `dotnet` CLI |
| SDK | .NET 8 SDK |
| 硬件 | 8GB 内存起（推荐 16GB+），支持 OpenGL 3.3 的显卡 |

### 获取源码与编译（命令行方式）

```bash
# 仓库体积较大（含 DLL 与资源），建议浅克隆
git clone --depth 1 https://github.com/znlgis/lightcad1.git
cd lightcad1

# 还原与编译
dotnet restore LightCAD1.sln
dotnet build LightCAD1.sln --configuration Debug
```

### 运行（VS 或 CLI）

```bash
# VS：用 Visual Studio 打开 LightCAD1.sln，将 LightCAD.WinForm 设为启动项目，按 F5
# CLI：
dotnet run --project src/LightCAD.WinForm
```

**验证**：稳定编译后启动主窗口即成功；插件调试采用 VS「附加到进程」绑定 `lightcad` 进程（参见 FY_Layout 插件示例的做法）。

---

## 解决方案结构（关键项目）

| 项目 | 职责 |
|------|------|
| `LightCAD.MathLib` | 向量/矩阵、曲线数学、几何求交（`Vector2`/`Vector3` 等） |
| `LightCAD.Core` | 核心数据模型：`LcDocument`、图元实体（`LcElement`）、`ElementType`、元素空间 |
| `LightCAD.RenderUtils` | Three.js4Net 桥接、资源与事件、三维控件 |
| `LightCAD.Drawing` / `LightCAD.Drawing.Actions` | 视口、输入系统、捕捉、交互 Action（`IDocumentEditor`） |
| `LightCAD.Runtime` | 应用运行时：`ILcPlugin`、`PluginManager`、命令框架（`CommandClass`/`CommandMethod`） |
| `LightCAD.Model` / `LightCAD.UI.WinForm` / `LightCAD.WinForm` | 模型控件、UI 层与主程序入口 |
| `LightCAD.ImportAndExport` | DWG/DXF/SketchUp 导入导出 |
| `Plugins/` | 预编译行业插件（QdArch 等） |
| `netDxf`、`Libs/`、`ThirdParty/` | DXF 库源码、本地 DLL（ThreeJs4Net/OpenTK）、第三方源码 |

---

## 核心 API

### 图元实体（LightCAD.Core）

二维基本图元以 `Lc` 前缀命名，与 AutoCAD 习惯一致：

```csharp
using LightCAD.Core;

// 常见二维图元
var line   = new LcLine();       // 直线
var circle = new LcCircle();     // 圆
var arc    = new LcArc();        // 圆弧
var pline  = new LcPolyLine();   // 多段线
var ell    = new LcEllipse();    // 椭圆
var hatch  = new LcHatch();      // 填充
var text   = new LcText();       // 文字

// 元素加入文档模型空间
lcDocument.ModelSpace.Elements.Add(line);
```

实体目录还包括三维图元（`Elements/Element3d`）、实体建模（`Elements/Solid`）、标注（`Elements/Dim`、`Dim3`）、表格（`Table`）等（详见仓库 `src/LightCAD.Core/Elements/`）。

### 插件接口（LightCAD.Runtime）

插件入口实现 `ILcPlugin`，由 `PluginManager` 通过 Weikio Plugin Framework 加载：

```csharp
using LightCAD.Runtime;
using LightCAD.Core;

public class MyPlugin : ILcPlugin
{
    public static TabItem MyTab = new TabItem { Name = "MyMajor", Text = "我的专业" };

    public void Loaded()
    {
        // 注册自定义元素类型（ElementType 需含唯一 Guid、Name、DispalyName 与 ClassType）
        LcDocument.RegistElementTypes(MyElementType.All);
        // 注册 2D/3D Action
        LcDocument.ElementActions.Add(MyElementType.Device, new DeviceAction());
        LcDocument.Element3dActions.Add(MyElementType.Device, new Device3dAction());
    }

    public void Completed()
    {
        AppRuntime.UISystem.AddInitTabItems(new[] { MyTab });   // 挂接 UI 菜单
    }

    public void OnInitializeDocRt(DocumentRuntime docRt) { }
    public void OnDisposeDocRt(DocumentRuntime docRt) { }
}
```

插件目录通过主程序旁的 `plugins.json`（`folders` 数组）配置，`PluginManager.LoadPlugins()` 扫描加载。

### 命令注册（CommandClass / CommandMethod）

```csharp
using LightCAD.Core;
using LightCAD.Runtime;

[CommandClass]
public class MyCmds
{
    [CommandMethod(Name = "MyCross", ShortCuts = "MCX")]
    public CommandResult DrawCross(IDocumentEditor docEditor, string[] args)
    {
        // 交互拾取与实体创建：参见 LightCAD.Drawing.Actions 中的 Action 基类
        // ...
        return CommandResult.Succ();
    }
}
```

命令行（命令行窗口 / 命令别名）与 AutoCAD 风格一致：`LINE`/`CIRCLE`/`PLINE`/`MOVE`/`COPY`/`MIRROR`/`TRIM` 等内置命令。

### DWG 导入导出

`LoadDwg` / `SaveDwg` 命令即为导入导出入口（`LightCAD.ImportAndExport`）：

```csharp
var lcDocument = DwgReader.Import(filePath);   // 读入 DWG → LcDocument
// 修改 lcDocument.ModelSpace.Elements 后
// 通过 SaveDwg 命令或导出器写回 DWG/DXF
```

---

## 端到端工作流

### 工作流一：从源码构建并运行平台

1. 安装 .NET 8 SDK 与 Visual Studio 2022（17.5.5+，.NET 桌面开发工作负载）
2. `git clone --depth 1 https://github.com/znlgis/lightcad1.git`
3. `dotnet restore LightCAD1.sln` → `dotnet build LightCAD1.sln -c Debug`
4. 启动 `LightCAD.WinForm`，在命令行窗口输入 `LINE` 画一条直线验证交互
5. 用 `LoadDwg`/`SaveDwg` 打开与保存 DWG 图纸验证文件链路

### 工作流二：开发一个行业插件（元素 + 命令 + Action）

1. 新建类库项目（`net8.0-windows`，与平台工程 TFM 保持一致），引用平台项目或 `Libs/` 下的 SDK DLL（LightCAD.Core、LightCAD.Runtime、LightCAD.Drawing.Actions、LightCAD.MathLib 等）
2. 定义 `ElementType` 静态集合（唯一 Guid、Name、`DispalyName`、`ClassType`），实体类继承 `LcElement`
3. 实现 `ILcPlugin`：在 `Loaded()` 注册元素类型与 2D/3D Action，在 `Completed()` 挂接菜单 Tab
4. 用 `[CommandClass]`/`[CommandMethod]` 编写用户命令，内部驱动 Action 完成交互绘制
5. 编译后把 DLL 放入插件目录（或配置 `plugins.json` 的 `folders`），启动平台验证命令可执行
6. VS 中以「附加到进程」调试 `lightcad` 进程；参考完整示例：<https://github.com/znlgis/FY_Layout>

---

## 最佳实践

1. **分层依赖**：业务代码只引用 `LightCAD.Core`/`LightCAD.MathLib`，UI 与交互逻辑放 Action 层，避免循环依赖
2. **元素类型 GUID 稳定**：`ElementType.Guid` 是序列化标识，发布后不可更改；注意 SDK 属性拼写为 `DispalyName`
3. **命令薄、Action 厚**：`[CommandMethod]` 只做参数解析与转发，交互逻辑放入 Action 类便于复用与调试
4. **大仓库浅克隆**：仓库含大量 DLL/字体资源，开发机建议 `--depth 1`
5. **渲染路径分离**：2D 显示与 3D 显示（ThreeJs4Net/OpenTK）分别验证，避免把 2D 交互问题误判为渲染问题
6. **DWG 兼容性**：DWG 读写依赖 ODA 相关 DLL，分发插件时确认 `Libs/` 依赖完整

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 编译报「找不到 ThreeJs4Net.dll / OpenTK.dll」 | 确认仓库 `src/Libs/` 下 DLL 完整（部分二进制依赖未随 Git 提供时需从发布包获取） |
| `The current .NET SDK does not support targeting .NET 8` | 安装 .NET 8 SDK（平台全部工程为 `net8.0` / `net8.0-windows` 目标） |
| WinForms 项目在非 Windows 上编译失败 | `net8.0-windows` 项目仅支持 Windows 编译与运行 |
| NuGet 还原失败（NU1301） | 检查网络或配置国内 NuGet 镜像源 |
| 插件不加载 | 检查 `plugins.json` 的 `folders` 配置、DLL 是否位于扫描目录、是否实现 `ILcPlugin` |
| 命令行输入命令无响应 | 确认平台已启动文档（文档未初始化时命令框架不执行） |
| DWG 打开异常 | 确认目标版本受 ODA 支持；必要时先用 ODA File Converter 转存 |

---

## AI 使用建议

- **推荐工作流模式**：先按「工作流一」用 .NET 8 SDK + VS2022 从源码构建并跑通平台（`LINE`/`LoadDwg`/`SaveDwg` 验证链路），再按「工作流二」以 `ILcPlugin` + `ElementType` + `[CommandMethod]` 开发行业插件；插件 DLL 放入插件目录或配置 `plugins.json` 的 `folders`。
- **关键注意事项**：① 分层依赖要守——业务代码只引用 `LightCAD.Core`/`LightCAD.MathLib`，UI 与交互放 Action 层；② `ElementType.Guid` 是序列化标识，发布后不可更改，且 SDK 属性拼写为 `DispalyName`（非 DisplayName）；③ 命令薄、Action 厚，`[CommandMethod]` 只做参数解析与转发；④ 仓库体积大，开发机建议 `--depth 1` 浅克隆。
- **常用代码模式**：插件入口 = 实现 `ILcPlugin` → `Loaded()` 注册 `ElementType` 与 2D/3D Action → `Completed()` 挂接菜单 Tab；命令 = `[CommandClass]` 类 + `[CommandMethod(Name=..., ShortCuts=...)]` 方法；文件读写 = `DwgReader.Import(filePath)` 读入 → 改 `ModelSpace.Elements` → `SaveDwg` 写回。
- **调试与验证**：用 VS「附加到进程」绑定 `lightcad` 进程下断点（参考 FY_Layout 插件示例）；2D 与 3D 渲染路径（ThreeJs4Net/OpenTK）分别验证，避免把 2D 交互问题误判为渲染问题。
- **不要臆造**：命令框架、`ILcPlugin`、`ElementType`、`plugins.json` 均以仓库源码为准，不要假设存在 AutoCAD 风格的未公开 API。

---

## 相关技能

- **fy_layout** — 飞扬平台场地布置插件示例（完整的插件工程结构与 SDK 用法）：[../fy_layout/SKILL.md](../fy_layout/SKILL.md)
- **ifoxcad** — AutoCAD .NET 二次开发框架（对照参考另一种 .NET CAD 插件模式）：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)
- **xbim** — .NET BIM/IFC 工具包（BIM 数据交换互补）：[../xbim/SKILL.md](../xbim/SKILL.md)
- **libredwg** — DWG/DXF 读写库（文件格式侧互补）：[../libredwg/SKILL.md](../libredwg/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/znlgis/lightcad1>
- 中文教程（20 章）：<https://znlgis.github.io/cad/LightCAD/>
- 插件示例仓库：<https://github.com/znlgis/FY_Layout>
- 关键章节：第 3 章（分层架构）、第 15 章（插件系统与扩展开发）、第 16 章（命令与操作系统）
