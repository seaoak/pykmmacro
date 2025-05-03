from collections import namedtuple
from dataclasses import dataclass

import pydirectinput

from .keyboardinput import MODIFIER, with_modifier_keys
from .utils import *
from .windowsapi import *

#=============================================================================
# Constant

@dataclass(frozen=True)
class _MouseButton:
    name: str
    code: str

_MOUSE_BUTTON_DICT = {
    'LEFT': 'left',
    'RIGHT': 'right',
    'MIDDLE': 'middle',
}

MOUSE_BUTTON = namedtuple("MouseButton", _MOUSE_BUTTON_DICT.keys())(**dict(((name, _MouseButton(name, value)) for name, value in _MOUSE_BUTTON_DICT.items())))

#=============================================================================
# Private function

_pending_buttons: set[_MouseButton] = set()

def _cleanup():
    if _pending_buttons:
        buttons = [button for button in _pending_buttons] # shallow copy because `_pending_buttons` is modified in iteration
        for button in buttons:
            _mouse_up(button)
        assert not _pending_buttons

def _mouse_down(button: _MouseButton):
    print(f"MouseDown: {button.name}")
    assert button not in _pending_buttons
    _pending_buttons.add(button)
    assert isinstance(button.code, str)
    pydirectinput.mouseDown(button=button.code)

def _mouse_up(button: _MouseButton):
    print(f"MouseUp: {button.name}")
    assert button in _pending_buttons
    assert isinstance(button.code, str)
    pydirectinput.mouseUp(button=button.code)
    _pending_buttons.remove(button)

#=============================================================================
# Public function

def mouse_click(button: _MouseButton = MOUSE_BUTTON.LEFT, modifier=MODIFIER.NONE, /):
    """
    Press mouse button.
    Modifier keys can be specified as a bitmap (use bit-OR to specify multiple modifier keys).
    """
    def helper():
        try:
            _mouse_down(button)
            my_sleep_a_moment()
        finally:
            _cleanup()
            my_sleep_a_moment()

    with_modifier_keys(helper, modifier)

def mouse_move_relative(diff_x: int, diff_y: int):
    """
    Move mouse cursor to specified position.
    """
    pydirectinput.move(diff_x, diff_y)

def mouse_move_to(offset: OffsetInWindow):
    """
    Move mouse cursor to specified relative position
    """
    pos = offset.to_position_in_screen()
    pydirectinput.moveTo(pos.x, pos.y)
