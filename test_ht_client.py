"""
测试华泰客户端（涨乐财富通）接口
使用 easytrader 实现

使用方法：
1. 在 Windows 上安装涨乐财富通 PC 版
2. 手动登录涨乐财富通
3. 运行此脚本测试连接

注意：
- 首次运行可能需要管理员权限
- 客户端窗口不能最小化
- 模拟模式下不需要真实账号
"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.ht_client import HTClient
from src.utils.logger import log


def test_ht_client(account: str = None, simulate: bool = True):
    """测试华泰客户端"""

    log.info("=" * 50)
    log.info("华泰客户端（涨乐财富通）测试")
    log.info("=" * 50)

    # 创建客户端
    client = HTClient(simulate=simulate)

    # 1. 连接测试
    log.info("\n【步骤 1】连接客户端")
    if simulate:
        log.info("模式: 模拟模式（无需真实账号）")
        success = client.connect()
    else:
        log.info("模式: 实盘模式")
        if not account:
            log.warning("请提供华泰账号")
            return
        log.info(f"账号: {account}")
        log.warning("请确保涨乐财富通已安装并登录")
        log.warning("按回车继续...")
        input()

        success = client.connect(account)

    if not success:
        log.error("❌ 连接失败，请检查")
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
            order_type="buy",
            quantity=1,
            price=2.5
        )
        log.info(f"结果: {buy_result['status']} - {buy_result['message']}")
        log.info(f"订单号: {buy_result['order_id']}")

        # 模拟卖出
        log.info("\n测试卖出 163406（兴全合润）1 手...")
        sell_result = client.place_order(
            code="163406",
            order_type="sell",
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
        log.info("切换到实盘模式步骤：")
        log.info("1. 安装涨乐财富通 PC 版")
        log.info("2. 手动登录客户端")
        log.info("3. 运行: python test_ht_client.py --account 你的账号")
    else:
        log.success("✅ 实盘模式测试通过")
    log.info("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试华泰客户端")
    parser.add_argument("--account", help="华泰账号")
    parser.add_argument("--real", action="store_true", help="实盘模式（默认模拟）")

    args = parser.parse_args()

    simulate = not args.real
    test_ht_client(account=args.account, simulate=simulate)
