import sys
from typing import Any, Callable, Final, Generator, Iterable, NoReturn

from pykmmacro import *

#=============================================================================
# Constants

_EXPECTED_WINDOW_TITLE: Final = "FINAL FANTASY XIV"

_TIMEOUT_MS_FOR_GENERAL: Final = 10 * 1000

#=============================================================================
# Exception

class MyNotActiveWindowError(MyError):
    pass

class MyPixelNotFoundError(MyError):
    pass

class MyRecipeEarlyFinishError(MyError):
    pass

#=============================================================================
# check pixel

_TABLE_OF_PIXEL_COLOR: Final[dict[str, list[tuple[OffsetInWindow | None, Color | None, bool]]]] = {
    'is_green_check_displayed': [
        (OffsetInWindow(979, 234),  Color.from_int(0x91E4A8), True),
        (None,                      None,                     False),
    ],
}

class Status:
    def __init__(self):
        self.screenshot = Screenshot()
        for label, table in _TABLE_OF_PIXEL_COLOR.items():
            value = None # default value when no match
            for offset, expected_color, meaning in table:
                assert not meaning is None
                if offset is None or expected_color is None:
                    value = meaning
                    break
                if False:
                    width = 256
                    base = offset.move(-1 * width // 2, -1 * width // 2)
                    print(f"scan for GREEN checkmask: {expected_color=!s} {offset=!r} {base=!r} {width=}")
                    for offset2 in self.screenshot.scan_pixel(expected_color, base, width, debug_print=False):
                        print(f"detected: {offset2!r}")
                color = self.screenshot.get_pixel(offset)
                if color == expected_color:
                    value = meaning
                    break
            if value is None:
                raise MyPixelNotFoundError(label)
            setattr(self, label, value)

    def __repr__(self):
        fields = ", ".join((f"{label}={getattr(self, label)}" for label in self.__dict__.keys() if label.startswith("is_")))
        return f"{self.__class__.__name__}({fields})"

    def is_already_completed(self) -> bool:
        return self.is_green_check_displayed

#=============================================================================
# Executor

def run(generator: Generator[None], callback_for_each_yield: Callable[[], Any]):
    for _ in generator:
        callback_for_each_yield()

#=============================================================================
# Main

def crate_callback_func():
    key_for_abort = ModifierKey.LSHIFT
    is_key_pressed_since_previous_call = setup_keyboard_listener()
    is_key_pressed_since_previous_call(key_for_abort) # call once in advance to clear status

    hwnd = 0

    def callback_func():
        nonlocal hwnd
        if is_key_pressed_since_previous_call(key_for_abort):
            print("Aborted by SHIFT key")
            sys.exit(3)
        window_info = get_active_window_info()
        if hwnd == 0 and window_info.title == _EXPECTED_WINDOW_TITLE:
            hwnd = window_info.hwnd
        elif hwnd != 0 and window_info.hwnd != hwnd:
            print("Aborted because the active window was changed")
            sys.exit(4)

    return callback_func

def usage(_args: Iterable[str]) -> NoReturn:
    print(f"Usage: python -m {__package__} num-of-loop")
    sys.exit(1)

def get_package_basename():
    assert __package__
    _, _, basename = __package__.rpartition('.')
    return basename

def g_main() -> Generator[None]:
    print(f"{get_package_basename()}: start at {my_get_str_timestamp()}")

    args: Final = sys.argv
    print(f"{args=!r}")
    if len(args) != 2:
        usage(args)
    _, arg_num_of_loop = args
    if not arg_num_of_loop:
        usage(args)
    try:
        num_of_loop = int(arg_num_of_loop)
        assert f"{num_of_loop}" == arg_num_of_loop
        assert num_of_loop > 0
    except Exception:
        print(f"ERROR: first argument should be an positive integer: \"{arg_num_of_loop}\"")
        usage(args)

    print("activate FF14 window")
    if not activate_window(_EXPECTED_WINDOW_TITLE):
        print(f"ERROR: can not find FF14 window (title={_EXPECTED_WINDOW_TITLE!r})")
        return
    print("waiting for activating FF14 window")
    while (window_info := get_active_window_info()).title != _EXPECTED_WINDOW_TITLE:
        yield from g_sleep(500)
    print("detect FF14 window")
    yield from g_sleep(1000)
    screen_info = get_screen_info()
    print(f"{screen_info=!r}")
    print(f"{window_info!r}")
    assert window_info.is_intersect(screen_info)
    assert window_info.client.is_intersect(window_info)
    assert not window_info.includes(MyPosition(100, 100))

    get_position_of_latest_click: Final = setup_mouse_listener()

    _ = get_position_of_latest_click() # discard old input
    print("waiting for clicking 1st NPC")
    while (pos1 := get_position_of_latest_click()) is None:
        yield from g_sleep_a_moment()
    offset1: Final = pos1.to_offset_in_client_region_of_active_window()
    print(f"detect 1st click at {pos1=!r} as {offset1=!r}")

    _ = get_position_of_latest_click() # discard old input
    print("waiting for 2nd NPC")
    while (pos2 := get_position_of_latest_click()) is None:
        yield from g_sleep_a_moment()
    offset2: Final = pos2.to_offset_in_client_region_of_active_window()
    print(f"detect 2nd click at {pos2=!r} as {offset2=!r}")

    yield from g_sleep(3 * 1000)

    for i in range(num_of_loop):
        yield from g_sleep(1*1000)
        yield from g_sleep_a_moment()

        print(f"start nouhin: {i+1} / {num_of_loop}")

        print(f"click 1st NPC: {offset1=!r}")
        mouse_move_to(offset1)
        yield from g_sleep_a_moment()
        mouse_click()
        yield from g_sleep_to_ensure()

        key_press(NormalKey.NUM_0)
        yield from g_sleep(1*1000) # wait for window open
        yield from g_sleep_a_moment()

        print("skip a message")
        key_press(NormalKey.NUM_0)
        yield from g_sleep_to_ensure()

        print("select menu item for crafters")
        key_press(NormalKey.NUM_2) # "Down"
        yield from g_sleep_to_ensure()
        key_press(NormalKey.NUM_0)
        yield from g_sleep(1*1000) # wait for window open
        yield from g_sleep_to_ensure()

        print("select Level 84")
        for _ in range(3):
            key_press(NormalKey.NUM_8) # "Up"
            yield from g_sleep_to_ensure()
        for _ in range(2):
            key_press(NormalKey.NUM_0)
            yield from g_sleep_to_ensure()

        if not Status().is_already_completed():
            key_press(NormalKey.NUM_2) # "Down"
            yield from g_sleep_to_ensure()
            key_press(NormalKey.NUM_0)
            yield from g_sleep_to_ensure()

        if not Status().is_already_completed():
            print("ERROR: can not find GREEN checkmark")
            return

        print("accept current item")
        key_press(NormalKey.NUM_0)
        yield from g_sleep_to_ensure()
        key_press(NormalKey.NUM_0)
        yield from g_sleep_to_ensure()
        key_press(NormalKey.ESC)
        yield from g_sleep_to_ensure()
        key_press(NormalKey.ESC)
        yield from g_sleep_to_ensure()

        print(f"click 2st NPC: {offset2=!r}")
        mouse_move_to(offset2)
        yield from g_sleep_a_moment()
        mouse_click()

        key_press(NormalKey.NUM_0)
        yield from g_sleep(1*1000) # wait for window open
        yield from g_sleep_a_moment()

        print("skip a message")
        key_press(NormalKey.NUM_0)
        yield from g_sleep_to_ensure()

        print("select nouhin item")
        key_press(NormalKey.TAB)
        yield from g_sleep_to_ensure()
        for _ in range(6):
            key_press(NormalKey.NUM_0)
            yield from g_sleep_to_ensure()

        print(f"finish nouhin: {i+1} / {num_of_loop}")

    print(f"{get_package_basename()}: completed at {my_get_str_timestamp()}")
    show_dialog(f"{get_package_basename()}: completed at {my_get_str_timestamp()}")

def main():
    callback_for_each_yield = crate_callback_func()
    run(g_main(), callback_for_each_yield)

main()
