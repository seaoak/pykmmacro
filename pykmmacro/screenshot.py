from __future__ import annotations

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

    @classmethod
    def from_int(cls, value: int) -> Color:
        assert 0 <= value and value <= 0xffffff
        red =   (value >> 16) & 0xff
        green = (value >>  8) & 0xff
        blue  =  value        & 0xff
        return cls(red, green, blue)

    def to_int(self) -> int:
        assert 0 <= self.red and self.red <= 0xff
        assert 0 <= self.green and self.green <= 0xff
        assert 0 <= self.blue and self.blue <= 0xff
        return (self.red << 16) | (self.green << 8) | self.blue

class Screenshot:
    def __init__(self, *, all_screens: bool = False):
        self.screen_info = get_screen_info()
        self.window_info = get_active_window_info()
        self.is_all_screens = all_screens
        if self.is_all_screens:
            # screenshot of all screens is affected by "monitor fading" of DisplayFusion
            # (screnshot of specified window is not affected)
            self.image = ImageGrab.grab(all_screens=True)
            assert self.image.width == self.screen_info.width, (self.image.width, self.screen_info.width, self.image, self.screen_info)
            assert self.image.height == self.screen_info.height, (self.image.height, self.screen_info.height, self.image, self.screen_info)
        else:
            assert self.window_info.client.width > 0
            assert self.window_info.client.height > 0
            hwnd = self.window_info.hwnd
            assert hwnd
            self.image = ImageGrab.grab(window=hwnd)
            assert self.image.width == self.window_info.client.width, (self.image.width, self.window_info.client.width, self.image, self.window_info)
            assert self.image.height == self.window_info.client.height, (self.image.height, self.window_info.client.width, self.image, self.window_info)

    def get_pixel(self, offset: OffsetInWindow) -> Color:
        assert self.window_info.client.includes(offset), (offset, self.window_info.client, self.window_info)
        if self.is_all_screens:
            offset_in_screen = offset.to_position_in_screen(window_info=self.window_info, screen_info=self.screen_info).to_offset_in_screen(screen_info=self.screen_info)
            color = self.image.getpixel((*offset_in_screen,))
        else:
            color = self.image.getpixel((*offset,))
        assert isinstance(color, tuple)
        assert len(color) == 3 # for Windows ("4" for macOS because color is RGBA)
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
        base = center.move(-1 * width // 2, -1 * height // 2)
        for offset in self.scan_pixel(expected_color, base, width, height):
            return offset # return immediately at the first hit
        return None

    def scan_pixel(self, expected_color:Color, base: OffsetInWindow, width: int, height: int = 0, /, *, debug_print: bool = False):
        """
        Generate offsets in active window matched to expected color in specified region of active window.
        """
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
                if debug_print:
                    print(f"scan_pixel: {offset2.x}, {offset2.y} : {color!s}")
                if color == expected_color:
                    yield offset2
