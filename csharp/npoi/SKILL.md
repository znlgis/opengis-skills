---
name: npoi
description: NPOI 是 Apache POI 的 .NET 移植，开源、免费，可在不依赖 Office 的情况下读写 Excel（.xls / .xlsx）、Word（.doc）、PowerPoint 等文档格式，是 .NET 生态中处理 Excel 的事实标准。
tags: dotnet, excel, word, office, npoi
---

> **项目地址：** <https://github.com/nissl-lab/npoi>
>
> **NuGet：** `NPOI`
>
> **官方文档：** <https://github.com/nissl-lab/npoi/wiki>
>
> **许可证：** Apache-2.0

## 概述

NPOI 主要能力：

- **xls（HSSF）** / **xlsx（XSSF）** / **流式 xlsx（SXSSF）** 读写
- **公式计算**：`FormulaEvaluator`
- **样式**：字体、边框、对齐、数据格式、条件格式
- **图表 / 图片 / 批注**
- **Word `.doc`（HWPF）** / Word `.docx`（XWPF）
- **PowerPoint `.ppt`/.pptx`**
- **跨平台**：.NET Framework / .NET 6+ / Linux / macOS

> 大文件写入推荐 SXSSF（流式），可处理百万行 Excel；大文件读取推荐 EventModel（XSSF SAX）。

---

## 安装

```bash
dotnet add package NPOI
```

主要命名空间：

- `NPOI.HSSF.UserModel` — xls
- `NPOI.XSSF.UserModel` — xlsx
- `NPOI.XSSF.Streaming` — 流式 xlsx
- `NPOI.SS.UserModel` — 通用接口（IWorkbook / ISheet / IRow / ICell）
- `NPOI.SS.Util` — CellRangeAddress、WorkbookUtil

---

## 写入 Excel（xlsx）

```csharp
using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;

IWorkbook wb = new XSSFWorkbook();
ISheet sh = wb.CreateSheet("Sheet1");

// 标题样式
ICellStyle headStyle = wb.CreateCellStyle();
IFont font = wb.CreateFont();
font.Boldweight = (short)FontBoldWeight.Bold; font.FontHeightInPoints = 12;
headStyle.SetFont(font);
headStyle.FillForegroundColor = IndexedColors.Grey25Percent.Index;
headStyle.FillPattern = FillPattern.SolidForeground;
headStyle.Alignment = HorizontalAlignment.Center;

string[] head = { "ID", "Name", "Score", "Time" };
IRow row = sh.CreateRow(0);
for (int i = 0; i < head.Length; i++) {
    var c = row.CreateCell(i);
    c.SetCellValue(head[i]);
    c.CellStyle = headStyle;
}

// 数据
for (int r = 1; r <= 10; r++) {
    var dr = sh.CreateRow(r);
    dr.CreateCell(0).SetCellValue(r);
    dr.CreateCell(1).SetCellValue("User" + r);
    dr.CreateCell(2).SetCellValue(80 + r);
    dr.CreateCell(3).SetCellValue(DateTime.Now);   // 注意要设置日期样式
}

// 列宽
sh.AutoSizeColumn(1);

using var fs = new FileStream("out.xlsx", FileMode.Create);
wb.Write(fs, leaveOpen: false);
```

---

## 读取 Excel

```csharp
using var fs = new FileStream("in.xlsx", FileMode.Open, FileAccess.Read);
IWorkbook wb = WorkbookFactory.Create(fs);   // 自动识别 xls/xlsx
ISheet sh = wb.GetSheetAt(0);

for (int r = sh.FirstRowNum; r <= sh.LastRowNum; r++) {
    IRow row = sh.GetRow(r); if (row == null) continue;
    for (int c = row.FirstCellNum; c < row.LastCellNum; c++) {
        ICell cell = row.GetCell(c);
        Console.Write(GetValue(cell) + "\t");
    }
    Console.WriteLine();
}

static object GetValue(ICell? cell) => cell?.CellType switch {
    CellType.Numeric => DateUtil.IsCellDateFormatted(cell) ? cell.DateCellValue : cell.NumericCellValue,
    CellType.String  => cell.StringCellValue,
    CellType.Boolean => cell.BooleanCellValue,
    CellType.Formula => cell.CachedFormulaResultType switch {
        CellType.Numeric => cell.NumericCellValue,
        CellType.String  => cell.StringCellValue,
        _ => ""
    },
    _ => ""
};
```

---

## 数据格式（日期 / 数字）

```csharp
ICellStyle dateStyle = wb.CreateCellStyle();
dateStyle.DataFormat = wb.CreateDataFormat().GetFormat("yyyy-MM-dd HH:mm:ss");

ICellStyle pctStyle = wb.CreateCellStyle();
pctStyle.DataFormat = HSSFDataFormat.GetBuiltinFormat("0.00%");
```

---

## 公式

```csharp
sh.CreateRow(11).CreateCell(2).SetCellFormula("SUM(C2:C11)");

// 计算公式（写出前）
var ev = wb.GetCreationHelper().CreateFormulaEvaluator();
ev.EvaluateAll();
```

---

## 流式写入（SXSSF，海量行）

```csharp
using NPOI.XSSF.Streaming;

using SXSSFWorkbook wb = new SXSSFWorkbook(rowAccessWindowSize: 1000);
ISheet sh = wb.CreateSheet("big");
for (int r = 0; r < 1_000_000; r++) {
    var row = sh.CreateRow(r);
    for (int c = 0; c < 10; c++)
        row.CreateCell(c).SetCellValue(r * 10 + c);
}
using var fs = File.Create("big.xlsx");
wb.Write(fs);
wb.Dispose();   // 清理临时文件
```

---

## 合并单元格 / 冻结 / 筛选

```csharp
sh.AddMergedRegion(new CellRangeAddress(0, 0, 0, 3));   // 合并第一行 A:D
sh.CreateFreezePane(0, 1);                              // 冻结首行
sh.SetAutoFilter(new CellRangeAddress(0, sh.LastRowNum, 0, 3));
```

---

## 图片

```csharp
byte[] img = File.ReadAllBytes("logo.png");
int picIdx = wb.AddPicture(img, PictureType.PNG);
IDrawing patriarch = sh.CreateDrawingPatriarch();
var anchor = wb.GetCreationHelper().CreateClientAnchor();
anchor.Col1 = 5; anchor.Row1 = 1;
var pic = patriarch.CreatePicture(anchor, picIdx);
pic.Resize();
```

---

## 条件格式

```csharp
var cf = (XSSFConditionalFormatting)sh.SheetConditionalFormatting;
var rule = cf.CreateConditionalFormattingRule(ComparisonOperator.GreaterThan, "60");
var pattern = rule.CreatePatternFormatting();
pattern.FillBackgroundColor = IndexedColors.Yellow.Index;
cf.AddConditionalFormatting(new[] { CellRangeAddress.ValueOf("C2:C11") }, rule);
```

---

## Word（XWPF）

```csharp
using NPOI.XWPF.UserModel;

XWPFDocument doc = new();
XWPFParagraph p  = doc.CreateParagraph();
XWPFRun r = p.CreateRun();
r.FontSize = 16; r.IsBold = true; r.SetText("Hello NPOI");

using var fs = File.Create("out.docx");
doc.Write(fs);
```

---

## 性能与最佳实践

1. **百万级写**用 SXSSF，注意 `Dispose()` 清理 tmp 文件
2. **样式数量受 64000 限制**：复用 `ICellStyle` 实例
3. **日期单元格** 必须设置 DataFormat，否则显示数字
4. **大文件读**用 `XSSFEventModel`（SAX）以减少内存
5. **xls 行数上限 65536**，xlsx 上限 1048576
6. **避免在循环内 `wb.CreateCellStyle()`**

---

## AI 使用建议

### 推荐工作流

1. **确定格式**：`.xls` 用 HSSFWorkbook，`.xlsx` 用 XSSFWorkbook，不确定用 `WorkbookFactory.Create()` 自动识别
2. **读文件**：`FileStream` → `WorkbookFactory.Create()` → `GetSheetAt(0)` → 遍历 Row/Cell → 根据 `CellType` 取值
3. **写文件**：`new XSSFWorkbook()` → `CreateSheet()` → `CreateRow()` → `CreateCell()` → `SetCellValue()` → `FileStream` 写出
4. **样式后设**：先写数据，再设样式（复用 `ICellStyle` 实例，避免 64000 限制）
5. **大文件处理**：写用 SXSSFWorkbook（流式），读用 EventModel（SAX 事件驱动）

### 关键模式与常见陷阱

- **日期变数字**：日期单元格必须设置带日期 DataFormat 的 `ICellStyle`，否则显示为数字
- **样式 64000 限制**：`ICellStyle` 实例总数不能超过 64000，必须在循环外 `CreateCellStyle()` 并复用
- **中文不乱码的前提**：xlsx 默认 UTF-8 不会乱码；xls 需要检查 Excel 打开时自动识别
- **公式需要求值**：`wb.GetCreationHelper().CreateFormulaEvaluator().EvaluateAll()` 在写出前调用
- **SXSSF 记得 Dispose**：流式写入后必须 `Dispose()` 清理临时文件
- **不要用 COM/Interop**：NPOI 纯托管，不依赖 Office 安装，服务器环境友好

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 简单导入导出（< 10 万行） | NPOI XSSFWorkbook |
| 百万级写入 | NPOI SXSSFWorkbook |
| 百万级读取 | NPOI EventModel（SAX） |
| WinForms/WPF 内嵌表格 | ReoGrid（底层用 NPOI 读写文件） |
| 纯数据交换（无格式） | MiniExcel / CsvHelper |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 中文乱码 | 文件流默认 UTF-8；xls 打开 Excel 自动识别 |
| 日期变数字 | 给 Cell 设置带日期 DataFormat 的 ICellStyle |
| 出现「This Workbook contains an invalid」 | 风格数超限或公式错误，减少样式 / 修正公式 |
| 内存溢出 | 改用 SXSSF / EventModel |
| Office 打开提示损坏 | 写完后 `wb.Write(fs)` 必须在文件流之前不要 Close 流 |

---

## 相关技能

- **reogrid** — .NET 电子表格控件，内嵌可编辑表格，底层依赖 NPOI 读写 Excel 文件：[../reogrid/SKILL.md](../reogrid/SKILL.md)
- **sqlsugar** — .NET ORM，可与 NPOI 配合：从数据库查询后批量导出 Excel：[../sqlsugar/SKILL.md](../sqlsugar/SKILL.md)

---

## 参考资源

- Wiki：<https://github.com/nissl-lab/npoi/wiki>
- Apache POI（API 等价）：<https://poi.apache.org/components/spreadsheet/>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/tutorial/npoi/>