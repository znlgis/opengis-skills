---
name: open3d
description: "Use when processing 3D point clouds and meshes in Python — read/write PLY/PCD, voxel downsample, normal estimation, outlier removal, RANSAC + ICP registration, Poisson surface reconstruction, quadric decimation, and headless/offscreen visualization. Open3D is Intel's open-source 3D data processing library with a C++ core and Python API."
tags:
  - 3d
  - point-cloud
  - mesh
  - registration
  - reconstruction
  - visualization
  - python
  - cpp
  - computer-vision
---

> **项目地址：** <https://github.com/isl-org/Open3D>
>
> **官方文档：** <https://www.open3d.org/docs/> ｜ **Python API：** <https://www.open3d.org/docs/release/python_api/>
>
> **许可证：** MIT ｜ **最新版本：** `v0.20.0`（PyPI `open3d` 与 GitHub Releases 双核实）｜ **默认分支：** `main`

## 概述

Open3D 是由 Intel 开源（组织 `isl-org`）的现代 3D 数据处理库，采用 C++ 内核并提供等价的 Python 与 C++ 接口，覆盖点云、网格、体素与 RGB-D 数据的完整处理链路。它以「一套数据结构 + 一套算法」把 IO、滤波、配准、重建、可视化串联起来，是学术与工程界处理三维数据的事实标准之一。

- **点云**：读写、体素/均匀下采样、法线估计、统计与半径离群点移除、平面分割、DBSCAN 聚类、裁剪。
- **配准**：粗配准（RANSAC / Fast Global Registration + FPFH 特征）与精配准（ICP，点到点 / 点到面）。
- **网格**：表面重建（泊松、Ball Pivoting、Alpha Shape）、二次误差简化、法线计算、平滑与拓扑修复。
- **可视化**：`draw_geometries` 快速查看、`O3DVisualizer` 可编程 GUI、`OffscreenRenderer` 无头渲染与截图。
- **生态**：与 NumPy 零拷贝互操作；张量后端与几何深度学习算子；覆盖桌面、服务器与传感器（RealSense）场景。

---

## 环境准备

### 安装

```bash
# 需要 Python >= 3.10（PyPI 元数据 requires_python）
pip install open3d

# 升级到最新版本
pip install --upgrade open3d
```

官方为 Linux / macOS / Windows 提供预编译 wheel，通常无需自行编译 C++ 内核。

### 验证安装

```bash
python -c "import open3d as o3d; print(o3d.__version__)"
# 预期输出：0.20.0
```

### 运行环境说明

- **桌面可视化**（`draw_geometries`）需要 OpenGL / GLFW 图形环境，在本地桌面可直接使用。
- **无头服务器**（CI、容器）请改用离屏渲染接口 `o3d.visualization.rendering.OffscreenRenderer`，不要调用需要窗口的 GUI 接口。
- 官方文档的稳定版位于 `https://www.open3d.org/docs/release/`，版本号可能滞后于 PyPI 发布。

---

## 核心 API 速览

以下函数名与签名均以官方 Python API 文档为准。

### 点云 IO 与格式支持

| 函数 | 说明 |
|------|------|
| `o3d.io.read_point_cloud(path)` | 按扩展名解码读取点云 |
| `o3d.io.write_point_cloud(path, pcd)` | 按扩展名写出点云 |
| `o3d.io.read_triangle_mesh(path)` / `write_triangle_mesh` | 读取/写出三角网格 |

点云支持格式（官方 File IO）：`xyz`、`xyzn`、`xyzrgb`、`pts`、`ply`、`pcd`。
网格支持格式：`ply`、`stl`、`obj`、`off`、`gltf` / `glb`。

> **LAS / LAZ 不在 Open3D 原生支持范围内**：需先用 PDAL、laspy 或 CloudCompare 转为 `ply` / `pcd` 再读入（见 FAQ）。

### 点云基础操作

| 方法 | 签名要点 | 用途 |
|------|----------|------|
| `voxel_down_sample(voxel_size)` | 体素边长 | 均匀降采样，保持几何分布 |
| `uniform_down_sample(every_k_points)` | 每 k 个点取一个 | 快速抽稀 |
| `estimate_normals(search_param, fast_normal_computation=True)` | `KDTreeSearchParamHybrid(radius, max_nn)` | 估计法线 |
| `remove_statistical_outlier(nb_neighbors, std_ratio)` | 返回 `(pcd, indices)` | 统计离群点移除 |
| `remove_radius_outlier(nb_points, radius)` | 返回 `(pcd, indices)` | 半径离群点移除 |
| `segment_plane(distance_threshold, ransac_n, num_iterations)` | RANSAC | 平面分割（地面/桌面） |
| `cluster_dbscan(eps, min_points)` | 返回标签数组 | 欧氏聚类分簇 |
| `compute_point_cloud_distance(target)` | 返回距离向量 | 点到点云的距离/误差 |
| `paint_uniform_color(color)` / `transform(T)` | 颜色、4×4 变换 | 着色、位姿变换 |

### NumPy 集成

`points` / `normals` / `colors` 均为 `Vector3dVector`，可与 NumPy 零拷贝互转：

```python
import numpy as np
import open3d as o3d

pcd = o3d.io.read_point_cloud("input.ply")
pts = np.asarray(pcd.points)                      # (N, 3) float64
colors = np.random.rand(len(pts), 3)
pcd.colors = o3d.utility.Vector3dVector(colors)   # 回写
pcd.points = o3d.utility.Vector3dVector(pts * 0.001)  # 例如 mm -> m
```

### 配准（registration）

| 名称 | 说明 |
|------|------|
| `o3d.pipelines.registration.registration_icp(source, target, threshold, init, estimation, criteria)` | 精配准 ICP |
| `TransformationEstimationPointToPoint(with_scaling=False)` | 点到点误差 |
| `TransformationEstimationPointToPlane()` | 点到面误差（需法线） |
| `ICPConvergenceCriteria(max_iteration=...)` | 迭代收敛条件 |
| `evaluate_registration(source, target, threshold, transform)` | 评估配准质量（fitness / inlier_rmse） |
| `compute_fpfh_feature(pcd, search_param)` | 计算 33 维 FPFH 特征 |
| `registration_ransac_based_on_feature_matching(...)` | 基于特征的 RANSAC 粗配准 |
| `CorrespondenceCheckerBasedOnEdgeLength / OnDistance / OnNormal` | 对应关系校验器 |
| `RANSACConvergenceCriteria(max_iteration, confidence)` | RANSAC 收敛条件 |

### 网格重建与处理

| 名称 | 说明 |
|------|------|
| `TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)` | 泊松重建，返回 `(mesh, densities)` |
| `TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, radii)` | Ball Pivoting，需法线 |
| `TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)` | Alpha Shape，需调 `alpha` |
| `orient_normals_consistent_tangent_plane(k)` | 法线一致化（泊松前必做） |
| `simplify_quadric_decimation(target_number_of_triangles=...)` | 二次误差简化 |
| `compute_vertex_normals()` / `compute_triangle_normals()` | 计算法线 |
| `remove_vertices_by_mask(mask)` | 按掩码删除顶点（如剔除低密度区） |

### 可视化

| 名称 | 说明 |
|------|------|
| `o3d.visualization.draw_geometries([geo, ...])` | 快速查看，支持 `zoom/front/lookat/up`、`point_show_normal` |
| `o3d.visualization.O3DVisualizer` | 可编程 GUI（`add_geometry`、`show`），适合自定义交互 |
| `o3d.visualization.rendering.OffscreenRenderer(width, height)` | 无头离屏渲染；`setup_camera` + `render_to_image` / `render_to_depth_image` |

---

## 典型工作流

### 工作流一：点云基础操作链（读取 → 滤波 → 下采样 → 法线）

```python
import open3d as o3d

pcd = o3d.io.read_point_cloud("raw.ply")

# 1. 统计离群点移除（去噪）
pcd, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

# 2. 体素下采样，统一密度
down = pcd.voxel_down_sample(voxel_size=0.02)

# 3. 估计并一致化法线
down.estimate_normals(
    o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
down.orient_normals_consistent_tangent_plane(100)

o3d.io.write_point_cloud("clean.ply", down)
o3d.visualization.draw_geometries([down], point_show_normal=True)
```

### 工作流二：粗配准 RANSAC + 精配准 ICP

```python
import copy
import numpy as np
import open3d as o3d

source = o3d.io.read_point_cloud("scan_a.pcd")
target = o3d.io.read_point_cloud("scan_b.pcd")
voxel_size = 0.05

def preprocess(pcd):
    d = pcd.voxel_down_sample(voxel_size)
    d.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30))
    fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        d, o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 5, max_nn=100))
    return d, fpfh

src_down, src_fpfh = preprocess(source)
tgt_down, tgt_fpfh = preprocess(target)

# 粗配准：RANSAC + FPFH
dist = voxel_size * 1.5
result_ransac = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
    src_down, tgt_down, src_fpfh, tgt_fpfh, True, dist,
    o3d.pipelines.registration.TransformationEstimationPointToPoint(False), 3,
    [o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
     o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(dist)],
    o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))

# 精配准：ICP（点到面），用粗配准结果作为初值
result_icp = o3d.pipelines.registration.registration_icp(
    source, target, voxel_size * 0.4, result_ransac.transformation,
    o3d.pipelines.registration.TransformationEstimationPointToPlane())

print(result_icp.fitness, result_icp.inlier_rmse)

# 评估并可视化
eval_ = o3d.pipelines.registration.evaluate_registration(
    source, target, voxel_size * 0.4, result_icp.transformation)
src_tmp = copy.deepcopy(source).transform(result_icp.transformation)
o3d.visualization.draw_geometries([src_tmp, target])
```

### 工作流三：网格重建（泊松 + 裁剪 + 简化）

```python
import numpy as np
import open3d as o3d

pcd = o3d.io.read_point_cloud("clean.ply")
pcd.estimate_normals(
    o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
pcd.orient_normals_consistent_tangent_plane(100)

# 泊松重建：depth 越大细节越多、越慢
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)

# 剔除低密度区域（重建产生的伪面）
densities = np.asarray(densities)
mesh.remove_vertices_by_mask(densities < np.quantile(densities, 0.01))

# 二次误差简化，控制三角形数量
mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=20000)
mesh.compute_vertex_normals()
o3d.io.write_triangle_mesh("recon.glb", mesh)
```

### 工作流四：可视化与无头截图

```python
import open3d as o3d

mesh = o3d.io.read_triangle_mesh("recon.glb")

# 本地桌面：交互查看
o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True)

# 无头服务器：离屏渲染成图像
renderer = o3d.visualization.rendering.OffscreenRenderer(1024, 768)
renderer.scene.add_geometry("mesh", mesh,
    o3d.visualization.rendering.MaterialRecord())
renderer.setup_camera(60.0, mesh.get_center(), [0, 0, 3], [0, 0, 1])
image = renderer.render_to_image()
o3d.io.write_image("screenshot.png", image)
```

### 工作流五：与高斯泼溅（3DGS）的上下游关系

Open3D 处理的是**有序/无序几何点集**（位置 + 可选法线/颜色），而 3DGS 的 `.ply` 存的是高斯基元（位置 + 协方差/缩放旋转 + 不透明度 + 球谐系数），两者数据布局不同，**不能直接用 `read_point_cloud` 当作普通点云读取**。

- **上游（Open3D → 3DGS）**：用 Open3D 清洗 COLMAP 稀疏点云、配准多视点云、估计法线、裁剪感兴趣区域，产出更干净的点云再送入 3DGS 训练。
- **下游（3DGS → 几何）**：从 3DGS 渲染深度/多视图像后，用 Open3D 做 TSDF/泊松重建得到可编辑网格。
- **可视化侧**：高斯模型请在浏览器/专用查看器处理，见 [supersplat](../supersplat/SKILL.md)；Open3D 只负责几何点云与网格。

---

## 最佳实践

- **下采样先行**：任何重算法（法线、FPFH、ICP、泊松）前先 `voxel_down_sample`，既提速又稳定。
- **法线是重建的前提**：泊松与 Ball Pivoting 都依赖法线，务必先 `estimate_normals` 再 `orient_normals_consistent_tangent_plane`。
- **ICP 需要好初值**：直接对未知位姿的扫描做 ICP 易陷入局部最优；先用 RANSAC/FGR 粗配准，再用点到面 ICP 精修。
- **阈值随尺度走**：配准距离阈值常取 `voxel_size * 1.5`（粗）与 `voxel_size * 0.4`（精），重建/滤波参数也应按点云尺度设定，而非固定常量。
- **离群点用两级策略**：`remove_statistical_outlier` 去稀疏噪声，`remove_radius_outlier` 去孤立簇，按数据特征选用。
- **无头环境别调 GUI**：服务器/CI 使用 `OffscreenRenderer`，避免 `draw_geometries` 因缺少 GLFW/OpenGL 报错。
- **大点云注意内存**：`np.asarray` 是视图（零拷贝），但 `Vector3dVector` 回写会拷贝；处理千万级点云时优先用下采样后的副本。

---

## 常见问题（FAQ）

| 问题 | 解决 |
|------|------|
| `pip install open3d` 失败 / 找不到 wheel | 确认 Python ≥ 3.10 且为 64 位；换用 `pip install --upgrade pip` 后重试；必要时指定平台 wheel |
| `import open3d` 报 GLIBCXX / 动态库错误 | Linux 上多为系统 libstdc++ 过旧，升级系统库或改用官方兼容 wheel；勿混装多版本 Open3D |
| `draw_geometries` 报错、闪退或无窗口 | 无头/容器环境缺少 OpenGL/GLFW；改用 `OffscreenRenderer` 离屏渲染，或安装 Xvfb/EGL 支持 |
| 读取 LAS / LAZ 失败 | Open3D 原生不支持 LAS/LAZ；先用 PDAL / laspy / CloudCompare 转为 `ply` 或 `pcd` 再读 |
| `write_point_cloud` 写出没有颜色 | 确认已设置 `pcd.colors`，且目标格式（如 `xyz`）本身不支持颜色；改用 `ply` / `pcd` |
| 泊松重建结果有大量飞面/破洞 | 法线未一致化或点云噪声大：先 `orient_normals_consistent_tangent_plane`，并用 `remove_vertices_by_mask(densities < 分位数)` 裁剪低密度区 |
| ICP 配准结果发散 / 不收敛 | 初值太差：先做 RANSAC 粗配准；或降低距离阈值、改用点到面估计并确保目标点云有法线 |
| 点云单位/尺度不对 | 读入后按需缩放：`pcd.points = o3d.utility.Vector3dVector(np.asarray(pcd.points) * 0.001)` |
| 无法把 3DGS 的 `.ply` 当点云读 | 高斯 `.ply` 含缩放/旋转/不透明度/球谐，非标准点云；请用 SuperSplat 等 3DGS 工具处理 |

---

## 参考资源

- 官方文档（稳定版）：<https://www.open3d.org/docs/release/>
- Python API 索引：<https://www.open3d.org/docs/release/python_api/>
- 点云教程：<https://www.open3d.org/docs/release/tutorial/geometry/pointcloud.html>
- 表面重建教程：<https://www.open3d.org/docs/release/tutorial/geometry/surface_reconstruction.html>
- 配准教程（ICP / 全局配准）：<https://www.open3d.org/docs/release/tutorial/pipelines/icp_registration.html>
- 可视化教程：<https://www.open3d.org/docs/release/tutorial/visualization/visualization.html>
- 源码仓库：<https://github.com/isl-org/Open3D>

---

## 相关技能

- **supersplat** — 浏览器端 3D 高斯泼溅（3DGS）编辑与发布，处理 Open3D 无法读取的高斯 `.ply`：[../supersplat/SKILL.md](../supersplat/SKILL.md)
- **ara3d-sdk** — .NET 高性能网格/BIM 处理，与 Open3D 的网格管线互补：[../ara3d-sdk/SKILL.md](../ara3d-sdk/SKILL.md)
- **photo-sphere-viewer** — Web 360° 全景查看器，展示三维重建成果的另一条路线：[../photo-sphere-viewer/SKILL.md](../photo-sphere-viewer/SKILL.md)
- **elements** — 纯 C# 编程生成建筑构件，可与 Open3D 网格互转：[../elements/SKILL.md](../elements/SKILL.md)

---

## AI 使用建议

- 用户提到「点云处理」「PLY/PCD 读写」「点云配准」「ICP / RANSAC」「泊松重建」「网格简化」「Open3D 可视化」时加载本技能。
- 区分三条主线：**点云操作链**（读取→滤波→下采样→法线）、**配准**（RANSAC 粗 + ICP 精）、**网格重建**（法线一致化 → 泊松 → 简化）。
- 一切重算法前先下采样；重建前必须先估计并一致化法线——这两点是排查结果异常的首要检查项。
- 配准参数随点云尺度设定（阈值取 `voxel_size` 的倍数），不要硬编码固定数值。
- 无头/服务器场景一律用 `OffscreenRenderer`，不要建议 `draw_geometries`。
- **不要臆造**：Open3D 原生不支持 LAS/LAZ 与 3DGS 高斯 `.ply`；点云 IO 只有 `xyz/xyzn/xyzrgb/pts/ply/pcd`，网格 IO 为 `ply/stl/obj/off/gltf/glb`，函数名以官方 Python API 文档为准。
