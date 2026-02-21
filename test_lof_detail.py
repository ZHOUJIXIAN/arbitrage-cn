"""
LOF 基金套利详细测试脚本
"""
import sys
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
import re
from loguru import logger as log

# 模拟 DataFetcher 的功能
def get_lof_realtime_price(fund_code: str):
    """从东方财富获取 LOF 数据"""
    try:
        # 判断交易所
        if fund_code.startswith('16') or fund_code.startswith('15'):
            market = '0'
        else:
            market = '0'

        # 获取场内价格
        price_url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={market}.{fund_code}"
        price_resp = requests.get(price_url, timeout=5)
        price_data = price_resp.json()

        if price_data.get('data'):
            market_price = price_data['data'].get('f43', 0) / 1000
            volume = price_data['data'].get('f47', 0)
            fund_name = price_data['data'].get('f58', '')
        else:
            return None

        # 获取净值
        fund_url = f"http://fund.eastmoney.com/{fund_code}.html"
        fund_resp = requests.get(fund_url, timeout=10)
        fund_resp.encoding = 'utf-8'

        soup = BeautifulSoup(fund_resp.text, 'html.parser')

        nav = 0.0
        nav_date = ''

        data_of_fund = soup.find('div', class_='dataOfFund')
        if data_of_fund:
            text = data_of_fund.get_text(strip=True)
            nav_pattern = r'单位净值\s*\((\d{4}-\d{2}-\d{2})\)(\d+\.\d+)(-\d+\.\d+%|\+\d+\.\d+%)?'
            nav_match = re.search(nav_pattern, text)
            if nav_match:
                nav_date = nav_match.group(1)
                nav = float(nav_match.group(2))

        # 计算溢价率
        premium_rate = 0
        if nav > 0:
            premium_rate = (market_price - nav) / nav

        return {
            'code': fund_code,
            'name': fund_name,
            'price': market_price,
            'nav': nav,
            'nav_date': nav_date,
            'premium_rate': premium_rate,
            'volume': volume,
        }

    except Exception as e:
        log.error(f"获取 LOF 数据失败 {fund_code}: {e}")
        return None


def test_detail():
    """详细测试每只基金的数据"""

    log.info("=== LOF 基金数据详细测试 ===")

    # 测试基金列表
    watchlist = ['163406', '161725', '160642']

    log.info(f"\n测试基金: {watchlist}\n")

    for fund_code in watchlist:
        log.info(f"--- {fund_code} ---")
        data = get_lof_realtime_price(fund_code)

        if data:
            print(f"基金名称: {data.get('name')}")
            print(f"场内价格: {data.get('price'):.4f} 元")
            print(f"净值: {data.get('nav'):.4f} 元")
            print(f"净值日期: {data.get('nav_date')}")
            print(f"溢价率: {data.get('premium_rate'):.2%}")

            # 判断是否是套利机会
            premium = data.get('premium_rate', 0)
            if premium > 0.01:
                print(f"  [溢价套利] 溢价率 {premium:.2%} > 1%")
            elif premium < -0.01:
                print(f"  [折价套利] 折价率 {abs(premium):.2%} > 1%")
            else:
                print(f"  [无套利机会] 溢价率 {premium:.2%} 在范围内")
        else:
            print(f"获取数据失败")

        print()


if __name__ == "__main__":
    test_detail()
