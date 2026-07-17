---
name: kicad
description: "Use when designing electronic circuits and PCBs  -- ?schematic capture, PCB layout, 3D viewer, SPICE simulation, Gerber export. KiCad: the leading open-source EDA/PCB design suite."
tags: [eda, pcb, electronics, schematic, gerber, python]
---

> **项目地址 -- ?* <https://gitlab.com/kicad/code/kicad>
>
> **官网 -- ?* <https://www.kicad.org/>
>
> **官方文档 -- ?* <https://docs.kicad.org/>
>
> **API（Python）：** <https://docs.kicad.org/doxygen-python/>
>
> **许可证：** GPL-3.0+

## 概述

KiCad 主要程序 -- ?

| 程序 | 用 -- ?|
|------|------|
| KiCad（项目管理） | 项目入口 |
| Eeschema | 原理图编 -- ?|
| Symbol Editor | 元件符号 -- ?|
| Pcbnew | PCB 布局布线 |
| Footprint Editor | 封装 -- ?|
| 3D Viewer | 3D 预览 |
| GerbView | Gerber 浏览 |
| BOM 工具 | 物料清单 |
| CLI（KiCad 7+ -- ?| 自动化（`kicad-cli` -- ?|

新版本改进（KiCad 7/8/9/10，当前稳定版 10.0.x -- ?026）：

- 全新原生 Python API（`pcbnew`），支持脚本扩展
- 标准 IPC-2581 输出
- 多板设计 / 互连
- DRC 规则丰富（差分对、长度匹配）

---

## 安装

```bash
# Linux
sudo add-apt-repository --yes ppa:kicad/kicad-10.0-releases
sudo apt install kicad

# macOS
brew install --cask kicad

# Windows: 安装 -- ?
```

库（Symbols/Footprints/3D Models）随主程序安装；亦可单独 `kicad-symbols / kicad-footprints / kicad-packages3D` 仓库 git 跟踪 -- ?

---

## 工作 -- ?

```
新建 Project (.kicad_pro)
     -- ?
    ├── 1. 原理 -- ?(.kicad_sch)：放置元 -- ? -- ?连线  -- ?注释  -- ?总线  -- ?分页
     -- ?       -- ?
     -- ?      └── ERC（Electrical Rules Check -- ?
     -- ?
    ├── 2. 分配封装：Tools  -- ?Assign Footprints（CvPcb -- ?
     -- ?
    ├── 3. 生成网表 / 同步 -- ?PCB（Update PCB from Schematic -- ?
     -- ?
    ├── 4. PCB 布局 (.kicad_pcb)：摆 -- ? -- ?布线  -- ?覆铜  -- ?DRC
     -- ?
    ├── 5. 3D 预览 / 导出 STEP
     -- ?
    └── 6. 制造输出：Gerber + Drill + Pick & Place + BOM
```

---

## 原理图（Eeschema）要 -- ?

- 元件：`A` 添加；`R/L/C` 等快捷键
- 连线：`W` Wire、`B` Bus
- 注释：Tools  -- ?Annotate Schematic
- 电气规则：`ERC`（菜 -- ?Inspect  -- ?ERC -- ?
- 分页：File  -- ?Schematic Setup  -- ?Page Settings；分页通过 Hierarchical Sheet
- 总线展开：`{NET[0..7]}`

---

## PCB（Pcbnew）要 -- ?

- 板框：Edge.Cuts 层用 `Polygon`  -- ?`Line`  -- ?
- 摆件：拖 -- ?/ 旋转 / 翻面 (`F`)
- 走线：`X` 起线、`V` 通孔 / 切层
- 网络规则：`File  -- ?Board Setup  -- ?Net Classes`
- 覆铜：`Add Filled Zone`，绑 -- ?GND/PWR
- DRC：`Inspect  -- ?Design Rules Checker`
- 推走线：菜单 Route  -- ?Interactive Router
- 长度调谐：Route  -- ?Tune Length

---

## 库管 -- ?

- 全局库：`Preferences  -- ?Manage Symbol/Footprint Libraries`（按用户/项目级别 -- ?
- 推荐项目级库：在项目目录新建 `lib/`  -- ?`.kicad_sym` / `.pretty/`
- KiCad 5.x  -- ?.lib / .mod 可通过 `Symbol Library Editor` 导入

---

## 制造输出（Gerber + Drill -- ?

```
File  -- ?Plot
  Layers: F.Cu, B.Cu, F.Mask, B.Mask, F.Silkscreen, B.Silkscreen, Edge.Cuts (+ inner)
  Format: Gerber (X2 推荐)
  Generate Drill Files  -- ?Excellon / Gerber X2

输出 -- ?
  *-F_Cu.gbr / *-B_Cu.gbr ...
  *-PTH.drl / *-NPTH.drl
  *-F_Pos.csv / *-B_Pos.csv  (Pick & Place)
```

打包 -- ?ZIP 上传给嘉立创/PCBWay/JLC 等代工厂 -- ?

---

## CLI 自动化（KiCad 7+ -- ?

```bash
# 原理图导 -- ?PDF
kicad-cli sch export pdf project/main.kicad_sch -o sch.pdf

# 网表
kicad-cli sch export netlist project/main.kicad_sch -o net.net

# Gerber + Drill
kicad-cli pcb export gerbers project/board.kicad_pcb -o gerber/
kicad-cli pcb export drill   project/board.kicad_pcb -o gerber/

# Pick & Place
kicad-cli pcb export pos     project/board.kicad_pcb --format csv -o pos.csv

# STEP -- ?D -- ?
kicad-cli pcb export step    project/board.kicad_pcb -o board.step
```

---

## Python 脚本（pcbnew -- ?

```python
import pcbnew

board = pcbnew.LoadBoard("board.kicad_pcb")
for fp in board.GetFootprints():
    print(fp.GetReference(), fp.GetValue(), fp.GetPosition())

# 添加新走 -- ?
track = pcbnew.PCB_TRACK(board)
track.SetStart(pcbnew.VECTOR2I_MM(10, 10))
track.SetEnd  (pcbnew.VECTOR2I_MM(20, 10))
track.SetLayer(pcbnew.F_Cu)
track.SetWidth(pcbnew.FromMM(0.25))
board.Add(track)

pcbnew.SaveBoard("out.kicad_pcb", board)
```

KiCad 8 中改 -- ?`pcbnew.VECTOR2I` + `pcbnew.FromMM`，旧 5/6  -- ?`wxPoint` + `pcbnew.FromMM` -- ?

---

## 性能与最佳实 -- ?

1. **使用项目级符 -- ?封装 -- ?*，便于版本管 -- ?
2. **网络类（Net Class -- ?*预设差分 -- ?/ 高速信号宽度间 -- ?
3. **覆铜后及 -- ?Refill Zones (`B`)** 检 -- ?
4. **DRC** 在每次重要修改后运行；不要忽略红色错 -- ?
5. **3D 模型**：使 -- ?STEP  -- ?WRL 体积小且更适合 STEP 联合导出
6. **多人协作**：用 Git LFS 管理 .kicad_pcb；避免冲 -- ?

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 元件找不 -- ?footprint |  -- ?Symbol 属性中绑定 footprint，或 -- ?CvPcb 重新分配 |
| 中文丝印 | 选支持中文的 TTF（KiCad 6+ 起支 -- ?TTF/OTF）；更早版本 -- ?stroke 字体 |
| Gerber 不全 | 板厂常需 -- ?`F.Mask/B.Mask/F.Silk/B.Silk/Edge.Cuts/F.Cu/B.Cu` + 钻孔 |
| 覆铜失效 | 重新 Refill；检查热焊盘连接 |
| 嘉立创不识别 | 输出格式 -- ?X2；勾 -- ?`Plot pad on silk` 关闭 |

---

## AI 使用建议

- **推荐工作流模 -- ?*：AI 助手应遵 -- ?KiCad 标准设计流程：原理图（Eeschema）→ 封装分配  -- ?PCB（Pcbnew）→ DRC  -- ?制造输出。自动化批处理使 -- ?`kicad-cli` 命令行工具，Python 脚本使用 `pcbnew` 模块 -- ?
- **关键注意事项**：① ERC/DRC 必须在每次重要修改后运行，红色错误不可忽略； -- ?元件封装需在原理图阶段绑定，否则同步到 PCB 时会丢失；③ Gerber 输出需包含完整层栈（F.Cu/B.Cu/F.Mask/B.Mask/Edge.Cuts/Silk + Drill）； -- ?覆铜后需 Refill Zones 检查热焊盘连接 -- ?
- **常用代码模式**：CLI 自动化：`kicad-cli sch export pdf` / `kicad-cli pcb export gerbers` / `kicad-cli pcb export drill`。Python：`pcbnew.LoadBoard("board.kicad_pcb")`  -- ?遍历 footprints/tracks  -- ?修改  -- ?`pcbnew.SaveBoard()` -- ?

---

## 相关技 -- ?

- **freecad**  -- ?3D 参数 -- ?CAD，可 -- ?KiCad 3D 模型协同：[../freecad/SKILL.md](../freecad/SKILL.md)
- **occt**  -- ?OCCT 几何内核（KiCad 3D Viewer 底层依赖）：[../occt/SKILL.md](../occt/SKILL.md)

---

## 典型工作 -- ?

### 工作流一：从原理图到 PCB 的完整设 -- ?

1. 新建项目（`.kicad_pro`）， -- ?Eeschema 中放置元件符号并联线
2. 运行 ERC 检查电气错误，Annotate 注释元件编号
3. 使用 CvPcb 为每个元件分配封装（Footprint -- ?
4. Update PCB from Schematic 同步网表 -- ?Pcbnew
5.  -- ?Pcbnew 中布局（摆件）、布线（走线）、覆 -- ?
6. 运行 DRC 检查设计规则，修复所有错 -- ?
7. 导出 Gerber + Drill + Pick & Place + BOM 用于制 -- ?

### 工作流二：CI 自动 -- ?Gerber 生成

1.  -- ?CI 环境安装 `kicad`（含 `kicad-cli` -- ?
2. `kicad-cli sch export netlist project/main.kicad_sch -o net.net`
3. `kicad-cli pcb export gerbers project/board.kicad_pcb -o gerber/`
4. `kicad-cli pcb export drill project/board.kicad_pcb -o gerber/`
5. `kicad-cli pcb export pos project/board.kicad_pcb --format csv -o pos.csv`
6. 打包 Gerber + Drill  -- ?ZIP 上传至构建产 -- ?

---

## 参考资 -- ?

- 官方文档 -- ?https://docs.kicad.org/>
- 入门教程（中文） -- ?https://docs.kicad.org/master/zh/getting_started_in_kicad/getting_started_in_kicad.html>
- pcbnew Python -- ?https://docs.kicad.org/doxygen-python/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/kicad/>
