---
name: go
description: "Use when writing Go/Golang code — goroutines/channels concurrency, net/http web servers, database/sql, generics (1.18+), module management, testing and benchmarking. Go: the language powering Docker, Kubernetes, and cloud-native infrastructure."
tags:
  - go
  - golang
  - backend
  - concurrency
  - cloud-native
  - compiled
  - static-typed
  - server
  - cli
---

> **官网：** <https://go.dev/>
>
> **项目地址：** <https://github.com/golang/go>
>
> **官方文档：** <https://go.dev/doc/>
>
> **Go by Example：** <https://gobyexample.com/>
>
> **Effective Go：** <https://go.dev/doc/effective_go>
>
> **许可证：** BSD-3-Clause ｜ **最新稳定版：** 参见 [go.dev/dl](https://go.dev/dl/)

## 概述

Go 是由 Robert Griesemer、Rob Pike 和 Ken Thompson 于 2007 年在 Google 发起的编程语言，2009 年首次公开发布，2012 年发布 Go 1.0。核心设计目标：简洁、高效、安全、并发优先、工程化。

| 特性 | 说明 |
|------|------|
| 静态类型 + 编译型 | 无运行时解释开销，编译为单文件原生机器码 |
| 垃圾回收 | 并发三色标记清除 GC，亚毫秒级 STW |
| 内置并发 | goroutine（轻量线程，2KB 初始栈）+ channel（CSP 模型） |
| 快速编译 | 增量编译 + 包缓存，大型项目秒级构建 |
| 丰富标准库 | net/http、database/sql、encoding/json、context 等开箱即用 |
| 统一代码风格 | `gofmt` 内置格式化，无风格争议 |
| 模块系统 | Go Modules（go.mod），语义版本控制 |
| 泛型 | Go 1.18+ 支持类型参数 |
| 工具链 | testing、benchmark、pprof、race detector 内置 |

### 版本里程碑

| 版本 | 年份 | 关键特性 |
|------|------|---------|
| 1.0 | 2012 | 首个稳定版 |
| 1.7 | 2016 | context 正式入标准库 |
| 1.11 | 2018 | Go Modules 引入 |
| 1.13 | 2019 | error wrapping（%w） |
| 1.18 | 2022 | 泛型、模糊测试、workspace（go.work） |
| 1.21 | 2023 | slices/maps 标准库、log/slog、atomic 类型、cmp.Ordered |
| 1.22 | 2024 | 循环变量每次迭代新作用域、增强 ServeMux 路由 |
| 1.23 | 2024 | range over func（迭代器函数）、unique 包 |
| 1.24 | 2025 | 泛型类型别名、Swiss Table map 优化、weak 指针 |
| 1.26 | 2026 | GC 默认启用新算法、工具链增强 |

---

## 环境准备

### 安装

```bash
# macOS
brew install go

# Linux（官方二进制）
wget https://go.dev/dl/go1.26.5.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.26.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# Windows
winget install Golang.go
```

### 环境变量

```bash
go env GOROOT          # Go 安装目录
go env GOPATH          # Go 工作区（默认 ~/go）
go env GOPROXY         # 模块代理（国内推荐 https://goproxy.cn）
go env GOSUMDB         # 校验数据库（默认 sum.golang.org）
go env GO111MODULE     # 模块模式（on，Go 1.22+ 默认）

# 国内加速
go env -w GOPROXY=https://goproxy.cn,direct
go env -w GOSUMDB=sum.golang.google.cn
```

### IDE 推荐

- **VS Code + gopls**（免费，推荐）
- **GoLand**（JetBrains，商业）
- **Neovim + gopls**（终端流）

---

> 基础语法、方法与接口、并发、错误处理与泛型的完整讲解见 [reference/language-basics.md](reference/language-basics.md)
> 包管理与工程化、标准库速查、Web 开发、数据库与测试的完整内容见 [reference/stdlib-web-db.md](reference/stdlib-web-db.md)

## 典型工作流

### 构建一个包含数据库和中间件的 Go REST API 服务

```bash
# 1. 初始化模块
go mod init example.com/myapi

# 2. 添加依赖
go get github.com/go-chi/chi/v5
go get github.com/go-sql-driver/mysql
go get github.com/redis/go-redis/v9
```

```go
// 3. cmd/api/main.go
package main

import (
    "log"
    "net/http"
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    r := chi.NewRouter()

    // 中间件
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(30 * time.Second))

    // 路由
    r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte(`{"status":"ok"}`))
    })

    r.Route("/api/users", func(r chi.Router) {
        r.Get("/", listUsers)
        r.Post("/", createUser)
        r.Get("/{id}", getUser)
    })

    log.Println("Server on :8080")
    log.Fatal(http.ListenAndServe(":8080", r))
}
```

```bash
# 4. 运行
go run ./cmd/api
```

---

## AI 使用建议

1. **优先用标准库**：Go 标准库覆盖面广（net/http、database/sql、encoding/json）。评估第三方依赖前先检查标准库。
2. **错误必须处理**：Go 没有 try/catch。每个 error 返回值都必须检查，避免 `_` 忽略。
3. **用 context 传播取消**：所有 I/O 操作应接受 `context.Context` 参数，支持超时和取消。
4. **goroutine 防泄漏**：确保每个 goroutine 都有退出路径（channel 关闭 / context 取消 / done 信号）。
5. **先写测试**：table-driven 测试是 Go 社区标准实践。
6. **gofmt 是强制的**：永远不要手动调格式，交给 `gofmt`/`goimports`。
7. **用 golangci-lint**：集成 staticcheck、go vet、unused 等多类静态检查。
8. **接口定义在消费方**：Go 风格是消费者定义接口（interface），而非提供者。
9. **结构体对齐**：字段按大小降序排列可减少 struct 内存占用（对齐填充）。

---

$h$faq`

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| 切片共享底层数组 | `s2 := s1[2:5]` 后修改 s2 影响 s1 | 用 `copy()` 创建独立副本 |
| 循环变量捕获（Go <1.22） | 闭包捕获的循环变量引用同一地址 | Go 1.22+ 已修复；旧版传参 `func(i int)` |
| nil 接口不等于 nil | `var p *T; var i error = p; i != nil` | 检查 `if p == nil` 而非接口 |
| nil map 写入 panic | `var m map[string]int; m["a"]=1` panic | 先 `m = make(map[string]int)` |
| defer 在循环中 | 大量 defer 堆积不执行 | 提取为函数或立即调用 |
| map 并发写 panic | 多 goroutine 同时写同一 map | 用 `sync.Map` 或加锁 |
| 浮点数比较 | `0.1 + 0.2 != 0.3` | 使用 tolerance 比较 |

---

## 参考资源

- [Go 官方文档](https://go.dev/doc/) — 语言规范与标准库
- [Go by Example](https://gobyexample.com/) — 代码示例集合
- [Effective Go](https://go.dev/doc/effective_go) — Go 最佳实践
- [Go Proverbs](https://go-proverbs.github.io/) — Go 设计哲学
- [Go Blog](https://go.dev/blog/) — 官方博客
- [golangci-lint](https://golangci-lint.run/) — 静态分析工具
- [上游中文教程](https://znlgis.github.io/others/go/) — 完整 18 章 Go 教程
