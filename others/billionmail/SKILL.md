---
name: billionmail
description: "Use when setting up self-hosted email marketing and transactional email �?SMTP relay, newsletter campaigns, bounce handling, delivery analytics. BillionMail: self-hosted email marketing platform with multi-tenant support."
tags: [email, smtp, self-hosted, newsletter, marketing]
---

> **项目地址�?* <https://github.com/aaPanel/BillionMail>
>
> **官网�?* <https://www.billionmail.com/>
>
> **官方文档�?* <https://docs.billionmail.com/>
>
> **许可证：** AGPL-3.0（社区版�?

## 概述

BillionMail 主要能力�?

- **多域名邮件服务器**（Postfix + Dovecot�?
- **批量营销发�?*：分批限速、退订链接、SPF/DKIM/DMARC
- **模板编辑�?*：拖�?+ 富文�?+ 变量
- **订阅者管�?*：分组、标签、导�?导出、退订列�?
- **触发邮件**：API / Webhook 触发事务邮件
- **送达率分�?*：点�?打开/退�?退订统�?
- **WebMail**：自带网页邮�?
- **多用�?/ 多租�?*

> BillionMail 由宝塔面板团队（aaPanel）出品，强调开箱即用、面板化运维�?

---

## 部署

### Docker Compose（推荐）

```bash
git clone https://github.com/aaPanel/BillionMail
cd BillionMail
cp .env.example .env
# 编辑 .env：DOMAIN、DB 密码、MX/SMTP 配置�?
docker compose up -d
```

### 一键脚�?

```bash
curl -sSL https://www.billionmail.com/install.sh | bash
```

### 端口要求

| 端口 | 服务 |
|------|------|
| 25 / 587 / 465 | SMTP |
| 143 / 993 | IMAP |
| 110 / 995 | POP3（可选） |
| 80 / 443 | Web 控制�?+ WebMail |

⚠️ 多数云厂商默认封�?25/587 端口，需提交工单解封；建议使用海�?VPS 或专用邮�?IP�?

---

## DNS 配置

为发件域 `mail.example.com` 配置�?

| 类型 | 主机 | �?|
|------|------|----|
| A | mail | <服务�?IP> |
| MX | @ | mail.example.com |
| TXT | @ | `v=spf1 mx ip4:<IP> ~all` |
| TXT | `default._domainkey` | `v=DKIM1;k=rsa;p=...`（管理后台生成） |
| TXT | `_dmarc` | `v=DMARC1;p=quarantine;rua=mailto:...` |
| PTR | <IP> | mail.example.com（联系机房设置反向解析） |

---

## 控制�?

访问 `https://your-server/`�?

- **域名管理**：添加发件域、生�?DKIM
- **邮箱账户**：创建邮箱、配额、SMTP/IMAP 密码
- **订阅�?*：分组、字段、批量导�?CSV
- **模板**：邮件模板（HTML + 变量�?
- **任务**：发送任务（即时 / 计划�?
- **统计**：到达率、打开、点击、退订、退�?
- **设置**：SMTP/反垃�?限�?IP �?

---

## 创建发送任�?

1. 设置「发件人」「主题�?
2. 选择模板或新建（变量：`{{name}}`、`{{unsubscribe_url}}`�?
3. 选择订阅者分组（可定向标签）
4. 限速（每分�?N �?/ 每小�?N 封）
5. 开始或计划发�?

发送过程中实时显示成功/失败/退信�?

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

Webhook 回调�?

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
- 退订后自动加入黑名单，再次发送被�?
- 提供 List-Unsubscribe / List-Unsubscribe-Post 头（兼容 Gmail/Outlook 一键退订）

---

## SPF/DKIM/DMARC 校验

控制�?�?设置 �?域名健康检查；或：

```bash
dig TXT default._domainkey.example.com
dig TXT _dmarc.example.com
```

```bash
mail-tester.com   # 免费送达率打�?
```

目标分数：≥ 9/10�?

---

## 性能与送达率优�?

1. **�?IP 预热**：从 50/day 起，�?2-3 天翻�?
2. **限速分�?*：避免被收件�?throttling
3. **�?IP �?*：营销与事务分开
4. **退信处�?*：硬退信立刻加黑名�?
5. **内容质量**：去除垃圾词、图文比例、HTML/纯文本双版本
6. **认证三件�?*：SPF + DKIM + DMARC 全配
7. **反向 DNS**：必须与 HELO 一�?
8. **TLS**：默�?STARTTLS

---

## 监控与日�?

- 容器日志：`docker compose logs -f postfix dovecot`
- 邮件队列：`mailq`（容器内�?
- 控制台「日志」页查看每条邮件状�?
- 集成 Prometheus / Grafana（可选）

---

## 典型工作�?

### 场景一：搭建企�?Newsletter 系统

```bash
# 1. 部署
git clone https://github.com/aaPanel/BillionMail
cd BillionMail
cp .env.example .env
# 编辑 .env：DOMAIN=mail.example.com, 数据库密�?
docker compose up -d

# 2. DNS 配置（在域名管理后台�?
# A     mail  �? <服务器IP>
# MX    @     �? mail.example.com
# TXT   @     �? "v=spf1 mx ip4:<IP> ~all"
# TXT   default._domainkey �?"v=DKIM1;k=rsa;p=..." (管理后台生成)
# TXT   _dmarc �?"v=DMARC1;p=quarantine;rua=mailto:admin@..."

# 3. 控制台操�?
#   �?添加发件�?�?生成 DKIM �?配置 DNS
#   �?导入订阅�?CSV（邮�?姓名,标签�?
#   �?创建模板（HTML + 变量 {{name}}, {{unsubscribe_url}}�?
#   �?新建发送任�?�?选择分组 �?限�?100�?小时（预热期�?
#   �?查看统计：到达率/打开�?点击�?退订率

# 4. 验证送达�?
# mail-tester.com �?目标 �?9/10

# 5. API 触发事务邮件
curl -X POST https://mail.example.com/api/v1/mail/send \
  -H 'Authorization: Bearer <API_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "noreply@example.com",
    "to": ["user@x.com"],
    "subject": "欢迎注册",
    "template_id": 12,
    "variables": {"name": "张三"}
  }'
```

### 场景二：�?Mailchimp 迁移到自�?

```markdown
1. **导出 Mailchimp 数据**：Audience �?Export CSV（含邮箱/姓名/标签/状态）
2. **导入 BillionMail**：订阅�?�?导入 CSV，映射字�?
3. **重建模板**：复�?Mailchimp 模板 HTML，替换变量为 `{{name}}` 格式
4. **保留退订列�?*：将 Mailchimp 退订名单导入黑名单
5. **IP 预热**：从 50/day 起，�?2-3 天翻倍，直到目标�?
6. **并行运行 1-2 �?*：新旧系统同时发，确认送达率一致后切换 DNS
```

---

## AI 使用建议

### 推荐工作�?

1. **先配 DNS 三件�?*：SPF + DKIM + DMARC 全配且验证通过，再开始发�?
2. **IP 预热是必须的**：新 IP 从低量开始，不要一次性大批量发�?
3. **模板先测�?*：用 `mail-tester.com` 打分，目标是 �?9/10
4. **分批限�?*：每分钟/每小时限速，避免被收件方 throttling 或标记垃�?
5. **监控退�?*：硬退信立刻加入黑名单，软退信重试最�?3 �?

### 关键模式与常见陷�?

- **25 端口被封**：云厂商默认封锁，需提交工单解封；或使用 587 + Relay 中转
- **Gmail 进垃圾箱**：SPF/DKIM/DMARC 缺一不可 + 反向 DNS + IP 预热 + 内容质量
- **退订合�?*：模板必须包�?`{{unsubscribe_url}}`，否则违�?CAN-SPAM/GDPR
- **�?IP �?*：营销邮件和事务邮件分开 IP，避免营销被投诉影响事务送达
- **内容质量**：去除垃圾词（免�?促销/点击领）、图文比例适中、HTML/纯文本双版本

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 少量事务邮件�?100/天） | 第三�?API（SendGrid/Mailgun 免费额度�?|
| 企业自建 Newsletter | BillionMail |
| 超大规模（百万级�?| BillionMail + �?IP �?+ 专业 ESP |
| 仅需 SMTP 中转 | Postfix + Dovecot，无需 BillionMail |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| Gmail 进垃圾箱 | 修复 SPF/DKIM/DMARC；预�?IP；降低发送量 |
| 25 端口被封 | 联系云厂�?/ �?587 + Relay |
| 退订链接无�?| 检�?`UNSUBSCRIBE_BASE_URL`；TLS 证书 |
| WebMail 无法登录 | 检�?Dovecot 与账号密码；查看容器日志 |
| 大文件附件失�?| 调整 `message_size_limit` |

---

## 相关技�?

- BillionMail 是独立的邮件平台，与其它技能无直接技术依赖。如需前端界面定制，可参�?Admin.NET 前后端框架�?

---

## 参考资�?

- 文档�?https://docs.billionmail.com/>
- 仓库�?https://github.com/aaPanel/BillionMail>
- 中文教程（znlgis）：<https://znlgis.github.io/others/tutorial/billionmail/>