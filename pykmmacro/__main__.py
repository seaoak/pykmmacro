import time

from . import *

def main():
    print("Hello world!")

    if False:
        target_key = ModifierKey.LSHIFT
        print("setup keyboard listener")
        is_pressed = setup_keyboard_listener()
        print(f"waiting for {target_key.keyname} key")
        for count in range(10):
            while not is_pressed(target_key):
                my_sleep_a_moment()
            print(f"detect {target_key.keyname} key ({count=})")
        print("finish")
        return

    print("sleep 3 sec")
    time.sleep(3)

    if True:
        screen_info = get_screen_info()
        print(f"{screen_info.size=!r}")
        window_info = get_active_window_info()
        print(f"{window_info=!r}")

        offset_in_window = OffsetInWindow(111, 222)
        print(f"{offset_in_window=!r}")
        pos = offset_in_window.to_position_in_screen()
        print(f"{pos=!r}")
        assert offset_in_window == pos.to_offset_in_client_region_of_active_window()
        offset_in_screen = pos.to_offset_in_screen()
        print(f"{offset_in_screen=!r}")

        print(f"{offset_in_window.move(3, 5)!r}")
        print(f"{pos.move(7, 11)}")
        print(f"{offset_in_screen.move(13, 17)}")

    if True:
        print("take screenshot")
        diff_x = 2565 - 2581 # difference from getpixel of KMmacro
        diff_y = 2105 - 2167 # difference from getpixel of KMmacro
        screenshot = Screenshot()
        window_info = screenshot.window_info
        if window_info.title != "FINAL FANTASY XIV":
            print(f"unexpected window title: {window_info.title!r}")
            return
        for expected_color, offset in ((Color(0xff, 0xff, 0xe2), OffsetInWindow(2581, 2167)), (Color(0x65, 0x67, 0x65), OffsetInWindow(2330, 2181))):
            offset = offset.move(diff_x, diff_y)
            color = screenshot.get_pixel(offset)
            print(f"get_pixel({offset!r}): {color!s}")
            width = 32
            offset2 = screenshot.search_pixel(expected_color, offset, width)
            print(f"search_pixel({expected_color!s}, {offset!r}, {width}): {offset2!r}")
            base = OffsetInWindow(window_info.client_left, window_info.client_top)
            for i, offset2 in enumerate(screenshot.scan_pixel(expected_color, base, window_info.client_width, window_info.client_height)):
                print(f"scan_pixel({expected_color!s})[{i}]: {offset2!r}")
        return

    if False:
        print("sleep 3 sec")
        time.sleep(3)

        print("press 'A'")
        key_press(NORMAL_KEY.A)

        print("press ']'")
        key_press(NORMAL_KEY.RightSquareBracket)

        print("press 'NUM*'")
        key_press(NORMAL_KEY.NUM_Multiply)

        print("press '1' with SHIFT key")
        key_press(NORMAL_KEY.One, MODIFIER.SHIFT)

        print("press Ctrl+Shift+O")
        key_press(NORMAL_KEY.O, MODIFIER.CTRL | MODIFIER.SHIFT)

    if get_active_window_info().title == "FINAL FANTASY XIV":
        pos = get_mouse_position()
        print(f"{pos=!r}")

        # click "Dig" icon at the slot 8 of hotbar 1
        pos = PositionInScreen(-1267, 2535)
        offset = pos.to_offset_in_client_region_of_active_window()
        print(f"mouse_move_to: {offset=!r}")
        mouse_move_to(offset)
        my_sleep_a_moment()
        diff = (-8, -31)
        print(f"mouse_move_relative: {diff=!r}")
        mouse_move_relative(*diff)
        my_sleep_a_moment()
        pos = get_mouse_position().to_offset_in_client_region_of_active_window()
        print(f"{pos=!r}")
        button = MOUSE_BUTTON.LEFT
        print(f"mouse_click: {button}")
        mouse_click(button)

    print("finish")

main()
