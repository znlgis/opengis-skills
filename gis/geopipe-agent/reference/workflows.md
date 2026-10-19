# GeoPipeAgent 典型工作流（可套用 YAML）

### 工作流 1：数据质检 + 修复流水线

```yaml
pipeline:
  name: "数据质检修复"
  steps:
    - id: read
      use: io.read_vector
      params:
        path: "data/buildings.shp"

    # 第一步：检查几何有效性
    - id: check_valid
      use: qc.geometry_validity
      params:
        input: "$read"
        severity: error

    # 第二步：条件修复（仅当发现问题时执行）
    - id: fix_valid
      use: qc.geometry_validity
      params:
        input: "$check_valid"
        auto_fix: true
      when: "$check_valid.issues_count > 0"

    # 第三步：属性完整性检查
    - id: check_attr
      use: qc.attribute_completeness
      params:
        input: "$fix_valid"
        required_fields: ["name", "height", "type"]
        severity: warning

    # 第四步：写入结果
    - id: save
      use: io.write_vector
      params:
        input: "$check_attr"
        path: "output/buildings_checked.gpkg"
        format: GPKG

  outputs:
    result: "$save"
    issues: "$check_attr.issues"
```

### 工作流 2：缓冲区 + 叠加分析

```yaml
pipeline:
  name: "道路影响范围分析"
  steps:
    - id: roads
      use: io.read_vector
      params:
        path: "data/roads.shp"
    - id: parcels
      use: io.read_vector
      params:
        path: "data/parcels.shp"

    # 500 米道路缓冲区
    - id: buffer
      use: vector.buffer
      params:
        input: "$roads"
        distance: 500

    # 缓冲区与地块求交集
    - id: overlay
      use: vector.overlay
      params:
        input: "$parcels"
        overlay_layer: "$buffer"
        how: intersection

    - id: save
      use: io.write_vector
      params:
        input: "$overlay"
        path: "output/affected_parcels.geojson"

  outputs:
    result: "$save"
```

### 工作流 3：DEM 分析 + 等值线

```yaml
pipeline:
  name: "DEM 地形分析"
  steps:
    - id: read_dem
      use: io.read_raster
      params:
        path: "data/dem.tif"

    # 栅格 QC：检查 NoData 和分辨率
    - id: check_nodata
      use: qc.raster_nodata
      params:
        input: "$read_dem"
        max_nodata_ratio: 0.1

    - id: check_resolution
      use: qc.raster_resolution
      params:
        input: "$check_nodata"
        expected_x: 30
        expected_y: 30

    # 生成等高线（50 米间距）
    - id: contour
      use: raster.contour
      params:
        input: "$check_resolution"
        interval: 50

    # 输出矢量等值线
    - id: save_contour
      use: io.write_vector
      params:
        input: "$contour"
        path: "output/contours_50m.gpkg"
        format: GPKG

  outputs:
    contour: "$save_contour"
```

### 工作流 4：网络分析

```yaml
pipeline:
  name: "紧急响应路径分析"
  steps:
    - id: roads
      use: io.read_vector
      params:
        path: "data/road_network.shp"

    # 最短路径
    - id: route
      use: network.shortest_path
      params:
        input: "$roads"
        origin: [116.3, 39.9]
        destination: [116.5, 40.0]

    # 服务区（5000 米）
    - id: service
      use: network.service_area
      params:
        input: "$roads"
        center: [116.4, 39.95]
        cost_limit: 5000

    - id: save_route
      use: io.write_vector
      params:
        input: "$route"
        path: "output/route.geojson"

    - id: save_service
      use: io.write_vector
      params:
        input: "$service"
        path: "output/service_area.geojson"

  outputs:
    route: "$save_route"
    service_area: "$save_service"
```

### 工作流 5：空间聚类 + 热力图

```yaml
pipeline:
  name: "犯罪热点分析"
  steps:
    - id: points
      use: io.read_vector
      params:
        path: "data/crime_points.shp"

    # DBSCAN 聚类
    - id: cluster
      use: analysis.cluster
      params:
        input: "$points"
        method: dbscan
        eps: 0.01
        min_samples: 3

    # 热力图
    - id: heatmap
      use: analysis.heatmap
      params:
        input: "$points"
        resolution: 200

    - id: save_clusters
      use: io.write_vector
      params:
        input: "$cluster"
        path: "output/clusters.geojson"

    - id: save_heatmap
      use: io.write_raster
      params:
        input: "$heatmap"
        path: "output/heatmap.tif"

  outputs:
    clusters: "$save_clusters"
    heatmap: "$save_heatmap"
```
