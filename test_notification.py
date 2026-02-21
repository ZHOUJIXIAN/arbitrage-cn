"""
测试通知功能
"""
import yaml
from src.utils.notifier import NotificationManager


def test_notification():
    """测试通知功能"""
    print("="*50)
    print("通知功能测试")
    print("="*50)

    # 加载配置
    with open("config/notification.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    notification_config = config.get("notification", {})
    print(f"\n配置状态:")
    print(f"  启用: {notification_config.get('enabled')}")
    print(f"  渠道: {notification_config.get('channels', [])}")

    # 初始化通知管理器
    notifier = NotificationManager(notification_config)

    # 测试 1: 套利机会通知
    print("\n[测试 1] 套利机会通知...")
    result1 = notifier.send_opportunity(
        fund_code="163406",
        fund_name="兴全合润混合",
        opportunity_type="premium",
        premium_rate=0.025,
        price=2.258,
        nav=2.203
    )
    print(f"结果: {'✅ 成功' if result1 else '❌ 失败'}")

    # 测试 2: 交易通知
    print("\n[测试 2] 交易通知...")
    result2 = notifier.send_trade(
        fund_code="163406",
        fund_name="兴全合润混合",
        action="买入",
        quantity=10,
        price=2.25,
        amount=2250.0
    )
    print(f"结果: {'✅ 成功' if result2 else '❌ 失败'}")

    # 测试 3: 错误通知
    print("\n[测试 3] 错误通知...")
    result3 = notifier.send_error(
        error_type="连接失败",
        error_message="无法连接到券商 API: Connection timeout"
    )
    print(f"结果: {'✅ 成功' if result3 else '❌ 失败'}")

    # 测试 4: 自定义通知
    print("\n[测试 4] 自定义通知...")
    result4 = notifier.send(
        title="📊 系统状态",
        message=f"""套利框架运行正常
- 数据获取: ✅
- 券商连接: ✅
- 策略执行: ✅

运行时间: {notifier._get_time()}"""
    )
    print(f"结果: {'✅ 成功' if result4 else '❌ 失败'}")

    print("\n" + "="*50)
    print("测试完成")
    print("="*50)

    if all([result1, result2, result3, result4]):
        print("\n✅ 所有测试通过！")
        return True
    else:
        print("\n⚠️ 部分测试失败")
        return False


if __name__ == "__main__":
    test_notification()
