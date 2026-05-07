---
name: ke3036-keyes-pico
description: KE3036 是 Keyes 推出的基于 Raspberry Pi Pico（RP2040）的开源学习套件配套主板/开发板，集成 LED、按键、蜂鸣器、OLED、传感器接口与扩展座，配合 MicroPython / C SDK 适合 IoT、机器人与 STEM 教学。
tags: micropython, rp2040, sensor, iot, pico
---

> **项目地址（资料/示例）：** <https://github.com/keyestudio/ke3036>（具体仓库请以 znlgis.github.io 与 keyestudio 官方为准）
>
> **Pico 官方文档：** <https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html>
>
> **MicroPython for RP2040：** <https://docs.micropython.org/en/latest/rp2/quickref.html>
>
> **许可证：** 配套示例多为 MIT / GPL（视具体文件）

## 概述

KE3036 套件常见组成：

- 主控：Raspberry Pi Pico / Pico W（RP2040，双核 ARM Cortex-M0+，264 KB SRAM，2 MB Flash）
- 外设：板载 LED、按键、蜂鸣器、OLED 0.96"、电位器、光敏、温度等
- 接口：杜邦 / Grove / GPIO 排针
- 配件：传感器扩展包（DHT11、超声波、舵机、显示屏、电机等）

---

## 烧录 MicroPython 固件

```bash
# 1. 下载固件：
#    https://micropython.org/download/RPI_PICO/  → .uf2

# 2. 按住 Pico 上的 BOOTSEL 键插入 USB → 出现 RPI-RP2 磁盘
# 3. 拷贝 .uf2 到该磁盘 → 自动重启进入 MicroPython
```

---

## 工具

```bash
pip install thonny             # 推荐 IDE
pip install mpremote esptool   # 命令行
mpremote connect /dev/ttyACM0 ls
mpremote connect /dev/ttyACM0 cp main.py :main.py
mpremote connect /dev/ttyACM0 run main.py
```

---

## GPIO 入门

### 板载 LED 闪烁（Pico GP25）

```python
from machine import Pin
from time import sleep
led = Pin(25, Pin.OUT)
while True:
    led.toggle()
    sleep(0.5)
```

Pico W 板载 LED：

```python
from machine import Pin
led = Pin("LED", Pin.OUT)
```

### 读取按键

```python
btn = Pin(15, Pin.IN, Pin.PULL_UP)
while True:
    if btn.value() == 0: print("pressed")
    sleep(0.1)
```

### PWM 蜂鸣器

```python
from machine import PWM, Pin
buz = PWM(Pin(14)); buz.freq(880); buz.duty_u16(20000)
sleep(0.5); buz.deinit()
```

---

## 模拟输入（电位器 / 光敏）

```python
from machine import ADC, Pin
adc = ADC(Pin(26))               # GP26 = ADC0
val = adc.read_u16()             # 0..65535
volt = val * 3.3 / 65535
```

板载温度传感器：

```python
adc = ADC(4)
v = adc.read_u16() * 3.3 / 65535
temp = 27 - (v - 0.706) / 0.001721
```

---

## I²C 与 OLED

```python
from machine import I2C, Pin
import ssd1306
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0); oled.text("Hello KE3036", 0, 0); oled.show()
```

---

## SPI / 1-Wire / DHT

```python
import dht, machine
d = dht.DHT11(machine.Pin(28))
d.measure(); print(d.temperature(), d.humidity())
```

---

## Pico W 的 Wi-Fi & MQTT

```python
import network, time
wlan = network.WLAN(network.STA_IF); wlan.active(True)
wlan.connect("SSID","PWD")
while not wlan.isconnected(): time.sleep(0.5)
print(wlan.ifconfig())

from umqtt.simple import MQTTClient
c = MQTTClient("pico", "broker.emqx.io", 1883)
c.connect()
c.publish(b"ke3036/temp", str(d.temperature()).encode())
```

---

## C/C++ SDK（更高性能）

```bash
git clone https://github.com/raspberrypi/pico-sdk
export PICO_SDK_PATH=$PWD/pico-sdk
mkdir build && cd build && cmake .. && make
# 生成 *.uf2，按 BOOTSEL 后拷贝到 RPI-RP2
```

```c
#include "pico/stdlib.h"
int main() {
    gpio_init(25); gpio_set_dir(25, GPIO_OUT);
    while (1) { gpio_put(25, 1); sleep_ms(500);
                gpio_put(25, 0); sleep_ms(500); }
}
```

---

## 常见外设速查

| 外设 | 接法 | 库 |
|------|------|----|
| OLED 0.96 | I²C SDA/SCL | `ssd1306` |
| DHT11/22 | 单线 | `dht` |
| 超声波 HC-SR04 | TRIG/ECHO | `machine.time_pulse_us` |
| 舵机 SG90 | PWM 50 Hz | `PWM` |
| 直流电机 + L298N | PWM + IN1/IN2 | `PWM`/`Pin` |
| MQ-2 烟雾 | ADC | `ADC` |
| RFID RC522 | SPI | `mfrc522` |

---

## 调试与排查

1. 通过 `Thonny → Stop / Restart` 进入 REPL
2. `from machine import freq; freq(125_000_000)`
3. 文件传输：Thonny 文件视图，或 `mpremote`
4. `pico_w` 程序需 `urequests` 等库通过 `mip` 安装：

```python
import mip; mip.install("umqtt.simple")
```

---

## 教学项目示例

- 温湿度记录仪（DHT11 + OLED + Wi-Fi 上报 MQTT）
- 智能小车（L298N + HC-SR04 避障）
- 太阳能小盆栽（光敏 + 舵机遮阳）
- 节奏游戏机（按键 + 蜂鸣器 + OLED）
- 简易 IoT 网关（Wi-Fi + MQTT + 多传感器）

---

## 典型工作流

### 场景一：温湿度记录仪

```python
# 1. 硬件连接：DHT11 接 GP28，OLED 接 I2C0 (SDA=GP0, SCL=GP1)

# 2. main.py
from machine import Pin, I2C
from time import sleep
import dht, ssd1306

# 初始化传感器
sensor = dht.DHT11(Pin(28))
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

while True:
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()

    # 显示到 OLED
    oled.fill(0)
    oled.text(f"Temp: {temp:.1f} C", 0, 0)
    oled.text(f"Hum:  {hum:.1f} %", 0, 20)
    oled.show()

    # 可选：通过 Wi-Fi (Pico W) 上报 MQTT
    # client.publish(b"ke3036/temp", str(temp).encode())

    sleep(5)

# 3. 用 mpremote 部署
# mpremote cp main.py :main.py
# mpremote run main.py
```

### 场景二：智能避障小车

```python
# 硬件：L298N 电机驱动 + HC-SR04 超声波
# 电机：IN1=GP2, IN2=GP3, ENA=GP4, IN3=GP5, IN4=GP6, ENB=GP7
# 超声波：TRIG=GP8, ECHO=GP9

from machine import Pin, PWM
from time import sleep_us, sleep

trig = Pin(8, Pin.OUT)
echo = Pin(9, Pin.IN)
ena = PWM(Pin(4)); enb = PWM(Pin(7))
ena.freq(1000); enb.freq(1000)

def distance():
    trig.low(); sleep_us(2)
    trig.high(); sleep_us(10); trig.low()
    while echo.value() == 0: pass
    start = time.ticks_us()
    while echo.value() == 1: pass
    return time.ticks_diff(time.ticks_us(), start) * 0.0343 / 2

while True:
    if distance() < 20:  # 障碍物 < 20cm → 转向
        # 左转
        ena.duty_u16(30000); enb.duty_u16(0)
    else:
        # 前进
        ena.duty_u16(40000); enb.duty_u16(40000)
    sleep(0.1)
```

---

## AI 使用建议

### 推荐工作流

1. **确认硬件型号**：先确定是 Pico 还是 Pico W（Wi-Fi 能力不同），GP25 vs "LED" 引脚名有差异
2. **烧录 MicroPython 固件**：按住 BOOTSEL 插入 USB → 拖入 `.uf2` → 自动重启
3. **用 Thonny 调试**：Thonny 的 REPL 交互最适合 MicroPython 快速验证
4. **先逐个测试外设**：LED → 按键 → I²C OLED → 传感器，不要一次性连接所有外设
5. **最终固化**：将 `main.py` 通过 `mpremote` 部署到 Pico，上电自启动

### 关键模式与常见陷阱

- **GPIO 引脚编号**：Pico 引脚丝印是 1-40，代码用 GP0-GP28，注意对照表
- **ADC 抖动**：读数波动大时多次采样取平均，或加旁路电容
- **I²C 不上拉**：Pico 内部有弱上拉，但长线或高速通信仍需外接 4.7kΩ 上拉电阻
- **Wi-Fi 仅 2.4GHz**：Pico W 不支持 5GHz，且需设置 `network.country('CN')`
- **文件系统空间**：Pico 只有 ~1.4MB 可用 Flash，大文件需存 SD 卡

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 快速原型 / STEM 教学 | MicroPython + Thonny |
| 高性能 / 实时控制 | C/C++ SDK (pico-sdk) |
| Wi-Fi 数据上报 | Pico W + MQTT |
| 简单桌面自动化 | 不用 Pico，用 openclaw |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 烧录后无 LED | 检查 GP25（Pico）/ "LED"（Pico W）使用正确 |
| ADC 抖动 | 多次平均；接旁路电容 |
| I²C 找不到设备 | `i2c.scan()` 查看；上拉电阻 4.7kΩ |
| Wi-Fi 不连 | 仅支持 2.4 GHz；密码与国别码（`network.country('CN')`） |
| 串口在 Linux 需要权限 | `sudo usermod -aG dialout $USER` |

---

## 相关技能

- **openclaw** — 桌面级 RPA 自动化 Agent，适合 PC 端而非嵌入式的自动化任务：[../../ai/openclaw/SKILL.md](../../ai/openclaw/SKILL.md)

---

## 参考资源

- Pico 文档：<https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html>
- MicroPython RP2 Quickref：<https://docs.micropython.org/en/latest/rp2/quickref.html>
- KE3036 资料：keyestudio 官网与 GitHub
- 中文教程（znlgis）：<https://znlgis.github.io/iot/tutorial/ke3036-keyes-pico/>