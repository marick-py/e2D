"""
Unit tests for e2D input system
Tests Keys and MouseButtons classes without requiring a window
"""

from e2D import Keys, MouseButtons, KeyState

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
    
    print("\n" + "="*50)
    print("✓ ALL INPUT TESTS PASSED")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
