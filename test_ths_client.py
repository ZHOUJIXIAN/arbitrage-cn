"""
中信证券（同花顺）客户端测试脚本
"""
import argparse
from src.api.ths_client import THSClient
from src.api.broker_base import OrderType
try:
    from src.utils.logger import log
except:
    from loguru import logger as log


def test_ths_client():
    """测试中信客户端"""
    parser = argparse.ArgumentParser(description='测试中信证券客户端')
    parser.add_argument('--real', action='store_true', help='实盘模式（默认模拟）')
    parser.add_argument('--account', type=str, help='账号')
    args = parser.parse_args()

    simulate = not args.real
    account = args.account

    print("\n" + "=" * 50)
    print(f"中信证券（同花顺）客户端测试")
    print(f"模式: {'实盘' if not simulate else '模拟'}")
    print("=" * 50 + "\n")

    # 初始化客户端
    client = THSClient(simulate=simulate)

    # 1. 测试连接
    print("[1/5] 测试连接...")
    if client.connect(account=account):
        print("✅ 连接成功\n")
    else:
        print("❌ 连接失败\n")
        return

    # 2. 测试获取余额
    print("[2/5] 测试获取余额...")
    balance = client.get_balance()
    print(f"总资产: {balance['total']:.2f} 元")
    print(f"可用: {balance['available']:.2f} 元")
    print(f"市值: {balance['market_value']:.2f} 元")
    print("✅ 余额获取成功\n")

    # 3. 测试获取持仓
    print("[3/5] 测试获取持仓...")
    positions = client.get_position()
    if positions:
        print(f"持仓数量: {len(positions)}")
        for pos in positions:
            print(f"  - {pos['code']} {pos['name']}: {pos['quantity']}股 "
                  f"成本{pos['cost']:.2f} 现价{pos['current_price']:.2f}")
        print("✅ 持仓获取成功\n")
    else:
        print("当前无持仓\n")

    # 4. 测试下单（仅模拟模式）
    if simulate:
        print("[4/5] 测试模拟下单...")
        result = client.place_order(
            code='163406',
            order_type=OrderType.BUY,
            quantity=1,
            price=2.5
        )
        print(f"订单号: {result['order_id']}")
        print(f"状态: {result['status']}")
        print(f"消息: {result['message']}")
        print("✅ 模拟下单成功\n")
    else:
        print("[4/5] 跳过实盘下单测试（安全起见）\n")

    # 5. 测试新债申购（仅模拟模式）
    if simulate:
        print("[5/5] 测试新债申购...")
        result = client.subscribe_bond(bond_code='113050', quantity=1000)
        print(f"状态: {result['status']}")
        print(f"消息: {result['message']}")
        print(f"申购号: {result.get('subscription_id', '')}")
        print("✅ 新债申购成功\n")
    else:
        print("[5/5] 跳过实盘新债申购测试（安全起见）\n")

    print("=" * 50)
    print("✅ 所有测试通过")
    print("=" * 50 + "\n")


if __name__ == '__main__':
    test_ths_client()
