from dataclasses import dataclass

from PIL import ImageGrab

from .windowsapi import *

@dataclass(frozen=True)
class Color:
    red: int
    green: int
    blue: int

    def __str__(self):
        return f"#{self.to_int():06X}"

    def to_int(self) -> int:
        assert 0 <= self.red and self.red <= 0xff
        assert 0 <= self.green and self.green <= 0xff
        assert 0 <= self.blue and self.blue <= 0xff
        return (self.red << 16) | (self.green << 8) | self.blue

class Screenshot:
    def __init__(self):
        self.image = ImageGrab.grab(all_screens=True)
        self.screen_info = get_screen_info()
        self.window_info = get_active_window_info()

    def get_pixel(self, offset: OffsetInWindow) -> Color:
        offset_in_screen = offset.to_position_in_screen(window_info=self.window_info, screen_info=self.screen_info).to_offset_in_screen(screen_info=self.screen_info)
        color = self.image.getpixel((offset_in_screen.x, offset_in_screen.y))
        return Color(*color)

    def search_pixel(self, expected_color:Color, center: OffsetInWindow, width: int, height: int = 0) -> None | OffsetInWindow:
        if not height:
            height = width
        assert width > 0
        assert width % 2 == 0
        assert height > 0
        assert height % 2 == 0
        assert center.x >= width // 2
        assert center.y >= height // 2
        base = OffsetInWindow(center.x - width // 2, center.y - height // 2)
        for h in range(height):
            for w in range(width):
                offset2 = base.move(w, h)
                color = self.get_pixel(offset2)
                # print(f"get_pixel({offset2!r}): {color!s}")
                if color == expected_color:
                    return offset2

        return None

    def scan_pixel(self, expected_color:Color, base: OffsetInWindow, width: int, height: int = 0):
        if not height:
            height = width
        assert width > 0
        assert height > 0
        assert base.x >= 0
        assert base.y >= 0
        for h in range(height):
            for w in range(width):
                offset2 = base.move(w, h)
                color = self.get_pixel(offset2)
                if color == expected_color:
                    yield offset2
