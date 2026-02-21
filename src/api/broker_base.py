"""
券商 API 基类
定义统一的交易接口
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from enum import Enum

# 避免循环导入
try:
    from src.utils.logger import log
except:
    pass


class OrderType(Enum):
    """订单类型"""
    BUY = "buy"
    SELL = "sell"


class BrokerBase(ABC):
    """券商 API 基类"""

    def __init__(self, simulate: bool = True):
        self.simulate = simulate
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """连接券商服务器"""
        pass

    @abstractmethod
    def get_balance(self) -> Dict:
        """
        获取账户余额

        Returns:
            {
                'total': 100000.0,
                'available': 80000.0,
                'cash': 50000.0,
                'market_value': 30000.0,
            }
        """
        pass

    @abstractmethod
    def get_position(self) -> List[Dict]:
        """
        获取持仓

        Returns:
            [
                {
                    'code': '163406',
                    'name': '兴全合润',
                    'quantity': 1000,
                    'available': 1000,
                    'cost': 2.5,
                    'current_price': 2.55,
                    'market_value': 2550,
                },
                ...
            ]
        """
        pass

    @abstractmethod
    def place_order(
        self,
        code: str,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None
    ) -> Dict:
        """
        下单

        Args:
            code: 证券代码
            order_type: 买入/卖出
            quantity: 数量
            price: 价格（None 表示市价单）

        Returns:
            {
                'order_id': '12345',
                'status': 'submitted',  # submitted, filled, rejected
                'message': '下单成功',
            }
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        pass

    @abstractmethod
    def subscribe_bond(self, bond_code: str, quantity: int) -> Dict:
        """
        可转债申购

        Args:
            bond_code: 转债代码
            quantity: 申购数量

        Returns:
            {
                'status': 'success',
                'message': '申购成功',
                'subscription_id': '12345',
            }
        """
        pass

    def is_simulated(self) -> bool:
        """是否为模拟模式"""
        return self.simulate
