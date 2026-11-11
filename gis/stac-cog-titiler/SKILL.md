---
name: stac-cog-titiler
description: "Use when building cloud-native imagery pipelines with STAC 1.1.0, Cloud Optimized GeoTIFF and TiTiler 2.4.0 — rio cogeo create/validate, pystac-client search, stac-fastapi 7.1.1 with stac-fastapi-pgstac 7.2.1, uvicorn stac_fastapi.pgstac.app:app, titiler.application /cog and /stac tilejson endpoints, MosaicJSON mosaics, or debugging HTTP 416 range errors, blank tiles from band index mismatch and 403 on private object storage."
license: MIT
metadata:
  category: gis
  tags: "stac, cog, titiler, raster, cloud-native, geotiff, fastapi, object-storage, mosaicjson, imagery"
---

> **项目地址：**
>
> - STAC 规范：<https://github.com/radiantearth/stac-spec>（STAC API 规范：<https://github.com/radiantearth/stac-api-spec>）
> - stac-fastapi：<https://github.com/stac-utils/stac-fastapi>（PostgreSQL 后端 <https://github.com/stac-utils/stac-fastapi-pgstac>）
> - pgstac：<https://github.com/stac-utils/pgstac>
> - COG 规范：<https://github.com/cogeotiff/cog-spec>；rio-cogeo：<https://github.com/cogeotiff/rio-cogeo>
> - TiTiler：<https://github.com/developmentseed/titiler>
>
> **官方文档：** <https://stacspec.org/> / <https://stac-utils.github.io/stac-fastapi/> / <https://cogeotiff.github.io/rio-cogeo/> / <https://developmentseed.org/titiler/>
>
> **最新版本：** STAC 1.1.0（2024-09）、STAC API 1.0.0；stac-fastapi 7.1.1、stac-fastapi-pgstac 7.2.1、pgstac v0.10.1；rio-cogeo 7.0.4、cogeo-mosaic 9.2.0；titiler.core / titiler.application 2.4.0、titiler-pgstac 3.2.0；pystac 1.16.0、pystac-client 0.9.1（截至 2026-11，逐个实测 PyPI 与 [GitHub Releases](https://github.com/stac-utils/stac-fastapi/releases)、[TiTiler Releases](https://github.com/developmentseed/titiler/releases)）
>
> **许可证：** STAC 规范 Apache-2.0；stac-fastapi / pgstac / TiTiler / rio-cogeo / pystac 均 MIT

## 概述

这条链路解决的是「影像不下载、按需出图」：原始影像转成 **COG**（云优化 GeoTIFF，带内部分块与金字塔，支持 HTTP Range 随机读）放到对象存储，用 **STAC** 元数据把资产编目成可检索的条目，再交给 **TiTiler** 按瓦片请求动态读窗口、重采样、配色并输出 PNG/JPEG。三者各自独立，组合起来才能做到入库即服务。

- **STAC**：Item/Collection/Catalog 三层 JSON 元数据模型，统一描述时空范围与资产链接，跨厂商可交换
- **COG**：内部按 512×512 分块、带 overview 金字塔、头部元数据在前，服务端只需几次 Range 请求就能取到任意窗口
- **stac-fastapi + pgstac**：STAC API 的 Python 实现，pgstac 把 JSONB 条目与空间索引放进 PostGIS，支持 CQL2 过滤与分页
- **TiTiler**：基于 FastAPI + rio-tiler 的动态切片服务，`/cog` 直接对单个 COG 出图，`/stac` 对 STAC Item 的资产出图，`/mosaicjson` 把多景拼成虚拟镶嵌
- **零预处理出图**：换波段组合、拉伸方式、色带、重采样都通过 URL 查询参数完成，不用重跑切片任务
- **标准接口**：OGC Tiles / WMTS 兼容端点，可直接作为 OpenLayers、MapLibre、Leaflet 的瓦片源

与相邻技术的差异：传统方案是 GeoServer + ImageMosaic 预先切片，改样式要重切片；本方案把「切片」推迟到请求时，样式灵活但依赖对象存储的 Range 性能与 CDN。

---

## 环境准备

### Python 依赖

本链路是纯 Python 生态，要求 **Python >= 3.11**（stac-fastapi、rio-cogeo、TiTiler 2.x 均要求 3.11+）。

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install "rio-cogeo==7.0.4" "pystac==1.16.0" "pystac-client==0.9.1"
python -m pip install "stac-fastapi.api==7.1.1" "stac-fastapi.types==7.1.1" \
                 "stac-fastapi.extensions==7.1.1" "stac-fastapi-pgstac==7.2.1" \
                 "titiler.application==2.4.0" uvicorn
```

> **注意：** 不要 `pip install titiler`。TiTiler 在 2025 年末已停止维护该元包（PyPI 上停留在 0.25.0），必须按命名空间安装 `titiler.core`、`titiler.application` 等子包（[官方说明](https://github.com/developmentseed/titiler/pull/1244)）。

### COG 生成需要 GDAL

`rio-cogeo` 依赖 rasterio 与系统 GDAL 库：

```bash
# Ubuntu / Debian
sudo apt-get install -y gdal-bin libgdal-dev

# macOS
brew install gdal

# Conda（推荐，自动解决 C 库版本）
conda install -c conda-forge gdal rio-cogeo
```

### 服务端组件

```bash
# 只用 TiTiler 的官方镜像（COG/STAC/MosaicJSON 端点齐全）
docker run --rm -p 8000:8000 ghcr.io/developmentseed/titiler:latest \
  uvicorn titiler.application.main:app --host 0.0.0.0 --port 8000

# STAC API 需要 PostgreSQL + PostGIS + pgstac
docker run --rm -p 5439:5432 -e POSTGRES_USER=username \
  -e POSTGRES_PASSWORD=password -e POSTGRES_DB=postgis postgis/postgis:16-3.4
```

### 验证

```bash
rio cogeo --version          # 应显示 7.0.4
python -c "import stac_fastapi.api, titiler.core; print('ok')"
curl -s http://localhost:8000/ | head -c 200      # TiTiler 落地页 JSON
curl -s http://localhost:8000/api.html -o /dev/null -w '%{http_code}\n'   # OpenAPI 文档
```

---

## 核心概念与命令

### COG：为什么它能按需出图

普通 GeoTIFF 的行按整幅宽存储，读一个小窗口也要下载大段数据。COG 做了三件事：

| 特性 | 作用 |
|------|------|
| 内部 tile（默认 512×512） | 任意窗口只需读少数几个 tile |
| 内部 overview 金字塔 | 缩小时直接读低分辨率层，不用全量重采样 |
| 头部元数据前置 | 客户端读前几百字节即可知道尺寸、分块、概览信息 |

因此服务端只需 `Range: bytes=...` 请求几次，就能取出渲染一片瓦片所需的数据——这是 TiTiler 能做到「不落盘、不预切」的前提。

### rio-cogeo：生成与校验

```bash
# 生成 COG（deflate 压缩，默认 512 分块，自动建 overview）
rio cogeo create input.tif output_cog.tif

# 常用选项
rio cogeo create input.tif output_cog.tif \
  --cog-profile deflate \        # deflate | zstd | lzw | jpeg | webp
  --overview-resampling bilinear \   # 建 overview 用的重采样算法（默认 nearest）
  --overview-level 6 \               # 从第 6 级开始建 overview；省略则自动选到最小 overview 小于 blocksize
  --blocksize 512 \                  # 覆盖 profile 的内部 tile 尺寸
  --nodata 0                      # 显式声明 nodata

# 校验是否符合 COG 规范
rio cogeo validate output_cog.tif

# 查看栅格与 COG 结构信息
rio cogeo info output_cog.tif
```

`validate` 通过是上云前的硬门槛；报错会指出缺失 overview、分块顺序不合法或未按 tile 组织。注意 `--overview-level` 是**从第几级开始建 overview**，不是"建几级金字塔"；省略时 rio-cogeo 自动建到最小 overview 小于内部 blocksize 为止。

### STAC：元数据模型

三层模型，逐层收窄：

```text
Catalog（目录，可嵌套）
  └── Collection（数据集，定义时空范围与许可）
        └── Item（单景，一个 datetime + 几何 + assets）
```

Item 的关键字段是 `id`、`bbox`、`geometry`、`properties.datetime`，以及 `assets`——资产用 `href` 指向对象存储里的 COG：

```json
{
  "type": "Feature",
  "stac_version": "1.1.0",
  "id": "S2B_32TMT_20260101",
  "bbox": [116.1, 39.7, 116.6, 40.1],
  "geometry": { "type": "Polygon", "coordinates": [[]] },
  "properties": { "datetime": "2026-01-01T03:20:00Z", "eo:cloud_cover": 3.2 },
  "assets": {
    "visual": {
      "href": "s3://bucket/cogs/S2B_32TMT_20260101.tif",
      "type": "image/tiff; application=geotiff; profile=cloud-optimized",
      "roles": ["data"]
    }
  },
  "links": []
}
```

用 pystac 构造与校验，避免手写 JSON 出错：

```python
import pystac

item = pystac.Item(
    id="S2B_32TMT_20260101",
    geometry=footprint,
    bbox=bbox,
    datetime=dt,
    properties={"eo:cloud_cover": 3.2},
)
item.add_asset("visual", pystac.Asset(
    href="s3://bucket/cogs/S2B_32TMT_20260101.tif",
    media_type=pystac.MediaType.COG,
    roles=["data"],
))
item.set_self_href("./S2B_32TMT_20260101/S2B_32TMT_20260101.json")
item.save_object()
```

### STAC API：stac-fastapi + pgstac

```bash
# 配置连接（.env 或环境变量）
export PGUSER=username PGPASSWORD=password PGDATABASE=postgis PGHOST=localhost PGPORT=5439
export STAC_FASTAPI_TITLE="My STAC API"
export STAC_FASTAPI_DESCRIPTION="Imagery catalog"

# 启动
uvicorn stac_fastapi.pgstac.app:app --host 0.0.0.0 --port 8080
```

数据库需先安装 pgstac 结构（`pgstac-migrate migrate`，需超级用户权限），并授权：

```bash
psql -d postgres://username@localhost:5439/postgis -c "GRANT pgstac_admin TO username"
```

检索走标准 STAC API：

```bash
# 集合与条目
curl -s 'http://localhost:8080/collections' | head -c 300
curl -s 'http://localhost:8080/collections/sentinel-2/items?limit=5'

# bbox + 时间 + 字段过滤（CQL2 需对应扩展）
curl -s 'http://localhost:8080/search?bbox=116,39,117,41&datetime=2026-01-01/2026-12-31&limit=10'
```

Python 客户端（推荐，处理分页与重试）：

```python
from pystac_client import Client

catalog = Client.open("http://localhost:8080")
search = catalog.search(
    collections=["sentinel-2"],
    bbox=[116, 39, 117, 41],
    datetime="2026-01-01/2026-12-31",
    max_items=20,
)
items = list(search.items())
```

### TiTiler：动态切片

`/cog` 端点直接对一个 COG 出图，`url` 为查询参数（需 URL 编码）：

```bash
COG='https%3A%2F%2Fexample.com%2Fcog%2Fdem.tif'

# TileJSON（前端地图直接用的配置）
curl "http://localhost:8000/cog/WebMercatorQuad/tilejson.json?url=${COG}"

# 单张瓦片
curl "http://localhost:8000/cog/tiles/WebMercatorQuad/8/210/98.png?url=${COG}" -o tile.png

# 基础信息与统计
curl "http://localhost:8000/cog/info?url=${COG}"
curl "http://localhost:8000/cog/statistics?url=${COG}"

# 预览图（不切瓦片）
curl "http://localhost:8000/cog/preview.png?url=${COG}&max_size=512" -o preview.png
```

`/stac` 端点直接对 **STAC Item JSON 的 URL** 出图，`url` 指向 Item 本身的 JSON 地址，`assets` 指定要读的资产名（必填）：

```bash
ITEM='https%3A%2F%2Fexample.com%2Fstac%2FS2B_32TMT_20260101.json'

curl "http://localhost:8000/stac/tiles/WebMercatorQuad/10/420/196.png?url=${ITEM}&assets=visual"
curl "http://localhost:8000/stac/WebMercatorQuad/tilejson.json?url=${ITEM}&assets=visual"
```

多资产组合（如多波段分别存放在不同资产）用重复的 `assets` 参数：`assets=red&assets=green&assets=blue`。

常用渲染参数（对所有 `/tiles` 端点通用）：

| 参数 | 作用 | 示例 |
|------|------|------|
| `bidx` | 波段组合 | `bidx=1&bidx=2&bidx=3` |
| `rescale` | 线性拉伸区间 | `rescale=0,4000` |
| `colormap_name` | 命名色带 | `colormap_name=terrain` |
| `resampling` | 重采样算法 | `resampling=bilinear` |
| `nodata` | 覆盖 nodata | `nodata=0` |
| `max_size` | 预览最大边长 | `max_size=512` |

### MosaicJSON：多景虚拟镶嵌

当范围跨多景时，用 MosaicJSON 把多个 COG 组织成一张虚拟镶嵌图，TiTiler 的 `/mosaicjson` 端点按瓦片动态挑选数据源：

```bash
python -m pip install "cogeo-mosaic==9.2.0"

# 由 COG 列表生成 MosaicJSON
cogeo-mosaic create cogs.txt -o mosaic.json --minzoom 8 --maxzoom 14
```

```bash
curl "http://localhost:8000/mosaicjson/WebMercatorQuad/tilejson.json?url=https%3A%2F%2Fexample.com%2Fmosaic.json"
```

---

## 典型工作流

### 链路一：单景影像从 TIFF 到可浏览瓦片

输入：`input.tif`（任意 GeoTIFF）；输出：可通过 TileJSON 浏览的 COG 服务。

1. **转 COG**：`rio cogeo create input.tif output_cog.tif --cog-profile deflate`
2. **校验**：`rio cogeo validate output_cog.tif`，必须返回 valid
3. **上传对象存储**：`aws s3 cp output_cog.tif s3://bucket/cogs/`（或 MinIO/OSS 等价命令）
4. **确认 Range 可读**：`curl -s -r 0-1023 -o /dev/null -w '%{http_code}' https://.../output_cog.tif` 应返回 206
5. **构造 STAC Item**：用 pystac 写入 `bbox`、`datetime`、`assets.visual.href`
6. **取 TileJSON**：`/cog/WebMercatorQuad/tilejson.json?url=...`，把返回的 `tiles` 填进前端地图
7. **校验产物**：瓦片图片非空白、`/cog/info` 的尺寸与波段与原图一致

```bash
rio cogeo create input.tif output_cog.tif --cog-profile deflate --blocksize 512
rio cogeo validate output_cog.tif
curl -s -r 0-1023 -o /dev/null -w 'range status: %{http_code}\n' "https://cdn.example.com/output_cog.tif"
```

### 链路二：批量入库 STAC API 并按需检索

输入：COG 列表 + 元数据表；输出：可按 bbox/时间检索的 STAC API。

1. **批量转 COG**：脚本遍历原始影像，逐个 `rio cogeo create` 并 `validate`
2. **生成 Item**：pystac 按集合模板逐景生成 Item JSON
3. **入库**：写入 pgstac（`INSERT INTO pgstac.items(content)` 或 pgstac 提供的批量导入工具）
4. **起服务**：`uvicorn stac_fastapi.pgstac.app:app`
5. **检索验证**：`/search?bbox=...&datetime=...` 返回预期条目，`/collections` 能看到集合
6. **接出图**：把检索到的 Item JSON 地址交给 TiTiler 的 `/stac/tiles?url=...&assets=...` 出图（TiTiler 直接读 Item JSON，不需要额外配置 STAC API 连接）

```python
from pystac_client import Client
from rio_cogeo.cogeo import cog_validate

assert cog_validate("output_cog.tif")[0], "COG 校验未通过，先修正再入库"

catalog = Client.open("http://localhost:8080")
items = list(catalog.search(collections=["sentinel-2"], bbox=[116, 39, 117, 41]).items())
print(len(items), items[0].assets["visual"].href)
```

### 链路三：多景镶嵌 + 前端地图接入

输入：跨多景的 COG 集合；输出：一张连续的镶嵌底图。

1. **列 COG 清单**：`cogs.txt` 每行一个 COG URL
2. **生成 MosaicJSON**：`cogeo-mosaic create cogs.txt -o mosaic.json --minzoom 8 --maxzoom 14`
3. **上传 mosaic.json** 到对象存储
4. **取 TileJSON**：`/mosaicjson/WebMercatorQuad/tilejson.json?url=...`
5. **前端接入**：OpenLayers/MapLibre 用返回的 `tiles` 模板建瓦片图层
6. **校验**：拼接处无明显接缝、边缘景号覆盖正确、缩到 minzoom 不出现空白

```javascript
// 前端：把 TileJSON 的 tiles 直接给 MapLibre
const tilejson = await fetch(
  'http://localhost:8000/mosaicjson/WebMercatorQuad/tilejson.json?url=' + encodeURIComponent(mosaicUrl)
).then(r => r.json());

map.addSource('mosaic', { type: 'raster', tiles: tilejson.tiles, tileSize: 256 });
map.addLayer({ id: 'mosaic', type: 'raster', source: 'mosaic' });
```

---

## 性能与工程实践

1. **COG 内部块别太小**：512×512 是通用最优；256 会增加请求次数，1024 会放大单次读取量
2. **对象存储必须支持 Range**：S3/OSS/MinIO/GCS 都支持；某些 CDN 或代理会忽略 `Range` 返回 200 全量，导致出图极慢
3. **CDN 缓存瓦片而非 COG**：瓦片 URL 带 `url` 参数，可对 `/cog/tiles/...` 做短期缓存；COG 本体交给对象存储直读
4. **限定 `maxzoom`**：超过数据实际分辨率继续放大只是插值，浪费算力，用源的真实分辨率推导上限
5. **服务端并发出图是 CPU 密集**：TiTiler 的瓶颈在重采样与编码，多 worker 部署（`--workers N`）比单进程调参有效
6. **MosaicJSON 分层**：超大范围按 maxzoom 分块生成多个 mosaics，避免单个 mosaic.json 过大
7. **私有数据用签名 URL**：不要在前端暴露永久凭据；TiTiler 支持通过环境变量注入 S3 凭据或前置签名
8. **入库前必须 `cog_validate`**：不合规的 COG 会在检索正常的情况下出图失败，排查成本高

---

## 常见问题

| 问题 | 原因 | 处置 |
|------|------|------|
| 瓦片请求返回 416 Range Not Satisfiable | COG 未按 tile 组织，或文件被部分上传/截断 | `rio cogeo validate` 重新校验；确认上传对象大小与本地一致；必要时重转 COG |
| 出图全黑或全白 | `bidx` 波段顺序错误，或缺 `rescale` 拉伸 | 用 `/cog/info` 看波段数与 dtype；单波段加 `rescale=min,max`，多波段用 `bidx=1&bidx=2&bidx=3` |
| 403 Forbidden 或 Access Denied | 对象存储桶/对象私有，TiTiler 没拿到凭据 | 给服务进程配置 AWS 凭据或 IAM 角色；或改用预签名 URL 作为 `url` 参数 |
| `pip install titiler` 装出来的东西不对 | TiTiler 已弃用该元包，PyPI 上停在 0.25.0 | 改装 `titiler.application==2.4.0` 或按需装 `titiler.core` 等子包 |
| `/stac/tiles` 报 400 或读不到资产 | `url` 指向的 Item JSON 不可访问，或 `assets` 名称与 Item 里的 `assets` 键不一致 | `curl` 打开 Item JSON 核对 `assets` 的键名；`url` 必须指向 Item 文件而不是 Collection 或 API 检索页 |
| stac-fastapi 启动报缺少 pgstac 表 | 数据库未执行 pgstac 迁移，或用户无权限 | 用 `pgstac-migrate migrate` 建结构，并 `GRANT pgstac_admin` 给连接用户 |
| 瓦片拼接处有明显接缝 | 多景镶嵌的重采样/色彩不一致 | 统一 `rescale` 与 `colormap`，或先做色彩一致性处理再生成 MosaicJSON |
| 预览图比预期模糊 | 默认预览尺寸受限，或源没有 overview | 设 `max_size`；确认 COG 带 overview（`rio cogeo info` 的 overviews 字段） |
| 前端加载瓦片很慢但服务端正常 | CDN/代理忽略 Range，或未缓存瓦片 | 检查 `curl -r 0-1023` 是否返回 206；对瓦片端点加缓存层 |

---

## AI 使用建议

- **执行环境**：`pip install`、`docker run` 在终端执行；本链路组件多，装包输出长，重定向到文件再分段读。Windows 下 Docker 需先确认守护进程在运行。
- **先探测版本**：`rio cogeo --version`、`python -c "import stac_fastapi.api as m; print(m.__version__)"`、`curl -s localhost:8000/ | head -c 200`。本技能按 rio-cogeo 7.0.4、stac-fastapi 7.1.1、TiTiler 2.4.0 编写；TiTiler 2.x 与 0.x 的包名和入口完全不同，别混用旧教程。
- **验证产物**：COG 用 `rio cogeo validate` 的返回值为准，不只看命令是否退出 0；瓦片用 `curl -o tile.png` 后检查文件大小与是否全透明；前端能否出图必须由浏览器确认，AI 助手通常看不到画面。
- **无 GPU/无对象存储环境**：可用本地 `file://` 或 `http.server` 充当 COG 源验证逻辑，但 Range 行为与真实对象存储不同，不要据此判断生产性能。
- **参数顺序**：`/cog/tiles/{tileMatrixSetId}/{z}/{x}/{y}.png?url=...` 中 `tileMatrixSetId` 缺省为 `WebMercatorQuad`；`url` 必须 URL 编码，否则带查询串的对象地址会被截断。
- **常见症状**：400 多为参数名拼错或 `bidx` 越界；404 是路由或 item 不存在；416 是文件不是合法 COG；500 先看服务端日志里的 rasterio 异常。
- **安全与权限**：不要在前端或汇报里回显云凭据；公开服务前确认影像的许可与分发范围，个别数据源禁止二次发布。

## 相关技能

- **gdal** — COG 生成与校验的底层工具链（`gdal_translate -of COG`）：[../gdal/SKILL.md](../gdal/SKILL.md)
- **pdal** — 点云/高程数据的处理，与 DEM 类 COG 配合：[../pdal/SKILL.md](../pdal/SKILL.md)
- **postgis** — pgstac 的空间检索基础（PostGIS 索引与查询）：[../postgis/SKILL.md](../postgis/SKILL.md)
- **openlayers** — 前端接入 TileJSON 瓦片源：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **maplibre-gl-js** — 矢量/栅格瓦片前端渲染：[../maplibre-gl-js/SKILL.md](../maplibre-gl-js/SKILL.md)
- **cesiumjs** — 影像与地形在三维地球上的叠加：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)

## 参考资源

- STAC 规范：<https://stacspec.org/>
- STAC 规范仓库：<https://github.com/radiantearth/stac-spec>
- STAC API 规范：<https://github.com/radiantearth/stac-api-spec>
- stac-fastapi 文档：<https://stac-utils.github.io/stac-fastapi/>
- pgstac：<https://github.com/stac-utils/pgstac>
- COG 规范：<https://github.com/cogeotiff/cog-spec>
- rio-cogeo 文档：<https://cogeotiff.github.io/rio-cogeo/>
- rio-cogeo CLI：<https://cogeotiff.github.io/rio-cogeo/CLI/>
- TiTiler 文档：<https://developmentseed.org/titiler/>
- TiTiler COG 端点：<https://developmentseed.org/titiler/endpoints/cog/>
- TiTiler STAC 端点：<https://developmentseed.org/titiler/endpoints/stac/>
- TiTiler 镜像：<https://github.com/developmentseed/titiler/pkgs/container/titiler>
- pystac-client 文档：<https://pystac-client.readthedocs.io/>
- 中文教程：<https://znlgis.github.io/gis/tutorial/STAC-COG-TiTiler/>
