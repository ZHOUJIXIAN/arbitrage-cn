"""
可转债打新策略
自动监控新债发行并申购
"""
import time
import schedule
from typing import Dict, List
from datetime import datetime, time as dt_time

from src.api.broker_base import BrokerBase
from src.utils.data_fetcher import DataFetcher
from src.utils.logger import log


class BondIPO:
    """可转债打新策略"""

    def __init__(
        self,
        broker: BrokerBase,
        config: Dict,
        simulate: bool = True
    ):
        self.broker = broker
        self.config = config
        self.simulate = simulate
        self.data_fetcher = DataFetcher()

        # 策略参数
        self.enabled = config.get('enabled', True)
        self.check_time = config.get('check_time', '09:30')
        self.max_amount = config.get('max_subscription_amount', 1000000)
        self.auto_subscribe = config.get('auto_subscribe', True)

        # 通知设置
        self.notify_new = config.get('notify_on_new_bond', True)
        self.notify_win = config.get('notify_on_win', True)
        self.notify_list = config.get('notify_on_list', True)

        # 运行状态
        self.running = False
        self.subscribed_bonds = []  # 已申购的转债

    def run(self):
        """运行打新策略"""
        if not self.enabled:
            log.info("可转债打新策略已禁用")
            return

        if not self.broker.connect():
            log.error("无法连接券商")
            return

        self.running = True
        log.info(f"可转债打新策略启动，检查时间: {self.check_time}")

        # 设置定时任务
        schedule.every().day.at(self.check_time).do(self.daily_check)

        # 立即执行一次检查
        self.daily_check()

        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            log.info("收到停止信号")
        finally:
            self.running = False
            log.info("可转债打新策略停止")

    def daily_check(self):
        """每日检查"""
        log.info(f"开始每日检查: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. 查询新发行的转债
        new_bonds = self.data_fetcher.get_new_bonds()

        if not new_bonds:
            log.info("没有发现新发行的转债")
            return

        log.info(f"发现 {len(new_bonds)} 只新发行的转债")

        for bond in new_bonds:
            self.check_and_subscribe(bond)

        # 2. 查询中签结果
        self.check_subscription_status()

    def check_and_subscribe(self, bond: Dict):
        """检查并申购转债"""
        bond_code = bond['code']
        bond_name = bond['name']

        # 检查是否已申购
        if bond_code in self.subscribed_bonds:
            log.debug(f"{bond_name} 已申购，跳过")
            return

        log.info(f"新债: {bond_name}({bond_code})")
        log.info(f"  发行日期: {bond.get('issue_date', '-')}")
        log.info(f"  申购日期: {bond.get('subscription_date', '-')}")
        log.info(f"  上市日期: {bond.get('list_date', '-')}")

        # 自动申购
        if self.auto_subscribe:
            self.subscribe_bond(bond)

    def subscribe_bond(self, bond: Dict):
        """申购转债"""
        bond_code = bond['code']
        bond_name = bond['name']

        log.warning(f"[申购] {bond_name}({bond_code}) 顶格申购 {self.max_amount} 元")

        if self.simulate:
            log.info(f"[模拟模式] 申购 {bond_name} 已记录")

            # 模拟申购
            result = self.broker.subscribe_bond(bond_code, self.max_amount)

            if result['status'] == 'success':
                self.subscribed_bonds.append(bond_code)
                log.info(f"申购记录: {result}")

                # 模拟中签概率（通常 10-30%）
                import random
                if random.random() < 0.2:
                    log.warning(f"[模拟中签] 恭喜！{bond_name} 中签 1 手")
                else:
                    log.info(f"[模拟] {bond_name} 未中签")

            return

        # 实盘申购
        result = self.broker.subscribe_bond(bond_code, self.max_amount)

        if result['status'] == 'success':
            self.subscribed_bonds.append(bond_code)
            log.info(f"申购成功: {bond_name}")
            log.info(f"申购 ID: {result.get('subscription_id')}")

            # 发送通知
            if self.notify_new:
                self.send_notification(
                    f"新债申购成功\n\n"
                    f"名称: {bond_name}\n"
                    f"代码: {bond_code}\n"
                    f"申购金额: {self.max_amount} 元"
                )
        else:
            log.error(f"申购失败: {result.get('message')}")

    def check_subscription_status(self):
        """查询申购状态"""
        # 查询中签结果
        status = self.data_fetcher.get_bond_subscription_status(account_id="self")

        pending = status.get('pending', [])
        if pending:
            log.info(f"待上市转债: {len(pending)} 只")
            for bond in pending:
                log.info(f"  {bond['name']}({bond['code']}) 中签 {bond.get('win_count', 0)} 手")

                # 发送通知
                if self.notify_win and bond.get('win_count', 0) > 0:
                    self.send_notification(
                        f"恭喜！中签了\n\n"
                        f"名称: {bond['name']}\n"
                        f"代码: {bond['code']}\n"
                        f"中签: {bond['win_count']} 手"
                    )

    def send_notification(self, message: str):
        """发送通知（需要实现）"""
        # 这里可以集成 Telegram、企业微信等通知
        log.info(f"通知: {message}")

    def stop(self):
        """停止策略"""
        self.running = False


# 测试
if __name__ == "__main__":
    from ..api.sim_broker import SimulatedBroker

    # 配置
    config = {
        'enabled': True,
        'check_time': '09:30',
        'max_subscription_amount': 1000000,
        'auto_subscribe': True,
        'notify_on_new_bond': True,
        'notify_on_win': True,
        'notify_on_list': True,
    }

    # 创建策略
    broker = SimulatedBroker()
    strategy = BondIPO(broker, config, simulate=True)

    # 手动触发检查
    strategy.daily_check()
