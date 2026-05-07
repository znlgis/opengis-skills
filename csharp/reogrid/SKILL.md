---
name: reogrid
description: ReoGrid 是开源的 .NET 电子表格控件，提供类 Excel 的 WinForms / WPF 表格控件，支持单元格样式、合并、公式计算、图表、冻结、批注、多工作表与 Excel 文件读写，适合在 .NET 桌面应用中嵌入电子表格能力。
---

> **项目地址：** <https://github.com/unvell/ReoGrid>
>
> **官网：** <https://reogrid.net/>
>
> **NuGet：** `unvell.ReoGrid`、`unvell.ReoGrid.WinForm`、`unvell.ReoGrid.WPF`
>
> **许可证：** GPL-3.0（社区版）；商业版另购

## 概述

ReoGrid 主要能力：

- **WinForms 与 WPF** 双控件
- **单元格**：样式、字体、边框、对齐、数据格式
- **合并单元格、冻结、批注**
- **公式**：内置 ~ 100 个 Excel 函数
- **数据验证**、自动筛选、排序
- **图表**：内置基础图表（柱状/折线/饼图）
- **打印**与导出（PDF/CSV）
- **Excel 互通**：读写 .xlsx / .xls（依赖 NPOI）
- **脚本扩展**：内嵌 JS 脚本（基于 ReoScript）

> ReoGrid 不依赖 Excel/COM，纯托管代码，跨 .NET Framework 与 .NET 6+。

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

```csharp
sh.AddRangeDataValidation(new DataValidation(
    new RangePosition("C2:C100"),
    DataValidationType.WholeNumber, 0, 100));
```

---

## 自动筛选

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

## 脚本（ReoScript）

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
grid.Print();      // 调用打印对话框

grid.Save("report.pdf", FileFormat.PDF);
```

---

## 性能优化

1. 大量写入用 `SetRangeData(...)` 替代逐格赋值
2. 改动期间禁用刷新：`sh.SuspendUIUpdates()` / `sh.ResumeUIUpdates()`
3. 数千公式时减少 `Recalculate`，由用户触发
4. 大文件读写依赖 NPOI，注意内存
5. 行/列上限：1,048,576 行 × 32,768 列（与 Excel 接近）

---

## 常见问题

| 问题 | 解决 |
|------|------|
| GPL 不适合商业 | 购买商业授权 |
| WPF 高 DPI 模糊 | 启用 `PerMonitorV2` DPI |
| 公式不计算 | 调用 `sh.Recalculate()` |
| Excel 打开样式丢失 | 仅支持核心样式，复杂样式建议直接 NPOI 处理 |

---

## 参考资源

- 官网：<https://reogrid.net/>
- 仓库：<https://github.com/unvell/ReoGrid>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/tutorial/reogrid/>
