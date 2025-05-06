from collections import deque

import pydirectinput
from pynput import mouse

from .windowsapi import PositionInScreen

#=============================================================================
# Get mouse cursor position

def get_mouse_position() -> PositionInScreen:
    x, y = pydirectinput.position()
    return PositionInScreen(x, y)

#=============================================================================
# Mouse event listener
# https://pypi.org/project/pynput/

def setup_mouse_listener():
    # https://docs.python.org/3/library/collections.html#deque-objects
    # - deque is thread-safe.
    # - if deque is full, when a new item is added, the item at the opposite side will be discarded.
    queue: deque[PositionInScreen] = deque(maxlen=1)

    def get_position_of_latest_click() -> PositionInScreen | None:
        try:
            pos = queue.popleft()
            return pos
        except IndexError:
            return None

    def on_click(x, y, button, pressed, _injected):
        if button != mouse.Button.left:
            return
        if pressed:
            return # ignore 'mouseDown' event (use 'mouseUp' event)
        queue.append(PositionInScreen(x, y))

    listener = mouse.Listener(on_click=on_click)

    listener.start() # start new listener theread

    return get_position_of_latest_click
