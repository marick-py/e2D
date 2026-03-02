"""
Unit tests for e2D UI system (headless — no window required).

Covers:
  - Pivot  class: presets, custom, from_vector, offset, __eq__, __hash__, __repr__
  - resolve_pivot()  backward-compat helper
  - _PIVOTS_ENUM_MAP
  - UITheme dataclass (DARK_THEME / LIGHT_THEME)
  - UIElement base class (position, size, pivot, visibility, z_index, parent/child tree)
"""

from e2D._pivot import Pivot, resolve_pivot, _PIVOTS_ENUM_MAP
from e2D.ui.theme import UITheme, DARK_THEME, LIGHT_THEME
from e2D.ui.base import UIElement
from e2D.vectors import Vector2D, V2
from e2D.colors import Color


# ---------------------------------------------------------------------------
# Pivot
# ---------------------------------------------------------------------------

def test_pivot_presets():
    """All 9 preset pivots exist and have correct (x, y) values."""
    print("\n=== Pivot Presets ===")

    expected = {
        'TOP_LEFT':      (0.0, 0.0),
        'TOP_MIDDLE':    (0.5, 0.0),
        'TOP_RIGHT':     (1.0, 0.0),
        'LEFT':          (0.0, 0.5),
        'CENTER':        (0.5, 0.5),
        'RIGHT':         (1.0, 0.5),
        'BOTTOM_LEFT':   (0.0, 1.0),
        'BOTTOM_MIDDLE': (0.5, 1.0),
        'BOTTOM_RIGHT':  (1.0, 1.0),
    }
    for name, (ex, ey) in expected.items():
        p = getattr(Pivot, name)
        assert isinstance(p, Pivot), f"Pivot.{name} should be a Pivot instance"
        assert p.x == ex and p.y == ey, f"Pivot.{name}: expected ({ex},{ey}), got ({p.x},{p.y})"

    print("✓ Pivot preset tests passed")


def test_pivot_custom():
    """Pivot.custom() creates a pivot with the given coordinates."""
    print("\n=== Pivot.custom ===")

    p = Pivot.custom(0.3, 0.7)
    assert isinstance(p, Pivot)
    assert p.x == 0.3
    assert p.y == 0.7
    assert 'custom' in repr(p).lower()

    # Floats are coerced
    p2 = Pivot.custom(0, 1)
    assert p2.x == 0.0 and p2.y == 1.0

    print("✓ Pivot.custom tests passed")


def test_pivot_from_vector():
    """Pivot.from_vector() accepts a Vector2D."""
    print("\n=== Pivot.from_vector ===")

    v = V2(0.25, 0.75)
    p = Pivot.from_vector(v)
    assert p.x == 0.25 and p.y == 0.75

    print("✓ Pivot.from_vector tests passed")


def test_pivot_offset():
    """offset() returns the correct translation tuple."""
    print("\n=== Pivot.offset ===")

    p = Pivot.CENTER   # (0.5, 0.5)
    ox, oy = p.offset(100.0, 60.0)
    assert ox == -50.0, f"Expected -50.0, got {ox}"
    assert oy == -30.0, f"Expected -30.0, got {oy}"

    tl = Pivot.TOP_LEFT   # (0.0, 0.0)
    assert tl.offset(200, 150) == (0.0, 0.0)

    br = Pivot.BOTTOM_RIGHT   # (1.0, 1.0)
    assert br.offset(200, 150) == (-200.0, -150.0)

    print("✓ Pivot.offset tests passed")


def test_pivot_equality():
    """Two pivots with the same (x, y) compare equal regardless of name."""
    print("\n=== Pivot Equality ===")

    a = Pivot.custom(0.5, 0.5)
    b = Pivot.CENTER
    assert a == b, "custom(0.5,0.5) should equal Pivot.CENTER"

    c = Pivot.custom(0.0, 0.0)
    d = Pivot.TOP_LEFT
    assert c == d

    # Different pivots are not equal
    assert Pivot.TOP_LEFT != Pivot.BOTTOM_RIGHT

    print("✓ Pivot equality tests passed")


def test_pivot_hash():
    """Pivots with the same (x, y) must share the same hash (usable as dict keys)."""
    print("\n=== Pivot Hash ===")

    mapping = {Pivot.CENTER: 'center'}
    key = Pivot.custom(0.5, 0.5)
    assert mapping[key] == 'center', "dict lookup by equal pivot should work"

    assert hash(Pivot.TOP_LEFT) == hash(Pivot.custom(0.0, 0.0))

    print("✓ Pivot hash tests passed")


def test_pivot_repr():
    """__repr__ includes the pivot name or coordinates."""
    print("\n=== Pivot __repr__ ===")

    assert 'TOP_LEFT' in repr(Pivot.TOP_LEFT)
    assert 'CENTER' in repr(Pivot.CENTER)
    custom_repr = repr(Pivot.custom(0.1, 0.9))
    assert 'custom' in custom_repr.lower() or '0.1' in custom_repr

    print("✓ Pivot __repr__ tests passed")


# ---------------------------------------------------------------------------
# resolve_pivot / _PIVOTS_ENUM_MAP
# ---------------------------------------------------------------------------

def test_resolve_pivot():
    """resolve_pivot accepts Pivot instances and returns them unchanged."""
    print("\n=== resolve_pivot ===")

    # Pivot instances pass through
    for name in ('TOP_LEFT', 'CENTER', 'BOTTOM_RIGHT', 'LEFT', 'RIGHT'):
        p = getattr(Pivot, name)
        result = resolve_pivot(p)
        assert result is p or result == p, f"resolve_pivot({name}) should return equal pivot"

    # Custom pivot preserves values
    cp = Pivot.custom(0.33, 0.66)
    assert resolve_pivot(cp) == cp

    print("✓ resolve_pivot tests passed")


def test_pivot_enum_map():
    """_PIVOTS_ENUM_MAP is a dict with int keys → Pivot values."""
    print("\n=== _PIVOTS_ENUM_MAP ===")

    assert isinstance(_PIVOTS_ENUM_MAP, dict), "_PIVOTS_ENUM_MAP should be a dict"
    for k, v in _PIVOTS_ENUM_MAP.items():
        assert isinstance(k, int), f"Key {k!r} should be int"
        assert isinstance(v, Pivot), f"Value for key {k} should be Pivot"

    print("✓ _PIVOTS_ENUM_MAP tests passed")


# ---------------------------------------------------------------------------
# UITheme
# ---------------------------------------------------------------------------

def test_uitheme_instantiation():
    """UITheme can be created with defaults."""
    print("\n=== UITheme Instantiation ===")

    theme = UITheme()
    assert isinstance(theme.primary, Color)
    assert isinstance(theme.bg_normal, Color)
    assert isinstance(theme.text_color, Color)
    assert isinstance(theme.font, str)
    assert isinstance(theme.font_size, int)
    assert theme.font_size > 0
    assert isinstance(theme.border_width, float)
    assert isinstance(theme.corner_radius, float)
    assert isinstance(theme.animate_hover, bool)
    assert theme.animation_speed > 0

    print("✓ UITheme instantiation tests passed")


def test_dark_light_theme_constants():
    """DARK_THEME and LIGHT_THEME are distinct UITheme instances."""
    print("\n=== DARK_THEME / LIGHT_THEME Constants ===")

    assert isinstance(DARK_THEME, UITheme)
    assert isinstance(LIGHT_THEME, UITheme)

    # They should differ in at least background colour
    assert DARK_THEME.bg_normal != LIGHT_THEME.bg_normal, \
        "DARK_THEME and LIGHT_THEME should have different bg_normal"

    # Dark theme should have darker background
    dark_brightness = DARK_THEME.bg_normal.r + DARK_THEME.bg_normal.g + DARK_THEME.bg_normal.b
    light_brightness = LIGHT_THEME.bg_normal.r + LIGHT_THEME.bg_normal.g + LIGHT_THEME.bg_normal.b
    assert dark_brightness < light_brightness, "DARK_THEME background should be darker"

    # Text colours should be inverted
    dark_text_brightness = DARK_THEME.text_color.r
    light_text_brightness = LIGHT_THEME.text_color.r
    assert dark_text_brightness > light_text_brightness, \
        "DARK_THEME text should be lighter than LIGHT_THEME text"

    print("✓ DARK_THEME / LIGHT_THEME constant tests passed")


def test_uitheme_custom():
    """UITheme accepts custom colour overrides."""
    print("\n=== UITheme Custom ===")

    red = Color(1.0, 0.0, 0.0, 1.0)
    theme = UITheme(primary=red, font_size=24)
    assert theme.primary == red
    assert theme.font_size == 24
    # Other fields retain defaults
    assert isinstance(theme.bg_normal, Color)

    print("✓ UITheme custom tests passed")


# ---------------------------------------------------------------------------
# UIElement (headless)
# ---------------------------------------------------------------------------

def test_uielement_instantiation():
    """UIElement can be created without a window or renderer."""
    print("\n=== UIElement Instantiation ===")

    el = UIElement()
    assert isinstance(el.pivot, Pivot)
    assert isinstance(el.visible, bool)
    assert isinstance(el.enabled, bool)
    assert el.visible is True
    assert el.enabled is True
    assert el.z_index == 0
    assert el.opacity == 1.0

    print("✓ UIElement instantiation tests passed")


def test_uielement_position_size():
    """UIElement position and size are settable via constructor and properties."""
    print("\n=== UIElement Position / Size ===")

    el = UIElement(position=(10.0, 20.0), size=(200.0, 100.0))
    assert el.position.x == 10.0
    assert el.position.y == 20.0
    assert el.size.x == 200.0
    assert el.size.y == 100.0

    # Tuple input
    el2 = UIElement(position=(0, 0), size=(50, 50))
    assert el2.size.x == 50.0

    # Vector2D input
    el3 = UIElement(position=V2(5.0, 15.0), size=V2(80.0, 40.0))
    assert el3.position.y == 15.0

    print("✓ UIElement position/size tests passed")


def test_uielement_pivot():
    """UIElement stores pivot correctly."""
    print("\n=== UIElement Pivot ===")

    el = UIElement(pivot=Pivot.CENTER)
    assert el.pivot == Pivot.CENTER

    el2 = UIElement(pivot=Pivot.BOTTOM_RIGHT)
    assert el2.pivot == Pivot.BOTTOM_RIGHT

    print("✓ UIElement pivot tests passed")


def test_uielement_visibility():
    """UIElement visible / enabled flags affect each other correctly."""
    print("\n=== UIElement Visibility ===")

    el = UIElement(visible=False, enabled=False)
    assert not el.visible
    assert not el.enabled

    el.visible = True
    assert el.visible

    print("✓ UIElement visibility tests passed")


def test_uielement_z_index():
    """UIElement z_index is stored correctly."""
    print("\n=== UIElement z_index ===")

    el = UIElement(z_index=5)
    assert el.z_index == 5

    el.z_index = -1
    assert el.z_index == -1

    print("✓ UIElement z_index tests passed")


def test_uielement_parent_child():
    """UIElement supports a parent/child hierarchy."""
    print("\n=== UIElement Parent/Child ===")

    parent = UIElement()
    child1 = UIElement()
    child2 = UIElement()

    parent.add_child(child1)
    parent.add_child(child2)

    assert child1 in parent._children
    assert child2 in parent._children
    assert child1._parent is parent
    assert child2._parent is parent

    parent.remove_child(child1)
    assert child1 not in parent._children
    assert child1._parent is None

    print("✓ UIElement parent/child tests passed")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_tests():
    print("\n" + "=" * 50)
    print("Running e2D UI Tests (Headless)")
    print("=" * 50)

    test_pivot_presets()
    test_pivot_custom()
    test_pivot_from_vector()
    test_pivot_offset()
    test_pivot_equality()
    test_pivot_hash()
    test_pivot_repr()
    test_resolve_pivot()
    test_pivot_enum_map()
    test_uitheme_instantiation()
    test_dark_light_theme_constants()
    test_uitheme_custom()
    test_uielement_instantiation()
    test_uielement_position_size()
    test_uielement_pivot()
    test_uielement_visibility()
    test_uielement_z_index()
    test_uielement_parent_child()

    print("\n" + "=" * 50)
    print("✓ ALL UI TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
