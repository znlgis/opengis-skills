---
name: cadquery
description: "Use when scripting parametric 3D CAD parts in Python with CadQuery — Workplane fluent API, Selector expressions like \">Z\" and \"|Z\", extrude/loft/sweep, fillet and shell, Sketch API, Assembly constraints, STEP/STL/glTF export. Covers conda-forge vs pip install of cadquery 2.8.0 with cadquery-ocp; also for selectors matching nothing, fillet failing on edge sets, and OCCT failures from degenerate geometry."
tags:
  - python
  - 3d
  - parametric
  - brep
  - step
  - stl
  - occt
  - cad
---

> **项目地址：** <https://github.com/CadQuery/cadquery>
>
> **官方文档：** <https://cadquery.readthedocs.io/en/latest/>
>
> **GUI：** CQ-editor（<https://github.com/CadQuery/CQ-editor>）
>
> **包管理器：** `cadquery`（最新 2.8.0，截至 2026-10；PyPI 与 conda-forge 同步，要求 Python ≥ 3.11，几何依赖 `cadquery-ocp` 7.9.x）
>
> **许可证：** Apache-2.0

## 概述

CadQuery 是用 Python 描述参数化零件的脚本化 CAD 库，几何内核为 OCCT（通过 `cadquery-ocp` 绑定），模型是带面/边/顶点可选择寻址的 BREP 实体，而不是 CSG 网格。API 以 `Workplane` 的链式调用为主，配合 Selector 表达式定位几何、`Assembly` 组织装配，最终导出 STEP/STL 等交换格式。与 OpenSCAD 的定位差异：

| 维度 | OpenSCAD | CadQuery |
|------|----------|----------|
| 语言 | 自有 DSL | Python |
| 几何内核 | CGAL/Manifold | OCCT |
| 模型 | CSG（实体加减） | BREP（带圆角/曲面/约束） |
| 装配 | 手动 | 内置 `Assembly` |
| 特征命名 | 弱 | 通过 Selector 访问面/边/顶点 |
| 输出 | STL/OFF/DXF | STEP/IGES/STL/glTF/DXF/SVG |

---

## 安装

```bash
# Conda / mamba（推荐，自动带 cadquery-ocp 与 OCCT）
conda install -c conda-forge cadquery

# pip（需自备可用的 cadquery-ocp wheel，Python ≥ 3.11）
pip install cadquery

# 可选 GUI
pip install cq-editor
```

验证安装（能打印版本且能建体即为就绪）：

```bash
python -c "import cadquery as cq; print(cq.__version__)"
python -c "import cadquery as cq; print(cq.Workplane(\"XY\").box(1,1,1).val().Volume())"
```

> 当前稳定版 **2.8.0**（PyPI 上传 2026-06-21；tag `v2.8.0` 见 [CadQuery GitHub Releases](https://github.com/CadQuery/cadquery/releases)）。PyPI 包要求 **Python ≥ 3.11**，几何依赖 `cadquery-ocp`（2.8.0 锁 `>=7.9.3.1,<8.0`，即 OCCT 7.9.x）；conda-forge 通道同步发布。

---

## 核心 API

### Hello CadQuery

```python
import cadquery as cq

result = (
    cq.Workplane("XY")
      .box(80, 60, 10)            # 立方体
      .faces(">Z").workplane()     # 选择 +Z 面，建立工作平面
      .hole(8)                    # 钻孔
      .edges("|Z").fillet(2)      # Z 方向边圆角 2
)

cq.exporters.export(result, "out.step")
cq.exporters.export(result, "out.stl")
```

---

### 工作平面（Workplane）

```python
wp = cq.Workplane("XY")               # XY/YZ/XZ 或自定义
wp = (cq.Workplane("front")           # 命名平面
        .center(10, 0)                # 偏移工作平面原点
        .rotateAboutCenter((0,0,1), 30))
```

---

### 二维草图与拉伸

```python
result = (cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(50, 0)
            .lineTo(50, 30).lineTo(0, 30).close()
            .extrude(20))

# 圆形 → 拉伸为圆柱
cyl = cq.Workplane("XY").circle(10).extrude(50)

# 矩形阵列
plate = (cq.Workplane("XY").rect(100, 60).extrude(2)
          .faces(">Z").workplane()
          .rarray(10, 10, 8, 5).hole(3))   # 8x5 阵列孔
```

---

### Selector（核心特性）

```python
result = result.faces(">Z")        # 最大 Z 的面
              .edges("|X")         # 平行 X 方向的边
              .vertices("<Y")       # 最小 Y 的顶点
              .faces("not >Z and %CIRCLE")  # 复合
```

| 表达式 | 含义 |
|--------|------|
| `>Z` / `<Z` | 最大/最小 Z 方向 |
| `|X` | 平行 X 轴 |
| `#X` | 垂直 X 轴 |
| `%CIRCLE` | 圆形（曲率） |
| `%PLANE` | 平面 |
| `>>X` | 严格按 X 排序 |

---

### 修饰特征

```python
res = (cq.Workplane("XY").box(50, 30, 10)
        .edges("|Z").fillet(2)             # 圆角
        .edges(">Z").chamfer(0.5)          # 倒角
        .faces(">Z").shell(-1.5))          # 抽壳，开口面

# 镜像 / 阵列 / 扫掠 / 放样
res = res.mirror("XY")
loft = (cq.Workplane("XY").circle(10).workplane(offset=10)
          .rect(15, 15).loft())

path = cq.Workplane("XZ").moveTo(0,0).lineTo(0,20).lineTo(20,20)
swept = cq.Workplane("XY").circle(2).sweep(path)
```

---

### 布尔运算

```python
a = cq.Workplane("XY").box(20, 20, 10)
b = cq.Workplane("XY").translate((10, 0, 5)).cylinder(20, 5)

c = a.union(b)
c = a.cut(b)
c = a.intersect(b)
```

---

### Sketch（新草图 API）

```python
sk = (cq.Sketch()
        .rect(60, 40)
        .circle(10, mode='s')             # 减
        .reset().rect(50, 30, mode='i')   # 交
        .reset().vertices().fillet(3))

result = cq.Workplane().placeSketch(sk).extrude(10)
```

---

### 装配（Assembly）

```python
asm = (cq.Assembly()
        .add(plate, name='base', color=cq.Color('gray'))
        .add(screw, name='screw1', loc=cq.Location((10, 10, 2))))

asm.constrain('base@faces@>Z', 'screw1@faces@<Z', 'Plane')
asm.solve()
asm.save('out.step')
asm.save('out.glb', 'GLTF')
```

---

### 参数化设计与脚本

```python
def make_box(L, W, H, hole_d=8):
    return (cq.Workplane('XY').box(L, W, H)
              .faces('>Z').workplane().hole(hole_d))

for L in (40, 60, 80):
    cq.exporters.export(make_box(L, 30, 10), f'box_{L}.step')
```

---

### CQ-editor / Jupyter

```python
# 在 cq-editor 中：
show_object(result, name='part', options={'color': (0.7, 0.7, 0.9)})

# 在 Jupyter：
from jupyter_cadquery import show
show(result)
```

---

### 导出

```python
cq.exporters.export(result, "out.step")   # STEP
cq.exporters.export(result, "out.brep")
cq.exporters.export(result, "out.stl",  tolerance=0.01)
cq.exporters.export(result, "out.dxf")
cq.exporters.export(result, "out.svg")
```

---

## 典型工作流

**输入**：一组尺寸参数（或参数矩阵 + 模板脚本）；**输出**：STEP/STL 等几何文件。

### 工作流一：从草图到 STEP 的完整零件建模

1. 确定零件几何参数（长宽高、孔径、圆角半径等），封装为 Python 函数参数
2. 使用 `cq.Workplane("XY")` 创建基准面
3. 绘制 2D 草图轮廓（`rect`/`circle`/`polyline` 等）
4. `extrude(length)` 生成 3D 实体
5. 通过 Selector（`.faces(">Z")` / `.edges("|Z")`）定位特征面/边
6. 添加修饰：`fillet()` / `chamfer()` / `shell()`
7. `cq.exporters.export(result, "out.step")` 导出 STEP 用于下游加工

### 工作流二：CI 流水线批量参数化生成

1. 编写参数化模型函数（接受尺寸参数，返回 Workplane 对象）
2. 在 GitHub Actions / Jenkins 中安装 `cadquery`（conda-forge）
3. 脚本遍历参数矩阵，调用模型函数，导出 STL/STEP
4. 将输出文件上传为构建产物（Artifacts），或直接在 CI 中对比几何差异
5. 对于复杂装配，使用 `cq.Assembly` 组合多个零件并添加约束

---

## 性能优化

1. 使用 **Sketch API** 比逐边 lineTo 更高效
2. 大量阵列用 `rarray/cboreHole` 等专用方法
3. 复杂模型缓存中间 `Workplane` 实例
4. 导出 STL 调整 `tolerance` / `angularTolerance`
5. CI 中无显示运行用 `headless` Python，避免 cq-editor

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `ImportError: cannot import name 'OCP'` / `cadquery-ocp` 装不上 | pip 下没有对应平台的 `cadquery-ocp` wheel：改用 `conda install -c conda-forge cadquery`（conda-forge 同步发布），并确认 Python ≥ 3.11 |
| Selector 选不到（`.faces(">Z")` 结果为空） | 先用 `result.faces().vals()` 或 `result.edges().vals()` 列出全部候选，核对方向/类型过滤条件后再加修饰；复合表达式在 `Val()` 上逐段验证 |
| 圆角/倒角抛 `OCCT` 异常 | 半径超过相邻边长、或边集合不连续都会失败；减小半径或拆成单条边逐一 `fillet`/`chamfer` |
| 布尔运算后几何异常/体积为 0 | 运算前确认两个实体都是闭合 Solid（`shape.isValid()`），退化几何先 `.clean()` |
| `cq.Assembly` 求解失败或不收敛 | 约束过多/冲突：减少约束、给定初始 `Location`，用 `asm.solve()` 的返回状态判断是否收敛 |
| 导出 STEP 体积巨大或丢失颜色 | STEP 以 BREP 精确保存，体积随面数增长；颜色需在 `Assembly.add(..., color=...)` 上给，`exporters.export` 对单实体不写颜色 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应将几何逻辑封装为可复用的 Python 函数，利用 CadQuery 的 fluent API 链式描述几何操作序列——遵循「基准面 → 2D 草图 → 拉伸/扫掠 → Selector 定位 → 修饰 → 导出」的模式。
- **关键注意事项**：① Selector 表达式需要调试，`result.faces().vals()` 可列出所有面供排查；② 圆角/倒角失败通常意味着半径过大或边不连续，可逐一添加而非批量；③ 布尔运算前确保实体无退化几何；④ Assembly 求解是数值优化，减少约束数量可提高成功率。
- **常用代码模式**：`cq.Workplane("XY").rect(...).extrude(...).faces(">Z").workplane().hole(...)` 是最经典的模式；多零件建模用 `cq.Assembly().add(...).constrain(...).solve()` 装配。

---

## 相关技能

- **occt** — 底层 OCCT 几何内核 API（C++/PythonOCC）：[../occt/SKILL.md](../occt/SKILL.md)
- **freecad** — 桌面参数化 CAD，含 Sketcher/PartDesign/BIM：[../freecad/SKILL.md](../freecad/SKILL.md)
- **openscad** — 声明式脚本建模（CSG 风格），适合对比选型：[../openscad/SKILL.md](../openscad/SKILL.md)
- **solvespace** — 轻量约束求解器建模，适合快速概念设计：[../solvespace/SKILL.md](../solvespace/SKILL.md)

---

## 参考资源

- 文档：<https://cadquery.readthedocs.io/>
- 示例：<https://github.com/CadQuery/cadquery/tree/master/examples>
- CQ-editor：<https://github.com/CadQuery/CQ-editor>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/cadquery/>
