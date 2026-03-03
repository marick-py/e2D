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

**Phases 1 and 2 are COMPLETE.** This document covers Phases 3–6.

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
- `ui/base.py` — added 6 interaction event hook stubs to `UIElement`: `on_hover_enter()`, `on_hover_exit()`, `on_mouse_press(mx, my)`, `on_mouse_release(mx, my)`, `on_mouse_drag(mx, my, dx, dy)`, `on_key_press(key)`
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

## PHASE 3 — InputField and MultiLineInput

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
  - `password=True`: renders text as bullet points `•` instead of actual characters
- Text editing uses `input.py` `Keyboard.get_chars()` and `Keyboard.char_buffer` system built in Phase 1 — read `input.py` first
- **Cursor:** blinking cursor (configurable blink rate via `cursor_blink_rate` in seconds) when focused. Cursor drawn as a thin vertical line using existing shape renderer
- **Text selection:** click and drag to select. Selected region highlighted with a configurable selection color. `Ctrl+A` selects all
- **Copy/paste:** `Ctrl+C` copies selection, `Ctrl+V` pastes from clipboard (use Python `tkinter.Tk().clipboard_get()` / `clipboard_clear()+clipboard_append()` for clipboard access — it's the safest cross-platform way with no extra deps)
- **Navigation keys:** Left/Right arrows move cursor, Home/End jump to start/end, Shift+arrows extend selection
- **Backspace/Delete:** remove character before/after cursor, or delete selection if any
- **Max length:** optional `max_length: int = None`
- Visual states: Normal, Focused, Disabled, Error (when validation fails)
- All colors, border, font configurable — defaults from UITheme

### MultiLineInput

- Separate class from InputField, also inherits from `UIElement`
- Same text editing features as InputField (selection, copy/paste, cursor)
- Enter key inserts newline instead of submitting
- `on_submit` triggered by `Ctrl+Enter` instead
- **Scrolling:** when text exceeds visible area, scroll vertically. Use mouse wheel when focused/hovered
- **Expand mode:** optional `auto_expand=True` — field grows vertically to fit content instead of scrolling
- Tab key inserts spaces (configurable `tab_width: int = 4`) — does NOT change focus when inside MultiLineInput; use Ctrl+Tab to change focus
- Visible scrollbar when content overflows (configurable `show_scrollbar=True`)

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

## PHASE 4 — Containers and Layout System

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

#### Module import reference for Phases 2–6:
- `_pivot.py` — `Pivot`, `resolve_pivot()`, `_PIVOTS_ENUM_MAP`
- `ui/base.py` — `UIElement` base class only
- `ui/theme.py` — `UITheme` (read to get exact field names)
- `ui/manager.py` — `UIManager` (read to understand focus/input dispatch API)
- `colors.py` — `Color` class (read to understand existing Color utilities)
- `palette.py` — pre-defined colors (read to see what's available)
- `input.py` — `Keyboard`/`Mouse` (read to understand the input system)
- `text.py` — `TextRenderer`/`TextStyle`/`TextLabel` (read to understand text API)
- `shapes.py` — `ShapeRenderer` (read to understand how shapes are drawn before adding new ones)
- `__init__.py` — `RootEnv` (read to understand the main loop, UIManager integration, and existing exports)
- `utils.py` ← **root level only** — utility functions (was `commons.py`)
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