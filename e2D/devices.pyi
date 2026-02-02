"""  
Type stubs for devices module
Input device handling (Keyboard and Mouse)
"""

from enum import Enum
from .types import VectorType, WindowType

class KeyState(Enum):
    """State of a keyboard key or mouse button"""
    PRESSED: int
    JUST_PRESSED: int
    JUST_RELEASED: int

class Keyboard:
    """Keyboard input handler"""
    pressed: set[int]
    just_pressed: set[int]
    just_released: set[int]
    
    def __init__(self) -> None: ...

    def _on_key(self, window: WindowType, key: int, scancode: int, action: int, mods: int) -> None:
        """Internal key event handler"""
        ...
    
    def update(self) -> None:
        """Update keyboard state (call once per frame)"""
        ...
    
    def get_key(self, key: int, state: KeyState|int) -> bool:
        """Check if a key is in the given state"""
        ...

class Mouse:
    """Mouse input handler"""
    position: VectorType
    last_position: VectorType
    delta: VectorType
    scroll: VectorType
    pressed: set[int]
    just_pressed: set[int]
    just_released: set[int]
    
    def __init__(self) -> None: ...

    def _on_cursor_pos(self, window: WindowType, x: float, y: float) -> None:
        """Internal cursor position event handler"""
        ...

    def _on_mouse_button(self, window: WindowType, button: int, action: int, mods: int) -> None:
        """Internal mouse button event handler"""
        ...

    def _on_scroll(self, window: WindowType, xoffset: float, yoffset: float) -> None:
        """Internal scroll event handler"""
        ...

    def update(self) -> None:
        """Update mouse state (call once per frame)"""
        ...
    
    def get_button(self, button: int, state: KeyState | int) -> bool:
        """Check if a mouse button is in the given state"""
        ...
