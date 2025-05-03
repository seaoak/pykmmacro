from collections import namedtuple
from dataclasses import dataclass

from pynput import keyboard

from .keyboardinput import MODIFIER
from .utils import *

#=============================================================================
# Key mapping

# Refer to the `pynput` repository on GitHub
# https://github.com/moses-palmer/pynput/blob/master/lib/pynput/keyboard/_win32.py

_MODIFIER_KEY_DICT = {
    'LSHIFT': keyboard.Key.shift_l,
    'LCTRL': keyboard.Key.ctrl_l,
    'LALT': keyboard.Key.alt_l,
    'LWIN': keyboard.Key.cmd_l,

    'RSHIFT': keyboard.Key.shift_r,
    'RCTRL': keyboard.Key.ctrl_r,
    'RALT': keyboard.Key.alt_r,
    'RWIN': keyboard.Key.cmd_r,
}

_KEYCODE_TO_KEYNAME = dict(((keycode, keyname) for keyname, keycode in _MODIFIER_KEY_DICT.items()))

@dataclass(frozen=True)
class ModifierKey:
    keyname: str

for keyname in _MODIFIER_KEY_DICT.keys():
    setattr(ModifierKey, keyname, ModifierKey(keyname))

ModifierKey.__init__ = my_fail_always # disable constructor

#=============================================================================
# Public function

# truncate bits because Integer type has unlimited precision
_BITMASK_FOR_TRUNCATE = 0xffffffff

def setup_keyboard_listener():
    counter_for_listerner_thread = dict(((keyname, 0) for keyname in _MODIFIER_KEY_DICT.keys()))
    counter_for_main_thread = counter_for_listerner_thread.copy()

    def is_key_pressed_since_previous_call(key: ModifierKey) -> bool:
        keyname = key.keyname
        count = counter_for_listerner_thread[keyname] # capture the value at this timing
        is_updated = count != counter_for_main_thread[keyname]
        if is_updated:
            counter_for_main_thread[keyname] = count
        return is_updated

    def on_press(keycode):
        print(f"on_press: {keycode!r}")
        if keycode in _KEYCODE_TO_KEYNAME:
            keyname = _KEYCODE_TO_KEYNAME[keycode]
            counter_for_listerner_thread[keyname] = (counter_for_listerner_thread[keyname] + 1) & _BITMASK_FOR_TRUNCATE

    def on_release(keycode):
        print(f"on_release: {keycode!r}")

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)

    listener.start() # start new listener theread

    return is_key_pressed_since_previous_call
