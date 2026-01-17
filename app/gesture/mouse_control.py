import pyautogui

def move(x, y):
    pyautogui.moveTo(x, y)

def left_click():
    pyautogui.click()

def right_click():
    pyautogui.rightClick()
