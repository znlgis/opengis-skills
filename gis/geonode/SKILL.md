---
name: geonode
description: "Use when deploying or automating GeoNode 5.1.1 — docker compose with create-envfile.py, geonode/geonode:5.1.1 image, django4geonode logs, /api/v2/resources and /api/v2/uploads/upload (action=upload|replace|upsert|create), OGC WMS/WFS links from resource.links[], geonode-project customization; also for 502 after compose up, 'GeoNode has no attribute' after upgrade, and upload 401/403 with Basic vs Bearer auth."
tags:
  - geonode
  - gis
  - django
  - python
  - docker
  - postgis
  - geoserver
  - rest-api
  - metadata
  - webgis
---

> **项目地址：** <https://github.com/GeoNode/geonode>
>
> **官方文档：** <https://docs.geonode.org/en/latest/>
>
> **演示站：** <https://development.demo.geonode.org>
>
> **最新版本：** 5.1.1（GitHub Release 与 PyPI 均为 5.1.1，截至 2026-10）；官方镜像 `geonode/geonode:5.1.1`
>
> **运行环境：** Python >= 3.10（PyPI 元数据），依赖 Django 5.2.18、psycopg2 2.9.13、Celery 5.6.3
>
> **许可证：** GPL-2.0-or-later

## 概述

GeoNode 是一个基于 Django 的地理空间内容管理系统（CMS），把数据发布、元数据编目、地图制作与权限管理整合到一个 Web 平台。它不是单个 GIS 组件，而是把成熟开源组件编排成一套可运营的服务。

核心构成：

- **Django 应用**：资源（dataset / map / document / geostory / dashboard）、用户与权限、元数据
- **GeoServer**：实际提供 WMS / WFS / WCS 服务与样式渲染
- **PostgreSQL + PostGIS**：元数据库 `geonode` 与数据库 `geonode_data` 两个库
- **pycsw**：CSW 目录服务与 ISO 元数据发布
- **Celery + Redis**：异步任务（上传解析、缩略图、元数据更新）
- **uWSGI + nginx（或仅 Django 开发服务器）**：对外服务与静态资源
- **REST API v2**：`/api/v2/*`，资源检索、上传、元数据编辑；旧版 Tastypie 接口仍在 `/api/*`

适合的场景是"要给一个组织提供数据门户"：统一登录、按用户/组授权、自动生成 OGC 服务与元数据记录。若只需要发几个 WMS 图层，GeoServer 单独部署更轻。

## 环境准备

### 方式一：Docker Compose（推荐，官方主路径）

```bash
git clone https://github.com/GeoNode/geonode.git
cd geonode

# 生成 .env（随机密码、OAuth2 client、站点地址）
python create-envfile.py --env_type dev --hostname localhost

# 构建并启动
docker compose build
docker compose up -d
```

`create-envfile.py` 的关键参数：

| 参数 | 作用 |
|------|------|
| `--env_type` | `dev`（DEBUG 开、无 SSL）、`test`（自签证书）、`prod`（申请 Let's Encrypt 证书） |
| `--hostname` | 对外访问域名/主机名，默认 `localhost` |
| `--email` | 管理员邮箱（`prod` 下用于证书签发） |
| `--geonodepwd` / `--geoserverpwd` | GeoNode / GeoServer 管理员密码；留空则随机生成并写入 .env |
| `--pgpwd` / `--dbpwd` / `--geodbpwd` | PostgreSQL 超级用户、GeoNode 库用户、数据库用户密码 |
| `--clientid` / `--clientsecret` | GeoServer 侧 OAuth2 客户端凭据 |

启动后访问 `http://localhost`，管理员账号为 `admin`，密码见生成的 `.env`（若未显式传入）。

```bash
# 跟踪初始化日志（迁移、fixtures、静态文件、词表加载）
docker compose logs -f django

# 或直接进容器
docker exec -it django4geonode /bin/bash
```

日志里出现 `Executing UWSGI server uwsgi --ini /usr/src/app/uwsgi.ini` 即表示应用已就绪。

### 方式二：预构建镜像

```bash
docker run -d --name geonode -p 8000:8000 geonode/geonode:5.1.1
```

单容器镜像适合快速试跑；缺少 PostGIS、GeoServer、Redis 的编排时功能不完整，正式部署仍应用 compose。

### 方式三：裸机安装（Ubuntu 24.04）

```bash
# 1) 虚拟环境
python3 -m venv ~/.virtualenvs/geonode
source ~/.virtualenvs/geonode/bin/activate

# 2) 源码与依赖
sudo mkdir -p /opt/geonode
sudo chown -R "$USER":www-data /opt/geonode
cd /opt && git clone https://github.com/GeoNode/geonode.git -b 5.1.x geonode
cd /opt/geonode
pip install -r requirements.txt --upgrade
pip install -e . --upgrade
```

分支要与版本对应：5.1.1 对应 `5.1.x`（旧文档里的 `5.0.x` 是上一个系列）。

```bash
# 3) PostGIS 两个库
sudo apt install -y postgresql-15 postgresql-15-postgis-3 postgresql-15-postgis-3-scripts
sudo -u postgres createuser -P geonode
sudo -u postgres createdb -O geonode geonode
sudo -u postgres createdb -O geonode geonode_data

for db in geonode geonode_data; do
  sudo -u postgres psql -d "$db" -c 'CREATE EXTENSION postgis;'
  sudo -u postgres psql -d "$db" -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
  sudo -u postgres psql -d "$db" -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'
done
```

```bash
# 4) 初始化应用
cd /opt/geonode
export DJANGO_SETTINGS_MODULE=geonode.settings
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

裸机路径还需要单独装 GeoServer 并配置 OAuth2 代理，官方文档的 bare installation 章节会逐步给出；不想折腾就用 Docker。

### 验证

```bash
# 版本
curl -s http://localhost/version.txt

# API 是否可用（公开资源无需认证）
curl -s "http://localhost/api/v2/resources?page_size=1" | head -c 300

# OGC 服务是否由 GeoServer 提供
curl -s "http://localhost/geoserver/web/" -o /dev/null -w "%{http_code}\n"
```

## 核心 API

### 认证

| 方式 | 请求头 | 说明 |
|------|--------|------|
| 匿名 | 无 | 只能读公开资源 |
| Basic | `Authorization: Basic base64(user:pass)` | 最简单，脚本首选 |
| Bearer | `Authorization: Bearer <token>` | 由 OAuth2 提供方 `/o/token/` 颁发 |

```bash
# 用 OAuth2 换取 token（client 凭据来自 .env 的 clientid / clientsecret）
curl -s -X POST http://localhost/o/token/ \
  -d "grant_type=password" \
  -d "username=admin" -d "password=<admin-password>" \
  -d "client_id=<clientid>" -d "client_secret=<clientsecret>"
```

### 资源检索

| 目的 | 请求 |
|------|------|
| 列出全部资源 | `GET /api/v2/resources` |
| 资源详情 | `GET /api/v2/resources/{pk}` |
| 按类型过滤 | `/api/v2/resources?filter{resource_type}=dataset` |
| 按子类型过滤 | `/api/v2/resources?filter{subtype}=vector` |
| 按关键词/分类/区域 | `?filter{keywords.name}=...`、`?filter{category.identifier}=...`、`?filter{regions.name}=...` |
| 按所有者 | `?filter{owner.username}=...` |
| 全文搜索 | `?search=text&search_fields=title&search_fields=abstract` |
| 只看已发布/已审核 | `?filter{is_published}=true`、`?filter{is_approved}=true` |
| 按范围 | `?extent=-180,-90,180,90` |

`filter{...}` 支持 `.in` 与 `.icontains` 后缀，例如 `?filter{regions.name.icontains}=global`。

```bash
curl -s "http://localhost/api/v2/resources?filter{resource_type}=dataset&page_size=5" \
  -H "Authorization: Basic $(printf 'admin:secret' | base64)"
```

### 上传与更新数据集

统一入口 `POST /api/v2/uploads/upload`（成功返回 201），由 `action` 参数决定行为：

| action | 用途 | 额外必填 |
|--------|------|----------|
| `upload`（默认） | 上传新数据集 | 无 |
| `replace` | 用新数据替换已有数据集 | `resource_pk` |
| `upsert` | 按关键字段合并（存在则更新，否则插入） | `resource_pk`（可选 `upsert_key`，默认 `fid`） |
| `create` | 建空数据集（不上传文件） | `title`、`geom`、`attributes` |
| `resource_style_upload` | 给已有数据集应用 SLD 样式 | `resource_pk` + SLD 文件 |
| `resource_metadata_upload` | 给已有数据集应用 XML 元数据 | `resource_pk` + XML 文件 |

支持的格式：Shapefile（zip）、GeoTIFF、CSV、ZIP 归档、XML 元数据、SLD。

```python
import requests

url = "http://localhost/api/v2/uploads/upload"
headers = {"Authorization": "Basic <base64(admin:password)>"}
with open("data/BoulderCityLimits.zip", "rb") as fh:
    files = [("base_file", ("BoulderCityLimits.zip", fh, "application/zip"))]
    print(requests.post(url, headers=headers, data={"action": "upload"}, files=files).status_code)
```

### 元数据与下载

| 目的 | 请求 / 字段 |
|------|-------------|
| 数据集元数据 | `PUT /api/v2/datasets/{id}/metadata` |
| 默认格式下载 | `resource.download_url`（矢量转 Shapefile，栅格转 GeoTIFF） |
| 元数据文档链接 | `resource.links[]` 中 `link_type == "metadata"` 的条目 |
| OGC 服务地址 | `links[]` 中 `link_type` 为 `OGC:WMS` / `OGC:WFS` / `OGC:WCS` |
| OGC 图层名 | `resource.alternate`（形如 `workspace:layername`） |
| 嵌入 iframe | `resource.embed_url` |

### 管理命令与运维

```bash
# 容器内的 Django 管理命令
docker compose exec django python manage.py migrate
docker compose exec django python manage.py createsuperuser
docker compose exec django python manage.py collectstatic --noinput

# 备份 / 恢复
docker compose exec db pg_dump -U postgres geonode > geonode.sql
docker compose exec db pg_dump -U postgres geonode_data > geonode_data.sql
```

`tasks.py`（Invoke 任务）提供了 `update`、`migrations`、`statics`、`fixtures`、`updateadmin` 等编排步骤，compose 的入口脚本在首次启动时会按顺序调它们。

## 典型工作流：上传 Shapefile → 补元数据 → 取 OGC 服务

目标：把一个 Shapefile 发布成带元数据的矢量数据集，并拿到可直接给前端用的 WMS 地址。

**步骤 1：上传**

```bash
BASE=http://localhost
AUTH="Authorization: Basic $(printf 'admin:<password>' | base64)"

curl -s -X POST "$BASE/api/v2/uploads/upload" \
  -H "$AUTH" \
  -F "action=upload" \
  -F "base_file=@data/roads.zip" \
  -o upload.json -w "%{http_code}\n"
```

返回体里带执行请求 id；上传解析是异步的，稍等片刻再查资源列表。

**步骤 2：确认资源已建好**

```bash
curl -s "$BASE/api/v2/resources?search=roads&page_size=5" -H "$AUTH" \
  | python -c "import json,sys;d=json.load(sys.stdin);print([(r['pk'], r['title'], r['subtype']) for r in d['resources']])"
```

**步骤 3：补元数据（标题、摘要、关键词、许可）**

```bash
curl -s -X PATCH "$BASE/api/v2/resources/<pk>" -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"title": "城市道路", "abstract": "2026 年道路中心线", "is_published": true}'
```

需要完整 ISO 元数据时，改用 `action=resource_metadata_upload` 或 `PUT /api/v2/datasets/{id}/metadata`。若上面的 `PATCH` 在某个部署上返回 405，改用 `PUT` 全量提交，或直接在后台 `/admin/` 的资源编辑页修改。

**步骤 4：取 OGC 地址并验证**

```python
import requests

r = requests.get("http://localhost/api/v2/resources/<pk>",
                 headers={"Authorization": "Basic <base64>"}).json()

wms = next(l["url"] for l in r["links"] if l["link_type"] == "OGC:WMS")
layer = r["alternate"]                      # 形如 workspace:roads
print(wms, layer)
print(requests.get(wms, params={
    "service": "WMS", "version": "1.3.0", "request": "GetMap",
    "layers": layer, "crs": "EPSG:4326",
    "bbox": "116.0,39.5,116.6,40.1", "width": "512", "height": "512",
    "format": "image/png",
}).status_code)
```

期望拿到 200 与 PNG 字节；返回 404 通常是图层名（`alternate`）写错，返回 400 多半是 bbox 顺序或 CRS 不匹配。

**步骤 5：验收**

- 后台 `/admin/` 能看到该数据集，状态为已发布
- `GetCapabilities` 里能找到 `alternate` 对应的图层
- `download_url` 能下载到 Shapefile

## 最佳实践

1. **用 `--env_type dev` 试跑，正式环境再上 `prod`**：`prod` 会尝试申请 Let's Encrypt 证书，域名不可达时会卡住或失败。
2. **两个数据库都要建 PostGIS**：`geonode` 存元数据、`geonode_data` 存业务数据，漏建任何一个都会在上传时报扩展错误。
3. **自定义就走 geonode-project**：不要直接改核心源码；用 <https://github.com/GeoNode/geonode-project> 模板生成项目，升级时只合并自己的改动。
4. **上传走异步，别立刻查**：上传接口返回的是执行请求 id，解析完成前资源可能还不完整；轮询 `/api/v2/resources` 或用后台任务状态确认。
5. **批量更新用 upsert**：`action=replace` 会整体替换数据，`action=upsert` 才能按 `upsert_key` 合并增量。
6. **OGC 地址从 API 取，不要手拼**：`links[]` 与 `alternate` 是权威来源，手拼工作区名在改名后会失效。
7. **备份两个库**：`geonode` 与 `geonode_data` 必须同时备份，只备份其一恢复后会缺资源定义或数据表。

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `docker compose up` 后页面 502 | Django 容器还在迁移/收集静态文件，或启动失败 | `docker compose logs -f django` 看到 uWSGI 启动行为止；失败时看首个 Traceback，常见是数据库连不上 |
| 上传接口返回 401 | 缺少或错误的 Authorization 头 | 用 Basic 或 Bearer；确认 base64 编码的是 `用户名:密码` 且未带多余空格 |
| 上传返回 403 | 用户没有 `base.add_resourcebase` 权限 | 换管理员账号，或在后台给该用户/组授予上传权限 |
| 管理员密码不知道 | `create-envfile.py` 随机生成了密码 | 查 `.env` 里的 `ADMIN_PASSWORD`/`GEONODE_ADMIN_PASSWORD`；已丢失则进容器 `python manage.py changepassword admin` |
| 上传后资源一直是"处理中" | Celery worker 未运行或 Redis 不可达 | `docker compose ps` 确认 celery/redis 状态；看 worker 日志 |
| GetMap 返回空白图 | 图层没有数据范围，或 CRS/bbox 不匹配 | 在后台重新计算边界（`UpdateLayerStatistics` 类似操作），并用 `resource.bbox` 核对 |
| 升级后报错 `AttributeError` / 表不存在 | 未执行迁移 | `docker compose exec django python manage.py migrate`；自定义项目先合并上游 settings 变更 |
| `docs.geonode.org` 某些深链 404 | 文档站路径随版本调整 | 从首页导航进入；或直接读仓库 `docs/src/` 下对应 Markdown |
| 裸机安装 GeoServer 登录失败 | OAuth2 client 与 GeoNode 不一致 | 按官方 OAuth2 章节核对 `clientid/clientsecret` 与 GeoServer 过滤器配置 |

## DeepSeek Harness 使用建议

- **加载技能**：skill("geonode")；技能目录只读，脚本与上传样例写到会话工作区。
- **先确认版本与入口**：`curl -s http://localhost/version.txt` 确认 5.1.1；Docker 部署优先用 `docker compose exec` 而不是宿主机的 `manage.py`，避免环境错位。
- **API 用 `/api/v2/`**：旧 Tastypie 的 `/api/*` 仍在，但新代码一律用 `/api/v2/resources` 与 `/api/v2/uploads/upload`；两者返回结构不同，不要混用。
- **认证信息不要进日志**：用环境变量传 `Authorization`，示例里出现的 `<base64>` 必须替换，不要把真实凭据写进脚本或报告。
- **验证产物**：上传后回读资源详情，核对 `subtype`、`alternate`、`links[]` 与 `download_url`，再对 WMS 发一次 `GetMap`；只看 201 响应不构成"发布成功"。
- **写操作确认**：`action=replace`、删除资源、`migrate`、恢复数据库都不可逆；执行前备份两个库并确认 `resource_pk`。

## 相关技能

- **geoserver** — GeoNode 背后的 OGC 服务引擎：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **geoserver-rest-api** — 直接操作 GeoServer 的 REST 接口：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **postgis** — 元数据库与数据库的底层扩展：[../postgis/SKILL.md](../postgis/SKILL.md)
- **gdal** — 上传前的数据准备与格式转换：[../gdal/SKILL.md](../gdal/SKILL.md)
- **opengis-all** — 全流程 GIS 索引：[../opengis-all/SKILL.md](../opengis-all/SKILL.md)

## 参考资源
- 官方文档：<https://docs.geonode.org/en/latest/>
- 快速安装：<https://docs.geonode.org/en/latest/overview/quick/>
- API 使用指南：<https://github.com/GeoNode/geonode/blob/master/docs/src/development/api.md>
- 项目模板（自定义部署）：<https://github.com/GeoNode/geonode-project>
- 演示站：<https://demo.geonode.org>
