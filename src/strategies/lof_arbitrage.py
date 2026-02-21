"""
LOF 基金套利策略
监控 LOF 基金场内价格与净值价差，自动执行套利
"""
import time
import yaml
from typing import Dict, List, Optional
from datetime import datetime

from src.api.broker_base import BrokerBase, OrderType
from src.utils.data_fetcher import DataFetcher
from src.utils.logger import log
from src.utils.notifier import NotificationManager


class LOFArbitrage:
    """LOF 基金套利策略"""

    def __init__(
        self,
        broker: BrokerBase,
        config: Dict,
        simulate: bool = True
    ):
        self.broker = broker
        self.config = config
        self.simulate = simulate
        self.data_fetcher = DataFetcher(source=config.get('common', {}).get('data_source', 'eastmoney'))

        # 策略参数
        self.enabled = config.get('enabled', True)
        self.interval = config.get('interval_seconds', 60)
        self.min_premium_rate = config.get('min_premium_rate', 0.015)
        self.min_discount_rate = config.get('min_discount_rate', 0.01)
        self.min_trade_amount = config.get('min_trade_amount', 1000)
        self.max_trade_amount = config.get('max_trade_amount', 20000)
        self.watchlist = config.get('watchlist', [])

        # 通知系统
        self.notifier = self._init_notifier()

        # 运行状态
        self.running = False
        self.opportunities = []  # 记录套利机会

    def _init_notifier(self) -> Optional[NotificationManager]:
        """初始化通知管理器"""
        try:
            # 加载通知配置
            with open("config/notification.yml", "r", encoding="utf-8") as f:
                notification_config = yaml.safe_load(f)

            return NotificationManager(notification_config.get("notification", {}))
        except Exception as e:
            log.warning(f"通知系统初始化失败: {e}")
            return None

    def run(self):
        """运行套利策略"""
        if not self.enabled:
            log.info("LOF 套利策略已禁用")
            return

        if not self.broker.connect():
            log.error("无法连接券商")
            return

        self.running = True
        log.info(f"LOF 套利策略启动，监控 {len(self.watchlist)} 只基金")

        try:
            while self.running:
                self.scan_opportunities()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            log.info("收到停止信号")
        finally:
            self.running = False
            log.info("LOF 套利策略停止")

    def scan_opportunities(self):
        """扫描套利机会"""
        if not self.watchlist:
            log.warning("监控列表为空")
            return

        log.debug("开始扫描套利机会...")

        for fund_code in self.watchlist:
            try:
                # 获取实时数据
                data = self.data_fetcher.get_lof_realtime_price(fund_code)
                if not data:
                    continue

                # 检查套利机会
                self.check_arbitrage_opportunity(data)

            except Exception as e:
                log.error(f"扫描 {fund_code} 时出错: {e}")

    def check_arbitrage_opportunity(self, data: Dict):
        """检查是否满足套利条件"""
        fund_code = data['code']
        fund_name = data['name']
        price = data['price']
        nav = data['nav']
        premium_rate = data['premium_rate']
        volume = data.get('volume', 0)

        log.debug(f"{fund_name}({fund_code}): 价格={price:.3f}, 净值={nav:.3f}, 溢价率={premium_rate:.2%}")

        # 净值为 0 或无成交，跳过
        if nav == 0 or volume == 0:
            return

        # 溢价套利：场内价格 > 净值 + 阈值
        if premium_rate >= self.min_premium_rate:
            log.info(f"发现溢价套利机会: {fund_name} 溢价率={premium_rate:.2%}")

            # 发送通知
            if self.notifier:
                self.notifier.send_opportunity(
                    fund_code=fund_code,
                    fund_name=fund_name,
                    opportunity_type="premium",
                    premium_rate=premium_rate,
                    price=price,
                    nav=nav
                )

            # 计算交易金额
            trade_amount = min(self.max_trade_amount, self.calculate_trade_amount(price))

            if trade_amount < self.min_trade_amount:
                log.warning(f"交易金额过小: {trade_amount:.2f} < {self.min_trade_amount}")
                return

            # 执行溢价套利
            self.execute_premium_arbitrage(data, trade_amount)

        # 折价套利：场内价格 < 净值 - 阈值
        elif premium_rate <= -self.min_discount_rate:
            log.info(f"发现折价套利机会: {fund_name} 折价率={abs(premium_rate):.2%}")

            # 发送通知
            if self.notifier:
                self.notifier.send_opportunity(
                    fund_code=fund_code,
                    fund_name=fund_name,
                    opportunity_type="discount",
                    premium_rate=premium_rate,
                    price=price,
                    nav=nav
                )

            # 计算交易金额
            trade_amount = min(self.max_trade_amount, self.calculate_trade_amount(price))

            if trade_amount < self.min_trade_amount:
                log.warning(f"交易金额过小: {trade_amount:.2f} < {self.min_trade_amount}")
                return

            # 执行折价套利
            self.execute_discount_arbitrage(data, trade_amount)

    def calculate_trade_amount(self, price: float) -> float:
        """计算交易金额"""
        # 基于账户余额计算
        balance = self.broker.get_balance()
        available = balance.get('available', 0)

        # 使用可用资金的 80%
        trade_amount = available * 0.8

        return trade_amount

    def execute_premium_arbitrage(self, data: Dict, trade_amount: float):
        """
        执行溢价套利

        策略：
        1. 场内卖出已有持仓
        2. 场外申购等额份额

        注意：
        - 需要先有持仓
        - 申购费用约 1.5%
        - T+2 到账
        """
        fund_code = data['code']
        fund_name = data['name']
        price = data['price']

        log.warning(f"[溢价套利] {fund_name}: 计划卖出 {trade_amount/price:.0f} 份")

        if self.simulate:
            log.info(f"[模拟模式] 溢价套利 {fund_name} 已记录")

            # 发送交易通知
            if self.notifier:
                quantity = int(trade_amount / price)
                self.notifier.send_trade(
                    fund_code=fund_code,
                    fund_name=fund_name,
                    action="卖出",
                    quantity=quantity,
                    price=price,
                    amount=trade_amount
                )

            self.opportunities.append({
                'type': 'premium',
                'code': fund_code,
                'name': fund_name,
                'price': price,
                'nav': data['nav'],
                'premium_rate': data['premium_rate'],
                'amount': trade_amount,
                'time': datetime.now().isoformat()
            })
            return

        # 实盘模式逻辑（需要券商 API 支持）
        # 1. 查询持仓
        position = self.broker.get_position()
        fund_position = next((p for p in position if p['code'] == fund_code), None)

        if not fund_position or fund_position['available'] == 0:
            log.warning(f"没有 {fund_name} 持仓，无法执行溢价套利")
            return

        # 2. 场内卖出
        quantity = min(int(trade_amount / price), fund_position['available'])
        order = self.broker.place_order(fund_code, OrderType.SELL, quantity)

        if order['status'] == 'filled':
            log.info(f"[溢价套利] 卖出成功: {fund_name} {quantity} 份")

            # 3. 场外申购（需要券商 API 支持）
            # 这里需要调用券商的基金申购接口
            log.warning("场外申购需要券商 API 支持")

    def execute_discount_arbitrage(self, data: Dict, trade_amount: float):
        """
        执行折价套利

        策略：
        1. 场内买入
        2. 场外赎回已有持仓

        注意：
        - 赎回费用约 0.5%
        - T+2 到账
        """
        fund_code = data['code']
        fund_name = data['name']
        price = data['price']

        log.warning(f"[折价套利] {fund_name}: 计划买入 {trade_amount/price:.0f} 份")

        if self.simulate:
            log.info(f"[模拟模式] 折价套利 {fund_name} 已记录")

            # 发送交易通知
            if self.notifier:
                quantity = int(trade_amount / price)
                self.notifier.send_trade(
                    fund_code=fund_code,
                    fund_name=fund_name,
                    action="买入",
                    quantity=quantity,
                    price=price,
                    amount=trade_amount
                )

            self.opportunities.append({
                'type': 'discount',
                'code': fund_code,
                'name': fund_name,
                'price': price,
                'nav': data['nav'],
                'premium_rate': data['premium_rate'],
                'amount': trade_amount,
                'time': datetime.now().isoformat()
            })
            return

        # 实盘模式逻辑
        # 1. 查询持仓（赎回需要先有持仓）
        position = self.broker.get_position()
        fund_position = next((p for p in position if p['code'] == fund_code), None)

        if not fund_position or fund_position['available'] == 0:
            log.warning(f"没有 {fund_name} 持仓，无法执行折价套利")
            return

        # 2. 场内买入
        quantity = int(trade_amount / price)
        order = self.broker.place_order(fund_code, OrderType.BUY, quantity)

        if order['status'] == 'filled':
            log.info(f"[折价套利] 买入成功: {fund_name} {quantity} 份")

            # 3. 场外赎回（需要券商 API 支持）
            log.warning("场外赎回需要券商 API 支持")

    def get_opportunities(self) -> List[Dict]:
        """获取记录的套利机会"""
        return self.opportunities

    def stop(self):
        """停止策略"""
        self.running = False


# 测试
if __name__ == "__main__":
    from ..api.sim_broker import SimulatedBroker

    # 配置
    config = {
        'enabled': True,
        'interval_seconds': 10,
        'min_premium_rate': 0.01,
        'min_discount_rate': 0.01,
        'min_trade_amount': 1000,
        'max_trade_amount': 10000,
        'watchlist': ['163406', '161725']
    }

    # 创建策略
    broker = SimulatedBroker(initial_cash=100000)
    strategy = LOFArbitrage(broker, config, simulate=True)

    # 运行一次扫描
    strategy.scan_opportunities()

    # 输出套利机会
    opportunities = strategy.get_opportunities()
    print(f"发现 {len(opportunities)} 个套利机会")
    for opp in opportunities:
        print(opp)
