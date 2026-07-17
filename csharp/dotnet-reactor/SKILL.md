---
name: dotnet-reactor
description: "Use when protecting .NET assemblies from reverse engineering  -- ?obfuscation, string encryption, control flow obfuscation, anti-debugging, licensing. .NET Reactor: commercial-grade .NET code protection and licensing tool."
tags: [dotnet, obfuscation, protection, licensing, security]
---

> **官网 -- ?* <https://www.eziriz.com/dotnet_reactor.htm>
>
> **下载 -- ?* <https://www.eziriz.com/downloads.htm>
>
> **许可证：** 商业（提供个 -- ?企业/全球许可证）

> ⚠️  -- ?SKILL 仅作为技术使用说明，请确保使 -- ?.NET Reactor 时拥有合法授权，并仅对自己拥有版权的代码使用 -- ?

## 概述

.NET Reactor 主要功能 -- ?

- **代码加密**：将 IL 编译为本机受保护代码（Necrobit -- ?
- **混淆**：方法名/类名/字段名重命名、控制流模糊
- **字符串加 -- ?*：常量字符串运行时解 -- ?
- **资源加密 / 压缩**
- **反调 -- ?/ 反篡 -- ?/ Anti-ILdasm**
- **许可证系 -- ?*：序列号 / 硬件绑定 / 试用 -- ?/ 黑名 -- ?
- **合并程序 -- ?*：将依赖 dll 合并入主可执行文 -- ?
- **支持目标** -- ?NET Framework 2.0  -- ?4.8 -- ?NET Core / .NET 5-10、Mono、Xamarin、Unity

---

## 安装与启 -- ?

1.  -- ?Eziriz 官网下载安装
2. 启动 .NET Reactor  -- ?输入授权
3. 主界面：左侧选项卡（Files / Protection / Native EXE File / License Manager / ... -- ?

也支持命令行 `dotNET_Reactor.Console.exe`  -- ?MSBuild 集成（CI 友好） -- ?

---

## 基本保护流程（GUI -- ?

1. **Files**  -- ?Add Files：添加要保护 -- ?.exe / .dll
2. **Protection** 选项卡：
   - **Necrobit Protection**（IL 加密）✅ 推荐
   - **Anti ILDASM**  -- ?
   - **Anti Tampering**  -- ?
   - **Obfuscation**  -- ?重命 -- ? -- ?
   - **Control Flow Obfuscation**  -- ?
   - **String Encryption**  -- ?
   - **Resource Encryption / Compression**（按需 -- ?
   - **Anti Debug**  -- ?
3. **Native EXE File**（可选）：将 EXE 编译为原生壳
4. **Output Path**：输出目 -- ?
5. 点击 **Protect**

完成后建议：

- 将原 dll/exe 备份
- 仅分发保护后的版 -- ?
- 测试运行（保护可能影响反射、序列化、IL 注入框架 -- ?

---

## 命令行（CI / 构建集成 -- ?

```bash
dotNET_Reactor.Console -project myproj.nrproj
# 或直接传 -- ?
dotNET_Reactor.Console -file App.dll \
                      -targetfile Protected\App.dll \
                      -necrobit 1 -obfuscation 1 -control_flow_obfuscation 1 \
                      -string_encryption 1 -anti_ildasm 1 -anti_tampering 1
```

`-project` 即保存的 GUI 配置 -- ?nrproj XML） -- ?

### MSBuild 集成

```xml
<Target Name="Protect" AfterTargets="Build">
  <Exec Command="dotNET_Reactor.Console -project $(MSBuildThisFileDirectory)protect.nrproj"/>
</Target>
```

---

## 排除规则（不重命名公开 API -- ?

通过 GUI **Obfuscation** 选项卡或属性：

```csharp
[Obfuscation(Exclude = true, ApplyToMembers = true)]
public class PublicApi
{
    public string Hello() => "hi";
}
```

或在 `.nrproj` 中手动配 -- ?Exclude 表 -- ?

> 推荐排除 -- ?

- 公共 API、对 -- ?SDK
- 反射调用的方 -- ?/ 类型
- 序列化字段（JSON/XML/Protobuf -- ?
- WPF/WinForms 控件类型（XAML 绑定 -- ?
- DI 容器扫描的服 -- ?

---

## 许可 -- ?/ 软件授权

### 1. 在主程序加入许可校验

下载 `License Generator + License Library`（Eziriz 提供），在代码中 -- ?

```csharp
using DNR.LicenseManager;

if (!License.IsValid()) {
    // 显示注册窗体或退 -- ?
    Application.Exit();
}
```

将类标记为不可重命名 -- ?

```csharp
[Obfuscation(Exclude = true, ApplyToMembers = true)]
public static class License { ... }
```

### 2.  -- ?GUI 启用 License Manager

`License Manager` 选项 -- ? -- ?Enable Licensing  -- ?配置 -- ?

- Type：Time-Limited / Hardware-Locked / Single Use
- Public Key：粘贴生成的公钥
- 校验失败动作：退 -- ?/ 显示对话 -- ?

### 3. 使用 License Generator 生成序列 -- ?

- Hardware ID：客户机器唯一 -- ?
- Expire Date：到期日
- Custom Data：自定义信息（用户名/邮箱 -- ?

---

## 试用 -- ?

GUI  -- ?License Manager  -- ?Trial Settings -- ?

- 试用天数 / 启动次数
- 试用结束动作：禁用功 -- ?/ 提示购买 / 退 -- ?

---

## 反调 -- ?/ 反篡 -- ?

GUI  -- ?Advanced -- ?

- Anti Debug：检测调试器  -- ?立即退 -- ?
- Anti Tampering：校验程序集签名 / Hash
- VM Detection：检测虚拟机
- Anti ILDASM：标记元数据 -- ?ILDASM 拒绝

---

## 程序集合 -- ?

`Files`  -- ?Add multi assemblies  -- ?`Merge Assemblies`：将依赖打包到主 exe -- ?

- 减少分发文件 -- ?
- 一并保护依 -- ?
- 注意：合并后程序集的强签名失效；反射 `Assembly.GetExecutingAssembly().Location` 可能变化

---

## .NET 5/6/7/8 注意事项

- 选择对应运行时（CoreCLR -- ?
- AOT 程序（NativeAOT）目 -- ?*不支 -- ?*保护，必须使 -- ?JIT 模式
- `dotnet publish -c Release` 后再保护，对 self-contained 多文件目录可批量保护
- 单文件发布：先生成单文件，再保护其外 -- ?EXE 可能受限；建议保 -- ?framework-dependent dll

---

## 与开源混淆器对比

| 工具 | 类型 | 强度 | 注意 |
|------|------|------|------|
| **.NET Reactor** | 商业 | 高（IL 加密 + 控制流） | 收费 |
| ConfuserEx 2 | 开 -- ?|  -- ?| 维护活跃度低 |
| Obfuscar | 开 -- ?| 仅重命名 | 简单稳 -- ?|
| Eazfuscator.NET | 商业 |  -- ?| 收费 |

---

## AI 使用建议

### 推荐工作 -- ?

1. **先确定保护目 -- ?*：反编译防护  -- ?Necrobit + Obfuscation，授权管 -- ? -- ?License Manager，分发简 -- ? -- ?Merge Assemblies
2. **GUI 先调 -- ?*：在 GUI 中逐项测试保护效果，保 -- ?`.nrproj` 配置文件
3. **CI 集成**：将 `.nrproj` 加入仓库，MSBuild AfterTarget 自动保护
4. **排除反射类型**：扫描项目中所 -- ?`Type.GetType()` / `Assembly.Load()` 调用，加 -- ?Exclude 列表
5. **测试验证**：对保护后的程序集跑完整回归测试

### 关键模式与常见陷 -- ?

- **反射失效**：混淆后 `Type.GetType("全名")` 会失败，必须排除被反射的类型
- **序列化字段丢 -- ?*：JSON/XML/Protobuf 序列化的属性名改变后反序列化失败，需 `[Obfuscation(Exclude=true)]`
- **WPF XAML 绑定断裂**：XAML  -- ?`{Binding Path=Name}` 依赖属性名，必须排除被绑定的类 -- ?
- **DI 容器扫描失败**：`ITransient`/`IScoped` 接口按名称匹配的服务可能失效
- **强签名失 -- ?*：合并程序集后强签名会丢失，需在保护后重新签名
- **AV 误报**：Necrobit 加密壳可能被杀软标记，建议联系厂商加白；可选择 Mild 模式降低误报

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 商业软件防破 -- ?| .NET Reactor（Necrobit + 授权 -- ?|
| 开源项目基础混淆 | Obfuscar（免费，仅重命名 -- ?|
| 无需混淆（API 已鉴权） | 不保护，靠服务端鉴权 |
| 单文件分 -- ?| Merge Assemblies + 保护 |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 反射 `Type.GetType("...")` 失败 | 排除被反射的类型/方法 |
| 序列化字段丢 -- ?| JSON  -- ?`[JsonProperty]` 显式映射；或排除字段 |
| WPF XAML 绑定失败 | 排除 -- ?XAML 引用的类型与属 -- ?|
| 启动 -- ?| Necrobit 解密成本；可关闭部分保护 -- ?|
|  -- ?AV 误报 | 联系杀软厂商加白；选择「Anti Debug = Mild -- ?|
| Linux 运行报错 | Necrobit 当前 -- ?Linux/.NET Core 支持，需用对应版 -- ?|

---

## 相关技 -- ?

- **furion**  -- ?.NET Web 框架，dotnet-reactor 可保 -- ?Furion 构建 -- ?API/桌面应用：[../furion/SKILL.md](../furion/SKILL.md)

---

## 参考资 -- ?

- 官网与文档：<https://www.eziriz.com/dotnet_reactor.htm>
- 用户手册（PDF）：<https://www.eziriz.com/dotnet_reactor.htm>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/tutorial/dotnet-reactor/>
