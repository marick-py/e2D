from enum import Enum
import glfw
from .types import WindowType
from .vectors import Vector2D

class KeyState(Enum):
    PRESSED = 1
    JUST_PRESSED = 2
    JUST_RELEASED = 3

class Keyboard:
    pressed: set[int]
    just_pressed: set[int]
    just_released: set[int]
    
    def __init__(self) -> None:
        self.pressed = set()
        self.just_pressed = set()
        self.just_released = set()

    def _on_key(self, window: WindowType, key: int, scancode: int, action: int, mods: int) -> None:
        if action == glfw.PRESS:
            self.pressed.add(key)
            self.just_pressed.add(key)
        elif action == glfw.RELEASE:
            self.pressed.discard(key)
            self.just_released.add(key)

    def update(self) -> None:
        self.just_pressed.clear()
        self.just_released.clear()

    def get_key(self, key: int, state: KeyState|int = KeyState.PRESSED) -> bool:
        if state == KeyState.PRESSED:
            return key in self.pressed
        elif state == KeyState.JUST_PRESSED:
            return key in self.just_pressed
        elif state == KeyState.JUST_RELEASED:
            return key in self.just_released
        return False

class Mouse:
    position: Vector2D
    last_position: Vector2D
    delta: Vector2D
    scroll: Vector2D
    pressed: set[int]
    just_pressed: set[int]
    just_released: set[int]
    
    def __init__(self) -> None:
        self.position = Vector2D(0, 0)
        self.last_position = Vector2D(0, 0)
        self.delta = Vector2D(0, 0)
        self.scroll = Vector2D(0, 0)
        self.pressed = set()
        self.just_pressed = set()
        self.just_released = set()

    def _on_cursor_pos(self, window: WindowType, x: float, y: float) -> None:
        self.position.set(x, y)

    def _on_mouse_button(self, window: WindowType, button: int, action: int, mods: int) -> None:
        if action == glfw.PRESS:
            self.pressed.add(button)
            self.just_pressed.add(button)
        elif action == glfw.RELEASE:
            self.pressed.discard(button)
            self.just_released.add(button)

    def _on_scroll(self, window: WindowType, xoffset: float, yoffset: float) -> None:
        self.scroll.set(xoffset, yoffset)

    def update(self) -> None:
        self.delta.set(self.position.x - self.last_position.x, self.position.y - self.last_position.y)
        self.last_position.set(self.position.x, self.position.y)
        self.just_pressed.clear()
        self.just_released.clear()
        self.scroll.set(0, 0)

    def get_button(self, button: int, state: KeyState) -> bool:
        if state == KeyState.PRESSED:
            return button in self.pressed
        elif state == KeyState.JUST_PRESSED:
            return button in self.just_pressed
        elif state == KeyState.JUST_RELEASED:
            return button in self.just_released
        return False