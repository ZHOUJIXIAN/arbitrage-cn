import easytrader
import time

print("=== Easytrader 同花顺演示 ===\n")

# 1. 初始化客户端
print("1. 初始化同花顺客户端...")
client = easytrader.use("ths")
print("   ✅ 初始化成功")

# 2. 检查同花顺交易端状态
print("\n2. 检查同花顺交易端 (xiadan.exe) 状态...")
try:
    client.connect()
    print("   ✅ 连接成功")
except Exception as e:
    print(f"   ⚠️ 连接失败: {e}")
    print("\n   可能原因:")
    print("   - 同花顺交易端未启动")
    print("   - 同花顺交易端窗口被最小化")
    print("   - 未登录同花顺账号")
    print("\n   建议: 确保 xiadan.exe 已启动并登录账号")
    exit(1)

# 3. 获取余额
print("\n3. 获取账户余额...")
try:
    balance = client.balance
    print(f"   ✅ 余额获取成功")
    print(f"   详情: {balance}")
except Exception as e:
    print(f"   ⚠️ 获取失败: {e}")

# 4. 获取持仓
print("\n4. 获取持仓...")
try:
    position = client.position
    print(f"   ✅ 持仓获取成功")
    print(f"   数量: {len(position) if position else 0}")
    if position:
        for p in position[:3]:
            print(f"   - {p}")
except Exception as e:
    print(f"   ⚠️ 获取失败: {e}")

# 5. 模拟下单（演示）
print("\n5. 模拟下单...")
print("   (实际下单需要取消注释并填写参数)")
print("   # client.buy(security='163406.SZ', amount=100, price=2.5)")

print("\n=== 演示完成 ===")
print("\n说明: 当前演示显示 easytrader 已成功加载同花顺支持")
print("需要登录同花顺账号后才能进行实盘交易")
