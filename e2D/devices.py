from enum import Enum
import glfw

class KeyState(Enum):
    PRESSED = 1
    JUST_PRESSED = 2
    JUST_RELEASED = 3

class Keyboard:
    def __init__(self) -> None:
        self.pressed = set()
        self.just_pressed = set()
        self.just_released = set()

    def _on_key(self, window, key, scancode, action, mods) -> None:
        if action == glfw.PRESS:
            self.pressed.add(key)
            self.just_pressed.add(key)
        elif action == glfw.RELEASE:
            self.pressed.discard(key)
            self.just_released.add(key)

    def update(self) -> None:
        self.just_pressed.clear()
        self.just_released.clear()

    def get_key(self, key, state: KeyState) -> bool:
        if state == KeyState.PRESSED:
            return key in self.pressed
        elif state == KeyState.JUST_PRESSED:
            return key in self.just_pressed
        elif state == KeyState.JUST_RELEASED:
            return key in self.just_released
        return False

class Mouse:
    def __init__(self) -> None:
        self.position = (0, 0)
        self.last_position = (0, 0)
        self.delta = (0, 0)
        self.scroll = (0, 0)
        self.pressed = set()
        self.just_pressed = set()
        self.just_released = set()

    def _on_cursor_pos(self, window, x, y) -> None:
        self.position = (x, y)

    def _on_mouse_button(self, window, button, action, mods) -> None:
        if action == glfw.PRESS:
            self.pressed.add(button)
            self.just_pressed.add(button)
        elif action == glfw.RELEASE:
            self.pressed.discard(button)
            self.just_released.add(button)

    def _on_scroll(self, window, xoffset, yoffset) -> None:
        self.scroll = (xoffset, yoffset)

    def update(self) -> None:
        self.delta = (self.position[0] - self.last_position[0], self.position[1] - self.last_position[1])
        self.last_position = self.position
        self.just_pressed.clear()
        self.just_released.clear()
        self.scroll = (0, 0)

    def get_button(self, button, state: KeyState) -> bool:
        if state == KeyState.PRESSED:
            return button in self.pressed
        elif state == KeyState.JUST_PRESSED:
            return button in self.just_pressed
        elif state == KeyState.JUST_RELEASED:
            return button in self.just_released
        return False