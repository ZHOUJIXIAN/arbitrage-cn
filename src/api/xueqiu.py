"""
雪球 API 接口封装
支持场内外交易（LOF 套利必备）
"""
import time
import json
import requests
from typing import Dict, List, Optional
from .broker_base import BrokerBase, OrderType
try:
    from src.utils.logger import log
except:
    from loguru import logger as log


class XueqiuClient(BrokerBase):
    """雪球客户端封装"""

    def __init__(self, simulate: bool = True):
        super().__init__(simulate)
        self.session = None
        self.cookie = None
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.base_url = 'https://xueqiu.com'

    def connect(self, cookie: str = None) -> bool:
        """
        连接雪球（通过 cookie 登录）

        Args:
            cookie: 雪球 cookie（从浏览器获取）

        Returns:
            bool: 连接是否成功
        """
        try:
            # 模拟模式不需要 cookie
            if self.simulate:
                self.connected = True
                log.info("✅ 模拟模式连接成功")
                return True

            # 实盘模式需要 cookie
            if not cookie:
                log.error("未提供 cookie，无法登录")
                log.info("获取 cookie 方法：")
                log.info("1. 浏览器访问 https://xueqiu.com")
                log.info("2. 登录账号")
                log.info("3. F12 → Application → Cookies → 复制全部")
                return False

            self.cookie = cookie

            # 创建会话
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': self.user_agent,
                'Cookie': cookie,
                'Referer': self.base_url
            })

            # 测试登录状态
            user_info = self._get_user_info()
            if not user_info:
                log.error("Cookie 无效或已过期")
                return False

            self.connected = True
            log.info(f"✅ 登录成功，用户: {user_info}")
            return True

        except Exception as e:
            log.error(f"❌ 连接失败: {e}")
            return False

    def _get_user_info(self) -> Optional[str]:
        """获取用户信息（测试登录状态）"""
        try:
            url = f"{self.base_url}/statuses/user_timeline.json"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'user' in data and len(data['user']) > 0:
                    return data['user'][0].get('screen_name', '未知')
            return None

        except Exception as e:
            log.debug(f"获取用户信息失败: {e}")
            return None

    def get_balance(self) -> Dict:
        """获取账户余额"""
        if not self.connected:
            return {
                'total': 0.0,
                'available': 0.0,
                'cash': 0.0,
                'market_value': 0.0,
            }

        try:
            if self.simulate:
                # 模拟模式返回测试数据
                return {
                    'total': 50000.0,
                    'available': 30000.0,
                    'cash': 20000.0,
                    'market_value': 30000.0,
                }

            # 实盘模式：获取真实余额
            url = f"{self.base_url}/account/sncash.json"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                log.warning(f"获取余额失败: HTTP {response.status_code}")
                return {
                    'total': 0.0,
                    'available': 0.0,
                    'cash': 0.0,
                    'market_value': 0.0,
                }

            data = response.json()
            return {
                'total': float(data.get('total_cash', 0) + data.get('market_value', 0)),
                'available': float(data.get('available_cash', 0)),
                'cash': float(data.get('available_cash', 0)),
                'market_value': float(data.get('market_value', 0)),
            }

        except Exception as e:
            log.error(f"获取余额失败: {e}")
            return {
                'total': 0.0,
                'available': 0.0,
                'cash': 0.0,
                'market_value': 0.0,
            }

    def get_position(self) -> List[Dict]:
        """获取持仓"""
        if not self.connected:
            return []

        try:
            if self.simulate:
                # 模拟模式返回测试数据
                return [
                    {
                        'code': '163406',
                        'name': '兴全合润',
                        'quantity': 1000,
                        'available': 1000,
                        'cost': 2.5,
                        'current_price': 2.55,
                        'market_value': 2550.0,
                    },
                ]

            # 实盘模式：获取真实持仓
            url = f"{self.base_url}/stock/portfolio.json"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                log.warning(f"获取持仓失败: HTTP {response.status_code}")
                return []

            data = response.json()
            result = []

            for pos in data.get('portfolio', []):
                result.append({
                    'code': pos.get('stock_code', ''),
                    'name': pos.get('stock_name', ''),
                    'quantity': int(pos.get('amount', 0)),
                    'available': int(pos.get('amount_available', 0)),
                    'cost': float(pos.get('cost_price', 0)),
                    'current_price': float(pos.get('current_price', 0)),
                    'market_value': float(pos.get('market_value', 0)),
                })

            log.info(f"获取持仓成功，共 {len(result)} 只")
            return result

        except Exception as e:
            log.error(f"获取持仓失败: {e}")
            return []

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
            quantity: 数量（手）
            price: 价格（None 表示市价单）

        Returns:
            {
                'order_id': '12345',
                'status': 'submitted',
                'message': '下单成功',
            }
        """
        if not self.connected:
            return {
                'order_id': '',
                'status': 'failed',
                'message': '未连接',
            }

        try:
            # 模拟模式
            if self.simulate:
                log.info(f"[模拟] {order_type.value.upper()} {code} {quantity}手 @ {price or '市价'}")
                return {
                    'order_id': f'SIM{int(time.time())}',
                    'status': 'submitted',
                    'message': '模拟下单成功',
                }

            # 实盘下单
            url = f"{self.base_url}/trade/stock/commit.json"

            payload = {
                'symbol': code,
                'portfolio': -1,  # 默认账户
                'side': order_type.value,  # buy/sell
                'amount': quantity * 100,  # 股数
                'price': price or 0,  # 0 表示市价
                'order_type': 'market' if price is None else 'limit',
            }

            response = self.session.post(url, json=payload, timeout=10)

            if response.status_code != 200:
                return {
                    'order_id': '',
                    'status': 'failed',
                    'message': f'HTTP {response.status_code}',
                }

            data = response.json()
            if data.get('error_code') != 0:
                return {
                    'order_id': '',
                    'status': 'failed',
                    'message': data.get('error_description', '未知错误'),
                }

            return {
                'order_id': data.get('order_id', ''),
                'status': 'submitted',
                'message': '下单成功',
            }

        except Exception as e:
            log.error(f"下单失败: {e}")
            return {
                'order_id': '',
                'status': 'failed',
                'message': str(e),
            }

    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        if not self.connected:
            log.warning("未连接")
            return False

        try:
            if self.simulate:
                log.info(f"[模拟] 撤单 {order_id}")
                return True

            # 实盘撤单
            url = f"{self.base_url}/trade/stock/cancel.json"
            payload = {'order_id': order_id}

            response = self.session.post(url, json=payload, timeout=10)
            return response.status_code == 200

        except Exception as e:
            log.error(f"撤单失败: {e}")
            return False

    def subscribe_bond(self, bond_code: str, quantity: int) -> Dict:
        """
        可转债申购

        Args:
            bond_code: 转债代码
            quantity: 申购数量（股）

        Returns:
            {
                'status': 'success',
                'message': '申购成功',
                'subscription_id': '12345',
            }
        """
        if not self.connected:
            return {
                'status': 'failed',
                'message': '未连接',
            }

        try:
            if self.simulate:
                log.info(f"[模拟] 申购新债 {bond_code} {quantity}股")
                return {
                    'status': 'success',
                    'message': '模拟申购成功',
                    'subscription_id': f'SIM{int(time.time())}',
                }

            # 实盘申购
            url = f"{self.base_url}/trade/convertible/subscribe.json"

            payload = {
                'code': bond_code,
                'amount': quantity,
            }

            response = self.session.post(url, json=payload, timeout=10)

            if response.status_code != 200:
                return {
                    'status': 'failed',
                    'message': f'HTTP {response.status_code}',
                }

            data = response.json()
            if data.get('error_code') != 0:
                return {
                    'status': 'failed',
                    'message': data.get('error_description', '未知错误'),
                }

            return {
                'status': 'success',
                'message': '申购成功',
                'subscription_id': data.get('subscription_id', ''),
            }

        except Exception as e:
            log.error(f"申购失败: {e}")
            return {
                'status': 'failed',
                'message': str(e),
            }
