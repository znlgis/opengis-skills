---
name: solvespace
description: "Use when doing lightweight parametric 2D/3D CAD in SolveSpace 3.3 — constraint sketching, linkage/mechanism checks, section and 2D views, STL for printing, or driving the solver from solvespace-cli / the PyPI slvs package in CI; also when sketch lines turn red (over-constrained) or blue (under-constrained), a constraint value change does not refresh (press Space), an exported STL has holes (Ctrl+Shift+N naked edges), or someone expects STEP import (STEP is export-only)."
tags:
  - 3d
  - 2d
  - parametric
  - cad
  - constraint-solver
  - step
  - dxf
  - python
---

> **项目地址：** <https://github.com/solvespace/solvespace>
>
> **官网：** <https://solvespace.com/>
>
> **文档：** <https://solvespace.com/help.pl>
>
> **许可证：** GPL-3.0+
>
> **最新稳定版：** 3.3（2026-10-21 发布，截至 2026-10，见 [GitHub Releases](https://github.com/solvespace/solvespace/releases)）；主线变化是 NURBS 曲面/边的修复与求解器改进（大尺寸值、此前不收敛的合法约束），以及 3.2 那处"解不出的约束被删除"的回归修复
>
> **参考手册：** <https://solvespace.com/ref.pl> ・ **教程：** <https://solvespace.com/tutorial.pl> ・ **网页版：** <https://solvespace.com/>（同一版本线的 Emscripten 构建）

## 概述

SolveSpace 特性：

- **基于约束求解**：草图通过几何约束（距离、平行、相切、对称…）实时求解
- **参数化 3D**：草图 → 拉伸 / 旋转 / 扫掠 / 螺旋扫掠 / 阵列
- **装配**：导入零件文件（.slvs）+ 3D 约束装配
- **机构分析**：Analyze 菜单的干涉检查、轨迹跟踪（Trace Point）
- **导出**：二维矢量 SVG / PDF / EPS / PS / DXF / HPGL / G 代码（.ngc）/ STEP；网格 STL / OBJ / VRML / Three.js（.js/.html）；精确三维曲面 STEP
- **脚本求解**：Cython 封装的求解器内核发布为 PyPI 包 [`slvs`](https://pypi.org/project/slvs/)（与 SolveSpace 同版号，当前 3.3），可只做约束求解不建模
- **占用极小**：单个可执行文件、无外部几何库依赖，桌面与网页版都能秒开

---

## 安装

```bash
# Linux：官方发行包 / Flatpak / Snap
sudo apt install solvespace
flatpak install flathub com.solvespace.SolveSpace
sudo snap install solvespace

# macOS
brew install --cask solvespace

# Windows：从 GitHub Releases 下载官方安装包（64 位）
```

只用约束求解器（无 GUI，CI 友好）：

```bash
pip install slvs          # 与 SolveSpace 同版号（当前 3.3），预编译 wheel
python -c "import slvs; print(slvs.__file__)"   # 验证可导入
```

自源码构建要求 CMake ≥ 3.31（见仓库 `CMakeLists.txt`），同时产出 `solvespace`（GUI）与 `solvespace-cli`（无头）：

```bash
cmake -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build
```

---

## 建模流程（GUI）

```text
新建文件 (.slvs)
  │
  ├── 1. 选定工作平面（Workplane: XY / YZ / XZ，或 Sketch in New Workplane）
  │       ├─ Sketch 菜单：Line Segment / Rectange / Circle / Arc / Cubic 等
  │       └─ Constraint 菜单：Distance / Angle / Parallel / Symmetric /
  │                           Equal Length / Coincident / Tangent …
  │
  ├── 2. 求解（自动）：黑色 = 完全约束；红色 = 过约束；蓝色 = 欠约束
  │
  ├── 3. Group → New Group 生成实体
  │       ├─ Extrude（拉伸，可勾选 skew 让方向有 3 自由度）
  │       ├─ Lathe / Revolve（旋转体）
  │       └─ Sweep / Helical（扫掠 / 螺旋）
  │
  ├── 4. 在新生成的面上继续草图
  │
  └── 5. File → Export 2d View / 3d Model / Mesh（SVG・DXF・STEP・STL …）
```

---

## 关键快捷键

以下取自源码菜单表（`src/graphicswin.cpp` 的 `Menu[]`，`S`/`C` 分别表示 Shift / Ctrl）。绘图与约束项都是**裸单键**，无需修饰键：

| 键 | 功能 |
|----|------|
| `s` / `r` / `c` / `a` / `b` | 直线段 / 矩形 / 圆 / 圆弧 / Bezier 样条（Sketch 菜单） |
| `p` / `t` | 基准点 / TrueType 文字 |
| `2` / `3` | 在工作平面内绘制 / 在任意 3D 空间绘制 |
| `g` / `Shift+a` / `i` | 切换构造线 / 过点的切弧 / 在交点处拆分曲线 |
| `d` / `n` | Distance·Diameter 距离或直径 / Angle·Equal Angle 角度或等角 |
| `h` / `v` | Horizontal / Vertical（3.2 起任意多条线可一次约束） |
| `q` | Equal Length·Radius 等长/等半径（3.2 起可对三、四条线同时生效） |
| `l` / `[` / `y` / `m` / `x` | 平行或相切 / 垂直 / 对称 / 中点 / 同向 |
| `o` / `]` / `z` / `j` / `;` | 点在线上·面上 / 拖拽锁定 / 比例 / 长度差 / 注释 |
| `Space` | Regenerate All（改完约束值不刷新时手动重算） |
| `f` / `w` / `+` / `-` | 缩放到全部 / 视图对齐工作平面 / 放大 / 缩小 |
| `Ctrl+E` | Select Edge Chain，沿切线连续选中整条轮廓 |
| `Ctrl+Tab` | 显示 / 隐藏工具栏（3.2 起） |
| `Ctrl+Shift+S` | Save As… |
| `Esc` | 全局为取消选择；**绘制中按下会删除当前实体而非完成**（3.2 行为变更） |

Analyze 菜单用 `Ctrl+Shift+字母`：`V` 体积、`A` 面积、`P` 周长、`I` 干涉零件、`N` 裸边（naked edges）、`C` 质心、`F` 高亮欠约束点、`T` 轨迹跟踪、`Shift+T` 停止跟踪、`D` 步进尺寸。

3.2 的多选约束增强：等长（>2 条线）、等直径/半径（>2 个圆弧）、水平/垂直（任意多条线、>2 个点）、点重合（>2 个点）、点在线上（1 点配 1–3 个面）；新增两面平行/垂直约束，相切不再要求端点重合。


---

## Group（组）= 特征树

每个 Group 代表一个建模步骤，New Group 菜单项（快捷键为 `Shift+字母`）：

- `Shift+3` Sketch In 3d（在任意 3D 空间草图）
- `Shift+W` Sketch In New Workplane（在新平面上草图）
- `Shift+X` Extrude（拉伸，3.2 起可勾选 skew，让拉伸方向有 3 个自由度）
- `Shift+L` Lathe / `Shift+V` Revolve（旋转体 / 绕轴回转）
- `Shift+H` Helix（螺旋）
- `Shift+T` Step Translating / `Shift+R` Step Rotating（线性 / 旋转阵列）
- `Shift+I` Link / Assemble…（导入 .slvs 零件做装配）

---

## 装配

1. 创建主装配文件（.slvs）
2. Group → New Group → Link / Assemble…（`Shift+I`）→ 选择一个或多个子零件 .slvs
3. 用 3D 草图约束（距离、同轴、平行、点重合）固定零件位置
4. 移动其中一个零件，约束驱动其它零件随动
5. `Ctrl+Shift+I` 检查干涉零件，`Ctrl+Shift+N` 检查裸边

---

## 导出 STEP 与其它格式

```text
File → Export Surfaces…      → 精确三维曲面，文件名后缀 .step / .stp
File → Export Triangle Mesh… → 三角网格，后缀 .stl / .obj / .wrl / .js / .html
File → Export 2d View…       → 当前视图矢量图，后缀 .svg .pdf .eps .ps .dxf .plt
                               .hpgl .ngc（G 代码）.txt .step（二维 STEP）
File → Export 2d Section…    → 剖切后的二维图，格式同上
File → Export Image…         → PNG 位图
```

要点：

- STEP 由 SolveSpace 自带写出器（`src/exportstep.cpp`）生成，不依赖 OCCT，可被 FreeCAD 等打开
- 二维矢量导出对**锯齿线（zigzag）与点画线（stippled）样式**不支持：3.3 起不会再崩溃，但这些样式仍不会被导出，必要时先改为实线
- 网格密度由 `Configuration…` 的 chord tolerance 控制；导出前用 Analyze → Show Naked Edges 确认实体闭合


## 命令行 / 批处理

自 3.x 起仓库同时构建 `solvespace`（GUI）与 `solvespace-cli`（无头），通用形式：

```bash
solvespace-cli <command> <options> <filename> [filename...]

solvespace-cli version                                                 # 打印版本
solvespace-cli regenerate input.slvs                                   # 重载导入文件、重求解并保存
solvespace-cli thumbnail --output %%-2d.png --view top --size 1024 input.slvs
solvespace-cli export-mesh --output out.stl input.slvs                 # 三角网格（STL 等）
solvespace-cli export-view --output out.svg --view top input.slvs      # 二维矢量视图
solvespace-cli export-wireframe --output out.svg input.slvs            # 三维线框
solvespace-cli export-surfaces --output out.step input.slvs            # 精确曲面（格式由扩展名决定）
```

关键选项语义（取自 CLI usage 文本）：

- `-o, --output <pattern>`：`%%` 会被替换为输入文件名（不含扩展名），适合批量；不带 `%%` 时多文件会互相覆盖
- `-v, --view <direction>`：`top` / `bottom` / `left` / `right` / `front` / `back` / `isometric`
- `-t, --chord-tol <tolerance>`：导出类命令单位为 mm（默认 1.0），非导出命令为 `%%`（默认 1.0）
- `-b, --bg-color <on|off>`：矢量导出是否带背景色，默认 off

`thumbnail` 不使用图形加速，出图与 GUI 可能有细微差异。常用于 CI 中批量更新参数化模型与生成装配缩略图。

---

## Python 求解器（slvs）

仓库把约束求解内核用 Cython 封装后发布到 PyPI（包名 `slvs`，与 SolveSpace 同版号，当前 3.3；该封装在 `pyproject.toml` 中标注 MIT，主程序仍是 GPL-3.0+）。它只做求解，不含 GUI 与几何建模：

```python
import slvs

slvs.clear_sketch()                 # 每次重新构造前先清空进程内草图
g = 1                               # group 句柄由调用方自定
wp = slvs.add_base_2d(g)            # 基准工作平面
p0 = slvs.add_point_2d(g, 0, 0, wp)
slvs.dragged(g, p0, wp)             # 固定（拖拽锁定）该点
p1 = slvs.add_point_2d(g, 90, 0, wp)
slvs.dragged(g, p1, wp)
line0 = slvs.add_line_2d(g, p0, p1, wp)

p2 = slvs.add_point_2d(g, 20, 20, wp)
p3 = slvs.add_point_2d(g, 0, 10, wp)
slvs.distance(g, p2, p3, 40, wp)    # 点到点距离约束
slvs.angle(g, line0, slvs.add_line_2d(g, p0, p3, wp), 45, wp, False)

res = slvs.solve_sketch(g, False)
assert res['result'] == slvs.ResultFlag.OKAY
print(res['dof'], res['rank'])      # 自由度与约束矩阵秩
x = slvs.get_param_value(p2['param'][0])
y = slvs.get_param_value(p2['param'][1])
```

API 面（见 `python/slvs/solvespace.pyi`）：

- 实体：`add_point_2d/3d`、`add_normal_2d/3d`、`add_distance`、`add_line_2d/3d`、`add_cubic`、`add_arc`、`add_circle`、`add_workplane`、`add_base_2d`
- 约束便捷函数：`coincident`、`distance`、`distance_proj`、`equal`、`equal_angle`、`equal_point_to_line`、`ratio`、`length_diff`、`symmetric`/`symmetric_h`/`symmetric_v`、`midpoint`、`horizontal`、`vertical`、`diameter`、`same_orientation`、`angle`、`parallel`、`perpendicular`、`tangent`、`dragged`；需要冷门类型时用 `add_constraint(g, ConstraintType.XXX, wp, v, …)`
- 求解：`solve_sketch(group, calculateFaileds)` 返回 `{result, dof, rank, bad}`；`ResultFlag` 有 `OKAY` / `INCONSISTENT` / `DIDNT_CONVERGE` / `TOO_MANY_UNKNOWNS` / `REDUNDANT_OKAY`
- 参数读写：实体是 TypedDict，`ent['param'][i]` 是参数句柄，配合 `get_param_value` / `set_param_value` 迭代求解（机构扫描、参数化批量出图）
- 四元数辅助：`make_quaternion`、`quaternion_u/v/n`

典型用法是把 SolveSpace 当"几何约束求解服务"：Python 端生成/驱动约束，结果写回参数或用 `solvespace-cli` 出图。适合 CI 中的参数化校核，不需要打开 GUI。

---

## 修改参数

- 双击约束的数值文字 → 输入新值 → Enter
- 右键参数的 Property Browser 条目可 `Edit Param Value` 直接改数值
- 改完不刷新时按 `Space`（Regenerate All）
- `Ctrl+Shift+F` 高亮所有欠约束点，`Ctrl+Shift+D` 做步进尺寸（Step Dimension）

---

## 简单仿真 / 动画

- Group → Step Translating / Step Rotating（多次平移/旋转）即可逐级摊开运动
- `Ctrl+Shift+T` Trace Point 跟踪点轨迹，`Ctrl+Shift+S` 停止跟踪
- 机构动画：把驱动尺寸做成参数，配合 `slvs` 或 Step Dimension 逐帧求解，再用 Export Image + 外部工具合成 GIF

---

## 典型工作流

### 工作流一：3D 打印零件快速建模

1. 新建文件（.slvs），确认活动工作平面为 XY，按 `s` 画直线、`c` 画圆、`a` 画弧，勾出闭合轮廓
2. `Ctrl+E` 沿切线连续选中整条轮廓，用 `h`/`v` 水平垂直、`d` 距离、`q` 等长、`l` 相切把草图变全黑（完全约束）
3. `Shift+X` 拉伸为 3D 实体；需要减材时把该 Group 的类型改为 Request 或在新 Group 里用布尔 Subtract
4. `Shift+W` 在新面上建工作平面继续草图，重复约束 → 拉伸
5. `Ctrl+Shift+N` 确认没有裸边（实体闭合），`Ctrl+Shift+I` 检查自干涉
6. File → Export Triangle Mesh → `.stl`，交给切片软件

### 工作流二：简单机构装配与验证

1. 各零件单独存为 .slvs 文件（每个零件自身的装配约束放在自己的文件里）
2. 新建主文件，`Shift+I`（Group → New Group → Link / Assemble…）一次性链接多个零件
3. 用 3D 草图与约束（`d` 距离、`o` 点在线上、`l` 平行、点重合）固定相对位置，留出一个自由度
4. 拖动驱动零件，从动件由求解器带动；`Space` 强制重算
5. `Ctrl+Shift+T` 跟踪关键点轨迹验证行程，`Ctrl+Shift+S` 停止
6. 需要批量扫参时改用 `slvs` Python 包，把驱动尺寸写成循环求解

### 工作流三：CI 中批量出图

1. 参数化模型与生成脚本一起入库，模型只存 .slvs
2. `solvespace-cli regenerate '%%.slvs'` 重求解并回写
3. `solvespace-cli export-view --output '%%-top.svg' --view top '%%.slvs'` 出二维图
4. `solvespace-cli thumbnail --output '%%-2d.png' --view isometric --size 1024 '%%.slvs'` 出文档缩略图

---

## 性能与精度

1. 求解器是稠密牛顿法，规模上限在数千实体；大型装配、复杂曲面应换 FreeCAD/OCCT
2. 导入格式限于 .slvs、DXF、IDF（ECAD 板框）与三角网格；**STEP 只能导出、不能导入**
3. 大尺寸值（毫米级长跨度）早期版本容易不收敛，3.3 明确改善了大数值约束与部分原本失败的约束求解
4. 网格密度用 `Edit → Configuration…` 的 chord tolerance 控制，越小越精细也越慢
5. `thumbnail` 与矢量导出走软件渲染，与 GUI 观感可能有细微差异

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 草图线条变红 | 过约束：删除冗余约束；若曾在 3.2 遇到过"求解不出的约束被直接删掉"，那是 3.2 的回归，3.3 起不再删除，用 3.3+ 或手工加回 |
| 草图线条蓝色 | 欠约束：补距离/角度/水平垂直；`Ctrl+Shift+F` 高亮所有欠约束点 |
| 改完约束值不刷新 | 按 `Space`（Regenerate All）；仍不对就 `Ctrl+Shift+D` 逐步维度检查 |
| 导出 STL 残缺 | 实体未闭合，`Ctrl+Shift+N` 查裸边，确认拉伸 Group 生成的是 Solid 而非 Shell |
| 升级到 3.3 后曲面显示变干净但旧文件几何有细微变化 | 3.3 是 NURBS 几何内核修复，平面/边、曲面与相切处都有改动，导出前用 `Ctrl+Shift+N` 与体积/面积核对关键尺寸 |
| 大尺寸模型（米级跨度）求解不收敛 | 3.3 改善了大数值约束的求解；仍在旧版时先升级，或把单位改为 mm 并统一量级 |
| 圆弧标注变成了直径 | 3.2 起圆/弧尺寸默认**半径**，在 Property Browser 取消 `use radius` 可切回直径 |
| 拉伸的图片/文字出现在 3D 里 | 3.2 起 Image 元素默认不复制到 3D Group，需要时对该 Image 执行 Toggle Construction |
| 中文乱码 | 内置矢量字体不含 CJK；TrueType 文字需系统字体，或导出 SVG 后用其它工具补文字 |
| 装配运动不顺 | 缺少同轴/距离约束导致多余自由度，逐个 `d`/`o`/`l` 补齐 |

---

## 适用 / 不适用场景

- 适用：3D 打印件、机构原理验证、图纸剖切与二维出图、教学、参数化小工具、CI 里的几何约束校核
- 不适用：复杂工业机械、汽车曲面、大型装配、需要 STEP 再导入的工作流（改用 FreeCAD / OCCT）

---

## AI 使用建议

- **推荐工作流模式**：按 SolveSpace 的自然约束流程引导——选工作平面 → 绘草图（`s`/`c`/`a`/`b`）→ 加约束（`d`/`n`/`h`/`v`/`q`/`l`/`y`）→ `Shift+X` 拉伸或 `Shift+L` 旋转 → 导出。约束状态用颜色判断：黑=完全约束、红=过约束（删冗余）、蓝=欠约束（补约束），可用 `Ctrl+Shift+F` 定位蓝点。
- **关键注意事项**：① 单键快捷键无需修饰键，但会全局拦截，画图中按 `Esc` 是**删除**该实体而非取消；② STEP 为只出不进，跨软件往返请用 DXF/网格或 FreeCAD；③ 从 3.2 升级时注意：3.2 有"无法求解的约束被删除"的回归，3.3 已修复，重要模型升级前先备份 .slvs；④ 圆/弧尺寸默认半径；⑤ 批量任务优先 `solvespace-cli` 或 `slvs`，不要试图脚本驱动 GUI。
- **常用代码模式**：GUI：`s` 画线 → 选实体 → `d` 距离、`n` 角度、`q` 等长 → `Shift+X` 拉伸 → Export Triangle Mesh。CLI：`solvespace-cli regenerate input.slvs`、`solvespace-cli export-mesh --output out.stl input.slvs`。Python：`slvs.add_base_2d(g)` → `slvs.add_point_2d` / `add_line_2d` → `slvs.distance/angle/parallel` → `slvs.solve_sketch(g, False)` → `slvs.get_param_value(ent['param'][i])`。
- **不要臆造**：SolveSpace 没有 Sweep/放样 Group（只有 Extrude、Lathe、Revolve、Helix、Step Translating/Rotating），没有 IGES 导出，也没有参数表达式表或外部变量文件。


---

## 相关技能

- **freecad** — 桌面参数化 CAD（更复杂的工业建模）：[../freecad/SKILL.md](../freecad/SKILL.md)
- **openscad** — 声明式 CSG 脚本建模：[../openscad/SKILL.md](../openscad/SKILL.md)
- **cadquery** — Python BREP 建模库：[../cadquery/SKILL.md](../cadquery/SKILL.md)
- **occt** — OCCT 几何内核（SolveSpace 的几何引擎可互补使用）：[../occt/SKILL.md](../occt/SKILL.md)

---

## 参考资源

- 参考手册：<https://solvespace.com/ref.pl>
- 官方教程：<https://solvespace.com/tutorial.pl>
- 论坛 / IRC：<https://solvespace.com/forum.pl>，#solvespace @ libera.chat
- Releases：<https://github.com/solvespace/solvespace/releases>
- 求解器 Python 包：<https://pypi.org/project/slvs/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/solvespace/>
