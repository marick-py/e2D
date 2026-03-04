"""
Slider and RangeSlider — single and dual-handle value selectors.

Usage::

    # horizontal slider 0–100, step 5
    sl = env.ui.slider(0, 100, step=5, value=40, on_change=on_vol,
                       position=V2(50, 200), size=V2(300, 20))

    # vertical slider
    sl = Slider(0.0, 1.0, orientation='vertical', show_labels=True,
                position=V2(20, 50), size=V2(20, 200))
    env.ui.add(sl)

    # range slider
    rs = env.ui.range_slider(0, 255, step=1,
                             low_value=64, high_value=192,
                             on_change=lambda lo, hi: print(lo, hi))

Keyboard (when focused):
    Horizontal: Left/Right arrows move the value.
    Vertical  : Up/Down arrows move the value.

Mouse modifiers during drag:
    Hold Ctrl  → snap to step increments.
    Hold Shift → fine control (10× less sensitive).
"""

from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from .base import UIElement
from .label import Label
from ..colors import Color
from .._pivot import Pivot
from ..text import DEFAULT_16_TEXT_STYLE, TextStyle
from ..vectors import V2

if TYPE_CHECKING:
    from .._types import ContextType
    from ..text import TextRenderer


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else (hi if v > hi else v)


def _snap(v: float, step: float, origin: float) -> float:
    """Snap v to the nearest multiple of step originating at origin."""
    if step <= 0:
        return v
    return origin + round((v - origin) / step) * step


# ---------------------------------------------------------------------------
# Slider
# ---------------------------------------------------------------------------

class Slider(UIElement):
    """Single-handle slider.

    Constructor keyword arguments beyond the standard :class:`UIElement` ones:

    * ``start``, ``end``  — float range (``start < end`` required)
    * ``step``            — snap granularity; ``None`` = continuous
    * ``value``           — initial value (clamped/snapped to range)
    * ``on_change``       — ``callable(float)``
    * ``orientation``     — ``'horizontal'`` (default) or ``'vertical'``
    * ``show_labels``     — show start/end/current value labels (default: ``False``)
    * ``animated``        — smooth thumb animation (default: ``True``)
    * ``color_track``     — empty track colour
    * ``color_fill``      — filled portion colour
    * ``color_thumb``     — thumb circle colour
    * ``color_disabled``  — all colours when ``enabled=False``
    * ``label_style``     — :class:`TextStyle` for value/range labels
    """

    def __init__(
        self,
        start: float = 0.0,
        end:   float = 1.0,
        step:  float | None = None,
        value: float | None = None,
        on_change: Callable[[float], None] | None = None,
        *,
        orientation:  str = 'horizontal',
        show_labels:  bool = False,
        animated:     bool = True,
        color_track:    Color | None = None,
        color_fill:     Color | None = None,
        color_thumb:    Color | None = None,
        color_disabled: Color | None = None,
        label_style:    TextStyle | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._focusable = True

        self.start = float(start)
        self.end   = float(end)
        if self.end <= self.start:
            self.end = self.start + 1.0
        self.step = step

        raw = float(value) if value is not None else self.start
        self._value = _clamp(raw, self.start, self.end)
        if step is not None:
            self._value = _snap(self._value, step, self.start)

        self._on_change: Callable[[float], None] | None = on_change
        self.orientation: str = orientation
        self.show_labels:  bool = show_labels
        self.animated:     bool = animated

        # Style overrides
        self._ov_color_track    = color_track
        self._ov_color_fill     = color_fill
        self._ov_color_thumb    = color_thumb
        self._ov_color_disabled = color_disabled
        self._ov_label_style    = label_style

        # Resolved colours
        self._c_track    = Color(0.22, 0.22, 0.22)
        self._c_fill     = Color(0.384, 0.0, 0.933)
        self._c_thumb    = Color(1.0, 1.0, 1.0)
        self._c_disabled = Color(0.15, 0.15, 0.15, 0.6)

        # Animated thumb fraction (0.0–1.0 across the track)
        self._thumb_frac: float = self._to_frac(self._value)
        self._dragging:   bool  = False
        self._is_hovered: bool  = False

        # Internal labels (created during _build when show_labels=True)
        self._lbl_min:   Optional[Label] = None
        self._lbl_max:   Optional[Label] = None
        self._lbl_value: Optional[Label] = None

    # ---------------------------------------------------------------------------
    # Build
    # ---------------------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:  # type: ignore[override]
        theme = self._manager.theme if self._manager else None

        def _ov(override, default):
            return override if override is not None else default

        if theme:
            self._c_track    = _ov(self._ov_color_track,    theme.bg_normal)
            self._c_fill     = _ov(self._ov_color_fill,     theme.primary)
            self._c_thumb    = _ov(self._ov_color_thumb,    Color(1.0, 1.0, 1.0))
            self._c_disabled = _ov(self._ov_color_disabled, theme.bg_disabled)
            lst = self._ov_label_style or TextStyle(
                font=theme.font_mono, font_size=12, color=theme.text_color)
        else:
            lst = self._ov_label_style or DEFAULT_16_TEXT_STYLE

        if self._size.x == 0 or self._size.y == 0:
            if self.orientation == 'horizontal':
                self._size.set(200.0, 20.0)
            else:
                self._size.set(20.0, 200.0)

        if self.show_labels:
            def _make(t: str) -> Label:
                lbl = Label(t, default_style=lst)
                lbl._build(ctx, text_renderer)
                return lbl

            self._lbl_min   = _make(self._fmt(self.start))
            self._lbl_max   = _make(self._fmt(self.end))
            self._lbl_value = _make(self._fmt(self._value))

        self._thumb_frac = self._to_frac(self._value)
        self._dirty = False

    # ---------------------------------------------------------------------------
    # Value API
    # ---------------------------------------------------------------------------

    def _to_frac(self, v: float) -> float:
        r = self.end - self.start
        return (v - self.start) / r if r != 0 else 0.0

    def _from_frac(self, f: float) -> float:
        v = self.start + _clamp(f, 0.0, 1.0) * (self.end - self.start)
        if self.step is not None:
            v = _snap(v, self.step, self.start)
        return _clamp(v, self.start, self.end)

    def _fmt(self, v: float) -> str:
        return str(int(v)) if (self.step is not None and self.step >= 1) else f"{v:.2f}"

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float) -> None:
        v = _clamp(float(v), self.start, self.end)
        if self.step is not None:
            v = _snap(v, self.step, self.start)
        if v != self._value:
            self._value = v
            if self._on_change:
                self._on_change(v)

    # ---------------------------------------------------------------------------
    # Track / thumb geometry helpers
    # ---------------------------------------------------------------------------

    def _track_rect(self) -> tuple[float, float, float, float]:
        """Return (x, y, w, h) of the visible track bar, in screen coords."""
        rx, ry, rw, rh = self.get_screen_rect()
        if self.orientation == 'horizontal':
            pad = rh * 0.5           # leave room for thumb overhang
            ty  = ry + rh * 0.5 - rh * 0.25
            return (rx + pad, ty, rw - pad * 2, rh * 0.5)
        else:
            pad = rw * 0.5
            tx  = rx + rw * 0.5 - rw * 0.25
            return (tx, ry + pad, rw * 0.5, rh - pad * 2)

    def _thumb_center(self, frac: float) -> tuple[float, float]:
        rx, ry, rw, rh = self.get_screen_rect()
        if self.orientation == 'horizontal':
            pad = rh * 0.5
            return (rx + pad + frac * (rw - 2 * pad), ry + rh * 0.5)
        else:
            pad = rw * 0.5
            return (rx + rw * 0.5, ry + pad + frac * (rh - 2 * pad))

    def _thumb_radius(self) -> float:
        _, _, rw, rh = self.get_screen_rect()
        return (rh if self.orientation == 'horizontal' else rw) * 0.5

    # ---------------------------------------------------------------------------
    # Per-frame
    # ---------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        target_frac = self._to_frac(self._value)

        # Only animate when not dragging (drag sets frac immediately)
        if self.animated and self._manager and not self._dragging:
            t = min(1.0, self._manager.theme.animation_speed * dt)
            self._thumb_frac += (target_frac - self._thumb_frac) * t
        else:
            self._thumb_frac = target_frac

        if self.show_labels and self._lbl_value is not None:
            self._lbl_value.set_plain_text(self._fmt(self._value))

        super().update(dt)

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return

        sr   = self._manager.shape_renderer
        mctx = ctx or self._manager.ctx
        rx, ry, rw, rh = self.get_screen_rect()
        alpha    = self.opacity
        is_horiz = self.orientation == 'horizontal'

        c_track = self._c_track if self.enabled else self._c_disabled
        c_fill  = self._c_fill  if self.enabled else self._c_disabled
        c_thumb = self._c_thumb if self.enabled else self._c_disabled

        tx, ty, tw, th = self._track_rect()
        track_r = (th if is_horiz else tw) * 0.5

        # Empty track  (layer 0 — drawn first)
        sr.draw_rect(
            V2(tx, ty), V2(tw, th),
            color=(c_track.r, c_track.g, c_track.b, c_track.a * alpha),
            corner_radius=track_r,
            layer=0,
        )

        # Filled portion  (layer 0 — same pass as track, on top because of insertion order)
        if is_horiz:
            fw = tw * self._thumb_frac
            if fw > 0:
                sr.draw_rect(
                    V2(tx, ty), V2(fw, th),
                    color=(c_fill.r, c_fill.g, c_fill.b, c_fill.a * alpha),
                    corner_radius=track_r,
                    layer=0,
                )
        else:
            fh = th * self._thumb_frac
            if fh > 0:
                # Fill from TOP down to thumb (frac=0 → top, frac=1 → bottom)
                sr.draw_rect(
                    V2(tx, ty), V2(tw, fh),
                    color=(c_fill.r, c_fill.g, c_fill.b, c_fill.a * alpha),
                    corner_radius=track_r,
                    layer=0,
                )

        # Thumb circle  (layer 1 — drawn AFTER all layer-0 rects)
        thumb_x, thumb_y = self._thumb_center(self._thumb_frac)
        thumb_r = self._thumb_radius()
        sr.draw_circle(
            V2(thumb_x, thumb_y), thumb_r,
            color=(c_thumb.r, c_thumb.g, c_thumb.b, c_thumb.a * alpha),
            border_color=(c_fill.r, c_fill.g, c_fill.b, c_fill.a * alpha * 0.6),
            border_width=1.5,
            layer=1,
        )

        # Optional labels  (flush deferred shapes first so labels render on top)
        if self.show_labels:
            sr.flush_queue()
            if is_horiz:
                if self._lbl_min is not None:
                    self._lbl_min._position.set(tx, ry + rh + 4)
                    self._lbl_min.pivot = Pivot.TOP_LEFT
                    self._lbl_min.draw(mctx)
                if self._lbl_max is not None:
                    self._lbl_max._position.set(tx + tw, ry + rh + 4)
                    self._lbl_max.pivot = Pivot.TOP_RIGHT
                    self._lbl_max.draw(mctx)
                if self._lbl_value is not None:
                    self._lbl_value._position.set(thumb_x, ry - 4)
                    self._lbl_value.pivot = Pivot.BOTTOM_MIDDLE
                    self._lbl_value.draw(mctx)
            else:
                if self._lbl_min is not None:
                    self._lbl_min._position.set(rx + rw + 4, ty + th)
                    self._lbl_min.pivot = Pivot.LEFT
                    self._lbl_min.draw(mctx)
                if self._lbl_max is not None:
                    self._lbl_max._position.set(rx + rw + 4, ty)
                    self._lbl_max.pivot = Pivot.LEFT
                    self._lbl_max.draw(mctx)
                if self._lbl_value is not None:
                    self._lbl_value._position.set(rx - 4, thumb_y)
                    self._lbl_value.pivot = Pivot.RIGHT
                    self._lbl_value.draw(mctx)

    # ---------------------------------------------------------------------------
    # Event hooks
    # ---------------------------------------------------------------------------

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False

    def on_mouse_press(self, mx: float, my: float) -> None:
        if not self.enabled:
            return
        self._dragging = True
        # Immediately set value to click position (snap if step)
        self._apply_mouse_pos(mx, my, snap_to_step=self.step is not None)

    def on_mouse_drag(self, mx: float, my: float, dx: float, dy: float) -> None:
        if not self._dragging or not self.enabled:
            return
        kb   = getattr(self._manager, '_keyboard', None) if self._manager else None
        snap = False
        fine = False
        if kb is not None:
            from ..input import Keys
            snap = kb.get_key(Keys.LEFT_CONTROL) or kb.get_key(Keys.RIGHT_CONTROL)
            fine = kb.get_key(Keys.LEFT_SHIFT)   or kb.get_key(Keys.RIGHT_SHIFT)
        self._apply_mouse_pos(mx, my, snap_to_step=snap, fine=fine)

    def on_mouse_release(self, mx: float, my: float) -> None:
        self._dragging = False

    def on_key_press(self, key: int) -> None:
        import glfw
        if not self.enabled:
            return
        key_step = self.step if self.step is not None else (self.end - self.start) / 100.0
        if self.orientation == 'horizontal':
            if key == glfw.KEY_RIGHT:
                self.value = self._value + key_step
            elif key == glfw.KEY_LEFT:
                self.value = self._value - key_step
        else:
            if key == glfw.KEY_UP:
                self.value = self._value + key_step
            elif key == glfw.KEY_DOWN:
                self.value = self._value - key_step

    # ---------------------------------------------------------------------------
    # Internal drag math
    # ---------------------------------------------------------------------------

    def _apply_mouse_pos(
        self,
        mx: float, my: float,
        snap_to_step: bool = False,
        fine: bool = False,
    ) -> None:
        rx, ry, rw, rh = self.get_screen_rect()
        is_horiz = self.orientation == 'horizontal'
        pad  = (rh if is_horiz else rw) * 0.5

        if is_horiz:
            usable = rw - 2 * pad
            frac   = (mx - rx - pad) / usable if usable > 0 else 0.0
        else:
            usable = rh - 2 * pad
            frac   = (my - ry - pad) / usable if usable > 0 else 0.0

        if fine:
            # Shrink sensitivity: map full-range to 1/10 of normal
            cur_frac = self._to_frac(self._value)
            frac     = cur_frac + (frac - cur_frac) * 0.1

        frac = _clamp(frac, 0.0, 1.0)
        v    = self.start + frac * (self.end - self.start)

        if snap_to_step and self.step is not None:
            v = _snap(v, self.step, self.start)
        elif self.step is not None:
            v = _snap(v, self.step, self.start)

        v = _clamp(v, self.start, self.end)
        if v != self._value:
            self._value      = v
            self._thumb_frac = self._to_frac(v)
            if self._on_change:
                self._on_change(v)

    # ---------------------------------------------------------------------------
    # Debug info
    # ---------------------------------------------------------------------------

    def _debug_info(self) -> list[tuple[str, str]]:
        rows = super()._debug_info()
        rows += [
            ("value",  self._fmt(self._value)),
            ("range",  f"{self._fmt(self.start)} -> {self._fmt(self.end)}"),
            ("step",   str(self.step) if self.step is not None else "continuous"),
            ("orient", self.orientation),
            ("drag",   "yes" if self._dragging else "no"),
        ]
        return rows

    # ---------------------------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------------------------

    def release(self) -> None:
        for lbl in (self._lbl_min, self._lbl_max, self._lbl_value):
            if lbl is not None:
                lbl.release()
        self._lbl_min = self._lbl_max = self._lbl_value = None
        super().release()


# ---------------------------------------------------------------------------
# RangeSlider
# ---------------------------------------------------------------------------

class RangeSlider(UIElement):
    """Two-handle slider for selecting a [low, high] sub-range.

    The two handles cannot cross; the filled region always shows the selected
    interval.

    Constructor keyword arguments beyond the standard :class:`UIElement` ones:

    * ``start``, ``end``       — float range
    * ``step``                 — snap granularity; ``None`` = continuous
    * ``low_value``            — initial low handle position
    * ``high_value``           — initial high handle position
    * ``on_change``            — ``callable(float, float)`` with ``(low, high)``
    * ``orientation``          — ``'horizontal'`` or ``'vertical'``
    * ``show_labels``          — show start/end/current labels (default: ``False``)
    * ``animated``             — smooth handle animation (default: ``True``)
    * ``color_track``          — empty track colour
    * ``color_fill``           — filled interval colour
    * ``color_thumb_low``      — low-handle thumb colour
    * ``color_thumb_high``     — high-handle thumb colour
    * ``color_disabled``       — colour when ``enabled=False``
    * ``label_style``          — :class:`TextStyle` for labels
    """

    def __init__(
        self,
        start: float = 0.0,
        end:   float = 1.0,
        step:  float | None = None,
        low_value:  float | None = None,
        high_value: float | None = None,
        on_change: Callable[[float, float], None] | None = None,
        *,
        orientation:     str = 'horizontal',
        show_labels:     bool = False,
        animated:        bool = True,
        color_track:      Color | None = None,
        color_fill:       Color | None = None,
        color_thumb_low:  Color | None = None,
        color_thumb_high: Color | None = None,
        color_disabled:   Color | None = None,
        label_style:      TextStyle | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._focusable = True

        self.start = float(start)
        self.end   = float(end)
        if self.end <= self.start:
            self.end = self.start + 1.0
        self.step = step

        lo = _clamp(float(low_value  if low_value  is not None else self.start), self.start, self.end)
        hi = _clamp(float(high_value if high_value is not None else self.end),   self.start, self.end)
        if step is not None:
            lo = _snap(lo, step, self.start)
            hi = _snap(hi, step, self.start)
        if lo > hi:
            lo, hi = hi, lo

        self._low:  float = lo
        self._high: float = hi
        self._on_change: Callable[[float, float], None] | None = on_change
        self.orientation: str  = orientation
        self.show_labels:  bool = show_labels
        self.animated:     bool = animated

        # Style overrides
        self._ov_color_track      = color_track
        self._ov_color_fill       = color_fill
        self._ov_color_thumb_low  = color_thumb_low
        self._ov_color_thumb_high = color_thumb_high
        self._ov_color_disabled   = color_disabled
        self._ov_label_style      = label_style

        # Resolved colours
        self._c_track      = Color(0.22, 0.22, 0.22)
        self._c_fill       = Color(0.384, 0.0, 0.933)
        self._c_thumb_low  = Color(1.0, 1.0, 1.0)
        self._c_thumb_high = Color(0.85, 0.85, 0.85)
        self._c_disabled   = Color(0.15, 0.15, 0.15, 0.6)

        # Animated fractions
        self._low_frac:  float = self._to_frac(lo)
        self._high_frac: float = self._to_frac(hi)

        # 0 = not dragging, 1 = low handle, 2 = high handle
        self._drag_handle: int = 0
        self._is_hovered:  bool = False

        # Labels
        self._lbl_min:  Optional[Label] = None
        self._lbl_max:  Optional[Label] = None
        self._lbl_low:  Optional[Label] = None
        self._lbl_high: Optional[Label] = None

    # ---------------------------------------------------------------------------
    # Build
    # ---------------------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:  # type: ignore[override]
        theme = self._manager.theme if self._manager else None

        def _ov(override, default):
            return override if override is not None else default

        if theme:
            self._c_track      = _ov(self._ov_color_track,      theme.bg_normal)
            self._c_fill       = _ov(self._ov_color_fill,        theme.primary)
            self._c_thumb_low  = _ov(self._ov_color_thumb_low,  Color(1.0, 1.0, 1.0))
            self._c_thumb_high = _ov(self._ov_color_thumb_high, Color(0.85, 0.85, 0.85))
            self._c_disabled   = _ov(self._ov_color_disabled,   theme.bg_disabled)
            lst = self._ov_label_style or TextStyle(
                font=theme.font_mono, font_size=12, color=theme.text_color)
        else:
            lst = self._ov_label_style or DEFAULT_16_TEXT_STYLE

        if self._size.x == 0 or self._size.y == 0:
            if self.orientation == 'horizontal':
                self._size.set(200.0, 20.0)
            else:
                self._size.set(20.0, 200.0)

        if self.show_labels:
            def _make(t: str) -> Label:
                lbl = Label(t, default_style=lst)
                lbl._build(ctx, text_renderer)
                return lbl

            self._lbl_min  = _make(self._fmt(self.start))
            self._lbl_max  = _make(self._fmt(self.end))
            self._lbl_low  = _make(self._fmt(self._low))
            self._lbl_high = _make(self._fmt(self._high))

        self._low_frac  = self._to_frac(self._low)
        self._high_frac = self._to_frac(self._high)
        self._dirty = False

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _to_frac(self, v: float) -> float:
        r = self.end - self.start
        return (v - self.start) / r if r != 0 else 0.0

    def _fmt(self, v: float) -> str:
        return str(int(v)) if (self.step is not None and self.step >= 1) else f"{v:.2f}"

    def _track_rect(self) -> tuple[float, float, float, float]:
        rx, ry, rw, rh = self.get_screen_rect()
        is_horiz = self.orientation == 'horizontal'
        if is_horiz:
            pad = rh * 0.5
            ty  = ry + rh * 0.5 - rh * 0.25
            return (rx + pad, ty, rw - pad * 2, rh * 0.5)
        else:
            pad = rw * 0.5
            tx  = rx + rw * 0.5 - rw * 0.25
            return (tx, ry + pad, rw * 0.5, rh - pad * 2)

    def _thumb_pos(self, frac: float) -> tuple[float, float]:
        rx, ry, rw, rh = self.get_screen_rect()
        if self.orientation == 'horizontal':
            pad = rh * 0.5
            return (rx + pad + frac * (rw - 2 * pad), ry + rh * 0.5)
        else:
            pad = rw * 0.5
            return (rx + rw * 0.5, ry + pad + frac * (rh - 2 * pad))

    def _thumb_radius(self) -> float:
        _, _, rw, rh = self.get_screen_rect()
        return (rh if self.orientation == 'horizontal' else rw) * 0.5

    # ---------------------------------------------------------------------------
    # Value properties
    # ---------------------------------------------------------------------------

    @property
    def low_value(self) -> float:
        return self._low

    @low_value.setter
    def low_value(self, v: float) -> None:
        v = _clamp(float(v), self.start, self._high)
        if self.step is not None:
            v = _snap(v, self.step, self.start)
        if v != self._low:
            self._low = v
            if self._on_change:
                self._on_change(self._low, self._high)

    @property
    def high_value(self) -> float:
        return self._high

    @high_value.setter
    def high_value(self, v: float) -> None:
        v = _clamp(float(v), self._low, self.end)
        if self.step is not None:
            v = _snap(v, self.step, self.start)
        if v != self._high:
            self._high = v
            if self._on_change:
                self._on_change(self._low, self._high)

    # ---------------------------------------------------------------------------
    # Per-frame
    # ---------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        target_lo = self._to_frac(self._low)
        target_hi = self._to_frac(self._high)

        if self.animated and self._manager and self._drag_handle == 0:
            t = min(1.0, self._manager.theme.animation_speed * dt)
            self._low_frac  += (target_lo - self._low_frac)  * t
            self._high_frac += (target_hi - self._high_frac) * t
        else:
            self._low_frac  = target_lo
            self._high_frac = target_hi

        if self.show_labels:
            if self._lbl_low  is not None:
                self._lbl_low.set_plain_text(self._fmt(self._low))
            if self._lbl_high is not None:
                self._lbl_high.set_plain_text(self._fmt(self._high))

        super().update(dt)

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return

        sr   = self._manager.shape_renderer
        mctx = ctx or self._manager.ctx
        rx, ry, rw, rh = self.get_screen_rect()
        alpha    = self.opacity
        is_horiz = self.orientation == 'horizontal'

        c_track = self._c_track      if self.enabled else self._c_disabled
        c_fill  = self._c_fill       if self.enabled else self._c_disabled
        c_lo    = self._c_thumb_low  if self.enabled else self._c_disabled
        c_hi    = self._c_thumb_high if self.enabled else self._c_disabled

        tx, ty, tw, th = self._track_rect()
        track_r = (th if is_horiz else tw) * 0.5

        # Empty track  (layer 0)
        sr.draw_rect(
            V2(tx, ty), V2(tw, th),
            color=(c_track.r, c_track.g, c_track.b, c_track.a * alpha),
            corner_radius=track_r,
            layer=0,
        )

        # Filled region between handles  (layer 0)
        lo_pos = self._thumb_pos(self._low_frac)
        hi_pos = self._thumb_pos(self._high_frac)
        if is_horiz:
            fill_w = hi_pos[0] - lo_pos[0]
            if fill_w > 0:
                sr.draw_rect(
                    V2(lo_pos[0], ty), V2(fill_w, th),
                    color=(c_fill.r, c_fill.g, c_fill.b, c_fill.a * alpha),
                    corner_radius=track_r,
                    layer=0,
                )
        else:
            fill_h = hi_pos[1] - lo_pos[1]
            if fill_h > 0:
                sr.draw_rect(
                    V2(tx, lo_pos[1]), V2(tw, fill_h),
                    color=(c_fill.r, c_fill.g, c_fill.b, c_fill.a * alpha),
                    corner_radius=track_r,
                    layer=0,
                )

        thumb_r = self._thumb_radius()

        # Low handle  (layer 1 — on top of all track rects)
        sr.draw_circle(
            V2(*lo_pos), thumb_r,
            color=(c_lo.r, c_lo.g, c_lo.b, c_lo.a * alpha),
            border_color=(c_fill.r, c_fill.g, c_fill.b, c_fill.a * alpha * 0.6),
            border_width=1.5,
            layer=1,
        )
        # High handle  (layer 1)
        sr.draw_circle(
            V2(*hi_pos), thumb_r,
            color=(c_hi.r, c_hi.g, c_hi.b, c_hi.a * alpha),
            border_color=(c_fill.r, c_fill.g, c_fill.b, c_fill.a * alpha * 0.6),
            border_width=1.5,
            layer=1,
        )

        # Labels  (flush deferred shapes first so labels render on top)
        if self.show_labels:
            sr.flush_queue()
            if is_horiz:
                if self._lbl_min is not None:
                    self._lbl_min._position.set(tx, ry + rh + 4)
                    self._lbl_min.pivot = Pivot.TOP_LEFT
                    self._lbl_min.draw(mctx)
                if self._lbl_max is not None:
                    self._lbl_max._position.set(tx + tw, ry + rh + 4)
                    self._lbl_max.pivot = Pivot.TOP_RIGHT
                    self._lbl_max.draw(mctx)
                if self._lbl_low is not None:
                    self._lbl_low._position.set(lo_pos[0], ry - 4)
                    self._lbl_low.pivot = Pivot.BOTTOM_MIDDLE
                    self._lbl_low.draw(mctx)
                if self._lbl_high is not None:
                    self._lbl_high._position.set(hi_pos[0], ry - 4)
                    self._lbl_high.pivot = Pivot.BOTTOM_MIDDLE
                    self._lbl_high.draw(mctx)
            else:
                if self._lbl_min is not None:
                    self._lbl_min._position.set(rx + rw + 4, ty + th)
                    self._lbl_min.pivot = Pivot.LEFT
                    self._lbl_min.draw(mctx)
                if self._lbl_max is not None:
                    self._lbl_max._position.set(rx + rw + 4, ty)
                    self._lbl_max.pivot = Pivot.LEFT
                    self._lbl_max.draw(mctx)
                if self._lbl_low is not None:
                    self._lbl_low._position.set(rx - 4, lo_pos[1])
                    self._lbl_low.pivot = Pivot.RIGHT
                    self._lbl_low.draw(mctx)
                if self._lbl_high is not None:
                    self._lbl_high._position.set(rx - 4, hi_pos[1])
                    self._lbl_high.pivot = Pivot.RIGHT
                    self._lbl_high.draw(mctx)

    # ---------------------------------------------------------------------------
    # Event hooks
    # ---------------------------------------------------------------------------

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False

    def on_mouse_press(self, mx: float, my: float) -> None:
        if not self.enabled:
            return
        # Pick the closest handle to the click position
        lo_pos   = self._thumb_pos(self._to_frac(self._low))
        hi_pos   = self._thumb_pos(self._to_frac(self._high))
        is_horiz = self.orientation == 'horizontal'
        coord    = mx if is_horiz else my
        lo_c     = lo_pos[0] if is_horiz else lo_pos[1]
        hi_c     = hi_pos[0] if is_horiz else hi_pos[1]
        self._drag_handle = 1 if abs(coord - lo_c) <= abs(coord - hi_c) else 2
        self._apply_mouse_pos(mx, my)

    def on_mouse_drag(self, mx: float, my: float, dx: float, dy: float) -> None:
        if self._drag_handle == 0 or not self.enabled:
            return
        kb   = getattr(self._manager, '_keyboard', None) if self._manager else None
        snap = False
        if kb is not None:
            from ..input import Keys
            snap = kb.get_key(Keys.LEFT_CONTROL) or kb.get_key(Keys.RIGHT_CONTROL)
        self._apply_mouse_pos(mx, my, snap_to_step=snap)

    def on_mouse_release(self, mx: float, my: float) -> None:
        self._drag_handle = 0

    def on_key_press(self, key: int) -> None:
        import glfw
        if not self.enabled:
            return
        key_step = self.step if self.step is not None else (self.end - self.start) / 100.0
        is_horiz = self.orientation == 'horizontal'
        # Arrow keys: Right/Up move high handle; Left/Down move low handle
        if is_horiz:
            if key == glfw.KEY_RIGHT:
                self.high_value = self._high + key_step
            elif key == glfw.KEY_LEFT:
                self.low_value = self._low - key_step
        else:
            if key == glfw.KEY_UP:
                self.high_value = self._high + key_step
            elif key == glfw.KEY_DOWN:
                self.low_value = self._low - key_step

    # ---------------------------------------------------------------------------
    # Internal drag math
    # ---------------------------------------------------------------------------

    def _apply_mouse_pos(self, mx: float, my: float, snap_to_step: bool = False) -> None:
        rx, ry, rw, rh = self.get_screen_rect()
        is_horiz = self.orientation == 'horizontal'
        pad  = (rh if is_horiz else rw) * 0.5

        if is_horiz:
            usable = rw - 2 * pad
            frac   = (mx - rx - pad) / usable if usable > 0 else 0.0
        else:
            usable = rh - 2 * pad
            frac   = (my - ry - pad) / usable if usable > 0 else 0.0

        frac = _clamp(frac, 0.0, 1.0)
        v    = self.start + frac * (self.end - self.start)
        if self.step is not None:
            v = _snap(v, self.step, self.start)

        if self._drag_handle == 1:
            v = _clamp(v, self.start, self._high)
            if v != self._low:
                self._low      = v
                self._low_frac = self._to_frac(v)
                if self._on_change:
                    self._on_change(self._low, self._high)
        elif self._drag_handle == 2:
            v = _clamp(v, self._low, self.end)
            if v != self._high:
                self._high      = v
                self._high_frac = self._to_frac(v)
                if self._on_change:
                    self._on_change(self._low, self._high)

    # ---------------------------------------------------------------------------
    # Debug info
    # ---------------------------------------------------------------------------

    def _debug_info(self) -> list[tuple[str, str]]:
        def _fmt(v: float) -> str:
            return str(int(v)) if (self.step is not None and self.step >= 1) else f"{v:.2f}"
        rows = super()._debug_info()
        rows += [
            ("low",    _fmt(self._low)),
            ("high",   _fmt(self._high)),
            ("range",  f"{_fmt(self.start)} -> {_fmt(self.end)}"),
            ("step",   str(self.step) if self.step is not None else "continuous"),
            ("orient", self.orientation),
            ("drag",   str(self._drag_handle)),
        ]
        return rows

    # ---------------------------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------------------------

    def release(self) -> None:
        for lbl in (self._lbl_min, self._lbl_max, self._lbl_low, self._lbl_high):
            if lbl is not None:
                lbl.release()
        self._lbl_min = self._lbl_max = self._lbl_low = self._lbl_high = None
        super().release()
