# e2D Engine — Claude Code Agent Project Specification
# FOR AGENT USE: Read this ENTIRE document before writing a single line of code.
# CRITICAL RULES at the bottom. Violation = wasted work.

---

## PROJECT OVERVIEW

e2D is a high-performance Python 2D graphics and simulation library built on top of:
- **ModernGL** — OpenGL 4.3+ rendering context
- **GLFW** — windowing and input
- **Cython** — compiled extensions for hot-path math (`cvectors.pyx`, `ccolors.pyx`)
- **NumPy** — GPU data transfer and batch operations
- **Pillow** — font/glyph atlas generation for text rendering

The project lives at:
`c:\Users\User\OneDrive\MyDev\Python\MyModules\e2D_2.0\e2D\`

**Phases 1, 2, 3, 4, the Theme Rebuild, Bug Fixes, and Debug Mode are COMPLETE.** This document covers Phases 5–6.

---

## CURRENT FOLDER STRUCTURE (post Phase 1)

```
e2D/
├── ccolors.c
├── ccolors.cp313-win_amd64.pyd
├── ccolors.pyi
├── ccolors.pyx
├── colors.py
├── core/
│   ├── camera.py
│   ├── utils.py
│   └── window.py
├── cvectors.c
├── cvectors.cp313-win_amd64.pyd
├── cvectors.pxd
├── cvectors.pyi
├── cvectors.pyx
├── input.py
├── palette.py
├── plot.py
├── recorder.py
├── shaders/
│   ├── curve_fragment.glsl
│   ├── curve_vertex.glsl
│   ├── line_instanced_vertex.glsl
│   ├── plot_grid_fragment.glsl
│   ├── plot_grid_vertex.glsl
│   ├── segment_fragment.glsl
│   ├── segment_vertex.glsl
│   ├── stream_fragment.glsl
│   ├── stream_shift_compute.glsl
│   └── stream_vertex.glsl
├── shapes.py
├── template.py
├── text.py
├── ui/
│   ├── base.py
│   ├── button.py        ← Phase 2
│   ├── containers.py    ← Phase 4
│   ├── input_field.py   ← Phase 3
│   ├── label.py
│   ├── manager.py
│   ├── slider.py        ← Phase 2
│   ├── theme.py
│   ├── toggle.py        ← Phase 2
│   └── __init__.py
├── utils.py
├── vectors.py
├── _constants.py
├── _pivot.py
├── _types.py
├── __init__.py
└── __main__.py
```

---

## MANDATORY AGENT BEHAVIOR

Before ANY code:

1. **READ every file you are about to modify or import from.** Use the Read tool.
2. **NEVER assume** what a file contains based on its name. Always read first.
3. **NEVER create a file** that already exists without reading the existing one first.
4. **If you are uncertain** about the name of a class, function, import, or variable in any existing file — READ THAT FILE before proceeding.
5. **Ask** (output a question, stop) if something is structurally ambiguous and cannot be resolved by reading.
6. **Do not duplicate** existing functionality. Before implementing anything, check if it already exists somewhere in the codebase.

---

## WHAT WAS BUILT IN PHASES 1 AND 2

### Phase 1 (complete)

These files were created or heavily modified in Phase 1:

**New files:**
- `ui/base.py` — `Pivot` class with 9 preset positions + `Pivot.custom(x, y)` + `Pivot.from_vector()`, and `UIElement` base class with: position, size, pivot, anchor-based layout, z-index, opacity, focus handling, parent-child tree structure
- `ui/theme.py` — `UITheme` dataclass with default colors/fonts/borders/spacing/animation settings; `DARK_THEME` and `LIGHT_THEME` presets
- `ui/label.py` — `Label(UIElement)` with rich text segments: `Label("Normal", ("Bold", BOLD_STYLE))`, per-atlas draw groups, GPU-side position/rotation/opacity via shader uniforms
- `ui/manager.py` — `UIManager` with `add()`/`remove()`, `label()` factory, focus/tab navigation, z-ordered drawing, input dispatch, `wants_keyboard`/`wants_mouse` flags
- `ui/__init__.py` — re-exports all UI symbols
- `_pivot.py` — standalone Pivot file (READ this to understand the exact Pivot API before using it in Phases 2+)

**Modified files:**
- `text.py` — baseline bug fixed (descender characters like g,j,p,q,y,(),@,[],_ etc. no longer pushed up), new shader uniforms `u_pivot_local`/`u_screen_pos`/`u_rotation`/`u_opacity`, multi-line `\n` support, `line_spacing`/`letter_spacing` in TextStyle
- `input.py` — `Keyboard` class now has `char_buffer`, `is_consumed` flag, `get_chars()` helper, `_on_char()` GLFW character callback
- `__init__.py` — `UIManager` instantiated in `RootEnv.__init__`, char callback registered in `loop()`, `ui.process_input()` / `ui.update()` / `ui.draw()` in main loop, FPS/UPS counters, `_on_resize` notifies UIManager, Pivot/UIManager/UITheme/Label in `__all__`

### Phase 2 (complete)

These files were created or heavily modified in Phase 2:

**New files:**
- `ui/button.py` — `Button(UIElement)` with animated state transitions (normal/hover/pressed/disabled/focused), internal `Label` for text, `on_click` callback, Space/Enter key activation; factory shortcut: `env.ui.button(...)`
- `ui/toggle.py` — `Switch(UIElement)` (pill track + animated sliding thumb, `value`/`toggle()`/`on_change`) and `Checkbox(UIElement)` (square box + animated ✓ checkmark); factory shortcuts: `env.ui.switch(...)` / `env.ui.checkbox(...)`
- `ui/slider.py` — `Slider(UIElement)` (horizontal/vertical, `start`/`end`/`step`/`value`/`on_change`, Ctrl=snap, Shift=fine drag, optional labels) and `RangeSlider(UIElement)` (dual handle, `low_value`/`high_value`/`on_change`); factory shortcuts: `env.ui.slider(...)` / `env.ui.range_slider(...)`

**Modified files:**
- `ui/base.py` — added 6 interaction event hook stubs to `UIElement`: `on_hover_enter()`, `on_hover_exit()`, `on_mouse_press(mx, my)`, `on_mouse_release(mx, my)`, `on_mouse_drag(mx, my, dx, dy)`, `on_key_press(key)`; added `tab_index: int = 0` constructor parameter (sets `self._tab_index`) so widgets can declare their focus-cycle order at creation time
- `ui/manager.py` — constructor now accepts `shape_renderer: ShapeRenderer` (stored as `self.shape_renderer`); added `_pressed_on`, `_keyboard`, `_mouse`, `_prev_mx/y` fields; `process_input()` completely rewritten to dispatch all six event hooks using `MouseButtons.LEFT` checks; `draw()` calls `self.shape_renderer.flush_queue()` after all elements render; five new factory methods: `button()`, `switch()`, `checkbox()`, `slider()`, `range_slider()`
- `ui/__init__.py` — exports `Button`, `Switch`, `Checkbox`, `Slider`, `RangeSlider`
- `__init__.py` — `UIManager(...)` now receives `self.shape_renderer`; `Button`, `Switch`, `Checkbox`, `Slider`, `RangeSlider` in `__all__`

---

## PHASE 2 — Buttons, Switches, Checkboxes, Sliders, RangeSliders (COMPLETE — do not re-implement)

**Target file location:** `ui/` folder — create new files as needed. Suggested structure:
```
ui/
├── base.py          (already exists — READ before modifying)
├── label.py         (already exists)
├── manager.py       (already exists)
├── theme.py         (already exists)
├── button.py        (NEW)
├── toggle.py        (NEW — contains Switch and Checkbox)
├── slider.py        (NEW — contains Slider and RangeSlider)
└── __init__.py      (already exists — UPDATE exports)
```

### Button

- Inherits from `UIElement` (read `ui/base.py` first)
- Constructor: `Button(text, on_click=None, **kwargs)` where `on_click` is a callable passed by the user, called when button is activated
- **Visual states:** Normal, Hovered, Pressed, Disabled, Focused — each state should have its own configurable style (colors, border, text style, etc.) that defaults to theme values
- Auto-derived defaults: hover = slightly lighter than normal, pressed = slightly darker, using existing `Color` utilities (read `colors.py` before implementing)
- Activation: click with mouse, or Space/Enter when focused — this must go through `UIManager`
- Animations: hover fade-in/fade-out, press animation (scale down slightly) — **toggleable** via `animated=True/False` on init
- Text rendered using existing `text.py` / `Label` system — do NOT reimplement text rendering

### Switch (Pill Toggle)

- Inherits from `UIElement`
- Visual style: iOS/Android pill toggle — a track with a sliding circle/thumb
- States: On, Off, Disabled, Focused
- `on_change: callable = None` — called with the new boolean value when toggled
- `animated=True/False` — toggles the sliding animation
- `value: bool` — readable/settable property
- All colors (track on/off, thumb, border) configurable, defaults to theme

### Checkbox

- Separate class from Switch, also inherits from `UIElement`
- Visual style: square with checkmark (✓) when checked
- Same `on_change`, `animated`, `value` API as Switch
- Checkmark drawn using existing shape/line rendering — do NOT invent a new drawing system
- All colors configurable

### Slider

- Horizontal AND vertical (configurable via `orientation='horizontal'` or `'vertical'`)
- Constructor: `Slider(start, end, step=None, value=None, on_change=None, **kwargs)`
- `start`, `end`: float range
- `step`: if provided, snaps to step increments
- Keyboard modifier behavior when dragging:
  - Normal drag: standard movement
  - Hold **Ctrl**: snap to step (if step is set)
  - Hold **Shift**: fine control (smaller increment per pixel)
- Labels: optional range labels (showing start/end values) and current value label — all toggleable via `show_labels=True/False`
- Animated: thumb movement smooth animation — `animated=True/False`
- All visual parts (track, filled track, thumb, label text style) configurable

### RangeSlider

- Two-handle slider for selecting a min-max range
- Constructor: `RangeSlider(start, end, step=None, low_value=None, high_value=None, on_change=None, **kwargs)`
- `on_change` called with `(low, high)` tuple
- Same step/Ctrl/Shift behavior as Slider
- Handles should not be able to cross each other
- Visual: filled region between the two handles
- Same label toggleability as Slider

### Integration Requirements for Phase 2

- All new elements must be registerable with `UIManager.add()`
- Focus/tab navigation must work for all interactive elements
- Space/Enter activation must work for Button, Switch, Checkbox when focused
- Arrow keys should move Slider/RangeSlider when focused
- Read `ui/manager.py` to understand the existing focus dispatch system before wiring up events
- Update `ui/__init__.py` to export all new classes
- Update `__init__.py` (root) `__all__` to include new UI exports

---

### Phase 4 (complete)

These files were created or modified in Phase 4:

**New files:**
- `ui/containers.py` — `SizeMode` constants (`FIXED`/`PERCENT`/`AUTO`); `Anchor` Godot-style preset tuples; `UIContainer` abstract base with background, padding, `clip_content`, theme-aware `_build()`, `_compute_layout()` hook, `add_child`/`remove_child` that trigger re-layout, `size` property override that triggers re-layout; `VBox` (vertical stack, `spacing`, `align`, `natural_size()` for AUTO); `HBox` (horizontal stack, same); `Grid` (rows × columns, `columns`, `cell_spacing`, `cell_size`); `FreeContainer` (absolute children, anchor propagation); `ScrollContainer` (single content child, vertical/horizontal scroll, scissor clipping, scrollbar track + draggable thumb, `scroll_y`/`scroll_x` properties, `on_scroll` wheel handler)

**Modified files:**
- `ui/base.py` — added `self.size_mode: str = 'fixed'` to `UIElement.__init__`; used by containers to interpret child sizes as FIXED pixels, PERCENT fractions, or AUTO
- `ui/manager.py` — 6 new factory methods: `vbox()`, `hbox()`, `grid()`, `free_container()`, `scroll_container()`
- `ui/__init__.py` — exports `UIContainer`, `VBox`, `HBox`, `Grid`, `FreeContainer`, `ScrollContainer`, `SizeMode`, `Anchor`
- `__init__.py` — same symbols in imports and `__all__`

---

### Phase 3 (complete)

These files were created or heavily modified in Phase 3:

**New files:**
- `ui/input_field.py` — `InputField(UIElement)` (single-line: placeholder, password mode (`*` char), cursor blink, text selection, copy/paste via GLFW clipboard, Ctrl+word-delete, validation + error state, horizontal scroll, **Ctrl+Z/Ctrl+Shift+Z undo/redo**) and `MultiLineInput(UIElement)` (multi-line: Enter inserts newline, Ctrl+Enter submits, Tab inserts spaces, Up/Down arrow line navigation, vertical scroll, auto-expand mode with `min_height`/`max_height`, optional scrollbar, Ctrl+Tab for focus cycle, **Ctrl+Z/Ctrl+Shift+Z undo/redo**)

**Modified files:**
- `ui/base.py` — added `_consumes_tab: bool` flag to `UIElement.__init__`; added `on_char_input(chars: list[str])` and `on_scroll(dy: float)` virtual methods with no-op defaults
- `ui/manager.py` — `__init__` now accepts optional `window` parameter (stored as `self._window`, used for clipboard); `process_input()` updated: Tab forwarded to element if `_consumes_tab` is True (Ctrl+Tab always cycles focus), `on_char_input()` called on focused element each frame with this frame's char buffer, `on_scroll()` dispatched to hovered element; two new factory methods: `input_field()`, `multi_line_input()`
- `ui/__init__.py` — exports `InputField`, `MultiLineInput`
- `__init__.py` — `UIManager(…)` call passes `window=self.window`; `InputField` and `MultiLineInput` in imports and `__all__`

---

## PHASE 3 — InputField and MultiLineInput (COMPLETE — do not re-implement)

**Target files:**
```
ui/
└── input_field.py   (NEW — contains InputField and MultiLineInput)
```

### InputField (single-line)

- Inherits from `UIElement`
- Constructor: `InputField(placeholder='', value='', on_submit=None, validate=None, password=False, **kwargs)`
  - `placeholder`: text shown when empty (styled with a dimmer version of text color)
  - `value`: initial text content
  - `on_submit`: callable called with current text string when Enter is pressed
  - `validate`: callable passed the current string, returns `bool`. Called on Enter — if False, show error state visual, do NOT call `on_submit`
  - `password=True`: renders text as `*` characters (ASCII — the font atlas is ASCII-only, so non-ASCII mask chars are invisible)
- Text editing uses `input.py` `Keyboard.get_chars()` and `Keyboard.char_buffer` system built in Phase 1 — read `input.py` first
- **Cursor:** blinking cursor (configurable blink rate via `cursor_blink_rate` in seconds) when focused. Cursor drawn as a thin vertical line using existing shape renderer
- **Text selection:** click and drag to select. Selected region highlighted with a configurable selection color. `Ctrl+A` selects all
- **Copy/paste:** `Ctrl+C` copies selection, `Ctrl+V` pastes from clipboard (`glfw.get_clipboard_string` / `glfw.set_clipboard_string` — cross-platform: Windows / X11 / Wayland; Linux returns `bytes`, decoded automatically)
- **Undo/redo:** `Ctrl+Z` undoes the last change (up to 100 snapshots, consecutive character inputs are coalesced into one undoable unit); `Ctrl+Shift+Z` redoes. All destructive operations (Backspace, Delete, Ctrl+X, Ctrl+V) push an undo snapshot first.
- **Navigation keys:** Left/Right arrows move cursor, Home/End jump to start/end, Shift+arrows extend selection
- **Backspace/Delete:** remove character before/after cursor, or delete selection if any
- **Max length:** optional `max_length: int = None`
- Visual states: Normal, Focused, Disabled, Error (when validation fails)
- All colors, border, font configurable — defaults from UITheme

### MultiLineInput

- Separate class from InputField, also inherits from `UIElement`
- Same text editing features as InputField (selection, copy/paste, cursor, **undo/redo**)
- Enter key inserts newline instead of submitting
- `on_submit` triggered by `Ctrl+Enter` instead
- **Scrolling:** when text exceeds visible area, scroll vertically. Use mouse wheel when focused/hovered
- **Expand mode:** optional `auto_expand=True` — field grows vertically to fit content instead of scrolling
  - `min_height: float = 0.0` — minimum height in pixels (0 = unconstrained)
  - `max_height: float = 0.0` — maximum height cap in pixels (0 = no cap); once reached, `auto_expand` stops growing and scrolling is enabled transparently
  - When `auto_expand=True` and content fits (not capped), `_scroll_y` is always reset to 0 and `_ensure_cursor_visible` skips scroll adjustment to prevent phantom scroll
- Tab key inserts spaces (configurable `tab_width: int = 4`) — does NOT change focus when inside MultiLineInput; use Ctrl+Tab to change focus
- Visible scrollbar when content overflows (configurable `show_scrollbar=True`)
- **Scissor note:** the bottom pad is excluded from the scissor height so descenders on the bottom-most row are not clipped

### Tab / Focus Navigation

- Tab moves focus to next focusable UIElement in UIManager's focus list
- Shift+Tab moves to previous
- This must go through `UIManager` — read `ui/manager.py` for the existing focus system
- Elements opt into focus chain via a `focusable=True` property on UIElement (check if this already exists in `ui/base.py` before adding)
- When inside a MultiLineInput, Tab inserts spaces and Ctrl+Tab navigates focus

### Integration Requirements for Phase 3

- Hook into existing `Keyboard` char system from `input.py`
- Hook into `UIManager` for focus, `wants_keyboard` flag must be `True` when any InputField/MultiLineInput is focused so the user's game loop knows keyboard is consumed
- Update `ui/__init__.py` and root `__init__.py` exports

---

## THEME SYSTEM REBUILD (COMPLETE — do not re-implement)

These changes were applied on top of Phases 1–3 and are already in the codebase. Read the relevant files before modifying them.

### Summary of changes

**Modified files:**
- `ui/theme.py` — `UITheme` fully filled out; new `bg_window` field; 9 built-in theme constants
- `ui/manager.py` — `theme` is now a **property** with setter that rebuilds all elements
- `ui/label.py` — fully theme-aware with `_explicit_style` / `_raw_segments` tracking
- `ui/button.py` — draw-order fix: `sr.flush_queue()` before `self._label.draw()`
- `ui/slider.py` — draw-order fix: layer params + flush before labels; vertical fill direction fix; range fill rounded caps
- `ui/toggle.py` — draw-order fix: track `layer=0`, thumb `layer=1`
- `ui/__init__.py` — all 9 theme constants exported
- `__init__.py` — all 9 theme constants in `__all__`
- `examples/example_widgets.py` — T key cycles all 9 themes, bg uses `theme.bg_window`
- `examples/example_input_fields.py` — T key cycles all 9 themes, window height 730px, `theme.bg_window`

---

### UITheme fields (complete as of this session)

```python
@dataclass
class UITheme:
    # ── Colors ─────────────────────────────────────────────────────────────
    bg_window:      Color   # window clear color  ← NEW
    bg_normal:      Color   # element background at rest
    bg_hover:       Color
    bg_pressed:     Color
    bg_focused:     Color
    bg_disabled:    Color

    border_color:   Color
    border_width:   float
    corner_radius:  float

    text_color:     Color
    text_disabled:  Color
    placeholder_color: Color
    selection_color: Color
    error_color:    Color
    cursor_color:   Color
    scrollbar_color: Color
    scrollbar_thumb: Color
    track_color:    Color
    fill_color:     Color
    thumb_color:    Color
    thumb_low_color: Color
    thumb_high_color: Color

    primary:        Color   # accent / fill for active state
    secondary:      Color   # accent 2
    accent:         Color   # extra highlight

    # ── Typography ─────────────────────────────────────────────────────────
    font:           str
    font_size:      int

    # ── Spacing ────────────────────────────────────────────────────────────
    padding_x:      float
    padding_y:      float

    # ── Animation ──────────────────────────────────────────────────────────
    animation_speed: float  # t multiplier; 0.0 = no animation

    # ── Checkbox / Switch ──────────────────────────────────────────────────
    checkmark_color: Color
    switch_on_color: Color
    switch_off_color: Color
```

**Rule:** All UIElements must derive their default colors from the active theme. Never hardcode `Color(...)` literals in a widget's `_build()` method — always read from `self._manager.theme`.

---

### UIManager.theme (property)

`theme` is now a Python **property** backed by `self._theme`:

- **Getter:** returns `self._theme`
- **Setter:** stores `self._theme`, then calls `elem._build(self.ctx, self.text_renderer)` on **every registered element** immediately. This guarantees all widgets instantly reflect the new theme's colors, fonts, and sizes.
- After setting a theme, there is no need to call anything else — the rebuild is automatic.
- Default theme: `MONOKAI_THEME` (was `DARK_THEME`)

```python
ui.theme = SOLARIZED_DARK    # rebuilds everything immediately
root.clear_color = ui.theme.bg_window
```

---

### Label theme-awareness

The `Label` class tracks whether its style was set explicitly by the caller:

| Field | Purpose |
|-------|---------|
| `_explicit_style: bool` | `True` if caller passed a concrete `TextStyle`; those labels ignore theme rebuilds |
| `_raw_segments: tuple` | Copy of original init segments, kept in sync by `set_text()` / `set_plain_text()` |
| `default_style: TextStyle / None` | `None` means "follow active theme"; `_build()` re-derives from `theme.font/font_size/text_color` |

When `UIManager.theme` is set it calls `Label._build()` which, for non-explicit labels, re-derives `default_style` from the new theme and re-parses `_raw_segments` so text picks up the new color/font immediately.

---

### Built-in themes

All 9 constants are exported from `e2D.ui.theme`, `e2D.ui`, and `e2D` (root).

```python
from e2D import (
    MONOKAI_THEME, DARK_THEME, LIGHT_THEME,
    SOLARIZED_DARK, SOLARIZED_LIGHT,
    NORD_THEME, DRACULA_THEME, TOKYO_NIGHT_THEME,
    HIGH_CONTRAST,
)
```

| Constant | Palette origin |
|----------|----------------|
| `MONOKAI_THEME` *(default)* | olive-black bg (`#272822`), neon orange/cyan/green, semi-transparent surfaces |
| `DARK_THEME` | neutral Material near-black, purple/teal |
| `LIGHT_THEME` | near-white bg, dark text, muted blue accent |
| `SOLARIZED_DARK` | `#002B36` warm dark, blue+cyan accents |
| `SOLARIZED_LIGHT` | `#FDF6E3` cream bg, blue+cyan accents |
| `NORD_THEME` | `#2E3440` Arctic blue-grey |
| `DRACULA_THEME` | `#282A36` purple-slate, neon pink+purple |
| `TOKYO_NIGHT_THEME` | `#1A1B26` deep navy, soft blue/violet, 8px radius |
| `HIGH_CONTRAST` | pure black/white, yellow accents, 0px radius, instant animation |

---

### Draw-order architecture (ShapeRenderer deferred queue)

`shapes.py` maintains a `_queue` list. `draw_rect`, `draw_circle`, and `draw_line` all take an optional `layer: int = 0` and append `(layer, type_char, ...)` to the queue. When `flush_queue()` is called, the list is sorted by `(layer, type_char)` and then all shapes are rendered in order.

**Critical:** `type_char` is a single letter: `'c'` = circle, `'l'` = line, `'r'` = rect. Alphabetically `'c' < 'l' < 'r'`, so **within the same layer, circles always render before rects**. If a circle (thumb) and a rect (track) are both at `layer=0`, the track rect will draw OVER the circle.

#### Rule for any widget that draws a circle ON TOP of a rect (thumb, switch knob, etc.)

```python
# Background rects (track, fill):  layer=0, type 'r'
sr.draw_rect(..., layer=0)
# Foreground circles (thumb, knob): layer=1, type 'c'
sr.draw_circle(..., layer=1)
# Result: layer 0 'r' renders first, then layer 1 'c' renders on top ✓
```

Applied to:
- `Slider`: track + fill at `layer=0`; thumb circle at `layer=1`
- `RangeSlider`: track + fill at `layer=0`; both handle circles at `layer=1`
- `Switch`: track rect at `layer=0`; thumb circle at `layer=1`

#### Rule for widgets that draw text (Label) on top of a background rect

`Label.draw()` renders immediately and bypasses the deferred queue. `flush_queue()` runs after ALL `UIManager.draw()` element calls. This means: if a widget queues a background rect and then calls `label.draw()`, the rect will render AFTER the text when `flush_queue()` fires — covering the text.

**Fix:** call `sr.flush_queue()` BEFORE any `label.draw()` inside a widget's `draw()` method.

```python
# Button.draw():
sr.draw_rect(...)       # queued at layer=0
sr.flush_queue()        # flush NOW → background renders immediately
self._label.draw(ctx)   # text renders on top ✓
```

Applied to:
- `Button.draw()` — flushes before `self._label.draw()`
- `Slider.draw()` — flushes before optional labels block (`if self.show_labels:`)
- `RangeSlider.draw()` — same

**Any future widget that draws a `Label` (or any immediate text) after queuing shapes must follow this pattern.**

#### Rule for containers drawing children

`UIContainer.draw()` (and all its subclasses) queues the background rect, then **calls `flush_queue()`** before iterating over children. This ensures the background renders first and children appear on top. The same rule applies to `ScrollContainer` which also calls `flush_queue()` after exiting the scissor region.

Applied to:
- `UIContainer.draw()` — flushes background before calling `_draw_children()`
- `ScrollContainer._draw_scrolled()` — flushes after drawing children (before `ctx.scissor = None`)

Any future container subclass that draws shapes before children must call `flush_queue()` in the same positions.

---

### Vertical slider fill direction

The fill rect for a vertical `Slider` was previously computed as:

```python
fill_y = ty + th - fh   # fills upward from bottom → wrong: thumb goes top→down
```

Corrected to:

```python
sr.draw_rect(V2(tx, ty), V2(tw, fh), ...)  # fills downward from top → matches thumb position ✓
```

### RangeSlider rounded fill caps

The fill rect for `RangeSlider` now passes `corner_radius=track_r` so the filled region between the two handles has rounded ends matching the track shape.

---

## BUG FIXES AND IMPORT CORRECTIONS (COMPLETE — do not re-implement)

These corrections were applied on top of Phases 1–3 and the Theme Rebuild. All affected files are already fixed.

### `devices.py` — import fix
- Line 3: `from .types import WindowType` → `from ._types import WindowType`
- The `types.py` alias module does not exist; the canonical file is `_types.py` (underscore-prefixed).

### `text_renderer.py` — import fixes
- `from .types import ...` → `from ._types import ...`
- `from .color_defs import WHITE, BLACK` → `from .palette import WHITE, BLACK`
- `color_defs.py` does not exist; the live color definitions file is `palette.py`.

### `__init__.py` — missing text-style exports
- Added `DEFAULT_16_TEXT_STYLE` and `MONO_16_TEXT_STYLE` to the `from .text import ...` line and to `__all__`.

### `shapes.py` — instanced rect shader half-extents bug
The instanced rect vertex shader was multiplying the unit quad (`-1..+1`) by the **full** pixel size instead of **half-extents**. This made every rect-based widget (buttons, slider tracks, input fields, etc.) render at 2× the intended size and misaligned with its hitbox.

Two shader fixes were applied in the instanced path only (the non-instanced `_generate_rect_vertices` path was already correct):

**Vertex shader (`expanded_size` calculation, ~line 420):**
```glsl
// Before (wrong):
vec2 expanded_size = in_size + expand;
// After (correct — half-extents):
vec2 expanded_size = in_size * 0.5 + expand;
```

**Fragment shader (`roundedBoxSDF` call, ~line 464):**
```glsl
// Before:
float dist = roundedBoxSDF(v_local_pos, v_size, v_radius);
// After:
float dist = roundedBoxSDF(v_local_pos, v_size * 0.5, v_radius);
```

---

## DEBUG MODE (COMPLETE — do not re-implement)

Debug mode is a built-in developer aid accessible via `F3` or programmatically. It was fully implemented on top of Phases 1–3 + Theme Rebuild.

### Activation

```python
env.ui.debug_mode = True        # programmatic
# — or —
# Press F3 at runtime (built into UIManager.process_input, always active)
```

`F3` is handled unconditionally in `UIManager.process_input()` right after the `keyboard.is_consumed` line, regardless of what element is focused.

### Visual output when `debug_mode = True`

**Color-coded hitbox outlines** are drawn for every visible element each frame:
- **Cyan** `(0, 1, 1, 0.5)` — currently hovered element
- **Yellow** `(1, 1, 0, 0.45)` — currently focused element
- **Dim grey** `(0.5, 0.5, 0.5, 0.18)` — all other visible elements

**Side panel** — when an element is hovered, a `_UIDebugPanel` (internal class in `manager.py`) appears at the right side of the window:
- 300 px wide, 8 px from right edge, 8 px from top
- Semi-transparent dark background
- Yellow title: `"Button"` / `"Slider"` / etc.
- Light grey key→value grid from `_debug_info()`
- Green source line: `"example_widgets.py:42"` (file + line where the element was constructed)
- Persistent `Label` pool — GPU text is only rebuilt when the displayed text actually changes (dirty-checked)
- `flush_queue()` is called before every `Label.draw()` inside the panel to preserve correct layer ordering

### `_debug_source` — automatic creation-site capture

`UIElement.__init__` walks the Python call stack (via `inspect.stack()`) and records the first frame whose file is **outside** the `e2D/` package directory. Stored as `self._debug_source = "filename.py:lineno"`.

If the stack walk fails for any reason, `_debug_source` is left as an empty string (silent).

### `_debug_info()` — virtual method

Defined on `UIElement`, returns `list[tuple[str, str]]`. Each tuple is a `(key, value)` pair displayed on one row of the debug panel.

**Base class rows** (all elements):

| Key | Value |
|-----|-------|
| `pos` | `(x, y)` in pixels |
| `size` | `(w, h)` in pixels |
| `pivot` | e.g. `TOP_LEFT` |
| `z-index` | int |
| `visible` | `yes` / `no` |
| `enabled` | `yes` / `no` |
| `opacity` | float |
| `focused` | `yes` / `no` |
| `hovered` | `yes` / `no` (only if `_is_hovered` attribute exists) |

**Overrides per element type:**

| Class | Extra rows |
|-------|-----------|
| `Button` | `text` (quoted), `state` (normal/hovered/pressed/focused/disabled) |
| `Switch` | `value` (ON / OFF) |
| `Checkbox` | `checked` (yes / no) |
| `Slider` | `value`, `range`, `step`, `orient`, `drag` |
| `RangeSlider` | `low`, `high`, `range`, `step`, `orient`, `drag` |

All overrides call `super()._debug_info()` and append their extra rows.

### Files modified for debug mode

| File | Changes |
|------|---------|
| `ui/base.py` | `import inspect as _inspect`, `import os as _os`; module-level `_e2d_dir` constant; `_debug_source` capture in `__init__`; `_debug_info()` virtual method |
| `ui/button.py` | `_debug_info()` override |
| `ui/toggle.py` | `_debug_info()` overrides on `Switch` and `Checkbox` |
| `ui/slider.py` | `_debug_info()` overrides on `Slider` and `RangeSlider` |
| `ui/manager.py` | `from ..vectors import V2`; `_UIDebugPanel` class; `_debug_panel` field; F3 key in `process_input()`; `draw()` rewritten with outlines + panel |

### `_UIDebugPanel` — internal constants

```python
PANEL_W  = 300    # px
PAD_X    = 10     # inner horizontal padding
PAD_Y    = 8      # inner vertical padding
LINE_H   = 17     # px per kv row
TITLE_H  = 24     # px for title row
```

Colors:
- Title: yellow `Color(1.00, 0.92, 0.25)` with `BOLD_TEXT_STYLE`
- KV rows: light grey `Color(0.87, 0.87, 0.90)`
- Source line: green `Color(0.35, 0.85, 0.45)`

### Draw-order note for debug panel

The debug panel labels follow the same `flush_queue()` + `Label.draw()` pattern described in the draw-order architecture section above. `_UIDebugPanel.draw()` calls `flush_queue()` before every `Label.draw()` internally — there is no need to call it again from the outside.

---

## PHASE 4 — Containers and Layout System (COMPLETE — do not re-implement)

**Target files:**
```
ui/
└── containers.py    (NEW — contains VBox, HBox, Grid, FreeContainer, ScrollContainer)
```

### UIContainer base class

- Inherits from `UIElement`
- Manages a list of child `UIElement` instances
- Has its own background style (color, gradient, border, corner_radius, padding)
- `add_child(element)` / `remove_child(element)` — after any structural change, triggers layout recalculation
- **Padding:** inner spacing between container edge and children (top, right, bottom, left independently configurable, or single value)
- **Margin** is on the child elements, not the container itself (already part of UIElement — confirm in `ui/base.py`)
- Nested containers: a container can be added as a child of another container. Layout must recurse

### Anchor System (Godot-style)

Every `UIElement` has 4 anchor values: `anchor_left`, `anchor_top`, `anchor_right`, `anchor_bottom` — each a float 0.0–1.0 representing percentage of parent size. Plus pixel offsets: `offset_left`, `offset_top`, `offset_right`, `offset_bottom`.

Computed rect:
```
left   = parent.width  * anchor_left   + offset_left
top    = parent.height * anchor_top    + offset_top
right  = parent.width  * anchor_right  + offset_right
bottom = parent.height * anchor_bottom + offset_bottom
```

**Check if this is already partially implemented in `ui/base.py` before adding.** Only add what's missing.

When parent (or window) resizes, all children with non-zero anchor range recalculate their rects. `UIManager._on_resize` (or equivalent — read `ui/manager.py`) must propagate resize to all root containers.

Convenience presets (like Godot):
- `Anchor.FULL_RECT` — fills parent completely
- `Anchor.TOP_LEFT`, `Anchor.TOP_RIGHT`, `Anchor.BOTTOM_LEFT`, `Anchor.BOTTOM_RIGHT` — corner anchors
- `Anchor.CENTER` — centered, fixed size
- `Anchor.TOP_WIDE`, `Anchor.BOTTOM_WIDE`, `Anchor.LEFT_WIDE`, `Anchor.RIGHT_WIDE` — full-width or full-height strips

### Sizing Modes (three modes, all must work)

On each UIElement, a `size_mode` property:
- `SizeMode.FIXED` — `size` is in pixels, never changes
- `SizeMode.PERCENT` — `size` is 0.0–1.0 fraction of parent's inner size
- `SizeMode.AUTO` — element sizes itself to fit its content (text width for labels, children bounds for containers)

### VBox

- Stacks children vertically, top to bottom
- `spacing: float = 0` — gap between children in pixels
- `align: str = 'left'` — horizontal alignment of children: `'left'`, `'center'`, `'right'`, `'stretch'` (stretch = children fill container width)

### HBox

- Stacks children horizontally, left to right
- `spacing: float = 0`
- `align: str = 'top'` — vertical alignment: `'top'`, `'center'`, `'bottom'`, `'stretch'`

### Grid

- Arranges children in a rows × columns grid
- `columns: int` — number of columns (rows auto-computed from child count)
- `cell_spacing: tuple[float, float] = (0, 0)` — (horizontal, vertical) gap between cells
- `cell_size: tuple | None = None` — if None, all cells are equal size filling the container; if set, fixed cell size

### FreeContainer

- Absolute positioning inside the container — each child's `position` is relative to the container's top-left
- No automatic layout, children must be positioned manually
- Still supports anchor system and resize propagation

### ScrollContainer

- Wraps exactly one child (typically a VBox or HBox)
- When child content exceeds visible area: clip the overflow, allow scrolling
- Mouse wheel scrolls when hovered or focused
- Optional visible scrollbar: `show_scrollbar=True` (default True)
- Scrollbar appearance configurable (width, color, thumb color)
- Scroll direction: `scroll_vertical=True`, `scroll_horizontal=False` (configurable)

### Integration Requirements for Phase 4

- All containers register with UIManager
- Resize events from window must propagate through the entire container tree
- Read `ui/manager.py` for how `_on_resize` currently works before adding propagation
- Update `ui/__init__.py` and root `__init__.py`

---

## PHASE 5 — Gradients, Blur, Transparency Fix

### Gradient System

**Gradient definition format** (user-facing API):
```python
# Stops: list of (Color, position) where position is 0.0–1.0
stops = [(Color1, 0.0), (Color2, 0.5), (Color3, 1.0)]

# Linear gradient
LinearGradient(stops, angle=0.0)   # angle in radians

# Radial gradient
RadialGradient(stops, center=(0.5, 0.5), radius=1.0)
# center is normalized (0,0)=top-left (1,1)=bottom-right of element
```

**Where gradients apply:**
- Any UIElement background (`bg_color` accepts a gradient instead of a plain Color)
- Container backgrounds
- Button backgrounds (per-state)
- TextStyle `bg_color`

**Implementation approach:**
- Gradients require fragment shader work. Create `ui/shaders/` subfolder for UI-specific GLSL
- For elements with gradients: pass gradient stops as uniform arrays to the shader
- Max gradient stops: 8 (hardcoded uniform array size) — document this limit in a comment
- The gradient shader replaces the solid-color fill, not the entire element shader
- **Read `shapes.py` and existing shaders in `shaders/` before implementing** to understand the current rendering pipeline and reuse as much as possible

### Frosted Glass / Blur Effect

**What it does:** a "backdrop blur" — elements behind a semi-transparent blurred element are blurred underneath it.

**Mechanism (Option A + B as discussed):**
- Option A is the mechanism: before drawing any UI element with `blur=True`, capture the current framebuffer contents (or a cached version), run a Gaussian blur shader on the region behind the element, then draw the element on top of the blurred background
- Option B is the API: `blur=True/False` per UIElement, `blur_radius: float = 10` (pixels)

**Implementation steps (in order):**
1. Create a ping-pong framebuffer pair for the blur pass (two FBOs, alternate between them for multi-pass Gaussian)
2. On each frame, before drawing UI: if any visible element has `blur=True`, capture the scene framebuffer into the blur FBO
3. Run separable Gaussian blur (horizontal pass + vertical pass = 2 draw calls)
4. When drawing the blurred element: bind the blurred texture as background, draw element geometry on top
5. Blur shaders: create `shaders/blur_horizontal.glsl` and `shaders/blur_vertical.glsl`

**Performance note:** This is expensive. Only re-capture the framebuffer if anything behind the blurred element changed (dirty flag). Document this clearly.

### Transparency Pipeline Fix

**The problem:** `plot.py` (formerly `plots.py`) uses a different viewport that makes everything underneath it opaque — semi-transparent colors appear solid because the plot canvas fills its viewport with an opaque color.

**Before fixing:** READ `plot.py` fully to understand the current implementation. Then fix the viewport clear/background so it respects alpha and composites correctly with what was drawn before it.

**General transparency:** All UIElements already use alpha via the Color system. Ensure the ModernGL blend mode in `__init__.py`/`RootEnv` is set correctly:
- Current: `SRC_ALPHA, ONE_MINUS_SRC_ALPHA`
- For correct layered UI rendering with premultiplied alpha (if used): switch to `ONE, ONE_MINUS_SRC_ALPHA`
- **Read the current blend setup in `__init__.py` before changing anything**

### Element Opacity Property

Each UIElement has an `opacity: float = 1.0` property (0.0 = fully transparent, 1.0 = fully opaque).
- Check if this was already added in Phase 1 by reading `ui/base.py`
- This opacity multiplies on top of all element colors, and cascades to children (child effective opacity = parent opacity × child opacity)
- Pass final computed opacity as `u_opacity` uniform to the shader (this uniform was added in Phase 1's text.py — confirm the pattern is consistent in other shaders)

---

## PHASE 6 — FPS/UPS Overlay

**Goal:** A clean FPS (and optionally UPS) display using the Phase 1 Label system.

**Configuration:** controlled by `WindowConfig` (read `core/window.py` to see the current WindowConfig implementation before modifying):
- `show_fps: bool = False`
- `fps_position: Vector2D | None = None` — defaults to top-left corner if None
- `fps_style: TextStyle | None = None` — defaults to MONO_16_TEXT_STYLE if None

**Display content:**
- If `fixed_update_rate > 0` (separate update loop): show `FPS: 60.0 | UPS: 120.0`
- If no fixed update rate: show `FPS: 60.0` only
- Values updated once per second (rolling average, not instant), to avoid jitter

**Implementation:**
- Use `UIManager.label()` or direct `Label` instance — do NOT reimplement text drawing
- The FPS label is managed internally by `RootEnv`, the user just sets `show_fps=True` in config
- Read `__init__.py` to see what FPS/UPS tracking was already added in Phase 1. Do NOT duplicate that logic — only add the display part if missing

---

## CROSS-PHASE RULES

### Imports and Module References

Before importing anything from an existing module, **read that module**. Do not guess import paths.

#### ⚠️ RESOLVED: Two `utils.py` files — only ONE is live

| Path | Status | Notes |
|------|--------|-------|
| `e2D/utils.py` | ✅ **LIVE — use this** | Renamed from `commons.py`. Uses `import moderngl` directly, real `isinstance(x, moderngl.Program)` checks. Imported by `shapes.py`, `plot.py`, and the rest of the package. |
| `e2D/core/utils.py` | ❌ **DEAD — never import** | Created by Phase 1 agent for a `core/` restructuring that was never finished. Has subtle runtime bugs (`isinstance(x, ProgramType)` with a string alias). Nothing in the package imports it. |

**Rule:** All Phase 2–6 code imports utilities from `e2D.utils`. Never touch `e2D.core.utils`.

#### ⚠️ RESOLVED: `_pivot.py` vs `ui/base.py` — two completely separate files

| File | Contains | Imports |
|------|----------|---------|
| `_pivot.py` | `Pivot` class, `resolve_pivot()`, `_PIVOTS_ENUM_MAP` | Zero dependency on `ui/` |
| `ui/base.py` | `UIElement` base class only | Imports `Pivot` from `_pivot.py` via `from .._pivot import Pivot, resolve_pivot, _PIVOTS_ENUM_MAP` |

The split is intentional to break a circular import chain: `text.py → ui/base → ui/__init__ → label → text`.

**Rule:** All Phase 2–6 code must import `Pivot` from `e2D._pivot` (or from the `e2D` root, which re-exports it). **Never import Pivot from `e2D.ui.base`** — that file does not define it, it only uses it.

#### Module import reference for Phases 4–6:
- `_pivot.py` — `Pivot`, `resolve_pivot()`, `_PIVOTS_ENUM_MAP`
- `ui/base.py` — `UIElement` base class only; also contains `_debug_info()` virtual method, `_debug_source` auto-capture (debug mode), and `size_mode` attribute (Phase 4)
- `ui/theme.py` — `UITheme` (read to get exact field names)
- `ui/manager.py` — `UIManager`; `_UIDebugPanel` and F3 toggle are already implemented; factory methods for all widget and container types are already added — do not add again
- `ui/containers.py` — `UIContainer`, `VBox`, `HBox`, `Grid`, `FreeContainer`, `ScrollContainer`, `SizeMode`, `Anchor` (Phase 4 — read before creating any layout container)
- `ui/input_field.py` — `InputField`, `MultiLineInput` (read before implementing any text-input in Phase 5+)
- `colors.py` — `Color` class (read to understand existing Color utilities)
- `palette.py` — pre-defined colors (read to see what's available)
- `input.py` — `Keyboard`/`Mouse` (read to understand the input system)
- `text.py` — `TextRenderer`/`TextStyle`/`TextLabel` (read to understand text API)
- `shapes.py` — `ShapeRenderer` (read to understand how shapes are drawn before adding new ones)
- `__init__.py` — `RootEnv` (read to understand the main loop, UIManager integration, and existing exports)
- `utils.py` ← **root level only** — utility functions (was `commons.py`); now also contains `find_system_font()`
- `_types.py` — type aliases (read before writing type annotations)

### Shader Files

Any new GLSL shaders:
- Place in `shaders/` for engine-level shaders (blur, etc.)
- Place in `ui/shaders/` for UI-specific shaders (gradient fills, etc.) — create this directory
- Always use `#version 430 core` (matches existing OpenGL 4.3 context)
- Check existing shaders in `shaders/` for the conventions (uniform naming, in/out variable style) before writing new ones

### Animation System

All animations (hover fade, press scale, slider thumb movement, switch slide, etc.) must:
- Be driven by `delta` time (read how `delta` is stored/accessed in `__init__.py`)
- Be togglable via `animated=True/False` on element init
- When `animated=False`: apply the final state immediately, no interpolation

### Performance

- No Python-side per-frame loops over large datasets inside the UI system
- UI elements only redraw when their state is dirty (use dirty flags)
- The `UIManager.draw()` call should only issue GL draw calls for visible elements
- Gradients are computed in the shader (not CPU-side)

### Error Handling

- If a user passes an invalid value (e.g., Slider value outside start/end range), clamp silently and do not raise
- Log a warning to console for clearly wrong configurations (wrong type, etc.)
- Never crash on missing optional callbacks

---

## RESOLVED DECISIONS

1. **Clipboard (Phase 3):** Use **GLFW's built-in clipboard API** — `glfw.get_clipboard_string(window)` and `glfw.set_clipboard_string(window, string)`. GLFW is already a dependency and this API works natively on Windows, X11, and Wayland with zero additional code or imports. Do not use `ctypes.windll`, `tkinter`, `pyperclip`, or `subprocess xclip/wl-copy`. The `window` handle is available from `RootEnv` — read `__init__.py` to see exactly how it's stored before implementing.

2. **Blur + Z-index interaction (Phase 5):** Game content is always rendered before `UIManager.draw()`. However, `UIManager` has explicit z-index ordering for UI elements. The framebuffer capture for a blurred element must happen **at that element's draw step within the z-ordered sequence**, not once before all UI. Concretely: when iterating z-ordered elements to draw, if the current element has `blur=True`, capture the framebuffer at that point, run the blur pass, then draw the element on top. Elements drawn after it (higher z-index) are not blurred.

3. **Phase ordering:** Complete and verify each phase before starting the next. After finishing a phase, confirm with the user before proceeding.

4. **Visual testing:** No automated test suite. The agent has no test script to run. After completing each phase, present a summary of what was implemented and ask the user to test manually.

5. **`__main__.py`:** A minimal CLI info tool with no window, no OpenGL, no interactive state, and no imports that clash with Phase 2+ work. It is safe to leave completely untouched. Agents have no reason to read or modify it.

---

## SHELL / ENVIRONMENT RULES

- **Always use `py -3.13`** for running Python on Windows. On Linux use `python3.13`. Never use bare `python` or `python3`.
- OpenGL minimum version: **4.3 core profile**. Do not use any OpenGL 4.4+ or 4.5+ features (no `glBindTextureUnit`, no `glNamedBuffer*`, etc.) unless you first verify the feature exists in 4.3.

---

## CROSS-PLATFORM POLICY — CRITICAL

**Target platforms: Windows and Linux (including Wayland).** Every line of Phase 2–6 code must work on both.

### What is already handled — do not touch

The codebase is already mostly cross-platform. Two platform-specific pieces exist and are already correctly handled:

1. **`ctypes.windll.winmm.timeBeginPeriod(1)` in `__init__.py`** — the 1ms timer-resolution trick for Windows frame pacing. Already guarded with `if sys.platform == 'win32':` (lines ~564–565) and its cleanup is guarded too. Linux doesn't need it. **Leave this as-is.**

2. **`recorder.py`** — the screen recording module. Originally written as a Windows-specific capture tool. It is **the only genuinely platform-limited piece** in the codebase. Do not modify `recorder.py`. Do not add functionality that depends on it. A cross-platform rewrite (framebuffer readback via `ctx.fbo.read()` piped to ffmpeg) is a deferred task outside the scope of Phases 2–6.

### Rules for all Phase 2–6 code

- **No `ctypes.windll` anywhere.** Not for clipboard, not for anything.
- **No `win32*` imports** (pywin32, win32api, win32con, etc.).
- **No `os.name == 'nt'` branching** for new features — if a feature cannot be implemented cross-platform, do not implement it and ask the user instead.
- **No Linux-only calls either** (no `xclip`, `xsel`, `wl-copy`, `/proc/`, etc.).
- GLFW, ModernGL, NumPy, and Python's standard library (`time`, `sys`, `math`, `ctypes` for non-Win32 uses) are all fully cross-platform and safe to use freely.
- **Clipboard specifically:** use `glfw.get_clipboard_string(window)` / `glfw.set_clipboard_string(window, string)` — GLFW handles Windows/X11/Wayland internally.

---

## CYTHON FILES — READ ONLY

The following files are **pre-compiled and must never be modified**:

| File | Role |
|------|------|
| `cvectors.pyx` | Cython source for vector math |
| `cvectors.pxd` | Cython header |
| `cvectors.cp313-win_amd64.pyd` | Compiled extension — already present |
| `cvectors.pyi` | Type stub — use this for type reference |
| `ccolors.pyx` | Cython source for color batch ops |
| `ccolors.cp313-win_amd64.pyd` | Compiled extension — already present |
| `ccolors.pyi` | Type stub — use this for type reference |

Do not modify `.pyx`, `.pxd`, or `.pyd` files. Do not attempt to recompile Cython. If you need to understand what these modules expose, read the `.pyi` stub files.

---

## TESTING

- Use `py -3.13` for all shell commands
- **Ask the user** for the path to any example/test script before running visual tests — do not assume one exists or invent a path

---

*This document was written with full knowledge of the chat log between the user and the previous Claude Code agent session. Any detail not explicitly stated in this document is UNKNOWN — ask the user, do not assume.*
---

## PHASE 5 ADDENDUM � Container UX Fixes & MouseMode System (COMPLETE)

### Overview

All changes below were made after Phases 1�4 and the Theme/Debug rebuild. They fix runtime bugs found in `example_containers.py` and add the `MouseMode` interaction model needed for PASS_THROUGH layout containers.

---

### 1. MouseMode System

**Problem:** `UIContainer` consumed mouse events so children were never hovered or clicked.

**Solution:** `MouseMode` class with four values:

| Value | Behaviour |
|---|---|
| `BLOCK` | Default for interactive widgets. Captures hover; children receive events. |
| `RELAY` | Element is hovered AND parent continues event propagation. |
| `PASS_THROUGH` | Transparent to mouse interaction; children are still hit-tested. |
| `IGNORE` | Element and all children are excluded from hit-testing entirely. |

- `UIContainer` default: `mouse_mode = MouseMode.PASS_THROUGH`
- `ScrollContainer` override: `mouse_mode = MouseMode.BLOCK` (must capture scroll)
- Hit-testing rewritten as recursive depth-first `_hit_test(elem, mx, my)` in `manager.py`.

---

### 2. max_width / max_height on UIElement

New optional kwargs stored on every `UIElement`:
- `max_width: float | None = None`
- `max_height: float | None = None`

**VBox** `align='stretch'`: clamps `cw = min(inner_w, child.max_width)` when set.
**HBox** `align='stretch'`: clamps `ch = min(inner_h, child.max_height)` when set.

Use case � prevent switch/checkbox stretching to full column width:

    ui.switch(value=True, size=V2(50, 26), max_width=50)
    ui.checkbox(value=False, size=V2(22, 22), max_width=22, max_height=22)

---

### 3. SizeMode.PERCENT Exponential Growth Bug Fix

**Root cause:** `_child_px_size` read `child._size.x` as the fraction. After layout wrote pixels into `_size`, the next layout call multiplied pixels x available_width ? exponential growth toward �3e50.

**Fix:** `UIContainer._percent_sizes: dict[int, tuple[float, float]]` saves original fractions at `add_child` time. `_child_px_size` (now instance method) reads from this dict first, so stored fractions are never overwritten by layout.

---

### 4. F3 Debug Visibility for Containers

**Problem:** PASS_THROUGH containers never appeared in the F3 panel.

**Solution:**
- `_debug_hovered: Optional[UIElement]` � found via `_debug_hit_test` which treats PASS_THROUGH as returnable (only IGNORE blocks traversal).
- `draw()` uses `debug_target = _debug_hovered or _hovered`.
- `UIContainer._debug_info` now shows: children count, inner size, padding (T/R/B/L), clip, mouse_mode, size_mode.

---

### 5. example_containers.py Fixes

| Bug | Fix |
|---|---|
| Can't click anything | PASS_THROUGH on containers � children now receive events |
| Switch/Checkbox stretched to full width | max_width/max_height applied at widget creation |
| Normal button did nothing | Added on_click + click counter label |
| SizeMode.PERCENT exponential growth | _percent_sizes stores original fractions |
| Grid panel overflows bottom | grid_h reduced 180 ? 148 |
| FreeContainer anchor demo was static | 10 interactive preset buttons cycling Anchor values |
| Window resize didn't update layout | Panels use anchor_min/anchor_max + margin; sidebar height updated in update() |

**Test counts:** 80/80 passing before and after all changes.

---

### 6. Button Auto-Sizing & natural_size() (e2D/ui/button.py)

**Problem:** Button.size defaulted to a hardcoded 120x36 fallback. Padding was stored but never used. Text changes (Button.text.setter) did not update the button size.

**Fix:** Button now tracks its preferred content size:

- `_auto_sized: bool` � set to `True` in `_build()` when size was (0,0) at construction.
- `_natural_w / _natural_h: float` � measured from `_label._text_width/_text_height + padding`.  Updated every time the label is rebuilt.
- `_update_natural_size()` � internal helper; computes effective padding: uses `self.padding` (T,R,B,L) if non-zero, else falls back to `Button._DEFAULT_PAD_H = 16 px` horizontal and `Button._DEFAULT_PAD_V = 8 px` vertical.
- `natural_size() -> (float, float)` � public API; returns `(_natural_w, _natural_h)`.

**text.setter** (changed):
`python
@text.setter
def text(self, value):
    self._text = value
    if self._label is not None:
        self._label.set_plain_text(value)
        self._label._rebuild()          # immediate re-measurement
        self._update_natural_size()
        if self._auto_sized:
            self._size.set(self._natural_w, self._natural_h)
`

**Effect:** Buttons created with no explicit `size` (or `size=V2(0,0)`) auto-fit their text.  When `btn.text` is updated, `_size` is kept in sync automatically, so anchoring calculations that depend on point-axis `_size` always have accurate dimensions.

**Usage:**
`python
btn = ui.button("OK")          # auto-sizes to text + 16px H + 8px V padding
btn.text = "Cancel"            # _size updates immediately to fit "Cancel"
w, h = btn.natural_size()      # query current preferred dimensions
`

**padding/margin on UIElement:**
Both `padding` and `margin` are constructor kwargs on every `UIElement` (base class).  They are stored as 4-tuples (top, right, bottom, left) and always available.  Their usage is as follows:

| Field | Where used |
|---|---|
| `padding` | UIContainer: insets children from the container edges. Button: contributes to `natural_size()` calculation |
| `margin` | `layout()`: offsets position from the anchor point; negative margins enable right/bottom alignment against point anchors |

No widget (Button, Slider, Switch, Checkbox) uses padding for visual inset inside its own rect. Padding affects only auto-sizing for Button and child positioning for containers.

---

### 7. Anchor System Additions (e2D/ui/containers.py)

Two new `Anchor` presets:

| Preset | anchor_min | anchor_max | Effect |
|---|---|---|---|
| `HCENTER_WIDE` | (0, 0.5) | (1, 0.5) | Full-width, vertically centred strip (point Y axis, use margin_top=-h/2) |
| `VCENTER_WIDE` | (0.5, 0) | (0.5, 1) | Full-height, horizontally centred strip (point X axis, use margin_left=-w/2) |

Per-axis `layout()` behaviour: each axis is handled independently.  When `amin[i] == amax[i]` (point anchor) the element keeps its current `_size[i]`; when they differ, the axis stretches.

---

## PHASE 5 — Gradients, Blur, Opacity Cascade, Plot Transparency

**Status:** ✅ Complete — 80/80 tests passing

---

### 1. Gradient System (`e2D/gradient.py`)

New module exposing two public gradient dataclasses and a type alias:

```python
@dataclass
class LinearGradient:
    stops: list[tuple[Color, float]]   # [(color, position 0..1), ...]
    angle: float = 0.0                 # radians; 0 = left → right

@dataclass
class RadialGradient:
    stops: list[tuple[Color, float]]
    center: tuple[float, float] = (0.5, 0.5)  # normalised bbox coords
    radius: float = 1.0                        # normalised radius

GradientType = Union[LinearGradient, RadialGradient]
```

Exported from both `e2D.ui` and the root `e2D` package.

---

### 2. Gradient Rectangles in ShapeRenderer (`e2D/shapes.py`)

`ShapeRenderer` gains a `draw_rect_gradient(...)` method and the internal
`_exec_gradient_draw(...)` executor.

**Architecture:** gradient rects cannot use the instanced batch (each rect has
unique per-draw uniforms).  They are queued as `(layer, 'g', callable)` tuples
in `_queue` — the same deferred lambda pattern used for text `'t'` items.
`flush_queue()` dispatches them in layer+type order, auto-flushing any pending
instanced batch before each `'g'` call.

**Shader design:**
- Vertex stage: transforms a unit quad by `u_pos`, `u_size`, `u_rotation`
  uniforms into NDC space.
- Fragment stage: `roundedBoxSDF` for corner-radius clipping and antialiasing;
  `sample_gradient(t)` interpolates up to **8 stops** stored in
  `u_stop_colors[i]` / `u_stop_positions[i]` uniform arrays.  Linear gradients
  project the fragment position onto the gradient direction vector; radial
  gradients use aspect-ratio-corrected distance from `u_center`.

**`RootEnv` proxy:**
```python
env.draw_rect_gradient(position, size, gradient=LinearGradient(...), ...)
```

---

### 3. Opacity Cascade (`e2D/ui/base.py`)

`UIElement._effective_opacity() -> float` walks the `_parent` chain multiplying
each ancestor's `opacity`, clamped to `[0, 1]`.

All containers now call `alpha = self._effective_opacity()` in their `draw()`
methods so nested container opacity composes correctly.

---

### 4. Background Gradient on UIContainer (`e2D/ui/containers.py`)

```python
panel = ui.container(bg_gradient=LinearGradient(
    stops=[(Color(0.1, 0.1, 0.2, 1.0), 0.0), (Color(0.0, 0.0, 0.0, 1.0), 1.0)],
    angle=0.0,
))
```

- New constructor parameter `bg_gradient: GradientType | None = None`.
- When set, `draw()` calls `sr.draw_rect_gradient(...)` instead of the flat
  `sr.draw_rect(...)` path (solid fallback is still used when `bg_gradient` is
  `None`).
- Applies to `UIContainer`, `VBox`, `HBox`, `Grid`, `FreeContainer`, and
  `ScrollContainer` (all inherit via `UIContainer.draw()`).

---

### 5. Blur (Frosted Glass) on UIElement (`e2D/ui/manager.py`)

Any widget or container can now request a frosted-glass backdrop:

```python
ui.container(blur=True, blur_radius=12.0, bg_color=Color(1,1,1,0.15))
```

**Mechanism:** `UIManager.draw()` detects elements with `blur=True` before the
main draw loop.  If any exist:

1. **Lazy FBO initialisation**: `_setup_blur_fbos(w, h)` creates three
   equal-sized FBOs (`_blur_capture_fbo`, `_blur_ping_fbo`, `_blur_pong_fbo`)
   plus two shader programs:
   - `_blur_prog` — separable Gaussian pass; direction selected by `u_direction`
     `vec2`.
   - `_blur_blit_prog` — screen-space blit that composites the processed texture
     at the element's position/size.
2. **Capture**: `_capture_and_blur(max_blur_radius)` copies the current
   framebuffer (`ctx.copy_framebuffer`, CPU fallback on older ModernGL) and runs
   a horizontal then vertical Gaussian pass.
3. **Per-element blit**: before each blur element is drawn, `_draw_blur_behind`
   renders the blurred texture clipped to the element rect.

FBOs are lazily recreated on window resize (`_blur_fbo_size` sentinel).

---

### 6. Plot Transparency Fix (`e2D/plot.py`, `e2D/shaders/plot_grid_fragment.glsl`)

**Problem:** `ctx.clear()` was commented out, leaving `bg_color` with no effect.

**Fix:** The grid fragment shader gains a `bg_color` uniform.  Non-grid/axis
pixels (previously `discard`-ed) now output `bg_color` instead, which:
- Supports fully opaque backgrounds (alpha = 1).
- Supports transparent/translucent backgrounds (alpha < 1): the plot region
  composites over the scene behind it via the existing GL blend state.
- Supports fully invisible backgrounds (alpha = 0): pixels that would have been
  discarded are now rendered with `vec4(0)`, preserving the scene beneath.

The `render()` method always submits the grid quad (removed the
`show_grid or show_axis` guard); the shader handles the no-grid, no-axis case
via its `bg_color` fallback.

---

## PHASE 6 — Live Stats Overlay (`e2D/ui/manager.py`)

**Status:** ✅ Complete — 80/80 tests passing

---

### Stats Panel

A dedicated `_UIStatsPanel` class provides a real-time performance HUD drawn on
top of the UI each frame when active.

**Activation:**
- Press **F2** at any time (always active, regardless of keyboard focus).
- Or programmatically: `env.ui.show_stats = True`.

**Displayed metrics:**

| Metric | Description |
|---|---|
| FPS | Frames per second (1-second rolling average) |
| Frame time | `delta * 1000` in milliseconds |
| UPS | Physics/logic updates per second (only when `fixed_update_rate > 0`) |
| Phys step | Fixed timestep (`fixed_dt * 1000` ms; shown only when UPS > 0) |
| Elapsed | Total runtime in `HH:MM:SS` / `MM:SS` format |

**Implementation:**
- `_UIStatsPanel(manager)` — allocates one `Label` per stat line on first
  `draw()` call (`_ensure_labels()`).  Labels are rebuilt only when line content
  changes; GPU resources are freed on `release()`.
- Panel is positioned top-left with `PAD_X / PAD_Y` insets and a dark
  semi-transparent background + green border drawn via `ShapeRenderer`.
- Stats are fed from `UIManager.update_stats(fps, delta, ups, fixed_dt, elapsed)`
  which `RootEnv.loop()` calls every frame after the FPS/UPS counter update.

**Property:**
```python
@property
def show_stats(self) -> bool: ...
@show_stats.setter
def show_stats(self, value: bool) -> None: ...
```

Setting `show_stats = False` immediately calls `_stats_panel.release()` to free
GPU resources.

