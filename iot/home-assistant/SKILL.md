---
name: home-assistant
description: "Use when automating a smart home with Home Assistant 2026.10 — configuration.yaml and automations.yaml, triggers/conditions/actions YAML, REST API /api/states and /api/services, WebSocket subscribe_events, long-lived access tokens, Docker container installs; also for 'Configuration invalid' after a YAML edit, 401 from the API, template errors, and entities stuck 'unavailable'. Open-source home automation that runs locally."
tags:
  - home-assistant
  - iot
  - automation
  - smart-home
  - yaml
  - rest-api
  - websocket
  - docker
  - python
  - mqtt
---

> **项目地址：** <https://github.com/home-assistant/core>
>
> **官方文档：** <https://www.home-assistant.io/docs/>
>
> **开发者文档：** <https://developers.home-assistant.io/>
>
> **最新版本：** 2026.10.4（GitHub Releases 与 Docker 镜像 tag 一致，截至 2026-10）
>
> **安装形态：** Home Assistant OS / Supervised / Container / Core（pip）
>
> **许可证：** Apache-2.0

## 概述

Home Assistant 是一个本地优先的开源家庭自动化平台。它把上千种设备与云服务统一成「实体（entity）」，再通过状态机、自动化规则、脚本与仪表盘把它们编排起来。数据与逻辑都跑在你自己的机器上，不依赖厂商云。

对脚本与自动化最关键的几层：

- **实体与状态**：每个设备暴露为 `domain.name`（如 `light.study`），状态 + 属性构成当前值
- **服务（service/action）**：`light.turn_on`、`climate.set_temperature` 这类可调用动作，是自动化与 API 的执行单位
- **自动化与脚本**：YAML 或 UI 定义的 `triggers/conditions/actions` 三段式规则
- **REST API**：`/api/*`，用长期访问令牌鉴权，适合外部程序读写状态、触发服务
- **WebSocket API**：`/api/websocket`，支持实时订阅事件、订阅触发器、批量取状态
- **模板（Jinja2）**：`{{ states('sensor.x') }}` 在自动化与 `/api/template` 中计算动态值

## 环境准备

### 方式一：Home Assistant OS（推荐给家庭用户）

在 Raspberry Pi / NUC / 虚拟机上刷写官方镜像，得到受管系统（含 Supervised、Add-ons、备份）。安装入口见 <https://www.home-assistant.io/installation/>。首次启动后浏览器访问 `http://<ip>:8123` 完成引导。

### 方式二：Docker Container

```bash
docker run -d \
  --name homeassistant \
  --restart=unless-stopped \
  --privileged \
  --network=host \
  -e TZ=Asia/Shanghai \
  -v /path/to/config:/config \
  -v /run/dbus:/run/dbus:ro \
  ghcr.io/home-assistant/home-assistant:stable
```

要点：

- `-v /path/to/config:/config` 必须持久化，否则升级即丢配置；
- `--network=host` 让设备发现（mDNS/SSDP）正常工作，端口直接是 8123；
- 需要直通 USB 设备（Zigbee/Z-Wave 棒）时加 `--device /dev/ttyUSB0:/dev/ttyUSB0`；
- 关机给足时间：`docker run --stop-timeout 60`，否则容易损坏数据库。

```yaml
# compose.yaml
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: homeassistant
    restart: unless-stopped
    network_mode: host
    privileged: true
    stop_grace_period: 60s
    environment:
      TZ: Asia/Shanghai
    volumes:
      - ./config:/config
      - /run/dbus:/run/dbus:ro
```

### 方式三：Core（pip，仅开发/调试）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install homeassistant==2026.10.4
hass --config ./config --debug
```

Core 不含 Supervisor 与 Add-ons，适合读源码、改集成、跑测试。

### 验证

```bash
# 容器形态
docker logs -f homeassistant | head -40

# 配置检查（容器内）
docker exec -it homeassistant python -m homeassistant --script check_config -c /config

# API 存活探测（需要长期令牌）
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8123/api/
```

最后一条应返回 `{"message":"API running."}`。

## 核心接口

### 目录与文件

| 路径 | 作用 |
|------|------|
| `configuration.yaml` | 主配置入口，集成、模板、HTTP 等 |
| `automations.yaml` | UI 生成的自动化（**不要手改**，UI 会覆写） |
| `scripts.yaml` / `scenes.yaml` | 脚本与场景 |
| `secrets.yaml` | 密钥，用 `!secret` 标签引用 |
| `.storage/` | 注册表与运行时数据（实体、设备、区域），**不要手改** |
| `home-assistant.log` | 运行日志（也可从 `/api/error_log` 取） |

### configuration.yaml 基础

```yaml
# 基础配置
homeassistant:
  name: Home
  unit_system: metric
  time_zone: Asia/Shanghai
  country: CN
  currency: CNY
  language: zh-Hans

# UI 管理的自动化以 include 方式接入
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

# 拆分配置（推荐：按功能放到 packages/）
homeassistant:
  packages: !include_dir_named packages
```

```yaml
# packages/lighting.yaml —— 一个文件描述一整套相关配置
input_boolean:
  hallway_night_mode:
    name: Hallway night mode

template:
  - sensor:
      - name: "Living room average temperature"
        unit_of_measurement: "°C"
        state: >
          {{ ((states('sensor.living_room_temp_1') | float(0)
               + states('sensor.living_room_temp_2') | float(0)) / 2) | round(1) }}
```

### 自动化结构（triggers / conditions / actions）

新版写法用复数键 `triggers` / `conditions` / `actions`（旧的单数形式仍在兼容范围内，但新代码应写复数）：

```yaml
automation:
  - id: "hallway_motion_light"
    alias: 走廊有人自动开灯
    description: 夜间检测到移动时开灯，2 分钟无移动后关闭
    mode: restart
    max_exceeded: silent

    triggers:
      - trigger: state
        entity_id: binary_sensor.hallway_motion
        from: "off"
        to: "on"
        for: "00:00:05"

    conditions:
      - condition: numeric_state
        entity_id: sensor.outdoor_illuminance
        below: 30
      - condition: state
        entity_id: input_boolean.hallway_night_mode
        state: "on"

    actions:
      - action: light.turn_on
        target:
          entity_id: light.hallway
        data:
          brightness_pct: 40
      - wait_for_trigger:
          - trigger: state
            entity_id: binary_sensor.hallway_motion
            to: "off"
            for: "00:02:00"
        timeout: "00:10:00"
      - action: light.turn_off
        target:
          entity_id: light.hallway
```

自动化内联写在 `configuration.yaml` 时用带标签的块（可多组）：

```yaml
automation: !include automations.yaml
automation kitchen:
  - triggers:
      - trigger: time
        at: "06:30:00"
    actions:
      - action: light.turn_on
        target:
          entity_id: light.kitchen
```

### REST API

所有请求带 `Authorization: Bearer <long-lived-token>`。令牌在网页界面 **个人资料 → 安全 → 长期访问令牌** 处创建。

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/` | GET | 健康检查 |
| `/api/config` | GET | 当前配置（版本、单位、时区等） |
| `/api/states` | GET | 全部实体状态 |
| `/api/states/<entity_id>` | GET / POST | 读 / 直接写状态 |
| `/api/services` | GET | 可用服务清单 |
| `/api/services/<domain>/<service>` | POST | 调用服务（核心动作） |
| `/api/events` / `/api/events/<event_type>` | GET / POST | 读事件总线 / 触发自定义事件 |
| `/api/template` | POST | 渲染 Jinja2 模板 |
| `/api/history/period/<timestamp>` | GET | 历史状态 |
| `/api/logbook/<timestamp>` | GET | 日志簿 |
| `/api/error_log` | GET | 文本日志 |
| `/api/config/core/check_config` | POST | 校验配置 |
| `/api/intent/handle` | POST | 走意图识别（语音助手同路径） |
| `/api/calendars` | GET | 日历事件 |

```bash
# 读一个实体的状态
curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  http://localhost:8123/api/states/light.hallway

# 调用服务：开灯并设置亮度
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"entity_id":"light.hallway","brightness_pct":40}' \
  http://localhost:8123/api/services/light/turn_on

# 渲染模板
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"template":"{{ states("sensor.outdoor_illuminance") }} lx"}' \
  http://localhost:8123/api/template
```

状态码含义：200/201 成功；400 请求体不合法；401 令牌缺失或失效；404 实体/端点不存在；405 方法用错。

### WebSocket API

连接 `ws://<host>:8123/api/websocket`，走「先认证、后命令」两阶段：

1. 服务器发 `{"type":"auth_required"}`
2. 客户端发 `{"type":"auth","access_token":"..."}`
3. 服务器回 `{"type":"auth_ok",...}`（失败为 `auth_invalid`）
4. 之后每条命令带唯一的 `id`，响应以 `{"type":"result","id":N,...}` 返回；事件推送为 `{"type":"event",...}`

常用命令：`get_states`、`get_config`、`get_services`、`get_panels`、`call_service`、`subscribe_events`、`unsubscribe_events`、`subscribe_trigger`、`fire_event`、`validate_config`、`ping`。

```python
import asyncio, json, websockets

async def main(token: str):
    async with websockets.connect("ws://localhost:8123/api/websocket") as ws:
        print(json.loads(await ws.recv()))                 # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        print(json.loads(await ws.recv()))                 # auth_ok
        await ws.send(json.dumps({"id": 1, "type": "get_states"}))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 1 and msg.get("type") == "result":
                print("entities:", len(msg["result"]))
                break
        # 订阅状态变化事件
        await ws.send(json.dumps({"id": 2, "type": "subscribe_events",
                                  "event_type": "state_changed"}))
        print(json.loads(await ws.recv()))                 # result: success
        print(json.loads(await ws.recv()))                 # 第一条 state_changed

asyncio.run(main("YOUR_LONG_LIVED_TOKEN"))
```

WebSocket 适合「要实时、要少轮询」的场景；REST 适合一次性读写。

## 典型工作流：外部传感器 → 自动写入状态 → 自动化响应 → 验收

输入：一台跑 Python 的边缘设备，每 30 秒读一次光照度；目标是把数据写进 Home Assistant，让「夜间自动开灯」自动化能用到它。

**步骤 1：创建长期访问令牌**

浏览器进入 `http://<ha>:8123/profile` → **安全** → **长期访问令牌** → 创建，复制整个令牌（只显示一次）。

```bash
export HA_URL="http://localhost:8123"
export TOKEN="<粘贴长期访问令牌>"
curl -s -H "Authorization: Bearer $TOKEN" "$HA_URL/api/"   # 期望 {"message":"API running."}
```

**步骤 2：把传感器数值写成实体状态**

```python
import os, time, random, requests

HA = os.environ["HA_URL"]; TOKEN = os.environ["TOKEN"]
HEAD = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def push_illuminance(lux: float) -> None:
    r = requests.post(
        f"{HA}/api/states/sensor.balcony_illuminance",
        headers=HEAD,
        json={"state": round(lux, 1),
              "attributes": {"unit_of_measurement": "lx",
                             "friendly_name": "Balcony illuminance",
                             "device_class": "illuminance"}},
        timeout=10,
    )
    r.raise_for_status()

if __name__ == "__main__":
    while True:
        push_illuminance(random.uniform(5, 200))   # 换成真实读数
        time.sleep(30)
```

关键点：用固定 `entity_id`（`sensor.balcony_illuminance`）反复 POST，Home Assistant 会更新同一实体而不是新建。Python 里用 f-string 拼 URL 时，注意别让 Jinja 的 `{{ }}` 与 f-string 的花括号互相干扰。

**步骤 3：让自动化消费该实体**

把前面的「走廊有人自动开灯」自动化里 `sensor.outdoor_illuminance` 换成 `sensor.balcony_illuminance`，保存后重新加载自动化（**开发者工具 → YAML → 重新加载自动化**）。

**步骤 4：验证链路**

```bash
# 实体是否已出现、值是否为最新
curl -s -H "Authorization: Bearer $TOKEN" "$HA_URL/api/states/sensor.balcony_illuminance" | python -m json.tool

# 手动触发一次自动化所依赖的服务，确认执行侧正常
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"entity_id":"light.hallway"}' "$HA_URL/api/services/light/toggle"
```

看 **设置 → 系统 → 日志** 或 `/api/error_log`，确认自动化被触发且没有模板错误。

**步骤 5：收尾**

- 把令牌与 URL 放进环境变量或 `secrets.yaml`，不要提交到仓库；
- 想长期可靠就用 MQTT 或专用集成，直接 POST 状态属于「外部状态注入」，重启后实体状态可能丢失。

## 最佳实践

1. **配置用 `packages` 拆分**：一个功能一个 YAML 文件，避免 `configuration.yaml` 变成千行巨石。
2. **UI 生成的 `automations.yaml` 不要手改**：UI 会整体覆写；要手写就用带标签的 `automation <name>:` 块放到自己的文件。
3. **改完配置先校验**：`python -m homeassistant --script check_config -c /config`，或 POST `/api/config/core/check_config`，再考虑重启。
4. **优先 reload 而不是 restart**：自动化、模板、脚本、input_* 都支持热重载，重启会打断正在跑的自动化。
5. **模板里一律给默认值**：`states('sensor.x') | float(0)`、`| default('unknown')`，实体缺失时避免整条自动化报错。
6. **自动化设 `mode`**：`single`（默认，丢弃重叠）、`restart`（取消旧跑新的）、`queued`（排队）、`parallel`（并行），按语义选。
7. **密钥走 `secrets.yaml`**：用 `!secret` 引用，避免把令牌写进配置或截图。
8. **容器务必持久化 `/config` 并设置停容器超时**：`--stop-timeout 60` / `stop_grace_period: 60s`，否则 SQLite 可能损坏。

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 启动后提示 **Configuration invalid** | YAML 语法或集成键值错 | 看通知里的具体文件与行号；跑 `check_config` 定位；常见是缩进用了 Tab 或 `:` 后少空格 |
| REST 调用返回 401 | 令牌缺失、过期或复制不全 | 重新在个人资料页创建长期令牌，确认请求头是 `Bearer <token>`（注意空格） |
| 调用服务返回 400 | 请求体字段名与服务不匹配 | 先 GET `/api/services` 看该服务的字段，再按示例 POST；注意 `entity_id` 与 `target` 的区别 |
| 实体显示 **unavailable** | 集成未加载、设备离线或重启中 | 看 `home-assistant.log`；在 **设置 → 设备与服务** 里重载对应集成 |
| 自动化不触发 | 触发器条件不满足，或自动化被关闭 | 打开自动化的 **追踪（Traces）** 看每一步；确认 `initial_state` 与 UI 上的开关状态 |
| 模板报 `TypeError` / `ValueError` | 实体不存在或值不是数字 | 用 `| float(0)`、`| int(0)`、`| default(...)` 兜底；先用 `/api/template` 单独试算 |
| 升级后集成报错 | 破坏性变更或自定义集成不兼容 | 先读版本发布说明的 Breaking Changes；回滚镜像 tag 到上一个版本 |
| 容器重启后配置全没了 | 没挂载 `/config` 卷 | 停容器，重新以 `-v <host>:/config` 启动；以后先确认卷再升级 |

## DeepSeek Harness 使用建议

- **加载技能**：skill("home-assistant")；技能目录只读，脚本与临时配置写到会话工作区。
- **先探版本与形态**：`GET /api/config` 拿 `version` 与 `location_name`；容器内 `docker exec` 跑命令比在宿主机猜路径可靠。
- **改 YAML 前必备份**：`cp configuration.yaml configuration.yaml.bak`，改完先 `check_config`，通过后再 reload/restart。
- **令牌不落盘**：用环境变量传 `TOKEN`，示例里的 `<粘贴长期访问令牌>` 必须替换；不要把令牌写进脚本或报告。
- **验证产物**：写状态后回读 `/api/states/<entity_id>` 核对值与属性；触发服务后看日志或追踪，确认动作真的执行，而不是只看 200。
- **写操作确认**：`POST /api/states` 会覆盖实体状态（重启后可能丢失），`homeassistant.restart` 会中断所有自动化；执行前向用户确认。

## 相关技能

- **node-red** — 另一种低代码自动化编排，常与 HA 通过 MQTT/HTTP 互通：[../node-red/SKILL.md](../node-red/SKILL.md)
- **esphome** — 给 HA 提供原生 API 的 ESP 固件框架：[../esphome/SKILL.md](../esphome/SKILL.md)
- **ke3036-keyes-pico** — 用 MicroPython 直接产出传感器数据：[../ke3036-keyes-pico/SKILL.md](../ke3036-keyes-pico/SKILL.md)
- **ollama** — 本地大模型，可被 HA 的对话助手调用：[../../ai/ollama/SKILL.md](../../ai/ollama/SKILL.md)

## 相关资源

- 官方文档：<https://www.home-assistant.io/docs/>
- 开发者文档（REST / WebSocket / 集成开发）：<https://developers.home-assistant.io/>
- 自动化 YAML 参考：<https://www.home-assistant.io/docs/automation/yaml/>
- 模板函数参考：<https://www.home-assistant.io/docs/configuration/templating/>
- 安装方式对比：<https://www.home-assistant.io/installation/>
