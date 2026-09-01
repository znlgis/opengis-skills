# Go Language Basics Reference

Go syntax, methods, interfaces, concurrency, error handling and generics split from SKILL.md.

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
    _        = iota  // iota: 1
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

