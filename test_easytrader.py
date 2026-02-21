"""
easytrader 测试脚本
在云服务器上运行此脚本测试券商连接
"""
import easytrader
from datetime import datetime

print("=" * 50)
print("easytrader 测试")
print("=" * 50)
print()

# 测试 easytrader 是否安装
try:
    import easytrader
    print("✓ easytrader 已安装")
    print(f"  版本: {easytrader.__version__ if hasattr(easytrader, '__version__') else '未知'}")
except ImportError as e:
    print("✗ easytrader 未安装")
    print(f"  错误: {e}")
    print("\n请运行: pip install easytrader")
    exit(1)

print()

# 测试华泰涨乐财富通
print("-" * 50)
print("测试华泰涨乐财富通连接")
print("-" * 50)
print()

# 请输入账号密码
print("请准备以下信息：")
print("  1. 资金账号")
print("  2. 登录密码")
print("  3. 交易密码（如果需要）")
print()

# 创建华泰交易客户端
trader = easytrader.use('ht')
print("✓ 华泰交易客户端已创建")

print()
print("下一步：")
print("  1. 确保涨乐财富通客户端已安装")
print("  2. 运行登录脚本连接券商")
print()

# 模拟登录测试
print("=" * 50)
print("测试完成")
print("=" * 50)
