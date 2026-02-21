# A股套利框架 (A-Share Arbitrage Framework)

## 简介

自动化 A 股套利交易系统，支持 LOF（上市型开放式基金）套利、可转债打新等策略。

## 功能

### 已实现

- **LOF 套利**: 自动扫描溢价/折价机会，执行套利交易
- **可转债打新**: 自动申购新发行的可转债
- **多券商支持**: 模拟、雪球、中信证券（同花顺）
- **实时数据**: 从东方财富获取基金净值、价格数据

### 券商支持

| 券商 | 代码 | 状态 | 说明 |
|------|------|------|------|
| 模拟 | `sim` | ✅ 完全支持 | 模拟交易测试 |
| 雪球 | `xueqiu` | ✅ 支持 | 纯 API 方式 |
| 中信 | `ths` | ✅ 支持 | 同花顺客户端（需要 easytrader） |
| 华泰 | `ht` | 🚧 开发中 | 涨乐财富通（需要 PC 客户端） |

## 安装

### 环境要求

- Python 3.11+
- Windows（实盘交易需要，用于券商客户端）
- Mac/Linux（仅模拟模式）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 实盘交易额外依赖（Windows）

```bash
pip install easytrader
pip install pywin32
```

## 使用

### 模拟模式测试

```bash
# LOF 套利测试
python main.py --strategy lof --broker sim --test

# 可转债打新测试
python main.py --strategy bond --broker sim --test

# 同时运行
python main.py --strategy all --broker sim --test
```

### 实盘模式

```bash
# 雪球 API
python main.py --strategy lof --broker xueqiu --account "your_cookie"

# 中信证券（同花顺）
python main.py --strategy lof --broker ths --account "your_account"
```

### 配置文件

编辑 `config/strategy.yml` 调整策略参数：

```yaml
lof:
  enabled: true
  min_premium: 0.01  # 最小溢价率 1%
  min_discount: -0.01  # 最小折价率 -1%

bond:
  enabled: true
  auto_subscribe: true
```

## 策略说明

### LOF 套利

LOF 基金可以在场内（证券交易所）和场外（基金公司）交易，存在价格差异时产生套利机会。

**溢价套利**:
- 场内价格 > 场外净值
- 操作：场内买入 → 场外赎回

**折价套利**:
- 场内价格 < 场外净值
- 操作：场外申购 → 场内卖出

### 可转债打新

新发行的可转债通常上市后会有一定涨幅，自动申购可转债是稳健的套利策略。

## 安全注意事项

1. **不要提交敏感信息**:
   - 配置文件: `config/config.yml`
   - API Keys: `.env`, `*.key`, `*.pem`
   - 账号密码

2. **实盘前测试**:
   - 先用模拟模式测试
   - 小额实盘验证
   - 检查订单参数

3. **风险管理**:
   - 设置合理的溢价率阈值
   - 控制单次交易金额
   - 监控账户余额

## 开发

### 项目结构

```
arbitrage_cn/
├── main.py              # 主程序
├── config/
│   └── strategy.yml      # 策略配置
├── src/
│   ├── api/            # 券商接口
│   │   ├── broker_base.py
│   │   ├── sim_broker.py
│   │   ├── xueqiu.py
│   │   └── ths_client.py
│   ├── strategies/     # 策略模块
│   │   ├── lof_arbitrage.py
│   │   └── bond_ipo.py
│   └── utils/          # 工具函数
│       ├── data_fetcher.py
│       └── logger.py
├── requirements.txt
└── README.md
```

## 许可证

MIT License

## 作者

总指挥 & 大龙虾 🦞

## 更新日志

- 2026-02-21: 新增中信证券（同花顺）支持
- 2026-02-20: 优化净值数据源
- 2026-02-19: 初始版本
