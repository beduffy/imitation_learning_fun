import pyautogui

def capture_screen(filename='screenshot.png'):
    # Take a screenshot using pyautogui
    screenshot = pyautogui.screenshot()
    # Save the screenshot to a file
    screenshot.save(filename)

# Usage
capture_screen('my_screenshot.png')