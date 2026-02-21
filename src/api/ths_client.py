"""
中信证券（同花顺）客户端接口
基于 easytrader 实现
"""
import time
from typing import Dict, List, Optional
from .broker_base import BrokerBase, OrderType
try:
    from src.utils.logger import log
except:
    from loguru import logger as log

# 延迟导入 easytrader（仅在非模拟模式需要）
easytrader = None


class THSClient(BrokerBase):
    """中信（同花顺）客户端封装"""

    def __init__(self, simulate: bool = True):
        super().__init__(simulate)
        self.client = None
        self.account = None

    def connect(self, account: Optional[str] = None) -> bool:
        """
        连接中信证券（同花顺）客户端

        Args:
            account: 账号（用于标识）

        Returns:
            bool: 连接是否成功
        """
        try:
            log.info("正在连接中信证券（同花顺）客户端...")

            # 模拟模式不需要 easytrader
            if self.simulate:
                self.client = None
                self.account = account
                self.connected = True
                log.info(f"✅ 模拟模式连接成功，账号: {account or '默认'}")
                return True

            # 实盘模式：导入 easytrader
            global easytrader
            if easytrader is None:
                try:
                    import easytrader
                except ImportError:
                    log.error("❌ easytrader 未安装，请运行：pip install easytrader")
                    return False

            # 初始化 easytrader 中信（同花顺）客户端
            self.client = easytrader.use('ths')

            # 连接客户端（需要先手动登录中信同花顺）
            self.client.prepare(account)

            self.account = account
            self.connected = True

            log.info(f"✅ 连接成功，账号: {account or '默认'}")
            return True

        except Exception as e:
            log.error(f"❌ 连接失败: {e}")
            log.warning("请确认：")
            log.warning("1. 中信证券（同花顺）已安装")
            log.warning("2. 中信同花顺已登录")
            log.warning("3. 客户端窗口未最小化")
            log.warning("4. easytrader 已安装 (pip install easytrader)")
            return False

    def get_balance(self) -> Dict:
        """获取账户余额"""
        # 模拟模式下，只要有 connected 标记即可
        if not self.connected:
            return {
                'total': 0.0,
                'available': 0.0,
                'cash': 0.0,
                'market_value': 0.0,
            }

        # 实盘模式下需要 client 对象
        if not self.simulate and not self.client:
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
            balance = self.client.balance
            if not balance or len(balance) == 0:
                log.warning("获取余额失败或无数据")
                return {
                    'total': 0.0,
                    'available': 0.0,
                    'cash': 0.0,
                    'market_value': 0.0,
                }

            # easytrader 返回的是列表，取第一个
            b = balance[0]
            return {
                'total': float(b.get('资产总值', 0) or b.get('总资产', 0)),
                'available': float(b.get('可用金额', 0) or b.get('可用', 0)),
                'cash': float(b.get('可用金额', 0) or b.get('可用', 0)),
                'market_value': float(b.get('证券市值', 0) or b.get('市值', 0)),
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
        # 模拟模式下，只要有 connected 标记即可
        if not self.connected:
            return []

        # 实盘模式下需要 client 对象
        if not self.simulate and not self.client:
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
            positions = self.client.position
            if not positions:
                return []

            result = []
            for pos in positions:
                result.append({
                    'code': pos.get('证券代码', '') or pos.get('代码', ''),
                    'name': pos.get('证券名称', '') or pos.get('名称', ''),
                    'quantity': int(pos.get('持仓数量', 0) or pos.get('数量', 0)),
                    'available': int(pos.get('可卖数量', 0) or pos.get('可卖', 0)),
                    'cost': float(pos.get('成本价', 0) or pos.get('成本', 0)),
                    'current_price': float(pos.get('当前价', 0) or pos.get('现价', 0)),
                    'market_value': float(pos.get('当前市值', 0) or pos.get('市值', 0)),
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
            code: 证券代码（需要加后缀，如 163406.SZ）
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
        # 模拟模式下，只要有 connected 标记即可
        if not self.connected:
            return {
                'order_id': '',
                'status': 'failed',
                'message': '未连接客户端',
            }

        # 实盘模式下需要 client 对象
        if not self.simulate and not self.client:
            return {
                'order_id': '',
                'status': 'failed',
                'message': '未连接客户端',
            }

        try:
            # 转换代码格式（163406 -> 163406.SZ）
            formatted_code = self._format_code(code)

            # 模拟模式
            if self.simulate:
                log.info(f"[模拟] {order_type.value.upper()} {code} {quantity}手 @ {price or '市价'}")
                return {
                    'order_id': f'SIM{int(time.time())}',
                    'status': 'submitted',
                    'message': '模拟下单成功',
                }

            # 实盘下单
            if order_type == OrderType.BUY:
                result = self.client.buy(
                    security=formatted_code,
                    amount=quantity * 100,  # easytrader 买入用股数
                    price=price
                )
            else:
                result = self.client.sell(
                    security=formatted_code,
                    amount=quantity * 100,
                    price=price
                )

            # 解析返回结果
            if result and len(result) > 0:
                # easytrader 返回格式：[{' entrust_no': '123', ...}]
                return {
                    'order_id': result[0].get('委托编号', '') or result[0].get('entrust_no', ''),
                    'status': 'submitted',
                    'message': '下单成功',
                }
            else:
                return {
                    'order_id': '',
                    'status': 'failed',
                    'message': '下单返回为空',
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
        # 模拟模式下，只要有 connected 标记即可
        if not self.connected:
            log.warning("未连接客户端")
            return False

        # 实盘模式下需要 client 对象
        if not self.simulate and not self.client:
            log.warning("未连接客户端")
            return False

        try:
            if self.simulate:
                log.info(f"[模拟] 撤单 {order_id}")
                return True

            # 实盘撤单
            result = self.client.cancel_entrust(entrust_no=order_id)
            return True if result else False

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
        # 模拟模式下，只要有 connected 标记即可
        if not self.connected:
            return {
                'status': 'failed',
                'message': '未连接客户端',
            }

        # 实盘模式下需要 client 对象
        if not self.simulate and not self.client:
            return {
                'status': 'failed',
                'message': '未连接客户端',
            }

        try:
            # 转换代码格式
            formatted_code = self._format_code(bond_code)

            if self.simulate:
                log.info(f"[模拟] 申购新债 {bond_code} {quantity}股")
                return {
                    'status': 'success',
                    'message': '模拟申购成功',
                    'subscription_id': f'SIM{int(time.time())}',
                }

            # 实盘申购
            result = self.client.buy(
                security=formatted_code,
                amount=quantity,
                price=100  # 新债申购价格固定为 100 元
            )

            if result and len(result) > 0:
                return {
                    'status': 'success',
                    'message': '申购成功',
                    'subscription_id': result[0].get('委托编号', '') or result[0].get('entrust_no', ''),
                }
            else:
                return {
                    'status': 'failed',
                    'message': '申购返回为空',
                }

        except Exception as e:
            log.error(f"申购失败: {e}")
            return {
                'status': 'failed',
                'message': str(e),
            }

    def _format_code(self, code: str) -> str:
        """
        格式化证券代码
        163406 -> 163406.SZ
        163406.SZ -> 163406.SZ（保持不变）
        """
        if '.' in code:
            return code

        # 判断市场：6 开头是沪市，其他是深市
        if code.startswith('6'):
            return f"{code}.SH"
        else:
            return f"{code}.SZ"
