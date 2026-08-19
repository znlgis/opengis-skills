---
name: robotgo-flow
description: "Use when building YAML-driven Windows RPA workflows in Go — step-by-step desktop automation with image template matching, interactive recording mode, hotkey triggers. RobotGo-Flow: YAML-based Windows RPA framework built on RobotGo."
tags:
  - go
  - golang
  - rpa
  - automation
  - desktop
  - windows
  - yaml
  - image-matching
  - wpf
---

> **项目地址：** <https://github.com/znlgis/robotgo-flow>
> **官方文档：** <https://github.com/znlgis/robotgo-flow#readme>
>
> **底层库：** [go-vgo/robotgo](https://github.com/go-vgo/robotgo)
>
> **上游中文教程：** <https://znlgis.github.io/others/robotgo-flow/>（共 19 章）
>
> **许可证：** MIT License

## 概述

robotgo-flow 是一款基于 [robotgo](https://github.com/go-vgo/robotgo) 实现的 **Windows 桌面 RPA 自动化框架**。通过 YAML 声明式描述自动化流程，用图像模板匹配定位屏幕 UI 元素，自动执行鼠标、键盘、浏览器等操作，**无需编写 Go 代码**。

- **Go CLI**：纯命令行工具（`run` / `record` / `capture` / `serve`），专注自动化逻辑。
- **WPF 托盘应用**：基于 .NET 10 WPF 的 Windows 托盘应用，实时进度监控与任务栏通知（可选组件）。
- **图像模板匹配**：预截取 UI 元素截图定位目标，适应窗口位置变化；窗口内优先搜索、全屏回退。
- **交互式动作**：运行时输入框（支持密码隐藏）、确认对话框、系统通知，可实现人工决策节点。
- **运行时变量注入**：`$input.<name>` 占位符，运行时动态替换文本。
- **人类行为模拟**：贝塞尔曲线鼠标轨迹、打字错误与修正、可变延迟、空闲抖动，降低被检测风险。
- **交互式录制器与截图工具**：CLI 逐步引导录制工作流、框选截图。
- **容错与调试**：每步自动截图、从指定步骤恢复、abort/skip/retry 三种错误策略、context 安全取消。
- **GBK/UTF-8 自动编码**：Windows 中文环境下自动处理路径与 YAML 编码。

> 当前仅支持 Windows 平台。命令与字段以仓库最新代码为准。

---

## 环境与构建

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Go | `1.26+` | <https://go.dev/dl/> |
| GCC (MinGW-w64) | x86_64 | 通过 MSYS2 安装 |
| .NET | `10.0+` | 仅 WPF 托盘应用需要 |
| Windows | 10 / 11 | 当前仅支持 Windows |

```powershell
# 安装 MSYS2 与编译工具链
winget install MSYS2.MSYS2
# 在 MSYS2 终端中：
pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-zlib
# 将 C:\msys64\mingw64\bin 加入系统 PATH
```

> 首次编译约 4 分钟（需编译 GLFW C 源码），后续增量编译约 1 秒。

```powershell
# 构建 Go CLI（必需）
.\scripts\build.ps1            # 优化输出（strip 调试信息）
.\scripts\build.ps1 -NoStrip   # 调试版本

# 构建 WPF 托盘应用（可选）
cd src\csharp
dotnet build RobotgoFlow.Wpf.sln -c Release

# 构建供 Tray 调用的 Go c-shared DLL
.\scripts\build.ps1 -Dll
```

---

## CLI 命令

```powershell
robotgo-flow                       # 无参数 → 显示帮助
robotgo-flow run <工作流文件>      # 执行工作流
robotgo-flow record                # 交互式录制工作流
robotgo-flow capture [元素名]      # 交互式截取模板
robotgo-flow serve <工作流文件>    # JSON-Line 协议服务（供 WPF GUI 调用）
```

**`run` 参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--from N` | 1（从头） | 从第 N 步开始执行（1-indexed） |
| `--debug` | false | 每步自动保存截图到输出目录 |
| `--out dir` | 工作流所在目录 | 截图输出目录（默认 `screenshots/`） |

```powershell
./robotgo-flow.exe run workflow.yaml
./robotgo-flow.exe run workflow.yaml --from 3     # 从第 3 步开始
./robotgo-flow.exe run workflow.yaml --debug      # 调试模式
```

**`record` 参数：** `--out`（默认 `workflow.yml`）、`--tpl-dir`（默认 `./templates`）。
**`capture` 参数：** `--out-dir`（默认 `templates`）。

---

## YAML 工作流结构

```yaml
name: "工作流名称"              # 必填
description: "描述"             # 可选
inputs:                        # 可选：运行时变量定义
  - name: username             #   变量名（引用：$input.username）
    label: "用户名"            #   输入提示标签
    required: true             #   是否必填
    placeholder: "请输入用户名" #   占位符（可选）
    mask: false                #   是否隐藏输入（密码模式）
settings:                      # 可选：全局设置
  element_timeout: 10          #   等待元素超时秒数（默认 10）
  on_error: abort              #   错误策略：abort / skip / retry（默认 abort）
  max_retries: 3               #   retry 模式最大重试次数（默认 3）
  browser_refresh_delay: 3     #   刷新页面等待秒数（默认 3）
  browser_navigation_delay: 2  #   前进/后退等待秒数（默认 2）
  browser_page_load_delay: 3   #   打开 URL 等待秒数（默认 3）
  human:                       #   人类行为模拟
    enabled: false             #     是否启用
    speed: 1.0                 #     速度系数（0.1~5.0，默认 1.0）
    mistake_rate: 0.03         #     打字错误率（0.0~1.0，默认 0.0）
steps:                         # 必填：步骤列表
  - name: "步骤名"
    actions: [...]             #   动作列表
```

### 错误处理策略（`on_error`）

| 值 | 说明 |
|----|------|
| `abort` | 立即终止执行（默认） |
| `skip` | 记录错误日志，跳过当前动作，继续下一个 |
| `retry` | 重试当前动作，最多 `max_retries` 次；耗尽后 abort |

---

## 动作参考

```yaml
# —— 鼠标 ——
- click: "templates/button.png"          # 模板匹配点击
- click: {x: 500, y: 300}                # 坐标点击
- double_click: "templates/item.png"
- right_click: "templates/menu.png"
- drag: {from: "templates/src.png", to: "templates/dst.png"}

# —— 键盘 ——
- type: {into: "templates/input.png", text: "Hello World"}
- press: "enter"                         # enter/tab/escape/backspace/space...
- combo: ["ctrl", "c"]                   # 组合键

# —— 等待/延时 ——
- wait: "templates/done.png"             # 等待元素出现（默认 element_timeout）
- wait: {template: "templates/popup.png", timeout: 30}
- wait_gone: "templates/loading.png"     # 等待元素消失
- sleep: 2.5                             # 固定延时（秒，支持小数）

# —— 浏览器 ——
- open_url: "https://example.com"        # 剪贴板+地址栏，自动定位浏览器窗口
- refresh: true                          # Ctrl+R
- back: true                             # Alt+Left
- forward: true                          # Alt+Right
- switch_tab: 2                          # Ctrl+数字（1-9）
- scroll: 500                            # 正数向下、负数向上

# —— 交互式 ——
- prompt: {title: "请输入验证码", message: "已发送至手机", into: "templates/input_code.png", mask: false}
- confirm: {title: "确认操作", message: "是否提交？"}
- notify: {title: "提醒", message: "处理已完成", duration: 3}
```

### 运行时变量注入

工作流文本可用 `$input.<变量名>` 占位符，执行前提示用户输入：

```yaml
inputs:
  - {name: username, label: "用户名", required: true}
  - {name: password, label: "密码", required: true, mask: true}
steps:
  - name: "登录"
    actions:
      - type: {into: "templates/input_user.png", text: "$input.username"}
      - type: {into: "templates/input_pwd.png", text: "$input.password"}
      - press: "enter"
```

---

## 图像模板匹配

1. 预先截取目标 UI 元素截图（PNG），保存到 `templates/`。
2. 运行时通过 `robotgo.FindBitmap()` 在屏幕搜索模板。
3. 定位成功后，在匹配位置中心执行鼠标/键盘操作。

- **窗口内搜索（优先）**：检测到浏览器窗口（Chrome/Edge/Firefox/Brave/Opera）时截取窗口区域匹配，避免误匹配。
- **全屏回退**：窗口内未找到时回退全屏搜索。
- 模板路径相对于工作流 YAML 所在目录。推荐结构：`project/{workflow.yaml, templates/*.png}`。

---

## 人类行为模拟

`settings.human.enabled: true` 启用，降低自动化被检测风险：

| 行为 | 说明 |
|------|------|
| 贝塞尔曲线鼠标轨迹 | 自然曲线路径，靠近目标减速 |
| 打字错误模拟 | 按 `mistake_rate` 引入相邻键错误/漏字/顺序颠倒并自动修正 |
| 可变延迟 | 操作间隔在随机范围内变化 |
| 滚动抖动 | 分块滚动，概率轻微反向回滚 |
| 空闲行为 | 长时等待时鼠标微抖动、步骤间概率移动到随机位置 |

---

## 架构与二次开发

- Go 源码位于 `src/go`：`cmd/robotgo-flow`（入口）、`internal/{config,engine,action,executor,serve,recorder,capture,encoding}`。
- `internal/action` 定义 `Runner` 与 `Engine` 接口，作为引擎与执行器契约；`factory.go` 的 `FromConfig` 将 `config.Action` 映射为 `Runner` 实现——**扩展新动作类型**即在此新增。
- WPF 托盘应用 (`src/csharp`) 通过 `robotgo-flow serve` 子进程 + JSON-Line stdin/stdout 协议通信。

```powershell
cd src/go
go test ./...                       # 运行全部测试
go test ./internal/config/ -v
go test ./internal/action/ -v
```

---

## AI 使用建议

- 生成工作流时优先用**模板匹配**（`templates/*.png`）而非硬编码坐标，以适应窗口移动。
- 涉及登录/密码等敏感输入，用 `inputs` + `$input.*` + `mask: true`，不要把凭证写进 YAML。
- 不稳定步骤设置 `on_error: retry` + `max_retries`；调试用 `run --debug` 逐步截图。
- 需要拟人化/反检测时启用 `settings.human`。
- 仅 Windows 平台；提醒用户 Go `1.26+` 与 MinGW-w64 工具链是编译前提。

---

## 常见问题（FAQ）

| 问题 | 说明 |
|------|------|
| 模板匹配不到元素？ | 确认截图清晰、缩放一致；浏览器场景确保目标在窗口内；必要时重新 `capture`。 |
| 首次编译很慢？ | 需编译 GLFW C 源码，约 4 分钟；后续增量编译约 1 秒。 |
| 中文路径乱码？ | `internal/encoding` 自动处理 GBK↔UTF-8，无需手动干预。 |
| 一定要 WPF 应用吗？ | 不需要；Go CLI 可独立使用，不依赖 .NET/WPF。 |
| 如何从中途恢复执行？ | `run --from N`（1-indexed）。 |

---

## 参考资源

- 项目仓库：<https://github.com/znlgis/robotgo-flow>
- robotgo 底层库：<https://github.com/go-vgo/robotgo>
- 上游中文教程（19 章）：<https://znlgis.github.io/others/robotgo-flow/>
- 相关技能：[../robotgo/SKILL.md](../robotgo/SKILL.md)（robotgo 库本身）
