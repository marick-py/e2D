"""
Unit tests for e2D UI system (headless — no window required).

Covers:
  Phase 1:
  - Pivot  class: presets, custom, from_vector, offset, __eq__, __hash__, __repr__
  - resolve_pivot()  backward-compat helper
  - _PIVOTS_ENUM_MAP
  - UITheme dataclass (DARK_THEME / LIGHT_THEME)
  - UIElement base class (position, size, pivot, visibility, z_index, parent/child tree)

  Phase 2:
  - Button: instantiation, focusable flag, text property, event hooks, on_click callback
  - Switch: instantiation, value property, toggle(), on_change callback, mouse/key events
  - Checkbox: instantiation, value property, toggle(), on_change callback
  - Slider: instantiation, value clamping/snapping, _to_frac/_from_frac math, on_change
  - RangeSlider: instantiation, handle clamping, low/high value props, on_change
"""

from e2D._pivot import Pivot, resolve_pivot, _PIVOTS_ENUM_MAP
from e2D.ui.theme import UITheme, DARK_THEME, LIGHT_THEME
from e2D.ui.base import UIElement
from e2D.ui.button import Button
from e2D.ui.toggle import Switch, Checkbox
from e2D.ui.slider import Slider, RangeSlider
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
# Phase 2 — Button (headless)
# ---------------------------------------------------------------------------

def test_button_instantiation():
    """Button can be created without a window."""
    print("\n=== Button Instantiation ===")

    btn = Button()
    assert btn._focusable is True
    assert btn.text == "Button"
    assert btn.enabled is True
    assert btn.visible is True
    assert btn._is_hovered is False
    assert btn._is_pressed is False

    btn2 = Button("Go!", animated=False)
    assert btn2.text == "Go!"
    assert btn2.animated is False

    print("✓ Button instantiation tests passed")


def test_button_text_property():
    """Button text property getter and setter work before _build."""
    print("\n=== Button text property ===")

    btn = Button("Hello")
    assert btn.text == "Hello"

    # Setter updates _text; _label is None until _build so no GPU call needed
    btn.text = "World"
    assert btn.text == "World"

    print("✓ Button text property tests passed")


def test_button_focusable():
    """Button sets _focusable = True and respects UIElement focus hooks."""
    print("\n=== Button focusable ===")

    btn = Button()
    assert btn._focusable
    assert btn._focused is False

    btn.on_focus()
    assert btn._focused is True

    btn.on_blur()
    assert btn._focused is False

    print("✓ Button focusable tests passed")


def test_button_hover_events():
    """Button tracks hover state via on_hover_enter / on_hover_exit."""
    print("\n=== Button hover events ===")

    btn = Button()
    assert btn._is_hovered is False

    btn.on_hover_enter()
    assert btn._is_hovered is True

    btn.on_hover_exit()
    assert btn._is_hovered is False

    print("✓ Button hover event tests passed")


def test_button_on_click():
    """Button calls on_click when released while hovered."""
    print("\n=== Button on_click ===")

    fired = []
    btn = Button("Click", on_click=lambda: fired.append(1),
                 position=V2(0, 0), size=V2(100, 40))

    # Press + release inside bounds → fires callback
    btn.on_mouse_press(50, 20)
    assert btn._is_pressed is True

    btn.on_mouse_release(50, 20)   # (50,20) inside (0,0,100,40)
    assert len(fired) == 1
    assert btn._is_pressed is False

    # Press then release outside bounds → no callback
    btn.on_mouse_press(50, 20)
    btn.on_mouse_release(200, 200)  # clearly outside
    assert len(fired) == 1          # still 1, not fired again

    print("✓ Button on_click tests passed")


def test_button_disabled():
    """Disabled button does not fire on_click."""
    print("\n=== Button disabled ===")

    fired = []
    btn = Button("X", on_click=lambda: fired.append(1),
                 position=V2(0, 0), size=V2(100, 40), enabled=False)

    btn.on_mouse_press(50, 20)
    btn.on_mouse_release(50, 20)
    assert len(fired) == 0

    print("✓ Button disabled tests passed")


# ---------------------------------------------------------------------------
# Phase 2 — Switch (headless)
# ---------------------------------------------------------------------------

def test_switch_instantiation():
    """Switch can be created without a window."""
    print("\n=== Switch Instantiation ===")

    sw = Switch()
    assert sw._focusable is True
    assert sw.value is False
    assert sw._thumb_t == 0.0

    sw_on = Switch(value=True)
    assert sw_on.value is True
    assert sw_on._thumb_t == 1.0

    print("✓ Switch instantiation tests passed")


def test_switch_toggle():
    """Switch.toggle() flips the value."""
    print("\n=== Switch toggle ===")

    sw = Switch(value=False)
    sw.toggle()
    assert sw.value is True
    sw.toggle()
    assert sw.value is False

    print("✓ Switch toggle tests passed")


def test_switch_on_change():
    """Switch calls on_change with the new boolean value."""
    print("\n=== Switch on_change ===")

    log = []
    sw = Switch(value=False, on_change=lambda v: log.append(v))

    sw.toggle()
    assert log == [True]

    sw.value = False
    assert log == [True, False]

    # Setting the same value again does NOT fire
    sw.value = False
    assert log == [True, False]

    print("✓ Switch on_change tests passed")


def test_switch_mouse_release():
    """Switch toggles on mouse release inside its bounds."""
    print("\n=== Switch mouse release ===")

    sw = Switch(value=False, position=V2(0, 0), size=V2(52, 28))
    assert sw.value is False

    sw.on_mouse_release(26, 14)   # centre of the switch — inside
    assert sw.value is True

    sw.on_mouse_release(200, 200)  # outside — no toggle
    assert sw.value is True

    print("✓ Switch mouse release tests passed")


def test_switch_disabled():
    """Disabled switch does not toggle."""
    print("\n=== Switch disabled ===")

    sw = Switch(value=False, position=V2(0, 0), size=V2(52, 28), enabled=False)
    sw.on_mouse_release(26, 14)
    assert sw.value is False

    print("✓ Switch disabled tests passed")


# ---------------------------------------------------------------------------
# Phase 2 — Checkbox (headless)
# ---------------------------------------------------------------------------

def test_checkbox_instantiation():
    """Checkbox can be created without a window."""
    print("\n=== Checkbox Instantiation ===")

    cb = Checkbox()
    assert cb._focusable is True
    assert cb.value is False
    assert cb._check_t == 0.0

    cb2 = Checkbox(value=True)
    assert cb2.value is True
    assert cb2._check_t == 1.0

    print("✓ Checkbox instantiation tests passed")


def test_checkbox_toggle():
    """Checkbox.toggle() flips the value and calls on_change."""
    print("\n=== Checkbox toggle ===")

    log = []
    cb = Checkbox(value=False, on_change=log.append)

    cb.toggle()
    assert cb.value is True
    assert log == [True]

    cb.toggle()
    assert cb.value is False
    assert log == [True, False]

    print("✓ Checkbox toggle tests passed")


def test_checkbox_mouse_release():
    """Checkbox toggles on mouse release inside its bounds."""
    print("\n=== Checkbox mouse release ===")

    cb = Checkbox(value=False, position=V2(0, 0), size=V2(24, 24))
    cb.on_mouse_release(12, 12)  # inside
    assert cb.value is True

    cb.on_mouse_release(100, 100)  # outside — no toggle
    assert cb.value is True

    print("✓ Checkbox mouse release tests passed")


# ---------------------------------------------------------------------------
# Phase 2 — Slider (headless math)
# ---------------------------------------------------------------------------

def test_slider_instantiation():
    """Slider can be created without a window."""
    print("\n=== Slider Instantiation ===")

    sl = Slider(0, 100)
    assert sl._focusable is True
    assert sl.start == 0.0
    assert sl.end   == 100.0
    assert sl.value == 0.0        # default value = start

    sl2 = Slider(0, 100, value=50)
    assert sl2.value == 50.0

    # Invalid range auto-corrected
    sl3 = Slider(5, 5)
    assert sl3.end > sl3.start

    print("✓ Slider instantiation tests passed")


def test_slider_value_clamping():
    """Setting Slider.value outside the range clamps silently."""
    print("\n=== Slider value clamping ===")

    sl = Slider(0, 100)
    sl.value = 150
    assert sl.value == 100.0

    sl.value = -50
    assert sl.value == 0.0

    print("✓ Slider value clamping tests passed")


def test_slider_step_snapping():
    """Slider snaps to step increments on construction and value assignment."""
    print("\n=== Slider step snapping ===")

    sl = Slider(0, 100, step=10, value=37)
    assert sl.value == 40.0   # nearest step

    sl.value = 23
    assert sl.value == 20.0

    sl.value = 100
    assert sl.value == 100.0

    print("✓ Slider step snapping tests passed")


def test_slider_frac_math():
    """Slider _to_frac / _from_frac round-trip is accurate."""
    print("\n=== Slider frac math ===")

    sl = Slider(0, 200)

    assert sl._to_frac(0)   == 0.0
    assert sl._to_frac(100) == 0.5
    assert sl._to_frac(200) == 1.0

    assert sl._from_frac(0.0) == 0.0
    assert sl._from_frac(0.5) == 100.0
    assert sl._from_frac(1.0) == 200.0

    # Fractional out of range is clamped
    assert sl._from_frac(2.0) == 200.0
    assert sl._from_frac(-1.0) == 0.0

    print("✓ Slider frac math tests passed")


def test_slider_on_change():
    """Slider.value setter fires on_change when value changes."""
    print("\n=== Slider on_change ===")

    log = []
    sl = Slider(0, 100, on_change=log.append)

    sl.value = 50
    assert log == [50.0]

    # Same value again — no callback
    sl.value = 50
    assert log == [50.0]

    sl.value = 0
    assert log == [50.0, 0.0]

    print("✓ Slider on_change tests passed")


def test_slider_orientation():
    """Slider stores orientation correctly."""
    print("\n=== Slider orientation ===")

    sl_h = Slider(orientation='horizontal')
    assert sl_h.orientation == 'horizontal'

    sl_v = Slider(orientation='vertical')
    assert sl_v.orientation == 'vertical'

    print("✓ Slider orientation tests passed")


# ---------------------------------------------------------------------------
# Phase 2 — RangeSlider (headless math)
# ---------------------------------------------------------------------------

def test_range_slider_instantiation():
    """RangeSlider can be created without a window."""
    print("\n=== RangeSlider Instantiation ===")

    rs = RangeSlider(0, 100)
    assert rs._focusable is True
    assert rs.start == 0.0
    assert rs.end   == 100.0
    assert rs.low_value  == 0.0
    assert rs.high_value == 100.0

    rs2 = RangeSlider(0, 100, low_value=20, high_value=80)
    assert rs2.low_value  == 20.0
    assert rs2.high_value == 80.0

    print("✓ RangeSlider instantiation tests passed")


def test_range_slider_clamping():
    """RangeSlider handles don't cross and stay in range."""
    print("\n=== RangeSlider clamping ===")

    rs = RangeSlider(0, 100, low_value=30, high_value=70)

    # low can't exceed high
    rs.low_value = 90
    assert rs.low_value <= rs.high_value

    # high can't go below low
    rs2 = RangeSlider(0, 100, low_value=30, high_value=70)
    rs2.high_value = 10
    assert rs2.high_value >= rs2.low_value

    # Out-of-range clamped
    rs3 = RangeSlider(0, 100, low_value=20, high_value=80)
    rs3.low_value = -50
    assert rs3.low_value == 0.0
    rs3.high_value = 200
    assert rs3.high_value == 100.0

    print("✓ RangeSlider clamping tests passed")


def test_range_slider_on_change():
    """RangeSlider fires on_change with (low, high) tuple."""
    print("\n=== RangeSlider on_change ===")

    log = []
    rs = RangeSlider(0, 100, low_value=20, high_value=80,
                     on_change=lambda lo, hi: log.append((lo, hi)))

    rs.low_value = 30
    assert log == [(30.0, 80.0)]

    rs.high_value = 60
    assert log == [(30.0, 80.0), (30.0, 60.0)]

    # Same value — no callback
    rs.high_value = 60
    assert len(log) == 2

    print("✓ RangeSlider on_change tests passed")


def test_range_slider_step():
    """RangeSlider snaps handles to step increments."""
    print("\n=== RangeSlider step ===")

    rs = RangeSlider(0, 100, step=5, low_value=12, high_value=88)
    assert rs.low_value  == 10.0
    assert rs.high_value == 90.0

    rs.low_value = 23
    assert rs.low_value == 25.0

    print("✓ RangeSlider step tests passed")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_tests():
    print("\n" + "=" * 50)
    print("Running e2D UI Tests (Headless)")
    print("=" * 50)

    # Phase 1
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

    # Phase 2
    test_button_instantiation()
    test_button_text_property()
    test_button_focusable()
    test_button_hover_events()
    test_button_on_click()
    test_button_disabled()
    test_switch_instantiation()
    test_switch_toggle()
    test_switch_on_change()
    test_switch_mouse_release()
    test_switch_disabled()
    test_checkbox_instantiation()
    test_checkbox_toggle()
    test_checkbox_mouse_release()
    test_slider_instantiation()
    test_slider_value_clamping()
    test_slider_step_snapping()
    test_slider_frac_math()
    test_slider_on_change()
    test_slider_orientation()
    test_range_slider_instantiation()
    test_range_slider_clamping()
    test_range_slider_on_change()
    test_range_slider_step()

    print("\n" + "=" * 50)
    print("✓ ALL UI TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
