from typing import Callable, Final

from pynput import keyboard

from .modifier import MyModifier
from .utils import *

#=============================================================================
# Key mapping

# Refer to the `pynput` repository on GitHub
# https://github.com/moses-palmer/pynput/blob/master/lib/pynput/keyboard/_win32.py

_MODIFIER_KEY_DICT: Final[dict[str, keyboard.Key]] = {
    'LSHIFT': keyboard.Key.shift_l,
    'LCTRL': keyboard.Key.ctrl_l,
    'LALT': keyboard.Key.alt_l,
    'LWIN': keyboard.Key.cmd_l,

    'RSHIFT': keyboard.Key.shift_r,
    'RCTRL': keyboard.Key.ctrl_r,
    'RALT': keyboard.Key.alt_r,
    'RWIN': keyboard.Key.cmd_r,
}

_KEYCODE_TO_KEYNAME: Final[dict[keyboard.Key, str]] = dict(((keycode, keyname) for keyname, keycode in _MODIFIER_KEY_DICT.items()))

def _validate_dict():
    for modifier in MyModifier: # not include aliases (such as "SHIFT")
        assert modifier.keyname in _MODIFIER_KEY_DICT
    for keyname in _MODIFIER_KEY_DICT:
        assert MyModifier[keyname] # may raise 'KeyError' exception

if True:
    _validate_dict()

#=============================================================================
# Public function

# truncate bits because Integer type has unlimited precision
_BITMASK_FOR_TRUNCATE: Final[int] = 0xffffffff

def setup_keyboard_listener() -> Callable[[MyModifier], bool]:
    counter_for_listerner_thread: dict[str, int] = dict(((keyname, 0) for keyname in _MODIFIER_KEY_DICT.keys()))
    counter_for_main_thread = counter_for_listerner_thread.copy()

    def is_modifier_keys_pressed_since_previous_call(modifiers: MyModifier) -> bool:
        """Return True if at least one of specified modifiers are pressed"""
        assert modifiers # at least one modifier should be specified
        return any(is_key_pressed_since_previous_call(key) for key in modifiers)

    def is_key_pressed_since_previous_call(modifier: MyModifier) -> bool:
        assert 1 == len(modifier)
        keyname = modifier.keyname
        count = counter_for_listerner_thread[keyname] # capture the value at this timing
        is_updated = count != counter_for_main_thread[keyname]
        if is_updated:
            counter_for_main_thread[keyname] = count
        return is_updated

    def on_press(keycode: keyboard.Key | keyboard.KeyCode | None) -> None:
        # print(f"on_press: {keycode!r}")
        if keycode in _KEYCODE_TO_KEYNAME:
            keyname = _KEYCODE_TO_KEYNAME[keycode]
            counter_for_listerner_thread[keyname] = (counter_for_listerner_thread[keyname] + 1) & _BITMASK_FOR_TRUNCATE

    def on_release(keycode: keyboard.Key | keyboard.KeyCode | None):
        # print(f"on_release: {keycode!r}")
        return

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)

    listener.start() # start new listener theread

    return is_modifier_keys_pressed_since_previous_call
