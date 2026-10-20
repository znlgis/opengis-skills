---
name: geoserver-cloud
description: "Use when deploying GeoServer Cloud 3.0.2 on Docker Compose or Kubernetes — gateway serving WMS/WFS/WCS/WPS/GWC microservices under /geoserver/cloud, PgConfig vs datadir backends, RabbitMQ config-bus sync, Helm chart geoservercloud 3.0.2, and diagnosing 502s via actuator/health and Consul registration."
tags:
  - java
  - server
  - wms
  - wfs
  - wmts
  - cloud
  - kubernetes
  - docker
  - microservices
  - spring-cloud
---

> **项目地址：** <https://github.com/geoserver/geoserver-cloud>
>
> **官方文档：** <https://geoserver.org/geoserver-cloud/>
>
> **Docker Hub：** <https://hub.docker.com/u/geoservercloud>（镜像标签与 GeoServer 主版本对应，如 `3.0.2`）
>
> **最新版本：** 3.0.2（2026-10-20，[GitHub Releases](https://github.com/geoserver/geoserver-cloud/releases)）
>
> **许可证：** GPL-2.0

## 概述

GeoServer Cloud（GS Cloud）：

- **微服务架构**：每种 OGC 服务为独立 Spring Boot 应用
- **配置同步**：Spring Cloud Bus + RabbitMQ 实时同步（`GEOSERVER_BUS_ENABLED`）
- **配置后端**：本地目录 / **PgConfig（推荐）** / JDBCConfig
- **可观测**：Actuator + Prometheus + Micrometer Tracing
- **容器友好**：官方镜像、Helm Chart、docker-compose
- **完全兼容社区版**：相同 Web UI、SLD、数据存储
- **默认路径前缀**：`/geoserver/cloud`（网关 `http://localhost:9090/geoserver/cloud/...`）

---

## 服务拆分

| 服务 | 镜像 | 用途 |
|------|------|------|
| `gateway` | `geoservercloud/geoserver-cloud-gateway` | 网关 |
| `discovery` | `geoservercloud/geoserver-cloud-discovery` | 服务发现（3.x 的官方 compose 改用 `hashicorp/consul`） |
| `config` | `geoservercloud/geoserver-cloud-config` | 配置中心 |
| `web-ui` | `geoservercloud/geoserver-cloud-webui` | 管理界面 |
| `rest` | `geoservercloud/geoserver-cloud-rest` | REST API |
| `wms` | `geoservercloud/geoserver-cloud-wms` | WMS |
| `wfs` | `geoservercloud/geoserver-cloud-wfs` | WFS |
| `wcs` | `geoservercloud/geoserver-cloud-wcs` | WCS |
| `wps` | `geoservercloud/geoserver-cloud-wps` | WPS |
| `gwc` | `geoservercloud/geoserver-cloud-gwc` | 瓦片缓存 |

---

## 环境准备与快速启动（docker-compose）

```bash
# 官方 Quick Start：下载稳定版 compose 文件（仓库内的 compose/ 目录仅供开发调试）
wget "https://geoserver.org/geoserver-cloud/deploy/docker-compose/stable/pgconfig/compose.yml"
docker compose pull
docker compose up -d
docker compose ps

# Gateway: http://localhost:9090/geoserver/cloud   （Web UI）
# Consul : http://localhost:8500                   （服务发现与控制台）
curl -u admin:geoserver "http://localhost:9090/geoserver/cloud/rest/workspaces.json"
```

---

## 配置后端

| 后端 | 适用场景 |
|------|---------|
| **datadir** | 共享卷（NFS/PVC），简单 |
| **pgconfig** | 生产推荐，强一致 |
| **jdbcconfig** | 旧方案，已被替代 |

启用 PgConfig：

```yaml
SPRING_PROFILES_ACTIVE: "pgconfig"   # 启用 PgConfig 后端
PGCONFIG_HOST: "geoserverdb"
PGCONFIG_PORT: "5432"
PGCONFIG_DATABASE: "geoserver"
PGCONFIG_USERNAME: "geoserver"
PGCONFIG_PASSWORD: "geoserver"
PGCONFIG_SCHEMA: "pgconfig"          # 启动时自动创建 schema
```

**注意：** 走 Spring Cloud Config Server 集中下发时，以上变量加前缀 `SPRING_CLOUD_CONFIG_SERVER_OVERRIDES_`（如 `SPRING_CLOUD_CONFIG_SERVER_OVERRIDES_PGCONFIG_HOST`）配在 config 服务上；`standalone` profile（Kubernetes 常用）则直接写在各服务上。

---

## Kubernetes（Helm）

```bash
# Chart：camptocamp/helm-geoserver-cloud（chart 名 geoservercloud，最新 3.0.2）
helm repo add geoserver-cloud https://camptocamp.github.io/helm-geoserver-cloud
helm repo update
```

> 官方要求把该 chart 作为**子 chart（依赖）**引入自己的 umbrella chart（不直接 `helm install`），副本数等参数写在子 chart 键 `geoservercloud` 下：
>
> ```yaml
> # Chart.yaml
> dependencies:
>   - name: geoservercloud
>     repository: https://camptocamp.github.io/helm-geoserver-cloud
>     version: 3.0.2
> ```
>
> ```yaml
> # values.yaml
> geoservercloud:
>   global:
>     profile: standalone,pgconfig
>   geoserver:
>     services:
>       wms:
>         replicaCount: 3
> ```
>
> ```bash
> helm dependency update && helm install my-gsc . -n gis --create-namespace -f values.yaml
> # 临时扩缩容也可直接改 Deployment（chart 默认 nameOverride 为 gsc）
> kubectl -n gis get deploy | grep wms
> ```

---

## 核心 API：网关路由与端点

| 路径 | 转发到 |
|------|--------|
| `/geoserver/cloud/wms` | wms |
| `/geoserver/cloud/wfs` | wfs |
| `/geoserver/cloud/wcs` | wcs |
| `/geoserver/cloud/wps` | wps |
| `/geoserver/cloud/gwc` | gwc |
| `/geoserver/cloud/rest` | rest |
| `/geoserver/cloud/web` | web-ui |

前缀由 `GEOSERVER_BASE_PATH`（默认 compose 中为 `/geoserver/cloud`）控制，网关的 `StripBasePath` 过滤器去掉前缀后再转发（`/geoserver/cloud/wms` → 下游 `/wms`）。

---

## 配置同步

任意修改 → REST/web-ui 发送 `RemoteApplicationEvent` 到 RabbitMQ → 所有副本订阅刷新本地 `Catalog`，秒级一致。

```yaml
# 环境变量形式（compose 中使用）
GEOSERVER_BUS_ENABLED: "true"
RABBITMQ_HOST: rabbitmq
RABBITMQ_PORT: "5672"
```

---

## 监控

```yaml
management:
  endpoints.web.exposure.include: "*"
  metrics.export.prometheus.enabled: true
```

- Prometheus 抓 `/actuator/prometheus`（Micrometer 指标，另有 `/actuator/metrics`）
- 日志 STDOUT，配合 EFK / Loki
- 分布式追踪非默认开启：可接 OpenTelemetry / Zipkin / Jaeger

---

## 与单体兼容

直接挂载现有 GeoServer 数据目录平滑迁移：

```bash
docker run -e SPRING_PROFILES_ACTIVE=datadir \
  -v /mnt/gsdata:/opt/app/data_directory \
  geoservercloud/geoserver-cloud-wms:3.0.2
```

---

## 性能优化

1. WMS 多副本 + Gateway 轮询；GWC 单独部署
2. PgConfig 数据库独立 + 连接池调优
3. RabbitMQ 设 `delivery_limit` 避免风暴
4. 关闭未用服务（不部署 WPS/WCS）
5. 配合 Caffeine + Redis 缓存（按需）
6. 影像金字塔与瓦片预切片

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 配置不同步 | 检查 RabbitMQ 可达 + `GEOSERVER_BUS_ENABLED=true` |
| Web UI 改了 wms 没生效 | 检查事件订阅 |
| 启动顺序错乱 | `depends_on` + 健康检查；K8s 用 `initContainers` |
| OOM | 调整 `-Xmx`，按服务独立资源 |
| Gateway 502 / 服务不可达 | 检查目标服务健康状态与 Consul 注册（服务名解析：`wms`、`wfs` 等） |
| 瓦片 404 / 缓存未命中 | 确认 gwc 服务已部署、`GEOSERVER_BASE_PATH` 与请求路径一致，必要时重新 seed |

---

## 典型工作流

### 工作流 1：从零部署高可用 GeoServer Cloud

```bash
# 下载稳定版 pgconfig compose（仓库内 compose/ 目录仅供开发调试）
wget "https://geoserver.org/geoserver-cloud/deploy/docker-compose/stable/pgconfig/compose.yml"

# 启动基础设施 + 所有微服务
docker compose pull
docker compose up -d

# 验证 Gateway 可访问
curl -u admin:geoserver http://localhost:9090/geoserver/cloud/rest/about/version.json

# 扩容 WMS 服务（3 副本）
docker compose up -d --scale wms=3
```

### 工作流 2：Kubernetes 生产部署 + 自动伸缩

```bash
# 添加 Helm 仓库（chart 名 geoservercloud，由 camptocamp 维护）
helm repo add geoserver-cloud https://camptocamp.github.io/helm-geoserver-cloud
helm repo update

# 在自己的 umbrella chart 中把 geoservercloud 声明为依赖（RabbitMQ/PostgreSQL 同样以依赖引入）
# values.yaml 里写 geoservercloud.geoserver.services.wms.replicaCount 等参数
helm dependency update
helm upgrade --install gs . -n gis --create-namespace -f values.yaml

# 手动伸缩 WMS（先查出 Deployment 名）
kubectl -n gis get deploy | grep wms
kubectl -n gis scale deploy <wms-deployment> --replicas=10
```

## DeepSeek Harness 使用建议

- **加载与引用**：`skill("geoserver-cloud")` 加载；技能目录只读，compose/values 覆写文件写到会话工作区。
- **执行环境**：命令交给 dsh 的 `pwsh`（Windows 无 `wget`，改 `curl.exe -LO`）；先用 `docker version`、`helm version`、`kubectl version --client` 确认工具在 PATH。
- **先探测版本**：`curl.exe -s -u admin:geoserver http://localhost:9090/geoserver/cloud/rest/about/version.json` 读 GeoServer 版本；`curl.exe -s http://localhost:9090/actuator/health` 取 `{"status":"UP"}`（被 profile 关掉时改用 `kubectl -n gis get pods` 判活）。
- **验证产物**：部署后逐服务探活，再经网关 `.../rest/workspaces.json` 与一次 WMS `GetMap` 走通全链路；`docker compose ps` 显示 Up 不等于 OGC 服务可用。
- **排障顺序**：502 → 查 Consul 注册与目标服务健康（`kubectl -n gis logs deploy/<wms>`）；配置不生效 → 查 RabbitMQ 与 `GEOSERVER_BUS_ENABLED`；瓦片 404 → 查 gwc 是否部署、`GEOSERVER_BASE_PATH` 前缀是否一致。
- **安全与权限**：`admin:geoserver`、`PGCONFIG_PASSWORD`、RabbitMQ 口令不要回显到报告；`docker compose down -v`、`helm uninstall`、删 PVC 或 PgConfig schema 会丢配置，先向用户确认并备份。
- **先本地复现**：能在 docker compose 复现的问题再上 K8s；镜像标签与 chart 版本保持同一版本号（3.0.2），避免网关与服务错配。

## 相关技能

- **geoserver** — GeoServer 单体服务器：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **geoserver-rest-api** — REST API 自动化管理：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)

## 参考资源

- 文档：<https://geoserver.org/geoserver-cloud/>
- 仓库：<https://github.com/geoserver/geoserver-cloud>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/geoserver-cloud/>
