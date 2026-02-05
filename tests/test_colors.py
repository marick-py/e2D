"""
Unit tests for e2D color system
Tests Color class, color operations, and utility functions without requiring a window
"""

from e2D import (
    Color, normalize_color, lerp_colors, gradient,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, TRANSPARENT
)
from e2D.color_defs import (
    MD_RED, MD_BLUE, PASTEL_RED, NEON_GREEN,
    UI_SUCCESS, UI_WARNING, UI_ERROR, UI_INFO
)

def test_color_creation():
    """Test color creation methods"""
    print("\n=== Color Creation ===")
    
    # Basic RGBA
    c1 = Color(1.0, 0.0, 0.0, 1.0)
    assert c1.r == 1.0 and c1.g == 0.0 and c1.b == 0.0 and c1.a == 1.0, "Basic creation failed"
    
    # From RGB
    c2 = Color.from_rgb(1.0, 0.5, 0.0)
    assert c2.r == 1.0 and c2.g == 0.5 and c2.b == 0.0 and c2.a == 1.0, "RGB creation failed"
    
    # From RGB255
    c3 = Color.from_rgb255(255, 128, 0)
    assert abs(c3.r - 1.0) < 0.01 and abs(c3.g - 0.5) < 0.01, "RGB255 creation failed"
    
    # From hex
    c4 = Color.from_hex("#FF0000")
    assert abs(c4.r - 1.0) < 0.01 and abs(c4.g) < 0.01 and abs(c4.b) < 0.01, "Hex creation failed"
    
    # From HSV
    c5 = Color.from_hsv(0.0, 1.0, 1.0)  # Red
    assert abs(c5.r - 1.0) < 0.01, "HSV creation failed"
    
    # From gray
    c6 = Color.from_gray(0.5)
    assert abs(c6.r - 0.5) < 0.01 and abs(c6.g - 0.5) < 0.01 and abs(c6.b - 0.5) < 0.01, "Gray creation failed"
    
    print("✓ Color creation tests passed")

def test_color_operations():
    """Test color manipulation operations"""
    print("\n=== Color Operations ===")
    
    red = Color.red()
    
    # Lighten
    lighter = red.lighten(0.2)
    assert lighter.r > red.r or lighter.g > red.g or lighter.b > red.b, "Lighten failed"
    
    # Darken
    darker = red.darken(0.2)
    assert darker.r < red.r, "Darken failed"
    
    # With alpha
    semi = red.with_alpha(0.5)
    assert abs(semi.a - 0.5) < 0.001, "with_alpha failed"
    
    # Invert
    inverted = red.invert()
    assert abs(inverted.r) < 0.01 and abs(inverted.g - 1.0) < 0.01 and abs(inverted.b - 1.0) < 0.01, "Invert failed"
    
    # Rotate hue
    rotated = red.rotate_hue(120)  # Should give greenish color
    assert rotated.g > 0.5, "Hue rotation failed"
    
    print("✓ Color operations tests passed")

def test_color_conversion():
    """Test color format conversions"""
    print("\n=== Color Conversion ===")
    
    red = Color.red()
    
    # To tuple
    rgba = red.to_rgba()
    assert len(rgba) == 4 and rgba[0] == 1.0, "to_rgba failed"
    
    rgb = red.to_rgb()
    assert len(rgb) == 3 and rgb[0] == 1.0, "to_rgb failed"
    
    # To 255
    rgb255 = red.to_rgb255()
    assert rgb255[0] == 255 and rgb255[1] == 0, "to_rgb255 failed"
    
    # To hex
    hex_color = red.to_hex()
    assert hex_color.upper() == "#FF0000", f"to_hex failed: {hex_color}"
    
    # To HSV
    hsv = red.to_hsv()
    assert len(hsv) == 3, "to_hsv failed"
    
    print("✓ Color conversion tests passed")

def test_predefined_colors():
    """Test pre-defined color constants"""
    print("\n=== Pre-defined Colors ===")
    
    # Basic colors - normalize first to satisfy type checker
    red = normalize_color(RED)
    green = normalize_color(GREEN)
    blue = normalize_color(BLUE)
    white = normalize_color(WHITE)
    black = normalize_color(BLACK)
    
    assert len(red) == 4 and red[0] == 1.0, "RED constant incorrect"
    assert len(green) == 4 and green[1] == 1.0, "GREEN constant incorrect"
    assert len(blue) == 4 and blue[2] == 1.0, "BLUE constant incorrect"
    assert len(white) == 4 and white[0] == 1.0 and white[1] == 1.0, "WHITE constant incorrect"
    assert len(black) == 4 and black[0] == 0.0 and black[1] == 0.0, "BLACK constant incorrect"
    
    # Transparent
    transparent = normalize_color(TRANSPARENT)
    assert transparent[3] == 0.0, "TRANSPARENT constant incorrect"
    
    # Material design colors
    md_red = normalize_color(MD_RED)
    md_blue = normalize_color(MD_BLUE)
    assert len(md_red) == 4, "MD_RED constant incorrect"
    assert len(md_blue) == 4, "MD_BLUE constant incorrect"
    
    # Pastel colors
    pastel_red = normalize_color(PASTEL_RED)
    assert len(pastel_red) == 4, "PASTEL_RED constant incorrect"
    
    # Neon colors
    neon_green = normalize_color(NEON_GREEN)
    assert len(neon_green) == 4, "NEON_GREEN constant incorrect"
    
    # UI colors
    ui_success = normalize_color(UI_SUCCESS)
    ui_warning = normalize_color(UI_WARNING)
    ui_error = normalize_color(UI_ERROR)
    ui_info = normalize_color(UI_INFO)
    assert len(ui_success) == 4, "UI_SUCCESS constant incorrect"
    assert len(ui_warning) == 4, "UI_WARNING constant incorrect"
    assert len(ui_error) == 4, "UI_ERROR constant incorrect"
    assert len(ui_info) == 4, "UI_INFO constant incorrect"
    
    print("✓ Pre-defined colors tests passed")

def test_normalize_color():
    """Test normalize_color utility function"""
    print("\n=== normalize_color Function ===")
    
    # From Color object
    color_obj = Color.red()
    normalized = normalize_color(color_obj)
    assert len(normalized) == 4 and normalized[0] == 1.0, "normalize Color object failed"
    
    # From tuple
    tuple_color = (1.0, 0.0, 0.0, 1.0)
    normalized = normalize_color(tuple_color)
    assert len(normalized) == 4 and normalized[0] == 1.0, "normalize tuple failed"
    
    # From constant
    normalized = normalize_color(RED)
    assert len(normalized) == 4 and normalized[0] == 1.0, "normalize constant failed"
    
    print("✓ normalize_color tests passed")

def test_lerp_colors():
    """Test color interpolation"""
    print("\n=== lerp_colors Function ===")
    
    # Interpolate red to blue
    color1 = RED
    color2 = BLUE
    
    # At t=0, should be red
    result = lerp_colors(color1, color2, 0.0)
    assert abs(result[0] - 1.0) < 0.01 and abs(result[2]) < 0.01, "lerp at t=0 failed"
    
    # At t=1, should be blue
    result = lerp_colors(color1, color2, 1.0)
    assert abs(result[0]) < 0.01 and abs(result[2] - 1.0) < 0.01, "lerp at t=1 failed"
    
    # At t=0.5, should be purple-ish
    result = lerp_colors(color1, color2, 0.5)
    assert result[0] > 0.4 and result[2] > 0.4, "lerp at t=0.5 failed"
    
    print("✓ lerp_colors tests passed")

def test_gradient():
    """Test gradient generation"""
    print("\n=== gradient Function ===")
    
    # Two color gradient (returns steps+1 colors for inclusive range)
    colors = gradient([RED, BLUE], steps=10)
    assert len(colors) == 11, f"Gradient length incorrect: {len(colors)} (expected 11 for steps=10)"
    
    # First should be red-ish
    assert colors[0][0] > 0.8, "Gradient start color incorrect"
    
    # Last should be blue-ish
    assert colors[-1][2] > 0.8, "Gradient end color incorrect"
    
    # Multi-color gradient (returns exact steps for multi-color)
    colors = gradient([RED, GREEN, BLUE], steps=15)
    assert len(colors) == 15, f"Multi-color gradient length incorrect: {len(colors)}"
    
    print("✓ gradient tests passed")

def test_color_interpolation():
    """Test Color.lerp method"""
    print("\n=== Color Interpolation ===")
    
    red = Color.red()
    blue = Color.blue()
    
    # Lerp between colors
    purple = red.lerp(blue, 0.5)
    assert purple.r > 0.4 and purple.b > 0.4, "Color.lerp failed"
    
    # Edge cases
    same_as_red = red.lerp(blue, 0.0)
    assert abs(same_as_red.r - 1.0) < 0.01, "Color.lerp at t=0 failed"
    
    same_as_blue = red.lerp(blue, 1.0)
    assert abs(same_as_blue.b - 1.0) < 0.01, "Color.lerp at t=1 failed"
    
    print("✓ Color interpolation tests passed")

def test_color_properties():
    """Test color property methods"""
    print("\n=== Color Properties ===")
    
    color = Color.red()
    
    # With alpha
    semi = color.with_alpha(0.5)
    assert abs(semi.a - 0.5) < 0.01, "with_alpha failed"
    
    # Lighten/darken
    lighter = color.lighten(0.2)
    assert isinstance(lighter, Color), "lighten failed"
    
    darker = color.darken(0.2)
    assert isinstance(darker, Color), "darken failed"
    
    print("✓ Color properties tests passed")

def run_all_tests():
    """Run all color tests"""
    print("\n" + "="*50)
    print("Running e2D Color Tests (Headless)")
    print("="*50)
    
    test_color_creation()
    test_color_operations()
    test_color_conversion()
    test_predefined_colors()
    test_normalize_color()
    test_lerp_colors()
    test_gradient()
    test_color_interpolation()
    test_color_properties()
    
    print("\n" + "="*50)
    print("✓ ALL COLOR TESTS PASSED")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
