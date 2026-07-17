---
name: acme.sh
description: "Use when automating SSL/TLS certificate issuance and renewal from Let's Encrypt, ZeroSSL, or BuyPass — wildcard certs, DNS API mode for 150+ providers, Nginx/Apache auto-reload. acme.sh: pure Shell ACME client, zero dependencies, crontab-friendly auto-renewal."
tags: [ssl, tls, acme, lets-encrypt, shell, certificate, devops, automation]
---

> **项目地址：** <https://github.com/acmesh-official/acme.sh>
>
> **官方文档（Wiki）：** <https://github.com/acmesh-official/acme.sh/wiki>
>
> **官网：** <https://acme.sh>
>
> **许可证：** GPL-3.0 ｜ **最新版本：** 3.1.3（2026-04）｜ **默认分支：** `master`

## 概述

acme.sh 是全球使用最广泛的 ACME 客户端之一（GitHub 40k+ Star），由 neilpang 发起维护，核心特点：

- **零依赖**：纯 POSIX Shell 实现，无需 Python/Node/Java，只要有 `curl`/`wget` 与 `cron`/`crontab` 即可。
- **跨平台**：Linux 全发行版、macOS、*BSD、Solaris、Windows（WSL/Cygwin/Git Bash）。
- **多 CA**：默认 ZeroSSL，可切换 Let's Encrypt、BuyPass、Google Trust Services（GTS）、SSL.com 等。
- **多验证方式**：HTTP-01（webroot / standalone / nginx / apache）、DNS-01（150+ 服务商 API，支持通配符）、TLS-ALPN-01。
- **自动续期**：安装时自动写入 cron，默认 60 天触发续期，支持 ARI（RFC 9773）提前续期。
- **证书部署**：内置 100+ deploy hook（nginx、ssh、docker、panel、CDN、路由器等）。
- **证书类型**：单域名、多域名 SAN、通配符 `*.example.com`、ECC（ec-256/384）与 RSA 双证书。

> ⚠️ **不要用 root 直接运行 `git` 仓库里的 `./acme.sh`**：请先 `--install` 到 `~/.acme.sh`，由安装后的副本管理证书与 cron。

---

## 安装

```bash
# 方法一：在线安装（推荐，-m 注册账户邮箱用于到期通知）
curl https://get.acme.sh | sh -s email=your@email.com
# 或 wget
wget -O - https://get.acme.sh | sh -s email=your@email.com

# 方法二：从 git 仓库安装
git clone --depth 1 https://github.com/acmesh-official/acme.sh.git
cd acme.sh
./acme.sh --install -m your@email.com

# 高级自定义安装目录
./acme.sh --install \
  --home /opt/acme.sh \
  --config-home /opt/acme.sh/data \
  --cert-home /etc/ssl/acme
```

安装会做三件事：复制脚本到 `~/.acme.sh/`、创建 `acme.sh` 别名、写入每日 cron。安装后重载 shell 或：

```bash
source ~/.bashrc
acme.sh --version          # 验证
```

升级：

```bash
acme.sh --upgrade                  # 手动升级
acme.sh --upgrade --auto-upgrade   # 开启自动升级
acme.sh --upgrade --auto-upgrade 0 # 关闭自动升级
```

---

## 核心命令

### 选择 CA（默认 ZeroSSL，常切到 Let's Encrypt）

```bash
acme.sh --set-default-ca --server letsencrypt
# 可选：zerossl / buypass / google / sslcom
# ZeroSSL / Google 需先注册账户（EAB）
acme.sh --register-account -m your@email.com                       # ZeroSSL
acme.sh --register-account -m your@email.com --server google \
  --eab-kid <KID> --eab-hmac-key <HMAC>                            # Google GTS
```

### 签发证书（HTTP-01）

```bash
# webroot 模式（已有 Web 服务，最常用）
acme.sh --issue -d example.com -d www.example.com -w /var/www/html

# standalone 模式（acme.sh 临时监听 80 端口，需先停掉占用 80 的服务）
acme.sh --issue --standalone -d example.com

# 已运行的 nginx / apache，自动找 webroot
acme.sh --issue -d example.com --nginx
acme.sh --issue -d example.com --apache
```

### 签发证书（DNS-01，支持通配符）

```bash
# Cloudflare（先导出 API Token 环境变量，会被保存到账户配置）
export CF_Token="xxxxxxxx"
export CF_Account_ID="yyyyyyyy"
acme.sh --issue --dns dns_cf -d example.com -d '*.example.com'

# 阿里云 DNS
export Ali_Key="xxx"; export Ali_Secret="xxx"
acme.sh --issue --dns dns_ali -d '*.example.com'

# 腾讯云 DNSPod
export DP_Id="xxx"; export DP_Key="xxx"
acme.sh --issue --dns dns_dp -d example.com

# DNS 手动模式（无 API 时，按提示添加 TXT 记录；不支持自动续期）
acme.sh --issue --dns -d example.com --yes-I-know-dns-manual-mode-enough-go-ahead-please
```

### ECC 证书与密钥长度

```bash
acme.sh --issue -d example.com --keylength ec-256   # ECC（ec-256 / ec-384）
acme.sh --issue -d example.com --keylength 2048     # RSA（默认 2048，可 3072/4096）
```

### 安装/部署证书到目标位置

```bash
# install-cert：把证书复制到指定路径，并设置重载命令（务必用此方式而非直接引用 ~/.acme.sh 下文件）
acme.sh --install-cert -d example.com \
  --key-file       /etc/nginx/ssl/example.com.key \
  --fullchain-file /etc/nginx/ssl/example.com.cer \
  --reloadcmd      "systemctl reload nginx"

# ECC 证书需加 --ecc
acme.sh --install-cert -d example.com --ecc \
  --key-file /etc/nginx/ssl/example.com.key \
  --fullchain-file /etc/nginx/ssl/example.com.cer \
  --reloadcmd "systemctl reload nginx"
```

### Deploy Hook（部署到服务/平台）

```bash
export DEPLOY_SSH_USER="root"
export DEPLOY_SSH_SERVER="server1"
acme.sh --deploy -d example.com --deploy-hook ssh        # 远程主机
acme.sh --deploy -d example.com --deploy-hook docker     # 重启容器
# 内置 hook 列表见 deploy/ 目录：nginx、haproxy、cpanel、synology_dsm、qiniu 等
```

### 续期、查询与吊销

```bash
acme.sh --list                       # 列出所有证书与到期/续期日期
acme.sh --info -d example.com        # 查看单个证书详情
acme.sh --renew -d example.com --force         # 强制续期
acme.sh --renew-all                  # 续期所有证书
acme.sh --cron                       # 手动触发 cron 续期逻辑（cron 实际调用此命令）
acme.sh --remove -d example.com      # 从管理列表移除（不删磁盘文件）
acme.sh --revoke -d example.com      # 向 CA 吊销证书
```

---

## 典型工作流

### Nginx + Cloudflare DNS 通配符证书全流程

```bash
# 1. 安装并注册
curl https://get.acme.sh | sh -s email=admin@example.com
source ~/.bashrc

# 2. 切换 Let's Encrypt
acme.sh --set-default-ca --server letsencrypt

# 3. 用 Cloudflare API 签发通配符 + 根域 ECC 证书
export CF_Token="..."; export CF_Account_ID="..."
acme.sh --issue --dns dns_cf -d example.com -d '*.example.com' --keylength ec-256

# 4. 安装到 nginx 并设置重载（acme.sh 会在续期后自动执行 reloadcmd）
acme.sh --install-cert -d example.com --ecc \
  --key-file       /etc/nginx/ssl/example.com.key \
  --fullchain-file /etc/nginx/ssl/example.com.cer \
  --reloadcmd      "systemctl reload nginx"

# 5. 验证自动续期任务已写入
crontab -l | grep acme.sh
```

---

## 最佳实践

- **始终用 `--install-cert`/deploy hook 引用证书**，不要直接软链或引用 `~/.acme.sh/<domain>/` 下文件——这些是内部文件，路径与格式可能变化。
- **优先 DNS-01 + API**：可签发通配符且不暴露 80 端口，支持全自动续期。手动 DNS 模式无法自动续期。
- **生产建议指定 Let's Encrypt 或 GTS**，并预先 `--register-account`，避免 ZeroSSL/Google 的 EAB 注册在续期时卡住。
- **重载命令做成幂等**，并在 `--install-cert` 时配置；续期由 cron `--cron` 自动完成，无需手工。
- **调试用 `--staging`/`--test`**（Let's Encrypt 测试环境）避免触发签发频率限制（rate limit），再用 `--debug 2` 看详细日志。
- **多服务器场景**用 deploy hook（ssh/docker）集中签发、分发，避免每台机器各自验证。

---

## 常见问题（FAQ）

| 问题 | 原因 / 解决 |
|------|------------|
| `Verify error: Invalid response` | HTTP-01 验证失败：检查 `-w` webroot 是否正确、`/.well-known/acme-challenge/` 可被外网访问、防火墙是否放行 80 端口 |
| 通配符证书签发失败 | 通配符**只能用 DNS-01**，确认使用 `--dns dns_xxx` 且 API 凭证正确 |
| `Create new order error` / rate limit | 触发 CA 频率限制；先用 `--staging` 调试，或切换其它 CA |
| ZeroSSL 报 EAB 错误 | 先执行 `acme.sh --register-account -m your@email.com` 注册 ZeroSSL 账户 |
| 续期后服务未生效 | `--install-cert` 未配置 `--reloadcmd`，或重载命令报错；用 `acme.sh --renew -d xxx --force` 复现排查 |
| cron 不生效 | 确认 `crontab -l` 含 acme.sh 条目；容器/无 cron 环境需自行调度 `acme.sh --cron --home ~/.acme.sh` |
| `command not found: acme.sh` | 未 `source ~/.bashrc` 或未安装；用 `~/.acme.sh/acme.sh` 全路径调用 |
| 想换默认 CA | `acme.sh --set-default-ca --server letsencrypt`（对后续新证书生效） |

---

## AI 使用建议

- 用户提到「免费 SSL 证书」「Let's Encrypt 自动续期」「通配符证书」「Nginx/宝塔自动 HTTPS」时，加载本技能。
- 生成命令前先确认三要素：**CA**（默认 ZeroSSL，多数人想要 Let's Encrypt）、**验证方式**（HTTP-01 还是 DNS-01）、**部署目标**（nginx/apache/容器/远程）。
- 通配符需求一律走 DNS-01 + 对应 `dns_xxx` 服务商 hook，并提示用户设置对应环境变量。
- 强调“用 `--install-cert` + `--reloadcmd`”而非手动复制文件，确保续期后自动生效。
- 调试场景优先建议 `--staging` 与 `--debug 2`，避免命中 CA 频率限制。

---

## 参考资源

- 官方 Wiki（命令、DNS API 列表、deploy hook）：<https://github.com/acmesh-official/acme.sh/wiki>
- DNS API 服务商列表：<https://github.com/acmesh-official/acme.sh/wiki/dnsapi>
- deploy hook 列表：<https://github.com/acmesh-official/acme.sh/wiki/deployhooks>
- 上游中文教程：<https://znlgis.github.io/>（others/acme.sh 系列）
