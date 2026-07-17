---
name: solvespace
description: "Use when doing lightweight parametric 2D/3D CAD with constraint-based sketching �?linkages, section analysis, STL export for 3D printing. SolveSpace: ultra-light parametric constraint solver CAD with real-time solving."
tags: [3d, 2d, parametric, cad, constraint-solver, step, dxf]
---

> **项目地址�?* <https://github.com/solvespace/solvespace>
>
> **官网�?* <https://solvespace.com/>
>
> **文档�?* <https://solvespace.com/help.pl>
>
> **许可证：** GPL-3.0+

## 概述

SolveSpace 特性：

- **基于约束求解**：草图通过几何约束（距离、平行、相切、对称…）自动求解
- **参数�?3D**：草�?�?拉伸/旋转/扫掠/放样
- **装配**：导入零件文件（.slvs�? 约束装配
- **力学仿真**：简单干涉检查、机构动�?
- **导出**：DXF、SVG、PDF、STL、STEP�?D）、IGES、Gerber
- **占用极小**：单可执�?~5MB，启�?< 1s

---

## 安装

```bash
# Linux
sudo apt install solvespace

# macOS
brew install --cask solvespace

# Windows: 官网下载
```

---

## 工作�?

```
新建文件 (.slvs)
  �?
  ├── 1. 在工作平面（Workplane: XY/YZ/XZ）上�?2D 草图
  �?      ├─ 直线 (S, L) / �?(S, C) / �?/ 矩形 / 样条
  �?      └─ 添加约束：距�?(D) / 角度 (A) / 平行 / 对称 / 等长 / 重合
  �?
  ├── 2. 求解（自动）：黑�?= 完全约束；红�?= 过约束；蓝色 = 欠约�?
  �?
  ├── 3. 拉伸/旋转/扫掠/放样
  �?      ├─ Sketch �?Extrude (Group �?New Group, Step Translating)
  �?      └─ Sketch �?Lathe (旋转)
  �?
  ├── 4. 在新平面上继续草图（Sketch in 3d / Sketch in New Workplane�?
  �?
  └── 5. 导出（File �?Export �?STL/STEP/DXF/...�?
```

---

## 关键快捷�?

| �?| 功能 |
|----|------|
| `S` 系列 | Sketch（S→L/C/R/...�?|
| `D` | Distance 约束 |
| `A` | Angle 约束 |
| `P` | Parallel |
| `E` | Equal |
| `H` | Horizontal |
| `V` | Vertical |
| `Ctrl+1..9` | 视图切换 |
| `Tab` | 切换可见 Group |

---

## Group（组�? 特征�?

每个 Group 代表一个建模步骤（草图 / 拉伸 / 旋转 / 装配 / 步骤平移）：

- New Group �?Step and Repeat Translating（线性阵列）
- New Group �?Step and Repeat Rotating（旋转阵列）
- New Group �?Extrude（拉伸）
- New Group �?Lathe（旋转体�?
- New Group �?Sweep
- New Group �?Helical Sweep（螺旋扫掠）
- New Group �?Linked / Imported（导入文件作为零件）

---

## 装配

1. 创建主装配文件（.slvs�?
2. New Group �?Linked / Imported file �?选择子零�?.slvs
3. �?3D 草图约束（距离、同轴、平行、点重合）固定零件位�?
4. 移动其中一个零件，约束驱动其它零件随动

---

## 导出 STEP（重要）

```
File �?Export 3D Model �?choose .step
```

注意�?

- 必须有「Active workplane = none」（可见 3D 实体�?
- 输出包含完整 BREP，可�?FreeCAD/CAD 打开

---

## 命令�?/ 批处�?

`solvespace-cli`（如果发行版自带）：

```bash
solvespace-cli regenerate input.slvs            # 重新求解
solvespace-cli thumbnail   --view top  out.png input.slvs
solvespace-cli export-mesh out.stl  input.slvs  # 输出 STL
solvespace-cli export-view out.svg  input.slvs --view top
```

主要用于 CI 中批量更新参数化模型�?

---

## 修改参数

- 双击约束值（D/A）→ 输入新�?�?Enter
- �?Edit Param Value 设置变量
- `View �?Show Parameters` 列出所有数�?

---

## 简单仿�?/ 动画

- New Group �?Step and Repeat（多次平�?旋转）即可手动播放运�?
- `Analyze �?Trace Point` 跟踪点轨�?
- 动画 GIF 通过外部工具结合 Export Image 实现

---

## 性能与精�?

1. 单文件几何复杂度有限（几千实体），大型装配不适用
2. STEP 导入支持有限，复杂几何建�?FreeCAD/OCCT
3. 求解失败：减少约束、检查冗余、按 F5 强制重算
4. STL 三角面用 `Configuration �?Chord Tolerance` 调整密度

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 草图变红 | 过约束：删除冗余约束 |
| 草图蓝色 | 欠约束：添加距离/角度�?|
| 导出 STL 残缺 | 实体未闭合，检查每�?Group �?Solid |
| 中文乱码 | 文字使用 SolveSpace 内置矢量字体（受限）；建议导�?SVG 后用其它工具加文�?|
| 装配运动不顺 | 添加旋转/距离约束以驱�?|

---

## 适用 / 不适用场景

�?适用�?D 打印件、机构原理验证、教学、参数化小工�?
�?不适用：复杂工业机械、汽车曲面、大型装配、PCB（用 KiCad�?

---

## AI 使用建议

- **推荐工作流模�?*：AI 助手应引导用户按 SolveSpace 的自然约束流程建模——在 Workplane 上绘草图 �?添加几何约束（距�?角度/平行/等长）→ 拉伸/旋转生成 3D。约束状态用颜色判断：黑�?完全约束，红�?过约束（删除冗余），蓝色=欠约束（继续添加）。CLI 批处理使�?`solvespace-cli`�?
- **关键注意事项**：① 草图变红表示过约束，需删除冗余约束；② 草图蓝色表示欠约束，需添加距离/角度等；�?导出 STEP 前确�?Active workplane = none�?D 实体可见）；�?复杂工业模型不适用 SolveSpace（几千实体为上限），建议�?FreeCAD�?
- **常用代码模式**：GUI：S→L 画线，D 添加距离约束，A 添加角度约束 �?New Group �?Extrude 拉伸。CLI：`solvespace-cli regenerate input.slvs` / `solvespace-cli export-mesh out.stl input.slvs`�?

---

## 相关技�?

- **freecad** �?桌面参数�?CAD（更复杂的工业建模）：[../freecad/SKILL.md](../freecad/SKILL.md)
- **openscad** �?声明�?CSG 脚本建模：[../openscad/SKILL.md](../openscad/SKILL.md)
- **cadquery** �?Python BREP 建模库：[../cadquery/SKILL.md](../cadquery/SKILL.md)
- **occt** �?OCCT 几何内核（SolveSpace 的几何引擎可互补使用）：[../occt/SKILL.md](../occt/SKILL.md)

---

## 典型工作�?

### 工作流一�?D 打印零件快速建�?

1. 新建文件�?slvs），�?XY Workplane 上用 S→L 画轮廓线
2. D 键添加距离约束，A 键添加角度约束，P 键添加平行约束，直到草图全黑（完全约束）
3. New Group �?Extrude 拉伸�?3D 实体
4. 在新面上继续草图（Sketch in New Workplane），绘制减材特征
5. 通过布尔差集（Subtract）去除材�?
6. 导出�?STL，用�?3D 打印切片软件

### 工作流二：简单机构装配与验证

1. 创建各零件独�?.slvs 文件
2. 创建主装配文件，New Group �?Linked/Imported file 导入各零�?
3. 使用 3D 草图约束（距离、同轴、点重合）固定零件相对位�?
4. 移动驱动零件，观察约束驱动的从动件运�?
5. Analyze �?Trace Point 跟踪关键点轨迹，验证机构运动范围

---

## 参考资�?

- 帮助�?https://solvespace.com/help.pl>
- 教程�?https://github.com/solvespace/solvespace/wiki>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/solvespace/>