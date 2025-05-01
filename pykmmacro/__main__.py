import time

from . import *

print("Hello world!")

print("sleep 3 sec")
time.sleep(3)

print("press 'A'")
key_press(NORMAL_KEY.A)

print("press ']'")
key_press(NORMAL_KEY.RightSquareBracket)

print("press 'NUM*'")
key_press(NORMAL_KEY.NUM_Multiply)

print("press '1' with SHIFT key")
key_press(NORMAL_KEY.One, MODIFIER.SHIFT)

print("press Ctrl+Shift+O")
key_press(NORMAL_KEY.O, MODIFIER.CTRL | MODIFIER.SHIFT)

print("finish")
