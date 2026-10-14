---
name: qcad
description: "Use when editing DXF files with a professional open-source 2D CAD application — CAM output, part libraries, isometric projection. QCAD: open-source 2D CAD with DXF as native format, scriptable via ECMAScript."
tags:
  - 2d
  - cad
  - dxf
  - dwg
  - qt
  - javascript
  - ecmascript
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
>
> **最新稳定版：** 3.33.1（截至2026年9月，GitHub tag `v3.33.1.0`，见 <https://qcad.org/en/download>）

## 概述

QCAD 由两部分组成：

- **QCAD Community Edition**：开源核心，支持 DXF（自带）+ DWG（需要 Teigha/ODA File Converter 或 LibreDWG）
- **QCAD/CAM 与 QCAD Pro**：商业插件（数控、PDF、SVG 详细输出等）

核心能力：

- 2D 绘图：线/弧/圆/多段线/样条/标注/填充/文本
- 图层、块、视图、布局、打印
- DXF/DWG/PDF/SVG 输入输出
- ECMAScript（QtScript / V8）脚本扩展
- 命令行：`qcad` 本体 + Pro 版附带的控制台工具（`dwginfo`、`dwg2pdf`、`dwg2svg`、`dwg2bmp` 等，见「命令行批处理」）

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

```text
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

### Pro 版控制台工具

QCAD Professional 安装目录自带一批转换与信息提取工具（社区版不含），统一形式为 `<tool> [OPTIONS]... <drawing file>`，输入既可以是 DWG 也可以是 DXF（同一套读取器），输出文件名由输入名推导：

| 工具 | 用途 |
|------|------|
| `dwginfo` / `dxfinfo` | 列出图层、块或实体总数 |
| `dwg2csv` | 实体导出为 CSV |
| `dwg2bmp` / `bmp2dwg` | 图纸 → 位图（BMP/PNG…）/ 位图 → 图纸 |
| `dwg2svg` / `svg2dwg` | 图纸 ↔ SVG |
| `dwg2pdf` | 图纸 → PDF |
| `dwg2dwg` / `pdf2dwg` | 版本转换 / PDF → DXF |
| `dwghatch` / `dwghatcharea` | 生成填充 / 统计填充面积 |
| `dwgexplode` | 炸开块参照 |
| `merge` / `bbox` | 合并图纸 / 求包围盒 |
| `dwgmapconvert` / `dwg2maptiles` | 地理坐标转换 / 生成地图切片 |
| `dwgnest` | CAM 排料（属 QCAD/CAM） |

工具名以 `dwg2*` 起头（表示读 DWG/DXF），没有 `dxf2pdf`、`dxf2svg`、`dxf2bmp` 这类名字。Windows 下是安装目录里的 `.bat` 批处理，macOS 下是 `QCAD-Pro.app/Contents/Resources` 内的 shell 脚本，Linux 下是安装目录内的 shell 脚本。

```bash
# 各工具的完整开关以官方 Command Line Tools 页与 Usage 输出为准
dwginfo drawing.dxf        # 图层 / 块 / 实体统计
dwg2pdf drawing.dxf        # → drawing.pdf
dwg2svg drawing.dxf        # → drawing.svg
dwg2bmp drawing.dxf        # → 位图

# Changelog 中记录的开关示例
dwg2pdf -color-correction drawing.dxf   # 防止白底白线导出（dwg2svg 同名开关）
dwg2pdf -auto-orientation drawing.dxf   # 按块包围盒自动选择纸张方向
```

### 用 `qcad` 本体做无界面转换

控制台工具不够用时（自定义过滤、批量另存版本），直接驱动 `qcad`：

```bash
qcad -no-gui -autostart scripts/File/SaveAs/SaveAs.js \
     -filter "DXF 2000" -outfile output.dxf input.dxf
```

`-no-gui` 无界面、`-autostart` 启动后执行脚本、`-exec` 执行后退出、`-filter` 指定导入过滤器、`-outfile` 指定输出文件。

---

## 自动化批处理（无界面脚本）

把输入文件跟在命令行末尾，`-autostart` 指定的脚本用 `getDocument()`（或 EAction 里的 `this.getDocument()`）就能拿到它，不必自己写导入逻辑：

```bash
# 逐文件调用自带脚本：读 DWG，按 DXF 2000 过滤器另存
for f in *.dwg; do
    qcad -no-gui -autostart scripts/File/SaveAs/SaveAs.js \
         -filter "DXF 2000" -outfile "out/${f%.dwg}.dxf" "$f"
done
```

QCAD 自带的转换脚本位于安装目录的 `scripts/File/`（另存、导出等）与 Pro 版的 `scripts/Pro/`（如 PDF 导出）下，文件名以安装目录实际内容为准；`-outfile` 指定输出路径，`-filter` 指定导入过滤器 / 版本。

需要更细的控制时，脚本内部直接用前文的 `RDocument` + `RAddObjectsOperation` / `RModifyObjectsOperation` 批量改实体，再走另存或控制台工具出图。

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

## 典型工作流

### 工作流一：ECMAScript 脚本自动绘图

1. 创建 `.js` 脚本文件，`include("scripts/EAction.js")` 引入基础类
2. 继承 `EAction`，在 `beginEvent()` 中通过 `this.getDocument()` 获取文档
3. 构建 `RLineEntity`/`RCircleEntity` 等实体对象
4. 使用 `RAddObjectsOperation` 批量添加实体
5. `doc.applyOperation(op)` 提交操作
6. 通过 `Misc → Run script` 运行，或 `qcad -no-gui -autostart script.js` 无界面执行

### 工作流二：命令行批量格式转换

1. 单个文件转格式：`dwg2pdf` / `dwg2svg` / `dwg2bmp` 直接吃 DWG 或 DXF，输出名由输入名推导
2. 先摸底再批量：`dwginfo` 列图层、块与实体数，确认图纸不是空布局
3. 白色实体导出丢失时给 `dwg2pdf` / `dwg2svg` 加 `-color-correction`
4. 需要指定 DXF 版本或自定义过滤器时改用 `qcad -no-gui -autostart … -filter … -outfile …`
5. Shell 循环遍历目录，把控制台工具或上述 `qcad` 命令逐文件调用

---

## 性能优化

1. 大文件：编辑期关掉暂不参与的图层（Layers 对话框），减少每次操作的重绘与求交开销
2. 使用 `RDocument` + `RMemoryStorage` 处理无 UI 转换
3. `RAddObjectsOperation.addObject(obj, false)` 不立即更新空间索引
4. 大量实体批量提交后再 `applyOperation`
5. 禁用快照（snap）与轨迹（tracking）以加速绘制

---

## 常见问题

| 问题 | 解决 |
|------|------|
| DWG 打不开 | CE 的 DWG 支持有限：在 Preferences → File I/O 配置 ODA File Converter，或先用其把 DWG 转成 DXF 再处理 |
| 字体缺失 | 复制 .shx/.ttf 到 `fonts/` 目录或安装到系统 |
| 中文显示乱 | 设置图层使用支持 CJK 的字体（如 simhei） |
| 脚本路径错 | 使用绝对路径或 `documentInterface.getDocument()` |
| 找不到 `dwg2pdf` / `dwg2svg` | 它们是 QCAD Professional 安装自带的控制台工具，社区版没有；Windows 为安装目录下的 `.bat`，macOS 在 `QCAD-Pro.app/Contents/Resources`，Linux 为安装目录下的 shell 脚本 |
| 导出的 PDF / SVG 里白色实体看不见 | 白底白线，用 `dwg2pdf -color-correction` / `dwg2svg -color-correction` |
| 批量改 DXF 版本 | `qcad -no-gui -autostart scripts/File/SaveAs/SaveAs.js -filter "DXF 2000" -outfile out.dxf in.dxf` |
| `-no-gui` 跑完不退出 | 改用 `-exec script.js`（执行完即退出），或在脚本里自行结束流程 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应根据场景选择 QCAD 接口——交互式操作使用 GUI 命令，批处理使用 Pro 版控制台工具（`dwginfo`、`dwg2pdf`、`dwg2svg`、`dwg2bmp` 等），控制台工具覆盖不到的转换用 `qcad -no-gui -autostart script.js` 无界面运行脚本。ECMAScript 脚本遵循「获取文档 → 构建操作（RAddObjectsOperation 等）→ applyOperation」的模式。
- **关键注意事项**：① 社区版的 DWG 支持有限，需 ODA File Converter 或先转 DXF；② 脚本需 `include("scripts/EAction.js")` 继承 EAction；③ 批量操作使用 `RAddObjectsOperation.addObject(obj, false)` 不立即更新空间索引，最后统一 `applyOperation`；④ 中文字体使用 CJK 支持的 TTF（如 simhei）；⑤ 控制台工具只在 Professional 安装中存在，且各平台位置不同。
- **常用代码模式**：简单的几何添加：`var line = new RLineEntity(doc, new RLineData(new RVector(0,0), new RVector(100,50)))` → `var op = new RAddObjectsOperation()` → `op.addObject(line)` → `doc.applyOperation(op)`。CLI 转换：`dwg2pdf drawing.dxf` / `dwg2svg drawing.dxf`（输入可为 DWG 或 DXF，输出名由输入名推导）。
- **不要臆造**：不存在 `dxf2pdf`、`dxf2svg`、`dxf2bmp` 这类命令；`dwg2dxf` 是 LibreDWG 的工具而非 QCAD 控制台工具列表中的条目；QCAD 脚本 API 名称以 <https://api.qcad.org/> 为准，未确认的类名与开关不要写进代码。

---

## 相关技能

- **librecad** — 开源 2D CAD，DXF 编辑：[../librecad/SKILL.md](../librecad/SKILL.md)
- **libredwg** — DWG/DXF 文件格式读写库：[../libredwg/SKILL.md](../libredwg/SKILL.md)
- **lightcad** — Web 2D CAD 框架：[../lightcad/SKILL.md](../lightcad/SKILL.md)
- **ifoxcad** — AutoCAD .NET 二次开发框架（类似的插件开发模式）：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)

---

## 参考资源

- 文档：<https://qcad.org/en/qcad-documentation>
- API：<https://api.qcad.org/>
- 控制台工具：<https://qcad.org/en/qcad-command-line-tools>
- 论坛：<https://qcad.org/rsforum/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/qcad/>
