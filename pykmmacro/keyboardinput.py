import atexit
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
import sys
from typing import Any, Callable, Final

import pydirectinput

from .utils import *

# for key name, refer to pydirectinput repository in GitHub
# https://github.com/learncodebygaming/pydirectinput/blob/master/pydirectinput/__init__.py

#=============================================================================
# Key mapping (for Japanese keyboard)

_MODIFIER_DICT: Final[dict[str, int]] = {
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

MyModifier: Final = namedtuple('Modifier', _MODIFIER_DICT.keys())(**_MODIFIER_DICT)

@dataclass
class _BaseKeyMixin:
    # type enfocement for Enum
    _val: str | int

class AllKey(_BaseKeyMixin, Enum):
    @property
    def keyname(self) -> str:
        return self.name

    @property
    def keycode(self) -> str | int:
        return self._val

    def __hash__(self):
        return hash((self.__class__, self._val))

class _ModifierKey(AllKey):
    LSHIFT = 'shiftleft'
    LCTRL = 'ctrlleft'
    LALT = 'altleft'
    LWIN = 'winleft'

    RSHIFT = 'shiftright'
    RCTRL = 'ctrlright'
    RALT = 'altright'
    RWIN = 'winright'

    # aliases
    SHIFT = LSHIFT
    CTRL = LCTRL
    ALT = LALT
    WIN = LWIN

class NormalKey(AllKey):
    CapsLock = 'capslock'
    NumLock = 'numlock'

    # special keys
    ESC = 'esc'
    PrintScreen = 'printscreen'
    ScrollLock = 'scrolllock'
    Pause = 'pause'
    Backspace = 'backspace'
    Insert = 'insert'
    Home = 'home'
    PageUp = 'pageup'
    PageDown = 'pagedown'
    TAB = 'tab'
    Delete = 'delete'
    End = 'end'
    Enter = 'enter'
    Space = 'space'
    Application = 'apps'
    Up = 'up'
    Left = 'left'
    Down = 'down'
    Right = 'right'

    # special keys for Japanese keyboard
    Zenkaku = '`' # 0x29
    Henkan = 0x79
    Muhenkan = 0x7B
    Hiragana = 0x70

    # symbols
    Hyphen = '-' # 0x0C
    Hat = '=' # 0x0D
    YenSign = 0x7D
    Atmark = '[' # 0x1A
    LeftSquareBracket = ']' # 0x1B
    RightSquareBracket = '\\' # 0x2B
    Colon = "'" # 0x28
    Semicolon = ';' # 0x27
    Comma = ',' # 0x33
    Period = '.' # 0x34
    Slash = '/' # 0x35
    BackSlash = 0x73

    # numbers
    One =   '1'
    Two =   '2'
    Three = '3'
    Four =  '4'
    Five =  '5'
    Six =   '6'
    Seven = '7'
    Eight = '8'
    Nine =  '9'
    Zero =  '0'

    # numpad (ten-key)
    NUM_Multiply = 'multiply'
    NUM_Plus = 'add'
    NUM_Minus = 'subtract'
    NUM_Devide = 'devide'
    NUM_Period = 'decimal'
    NUM_Enter = 'numpadenter'
    NUM_1 = 'numpad1'
    NUM_2 = 'numpad2'
    NUM_3 = 'numpad3'
    NUM_4 = 'numpad4'
    NUM_5 = 'numpad5'
    NUM_6 = 'numpad6'
    NUM_7 = 'numpad7'
    NUM_8 = 'numpad8'
    NUM_9 = 'numpad9'
    NUM_0 = 'numpad0'

    # function keys
    F1 = 'f1'
    F2 = 'f2'
    F3 = 'f3'
    F4 = 'f4'
    F5 = 'f5'
    F6 = 'f6'
    F7 = 'f7'
    F8 = 'f8'
    F9 = 'f9'
    F10 = 'f10'
    F11 = 'f11'
    F12 = 'f12'

    # alphabet keys
    A = 'a'
    B = 'b'
    C = 'c'
    D = 'd'
    E = 'e'
    F = 'f'
    G = 'g'
    H = 'h'
    I = 'i'
    J = 'j'
    K = 'k'
    L = 'l'
    M = 'm'
    N = 'n'
    O = 'o'
    P = 'p'
    Q = 'q'
    R = 'r'
    S = 's'
    T = 't'
    U = 'u'
    V = 'v'
    W = 'w'
    X = 'x'
    Y = 'y'
    Z = 'z'

def _test_keys():
    def check_key(k: AllKey):
        print(f"{k=!r} / {k.name=!r} / {k.value=!r} / {k.keyname=!r} / {k.keycode=!r}")

    assert _ModifierKey.LSHIFT == _ModifierKey.SHIFT
    assert hash(_ModifierKey.LSHIFT) == hash(_ModifierKey.SHIFT)
    print(f"the number of symbols for modifier keys: {len(_ModifierKey.__members__)}")
    print(f"the number of modifier keys: {len(list(_ModifierKey))}")
    print(f"the number of normal keys: {len(list(NormalKey))}")
    for k in (NormalKey.F8, _ModifierKey.LSHIFT, _ModifierKey.SHIFT):
        check_key(k)
    sys.exit(1)

if False:
    _test_keys()

#=============================================================================
# Shared variables

_pending_keys: Final[set[AllKey]] = set()

_is_handler_at_exit_already_registered = False

#=============================================================================
# Private functions

def _handler_at_exit():
    if _pending_keys:
        print(f"handler_at_exit: release {len(_pending_keys)} keys")
    _cleanup()

def _cleanup() -> None:
    keys = [key for key in _pending_keys] # shallow copy because `_pending_keys` is modified in iteration
    for key in keys:
        _key_up(key)
    assert not _pending_keys

def _key_down(key: AllKey) -> None:
    global _is_handler_at_exit_already_registered
    # print(f"keyDown: {key.keyname}")
    if not _is_handler_at_exit_already_registered:
        _is_handler_at_exit_already_registered = True
        atexit.register(_handler_at_exit)
    assert key.keycode in pydirectinput.KEYBOARD_MAPPING
    assert key not in _pending_keys
    _pending_keys.add(key)
    pydirectinput.keyDown(key.keycode)

def _key_up(key: AllKey) -> None:
    # print(f"keyUp: {key.keyname}")
    assert key.keycode in pydirectinput.KEYBOARD_MAPPING
    assert key in _pending_keys
    pydirectinput.keyUp(key.keycode)
    _pending_keys.remove(key)

#=============================================================================
# Public functions

def with_modifier_keys(func: Callable[[], Any], modifier=MyModifier.NONE, /):
    """
    Call `func` with pressing modifier keys.
    Modifier keys can be specified as a bitmap (use bit-OR to specify multiple modifier keys).
    """
    try:
        selected_keys = (name for name, bitmap in _MODIFIER_DICT.items() if modifier & bitmap and name.startswith(('L', 'R')))
        bitmap = 0
        for name in selected_keys:
            bitmap |= _MODIFIER_DICT[name]
            _key_down(_ModifierKey[name])
            my_sleep_a_moment()
        assert 0 == modifier & ~bitmap # ensure that undefined bit are not set
        func()
    finally:
        if _pending_keys:
            my_sleep_a_moment()
            _cleanup()
            my_sleep_a_moment()

def key_press(key: NormalKey | None, modifier=MyModifier.NONE, /) -> None:
    """
    Press key with modifier keys.
    Modifier keys can be specified as a bitmap (use bit-OR to specify multiple modifier keys).
    If you want to press a modifier key only, use `None` as `key` argument
    """
    def f():
        if key is None:
            return
        _key_down(key)
        my_sleep_with_random(6, variation_ratio=2/6) # use specific period instead of `my_sleep_a_moment()` because max 9ms wait cause key repeat
        _key_up(key)

    if False:
        prefix = ''
        if modifier != 0:
            selected_keys = (name for name, bitmap in _MODIFIER_DICT.items() if modifier & bitmap and not name.startswith(('L', 'R')))
            prefix = ' + '.join(selected_keys) + ' + '
        keyname = key.keyname if key else "NOKEY"
        print(f"key_press: {prefix}{keyname}")

    with_modifier_keys(f, modifier)
