---
name: docker-compose
description: "Use when orchestrating multi-container Docker applications from a single declarative compose.yaml — defining services, networks, and volumes, then building, starting, and stopping them as one unit. Covers image/build, ports, volumes, environment, depends_on, healthcheck, profiles, and the docker compose CLI."
tags:
  - docker
  - docker-compose
  - containers
  - orchestration
  - yaml
  - devops
  - deployment
  - healthcheck
  - profiles
---

> **项目地址：** <https://github.com/docker/compose>
>
> **官方文档：** <https://docs.docker.com/compose/>
>
> **许可证：** Apache-2.0 ｜ **最新版本：** v5.6.0

## 概述

Docker Compose 是定义和运行多容器 Docker 应用的工具。它用单个 YAML 文件（默认 `compose.yaml`）描述应用的服务、网络与卷，再用一条命令统一构建、启动、停止和查看。Compose 是 Compose Specification 的参考实现，旧的 2.x / 3.x 文件格式已并入统一规范，不再需要顶层 `version:` 字段。它面向单机（单 Docker 引擎）编排，是开发环境与单服务器部署的常用方案。

主要能力：

- **声明式编排**：在 `compose.yaml` 中定义 `services` / `networks` / `volumes`，配置即代码
- **生命周期管理**：`up` / `down` / `ps` / `logs` / `exec` 统一管理全部容器
- **与 Dockerfile 协作**：`build` 从源码构建镜像，`image` 直接拉取现成镜像
- **配置注入**：`environment` / `env_file` / `.env` 配合变量插值
- **启动顺序控制**：`depends_on` + `healthcheck` 等待依赖就绪
- **分组开关**：`profiles` 按场景启用调试或工具类服务
- **多文件叠加**：`-f base.yaml -f override.yaml` 按环境分层覆盖

---

## 环境准备

Compose v2+ 以插件形式随 Docker CLI 提供，命令为 `docker compose`（空格，区别于已停止维护的旧版 `docker-compose`）。

### Docker Desktop（Windows / macOS）

- 安装 Docker Desktop 即自带 Compose 插件与 Docker Engine，无需单独安装。
- 启动 Docker Desktop 后，终端即可使用 `docker compose`。

### Linux（Docker Engine + compose 插件）

```bash
# Debian / Ubuntu
sudo apt-get update
sudo apt-get install docker-compose-plugin

# RHEL / CentOS / Fedora（dnf 或 yum）
sudo dnf install docker-compose-plugin
# 或
sudo yum install docker-compose-plugin
```

### 验证

```bash
docker compose version
# 预期输出：Docker Compose version v5.6.0
```

> 独立的 `docker-compose`（v1，Python 实现）已停止维护，请使用 v2+ 的 `docker compose` 子命令。

---

## 核心 API/命令

### compose.yaml 顶层结构

```yaml
name: myapp            # 项目名，默认取所在目录名
services:              # 必填：服务（容器）集合
  web:
    image: nginx:1.27
networks:              # 可选：自定义网络
  frontend:
volumes:               # 可选：命名卷，供多个服务复用
  db-data:
```

- `services`：每个条目定义一个容器及其运行时配置
- `networks`：定义服务之间通信的网络，默认自动创建 `default` 网络
- `volumes`：定义命名卷；跨服务复用的卷必须在此声明
- `configs` / `secrets`：挂载配置文件与敏感数据（可选）

### 服务常用字段

```yaml
services:
  web:
    image: nginx:1.27                 # 直接使用现成镜像
    # build: .                        # 或从 Dockerfile 构建（二选一）
    ports:
      - "8080:80"                     # 短语法 HOST:CONTAINER
    volumes:
      - ./html:/usr/share/nginx/html  # bind mount（宿主机目录）
      - static:/app/static            # named volume（需顶层声明）
    environment:
      APP_ENV: production
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
```

`build` 段可指定上下文、Dockerfile、构建参数与多阶段目标：

```yaml
services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
      args:
        NODE_ENV: production
      target: builder
```

### 健康检查

```yaml
services:
  db:
    image: postgres:18
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 10s
      retries: 5
      start_period: 30s
```

- `test`：探活命令，`CMD` 直接执行，`CMD-SHELL` 经 shell 执行
- `interval` / `timeout` / `retries` / `start_period`：探测间隔、超时、重试次数、启动宽限期
- `disable: true` 或 `test: ["NONE"]` 可关闭健康检查

### 依赖与启动顺序

- 短语法 `depends_on: [db]` 只保证启动先后，**不等待依赖就绪**。
- 长语法 `condition` 支持三种条件：

```yaml
services:
  web:
    depends_on:
      db:
        condition: service_healthy       # 等待 db 健康
        restart: true                    # db 重启时 web 一并重启
      redis:
        condition: service_started       # 仅等待启动
      migrate:
        condition: service_completed_successfully  # 等待一次性任务成功退出
```

### profiles 分组

```yaml
services:
  app:
    image: myapp            # 无 profile，默认始终启动
  phpmyadmin:
    image: phpmyadmin
    profiles: [debug]       # 仅激活 debug 时才启动
```

```bash
docker compose --profile debug up -d
COMPOSE_PROFILES=debug docker compose up -d
docker compose --profile "*" up -d      # 启用全部 profile
```

### 环境变量与 .env

- `.env` 默认位于项目目录（与 `compose.yaml` 同级）。
- 插值语法：`${VAR}`、`${VAR:-default}`（空则取默认）、`${VAR:?err}`（缺失即报错）；`$$` 转义为字面 `$`。
- 优先级（高到低）：shell 环境变量 → `--env-file` 指定文件 → `.env` 文件。
- 服务级 `environment` 的取值优先级高于 `env_file`。

```yaml
services:
  web:
    image: "webapp:${TAG:-latest}"
```

```bash
docker compose --env-file .env.prod config --environment
```

### 常用命令

```bash
docker compose up -d                 # 构建并后台启动全部服务
docker compose up -d --build         # 强制重建镜像后再启动
docker compose down                  # 停止并删除容器与网络
docker compose down -v               # 同时删除命名卷（数据会丢失）
docker compose ps                    # 查看容器状态
docker compose logs -f web           # 跟踪指定服务日志
docker compose exec web sh           # 在运行中的容器内执行命令
docker compose run --rm web sh       # 一次性运行（不占用已发布端口）
docker compose build                 # 构建 / 重建镜像
docker compose pull                  # 拉取服务镜像
docker compose config                # 渲染并校验最终配置
docker compose restart web           # 重启服务
docker compose stop / start          # 停止 / 启动
docker compose cp ./x.txt web:/tmp/  # 在容器与宿主间复制文件
docker compose watch                 # 监听变更并同步 / 重建
```

---

## 典型工作流

### 场景一：从零编排 Web + 数据库

```bash
# 目录结构
# myapp/
# ├── compose.yaml
# ├── .env
# └── api/Dockerfile

# 1. 构建并启动
docker compose up -d --build

# 2. 校验最终配置与状态
docker compose config
docker compose ps

# 3. 观察日志
docker compose logs -f api

# 4. 进入容器调试
docker compose exec db psql -U postgres

# 5. 清理（含数据卷）
docker compose down -v
```

### 场景二：多文件分环境叠加

```bash
# 基础文件 + 生产覆盖文件
docker compose -f compose.yaml -f compose.production.yaml up -d

# 仅重建并替换单个服务，不重启其依赖
docker compose build web
docker compose up --no-deps -d web
```

---

## 最佳实践

1. 生产环境移除源码 bind mount，使用镜像内已构建的代码。
2. 为长驻服务设置 `restart: unless-stopped` 或 `always`，减少停机。
3. 为被依赖服务配置 `healthcheck`，并用 `depends_on.condition: service_healthy` 等待就绪。
4. 用 `deploy.resources.limits` 限制 `cpus` 与 `memory`。
5. 为日志配置 `max-size` / `max-file` 轮转，避免磁盘被写满。
6. 密码、令牌等敏感数据用 `secrets` 或 `env_file`，不要硬编码进 `compose.yaml`。
7. 固定镜像 tag（含摘要更佳），避免 `latest` 漂移导致环境不一致。
8. 用 `profiles` 区分核心服务与调试 / 运维工具服务。
9. 在 CI 中运行 `docker compose config` 校验语法与插值。

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 512M
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 提示 `docker: 'compose' is not a docker command` | 安装 compose 插件（v2+），并确认使用 `docker compose`（空格）而非旧版 `docker-compose` |
| `ports` 报端口被占用 | 修改宿主机端口，或排查占用进程后释放 |
| `depends_on` 后应用仍连接失败 | 短语法不等待就绪，改用 `condition: service_healthy` 并配置 `healthcheck` |
| `down` 后数据库数据丢失 | `down -v` 会删除命名卷；日常清理不要加 `-v`，或先备份卷 |
| 修改代码后容器未更新 | 用 `up -d --build` 重建，或使用 `docker compose watch` |
| `.env` 中的变量未生效 | 确认 `.env` 与 `compose.yaml` 同目录；检查是否被 shell 同名变量覆盖 |
| 顶层 `version` 出现告警 | Compose Specification 已弃用 `version:`，删除该字段 |
| Windows 下路径挂载失败 | 使用绝对路径或 `${PWD}`，并在 Docker Desktop 中开启文件共享 |
| 容器日志占满磁盘 | 配置 `logging.options.max-size` / `max-file` 做轮转 |
| `profiles` 服务未启动 | 启动时加 `--profile <名>` 或设置 `COMPOSE_PROFILES` |
| 资源限制未生效 | 使用 `deploy.resources.limits`，而非旧版的 `mem_limit` / `cpus` |

---

## 参考资源

- 官方文档：<https://docs.docker.com/compose/>
- Compose 文件参考：<https://docs.docker.com/reference/compose-file/>
- CLI 命令参考：<https://docs.docker.com/reference/cli/docker/compose/>
- 项目仓库：<https://github.com/docker/compose>
- Compose 规范：<https://github.com/compose-spec/compose-spec>

---

## 相关技能

- [geoserver-cloud](../../gis/geoserver-cloud/SKILL.md) — GeoServer 云原生微服务，本地开发或单机部署可用 Compose 编排。
- [billionmail](../billionmail/SKILL.md) — 自托管邮件营销平台，官方推荐以 `docker compose` 部署。
- [ruoyi-cloud](../ruoyi-cloud/SKILL.md) — Java 微服务脚手架，常用 Compose 编排 Nacos、MySQL 等依赖中间件。

---

## AI 使用建议

### 推荐工作流

1. 先写 `compose.yaml` 骨架（`name` / `services` / `networks` / `volumes`），再逐服务补充字段。
2. 被依赖服务先加 `healthcheck`，再用 `depends_on.condition` 串联启动顺序。
3. 每次改动后运行 `docker compose config` 校验，再执行 `up -d`。
4. 敏感配置放入 `.env` / `env_file`，不写进版本库。

### 关键模式与常见陷阱

- **端口语义**：`ports` 是发布到宿主机的映射；`expose` 仅声明内部端口，不对外发布。
- **卷类型**：`./path:/x` 为 bind mount，单独 `/x` 为匿名卷，命名卷需在顶层 `volumes` 声明。
- **插值时机**：`compose.yaml` 中的 `${VAR}` 由 Compose 解析；容器内需用 `$$VAR` 交给 shell。
- **就绪 vs 运行**：`depends_on` 只保证容器运行，健康检查才保证服务可用。
- **多文件合并**：后指定的 `-f` 文件覆盖前者；`config` 可查看合并后的最终结果。

### 如何选择方案

| 场景 | 推荐方案 |
|------|---------|
| 单机多容器开发或小规模生产 | Docker Compose |
| 多节点集群 / 自动扩缩容 | Kubernetes 或 Swarm |
| 仅运行单个容器 | `docker run` |
| 需要密钥托管与集中管理 | Compose `secrets` 或外部密钥管理服务 |
