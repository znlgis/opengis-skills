---
name: admin-net-frontend
description: "Use when building Vue 3 admin dashboard frontends with dynamic routing, permission-based menus, and CRUD page generation. Admin.NET Frontend: Vue 3 + Vite + TypeScript admin UI for Admin.NET backend."
tags:
  - vue
  - vue3
  - typescript
  - element-plus
  - vite
  - admin
  - frontend
---

> **项目地址（上游）：** <https://github.com/zuohuaijun/Admin.NET>
>
> **znlgis 维护分支：** <https://github.com/znlgis/Admin.NET>
>
> **前端代码目录：** `Web/`（Vue3 应用）
>
> **在线文档：** <https://adminnet.top/>
>
> **演示环境：** <https://demo.adminnet.top>（账号：superAdmin.NET / 密码：Admin.NET++010101）
>
> **许可证：** MIT

## 概述

Admin.NET 前端基于 **vue-next-admin** 模板二次开发，采用 **Vue 3 Composition API** + **TypeScript** + **Element Plus** + **Vite 5** 技术栈。项目提供完整的企业级中后台管理界面，包括登录认证、动态菜单/路由、RBAC 权限控制、多语言、主题切换、SignalR 实时通讯等能力。

**核心技术栈：**
- **框架：** Vue 3.5+（Composition API + `<script setup>`）
- **语言：** TypeScript 5.x
- **构建：** Vite 5+ / pnpm
- **UI 组件：** Element Plus 2.x
- **路由：** Vue Router 5
- **状态管理：** Pinia 3
- **国际化：** vue-i18n 11
- **HTTP 客户端：** Axios
- **图表：** ECharts 6
- **实时通讯：** @microsoft/signalr

---

## 项目结构

```
Web/
├── public/                        # 公共静态资源
├── lang/                          # 国际化语言文件
├── api_build/                     # API 代码自动生成脚本
├── scripts/                       # 构建辅助脚本
├── src/
│   ├── api/                       # 手写 API 调用（axios 封装）
│   ├── api-services/              # 自动生成的 API 服务（对应后端 Swagger）
│   ├── api-plugins/               # 插件相关的 API 服务
│   ├── assets/                    # 静态资源（图片、样式）
│   ├── components/                # 全局公共组件
│   ├── directive/                 # 自定义指令（如权限指令）
│   ├── layout/                    # 布局组件（侧边栏、头部、标签页等）
│   ├── router/                    # 路由配置
│   ├── stores/                    # Pinia 状态管理
│   ├── theme/                     # 主题样式
│   ├── types/                     # TypeScript 类型定义
│   ├── utils/                     # 工具函数
│   ├── views/                     # 页面视图
│   │   ├── login/                 # 登录页
│   │   ├── home/                  # 首页/仪表盘
│   │   ├── system/                # 系统管理页面集合
│   │   ├── approvalFlow/          # 审批流程
│   │   ├── mqttx/                 # MQTT 客户端
│   │   ├── elive/                 # 视频监控
│   │   ├── about/                 # 关于页
│   │   └── error/                 # 错误页（403/404/500）
│   ├── App.vue                    # 根组件
│   └── main.ts                    # 应用入口
├── index.html                     # HTML 入口
├── package.json                   # 依赖配置
├── vite.config.ts                 # Vite 构建配置
├── tsconfig.json                  # TypeScript 配置
├── eslint.config.mjs              # ESLint 配置
├── .prettierrc.cjs                # Prettier 配置
├── .env                           # 通用环境变量
├── .env.development               # 开发环境变量
└── .env.production                # 生产环境变量
```

---

## 环境准备与运行

### 前置要求

- **Node.js：** >= 18.0.0
- **包管理器：** pnpm（推荐 10.x）

### 安装与启动

```bash
cd Web

# 安装依赖
pnpm install

# 开发模式运行
pnpm run dev

# 生产构建
pnpm run build
```

### 环境变量

```bash
# .env（通用）
VITE_PORT = 2800
VITE_OPEN = false
VITE_APP_TITLE = Admin.NET

# .env.development（开发环境）
VITE_API_URL = http://localhost:5005

# .env.production（生产环境）
VITE_API_URL = /
```

---

> 核心模块的完整说明见 [reference/core-modules.md](reference/core-modules.md)
> 页面开发模板、常用组件与样式主题的完整内容见 [reference/page-templates.md](reference/page-templates.md)

## 构建与部署

### 生产构建

```bash
pnpm run build
# 产物输出到 dist/ 目录
```

### Nginx 部署配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;  # SPA 路由支持
    }

    location /api {
        proxy_pass http://backend-server:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /hubs {
        proxy_pass http://backend-server:5005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";    # WebSocket 支持
    }
}
```

---

## AI 使用建议

### 推荐工作流

1. **环境准备**：Node.js >= 18 + pnpm → `pnpm install` → `pnpm run dev`
2. **新增页面**：`src/views/` 下新建目录和 `.vue` 文件 → 后端管理界面配菜单（路由路径 + 组件路径）→ 前端自动加载
3. **API 对接**：后端 Swagger 更新后运行 `api_build` 脚本自动生成 TypeScript API 客户端 → 用 `getAPI(XxxApi)` 调用
4. **权限控制**：后端菜单配置按钮权限标识 → 前端用 `v-auth="'xxx:action'"` 指令控制按钮显示
5. **构建部署**：`pnpm run build` → `dist/` 产物 → Nginx 部署（SPA try_files + API 代理 + WebSocket /hubs）

### 关键模式与常见陷阱

- **包管理器**：必须用 `pnpm`，项目依赖 `pnpm-workspace.yaml`，npm/yarn 可能失败
- **环境变量前缀**：Vite 项目中自定义环境变量必须以 `VITE_` 开头，否则 `import.meta.env` 读不到
- **路由组件路径**：后端菜单配置的组件路径对应 `src/views/` 下的文件路径（不含 `.vue` 后缀），大小写敏感
- **权限标识一致性**：前端 `v-auth` 指令中的标识必须与后端菜单配置中的按钮权限标识完全一致
- **API 自动生成**：修改后端接口后务必重新运行 `api_build` 脚本，否则类型定义过期
- **SignalR 代理**：Nginx 需配置 WebSocket 代理（`/hubs` 路径），否则实时通知不工作

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 配合 Admin.NET 后端 | Admin.NET 前端（开箱即用） |
| 独立 Vue3 后台项目 | 直接用 vue-next-admin 模板 + Element Plus |
| 仅需简单管理界面 | vue-pure-admin / naive-ui-admin |
| 移动端/小程序 | uni-app / Taro |

---

## 注意事项

1. **包管理器**：务必使用 `pnpm`，项目使用 `pnpm-workspace.yaml` 管理
2. **API 自动生成**：修改后端接口后需重新运行 `api_build` 脚本更新前端 API 类型定义
3. **权限标识**：前端 `v-auth` 指令中使用的权限标识需与后端菜单配置中的按钮权限一致
4. **路由组件路径**：后端菜单配置的组件路径对应 `src/views/` 下的文件路径（不含后缀）
5. **环境变量前缀**：Vite 项目中自定义环境变量必须以 `VITE_` 开头
6. **国密加密**：登录密码等敏感数据前端使用 `sm-crypto-v2` 做 SM2 加密后传输
7. **SignalR 连接**：需正确配置 Nginx 代理 WebSocket（`/hubs` 路径）
8. **Node 版本**：要求 Node.js >= 18.0.0

---

## 相关技能

- **admin-net-backend** — Admin.NET 配套后端（.NET + Furion + SqlSugar）：[../admin-net-backend/SKILL.md](../admin-net-backend/SKILL.md)
- **furion** — 后端使用的 .NET Web 框架，前端通过其动态 API 自动生成接口：[../furion/SKILL.md](../furion/SKILL.md)

---

## 参考资源

- **GitHub：** <https://github.com/znlgis/Admin.NET>
- **GitHub 镜像：** <https://github.com/zuohuaijun/Admin.NET>
- **Gitee 镜像：** <https://gitee.com/zuohuaijun/Admin.NET>
- **GitCode 镜像：** <https://gitcode.com/zuohuaijun/Admin.NET>
- **在线文档：** <https://adminnet.top/>
- **Vue 3 文档：** <https://vuejs.org/>
- **Element Plus 文档：** <https://element-plus.org/>
- **Vite 文档：** <https://vitejs.dev/>
- **Pinia 文档：** <https://pinia.vuejs.org/>
- **vue-next-admin：** <https://lyt-top.gitee.io/vue-next-admin-doc-preview/>
