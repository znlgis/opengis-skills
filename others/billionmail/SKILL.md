---
name: billionmail
description: BillionMail 是开源自托管邮件营销与事务邮件平台，提供 SMTP 中转、模板编辑、订阅者管理、批量发送、退订处理、送达率分析与 API 集成，适合企业自建营销邮件 / 通知 / Newsletter 系统，替代 Mailchimp / SendGrid 等商业方案。
---

> **项目地址：** <https://github.com/aaPanel/BillionMail>
>
> **官网：** <https://www.billionmail.com/>
>
> **官方文档：** <https://docs.billionmail.com/>
>
> **许可证：** AGPL-3.0（社区版）

## 概述

BillionMail 主要能力：

- **多域名邮件服务器**（Postfix + Dovecot）
- **批量营销发送**：分批限速、退订链接、SPF/DKIM/DMARC
- **模板编辑器**：拖拽 + 富文本 + 变量
- **订阅者管理**：分组、标签、导入/导出、退订列表
- **触发邮件**：API / Webhook 触发事务邮件
- **送达率分析**：点击/打开/退信/退订统计
- **WebMail**：自带网页邮箱
- **多用户 / 多租户**

> BillionMail 由宝塔面板团队（aaPanel）出品，强调开箱即用、面板化运维。

---

## 部署

### Docker Compose（推荐）

```bash
git clone https://github.com/aaPanel/BillionMail
cd BillionMail
cp .env.example .env
# 编辑 .env：DOMAIN、DB 密码、MX/SMTP 配置等
docker compose up -d
```

### 一键脚本

```bash
curl -sSL https://www.billionmail.com/install.sh | bash
```

### 端口要求

| 端口 | 服务 |
|------|------|
| 25 / 587 / 465 | SMTP |
| 143 / 993 | IMAP |
| 110 / 995 | POP3（可选） |
| 80 / 443 | Web 控制台 + WebMail |

⚠️ 多数云厂商默认封锁 25/587 端口，需提交工单解封；建议使用海外 VPS 或专用邮件 IP。

---

## DNS 配置

为发件域 `mail.example.com` 配置：

| 类型 | 主机 | 值 |
|------|------|----|
| A | mail | <服务器 IP> |
| MX | @ | mail.example.com |
| TXT | @ | `v=spf1 mx ip4:<IP> ~all` |
| TXT | `default._domainkey` | `v=DKIM1;k=rsa;p=...`（管理后台生成） |
| TXT | `_dmarc` | `v=DMARC1;p=quarantine;rua=mailto:...` |
| PTR | <IP> | mail.example.com（联系机房设置反向解析） |

---

## 控制台

访问 `https://your-server/`：

- **域名管理**：添加发件域、生成 DKIM
- **邮箱账户**：创建邮箱、配额、SMTP/IMAP 密码
- **订阅者**：分组、字段、批量导入 CSV
- **模板**：邮件模板（HTML + 变量）
- **任务**：发送任务（即时 / 计划）
- **统计**：到达率、打开、点击、退订、退信
- **设置**：SMTP/反垃圾/限速/IP 池

---

## 创建发送任务

1. 设置「发件人」「主题」
2. 选择模板或新建（变量：`{{name}}`、`{{unsubscribe_url}}`）
3. 选择订阅者分组（可定向标签）
4. 限速（每分钟 N 封 / 每小时 N 封）
5. 开始或计划发送

发送过程中实时显示成功/失败/退信。

---

## API（事务邮件）

```bash
curl -X POST https://your-server/api/v1/mail/send \
  -H 'Authorization: Bearer <API_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "noreply@example.com",
    "to":   ["user@x.com"],
    "subject": "欢迎注册",
    "template_id": 12,
    "variables": { "name": "张三" }
  }'
```

Webhook 回调：

```json
POST https://yourapp.com/hooks/billionmail
{
  "event": "delivered|bounced|opened|clicked|unsubscribed",
  "message_id": "...",
  "to": "...",
  "ts": 1700000000
}
```

---

## 退订与合规

- 模板默认包含 `{{unsubscribe_url}}`
- 退订后自动加入黑名单，再次发送被拒
- 提供 List-Unsubscribe / List-Unsubscribe-Post 头（兼容 Gmail/Outlook 一键退订）

---

## SPF/DKIM/DMARC 校验

控制台 → 设置 → 域名健康检查；或：

```bash
dig TXT default._domainkey.example.com
dig TXT _dmarc.example.com
```

```bash
mail-tester.com   # 免费送达率打分
```

目标分数：≥ 9/10。

---

## 性能与送达率优化

1. **新 IP 预热**：从 50/day 起，每 2-3 天翻倍
2. **限速分批**：避免被收件方 throttling
3. **多 IP 池**：营销与事务分开
4. **退信处理**：硬退信立刻加黑名单
5. **内容质量**：去除垃圾词、图文比例、HTML/纯文本双版本
6. **认证三件套**：SPF + DKIM + DMARC 全配
7. **反向 DNS**：必须与 HELO 一致
8. **TLS**：默认 STARTTLS

---

## 监控与日志

- 容器日志：`docker compose logs -f postfix dovecot`
- 邮件队列：`mailq`（容器内）
- 控制台「日志」页查看每条邮件状态
- 集成 Prometheus / Grafana（可选）

---

## 常见问题

| 问题 | 解决 |
|------|------|
| Gmail 进垃圾箱 | 修复 SPF/DKIM/DMARC；预热 IP；降低发送量 |
| 25 端口被封 | 联系云厂商 / 用 587 + Relay |
| 退订链接无效 | 检查 `UNSUBSCRIBE_BASE_URL`；TLS 证书 |
| WebMail 无法登录 | 检查 Dovecot 与账号密码；查看容器日志 |
| 大文件附件失败 | 调整 `message_size_limit` |

---

## 参考资源

- 文档：<https://docs.billionmail.com/>
- 仓库：<https://github.com/aaPanel/BillionMail>
- 中文教程（znlgis）：<https://znlgis.github.io/others/tutorial/billionmail/>
