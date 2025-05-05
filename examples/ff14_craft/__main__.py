from pykmmacro import *

#=============================================================================
# Constants

_EXPECTED_WINDOW_TITLE = "FINAL FANTASY XIV"

_TIMEOUT_MS_FOR_GENERAL = 2000

#=============================================================================
# Exception

class MyNotActiveWindowError(MyError):
    pass

class MyPixelNotFoundError(MyError):
    pass

#=============================================================================
# Abort if the title of active window is not matched to expected

def check_window_title(window_info=None):
    if window_info is None:
        window_info = get_active_window_info()
    if window_info.title != _EXPECTED_WINDOW_TITLE:
        raise MyNotActiveWindowError

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
                raise MyPixelNotFoundError(label)
            setattr(self, label, value)

    def __repr__(self):
        fields = ", ".join((f"{label}={getattr(self, label)}" for label in self.__dict__.keys() if label.startswith("is_")))
        return f"{__class__.__name__}({fields})"

    def is_busy(self) -> bool:
        return not self.is_bright_dig_icon_slot8_hotbar1

    def is_in_craft_mode(self) -> bool:
        return not self.is_bright_recepi_icon_slot3_hotbar1

    def is_in_input_mode(self) -> bool:
        return not self.is_visible_ime_icon

#=============================================================================
# Issue command

def g_issue_command(text: str):
    print(f"issue_command: {text!r}")
    assert text
    assert text.startswith('/')
    status = Status()
    assert not status.is_busy()
    assert not status.is_in_input_mode()
    copy_to_clipboard(text)
    key_press(NormalKey.Slash)
    yield from g_with_timeout_until(_TIMEOUT_MS_FOR_GENERAL, lambda: Status().is_in_input_mode())
    yield from g_sleep_to_ensure()
    key_press(NormalKey.Backspace)
    yield from g_sleep_a_moment()
    key_press(NormalKey.Backspace) # twice (just in case)
    yield from g_sleep_a_moment()
    key_press(NormalKey.V, MODIFIER.CTRL)
    yield from g_sleep_to_ensure()
    key_press(NormalKey.Enter)
    yield from g_with_timeout_while(_TIMEOUT_MS_FOR_GENERAL, lambda: (status := Status()).is_busy() or status.is_in_input_mode())
    copy_to_clipboard(f"{my_random()}") # overwrite clipboard by random text

#=============================================================================
# Executor

def run(generator):
    print(f"run: {generator.__name__}")
    for ret in generator:
        pass
    return ret

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
        my_sleep_ms(500)
    print("detect FF14 window")
    my_sleep_ms(1000)
    screen_info = get_screen_info()
    print(f"{screen_info=!r}")
    print(f"{window_info!r}")
    assert is_rect_intersect(window_info, screen_info.box)
    assert is_rect_intersect(window_info.client, window_info)
    assert not is_in_rect((100, 100), window_info)
    print("Move mouse cursor to topleft corner")
    mouse_move_to(OffsetInWindow(window_info.client.left, window_info.client.top))
    print("check pixel")
    status = Status()
    print(f"{status=!r}")
    run(g_issue_command("/bow"))
    print("finish")

main()
