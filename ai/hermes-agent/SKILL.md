---
name: hermes-agent
description: hermes-agent 是开源的 LLM Agent 框架/产品，专注于消息编排、工具调用与多智能体协作，支持函数调用、ReAct、流式响应、记忆与监控，可作为后端服务接入聊天、客服、办公自动化等场景。
---

> **项目地址：** <https://github.com/znlgis/hermes-agent>（如位置变动请以 znlgis.github.io 为准）
>
> **许可证：** MIT / Apache-2.0（视仓库声明）

## 概述

hermes-agent 通常包含：

- **Agent 引擎**：ReAct / FunctionCall / Plan-Execute
- **多 LLM 适配**：OpenAI 协议 / Anthropic / 通义 / 智谱 / Ollama
- **工具系统**：原生函数 + OpenAPI + MCP
- **会话与记忆**：Redis / SQL 持久化
- **流式响应**：SSE / WebSocket
- **可观测**：结构化日志、Tracing、Token 计量
- **部署**：单二进制 / Docker / K8s

---

## 安装

```bash
git clone https://github.com/znlgis/hermes-agent
cd hermes-agent
cp .env.example .env
docker compose up -d
# 或本地：
pip install -r requirements.txt   # 或 pnpm install
```

`.env`：

```
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://hermes:hermes@localhost:5432/hermes
LOG_LEVEL=INFO
```

---

## 创建一个 Agent（YAML/JSON 配置）

```yaml
name: customer-support
description: 客服助手
llm:
  model: gpt-4o-mini
  temperature: 0.3
system_prompt: |
  你是 ACME 公司的客服助手……
tools:
  - name: search_orders
    type: openapi
    spec_url: https://api.example.com/openapi.json
    auth: { type: bearer, token: ${ORDER_API_TOKEN} }
  - name: send_email
    type: builtin
memory:
  type: redis
  ttl: 86400
max_iter: 6
```

---

## API 调用

```bash
# 创建会话
curl -X POST http://localhost:8000/sessions \
  -H 'Content-Type: application/json' \
  -d '{"agent": "customer-support", "user_id": "u1"}'
# → {"session_id":"sess_abc"}

# 发送消息（流式）
curl -N -X POST http://localhost:8000/sessions/sess_abc/messages \
  -H 'Content-Type: application/json' \
  -d '{"input":"我的订单 12345 到哪了？","stream":true}'
```

SSE 输出：

```
event: token
data: 您好...

event: tool_call
data: {"name":"search_orders","arguments":{"id":"12345"}}

event: tool_result
data: {...}

event: done
data: {"finish_reason":"stop","usage":{"total_tokens":857}}
```

---

## 工具开发（Python 示例）

```python
from hermes_agent import tool

@tool(name="get_weather", description="查询天气")
def get_weather(city: str) -> dict:
    import requests
    return requests.get(f"https://wttr.in/{city}?format=j1").json()
```

注册：放到 `tools/` 目录，重启即生效；或通过 `POST /tools` 动态注册。

---

## 多智能体协作

```yaml
name: research-team
agents:
  - role: planner
    llm: gpt-4o
  - role: searcher
    llm: gpt-4o-mini
    tools: [web_search]
  - role: writer
    llm: gpt-4o
flow: planner -> searcher -> writer
```

---

## 流式响应（前端）

```js
const evt = new EventSource(`/sessions/${sid}/stream`);
evt.addEventListener('token', e => append(e.data));
evt.addEventListener('tool_call', e => showTool(JSON.parse(e.data)));
evt.addEventListener('done', () => evt.close());
```

---

## 记忆与会话

- 短期：Redis 滑窗历史（默认最近 N 轮）
- 长期：向量记忆（PGVector/Qdrant），按 session_id 聚类
- 用户级：`user_profile` 持久化到 Postgres

```bash
GET /sessions/{id}/messages?limit=50
DELETE /sessions/{id}
```

---

## 监控与日志

- 默认 JSON 日志输出 stdout，建议 EFK / Loki 收集
- 暴露 `/metrics`（Prometheus）：QPS、延迟、token 用量、工具调用次数
- Tracing：OpenTelemetry，OTLP 端点可配置

---

## 部署

```yaml
# docker-compose.yml 片段
services:
  hermes:
    image: hermes-agent:latest
    env_file: .env
    ports: ["8000:8000"]
    depends_on: [redis, postgres]
```

K8s：Helm Chart（如仓库提供）或自定义 Deployment + Service + Ingress；生产 ≥ 2 副本，Redis/Postgres 单独管理。

---

## 性能与最佳实践

1. **流式优先**：减少首字节时间
2. **限制 `max_iter`**：避免推理死循环
3. **工具结果缓存**：相同输入直接命中
4. **Token 计量与限流**：每用户 / 每会话 / 每天
5. **熔断**：LLM 错误率 > 阈值时降级到备选模型
6. **会话隔离**：用户 ID + 租户 ID 严格隔离
7. **审计**：保存所有工具输入输出，便于追责

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 工具调用 JSON 解析失败 | 启用 strict function-calling；或回退 ReAct |
| 国产模型不支持 function-call | 配置 `tool_protocol: react`（文本协议） |
| 流式输出乱序 | 客户端按 event id 排序 |
| 会话泄漏 | 设置 `MEMORY_TTL` + 定期清理 |
| 记忆膨胀 | 启用摘要压缩 + 滑窗 |

---

## 参考资源

- 仓库：<https://github.com/znlgis/hermes-agent>
- 中文教程（znlgis）：<https://znlgis.github.io/ai/tutorial/hermes-agent/>
