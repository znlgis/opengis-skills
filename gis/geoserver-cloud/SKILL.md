---
name: geoserver-cloud
description: "Use when deploying GeoServer on Kubernetes as cloud-native microservices with auto-scaling, service discovery, and centralized configuration. GeoServer Cloud: break monolithic GeoServer into independently scalable WMS/WFS/WCS services."
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
> **Docker Hub：** <https://hub.docker.com/u/geoservercloud>（镜像标签与 GeoServer 主版本对应，如 `3.0.0`）
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

## 快速启动（docker-compose）

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
# Chart：camptocamp/helm-geoserver-cloud（chart 名 geoservercloud，最新 3.0.1）
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
>     version: 3.0.1
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

## 网关默认路由

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
  geoservercloud/geoserver-cloud-wms:3.0.0
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

## AI 使用建议

### 推荐工作流

1. **确定架构**：根据业务需求选择配置后端（生产推荐 PgConfig）
2. **部署基础设施**：先部署 RabbitMQ + PostgreSQL（PgConfig 目录库），再启动微服务
3. **启动服务**：下载官方稳定版 docker-compose 文件或用 Helm Chart 部署
4. **验证服务**：通过 Gateway (`localhost:9090/geoserver/cloud`) 访问 Web UI
5. **配置监控**：启用 Prometheus + Grafana 监控各微服务状态
6. **弹性伸缩**：按负载独立扩缩 WMS/WFS 等服务的副本数

### 关键注意事项

- **启动顺序**：先启动 discovery/Consul → config → 数据库/RabbitMQ → 各业务服务
- **配置同步**：确保 `GEOSERVER_BUS_ENABLED=true` 且 RabbitMQ 可达
- **路径前缀**：默认 `GEOSERVER_BASE_PATH=/geoserver/cloud`，构造服务 URL 时不要漏掉
- **PgConfig 一致性**：多副本共享同一个 PgConfig 数据库实现强一致
- **JVM 独立调优**：每个微服务根据负载独立设置 `-Xmx`，避免 OOM
- **不部署不需要的服务**：如不使用 WPS/WCS，直接从 docker-compose 中移除

## 相关技能

- **geoserver** — GeoServer 单体服务器：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **geoserver-rest-api** — REST API 自动化管理：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)

## 参考资源

- 文档：<https://geoserver.org/geoserver-cloud/>
- 仓库：<https://github.com/geoserver/geoserver-cloud>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/geoserver-cloud/>
