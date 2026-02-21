import easytrader

client = easytrader.use("ths")

print("=== THS Client Methods ===")
methods = [m for m in dir(client) if not m.startswith('_')]
for method in methods:
    print(f"  - {method}")

print("\n=== Try connect ===")
try:
    client.connect()
    print("Connect OK")
except Exception as e:
    print(f"Connect Fail: {e}")

print("\n=== Try balance ===")
try:
    balance = client.balance
    print(f"Balance: {balance}")
except Exception as e:
    print(f"Balance Fail: {e}")
