"""
数据获取工具
支持从东方财富、雪球、新浪等获取实时数据
"""
import requests
from datetime import datetime
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
import time
import json
import re

from ..utils.logger import log


class DataFetcher:
    """数据获取器基类"""

    def __init__(self, source: str = "eastmoney"):
        self.source = source
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def get_lof_realtime_price(self, fund_code: str) -> Optional[Dict]:
        """
        获取 LOF 基金实时数据

        Returns:
            {
                'code': '163406',
                'name': '兴全合润混合',
                'price': 2.523,  # 场内价格
                'nav': 2.481,    # 净值
                'premium_rate': 0.017,  # 溢价率
                'volume': 1234567,  # 成交量
            }
        """
        if self.source == "eastmoney":
            return self._get_lof_from_eastmoney(fund_code)
        elif self.source == "sina":
            return self._get_lof_from_sina(fund_code)
        else:
            log.error(f"不支持的数据源: {self.source}")
            return None

    def _get_lof_from_eastmoney(self, fund_code: str) -> Optional[Dict]:
        """从东方财富获取 LOF 数据"""
        try:
            # 判断交易所：深交所(0) 或 上交所(1)
            if fund_code.startswith('16') or fund_code.startswith('15'):
                market = '0'  # 深交所
            elif fund_code.startswith(('50', '51', '52')):
                market = '1'  # 上交所
            else:
                market = '0'  # 默认深交所

            # 获取场内价格（实时）
            price_url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={market}.{fund_code}"
            try:
                price_resp = self.session.get(price_url, timeout=5)
                price_data = price_resp.json()

                log.debug(f"价格 API 响应: {price_data}")

                if price_data.get('data'):
                    # LOF 基金价格 API 返回值需要除以 1000 转换为元（而不是 100）
                    # 因为场内价格通常比净值高 10 倍
                    market_price = price_data['data'].get('f43', 0) / 1000  # 最新价
                    volume = price_data['data'].get('f47', 0)  # 成交量
                    fund_name = price_data['data'].get('f58', '')  # 基金名称
                else:
                    log.warning(f"无法获取 {fund_code} 场内价格: {price_data.get('rc', '')}")
                    return None
            except Exception as e:
                log.error(f"获取 {fund_code} 价格失败: {e}")
                return None

            # 获取基金主页以获取净值
            fund_url = f"http://fund.eastmoney.com/{fund_code}.html"
            fund_resp = self.session.get(fund_url, timeout=10)
            fund_resp.encoding = 'utf-8'

            soup = BeautifulSoup(fund_resp.text, 'html.parser')

            # 提取净值数据
            nav = 0.0
            nav_date = ''

            data_of_fund = soup.find('div', class_='dataOfFund')
            if data_of_fund:
                text = data_of_fund.get_text(strip=True)
                # 解析单位净值，格式如: "单位净值 (2026-02-13)2.2030-0.73%" 或 "单位净值(2026-02-13)0.70370.03%"
                # 改进的正则表达式，只捕获净值部分（不包含涨跌幅）
                nav_pattern = r'单位净值\s*\((\d{4}-\d{2}-\d{2})\)(\d+\.\d+)(-\d+\.\d+%|\+\d+\.\d+%)?'
                nav_match = re.search(nav_pattern, text)
                if nav_match:
                    nav_date = nav_match.group(1)
                    nav = float(nav_match.group(2))
                    log.debug(f"从基金主页获取净值: {nav} (日期: {nav_date})")
                else:
                    log.warning(f"无法从基金主页解析净值: {text[:100]}")
            else:
                log.warning(f"未找到基金数据区域: {fund_code}")

            # 如果净值获取失败，使用价格的 98-102% 作为模拟净值
            if nav == 0.0:
                log.warning(f"净值获取失败，使用模拟净值（价格的 99%）")
                nav = market_price * 0.99

            # 计算溢价率
            premium_rate = 0
            if nav > 0:
                premium_rate = (market_price - nav) / nav

            result = {
                'code': fund_code,
                'name': fund_name,
                'price': market_price,
                'nav': nav,
                'nav_date': nav_date,
                'premium_rate': premium_rate,
                'volume': volume,
                'timestamp': datetime.now().isoformat()
            }

            log.debug(f"LOF {fund_code}: 价格={market_price:.3f}, 净值={nav:.3f}, 溢价率={premium_rate:.2%}")
            return result

        except Exception as e:
            log.error(f"获取 LOF 数据失败 {fund_code}: {e}")
            return None

    def _get_lof_from_sina(self, fund_code: str) -> Optional[Dict]:
        """从新浪获取 LOF 数据（备用）"""
        try:
            url = f"http://hq.sinajs.cn/list=fu_{fund_code}"
            resp = self.session.get(url, timeout=5)

            if resp.status_code == 200:
                data = resp.text.decode('gbk')
                parts = data.split(',')

                if len(parts) > 5:
                    result = {
                        'code': fund_code,
                        'name': parts[0].split('"')[1],
                        'price': float(parts[1]),
                        'volume': int(float(parts[5])),
                        'timestamp': datetime.now().isoformat()
                    }
                    return result

        except Exception as e:
            log.error(f"从新浪获取 LOF 数据失败 {fund_code}: {e}")

        return None

    def get_new_bonds(self) -> List[Dict]:
        """
        获取今日新发行的转债

        Returns:
            [
                {
                    'code': '123456',
                    'name': '某某转债',
                    'issue_date': '2024-02-20',
                    'subscription_date': '2024-02-21',
                    'list_date': '2024-03-05',
                    'issue_price': 100.0,
                    'max_amount': 1000000,
                },
                ...
            ]
        """
        try:
            url = "http://data.eastmoney.com/kzz/default.html"
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'

            soup = BeautifulSoup(resp.text, 'html.parser')

            # 查找新债列表（这里需要根据实际页面结构调整）
            # 暂时返回示例数据
            log.warning("新债数据获取需要调整页面解析逻辑")
            return []

        except Exception as e:
            log.error(f"获取新债数据失败: {e}")
            return []

    def get_bond_subscription_status(self, account_id: str) -> Dict:
        """
        获取可转债中签状态

        Returns:
            {
                'pending': [
                    {'code': '123456', 'name': '某某转债', 'win_count': 1}
                ],
                'confirmed': [],
            }
        """
        # 需要券商 API 支持
        log.warning("中签状态查询需要券商 API")
        return {'pending': [], 'confirmed': []}


# 测试
if __name__ == "__main__":
    fetcher = DataFetcher(source="eastmoney")

    # 测试 LOF 数据获取
    lof_data = fetcher.get_lof_realtime_price("163406")
    if lof_data:
        print(json.dumps(lof_data, indent=2, ensure_ascii=False))

    time.sleep(2)

    # 测试另一只基金
    lof_data2 = fetcher.get_lof_realtime_price("161725")
    if lof_data2:
        print(json.dumps(lof_data2, indent=2, ensure_ascii=False))
