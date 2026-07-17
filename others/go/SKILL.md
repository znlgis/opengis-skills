---
name: go
description: Use when writing Go/Golang code — goroutines/channels concurrency, net/http web servers, database/sql, generics (1.18+), module management, testing and benchmarking. Go: the language powering Docker, Kubernetes, and cloud-native infrastructure.
tags: [go, golang, backend, concurrency, cloud-native, compiled, static-typed, server, cli]
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
wget https://go.dev/dl/go1.26.4.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.26.4.linux-amd64.tar.gz
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

## 基础语法

### 变量与类型

```go
// 变量声明
var a int = 10           // 显式类型
var b = 20               // 类型推断
c := 30                  // 短变量声明（函数内）
var (                    // 批量声明
    name string = "Go"
    pi   float64 = 3.14
)

// 基本类型
// int/uint (平台相关), int8/16/32/64, uint8/16/32/64
// float32/float64, complex64/complex128
// bool, string, byte(uint8), rune(int32)

// 常量
const Pi = 3.14159
const (
    StatusOK = 200
    _        = iota  // iota: 0
    StatusError      // iota: 2
)
```

### 控制流

```go
// if（可带初始化语句）
if n := len(s); n > 0 {
    fmt.Println(n)
}

// for（Go 只有 for，没有 while）
for i := 0; i < 10; i++ { }        // 经典
for condition { }                   // while 风格
for { break }                       // 无限循环
for i, v := range slice { }         // range 遍历
for k, v := range m { }             // map 遍历（随机顺序）

// switch
switch x {
case 1, 2:
    // ...
case 3:
    // ...
    fallthrough                      // 穿透到下一 case
default:
    // ...
}

// type switch
switch v := i.(type) {
case int:
case string:
}

// Go 1.22+：循环变量每次迭代新作用域
for i := 0; i < 3; i++ {
    go func() { fmt.Println(i) }()  // 正确！输出 0,1,2（Go 1.22+）
}
```

### 函数

```go
// 多返回值
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("divide by zero")
    }
    return a / b, nil
}

// 命名返回值
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return  // naked return
}

// 可变参数
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

// 闭包
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

// defer（LIFO）
func main() {
    defer fmt.Println("third")
    defer fmt.Println("second")
    fmt.Println("first")
    // 输出：first, second, third
}
```

### 复合类型

```go
// 数组（值类型，固定长度）
var arr [3]int = [3]int{1, 2, 3}

// 切片（引用类型，动态长度）
s := []int{1, 2, 3}
s = append(s, 4)
len(s)  // 4
cap(s)  // 底层数组容量
copy(dst, src)

// map（无序，非并发安全）
m := map[string]int{"a": 1, "b": 2}
v, ok := m["a"]     // comma-ok 惯用法
delete(m, "b")

// struct
type Person struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}
p := Person{Name: "Alice", Age: 30}
```

---

## 方法与接口

### 方法

```go
type Counter struct{ count int }

// 值接收者
func (c Counter) Get() int { return c.count }

// 指针接收者（可修改原值）
func (c *Counter) Inc() { c.count++ }
```

### 接口（隐式实现 / 鸭子类型）

```go
type Stringer interface {
    String() string
}

type Animal interface {
    Sound() string
}

type Dog struct{}
func (d Dog) Sound() string { return "Woof" }  // 隐式实现 Animal

// 空接口（Go 1.18+ 别名 any）
var v any = 42

// 类型断言
str, ok := v.(string)

// 接口组合
type ReadWriter interface {
    io.Reader
    io.Writer
}
```

> **nil 接口陷阱**：一个接口值 = (类型, 值)。即使值为 nil，只要类型不为 nil，接口就不为 nil。检查 `if err != nil` 时要注意。

---

## 并发

### goroutine 与 channel

```go
// goroutine
go func() {
    fmt.Println("running in goroutine")
}()

// 无缓冲 channel（同步）
ch := make(chan int)
go func() { ch <- 42 }()
val := <-ch

// 缓冲 channel
ch := make(chan int, 3)
ch <- 1; ch <- 2; ch <- 3

// directional channel
func producer(out chan<- int) { out <- 42 }   // 只发送
func consumer(in <-chan int) { val := <-in }  // 只接收

// range channel
for v := range ch {
    fmt.Println(v)
}
// 需要 close(ch) 才能退出 range

// select（多路复用）
select {
case v := <-ch1:
    fmt.Println(v)
case ch2 <- 42:
case <-time.After(time.Second):
    fmt.Println("timeout")
}
```

### sync 包

```go
// Mutex / RWMutex
var mu sync.RWMutex
mu.Lock(); mu.Unlock()
mu.RLock(); mu.RUnlock()

// WaitGroup
var wg sync.WaitGroup
wg.Add(2)
go func() { defer wg.Done(); /* ... */ }()
go func() { defer wg.Done(); /* ... */ }()
wg.Wait()

// Once（单例）
var once sync.Once
once.Do(func() { /* 初始化 */ })

// atomic（Go 1.19+ 类型化原子操作）
var counter atomic.Int64
counter.Add(1)
counter.Load()

// sync.Map（并发安全 map）
var m sync.Map
m.Store("key", "value")
v, ok := m.Load("key")
```

### context（取消、超时、传值）

```go
// 取消
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

// 超时
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// 传值
ctx = context.WithValue(ctx, "userID", 42)

// 使用
select {
case <-ctx.Done():
    return ctx.Err()
default:
}
```

### 并发模式

```go
// Worker Pool
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        results <- j * 2
    }
}

// Fan-out / Fan-in
func fanOutFanIn(inputs []int) []int {
    out := make(chan int, len(inputs))
    for _, input := range inputs {
        go func(n int) { out <- process(n) }(input)
    }
    var results []int
    for i := 0; i < len(inputs); i++ {
        results = append(results, <-out)
    }
    return results
}

// Pipeline
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() { defer close(out); for _, n := range nums { out <- n } }()
    return out
}
```

---

## 错误处理

```go
// error 接口
type error interface{ Error() string }

// 创建错误
errors.New("error message")
fmt.Errorf("error: %s", detail)

// Go 1.13+ 错误包装
err := fmt.Errorf("operation failed: %w", originalErr)

// 错误检查
errors.Is(err, os.ErrNotExist)     // 值比较
var pathErr *fs.PathError
errors.As(err, &pathErr)            // 类型断言
errors.Unwrap(err)                  // 解包

// panic / recover
defer func() {
    if r := recover(); r != nil {
        log.Println("recovered:", r)
    }
}()
panic("unexpected error")
```

---

## 泛型（Go 1.18+）

```go
// 类型参数
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

// 约束
type Number interface {
    ~int | ~int64 | ~float64
}

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}

// Go 1.21+ 标准库约束
import "cmp"
func Max[T cmp.Ordered](a, b T) T {
    if a > b { return a }
    return b
}

// 泛型类型
type Stack[T any] struct {
    items []T
}
```

---

## 包管理与工程化

### Go Modules

```bash
go mod init github.com/user/project    # 初始化
go mod tidy                            # 整理依赖
go get github.com/pkg/errors@v1.0.0    # 指定版本
go get -u ./...                        # 升级所有
go mod vendor                          # vendor 模式
go work init ./module-a ./module-b     # workspace 模式
```

### 项目结构（推荐）

```
project/
├── cmd/
│   └── app/main.go        # 入口
├── internal/              # 私有包（不可外部导入）
│   ├── handler/
│   ├── service/
│   └── repository/
├── pkg/                   # 公共包（可被导入）
├── api/                   # API 定义（proto/openapi）
├── configs/
├── scripts/
├── go.mod
└── go.sum
```

### 可见性规则

- 首字母大写 = 导出（public）
- 首字母小写 = 未导出（private）
- `internal/` 目录下的包只能被同模块导入

---

## 标准库速查

| 包 | 用途 |
|------|------|
| `net/http` | HTTP 服务端/客户端 |
| `encoding/json` | JSON 序列化/反序列化 |
| `database/sql` | 数据库访问接口 |
| `context` | 取消/超时/值传递 |
| `sync` | 并发原语 |
| `io` / `bufio` | I/O 操作 |
| `os` | 操作系统交互 |
| `fmt` | 格式化 I/O |
| `strings` / `bytes` | 字符串/字节操作 |
| `strconv` | 字符串与类型转换 |
| `time` | 时间操作（参考时间 `2006-01-02 15:04:05`） |
| `regexp` | 正则表达式 |
| `log/slog` | 结构化日志（Go 1.21+） |
| `sort` | 排序 |
| `slices` / `maps` | 泛型切片/映射工具（Go 1.21+） |
| `flag` | 命令行参数 |
| `errors` | 错误处理 |
| `testing` | 测试框架 |
| `html/template` | HTML 模板（自动转义） |

---

## Web 开发

### 标准库 net/http（Go 1.22+ 增强路由）

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type Response struct {
    Message string `json:"message"`
}

func main() {
    mux := http.NewServeMux()

    // Go 1.22+ 增强路由：方法匹配 + 路径参数
    mux.HandleFunc("GET /api/users/{id}", func(w http.ResponseWriter, r *http.Request) {
        id := r.PathValue("id")
        json.NewEncoder(w).Encode(Response{Message: "User " + id})
    })

    mux.HandleFunc("POST /api/users", func(w http.ResponseWriter, r *http.Request) {
        var body struct{ Name string `json:"name"` }
        json.NewDecoder(r.Body).Decode(&body)
        w.WriteHeader(http.StatusCreated)
        json.NewEncoder(w).Encode(Response{Message: "Created " + body.Name})
    })

    log.Println("Server on :8080")
    log.Fatal(http.ListenAndServe(":8080", mux))
}
```

### 中间件模式

```go
func logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

// 优雅关闭
func main() {
    srv := &http.Server{Addr: ":8080", Handler: mux}
    go func() { srv.ListenAndServe() }()
    // 等待中断信号
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, os.Interrupt)
    <-sigCh
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    srv.Shutdown(ctx)
}
```

### 主流 Web 框架对比

| 框架 | 特点 | 适用场景 |
|------|------|---------|
| 标准库 net/http | 零依赖，Go 1.22+ 路由增强 | 小型/微服务 |
| Gin | 高性能，中间件生态丰富 | REST API |
| Echo | 轻量高性能 | REST API |
| Fiber | Express 风格（基于 fasthttp） | 高并发 API |
| Chi | 兼容标准库，轻量 | 微服务 |
| Beego | 全栈 MVC | 企业级应用 |

---

## 数据库

```go
import (
    "database/sql"
    _ "github.com/go-sql-driver/mysql"
)

db, err := sql.Open("mysql", "user:pass@tcp(127.0.0.1:3306)/db?parseTime=true")
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)

// 查询单行
var name string
err = db.QueryRowContext(ctx, "SELECT name FROM users WHERE id = ?", id).Scan(&name)

// 查询多行
rows, err := db.QueryContext(ctx, "SELECT id, name FROM users")
defer rows.Close()
for rows.Next() {
    var id int; var name string
    rows.Scan(&id, &name)
}

// 事务
tx, err := db.BeginTx(ctx, nil)
defer tx.Rollback()  // 安全：Commit 后 Rollback 无操作
_, err = tx.ExecContext(ctx, "INSERT INTO ...")
err = tx.Commit()
```

ORM 工具：GORM（最流行）、sqlx（轻量增强）、sqlc（SQL→代码生成）、ent（Facebook 图式 ORM）

---

## 测试

```go
// xxx_test.go（同包）
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -1, -2},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}

// 基准测试
func BenchmarkProcess(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```

```bash
go test ./...                    # 运行所有测试
go test -v -run TestAdd ./...    # 详细模式，过滤
go test -cover -coverprofile=c.out  # 覆盖率
go test -bench=. -benchmem       # 基准测试 + 内存
go test -race ./...              # 竞态检测器
go tool pprof cpu.prof           # CPU 性能分析
go tool cover -html=c.out        # 覆盖率报告
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

## 常见陷阱

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
