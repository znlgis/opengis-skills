---
name: mapsui
description: Mapsui 是面向现代 .NET 的开源跨平台地图组件库，支持 WPF、WinUI、MAUI、Avalonia、Uno、Blazor、WinForms 等几乎所有 .NET UI 框架，主打高性能（基于 SkiaSharp）、易用 API 和丰富的图层/瓦片源支持。
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

## 参考资源

- 文档：<https://mapsui.com/documentation/>
- 示例：<https://mapsui.com/samples>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/mapsui/>
