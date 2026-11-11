---
name: geos
description: "Use when working with the GEOS C/C++ geometry engine that powers PostGIS, QGIS, Shapely and GDAL — GEOSGeomFromWKT/GEOSIntersection/GEOSBuffer/GEOSMakeValid C API, geos::geom C++ API, OverlayNG robustness, GEOSPrepare and GEOSSTRtree, or debugging TopologyException and self-intersection."
license: MIT
metadata:
  category: gis
  tags: "c, cpp, geometry, topology, overlay, postgis, shapely, gis"
---

> **项目地址：** <https://github.com/libgeos/geos>
>
> **官方文档：** <https://libgeos.org/>
>
> **最新版本：** 3.15.0（2026-09-01 发布，截至 2026-11，[Release 3.15.0](https://github.com/libgeos/geos/releases/tag/3.15.0) / [下载与构建页](https://libgeos.org/usage/download/)）
>
> **C API 文档：** <https://libgeos.org/usage/c_api/> ｜ **C++ API 文档：** <https://libgeos.org/usage/cpp_api/>
>
> **许可证：** LGPL-2.1（C 库链接后按 LGPL 动态链接条款使用）

## 概述

GEOS（Geometry Engine, Open Source）是用 C++ 实现的二维矢量几何运算库，主体移植自 Java 的 JTS Topology Suite。它是开源空间数据栈的「几何内核」：PostGIS 的 ST_Intersection/ST_Buffer、QGIS 的叠加分析、Python Shapely、GDAL/OGR 的矢量叠加后端、R 的 sf 包，底层都在调用 GEOS。

核心能力：

- **几何模型**：Point / LineString / LinearRing / Polygon / Multi* / GeometryCollection，支持 XY、XYZ、XYM、XYZM
- **空间关系**：Intersects、Contains、Within、Touches、Crosses、Overlaps、Covers、Relate（DE-9IM）
- **集合与叠加运算**：Intersection、Union、Difference、SymDifference、UnaryUnion、Buffer、Clip、Split
- **构造与修复**：MakeValid、Normalize、Snap、Node、Polygonize、Densify、Simplify
- **索引与加速**：STRtree（批量窗口查询、最近邻）、PreparedGeometry（重复谓词加速）
- **序列化**：WKT、WKB、GeoJSON 读写器

**与相邻技术的分工**：JTS 是同一套算法的 Java 实现（GEOS 的语义上游）；Shapely 是 GEOS 的 Python 绑定；PostGIS 把 GEOS 编译进数据库后端；GDAL/OGR 用 GEOS 做矢量叠加，但数据格式读写由 GDAL 负责。需要跨语言一致结果时以 GEOS 版本为准——不同 GEOS 版本的叠加结果可能有细微差异。

**API 选型结论先行**：一般应用用 **C API**（`geos_c.h`，ABI 稳定、可跨小版本换库）；要嵌入 C++ 工程并接受重新编译时用 **C++ API**（`geos/geom/*.h`，无 ABI 稳定承诺）。下文示例默认 C API，C++ 差异单独标注。

---

## 环境准备与安装

### 通过包管理器

```bash
# Ubuntu / Debian（需要更新版本时可加 ppa:ubuntugis/ppa）
sudo apt-get install geos libgeos-dev

# RHEL / Amazon Linux（EPEL 提供）
sudo yum install -y epel-release geos geos-devel

# macOS
brew install geos
```

```bash
# 自检：确认版本与头文件/库可见
geos-config --version
pkg-config --modversion geos
```

### 从源码构建（官方 CMake 流程）

```bash
tar xvfj geos-3.15.0.tar.bz2
cd geos-3.15.0
mkdir _build && cd _build

cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  ..
make -j4
ctest                     # 可选但建议：跑一遍单元测试
sudo make install
```

**构建要求**：CMake ≥ 3.15、支持 C++14 的编译器（常规测试 GCC / Clang / MSVC）、可选 Doxygen 生成 API 文档。常用开关：`BUILD_SHARED_LIBS=ON`（默认开）、`BUILD_TESTING=ON`（默认开）、`BUILD_DOCUMENTATION=OFF`（默认关）、`CMAKE_BUILD_TYPE` 取 `Release` / `RelWithDebInfo` / `Debug` / `ASAN`。

链接时 C API 用 `-lgeos_c`，C++ API 用 `-lgeos`。用 pkg-config 更省事：

```bash
cc myapp.c -o myapp $(pkg-config --cflags --libs geos)
```

Windows 下建议用 vcpkg 或 conda-forge 安装，并让 `geos_c.dll` 与可执行文件同目录或加入 `PATH`。

---

## C API 基础骨架

C API 只有一个头文件 `<geos_c.h>`，使用前必须注册消息回调并初始化全局状态，退出时清理。

```c
#include <stdio.h>
#include <stdarg.h>
#include <geos_c.h>

static void geos_msg_handler(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
}

int main(void) {
    initGEOS(geos_msg_handler, geos_msg_handler);

    GEOSWKTReader *reader = GEOSWKTReader_create();
    GEOSGeometry *geom = GEOSWKTReader_read(reader, "POINT(1 1)");

    GEOSWKTWriter *writer = GEOSWKTWriter_create();
    char *wkt = GEOSWKTWriter_write(writer, geom);
    printf("%s\n", wkt);

    GEOSFree(wkt);              /* GEOS 分配的字符串必须用 GEOSFree 释放 */
    GEOSGeom_destroy(geom);
    GEOSWKTWriter_destroy(writer);
    GEOSWKTReader_destroy(reader);

    finishGEOS();
    return 0;
}
```

编译：`cc hello.c -o hello -lgeos_c`。

### 可重入与多线程版本

所有 C 函数都有 `_r` 后缀的可重入变体，多一个 `GEOSContextHandle_t` 参数。每个线程各自 `GEOS_init_r()` 建上下文、自己 `GEOS_finish_r()`，**不要跨线程共享 context handle**。

```c
GEOSContextHandle_t ctx = GEOS_init_r();
GEOSContext_setNoticeHandler_r(ctx, geos_msg_handler);
GEOSContext_setErrorHandler_r(ctx, geos_msg_handler);

GEOSWKTReader *reader = GEOSWKTReader_create_r(ctx);
GEOSGeometry *g = GEOSWKTReader_read_r(ctx, reader, "POINT(1 1)");
GEOSWKTWriter *writer = GEOSWKTWriter_create_r(ctx);
char *wkt = GEOSWKTWriter_write_r(ctx, writer, g);

GEOSFree_r(ctx, wkt);
GEOSGeom_destroy_r(ctx, g);
GEOSWKTWriter_destroy_r(ctx, writer);
GEOSWKTReader_destroy_r(ctx, reader);
GEOS_finish_r(ctx);
```

---

## 核心 API

### 几何构造

| 用途 | C 函数 |
|---|---|
| 点 | `GEOSGeom_createPointFromXY(x, y)`、`GEOSGeom_createPoint(seq)` |
| 线串 / 环 | `GEOSGeom_createLineString(seq)`、`GEOSGeom_createLinearRing(seq)` |
| 面 | `GEOSGeom_createPolygon(shell, holes, nholes)` |
| 集合 | `GEOSGeom_createCollection(type, geoms, n)` |
| 坐标序列 | `GEOSCoordSeq_create(n, dims)`、`GEOSCoordSeq_copyFromBuffer(buf, n, hasZ, hasM)` |
| 文本 → 几何 | `GEOSWKTReader_read`、`GEOSWKBReader_read`、`GEOSGeoJSONReader_readGeometry` |

```c
/* 用坐标数组造一条 3 点的线，再转 WKT */
double coords[] = {0, 0, 10, 10, 20, 0};
GEOSCoordSequence *seq = GEOSCoordSeq_copyFromBuffer(coords, 3, 0, 0);
GEOSGeometry *line = GEOSGeom_createLineString(seq);  /* 所有权转移给 geometry */
```

**所有权规则**：`GEOSGeom_create*()` 接收坐标序列后由其负责释放，**不要再手动 `GEOSCoordSeq_destroy`**；几何对象一律 `GEOSGeom_destroy()`，GEOS 返回的字符串一律 `GEOSFree()`。

### 叠加与缓冲

```c
GEOSGeometry *a = GEOSWKTReader_read(r, "POLYGON((0 0,10 0,10 10,0 10,0 0))");
GEOSGeometry *b = GEOSWKTReader_read(r, "POLYGON((5 5,15 5,15 15,5 15,5 5))");

GEOSGeometry *inter = GEOSIntersection(a, b);       /* 相交 */
GEOSGeometry *uni   = GEOSUnion(a, b);             /* 合并 */
GEOSGeometry *diff  = GEOSDifference(a, b);        /* 差集 */
GEOSGeometry *sym   = GEOSSymDifference(a, b);     /* 对称差 */
GEOSGeometry *buf   = GEOSBuffer(a, 2.0, 8);       /* 半径 2，每四分之一圆 8 段 */
GEOSGeometry *hull  = GEOSConvexHull(a);
```

`GEOSBuffer` 默认圆头圆角；方头 / 斜接需用 `GEOSBufferWithStyle`（参数：quadSegs、endCapStyle、joinStyle、mitreLimit）。

### 空间谓词与 DE-9IM

```c
char hit     = GEOSIntersects(a, b);          /* 1 真 / 2 假 / 0 异常 */
char inside  = GEOSContains(a, b);
char covered = GEOSCovers(a, b);
char rel     = GEOSRelatePattern(a, b, "T*F**FFF*");
char *matrix = GEOSRelate(a, b);              /* 9 字符 DE-9IM 矩阵 */
GEOSFree(matrix);
```

谓词返回 `char`：`1` 真、`2` 假、`0` 出错（查错误回调）。**不要当布尔直接取反**。

### PreparedGeometry：重复谓词加速

同一个大面被几万个点反复 `Intersects` / `Contains` 时，预处理能带来数量级提升。

```c
const GEOSPreparedGeometry *prep = GEOSPrepare(polygon);  /* 只读，不接管 polygon 所有权 */
for (size_t i = 0; i < n; i++) {
    if (GEOSPreparedIntersects(prep, pts[i]) == 1) {
        /* 命中 */
    }
}
GEOSPreparedGeom_destroy(prep);
/* polygon 与 pts 仍需自行 destroy */
```

### STRtree：窗口查询与最近邻

```c
typedef struct { GEOSGeometry *geom; size_t id; } item;

GEOSSTRtree *tree = GEOSSTRtree_create(10);   /* 参数是节点分支数，10 是常用值 */
for (size_t i = 0; i < n; i++) {
    GEOSSTRtree_insert(tree, items[i]->geom, items[i]);  /* 只存指针，不接管所有权 */
}

GEOSGeometry *queryEnv = GEOSWKTReader_read(r, "POLYGON((20 20,22 20,22 22,20 22,20 20))");
GEOSSTRtree_query(tree, queryEnv, queryCallback, &count);  /* 回调逐个给候选 */
```

最近邻用 `GEOSSTRtree_nearest_generic(tree, item, geom, distanceCallback, userdata)`，距离回调里调用 `GEOSDistance` 判定真实距离。用完 `GEOSSTRtree_destroy(tree)`，并自行释放所有 item 几何。

### 有效性修复与精度

```c
GEOSGeometry *fixed = GEOSMakeValid(invalid);   /* 自相交、环重叠等无效面修复 */
char ok = GEOSisValid(invalid);                 /* 1 有效 / 2 无效 / 0 出错 */
char *reason = GEOSisValidReason(invalid);      /* 无效原因文本 */
GEOSGeometry *snapped = GEOSSnap(a, b, 1e-6);   /* 容差吸附，治理近重合顶点 */
```

**OverlayNG**：自 GEOS 3.9 起默认叠加引擎已是 OverlayNG（鲁棒、失败率显著低于旧引擎），无需额外开关。遇到 `TopologyException` 优先做有效性修复或加容差（`GEOSSnap` / 先量化坐标），而不是反复重算。3.15 的破坏性变化之一：叠加遇到连续子段时输出 `LineString` 而非 `MultiLineString`，下游不要假设返回类型。

### 内存与错误处理要点

| 规则 | 说明 |
|---|---|
| 成对释放 | `GEOSGeom_destroy` / `GEOSWKTReader_destroy` / `GEOSSTRtree_destroy` / `GEOSFree` 各管各的对象 |
| 字符串专用 | `GEOSWKTWriter_write`、`GEOSRelate` 返回的 `char*` 必须 `GEOSFree`，不能用 `free()` |
| 序列所有权 | `GEOSGeom_createLineString/Polygon` 成功后不得再 destroy 该坐标序列 |
| 空结果 | 无交返回 `POLYGON EMPTY` 一类空几何，不是 `NULL`；`NULL` 只表示出错 |
| 出错排查 | `GEOS_getLastError()`（可重入版 `GEOS_getLastError_r(ctx)`）配合错误回调看原文 |

---

## 典型工作流

### 工作流一：WKT → 缓冲 → 相交 → 输出 WKT（C API）

输入两块相交的 WKT 多边形；输出缓冲后的相交面积与 WKT。

```c
initGEOS(geos_msg_handler, geos_msg_handler);
GEOSWKTReader *r = GEOSWKTReader_create();
GEOSGeometry *a = GEOSWKTReader_read(r, "POLYGON((0 0,10 0,10 10,0 10,0 0))");
GEOSGeometry *b = GEOSWKTReader_read(r, "POLYGON((5 5,15 5,15 15,5 15,5 5))");

GEOSGeometry *inter = GEOSIntersection(a, b);
GEOSGeometry *buf = GEOSBuffer(inter, 0.5, 8);

double area = 0.0;
GEOSArea(buf, &area);                 /* 校验：应大于 0 */
printf("area = %.3f\n", area);

GEOSWKTWriter *w = GEOSWKTWriter_create();
GEOSWKTWriter_setTrim(w, 1);          /* 3.12 起默认已 trim，此行仅显式声明 */
char *out = GEOSWKTWriter_write(w, buf);
printf("%s\n", out);

GEOSFree(out);
GEOSGeom_destroy(buf); GEOSGeom_destroy(inter);
GEOSGeom_destroy(a); GEOSGeom_destroy(b);
GEOSWKTWriter_destroy(w); GEOSWKTReader_destroy(r);
finishGEOS();
```

**校验产物**：`area` 为正、输出 WKT 能被 `GEOSWKTReader_read` 读回且 `GEOSisValid` 为 1。

### 工作流二：C++ API 嵌入（geos::geom）

```cpp
#include <iostream>
#include <memory>
#include <geos/geom/GeometryFactory.h>
#include <geos/geom/Geometry.h>
#include <geos/io/WKTReader.h>
#include <geos/io/WKTWriter.h>

using namespace geos::geom;
using namespace geos::io;

int main() {
    GeometryFactory::Ptr factory = GeometryFactory::create();
    WKTReader reader(*factory);

    std::unique_ptr<Geometry> a(reader.read("POLYGON((0 0,10 0,10 10,0 10,0 0))"));
    std::unique_ptr<Geometry> b(reader.read("POLYGON((5 5,15 5,15 15,5 15,5 5))"));
    std::unique_ptr<Geometry> inter = a->intersection(b.get());

    WKTWriter writer;
    writer.setTrim(true);            /* 3.12 之前才必须显式设置 */
    std::cout << writer.write(inter.get()) << std::endl;
    return 0;
}
```

编译：`g++ -std=c++14 demo.cpp -o demo -lgeos`。C++ 侧注意：`GeometryFactory::create()` 返回 `Ptr`（`std::unique_ptr`）；`WKTReader` 必须绑定 factory 以共享 PrecisionModel；**C++ ABI 不跨版本稳定**，升级 GEOS 后必须重新编译。

### 工作流三：几何清洗流水线（服务端批处理）

1. `GEOSWKBReader_read` 读入源数据（比 WKT 更小更快）
2. `GEOSisValid` 检查，无效则 `GEOSMakeValid` 修复
3. `GEOSNormalize` 统一顶点顺序与环方向，便于结果比对
4. `GEOSUnaryUnion` 合并同层要素，`GEOSBuffer(geom, 0, 8)` 消除自相交残渣
5. `GEOSWKBWriter_write` 写回，并记录修复前后 `GEOSisValid` 结果

**校验产物**：抽样统计修复前后 `GEOSisValid == 1` 的比例，以及 `GEOSArea` 总量变化不超过阈值（避免修复把几何吃掉）。

---

## 常见问题

| 问题 | 原因 | 处置 |
|---|---|---|
| `TopologyException: side location conflict` / `Self-intersection` | 输入几何无效（自相交、环重叠、重复点） | 先 `GEOSisValid` + `GEOSMakeValid` 修复；仍失败加 `GEOSSnap` 容差 |
| 段错误（Segmentation fault） | 忘记 `initGEOS`、跨线程共用 context、或对已 destroy 的几何再操作 | 补初始化 / 用 `_r` 每线程独立 context；用 ASAN 构建定位 |
| 返回字符串释放后崩溃 | 用 `free()` 释放 GEOS 分配的字符串 | 改用 `GEOSFree()`（Windows 上尤为关键） |
| 退出时报内存泄漏 | 坐标序列被重复释放，或 item 几何未销毁 | 确认 `GEOSGeom_create*` 后不再 destroy 序列；STRtree 只存指针，item 自己释放 |
| 链接报 `undefined reference to GEOSIntersection` | 只链接了 `-lgeos`（C++ 库） | C API 要链接 `-lgeos_c`，用 `pkg-config --libs geos` 最稳 |
| 谓词判断结果反了 | C API 谓词返回 `char`：1 真 / 2 假 / 0 异常 | 用 `== 1` 判真，不要直接当布尔取反 |
| 升级后叠加结果类型变了 | 3.15 起连续子段叠加输出 `LineString` 而非 `MultiLineString` | 按 `GEOSGeomTypeId` 分支处理，不要硬转型 |
| 空结果被当成错误 | 无交返回 `POLYGON EMPTY`，不是 `NULL` | 用 `GEOSisEmpty` 判断而非判空指针 |

---

## AI 使用建议

- **执行环境**：C 示例用 `cc demo.c -o demo $(pkg-config --cflags --libs geos)` 编译；C++ 示例用 `g++ -std=c++14 demo.cpp -lgeos`。Windows 优先 vcpkg / conda-forge，运行时确保 `geos_c.dll` 在搜索路径。
- **先探测版本**：`geos-config --version` 或 `pkg-config --modversion geos`；版本差异集中在叠加引擎、空几何语义与 M 值保留，报告结论时带上版本号。
- **验证产物**：不要只看「程序没崩」——用 `GEOSisValid`、`GEOSArea`、`GEOSGetNumGeometries` 三方断言；WKT/WKB 往返后再比一次面积与顶点数。
- **易错操作**：混用 `GEOSGeom_destroy` 与 `GEOSFree`、忘记 `initGEOS`、多线程共享 context、对 `char*` 调 `free()`——这四类占了绝大多数崩溃与泄漏。
- **性能验证**：重复谓词先用 `GEOSPrepare`，批量窗口查询先建 `GEOSSTRtree`，再用 `std::chrono` / `clock_gettime` 计时对比，用数据证明优化有效。
- **安全与权限**：`make install` 会写系统目录（默认 `/usr/local`），执行前先征得用户同意；生产升级前先备份，并在副本上跑一遍几何回归。

## 相关技能

- **jts** — GEOS 的 Java 上游实现（算法语义同源）：[../jts/SKILL.md](../jts/SKILL.md)
- **shapely** — GEOS 的 Python 绑定，本技能是其底层内核：[../shapely/SKILL.md](../shapely/SKILL.md)
- **postgis** — 把 GEOS 编进数据库后端提供 ST_* 函数：[../postgis/SKILL.md](../postgis/SKILL.md)
- **gdal** — OGR 矢量处理，叠加运算调用 GEOS：[../gdal/SKILL.md](../gdal/SKILL.md)
- **nettopologysuite** — JTS 的 .NET 移植（同族算法）：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)

## 参考资源

- **GitHub 仓库：** <https://github.com/libgeos/geos>
- **官网：** <https://libgeos.org/>
- **C API 编程指南：** <https://libgeos.org/usage/c_api/>
- **C++ API 编程指南：** <https://libgeos.org/usage/cpp_api/>
- **下载与构建：** <https://libgeos.org/usage/download/>
- **安装包说明：** <https://libgeos.org/usage/install/>
- **C API 参考（Doxygen）：** <https://libgeos.org/usage/doxygen/>
- **常见问题：** <https://libgeos.org/usage/faq/>
- **旧版本下载：** <https://download.osgeo.org/geos/>
- **绑定列表（Shapely / sf / PostGIS 等）：** <https://libgeos.org/usage/bindings/>
