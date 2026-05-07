---
name: qcad
description: QCAD 是基于 Qt 的开源 2D CAD 应用与 SDK，专注 DWG/DXF 二维制图，提供 ECMAScript（JavaScript）扩展与脚本控制台、命令行工具 dxf2*/转换器，适合机械、建筑、测绘的二维出图与自动化处理。
---

> **项目地址：** <https://github.com/qcad/qcad>
>
> **官网：** <https://qcad.org/>
>
> **官方文档：** <https://qcad.org/en/qcad-documentation>
>
> **API 参考：** <https://api.qcad.org/>
>
> **许可证：** GPL-3.0（社区版）；Pro 版商业许可

## 概述

QCAD 由两部分组成：

- **QCAD Community Edition**：开源核心，支持 DXF（自带）+ DWG（需要 Teigha/ODA File Converter 或 LibreDWG）
- **QCAD/CAM 与 QCAD Pro**：商业插件（数控、PDF、SVG 详细输出等）

核心能力：

- 2D 绘图：线/弧/圆/多段线/样条/标注/填充/文本
- 图层、块、视图、布局、打印
- DXF/DWG/PDF/SVG 输入输出
- ECMAScript（QtScript / V8）脚本扩展
- 命令行：`qcad`、`dwg2dxf`、`dxf2pdf`、`dxf2bmp` 等

---

## 安装

```bash
# 二进制：<https://qcad.org/en/download>
# Linux 自带：sudo apt install qcad

# 命令行
qcad             # 启动 GUI
qcad -no-gui -autostart script.js   # 无界面运行脚本
```

将 ODA File Converter（免费）放在 PATH 中以支持 DWG。

---

## 项目结构

```
qcad-installation/
├── qcad             # 主程序
├── plugins/         # 二进制插件
├── scripts/         # 脚本扩展（自带 + 用户）
│   ├── Draw/
│   ├── Modify/
│   ├── File/
│   └── Examples/
└── doc/api/         # API 文档（同 api.qcad.org）
```

用户脚本目录：`$HOME/.qcad/scripts`（Linux）或对应路径。

---

## ECMAScript 入门：画一条线

```javascript
include("scripts/EAction.js");

function MyLine(guiAction) { EAction.call(this, guiAction); }
MyLine.prototype = new EAction();

MyLine.prototype.beginEvent = function() {
    EAction.prototype.beginEvent.call(this);
    var doc = this.getDocument();

    var line = new RLineEntity(doc, new RLineData(
        new RVector(0, 0), new RVector(100, 50)));

    var op = new RAddObjectsOperation();
    op.addObject(line);
    doc.applyOperation(op);

    this.terminate();
};
```

将文件保存为 `~/.qcad/scripts/MyLine.js` 并通过 `Misc → Run script`，或在控制台调用。

---

## 脚本控制台（Tools → Script Shell）

```javascript
var doc = getDocument();
print(doc.getEntityIdsByType(RS.EntityLine).length);

// 添加圆
var circle = new RCircleEntity(doc, new RCircleData(new RVector(0,0), 10));
var op = new RAddObjectsOperation();
op.addObject(circle);
doc.applyOperation(op);
```

---

## 命令行批处理

```bash
# DXF → PDF
dxf2pdf -o out.pdf input.dxf

# DXF → SVG
dxf2svg -o out.svg input.dxf

# DWG → DXF（需 ODA File Converter 或 LibreDWG）
dwg2dxf -outversion=2018 input.dwg

# DXF → BMP / PNG
dxf2bmp -a -o out.png input.dxf
```

---

## 自动化批处理（脚本）

```javascript
// batch_export.js
var fileList = ["a.dxf", "b.dxf", "c.dxf"];
for (var i = 0; i < fileList.length; ++i) {
    var doc = new RDocument(new RMemoryStorage(), createSpatialIndex());
    var fi = new RFileImporterRegistry();
    var importer = fi.getFileImporterFromFileName(fileList[i], doc);
    importer.importFile(fileList[i]);

    // 导出 PDF
    var exporter = new RPdfExporter(doc);
    exporter.exportToFile("out_" + i + ".pdf");
}
```

运行：

```bash
qcad -no-gui -autostart batch_export.js
```

---

## 实体与文档 API

```javascript
var doc = getDocument();

// 遍历所有实体
var ids = doc.queryAllEntities();
for (var i = 0; i < ids.length; ++i) {
    var e = doc.queryEntity(ids[i]);
    if (isLineEntity(e))
        print("LINE", e.getStartPoint(), "→", e.getEndPoint());
}

// 修改图层
var layer = new RLayer(doc, "WALL", false, false,
    new RColor("#ff0000"), doc.getLinetypeId("CONTINUOUS"), RLineweight.Weight030);
var op = new RAddObjectsOperation();
op.addObject(layer);
doc.applyOperation(op);
```

---

## 常用操作

| 操作 | API |
|------|-----|
| 添加 | `RAddObjectsOperation` |
| 修改 | `RModifyObjectsOperation` |
| 删除 | `RDeleteObjectsOperation` |
| 平移/旋转/缩放 | `RModifyObjectsOperation` + `RTransform*` |
| 选择集 | `getDocumentInterface().getStorage().queryAllSelectedEntities()` |
| 块 | `RBlockReferenceEntity` + `RBlock` |

---

## 打印与布局

- 视图（Layouts）→ Block-based Page Layout
- 打印对话框：File → Print；支持多布局批量
- 通过脚本：`RGraphicsSceneQt + RPrinter`

---

## 性能优化

1. 大文件：禁用 Hatches 自动重算（Drafting → Auto-Regen）
2. 使用 `RDocument` + `RMemoryStorage` 处理无 UI 转换
3. `RAddObjectsOperation.addObject(obj, false)` 不立即更新空间索引
4. 大量实体批量提交后再 `applyOperation`
5. 禁用快照（snap）与轨迹（tracking）以加速绘制

---

## 常见问题

| 问题 | 解决 |
|------|------|
| DWG 打不开 | 安装 ODA File Converter 并在 Preferences → File I/O 配置 |
| 字体缺失 | 复制 .shx/.ttf 到 `fonts/` 目录或安装到系统 |
| 中文显示乱 | 设置图层使用支持 CJK 的字体（如 simhei） |
| 脚本路径错 | 使用绝对路径或 `documentInterface.getDocument()` |

---

## 参考资源

- 文档：<https://qcad.org/en/qcad-documentation>
- API：<https://api.qcad.org/>
- 论坛：<https://qcad.org/rsforum/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/qcad/>
