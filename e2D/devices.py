from enum import Enum
import glfw
from .types import WindowType
from .vectors import Vector2D


class Keys:
    """GLFW key constants for easy access with autocompletion.
    
    Usage:
        if keyboard.get_key(Keys.SPACE):
            print("Space pressed!")
        
        if keyboard.get_key(Keys.W, KeyState.JUST_PRESSED):
            print("W just pressed!")
    """
    # Special keys
    SPACE: int = glfw.KEY_SPACE
    APOSTROPHE: int = glfw.KEY_APOSTROPHE  # '
    COMMA: int = glfw.KEY_COMMA  # ,
    MINUS: int = glfw.KEY_MINUS  # -
    PERIOD: int = glfw.KEY_PERIOD  # .
    SLASH: int = glfw.KEY_SLASH  # /
    SEMICOLON: int = glfw.KEY_SEMICOLON  # ;
    EQUAL: int = glfw.KEY_EQUAL  # =
    LEFT_BRACKET: int = glfw.KEY_LEFT_BRACKET  # [
    BACKSLASH: int = glfw.KEY_BACKSLASH  # \
    RIGHT_BRACKET: int = glfw.KEY_RIGHT_BRACKET  # ]
    GRAVE_ACCENT: int = glfw.KEY_GRAVE_ACCENT  # `
    
    # Numbers
    NUM_0: int = glfw.KEY_0
    NUM_1: int = glfw.KEY_1
    NUM_2: int = glfw.KEY_2
    NUM_3: int = glfw.KEY_3
    NUM_4: int = glfw.KEY_4
    NUM_5: int = glfw.KEY_5
    NUM_6: int = glfw.KEY_6
    NUM_7: int = glfw.KEY_7
    NUM_8: int = glfw.KEY_8
    NUM_9: int = glfw.KEY_9
    
    # Letters
    A: int = glfw.KEY_A
    B: int = glfw.KEY_B
    C: int = glfw.KEY_C
    D: int = glfw.KEY_D
    E: int = glfw.KEY_E
    F: int = glfw.KEY_F
    G: int = glfw.KEY_G
    H: int = glfw.KEY_H
    I: int = glfw.KEY_I
    J: int = glfw.KEY_J
    K: int = glfw.KEY_K
    L: int = glfw.KEY_L
    M: int = glfw.KEY_M
    N: int = glfw.KEY_N
    O: int = glfw.KEY_O
    P: int = glfw.KEY_P
    Q: int = glfw.KEY_Q
    R: int = glfw.KEY_R
    S: int = glfw.KEY_S
    T: int = glfw.KEY_T
    U: int = glfw.KEY_U
    V: int = glfw.KEY_V
    W: int = glfw.KEY_W
    X: int = glfw.KEY_X
    Y: int = glfw.KEY_Y
    Z: int = glfw.KEY_Z
    
    # Function keys
    ESCAPE: int = glfw.KEY_ESCAPE
    ENTER: int = glfw.KEY_ENTER
    TAB: int = glfw.KEY_TAB
    BACKSPACE: int = glfw.KEY_BACKSPACE
    INSERT: int = glfw.KEY_INSERT
    DELETE: int = glfw.KEY_DELETE
    RIGHT: int = glfw.KEY_RIGHT
    LEFT: int = glfw.KEY_LEFT
    DOWN: int = glfw.KEY_DOWN
    UP: int = glfw.KEY_UP
    PAGE_UP: int = glfw.KEY_PAGE_UP
    PAGE_DOWN: int = glfw.KEY_PAGE_DOWN
    HOME: int = glfw.KEY_HOME
    END: int = glfw.KEY_END
    CAPS_LOCK: int = glfw.KEY_CAPS_LOCK
    SCROLL_LOCK: int = glfw.KEY_SCROLL_LOCK
    NUM_LOCK: int = glfw.KEY_NUM_LOCK
    PRINT_SCREEN: int = glfw.KEY_PRINT_SCREEN
    PAUSE: int = glfw.KEY_PAUSE
    
    # F1-F25
    F1: int = glfw.KEY_F1
    F2: int = glfw.KEY_F2
    F3: int = glfw.KEY_F3
    F4: int = glfw.KEY_F4
    F5: int = glfw.KEY_F5
    F6: int = glfw.KEY_F6
    F7: int = glfw.KEY_F7
    F8: int = glfw.KEY_F8
    F9: int = glfw.KEY_F9
    F10: int = glfw.KEY_F10
    F11: int = glfw.KEY_F11
    F12: int = glfw.KEY_F12
    F13: int = glfw.KEY_F13
    F14: int = glfw.KEY_F14
    F15: int = glfw.KEY_F15
    F16: int = glfw.KEY_F16
    F17: int = glfw.KEY_F17
    F18: int = glfw.KEY_F18
    F19: int = glfw.KEY_F19
    F20: int = glfw.KEY_F20
    F21: int = glfw.KEY_F21
    F22: int = glfw.KEY_F22
    F23: int = glfw.KEY_F23
    F24: int = glfw.KEY_F24
    F25: int = glfw.KEY_F25
    
    # Keypad
    KP_0: int = glfw.KEY_KP_0
    KP_1: int = glfw.KEY_KP_1
    KP_2: int = glfw.KEY_KP_2
    KP_3: int = glfw.KEY_KP_3
    KP_4: int = glfw.KEY_KP_4
    KP_5: int = glfw.KEY_KP_5
    KP_6: int = glfw.KEY_KP_6
    KP_7: int = glfw.KEY_KP_7
    KP_8: int = glfw.KEY_KP_8
    KP_9: int = glfw.KEY_KP_9
    KP_DECIMAL: int = glfw.KEY_KP_DECIMAL
    KP_DIVIDE: int = glfw.KEY_KP_DIVIDE
    KP_MULTIPLY: int = glfw.KEY_KP_MULTIPLY
    KP_SUBTRACT: int = glfw.KEY_KP_SUBTRACT
    KP_ADD: int = glfw.KEY_KP_ADD
    KP_ENTER: int = glfw.KEY_KP_ENTER
    KP_EQUAL: int = glfw.KEY_KP_EQUAL
    
    # Modifiers
    LEFT_SHIFT: int = glfw.KEY_LEFT_SHIFT
    LEFT_CONTROL: int = glfw.KEY_LEFT_CONTROL
    LEFT_ALT: int = glfw.KEY_LEFT_ALT
    LEFT_SUPER: int = glfw.KEY_LEFT_SUPER  # Windows/Command key
    RIGHT_SHIFT: int = glfw.KEY_RIGHT_SHIFT
    RIGHT_CONTROL: int = glfw.KEY_RIGHT_CONTROL
    RIGHT_ALT: int = glfw.KEY_RIGHT_ALT
    RIGHT_SUPER: int = glfw.KEY_RIGHT_SUPER
    MENU: int = glfw.KEY_MENU


class MouseButtons:
    """GLFW mouse button constants for easy access with autocompletion.
    
    Usage:
        if mouse.get_button(MouseButtons.LEFT, KeyState.PRESSED):
            print("Left mouse button pressed!")
    """
    LEFT: int = glfw.MOUSE_BUTTON_LEFT
    RIGHT: int = glfw.MOUSE_BUTTON_RIGHT
    MIDDLE: int = glfw.MOUSE_BUTTON_MIDDLE
    BUTTON_4: int = glfw.MOUSE_BUTTON_4
    BUTTON_5: int = glfw.MOUSE_BUTTON_5
    BUTTON_6: int = glfw.MOUSE_BUTTON_6
    BUTTON_7: int = glfw.MOUSE_BUTTON_7
    BUTTON_8: int = glfw.MOUSE_BUTTON_8


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