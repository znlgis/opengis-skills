---
name: mapsui
description: Mapsui 是面向现代 .NET 的开源跨平台地图组件库，支持 WPF、WinUI、MAUI、Avalonia、Uno、Blazor、WinForms 等几乎所有 .NET UI 框架，主打高性能（基于 SkiaSharp）、易用 API 和丰富的图层/瓦片源支持。
tags:
  - dotnet
  - csharp
  - map
  - wpf
  - maui
  - avalonia
  - blazor
  - skia
  - wms
  - tiles
---

> **项目地址：** <https://github.com/Mapsui/Mapsui>
>
> **官方文档：** <https://mapsui.com/documentation/>
>
> **许可证：** LGPL-2.1+

## 概述

- 跨 UI 框架：WPF / WinUI / MAUI / Avalonia / Uno / Blazor / WinForms
- SkiaSharp 渲染，性能优于 GDI+
- 数据源：OSM / WMS / WMTS / TMS / XYZ / Shapefile / GeoJSON / MBTiles / PostGIS
- 几何基于 NetTopologySuite
- 投影：`ProjNet` / `Mapsui.Projections`
- 内置交互：拖动、缩放、旋转、捏合、命中

---

## 安装

```bash
dotnet add package Mapsui.Wpf            # 或 Mapsui.Maui / Mapsui.Avalonia / ...
dotnet add package Mapsui.Tiling
dotnet add package Mapsui.Nts
```

---

## WPF 入门

```xml
<Window xmlns:mapsui="clr-namespace:Mapsui.UI.Wpf;assembly=Mapsui.UI.Wpf">
    <mapsui:MapControl x:Name="MapControl"/>
</Window>
```

```csharp
using Mapsui;
using Mapsui.Tiling;
using Mapsui.Projections;

var map = new Map();
map.Layers.Add(OpenStreetMap.CreateTileLayer());

var pt = SphericalMercator.FromLonLat(116.397, 39.908).ToMPoint();
map.Navigator.CenterOnAndZoomTo(pt, map.Navigator.Resolutions[10]);

MapControl.Map = map;
```

---

## 核心概念

| 类型 | 说明 |
|------|------|
| `Map` | 地图 |
| `Layer` / `MemoryLayer` / `ImageLayer` / `TileLayer` | 图层 |
| `IProvider` | 数据提供者 |
| `IFeature` / `GeometryFeature` | 要素（NTS 几何） |
| `IStyle` / `VectorStyle` / `LabelStyle` / `SymbolStyle` | 样式 |
| `Navigator` | 视图操作 |

---

## 矢量图层

```csharp
using Mapsui.Nts;
using Mapsui.Styles;

var features = new List<IFeature>();
foreach (var f in geoJsonFeatures)
    features.Add(new GeometryFeature(f.Geometry) {
        Styles = { new VectorStyle {
            Fill = new Brush(Color.Red),
            Outline = new Pen(Color.Black, 1)
        }}
    });

map.Layers.Add(new MemoryLayer("Roads") { Features = features, Style = null });
```

---

## Shapefile

```csharp
using Mapsui.Nts.Providers.Shapefile;
var prov = new ShapeFile("china.shp", true);
map.Layers.Add(new Layer("China") { DataSource = prov });
```

---

## 瓦片图层

```csharp
map.Layers.Add(OpenStreetMap.CreateTileLayer());

var src = new HttpTileSource(
    new GlobalSphericalMercator(0, 18),
    "https://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
    name: "AMap");
map.Layers.Add(new TileLayer(src) { Name = "AMap" });

// MBTiles
var mb = new MbTilesTileSource(new SQLiteConnectionString("city.mbtiles", false));
map.Layers.Add(new TileLayer(mb));
```

---

## WMS

```csharp
using Mapsui.Providers.Wms;
var wms = new WmsProvider("https://demo.mapserver.org/cgi-bin/wms?",
    new[] { "continents" });
map.Layers.Add(new ImageLayer("WMS") { DataSource = wms });
```

---

## 样式

```csharp
new SymbolStyle { SymbolScale = 0.7, Fill = new Brush(Color.Red) };

new LabelStyle {
    Text = "{name}",
    Font = new Font { Size = 14 },
    BackColor = new Brush(Color.WhiteSmoke),
    Halo = new Pen(Color.White, 2)
};
```

---

## 主题样式

```csharp
public class PopulationStyle : IThemeStyle {
    public IStyle? GetStyle(IFeature f) {
        var pop = (int)f["population"];
        return new VectorStyle { Fill = new Brush(pop > 1_000_000 ? Color.Red : Color.Blue) };
    }
}
layer.Style = new PopulationStyle();
```

---

## 交互

```csharp
MapControl.Info += (s, e) => {
    if (e.MapInfo?.Feature is GeometryFeature gf)
        Debug.WriteLine($"clicked {gf["name"]}");
};
```

---

## 性能优化

1. 海量点 → `RasterizingTileLayer` 包一层（按瓦片预渲染）
2. 优先 `MemoryLayer` + 缓存 Feature
3. 异步加载 + `await Layer.WaitForFinishedRefresh()`
4. 共享 Brush/Pen/Style 实例
5. SkiaSharp 关闭抗锯齿对极小符号有性能提升

---

## 常见问题

| 问题 | 解决 |
|------|------|
| WPF 无图 | NuGet 缺 `Mapsui.Wpf` 或没设置 `MapControl.Map` |
| 投影错误 | `SphericalMercator.FromLonLat` 转换 |
| MAUI 空白 | `MauiProgram` 中 `UseSkiaSharp()` + `UseMapsui()` |
| Shapefile 中文乱码 | 指定 Encoding |

---

## AI 使用建议

### 推荐工作流

1. **选择 UI 框架**：Mapsui 支持 WPF/WinUI/MAUI/Avalonia/Uno/Blazor/WinForms，根据需要选择对应的 NuGet 包
2. **创建 Map**：实例化 `Map`，添加图层（`TileLayer` 作为底图 + `MemoryLayer` 作为矢量覆盖层）
3. **数据转换**：通过 `SphericalMercator.FromLonLat()` 将经纬度转为 Web Mercator 坐标
4. **绑定控件**：将 `MapControl.Map` 设置为创建的 Map 对象
5. **添加交互**：通过 `MapControl.Info` 事件处理点击拾取，`Navigator` 控制视图

### 关键注意事项

- **NuGet 包完整**：确保安装了 `Mapsui.<UI框架>`、`Mapsui.Tiling`、`Mapsui.Nts` 三个包
- **投影转换**：WGS84 经纬度必须通过 `SphericalMercator.FromLonLat()` 转换后才能用于 Mapsui 定位
- **Shapefile 编码**：中文 Shapefile 需指定 `Encoding`（如 `Encoding.UTF8` 或 `Encoding.GetEncoding("GBK")`）
- **样式共享**：共享 `Brush`/`Pen`/`VectorStyle` 实例可提升性能
- **海量点优化**：使用 `RasterizingTileLayer` 包装海量点图层，按瓦片预渲染

## 典型工作流

### 工作流 1：加载底图 + GeoJSON 矢量数据

```csharp
using Mapsui;
using Mapsui.Tiling;
using Mapsui.Nts;
using Mapsui.Styles;
using NetTopologySuite.IO;

var map = new Map();

// 1. 添加 OSM 底图
map.Layers.Add(OpenStreetMap.CreateTileLayer());

// 2. 读取 GeoJSON 并添加为矢量图层
var gjReader = new GeoJsonReader();
var features = new List<IFeature>();
foreach (var f in geojsonFeatures)
{
    features.Add(new GeometryFeature(f.Geometry)
    {
        Styles = { new VectorStyle { Fill = new Brush(Color.Red) } }
    });
}
map.Layers.Add(new MemoryLayer("Data") { Features = features });

// 3. 定位
var center = SphericalMercator.FromLonLat(116.4, 39.9).ToMPoint();
map.Navigator.CenterOnAndZoomTo(center, map.Navigator.Resolutions[10]);

MapControl.Map = map;
```

### 工作流 2：Shapefile + WMS 叠加

```csharp
// Shapefile 图层
var shpProvider = new ShapeFile("china.shp", true);
map.Layers.Add(new Layer("China") { DataSource = shpProvider });

// WMS 图层（叠加）
var wmsProvider = new WmsProvider("https://geo.example.com/wms?", new[] { "rivers" });
map.Layers.Add(new ImageLayer("Rivers") { DataSource = wmsProvider });

map.ZoomToExtents();
```

## 相关技能

- **openlayers** — Web 二维地图库（JavaScript）：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **sharpmap** — .NET 传统地图渲染引擎：[../sharpmap/SKILL.md](../sharpmap/SKILL.md)
- **nettopologysuite** — .NET 几何计算核心：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)
- **geoserver** — 地图服务发布：[../geoserver/SKILL.md](../geoserver/SKILL.md)

## 参考资源

- 文档：<https://mapsui.com/documentation/>
- 示例：<https://mapsui.com/samples>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/mapsui/>
