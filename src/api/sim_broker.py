"""
模拟券商 API
用于测试和回测
"""
import time
from typing import Dict, List
from uuid import uuid4

from src.api.broker_base import BrokerBase, OrderType
from src.utils.logger import log


class SimulatedBroker(BrokerBase):
    """模拟券商"""

    def __init__(self, initial_cash: float = 100000.0):
        super().__init__(simulate=True)
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}  # code -> position
        self.orders = {}  # order_id -> order
        self.connected = False

    def connect(self) -> bool:
        """连接（模拟）"""
        log.info("连接到模拟券商")
        self.connected = True
        return True

    def get_balance(self) -> Dict:
        """获取账户余额"""
        market_value = sum(
            pos['quantity'] * pos['current_price']
            for pos in self.positions.values()
        )

        return {
            'total': self.cash + market_value,
            'available': self.cash,
            'cash': self.cash,
            'market_value': market_value,
        }

    def get_position(self) -> List[Dict]:
        """获取持仓"""
        return list(self.positions.values())

    def place_order(
        self,
        code: str,
        order_type: OrderType,
        quantity: int,
        price: float = None
    ) -> Dict:
        """
        下单（模拟）

        模拟规则：
        - 市价单：立即成交
        - 限价单：假设成交概率 80%（简化）
        """
        if not self.connected:
            return {'order_id': '', 'status': 'rejected', 'message': '未连接'}

        order_id = str(uuid4())
        log.info(f"模拟下单: {order_type.value} {code} {quantity}股 价格={price}")

        if order_type == OrderType.BUY:
            # 买入
            if price is None:
                # 市价单：假设价格为当前价格的 1.001
                price = 2.5  # 简化

            amount = price * quantity
            if amount > self.cash:
                log.warning(f"资金不足，需要 {amount:.2f}，可用 {self.cash:.2f}")
                return {
                    'order_id': order_id,
                    'status': 'rejected',
                    'message': '资金不足'
                }

            # 扣除资金
            self.cash -= amount

            # 增加持仓
            if code not in self.positions:
                self.positions[code] = {
                    'code': code,
                    'name': f'模拟{code}',
                    'quantity': 0,
                    'available': 0,
                    'cost': 0,
                    'current_price': price,
                    'market_value': 0,
                }

            pos = self.positions[code]
            total_cost = pos['cost'] * pos['quantity'] + amount
            pos['quantity'] += quantity
            pos['available'] += quantity
            pos['cost'] = total_cost / pos['quantity']
            pos['current_price'] = price
            pos['market_value'] = pos['quantity'] * pos['current_price']

            log.info(f"模拟买入成功: {code} {quantity}股 @ {price:.3f}")

        else:  # OrderType.SELL
            # 卖出
            if code not in self.positions:
                return {
                    'order_id': order_id,
                    'status': 'rejected',
                    'message': '没有持仓'
                }

            pos = self.positions[code]
            if quantity > pos['available']:
                log.warning(f"持仓不足，需要 {quantity}，可用 {pos['available']}")
                return {
                    'order_id': order_id,
                    'status': 'rejected',
                    'message': '持仓不足'
                }

            if price is None:
                # 市价单
                price = pos['current_price'] * 0.999

            amount = price * quantity

            # 减少持仓
            pos['quantity'] -= quantity
            pos['available'] -= quantity
            pos['market_value'] = pos['quantity'] * pos['current_price']

            # 增加现金
            self.cash += amount

            log.info(f"模拟卖出成功: {code} {quantity}股 @ {price:.3f}")

        # 记录订单
        self.orders[order_id] = {
            'order_id': order_id,
            'code': code,
            'type': order_type.value,
            'quantity': quantity,
            'price': price,
            'status': 'filled',
            'amount': amount,
            'timestamp': time.time()
        }

        return {
            'order_id': order_id,
            'status': 'filled',
            'message': '模拟成交'
        }

    def cancel_order(self, order_id: str) -> bool:
        """撤单（模拟）"""
        if order_id in self.orders:
            log.info(f"模拟撤单: {order_id}")
            self.orders[order_id]['status'] = 'cancelled'
            return True
        return False

    def subscribe_bond(self, bond_code: str, quantity: int) -> Dict:
        """可转债申购（模拟）"""
        log.info(f"模拟申购转债: {bond_code} {quantity}张")
        return {
            'status': 'success',
            'message': '申购成功',
            'subscription_id': str(uuid4())
        }

    def reset(self):
        """重置账户"""
        self.cash = self.initial_cash
        self.positions = {}
        self.orders = {}
        log.info("模拟账户已重置")


# 测试
if __name__ == "__main__":
    broker = SimulatedBroker(initial_cash=100000)
    broker.connect()

    # 测试余额
    balance = broker.get_balance()
    print("余额:", balance)

    # 测试买入
    order = broker.place_order("163406", OrderType.BUY, 1000, 2.5)
    print("买入结果:", order)

    # 测试余额
    balance = broker.get_balance()
    print("余额:", balance)

    # 测试卖出
    order = broker.place_order("163406", OrderType.SELL, 500, 2.55)
    print("卖出结果:", order)

    # 测试持仓
    position = broker.get_position()
    print("持仓:", position)
