from enum import Flag, auto
import sys

class MyModifier(Flag):
    NONE = 0

    LSHIFT = auto()
    LCTRL = auto()
    LALT = auto()
    LWIN = auto()

    RSHIFT = auto()
    RCTRL = auto()
    RALT = auto()
    RWIN = auto()

    # aliases
    SHIFT = LSHIFT
    CTRL = LCTRL
    ALT = LALT
    WIN = LWIN

    @property
    def keyname(self) -> str:
        assert 1 == len(self)
        assert self.name
        return self.name

def _test_modifier():
    assert MyModifier.SHIFT.keyname == "LSHIFT"
    assert MyModifier.SHIFT == MyModifier.LSHIFT
    assert hash(MyModifier.SHIFT) == hash(MyModifier.LSHIFT)
    assert not MyModifier.SHIFT & MyModifier.NONE
    assert MyModifier.SHIFT | MyModifier.NONE == MyModifier.LSHIFT
    print("OK")
    sys.exit(1)

if False:
    _test_modifier()
