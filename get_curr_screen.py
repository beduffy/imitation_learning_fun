import pyautogui
import cv2
import numpy as np

from PIL import ImageGrab, ImageDraw

# TODO do only one screen or just unplug one? # Example usage for a monitor at position (0, 0) with resolution 1920x1080
# screenshot = pyautogui.screenshot(region=(x_start, y_start, width, height))
# capture_specific_monitor(0, 0, 1920, 1080, 'monitor1_screenshot.png')
# TODO what should the output of DETR/vae/transformer be? pixels to move the mouse? relative or absolute pixels?

def show_screen_live():
    # Continuously capture the screen, display it live, and move the mouse left and right
    move_left = True
    while True:
        # Take a screenshot, convert to numpy array, change color space from RGB to BGR, and resize
        
        # Capture the screen
        screenshot = ImageGrab.grab()
        # Get the current position of the mouse
        x, y = pyautogui.position()
        # Create a drawing context
        draw = ImageDraw.Draw(screenshot)
        # Define the size of the cursor
        cursor_size = 10
        # Draw the cursor as a red circle
        draw.ellipse((x - cursor_size, y - cursor_size, x + cursor_size, y + cursor_size), fill='red')
        
        # frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # frame = np.array(screenshot)
        width = 1080
        height = int(frame.shape[0] * (width / frame.shape[1]))
        frame = cv2.resize(frame, (width, height))
        # Display the resized frame using OpenCV
        cv2.imshow("Live Screen", frame)
        
        # Move mouse left 100 pixels or right 100 pixels
        current_mouse_x, current_mouse_y = pyautogui.position()
        amount_to_move_mouse = 400
        if move_left:
            pyautogui.moveTo(current_mouse_x - amount_to_move_mouse, current_mouse_y)
            move_left = False  # Next move should be to the right
        else:
            pyautogui.moveTo(current_mouse_x + amount_to_move_mouse, current_mouse_y)
            move_left = True  # Next move should be to the left

        if cv2.waitKey(100) & 0xFF == ord('q'):  # Break the loop when 'q' is pressed
            break

    cv2.destroyAllWindows()

# Usage
show_screen_live()