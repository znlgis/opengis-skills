---
name: solvespace
description: SolveSpace 是一款轻量、开源的参数化 2D/3D CAD，专注约束求解器驱动的草图与简单装配，原生跨平台（Windows/macOS/Linux），文件体积小、启动快，适合快速参数化建模、3D 打印零件与教学。
---

> **项目地址：** <https://github.com/solvespace/solvespace>
>
> **官网：** <https://solvespace.com/>
>
> **文档：** <https://solvespace.com/help.pl>
>
> **许可证：** GPL-3.0+

## 概述

SolveSpace 特性：

- **基于约束求解**：草图通过几何约束（距离、平行、相切、对称…）自动求解
- **参数化 3D**：草图 → 拉伸/旋转/扫掠/放样
- **装配**：导入零件文件（.slvs）+ 约束装配
- **力学仿真**：简单干涉检查、机构动画
- **导出**：DXF、SVG、PDF、STL、STEP（3D）、IGES、Gerber
- **占用极小**：单可执行 ~5MB，启动 < 1s

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

## 工作流

```
新建文件 (.slvs)
  │
  ├── 1. 在工作平面（Workplane: XY/YZ/XZ）上画 2D 草图
  │       ├─ 直线 (S, L) / 圆 (S, C) / 弧 / 矩形 / 样条
  │       └─ 添加约束：距离 (D) / 角度 (A) / 平行 / 对称 / 等长 / 重合
  │
  ├── 2. 求解（自动）：黑色 = 完全约束；红色 = 过约束；蓝色 = 欠约束
  │
  ├── 3. 拉伸/旋转/扫掠/放样
  │       ├─ Sketch → Extrude (Group → New Group, Step Translating)
  │       └─ Sketch → Lathe (旋转)
  │
  ├── 4. 在新平面上继续草图（Sketch in 3d / Sketch in New Workplane）
  │
  └── 5. 导出（File → Export → STL/STEP/DXF/...）
```

---

## 关键快捷键

| 键 | 功能 |
|----|------|
| `S` 系列 | Sketch（S→L/C/R/...） |
| `D` | Distance 约束 |
| `A` | Angle 约束 |
| `P` | Parallel |
| `E` | Equal |
| `H` | Horizontal |
| `V` | Vertical |
| `Ctrl+1..9` | 视图切换 |
| `Tab` | 切换可见 Group |

---

## Group（组）= 特征树

每个 Group 代表一个建模步骤（草图 / 拉伸 / 旋转 / 装配 / 步骤平移）：

- New Group → Step and Repeat Translating（线性阵列）
- New Group → Step and Repeat Rotating（旋转阵列）
- New Group → Extrude（拉伸）
- New Group → Lathe（旋转体）
- New Group → Sweep
- New Group → Helical Sweep（螺旋扫掠）
- New Group → Linked / Imported（导入文件作为零件）

---

## 装配

1. 创建主装配文件（.slvs）
2. New Group → Linked / Imported file → 选择子零件 .slvs
3. 用 3D 草图约束（距离、同轴、平行、点重合）固定零件位置
4. 移动其中一个零件，约束驱动其它零件随动

---

## 导出 STEP（重要）

```
File → Export 3D Model → choose .step
```

注意：

- 必须有「Active workplane = none」（可见 3D 实体）
- 输出包含完整 BREP，可被 FreeCAD/CAD 打开

---

## 命令行 / 批处理

`solvespace-cli`（如果发行版自带）：

```bash
solvespace-cli regenerate input.slvs            # 重新求解
solvespace-cli thumbnail   --view top  out.png input.slvs
solvespace-cli export-mesh out.stl  input.slvs  # 输出 STL
solvespace-cli export-view out.svg  input.slvs --view top
```

主要用于 CI 中批量更新参数化模型。

---

## 修改参数

- 双击约束值（D/A）→ 输入新值 → Enter
- 选 Edit Param Value 设置变量
- `View → Show Parameters` 列出所有数值

---

## 简单仿真 / 动画

- New Group → Step and Repeat（多次平移/旋转）即可手动播放运动
- `Analyze → Trace Point` 跟踪点轨迹
- 动画 GIF 通过外部工具结合 Export Image 实现

---

## 性能与精度

1. 单文件几何复杂度有限（几千实体），大型装配不适用
2. STEP 导入支持有限，复杂几何建议 FreeCAD/OCCT
3. 求解失败：减少约束、检查冗余、按 F5 强制重算
4. STL 三角面用 `Configuration → Chord Tolerance` 调整密度

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 草图变红 | 过约束：删除冗余约束 |
| 草图蓝色 | 欠约束：添加距离/角度等 |
| 导出 STL 残缺 | 实体未闭合，检查每个 Group 的 Solid |
| 中文乱码 | 文字使用 SolveSpace 内置矢量字体（受限）；建议导出 SVG 后用其它工具加文字 |
| 装配运动不顺 | 添加旋转/距离约束以驱动 |

---

## 适用 / 不适用场景

✅ 适用：3D 打印件、机构原理验证、教学、参数化小工具
❌ 不适用：复杂工业机械、汽车曲面、大型装配、PCB（用 KiCad）

---

## 参考资源

- 帮助：<https://solvespace.com/help.pl>
- 教程：<https://github.com/solvespace/solvespace/wiki>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/solvespace/>
