# Admin.NET Frontend Core Modules Reference

Frontend core module details split from SKILL.md.

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

