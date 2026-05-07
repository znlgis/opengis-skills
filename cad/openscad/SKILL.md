---
name: openscad
description: OpenSCAD 是面向程序员的开源 3D CAD 软件，用声明式脚本语言定义参数化模型，配合 CSG（构造实体几何）原语和函数模块构造复杂几何，特别适合机械零件、3D 打印模型与教育用途。
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
# macOS
brew install --cask openscad
# Windows: 安装包
# 开发版（更快的 Manifold 内核）：<https://openscad.org/downloads.html#snapshots>
```

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
# 渲染 STL
openscad -o out.stl part.scad

# 传参覆盖
openscad -D 'length=80' -D 'width=40' -o out.stl part.scad

# 导出 PNG 预览
openscad -o preview.png --camera=0,0,0,55,0,25,150 --imgsize=800,600 part.scad
```

---

## 性能优化

1. `$fn` 不要全局设过高，需要圆滑的对象再设
2. **Manifold 内核**（开发版）：选 Edit → Preferences → Features 启用，比 CGAL 快 10×+
3. **避免大量布尔嵌套**：使用 `hull()` 或 `minkowski()` 后立即缓存为模块
4. **复用模块**优于复制粘贴
5. **`use <lib.scad>`** 引入库不递归求值

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

## 常见问题

| 问题 | 解决 |
|------|------|
| 渲染极慢 | 启用 Manifold 内核；降低 `$fn` |
| 导出 STL 不闭合 | 检查布尔输入是否流形 |
| 中文文字 | `font = "Noto Sans CJK SC"` |
| `import("a.stl")` 慢 | 转换为 OFF 或预先 mesh decimation |
| 装配线性挤出失真 | `convexity` 参数加大 |

---

## 参考资源

- 文档：<https://openscad.org/documentation.html>
- Cheatsheet：<https://openscad.org/cheatsheet/>
- 用户手册（Wikibook）：<https://en.wikibooks.org/wiki/OpenSCAD_User_Manual>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/openscad/>
