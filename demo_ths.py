import easytrader

print("=== THS Demo ===")
print("1. Easytrader loaded")

try:
    client = easytrader.use("ths")
    print("2. THS client created")

    # This will connect to the running xiadan.exe
    client.prepare()
    print("3. Connected to xiadan.exe")

    balance = client.balance
    print(f"4. Balance: {balance}")

    position = client.position
    print(f"5. Position: {position}")

except Exception as e:
    print(f"Error: {e}")
    print("Need to login to THS trading client (xiadan.exe)")
