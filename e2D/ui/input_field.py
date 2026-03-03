"""
InputField and MultiLineInput — text editing widgets for e2D UI.

Usage::

    # factory shortcuts (preferred)
    field = env.ui.input_field(placeholder="Enter name…", on_submit=handle_submit)
    area  = env.ui.multi_line_input(value="Hello\\nWorld", auto_expand=True)

    # direct construction
    field = InputField(
        placeholder="Search…",
        on_submit=lambda s: print("submitted:", s),
        validate=lambda s: len(s) >= 3,
        position=V2(100, 200),
        size=V2(300, 40),
    )
    env.ui.add(field)

Clipboard is handled via GLFW (cross-platform: Windows / X11 / Wayland).
"""

from __future__ import annotations

import math
from typing import Callable, Optional, TYPE_CHECKING

import glfw

from .base import UIElement
from ..colors import Color
from .._pivot import Pivot
from ..text import DEFAULT_16_TEXT_STYLE, TextStyle
from ..vectors import V2

if TYPE_CHECKING:
    from .._types import ContextType
    from ..text import TextRenderer


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _sel_range(a: int, b: int) -> tuple[int, int]:
    """Return (lo, hi) regardless of order."""
    return (min(a, b), max(a, b))


# ---------------------------------------------------------------------------
# InputField — single-line text input
# ---------------------------------------------------------------------------

class InputField(UIElement):
    """Single-line text-input widget.

    Constructor keyword arguments (in addition to :class:`UIElement` kwargs):

    * ``placeholder``       — faint hint text shown when the field is empty
    * ``value``             — initial text content
    * ``on_submit``         — ``callable(str)`` called when the user presses Enter
    * ``validate``          — ``callable(str) -> bool``; Entry only submitted if True
    * ``password``          — render characters as ``•`` instead of literal text
    * ``max_length``        — maximum number of characters allowed (``None`` = unlimited)
    * ``text_style``        — :class:`TextStyle` override
    * ``color_normal``      — background colour
    * ``color_focused``     — background while focused
    * ``color_disabled``    — background while disabled
    * ``color_error``       — background when validation fails
    * ``border_color``      — border in normal/error state
    * ``border_color_focused`` — border while focused
    * ``border_width``      — border thickness in px (``None`` → theme default)
    * ``corner_radius``     — rounded-corner radius  (``None`` → theme default)
    * ``selection_color``   — highlight colour for selected text
    * ``cursor_blink_rate`` — seconds per blink half-cycle (``None`` → theme default)
    * ``animated``          — whether to smoothly animate colour between states
    """

    def __init__(
        self,
        placeholder: str = "",
        value: str = "",
        on_submit: Callable[[str], None] | None = None,
        validate: Callable[[str], bool] | None = None,
        password: bool = False,
        max_length: int | None = None,
        text_style: TextStyle | None = None,
        color_normal: Color | None = None,
        color_focused: Color | None = None,
        color_disabled: Color | None = None,
        color_error: Color | None = None,
        border_color: Color | None = None,
        border_color_focused: Color | None = None,
        border_width: float | None = None,
        corner_radius: float | None = None,
        selection_color: Color | None = None,
        cursor_blink_rate: float | None = None,
        animated: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._focusable = True
        self.animated = animated

        # Content
        self._chars: list[str] = list(value)
        self._cursor: int = len(self._chars)
        self._sel_start: int = -1   # -1 = no selection
        self._sel_end: int   = -1

        # Config
        self._placeholder    = placeholder
        self._on_submit      = on_submit
        self._validate       = validate
        self._password       = password
        self._max_length     = max_length

        # Scroll offset — how many px to the right the view is scrolled
        self._scroll_x: float = 0.0

        # Visual state
        self._is_hovered:  bool  = False
        self._error_state: bool  = False
        self._blink_timer: float = 0.0
        self._cursor_vis:  bool  = True

        # Undo / redo history
        self._undo_stack: list[tuple[list[str], int]] = []
        self._redo_stack: list[tuple[list[str], int]] = []
        self._undo_coalescing: bool = False

        # Style overrides (resolved in _build)
        self._ov_text_style        = text_style
        self._ov_color_normal      = color_normal
        self._ov_color_focused     = color_focused
        self._ov_color_disabled    = color_disabled
        self._ov_color_error       = color_error
        self._ov_border_color      = border_color
        self._ov_border_focused    = border_color_focused
        self._ov_border_width      = border_width
        self._ov_corner_radius     = corner_radius
        self._ov_selection_color   = selection_color
        self._ov_cursor_blink_rate = cursor_blink_rate

        # Resolved in _build
        self._text_style:        TextStyle = DEFAULT_16_TEXT_STYLE
        self._c_normal:          Color = Color(0.12, 0.12, 0.12)
        self._c_focused:         Color = Color(0.16, 0.16, 0.20)
        self._c_disabled:        Color = Color(0.10, 0.10, 0.10, 0.6)
        self._c_error:           Color = Color(0.25, 0.08, 0.08)
        self._border_c:          Color = Color(0.30, 0.30, 0.30)
        self._border_focused_c:  Color = Color(0.40, 0.40, 0.80)
        self._border_w:          float = 1.5
        self._corner_r:          float = 6.0
        self._selection_c:       Color = Color(0.26, 0.46, 0.76, 0.45)
        self._cursor_blink_rate: float = 0.53
        self._cur_color:         Color = self._c_normal

    # -----------------------------------------------------------------------
    # Build
    # -----------------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:
        theme = self._manager.theme if self._manager else None

        def _ov(override, default):
            return override if override is not None else default

        if theme:
            self._c_normal       = _ov(self._ov_color_normal,   theme.bg_normal)
            self._c_focused      = _ov(self._ov_color_focused,  theme.bg_focused)
            self._c_disabled     = _ov(self._ov_color_disabled, theme.bg_disabled)
            self._c_error        = _ov(self._ov_color_error,    Color(0.25, 0.08, 0.08))
            self._border_c       = _ov(self._ov_border_color,   theme.border_color)
            self._border_focused_c = _ov(self._ov_border_focused, theme.accent)
            self._border_w       = _ov(self._ov_border_width,   theme.border_width)
            self._corner_r       = _ov(self._ov_corner_radius,  theme.corner_radius)
            self._selection_c    = _ov(self._ov_selection_color, Color(0.26, 0.46, 0.76, 0.45))
            self._cursor_blink_rate = _ov(self._ov_cursor_blink_rate, theme.cursor_blink_rate)
            self._text_style     = self._ov_text_style or TextStyle(
                font=theme.font, font_size=theme.font_size, color=theme.text_color,
            )
        else:
            self._cursor_blink_rate = _ov(self._ov_cursor_blink_rate, 0.53)
            self._text_style = self._ov_text_style or DEFAULT_16_TEXT_STYLE

        self._cur_color = self._c_normal

        if self._size.x == 0 or self._size.y == 0:
            self._size.set(200.0, 36.0)

        self._dirty = False

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    @property
    def value(self) -> str:
        return "".join(self._chars)

    @value.setter
    def value(self, v: str) -> None:
        self._chars = list(v)
        self._cursor = len(self._chars)
        self._sel_start = self._sel_end = -1
        self._scroll_x = 0.0
        self._error_state = False

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _display_text(self) -> str:
        """Text as rendered — asterisks for password mode."""
        if self._password:
            return "*" * len(self._chars)  # '•' U+2022 not in ASCII atlas
        return "".join(self._chars)

    def _padding(self) -> tuple[float, float, float, float]:
        """(top, right, bottom, left) inner padding."""
        return (self.padding[0] or 8.0, self.padding[1] or 8.0,
                self.padding[2] or 8.0, self.padding[3] or 8.0)

    def _has_selection(self) -> bool:
        return self._sel_start != -1 and self._sel_start != self._sel_end

    def _selected_text(self) -> str:
        if not self._has_selection():
            return ""
        lo, hi = _sel_range(self._sel_start, self._sel_end)
        return "".join(self._chars[lo:hi])

    def _delete_selection(self) -> None:
        if not self._has_selection():
            return
        lo, hi = _sel_range(self._sel_start, self._sel_end)
        del self._chars[lo:hi]
        self._cursor = lo
        self._sel_start = self._sel_end = -1

    def _cursor_x_offset(self, pos: int) -> float:
        """X pixel offset of the cursor at *pos* from the start of the text."""
        text = self._display_text()
        prefix = text[:pos]
        if not self._manager:
            return 0.0
        return self._manager.text_renderer.get_text_width(prefix, style=self._text_style)

    def _char_at_x(self, target_x: float) -> int:
        """Return the character index at *target_x* (relative to text start)."""
        text = self._display_text()
        if not self._manager:
            return 0
        tr = self._manager.text_renderer
        x = 0.0
        for i, ch in enumerate(text):
            w = tr.get_text_width(ch, style=self._text_style)
            if target_x < x + w * 0.5:
                return i
            x += w
        return len(text)

    def _ensure_cursor_visible(self) -> None:
        """Adjust _scroll_x so the cursor is within the visible area."""
        if not self._manager:
            return
        _, _, rw, _ = self.get_screen_rect()
        pad = self._padding()
        inner_w = rw - pad[1] - pad[3]
        cx = self._cursor_x_offset(self._cursor)
        if cx - self._scroll_x > inner_w - 4:
            self._scroll_x = cx - inner_w + 4
        elif cx - self._scroll_x < 0:
            self._scroll_x = max(0.0, cx - 4)

    def _is_ctrl(self) -> bool:
        kb = self._manager._keyboard if self._manager else None
        if kb is None:
            return False
        return (glfw.KEY_LEFT_CONTROL in kb.pressed or
                glfw.KEY_RIGHT_CONTROL in kb.pressed)

    def _is_shift(self) -> bool:
        kb = self._manager._keyboard if self._manager else None
        if kb is None:
            return False
        return (glfw.KEY_LEFT_SHIFT in kb.pressed or
                glfw.KEY_RIGHT_SHIFT in kb.pressed)

    def _target_color(self) -> Color:
        if not self.enabled:
            return self._c_disabled
        if self._error_state:
            return self._c_error
        if self._focused:
            return self._c_focused
        return self._c_normal

    # -----------------------------------------------------------------------
    # Per-frame
    # -----------------------------------------------------------------------

    def update(self, dt: float) -> None:
        # Colour animation
        target = self._target_color()
        if self.animated and self._manager:
            t = min(1.0, self._manager.theme.animation_speed * dt)
            self._cur_color = self._cur_color.lerp(target, t)
        else:
            self._cur_color = target

        # Cursor blink
        if self._focused:
            self._blink_timer += dt
            if self._blink_timer >= self._cursor_blink_rate:
                self._blink_timer = 0.0
                self._cursor_vis = not self._cursor_vis
        else:
            self._cursor_vis = False
            self._blink_timer = 0.0

        super().update(dt)

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return
        ctx = ctx or self._manager.ctx
        sr  = self._manager.shape_renderer
        tr  = self._manager.text_renderer

        rx, ry, rw, rh = self.get_screen_rect()
        pad = self._padding()
        alpha = self.opacity

        # Background
        c  = self._cur_color
        bc = self._border_focused_c if self._focused else self._border_c
        sr.draw_rect(
            V2(rx, ry), V2(rw, rh),
            color=(c.r, c.g, c.b, c.a * alpha),
            corner_radius=self._corner_r,
            border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
            border_width=self._border_w,
        )

        # Flush shapes before scissor so they don't bleed out
        sr.flush_queue()

        # Scissor to inner content area
        win_h = int(self._manager._window_size.y)
        ix  = int(rx + pad[3])
        iy  = int(ry + pad[0])
        iw  = max(1, int(rw - pad[1] - pad[3]))
        ih  = max(1, int(rh - pad[0] - pad[2]))
        # OpenGL scissor Y is from bottom
        ctx.scissor = (ix, win_h - iy - ih, iw, ih)

        text_y = ry + rh * 0.5  # vertical centre
        text_x_base = rx + pad[3] - self._scroll_x
        disp = self._display_text()

        # Selection highlight
        if self._has_selection():
            lo, hi = _sel_range(self._sel_start, self._sel_end)
            sel_x0 = text_x_base + self._cursor_x_offset(lo)
            sel_x1 = text_x_base + self._cursor_x_offset(hi)
            # Clip to visible inner area
            sel_x0 = max(sel_x0, rx + pad[3])
            sel_x1 = min(sel_x1, rx + rw - pad[1])
            if sel_x1 > sel_x0:
                sc = self._selection_c
                sr.draw_rect(
                    V2(sel_x0, ry + pad[0]),
                    V2(sel_x1 - sel_x0, rh - pad[0] - pad[2]),
                    color=(sc.r, sc.g, sc.b, sc.a * alpha),
                    corner_radius=0.0,
                )
                sr.flush_queue()

        # Text (or placeholder)
        theme = self._manager.theme
        if disp:
            ts = self._text_style
            tr.draw_text(disp, (text_x_base, text_y), style=ts, pivot=Pivot.LEFT)
        elif self._placeholder:
            ph_color = theme.text_color_placeholder if theme else Color(0.45, 0.45, 0.45)
            ph_style = TextStyle(
                font=self._text_style.font,
                font_size=self._text_style.font_size,
                color=(ph_color.r, ph_color.g, ph_color.b, ph_color.a * alpha),
            )
            tr.draw_text(self._placeholder, (text_x_base, text_y), style=ph_style,
                         pivot=Pivot.LEFT)

        # Cursor
        if self._focused and self._cursor_vis:
            cx = text_x_base + self._cursor_x_offset(self._cursor)
            cursor_top = ry + pad[0] + 2
            cursor_bot = ry + rh - pad[2] - 2
            sr.draw_line(
                (cx, cursor_top), (cx, cursor_bot),
                color=(1.0, 1.0, 1.0, 0.85 * alpha),
                width=1.5,
            )
            sr.flush_queue()

        # Restore scissor
        ctx.scissor = None

    # -----------------------------------------------------------------------
    # Mouse events
    # -----------------------------------------------------------------------

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False

    def on_mouse_press(self, mx: float, my: float) -> None:
        if not self.enabled:
            return
        rx, ry, rw, _ = self.get_screen_rect()
        pad = self._padding()
        rel_x = mx - (rx + pad[3]) + self._scroll_x
        self._cursor = self._char_at_x(rel_x)
        self._sel_start = self._cursor
        self._sel_end   = self._cursor
        self._reset_blink()
        self._error_state = False

    def on_mouse_drag(self, mx: float, my: float, dx: float, dy: float) -> None:
        if not self.enabled:
            return
        rx, _, rw, _ = self.get_screen_rect()
        pad = self._padding()
        rel_x = mx - (rx + pad[3]) + self._scroll_x
        self._cursor = self._char_at_x(rel_x)
        self._sel_end = self._cursor

    # -----------------------------------------------------------------------
    # Keyboard events
    # -----------------------------------------------------------------------

    def on_focus(self) -> None:
        super().on_focus()
        self._reset_blink()

    def on_blur(self) -> None:
        super().on_blur()
        self._sel_start = self._sel_end = -1

    def on_char_input(self, chars: list[str]) -> None:
        """Called by UIManager with newly typed characters this frame."""
        if not self.enabled:
            return
        if not self._undo_coalescing:
            # First char of a new typing session — snapshot before inserting
            self._undo_stack.append((self._chars.copy(), self._cursor))
            if len(self._undo_stack) > 100:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
            self._undo_coalescing = True
        for ch in chars:
            self._insert_char(ch)

    def on_key_press(self, key: int) -> None:
        if not self.enabled:
            return
        ctrl  = self._is_ctrl()
        shift = self._is_shift()
        kb    = self._manager._keyboard if self._manager else None
        # Any explicit key press ends char-input coalescing
        self._undo_coalescing = False

        if key == glfw.KEY_BACKSPACE:
            self._push_undo()
            if self._has_selection():
                self._delete_selection()
            elif self._cursor > 0:
                if ctrl:
                    # Delete previous word
                    word_start = self._find_word_start(self._cursor)
                    del self._chars[word_start:self._cursor]
                    self._cursor = word_start
                else:
                    del self._chars[self._cursor - 1]
                    self._cursor -= 1
            self._error_state = False

        elif key == glfw.KEY_DELETE:
            self._push_undo()
            if self._has_selection():
                self._delete_selection()
            elif self._cursor < len(self._chars):
                if ctrl:
                    word_end = self._find_word_end(self._cursor)
                    del self._chars[self._cursor:word_end]
                else:
                    del self._chars[self._cursor]
            self._error_state = False

        elif key in (glfw.KEY_ENTER, glfw.KEY_KP_ENTER):
            self._submit()

        elif key == glfw.KEY_LEFT:
            if shift:
                if self._sel_start == -1:
                    self._sel_start = self._cursor
                self._cursor = max(0, self._cursor - 1)
                self._sel_end = self._cursor
            else:
                if self._has_selection():
                    lo, _ = _sel_range(self._sel_start, self._sel_end)
                    self._cursor = lo
                    self._sel_start = self._sel_end = -1
                elif self._cursor > 0:
                    self._cursor -= 1

        elif key == glfw.KEY_RIGHT:
            if shift:
                if self._sel_start == -1:
                    self._sel_start = self._cursor
                self._cursor = min(len(self._chars), self._cursor + 1)
                self._sel_end = self._cursor
            else:
                if self._has_selection():
                    _, hi = _sel_range(self._sel_start, self._sel_end)
                    self._cursor = hi
                    self._sel_start = self._sel_end = -1
                elif self._cursor < len(self._chars):
                    self._cursor += 1

        elif key == glfw.KEY_HOME:
            if shift:
                if self._sel_start == -1:
                    self._sel_start = self._cursor
                self._cursor = 0
                self._sel_end = self._cursor
            else:
                self._cursor = 0
                if not shift:
                    self._sel_start = self._sel_end = -1

        elif key == glfw.KEY_END:
            if shift:
                if self._sel_start == -1:
                    self._sel_start = self._cursor
                self._cursor = len(self._chars)
                self._sel_end = self._cursor
            else:
                self._cursor = len(self._chars)
                self._sel_start = self._sel_end = -1

        elif ctrl and key == glfw.KEY_A:
            self._sel_start = 0
            self._sel_end   = len(self._chars)
            self._cursor    = len(self._chars)

        elif ctrl and key == glfw.KEY_C:
            sel = self._selected_text()
            if sel and self._manager and self._manager._window:
                glfw.set_clipboard_string(self._manager._window, sel)

        elif ctrl and key == glfw.KEY_X:
            sel = self._selected_text()
            if sel and self._manager and self._manager._window:
                self._push_undo()
                glfw.set_clipboard_string(self._manager._window, sel)
                self._delete_selection()
                self._error_state = False

        elif ctrl and key == glfw.KEY_V:
            if self._manager and self._manager._window:
                clip = glfw.get_clipboard_string(self._manager._window)
                if clip:
                    # glfw may return bytes on Linux — decode to str
                    if isinstance(clip, (bytes, bytearray)):
                        clip = clip.decode('utf-8', errors='replace')
                    self._push_undo()
                    if self._has_selection():
                        self._delete_selection()
                    for ch in clip:
                        self._insert_char(ch)
                    self._error_state = False

        elif ctrl and key == glfw.KEY_Z:
            if shift:
                # Ctrl+Shift+Z — redo
                if self._redo_stack:
                    self._undo_stack.append((self._chars.copy(), self._cursor))
                    chs, cur = self._redo_stack.pop()
                    self._chars  = list(chs)
                    self._cursor = int(_clamp(cur, 0, len(self._chars)))
                    self._sel_start = self._sel_end = -1
            else:
                # Ctrl+Z — undo
                if self._undo_stack:
                    self._redo_stack.append((self._chars.copy(), self._cursor))
                    chs, cur = self._undo_stack.pop()
                    self._chars  = list(chs)
                    self._cursor = int(_clamp(cur, 0, len(self._chars)))
                    self._sel_start = self._sel_end = -1

        self._ensure_cursor_visible()
        self._reset_blink()

    # -----------------------------------------------------------------------
    # Internal editing helpers
    # -----------------------------------------------------------------------

    def _insert_char(self, ch: str) -> None:
        """Insert *ch* at cursor, honouring max_length."""
        if not isinstance(ch, str):
            return  # guard against bytes iteration on clipboard paste
        if self._max_length is not None and len(self._chars) >= self._max_length:
            return
        if self._has_selection():
            self._delete_selection()
        self._chars.insert(self._cursor, ch)
        self._cursor += 1
        self._ensure_cursor_visible()
        self._reset_blink()

    def _submit(self) -> None:
        val = self.value
        if self._validate is not None and not self._validate(val):
            self._error_state = True
            return
        self._error_state = False
        if self._on_submit:
            self._on_submit(val)

    def _reset_blink(self) -> None:
        self._cursor_vis  = True
        self._blink_timer = 0.0

    def _push_undo(self) -> None:
        """Snapshot current chars+cursor onto the undo stack; clear redo."""
        self._undo_stack.append((self._chars.copy(), self._cursor))
        if len(self._undo_stack) > 100:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _find_word_start(self, pos: int) -> int:
        """Return the start index of the word ending at *pos*."""
        i = pos - 1
        while i > 0 and not self._chars[i - 1].isspace():
            i -= 1
        return i

    def _find_word_end(self, pos: int) -> int:
        """Return the end index of the word starting at *pos*."""
        i = pos
        n = len(self._chars)
        while i < n and not self._chars[i].isspace():
            i += 1
        return i

    def release(self) -> None:
        super().release()


# ---------------------------------------------------------------------------
# MultiLineInput — multi-line text-editing area
# ---------------------------------------------------------------------------

class MultiLineInput(UIElement):
    """Multi-line text editing widget.

    In addition to :class:`InputField` arguments the constructor accepts:

    * ``tab_width``     — spaces inserted when Tab is pressed (default 4)
    * ``auto_expand``   — grow height to fit content instead of scrolling
    * ``show_scrollbar``— draw a vertical scrollbar when content overflows
    * ``min_height``    — minimum height in pixels (0 = unconstrained)
    * ``max_height``    — maximum height in pixels (0 = unconstrained); when
                          auto_expand reaches max_height the field scrolls
    """

    def __init__(
        self,
        placeholder: str = "",
        value: str = "",
        on_submit: Callable[[str], None] | None = None,
        validate: Callable[[str], bool] | None = None,
        max_length: int | None = None,
        text_style: TextStyle | None = None,
        tab_width: int = 4,
        auto_expand: bool = False,
        show_scrollbar: bool = True,
        min_height: float = 0.0,
        max_height: float = 0.0,
        color_normal: Color | None = None,
        color_focused: Color | None = None,
        color_disabled: Color | None = None,
        color_error: Color | None = None,
        border_color: Color | None = None,
        border_color_focused: Color | None = None,
        border_width: float | None = None,
        corner_radius: float | None = None,
        selection_color: Color | None = None,
        cursor_blink_rate: float | None = None,
        animated: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._focusable = True
        self._consumes_tab = True   # Tab inserts spaces; Ctrl+Tab cycles focus
        self.animated = animated

        # Content stored as flat list of chars; newlines are regular '\n' chars
        self._chars: list[str] = list(value)
        self._cursor: int = len(self._chars)
        self._sel_start: int = -1
        self._sel_end:   int = -1

        # Config
        self._placeholder    = placeholder
        self._on_submit      = on_submit
        self._validate       = validate
        self._max_length     = max_length
        self._tab_width      = tab_width
        self._auto_expand    = auto_expand
        self._show_scrollbar = show_scrollbar
        self._min_height     = min_height
        self._max_height     = max_height

        # Scroll
        self._scroll_y: float = 0.0

        # Visual state
        self._is_hovered:  bool  = False
        self._error_state: bool  = False
        self._blink_timer: float = 0.0
        self._cursor_vis:  bool  = True

        # Undo / redo history
        self._undo_stack: list[tuple[list[str], int]] = []
        self._redo_stack: list[tuple[list[str], int]] = []
        self._undo_coalescing: bool = False

        # Style overrides
        self._ov_text_style        = text_style
        self._ov_color_normal      = color_normal
        self._ov_color_focused     = color_focused
        self._ov_color_disabled    = color_disabled
        self._ov_color_error       = color_error
        self._ov_border_color      = border_color
        self._ov_border_focused    = border_color_focused
        self._ov_border_width      = border_width
        self._ov_corner_radius     = corner_radius
        self._ov_selection_color   = selection_color
        self._ov_cursor_blink_rate = cursor_blink_rate

        # Resolved in _build
        self._text_style:        TextStyle = DEFAULT_16_TEXT_STYLE
        self._c_normal:          Color = Color(0.12, 0.12, 0.12)
        self._c_focused:         Color = Color(0.16, 0.16, 0.20)
        self._c_disabled:        Color = Color(0.10, 0.10, 0.10, 0.6)
        self._c_error:           Color = Color(0.25, 0.08, 0.08)
        self._border_c:          Color = Color(0.30, 0.30, 0.30)
        self._border_focused_c:  Color = Color(0.40, 0.40, 0.80)
        self._border_w:          float = 1.5
        self._corner_r:          float = 6.0
        self._selection_c:       Color = Color(0.26, 0.46, 0.76, 0.45)
        self._cursor_blink_rate: float = 0.53
        self._cur_color:         Color = self._c_normal

    # -----------------------------------------------------------------------
    # Build
    # -----------------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:
        theme = self._manager.theme if self._manager else None

        def _ov(override, default):
            return override if override is not None else default

        if theme:
            self._c_normal       = _ov(self._ov_color_normal,   theme.bg_normal)
            self._c_focused      = _ov(self._ov_color_focused,  theme.bg_focused)
            self._c_disabled     = _ov(self._ov_color_disabled, theme.bg_disabled)
            self._c_error        = _ov(self._ov_color_error,    Color(0.25, 0.08, 0.08))
            self._border_c       = _ov(self._ov_border_color,   theme.border_color)
            self._border_focused_c = _ov(self._ov_border_focused, theme.accent)
            self._border_w       = _ov(self._ov_border_width,   theme.border_width)
            self._corner_r       = _ov(self._ov_corner_radius,  theme.corner_radius)
            self._selection_c    = _ov(self._ov_selection_color, Color(0.26, 0.46, 0.76, 0.45))
            self._cursor_blink_rate = _ov(self._ov_cursor_blink_rate, theme.cursor_blink_rate)
            self._text_style     = self._ov_text_style or TextStyle(
                font=theme.font, font_size=theme.font_size, color=theme.text_color,
            )
        else:
            self._cursor_blink_rate = _ov(self._ov_cursor_blink_rate, 0.53)
            self._text_style = self._ov_text_style or DEFAULT_16_TEXT_STYLE

        self._cur_color = self._c_normal

        if self._size.x == 0 or self._size.y == 0:
            self._size.set(300.0, 120.0)

        self._dirty = False

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    @property
    def value(self) -> str:
        return "".join(self._chars)

    @value.setter
    def value(self, v: str) -> None:
        self._chars = list(v)
        self._cursor = len(self._chars)
        self._sel_start = self._sel_end = -1
        self._scroll_y = 0.0
        self._error_state = False

    # -----------------------------------------------------------------------
    # Internal helpers — shared with InputField pattern
    # -----------------------------------------------------------------------

    def _padding(self) -> tuple[float, float, float, float]:
        return (self.padding[0] or 8.0, self.padding[1] or 8.0,
                self.padding[2] or 8.0, self.padding[3] or 8.0)

    def _has_selection(self) -> bool:
        return self._sel_start != -1 and self._sel_start != self._sel_end

    def _selected_text(self) -> str:
        if not self._has_selection():
            return ""
        lo, hi = _sel_range(self._sel_start, self._sel_end)
        return "".join(self._chars[lo:hi])

    def _delete_selection(self) -> None:
        if not self._has_selection():
            return
        lo, hi = _sel_range(self._sel_start, self._sel_end)
        del self._chars[lo:hi]
        self._cursor = lo
        self._sel_start = self._sel_end = -1

    def _is_ctrl(self) -> bool:
        kb = self._manager._keyboard if self._manager else None
        if kb is None:
            return False
        return (glfw.KEY_LEFT_CONTROL in kb.pressed or
                glfw.KEY_RIGHT_CONTROL in kb.pressed)

    def _is_shift(self) -> bool:
        kb = self._manager._keyboard if self._manager else None
        if kb is None:
            return False
        return (glfw.KEY_LEFT_SHIFT in kb.pressed or
                glfw.KEY_RIGHT_SHIFT in kb.pressed)

    def _target_color(self) -> Color:
        if not self.enabled:
            return self._c_disabled
        if self._error_state:
            return self._c_error
        if self._focused:
            return self._c_focused
        return self._c_normal

    def _line_height(self) -> float:
        if not self._manager:
            return float(self._text_style.font_size) * 1.3
        tr = self._manager.text_renderer
        fa = tr._get_or_create_font_atlas(self._text_style.font, self._text_style.font_size)
        return fa['line_height'] * self._text_style.line_spacing

    def _lines(self) -> list[str]:
        return "".join(self._chars).split("\n")

    def _cursor_line_col(self) -> tuple[int, int]:
        """Return (line_index, col_index) for the current cursor position."""
        text = "".join(self._chars[:self._cursor])
        lines = text.split("\n")
        return len(lines) - 1, len(lines[-1])

    def _line_start_index(self, line_idx: int) -> int:
        """Return the flat char index of the start of *line_idx*."""
        lines = self._lines()
        idx = 0
        for i, ln in enumerate(lines):
            if i == line_idx:
                return idx
            idx += len(ln) + 1  # +1 for the \n
        return idx

    def _total_content_height(self) -> float:
        return len(self._lines()) * self._line_height()

    def _cursor_x_offset(self, col: int, line_idx: int) -> float:
        """X pixel offset of cursor at *col* on *line_idx*."""
        if not self._manager:
            return 0.0
        lines = self._lines()
        line  = lines[line_idx] if line_idx < len(lines) else ""
        return self._manager.text_renderer.get_text_width(line[:col],
                                                          style=self._text_style)

    def _char_at_xy(self, rel_x: float, rel_y: float) -> int:
        """Return flat char index for click at (rel_x, rel_y) inside text area."""
        if not self._manager:
            return 0
        lh     = self._line_height()
        lines  = self._lines()
        line_i = int(rel_y / lh) if lh > 0 else 0
        line_i = _clamp(line_i, 0, len(lines) - 1)
        line   = lines[line_i] # type: ignore
        tr     = self._manager.text_renderer

        x = 0.0
        col = len(line)
        for i, ch in enumerate(line):
            w = tr.get_text_width(ch, style=self._text_style)
            if rel_x < x + w * 0.5:
                col = i
                break
            x += w

        return self._line_start_index(line_i) + col # type: ignore

    def _ensure_cursor_visible(self) -> None:
        if not self._manager:
            return
        # In auto-expand mode the field grows to show all content,
        # so scrolling is only needed when capped at max_height.
        if self._auto_expand:
            uncapped = (self._max_height == 0 or
                        self._total_content_height() + self._padding()[0] + self._padding()[2]
                        <= self._max_height)
            if uncapped:
                return  # no scroll needed — height will expand to fit
        _, _, _, rh = self.get_screen_rect()
        pad = self._padding()
        inner_h = rh - pad[0] - pad[2]
        lh = self._line_height()
        line_i, _ = self._cursor_line_col()
        cy_top = line_i * lh
        cy_bot = cy_top + lh
        if cy_bot - self._scroll_y > inner_h:
            self._scroll_y = cy_bot - inner_h
        elif cy_top - self._scroll_y < 0:
            self._scroll_y = max(0.0, cy_top)

    def _reset_blink(self) -> None:
        self._cursor_vis  = True
        self._blink_timer = 0.0

    def _push_undo(self) -> None:
        """Snapshot current chars+cursor onto the undo stack; clear redo."""
        self._undo_stack.append((self._chars.copy(), self._cursor))
        if len(self._undo_stack) > 100:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    # -----------------------------------------------------------------------
    # Per-frame
    # -----------------------------------------------------------------------

    def update(self, dt: float) -> None:
        target = self._target_color()
        if self.animated and self._manager:
            t = min(1.0, self._manager.theme.animation_speed * dt)
            self._cur_color = self._cur_color.lerp(target, t)
        else:
            self._cur_color = target

        if self._focused:
            self._blink_timer += dt
            if self._blink_timer >= self._cursor_blink_rate:
                self._blink_timer = 0.0
                self._cursor_vis = not self._cursor_vis
        else:
            self._cursor_vis = False
            self._blink_timer = 0.0

        # Auto-expand: grow height to fit content
        if self._auto_expand and self._manager:
            pad = self._padding()
            needed = self._total_content_height() + pad[0] + pad[2]
            if self._min_height > 0:
                needed = max(needed, self._min_height)
            capped = self._max_height > 0 and needed > self._max_height
            if capped:
                needed = self._max_height
            else:
                # Not capped: no scroll needed, reset to 0
                self._scroll_y = 0.0
            if abs(self._size.y - needed) > 1.0:
                self._size.y = needed

        super().update(dt)

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return
        ctx = ctx or self._manager.ctx
        sr  = self._manager.shape_renderer
        tr  = self._manager.text_renderer

        rx, ry, rw, rh = self.get_screen_rect()
        pad = self._padding()
        alpha = self.opacity

        # Background
        c  = self._cur_color
        bc = self._border_focused_c if self._focused else self._border_c
        sr.draw_rect(
            V2(rx, ry), V2(rw, rh),
            color=(c.r, c.g, c.b, c.a * alpha),
            corner_radius=self._corner_r,
            border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
            border_width=self._border_w,
        )
        sr.flush_queue()

        # Scissor
        win_h = int(self._manager._window_size.y)
        ix  = int(rx + pad[3])
        iy  = int(ry + pad[0])
        iw  = max(1, int(rw - pad[1] - pad[3]))
        # Extend scissor to full widget bottom so descenders on the last
        # visible line are not clipped (bottom padding is text layout only).
        ih  = max(1, int(rh - pad[0]))
        ctx.scissor = (ix, win_h - iy - ih, iw, ih)

        lh     = self._line_height()
        lines  = self._lines()
        flat   = "".join(self._chars)
        text_x = rx + pad[3]
        theme  = self._manager.theme

        # Selection highlight
        if self._has_selection():
            lo, hi = _sel_range(self._sel_start, self._sel_end)
            sc = self._selection_c
            flat_idx = 0
            for li, line in enumerate(lines):
                line_start = self._line_start_index(li)
                line_end   = line_start + len(line)
                # Overlap with [lo, hi]?
                ol = max(lo, line_start)
                oh = min(hi, line_end)
                if ol < oh:
                    sel_col_lo = ol - line_start
                    sel_col_hi = oh - line_start
                    sel_x0 = text_x + tr.get_text_width(line[:sel_col_lo], style=self._text_style)
                    sel_x1 = text_x + tr.get_text_width(line[:sel_col_hi], style=self._text_style)
                    # Also select the newline gutter if selection crosses the line boundary
                    if hi > line_end:
                        sel_x1 = rx + rw - pad[1]
                    sel_y = ry + pad[0] + li * lh - self._scroll_y
                    sr.draw_rect(
                        V2(sel_x0, sel_y),
                        V2(sel_x1 - sel_x0, lh),
                        color=(sc.r, sc.g, sc.b, sc.a * alpha),
                        corner_radius=0.0,
                    )
            sr.flush_queue()

        # Text lines (or placeholder)
        if flat:
            ts = self._text_style
            for li, line in enumerate(lines):
                ty = ry + pad[0] + li * lh + lh * 0.5 - self._scroll_y
                if ty + lh < ry + pad[0] or ty - lh > ry + rh - pad[2]:
                    continue  # cull off-screen lines
                tr.draw_text(line, (text_x, ty), style=ts, pivot=Pivot.LEFT)
        elif self._placeholder:
            ph_color = theme.text_color_placeholder if theme else Color(0.45, 0.45, 0.45)
            ph_style = TextStyle(
                font=self._text_style.font,
                font_size=self._text_style.font_size,
                color=(ph_color.r, ph_color.g, ph_color.b, ph_color.a * alpha),
            )
            # Render each placeholder line separately so \n is respected
            ph_lines = self._placeholder.split("\n")
            for li, ph_line in enumerate(ph_lines):
                ty = ry + pad[0] + li * lh + lh * 0.5 - self._scroll_y
                if ty + lh < ry + pad[0] or ty - lh > ry + rh - pad[2]:
                    continue  # cull off-screen lines
                tr.draw_text(ph_line, (text_x, ty), style=ph_style, pivot=Pivot.LEFT)

        # Cursor
        if self._focused and self._cursor_vis:
            line_i, col = self._cursor_line_col()
            cx = text_x + self._cursor_x_offset(col, line_i)
            cy_top = ry + pad[0] + line_i * lh + 2 - self._scroll_y
            cy_bot = cy_top + lh - 4
            sr.draw_line(
                (cx, cy_top), (cx, cy_bot),
                color=(1.0, 1.0, 1.0, 0.85 * alpha),
                width=1.5,
            )
            sr.flush_queue()

        # Scrollbar
        if self._show_scrollbar and not self._auto_expand:
            total_h = self._total_content_height()
            if total_h > ih:
                sb_w    = 5.0
                sb_x    = rx + rw - pad[1] - sb_w
                sb_h    = ih
                sb_y    = ry + pad[0]
                ratio   = ih / total_h
                thumb_h = max(20.0, sb_h * ratio)
                thumb_y = sb_y + (self._scroll_y / max(1.0, total_h - ih)) * (sb_h - thumb_h)
                # Track
                sr.draw_rect(V2(sb_x, sb_y), V2(sb_w, sb_h),
                             color=(0.15, 0.15, 0.15, 0.5 * alpha), corner_radius=3.0)
                # Thumb
                sr.draw_rect(V2(sb_x, thumb_y), V2(sb_w, thumb_h),
                             color=(0.55, 0.55, 0.55, 0.8 * alpha), corner_radius=3.0)
                sr.flush_queue()

        ctx.scissor = None

    # -----------------------------------------------------------------------
    # Mouse events
    # -----------------------------------------------------------------------

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False

    def on_mouse_press(self, mx: float, my: float) -> None:
        if not self.enabled:
            return
        rx, ry, _, _ = self.get_screen_rect()
        pad = self._padding()
        rel_x = mx - (rx + pad[3])
        rel_y = my - (ry + pad[0]) + self._scroll_y
        self._cursor = self._char_at_xy(rel_x, rel_y)
        self._sel_start = self._cursor
        self._sel_end   = self._cursor
        self._reset_blink()
        self._error_state = False

    def on_mouse_drag(self, mx: float, my: float, dx: float, dy: float) -> None:
        if not self.enabled:
            return
        rx, ry, _, _ = self.get_screen_rect()
        pad = self._padding()
        rel_x = mx - (rx + pad[3])
        rel_y = my - (ry + pad[0]) + self._scroll_y
        self._cursor = self._char_at_xy(rel_x, rel_y)
        self._sel_end = self._cursor

    # Scroll with mouse wheel when hovered/focused
    def on_scroll(self, dy: float) -> None:
        if not self._manager:
            return
        theme = self._manager.theme
        spd = theme.scroll_speed if theme else 40.0
        _, _, _, rh = self.get_screen_rect()
        pad = self._padding()
        inner_h  = rh - pad[0] - pad[2]
        total_h  = self._total_content_height()
        max_scroll = max(0.0, total_h - inner_h)
        self._scroll_y = _clamp(self._scroll_y - dy * spd, 0.0, max_scroll)

    # -----------------------------------------------------------------------
    # Focus
    # -----------------------------------------------------------------------

    def on_focus(self) -> None:
        super().on_focus()
        self._reset_blink()

    def on_blur(self) -> None:
        super().on_blur()
        self._sel_start = self._sel_end = -1

    # -----------------------------------------------------------------------
    # Keyboard
    # -----------------------------------------------------------------------

    def on_char_input(self, chars: list[str]) -> None:
        if not self.enabled:
            return
        if not self._undo_coalescing:
            self._undo_stack.append((self._chars.copy(), self._cursor))
            if len(self._undo_stack) > 100:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
            self._undo_coalescing = True
        for ch in chars:
            self._insert_char(ch)

    def on_key_press(self, key: int) -> None:
        if not self.enabled:
            return
        ctrl  = self._is_ctrl()
        shift = self._is_shift()
        # Any explicit key press ends char-input coalescing
        self._undo_coalescing = False

        if key == glfw.KEY_BACKSPACE:
            self._push_undo()
            if self._has_selection():
                self._delete_selection()
            elif self._cursor > 0:
                if ctrl:
                    word_start = self._find_word_start(self._cursor)
                    del self._chars[word_start:self._cursor]
                    self._cursor = word_start
                else:
                    del self._chars[self._cursor - 1]
                    self._cursor -= 1
            self._error_state = False

        elif key == glfw.KEY_DELETE:
            self._push_undo()
            if self._has_selection():
                self._delete_selection()
            elif self._cursor < len(self._chars):
                if ctrl:
                    word_end = self._find_word_end(self._cursor)
                    del self._chars[self._cursor:word_end]
                else:
                    del self._chars[self._cursor]
            self._error_state = False

        elif key == glfw.KEY_ENTER or key == glfw.KEY_KP_ENTER:
            if ctrl:
                self._submit()
            else:
                self._insert_char('\n')

        elif key == glfw.KEY_TAB:
            # Tab inserts spaces — focus navigation handled by UIManager
            # only when Ctrl+Tab is pressed (UIManager consumes plain Tab)
            spaces = ' ' * self._tab_width
            for ch in spaces:
                self._insert_char(ch)
            return  # don't process further

        elif key == glfw.KEY_LEFT:
            if shift:
                if self._sel_start == -1:
                    self._sel_start = self._cursor
                self._cursor = max(0, self._cursor - 1)
                self._sel_end = self._cursor
            else:
                if self._has_selection():
                    lo, _ = _sel_range(self._sel_start, self._sel_end)
                    self._cursor = lo
                    self._sel_start = self._sel_end = -1
                elif self._cursor > 0:
                    self._cursor -= 1

        elif key == glfw.KEY_RIGHT:
            if shift:
                if self._sel_start == -1:
                    self._sel_start = self._cursor
                self._cursor = min(len(self._chars), self._cursor + 1)
                self._sel_end = self._cursor
            else:
                if self._has_selection():
                    _, hi = _sel_range(self._sel_start, self._sel_end)
                    self._cursor = hi
                    self._sel_start = self._sel_end = -1
                elif self._cursor < len(self._chars):
                    self._cursor += 1

        elif key == glfw.KEY_UP:
            line_i, col = self._cursor_line_col()
            if line_i > 0:
                lines = self._lines()
                prev_line = lines[line_i - 1]
                new_col = min(col, len(prev_line))
                self._cursor = self._line_start_index(line_i - 1) + new_col
                if shift:
                    if self._sel_start == -1:
                        self._sel_start = self._cursor
                    self._sel_end = self._cursor
                else:
                    self._sel_start = self._sel_end = -1

        elif key == glfw.KEY_DOWN:
            line_i, col = self._cursor_line_col()
            lines = self._lines()
            if line_i < len(lines) - 1:
                next_line = lines[line_i + 1]
                new_col = min(col, len(next_line))
                self._cursor = self._line_start_index(line_i + 1) + new_col
                if shift:
                    if self._sel_start == -1:
                        self._sel_start = self._cursor
                    self._sel_end = self._cursor
                else:
                    self._sel_start = self._sel_end = -1

        elif key == glfw.KEY_HOME:
            line_i, _ = self._cursor_line_col()
            new_pos = self._line_start_index(line_i)
            if shift:
                if self._sel_start == -1:
                    self._sel_start = self._cursor
                self._cursor = new_pos
                self._sel_end = self._cursor
            else:
                self._cursor = new_pos
                self._sel_start = self._sel_end = -1

        elif key == glfw.KEY_END:
            line_i, _ = self._cursor_line_col()
            lines = self._lines()
            line  = lines[line_i] if line_i < len(lines) else ""
            new_pos = self._line_start_index(line_i) + len(line)
            if shift:
                if self._sel_start == -1:
                    self._sel_start = self._cursor
                self._cursor = new_pos
                self._sel_end = self._cursor
            else:
                self._cursor = new_pos
                self._sel_start = self._sel_end = -1

        elif ctrl and key == glfw.KEY_A:
            self._sel_start = 0
            self._sel_end   = len(self._chars)
            self._cursor    = len(self._chars)

        elif ctrl and key == glfw.KEY_C:
            sel = self._selected_text()
            if sel and self._manager and self._manager._window:
                glfw.set_clipboard_string(self._manager._window, sel)

        elif ctrl and key == glfw.KEY_X:
            sel = self._selected_text()
            if sel and self._manager and self._manager._window:
                self._push_undo()
                glfw.set_clipboard_string(self._manager._window, sel)
                self._delete_selection()
                self._error_state = False

        elif ctrl and key == glfw.KEY_V:
            if self._manager and self._manager._window:
                clip = glfw.get_clipboard_string(self._manager._window)
                if clip:
                    # glfw may return bytes on Linux — decode to str
                    if isinstance(clip, (bytes, bytearray)):
                        clip = clip.decode('utf-8', errors='replace')
                    self._push_undo()
                    if self._has_selection():
                        self._delete_selection()
                    for ch in clip:
                        self._insert_char(ch)
                    self._error_state = False

        elif ctrl and key == glfw.KEY_Z:
            if shift:
                # Ctrl+Shift+Z — redo
                if self._redo_stack:
                    self._undo_stack.append((self._chars.copy(), self._cursor))
                    chs, cur = self._redo_stack.pop()
                    self._chars  = list(chs)
                    self._cursor = int(_clamp(cur, 0, len(self._chars)))
                    self._sel_start = self._sel_end = -1
            else:
                # Ctrl+Z — undo
                if self._undo_stack:
                    self._redo_stack.append((self._chars.copy(), self._cursor))
                    chs, cur = self._undo_stack.pop()
                    self._chars  = list(chs)
                    self._cursor = int(_clamp(cur, 0, len(self._chars)))
                    self._sel_start = self._sel_end = -1

        self._ensure_cursor_visible()
        self._reset_blink()

    # -----------------------------------------------------------------------
    # Editing helpers
    # -----------------------------------------------------------------------

    def _insert_char(self, ch: str) -> None:
        if not isinstance(ch, str):
            return  # guard against bytes iteration on clipboard paste
        if self._max_length is not None and len(self._chars) >= self._max_length:
            return
        if self._has_selection():
            self._delete_selection()
        self._chars.insert(self._cursor, ch)
        self._cursor += 1
        self._ensure_cursor_visible()
        self._reset_blink()

    def _submit(self) -> None:
        val = self.value
        if self._validate is not None and not self._validate(val):
            self._error_state = True
            return
        self._error_state = False
        if self._on_submit:
            self._on_submit(val)

    def _find_word_start(self, pos: int) -> int:
        i = pos - 1
        while i > 0 and not self._chars[i - 1].isspace():
            i -= 1
        return i

    def _find_word_end(self, pos: int) -> int:
        i = pos
        n = len(self._chars)
        while i < n and not self._chars[i].isspace():
            i += 1
        return i

    def release(self) -> None:
        super().release()
