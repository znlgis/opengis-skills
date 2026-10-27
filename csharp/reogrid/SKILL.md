---
name: reogrid
description: "Use when embedding an Excel-like spreadsheet control in .NET WinForms/WPF — ReoGridControl, CurrentWorksheet, SetRangeData, SetRangeStyles, MergeRange, FreezeToCell, CreateColumnFilter, Save to xlsx/CSV/RGF. Also for formulas not recalculating until Recalculate(), slow per-cell writes, grid.RunScript not compiling (EX_SCRIPT), and WPF blurry rendering on high-DPI. ReoGrid: MIT spreadsheet component (V3 community; V4 commercial)."
tags:
  - dotnet
  - spreadsheet
  - winforms
  - wpf
  - excel
  - spreadsheet-control
---

> **项目地址：** <https://github.com/unvell/ReoGrid>
>
> **官网：** <https://reogrid.net/>
>
> **NuGet：** `unvell.ReoGrid.DLL`（WinForms，net48 / net8.0-windows）、`unvell.ReoGridWPF.dll`（WPF）、`unvell.ReoGrid8.dll`（.NET 8 重打包，作者 Jingwood）
>
> **最新版本：** unvell.ReoGrid.dll 3.3.1 / unvell.ReoGridWPF.dll 3.3.0 / unvell.ReoGrid8.dll 8.1.0（截至 2026-10，NuGet 实测；GitHub 最新 tag v3.3.0）
>
> **许可证：** MIT（V3 社区版，即本仓库）；V4 商业版特性另售，V5 以 Avalonia 为核心（截至 2026-10）

## 概述

ReoGrid 主要能力：

- **WinForms 与 WPF** 双控件
- **单元格**：样式、字体、边框、对齐、数据格式
- **合并单元格、冻结、批注**
- **公式**：内置 ~ 100 个 Excel 函数
- **数据验证**、自动筛选、排序
- **图表**：内置基础图表（柱状/折线/饼图）
- **打印**与导出（PDF/CSV）
- **Excel 互通**：读写 .xlsx（内置 `ReoGrid.IO.OpenXML` 实现，不依赖 NPOI 或 Office）
- **脚本扩展**：内嵌 JS 脚本（基于 ReoScript）

> ReoGrid 不依赖 Excel/COM，纯托管代码，跨 .NET Framework 与 .NET 6+。

---

## 安装

### 方式一：dotnet CLI

```bash
# WinForms
dotnet add package unvell.ReoGrid.dll

# WPF
dotnet add package unvell.ReoGridWPF.dll

# .NET 8 重打包版本
# dotnet add package unvell.ReoGrid8.dll
```

### 方式二：PackageReference

```xml
<ItemGroup>
  <!-- net48 与 net8.0-windows7.0 两个 TFM，依赖 Microsoft.WindowsDesktop.App -->
  <PackageReference Include="unvell.ReoGrid.dll" Version="3.3.1" />
</ItemGroup>
```

### 方式三：包管理器控制台

```powershell
Install-Package unvell.ReoGrid.dll -Version 3.3.1
```

### 验证安装

```bash
dotnet list package | grep -i reogrid
```

> WinForms 包的 NuGet id 是 `unvell.ReoGrid.dll`（程序集同名），WPF 包 `unvell.ReoGridWPF.dll`，`unvell.ReoGrid8.dll` 是作者为 .NET 8 重新打包的版本。命名空间统一是 `unvell.ReoGrid.*`。
>
> 目标框架以包内 `lib/` 为准：3.3.1 提供 `net48` 与 `net8.0-windows7.0` 两份，ASP.NET Core / 控制台等非 Windows 桌面项目**不能用**（`frameworkReference` 依赖 `Microsoft.WindowsDesktop.App`）。

---

## 核心 API 速查

| 对象 | 入口 | 说明 |
|------|------|------|
| 控件 | `ReoGridControl`（WinForms / WPF） | 宿主控件，`Dock = DockStyle.Fill` 铺满 |
| 工作表 | `grid.CurrentWorksheet` / `grid.Worksheets` | 当前表与表集合 |
| 单元格 / 区域 | `sheet["A1"]` / `sheet["A2:C4"]` / `sheet.SetRangeData(...)` | 索引器按地址读写，支持区域赋值 |
| 区域样式 | `RangePosition` + `sheet.SetRangeStyles(...)` | 见「样式」章 |
| 公式 | `sheet["C2"] = "=A2*B2"` / `sheet.Recalculate()` | 重算需显式触发 |
| 文件 IO | `unvell.ReoGrid.IO`（Excel / CSV 导入导出） | 见「Excel 文件读写」章 |
| 脚本 | ReoScript | 需 `EX_SCRIPT` 条件编译，官方包默认不含，见「脚本」章 |

---

## WinForms 入门

```csharp
using unvell.ReoGrid;
using unvell.ReoGrid.IO;

var grid = new ReoGridControl { Dock = DockStyle.Fill };
this.Controls.Add(grid);

var sheet = grid.CurrentWorksheet;
sheet["A1"] = "ID";
sheet["B1"] = "Name";
sheet["C1"] = "Score";

sheet["A2"] = 1;
sheet["B2"] = "Tom";
sheet["C2"] = 95;
```

---

## WPF 入门

```xml
<Window xmlns:rg="clr-namespace:unvell.ReoGrid;assembly=unvell.ReoGrid">
  <rg:ReoGridControl x:Name="Grid"/>
</Window>
```

```csharp
var sh = Grid.CurrentWorksheet;
sh["A1:C1"] = new object[] { "ID", "Name", "Score" };
sh["A2:C2"] = new object[] { 1, "Tom", 95 };
```

---

## 区域操作

```csharp
sh.SetRangeData("A2:C4", new object[,] {
    { 1, "Tom",  95 },
    { 2, "Lucy", 88 },
    { 3, "Mike", 72 },
});

object[,] data = (object[,])sh.GetRangeData("A2:C4");
```

---

## 样式

```csharp
sh.SetRangeStyles("A1:C1", new WorksheetRangeStyle {
    Flag = PlainStyleFlag.All,
    Bold = true,
    BackColor = Color.LightGray,
    HAlign = ReoGridHorAlign.Center,
    VAlign = ReoGridVerAlign.Middle,
    TextColor = Color.Black,
    FontSize = 12
});

// 数据格式（百分比 / 日期）
sh.SetRangeDataFormat("C2:C100", CellDataFormatFlag.Percent,
    new NumberDataFormatter.NumberFormatArgs { DecimalPlaces = 2 });

sh.SetRangeDataFormat("D2:D100", CellDataFormatFlag.DateTime,
    new DateTimeDataFormatter.DateTimeFormatArgs { Format = "yyyy-MM-dd" });
```

---

## 公式

```csharp
sh["C5"] = "=SUM(C2:C4)";
sh["C6"] = "=AVERAGE(C2:C4)";
sh["C7"] = "=IF(C2>90, \"A\", \"B\")";

sh.Recalculate();   // 强制重算
```

---

## 合并 / 冻结 / 批注

```csharp
sh.MergeRange("A1:C1");
sh.FreezeToCell("A2");

sh.Cells["B2"].Comment = new Comment("张三是优秀员工");
```

---

## 数据验证

V3 社区版的内核没有 `DataValidation` API（数据验证是 ReoGrid V4 商业版的特性）。V3 要做输入约束，用单元格类型 + 事件拦截：

```csharp
// 下拉候选（单元格类型，具体子类见 unvell.ReoGrid.CellTypes）
var cell = sh.Cells["C2"];
cell.Body = new DropdownListCell("待办", "进行中", "已完成");

// 数值范围用事件兜底（CellEventArgs 暴露 Cell，位置用 e.Cell.Position）
sh.CellDataChanged += (s, e) =>
{
    if (e.Cell.Position.Col == 2 && e.Cell.Data is double d && (d < 0 || d > 100))
        e.Cell.Data = Math.Clamp(d, 0, 100);
};
```

---

## 自动筛选

```csharp
// 区域内建列筛选（参数：起始列、结束列、标题行数）
var filter = sh.CreateColumnFilter("A", "C", titleRows: 1);
```

---

## Excel 文件读写

```csharp
// ReoGridControl 级加载 / 保存
grid.Load("input.xlsx");                      // 按扩展名自动识别
grid.Load("input.xlsx", FileFormat.Excel2007);
grid.Save("output.xlsx", FileFormat.Excel2007);
grid.Save("data.csv",    FileFormat.CSV);

// Worksheet 级只读单个文件（含 CSV 专项）
sh.Load("input.xlsx");
sh.LoadCSV("data.csv");
```

---

## 事件

```csharp
// CellEventArgs：e.Cell 指向变更单元格
sh.CellDataChanged += (s, e) =>
    Debug.WriteLine($"{e.Cell.Position.ToAddress()} 改为 {e.Cell.Data}");
```

---

## 图表

```csharp
using unvell.ReoGrid.Drawing;
using unvell.ReoGrid.Chart;

var chart = new LineChart {
    Bounds = new Rectangle(300, 50, 400, 300),
    Title = "成绩",
    DataSource = new WorksheetChartDataSource(sh, "B1:B4", "C2:C4")
};
sh.FloatingObjects.Add(chart);
```

---

## 脚本（ReoScript）

ReoScript 引擎在源码里由 `EX_SCRIPT` 条件编译符号控制，官方 NuGet 包**默认不带该符号**，`grid.RunScript(...)` 与 `grid.Script` 在开箱即用的 3.3.1 包中不可用。需要脚本能力时自行从源码带 `EX_SCRIPT` 重新编译：

```csharp
// 仅在自行启用 EX_SCRIPT 编译后可用
grid.Script = @"
function autoFill(sheet) {
    for (var i = 1; i < 10; i++) {
        sheet['A' + (i + 1)] = i;
        sheet['B' + (i + 1)] = i * 100;
    }
}";
grid.RunScript("autoFill(workbook.currentWorksheet);");
```

一般场景直接用 C# 循环写 `SetRangeData` 更省事，脚本只在需要最终用户自定义逻辑时才值得开。

---

## 打印 / 导出

```csharp
// 页面设置（Worksheet 级）
// 3.3.1 的 PrintSettings 用 Landscape 布尔值，没有 PageOrientation 枚举；
// PageMargins 的参数顺序是 (top, bottom, left, right)，单位英寸
sh.PrintSettings = new PrintSettings {
    Landscape = true,
    Margins = new PageMargins(0.5f, 0.5f, 0.5f, 0.5f)
};
```

导出只支持 `FileFormat` 枚举里的三种（`ReoGridFormat` / `CSV` / `Excel2007`），**没有 PDF**：

```csharp
grid.Save("report.xlsx", FileFormat.Excel2007);
grid.Save("report.csv",  FileFormat.CSV);
grid.Save("report.rgf",  FileFormat.ReoGridFormat);
```

打印走 `PrintSession`（`ReoGridControl` 的打印入口在内部 `PrintSession.Print()` 上），需要 PDF 请用 Excel2007 导出后在外部转 PDF。

---

## 性能优化

1. 大量写入用 `SetRangeData(...)` 替代逐格赋值
2. 改动期间禁用刷新：`sh.SuspendUIUpdates()` / `sh.ResumeUIUpdates()`
3. 数千公式时减少 `Recalculate`，由用户触发
4. Excel 读写是内置 OpenXML 实现（`ReoGrid.IO.OpenXML`），不走 NPOI；大文件仍要注意内存
5. 行/列上限：1,048,576 行 × 32,768 列（源码 `Position.cs` 中与 Excel 对齐）

---

## 典型工作流

### 场景一：在 WinForms 应用中嵌入数据报表

```csharp
// 1. 创建控件并加载数据
var grid = new ReoGridControl { Dock = DockStyle.Fill };
this.Controls.Add(grid);
var sheet = grid.CurrentWorksheet;

// 2. 设置标题行样式
sheet.SetRangeStyles("A1:D1", new WorksheetRangeStyle {
    Flag = PlainStyleFlag.All,
    Bold = true,
    BackColor = Color.LightGray,
    HAlign = ReoGridHorAlign.Center,
});

// 3. 批量填充数据
sheet["A1:D1"] = new object[] { "ID", "姓名", "部门", "薪资" };
sheet.SetRangeData("A2:D100", dataArray);   // 大批量用 SetRangeData

// 4. 添加汇总公式
sheet["D101"] = "=SUM(D2:D100)";
sheet["A101"] = "合计：";
sheet.MergeRange("A101:C101");

// 5. 冻结标题行 + 自动筛选
sheet.FreezeToCell("A2");
sheet.CreateColumnFilter("A", "D", titleRows: 1);

// 6. 导出
grid.Save("report.xlsx", FileFormat.Excel2007);
```

### 场景二：构建交互式数据录入表格

```csharp
// 1. 创建带验证的模板
sheet["A1:C1"] = new object[] { "日期", "项目", "金额" };
sheet.SetRangeStyles("A1:C1", new WorksheetRangeStyle { Bold = true });

// 2. 设置日期列格式
sheet.SetRangeDataFormat("A2:A100", CellDataFormatFlag.DateTime,
    new DateTimeDataFormatter.DateTimeFormatArgs { Format = "yyyy-MM-dd" });

// 3. 金额列输入约束（V3 无 DataValidation API，用事件兜底）
sheet.CellDataChanged += (s, e) =>
{
    if (e.Cell.Position.Col == 2 && e.Cell.Data is double v && (v < 0 || v > 100000))
        e.Cell.Data = Math.Clamp(v, 0, 100000);
};

// 4. 监听数据变更做实时计算（e.Cell.Position.Col 是 0 基列号，C 列为 2）
sheet.CellDataChanged += (s, e) => {
    if (e.Cell.Position.Col == 2)
        sheet["C101"] = "=SUM(C2:C100)";
};

// 5. 提供保存按钮
btnSave.Click += (s, e) => grid.Save("data.xlsx", FileFormat.Excel2007);
```

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 需要数据验证 / 条件样式 / 懒加载百万行 | 这些是 V4 商业版特性，V3 社区版没有；V3 用单元格类型 + `CellDataChanged` 事件兜底 |
| `grid.RunScript(...)` 编译不过 | 脚本引擎受 `EX_SCRIPT` 条件编译控制，官方 3.3.1 包默认不含；如需脚本自行带符号编译 |
| 想导出 PDF | `FileFormat` 只有 `ReoGridFormat` / `CSV` / `Excel2007`，没有 PDF；先导出 xlsx 再外部转换 |
| WPF 高 DPI 模糊 | 启用 `PerMonitorV2` DPI |
| 公式不计算 | 调用 `sh.Recalculate()` |
| Excel 打开样式丢失 | 仅支持核心样式，复杂样式建议用 NPOI 单独生成 |
| 写入几万行卡顿 | 用 `SetRangeData(...)` 批量赋值替代逐格赋值，并减少 `Recalculate()` 的调用次数 |

---

## AI 使用建议

### 推荐工作流

1. **明确需求**：确认是 WinForms 还是 WPF 项目，需要哪些功能（只读展示/可编辑/公式/图表）
2. **快速搭建原型**：先创建一个最小可用控件，用 `sheet["A1"] = ...` 方式快速填充测试数据
3. **优化性能**：大批量数据改用 `SetRangeData()` + `SuspendUIUpdates()`
4. **样式完善**：复用 `WorksheetRangeStyle` 实例，避免在循环内创建
5. **集成导出**：复杂 Excel 格式（条件格式、数据透视）用 NPOI 单独生成，再在 ReoGrid 里打开；ReoGrid 自身的读写是内置 OpenXML 实现

### 关键模式与常见陷阱

- **批量赋值优先**：逐格赋值 (`sheet["A1"] = val`) 在千行以上会很慢，必须改用 `SetRangeData()`
- **UI 更新暂停**：大量数据填充期间务必 `SuspendUIUpdates()` / `ResumeUIUpdates()`
- **公式不会自动触发**：设置了公式后需要调用 `Recalculate()`，或在 `CellDataChanged` 事件中手动触发
- **样式限制**：ReoGrid 仅支持核心 Excel 样式，复杂条件格式/图表建议用 NPOI 生成后导入
- **商业授权**：V3社区版为MIT许可，商业闭源产品需购买V4商业许可
- **DPI 适配**：WPF 高 DPI 环境需启用 `PerMonitorV2`，否则控件模糊

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 简单数据展示/导出 | 直接用 NPOI，无需 ReoGrid |
| WinForms/WPF 内嵌可编辑表格 | ReoGrid |
| 纯 Excel 文件处理（无 UI） | NPOI |
| 复杂图表/数据透视表 | 商业控件（ReoGrid V4 / Spread.NET / Aspose.Cells） |

---

## 相关技能

- **npoi** — .NET Excel/Word 读写库，无 UI 的批量导入导出用它，复杂格式也可先 NPOI 生成再进 ReoGrid：[../npoi/SKILL.md](../npoi/SKILL.md)
- **sqlsugar** — 数据来源：查询后把结果集灌入 `SetRangeData(...)`：[../sqlsugar/SKILL.md](../sqlsugar/SKILL.md)
- **sod** — 另一套 .NET ORM，报表数据同样可经它取出再填充表格：[../sod/SKILL.md](../sod/SKILL.md)

---

## 参考资源

- 官网：<https://reogrid.net/>
- 仓库：<https://github.com/unvell/ReoGrid>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/ReoGrid/>
