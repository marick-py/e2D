"""
Unit tests for e2D input system
Tests Keys, MouseButtons, KeyState, Keyboard, and Mouse without requiring a window
"""

from e2D import Keys, MouseButtons, KeyState
from e2D.input import Keyboard, Mouse

def test_keys_class():
    """Test Keys class constants"""
    print("\n=== Keys Class ===")
    
    # Test letter keys
    assert hasattr(Keys, 'A'), "Keys.A should exist"
    assert hasattr(Keys, 'W'), "Keys.W should exist"
    assert hasattr(Keys, 'Z'), "Keys.Z should exist"
    
    # Test number keys
    for i in range(10):
        attr = f"NUM_{i}"
        assert hasattr(Keys, attr), f"Keys.{attr} should exist"
        value = getattr(Keys, attr)
        assert isinstance(value, int), f"Keys.{attr} should be an int"
    
    # Test function keys
    for i in range(1, 26):  # F1-F25
        attr = f"F{i}"
        assert hasattr(Keys, attr), f"Keys.{attr} should exist"
    
    # Test arrow keys
    assert hasattr(Keys, 'UP'), "Keys.UP should exist"
    assert hasattr(Keys, 'DOWN'), "Keys.DOWN should exist"
    assert hasattr(Keys, 'LEFT'), "Keys.LEFT should exist"
    assert hasattr(Keys, 'RIGHT'), "Keys.RIGHT should exist"
    
    # Test modifier keys
    assert hasattr(Keys, 'LEFT_SHIFT'), "Keys.LEFT_SHIFT should exist"
    assert hasattr(Keys, 'RIGHT_SHIFT'), "Keys.RIGHT_SHIFT should exist"
    assert hasattr(Keys, 'LEFT_CONTROL'), "Keys.LEFT_CONTROL should exist"
    assert hasattr(Keys, 'RIGHT_CONTROL'), "Keys.RIGHT_CONTROL should exist"
    assert hasattr(Keys, 'LEFT_ALT'), "Keys.LEFT_ALT should exist"
    assert hasattr(Keys, 'RIGHT_ALT'), "Keys.RIGHT_ALT should exist"
    
    # Test special keys
    assert hasattr(Keys, 'SPACE'), "Keys.SPACE should exist"
    assert hasattr(Keys, 'ENTER'), "Keys.ENTER should exist"
    assert hasattr(Keys, 'ESCAPE'), "Keys.ESCAPE should exist"
    assert hasattr(Keys, 'TAB'), "Keys.TAB should exist"
    assert hasattr(Keys, 'BACKSPACE'), "Keys.BACKSPACE should exist"
    
    # Test numpad keys
    for i in range(10):
        attr = f"KP_{i}"
        assert hasattr(Keys, attr), f"Keys.{attr} should exist"
    
    print("✓ Keys class tests passed")

def test_mouse_buttons_class():
    """Test MouseButtons class constants"""
    print("\n=== MouseButtons Class ===")
    
    # Test basic mouse buttons
    assert hasattr(MouseButtons, 'LEFT'), "MouseButtons.LEFT should exist"
    assert hasattr(MouseButtons, 'RIGHT'), "MouseButtons.RIGHT should exist"
    assert hasattr(MouseButtons, 'MIDDLE'), "MouseButtons.MIDDLE should exist"
    
    # Test additional buttons
    assert hasattr(MouseButtons, 'BUTTON_4'), "MouseButtons.BUTTON_4 should exist"
    assert hasattr(MouseButtons, 'BUTTON_5'), "MouseButtons.BUTTON_5 should exist"
    assert hasattr(MouseButtons, 'BUTTON_6'), "MouseButtons.BUTTON_6 should exist"
    assert hasattr(MouseButtons, 'BUTTON_7'), "MouseButtons.BUTTON_7 should exist"
    assert hasattr(MouseButtons, 'BUTTON_8'), "MouseButtons.BUTTON_8 should exist"
    
    # Verify they are integers
    assert isinstance(MouseButtons.LEFT, int), "MouseButtons.LEFT should be an int"
    assert isinstance(MouseButtons.RIGHT, int), "MouseButtons.RIGHT should be an int"
    assert isinstance(MouseButtons.MIDDLE, int), "MouseButtons.MIDDLE should be an int"
    
    print("✓ MouseButtons class tests passed")

def test_key_state_enum():
    """Test KeyState enum"""
    print("\n=== KeyState Enum ===")
    
    # Test that KeyState has all required states
    assert hasattr(KeyState, 'PRESSED'), "KeyState.PRESSED should exist"
    assert hasattr(KeyState, 'JUST_PRESSED'), "KeyState.JUST_PRESSED should exist"
    assert hasattr(KeyState, 'JUST_RELEASED'), "KeyState.JUST_RELEASED should exist"
    
    # Verify they have numeric values (enum members)
    assert KeyState.PRESSED is not None, "KeyState.PRESSED should exist"
    assert KeyState.JUST_PRESSED is not None, "KeyState.JUST_PRESSED should exist"
    assert KeyState.JUST_RELEASED is not None, "KeyState.JUST_RELEASED should exist"
    
    # Verify they have different values
    assert KeyState.PRESSED != KeyState.JUST_PRESSED, "States should have different values"
    assert KeyState.PRESSED != KeyState.JUST_RELEASED, "States should have different values"
    assert KeyState.JUST_PRESSED != KeyState.JUST_RELEASED, "States should have different values"
    
    print("✓ KeyState enum tests passed")

def test_keys_completeness():
    """Test that all expected key categories exist"""
    print("\n=== Keys Completeness ===")
    
    # Letter keys (A-Z)
    letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    for letter in letters:
        assert hasattr(Keys, letter), f"Keys.{letter} should exist"
    
    # Number keys (NUM_0 to NUM_9)
    for i in range(10):
        assert hasattr(Keys, f"NUM_{i}"), f"Keys.NUM_{i} should exist"
    
    # Function keys (F1-F25)
    for i in range(1, 26):
        assert hasattr(Keys, f"F{i}"), f"Keys.F{i} should exist"
    
    # Numpad keys
    for i in range(10):
        assert hasattr(Keys, f"KP_{i}"), f"Keys.KP_{i} should exist"
    
    # Numpad special keys
    assert hasattr(Keys, 'KP_DECIMAL'), "Keys.KP_DECIMAL should exist"
    assert hasattr(Keys, 'KP_DIVIDE'), "Keys.KP_DIVIDE should exist"
    assert hasattr(Keys, 'KP_MULTIPLY'), "Keys.KP_MULTIPLY should exist"
    assert hasattr(Keys, 'KP_SUBTRACT'), "Keys.KP_SUBTRACT should exist"
    assert hasattr(Keys, 'KP_ADD'), "Keys.KP_ADD should exist"
    assert hasattr(Keys, 'KP_ENTER'), "Keys.KP_ENTER should exist"
    assert hasattr(Keys, 'KP_EQUAL'), "Keys.KP_EQUAL should exist"
    
    print("✓ Keys completeness tests passed")

def test_keys_values_unique():
    """Test that key values are unique"""
    print("\n=== Keys Uniqueness ===")
    
    # Collect some key values
    key_values = {}
    test_keys = ['A', 'W', 'S', 'D', 'SPACE', 'ENTER', 'UP', 'DOWN', 'LEFT', 'RIGHT']
    
    for key_name in test_keys:
        if hasattr(Keys, key_name):
            value = getattr(Keys, key_name)
            if value in key_values:
                raise AssertionError(f"Duplicate key value: {key_name} and {key_values[value]} both have value {value}")
            key_values[value] = key_name
    
    print(f"✓ Keys uniqueness tests passed ({len(key_values)} keys checked)")

def test_mouse_buttons_values():
    """Test MouseButtons have valid GLFW values"""
    print("\n=== MouseButtons Values ===")
    
    # GLFW mouse button values typically start at 0
    assert MouseButtons.LEFT >= 0, "MouseButtons.LEFT should be >= 0"
    assert MouseButtons.RIGHT >= 0, "MouseButtons.RIGHT should be >= 0"
    assert MouseButtons.MIDDLE >= 0, "MouseButtons.MIDDLE should be >= 0"
    
    # Buttons should have different values
    buttons = [MouseButtons.LEFT, MouseButtons.RIGHT, MouseButtons.MIDDLE]
    assert len(buttons) == len(set(buttons)), "Mouse buttons should have unique values"
    
    print("✓ MouseButtons values tests passed")

def test_keyboard_instantiation():
    """Test Keyboard can be instantiated without a window"""
    print("\n=== Keyboard Instantiation ===")

    kb = Keyboard()
    assert isinstance(kb.pressed, set), "pressed should be a set"
    assert isinstance(kb.just_pressed, set), "just_pressed should be a set"
    assert isinstance(kb.just_released, set), "just_released should be a set"
    assert isinstance(kb.char_buffer, list), "char_buffer should be a list"
    assert isinstance(kb.is_consumed, bool), "is_consumed should be a bool"
    assert len(kb.pressed) == 0
    assert len(kb.char_buffer) == 0
    assert kb.is_consumed is False

    print("✓ Keyboard instantiation tests passed")

def test_keyboard_key_states():
    """Test Keyboard key state tracking via internal _on_key callback"""
    print("\n=== Keyboard Key States ===")

    import glfw

    kb = Keyboard()

    # Simulate PRESS
    kb._on_key(None, Keys.A, 0, glfw.PRESS, 0)  # type: ignore[arg-type]
    assert Keys.A in kb.pressed, "A should be in pressed after PRESS"
    assert Keys.A in kb.just_pressed, "A should be in just_pressed after PRESS"
    assert Keys.A not in kb.just_released

    # get_key helpers
    assert kb.get_key(Keys.A, KeyState.PRESSED)
    assert kb.get_key(Keys.A, KeyState.JUST_PRESSED)
    assert not kb.get_key(Keys.A, KeyState.JUST_RELEASED)

    # Update clears transient sets
    kb.update()
    assert Keys.A in kb.pressed, "A should remain in pressed after update"
    assert Keys.A not in kb.just_pressed, "just_pressed should clear after update"
    assert len(kb.just_released) == 0

    # Simulate RELEASE
    kb._on_key(None, Keys.A, 0, glfw.RELEASE, 0)  # type: ignore[arg-type]
    assert Keys.A not in kb.pressed
    assert Keys.A in kb.just_released
    assert kb.get_key(Keys.A, KeyState.JUST_RELEASED)

    kb.update()
    assert Keys.A not in kb.just_released, "just_released should clear after update"

    print("✓ Keyboard key state tests passed")

def test_keyboard_char_buffer():
    """Test Keyboard char_buffer and get_chars()"""
    print("\n=== Keyboard char_buffer / get_chars ===")

    kb = Keyboard()

    # Simulate typing "Hi!"
    for cp in [ord('H'), ord('i'), ord('!')]:
        kb._on_char(None, cp)  # type: ignore[arg-type]

    assert kb.char_buffer == ['H', 'i', '!'], f"Expected ['H','i','!'], got {kb.char_buffer}"

    chars = kb.get_chars()
    assert chars == ['H', 'i', '!'], "get_chars() should return typed characters"
    # get_chars returns a copy — mutating it must not affect internal buffer
    chars.clear()
    assert kb.char_buffer == ['H', 'i', '!'], "get_chars() must return a copy"

    # update() clears the buffer
    kb.update()
    assert kb.char_buffer == [], "char_buffer should be empty after update()"
    assert kb.get_chars() == []

    print("✓ Keyboard char_buffer / get_chars tests passed")

def test_keyboard_is_consumed():
    """Test Keyboard.is_consumed flag"""
    print("\n=== Keyboard is_consumed ===")

    kb = Keyboard()
    assert kb.is_consumed is False

    kb.is_consumed = True
    assert kb.is_consumed is True

    # update() should reset the flag
    kb.update()
    assert kb.is_consumed is False

    print("✓ Keyboard is_consumed tests passed")

def test_mouse_instantiation():
    """Test Mouse can be instantiated and helper methods work without a window"""
    print("\n=== Mouse Instantiation ===")

    from e2D.vectors import Vector2D

    m = Mouse()
    assert isinstance(m.position, Vector2D)
    assert isinstance(m.delta, Vector2D)
    assert isinstance(m.scroll, Vector2D)
    assert len(m.pressed) == 0
    assert len(m.just_pressed) == 0
    assert len(m.just_released) == 0

    print("✓ Mouse instantiation tests passed")

def test_mouse_movement():
    """Test Mouse position tracking"""
    print("\n=== Mouse Movement ===")

    m = Mouse()

    m._on_cursor_pos(None, 100.0, 200.0)  # type: ignore[arg-type]
    assert m.position.x == 100.0
    assert m.position.y == 200.0

    m.update()
    assert m.delta.x == 100.0, f"Expected delta.x=100.0, got {m.delta.x}"
    assert m.delta.y == 200.0

    m._on_cursor_pos(None, 110.0, 195.0)  # type: ignore[arg-type]
    m.update()
    assert m.delta.x == 10.0
    assert m.delta.y == -5.0

    print("✓ Mouse movement tests passed")

def test_mouse_buttons():
    """Test Mouse button state tracking"""
    print("\n=== Mouse Button States ===")

    import glfw

    m = Mouse()

    m._on_mouse_button(None, MouseButtons.LEFT, glfw.PRESS, 0)  # type: ignore[arg-type]
    assert MouseButtons.LEFT in m.pressed
    assert MouseButtons.LEFT in m.just_pressed
    assert m.get_button(MouseButtons.LEFT, KeyState.PRESSED)
    assert m.get_button(MouseButtons.LEFT, KeyState.JUST_PRESSED)

    m.update()
    assert MouseButtons.LEFT in m.pressed
    assert MouseButtons.LEFT not in m.just_pressed

    m._on_mouse_button(None, MouseButtons.LEFT, glfw.RELEASE, 0)  # type: ignore[arg-type]
    assert MouseButtons.LEFT not in m.pressed
    assert m.get_button(MouseButtons.LEFT, KeyState.JUST_RELEASED)

    print("✓ Mouse button state tests passed")

def test_mouse_scroll():
    """Test Mouse scroll tracking"""
    print("\n=== Mouse Scroll ===")

    m = Mouse()
    m._on_scroll(None, 0.0, 3.0)  # type: ignore[arg-type]
    assert m.scroll.y == 3.0

    m.update()
    assert m.scroll.x == 0.0 and m.scroll.y == 0.0, "scroll should reset after update"

    print("✓ Mouse scroll tests passed")


def run_all_tests():
    """Run all input tests"""
    print("\n" + "="*50)
    print("Running e2D Input Tests (Headless)")
    print("="*50)
    
    test_keys_class()
    test_mouse_buttons_class()
    test_key_state_enum()
    test_keys_completeness()
    test_keys_values_unique()
    test_mouse_buttons_values()
    test_keyboard_instantiation()
    test_keyboard_key_states()
    test_keyboard_char_buffer()
    test_keyboard_is_consumed()
    test_mouse_instantiation()
    test_mouse_movement()
    test_mouse_buttons()
    test_mouse_scroll()
    
    print("\n" + "="*50)
    print("✓ ALL INPUT TESTS PASSED")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
