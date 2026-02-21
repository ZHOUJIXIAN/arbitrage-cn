"""
LOF 基金套利测试脚本
"""
import sys
from pathlib import Path

# 添加 src 到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from api.sim_broker import SimulatedBroker
from strategies.lof_arbitrage import LOFArbitrage
from utils.logger import setup_logger

log = setup_logger("test_lof")


def test_lof_arbitrage():
    """测试 LOF 套利策略"""

    log.info("=== LOF 基金套利测试 ===")

    # 创建模拟券商
    broker = SimulatedBroker(initial_cash=100000)
    broker.connect()

    # 配置
    config = {
        'enabled': True,
        'interval_seconds': 10,
        'min_premium_rate': 0.01,
        'min_discount_rate': 0.01,
        'min_trade_amount': 1000,
        'max_trade_amount': 10000,
        'watchlist': ['163406', '161725', '160642']  # 测试几只常见 LOF
    }

    # 创建策略
    strategy = LOFArbitrage(broker, config, simulate=True)

    # 查看账户信息
    balance = broker.get_balance()
    log.info(f"账户余额: {balance}")

    # 运行一次扫描
    log.info("开始扫描套利机会...")
    strategy.scan_opportunities()

    # 查看套利机会
    opportunities = strategy.get_opportunities()

    log.info(f"\n=== 扫描完成 ===")
    log.info(f"发现 {len(opportunities)} 个套利机会:")

    if opportunities:
        for i, opp in enumerate(opportunities, 1):
            log.info(f"\n机会 {i}:")
            log.info(f"  类型: {opp['type']}")
            log.info(f"  基金: {opp['name']}({opp['code']})")
            log.info(f"  价格: {opp['price']:.3f}")
            log.info(f"  净值: {opp['nav']:.3f}")
            log.info(f"  溢价率: {opp['premium_rate']:.2%}")
            log.info(f"  金额: {opp['amount']:.2f} 元")

    else:
        log.info("当前没有发现套利机会")

    return opportunities


if __name__ == "__main__":
    test_lof_arbitrage()
