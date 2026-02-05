"""
Unit test to verify ColorType accepts both Color objects and tuples
Tests the flexibility of ColorType without requiring a window (headless)
"""

from e2D import Color, normalize_color, RED, GREEN, BLUE

def test_color_types():
    """Test that ColorType accepts both Color objects and tuples"""
    print("\n=== ColorType Flexibility ===")
    
    # Test with Color object
    color_obj = Color(1.0, 0.0, 0.0, 1.0)
    normalized = normalize_color(color_obj)
    assert normalized == (1.0, 0.0, 0.0, 1.0), "Color object normalization failed"
    print("✓ Color object accepted")
    
    # Test with tuple
    color_tuple = (0.0, 1.0, 0.0, 1.0)
    normalized = normalize_color(color_tuple)
    assert normalized == (0.0, 1.0, 0.0, 1.0), "Color tuple normalization failed"
    print("✓ Color tuple accepted")
    
    # Test with hex string
    color_hex = "#FF0000"
    normalized = normalize_color(color_hex)
    assert normalized == (1.0, 0.0, 0.0, 1.0), "Hex color normalization failed"
    print("✓ Hex string accepted")
    
    # Test with predefined colors
    normalized = normalize_color(RED)
    assert normalized == RED, "Predefined color normalization failed"
    print("✓ Predefined color constants accepted")
    
    # Test that Color methods return tuples
    color = Color.from_rgb(1.0, 0.5, 0.0)
    rgba = color.to_rgba()
    assert isinstance(rgba, tuple) and len(rgba) == 4, "Color.to_rgba should return tuple"
    print("✓ Color.to_rgba returns tuple")
    
    # Test mixed usage
    colors = [
        RED,  # Predefined tuple
        Color.red(),  # Color object
        (0.0, 1.0, 0.0, 1.0),  # Direct tuple
        Color.from_hex("#0000FF")  # Color from hex
    ]
    
    normalized_colors = [normalize_color(c) for c in colors]
    assert all(isinstance(c, tuple) and len(c) == 4 for c in normalized_colors), "All colors should normalize to tuples"
    print("✓ Mixed color types normalize correctly")
    
    print("\n✓ All ColorType flexibility tests passed!")

def run_all_tests():
    """Run all color type tests"""
    print("\n" + "="*50)
    print("Running ColorType Tests (Headless)")
    print("="*50)
    
    test_color_types()
    
    print("\n" + "="*50)
    print("✓ ALL COLORTYPE TESTS PASSED")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
