---
name: libredwg
description: LibreDWG 是 GNU 项目下的开源 DWG/DXF 读写库（C 语言），支持 R13–R2018 多个 AutoCAD 版本，提供 C/C++/Python/Lisp 等多语言绑定与一组命令行工具（dwgread/dwgwrite/dwg2dxf/dxf2dwg），是开源 CAD 互操作的关键基础。
tags: [dwg, dxf, cad, c, python, conversion]
---

> **项目地址：** <https://github.com/LibreDWG/libredwg>
>
> **官网：** <https://www.gnu.org/software/libredwg/>
>
> **手册：** <https://www.gnu.org/software/libredwg/manual/libredwg.html>
>
> **许可证：** GPL-3.0+

## 概述

LibreDWG 解决 DWG 二进制格式的开源读写：

- **支持版本**：DWG R13、R14、R2000、R2004、R2007、R2010、R2013、R2018
- **读写**：DWG ↔ DXF（ASCII/Binary），并能转 JSON/XML/SVG
- **命令行工具**：`dwgread`、`dwgwrite`、`dwg2dxf`、`dxf2dwg`、`dwg2SVG`、`dwgrewrite`
- **绑定**：C API、Python（`libredwg.python`）、Common Lisp、Perl

> 与 ODA / Teigha 的差异：LibreDWG 完全开源（GPL），但版本兼容范围比商业库窄、写入支持仍在完善。

---

## 安装

```bash
# Debian/Ubuntu
sudo apt install libredwg-dev libredwg0      # 库 + 头文件
sudo apt install libredwg-tools              # CLI

# Fedora
sudo dnf install libredwg-tools libredwg-devel

# macOS
brew install libredwg

# 源码
git clone https://github.com/LibreDWG/libredwg
./autogen.sh && ./configure --enable-write && make && sudo make install
```

---

## 命令行工具

```bash
# DWG → DXF（ASCII）
dwg2dxf -y input.dwg                       # → input.dxf
dwg2dxf -y -m -b input.dwg                 # binary DXF

# DXF → DWG
dxf2dwg -y input.dxf

# DWG → JSON / SVG / GeoJSON / YAML
dwgread -O JSON  -o out.json input.dwg
dwgread -O GeoJSON -o out.geojson input.dwg
dwg2SVG          input.dwg > out.svg

# 列出实体统计
dwgread input.dwg | head -50

# 重写（修复/版本转换）
dwgrewrite -v 2018 input.dwg out.dwg       # 转换为 R2018
```

常用 `-y` 强制覆盖，`-O` 选输出格式，`-v` 指定 DWG 版本。

---

## C API 入门

```c
#include <dwg.h>
#include <dwg_api.h>

int main(void) {
    Dwg_Data dwg = { 0 };
    if (dwg_read_file("input.dwg", &dwg) != 0) return 1;

    // 遍历模型空间实体
    BITCODE_BL n; Dwg_Object_Ref **mspace_refs = NULL;
    Dwg_Object *mspace = dwg_get_first_object(&dwg, DWG_TYPE_BLOCK_HEADER);
    Dwg_Object_BLOCK_HEADER *blk = mspace ? mspace->tio.object->tio.BLOCK_HEADER : NULL;

    if (blk) {
        Dwg_Object_Ref **ents = dwg_block_header_get_entities(blk, &error, &n);
        for (BITCODE_BL i = 0; i < n; ++i) {
            Dwg_Object *o = dwg_ref_object(&dwg, ents[i]);
            if (!o) continue;
            switch (o->fixedtype) {
              case DWG_TYPE_LINE: {
                Dwg_Entity_LINE *l = o->tio.entity->tio.LINE;
                printf("LINE (%g,%g)-(%g,%g)\n",
                       l->start.x, l->start.y, l->end.x, l->end.y);
                break;
              }
              case DWG_TYPE_CIRCLE: {
                Dwg_Entity_CIRCLE *c = o->tio.entity->tio.CIRCLE;
                printf("CIRCLE (%g,%g) r=%g\n", c->center.x, c->center.y, c->radius);
                break;
              }
            }
        }
    }
    dwg_free(&dwg);
}
```

编译：

```bash
gcc demo.c -o demo $(pkg-config --cflags --libs libredwg)
```

---

## 写入新 DWG

```c
Dwg_Data dwg = { 0 };
dwg.header.version = R_2018;
dwg.opts = DWG_OPTS_LOGLEVEL_INFO;

// 通过 dwg_add_* 系列工厂函数
Dwg_Object_BLOCK_HEADER *mspace = dwg_add_*();
dwg_add_LINE(mspace, &(Dwg_Object_3DPOINT){0}, &(Dwg_Object_3DPOINT){10,0,0});
dwg_add_CIRCLE(mspace, &(Dwg_Object_3DPOINT){5,0,0}, 2.0);

dwg_write_file("out.dwg", &dwg);
dwg_free(&dwg);
```

> 写入 API 仍在演化，建议参考 `programs/` 下示例与最新 API。

---

## Python 绑定

```bash
pip install LibreDWG-python
```

```python
import LibreDWG as dwg
data = dwg.dwg_read_file("input.dwg")
for e in data.modelspace.entities:
    print(type(e).__name__, getattr(e, 'layer', ''))
```

或使用 `subprocess` 调用 CLI 进行批处理：

```python
import subprocess, json
out = subprocess.check_output(["dwgread", "-O", "JSON", "input.dwg"])
data = json.loads(out)
```

---

## 转换为 GeoJSON（GIS 用途）

```bash
dwgread -O GeoJSON input.dwg -o out.geojson
```

适合将 DWG 中的多段线/多边形转入 PostGIS / QGIS。

---

## 性能与精度

1. 大文件用 `--no-check`、`-O DXFB`（二进制 DXF）减小体积
2. 读取后通过 `dwg_get_BLOCKS_HEADER` 等高层 API，避免遍历所有 objects
3. 写入时显式设置 `dwg.header.version`
4. 检查 `dwg_errstrings` 与 `dwg_set_loglevel` 排查
5. 浮点比较使用 `Dwg_Bitcode_2RD` 字段直接对比

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 高版本 DWG 无法读 | 等待 LibreDWG 支持，或先用 ODA File Converter 转为 R2010 |
| 写入失真 | 启用 `--enable-write` 编译；优先使用 DXF 出口 |
| 中文文字乱码 | DWG 编码为 ANSI/CP936；`dwgread -c utf8` 切换 |
| 引用块缺失 | 解析 `INSERT` 时跟随 `BLOCK_HEADER` 引用 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应根据场景选择 LibreDWG 的使用层级——简单转换用 CLI（`dwg2dxf`/`dwgread`），数据提取用 JSON/GeoJSON 输出，复杂处理用 C API 或 Python 绑定。写入功能仍在完善，写 DWG 前考虑先写 DXF 再转换。
- **关键注意事项**：① 高版本 DWG（R2021+）不被支持，先用 ODA File Converter 转为 R2010/R2018；② 中文文字编码默认为 ANSI/CP936，读取时可用 `dwgread -c utf8`；③ 写入需编译时启用 `--enable-write`；④ 大文件用 `--no-check` 加速读取。
- **常用代码模式**：CLI 转换：`dwg2dxf -y input.dwg` / `dwgread -O JSON input.dwg -o out.json` / `dwg2SVG input.dwg > out.svg`。C API：`dwg_read_file("input.dwg", &dwg)` → `dwg_get_first_object(&dwg, DWG_TYPE_BLOCK_HEADER)` → 遍历实体 → `dwg_free(&dwg)`。

---

## 相关技能

- **librecad** — 开源 2D CAD，DXF 编辑与 LibreDWG 协同使用：[../librecad/SKILL.md](../librecad/SKILL.md)
- **qcad** — 2D CAD 软件，DXF/DWG 处理：[../qcad/SKILL.md](../qcad/SKILL.md)
- **ifoxcad** — AutoCAD .NET 二次开发框架（DWG 读写高层封装）：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)
- **lightcad** — Web 2D CAD 框架：[../lightcad/SKILL.md](../lightcad/SKILL.md)

---

## 典型工作流

### 工作流一：DWG 数据提取与格式转换

1. `dwg2dxf -y input.dwg` 将 DWG 转为 DXF ASCII 格式
2. `dwgread -O JSON input.dwg -o out.json` 提取结构化数据
3. 解析 JSON，遍历模型空间实体（LINE/CIRCLE/INSERT/TEXT 等）
4. 将提取的几何数据转入下游系统（GIS/数据库/可视化）
5. 对于 GIS 用途：`dwgread -O GeoJSON input.dwg -o out.geojson` 直接生成 GeoJSON

### 工作流二：以 C 程序读写 DWG 文件

1. 引入 `<dwg.h>` 和 `<dwg_api.h>`，链接 `libredwg`
2. `dwg_read_file("input.dwg", &dwg)` 读取文件
3. 通过 `dwg_get_first_object(&dwg, DWG_TYPE_BLOCK_HEADER)` 获取模型空间
4. 使用 `dwg_block_header_get_entities()` 获取实体引用列表
5. 遍历实体，按 `fixedtype` 分派处理（DWG_TYPE_LINE / CIRCLE / TEXT 等）
6. `dwg_free(&dwg)` 释放内存

---

## 参考资源

- 手册：<https://www.gnu.org/software/libredwg/manual/libredwg.html>
- 示例：<https://github.com/LibreDWG/libredwg/tree/master/examples>
- 邮件列表：<bug-libredwg@gnu.org>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/libredwg/>