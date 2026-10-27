---
name: brutile
description: "Use when fetching or enumerating map tiles in .NET with BruTile 6.0.0 — HttpTileSource over HttpClient, KnownTileSources.Create, ITileSchema.GetTileInfos for a viewport and resolution, MbTilesTileSource for offline MBTiles, or wiring tiles into Mapsui/SharpMap. Also for missing 'BruTile.Desktop' packages, CS0246 on KnownTileSources, MBTiles SQLite native load failures, and 404s from inverted TMS/OSM y-axis."
tags:
  - dotnet
  - csharp
  - tiles
  - tms
  - wmts
  - mbtiles
  - openstreetmap
  - webmapping
  - http
---

> **项目地址：** <https://github.com/BruTile/BruTile>
>
> **NuGet：** `BruTile` 6.0.0 / `BruTile.MbTiles` 6.0.0（net8.0 / net9.0，截至 2026-10）
>
> **官方文档：** <https://github.com/BruTile/BruTile>
>
> **许可证：** Apache-2.0

## 概述

BruTile 是一个只管「瓦片」的 .NET 库：给定视口范围与分辨率，算出需要哪些瓦片，再去对应服务把瓦片字节取回来。它不做渲染、不含 UI，瓦片最终由 Mapsui、SharpMap、ArcBruTile 等地图组件显示。这种职责划分让 BruTile 可以同时支撑 WPF、MAUI、Blazor、ASP.NET 等多种宿主，也是它在 .NET 地图栈中长期作为底座的原因。

- **瓦片方案（schema）**：Web 墨卡托全球网格、WMTS、TMS、WMS-C 等组织的分辨率与瓦片索引映射
- **瓦片源**：HTTP 瓦片服务（XYZ/OSM、ArcGIS、Bing 等）、MBTiles 离线文件、文件系统瓦片缓存
- **视口计算**：`ITileSchema.GetTileInfos(extent, resolution)` 求当前需要渲染的瓦片集合
- **缓存**：内存缓存与持久化缓存（MBTiles、文件系统）可组合
- **坐标系约定**：默认 Web 墨卡托（EPSG:3857），OSM 与 TMS 的 y 轴方向不同，需显式选择

> **版本提示**：BruTile 6.0.0 只发布 net8.0 / net9.0 目标。需要 netstandard2.0 的场景（例如 .NET Framework、SharpMap 1.2）只能用 5.0.6 或更早版本，详见下方版本对照表。

---

## 环境准备

### 安装

```bash
# 在线瓦片（HTTP 服务）
dotnet add package BruTile --version 6.0.0

# 离线 MBTiles 需要额外的包
dotnet add package BruTile.MbTiles --version 6.0.0

# 需要挂在 Mapsui 上时
dotnet add package Mapsui --version 5.1.0
```

```powershell
Install-Package BruTile -Version 6.0.0
```

### 验证

```csharp
using BruTile;
using BruTile.Predefined;

var schema = new GlobalSphericalMercator();
Console.WriteLine(schema.Resolutions.Count);   // 默认 0..19 级共 20 个分辨率
var tileInfos = schema.GetTileInfos(
    new Extent(-20037508, -20037508, 20037508, 20037508), 156543.03392804097);
Console.WriteLine(tileInfos.Count());          // 0 级应只有 1 张
```

```bash
dotnet run
```

### 版本与目标框架对照

| BruTile 版本 | 目标框架 | 说明 |
|--------------|----------|------|
| 6.0.0 | net8.0 / net9.0 | 当前版本；`HttpTileSource.GetTileAsync` 需要传入 `HttpClient` |
| 5.0.6 | net6.0 / netstandard2.0 | 兼容 .NET Framework 4.6.1+ 与 .NET 6/7 |
| 4.0.0 / 3.1.3 | netstandard2.0 / netstandard1.1 | 老项目常用；`BruTile.Desktop` 在 4.0 起被删除，内容并入 `BruTile` |

`BruTile.Desktop`、`BruTile.Desktop.DbCache` 这两个包名在 4.0 之后已不存在，旧代码里的 `using BruTile.Desktop` 需要改命名空间。

---

## 核心 API

### TileSchema 与分辨率

```csharp
using BruTile;
using BruTile.Predefined;

// 全球 Web 墨卡托，默认 0-19 级；y 轴默认 OSM 约定
var schema = new GlobalSphericalMercator(minZoomLevel: 0, maxZoomLevel: 18);

// 自定义瓦片方案
var custom = new TileSchema
{
    Name = "MyTiles",
    Srs = "EPSG:3857",
    Extent = new Extent(-20037508, -20037508, 20037508, 20037508),
    YAxis = YAxis.OSM,
    Format = "image/png",
};
custom.Resolutions.Add(0, new Resolution(0, 156543.03392804097, 256, 256));
custom.Resolutions.Add(1, new Resolution(1, 78271.51696402048, 256, 256));
```

| 成员 | 说明 |
|------|------|
| `GlobalSphericalMercator(int min = 0, int max = 19)` | 标准 Web 墨卡托网格，最常用 |
| `TileSchema.Resolutions` | 级别 → `Resolution(level, unitsPerPixel, tileWidth, tileHeight, …)` |
| `TileSchema.YAxis` | `YAxis.OSM`（原点左上，y 向下）或 `YAxis.TMS`（原点左下，y 向上） |
| `TileSchema.Extent` / `Srs` / `Format` | 服务范围、坐标系与瓦片格式 |
| `schema.GetTileInfos(extent, unitsPerPixel)` | 按视口范围与分辨率求需要的瓦片 |
| `schema.GetTileInfos(extent, level)` | 按缩放级别求瓦片 |

### HttpTileSource

```csharp
using BruTile;
using BruTile.Predefined;
using BruTile.Web;

// 自定义 XYZ 服务；{s} 为子域占位，传 serverNodes 展开
var source = new HttpTileSource(
    new GlobalSphericalMercator(0, 18),
    "https://{s}.tile.example.com/{z}/{x}/{y}.png",
    new[] {"a", "b", "c"},
    name: "example");

using var http = new HttpClient();
var extent = new Extent(12900000, 4800000, 13000000, 4900000);
double resolution = extent.Width / 800;          // 800 像素宽的视口

foreach (TileInfo info in source.Schema.GetTileInfos(extent, resolution))
{
    byte[]? png = await source.GetTileAsync(http, info);   // 6.x：显式传 HttpClient
    Console.WriteLine($"{info.Index.Level}/{info.Index.Col}/{info.Index.Row}: {png?.Length ?? 0} bytes");
}
```

| 成员 | 说明 |
|------|------|
| `HttpTileSource(ITileSchema, string urlFormatter, IEnumerable<string>? serverNodes, ...)` | 用 URL 模板构造，`{s}`/`{z}`/`{x}`/`{y}` 为占位符 |
| `HttpTileSource(ITileSchema, IUrlBuilder, ...)` | 自定义 URL 构造逻辑，适合带签名参数的商业服务 |
| `IHttpTileSource.GetTileAsync(HttpClient, TileInfo, CancellationToken?)` | 6.x 取瓦片，HttpClient 由调用方持有以便复用连接 |
| `Name` / `Attribution` | 显示名称与版权信息，出图时必须展示 |

`HttpClient` 按应用生命周期创建一次即可，每次请求 new 一个会耗尽 socket；这是 `IHttpTileSource` 把客户端作为参数传进来的主要原因。

### KnownTileSources

```csharp
using BruTile.Predefined;

var osm     = KnownTileSources.Create();                                  // 默认 OpenStreetMap
var cycle   = KnownTileSources.Create(KnownTileSource.OpenCycleMap);
var satellite = KnownTileSources.Create(KnownTileSource.BingAerial, apiKey: "YOUR_BING_KEY");
var noneApi = KnownTileSources.Create(KnownTileSource.EsriWorldTopo);
```

`KnownTileSource` 覆盖 OSM/OpenCycleMap、Bing（Aerial/Hybrid/Roads 及其 Staging 变体）、Stamen 系列、Esri World 系列、BKG（德国）、Here 系列；需要密钥的服务通过 `apiKey` 传入。`Create` 还可传 `minZoomLevel` / `maxZoomLevel` 限制范围，但每个服务内部会再按自身能力截断（例如 OSM 最高 18 级、Bing 从 1 级起），实际可用级别以返回的 `Schema.Resolutions` 为准。

### MBTiles 离线瓦片

```csharp
using BruTile;
using BruTile.MbTiles;
using SQLite;

var connection = new SQLiteConnectionString("data/world.mbtiles", SQLiteOpenFlags.ReadOnly);
var mbTiles = new MbTilesTileSource(connection);

var tile = await mbTiles.GetTileAsync(new TileInfo {Index = new TileIndex(0, 0, 0)});
Console.WriteLine(tile?.Length);
```

| 成员 | 说明 |
|------|------|
| `MbTilesTileSource(SQLiteConnectionString, ITileSchema?, MbTilesType, ...)` | 打开 MBTiles；schema 可从元数据读取，也可显式传入 |
| `MbTilesTileSource.GetTileAsync(TileInfo)` | 实现 `ILocalTileSource`，本地读取不需要 HttpClient |
| `MbTilesType` | `None` / `BaseLayer` / `Overlay` 等，用于区分图层语义 |

`SQLiteConnectionString` 来自 `sqlite-net`，6.0.0 的 MBTiles 包通过 `SQLitePCLRaw` 3.x 带原生库；发布到 AOT/裁剪环境时必须显式保留 SQLite 原生库，否则运行期报「无法加载 sqlite3」。

---

## 典型工作流

把 OSM 在线底图和一个 MBTiles 离线图层组合起来，先判断视口需要哪些瓦片，再分别取图并统计缓存命中：

**输入**：视口范围（Web 墨卡托米）、屏幕像素宽度、MBTiles 文件
**输出**：控制台打印每张瓦片的来源与字节数

1. 用 `GlobalSphericalMercator` 建立方案，按视口宽 / 像素宽算出分辨率
2. 用 `GetTileInfos(extent, resolution)` 得到需要的瓦片列表
3. MBTiles 优先，缺失时回落到 HTTP 源
4. 复用同一个 `HttpClient`

```csharp
using BruTile;
using BruTile.MbTiles;
using BruTile.Predefined;
using SQLite;

var extent = new Extent(12957000, 4852000, 12960000, 4855000);
const int viewportWidth = 1024;
double resolution = extent.Width / viewportWidth;

var http = new HttpClient();
var osm = KnownTileSources.Create(KnownTileSource.OpenStreetMap);

var offline = new MbTilesTileSource(
    new SQLiteConnectionString("data/region.mbtiles", SQLiteOpenFlags.ReadOnly));

int fromCache = 0, fromWeb = 0;
foreach (TileInfo info in osm.Schema.GetTileInfos(extent, resolution))
{
    byte[]? bytes = await offline.GetTileAsync(info);
    if (bytes is {Length: > 0})
    {
        fromCache++;
        continue;
    }

    bytes = await osm.GetTileAsync(http, info);
    if (bytes is {Length: > 0}) fromWeb++;
}

Console.WriteLine($"cache={fromCache} web={fromWeb}");
```

**检查点**：瓦片数量随缩放级别呈 4 倍增长，`fromWeb` 异常大通常说明 MBTiles 的 y 轴约定与 schema 不一致（OSM 与 TMS 相反），可在 `MbTilesTileSource` 构造时显式传 schema 验证。

---

## 最佳实践

1. **复用 HttpClient 与 TileSource**：瓦片源与 HttpClient 都是无状态可复用的对象，放在字段或 DI 单例里
2. **明确 y 轴约定**：OSM 原点在左上、TMS 在左下；瓦片行列错位错位一整屏，先把 `YAxis` 对齐再排查网络
3. **缓存分两层**：内存缓存应对快速平移缩放，MBTiles 或文件系统缓存应对离线与省钱；构造 `HttpTileSource` 时传 `persistentCache`
4. **限制缩放级别**：`GlobalSphericalMercator(min, max)` 与服务实际级别一致，超出范围只会拿到 404
5. **尊重版权与速率限制**：OSM 等公共服务有使用政策，生产环境用商业或自建瓦片服务，`Attribution` 要显示出来
6. **MBTiles 只读打开**：`SQLiteOpenFlags.ReadOnly` + 单例连接，避免多线程写锁
7. **按目标框架选版本**：net8+ 用 6.0.0；netstandard2.0 或 SharpMap 1.2 场景降到 5.0.6/4.0.0

---

## 常见问题

| 问题 | 原因与解决 |
|------|------------|
| 编译报 `CS0246: 找不到类型 KnownTileSources` | 缺少 `using BruTile.Predefined;`；6.x 中该类型命名空间是 `BruTile.Predefined` |
| 找不到 `BruTile.Desktop` 包 | 该包在 4.0 起被删除，内容并入 `BruTile`：改用 `BruTile` 主包与 `BruTile.MbTiles` |
| `HttpTileSource.GetTileAsync(tileInfo)` 编译失败 | 6.x 改为 `IHttpTileSource.GetTileAsync(httpClient, tileInfo, cancellationToken)`：传入复用的 `HttpClient`，或降到 5.0.6 |
| 瓦片全部 404 | 缩放级别超出服务范围，或 `{z}/{x}/{y}` 模板与服务的路径顺序不符；先用浏览器直接请求一张瓦片验证模板 |
| 瓦片内容上下颠倒 / 行列错位 | OSM（原点左上）与 TMS（原点左下）的 y 轴相反：调整 `TileSchema.YAxis` 或改用 `YAxis.TMS` 的方案 |
| MBTiles 打开报「无法加载 sqlite3」 | 原生库未随应用发布：确认 `SQLitePCLRaw` 相关包被复制到输出目录，AOT/裁剪时显式保留 |
| 拉取大量瓦片后程序卡死或连接耗尽 | 每次请求 new `HttpClient`：改为共享实例，并配合并发上限（如 `SemaphoreSlim`） |
| 地图上瓦片模糊或偏移 | 分辨率计算用了错误的视口宽度，或瓦片尺寸不是 256：`Resolution` 的 `tileWidth`/`tileHeight` 必须与服务一致 |

---

## AI 使用建议

- **执行环境**：`dotnet add package` / `dotnet build` / `dotnet run` 在终端中执行，首次 restore 需访问 NuGet。
- **先探测版本**：`dotnet list package` 确认 `BruTile` 是 6.0.0 还是 5.x——两者的 `GetTileAsync` 签名不同，写代码前必须确认；目标框架须为 net8.0/net9.0 才能用 6.0.0。
- **验证产物**：先跑「schema + GetTileInfos 计数」的最小用例（0 级应为 1 张瓦片），再验证网络取图；取图结果检查字节长度大于 0，不要只看是否抛异常。
- **网络与权限**：抓取第三方瓦片服务前确认其使用政策与是否需要 key；不要在示例里写死真实密钥。
- **失败信号**：404 先查模板与级别；行列错位查 `YAxis`；`DllNotFoundException`/无法加载 sqlite3 查 MBTiles 原生库复制。
- **排错顺序**：先离线验证 schema 计算，再接网络层，最后接 UI；把三层分开验证能快速定位是坐标、网络还是渲染问题。

## 相关技能

- **mapsui** — 现代跨平台 .NET 地图组件，直接用 BruTile 作瓦片源：[../mapsui/SKILL.md](../mapsui/SKILL.md)
- **sharpmap** — 旧版渲染库，通过 `SharpMap.Layers.BruTile` 使用 BruTile（版本受限）：[../sharpmap/SKILL.md](../sharpmap/SKILL.md)
- **nettopologysuite** — 空间几何与坐标，常与瓦片坐标换算配合：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)
- **projnet4geoapi** — 坐标变换，处理非 Web 墨卡托瓦片时使用：[../projnet4geoapi/SKILL.md](../projnet4geoapi/SKILL.md)
- **leaflet** — Web 端瓦片地图，便于对照 XYZ 模板与 y 轴约定：[../leaflet/SKILL.md](../leaflet/SKILL.md)

## 参考资源

- 源码与示例（`Samples/BruTile.GettingStarted`）：<https://github.com/BruTile/BruTile>
- 预定义瓦片源定义：<https://github.com/BruTile/BruTile/blob/master/BruTile/Predefined/KnownTileSources.cs>
- NuGet：<https://www.nuget.org/packages/BruTile>
- MBTiles 规范：<https://github.com/mapbox/mbtiles-spec>
- OSM 瓦片使用政策：<https://operations.osmfoundation.org/policies/tiles/>
