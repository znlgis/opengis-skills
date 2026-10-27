---
name: openscad
description: "Use when generating 3D models from code with OpenSCAD — CSG scripts for parametric parts, 3D-printable fixtures, or CI batch export; also when renders are painfully slow and you need --backend Manifold, an exported STL is not manifold / slice software rejects it, or import() of an STL or SVG is the bottleneck. Covers cube/sphere/cylinder, difference/union/intersection, linear_extrude/rotate_extrude, hull/minkowski, Customizer annotations, and openscad -o out.stl -D var=value automation."
tags:
  - 3d
  - parametric
  - csg
  - scripting
  - stl
  - openscad
  - cli
---

> **项目地址：** <https://github.com/openscad/openscad>
>
> **官网：** <https://openscad.org/>
>
> **官方文档：** <https://openscad.org/documentation.html>
>
> **Cheatsheet：** <https://openscad.org/cheatsheet/>
>
> **许可证：** GPL-2.0+
>
> **最新稳定版：** 2021.01（GitHub 最后一个正式 Release，截至 2026-10 未变）。日常实操普遍用**快照/测试版**：仓库最新标签为 `openscad-2026.10-TEST4`（2026-10-15），官网 Snapshots 提供各平台每日构建；Manifold 后端与新增函数（如 `offset` 的 3D 模式、`polyline()` 等）只在快照里可用，见 [tags](https://github.com/openscad/openscad/tags) 与 [downloads](https://openscad.org/downloads.html)

## 概述

OpenSCAD 与传统 GUI CAD 的区别：

- **代码即模型**：所有几何由 .scad 脚本生成
- **CSG 内核**：基于 CGAL（精确）或新版 Manifold（更快）
- **三大基础**：原语 + 变换 + 布尔
- **强参数化**：变量、模块、函数、循环、列表推导
- **导入导出**：STL、OFF、DXF、SVG、AMF、3MF；可导入 STL 做处理
- **批处理**：CLI `openscad -o out.stl model.scad`

---

## 安装

```bash
# Linux
sudo apt install openscad
# macOS（Homebrew 只有 cask）
brew install --cask openscad
# Windows: 官方安装包 / 便携版
# 开发版（含 Manifold 后端）：<https://openscad.org/downloads.html#snapshots>
```

验证安装与版本：

```bash
openscad --version          # 打印版本
openscad --info             # 打印构建信息（编译器、依赖库、Manifold 是否编入）
openscad --help             # 列出当前构建支持的全部开关
```

> 各发行版仓库里的 openscad 常年停在 2021.01，没有 Manifold 后端与新版函数。需要这些特性时装官网 Snapshots 构建。

---

## 基础语法

```scad
// 变量
length = 50;
width  = 30;
height = 10;

// 立方体
cube([length, width, height], center = false);

// 球
sphere(r = 5, $fn = 64);          // $fn 控制圆滑度

// 圆柱
cylinder(h = 20, r1 = 5, r2 = 10, center = true, $fn = 32);

// 文字
text("Hello", size = 8, font = "DejaVu Sans:style=Bold");
```

---

## 变换

```scad
translate([10, 0, 0])  cube(5);
rotate([0, 0, 45])     cube(5);
scale([2, 1, 1])       cube(5);
mirror([1, 0, 0])      cube(5);
```

链式：

```scad
translate([20, 0, 0])
    rotate([0, 90, 0])
        cylinder(h = 10, r = 2);
```

---

## 布尔（CSG）

```scad
union()        { cube(10); translate([8,0,0]) cube(10); }
difference()   { cube(10); translate([5,5,-1]) cylinder(h=12, r=2); }
intersection() { cube(10); translate([5,5,5]) sphere(7); }
```

---

## 模块与函数

```scad
module hex(d = 10, h = 5) {
    cylinder(h = h, r = d/2, $fn = 6);
}

// 阵列模块
module hex_grid(rows, cols, sp = 12) {
    for (i = [0:rows-1])
        for (j = [0:cols-1])
            translate([i*sp, j*sp*sin(60), 0])
                hex();
}

hex_grid(rows = 5, cols = 5);

// 函数（返回值）
function sq(x) = x * x;
echo(sq(5));     // → 25
```

---

## 循环与列表

```scad
// for 循环
for (i = [0 : 30 : 360])
    rotate([0, 0, i]) translate([20, 0, 0]) cube(2);

// 列表推导
points = [for (i = [0 : 0.1 : 6.28]) [10*cos(i*180/PI), 10*sin(i*180/PI)]];
polygon(points);
```

---

## 2D → 3D

```scad
// 2D 多边形拉伸
linear_extrude(height = 5, twist = 30, scale = 0.5)
    polygon([[0,0],[10,0],[10,10],[0,10]]);

// 旋转扫掠
rotate_extrude($fn = 100)
    translate([20, 0, 0]) circle(r = 3);

// 导入 SVG 后拉伸
linear_extrude(height = 4) import("logo.svg");
```

---

## 高级特性

### Hull 与 Minkowski

```scad
hull() {
    translate([0,0,0])  sphere(2);
    translate([20,0,0]) sphere(2);
}

minkowski() {
    cube(10);
    sphere(2);     // 倒圆角效果
}
```

### Customizer（参数面板）

```scad
/* [Box] */
length = 50;          // [10:1:200]
width  = 30;          // [10:1:200]

/* [Hidden] */
$fn = 64;
```

注释格式让 GUI 自动生成参数滑块。

---

## 命令行（CI/批处理）

```bash
# 渲染 STL（缺省是 ASCII STL，文件偏大）
openscad -o out.stl part.scad

# 明确要二进制 STL 或指定导出格式
openscad -o out.stl --export-format binstl part.scad

# 传参覆盖（-D 可重复）
openscad -D 'length=80' -D 'width=40' -o out.stl part.scad

# 改用 Manifold 后端（需该构建编入了 Manifold，先 openscad --info 确认）
openscad --backend Manifold -o out.stl part.scad

# 一次性多格式导出：-o 可重复
openscad -o out.stl -o out.3mf part.scad

# 导出 PNG 预览（PNG 走预览渲染，加 --render 才做完整几何求值）
openscad -o preview.png --camera=0,0,0,55,0,25,150 --imgsize=800,600 --render part.scad

# 导出 CSG/参数表等文本产物
openscad -o out.csg part.scad
```

| 开关 | 作用 |
|------|------|
| `-o, --o <file>` | 输出文件，扩展名决定格式（stl/off/wrl/amf/3mf/csg/dxf/svg/pdf/png/echo 等）；可重复；`-` 表示 stdout |
| `--export-format <fmt>` | 覆盖 `-o` 推导出的格式；ASCII 用 `asciistl`、二进制用 `binstl` |
| `-D, --D var=val` | 预定义变量，可重复 |
| `-p / -P` | 载入 Customizer 参数文件 / 参数集 |
| `-O <section/key=value>` | 传导出设置，如 `export-pdf/paper-size=a3`；`--help-export` 列出全部 |
| `--backend <CGAL\|Manifold>` | 3D 渲染后端；Manifold 快很多 |
| `--render` | PNG 导出时做完整几何求值（否则是预览渲染） |
| `--camera / --imgsize / --viewall / --autocenter` | PNG 相机与画布 |
| `--enable <feature>` | 打开实验特性（`roof`、`lazy-union`、`textmetrics`…，`all` 全开） |
| `-v, --version` / `--info` / `--help` | 版本 / 构建信息 / 帮助 |

> `-O` 的可用键随构建而变，写进 CI 前先跑一次 `--help-export`。

---

## 性能优化

1. `$fn` 不要全局设过高，需要圆滑的对象再设
2. **Manifold 后端**：CLI 加 `--backend Manifold`，GUI 在 Preferences → Features 启用，比 CGAL 快一个数量级
3. **避免大量布尔嵌套**：使用 `hull()` 或 `minkowski()` 后立即缓存为模块
4. **复用模块**优于复制粘贴
5. **`use <lib.scad>`** 引入库不递归求值
6. 大模型出图用 `-o` 只导需要的格式，别同时导 STL + PNG + 3MF

---

## 常用库

| 库 | 用途 |
|----|------|
| BOSL2 | 强大的几何工具集（齿轮/螺纹/金属件） |
| MCAD | 早期通用机械库 |
| NopSCADlib | 大量真实零部件（电机/轴承/PCB） |
| dotSCAD | 工程函数 / 多边形工具 |
| BezierScad | 贝塞尔曲线扫掠 |

---

## 典型工作流

### 工作流一：参数化零件从脚本到可打印 STL（端到端）

输入：一个尺寸参数表 + `part.scad`；输出：`build/*.stl`（逐个变体）+ 预览图。

1. 把尺寸写成顶部全局变量，并加 Customizer 注释：
   ```scad
   /* [Dimensions] */
   length = 50;   // [10:1:200]
   width  = 30;   // [10:1:200]
   height = 10;   // [2:1:60]
   hole_r = 2;    // [0.5:0.5:10]
   ```
2. 模块化：`module base() { cube([length, width, height]); }`、`module holes() { translate(...) cylinder(h=height+1, r=hole_r); }`
3. 主模型用 CSG 组合：`difference() { base(); holes(); }`
4. GUI 里 F6 预览、F7 渲染，确认实体为单一流形（不要有零厚度面）
5. 命令行出件（建议显式二进制 STL）：
   ```bash
   mkdir -p build
   openscad --backend Manifold -o build/part.stl --export-format binstl part.scad
   ```
6. 打印前自检：切片软件能正常读入且没有"非流形/未闭合"提示；有提示就回去查布尔输入

### 工作流二：CI 里按参数矩阵批量出件

1. 参数矩阵写成 CSV（`variants.csv`，每行一组参数），CI 逐行读取
2. 每行渲染一次，输出名带参数后缀：
   ```bash
   while IFS=, read -r L W; do
       openscad -D "length=$L" -D "width=$W" \
           -o "build/part_${L}x${W}.stl" --export-format binstl part.scad
   done < variants.csv
   ```
3. 需要缩略图时加一次 PNG 导出（`--camera` + `--imgsize` + `--render`）
4. 把 `build/` 作为 CI artifact 上传；渲染耗时高时开 `--backend Manifold`
5. 失败排查：`openscad` 非零退出码 + 终端里的 WARNING/ERROR 行，先单独重跑该变体

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 渲染极慢（几分钟以上） | 换 `--backend Manifold`；降低 `$fn`；减少布尔嵌套层数 |
| 导出 STL 不闭合 / 切片报非流形 | 布尔输入必须是流形实体；`linear_extrude` 的 2D 轮廓要闭合，避免零厚度壁与自相交 |
| 中文显示为方块或乱码 | 用系统已安装的 CJK 字体：`font = "Noto Sans CJK SC"`（Linux/Windows 字体名不同，先 `fc-list` 查） |
| `import("a.stl")` 很慢 | STL 三角面太多；先减面或转 OFF，并把导入结果缓存成模块只算一次 |
| 线性挤出后表面有杂线/失真 | 提高 `convexity`（`linear_extrude(height=10, convexity=10)`），减少渲染器误判 |
| `--backend Manifold` 报未知参数 | 该构建未编入 Manifold（发行版仓库版常见）；用官网 Snapshots 构建，`--info` 可确认 |
| 导出的 STL 比预期大很多 | 缺省是 ASCII STL；加 `--export-format binstl` |
| `-D` 传带引号或空格的值被 shell 吃掉 | 整体包在单引号里、内部用双引号：`-D 'quality="production"'`（Windows cmd 用双引号包裹并转义） |
| `-O` 设置报错 | 该键在当前构建不存在；先 `--help-export` 看可用键 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应将 OpenSCAD 模型组织为「全局参数 → 模块定义 → 主模型组合」的结构，利用 `module` 封装可复用组件。参数化面板用 `/* [ParamGroup] */` 注释格式暴露变量给 GUI Customizer。批处理使用 CLI `openscad -o out.stl model.scad -D 'param=value'`。
- **关键注意事项**：① `$fn` 不要全局设过高，仅对需要圆滑的对象单独设置；② Manifold 后端 CLI 用 `--backend Manifold`、GUI 在 Preferences → Features 启用（需安装带 Manifold 的构建）；③ `import("a.stl")` 场景避免频繁重导入，应缓存为模块；④ 中文字体使用 `font = "Noto Sans CJK SC"`；⑤ 缺省导出 ASCII STL，脚本里显式写 `--export-format binstl` 以免未来默认值变更时产出漂移。
- **不要臆造**：OpenSCAD 没有 `--headless` 参数（无 GUI 时用 `-o` 即可）；没有 `--script`/`--python` 之类内嵌脚本入口；`import()` 只吃 stl/off/svg/dxf 等有限格式，不要假设它能读 STEP。
- **常用代码模式**：基础体：`cube([l,w,h])` / `cylinder(h, r, $fn=N)` / `sphere(r, $fn=N)`。布尔：`difference() { ... }`。变换：`translate([x,y,z]) rotate([ax,ay,az])`。参数暴露：`/* [Section] */ variable = default; // [min:step:max]`。

---

## 相关技能

- **cadquery** — Python 参数化 CAD（BREP 内核，适合工业零件）：[../cadquery/SKILL.md](../cadquery/SKILL.md)
- **freecad** — 桌面参数化 CAD，含 GUI + Python 脚本：[../freecad/SKILL.md](../freecad/SKILL.md)
- **solvespace** — 轻量约束求解器建模，互补性工具：[../solvespace/SKILL.md](../solvespace/SKILL.md)
- **occt** — 工业级 B-Rep 内核（需要精确实体/STEP 往返时改用 OCCT 系工具）：[../occt/SKILL.md](../occt/SKILL.md)

---

## 参考资源

- 文档：<https://openscad.org/documentation.html>
- Cheatsheet：<https://openscad.org/cheatsheet/>
- 用户手册（Wikibook）：<https://en.wikibooks.org/wiki/OpenSCAD_User_Manual>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/openscad/>
