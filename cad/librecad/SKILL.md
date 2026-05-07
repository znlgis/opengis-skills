---
name: librecad
description: LibreCAD 是基于 Qt 的开源 2D CAD 软件，专注 DXF 编辑（R12/R2007），界面与 AutoCAD 经典版相似，适合机械制图、建筑施工图、教育与小型工程团队作为免费替代方案。
---

> **项目地址：** <https://github.com/LibreCAD/LibreCAD>
>
> **官网：** <https://librecad.org/>
>
> **Wiki：** <https://github.com/LibreCAD/LibreCAD/wiki>
>
> **许可证：** GPL-2.0

## 概述

LibreCAD 主要特性：

- 2D 矢量绘图：线/圆/弧/椭圆/多段线/样条/标注/文字/图案填充
- 图层、块、属性、坐标输入（绝对/相对/极坐标）
- 文件：DXF（R12/R2007 读写）、PDF/SVG/PNG（导出）、DWG（通过 ODA File Converter 或 LibreDWG 转换）
- 跨平台：Windows、macOS、Linux
- 国际化：含完善的中文界面

> 读写 DWG 原生支持有限，建议先用 LibreDWG 或 ODA 转 DXF。

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

```bash
# DXF（自带）
File → Open / Save As / Export

# DWG → DXF（需要 ODA File Converter）
ODAFileConverter input.dwg . ACAD2010 DXF 1 0
# 或
dwg2dxf -y input.dwg            # LibreDWG

# 导出 PDF
File → Export → Export as PDF
```

---

## 命令行（无界面）

```bash
# 启动并运行命令脚本（需自定义脚本插件支持）
librecad --no-startup-window

# 配合 dxf-tools / Python 脚本批处理
```

LibreCAD 自身脚本能力较弱；批量转换建议结合：

- LibreDWG 转换 DWG ↔ DXF
- `ezdxf`（Python 库）做 DXF 解析与生成
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

## 性能与稳定性

1. 大图分图层管理，关闭不必要图层
2. 关闭 OSNAP 中过多选项
3. 导出 PDF 前 `Tools → Recalculate Dimensions`
4. 备份 .dxf；DXF R2007 比 R12 信息更全
5. 中文路径在 Windows 下避免

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 中文乱码 | 切换字体到 TTF（`SimHei`/`Noto`），SHX 字体文件放入 `fonts/` |
| DWG 打不开 | 用 ODA File Converter 或 LibreDWG 转 DXF |
| 标注比例小看不见 | Drawing Preferences → Dimensions → General Scale |
| 打开崩溃 | 删除 `~/.config/LibreCAD/LibreCAD.conf` 重置 |
| 无法填充 | 闭合多段线后再 hatch；检查孔/外边界顺序 |

---

## 参考资源

- 仓库：<https://github.com/LibreCAD/LibreCAD>
- Wiki：<https://github.com/LibreCAD/LibreCAD/wiki>
- 用户手册：<https://librecad.readthedocs.io/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/librecad/>
