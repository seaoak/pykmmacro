from collections import namedtuple
from dataclasses import dataclass

import win32api
import win32gui

from .utils import *

#=============================================================================
# Declaration

class PositionInScreen:
    pass

class OffsetInWindow:
    pass

class OffsetInScreen:
    pass

#=============================================================================
# Private function

def _get_client_rect(hwnd):
    """get client area of active window"""
    # https://mhammond.github.io/pywin32/win32gui__GetClientRect_meth.html
    rect = win32gui.GetClientRect(hwnd)
    rect = dict(zip(("left", "top", "right", "bottom"), rect))
    rect["width"] = rect["right"] - rect["left"]
    rect["height"] = rect["bottom"] - rect["top"]
    rect = namedtuple("ClientRect", rect.keys())(**rect)
    return rect

def _get_window_rect(hwnd):
    """get the whole area of active window (include MENU and BORDER)"""
    # https://mhammond.github.io/pywin32/win32gui__GetWindowRect_meth.html
    rect = win32gui.GetWindowRect(hwnd)
    rect = dict(zip(("left", "top", "right", "bottom"), rect))
    rect["width"] = rect["right"] - rect["left"]
    rect["height"] = rect["bottom"] - rect["top"]
    rect = namedtuple("WindowRect", rect.keys())(**rect)
    return rect

def _get_window_title(hwnd):
    """get the title of active window"""
    # https://mhammond.github.io/pywin32/win32gui__GetWindowText_meth.html
    title = win32gui.GetWindowText(hwnd)
    return title

def _get_all_display_info():
    # https://qiita.com/kznSk2/items/1c756eb4bee80c66233d
    # https://mhammond.github.io/pywin32/win32api.html
    monitors = win32api.EnumDisplayMonitors()
    #print(f"{monitors=!r}")
    infos = []
    for monitor in monitors:
        (hMonitor, hdcMonitor, PyRECT) = monitor
        info = win32api.GetMonitorInfo(hMonitor)
        #print(f"{info=!r}")
        table = {
            "top":        info["Monitor"][1],
            "right":      info["Monitor"][2],
            "bottom":     info["Monitor"][3],
            "left":       info["Monitor"][0],
            "width":      info["Monitor"][2] - info["Monitor"][0],
            "height":     info["Monitor"][3] - info["Monitor"][1],
            "is_primary": info["Flags"] == 1,
            "name":       info["Device"],
        }
        table = namedtuple("MonitorInfo", table.keys())(**table)
        infos.append(table)

    return infos

def _convert_position_in_screen_to_offset_in_screen(pos: PositionInScreen, /, *, screen_info=None) -> OffsetInScreen:
    """
    Convert `pos` to offset in screen.
    `pos` should be in client region of active window.
    And also `pos` should be in screen (active window may be beyond screen edge)
    """
    if screen_info is None:
        screen_info = get_screen_info()
    offset_x = screen_info.origin.x + pos.x
    offset_y = screen_info.origin.y + pos.y
    assert offset_x >= 0
    assert offset_y >= 0
    assert offset_x < screen_info.size.width
    assert offset_y < screen_info.size.height
    return OffsetInScreen(offset_x, offset_y)

def _convert_position_in_screen_to_offset_in_client_region_of_active_window(pos: PositionInScreen, /, *, window_info=None, screen_info=None) -> OffsetInWindow:
    """
    Convert `pos` to offset in client region of active window.
    `pos` should be in client region of active window.
    And also `pos` should be in screen (active window may be beyond screen edge)
    """
    if True:
        if screen_info is None:
            screen_info = get_screen_info()
        assert pos.x >= screen_info.box.left
        assert pos.x < screen_info.box.right
        assert pos.y >= screen_info.box.top
        assert pos.y < screen_info.box.bottom

    if window_info is None:
        window_info = get_active_window_info()
    assert pos.x >= window_info.left + window_info.padding_left
    assert pos.x < window_info.right - window_info.padding_right
    assert pos.y >= window_info.top + window_info.padding_top
    assert pos.y < window_info.bottom - window_info.padding_bottom
    offset_x = pos.x - window_info.left - window_info.padding_left
    offset_y = pos.y - window_info.top - window_info.padding_top
    assert offset_x >= 0
    assert offset_y >= 0
    assert offset_x < window_info.width - window_info.padding_right - window_info.padding_left
    assert offset_y < window_info.height - window_info.padding_top - window_info.padding_bottom
    return OffsetInWindow(offset_x, offset_y)

def _convert_offset_in_screen_to_position_in_screen(offset: OffsetInScreen, /, *, screen_info=None) -> PositionInScreen:
    if screen_info is None:
        screen_info = get_screen_info()
    assert offset.x >= 0
    assert offset.y >= 0
    assert offset.x < screen_info.size.width
    assert offset.y < screen_info.size.height
    x = offset.x - screen_info.origin.x
    y = offset.y - screen_info.origin.y
    assert x >= screen_info.box.left
    assert x < screen_info.box.right
    assert y >= screen_info.box.top
    assert y < screen_info.box.bottom
    return PositionInScreen(x, y)

def _convert_offset_in_client_region_of_active_window_to_position_in_screen(offset: OffsetInWindow, /, *, window_info=None, screen_info=None) -> PositionInScreen:
    """
    Convert `offset` to position in screen.
    `offset` should be in client region of active window.
    And also `offset` should be in screen (active window may be beyond screen edge)
    """
    if window_info is None:
        window_info = get_active_window_info()
    assert offset.x >= 0
    assert offset.y >= 0
    assert offset.x < window_info.width - window_info.padding_right - window_info.padding_left
    assert offset.y < window_info.height - window_info.padding_top - window_info.padding_bottom
    x = window_info.left + window_info.padding_left + offset.x
    y = window_info.top + window_info.padding_top + offset.y
    if True:
        if screen_info is None:
            screen_info = get_screen_info()
        assert x >= screen_info.box.left
        assert x < screen_info.box.right
        assert y >= screen_info.box.top
        assert y < screen_info.box.bottom
    return PositionInScreen(x, y)

#=============================================================================
# Public class

@dataclass(frozen=True)
class PositionInScreen:
    """
    Represent position in screen
    """

    x: int
    y: int

    def __str__(self):
        return f"{__class__.__name__}({self.x}, {self.y})"

    def move(self, diff_x, diff_y) -> PositionInScreen:
        return PositionInScreen(self.x + diff_x, self.y + diff_y)

    def to_offset_in_screen(self, /, *, screen_info=None) -> OffsetInScreen:
        return _convert_position_in_screen_to_offset_in_screen(self, screen_info=screen_info)
    
    def to_offset_in_client_region_of_active_window(self, /, *, window_info=None, screen_info=None) -> OffsetInWindow:
        return _convert_position_in_screen_to_offset_in_client_region_of_active_window(self, window_info=window_info, screen_info=screen_info)

@dataclass(frozen=True)
class OffsetInScreen:
    """
    Represent offset in screen.
    This can be used for offset in screenshot of whole desktop.
    """

    x: int
    y: int

    def __str__(self):
        return f"{__class__.__name__}({self.x}, {self.y})"

    def move(self, diff_x, diff_y) -> OffsetInScreen:
        return OffsetInScreen(self.x + diff_x, self.y + diff_y)

    def to_position_in_screen(self, /, *, screen_info=None) -> PositionInScreen:
        return _convert_offset_in_screen_to_position_in_screen(self, screen_info=screen_info)

@dataclass(frozen=True)
class OffsetInWindow:
    """
    Represent offset in client area of active window
    """

    x: int
    y: int

    def __str__(self):
        return f"{__class__.__name__}({self.x}, {self.y})"
    
    def move(self, diff_x, diff_y) -> OffsetInWindow:
        return OffsetInWindow(self.x + diff_x, self.y + diff_y)

    def to_position_in_screen(self, /, *, window_info=None, screen_info=None) -> PositionInScreen:
        return _convert_offset_in_client_region_of_active_window_to_position_in_screen(self, window_info=window_info, screen_info=screen_info)

#=============================================================================
# Public function

def get_active_window_info():
    # https://github.com/asweigart/PyGetWindow/blob/master/src/pygetwindow/_pygetwindow_win.py
    hwnd = win32gui.GetForegroundWindow()
    assert hwnd != 0
    client_rect = _get_client_rect(hwnd)
    window_rect = _get_window_rect(hwnd)
    title = _get_window_title(hwnd)

    diff_x = window_rect.width - client_rect.width - client_rect.left
    assert diff_x >= 0, (window_rect.width, client_rect.width, client_rect.left)
    assert diff_x % 2 == 0
    padding_width = diff_x // 2 # may be zero
    diff_y = window_rect.height - client_rect.height - client_rect.top
    assert diff_y >= padding_width # padding_top may be zero

    info = {
        "title":  title,
        "top":    window_rect.top,
        "right":  window_rect.right,
        "bottom": window_rect.bottom,
        "left":   window_rect.left,
        "width":  window_rect.width,
        "height": window_rect.height,
        "padding_top":    diff_y - padding_width,
        "padding_right":  padding_width,
        "padding_bottom": padding_width,
        "padding_left":   padding_width,
        "client_top":    client_rect.top,
        "client_right":  client_rect.right,
        "client_bottom": client_rect.bottom,
        "client_left":   client_rect.left,
        "client_width":  client_rect.width,
        "client_height": client_rect.height,
    }
    info = namedtuple("WindowInfo", info.keys())(**info)
    #print(f"{info=}")
    return info

def get_screen_info():
    monitors = _get_all_display_info()
    origin = {
        "x": -1 * min(monitor.left for monitor in monitors),
        "y": -1 * min(monitor.top for monitor in monitors),
    }
    origin = namedtuple("ScreenOrigin", origin.keys())(**origin)
    assert origin.x >= 0
    assert origin.y >= 0
    size = {
        "width":  max(monitor.right for monitor in monitors) - min(monitor.left for monitor in monitors),
        "height": max(monitor.bottom for monitor in monitors) - min(monitor.top for monitor in monitors),
    }
    size = namedtuple("ScreenSize", size.keys())(**size)
    assert size.width > 0
    assert size.height > 0
    box = {
        "top":    min(monitor.top for monitor in monitors),
        "right":  max(monitor.right for monitor in monitors),
        "bottom": max(monitor.bottom for monitor in monitors),
        "left":   min(monitor.left for monitor in monitors),
    }
    box = namedtuple("ScreenBox", box.keys())(**box)
    assert box.top <= 0
    assert box.right > 0
    assert box.bottom > 0
    assert box.left <= 0
    result = {
        "origin":   origin,
        "size":     size,
        "box":      box,
        "monitors": monitors,
    }
    result = namedtuple("ScreenInfo", result.keys())(**result)
    #print(result)
    return result

def show_dialog(text: str) -> None:
    win32gui.MessageBox(None, text, "PyKMmacro Dialog", 1)
