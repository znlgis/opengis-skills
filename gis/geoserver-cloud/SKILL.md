---
name: geoserver-cloud
description: GeoServer Cloud 是面向云原生的 GeoServer 微服务化版本，将单体 GeoServer 拆分为独立的 OGC 服务（wms/wfs/wcs/wps/gwc/rest/web-ui），通过 Spring Cloud + 配置中心 + 消息总线在 Kubernetes/Docker 上水平伸缩，特别适合大流量、多租户场景。
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
> **Docker Hub：** <https://hub.docker.com/u/geoservercloud>
>
> **许可证：** GPL-2.0

## 概述

GeoServer Cloud（GS Cloud）：

- **微服务架构**：每种 OGC 服务为独立 Spring Boot 应用
- **配置同步**：`spring-cloud-bus` + RabbitMQ 实时同步
- **配置后端**：本地目录 / **PgConfig（推荐）** / JDBCConfig
- **可观测**：Actuator + Prometheus + Sleuth Tracing
- **容器友好**：官方镜像、Helm Chart、docker-compose
- **完全兼容社区版**：相同 Web UI、SLD、数据存储

---

## 服务拆分

| 服务 | 镜像 | 用途 |
|------|------|------|
| `gateway` | `geoservercloud/geoserver-cloud-gateway` | 网关 |
| `discovery` | `geoservercloud/geoserver-cloud-discovery` | 服务发现 |
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
git clone https://github.com/geoserver/geoserver-cloud.git
cd geoserver-cloud/compose
docker compose -f compose.yml -f catalog-pgconfig.yml up -d
# Gateway: http://localhost:9090/geoserver
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
GEOSERVER_BACKEND_PGCONFIG_ENABLED: "true"
GEOSERVER_BACKEND_PGCONFIG_JDBCURL: "jdbc:postgresql://pg:5432/gsconfig"
GEOSERVER_BACKEND_PGCONFIG_USERNAME: "gs"
GEOSERVER_BACKEND_PGCONFIG_PASSWORD: "gs"
```

---

## Kubernetes（Helm）

```bash
helm repo add geoserver-cloud https://geoserver.github.io/geoserver-cloud/
helm install gs geoserver-cloud/geoserver-cloud \
  -n gis --create-namespace \
  --set rabbitmq.enabled=true \
  --set postgresql.enabled=true \
  --set wms.replicaCount=3 \
  --set wfs.replicaCount=2

kubectl scale deploy gs-wms -n gis --replicas=10
```

---

## 网关默认路由

| 路径 | 转发到 |
|------|--------|
| `/geoserver/wms` | wms |
| `/geoserver/wfs` | wfs |
| `/geoserver/wcs` | wcs |
| `/geoserver/wps` | wps |
| `/geoserver/gwc` | gwc |
| `/geoserver/rest` | rest |
| `/geoserver/web` | web-ui |

---

## 配置同步

任意修改 → REST/web-ui 发送 `RemoteApplicationEvent` 到 RabbitMQ → 所有副本订阅刷新本地 `Catalog`，秒级一致。

```yaml
spring:
  cloud.bus.enabled: true
  rabbitmq.host: rabbitmq
```

---

## 监控

```yaml
management:
  endpoints.web.exposure.include: "*"
  metrics.export.prometheus.enabled: true
```

- Prometheus 抓 `/actuator/prometheus`
- 日志 STDOUT，配合 EFK / Loki
- Tracing：Sleuth + Zipkin/Tempo

---

## 与单体兼容

直接挂载现有 GeoServer 数据目录平滑迁移：

```bash
docker run -v /mnt/gsdata:/opt/app/data_dir geoservercloud/geoserver-cloud-wms:...
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
| 配置不同步 | 检查 RabbitMQ + `spring.cloud.bus.enabled` |
| Web UI 改了 wms 没生效 | 检查事件订阅 |
| 启动顺序错乱 | `depends_on` + 健康检查；K8s 用 `initContainers` |
| OOM | 调整 `-Xmx`，按服务独立资源 |

---

## AI 使用建议

### 推荐工作流

1. **确定架构**：根据业务需求选择配置后端（生产推荐 PgConfig）
2. **部署基础设施**：先部署 RabbitMQ + PostgreSQL + Redis，再启动微服务
3. **启动服务**：使用 docker-compose 或 Helm Chart 一键部署
4. **验证服务**：通过 Gateway (`localhost:9090/geoserver`) 访问 Web UI
5. **配置监控**：启用 Prometheus + Grafana 监控各微服务状态
6. **弹性伸缩**：按负载独立扩缩 WMS/WFS 等服务的副本数

### 关键注意事项

- **启动顺序**：先启动 discovery → config → 数据库/RabbitMQ → 各业务服务
- **配置同步**：确保 `spring.cloud.bus.enabled=true` 且 RabbitMQ 可达
- **PgConfig 一致性**：多副本共享同一个 PgConfig 数据库实现强一致
- **JVM 独立调优**：每个微服务根据负载独立设置 `-Xmx`，避免 OOM
- **不部署不需要的服务**：如不使用 WPS/WCS，直接从 docker-compose 中移除

## 典型工作流

### 工作流 1：从零部署高可用 GeoServer Cloud

```bash
# 克隆仓库
git clone https://github.com/geoserver/geoserver-cloud.git
cd geoserver-cloud/compose

# 启动基础设施 + 所有微服务
docker compose -f compose.yml -f catalog-pgconfig.yml up -d

# 验证 Gateway 可访问
curl -u admin:geoserver http://localhost:9090/geoserver/rest/about/version.json

# 扩容 WMS 服务（3 副本）
docker compose up -d --scale wms=3
```

### 工作流 2：Kubernetes 生产部署 + 自动伸缩

```bash
# 添加 Helm 仓库
helm repo add geoserver-cloud https://geoserver.github.io/geoserver-cloud/
helm repo update

# 安装（含 RabbitMQ + PostgreSQL）
helm install gs geoserver-cloud/geoserver-cloud \
  -n gis --create-namespace \
  --set rabbitmq.enabled=true \
  --set postgresql.enabled=true \
  --set wms.replicaCount=3 \
  --set wfs.replicaCount=2

# 手动伸缩 WMS
kubectl scale deploy gs-wms -n gis --replicas=10
```

## 相关技能

- **geoserver** — GeoServer 单体服务器：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **geoserver-rest-api** — REST API 自动化管理：[../geoserver-rest-api/SKILL.md](../geoserver-rest-api/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)

## 参考资源

- 文档：<https://geoserver.org/geoserver-cloud/>
- 仓库：<https://github.com/geoserver/geoserver-cloud>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/geoserver-cloud/>
