import pyperclip

def copy_to_clipboard(text: str) -> bool:
    """
    Copy text into clipboard.
    """
    assert text
    pyperclip.copy(text)
