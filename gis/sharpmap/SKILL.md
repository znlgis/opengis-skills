---
name: sharpmap
description: "Use when rendering 2D maps in legacy .NET Framework 4.7.2 WinForms or ASP.NET WebForms apps with SharpMap 1.2.0 — Map.GetMap() to PNG, ShapeFile/PostGIS providers, VectorLayer with CustomTheme, TileAsyncLayer via BruTile, ProjNet4GeoAPI transforms, or debugging blank output and GDI+ handle leaks. New projects should use Mapsui."
tags:
  - dotnet
  - csharp
  - 2d
  - map
  - rendering
  - wms
  - shapefile
  - postgis
  - winforms
---

> **项目地址：** <https://github.com/SharpMap/SharpMap>
>
> **官方文档：** <https://github.com/SharpMap/SharpMap/wiki>
>
> **NuGet：** `SharpMap`、`SharpMap.UI`、`SharpMap.Extensions`、`SharpMap.Web`、`SharpMap.Layers.BruTile`
>
> **最新版本：** 1.2.0（截至2026-10，NuGet；发布于 2021-03，仓库未归档但维护低频）
>
> **许可证：** LGPL-2.1-or-later

## 概述

SharpMap 提供：

- **数据源**：Shapefile、PostGIS、SQL Server Spatial、Oracle Spatial、SQLite/SpatiaLite、WMS、WFS、TileSource（OSM/Bing）
- **图层模型**：`VectorLayer`、`LabelLayer`、`TileLayer`、`WmsLayer`
- **样式**：`VectorStyle`、`LabelStyle`、按属性主题样式
- **坐标变换**：通过 `ProjNet`
- **几何**：基于 NetTopologySuite
- **渲染**：System.Drawing 位图 / WMS 服务输出
- **UI 控件**：WinForms `MapBox`

> **注意**：SharpMap 核心库目标框架为 netstandard2.0，而 WinForms 控件包 `SharpMap.UI` 仅支持 .NET Framework 4.7.2；仓库未归档但维护低频。新项目建议改用 Mapsui。

---

## 安装

```bash
dotnet add package SharpMap                 # 核心（netstandard2.0）
dotnet add package SharpMap.UI              # WinForms MapBox 控件（.NET Framework 4.7.2）
dotnet add package SharpMap.Extensions      # 扩展数据源（PostGIS、OGR、SpatiaLite 等）
dotnet add package SharpMap.Layers.BruTile  # 在线瓦片图层 TileAsyncLayer（依赖 BruTile 2.1.2）
dotnet add package SharpMap.Web             # ASP.NET WMS 服务
dotnet add package ProjNet4GeoAPI           # 坐标变换（实现 GeoAPI 接口；ProjNet 2.x 与 SharpMap 1.2 类型不兼容）
```

---

## 核心 API：核心对象

| 类型 | 说明 |
|------|------|
| `Map` | 地图 |
| `ILayer` / `VectorLayer` / `LabelLayer` / `TileLayer` | 图层 |
| `IProvider` | 数据提供者 |
| `VectorStyle` / `LabelStyle` | 样式 |

---

## WinForms 入门

```csharp
using SharpMap;
using SharpMap.Layers;
using SharpMap.Data.Providers;
using SharpMap.Styles;
using System.Drawing;

var map = new Map(new Size(800, 600));

var prov = new ShapeFile("countries.shp", true);
var layer = new VectorLayer("countries", prov)
{
    Style = new VectorStyle {
        Fill = new SolidBrush(Color.LightGreen),
        Outline = Pens.Black,
        EnableOutline = true
    }
};
map.Layers.Add(layer);

var labels = new LabelLayer("labels") {
    DataSource = prov,
    LabelColumn = "NAME",
    Style = new LabelStyle { Font = new Font("Arial", 10) }
};
map.Layers.Add(labels);

map.ZoomToExtents();
mapBox1.Map = map;
mapBox1.Refresh();
```

---

## PostGIS 数据源

```csharp
var conn = "Host=localhost;Database=gisdb;User Id=postgres;Password=pg";
var prov = new PostGIS(conn, "poi", "geom", "id");
map.Layers.Add(new VectorLayer("poi", prov));
```

---

## OSM 瓦片底图

```csharp
using BruTile.Predefined;
var src = KnownTileSources.Create(KnownTileSource.OpenStreetMap);
map.Layers.Add(new TileAsyncLayer(src, "OSM"));
map.SRID = 3857;
```

---

## 主题样式

```csharp
using SharpMap.Rendering.Thematics;

var theme = new CustomTheme(row => {
    var pop = (int)row["POP"];
    return new VectorStyle {
        Fill = new SolidBrush(pop > 1_000_000 ? Color.Red : Color.Blue)
    };
});
layer.Theme = theme;
```

---

## 坐标变换

```csharp
using ProjNet.CoordinateSystems;
using ProjNet.CoordinateSystems.Transformations;

var ctf = new CoordinateTransformationFactory();
layer.CoordinateTransformation = ctf.CreateFromCoordinateSystems(
    GeographicCoordinateSystem.WGS84,
    ProjectedCoordinateSystem.WebMercator);
map.SRID = 3857;
```

---

## 输出图像与 WMS

```csharp
using var img = map.GetMap();
img.Save("map.png");

// ASP.NET WMS
public void ProcessRequest(HttpContext ctx)
{
    var map = MapHelper.InitializeMap();
    SharpMap.Web.Wms.WmsServer.ProcessRequest(ctx, map);
}
```

---

## 拾取与查询

```csharp
mapBox1.MouseDown += (s, e) => {
    var pt = mapBox1.Map.ImageToWorld(new PointF(e.X, e.Y));
    var ds = new SharpMap.Data.FeatureDataSet();
    layer.DataSource.ExecuteIntersectionQuery(
        new NetTopologySuite.Geometries.Envelope(pt.X-1e-3, pt.X+1e-3,
                                                 pt.Y-1e-3, pt.Y+1e-3), ds);
    foreach (FeatureDataRow row in ds.Tables[0].Rows)
        Console.WriteLine(row["NAME"]);
};
```

---

## 性能建议

1. 预建空间索引（Shapefile `.qix`、PostGIS GiST）
2. `TileAsyncLayer` 用于在线底图
3. 避免主线程加载大数据
4. `LabelLayer` 启用优先级与碰撞检测
5. 复用 `Brush/Pen/VectorStyle`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 无图 | 检查 SRID、`ZoomToExtents` |
| 文字模糊 | 设置高 DPI Aware、`MapBox.MapTransform` |
| GDI+ 内存泄漏 | 释放 `Brush/Pen/Bitmap` |
| Shapefile 中文乱码 | `new ShapeFile(path, true, false, Encoding.UTF8)` |
| 找不到 `SharpMap.UI.WinForms` 包 | 该包名在 NuGet 上不存在，WinForms 控件在 `SharpMap.UI` 包中 |
| `CoordinateTransformation` 赋值编译错误 | ProjNet 2.x 不再实现 GeoAPI 接口，改用 `ProjNet4GeoAPI` 1.4.1 |
| 找不到 `TileAsyncLayer` | 瓦片图层不在核心包中，需安装 `SharpMap.Layers.BruTile` |

---

## 典型工作流

### 工作流 1：Shapefile 渲染 + 主题样式 + 输出图片

```csharp
using SharpMap;
using SharpMap.Layers;
using SharpMap.Data.Providers;
using SharpMap.Styles;
using SharpMap.Rendering.Thematics;
using System.Drawing;

// 创建地图
var map = new Map(new Size(1024, 768));
map.SRID = 4326;

// 添加 Shapefile 图层
var prov = new ShapeFile("countries.shp", true);
var layer = new VectorLayer("Countries", prov)
{
    Style = new VectorStyle
    {
        Fill = Brushes.LightGreen,
        Outline = Pens.Black,
        EnableOutline = true
    }
};

// 按人口设置主题样式
layer.Theme = new CustomTheme(row =>
{
    var pop = (int)row["POP_EST"];
    return new VectorStyle
    {
        Fill = new SolidBrush(pop > 100_000_000 ? Color.Red : Color.LightBlue)
    };
});
map.Layers.Add(layer);

// 添加行政标注
var labels = new LabelLayer("Labels")
{
    DataSource = prov, LabelColumn = "NAME",
    Style = new LabelStyle { Font = new Font("Arial", 10) }
};
map.Layers.Add(labels);

// 渲染
map.ZoomToExtents();
using var img = map.GetMap();
img.Save("output.png");
```

### 工作流 2：PostGIS 数据 + OSM 底图 + WMS 发布

```csharp
// PostGIS 数据
var pgConn = "Host=localhost;Database=gisdb;User Id=postgres;Password=pg";
var poiProvider = new PostGIS(pgConn, "poi", "geom", "id");
map.Layers.Add(new VectorLayer("POI", poiProvider)
{
    Style = new VectorStyle { Fill = Brushes.OrangeRed }
});

// OSM 底图
using BruTile.Predefined;
var tileSrc = KnownTileSources.Create(KnownTileSource.OpenStreetMap);
map.Layers.Add(new TileAsyncLayer(tileSrc, "OSM"));
map.SRID = 3857;
```

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("sharpmap")` 加载（用户也可输入 `/sharpmap`）；示例写入会话工作区的 .NET 工程，技能目录只读。
- **执行环境**：先 `dotnet --list-sdks`；核心包 `SharpMap` 是 netstandard2.0，可被 .NET 8+ 工程引用，但 WinForms 控件 `SharpMap.UI` 只有 .NET Framework 4.7.2，目标框架必须选 net472，不能套 net8.0。
- **验证产物**：`dotnet build` 后 `map.GetMap()` 取 `System.Drawing.Image` 再 `Save("output.png")`，用 `read_image` 看实际着色与标注；编译通过不代表渲染正确。
- **依赖风险**：SharpMap 1.2.0（2021-03）的传递依赖含 `NetTopologySuite.Core` 1.15.3、`System.Drawing.Common` 4.6.0、`System.Data.SqlClient` 4.7.0，`dotnet restore` 会报 NU1902/NU1903/NU1904 漏洞告警，需向用户说明而不是静默忽略。
- **坐标与 SRID**：`map.SRID` 与图层 SRID 必须一致；ProjNet 2.x 不再实现 GeoAPI 接口，坐标变换用 `ProjNet4GeoAPI` 1.4.1。
- **资源释放**：GDI+ 的 `Brush`/`Pen`/`Bitmap` 必须 `using` 或 `Dispose`，否则长时间运行内存持续上涨。
- **安全与权限**：新建工程、装包、连接 PostGIS 前先征得用户同意；连接串里的密码不要写进代码或回答。

## 相关技能

- **mapsui** — .NET 现代跨平台地图组件（推荐替代）：[../mapsui/SKILL.md](../mapsui/SKILL.md)
- **nettopologysuite** — .NET 几何计算核心：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)
- **openlayers** — Web 二维地图库：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)

## 参考资源

- Wiki：<https://github.com/SharpMap/SharpMap/wiki>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/SharpMap/>
