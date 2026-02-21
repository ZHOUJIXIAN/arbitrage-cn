import easytrader
import os

print("Easytrader version:", easytrader.__version__ if hasattr(easytrader, '__version__') else "unknown")
print("Location:", os.path.dirname(easytrader.__file__))

print("\nSupported brokers:")
print("  - ths (TongHuaShun)")
print("  - yh (YinHe)")
print("  - gj (GuoJin)")
print("  - xq (XueQiu)")

print("\nTHS broker info:")
client = easytrader.use("ths")
print("  Type:", client.broker_type if hasattr(client, 'broker_type') else "ths")
print("  App:", client.app if hasattr(client, 'app') else "xiadan.exe")
