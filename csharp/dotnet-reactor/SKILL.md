---
name: dotnet-reactor
description: .NET Reactor 是商业的 .NET 程序集保护工具（Eziriz 出品），提供混淆、控制流加密、字符串加密、IL/Native 代码加密、防调试、序列号 / 试用授权、合并程序集、压缩与许可证管理，广泛用于 .NET 商业软件的版权保护。
tags: dotnet, obfuscation, protection, licensing, security
---

> **官网：** <https://www.eziriz.com/dotnet_reactor.htm>
>
> **下载：** <https://www.eziriz.com/downloads.htm>
>
> **许可证：** 商业（提供个人/企业/全球许可证）

> ⚠️ 本 SKILL 仅作为技术使用说明，请确保使用 .NET Reactor 时拥有合法授权，并仅对自己拥有版权的代码使用。

## 概述

.NET Reactor 主要功能：

- **代码加密**：将 IL 编译为本机受保护代码（Necrobit）
- **混淆**：方法名/类名/字段名重命名、控制流模糊
- **字符串加密**：常量字符串运行时解密
- **资源加密 / 压缩**
- **反调试 / 反篡改 / Anti-ILdasm**
- **许可证系统**：序列号 / 硬件绑定 / 试用期 / 黑名单
- **合并程序集**：将依赖 dll 合并入主可执行文件
- **支持目标**：.NET Framework 2.0 – 4.8、.NET Core / .NET 5/6/7/8、Mono、Xamarin、Unity

---

## 安装与启动

1. 从 Eziriz 官网下载安装
2. 启动 .NET Reactor → 输入授权
3. 主界面：左侧选项卡（Files / Protection / Native EXE File / License Manager / ...）

也支持命令行 `dotNET_Reactor.Console.exe` 与 MSBuild 集成（CI 友好）。

---

## 基本保护流程（GUI）

1. **Files** → Add Files：添加要保护的 .exe / .dll
2. **Protection** 选项卡：
   - **Necrobit Protection**（IL 加密）✅ 推荐
   - **Anti ILDASM** ✅
   - **Anti Tampering** ✅
   - **Obfuscation** → 重命名 ✅
   - **Control Flow Obfuscation** ✅
   - **String Encryption** ✅
   - **Resource Encryption / Compression**（按需）
   - **Anti Debug** ✅
3. **Native EXE File**（可选）：将 EXE 编译为原生壳
4. **Output Path**：输出目录
5. 点击 **Protect**

完成后建议：

- 将原 dll/exe 备份
- 仅分发保护后的版本
- 测试运行（保护可能影响反射、序列化、IL 注入框架）

---

## 命令行（CI / 构建集成）

```bash
dotNET_Reactor.Console -project myproj.nrproj
# 或直接传参
dotNET_Reactor.Console -file App.dll \
                      -targetfile Protected\App.dll \
                      -necrobit 1 -obfuscation 1 -control_flow_obfuscation 1 \
                      -string_encryption 1 -anti_ildasm 1 -anti_tampering 1
```

`-project` 即保存的 GUI 配置（.nrproj XML）。

### MSBuild 集成

```xml
<Target Name="Protect" AfterTargets="Build">
  <Exec Command="dotNET_Reactor.Console -project $(MSBuildThisFileDirectory)protect.nrproj"/>
</Target>
```

---

## 排除规则（不重命名公开 API）

通过 GUI **Obfuscation** 选项卡或属性：

```csharp
[Obfuscation(Exclude = true, ApplyToMembers = true)]
public class PublicApi
{
    public string Hello() => "hi";
}
```

或在 `.nrproj` 中手动配置 Exclude 表。

> 推荐排除：

- 公共 API、对外 SDK
- 反射调用的方法 / 类型
- 序列化字段（JSON/XML/Protobuf）
- WPF/WinForms 控件类型（XAML 绑定）
- DI 容器扫描的服务

---

## 许可证 / 软件授权

### 1. 在主程序加入许可校验

下载 `License Generator + License Library`（Eziriz 提供），在代码中：

```csharp
using DNR.LicenseManager;

if (!License.IsValid()) {
    // 显示注册窗体或退出
    Application.Exit();
}
```

将类标记为不可重命名：

```csharp
[Obfuscation(Exclude = true, ApplyToMembers = true)]
public static class License { ... }
```

### 2. 在 GUI 启用 License Manager

`License Manager` 选项卡 → Enable Licensing → 配置：

- Type：Time-Limited / Hardware-Locked / Single Use
- Public Key：粘贴生成的公钥
- 校验失败动作：退出 / 显示对话框

### 3. 使用 License Generator 生成序列号

- Hardware ID：客户机器唯一码
- Expire Date：到期日
- Custom Data：自定义信息（用户名/邮箱）

---

## 试用版

GUI → License Manager → Trial Settings：

- 试用天数 / 启动次数
- 试用结束动作：禁用功能 / 提示购买 / 退出

---

## 反调试 / 反篡改

GUI → Advanced：

- Anti Debug：检测调试器 → 立即退出
- Anti Tampering：校验程序集签名 / Hash
- VM Detection：检测虚拟机
- Anti ILDASM：标记元数据让 ILDASM 拒绝

---

## 程序集合并

`Files` → Add multi assemblies → `Merge Assemblies`：将依赖打包到主 exe：

- 减少分发文件数
- 一并保护依赖
- 注意：合并后程序集的强签名失效；反射 `Assembly.GetExecutingAssembly().Location` 可能变化

---

## .NET 5/6/7/8 注意事项

- 选择对应运行时（CoreCLR）
- AOT 程序（NativeAOT）目前**不支持**保护，必须使用 JIT 模式
- `dotnet publish -c Release` 后再保护，对 self-contained 多文件目录可批量保护
- 单文件发布：先生成单文件，再保护其外层 EXE 可能受限；建议保护 framework-dependent dll

---

## 与开源混淆器对比

| 工具 | 类型 | 强度 | 注意 |
|------|------|------|------|
| **.NET Reactor** | 商业 | 高（IL 加密 + 控制流） | 收费 |
| ConfuserEx 2 | 开源 | 中 | 维护活跃度低 |
| Obfuscar | 开源 | 仅重命名 | 简单稳定 |
| Eazfuscator.NET | 商业 | 高 | 收费 |

---

## AI 使用建议

### 推荐工作流

1. **先确定保护目标**：反编译防护 → Necrobit + Obfuscation，授权管理 → License Manager，分发简化 → Merge Assemblies
2. **GUI 先调参**：在 GUI 中逐项测试保护效果，保存 `.nrproj` 配置文件
3. **CI 集成**：将 `.nrproj` 加入仓库，MSBuild AfterTarget 自动保护
4. **排除反射类型**：扫描项目中所有 `Type.GetType()` / `Assembly.Load()` 调用，加入 Exclude 列表
5. **测试验证**：对保护后的程序集跑完整回归测试

### 关键模式与常见陷阱

- **反射失效**：混淆后 `Type.GetType("全名")` 会失败，必须排除被反射的类型
- **序列化字段丢失**：JSON/XML/Protobuf 序列化的属性名改变后反序列化失败，需 `[Obfuscation(Exclude=true)]`
- **WPF XAML 绑定断裂**：XAML 中 `{Binding Path=Name}` 依赖属性名，必须排除被绑定的类型
- **DI 容器扫描失败**：`ITransient`/`IScoped` 接口按名称匹配的服务可能失效
- **强签名失效**：合并程序集后强签名会丢失，需在保护后重新签名
- **AV 误报**：Necrobit 加密壳可能被杀软标记，建议联系厂商加白；可选择 Mild 模式降低误报

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 商业软件防破解 | .NET Reactor（Necrobit + 授权） |
| 开源项目基础混淆 | Obfuscar（免费，仅重命名） |
| 无需混淆（API 已鉴权） | 不保护，靠服务端鉴权 |
| 单文件分发 | Merge Assemblies + 保护 |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 反射 `Type.GetType("...")` 失败 | 排除被反射的类型/方法 |
| 序列化字段丢失 | JSON 用 `[JsonProperty]` 显式映射；或排除字段 |
| WPF XAML 绑定失败 | 排除被 XAML 引用的类型与属性 |
| 启动慢 | Necrobit 解密成本；可关闭部分保护项 |
| 被 AV 误报 | 联系杀软厂商加白；选择「Anti Debug = Mild」 |
| Linux 运行报错 | Necrobit 当前对 Linux/.NET Core 支持，需用对应版本 |

---

## 相关技能

- **furion** — .NET Web 框架，dotnet-reactor 可保护 Furion 构建的 API/桌面应用：[../furion/SKILL.md](../furion/SKILL.md)

---

## 参考资源

- 官网与文档：<https://www.eziriz.com/dotnet_reactor.htm>
- 用户手册（PDF）：<https://www.eziriz.com/dotnet_reactor.htm>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/tutorial/dotnet-reactor/>