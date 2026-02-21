# Telegram Bot 配置指南

## 步骤 1: 创建 Telegram Bot

1. 打开 Telegram，搜索 **@BotFather**
2. 发送 `/newbot` 命令
3. 按提示设置 Bot 名称和用户名
4. 获取 **Bot Token**（格式: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

## 步骤 2: 获取 Chat ID

### 方法 1: 通过 BotFather（推荐）

1. 发送 `/mybots` 命令给 BotFather
2. 选择你的 Bot
3. 点击 "API Token"
4. Chat ID 可能不直接显示

### 方法 2: 通过自己的 Bot

1. 在 Telegram 中搜索并点击你的 Bot
2. 发送任意消息（如 `/start`）
3. 在浏览器访问以下链接（替换 YOUR_BOT_TOKEN）：
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. 找到 `chat` → `id` 字段，这就是 Chat ID
5. **注意**: 私聊通常是正数，群聊是负数

### 方法 3: 使用第三方工具

访问以下网站，发送任意消息给 Bot 后查看 Chat ID：
```
https://t.me/userinfobot
```

## 步骤 3: 配置到套利框架

1. 打开 `config/notification.yml`
2. 填入配置：

```yaml
notification:
  enabled: true
  channels:
    - console   # 保留 console 用于调试
    - telegram  # 启用 telegram

  telegram:
    bot_token: "你的_BOT_TOKEN"  # 替换为实际 Token
    chat_id: "你的_CHAT_ID"      # 替换为实际 Chat ID
```

3. 保存文件

## 步骤 4: 测试通知

```bash
cd ~/arbitrage_cn
python3 test_notification.py
```

成功后，你的 Telegram 会收到 4 条测试消息。

## 常见问题

### Q: Bot 没有发送消息

**可能原因**:
1. Bot Token 错误
2. Chat ID 错误
3. Bot 没有被启动（发送 `/start` 给 Bot）

**解决方法**:
1. 检查 Token 和 Chat ID 是否正确
2. 确保给 Bot 发送过 `/start` 命令
3. 查看日志确认错误信息

### Q: 如何获取群组的 Chat ID

**步骤**:
1. 将 Bot 添加到群组
2. 在群组中发送任意消息
3. 访问 `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
4. 找到 `chat` → `id` 字段（通常是负数）

### Q: 如何只接收重要通知

**方法**:
在 `config/notification.yml` 中调整通知类型：

```yaml
notification:
  types:
    opportunity:
      enabled: true
      min_premium_rate: 0.02  # 只通知超过 2% 的机会

    trade:
      enabled: true
      notify_on_buy: true
      notify_on_sell: false   # 不通知卖出

    error:
      enabled: true
```

## 通知类型

### 1. 套利机会通知
```
🚀 LOF 套利机会 - 兴全合润混合
基金代码: 163406
基金名称: 兴全合润混合
机会类型: 溢价 2.50%
场内价格: 2.258 元
场外净值: 2.203 元
价差: 0.055 元
```

### 2. 交易通知
```
🟢 交易执行 - 兴全合润混合
基金代码: 163406
基金名称: 兴全合润混合
操作类型: 买入
成交数量: 10 手
成交价格: 2.250 元
成交金额: 2250.00 元
```

### 3. 错误通知
```
❌ 套利框架异常 - 连接失败
错误类型: 连接失败
错误详情: 无法连接到券商 API: Connection timeout
时间: 2026-02-21 14:27:55
```

### 4. 系统状态通知
```
📊 系统状态
套利框架运行正常
- 数据获取: ✅
- 券商连接: ✅
- 策略执行: ✅
```

## 安全建议

1. **保护 Bot Token**: 不要公开分享
2. **限制 Bot 权限**: 只保留必要功能
3. **监控异常**: 定期检查 Bot 日志
4. **备份配置**: 保存 Token 和 Chat ID 到安全位置

## 其他通知渠道

### Slack

1. 创建 Slack Workspace
2. 创建 Incoming Webhook: https://api.slack.com/messaging/webhooks
3. 复制 Webhook URL
4. 配置到 `config/notification.yml`

### 飞书（Feishu Bridge）

已集成飞书桥接技能，配置后可直接使用。

---

配置完成后，套利框架会自动发送通知到 Telegram！
