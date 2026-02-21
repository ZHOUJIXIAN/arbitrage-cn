"""
可转债打新测试脚本
"""
import sys
from pathlib import Path

# 添加 src 到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from api.sim_broker import SimulatedBroker
from strategies.bond_ipo import BondIPO
from utils.logger import setup_logger

log = setup_logger("test_bond")


def test_bond_ipo():
    """测试可转债打新策略"""

    log.info("=== 可转债打新测试 ===")

    # 创建模拟券商
    broker = SimulatedBroker()
    broker.connect()

    # 配置
    config = {
        'enabled': True,
        'check_time': '09:30',
        'max_subscription_amount': 1000000,
        'auto_subscribe': True,
        'notify_on_new_bond': True,
        'notify_on_win': True,
        'notify_on_list': True,
    }

    # 创建策略
    strategy = BondIPO(broker, config, simulate=True)

    # 运行每日检查
    log.info("运行每日检查...")
    strategy.daily_check()

    # 查看申购记录
    log.info(f"\n=== 检查完成 ===")
    log.info(f"已申购转债: {len(strategy.subscribed_bonds)} 只")

    if strategy.subscribed_bonds:
        log.info("申购列表:")
        for code in strategy.subscribed_bonds:
            log.info(f"  - {code}")

    return strategy.subscribed_bonds


if __name__ == "__main__":
    test_bond_ipo()
