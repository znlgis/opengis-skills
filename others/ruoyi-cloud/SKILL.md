---
name: ruoyi-cloud
description: RuoYi-Cloud 是 RuoYi 系列开源 Java 微服务版后台管理系统脚手架，基于 Spring Boot 3 + Spring Cloud + Spring Cloud Alibaba（Nacos/Sentinel/Seata）+ MyBatis Plus + Vue 3，提供完整 RBAC、网关、认证、配置中心、链路追踪、定时任务与代码生成，是国内 Java 微服务最流行的脚手架之一。
tags: java, spring-cloud, microservices, rbac, nacos
---

> **项目地址：** <https://gitee.com/y_project/RuoYi-Cloud>
>
> **GitHub 镜像：** <https://github.com/yangzongzhuan/RuoYi-Cloud>
>
> **官网：** <http://ruoyi.vip/>
>
> **文档：** <http://doc.ruoyi.vip/>
>
> **许可证：** MIT

## 概述

RuoYi-Cloud 主要特性：

- **Spring Cloud Alibaba**：Nacos（注册/配置）、Sentinel（熔断限流）、Seata（分布式事务）
- **网关**：Spring Cloud Gateway + 鉴权过滤器
- **认证**：JWT + Spring Security + OAuth2
- **业务模块**：RBAC（菜单/角色/权限/部门/用户）、字典、参数、日志、文件、定时任务、监控
- **代码生成**：单表/树表/主子表 → Mapper + Service + Controller + Vue 页面
- **前端**：Vue 3 + Vite + Element Plus + Pinia
- **DevOps**：Docker Compose 一键部署、SkyWalking / Prometheus 集成

---

## 模块结构

```
RuoYi-Cloud
├── ruoyi-gateway        # API 网关
├── ruoyi-auth           # 认证服务
├── ruoyi-modules
│   ├── ruoyi-system     # 系统模块
│   ├── ruoyi-gen        # 代码生成
│   ├── ruoyi-job        # 定时任务
│   └── ruoyi-file       # 文件服务
├── ruoyi-api            # 远程调用 Feign 接口
├── ruoyi-common         # 公共工具
├── ruoyi-visual
│   ├── ruoyi-monitor    # Spring Boot Admin
│   └── ruoyi-visual-name # Nacos / Sentinel UI 入口
└── ruoyi-ui             # Vue 3 前端
```

---

## 环境与依赖

| 组件 | 版本 |
|------|------|
| JDK | 17+（最新版）/ 8（老分支） |
| Maven | 3.9+ |
| MySQL | 5.7+ / 8.0 |
| Redis | 5.0+ |
| Nacos | 2.x |
| Sentinel | 1.8+ |
| Seata | 1.6+（可选） |
| Node.js | 18+ |

---

## 启动步骤

```bash
# 1. 克隆
git clone https://gitee.com/y_project/RuoYi-Cloud.git
cd RuoYi-Cloud

# 2. 数据库
mysql -u root -p < sql/ry_20240629.sql
mysql -u root -p < sql/ry_config_20240629.sql

# 3. Nacos：将 nacos/config 下 .yml 推送到 Nacos
#    或直接通过控制台导入 ZIP

# 4. 启动基础设施
docker compose -f docker/docker-compose.yml up -d  # 含 mysql/redis/nacos

# 5. 启动后端
mvn clean install -DskipTests
# 顺序：ruoyi-gateway → ruoyi-auth → ruoyi-modules-system → 其它

# 6. 前端
cd ruoyi-ui
npm install --registry=https://registry.npmmirror.com
npm run dev   # http://localhost:80
```

默认账号：`admin / admin123`。

---

## 配置中心（Nacos）

每个微服务启动时从 Nacos 拉取：

```
ruoyi-gateway-dev.yml
ruoyi-auth-dev.yml
ruoyi-system-dev.yml
application-dev.yml         # 公共
sentinel-ruoyi-gateway.json # Sentinel 限流规则
```

切换环境：`spring.profiles.active=dev|test|prod`。

---

## 网关与认证

请求流程：

```
Client → Gateway
  ├─ 路由匹配（lb://ruoyi-system）
  ├─ AuthFilter：从 Header 取 token，调 redis 校验
  ├─ Sentinel：限流 / 熔断
  └─ 转发到目标服务（带 user_key/user_id）
```

```yaml
# ruoyi-gateway-dev.yml
spring:
  cloud:
    gateway:
      routes:
        - id: ruoyi-system
          uri: lb://ruoyi-system
          predicates:
            - Path=/system/**
          filters:
            - StripPrefix=1
```

获取 token：

```bash
curl -X POST http://localhost:8080/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123","code":"x","uuid":"x"}'
```

---

## RBAC 权限

- 数据库：`sys_user / sys_role / sys_menu / sys_dept / sys_role_menu / sys_user_role`
- Spring Security：`@RequiresPermissions("system:user:list")`
- 前端：根据返回菜单/按钮动态渲染

```java
@PreAuthorize("@ss.hasPermi('system:user:edit')")
@PutMapping
public AjaxResult edit(@RequestBody SysUser user) { ... }
```

---

## Feign 远程调用

```java
@FeignClient(value = "ruoyi-system", contextId = "remoteUserService")
public interface RemoteUserService {
    @GetMapping("/user/info/{username}")
    R<LoginUser> getUserInfo(@PathVariable("username") String username);
}
```

---

## Sentinel 限流

```java
@SentinelResource(value = "listUser",
    blockHandler = "listUserBlock",
    fallback     = "listUserFallback")
public AjaxResult list() { ... }
```

控制台 `localhost:8718` 配置规则，热更新到 Nacos。

---

## Seata 分布式事务

```java
@GlobalTransactional(rollbackFor = Exception.class)
public void createOrder(...) {
    orderService.save(...);
    accountService.deduct(...);
    inventoryService.reduce(...);
}
```

需启动 Seata Server + 在每个微服务接入 `io.seata:seata-spring-boot-starter`。

---

## 代码生成

1. 设计表（添加 `t_` 前缀业务表）
2. 系统工具 → 代码生成 → 选表 → 编辑信息（生成路径/作者/包名/前端目录）
3. 下载 zip 或同步到 Maven 工程

生成内容：Entity / Mapper.xml / Mapper / Service / ServiceImpl / Controller + Vue 页面 + SQL（菜单 + 权限）。

---

## 定时任务（Quartz）

后台「系统监控 → 定时任务」 → 添加：

- Bean 名：`ryTask`
- 方法：`ryParams('test')`
- Cron：`0 0/5 * * * ?`

```java
@Component("ryTask")
public class RyTask {
    public void ryParams(String params) { /* ... */ }
}
```

---

## 日志与监控

- 操作日志、登录日志：`@Log(title = "...", businessType = ...)`
- Spring Boot Admin：`http://localhost:9100/`
- SkyWalking 集成：`-javaagent:skywalking-agent.jar`
- Prometheus / Micrometer

---

## Docker 部署

```bash
cd docker
sh deploy.sh save       # 构建并保存镜像
sh deploy.sh base       # mysql/redis/nacos
sh deploy.sh server     # 业务服务
sh deploy.sh web        # 前端
```

---

## 升级与定制

1. **保留扩展点**：新建模块 `ruoyi-modules-mybiz`，不要直接改 system
2. **统一基础包名**：`com.ruoyi` 替换为公司域名（IDE 重构）
3. **按需删除模块**：不需要 Seata 可移除依赖
4. **多租户**：基于 MyBatis Plus 拦截器或 ShardingSphere 改造

---

## 性能与最佳实践

1. **网关连接池**：调整 Reactor Netty 与下游 Feign
2. **Redis 缓存权限**：`@CacheEvict` 在权限变更时清空
3. **Nacos 双注册中心** + **配置版本灰度**
4. **慢 SQL**：MyBatis Plus + p6spy；EXPLAIN 调优
5. **链路追踪**：SkyWalking + 全链路日志 traceId

---

## AI 使用建议

### 推荐工作流

1. **启动基础设施**：Nacos + MySQL + Redis → Docker Compose 一键启动
2. **导入配置**：将 Nacos 配置导入到 Nacos 控制台（SQL 或 ZIP 导入）
3. **启动微服务**：按顺序启动 gateway → auth → system → gen → job → file
4. **新增业务模块**：`ruoyi-modules/` 下新建模块 → 注册到 Nacos → 网关配置路由
5. **代码生成**：设计表 → 代码生成工具 → 一键生成 Entity/Mapper/Service/Controller + Vue 页面

### 关键模式与常见陷阱

- **启动顺序**：必须先启 Nacos，再启 Gateway → Auth → 业务模块，否则服务发现失败
- **Nacos 命名空间**：确保所有微服务的 `namespace` 与 `group` 一致，否则无法发现
- **Token 过期**：Redis 中 token TTL 与 JWT 过期时间要保持一致；时间不同步会导致 401
- **分布式事务**：Seata `tx-service-group` 必须与 Nacos 配置一致，否则不回滚
- **新建模块隔离**：新建业务模块 `ruoyi-modules-mybiz`，不要直接修改 system 模块，方便升级
- **性能优化**：网关连接池调优 + Redis 缓存权限 + SkyWalking 全链路追踪

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| Java 微服务后台 | RuoYi-Cloud |
| .NET 微服务后台 | Admin.NET（单体/插件式） |
| 简单单体应用 | RuoYi（单体版） |
| 前端定制 | RuoYi-Cloud 自带 Vue3 前端，也可替换为 React/Angular |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 启动慢/服务发现不到 | 检查 Nacos 命名空间与 group 一致 |
| 鉴权失败 401 | Redis 中 token 过期；时间不同步 |
| 前端 401 反复 | 检查 axios 拦截器与刷新机制 |
| 分布式事务不回滚 | Seata `tx-service-group` 与配置中心一致 |
| 性能问题 | 网关 + 业务服务横向扩容；启用本地缓存 |

---

## 相关技能

- RuoYi-Cloud 是 Java 生态的独立技能。如需 .NET 生态的类似框架，可参考 Admin.NET 后端（Furion + SqlSugar），它在架构思想上与 RuoYi 类似但技术栈不同。

---

## 参考资源

- 文档：<http://doc.ruoyi.vip/>
- 仓库：<https://gitee.com/y_project/RuoYi-Cloud>
- 中文教程（znlgis）：<https://znlgis.github.io/others/tutorial/ruoyi-cloud/>