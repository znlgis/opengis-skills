---
name: librecad
description: "Use when editing 2D DXF/DWG drawings with LibreCAD 2.2.1 — floor plans, mechanical drawings, laser-cut layouts — or scripting conversions with the librecad dxf2pdf / dxf2svg / dxf2png / dwg2dxf command line; also when CJK text renders as boxes (missing TTF/SHX fonts), a DWG will not open without ODA File Converter or LibreDWG dwg2dxf, or dimensions are too small to read. LibreCAD: Qt/C++ open-source 2D CAD, community fork of QCAD."
tags:
  - 2d
  - cad
  - dxf
  - dwg
  - qt
  - cpp
  - drafting
  - cli
---

> **项目地址：** <https://github.com/LibreCAD/LibreCAD>
>
> **官网：** <https://librecad.org/>
>
> **Wiki：** <https://github.com/LibreCAD/LibreCAD/wiki>
>
> **许可证：** GPL-2.0
>
> **最新稳定版：** v2.2.1.6（2026-10-17 发布，截至 2026-10，见 [GitHub Releases](https://github.com/LibreCAD/LibreCAD/releases)）

## 概述

LibreCAD 主要特性：

- 2D 矢量绘图：线/圆/弧/椭圆/多段线/样条/标注/文字/图案填充
- 图层、块、属性、坐标输入（绝对/相对/极坐标）
- 文件：DXF 读写（命令行 `-V` 可选 r12/r14/r2000/r2004/r2007（缺省）/r2010/r2013/r2018）、PDF/SVG/PNG 导出、DWG 经 ODA File Converter 或 LibreDWG 转换
- 跨平台：Windows、macOS、Linux
- 国际化：含完善的中文界面
- 底层文件读写：由 [libdxfrw](https://github.com/LibreCAD/libdxfrw) 提供——LibreCAD 的 C++ DXF/DWG 读写库，承担 DXF 解析与 DWG 转换

> 读写 DWG 原生支持有限，建议先用 LibreDWG 或 ODA 转 DXF。

---

## 安装

```bash
# macOS（Homebrew 只有 cask，没有 formula）
brew install --cask librecad

# Linux：发行版仓库
sudo apt install librecad

# Windows / 其它平台：官方下载页（含 AppImage / DMG / MSI）
# https://librecad.readthedocs.io/ 与 https://librecad.org/ 的下载入口
```

验证安装与命令行转换器：

```bash
librecad                                   # 启动 GUI
librecad dxf2pdf -h                        # 打印该子命令的完整开关
```

> 子命令集合随构建而变：master 分支 README 记录的是 `librecad <command> [options] <input files>` 一组转换器（`dxf2pdf`/`dxf2png`/`dxf2svg`/`dxf2dwg` 与 `dwg2pdf`/`dwg2png`/`dwg2svg`/`dwg2dxf`），其中 DWG 读写要求构建时启用 `DWGSUPPORT`。发出转换命令前一律先用 `librecad <command> -h` 确认当前安装包是否带该子命令。

---

## 界面与基本操作

| 区域 | 用途 |
|------|------|
| 顶部菜单 | File / Edit / View / Plugins / Tools / Drawing / Dimension / Modify / Info |
| 左侧工具栏 | 绘图（CAD Toolbars）、捕捉、修改 |
| 命令行（按 ":" 唤出） | 类 AutoCAD 命令输入 |
| 图层管理 | 右侧 Layer List |
| 块管理 | 右侧 Block List |

### 常用命令缩写

| 命令 | 功能 |
|------|------|
| `li` | line 直线 |
| `ci` | circle 圆 |
| `re` | rectangle |
| `pl` | polyline 多段线 |
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
| `100,50` | 绝对笛卡尔 |
| `@100,50` | 相对笛卡尔（相对上一点） |
| `@100<30` | 相对极坐标（长度<角度） |

---

## 图层与块

- **图层**：右侧面板 → New，可设置颜色/线型/线宽/打印开关
- **块**：选中要素 → 右键 → Create Block，或 Drawing → Block → New
- 当前图层在状态栏切换；锁定/隐藏/冻结按钮

---

## 标注

- 线性、对齐、半径、直径、角度、引线
- 标注样式：`Options → Drawing Preferences → Dimensions`
- 全局标注比例 + 字高

---

## 图案填充与文字

- Hatch：选中边界 → 选图案（ANSI/ISO/Earth/Solid）+ 比例 + 角度
- 文字：单行 / 多行；支持 SHX 与 TTF 字体；中文使用 `Noto Sans CJK SC` 等

---

## 文件交互

GUI 入口用菜单（不是命令）：

```text
File → Open / Save As / Export
File → Export → Export as PDF
```

DWG 需要外部工具转换：

```bash
# ODA File Converter（图形安装后提供同名 CLI）
ODAFileConverter input.dwg . ACAD2010 DXF 1 0

# 或 LibreDWG
dwg2dxf -y input.dwg            # → input.dxf
```

---

## 命令行与批处理

`librecad` 本体除打开图纸外，还提供一组转换子命令（形式为 `librecad <command> [options] <input files>`），可在无图形界面下出图：

```bash
# DWG → DXF R2018
librecad dwg2dxf -V r2018 -o drawing.dxf drawing.dwg

# DXF → 铺满页面并居中的 PDF
librecad dxf2pdf -a -o drawing.pdf drawing.dxf

# DXF → SVG / PNG
librecad dxf2svg -o drawing.svg drawing.dxf
librecad dxf2png -o drawing.png drawing.dxf
```

要点（取自仓库 README 与 `librecad <command> -h` 输出）：

- 输出缺省写在输入文件旁、同名换扩展名；`-t <directory>` 指定输出目录，`-o <file>` 指定输出文件名，两者不可同时用；`-o` 只接受单个输入（PDF 例外，可多图合并）
- PDF：`-a` 适配居中，`-p <WxH>` 纸张毫米尺寸，`-r <DPI>` 分辨率；PNG：`-r <WxH>` 像素尺寸
- DWG/DXF 输出：`-V` 选版本（DWG 为 `r2000`/`r2004`/`r2007`/`r2010`/`r2013`/`r2018`；DXF 额外支持 `r12`/`r14`，缺省 `r2007`）
- 无显示器的服务器上出 PDF/PNG/SVG 前设 `QT_QPA_PLATFORM=offscreen`
- Windows 上 `LibreCAD.exe` 是 GUI 程序：命令行不会等待转换结束也不设置退出码，脚本里要用 `start /wait "" LibreCAD.exe ...`（cmd）或 `Start-Process -Wait -PassThru`（PowerShell）

LibreCAD 没有通用脚本引擎；需要程序化生成/改写 DXF 时配合：

- `ezdxf`（Python 库）做 DXF 解析与生成
- LibreDWG（`dwg2dxf`）做 DWG ↔ DXF
- `inkscape` 做 DXF → SVG/PDF

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

## 典型工作流

### 工作流一：DWG 批量转 PDF（命令行，端到端）

输入：`data/*.dwg`；输出：`out/*.pdf`。

1. 先看单文件能不能转，并确认子命令存在：`librecad dwg2pdf -h`
2. 建输出目录，逐文件转换（`-o` 必须配合单个输入）：
   ```bash
   mkdir -p out
   for f in data/*.dwg; do
       base=$(basename "$f" .dwg)
       librecad dwg2pdf -a -o "out/$base.pdf" "$f"
   done
   ```
3. 服务器/容器里没有显示器时先 `export QT_QPA_PLATFORM=offscreen`
4. 打开任一 PDF 抽查图层与中文文字；PDF 页面尺寸不对时用 `-p <WxH>`（毫米）与 `-r <DPI>` 调整
5. 大批量转换前先跑 3 个文件，确认 `-h` 列出的开关在本机构建上确实存在，再全量执行

### 工作流二：绘制并交付建筑平面图（GUI）

1. 新建文件，设置绘图单位（Drawing Preferences → Units → mm）
2. 创建图层（墙体/门窗/标注/文字），设置颜色与线型
3. 用 `li` 画轴线，`re` 画矩形墙体，`ci` 画圆形柱
4. `tr` 修剪交叉线，`pl` 画多段线轮廓
5. 加线性/对齐标注（`dimlinear`/`dimaligned`）
6. 交付：`File → Export → Export as PDF` 出图，另存 DXF R2007 交给 AutoCAD/其它软件

### 工作流三：程序化生成 DXF 再回读

1. 用 `ezdxf` 生成图纸（见上节代码）
2. `librecad dwg2dxf ...` 或直接打开 DXF 校验图层/字体
3. 需要批量改写时回到 `ezdxf`/LibreDWG 处理，再回 LibreCAD 出图

---

## 性能与稳定性

1. 大图分图层管理，关闭不必要图层
2. 关闭 OSNAP 中过多选项
3. 导出 PDF 前 `Tools → Recalculate Dimensions`
4. 备份 .dxf；DXF R2007 比 R12 信息更全
5. 中文路径在 Windows 下避免
6. 批处理一台机器串行跑即可：`librecad` 子命令本身不并发，多个实例同时写同一输出目录会互相覆盖

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 中文乱码 / 显示方框 | 改用 TTF 字体（`SimHei`、`Noto Sans CJK SC`）；仍用 SHX 时把字体文件放进 `fonts/` 目录 |
| 打不开 DWG | LibreCAD 的 DWG 支持依赖构建选项与 ODA/libdxfrw；用 ODA File Converter 或 `dwg2dxf` 先转 DXF |
| 标注比例小、看不见 | Drawing Preferences → Dimensions → General Scale，改全局比例与字高 |
| 启动即崩溃 | 删除配置 `~/.config/LibreCAD/LibreCAD.conf`（Windows 为安装目录/用户配置下同名文件）重置 |
| 无法填充（hatch 失败） | 先闭合边界；多段线要首尾相接，检查孔/外边界顺序 |
| `librecad dxf2pdf` 提示未知命令 | 该安装包未带转换子命令（不同构建/版本子命令集不同）；用 `librecad -h` 看可用项，或升级到带转换器的构建 |
| Windows bat 里转换"瞬间返回"、后续步骤拿不到文件 | `LibreCAD.exe` 是 GUI 程序，脚本不会等待；改用 `start /wait "" LibreCAD.exe dxf2pdf ...`（cmd）或 `Start-Process -Wait -PassThru` |
| 无显示器环境报 Qt 平台插件错误 | 设 `QT_QPA_PLATFORM=offscreen` 再跑 PDF/PNG/SVG 转换 |
| 导出的 PDF 里白色实体消失 | 白底白线的正常现象；出图前把白色图层临时改为深色，或换用带颜色校正选项的构建（先 `-h` 确认） |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应优先使用 DXF 作为中间交换格式——DWG 先用 ODA File Converter 或 LibreDWG `dwg2dxf` 转 DXF，再用 LibreCAD 编辑或 `librecad dxf2pdf`/`dxf2svg` 出图。批处理一律走命令行子命令，GUI 步骤只作为人工兜底。
- **关键注意事项**：① 子命令集合随构建而变，调用任何 `librecad <command>` 前先用 `-h` 确认；② `-o` 只能配单个输入（PDF 可多图合并），`-t`/`-o` 不可同时用；③ 中文文字要用 TTF 或把 SHX 放进 `fonts/`；④ 大图分图层管理并关闭多余 OSNAP；⑤ 命令缩写（`li`/`ci`/`pl`/`tr`/`mi`）与 AutoCAD 相似但不完全相同。
- **常用代码模式**：命令行转换 = `librecad dwg2dxf -V r2018 -o drawing.dxf drawing.dwg` / `librecad dxf2pdf -a -o drawing.pdf drawing.dxf`。Python 生成 DXF = `ezdxf.new('R2010')` → `msp.add_line/add_circle` → `doc.saveas('out.dxf')`。
- **不要臆造**：LibreCAD 没有通用内嵌脚本引擎（不要写 `librecad --script`）；不存在 `librecad --version` 的保证，验证版本请查 GUI About 或安装包元数据。

---

## 相关技能

- **qcad** — 2D CAD 软件，ECMAScript 脚本扩展与 DWG/DXF 处理：[../qcad/SKILL.md](../qcad/SKILL.md)
- **libredwg** — DWG/DXF 文件格式读写库（C 语言）：[../libredwg/SKILL.md](../libredwg/SKILL.md)
- **lightcad** — Web 2D CAD 框架，DXF 导入导出：[../lightcad/SKILL.md](../lightcad/SKILL.md)
- **ifoxcad** — AutoCAD .NET 二次开发框架：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/LibreCAD/LibreCAD>
- Wiki：<https://github.com/LibreCAD/LibreCAD/wiki>
- 用户手册：<https://librecad.readthedocs.io/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/LibreCAD/>
