import pydirectinput

from .windowsapi import PositionInScreen

def get_mouse_position() -> PositionInScreen:
    x, y = pydirectinput.position()
    return PositionInScreen(x, y)
