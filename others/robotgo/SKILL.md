---
name: robotgo
description: Use when automating desktop GUI operations in Go — mouse/keyboard control, screen capture, image recognition via OpenCV, global hotkeys via gohook. RobotGo: cross-platform Go desktop automation (RPA) library for macOS, Windows, and Linux.
tags: [go, golang, rpa, automation, desktop, screen-capture, mouse, keyboard, clipboard, gui, testing]
---

> **项目地址：** <https://github.com/go-vgo/robotgo>
>
> **官方文档：** <https://github.com/go-vgo/robotgo#documentation>
>
> **许可证：** Apache-2.0 ｜ **最新版本：** 参见 [GitHub Releases](https://github.com/go-vgo/robotgo/releases)｜ **默认分支：** `master`
>
> **生态子库：**
>
> | 子库 | 仓库 | 用途 |
> |------|------|------|
> | gohook | [robotn/gohook](https://github.com/robotn/gohook) | 全局键盘/鼠标事件监听 |
> | bitmap | [vcaesar/bitmap](https://github.com/vcaesar/bitmap) | 位图操作与图像查找 |
> | gcv | [vcaesar/gcv](https://github.com/vcaesar/gcv) | OpenCV 图像识别 |
> | imgo | [vcaesar/imgo](https://github.com/vcaesar/imgo) | 图像读写与格式转换 |
> | adb | [vcaesar/adb](https://github.com/vcaesar/adb) | Android adb 封装（移动端自动化） |

## 概述

RobotGo 是 Go 生态中最成熟的桌面自动化库（GitHub 10.7k+ Star），核心能力覆盖 RPA 全链路：

| 能力域 | 主要 API |
|--------|---------|
| 鼠标控制 | Move、MoveSmooth、MoveRelative、Click、Toggle、DragSmooth、Scroll、ScrollDir |
| 键盘控制 | Type、KeyTap、KeyToggle、UnicodeType、WriteAll、ReadAll |
| 屏幕读取 | GetScreenSize、GetPixelColor、DisplaysNum、GetDisplayBounds、Scale |
| 截图/图像 | CaptureScreen、CaptureImg、SaveCapture、Save、SaveJpeg、DecodeImg |
| 位图查找 | bitmap.Find、bitmap.FindAll、bitmap.Open、bitmap.Save |
| 进程/窗口 | FindIds、Process、PidExists、ActivePid、GetTitle、GetBounds、Kill |
| 全局事件监听 | hook.Register、hook.Start、hook.Process、hook.End |
| OpenCV 识别 | gcv.FindImgFile、gcv.FindAllImgFile、gcv.Find、gcv.FindX |

> **v1.0.0+ 重大变更：** v1.0.0（2025-12）起对 API 进行了重构。v1.0.2 移除了旧版 FindBitmap / OpenBitmap / SaveBitmap 等位图函数（迁移至 `bitmap` 子库）。如需旧 API，使用 `v0.100.10`（最后一个保留旧位图 API 的版本）。

---

## 安装

### 前置条件

- **Go 1.21+**（推荐 1.24+）
- **GCC 工具链**（Cgo 模式必需）

### 平台安装

```bash
# ── macOS ──
brew install go
xcode-select --install
# 需在「系统设置 → 隐私与安全性」中授予「辅助功能」和「屏幕录制」权限

# ── Windows ──
winget install Golang.go
# GCC 工具链（三选一）：
winget install MartinStorsjo.LLVM-MinGW.UCRT   # 推荐：LLVM-MinGW UCRT
# 或 winget install WinLibs.WinLibs-MINGW        # WinLibs GCC
# 或 MSYS2: pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-zlib

# ── Linux (Ubuntu/Debian) ──
sudo apt install gcc libc6-dev
sudo apt install libx11-dev xorg-dev libxtst-dev       # X11
sudo apt install xsel xclip                              # 剪贴板
sudo apt install libpng++-dev                            # 位图
sudo apt install xcb libxcb-xkb-dev x11-xkb-utils libx11-xcb-dev \
     libxkbcommon-x11-dev libxkbcommon-dev              # GoHook

# ── Linux (Fedora) ──
sudo dnf install gcc libXtst-devel xsel xclip libpng-devel \
     libxkbcommon-devel libxkbcommon-x11-devel xkbcomp-devel
```

### 导入与构建

```bash
go get github.com/go-vgo/robotgo
```

**Cgo-free 纯 Go 后端（实验性）：**

```bash
# Windows 纯 Go 后端（无需 GCC）
CGO_ENABLED=0 go build -tags win

# Linux Wayland 后端（wlroots 合成器：Sway/Hyprland/Wayfire）
CGO_ENABLED=0 go build -tags wayland

# Linux GNOME/KDE 后端（通过 xdg-desktop-portal + libei）
CGO_ENABLED=0 go build -tags libei
```

---

## 核心 API

### 鼠标控制

```go
package main

import "github.com/go-vgo/robotgo"

func main() {
    // 瞬移
    robotgo.Move(100, 200)

    // 平滑移动（可选速度系数）
    robotgo.MoveSmooth(300, 400)
    robotgo.MoveSmooth(300, 400, 5.0, 10.0)  // low=5, high=10

    // 相对移动
    robotgo.MoveRelative(10, -5)

    // 当前位置
    x, y := robotgo.Location()

    // 点击
    robotgo.Click()                          // 默认左键单击
    robotgo.Click("right")                   // 右键
    robotgo.Click("center", true)           // 中键双击
    robotgo.Click("wheelLeft")              // 水平滚轮左

    // 按住/释放
    robotgo.Toggle("left", "down")
    // ... 拖拽操作 ...
    robotgo.Toggle("left", "up")

    // 拖拽
    robotgo.DragSmooth(500, 600)

    // 滚轮
    robotgo.ScrollDir(3, "down")            // 向下滚 3 格
    robotgo.Scroll(0, -5)                   // 水平 0, 垂直 -5
    robotgo.ScrollSmooth(10)
    robotgo.ScrollRelative(0, 5)
}
```

### 键盘控制

```go
// 输入文本（支持 Unicode / 中文）
robotgo.Type("Hello 世界")
robotgo.Type("Hello", pid)                   // 指定目标进程

// Unicode 码点输入
robotgo.UnicodeType(0x4e16)                 // '世'

// 按键（支持修饰键组合）
robotgo.KeyTap("a")
robotgo.KeyTap("ctrl", "c")                 // Ctrl+C
robotgo.KeyTap("ctrl", "shift", "t")       // Ctrl+Shift+T

// 按住/释放
robotgo.KeyToggle("shift", "down")
// ... 操作 ...
robotgo.KeyToggle("shift", "up")

// 键名速查
// 字母：a-z, A-Z ｜ 数字：0-9
// 控制：enter, tab, esc, backspace, delete, space
// 方向：up, down, left, right
// 导航：home, end, pageup, pagedown
// 功能：f1-f24
// 修饰：cmd, ctrl, alt, shift（含左右变体 cmdl/cmdr, ctrll/ctrlr, altl/altr, shiftl/shiftr）
// 多媒体：audio_mute, audio_vol_up, audio_vol_down, audio_play, audio_stop, audio_pause
// 小键盘：num0-num9, num.+-*/, num_clear, num_enter, num_equal
```

### 屏幕读取

```go
w, h := robotgo.GetScreenSize()
color := robotgo.GetPixelColor(10, 10)      // 返回 hex（不含 #）

// 多显示器
num := robotgo.DisplaysNum()
x, y, dw, dh := robotgo.GetDisplayBounds(1)  // 第二台显示器
robotgo.DisplayID = 1                        // 设置目标显示器

// DPI 缩放
scale := robotgo.Scale()                      // int
scaleF := robotgo.ScaleF()                    // float64
```

### 截图与图像

```go
// 一行截图保存
robotgo.SaveCapture("screenshot.png")

// 区域截图
robotgo.SaveCapture("region.png", 0, 0, 800, 600)

// 获取位图对象（v1.0+ 必须手动释放）
bit := robotgo.CaptureScreen(0, 0, 800, 600)
defer robotgo.FreeBitmap(bit)

// 获取 Go image.Image（无需手动释放）
img, err := robotgo.CaptureImg(0, 0, 800, 600)

// 保存图像
robotgo.Save(img, "output.bmp")
robotgo.SaveJpeg(img, "output.jpg", 75)    // quality=75

// 解码图像文件
img2, ext, err := robotgo.DecodeImg("photo.png")

// 类型转换
goImg := robotgo.ToImage(bit)                // CBitmap → image.Image
```

### 位图查找（via bitmap 子库）

```go
import "github.com/vcaesar/bitmap"

// 从文件加载位图
bit := bitmap.Open("template.png")

// 查找（返回坐标，未找到返回 -1, -1）
x, y := bitmap.Find(bit)
if x != -1 && y != -1 {
    robotgo.Move(x, y)
    robotgo.Click()
}

// 查找全部匹配
results := bitmap.FindAll(bit)
for _, r := range results {
    fmt.Printf("Found at (%d, %d)\n", r.X, r.Y)
}
```

### 剪贴板

```go
robotgo.WriteAll("Hello")
text, err := robotgo.ReadAll()
// Linux 需要 xsel 或 xclip 已安装
```

### 进程与窗口管理

```go
// 查找进程（部分匹配）
pids, _ := robotgo.FindIds("chrome")

// 进程信息
procs, _ := robotgo.Process()
exists, _ := robotgo.PidExists(1234)
name, _ := robotgo.FindName(1234)

// 窗口操作
robotgo.ActivePid(pids[0])                  // 激活窗口
robotgo.ActiveName("Chrome")
title := robotgo.GetTitle(pids[0])
x, y, w, h := robotgo.GetBounds(pids[0])
robotgo.Kill(pids[0])

// 系统对话框
ok := robotgo.Alert("提示", "确定要执行吗？")
```

### 全局事件监听（via gohook 子库）

```go
package main

import (
    "fmt"
    hook "github.com/robotn/gohook"
)

func main() {
    // 注册事件回调
    hook.Register(hook.KeyDown, []string{"q", "ctrl"}, func(e hook.Event) {
        fmt.Println("Ctrl+Q pressed, exiting...")
        hook.End()
    })

    hook.Register(hook.MouseDown, []string{}, func(e hook.Event) {
        fmt.Printf("Mouse at (%d, %d)\n", e.X, e.Y)
    })

    // 启动监听（阻塞）
    s := hook.Start()
    hook.Process(s)    // 处理回调，直到 hook.End()
}

// ── 阻塞式单事件等待 ──
ok := hook.AddEvent("ctrl")          // 等待 Ctrl 按下
ok = hook.AddEvents("ctrl", "shift") // 等待 Ctrl+Shift 组合
```

### OpenCV 图像识别（via gcv 子库）

```go
import "github.com/vcaesar/gcv"

// 基于文件的模板匹配
result := gcv.FindImgFile("template.png", "screenshot.png")
fmt.Printf("Found at (%d, %d)\n", result.TopLeft.X, result.TopLeft.Y)

// 查找全部匹配
results := gcv.FindAllImgFile("template.png", "screenshot.png")

// 基于内存图像的匹配
result := gcv.FindImg(templateImg, sourceImg)

// 便捷坐标返回
x, y := gcv.FindX(templateImg, sourceImg)
```

> **gcv 依赖：** 需要安装 OpenCV + [GoCV](https://github.com/hybridgroup/gocv)。安装方法参考 GoCV 官方文档。

---

## 典型工作流

### 工作流 1：等待图像出现并点击

```go
func waitAndClick(template string, timeout time.Duration) error {
    deadline := time.Now().Add(timeout)
    for time.Now().Before(deadline) {
        // 截屏
        img, _ := robotgo.CaptureImg()
        // 查找
        result := gcv.FindImgFile(template, "temp.png")
        robotgo.Save(img, "temp.png")
        if result.TopLeft.X >= 0 {
            robotgo.MoveSmooth(result.TopLeft.X+5, result.TopLeft.Y+5)
            time.Sleep(100 * time.Millisecond)
            robotgo.Click()
            return nil
        }
        time.Sleep(500 * time.Millisecond)
    }
    return fmt.Errorf("timeout waiting for %s", template)
}
```

### 工作流 2：RPA 自动填表

```go
func fillForm() {
    // 1. 激活目标窗口
    pids, _ := robotgo.FindIds("notepad")
    if len(pids) > 0 {
        robotgo.ActivePid(pids[0])
    }

    time.Sleep(500 * time.Millisecond)

    // 2. 通过剪贴板输入（避免输入法干扰）
    robotgo.WriteAll("自动填入的内容")
    robotgo.KeyTap("ctrl", "v")

    // 3. Tab 导航
    robotgo.KeyTap("tab")
    robotgo.WriteAll("第二字段")
    robotgo.KeyTap("ctrl", "v")

    // 4. 回车提交
    robotgo.KeyTap("enter")
}
```

### 工作流 3：全局热键启动器

```go
func hotkeyLauncher() {
    hook.Register(hook.KeyDown, []string{"ctrl", "shift", "s"}, func(e hook.Event) {
        // 截图保存
        robotgo.SaveCapture(fmt.Sprintf("shot_%d.png", time.Now().Unix()))
    })

    hook.Register(hook.KeyDown, []string{"ctrl", "shift", "q"}, func(e hook.Event) {
        hook.End()
    })

    s := hook.Start()
    hook.Process(s)
}
```

---

## 延时控制

```go
robotgo.Sleep(2)                           // 秒
robotgo.MilliSleep(500)                    // 毫秒

// 全局操作间隔（影响所有鼠标/键盘操作）
robotgo.MouseSleep = 100                    // 鼠标操作后等待 100ms
robotgo.KeySleep = 50                      // 键盘操作后等待 50ms
```

---

## AI 使用建议

1. **优先用 CaptureImg 而非 CaptureScreen**：CaptureImg 返回 `image.Image` 无需手动释放，避免内存泄漏。
2. **中文输入用剪贴板**：`Type()` 可能被活动输入法拦截/转换。中文文本建议 `WriteAll()` + `KeyTap("ctrl", "v")`。
3. **macOS 权限**：程序运行前必须授予终端/IDE 的「辅助功能」和「屏幕录制」权限，否则鼠标键盘静默失效、截图全黑。
4. **位图模板需同环境截取**：`bitmap.Find` 要求精确像素匹配，不同分辨率/DPI/主题/抗锯齿下会失败。
5. **防无限循环**：robotgo 模拟的键鼠事件会被 gohook 捕获。用状态标志区分「程序触发」和「用户操作」。
6. **v1.0+ API 变更**：若从 v0.100.x 迁移，注意 `FindBitmap`/`OpenBitmap`/`SaveBitmap` 已移至 `bitmap` 子库，`GetBitmapSize` 改为 `GetImgSize(path)`。
7. **CGO 交叉编译极困难**：Cgo 模式需要目标平台的 C 交叉工具链和系统头文件。推荐在各平台原生构建，或使用 Cgo-free 后端。

---

## 常见问题（FAQ）

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| macOS 鼠标/键盘无反应 | 未授予权限 | 系统设置 → 隐私与安全性 → 辅助功能 + 屏幕录制 |
| 截图全黑 | 未授予屏幕录制权限 | 同上 |
| `png.h not found` | 缺少 libpng 开发头文件 | Linux: `apt install libpng++-dev`；Windows: 换用 Cgo-free `-tags win` |
| Linux 剪贴板报错 | 未安装 xsel/xclip | `apt install xsel xclip` |
| Wayland 下无法工作 | Wayland 不支持 X11 协议 | 使用 `-tags wayland`（wlroots）或 `-tags libei`（GNOME/KDE） |
| `bitmap.Find` 总返回 -1,-1 | 模板与截图环境不一致 | 确保相同分辨率/DPI/缩放/主题下截取模板 |
| Go 1.10.x 编译报错 | Go #24355 缓存 Bug | 升级 Go 到 1.21+ |
| libei 后端截图失败 | libei 仅处理输入 | libei 后端不支持截图/窗口管理，使用 Cgo 模式 |

---

## RobotGo-Pro（商业版）

RobotGo-Pro 是非开源商业版本，提供 JavaScript、Python、Lua 等多语言绑定，包含技术支持和新特性。本技能仅覆盖开源 Go 版本。

---

## 参考资源

- [RobotGo GitHub](https://github.com/go-vgo/robotgo) — 源码与文档
- [gohook](https://github.com/robotn/gohook) — 全局事件监听
- [bitmap](https://github.com/vcaesar/bitmap) — 位图操作
- [gcv](https://github.com/vcaesar/gcv) — OpenCV 图像识别
- [GoCV](https://github.com/hybridgroup/gocv) — OpenCV Go 绑定（gcv 依赖）
- [上游中文教程](https://znlgis.github.io/others/robotgo/) — 完整 15 章 RobotGo 教程
