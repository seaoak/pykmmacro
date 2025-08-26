from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import win32api
import win32gui

from .utils import *

#=============================================================================
# Definition

_TIMEOUT_MS_FOR_WINDOW_SWITCH: Final[int] = 500

class TimeoutForWindowSwitch(Exception):
    pass

#=============================================================================
# Private function

def _restore_window(hwnd: int):
    """
    Restore a window from maxmized/minimized.
    """
    # https://github.com/asweigart/PyGetWindow/blob/master/src/pygetwindow/_pygetwindow_win.py#L230-L232
    assert hwnd != 0
    cmdShow = 0x9
    win32gui.ShowWindow(hwnd, cmdShow)

def _get_hwnd_of_active_window() -> int:
    return win32gui.GetForegroundWindow() # may be zero

def _get_client_rect(hwnd: int) -> MyRect:
    """get client area of active window"""
    # https://mhammond.github.io/pywin32/win32gui__GetClientRect_meth.html
    assert hwnd != 0
    t = win32gui.GetClientRect(hwnd)
    rect = dict(zip(("left", "top", "right", "bottom"), t))
    return MyRect(**rect)

def _get_window_rect(hwnd: int) -> MyRect:
    """get the whole area of active window (include MENU and BORDER)"""
    # https://mhammond.github.io/pywin32/win32gui__GetWindowRect_meth.html
    assert hwnd != 0
    t = win32gui.GetWindowRect(hwnd)
    rect = dict(zip(("left", "top", "right", "bottom"), t))
    return MyRect(**rect)

def _get_window_title(hwnd: int) -> str:
    """get the title of active window"""
    # https://mhammond.github.io/pywin32/win32gui__GetWindowText_meth.html
    assert hwnd != 0
    title = win32gui.GetWindowText(hwnd)
    return title

def _get_all_monitor_info() -> list[MyMonitorInfo]:
    # https://qiita.com/kznSk2/items/1c756eb4bee80c66233d
    # https://mhammond.github.io/pywin32/win32api.html
    monitors = win32api.EnumDisplayMonitors()
    #print(f"{monitors=!r}")
    infos: list[MyMonitorInfo] = []
    for monitor in monitors:
        hMonitor, _hdcMonitor, _rect = monitor
        info = win32api.GetMonitorInfo(hMonitor.handle)
        #print(f"{info=!r}")
        table = MyMonitorInfo(
            top        = info["Monitor"][1],
            right      = info["Monitor"][2],
            bottom     = info["Monitor"][3],
            left       = info["Monitor"][0],
            is_primary = info["Flags"] == 1,
            name       = info["Device"],
        )
        infos.append(table)

    return infos

def _convert_position_in_screen_to_offset_in_screen(pos: PositionInScreen, /, *, screen_info: MyScreenInfo | None = None) -> OffsetInScreen:
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
    assert offset_x < screen_info.width
    assert offset_y < screen_info.height
    return OffsetInScreen(offset_x, offset_y)

def _convert_position_in_screen_to_offset_in_client_region_of_active_window(pos: PositionInScreen, /, *, window_info: MyWindowInfo | None = None, screen_info: MyScreenInfo | None = None) -> OffsetInWindow:
    """
    Convert `pos` to offset in client region of active window.
    `pos` should be in client region of active window.
    And also `pos` should be in screen (active window may be beyond screen edge)
    """
    if True:
        if screen_info is None:
            screen_info = get_screen_info()
        assert screen_info.includes(pos)

    if window_info is None:
        window_info = get_active_window_info()
    assert window_info.includes(pos)

    offset_x = pos.x - window_info.left - window_info.padding.left
    offset_y = pos.y - window_info.top - window_info.padding.top
    assert window_info.client.includes(MyPosition(offset_x, offset_y))
    return OffsetInWindow(offset_x, offset_y)

def _convert_offset_in_screen_to_position_in_screen(offset: OffsetInScreen, /, *, screen_info: MyScreenInfo | None = None) -> PositionInScreen:
    if screen_info is None:
        screen_info = get_screen_info()
    assert offset.x >= 0
    assert offset.y >= 0
    assert offset.x < screen_info.width
    assert offset.y < screen_info.height
    x = offset.x - screen_info.origin.x
    y = offset.y - screen_info.origin.y
    assert screen_info.includes(MyPosition(x, y))
    return PositionInScreen(x, y)

def _convert_offset_in_client_region_of_active_window_to_position_in_screen(offset: OffsetInWindow, /, *, window_info: MyWindowInfo | None = None, screen_info: MyScreenInfo | None = None) -> PositionInScreen:
    """
    Convert `offset` to position in screen.
    `offset` should be in client region of active window.
    And also `offset` should be in screen (active window may be beyond screen edge)
    """
    if window_info is None:
        window_info = get_active_window_info()
    assert window_info.client.includes(offset)
    x = window_info.left + window_info.padding.left + offset.x
    y = window_info.top + window_info.padding.top + offset.y
    if True:
        if screen_info is None:
            screen_info = get_screen_info()
        assert screen_info.includes(MyPosition(x, y))
    return PositionInScreen(x, y)

#=============================================================================
# Public class

@dataclass(frozen=True, kw_only=True)
class MyMonitorInfo(MyRect):
    is_primary: bool
    name: str

    def __post_init__(self):
        super().__post_init__()
        assert self.name
        assert self.width > 0
        assert self.height > 0

@dataclass(frozen=True, kw_only=True)
class MyScreenInfo(MyRect):
    origin: MyOffsetInRect
    monitors: list[MyMonitorInfo]

    def __post_init__(self):
        super().__post_init__()
        assert self.monitors

@dataclass(frozen=True, kw_only=True)
class MyPaddingInfo:
    """
    Represent paddings of a rectangle
    """

    top: int
    right: int
    bottom: int
    left: int

    def __post_init__(self):
        assert self.top >= 0
        assert self.right >= 0
        assert self.bottom >= 0
        assert self.left >= 0

@dataclass(frozen=True, kw_only=True)
class MyWindowInfo(MyRect):
    hwnd: int
    title: str
    padding: MyPaddingInfo
    client: MyRect

    def __post_init__(self):
        super().__post_init__()
        assert self.hwnd != 0

@dataclass(frozen=True)
class PositionInScreen(MyPosition):
    """
    Represent position in screen
    """

    def to_offset_in_screen(self, /, *, screen_info: MyScreenInfo | None = None) -> OffsetInScreen:
        return _convert_position_in_screen_to_offset_in_screen(self, screen_info=screen_info)

    def to_offset_in_client_region_of_active_window(self, /, *, window_info: MyWindowInfo | None = None, screen_info: MyScreenInfo | None = None) -> OffsetInWindow:
        return _convert_position_in_screen_to_offset_in_client_region_of_active_window(self, window_info=window_info, screen_info=screen_info)

@dataclass(frozen=True)
class OffsetInScreen(MyOffsetInRect):
    """
    Represent offset in screen.
    This can be used for offset in screenshot of whole desktop.
    """

    def to_position_in_screen(self, /, *, screen_info: MyScreenInfo | None = None) -> PositionInScreen:
        return _convert_offset_in_screen_to_position_in_screen(self, screen_info=screen_info)

@dataclass(frozen=True)
class OffsetInWindow(MyOffsetInRect):
    """
    Represent offset in client area of active window
    """

    def to_position_in_screen(self, /, *, window_info: MyWindowInfo | None = None, screen_info: MyScreenInfo | None = None) -> PositionInScreen:
        return _convert_offset_in_client_region_of_active_window_to_position_in_screen(self, window_info=window_info, screen_info=screen_info)

#=============================================================================
# Public function

def get_active_window_info() -> MyWindowInfo:
    """
    Return infomation about active (foreground) window.
    This function is synchronous (blocking) API.
    """
    # https://github.com/asweigart/PyGetWindow/blob/master/src/pygetwindow/_pygetwindow_win.py
    timestamp_at_start = my_get_timestamp_ms()
    while (hwnd := _get_hwnd_of_active_window()) == 0:
        # may be switching window now
        if my_get_timestamp_ms() - timestamp_at_start > _TIMEOUT_MS_FOR_WINDOW_SWITCH:
            raise TimeoutForWindowSwitch()
        my_sleep_a_moment()
    assert hwnd != 0

    client_rect = _get_client_rect(hwnd)
    window_rect = _get_window_rect(hwnd)
    title = _get_window_title(hwnd)

    if client_rect.width == 0 or client_rect.height == 0:
        padding_width = 0
        diff_y = 0
    else:
        diff_x = window_rect.width - client_rect.width - client_rect.left
        assert diff_x >= 0, (window_rect.width, client_rect.width, client_rect.left)
        assert diff_x % 2 == 0
        padding_width = diff_x // 2 # may be zero
        diff_y = window_rect.height - client_rect.height - client_rect.top
        assert diff_y >= padding_width, (diff_y, padding_width, window_rect, client_rect) # padding_top may be zero

    padding_info = MyPaddingInfo(
        top    = diff_y - padding_width,
        right  =  padding_width,
        bottom = padding_width,
        left   = padding_width,
    )

    info = MyWindowInfo(
        hwnd = hwnd,
        title = title,
        padding = padding_info,
        client = client_rect,
        **window_rect.asdict(),
    )
    #print(f"{info=}")
    return info

def get_screen_info():
    monitors = _get_all_monitor_info()
    origin = MyOffsetInRect(
        x = -1 * min(monitor.left for monitor in monitors),
        y = -1 * min(monitor.top for monitor in monitors),
    )
    result = MyScreenInfo(
        top    = min(monitor.top for monitor in monitors),
        right  = max(monitor.right for monitor in monitors),
        bottom = max(monitor.bottom for monitor in monitors),
        left   = min(monitor.left for monitor in monitors),
        origin = origin,
        monitors = monitors,
    )
    #print(result)
    return result

def show_dialog(text: str) -> None:
    # https://mhammond.github.io/pywin32/win32gui__MessageBox_meth.html
    # https://github.com/asweigart/PyMsgBox/blob/master/src/pymsgbox/_native_win.py#L69
    flags = 0
    flags |= 0x0     # MB_OK
    flags |= 0x10000 # MB_SETFOREGROUND
    flags |= 0x40000 # MB_TOPMOST
    win32gui.MessageBox(None, text, "PyKMmacro Dialog", flags) # type: ignore

def activate_window(title: str) -> bool:
    """
    Search the window whose title matches specified text, and make the window active (foreground).
    This function is synchronous (blocking) API.
    """
    assert title
    hwnd = 0
    def callback(hwnd2: int, _data: Any):
        nonlocal hwnd
        assert hwnd2 != 0
        title2 = _get_window_title(hwnd2)
        if title2 and title2 == title:
            hwnd = hwnd2
            return False # stop enumeration
    win32gui.EnumWindows(callback, None)
    if hwnd == 0:
        return False
    _restore_window(hwnd)
    win32gui.SetForegroundWindow(hwnd)
    timestamp_at_start = my_get_timestamp_ms()
    while _get_hwnd_of_active_window() != hwnd:
        if my_get_timestamp_ms() - timestamp_at_start > _TIMEOUT_MS_FOR_WINDOW_SWITCH:
            raise TimeoutForWindowSwitch()
        my_sleep_a_moment()
    my_sleep_a_moment()
    return True
