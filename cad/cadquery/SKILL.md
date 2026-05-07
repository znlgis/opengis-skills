---
name: cadquery
description: CadQuery 是基于 Python 的开源参数化 CAD 库，构建于 OCCT 几何内核之上，提供流畅的 fluent API 来描述工业级 BREP 模型，支持装配、CAM、STEP/IGES/STL/glTF 输出，特别适合可编程设计、批量参数化、CI 流水线与教育。
tags: [python, 3d, parametric, brep, step, stl, occ, cad]
---

> **项目地址：** <https://github.com/CadQuery/cadquery>
>
> **官方文档：** <https://cadquery.readthedocs.io/en/latest/>
>
> **GUI：** CQ-editor（<https://github.com/CadQuery/CQ-editor>）
>
> **许可证：** Apache-2.0

## 概述

CadQuery 与 OpenSCAD 的对比：

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
# Conda（推荐，自动带 OCCT）
conda install -c conda-forge cadquery
# pip
pip install cadquery
# 安装 GUI
pip install cq-editor
```

> Python 3.10/3.11 推荐。`cadquery-ocp` 提供新版本 OCCT 绑定。

---

## Hello CadQuery

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

## 工作平面（Workplane）

```python
wp = cq.Workplane("XY")               # XY/YZ/XZ 或自定义
wp = (cq.Workplane("front")           # 命名平面
        .center(10, 0)                # 偏移工作平面原点
        .rotateAboutCenter((0,0,1), 30))
```

---

## 二维草图与拉伸

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

## Selector（核心特性）

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

## 修饰特征

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

## 布尔运算

```python
a = cq.Workplane("XY").box(20, 20, 10)
b = cq.Workplane("XY").translate((10, 0, 5)).cylinder(20, 5)

c = a.union(b)
c = a.cut(b)
c = a.intersect(b)
```

---

## Sketch（新草图 API）

```python
sk = (cq.Sketch()
        .rect(60, 40)
        .circle(10, mode='s')             # 减
        .reset().rect(50, 30, mode='i')   # 交
        .reset().vertices().fillet(3))

result = cq.Workplane().placeSketch(sk).extrude(10)
```

---

## 装配（Assembly）

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

## 参数化设计与脚本

```python
def make_box(L, W, H, hole_d=8):
    return (cq.Workplane('XY').box(L, W, H)
              .faces('>Z').workplane().hole(hole_d))

for L in (40, 60, 80):
    cq.exporters.export(make_box(L, 30, 10), f'box_{L}.step')
```

---

## CQ-editor / Jupyter

```python
# 在 cq-editor 中：
show_object(result, name='part', options={'color': (0.7, 0.7, 0.9)})

# 在 Jupyter：
from jupyter_cadquery import show
show(result)
```

---

## 导出

```python
cq.exporters.export(result, "out.step")   # STEP
cq.exporters.export(result, "out.brep")
cq.exporters.export(result, "out.stl",  tolerance=0.01)
cq.exporters.export(result, "out.dxf")
cq.exporters.export(result, "out.svg")
```

---

## 典型工作流

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
| OCCT 异常 | 检查输入几何是否合法；调用 `.clean()` |
| Selector 选不到 | 使用 `result.faces().vals()` 调试 |
| 圆角失败 | 减小半径或拆分到边集合后逐一加 |
| Conda 安装慢 | 使用 mamba |
| `cq.Assembly` 求解失败 | 减少冲突约束、给定初始 `Location` |

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
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/cadquery/>
