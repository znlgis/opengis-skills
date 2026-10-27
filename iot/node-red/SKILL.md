---
name: node-red
description: "Use when building IoT data flows and API integration with Node-RED low-code programming — inject/debug/function/change/switch nodes, the msg.payload message model, MQTT in/out broker configuration and pub/sub, HTTP in/out REST endpoints, context storage, subflows, node-red-dashboard panels, and settings.js configuration."
tags:
  - node-red
  - iot
  - low-code
  - mqtt
  - flow-programming
  - javascript
  - dashboard
  - automation
  - http-api
---

> **项目地址：** <https://github.com/node-red/node-red>
>
> **官方文档：** <https://nodered.org/docs/>
>
> **npm：** `node-red` 5.0.9（`latest` dist-tag，截至 2026-10）｜ **Node 要求：** `>=22.9`（`package.json` 的 `engines`）
>
> **许可证：** Apache-2.0

## 概述

Node-RED 是构建在 Node.js 之上的低代码事件驱动编程工具，用于把设备、API 和在线服务以「连线」的方式编排成数据流。它最初由 IBM 新兴技术团队发起，现为 OpenJS Foundation 项目，最新版本 5.0.9。运行时以「消息在节点之间传递」为核心模型：每个节点接收一个 JavaScript 对象 `msg`，处理后交给下一个节点。流（flow）在浏览器中的编辑器里以拖拽方式搭建，保存为 JSON（默认 `flows_<hostname>.json`）。

关键概念：

- **节点（node）**：流的处理单元，分为输入（inject、mqtt in、http in）、处理（function、change、switch、json）、输出（debug、mqtt out、http response）三类
- **消息（msg）**：在节点间传递的 JavaScript 对象，约定使用 `msg.payload` 承载数据，运行时自动附加 `_msgid` 用于追踪
- **流（flow）/ 标签页（tab）**：一组连线的节点，同一标签页共享 flow 级上下文
- **子流程（subflow）**：把一组节点折叠成一个可复用节点，暴露属性为环境变量
- **上下文（context）**：节点级 / flow 级 / global 级三层状态存储
- **面板（dashboard）**：通过 `node-red-dashboard` 等包把消息渲染成图表、仪表盘等 UI

---

## 环境准备

需要 Node.js `>=22.9`（`node-red` 5.x 的 `engines` 要求；低于此版本会安装失败或运行时报错）。

### 方式一：npm 全局安装

```bash
# 全局安装 Node-RED（Windows 去掉 sudo）
npm install -g --unsafe-perm node-red

# 启动，默认监听 1880 端口
node-red
```

### 方式二：Docker

```bash
# 镜像名为 nodered/node-red（1.0 起），映射 1880 端口并持久化 /data
docker run -it -p 1880:1880 -v node_red_data:/data --name mynodered nodered/node-red
```

`docker-compose.yml` 参考：

```yaml
version: "3.7"

services:
  node-red:
    image: nodered/node-red:latest
    environment:
      - TZ=Asia/Shanghai
    ports:
      - "1880:1880"
    volumes:
      - node-red-data:/data

volumes:
  node-red-data:
```

### 验证

启动后浏览器访问编辑器：`http://localhost:1880`

默认目录与文件：用户目录 `~/.node-red`，流文件 `flows_<hostname>.json`，配置文件 `settings.js`。停止服务用 `Ctrl-C`。

---

## 核心 API / 命令

### 消息对象 msg

| 属性 | 含义 |
|------|------|
| `msg.payload` | 节点默认操作的数据主体，可为任意 JS 类型（String/Number/Boolean/Array/Object/Buffer/Null） |
| `msg.topic` | 主题标识，MQTT 节点默认用它作为发布/订阅主题 |
| `msg._msgid` | 运行时自动添加的消息追踪 ID |
| `msg.parts` | 消息序列元数据（`id`/`index`/`count`），由 split、join、batch 等节点维护 |

对象类型属性用点路径访问，例如 `payload.Phone[2].type`。JSON 字符串需先用 JSON 节点解析后才能访问其内部字段。

### 核心节点速查

| 节点 | 类型 | 说明与关键属性 |
|------|------|----------------|
| `inject` | 输入 | 手动点击或按间隔自动触发；可设置任意消息属性，payload 支持字符串/数字/布尔/JSON/时间戳/上下文值；最大间隔 596 小时 |
| `debug` | 输出 | 在调试侧栏结构化展示消息，可切换输出到运行时日志或节点状态文本（32 字符） |
| `function` | 处理 | 对消息执行 JavaScript 代码 |
| `change` | 处理 | 无需写代码修改消息/上下文属性；操作按 Set、Change、Move、Delete 顺序执行，值支持 JSONata 表达式 |
| `switch` | 处理 | 按规则（值、序列、JSONata、Otherwise）把消息路由到不同输出；可匹配多个输出或首个匹配即停 |
| `template` | 处理 | 用 Mustache 语法生成文本，结果若为合法 JSON/YAML 可解析为对象 |
| `mqtt in` | 输入 | 订阅主题，输出消息 |
| `mqtt out` | 输出 | 发布消息到主题 |
| `http in` | 输入 | 暴露 HTTP 端点，生成 `msg.req`/`msg.res` |
| `http response` | 输出 | 用 `msg.payload` 作为响应体返回 |
| `http request` | 处理 | 主动发起 HTTP 请求 |

### Function 节点编写 JS

```javascript
// 返回消息（返回 null 结束流；返回数字/字符串会报错）
return msg;

// 构造新消息（会丢失原消息的其他属性）
const newMsg = { payload: msg.payload.length };
return newMsg;

// 多输出：返回数组
return [msg, newMsg];

// 多输出且每个输出可发多条：嵌套数组
return [[msg1, msg2, msg3], msg4];

// 异步发送
doSomeAsyncWork(msg, function (result) {
    msg.payload = result;
    node.send(msg);
    node.done();          // 通知运行时处理完成
});
return;

// 触发 Catch 节点并记录错误
node.error("hit an error", msg);

// 设置节点状态
node.status({ fill: "red", shape: "ring", text: "disconnected" });
node.status({});          // 清除状态
```

Function 节点内可直接使用 `context`（节点级）、`flow`、`global` 三个上下文变量：

```javascript
let myCount = flow.get("count");
flow.set("count", 123);

// 批量读写
let values = flow.get(["count", "colour", "temperature"]);
flow.set(["count", "colour", "temperature"], [123, "red", "12.5"]);

// 异步存储需回调
flow.get("count", function (err, myCount) { /* ... */ });
```

Function 节点不能直接 `require` 模块，需在 `settings.js` 的 `functionGlobalContext` 中声明后经 `global.get` 取用：

```javascript
// settings.js
functionGlobalContext: {
    osModule: require('os')
}
```

```javascript
// function 节点内
const os = global.get('osModule');
```

### 上下文（context）与持久化

上下文分三层：节点级仅自身可见，flow 级同一标签页共享，global 级全局可见。默认仅存于内存，重启即清空；自 0.19 起可在 `settings.js` 通过 `contextStorage` 持久化。内置 `memory` 与 `localfilesystem` 两个模块。

```javascript
// settings.js：文件持久化
contextStorage: {
    default: {
        module: "localfilesystem"
    }
}
```

文件默认落在 `~/.node-red/context/`，内存缓存每 30 秒落盘一次。多存储示例：

```javascript
contextStorage: {
    default: "memoryOnly",
    memoryOnly: { module: 'memory' },
    file: { module: 'localfilesystem' }
}
```

### settings.js 常用配置

| 属性 | 作用 | 默认 |
|------|------|------|
| `uiPort` | 编辑器 UI 端口（独立运行时） | `1880` |
| `userDir` | 用户数据目录（流、凭据、库） | `$HOME/.node-red` |
| `flowFile` | 存储流的文件 | `flows_<hostname>.json` |
| `httpNodeRoot` | 节点提供的 HTTP 端点根路径，设为 `false` 可禁用 | `/` |
| `functionGlobalContext` | 注入到全局函数上下文的模块/对象 | 空 |
| `contextStorage` | 上下文存储后端 | 内存 |
| `editorTheme` | 编辑器外观定制（标题、favicon、CSS、配色等） | 默认主题 |
| `adminAuth` | 编辑器与管理 API 的访问控制 | 关闭 |
| `httpNodeAuth` | 节点 HTTP 端点的 Basic 认证 | 关闭 |
| `logging` | 控制台日志级别：fatal/error/warn/info/debug/trace | `info` |

### 命令行选项

```bash
node-red -p 1881                # 指定端口
node-red -u /path/to/userdir    # 指定用户目录
node-red -s /path/to/settings.js
node-red --safe                 # 安全模式启动，不加载流
node-red -D key=value           # 覆盖单个设置项
node-red -v                     # 显示版本
```

---

## 典型工作流

### 场景一：MQTT 采集与转发

1. 拖入 `mqtt in` 节点，点击服务器字段旁的编辑按钮新建 broker 配置节点：填写地址与端口（默认 `1883`，TLS 用 `8883`）、客户端 ID、Keep Alive（默认 60）、Clean Session、协议版本（MQTT V3.1.1 / V5），在 Security 选项卡填用户名密码。
2. `mqtt in` 节点填写订阅主题，支持通配符（`+` 单层、`#` 多层，如 `sensor/+/temperature`、`home/#`），选择 QoS（0/1/2），输出可选自动识别、解析后的 JSON 对象或单个 Buffer 字符串；一个 `mqtt in` 可订阅多个主题。
3. 接 `json` 节点解析后由 `function` 处理，再由 `mqtt out` 发布：主题留空时使用 `msg.topic`，payload 为 Object 时自动转 JSON 字符串，Buffer 原样发送；设置 QoS 与 Retain。

```json
[
  {
    "type": "mqtt in",
    "name": "订阅温度",
    "topic": "sensor/+/temperature",
    "qos": "0",
    "broker": "mqtt-broker",
    "wires": [["json-parse"]]
  }
]
```

### 场景二：HTTP API 对接

用 `http in` → 处理节点 → `http response` 搭建接口。`http in` 配置 `url`（如 `/api/readings`）与 `method`（get/post/put/delete/patch）；请求上下文在 `msg.req`，响应对象在 `msg.res`。响应体取 `msg.payload`，可用 `msg.statusCode` 设置状态码、`msg.headers` 设置响应头。

```javascript
// function 节点：处理 POST 请求体并构造响应
const body = msg.payload;                 // http in 已将请求体解析为 msg.payload
const reading = {
    deviceId: body.deviceId,
    value: Number(body.value),
    ts: Date.now()
};
flow.set("lastReading", reading);
msg.statusCode = 201;
msg.headers = { "Content-Type": "application/json" };
msg.payload = { ok: true, reading };
return msg;
```

注意：任何以 `http in` 起始的流必须有路径连到 `http response`，否则请求最终超时。

### 场景三：Dashboard 面板

安装 `node-red-dashboard` 后拖入 `ui_*` 节点，UI 默认发布在 `http://localhost:1880/ui`。

```bash
# 在 Node-RED 用户目录执行（或通过编辑器「管理面板」搜索安装）
npm i node-red-dashboard
```

常用节点：`ui_base`（页面与站点配置）、`ui_tab`、`ui_group`（布局容器）、`ui_text`、`ui_gauge`、`ui_chart`、`ui_button`、`ui_template`。布局按网格排布，组默认 6 单位宽，控件默认 `auto` 宽；控件可通过 `msg.enabled=false` 禁用，用 `msg.ui_control` 运行时配置。

> 注意：`node-red-dashboard` 已于 2024-06-27 标记弃用，官方推荐改用 FlowFuse Dashboard（`@flowfuse/node-red-dashboard`）或 UIBUILDER。

### 场景四：子流程与流导入导出

- 菜单 `Subflows → Create subflow` 新建空白子流程，或用 `Selection to Subflow` 把选中节点折叠为子流程（仅当输入线汇聚到单一节点时可用，子流程最多一个输入、可多个输出）。
- 子流程属性页定义的属性会在子流程内部暴露为环境变量，可逐实例配置；子流程从 0.20 起可用 `$parent.` 访问父 flow 上下文，例如 `flow.get("$parent.colour")`。
- 工具栏可添加 status 输出，用 `msg.payload`（字符串或状态对象）更新子流程实例节点的状态。
- 导入导出：编辑器菜单 `Import`/`Export`（快捷键 `Ctrl/⌘-i`、`Ctrl/⌘-e`），可粘贴 JSON、上传文件、存到本地库或导出为紧凑/格式化 JSON。

---

## 最佳实践

- 用 `change` / `switch` 等内置节点能完成的工作优先不写 `function`，降低维护成本。
- 消息处理保持幂等与无副作用：同一节点可能因重试或循环被多次触发。
- 大对象传递时注意消息克隆开销，异步场景可用 `node.send(msg, false)` 跳过克隆。
- 上下文按最小可见范围选择：能放节点级就不放 flow 级，能放 flow 级就不放 global 级；需要跨重启保留的数据显式配置 `contextStorage`。
- MQTT 主题命名遵循层级约定（如 `设备类型/设备ID/指标`），订阅用通配符前评估消息量；QoS 按可靠性需求选择（0 最多一次、1 至少一次、2 仅一次），状态类消息用 Retain 便于新订阅者获取最后值。
- `http in` 端点务必连接到 `http response`；对公网接口启用 `httpNodeAuth`，对编辑器启用 `adminAuth`。
- 流文件纳入版本管理，用子流程复用公共逻辑；部署前用调试侧栏验证 `msg` 结构。

---

## 常见问题

| 问题 | 排查与解决 |
|------|-----------|
| `npm install -g node-red` 报权限错误 | Linux/macOS 用 `sudo npm install -g --unsafe-perm node-red`；Windows 去掉 `sudo`；或改用 Docker |
| 启动后浏览器打不开编辑器 | 确认进程已监听 1880 端口，访问 `http://localhost:1880`；端口被占用时用 `node-red -p 1881` 换端口 |
| 部署后流未生效或丢失 | 检查是否点了「部署」；流保存在用户目录 `~/.node-red/flows_<hostname>.json`，Docker 下需挂载 `/data` 卷，否则容器重建即丢失 |
| MQTT 节点连不上 broker | 核对地址/端口（明文 1883、TLS 8883）、用户名密码、客户端 ID；启用 TLS 时勾选 Use TLS；检查网络与 broker 的 ACL |
| MQTT 收到的 payload 是字符串无法取字段 | 在 `mqtt in` 的输出选项选择「解析后的 JSON 对象」，或后接 `json` 节点解析 |
| `http in` 请求超时无响应 | 确认流中存在到 `http response` 的路径；`http in` 起始的流必须有响应节点 |
| 重启后上下文数据消失 | 默认上下文仅存内存；在 `settings.js` 配置 `contextStorage` 使用 `localfilesystem` 持久化 |
| Function 节点中 `require` 模块报错 | 不能直接 require；在 `settings.js` 的 `functionGlobalContext` 声明后经 `global.get` 获取，或开启 `functionExternalModules` 在编辑对话框选择模块 |
| Dashboard 面板不显示 | 确认已安装 `node-red-dashboard` 并重启 Node-RED，访问 `http://localhost:1880/ui`；注意该包已弃用，可迁移到 FlowFuse Dashboard |

---

## AI 使用建议

### 推荐工作流

1. **确认部署形态**：本地 npm 全局安装还是 Docker 容器，Docker 必须挂载 `/data` 才能持久化流与凭据。
2. **先搭最小流验证链路**：`inject → debug` 验证编辑器与运行时，再逐步加入 MQTT/HTTP 节点。
3. **按需求选节点**：简单改值用 `change`，条件分支用 `switch`，复杂逻辑才用 `function`。
4. **验证消息结构**：用调试侧栏观察 `msg.payload` 实际类型（字符串还是对象），再决定是否加 `json` 节点。
5. **导出 flows.json 纳入版本管理**，复杂逻辑封装为子流程复用。

### 关键模式与常见陷阱

- **payload 类型**：MQTT 与 HTTP 传入的 payload 可能是字符串，取字段前需解析为对象。
- **HTTP 必须闭环**：`http in` 起始的流一定要连到 `http response`。
- **上下文易失**：默认内存存储重启即丢，需持久化要配 `contextStorage`。
- **Function 不能 require**：第三方模块须经 `functionGlobalContext` 或 `functionExternalModules`。
- **端口与权限**：默认 1880；全局安装的权限问题用 `--unsafe-perm` 或 Docker 规避。

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 本地快速原型 | npm 全局安装 + 浏览器编辑器 |
| 服务器长期运行 | Docker `nodered/node-red` + `/data` 卷 |
| 设备数据上云 | `mqtt in` 订阅 + `function` 处理 + `mqtt out` 转发 |
| 对外提供接口 | `http in` / `http response` + `httpNodeAuth` |
| 可视化监控面板 | FlowFuse Dashboard（`node-red-dashboard` 已弃用） |

## 相关技能

- **ke3036-keyes-pico** — Raspberry Pi Pico（RP2040）MicroPython 开发，可作为 Node-RED 流的传感器/设备端数据源（Wi-Fi + MQTT 上报）：[../ke3036-keyes-pico/SKILL.md](../ke3036-keyes-pico/SKILL.md)

---

## 参考资源

- Node-RED 官方文档：<https://nodered.org/docs/>
- 用户指南：<https://nodered.org/docs/user-guide/>
- 本地安装：<https://nodered.org/docs/getting-started/local>
- Docker 部署：<https://nodered.org/docs/getting-started/docker>
- 配置（settings.js）：<https://nodered.org/docs/user-guide/runtime/configuration>
- 消息与上下文：<https://nodered.org/docs/user-guide/messages>、<https://nodered.org/docs/user-guide/context>
- 编写函数：<https://nodered.org/docs/user-guide/writing-functions>
- 节点库与 Dashboard：<https://flows.nodered.org/node/node-red-dashboard>
- 项目仓库：<https://github.com/node-red/node-red>
