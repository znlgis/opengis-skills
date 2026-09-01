# GeoTools Raster and Rendering Reference

GeoTIFF raster processing and map rendering examples split from SKILL.md.

---

## 栅格数据（GeoTIFF）

### 读取 GeoTIFF

```java
import org.geotools.gce.geotiff.GeoTiffReader;
import org.geotools.coverage.grid.GridCoverage2D;

File file = new File("data/dem.tif");
GeoTiffReader reader = new GeoTiffReader(file);
GridCoverage2D coverage = reader.read(null);

// 获取 CRS
CoordinateReferenceSystem crs = coverage.getCoordinateReferenceSystem();

// 获取范围
ReferencedEnvelope envelope = new ReferencedEnvelope(coverage.getEnvelope());

// 获取像素值
double[] values = coverage.evaluate(
    new DirectPosition2D(crs, 116.4, 39.9), (double[]) null
);

// 获取栅格图像
RenderedImage image = coverage.getRenderedImage();

reader.dispose();
```

### 写入 GeoTIFF

```java
import org.geotools.gce.geotiff.GeoTiffWriter;

File output = new File("output/result.tif");
GeoTiffWriter writer = new GeoTiffWriter(output);
writer.write(coverage, null);
writer.dispose();
```

---

## 地图渲染

### 渲染为 PNG 图片

```java
import org.geotools.map.*;
import org.geotools.styling.*;
import org.geotools.renderer.lite.StreamingRenderer;
import java.awt.image.BufferedImage;
import java.awt.*;

// 创建地图
MapContent map = new MapContent();
map.setTitle("城市分布图");

// 添加矢量图层
Style style = SLD.createSimpleStyle(featureSource.getSchema());
map.addLayer(new FeatureLayer(featureSource, style));

// 渲染为图片
int width = 800, height = 600;
BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
Graphics2D g2d = image.createGraphics();
g2d.setColor(Color.WHITE);
g2d.fillRect(0, 0, width, height);

StreamingRenderer renderer = new StreamingRenderer();
renderer.setMapContent(map);
renderer.paint(g2d, new Rectangle(width, height), map.getMaxBounds());
g2d.dispose();

// 保存
javax.imageio.ImageIO.write(image, "png", new File("output/map.png"));
map.dispose();
```

### 使用 SLD 样式

```java
import org.geotools.styling.*;
import org.geotools.factory.CommonFactoryFinder;

StyleFactory sf = CommonFactoryFinder.getStyleFactory();
FilterFactory2 ff = CommonFactoryFinder.getFilterFactory2();

// 创建面填充样式
Fill fill = sf.createFill(ff.literal(new Color(0, 128, 255, 128)));
Stroke stroke = sf.createStroke(ff.literal(Color.BLACK), ff.literal(1.0));
PolygonSymbolizer sym = sf.createPolygonSymbolizer(stroke, fill, null);

Rule rule = sf.createRule();
rule.symbolizers().add(sym);

FeatureTypeStyle fts = sf.createFeatureTypeStyle(new Rule[]{rule});
Style style = sf.createStyle();
style.featureTypeStyles().add(fts);
```

---

