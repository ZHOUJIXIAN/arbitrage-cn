"""
配置文件验证脚本
检查所有配置文件的格式和完整性
"""
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


class ConfigValidator:
    """配置文件验证器"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """验证所有配置文件"""
        self.errors = []
        self.warnings = []

        print("=" * 60)
        print("📋 配置文件验证")
        print("=" * 60)

        # 检查策略配置
        self._validate_file("strategy.yml", required=True)

        # 检查通知配置
        self._validate_file("notification.yml", required=False)

        # 检查 API 密钥配置
        self._validate_file("api_keys.yml", required=False)

        # 显示结果
        self._show_results()

        return len(self.errors) == 0

    def _validate_file(self, filename: str, required: bool = False):
        """验证单个配置文件"""
        filepath = self.config_dir / filename

        if not filepath.exists():
            if required:
                self.errors.append(f"❌ {filename}: 文件不存在（必需）")
            else:
                self.warnings.append(f"⚠️  {filename}: 文件不存在（可选）")
            return

        print(f"\n验证: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if config is None:
                self.warnings.append(f"⚠️  {filename}: 配置文件为空")
                return

            # 检查必需的配置项
            if filename == "strategy.yml":
                self._validate_strategy(config)
            elif filename == "notification.yml":
                self._validate_notification(config)
            elif filename == "api_keys.yml":
                self._validate_api_keys(config)

            print(f"  ✅ 格式正确")

        except yaml.YAMLError as e:
            self.errors.append(f"❌ {filename}: YAML 格式错误 - {e}")
        except Exception as e:
            self.errors.append(f"❌ {filename}: 验证失败 - {e}")

    def _validate_strategy(self, config: Dict):
        """验证策略配置"""
        required_sections = ['lof', 'bond', 'common']

        for section in required_sections:
            if section not in config:
                self.warnings.append(f"⚠️  缺少配置段: {section}")

        # 检查 LOF 配置
        lof_config = config.get('lof', {})
        if 'watchlist' in lof_config and not lof_config['watchlist']:
            self.warnings.append("⚠️  LOF 监控列表为空")

        if 'min_premium_rate' in lof_config:
            rate = lof_config['min_premium_rate']
            if rate < 0 or rate > 1:
                self.errors.append(f"❌ LOF 最小溢价率无效: {rate}")

        if 'min_discount_rate' in lof_config:
            rate = lof_config['min_discount_rate']
            if rate < 0 or rate > 1:
                self.errors.append(f"❌ LOF 最小折价率无效: {rate}")

        # 检查可转债配置
        bond_config = config.get('bond', {})
        if 'max_subscription_amount' in bond_config:
            amount = bond_config['max_subscription_amount']
            if amount < 0:
                self.errors.append(f"❌ 可转债申购金额无效: {amount}")

        # 检查通用配置
        common_config = config.get('common', {})
        if 'simulate_mode' in common_config:
            if not isinstance(common_config['simulate_mode'], bool):
                self.errors.append("❌ 模拟模式配置类型错误")

    def _validate_notification(self, config: Dict):
        """验证通知配置"""
        notification_config = config.get('notification', {})

        # 检查是否启用
        if not notification_config.get('enabled', False):
            self.warnings.append("⚠️  通知功能未启用")
            return

        # 检查渠道配置
        channels = notification_config.get('channels', [])
        if not channels:
            self.warnings.append("⚠️  未配置通知渠道")

        # 检查 Telegram 配置
        if 'telegram' in channels:
            telegram_config = notification_config.get('telegram', {})
            bot_token = telegram_config.get('bot_token', '')
            chat_id = telegram_config.get('chat_id', '')

            if not bot_token:
                self.warnings.append("⚠️  Telegram Bot Token 未配置")
            if not chat_id:
                self.warnings.append("⚠️  Telegram Chat ID 未配置")

        # 检查 Slack 配置
        if 'slack' in channels:
            slack_config = notification_config.get('slack', {})
            webhook_url = slack_config.get('webhook_url', '')

            if not webhook_url:
                self.warnings.append("⚠️  Slack Webhook URL 未配置")

        # 检查通知类型配置
        types = notification_config.get('types', {})
        if 'opportunity' in types:
            opp_config = types['opportunity']
            if opp_config.get('min_premium_rate', 0) < 0:
                self.errors.append("❌ 最小溢价率不能为负数")

        # 检查频率限制配置
        rate_limit = notification_config.get('rate_limit', {})
        if rate_limit.get('enabled', False):
            max_per_min = rate_limit.get('max_notifications_per_minute', 0)
            if max_per_min <= 0:
                self.errors.append("❌ 每分钟最大通知数必须大于 0")

    def _validate_api_keys(self, config: Dict):
        """验证 API 密钥配置"""
        if not config:
            self.warnings.append("⚠️  API 密钥配置为空")
            return

        # 检查必需的密钥
        required_keys = ['BRAVE_API_KEY', 'ELEVENLABS_API_KEY',
                        'OPENAI_API_KEY', 'NOTION_API_KEY']

        for key in required_keys:
            value = config.get(key, '')
            if not value:
                self.warnings.append(f"⚠️  {key} 未配置（可选）")
            elif len(value) < 10:
                self.warnings.append(f"⚠️  {key} 密钥长度似乎过短")

    def _show_results(self):
        """显示验证结果"""
        print("\n" + "=" * 60)
        print("验证结果")
        print("=" * 60)

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)} 个):")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print(f"\n❌  错误 ({len(self.errors)} 个):")
            for error in self.errors:
                print(f"  {error}")
        else:
            print("\n✅ 所有配置文件格式正确")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    validator = ConfigValidator()
    success = validator.validate_all()

    return success


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
