import os
from pathlib import Path, WindowsPath
import re
import sys
from typing import Any, Callable, Final, Generator, Iterable, NoReturn

from pykmmacro import *

#=============================================================================
# Constants

_EXPECTED_WINDOW_TITLE: Final = "FINAL FANTASY XIV"

_TIMEOUT_MS_FOR_GENERAL: Final = 10 * 1000

_REGEXP_FOR_ACTION_NAME: Final = re.compile(r"^[I\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+$")

#=============================================================================
# Exception

class MyNotActiveWindowError(MyError):
    pass

class MyPixelNotFoundError(MyError):
    pass

class MyRecipeEarlyFinishError(MyError):
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

_DIFFERENCE_FROM_KMMACRO: Final[tuple[int, int]] = (2565 - 2581, 2105 - 2167)

_TABLE_OF_PIXEL_COLOR: Final[dict[str, list[tuple[OffsetInWindow, Color | None, bool]]]] = {
    'is_bright_dig_icon_slot8_hotbar1': [
        (OffsetInWindow(2581, 2167).move(*_DIFFERENCE_FROM_KMMACRO),    Color.from_int(0xFFFFE2), True),
        (OffsetInWindow(2581, 2167).move(*_DIFFERENCE_FROM_KMMACRO),    Color.from_int(0x7F7F71), False),
    ],
    'is_bright_recipe_icon_slot3_hotbar1': [
        (OffsetInWindow(2330, 2181).move(*_DIFFERENCE_FROM_KMMACRO),    Color.from_int(0x656765), True),
        (OffsetInWindow(2330, 2181).move(*_DIFFERENCE_FROM_KMMACRO),    Color.from_int(0x3B3C3B), False),
    ],
    'is_visible_ime_icon': [
        (OffsetInWindow(54, 2168).move(*_DIFFERENCE_FROM_KMMACRO),      Color.from_int(0xFFFFFF), True),
        (OffsetInWindow(54, 2168).move(*_DIFFERENCE_FROM_KMMACRO),      None,                     False),
    ],
}

class Status:
    _screenshot: Screenshot
    _flags: dict[str, bool]

    def __init__(self):
        self._screenshot = Screenshot()
        self._flags = dict()
        check_window_title(self._screenshot.window_info)
        for label, table in _TABLE_OF_PIXEL_COLOR.items():
            value = None # default value when no match
            for offset, expected_color, meaning in table:
                assert not meaning is None
                if expected_color is None:
                    value = meaning
                    break
                color = self._screenshot.get_pixel(offset)
                if color == expected_color:
                    value = meaning
                    break
            if value is None:
                raise MyPixelNotFoundError(label)
            self._flags[label] = value

    def __repr__(self):
        fields = ", ".join((f"{label}={getattr(self, label)}" for label in self.__dict__.keys() if label.startswith("is_")))
        return f"{self.__class__.__name__}({fields})"

    def is_busy(self) -> bool:
        return not self._flags['is_bright_dig_icon_slot8_hotbar1']

    def is_in_craft_mode(self) -> bool:
        return not self._flags['is_bright_recipe_icon_slot3_hotbar1']

    def is_in_input_mode(self) -> bool:
        return not self._flags['is_visible_ime_icon']

#=============================================================================
# Proces a recipe

def g_issue_command(text: str) -> Generator[None]:
    print(f"issue_command: {text!r}")
    assert text
    assert text.startswith('/')
    text = text[1:] # remove slash at the first
    status = Status()
    assert not status.is_busy()
    assert status.is_in_craft_mode()
    assert not status.is_in_input_mode()
    copy_to_clipboard(text)
    key_press(NormalKey.Slash)
    yield from g_with_timeout_until(_TIMEOUT_MS_FOR_GENERAL, lambda: Status().is_in_input_mode())
    yield from g_sleep_a_moment()
    key_press(NormalKey.V, MyModifier.CTRL)
    yield from g_sleep_a_moment()
    key_press(NormalKey.Enter)
    yield from g_with_timeout_until(_TIMEOUT_MS_FOR_GENERAL, lambda: Status().is_busy())
    yield from g_with_timeout_while(_TIMEOUT_MS_FOR_GENERAL, lambda: Status().is_in_input_mode())
    copy_to_clipboard(f"{my_random()}") # overwrite clipboard by random text

def g_process_a_recipe(recipe: list[str]) -> Generator[None]:
    print(f"process a recipe ({len(recipe)} steps)")
    yield from g_sleep_with_random(1000, variation_ratio=0.0)
    key_press(NormalKey.NUM_0)
    yield from g_sleep_to_ensure()
    key_press(NormalKey.NUM_0)
    yield from g_sleep_to_ensure()
    yield from g_with_timeout_until(_TIMEOUT_MS_FOR_GENERAL, lambda: (status := Status()).is_in_craft_mode() and not status.is_busy())
    yield from g_sleep_to_ensure()
    assert not Status().is_in_input_mode()
    for skill_name in recipe:
        assert skill_name
        assert not skill_name.startswith('/')
        assert -1 == skill_name.find('+') # not supporeted yet
        if not Status().is_in_craft_mode():
            # early finish
            match skill_name:
                case '作業' | '下地作業' | '模範作業':
                    print(f"Recipe is finished early")
                    break
                case _:
                    raise MyRecipeEarlyFinishError(skill_name)
        command = f"/ac {skill_name}"
        yield from g_issue_command(command)
        yield from g_with_timeout_while(_TIMEOUT_MS_FOR_GENERAL, lambda: (status := Status()).is_busy() and status.is_in_craft_mode())
        yield from g_sleep_a_moment()
    g_with_timeout_while(_TIMEOUT_MS_FOR_GENERAL, lambda: Status().is_in_craft_mode())
    yield from g_sleep_to_ensure()
    assert Status().is_busy() # because keep sitting
    print("finish a recipe")

def parse_recipe_file(generator_for_lines: Iterable[str]) -> list[str]:
    def generator():
        is_skipping_header_part = True
        for line in generator_for_lines:
            line = line.strip(' \t\r\n')
            if is_skipping_header_part:
                if line == ";---DATA---":
                    is_skipping_header_part = False
                continue
            if not line:
                continue # skip an empty line
            if line.startswith(';'):
                continue # skip a comment line
            line = line.lstrip('/')
            assert -1 == line.find(' ')
            assert -1 == line.find('\t')
            assert -1 == line.find('　')
            assert _REGEXP_FOR_ACTION_NAME.match(line), f"Action name should be a string of I/Kanji/Hiragana/Katakana: {line}"
            yield line
    return [text for text in generator()] # make a real list to validate all lines in input

def g_process_a_recipe_file(path: Path, num_of_loop: int) -> Generator[None]:
    print(f"start processing a recipe file \"{path}\" at {my_get_str_timestamp()}")
    assert num_of_loop > 0
    assert path.suffix == '.MAC'
    def generator_for_lines() -> Generator[str]:
        with open(path, encoding='shiftjis') as f:
            yield from f
    recipe: list[str] = parse_recipe_file(generator_for_lines())

    key_press(NormalKey.Three, MyModifier.CTRL) # open craft menu
    yield from g_sleep(1*1000)
    yield from g_sleep_a_moment()
    key_press(NormalKey.NUM_0) # just in case (redundant NUM_0 key has no effect)
    yield from g_sleep_to_ensure()

    status = Status()
    assert not status.is_busy()
    assert not status.is_in_craft_mode()
    assert not status.is_in_input_mode()

    for i in range(num_of_loop):
        print(f"loop: {i+1} / {num_of_loop} ({num_of_loop - i - 1} remains) at {my_get_str_timestamp()}")
        yield from g_process_a_recipe(recipe)

    print(f"finish processing a recipe file \"{path}\" at {my_get_str_timestamp()}")

#=============================================================================
# Executor

def run(generator: Generator[None], callback_for_each_yield: Callable[[], Any]):
    for _ in generator:
        callback_for_each_yield()

#=============================================================================
# Main

def crate_callback_func():
    key_for_abort = MyModifier.LSHIFT
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
    print(f"Usage: python -m {__package__} macro-file num-of-loop")
    sys.exit(1)

def g_main() -> Generator[None]:
    print(f"start ff14_craft at {my_get_str_timestamp()}")

    args = sys.argv
    print(f"{args=!r}")
    if len(args) != 3:
        usage(args)
    _, arg_path, arg_num_of_loop = args
    if not arg_path or not arg_num_of_loop:
        usage(args)
    try:
        num_of_loop = int(arg_num_of_loop)
        assert f"{num_of_loop}" == arg_num_of_loop
        assert num_of_loop > 0
    except Exception:
        print(f"ERROR: second argument should be an positive integer: \"{arg_num_of_loop}\"")
        usage(args)
    path = WindowsPath(arg_path)
    if not path.exists():
        print(f"ERROR: file not fould: \"{path}\"")
        sys.exit(1)
    stat = os.stat(path)
    if stat.st_mode & 0o400 == 0:
        print(f"ERROR: permission error: \"{path}\"")
        sys.exit(1)

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
    assert window_info.is_intersect(screen_info) # the window should be displayed at least partially
    assert not window_info.includes(MyPosition(100, 100))

    print("Move mouse cursor to topleft corner")
    mouse_move_to(OffsetInWindow(window_info.client.left, window_info.client.top))

    status = Status()
    print(f"{status=!r}")
    assert not status.is_busy()
    assert not status.is_in_craft_mode()
    assert not status.is_in_input_mode()

    yield from g_process_a_recipe_file(path, num_of_loop)

    print("finish")
    show_dialog(f"PyKMmacro: finish at {my_get_str_timestamp()}")

def main():
    callback_for_each_yield = crate_callback_func()
    try:
        run(g_main(), callback_for_each_yield)
    except Exception as ex:
        # show diaglog to change FF14 window from foreground to background
        show_dialog(f"ERROR: {ex!r}")
        raise ex

main()
