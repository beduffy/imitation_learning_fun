import pyautogui
import cv2
import numpy as np

def show_screen_live():
    # Continuously capture the screen and display it live
    while True:
        # Take a screenshot, convert to numpy array, change color space from RGB to BGR, and resize
        frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
        width = 1080
        height = int(frame.shape[0] * (width / frame.shape[1]))
        frame = cv2.resize(frame, (width, height))
        # Display the resized frame using OpenCV
        cv2.imshow("Live Screen", frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):  # Break the loop when 'q' is pressed
            break

        
    cv2.destroyAllWindows()

# Usage
show_screen_live()
