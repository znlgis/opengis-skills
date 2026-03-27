# GeoPipeAgent Steps Reference

Auto-generated reference of all available pipeline steps.

## analysis

### `analysis.cluster`

**空间聚类** — 对点数据进行空间聚类分析（支持 DBSCAN 和 KMeans）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入点矢量数据 |
| `method` | string | ❌ | dbscan | 聚类算法 (options: dbscan, kmeans) |
| `n_clusters` | number | ❌ | 5 | 簇数量（仅 KMeans 有效） |
| `eps` | number | ❌ | 0.5 | 邻域半径（仅 DBSCAN 有效） |
| `min_samples` | number | ❌ | 5 | 最小样本数（仅 DBSCAN 有效） |

**Outputs:**

- `output` (geodataframe): 带聚类标签的矢量数据

**Examples:**

- DBSCAN 聚类: `{'input': '$points.output', 'method': 'dbscan', 'eps': 0.1}`

---

### `analysis.heatmap`

**热力图** — 基于核密度估计（KDE）生成热力图栅格

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入点矢量数据 |
| `resolution` | number | ❌ | 100 | 输出栅格分辨率（像素数，宽度方向） |
| `bandwidth` | number | ❌ | — | 核函数带宽。不指定则自动估计 |

**Outputs:**

- `output` (raster_info): 热力图栅格数据

**Examples:**

- 生成犯罪热力图: `{'input': '$crimes.output', 'resolution': 200}`

---

### `analysis.interpolate`

**空间插值** — 将点数据插值为连续栅格表面（IDW 或 线性/最近邻/三次插值）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入点矢量数据 |
| `value_field` | string | ✅ | — | 用于插值的属性字段名 |
| `method` | string | ❌ | linear | 插值方法 (options: linear, nearest, cubic, idw) |
| `resolution` | number | ❌ | 100 | 输出栅格分辨率（像素数，宽度方向） |
| `power` | number | ❌ | 2 | IDW 距离幂次（仅 method=idw 时有效） |

**Outputs:**

- `output` (raster_info): 插值结果栅格

**Examples:**

- 线性插值温度数据: `{'input': '$stations.output', 'value_field': 'temperature', 'method': 'linear', 'resolution': 200}`

---

### `analysis.voronoi`

**泰森多边形** — 根据输入点数据生成泰森多边形（Voronoi图）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入点矢量数据 |
| `envelope` | geodataframe | ❌ | — | 裁剪边界（不指定则使用点的凸包缓冲区） |

**Outputs:**

- `output` (geodataframe): 泰森多边形矢量数据

**Examples:**

- 为气象站点生成泰森多边形: `{'input': '$stations.output'}`

---

## io

### `io.read_raster`

**读取栅格数据** — 从文件读取栅格数据（GeoTIFF 等），返回 rasterio DatasetReader 信息

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `path` | string | ✅ | — | 栅格数据文件路径 |

**Outputs:**

- `output` (raster_info): 栅格数据信息字典

**Examples:**

- 读取 GeoTIFF: `{'path': 'data/dem.tif'}`

---

### `io.read_vector`

**读取矢量数据** — 从文件读取矢量数据（Shapefile, GeoJSON, GPKG 等），返回 GeoDataFrame

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `path` | string | ✅ | — | 矢量数据文件路径 |
| `layer` | string | ❌ | — | 图层名称（多图层文件时使用） |
| `encoding` | string | ❌ | utf-8 | 文件编码 |

**Outputs:**

- `output` (geodataframe): 读取的矢量数据

**Examples:**

- 读取 Shapefile: `{'path': 'data/roads.shp'}`
- 读取 GeoJSON: `{'path': 'data/buildings.geojson'}`

---

### `io.write_raster`

**写入栅格数据** — 将栅格数据写入文件（GeoTIFF 等）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster_info | ✅ | — | 输入栅格数据（包含 data, profile 的字典） |
| `path` | string | ✅ | — | 输出文件路径 |

**Outputs:**

- `output` (string): 输出文件路径

**Examples:**

- 写入 GeoTIFF: `{'input': '$raster.output', 'path': 'output/result.tif'}`

---

### `io.write_vector`

**写入矢量数据** — 将矢量数据写入文件（GeoJSON, Shapefile, GPKG 等）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `path` | string | ✅ | — | 输出文件路径 |
| `format` | string | ❌ | GeoJSON | 输出格式 (GeoJSON, Shapefile, GPKG) |
| `encoding` | string | ❌ | utf-8 | 文件编码 |

**Outputs:**

- `output` (string): 输出文件路径

**Examples:**

- 输出为 GeoJSON: `{'input': '$buffer.output', 'path': 'output/result.geojson', 'format': 'GeoJSON'}`

---

## network

### `network.geocode`

**地理编码** — 将地址列表转换为地理坐标（使用 geopy 库）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `addresses` | list | ✅ | — | 地址列表 |
| `provider` | string | ❌ | nominatim | 地理编码服务提供商（nominatim, google 等） |
| `user_agent` | string | ❌ | geopipe-agent | HTTP User-Agent 标头（Nominatim 要求） |

**Outputs:**

- `output` (geodataframe): 地理编码结果（点数据）

**Examples:**

- 地理编码地址列表: `{'addresses': ['北京市天安门', '上海市外滩'], 'provider': 'nominatim'}`

---

### `network.service_area`

**服务区分析** — 计算网络中从给定点出发在指定成本内可达的服务区域

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入线矢量数据（道路/管线网络） |
| `center` | list | ✅ | — | 中心点坐标 [x, y] |
| `cost_limit` | number | ✅ | — | 最大行程成本（距离或时间） |
| `weight` | string | ❌ | — | 权重字段名。不指定则使用几何长度 |

**Outputs:**

- `output` (geodataframe): 服务区域（可达边线集合）

**Examples:**

- 计算 1000 米服务区: `{'input': '$roads.output', 'center': [116.4, 39.9], 'cost_limit': 1000}`

---

### `network.shortest_path`

**最短路径** — 在道路/管线网络中计算两点之间的最短路径

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入线矢量数据（道路/管线网络） |
| `origin` | list | ✅ | — | 起点坐标 [x, y] |
| `destination` | list | ✅ | — | 终点坐标 [x, y] |
| `weight` | string | ❌ | — | 权重字段名（如 'length'）。不指定则使用几何长度 |

**Outputs:**

- `output` (geodataframe): 最短路径矢量数据

**Examples:**

- 计算两点间最短路径: `{'input': '$roads.output', 'origin': [116.3, 39.9], 'destination': [116.5, 40.0]}`

---

## qc

### `qc.attribute_completeness`

**属性完整性检查** — 检查矢量数据的必填字段是否缺失或为空值

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `required_fields` | list | ✅ | — | 必填字段名列表 |
| `allow_empty` | boolean | ❌ | False | 是否允许空字符串（默认不允许） |
| `severity` | string | ❌ | warning | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (geodataframe): 透传的输入数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查建筑物必填属性: `{'input': '$buildings.output', 'required_fields': ['name', 'height', 'type']}`

---

### `qc.attribute_domain`

**属性值域检查** — 检查矢量数据中指定字段的值是否在允许的值域范围内（枚举列表或正则模式）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `field` | string | ✅ | — | 要检查的字段名 |
| `allowed_values` | list | ❌ | — | 允许的值列表（枚举方式） |
| `pattern` | string | ❌ | — | 允许的值正则表达式模式 |
| `severity` | string | ❌ | warning | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (geodataframe): 透传的输入数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查用地类型是否在允许范围内: `{'input': '$parcels.output', 'field': 'land_use', 'allowed_values': ['residential', 'commercial', 'industrial', 'green']}`

---

### `qc.crs_check`

**坐标参考系检查** — 验证矢量数据的坐标参考系是否正确、是否缺失

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `expected_crs` | string | ❌ | — | 期望的 CRS（如 'EPSG:4326'），不指定则仅检查 CRS 是否存在 |
| `severity` | string | ❌ | error | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (geodataframe): 透传的输入数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查数据 CRS 是否为 EPSG:4326: `{'input': '$data.output', 'expected_crs': 'EPSG:4326'}`

---

### `qc.duplicate_check`

**重复要素检查** — 检测矢量数据中几何或属性重复的要素

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `check_geometry` | boolean | ❌ | True | 是否检查几何重复 |
| `check_fields` | list | ❌ | — | 要检查重复的属性字段列表（不指定则不检查属性重复） |
| `tolerance` | number | ❌ | 0.0 | 几何比较容差 |
| `severity` | string | ❌ | warning | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (geodataframe): 透传的输入数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查几何和名称重复: `{'input': '$buildings.output', 'check_geometry': True, 'check_fields': ['name']}`

---

### `qc.geometry_validity`

**几何有效性检查** — 检查矢量数据的几何有效性，检测自相交、空几何、环方向错误等问题

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `auto_fix` | boolean | ❌ | False | 是否自动修复无效几何（buffer(0)） |
| `severity` | string | ❌ | error | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (geodataframe): 透传的输入数据（或修复后的数据）
- `issues` (list): 质检问题列表

**Examples:**

- 检查建筑物几何有效性: `{'input': '$buildings.output', 'auto_fix': False}`

---

### `qc.raster_nodata`

**NoData一致性检查** — 检查栅格数据的 NoData 值是否设置、NoData 像元比例是否异常

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster | ✅ | — | 输入栅格数据（dict: data, transform, crs, profile） |
| `expected_nodata` | number | ❌ | — | 期望的 NoData 值（不指定则仅检查是否设置了 NoData） |
| `max_nodata_ratio` | number | ❌ | 0.5 | 允许的最大 NoData 像元比例（0~1），超过此比例视为异常 |
| `severity` | string | ❌ | warning | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (raster): 透传的输入栅格数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查 DEM 的 NoData 设置: `{'input': '$dem.output', 'expected_nodata': -9999, 'max_nodata_ratio': 0.3}`

---

### `qc.raster_resolution`

**分辨率一致性检查** — 检查栅格数据的像元大小是否符合预期

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster | ✅ | — | 输入栅格数据（dict: data, transform, crs, profile） |
| `expected_x` | number | ✅ | — | 期望的 X 方向像元大小（绝对值） |
| `expected_y` | number | ✅ | — | 期望的 Y 方向像元大小（绝对值） |
| `tolerance` | number | ❌ | 0.0001 | 像元大小的允许偏差 |
| `severity` | string | ❌ | warning | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (raster): 透传的输入栅格数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查 DEM 分辨率为 30m: `{'input': '$dem.output', 'expected_x': 30, 'expected_y': 30, 'tolerance': 0.5}`

---

### `qc.raster_value_range`

**栅格值域检查** — 检查栅格数据像素值是否在预期范围内

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster | ✅ | — | 输入栅格数据（dict: data, transform, crs, profile） |
| `min` | number | ❌ | — | 允许的最小像素值（含），不指定则不检查下界 |
| `max` | number | ❌ | — | 允许的最大像素值（含），不指定则不检查上界 |
| `band` | integer | ❌ | 0 | 要检查的波段索引（0-based），默认检查第一个波段 |
| `severity` | string | ❌ | warning | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (raster): 透传的输入栅格数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查 NDVI 值在 -1 到 1 之间: `{'input': '$ndvi.output', 'min': -1, 'max': 1}`

---

### `qc.topology`

**拓扑关系检查** — 检查矢量数据的拓扑关系，检测缝隙(gaps)、重叠(overlaps)、悬挂线(dangles)等问题

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `rules` | list | ✅ | — | 要检查的拓扑规则列表: no_overlaps, no_gaps, no_dangles |
| `tolerance` | number | ❌ | 0.0 | 容差值（用于判定是否重叠/缝隙） |
| `severity` | string | ❌ | error | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (geodataframe): 透传的输入数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查地块数据无重叠: `{'input': '$parcels.output', 'rules': ['no_overlaps'], 'tolerance': 0.001}`

---

### `qc.value_range`

**数值范围检查** — 检查矢量数据中数值字段的值是否在指定的最小/最大范围内

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `field` | string | ✅ | — | 要检查的数值字段名 |
| `min` | number | ❌ | — | 允许的最小值（含），不指定则不检查下界 |
| `max` | number | ❌ | — | 允许的最大值（含），不指定则不检查上界 |
| `severity` | string | ❌ | warning | 问题严重级别 (options: error, warning, info) |

**Outputs:**

- `output` (geodataframe): 透传的输入数据
- `issues` (list): 质检问题列表

**Examples:**

- 检查建筑高度在合理范围内: `{'input': '$buildings.output', 'field': 'height', 'min': 0, 'max': 1000}`

---

## raster

### `raster.calc`

**栅格计算** — 对栅格波段执行数学运算（如 NDVI = (B4-B3)/(B4+B3)）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster_info | ✅ | — | 输入栅格数据 |
| `expression` | string | ✅ | — | 计算表达式，使用 B1, B2, ... 引用波段（如 '(B4-B3)/(B4+B3)'） |

**Outputs:**

- `output` (raster_info): 计算结果栅格

**Examples:**

- 计算 NDVI: `{'input': '$satellite.output', 'expression': '(B4-B3)/(B4+B3)'}`

---

### `raster.clip`

**栅格裁剪** — 使用矢量几何或边界框裁剪栅格数据

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster_info | ✅ | — | 输入栅格数据 |
| `mask` | geodataframe | ✅ | — | 裁剪掩膜（矢量数据） |
| `crop` | boolean | ❌ | True | 是否裁剪到掩膜范围 |
| `nodata` | number | ❌ | 0 | 无数据填充值 |

**Outputs:**

- `output` (raster_info): 裁剪后的栅格数据

**Examples:**

- 用矢量边界裁剪栅格: `{'input': '$dem.output', 'mask': '$boundary.output'}`

---

### `raster.contour`

**生成等值线** — 从栅格数据生成等值线矢量数据

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster_info | ✅ | — | 输入栅格数据 |
| `interval` | number | ✅ | — | 等值线间距 |
| `band` | number | ❌ | 1 | 波段编号（从1开始） |
| `base` | number | ❌ | 0 | 等值线基准值 |

**Outputs:**

- `output` (geodataframe): 等值线矢量数据

**Examples:**

- 每100米生成等高线: `{'input': '$dem.output', 'interval': 100}`

---

### `raster.reproject`

**栅格投影转换** — 将栅格数据从当前坐标参考系转换到目标坐标参考系

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster_info | ✅ | — | 输入栅格数据 |
| `target_crs` | string | ✅ | — | 目标坐标参考系（如 EPSG:4326, EPSG:3857） |
| `resampling` | string | ❌ | nearest | 重采样方法 (options: nearest, bilinear, cubic, lanczos) |

**Outputs:**

- `output` (raster_info): 转换后的栅格数据

**Examples:**

- 转换到 Web Mercator: `{'input': '$dem.output', 'target_crs': 'EPSG:3857'}`

---

### `raster.stats`

**栅格统计** — 计算栅格数据的统计信息（最小值、最大值、均值、标准差）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | raster_info | ✅ | — | 输入栅格数据 |
| `band` | number | ❌ | 1 | 波段编号（从1开始） |

**Outputs:**

- `output` (dict): 统计结果

**Examples:**

- 计算DEM第一波段统计: `{'input': '$dem.output', 'band': 1}`

---

## vector

### `vector.buffer`

**矢量缓冲区分析** — 对输入的矢量数据生成指定距离的缓冲区

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `distance` | number | ✅ | — | 缓冲区距离（单位取决于 CRS） |
| `cap_style` | string | ❌ | round | 端点样式 (options: round, flat, square) |

**Outputs:**

- `output` (geodataframe): 缓冲区结果
- `stats` (dict): 统计信息

**Examples:**

- 500米道路缓冲区: `{'input': '$roads.output', 'distance': 500}`

**Backends:** native_python, qgis_process

---

### `vector.clip`

**矢量裁剪** — 用裁剪范围裁剪输入矢量数据

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `clip_geometry` | geodataframe | ✅ | — | 裁剪范围（矢量数据） |

**Outputs:**

- `output` (geodataframe): 裁剪结果

**Examples:**

- 裁剪道路数据到研究区范围: `{'input': '$roads.output', 'clip_geometry': '$boundary.output'}`

**Backends:** native_python, qgis_process

---

### `vector.dissolve`

**矢量融合** — 将矢量要素按指定字段融合（合并几何）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `by` | string | ❌ | — | 分组字段名。不指定则全部融合 |
| `aggfunc` | string | ❌ | first | 属性聚合函数 (first, sum, mean, count 等) |

**Outputs:**

- `output` (geodataframe): 融合结果

**Examples:**

- 按类型字段融合: `{'input': '$data.output', 'by': 'type'}`

**Backends:** native_python

---

### `vector.overlay`

**矢量叠加分析** — 对两个矢量图层进行叠加分析（交集、并集、差集等）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `overlay_layer` | geodataframe | ✅ | — | 叠加图层 |
| `how` | string | ❌ | intersection | 叠加方式 (options: intersection, union, difference, symmetric_difference, identity) |

**Outputs:**

- `output` (geodataframe): 叠加分析结果

**Examples:**

- 两个图层求交集: `{'input': '$layer1.output', 'overlay_layer': '$layer2.output', 'how': 'intersection'}`

**Backends:** native_python

---

### `vector.query`

**矢量查询** — 按属性表达式查询/过滤矢量要素

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `expression` | string | ✅ | — | Pandas query 表达式（如 'population > 1000'） |

**Outputs:**

- `output` (geodataframe): 查询结果

**Examples:**

- 筛选人口大于1000的要素: `{'input': '$data.output', 'expression': 'population > 1000'}`

---

### `vector.reproject`

**矢量投影转换** — 将矢量数据从当前坐标参考系转换到目标坐标参考系

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `target_crs` | string | ✅ | — | 目标坐标参考系（如 EPSG:4326, EPSG:3857） |

**Outputs:**

- `output` (geodataframe): 转换后的矢量数据

**Examples:**

- 转换到 Web Mercator: `{'input': '$roads.output', 'target_crs': 'EPSG:3857'}`

**Backends:** native_python, qgis_process

---

### `vector.simplify`

**矢量简化** — 简化矢量几何（减少顶点数量）

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input` | geodataframe | ✅ | — | 输入矢量数据 |
| `tolerance` | number | ✅ | — | 简化容差（单位取决于 CRS） |
| `preserve_topology` | boolean | ❌ | True | 是否保持拓扑 |

**Outputs:**

- `output` (geodataframe): 简化后的矢量数据

**Examples:**

- 简化道路数据（容差100米）: `{'input': '$roads.output', 'tolerance': 100}`

**Backends:** native_python

---
