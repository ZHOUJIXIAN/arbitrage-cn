"""
券商登录测试脚本
测试 easytrader 能否连接华泰涨乐财富通
"""
import easytrader
from datetime import datetime

print("=" * 60)
print("华泰涨乐财富通登录测试")
print("=" * 60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 输入账号密码
print("请输入账号信息：")
account = input("资金账号: ").strip()
password = input("登录密码: ").strip()
comm_password = input("交易密码（没有则留空）: ").strip() or None

print()
print("-" * 60)
print("正在连接券商...")
print("-" * 60)
print()

try:
    # 创建华泰交易客户端
    trader = easytrader.use('ht')

    # 准备登录参数
    login_params = {
        'account': account,
        'password': password,
    }
    if comm_password:
        login_params['comm_password'] = comm_password

    # 登录
    print("正在登录...")
    result = trader.prepare(**login_params)

    print()
    print("✓ 登录成功！")
    print()

    # 测试查询余额
    print("-" * 60)
    print("查询账户余额")
    print("-" * 60)
    try:
        balance = trader.balance
        print(f"账户余额:")
        for key, value in balance.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"查询余额失败: {e}")

    print()

    # 测试查询持仓
    print("-" * 60)
    print("查询持仓")
    print("-" * 60)
    try:
        position = trader.position
        print(f"持仓数量: {len(position)}")
        for pos in position:
            print(f"  代码: {pos.get('证券代码', 'N/A')}")
            print(f"  名称: {pos.get('证券名称', 'N/A')}")
            print(f"  数量: {pos.get('持仓数量', 'N/A')}")
            print()
    except Exception as e:
        print(f"查询持仓失败: {e}")

    print()
    print("=" * 60)
    print("测试完成！easytrader 可以正常使用")
    print("=" * 60)

except Exception as e:
    print()
    print("=" * 60)
    print("✗ 登录失败")
    print("=" * 60)
    print(f"错误信息: {e}")
    print()
    print("可能的原因:")
    print("  1. 涨乐财富通客户端未安装")
    print("  2. 涨乐财富通客户端未登录")
    print("  3. 账号密码错误")
    print("  4. 网络连接问题")
    print()
