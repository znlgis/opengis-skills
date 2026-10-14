# GDAL Data Formats Reference

> 这是 [../SKILL.md](../SKILL.md) 的补充文件，收录 GDAL/OGR 常用矢量与栅格格式对照表。

---

## 矢量格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| Shapefile | .shp | ESRI 标准格式 |
| GeoJSON | .geojson | Web 标准 JSON |
| GeoPackage | .gpkg | SQLite 基础，推荐 |
| KML | .kml | Google Maps 格式 |
| PostGIS | N/A | 数据库矢量存储 |
| GML | .gml | ISO 标准 XML |
| CSV | .csv | 点数据 |
| DXF | .dxf | CAD 格式 |
| MapInfo | .tab | MapInfo 格式 |

## 栅格格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| GeoTIFF | .tif, .tiff | 标准地理栅格（推荐） |
| PNG | .png | Web 图像 |
| JPEG | .jpg, .jpeg | 有损压缩 |
| COG | .tif | 云优化 GeoTIFF |
| NetCDF | .nc | 科学数据 |
| HDF5 | .h5, .he5 | 多维数据 |
| ASCII Grid | .asc | 简单栅格（DEM） |
| JPEG2000 | .jp2 | 高质量压缩 |
| ECW | .ecw | ERDAS ECW 格式 |
