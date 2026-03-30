---
name: Admin.NET 前端
description: Admin.NET 前端基于 Vue3 + Element Plus + Vite5 + TypeScript 构建的企业级中后台管理界面，提供完整的权限管理、动态路由、国际化、主题切换、代码生成、表单构建器等功能模块。
---

> **项目地址：** <https://github.com/znlgis/Admin.NET>
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

## 核心模块

### API 服务调用

前端 API 调用分为两种模式：

#### 1. 自动生成的 API 服务（`src/api-services/`）

通过 `api_build/` 脚本从后端 Swagger JSON 自动生成 TypeScript API 客户端：

```bash
# 生成 API 服务代码
cd api_build
node index.js
```

生成的代码按后端服务模块组织，可直接调用：

```typescript
import { getAPI } from '/@/utils/axios-utils';
import { SysUserApi } from '/@/api-services/api';

// 获取用户列表
const res = await getAPI(SysUserApi).apiSysUserPagePost(queryParams);

// 新增用户
await getAPI(SysUserApi).apiSysUserAddPost(userData);

// 删除用户
await getAPI(SysUserApi).apiSysUserDeletePost({ id: userId });
```

#### 2. 手写 API 调用（`src/api/`）

对于自定义或简单场景，直接使用封装的 axios：

```typescript
import request from '/@/utils/request';

// GET 请求
export const getMyData = (params: object) => {
    return request({
        url: '/api/myService/list',
        method: 'get',
        params,
    });
};

// POST 请求
export const addMyData = (data: object) => {
    return request({
        url: '/api/myService/add',
        method: 'post',
        data,
    });
};
```

---

### 路由与菜单

Admin.NET 前端采用 **动态路由** 方案，菜单和路由信息从后端接口获取：

```typescript
// 登录后获取菜单数据 → 动态添加路由
// 路由元信息定义
interface RouteMeta {
    title: string;           // 菜单名称
    icon?: string;           // 菜单图标
    isHide?: boolean;        // 是否隐藏
    isKeepAlive?: boolean;   // 是否缓存
    isAffix?: boolean;       // 是否固定标签
    isLink?: string;         // 外链地址
    isIframe?: boolean;      // 是否内嵌 iframe
    auth?: string[];         // 按钮权限标识数组
}
```

#### 添加新页面

1. 在 `src/views/` 下新建目录和 `.vue` 文件
2. 在后端管理界面中配置菜单（指定路由路径和组件路径）
3. 前端自动加载，无需手动注册路由

---

### 状态管理（Pinia）

```typescript
// src/stores/ 下按功能组织 store
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
    state: () => ({
        userInfo: {} as UserInfo,
        token: '',
    }),
    actions: {
        async login(data: LoginData) {
            const res = await loginApi(data);
            this.token = res.data.accessToken;
            this.userInfo = res.data.userInfo;
        },
        async logout() {
            this.token = '';
            this.userInfo = {} as UserInfo;
        },
    },
});
```

---

### 权限控制

#### 按钮级权限指令

```vue
<template>
  <!-- 通过 v-auth 指令控制按钮显示 -->
  <el-button v-auth="'sysUser:add'" type="primary">新增用户</el-button>
  <el-button v-auth="'sysUser:edit'" type="warning">编辑</el-button>
  <el-button v-auth="'sysUser:delete'" type="danger">删除</el-button>
</template>
```

#### 编程式权限判断

```typescript
import { useUserStore } from '/@/stores/user';

const userStore = useUserStore();
if (userStore.userInfo.authBtnList.includes('sysUser:add')) {
    // 有权限
}
```

---

### 国际化（i18n）

```
Web/lang/
├── zh-cn.ts    # 简体中文
├── en.ts       # 英语
└── ...         # 其他语言
```

```typescript
// 在组件中使用
import { useI18n } from 'vue-i18n';
const { t } = useI18n();
// 模板中：{{ $t('message.title') }}
```

---

### SignalR 实时通讯

前端通过 `@microsoft/signalr` 与后端 Hub 建立长连接：

```typescript
import * as signalR from '@microsoft/signalr';

const connection = new signalR.HubConnectionBuilder()
    .withUrl('/hubs/onlineUser', {
        accessTokenFactory: () => token,
    })
    .withAutomaticReconnect()
    .build();

// 接收在线用户变更
connection.on('onlineUserChanged', (data) => {
    console.log('在线用户更新:', data);
});

// 接收系统通知
connection.on('receiveNotice', (notice) => {
    ElNotification({ title: notice.title, message: notice.content });
});

await connection.start();
```

---

## 页面开发模板

### 标准 CRUD 页面

```vue
<template>
  <div class="my-page-container">
    <!-- 搜索区域 -->
    <el-card shadow="hover">
      <el-form :model="queryParams" :inline="true">
        <el-form-item label="名称">
          <el-input v-model="queryParams.name" placeholder="请输入名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><ele-Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><ele-Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮 -->
    <el-card shadow="hover" style="margin-top: 8px">
      <el-button v-auth="'myBiz:add'" type="primary" @click="openAddDialog">
        <el-icon><ele-Plus /></el-icon> 新增
      </el-button>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button v-auth="'myBiz:edit'" type="warning" size="small"
              @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button v-auth="'myBiz:delete'" type="danger" size="small"
              @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:currentPage="queryParams.page"
        v-model:page-size="queryParams.pageSize"
        :total="total"
        @current-change="handleQuery"
        @size-change="handleQuery"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { getAPI } from '/@/utils/axios-utils';
import { MyBizApi } from '/@/api-services/api';

const loading = ref(false);
const tableData = ref([]);
const total = ref(0);
const queryParams = ref({
    name: '',
    page: 1,
    pageSize: 20,
});

const handleQuery = async () => {
    loading.value = true;
    const res = await getAPI(MyBizApi).apiMyBizPagePost(queryParams.value);
    tableData.value = res.data.result?.items ?? [];
    total.value = res.data.result?.total ?? 0;
    loading.value = false;
};

const resetQuery = () => {
    queryParams.value = { name: '', page: 1, pageSize: 20 };
    handleQuery();
};

const handleDelete = (row: any) => {
    ElMessageBox.confirm('确定删除吗？', '提示', { type: 'warning' }).then(async () => {
        await getAPI(MyBizApi).apiMyBizDeletePost({ id: row.id });
        ElMessage.success('删除成功');
        handleQuery();
    });
};

onMounted(() => {
    handleQuery();
});
</script>
```

---

## 常用组件

| 组件 | 包 / 路径 | 用途 |
|------|----------|------|
| `el-table` / `el-form` / `el-dialog` | Element Plus | 表格、表单、对话框 |
| `el-tree` / `el-tree-select` | Element Plus | 树形选择（机构、菜单） |
| `el-upload` | Element Plus | 文件上传 |
| `@wangeditor/editor` | wangEditor | 富文本编辑器 |
| `md-editor-v3` | md-editor-v3 | Markdown 编辑器 |
| `monaco-editor` | Monaco Editor | 代码编辑器 |
| `echarts` / `echarts-gl` | ECharts 6 | 图表与 3D 可视化 |
| `vform3-builds` | VForm3 | 在线表单构建器 |
| `vue-plugin-hiprint` / `print-js` | hiprint | 打印与报表 |
| `@vue-office/pdf` / `excel` / `docx` | vue-office | Office 文件预览 |
| `logicflow` | LogicFlow | 流程图编辑 |
| `relation-graph` | relation-graph | 关系图可视化 |
| `json-editor-vue` | json-editor-vue | JSON 编辑器 |
| `vue-grid-layout` | vue-grid-layout | 网格拖拽布局 |
| `vue-draggable-plus` | vue-draggable-plus | 拖拽排序 |
| `splitpanes` | splitpanes | 分割面板 |
| `cropperjs` | cropperjs | 图片裁剪 |
| `xlsx-js-style` | xlsx-js-style | Excel 处理 |
| `mqtt` | mqtt 5 | MQTT 物联网通讯 |
| `sm-crypto-v2` | sm-crypto-v2 | 国密 SM2/SM3/SM4 |

---

## 样式与主题

- **CSS 预处理器：** SASS
- **主题方案：** Element Plus 主题变量 + 自定义 CSS 变量
- **暗黑模式：** 支持亮色/暗色主题切换
- **布局模式：** 支持多种布局（经典、横向、分栏、混合）

```scss
// 自定义主题变量示例
:root {
    --el-color-primary: #409eff;
    --next-bg-main-color: #f0f2f5;
}
```

---

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

## 参考链接

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
