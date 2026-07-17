---
name: reogrid
description: "Use when embedding an Excel-like spreadsheet control in .NET WinForms/WPF applications �?formula engine, cell editing, clipboard, undo/redo. ReoGrid: .NET spreadsheet component with NPOI-based Excel read/write."
tags: [dotnet, spreadsheet, winforms, wpf, excel]
---

> **项目地址�?* <https://github.com/unvell/ReoGrid>
>
> **官网�?* <https://reogrid.net/>
>
> **NuGet�?* `unvell.ReoGrid`、`unvell.ReoGrid.WinForm`、`unvell.ReoGrid.WPF`
>
> **许可证：** GPL-3.0（社区版）；商业版另�?

## 概述

ReoGrid 主要能力�?

- **WinForms �?WPF** 双控�?
- **单元�?*：样式、字体、边框、对齐、数据格�?
- **合并单元格、冻结、批�?*
- **公式**：内�?~ 100 �?Excel 函数
- **数据验证**、自动筛选、排�?
- **图表**：内置基础图表（柱�?折线/饼图�?
- **打印**与导出（PDF/CSV�?
- **Excel 互�?*：读�?.xlsx / .xls（依�?NPOI�?
- **脚本扩展**：内�?JS 脚本（基�?ReoScript�?

> ReoGrid 不依�?Excel/COM，纯托管代码，跨 .NET Framework �?.NET 6+�?

---

## 安装

```bash
# WinForms
dotnet add package unvell.ReoGrid.WinForm

# WPF
dotnet add package unvell.ReoGrid.WPF
```

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
<Window xmlns:rg="clr-namespace:unvell.ReoGrid;assembly=unvell.ReoGrid.WPF">
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
    HorizontalAlign = ReoGridHorAlign.Center,
    VerticalAlign   = ReoGridVerAlign.Middle,
    TextColor = Color.Black,
    FontSize = 12
});

// 数据格式（百分比 / 日期�?
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

```csharp
sh.AddRangeDataValidation(new DataValidation(
    new RangePosition("C2:C100"),
    DataValidationType.WholeNumber, 0, 100));
```

---

## 自动筛�?

```csharp
sh.CreateAutoFilter("A1:C100");
```

---

## Excel 文件读写

```csharp
grid.Load("input.xlsx", FileFormat.Excel2007);
grid.Save("output.xlsx", FileFormat.Excel2007);
grid.Save("data.csv", FileFormat.CSV);
```

---

## 事件

```csharp
sh.CellDataChanged += (s, e) =>
    Debug.WriteLine($"{e.Cell.PositionAsString} 改为 {e.Cell.Data}");

sh.SelectionChanged += (s, e) => statusLabel.Text = e.Range.ToAddress();
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

## 脚本（ReoScript�?

```js
// 内嵌 JS
function autoFill(sheet) {
    for (var i = 1; i < 10; i++) {
        sheet["A" + (i+1)] = i;
        sheet["B" + (i+1)] = i * 100;
    }
}
```

```csharp
grid.RunScript(@"autoFill(workbook.currentWorksheet);");
```

---

## 打印 / 导出 PDF

```csharp
grid.Worksheets[0].PrintSettings = new PrintSettings {
    PageOrientation = PageOrientation.Landscape,
    Margins = new PageMargins(0.5f, 0.5f, 0.5f, 0.5f)
};
grid.Print();      // 调用打印对话�?

grid.Save("report.pdf", FileFormat.PDF);
```

---

## 性能优化

1. 大量写入�?`SetRangeData(...)` 替代逐格赋�?
2. 改动期间禁用刷新：`sh.SuspendUIUpdates()` / `sh.ResumeUIUpdates()`
3. 数千公式时减�?`Recalculate`，由用户触发
4. 大文件读写依�?NPOI，注意内�?
5. �?列上限：1,048,576 �?× 32,768 列（�?Excel 接近�?

---

## 典型工作�?

### 场景一：在 WinForms 应用中嵌入数据报�?

```csharp
// 1. 创建控件并加载数�?
var grid = new ReoGridControl { Dock = DockStyle.Fill };
this.Controls.Add(grid);
var sheet = grid.CurrentWorksheet;

// 2. 设置标题行样�?
sheet.SetRangeStyles("A1:D1", new WorksheetRangeStyle {
    Flag = PlainStyleFlag.All,
    Bold = true,
    BackColor = Color.LightGray,
    HorizontalAlign = ReoGridHorAlign.Center,
});

// 3. 批量填充数据
sheet["A1:D1"] = new object[] { "ID", "姓名", "部门", "薪资" };
sheet.SetRangeData("A2:D100", dataArray);   // 大批量用 SetRangeData

// 4. 添加汇总公�?
sheet["D101"] = "=SUM(D2:D100)";
sheet["A101"] = "合计�?;
sheet.MergeRange("A101:C101");

// 5. 冻结标题�?+ 自动筛�?
sheet.FreezeToCell("A2");
sheet.CreateAutoFilter("A1:D100");

// 6. 导出
grid.Save("report.xlsx", FileFormat.Excel2007);
```

### 场景二：构建交互式数据录入表�?

```csharp
// 1. 创建带验证的模板
sheet["A1:C1"] = new object[] { "日期", "项目", "金额" };
sheet.SetRangeStyles("A1:C1", new WorksheetRangeStyle { Bold = true });

// 2. 设置日期列格�?
sheet.SetRangeDataFormat("A2:A100", CellDataFormatFlag.DateTime,
    new DateTimeDataFormatter.DateTimeFormatArgs { Format = "yyyy-MM-dd" });

// 3. 金额列添加数据验证（0-100000�?
sheet.AddRangeDataValidation(new DataValidation(
    new RangePosition("C2:C100"),
    DataValidationType.Decimal, 0, 100000));

// 4. 监听数据变更做实时计�?
sheet.CellDataChanged += (s, e) => {
    if (e.Cell.Column == 2)  // C 列变更时重算合计
        sheet["C101"] = "=SUM(C2:C100)";
};

// 5. 提供保存按钮
btnSave.Click += (s, e) => grid.Save("data.xlsx", FileFormat.Excel2007);
```

---

## AI 使用建议

### 推荐工作�?

1. **明确需�?*：确认是 WinForms 还是 WPF 项目，需要哪些功能（只读展示/可编�?公式/图表�?
2. **快速搭建原�?*：先创建一个最小可用控件，�?`sheet["A1"] = ...` 方式快速填充测试数�?
3. **优化性能**：大批量数据改用 `SetRangeData()` + `SuspendUIUpdates()`
4. **样式完善**：复�?`WorksheetRangeStyle` 实例，避免在循环内创�?
5. **集成导出**：对�?NPOI 处理复杂 Excel 格式（ReoGrid �?Excel 读写底层依赖 NPOI�?

### 关键模式与常见陷�?

- **批量赋值优�?*：逐格赋�?(`sheet["A1"] = val`) 在千行以上会很慢，必须改�?`SetRangeData()`
- **UI 更新暂停**：大量数据填充期间务�?`SuspendUIUpdates()` / `ResumeUIUpdates()`
- **公式不会自动触发**：设置了公式后需要调�?`Recalculate()`，或�?`CellDataChanged` 事件中手动触�?
- **样式限制**：ReoGrid 仅支持核�?Excel 样式，复杂条件格�?图表建议直接�?NPOI 生成后导�?
- **商业授权**：GPL-3.0 限制，商业闭源产品需购买商业许可
- **DPI 适配**：WPF �?DPI 环境需启用 `PerMonitorV2`，否则控件模�?

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 简单数据展�?导出 | 直接�?NPOI，无需 ReoGrid |
| WinForms/WPF 内嵌可编辑表�?| ReoGrid |
| �?Excel 文件处理（无 UI�?| NPOI |
| 复杂图表/数据透视�?| 商业控件（Spread.NET / Aspose.Cells�?|

---

## 常见问题

| 问题 | 解决 |
|------|------|
| GPL 不适合商业 | 购买商业授权 |
| WPF �?DPI 模糊 | 启用 `PerMonitorV2` DPI |
| 公式不计�?| 调用 `sh.Recalculate()` |
| Excel 打开样式丢失 | 仅支持核心样式，复杂样式建议直接 NPOI 处理 |

---

## 相关技�?

- **npoi** �?.NET Excel/Word 读写库，ReoGrid �?Excel 导入导出底层依赖：[../npoi/SKILL.md](../npoi/SKILL.md)

---

## 参考资�?

- 官网�?https://reogrid.net/>
- 仓库�?https://github.com/unvell/ReoGrid>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/tutorial/reogrid/>