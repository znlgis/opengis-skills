# Go Standard Library, Web and Database Reference

Go package management, standard library, web development, databases and testing split from SKILL.md.

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

