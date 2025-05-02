import time

from . import *

def main():
    print("Hello world!")

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
        button = MOUSE_BUTTON.LEFT
        print(f"mouse_click: {button}")
        mouse_click(button)

    print("finish")

main()
