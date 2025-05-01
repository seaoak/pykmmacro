from collections import namedtuple

import pydirectinput

from .utils import *

# for key name, refer to pydirectinput repository in GitHub
# https://github.com/learncodebygaming/pydirectinput/blob/master/pydirectinput/__init__.py

#=============================================================================
# Key mapping (for Japanese keyboard)

_MODIFIER_DICT = {
    'NONE':   (0x00),

    'SHIFT':  (0x01 << 0),
    'CTRL':   (0x01 << 1),
    'ALT':    (0x01 << 2),
    'WIN':    (0x01 << 3),

    'RSHIFT': (0x01 << 4),
    'RCTRL':  (0x01 << 5),
    'RALT':   (0x01 << 6),
    'RWIN':   (0x01 << 7),

    'LSHIFT': (0x01 << 0),
    'LCTRL':  (0x01 << 1),
    'LALT':   (0x01 << 2),
    'LWIN':   (0x01 << 3),
}

MODIFIER = namedtuple('Modifier', _MODIFIER_DICT.keys())(**_MODIFIER_DICT)

_MODIFIER_KEY_DICT = {
    'SHIFT': 'shiftleft',
    'CTRL': 'ctrlleft',
    'ALT': 'altleft',
    'WIN': 'winleft',

    'RSHIFT': 'shiftright',
    'RCTRL': 'ctrlright',
    'RALT': 'altright',
    'RWIN': 'winright',

    'LSHIFT': 'shiftleft',
    'LCTRL': 'ctrlleft',
    'LALT': 'altleft',
    'LWIN': 'winleft',
}

_MODIFIER_KEY = namedtuple("ModifierKey", _MODIFIER_KEY_DICT.keys())(**dict(((name, (name, value)) for name, value in _MODIFIER_KEY_DICT.items())))

_NORMAL_KEY_DICT = ({
    'CapsLock': 'capslock',
    'NumLock': 'numlock',

    # special keys
    'ESC': 'esc',
    'PrintScreen': 'printscreen',
    'ScrollLock': 'scrolllock',
    'Pause': 'pause',
    'Backspace': 'backspace',
    'Insert': 'insert',
    'Home': 'home',
    'PageUp': 'pageup',
    'PageDown': 'pagedown',
    'Tab': 'tab',
    'Delete': 'delete',
    'End': 'end',
    'Enter': 'enter',
    'Space': 'space',
    'Application': 'apps',
    'Up': 'up',
    'Left': 'left',
    'Down': 'down',
    'Right': 'right',

    # special keys for Japanese keyboard
    'Zenkaku': '`', # 0x29,
    'Henkan': 0x79,
    'Muhenkan': 0x7B,
    'Hiragana': 0x70,

    # symbols
    'Hyphen': '-', # 0x0C,
    'Hat': '=', # 0x0D,
    'YenSign': 0x7D,
    'Atmark': '[', # 0x1A,
    'LeftSquareBracket': ']', # 0x1B,
    'RightSquareBracket': '\\', # 0x2B,
    'Colon': "'", # 0x28,
    'Semicolon': ';', # 0x27,
    'Comma': ',', # 0x33,
    'Period': '.', # 0x34,
    'Slash': '/', # 0x35,
    'BackSlash': 0x73,

    # numbers
    'One':   '1',
    'Two':   '2',
    'Three': '3',
    'Four':  '4',
    'Five':  '5',
    'Six':   '6',
    'Seven': '7',
    'Eight': '8',
    'Nine':  '9',
    'Zero':  '0',

    # numpad
    'NUM_Multiply': 'multiply',
    'NUM_Plus': 'add',
    'NUM_Minus': 'subtract',
    'NUM_Devide': 'devide',
    'NUM_Period': 'decimal',
    'NUM_Enter': 'numpadenter',
    'NUM_1': 'numpad1',
    'NUM_2': 'numpad2',
    'NUM_3': 'numpad3',
    'NUM_4': 'numpad4',
    'NUM_5': 'numpad5',
    'NUM_6': 'numpad6',
    'NUM_7': 'numpad7',
    'NUM_8': 'numpad8',
    'NUM_9': 'numpad9',
    'NUM_0': 'numpad0',
}
    | dict(((f"F{i}", f"f{i}") for i in range(1, 12))) # function keys
    | dict(((chr(x), chr(ord('a')+x-ord('A'))) for x in range(ord('A'), ord('Z')))) # alphabets
    | dict(((chr(x), chr(x)) for x in range(ord('1'), ord('0')))) # numbers
)

NORMAL_KEY = namedtuple("NormalKey", _NORMAL_KEY_DICT.keys())(**dict(((name, (name, value)) for name, value in _NORMAL_KEY_DICT.items())))

_ALL_KEY_DICT = _MODIFIER_KEY_DICT | _NORMAL_KEY_DICT

#=============================================================================
# Shared variables

pending_keys = dict()

#=============================================================================
# Private functions

def _cleanup():
    keys = [key for key in pending_keys.keys()] # shallow copy
    for key in keys:
        _key_up(key)
    assert not pending_keys

def _key_down(key):
    name, keycode = key
    print(f"keyDown: {name}")
    assert name in _ALL_KEY_DICT
    assert keycode == _ALL_KEY_DICT[name]
    assert keycode in pydirectinput.KEYBOARD_MAPPING
    assert not (key in pending_keys)
    pending_keys[key] = True
    pydirectinput.keyDown(keycode)

def _key_up(key):
    name, keycode = key
    print(f"keyUp: {name}")
    assert name in _ALL_KEY_DICT
    assert keycode == _ALL_KEY_DICT[name]
    assert keycode in pydirectinput.KEYBOARD_MAPPING
    assert key in pending_keys
    pydirectinput.keyUp(keycode)
    del pending_keys[key]

#=============================================================================
# Public functions

def with_modifier_keys(func, modifier=MODIFIER.NONE, /):
    """
    Call `func` with pressing modifier keys.
    Modifier keys can be specified as a bitmap (use bit-OR to specify multiple modifier keys).
    """
    try:
        selected_keys = (name for name, bitmap in _MODIFIER_DICT.items() if modifier & bitmap and name.startswith(('L', 'R')))
        bitmap = 0
        for name in selected_keys:
            bitmap |= _MODIFIER_DICT[name]
            _key_down(getattr(_MODIFIER_KEY, name))
            my_sleep_a_moment()
        assert 0 == modifier & ~bitmap # ensure that undefined bit are not set
        func()
    finally:
        if pending_keys:
            my_sleep_a_moment()
            _cleanup()
            my_sleep_a_moment()

def key_press(key, modifier=MODIFIER.NONE, /):
    """
    Press key with modifier keys.
    Modifier keys can be specified as a bitmap (use bit-OR to specify multiple modifier keys).
    If you want to press a modifier key only, use `None` as `key` argument
    """
    def f():
        if key is None:
            return
        _key_down(key)
        my_sleep_a_moment()
        _key_up(key)
 
    with_modifier_keys(f, modifier)
