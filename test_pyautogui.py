import pyautogui
import cv2

print("Testing pyautogui and OpenCV...")
print(f"pyautogui version: {pyautogui.__version__}")
print(f"OpenCV version: {cv2.__version__}")

# Test if confidence parameter works
try:
    # This will fail if OpenCV is not properly integrated
    # but should not crash
    print("Testing locateOnScreen with confidence...")
    # We're not actually looking for an image, just testing the parameter
    result = pyautogui.locateOnScreen('target.png', confidence=0.85)
    print("Confidence parameter works!")
except Exception as e:
    print(f"Error with confidence parameter: {e}")

print("Test completed.")
