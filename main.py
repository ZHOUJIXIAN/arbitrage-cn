"""
A 股套利框架主程序
"""
import sys
import yaml
import argparse
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.sim_broker import SimulatedBroker
# from src.api.ht_client import HTClient  # 暂时注释，需要 easytrader
from src.api.xueqiu import XueqiuClient
from src.api.ths_client import THSClient
from src.api.broker_base import OrderType
from src.strategies.lof_arbitrage import LOFArbitrage
from src.strategies.bond_ipo import BondIPO
from src.utils.logger import log
from src.utils.data_fetcher import DataFetcher


def load_config(config_path: str = "config/strategy.yml") -> dict:
    """加载配置文件"""
    config_file = Path(__file__).parent / config_path

    if not config_file.exists():
        log.error(f"配置文件不存在: {config_file}")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='A 股套利框架')
    parser.add_argument(
        '--strategy',
        type=str,
        choices=['lof', 'bond', 'all'],
        default='all',
        help='运行的策略'
    )
    parser.add_argument(
        '--broker',
        type=str,
        choices=['sim', 'xueqiu', 'ths'],  # sim=模拟, xueqiu=雪球, ths=中信
        default='sim',
        help='券商选择 (sim=模拟, xueqiu=雪球, ths=中信)'
    )
    parser.add_argument(
        '--account',
        type=str,
        help='券商账号/cookie（实盘模式需要）'
    )
    parser.add_argument(
        '--simulate',
        action='store_true',
        default=None,
        help='模拟模式（覆盖配置）'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式（运行一次后退出）'
    )

    args = parser.parse_args()

    # 加载配置
    config = load_config()

    # 确定模拟模式
    common_config = config.get('common', {})
    simulate = args.simulate if args.simulate is not None else common_config.get('simulate_mode', True)

    log.info(f"=== A 股套利框架启动 ===")
    log.info(f"策略: {args.strategy}")
    log.info(f"券商: {args.broker}")
    log.info(f"模拟模式: {simulate}")

    # 创建券商客户端
    if args.broker == 'sim' or simulate:
        # 模拟券商
        broker = SimulatedBroker(initial_cash=100000)
    # elif args.broker == 'ht':
    #     # 华泰客户端（暂时注释）
    #     broker = HTClient(simulate=simulate)
    #     if not simulate and not args.account:
    #         log.error("华泰实盘模式需要提供账号 (--account)")
    #         sys.exit(1)
    elif args.broker == 'xueqiu':
        # 雪球 API
        broker = XueqiuClient(simulate=simulate)
        if not simulate and not args.account:
            log.error("雪球实盘模式需要提供 cookie (--account)")
            sys.exit(1)
    elif args.broker == 'ths':
        # 中信证券（同花顺）
        broker = THSClient(simulate=simulate)
        if not simulate and not args.account:
            log.error("中信实盘模式需要提供账号 (--account)")
            sys.exit(1)
    else:
        log.error(f"不支持的券商: {args.broker}")
        sys.exit(1)

    # 创建策略
    strategies = []

    if args.strategy in ['lof', 'all']:
        lof_config = config.get('lof', {})
        if lof_config.get('enabled', True):
            strategies.append({
                'name': 'LOF 套利',
                'instance': LOFArbitrage(broker, lof_config, simulate=simulate)
            })

    if args.strategy in ['bond', 'all']:
        bond_config = config.get('bond', {})
        if bond_config.get('enabled', True):
            strategies.append({
                'name': '可转债打新',
                'instance': BondIPO(broker, bond_config, simulate=simulate)
            })

    if not strategies:
        log.error("没有启用的策略")
        sys.exit(1)

    log.info(f"已加载 {len(strategies)} 个策略:")
    for s in strategies:
        log.info(f"  - {s['name']}")

    # 测试模式：运行一次后退出
    if args.test:
        log.info("测试模式：运行一次后退出")

        # 连接券商
        if args.broker in ['xueqiu', 'ths'] and not simulate:
            if not broker.connect(args.account):
                log.error("无法连接券商")
                sys.exit(1)
        else:
            if not broker.connect():
                log.error("无法连接券商")
                sys.exit(1)

        # 测试 LOF 套利
        if args.strategy in ['lof', 'all']:
            for s in strategies:
                if s['name'] == 'LOF 套利':
                    s['instance'].scan_opportunities()
                    opps = s['instance'].get_opportunities()
                    log.info(f"LOF 套利机会: {len(opps)} 个")
                    for opp in opps:
                        log.info(f"  {opp}")

        # 测试可转债打新
        if args.strategy in ['bond', 'all']:
            for s in strategies:
                if s['name'] == '可转债打新':
                    s['instance'].daily_check()

        log.info("测试完成")
        sys.exit(0)

    # 正常运行模式
    try:
        # 启动所有策略
        import threading

        threads = []
        for s in strategies:
            t = threading.Thread(target=s['instance'].run, daemon=True)
            t.start()
            threads.append(t)
            log.info(f"{s['name']} 已启动")

        # 主线程等待
        log.info("所有策略已启动，按 Ctrl+C 停止")
        for t in threads:
            t.join()

    except KeyboardInterrupt:
        log.info("收到停止信号")
    finally:
        # 停止所有策略
        for s in strategies:
            s['instance'].stop()

        log.info("所有策略已停止")


if __name__ == "__main__":
    main()
