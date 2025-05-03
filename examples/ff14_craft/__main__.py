from pykmmacro import *

#=============================================================================
# Exception

class NotActiveWindow(Exception):
    pass

class PixelNotFound(Exception):
    pass

#=============================================================================
# Abort if the title of active window is not matched to expected

_EXPECTED_WINDOW_TITLE = "FINAL FANTASY XIV"

def check_window_title(window_info=None):
    if window_info is None:
        window_info = get_active_window_info()
    if window_info.title != _EXPECTED_WINDOW_TITLE:
        raise NotActiveWindow

#=============================================================================
# check pixel

_DIFFERENCE_FROM_KMMACRO = (2565 - 2581, 2105 - 2167)

_TABLE_OF_PIXEL_COLOR = {
    'is_bright_dig_icon_slot8_hotbar1': [
        (OffsetInWindow(2581, 2167).move(*_DIFFERENCE_FROM_KMMACRO),    Color.from_int(0xFFFFE2), True),
        (OffsetInWindow(2581, 2167).move(*_DIFFERENCE_FROM_KMMACRO),    Color.from_int(0x7F7F71), False),
    ],
    'is_bright_recepi_icon_slot3_hotbar1': [
        (OffsetInWindow(2330, 2181).move(*_DIFFERENCE_FROM_KMMACRO),    Color.from_int(0x656765), True),
        (OffsetInWindow(2330, 2181).move(*_DIFFERENCE_FROM_KMMACRO),    Color.from_int(0x3B3C3B), False),
    ],
    'is_visible_ime_icon': [
        (OffsetInWindow(54, 2168).move(*_DIFFERENCE_FROM_KMMACRO),      Color.from_int(0xFFFFFF), True),
        (OffsetInWindow(54, 2168).move(*_DIFFERENCE_FROM_KMMACRO),      None,                     False),
    ],
}

class Status:
    def __init__(self):
        self.screenshot = Screenshot()
        check_window_title(self.screenshot.window_info)
        for label, table in _TABLE_OF_PIXEL_COLOR.items():
            value = None # default value when no match
            for offset, expected_color, meaning in table:
                assert not meaning is None
                if offset is None or expected_color is None:
                    value = meaning
                    break
                color = self.screenshot.get_pixel(offset)
                if color == expected_color:
                    value = meaning
                    break
            if value is None:
                raise PixelNotFound(label)
            setattr(self, label, value)

    def __repr__(self):
        fields = ", ".join((f"{label}={getattr(self, label)}" for label in self.__dict__.keys() if label.startswith("is_")))
        return f"{__class__.__name__}({fields})"

#=============================================================================
# Main

def main():
    print("start ff14_craft")
    print("activate FF14 window")
    if not activate_window(_EXPECTED_WINDOW_TITLE):
        print(f"ERROR: can not find FF14 window (title={_EXPECTED_WINDOW_TITLE!r})")
        return
    print("waiting for activating FF14 window")
    while (window_info := get_active_window_info()).title != _EXPECTED_WINDOW_TITLE:
        my_sleep(0.5)
    print("detect FF14 window")
    my_sleep(1)
    screen_info = get_screen_info()
    assert is_rect_intersect(window_info, screen_info.box)
    assert not is_in_rect((100, 100), window_info)
    print("Move mouse cursor to topleft corner")
    mouse_move_to(OffsetInWindow(window_info.client_left, window_info.client_top))
    print("check pixel")
    status = Status()
    print(f"{status=!r}")
    print("finish")

main()
