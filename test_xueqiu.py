"""
测试雪球 API 接口
使用方法：
1. 注册雪球账号：https://xueqiu.com
2. 浏览器登录
3. F12 → Application → Cookies → 复制全部 cookie
4. 运行此脚本测试

Cookie 格式示例：
xq_a_token=abc123; xq_r_token=xyz789; xq_is_login=1
"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.xueqiu import XueqiuClient
from src.api.broker_base import OrderType
from src.utils.logger import log


def test_xueqiu(cookie: str, simulate: bool = True):
    """测试雪球 API"""

    log.info("=" * 50)
    log.info("雪球 API 测试")
    log.info("=" * 50)

    # 创建客户端
    client = XueqiuClient(simulate=simulate)

    # 1. 连接测试
    log.info("\n【步骤 1】连接雪球")
    if simulate:
        log.info("模式: 模拟模式（无需 cookie）")
        success = client.connect()
    else:
        log.info("模式: 实盘模式")
        log.info(f"Cookie 长度: {len(cookie) if cookie else 0} 字符")
        success = client.connect(cookie)

    if not success:
        log.error("❌ 连接失败，请检查 cookie")
        return

    log.success("✅ 连接成功")

    # 2. 获取余额
    log.info("\n【步骤 2】获取余额")
    balance = client.get_balance()
    log.info(f"总资产: ¥{balance['total']:,.2f}")
    log.info(f"可用: ¥{balance['available']:,.2f}")
    log.info(f"市值: ¥{balance['market_value']:,.2f}")

    # 3. 获取持仓
    log.info("\n【步骤 3】获取持仓")
    positions = client.get_position()
    if positions:
        log.info(f"持仓数量: {len(positions)}")
        for pos in positions:
            log.info(
                f"  {pos['code']} {pos['name']}: "
                f"{pos['quantity']}股 "
                f"@ ¥{pos['current_price']:.2f} "
                f"市值 ¥{pos['market_value']:,.2f}"
            )
    else:
        log.info("无持仓")

    # 4. 模拟下单测试（仅模拟模式）
    if simulate:
        log.info("\n【步骤 4】模拟下单测试")

        # 模拟买入
        log.info("\n测试买入 163406（兴全合润）1 手...")
        buy_result = client.place_order(
            code="163406",
            order_type=OrderType.BUY,
            quantity=1,
            price=2.5
        )
        log.info(f"结果: {buy_result['status']} - {buy_result['message']}")
        log.info(f"订单号: {buy_result['order_id']}")

        # 模拟卖出
        log.info("\n测试卖出 163406（兴全合润）1 手...")
        sell_result = client.place_order(
            code="163406",
            order_type=OrderType.SELL,
            quantity=1,
            price=2.5
        )
        log.info(f"结果: {sell_result['status']} - {sell_result['message']}")
        log.info(f"订单号: {sell_result['order_id']}")

        # 模拟新债申购
        log.info("\n测试新债申购...")
        bond_result = client.subscribe_bond(
            bond_code="123456",
            quantity=1000
        )
        log.info(f"结果: {bond_result['status']} - {bond_result['message']}")

    # 总结
    log.info("\n" + "=" * 50)
    if simulate:
        log.success("✅ 模拟模式测试通过")
        log.info("\n切换到实盘模式步骤：")
        log.info("1. 注册雪球账号：https://xueqiu.com")
        log.info("2. 浏览器登录账号")
        log.info("3. F12 → Application → Cookies")
        log.info("4. 右键 → Copy all as HTTP header format")
        log.info("5. 运行: python test_xueqiu.py --cookie '你的cookie'")
    else:
        log.success("✅ 实盘模式测试通过")
    log.info("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试雪球 API")
    parser.add_argument("--cookie", help="雪球 cookie（从浏览器获取）")
    parser.add_argument("--real", action="store_true", help="实盘模式（默认模拟）")

    args = parser.parse_args()

    if not args.real and not args.cookie:
        # 默认模拟模式
        simulate = True
        cookie = None
    else:
        simulate = not args.real
        cookie = args.cookie

    test_xueqiu(cookie=cookie, simulate=simulate)
