import mouse
import pyautogui
from pynput.mouse import Button, Controller
import time

mouse2 = Controller()
while True:
    print("Mouse:",mouse.get_position())
    print("pyautogui",pyautogui.position())
    print("pynput: ",mouse2.position)
    time.sleep(1)