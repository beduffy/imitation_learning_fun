import pyautogui
import time

def print_mouse_position_continuously():
    try:
        while True:
            x, y = pyautogui.position()
            print(f"Current mouse position: X={x}, Y={y}")
            time.sleep(0.05)  # Delay to make the output readable
    except KeyboardInterrupt:
        print("Stopped printing mouse positions.")

print_mouse_position_continuously()
