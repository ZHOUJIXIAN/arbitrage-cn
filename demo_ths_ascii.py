import easytrader

print("=== Easytrader THS Demo ===\n")

# 1. Initialize client
print("1. Initialize THS client...")
client = easytrader.use("ths")
print("   [OK] Init success")

# 2. Check connection
print("\n2. Connect to xiadan.exe...")
try:
    client.connect()
    print("   [OK] Connected")
except Exception as e:
    print(f"   [FAIL] {e}")
    print("\n   Reasons:")
    print("   - xiadan.exe not running")
    print("   - xiadan.exe window minimized")
    print("   - Not logged in")
    print("\n   Solution: Start and login to xiadan.exe")
    exit(1)

# 3. Get balance
print("\n3. Get balance...")
try:
    balance = client.balance
    print("   [OK] Got balance")
    print(f"   Details: {balance}")
except Exception as e:
    print(f"   [FAIL] {e}")

# 4. Get position
print("\n4. Get position...")
try:
    position = client.position
    print("   [OK] Got position")
    print(f"   Count: {len(position) if position else 0}")
    if position:
        for p in position[:3]:
            print(f"   - {p}")
except Exception as e:
    print(f"   [FAIL] {e}")

# 5. Mock order
print("\n5. Mock order...")
print("   (Uncomment to place real order)")
print("   # client.buy(security='163406.SZ', amount=100, price=2.5)")

print("\n=== Demo Complete ===")
print("\nNote: Easytrader can control THS client")
print("Need to login THS account for real trading")
