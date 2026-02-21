import pyautogui
import time

pyautogui.FAILSAFE = False

print("=== THS Control Demo with PyAutoGUI ===\n")

# Get window list (simulate)
print("1. Screen info:")
print(f"   Size: {pyautogui.size()}")
print(f"   Mouse: {pyautogui.position()}")

print("\n2. Simulate THS operations:")
print("   - Moving mouse to THS window...")

time.sleep(2)

# Move mouse to a position (top-left area)
pyautogui.moveTo(100, 100, duration=1)
print("   - Mouse moved to (100, 100)")

time.sleep(1)

# Click
print("   - Clicking...")
pyautogui.click()
print("   - Clicked")

time.sleep(1)

# Type something (simulating entering stock code)
print("   - Typing stock code...")
pyautogui.write("163406", interval=0.1)
print("   - Typed: 163406")

time.sleep(1)

# Press Enter
print("   - Pressing Enter...")
pyautogui.press('enter')
print("   - Enter pressed")

print("\n3. What PyAutoGUI can do:")
print("   - Mouse control: move, click, drag, scroll")
print("   - Keyboard input: type text, press keys")
print("   - Screenshot: find images and click")
print("   - Window control: activate, minimize, maximize")

print("\n=== Demo Complete ===")
print("\nNote: PyAutoGUI can control ANY GUI application")
print("This is how easytrader works internally too!")
