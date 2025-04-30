# PyKMmacro

**PyKMmacro** is a tiny clone of KMmacro written by Python.

The purpose of PyKMmacro is to provide a substitute for KMmacro as an interpreter for its original macro file.
So the folowing features are NOT targeted:

- Recording keyboard/mouse operations
- Menu
- TSR (Terminate-and-Stay Resident) mode
- Hotkey

This software is a practice in Python programming.

## About KMmacro

**KMmacro** is an automation software on Microsoft Windows.
KMmacro is developed by たわしと (TAWASHITO).

- KMmacro - Vector   
  https://www.vector.co.jp/soft/winnt/util/se211440.html
- KMmacro BBS   
  https://trick-room.bbs.fc2.com/

KMmacro can record keyboard/mouse operations and reproduce them later.
In addition, KMmacro has an interpreter for original macro file.
In the macro file, the folowing features are available:

- Flow control (such as `IF`, `GOTO`, and `FOR`)
- Function-like flow control (`CALL` and `RETURN`)
- Variable (such as `DIM` and `SET`)
- Keyboard input emulation (such as "key press", "key down" and "key up")
- Mouse input emulation (such as "click", "move" and "wheel")
- Capture pixel color on screen (`getpixel`)
- Clipboard operation (such as `CLIPBOARD` and `PASTE`)
- File operation (such as `open`, `read`, `write` and `INCLUDE`)
- OS shell wrapper (such as `EXEC` and `SHELL`)
- Win32API wrapper (such as "get title of active window" and "get mouse position")
- GUI dialog (such as `MESSAGE` and `inputbox`)
- Arithmetic/boolean/string operation
- Utilities (such as `DELAY`)

## Requirements

- Windows 11 23H2 (x86_64) or later
- Python 3.13.3 or later (not tested with previous versions)

## License

MIT
