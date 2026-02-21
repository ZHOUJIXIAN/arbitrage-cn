"""
通知模块 - 支持多种通知渠道
"""
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

try:
    from loguru import logger as log
except:
    log = logging.getLogger(__name__)


class NotifierBase(ABC):
    """通知基类"""

    @abstractmethod
    def send(self, title: str, message: str, **kwargs) -> bool:
        """发送通知"""
        pass


class TelegramNotifier(NotifierBase):
    """Telegram 通知"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send(self, title: str, message: str, **kwargs) -> bool:
        """发送 Telegram 通知"""
        try:
            import requests

            # 格式化消息
            text = f"*{title}*\n\n{message}"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }

            response = requests.post(
                f"{self.api_url}/sendMessage",
                data=data,
                timeout=10
            )
            response.raise_for_status()

            log.info(f"Telegram 通知发送成功: {title}")
            return True

        except Exception as e:
            log.error(f"Telegram 通知失败: {e}")
            return False


class SlackNotifier(NotifierBase):
    """Slack 通知"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, title: str, message: str, **kwargs) -> bool:
        """发送 Slack 通知"""
        try:
            import requests

            data = {
                "text": f"*{title}*\n{message}",
                "mrkdwn": True
            }

            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=10
            )
            response.raise_for_status()

            log.info(f"Slack 通知发送成功: {title}")
            return True

        except Exception as e:
            log.error(f"Slack 通知失败: {e}")
            return False


class ConsoleNotifier(NotifierBase):
    """控制台通知（测试用）"""

    def send(self, title: str, message: str, **kwargs) -> bool:
        """打印到控制台"""
        try:
            print(f"\n{'='*50}")
            print(f"📢 {title}")
            print(f"{'='*50}")
            print(f"{message}\n")
            log.info(f"通知: {title}")
            return True
        except Exception as e:
            log.error(f"控制台通知失败: {e}")
            return False


class NotificationManager:
    """通知管理器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知管理器

        Args:
            config: 通知配置
                {
                    'enabled': True,
                    'channels': ['telegram', 'console'],
                    'telegram': {
                        'bot_token': 'xxx',
                        'chat_id': 'xxx'
                    },
                    'slack': {
                        'webhook_url': 'xxx'
                    }
                }
        """
        self.config = config
        self.notifiers = []
        self._init_notifiers()

    def _init_notifiers(self):
        """初始化通知渠道"""
        if not self.config.get('enabled', False):
            log.info("通知已禁用")
            return

        channels = self.config.get('channels', [])

        for channel in channels:
            if channel == 'telegram':
                telegram_config = self.config.get('telegram', {})
                bot_token = telegram_config.get('bot_token')
                chat_id = telegram_config.get('chat_id')

                if bot_token and chat_id:
                    self.notifiers.append(
                        TelegramNotifier(bot_token, chat_id)
                    )
                    log.info("Telegram 通知已启用")
                else:
                    log.warning("Telegram 配置不完整，跳过")

            elif channel == 'slack':
                slack_config = self.config.get('slack', {})
                webhook_url = slack_config.get('webhook_url')

                if webhook_url:
                    self.notifiers.append(
                        SlackNotifier(webhook_url)
                    )
                    log.info("Slack 通知已启用")
                else:
                    log.warning("Slack 配置不完整，跳过")

            elif channel == 'console':
                self.notifiers.append(ConsoleNotifier())
                log.info("控制台通知已启用")

    def send(self, title: str, message: str, **kwargs) -> bool:
        """
        发送通知到所有已配置的渠道

        Args:
            title: 标题
            message: 消息内容
            **kwargs: 额外参数

        Returns:
            bool: 是否至少有一个渠道发送成功
        """
        if not self.notifiers:
            log.warning("没有启用的通知渠道")
            return False

        success_count = 0

        for notifier in self.notifiers:
            try:
                if notifier.send(title, message, **kwargs):
                    success_count += 1
            except Exception as e:
                log.error(f"通知发送失败 ({notifier.__class__.__name__}): {e}")

        return success_count > 0

    def send_opportunity(self, fund_code: str, fund_name: str,
                       opportunity_type: str, premium_rate: float,
                       price: float, nav: float) -> bool:
        """
        发送套利机会通知

        Args:
            fund_code: 基金代码
            fund_name: 基金名称
            opportunity_type: 机会类型 (premium/discount)
            premium_rate: 溢价率
            price: 场内价格
            nav: 场外净值
        """
        type_cn = "溢价" if opportunity_type == "premium" else "折价"
        title = f"🚀 LOF 套利机会 - {fund_name}"
        message = f"""基金代码: {fund_code}
基金名称: {fund_name}
机会类型: {type_cn} {premium_rate*100:.2f}%
场内价格: {price:.3f} 元
场外净值: {nav:.3f} 元
价差: {price - nav:.3f} 元"""

        return self.send(title, message)

    def send_trade(self, fund_code: str, fund_name: str,
                  action: str, quantity: int, price: float,
                  amount: float) -> bool:
        """
        发送交易通知

        Args:
            fund_code: 基金代码
            fund_name: 基金名称
            action: 操作 (买入/卖出/申购/赎回)
            quantity: 数量（手）
            price: 价格
            amount: 金额（元）
        """
        action_icon = "🟢" if action in ["买入", "申购"] else "🔴"
        title = f"{action_icon} 交易执行 - {fund_name}"
        message = f"""基金代码: {fund_code}
基金名称: {fund_name}
操作类型: {action}
成交数量: {quantity} 手
成交价格: {price:.3f} 元
成交金额: {amount:.2f} 元"""

        return self.send(title, message)

    def send_error(self, error_type: str, error_message: str) -> bool:
        """
        发送错误通知

        Args:
            error_type: 错误类型
            error_message: 错误消息
        """
        title = f"❌ 套利框架异常 - {error_type}"
        message = f"""错误类型: {error_type}
错误详情: {error_message}
时间: {self._get_time()}"""

        return self.send(title, message)

    def _get_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
