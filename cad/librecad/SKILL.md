---
name: librecad
description: "Use when editing 2D DXF/DWG drawings with a lightweight open-source CAD �?floor plans, mechanical drawings, laser cutting layouts. LibreCAD: open-source 2D CAD based on Qt/C++, community edition fork of QCAD."
tags: [2d, cad, dxf, dwg, qt, drafting]
---

> **项目地址�?* <https://github.com/LibreCAD/LibreCAD>
>
> **官网�?* <https://librecad.org/>
>
> **Wiki�?* <https://github.com/LibreCAD/LibreCAD/wiki>
>
> **许可证：** GPL-2.0

## 概述

LibreCAD 主要特性：

- 2D 矢量绘图：线/�?�?椭圆/多段�?样条/标注/文字/图案填充
- 图层、块、属性、坐标输入（绝对/相对/极坐标）
- 文件：DXF（R12/R2007 读写）、PDF/SVG/PNG（导出）、DWG（通过 ODA File Converter �?LibreDWG 转换�?
- 跨平台：Windows、macOS、Linux
- 国际化：含完善的中文界面

> 读写 DWG 原生支持有限，建议先�?LibreDWG �?ODA �?DXF�?

---

## 安装

```bash
# Linux
sudo apt install librecad

# macOS
brew install librecad

# Windows / 其它：从官网下载
```

---

## 界面与基本操�?

| 区域 | 用�?|
|------|------|
| 顶部菜单 | File / Edit / View / Plugins / Tools / Drawing / Dimension / Modify / Info |
| 左侧工具�?| 绘图（CAD Toolbars）、捕捉、修�?|
| 命令行（�?":" 唤出�?| �?AutoCAD 命令输入 |
| 图层管理 | 右侧 Layer List |
| 块管�?| 右侧 Block List |

### 常用命令缩写

| 命令 | 功能 |
|------|------|
| `li` | line 直线 |
| `ci` | circle �?|
| `re` | rectangle |
| `pl` | polyline 多段�?|
| `tr` | trim 修剪 |
| `mi` | mirror 镜像 |
| `co` / `cp` | copy |
| `mv` | move |
| `ro` | rotate |
| `sc` | scale |
| `os` | osnap 对象捕捉 |
| `di` | distance 测距 |
| `pu` | purge |

---

## 坐标输入

| 输入 | 含义 |
|------|------|
| `100,50` | 绝对笛卡�?|
| `@100,50` | 相对笛卡尔（相对上一点） |
| `@100<30` | 相对极坐标（长度<角度�?|

---

## 图层与块

- **图层**：右侧面�?�?New，可设置颜色/线型/线宽/打印开�?
- **�?*：选中要素 �?右键 �?Create Block，或 Drawing �?Block �?New
- 当前图层在状态栏切换；锁�?隐藏/冻结按钮

---

## 标注

- 线性、对齐、半径、直径、角度、引�?
- 标注样式：`Options �?Drawing Preferences �?Dimensions`
- 全局标注比例 + 字高

---

## 图案填充与文�?

- Hatch：选中边界 �?选图案（ANSI/ISO/Earth/Solid�? 比例 + 角度
- 文字：单�?/ 多行；支�?SHX �?TTF 字体；中文使�?`Noto Sans CJK SC` �?

---

## 文件交互

```bash
# DXF（自带）
File �?Open / Save As / Export

# DWG �?DXF（需�?ODA File Converter�?
ODAFileConverter input.dwg . ACAD2010 DXF 1 0
# �?
dwg2dxf -y input.dwg            # LibreDWG

# 导出 PDF
File �?Export �?Export as PDF
```

---

## 命令行（无界面）

```bash
# 启动并运行命令脚本（需自定义脚本插件支持）
librecad --no-startup-window

# 配合 dxf-tools / Python 脚本批处�?
```

LibreCAD 自身脚本能力较弱；批量转换建议结合：

- LibreDWG 转换 DWG �?DXF
- `ezdxf`（Python 库）�?DXF 解析与生�?
- `inkscape` �?DXF �?SVG/PDF

---

## ezdxf 配合 LibreCAD

```python
import ezdxf
doc = ezdxf.new('R2010')
msp = doc.modelspace()
msp.add_line((0,0), (100,0))
msp.add_circle((50,0), 10)
doc.saveas('out.dxf')   # LibreCAD 可直接打开
```

---

## 性能与稳定�?

1. 大图分图层管理，关闭不必要图�?
2. 关闭 OSNAP 中过多选项
3. 导出 PDF �?`Tools �?Recalculate Dimensions`
4. 备份 .dxf；DXF R2007 �?R12 信息更全
5. 中文路径�?Windows 下避�?

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 中文乱码 | 切换字体�?TTF（`SimHei`/`Noto`），SHX 字体文件放入 `fonts/` |
| DWG 打不开 | �?ODA File Converter �?LibreDWG �?DXF |
| 标注比例小看不见 | Drawing Preferences �?Dimensions �?General Scale |
| 打开崩溃 | 删除 `~/.config/LibreCAD/LibreCAD.conf` 重置 |
| 无法填充 | 闭合多段线后�?hatch；检查孔/外边界顺�?|

---

## AI 使用建议

- **推荐工作流模�?*：AI 助手应优先使�?DXF 作为中间交换格式——DWG 文件先通过 ODA File Converter �?LibreDWG 转为 DXF，再�?LibreCAD 编辑。批处理场景�?`ezdxf`（Python 库）配合 CLI 工具完成�?
- **关键注意事项**：① DWG 原生支持有限，应�?DXF 为主交换格式；② 中文文字需使用 TTF 字体（`Noto Sans CJK SC` / `SimHei`），SHX 需放入 `fonts/` 目录；③ 大图应分图层管理、关闭不必要 OSNAP；④ 命令缩写（`li`/`ci`/`pl`/`tr`/`mi`）与 AutoCAD 相似但不完全相同�?
- **常用代码模式**：GUI 交互：按 `:` 唤出命令�?�?输入命令缩写 �?坐标输入（`@100,50` 相对笛卡尔，`@100<30` 相对极坐标）。Python 批处理：`ezdxf.new('R2010')` �?`msp.add_line/add_circle` �?`doc.saveas('out.dxf')`�?

---

## 相关技�?

- **qcad** �?2D CAD 软件，ECMAScript 脚本扩展�?DWG/DXF 处理：[../qcad/SKILL.md](../qcad/SKILL.md)
- **libredwg** �?DWG/DXF 文件格式读写库（C 语言）：[../libredwg/SKILL.md](../libredwg/SKILL.md)
- **lightcad** �?Web 2D CAD 框架，DXF 导入导出：[../lightcad/SKILL.md](../lightcad/SKILL.md)
- **ifoxcad** �?AutoCAD .NET 二次开发框架：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)

---

## 典型工作�?

### 工作流一：绘制建筑平面图

1. 新建文件，设置绘图单位（Drawing Preferences �?Units �?mm�?
2. 创建图层（墙�?门窗/标注/文字），设置颜色与线�?
3. 使用 `li` 命令绘制轴线，`re` 绘制矩形墙体，`ci` 绘制圆形�?
4. `tr` 修剪交叉线，`pl` 绘制多段线轮�?
5. 添加线�?对齐标注（`dimlinear`/`dimaligned`�?
6. 导出 PDF 用于打印，或保存 DXF R2007 用于 AutoCAD 交换

### 工作流二：批量转�?DWG �?DXF

1. 安装 ODA File Converter �?LibreDWG 工具（`dwg2dxf`�?
2. `ODAFileConverter input.dwg . ACAD2010 DXF 1 0` �?`dwg2dxf -y input.dwg`
3. �?LibreCAD 中打开生成�?DXF，检查中文文字和图层
4. 必要时用 `ezdxf` Python 脚本修复格式问题
5. 保存�?R2007 DXF，确保兼容�?

---

## 参考资�?

- 仓库�?https://github.com/LibreCAD/LibreCAD>
- Wiki�?https://github.com/LibreCAD/LibreCAD/wiki>
- 用户手册�?https://librecad.readthedocs.io/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/librecad/>