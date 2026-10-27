---
name: libredwg
description: "Use when reading or writing AutoCAD DWG files programmatically with LibreDWG 0.14 — entity extraction, DWG to DXF/JSON/GeoJSON conversion, or dwg2dxf / dxf2dwg / dwgread batch pipelines; also when dwg2dxf blocks on an overwrite prompt (add -y), a R2021+ DWG will not load, or the CLI is missing on Linux because distro repos ship no libredwg package. C library (dwg_read_file, dwg_get_block_header, dwg_add_LINE) plus SWIG bindings."
tags:
  - dwg
  - dxf
  - cad
  - c
  - python
  - conversion
  - cli
---

> **项目地址：** <https://github.com/LibreDWG/libredwg>
>
> **官网：** <https://www.gnu.org/software/libredwg/>
>
> **手册：** <https://www.gnu.org/software/libredwg/>
>
> **许可证：** GPL-3.0+
>
> **最新稳定版：** 0.14（2026-06-27 发布，截至 2026-10，见 [GitHub Releases](https://github.com/LibreDWG/libredwg/releases)）

## 概述

LibreDWG 解决 DWG 二进制格式的开源读写：

- **读取版本**：DWG R1.4 – R2018+（R13、R14、R2000、R2004、R2007、R2010、R2013、R2018）
- **写入版本**：稳定支持 R1.4 – R2004（R2007+ 写入仍试验性）
- **读写**：DWG ↔ DXF（ASCII/DXFB），并能转 JSON/minJSON/GeoJSON/SVG
- **命令行工具**：`dwgread`、`dwgwrite`、`dwg2dxf`、`dxf2dwg`、`dwg2SVG`、`dwgrewrite`
- **绑定**：C API、Python（`LibreDWG` 模块，SWIG 生成）、Common Lisp、Perl

> 与 ODA / Teigha 的差异：LibreDWG 完全开源（GPL），但版本兼容范围比商业库窄、高版本写入支持仍在完善。当前稳定版 **0.14**（2026-06-27），详见 [GitHub Releases](https://github.com/LibreDWG/libredwg/releases)。

---

## 安装

```bash
# macOS（Homebrew，当前为 0.14）
brew install libredwg

# 源码构建（上游 README 流程；DWG 写入默认启用，需关闭时用 --disable-write）
git clone https://github.com/LibreDWG/libredwg
cd libredwg
./autogen.sh          # 从 git 检出源码时执行
./configure           # 可选：--disable-bindings / --disable-docs / --disable-shared
make
make check
sudo make install
```

> Debian/Ubuntu 与 Fedora 官方仓库均未提供 LibreDWG 包（不存在 `libredwg-dev`/`libredwg-tools`），Linux 请按上述源码方式构建。

---

## 命令行工具

```bash
# DWG → DXF（ASCII）
dwg2dxf -y input.dwg                       # → input.dxf
dwg2dxf -y -m -b input.dwg                 # -b = 二进制 DXB（→ input.dxb），-m 只留最小头

# DXF → DWG
dxf2dwg -y input.dxf

# DWG → JSON / GeoJSON（dwgread 的 -O 支持 DXF、DXFB、JSON、minJSON、GeoJSON）
dwgread -O JSON    -o out.json    input.dwg
dwgread -O GeoJSON -o out.geojson input.dwg

# DWG → SVG（独立程序 dwg2SVG）
dwg2SVG input.dwg > out.svg

# 列出实体统计 / 排错
dwgread input.dwg | head -50

# 重写（修复或版本转换，--as rNNNN 指定目标版本）
dwgrewrite --as r2004 input.dwg out.dwg    # 写成 R2004
```

要点：

- `-y` 免覆盖确认；`-O` 选输出格式，`-o` 指定输出文件（`dwgread -o` 的扩展名也能反推格式）
- `dwg2dxf -b` 产出的是 **DXB（二进制 DXF 的旧式载体，`.dxb`）**，不等于"二进制 DXF"；需要普通 DXF 就去掉 `-b`
- `--as rNNNN` 的可写版本：`r1.4`–`r2004` 可用，`r2007`/`r2010`/`r2013`/`r2018` 在用法说明里仍标为 **Planned**，写不出去
- `-v[0-9]` 提高 verbosity；`dwgread --version` 可打印版本

---

## C API 入门

读取后遍历 `dwg.object` 数组、按 `fixedtype` 分派，是与仓库 `examples/load_dwg.c` 一致的稳定写法：

```c
#include <stdio.h>
#include <string.h>
#include <dwg.h>
#include <dwg_api.h>

int main(void) {
    Dwg_Data dwg;
    memset(&dwg, 0, sizeof(Dwg_Data));

    if (dwg_read_file("input.dwg", &dwg) != 0)
        return 1;

    for (BITCODE_BL i = 0; i < dwg.num_objects; i++) {
        Dwg_Object *o = &dwg.object[i];
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

    dwg_free(&dwg);
    return 0;
}
```

编译（pkg-config 文件由 `make install` 安装）：

```bash
gcc demo.c -o demo $(pkg-config --cflags --libs libredwg)
```

---

## 写入 DWG

写入走 `dwg_add_*` 工厂函数，第一个参数是模型空间对应的 `BLOCK_HEADER`（经 `dwg_get_block_header` 取得）。以下为常用子集：

```c
#include <string.h>
#include <dwg.h>
#include <dwg_api.h>

int main(void) {
    Dwg_Data dwg;
    int error = 0;
    dwg_point_3d p1 = { 0.0, 0.0, 0.0 };
    dwg_point_3d p2 = { 10.0, 0.0, 0.0 };

    memset(&dwg, 0, sizeof(Dwg_Data));
    dwg.header.version = R_2000;          /* 写入稳定版本区间：R1.4 – R2004 */

    Dwg_Object_BLOCK_HEADER *hdr = dwg_get_block_header(&dwg, &error);
    if (!hdr || error)
        return 1;

    Dwg_Entity_LINE *line = dwg_add_LINE(hdr, &p1, &p2);
    if (!line)
        return 1;

    if (dwg_write_file("out.dwg", &dwg) != 0)
        return 2;

    dwg_free(&dwg);
    return 0;
}
```

> 写入 API 仍在演化：具体签名以 `include/dwg_api.h` 与 `examples/dwgadd.c` 为准；R2007+ 写入仍属试验性，跨软件交换请停在上表的稳定版本或先出 DXF。

---

## Python 绑定

```bash
# 源码构建：SWIG 绑定默认启用（需先装 SWIG），可用 --disable-bindings / --disable-python 关闭
./autogen.sh && ./configure && make && sudo make install
```

> PyPI 上没有 LibreDWG-python 包，Linux 发行版官方仓库也未打包绑定，Python 绑定须随源码一起构建。

SWIG 模块名为 `LibreDWG`，绑定是 `include/dwg.h` 结构体的薄封装（没有 `modelspace.entities` 这类封装层），字段名与 C 结构体一致；实际字段以 `bindings/dwg.i` 与 `include/dwg.h` 为准，升级版本后要重新核对。

多数批处理场景用 `subprocess` 调 CLI 更省事，输出稳定且不受绑定版本影响：

```python
import subprocess, json

out = subprocess.check_output(["dwgread", "-O", "JSON", "input.dwg"])
data = json.loads(out)                 # 顶层含 HEADER / OBJECTS / CLASSES 等段
print(len(data.get("OBJECTS", [])) if isinstance(data, dict) else len(data))
```

---

## 转换为 GeoJSON（GIS 用途）

```bash
dwgread -O GeoJSON input.dwg -o out.geojson
```

适合将 DWG 中的多段线/多边形转入 PostGIS / QGIS。

---

## 典型工作流

### 工作流一：DWG 实体提取并转入 GIS（端到端）

输入：`input.dwg`；输出：`out/entities.json` 与 `out/model.geojson`。

1. 摸底：`dwgread input.dwg | head -50` 看能否解析、实体量级如何
2. 转 DXF 做人工核查：`dwg2dxf -y -o out/drawing.dxf input.dwg`
3. 提结构化数据：`dwgread -O JSON input.dwg -o out/entities.json`
4. 需要空间数据时直接出 GeoJSON：`dwgread -O GeoJSON input.dwg -o out/model.geojson`
5. 把 GeoJSON 灌进 PostGIS/QGIS 前先确认坐标系：DWG 的 UCS 与实际 CRS 未必一致，缺 CRS 时要人工指定后再入库
6. 校验：`python -c "import json;d=json.load(open('out/entities.json'));print(type(d))"` 确认结构与规模

### 工作流二：用 C 程序读 DWG 并筛选实体

1. 引入 `<dwg.h>` 与 `<dwg_api.h>`，链接 `-lredwg`（或 `pkg-config --cflags --libs libredwg`）
2. `dwg_read_file("input.dwg", &dwg)` 读取文件，失败即返回
3. 遍历 `dwg.object[0..num_objects)`，按 `fixedtype` 分派（`DWG_TYPE_LINE` / `DWG_TYPE_CIRCLE` / `DWG_TYPE_TEXT` …）
4. 从 `o->tio.entity->tio.LINE` 等联合体成员取几何字段，做过滤/统计/导出
5. `dwg_free(&dwg)` 释放；需要写回时按上节用 `dwg_get_block_header` + `dwg_add_*`
6. 用 `gcc demo.c -o demo $(pkg-config --cflags --libs libredwg)` 编译，先在小样本 DWG 上跑通再上大文件

---

## 性能与精度

1. 大文件用 `--no-check`、`-O DXFB`（二进制 DXF）减小体积
2. 只关心少数实体时，可在遍历 `dwg.object` 时提前跳过不匹配的 `fixedtype`，避免逐个解析联合体
3. 写入时显式设置 `dwg.header.version`，且目标版本落在写入稳定区间（R1.4 – R2004）
4. 排错时提高 verbosity（`-v`/`LIBREDWG_TRACE`），并检查 `dwg_read_file` 的返回值
5. 浮点比较直接用位码字段（如 `Dwg_Entity_LINE` 的坐标字段），不要与字符串输出互相印证

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 高版本 DWG 无法读 | 当前支持到 R2018 的**读**；更高版本先用 ODA File Converter 转 R2010/R2018 |
| `dwgrewrite --as r2018` 报错或没有产出，或 `dwg2dxf -b` 出来的东西别的软件不认 | `r2007`–`r2018` 写入仍是 Planned，只能写到 `r2004` 及以下；`-b` 是 DXB 不是二进制 DXF |
| 写入失真 | 确认编译时未加 `--disable-write`（DWG 写入默认启用）；优先使用 DXF 出口 |
| 中文文字乱码 | 编码由 DWG 头 `$DWGCODEPAGE` 决定（简体中文常见 ANSI_936）；优先用 `dwgread -O JSON` 输出 UTF-8，或对 DXF 输出用 iconv 转码 |
| 引用块缺失 | 解析 `INSERT` 时跟随 `BLOCK_HEADER` 引用 |
| 脚本里 `dwg2dxf` 卡在"覆盖已存在文件"确认 | 加 `-y` 免确认（`dwg2dxf -y`、`dxf2dwg -y`），CI 里必带 |
| Linux 上找不到 `dwgread` | Debian/Fedora 官方仓库不提供 LibreDWG 包；须从源码 `make install`，CLI 工具（`dwgread`/`dwg2dxf` 等）随源码一并安装 |
| 写出的 DWG 其它软件打不开 | DWG 写入器（`dxf2dwg`/`dwgwrite`，写入默认启用，除非 configure 加了 `--disable-write`）覆盖面仍不完整；稳妥做法是停在 DXF：`dwg2dxf` 读出 → 编辑 DXF → 交 AutoCAD/ODA 侧另存 DWG |
| GeoJSON 里线型丢失或几何不闭合 | GeoJSON 只导出可平面化的几何；需要保形状先 `dwg2SVG` 或 `dwg2dxf`，在 DXF 层面做处理再回转 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应根据场景选择 LibreDWG 的使用层级——简单转换用 CLI（`dwg2dxf`/`dwgread`），数据提取用 JSON/GeoJSON 输出，复杂处理用 C API 或 Python 绑定。写入功能仍在完善，写 DWG 前考虑先写 DXF 再转换。
- **关键注意事项**：① 高版本 DWG（R2021+）不被支持，先用 ODA File Converter 转为 R2010/R2018；② 中文文字编码由 DWG 头 `$DWGCODEPAGE` 决定（简体中文常见 ANSI/CP936），输出 JSON 为 UTF-8；③ DWG 写入默认启用（configure 加 `--disable-write` 才关闭）；④ 大文件用 `--no-check` 加速读取。
- **常用代码模式**：CLI 转换：`dwg2dxf -y input.dwg` / `dwgread -O JSON input.dwg -o out.json` / `dwg2SVG input.dwg > out.svg`。C API：`dwg_read_file("input.dwg", &dwg)` → 遍历 `dwg.object[i]` 按 `fixedtype` 分派 → `dwg_free(&dwg)`；写 DWG 走 `dwg_get_block_header` + `dwg_add_LINE` + `dwg_write_file`。
- **不要臆造**：没有 `dwg_get_first_object` 取"模型空间实体列表"这种一步到位的封装；绑定模块名固定为 `LibreDWG`（SWIG），不要写 `import libredwg` / `from pydwg import ...`；Debian/Fedora 官方仓库确实没有 `libredwg-tools` 包。

---

## 相关技能

- **librecad** — 开源 2D CAD，DXF 编辑与 LibreDWG 协同使用：[../librecad/SKILL.md](../librecad/SKILL.md)
- **qcad** — 2D CAD 软件，DXF/DWG 处理：[../qcad/SKILL.md](../qcad/SKILL.md)
- **ifoxcad** — AutoCAD .NET 二次开发框架（DWG 读写高层封装）：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)
- **lightcad** — Web 2D CAD 框架：[../lightcad/SKILL.md](../lightcad/SKILL.md)

---

## 参考资源

- 手册：<https://www.gnu.org/software/libredwg/>
- 示例：<https://github.com/LibreDWG/libredwg/tree/master/examples>
- 邮件列表：<bug-libredwg@gnu.org>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/libredwg/>
