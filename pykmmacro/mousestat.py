from collections import deque
from typing import Callable

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

def setup_mouse_listener() -> Callable[[], PositionInScreen | None]:
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

    def on_click(x: int, y: int, button: mouse.Button, pressed: bool) -> bool | None:
        if button != mouse.Button.left:
            return None
        if pressed:
            return None # ignore 'mouseDown' event (use 'mouseUp' event)
        queue.append(PositionInScreen(x, y))
        return None

    listener = mouse.Listener(on_click=on_click)

    listener.start() # start new listener theread

    return get_position_of_latest_click
