from typing import Callable, Final

from pynput import keyboard

from .modifier import MyModifier
from .utils import *

#=============================================================================
# Key mapping

# Refer to the `pynput` repository on GitHub
# https://github.com/moses-palmer/pynput/blob/master/lib/pynput/keyboard/_win32.py

_MODIFIER_KEY_DICT: Final[dict[MyModifier, keyboard.Key]] = {
    MyModifier.LSHIFT: keyboard.Key.shift_l,
    MyModifier.LCTRL: keyboard.Key.ctrl_l,
    MyModifier.LALT: keyboard.Key.alt_l,
    MyModifier.LWIN: keyboard.Key.cmd_l,

    MyModifier.RSHIFT: keyboard.Key.shift_r,
    MyModifier.RCTRL: keyboard.Key.ctrl_r,
    MyModifier.RALT: keyboard.Key.alt_r,
    MyModifier.RWIN: keyboard.Key.cmd_r,
}

def _validate_dict():
    for modifier in MyModifier: # not include aliases (such as "SHIFT")
        assert modifier in _MODIFIER_KEY_DICT

if True:
    _validate_dict()

#=============================================================================
# Public function

# truncate bits because Integer type has unlimited precision
_BITMASK_FOR_TRUNCATE: Final[int] = 0xffffffff

def setup_keyboard_listener() -> Callable[[MyModifier], bool]:
    counter_for_listerner_thread: dict[keyboard.Key, int] = dict(((key, 0) for key in _MODIFIER_KEY_DICT.values()))
    counter_for_main_thread = counter_for_listerner_thread.copy()

    def is_modifier_keys_pressed_since_previous_call(modifiers: MyModifier) -> bool:
        """Return True if at least one of specified modifiers are pressed"""
        assert modifiers # at least one modifier should be specified
        return any(is_key_pressed_since_previous_call(key) for key in modifiers)

    def is_key_pressed_since_previous_call(modifier: MyModifier) -> bool:
        assert 1 == len(modifier)
        key = _MODIFIER_KEY_DICT[modifier]
        count = counter_for_listerner_thread[key] # capture the value at this timing
        is_updated = count != counter_for_main_thread[key]
        if is_updated:
            counter_for_main_thread[key] = count
        return is_updated

    def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
        # print(f"on_press: {key!r}")
        if key in counter_for_listerner_thread:
            counter_for_listerner_thread[key] = (counter_for_listerner_thread[key] + 1) & _BITMASK_FOR_TRUNCATE

    def on_release(key: keyboard.Key | keyboard.KeyCode | None):
        # print(f"on_release: {key!r}")
        return

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)

    listener.start() # start new listener theread

    return is_modifier_keys_pressed_since_previous_call
