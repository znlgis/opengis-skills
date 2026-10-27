---
name: esphome
description: "Use when flashing or automating ESP32/ESP8266 firmware with ESPHome 2026.10 — YAML configuration with esphome/esp32/api/ota/wifi blocks, esphome run/compile/logs/upload CLI, OTA updates, native API encryption, substitutions and packages; also for 'Component not found', OTA upload failures, boot loops after flashing, and missing sensor entities in Home Assistant. YAML-driven ESP firmware framework."
tags:
  - esphome
  - iot
  - esp32
  - esp8266
  - yaml
  - firmware
  - home-assistant
  - ota
  - mqtt
  - microcontrollers
---

> **项目地址：** <https://github.com/esphome/esphome>
>
> **官方文档：** <https://esphome.io/>
>
> **PyPI：** `esphome` 2026.10.0（GitHub Releases 同日发布，截至 2026-10）
>
> **许可证：** MIT（部分组件依赖的第三方库另有许可）

## 概述

ESPHome 是一个「用 YAML 生成 ESP 固件」的框架。你描述设备**有什么**（板子型号、传感器接在哪个引脚、要暴露哪些实体），它负责生成 C++、编译、上传，并把设备自动接入 Home Assistant。

核心模型：

- **一份 YAML = 一台设备**：`esphome:`、`esp32:`、`wifi:`、`api:`、`ota:` 是骨架，其余都是组件
- **组件（component）**：`sensor:`、`binary_sensor:`、`light:`、`display:` 等平台，每个下面按 `platform:` 选具体实现
- **实体（entity）**：组件里带 `name:` 的条目会变成 Home Assistant 的实体；不带 `name` 的是内部件
- **原生 API**：`api:` 段启用 protobuf over TCP（默认 6053），是 HA 集成的首选通道；MQTT 是另一条可选通道
- **OTA**：`ota: - platform: esphome` 让后续更新走网络，不必每次插 USB

相比手写 Arduino/ESP-IDF，它把构建系统、网络栈、HA 对接、OTA 都收敛到声明式配置里；代价是组件能力受框架支持范围限制。

## 环境准备

### 方式一：pip 安装 CLI（推荐，可脚本化）

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install esphome==2026.10.0

esphome version
```

`esphome version` 应打印 `Version: 2026.10.0`。CLI 会自行下载 PlatformIO 与工具链（首次编译较慢）。

### 方式二：Docker

```bash
docker run --rm -it \
  -v "$PWD":/config \
  -v esphome-cache:/cache \
  --network host \
  ghcr.io/esphome/esphome:2026.10.0 version
```

把 `/config` 指向存放 YAML 的目录；串口烧写需要额外 `--device /dev/ttyUSB0` 直通。

### 方式三：ESPHome Device Builder（图形界面）

官方容器也能以 dashboard 形态运行（暴露 6052 端口），在浏览器里点选配置。命令行仍是理解配置与做自动化的主路径，本技能以 CLI 为准。

### 验证

```bash
esphome version
esphome config my-device.yaml        # 校验配置并打印最终生效内容
```

第二条命令不接硬件就能验证 YAML 是否正确，是改配置后的第一道检查。

## 核心 API / 配置

### 最小可用骨架

```yaml
esphome:
  name: livingroom
  friendly_name: Living Room
  area: "Living Room"

esp32:
  variant: esp32s3          # 或 esp32 / esp32c3 / esp32c6 …；推荐用 variant 而非 board

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  manual_ip:
    static_ip: 192.168.1.50
    gateway: 192.168.1.1
    subnet: 255.255.255.0

api:
  encryption:
    key: !secret livingroom__encryption_key

ota:
  - platform: esphome

logger:

sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Living room temperature"
    humidity:
      name: "Living room humidity"
    update_interval: 60s
```

要点：

- `name` 只允许小写字母、数字与连字符，默认最长 24 字符（`name_add_mac_suffix: false` 时可达 31）；
- `esp32` 段至少要给 `variant` 或 `board` 之一，两者须指向同一型号；新配置用 `variant`；
- `wifi` 必须存在（或 Ethernet 等其它网络段），否则校验阶段就失败；
- `api.encryption.key` 建议与 `ota` 复用同一把密钥。

### 常用组件速览

| 组件 | 用途 | 关键字段 |
|------|------|----------|
| `sensor` | 数值型实体 | `platform`、`name`、`update_interval` |
| `binary_sensor` | 开关量实体（门磁、人体感应） | `platform`、`device_class` |
| `switch` / `light` | 可执行实体 | `platform`（`gpio`、`esp32_rmt_led_strip` 等） |
| `output` | 底层 PWM/GPIO 输出 | `platform`、`pin` |
| `display` | OLED/LCD/墨水屏 | `platform`、`lambda` |
| `i2c` / `spi` / `uart` | 总线定义 | `sda`/`scl`、`mosi`/`clk`、`tx_pin`/`rx_pin` |
| `mqtt` | 接入 MQTT 而非原生 API | `broker`、`topic_prefix` |
| `web_server` | 浏览器直接看状态 | `port`（默认 80） |

### substitutions 与 packages

`substitutions` 用 bash 风格语法 `${key}`（等价于 `$key`），适合一份文件跑多台设备：

```yaml
substitutions:
  device_name: livingroom
  room: "Living Room"

esphome:
  name: ${device_name}
  friendly_name: ${room} Controller

sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "${room} temperature"
```

命令行也能覆盖（可多次给出）：`esphome run -s device_name kitchen my-device.yaml`。

`packages` 用来复用公共片段：

```yaml
packages:
  base: !include common/base.yaml
  wifi: !include common/wifi.yaml
```

### 关键配置项对照

| 段 | 字段 | 说明 |
|----|------|------|
| `api` | `port` | 默认 6053 |
| `api` | `encryption.key` | 加密密钥；写入后 HA 需填同一把 base64 密钥 |
| `api` | `batch_delay` | 默认 100ms；实时性要求高时降到 `50ms` |
| `ota` | `platform: esphome` + `password` | 无加密密钥时的退路：只认证上传方，不保密镜像 |
| `ota` | `platform: esphome` + `encryption:` | 复用 api 加密（推荐） |
| `wifi` | `manual_ip` | 固定 IP，显著改善连接时间 |
| `esp32` | `flash_size` | `2MB`–`32MB`；写超过实际容量会导致无法启动 |

## 命令行

基本形式：`esphome [OPTIONS] <COMMAND> <CONFIGURATION...>`，部分命令支持一次给多个 YAML。

| 命令 | 作用 |
|------|------|
| `run <CONFIG>` | 校验 → 编译 → 上传（OTA 或 USB）→ 打开日志，最常用 |
| `config <CONFIG>` | 只校验并打印最终配置 |
| `config-hash <CONFIG>` | 计算配置哈希，可与设备上的 Version 文本传感器比对 |
| `compile <CONFIG>` | 只编译（`--only-generate` 仅生成 C++ 不编译） |
| `upload <CONFIG>` | 上传最近一次构建的固件 |
| `logs <CONFIG>` | 只看日志 |
| `clean` / `clean-mqtt` | 清理构建目录 / 清除 MQTT 保留的发现消息 |
| `wizard <CONFIG>` | 交互式生成配置骨架 |

常用选项：

| 选项 | 作用 |
|------|------|
| `--device <port-or-ip>` | 指定串口或 IP；可多次给出做兜底（如 `--device 192.168.1.100 --device 2001:db8::1`）；写 `OTA` 表示自动解析地址 |
| `--upload_speed <baud>` | 串口上传速率，默认 460800 |
| `--no-logs` | 上传完不打开日志（CI 里必加） |
| `-s / --substitution KEY VALUE` | 覆盖 substitution，可多次 |
| `--error-format line` | 错误按 `file:line:col: error: ...` 输出，便于编辑器与 CI 链接 |
| `--toolchain <T>` | `esp-idf`（ESP32 默认）/ `arduino`（ESP8266 默认）/ `sdk-nrf` / `host` / `platformio` |
| `-v / --verbose` | 打开 ESPHome 自身的详细日志 |

```bash
# 首次：USB 烧写并进日志
esphome run livingroom.yaml --device /dev/ttyUSB0

# 之后：走 OTA 更新
esphome run livingroom.yaml --device 192.168.1.50

# CI：只校验，不编译不上传
esphome config livingroom.yaml --error-format line
```

## 典型工作流：新设备 → 配置 → USB 首刷 → OTA 更新 → HA 接入

目标：让一块 ESP32-S3 + DHT 温湿度传感器从零变成 Home Assistant 里的两个实体，并验证 OTA 通路。

**步骤 1：生成骨架并填硬件参数**

```bash
esphome wizard livingroom.yaml        # 交互式填 name / 板型 / WiFi
esphome config livingroom.yaml        # 先确认骨架校验通过
```

把 `esp32.variant` 改成实际型号（如 `esp32s3`），WiFi 与密钥移入 `secrets.yaml`。

**步骤 2：加传感器与实体名**

在 YAML 末尾追加上一节的 `sensor:` 段（DHT 接 `GPIO4`），`name` 用人能读懂的名字。

```bash
esphome config livingroom.yaml | grep -A 3 "Living room temperature"
```

**步骤 3：USB 首次烧写**

```bash
esphome run livingroom.yaml --device /dev/ttyUSB0
```

编译完成后开始上传，随后进入日志视图；看到 WiFi 连上、`api` 服务启动即可拔线。

**步骤 4：OTA 更新（改配置后的常规路径）**

```bash
esphome run livingroom.yaml --device 192.168.1.50
esphome run livingroom.yaml --device 192.168.1.50 --no-logs   # 脚本/CI
```

**步骤 5：Home Assistant 接入与验收**

在 HA 的 **设置 → 设备与服务** 等待 ESPHome 集成自动发现（最多约 5 分钟），或手动添加并填 `livingroom.local` 或 IP；启用了加密则填同一把 base64 密钥。

```bash
# 1) 日志里能看到传感器读数变化
esphome logs livingroom.yaml

# 2) 配置哈希与设备上报一致（排错很有用）
esphome config-hash livingroom.yaml

# 3) HA 侧实体存在且状态在变（需要长期令牌）
curl -s -H "Authorization: Bearer $TOKEN" \
  http://homeassistant.local:8123/api/states/sensor.living_room_temperature
```

## 最佳实践

1. **配置进版本控制**：YAML 是唯一事实来源；`secrets.yaml` 与 `.esphome/` 放进 `.gitignore`。
2. **优先 `variant` 而非 `board`**：官方已把 `board` 标为不再推荐，`variant` 会自动补标准 devkit 配置。
3. **固定 IP**：`wifi.manual_ip` 明显缩短连接时间，也让 OTA 目标稳定。
4. **密钥复用**：`api.encryption.key` 与 `ota.encryption` 共用一把，减少漏配。
5. **改配置必跑 `esphome config`**：比直接 `run` 快得多，且不碰硬件就能抓出拼写与缩进错误。
6. **公共片段用 `packages`**：WiFi、OTA、基础诊断抽到 `common/*.yaml`，避免逐台复制。
7. **CI 用 `--no-logs` 加 `--error-format line`**：否则会挂在日志视图上，错误也难以定位。
8. **OTA 翻车留后路**：保留可插 USB 的物理通道，并开启 safe mode（OTA 平台默认启用），否则配置写错可能只能拆机重刷。

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 校验报 `Component not found` / `Platform not found` | 组件名拼错，或该平台不支持当前芯片 | 核对官方组件页名称；ESP8266 上不存在的 ESP32 专属平台会直接报错 |
| `esphome run` 卡在 "Looking for ESP" | 串口名不对，或用户不在 `dialout`/`uucp` 组 | `ls /dev/ttyUSB*` 确认端口；把用户加入串口组后重新登录 |
| OTA 上传失败或连接被拒 | IP 变了、设备掉线，或旧固件没开 OTA | 先用 `ping` 与 `esphome logs` 确认在线；确认 YAML 有 `ota:` 段且至少刷入过一次 |
| HA 里实体缺失或 `unavailable` | 组件没写 `name`，或 API 加密密钥不匹配 | 给组件条目补 `name`；在 HA 里重新配置 ESPHome 集成并填同一密钥 |
| 编译报工具链/依赖下载失败 | 首次构建需联网拉 PlatformIO 平台与库 | 换网络或配代理；Docker 形态把 `/cache` 挂成卷复用 |
| 刷完反复重启（boot loop） | `flash_size` / `flash_mode` 与实际芯片不符，或引脚冲突 | 改成实际值（如 `8MB`）；检查是否把启动引脚复用成普通 GPIO |
| `${key}` 没被替换 | substitution 名大小写不匹配，或引用早于定义 | 名字小写且与 `substitutions` 键完全一致；必要时用 `-s` 覆盖调试 |
| 日志反复出现 `WiFi: Connection lost` | 信号弱或密码错误 | 用 `manual_ip` 并靠近 AP；先用手机确认密码；必要时调 `reboot_timeout` |

## AI 使用建议

- **先探版本**：`esphome version` 确认与文档一致（2026.10.0）；CLI 选项随版本改名，旧教程里的参数可能已失效。
- **不碰硬件也能验证**：改完先 `esphome config --error-format line`，过了校验再谈烧写，能省大量插拔。
- **写盘前确认设备目标**：`run` / `upload` 会覆盖设备固件，`--device` 指错可能刷到别的设备；执行前向用户确认端口或 IP。
- **验证产物**：烧写后用 `esphome logs` 看启动日志与读数，并用 `config-hash` 与设备上报值比对，确认刷进去的是这次构建。
- **密钥不入库**：`secrets.yaml` 与示例里的 `!secret` 占位符不要换成真实值提交，报告里也不要粘贴加密密钥。

## 相关技能

- **home-assistant** — 设备最终接入的平台与 API：[../home-assistant/SKILL.md](../home-assistant/SKILL.md)
- **node-red** — 用低代码编排设备数据流：[../node-red/SKILL.md](../node-red/SKILL.md)
- **ke3036-keyes-pico** — MicroPython 路线的对照（RP2040 学习套件）：[../ke3036-keyes-pico/SKILL.md](../ke3036-keyes-pico/SKILL.md)
- **ollama** — 本地大模型，可与 HA 语音助手组合：[../../ai/ollama/SKILL.md](../../ai/ollama/SKILL.md)

## 相关资源

- 官方文档：<https://esphome.io/>
- CLI 参考：<https://esphome.io/guides/cli/>
- 组件索引：<https://esphome.io/components/>
- 安全最佳实践（密钥与 WiFi）：<https://esphome.io/guides/security_best_practices/>
