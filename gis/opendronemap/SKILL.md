---
name: opendronemap
description: "Use when turning drone/aerial imagery into orthophotos, DSM/DTM, point clouds or 3D Tiles with OpenDroneMap — odm CLI via docker run --project-path, --dsm --dtm --orthophoto-resolution --pc-quality --3d-tiles, WebODM 4.0.0 compose, /api/token-auth/ and /api/projects/{id}/tasks, pyodm Node('localhost',3000); also for 'odm_orthophoto.tif' outputs and out-of-memory failures."
license: MIT
metadata:
  category: gis
  tags: "photogrammetry, drone, orthophoto, point-cloud, dsm, dtm, 3d-tiles, webodm, docker, gis"
---

> **项目地址：** <https://github.com/OpenDroneMap/ODM>（CLI/引擎）、<https://github.com/OpenDroneMap/WebODM>（Web 平台）
>
> **官方文档：** <https://docs.opendronemap.org/>（ODM）· <https://docs.webodm.org/>（WebODM）
>
> **最新版本：** ODM **3.6.2**（2026-08-12，[GitHub Releases](https://github.com/OpenDroneMap/ODM/releases)；镜像 `opendronemap/odm:3.6.2`，2026-08-13 推送）；WebODM **4.0.0**（2026-11-05，[GitHub Releases](https://github.com/OpenDroneMap/WebODM/releases)；镜像 `webodm/webodm_webapp:4.0.0`，2026-11-04 推送）；NodeODM **3.6.2**（镜像 `opendronemap/nodeodm:3.6.2`）（截至 2026-11）
>
> **运行环境：** Docker（Linux 推荐，Windows 原生安装包亦可）；WebODM 4.0.0 栈为 Python 3.14、PostgreSQL 18、Valkey 9.1、Ubuntu 24.04
>
> **许可证：** AGPL-3.0（ODM 与 WebODM）
>
> **配套客户端：** PyODM 1.5.13（PyPI `pyodm`，通过 NodeODM REST API 提交任务）

## 概述

OpenDroneMap（ODM）是一套完全开源的无人机航空摄影测量流水线：给一个装满照片的目录，它输出带地理坐标的正射影像、数字表面模型、点云与纹理三维模型。它把 SfM 空三（OpenSfM）、稠密匹配（OpenMVS）、网格重建、纹理映射与地理配准串成一条可复现的命令行流水线，是商业航测软件（Pix4D、Metashape）之外成本最低的替代路线。

生态由四个组件构成，选择取决于你要「一次性出图」还是「长期运营一个出图平台」：

- **ODM（引擎/CLI）** — 真正干活的部分，一个 Docker 镜像 + 一组命令行参数，产物落在项目目录
- **NodeODM** — 把 ODM 包成 REST 任务队列服务（默认 3000 端口），可多机分布式
- **WebODM** — Django 前端：项目管理、任务队列、2D/3D 查看器、量测与 GCP 界面，底层通过 NodeODM 调度
- **PyODM** — Python 客户端，直接对 NodeODM API 编程，适合把航测接进已有系统

**与相邻技术的差异：** GDAL/PDAL 处理的是「已经有坐标的数据」，ODM 解决的是「只有照片，如何得到有坐标的数据」——它内部确实会调用 GDAL/PROJ 做地理配准与 GeoTIFF 写出，但入口是影像而非矢量/点云。

## 环境准备

### 方式一：Docker 跑 ODM CLI（推荐，最省事）

无需安装任何摄影测量依赖，镜像内已含 OpenSfM、OpenMVS、Entwine、PDAL、GDAL 等全部组件。目录约定是硬性的：项目目录下必须有一个名为 `images` 的子目录，否则流水线找不到输入。

```bash
# 目录结构：/datasets/<项目名>/images/*.jpg
docker run -ti --rm \
  -v /home/user/datasets:/datasets \
  opendronemap/odm \
  --project-path /datasets my_project
```

```powershell
# Windows PowerShell（路径用正斜杠，避免反斜杠被当转义）
docker run -ti --rm -v c:/Users/user/datasets:/datasets opendronemap/odm --project-path /datasets my_project
```

固定版本比追 latest 更可靠：把 `opendronemap/odm` 换成 `opendronemap/odm:3.6.2`。需要 GPU 加速 SIFT 特征提取时用 `opendronemap/odm:gpu`（或 `opendronemap/odm:3.6.2-gpu`）并加 `--gpus all`。

### 方式二：WebODM 平台（需要界面/多人协作时）

WebODM 4.0.0 官方仓库自带 `webodm.sh` 管理脚本，它会拉取 `webodm/webodm_webapp:4.0.0`、`webodm/webodm_db:18` 与 Valkey broker：

```bash
git clone https://github.com/OpenDroneMap/WebODM.git
cd WebODM

./webodm.sh start           # 默认 http://localhost:8000
./webodm.sh --port 8000 --hostname localhost start
./webodm.sh --gpu start     # Linux：挂 GPU 处理节点
```

```bash
./webodm.sh stop            # 停止容器
./webodm.sh down            # 停止并删除容器（数据卷保留）
./webodm.sh liveupdate      # 不停止服务地升级到最新发布
```

首次启动会创建管理员账号 `admin`（密码在控制台输出，或首次登录时设置）。`.env` 里的 `WO_PORT`（默认 8000）、`WO_HOST`、`WO_MEDIA_DIR`、`WO_DB_DIR` 决定端口与数据落盘位置，改完重启生效。

### 方式三：原生安装与 Python 客户端

- **Windows**：从 ODM Releases 下载 setup 安装包，打开 ODM Console 后执行 `run C:\path\to\project --dsm`，无需 Docker
- **PyODM 客户端**：`pip install -U pyodm`，用于对 NodeODM 编程提交任务

```bash
# 起一个本地 NodeODM 处理节点（默认 3000 端口）
docker run -ti -p 3000:3000 opendronemap/nodeodm:3.6.2
```

### 验证

```bash
docker run --rm opendronemap/odm:3.6.2 --version   # 打印 ODM 版本
curl -s http://localhost:3000/info                 # NodeODM 节点信息（version、queueCount、maxImages）
curl -s http://localhost:8000/api/                 # WebODM API 根（返回带 version 的 JSON）
```

## 核心命令

### ODM CLI 常用参数

```bash
docker run -ti --rm -v /datasets:/datasets opendronemap/odm:3.6.2 \
  --project-path /datasets my_project \
  --dsm \
  --orthophoto-resolution 2 \
  --pc-quality high
```

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `--project-path <path>` | 必填 | 项目父目录；每个子目录是一个数据集，内含 `images/` |
| `--dsm` / `--dtm` | 关闭 | 生成数字表面模型 / 数字地形模型（不传就**没有** DEM 产物） |
| `--orthophoto-resolution <float>` | 5 | 正射影像地面分辨率（cm/px），值越小越精细也越慢 |
| `--dem-resolution <float>` | 5 | DSM/DTM 分辨率（cm/px） |
| `--pc-quality <ultra|high|medium|low|lowest>` | medium | 点云质量，直接决定稠密匹配耗时 |
| `--feature-quality <...>` | high | 特征提取质量（SIFT） |
| `--fast-orthophoto` | 关闭 | 跳过稠密重建与三维模型，只出 2D 正射（航拍平地区域首选） |
| `--skip-3dmodel` | 关闭 | 保留点云与正射，但跳过纹理三维模型 |
| `--3d-tiles` | 关闭 | 额外输出 OGC 3D Tiles（`3d_tiles/`，供 Cesium 等加载） |
| `--cog` | 关闭 | 输出 Cloud-Optimized GeoTIFF 而非普通 GeoTIFF |
| `--auto-boundary` | 关闭 | 用相机航迹自动裁掉重建范围外的噪声 |
| `--gcp <path>` | 无 | 控制点文件，用于提升绝对精度 |
| `--geo <path>` | 无 | 手动指定影像地理定位（无 EXIF/GPS 时） |
| `--mesh-size <int>` | 200000 | 三维网格面数上限，越大越精细 |
| `--max-concurrency <int>` | CPU 核数 | 并行任务数，内存不足时调小 |
| `--rerun <stage>` | 无 | 只重跑指定阶段并停止（改参数重算时省时间） |
| `--copy-to <path>` | 无 | 处理完成后把结果目录复制到此路径 |

### 常用预设组合

```bash
# 1) 快速正射（应急出图、只做 2D）
docker run -ti --rm -v /datasets:/datasets opendronemap/odm:3.6.2 \
  --project-path /datasets my_project --fast-orthophoto --orthophoto-resolution 3

# 2) 标准测绘产物：正射 + DSM + DTM
docker run -ti --rm -v /datasets:/datasets opendronemap/odm:3.6.2 \
  --project-path /datasets my_project --dsm --dtm --cog --auto-boundary

# 3) 带三维与 3D Tiles（数字孪生/Web 发布）
docker run -ti --rm -v /datasets:/datasets opendronemap/odm:3.6.2 \
  --project-path /datasets my_project --dsm --3d-tiles --pc-quality high

# 4) 带控制点的高精度成果
docker run -ti --rm -v /datasets:/datasets opendronemap/odm:3.6.2 \
  --project-path /datasets my_project --gcp /datasets/my_project/gcp_list.txt --dsm --dtm
```

### 产物目录

ODM 把每个阶段的结果留在项目目录下，交付时按需取用：

```text
my_project/
├── images/                                  # 输入照片
├── opensfm/                                 # 空三：相机位姿与连接点
├── odm_georeferencing/
│   └── odm_georeferenced_model.laz          # 带坐标的点云（--pc-las 可出 .las）
├── odm_dem/
│   ├── dsm.tif                              # 仅 --dsm 时生成
│   └── dtm.tif                              # 仅 --dtm 时生成
├── odm_orthophoto/
│   ├── odm_orthophoto.tif                   # 正射影像 GeoTIFF
│   └── odm_orthophoto.original.tif          # 未裁切版本
├── odm_texturing/
│   ├── odm_textured_model.obj               # 纹理模型（局部坐标）
│   └── odm_textured_model_geo.obj           # 带地理坐标的纹理模型
├── odm_report/                              # 质量报告（PDF/HTML）
├── 3d_tiles/                                # 仅 --3d-tiles 时生成
├── orthophoto_tiles/  dsm_tiles/  dtm_tiles/ # --tiles 时生成的瓦片
└── entwine_pointcloud/                      # Entwine 点云索引（供 Potree 浏览）
```

> 交付前先确认 `odm_report/` 里的重叠度与重投影误差：重叠度不足或空三失败时，后面的正射与 DSM 即使生成也不可信。

### WebODM REST API

WebODM 的 API 与 ODM 引擎解耦，可用任意 HTTP 客户端驱动。认证走 JWT：

```bash
# 1) 换 token（返回 {"token": "..."}）
TOKEN=$(curl -s -X POST http://localhost:8000/api/token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<password>"}' | python -c "import json,sys;print(json.load(sys.stdin)['token'])")

# 2) 建项目 → 建任务（上传影像 zip 或逐张 multipart）
curl -s -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: JWT $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"my_project"}'

curl -s -X POST http://localhost:8000/api/projects/1/tasks/ \
  -H "Authorization: JWT $TOKEN" \
  -F "images=@images.zip" \
  -F "options={\"dsm\": true, \"orthophoto-resolution\": 2}"

# 3) 查任务状态（status: 10 排队 / 20 运行 / 30 失败 / 40 完成 / 50 取消）
curl -s http://localhost:8000/api/projects/1/tasks/1/ -H "Authorization: JWT $TOKEN"
```

成果通过固定路径取用：`/api/projects/{pid}/tasks/{tid}/orthophoto/tiles.json`（瓦片元数据）、`.../orthophoto/tiles/{z}/{x}/{y}.png`（瓦片）、`.../download/{asset}`（原始成果下载）、`.../assets/...`（单项资产）。把 `orthophoto` 换成 `dsm`、`dtm` 即可取高程瓦片，可直接喂给 Leaflet / OpenLayers / Cesium。

### PyODM：直接对 NodeODM 编程

```python
from pyodm import Node

node = Node("localhost", 3000)
task = node.create_task(
    ["images/1.jpg", "images/2.jpg"],
    {"dsm": True, "orthophoto-resolution": 2},
    name="demo",
)
task.wait_for_completion()          # 阻塞直到完成或失败
assets = task.download_assets("results")
print(assets)                        # 含 odm_orthophoto、odm_dem 等目录
```

## 典型工作流

### 工作流一：一段视频 / 一批照片 → 正射 + DSM 交付

**输入**：一次航飞的 JPG（带 GPS EXIF），或一段航拍视频抽帧后的图片序列。

1. **检查输入**：照片带 GPS 且覆盖率足够（航向重叠 ≥ 70%、旁向 ≥ 60%），删掉糊片与地面随手拍，否则空三会失败
2. **组织目录**：`/datasets/my_project/images/*.jpg`
3. **先跑快速版确认数据可用**：加 `--fast-orthophoto --orthophoto-resolution 5`，十几分钟就能看出空三是否成立
4. **再跑正式版**：`--dsm --dtm --cog --auto-boundary --pc-quality high`
5. **验收**：`odm_report/` 看重叠度与重投影误差，用 `gdalinfo` 核对正射影像的 CRS 与分辨率

```bash
# 第 5 步验收
gdalinfo -json /datasets/my_project/odm_orthophoto/odm_orthophoto.tif \
  | python -c "import json,sys;d=json.load(sys.stdin);print(d['size'], d['coordinateSystem']['wkt'][:60], d['geoTransform'])"
gdalinfo -stats /datasets/my_project/odm_dem/dsm.tif | grep -E 'Minimum|Maximum'
```

### 工作流二：成果入库并发布为 OGC 服务

ODM 的 GeoTIFF 与点云要真正「可用」，还需接进既有 GIS 栈：

1. **正射影像 → COG**（已是 `--cog` 时可跳过）：`gdal_translate -of COG odm_orthophoto.tif ortho_cog.tif`
2. **DSM/DTM → PostGIS 栅格**：`raster2pgsql -s <SRID> -I -C -M -t 256x256 dsm.tif public.dsm | psql -d gisdb`
3. **点云 → PDAL 清洗/重投影**：`pdal translate odm_georeferenced_model.laz clean.laz outlier` 再去分类与抽稀
4. **三维成果 → 3D Tiles 上云**：用 `--3d-tiles` 的 `3d_tiles/` 直接由 CesiumJS 加载

```bash
gdalinfo -json odm_dem/dsm.tif | python -c "import json,sys;print(json.load(sys.stdin)['coordinateSystem']['wkt'][:120])"
# 用上面的 SRID（或 EPSG 码）替换下面的 <SRID>
raster2pgsql -s <SRID> -I -C -M -t 256x256 odm_dem/dsm.tif public.dsm_gen | psql -d gisdb
```

### 工作流三：WebODM 平台化批量作业

**场景**：一个团队要反复出图，需要项目管理、权限与在线查看器。

1. `./webodm.sh start` 起平台，登录后先在「Processing Nodes」确认自带 ODM 节点在线
2. 建项目 → 上传影像 zip → 选质量预设（Default / High Resolution / Fast Orthophoto）→ 提交
3. 任务详情页看日志与进度；失败时读 `Task Output` 里的最后一段 Traceback
4. 出图后在 2D 查看器量距/量面，3D 查看器看纹理模型；成果用 `Download` 打包全部资产
5. 批量脚本化时改用 API（见上文 REST 小节）或 PyODM，不要靠点界面

### 工作流四：只重算某一阶段

改了某个参数不想从头跑（SfM 可能花掉一半时间）时，用 `--rerun` 指定阶段：

```bash
docker run -ti --rm -v /datasets:/datasets opendronemap/odm:3.6.2 \
  --project-path /datasets my_project --rerun odm_meshing --mesh-size 400000
```

## 常见问题

| 报错 / 现象 | 原因 | 处置 |
|------|------|------|
| `No images found in .../images` | 项目目录下没有 `images/` 子目录，或照片放在 `--project-path` 直下 | 严格按 `<project-path>/<dataset>/images/` 组织；`--project-path` 传父目录、末尾再跟数据集名 |
| 空三阶段失败、`Not enough images` / 大量未注册影像 | 重叠度不足、影像过糊、曝光差异过大，或照片缺少时间戳 | 提高航向/旁向重叠度重飞；删糊片；必要时加 `--matcher-type bruteforce` 或 `--feature-quality ultra` |
| 容器被 OOM killer 杀掉（退出码 137） | `--pc-quality ultra` 叠加高分辨率影像超出可用内存 | 降 `--pc-quality`、调小 `--max-concurrency`、加 `--split` 分块，或换更大内存机器 |
| 产物坐标在几千公里外 / 与底图对不上 | 影像 EXIF 的 GPS 有系统偏移，或缺 GCP | 用 `--gcp` 提供控制点；检查 EXIF 是否真的是 WGS84；`--gps-accuracy` 可放宽对 GPS 的信任 |
| 正射影像是空白 / 被裁成一条 | `--auto-boundary` 在影像不足时收缩过度，或空三只注册了少数影像 | 先去掉 `--auto-boundary` 看完整范围，再决定是否加回 |
| 没有 `dsm.tif` / `dtm.tif` | 没传 `--dsm` / `--dtm`，默认不生成 DEM | 明确加 `--dsm`、`--dtm`；只做 2D 的 `--fast-orthophoto` 也不产 DEM |
| `3d_tiles/` 目录不存在 | 没传 `--3d-tiles`，或该阶段被 `--rerun`/`--end-with` 提前截断 | 加 `--3d-tiles` 并确认 `--end-with` 未停在 `odm_postprocess` 之前 |
| Windows 下 `-v c:\data:/datasets` 挂载失败 | 反斜杠被 shell 转义，或 Docker Desktop 未共享该盘 | 用 `c:/data:/datasets` 正斜杠；在 Docker Desktop 里共享对应盘符 |
| WebODM 上传后任务一直排队 | 没有可用的 Processing Node，或节点已被占用 | 在 Processing Nodes 页面确认节点是绿色在线；`docker logs` 看 nodeodm 容器 |
| WebODM 接口返回 401 | 用了 Basic Auth 而非 JWT，或 token 过期 | 先 `POST /api/token-auth/` 取 token，请求头写 `Authorization: JWT <token>`，过期用 `/api/token-auth/refresh/` 换新 |

## AI 使用建议

- **先判断产物需求**：只要正射就用 `--fast-orthophoto`（快数倍）；要 DEM 必须显式加 `--dsm`/`--dtm`；要 Web 三维再加 `--3d-tiles`。不要默认把所有开关都打开——三维与超高质点云是主要耗时来源。
- **先探环境再动手**：`docker --version`、`docker run --rm opendronemap/odm:3.6.2 --version`；宿主机内存与磁盘要先确认（中间文件常达原图数倍），磁盘不足会在纹理阶段失败得很难看。
- **先快速跑通再上正式参数**：用 3–5 张照片或 `--fast-orthophoto` 跑一次端到端，确认挂载路径与目录结构正确，再换成正式参数，避免跑几小时后才发现 `images/` 放错位置。
- **验证产物而不是只看退出码**：`odm_orthophoto/odm_orthophoto.tif` 用 `gdalinfo` 核对 CRS/尺寸；`odm_dem/*.tif` 用 `-stats` 看高程范围是否合理；点云用 PDAL `info` 看点数与 SRS；`odm_report/` 的重投影误差是质量判据。
- **失败信号优先级**：容器退出码 137 是 OOM（先降 `--pc-quality`）；空三失败几乎都是数据问题（重叠度、糊片、GPS），改参数救不回来；WebODM 任务卡住先查 Processing Node 而不是重装平台。
- **版本与可复现**：把镜像标签写死为 `opendronemap/odm:3.6.2` / `webodm/webodm_webapp:4.0.0`，不要只用 `latest`；不同 ODM 版本的默认参数与产物目录结构会变，复现旧项目时记录版本号。
- **安全与权限**：WebODM 的 `admin` 凭据、`WO_SECRET_KEY`、JWT token 不要写进脚本或回显到报告；`./webodm.sh down`、删项目、`--rerun` 覆盖已有产物均不可逆，执行前向用户确认；无人机影像可能涉及测绘资质与隐私，外传前确认合规。

## 相关技能

- **pdal** — 点云清洗、分类与重投影，处理 ODM 输出的 `.laz`：[../pdal/SKILL.md](../pdal/SKILL.md)
- **gdal** — 正射影像/DSM 的 COG 转换、裁剪与栅格入库：[../gdal/SKILL.md](../gdal/SKILL.md)
- **cesiumjs** — 加载 `--3d-tiles` 产出的 OGC 3D Tiles 做 Web 三维发布：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)
- **postgis** — DSM/DTM 与矢量成果入库、空间查询与瓦片服务：[../postgis/SKILL.md](../postgis/SKILL.md)

## 参考资源

- **ODM 官方文档：** <https://docs.opendronemap.org/> | [全部参数](https://docs.opendronemap.org/arguments/) | [产出说明](https://docs.opendronemap.org/outputs/) | [安装](https://docs.opendronemap.org/installation/)
- **WebODM 文档：** <https://docs.webodm.org/> | [API Quickstart](https://docs.webodm.org/api/quickstart/) | [认证](https://docs.webodm.org/api/authentication/)
- **PyODM 文档：** <https://pyodm.readthedocs.io/>
- **源码：** [ODM](https://github.com/OpenDroneMap/ODM) | [WebODM](https://github.com/OpenDroneMap/WebODM) | [NodeODM](https://github.com/OpenDroneMap/NodeODM) | [pyodm](https://github.com/OpenDroneMap/pyodm)
- **GCP 与控制点：** <https://docs.opendronemap.org/gcp/>
- **镜像：** [opendronemap/odm](https://hub.docker.com/r/opendronemap/odm) | [opendronemap/nodeodm](https://hub.docker.com/r/opendronemap/nodeodm) | [webodm/webodm_webapp](https://hub.docker.com/r/webodm/webodm_webapp)
- **社区论坛：** <https://community.opendronemap.org/>
