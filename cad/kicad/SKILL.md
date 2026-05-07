---
name: kicad
description: KiCad 是开源跨平台 EDA（电子设计自动化）套件，集成 Eeschema 原理图、Pcbnew PCB 布线、3D 查看、Gerber 输出与器件库管理，是 PCB 设计领域的开源旗舰，广泛用于工业、教育与开源硬件项目。
tags: [eda, pcb, electronics, schematic, gerber, python]
---

> **项目地址：** <https://gitlab.com/kicad/code/kicad>
>
> **官网：** <https://www.kicad.org/>
>
> **官方文档：** <https://docs.kicad.org/>
>
> **API（Python）：** <https://docs.kicad.org/doxygen-python/>
>
> **许可证：** GPL-3.0+

## 概述

KiCad 主要程序：

| 程序 | 用途 |
|------|------|
| KiCad（项目管理） | 项目入口 |
| Eeschema | 原理图编辑 |
| Symbol Editor | 元件符号库 |
| Pcbnew | PCB 布局布线 |
| Footprint Editor | 封装库 |
| 3D Viewer | 3D 预览 |
| GerbView | Gerber 浏览 |
| BOM 工具 | 物料清单 |
| CLI（KiCad 7+） | 自动化（`kicad-cli`） |

新版本（7/8）改进：

- 全新原生 Python API（`pcbnew`），支持脚本扩展
- 标准 IPC-2581 输出
- 多板设计 / 互连
- DRC 规则丰富（差分对、长度匹配）

---

## 安装

```bash
# Linux
sudo add-apt-repository --yes ppa:kicad/kicad-8.0-releases
sudo apt install kicad

# macOS
brew install --cask kicad

# Windows: 安装包
```

库（Symbols/Footprints/3D Models）随主程序安装；亦可单独 `kicad-symbols / kicad-footprints / kicad-packages3D` 仓库 git 跟踪。

---

## 工作流

```
新建 Project (.kicad_pro)
    │
    ├── 1. 原理图 (.kicad_sch)：放置元件 → 连线 → 注释 → 总线 → 分页
    │       │
    │       └── ERC（Electrical Rules Check）
    │
    ├── 2. 分配封装：Tools → Assign Footprints（CvPcb）
    │
    ├── 3. 生成网表 / 同步到 PCB（Update PCB from Schematic）
    │
    ├── 4. PCB 布局 (.kicad_pcb)：摆件 → 布线 → 覆铜 → DRC
    │
    ├── 5. 3D 预览 / 导出 STEP
    │
    └── 6. 制造输出：Gerber + Drill + Pick & Place + BOM
```

---

## 原理图（Eeschema）要点

- 元件：`A` 添加；`R/L/C` 等快捷键
- 连线：`W` Wire、`B` Bus
- 注释：Tools → Annotate Schematic
- 电气规则：`ERC`（菜单 Inspect → ERC）
- 分页：File → Schematic Setup → Page Settings；分页通过 Hierarchical Sheet
- 总线展开：`{NET[0..7]}`

---

## PCB（Pcbnew）要点

- 板框：Edge.Cuts 层用 `Polygon` 或 `Line` 画
- 摆件：拖动 / 旋转 / 翻面 (`F`)
- 走线：`X` 起线、`V` 通孔 / 切层
- 网络规则：`File → Board Setup → Net Classes`
- 覆铜：`Add Filled Zone`，绑定 GND/PWR
- DRC：`Inspect → Design Rules Checker`
- 推走线：菜单 Route → Interactive Router
- 长度调谐：Route → Tune Length

---

## 库管理

- 全局库：`Preferences → Manage Symbol/Footprint Libraries`（按用户/项目级别）
- 推荐项目级库：在项目目录新建 `lib/` 放 `.kicad_sym` / `.pretty/`
- KiCad 5.x 旧 .lib / .mod 可通过 `Symbol Library Editor` 导入

---

## 制造输出（Gerber + Drill）

```
File → Plot
  Layers: F.Cu, B.Cu, F.Mask, B.Mask, F.Silkscreen, B.Silkscreen, Edge.Cuts (+ inner)
  Format: Gerber (X2 推荐)
  Generate Drill Files → Excellon / Gerber X2

输出：
  *-F_Cu.gbr / *-B_Cu.gbr ...
  *-PTH.drl / *-NPTH.drl
  *-F_Pos.csv / *-B_Pos.csv  (Pick & Place)
```

打包成 ZIP 上传给嘉立创/PCBWay/JLC 等代工厂。

---

## CLI 自动化（KiCad 7/8）

```bash
# 原理图导出 PDF
kicad-cli sch export pdf project/main.kicad_sch -o sch.pdf

# 网表
kicad-cli sch export netlist project/main.kicad_sch -o net.net

# Gerber + Drill
kicad-cli pcb export gerbers project/board.kicad_pcb -o gerber/
kicad-cli pcb export drill   project/board.kicad_pcb -o gerber/

# Pick & Place
kicad-cli pcb export pos     project/board.kicad_pcb --format csv -o pos.csv

# STEP（3D）
kicad-cli pcb export step    project/board.kicad_pcb -o board.step
```

---

## Python 脚本（pcbnew）

```python
import pcbnew

board = pcbnew.LoadBoard("board.kicad_pcb")
for fp in board.GetFootprints():
    print(fp.GetReference(), fp.GetValue(), fp.GetPosition())

# 添加新走线
track = pcbnew.PCB_TRACK(board)
track.SetStart(pcbnew.VECTOR2I_MM(10, 10))
track.SetEnd  (pcbnew.VECTOR2I_MM(20, 10))
track.SetLayer(pcbnew.F_Cu)
track.SetWidth(pcbnew.FromMM(0.25))
board.Add(track)

pcbnew.SaveBoard("out.kicad_pcb", board)
```

KiCad 8 中改用 `pcbnew.VECTOR2I` + `pcbnew.FromMM`，旧 5/6 用 `wxPoint` + `pcbnew.FromMM`。

---

## 性能与最佳实践

1. **使用项目级符号/封装库**，便于版本管理
2. **网络类（Net Class）**预设差分对 / 高速信号宽度间距
3. **覆铜后及时 Refill Zones (`B`)** 检查
4. **DRC** 在每次重要修改后运行；不要忽略红色错误
5. **3D 模型**：使用 STEP 比 WRL 体积小且更适合 STEP 联合导出
6. **多人协作**：用 Git LFS 管理 .kicad_pcb；避免冲突

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 元件找不到 footprint | 在 Symbol 属性中绑定 footprint，或用 CvPcb 重新分配 |
| 中文丝印 | 选支持中文的 TTF（KiCad 8+ 支持 TTF）；旧版本仅 stroke 字体 |
| Gerber 不全 | 板厂常需要 `F.Mask/B.Mask/F.Silk/B.Silk/Edge.Cuts/F.Cu/B.Cu` + 钻孔 |
| 覆铜失效 | 重新 Refill；检查热焊盘连接 |
| 嘉立创不识别 | 输出格式选 X2；勾选 `Plot pad on silk` 关闭 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应遵循 KiCad 标准设计流程：原理图（Eeschema）→ 封装分配 → PCB（Pcbnew）→ DRC → 制造输出。自动化批处理使用 `kicad-cli` 命令行工具，Python 脚本使用 `pcbnew` 模块。
- **关键注意事项**：① ERC/DRC 必须在每次重要修改后运行，红色错误不可忽略；② 元件封装需在原理图阶段绑定，否则同步到 PCB 时会丢失；③ Gerber 输出需包含完整层栈（F.Cu/B.Cu/F.Mask/B.Mask/Edge.Cuts/Silk + Drill）；④ 覆铜后需 Refill Zones 检查热焊盘连接。
- **常用代码模式**：CLI 自动化：`kicad-cli sch export pdf` / `kicad-cli pcb export gerbers` / `kicad-cli pcb export drill`。Python：`pcbnew.LoadBoard("board.kicad_pcb")` → 遍历 footprints/tracks → 修改 → `pcbnew.SaveBoard()`。

---

## 相关技能

- **freecad** — 3D 参数化 CAD，可与 KiCad 3D 模型协同：[../freecad/SKILL.md](../freecad/SKILL.md)
- **occt** — OCCT 几何内核（KiCad 3D Viewer 底层依赖）：[../occt/SKILL.md](../occt/SKILL.md)

---

## 典型工作流

### 工作流一：从原理图到 PCB 的完整设计

1. 新建项目（`.kicad_pro`），在 Eeschema 中放置元件符号并联线
2. 运行 ERC 检查电气错误，Annotate 注释元件编号
3. 使用 CvPcb 为每个元件分配封装（Footprint）
4. Update PCB from Schematic 同步网表到 Pcbnew
5. 在 Pcbnew 中布局（摆件）、布线（走线）、覆铜
6. 运行 DRC 检查设计规则，修复所有错误
7. 导出 Gerber + Drill + Pick & Place + BOM 用于制造

### 工作流二：CI 自动化 Gerber 生成

1. 在 CI 环境安装 `kicad`（含 `kicad-cli`）
2. `kicad-cli sch export netlist project/main.kicad_sch -o net.net`
3. `kicad-cli pcb export gerbers project/board.kicad_pcb -o gerber/`
4. `kicad-cli pcb export drill project/board.kicad_pcb -o gerber/`
5. `kicad-cli pcb export pos project/board.kicad_pcb --format csv -o pos.csv`
6. 打包 Gerber + Drill 为 ZIP 上传至构建产物

---

## 参考资源

- 官方文档：<https://docs.kicad.org/>
- 入门教程（中文）：<https://docs.kicad.org/master/zh/getting_started_in_kicad/getting_started_in_kicad.html>
- pcbnew Python：<https://docs.kicad.org/doxygen-python/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/kicad/>