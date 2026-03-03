"""
Switch and Checkbox — boolean toggle controls.

Switch is an iOS-style sliding pill toggle.
Checkbox is a square with an animated checkmark.

Usage::

    sw  = env.ui.switch(value=True,  on_change=lambda v: print("switch:", v))
    cb  = env.ui.checkbox(value=False, on_change=lambda v: print("checked:", v))

    # manual construction + themed colours
    sw = Switch(
        value=True,
        color_on=Color(0.2, 0.8, 0.4),
        position=V2(200, 100),
    )
    env.ui.add(sw)
"""

from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from .base import UIElement
from ..colors import Color
from ..vectors import V2

if TYPE_CHECKING:
    from .._types import ContextType
    from ..text import TextRenderer


# ---------------------------------------------------------------------------
# Switch — pill-shaped sliding toggle
# ---------------------------------------------------------------------------

class Switch(UIElement):
    """iOS/Android-style pill toggle.

    Constructor keyword arguments beyond the standard :class:`UIElement` ones:

    * ``value``          — initial boolean state (default ``False``)
    * ``on_change``      — ``callable(bool)`` called when the value changes
    * ``color_on``       — track colour when value is ``True``
    * ``color_off``      — track colour when value is ``False``
    * ``color_disabled`` — track colour when ``enabled=False``
    * ``color_thumb``    — thumb (knob) colour
    * ``border_color``   — track border colour
    * ``border_width``   — track border width in pixels
    * ``animated``       — smooth thumb slide (default: ``True``)
    """

    def __init__(
        self,
        value: bool = False,
        on_change: Callable[[bool], None] | None = None,
        *,
        color_on:       Color | None = None,
        color_off:      Color | None = None,
        color_disabled: Color | None = None,
        color_thumb:    Color | None = None,
        border_color:   Color | None = None,
        border_width:   float | None = None,
        animated: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._focusable = True

        self._value: bool = bool(value)
        self._on_change: Callable[[bool], None] | None = on_change
        self.animated: bool = animated

        # Style overrides
        self._ov_color_on       = color_on
        self._ov_color_off      = color_off
        self._ov_color_disabled = color_disabled
        self._ov_color_thumb    = color_thumb
        self._ov_border_color   = border_color
        self._ov_border_width   = border_width

        # Resolved colours (overwritten in _build)
        self._c_on       = Color(0.2,  0.72, 0.32)   # green
        self._c_off      = Color(0.25, 0.25, 0.25)
        self._c_disabled = Color(0.15, 0.15, 0.15, 0.6)
        self._c_thumb    = Color(1.0,  1.0,  1.0)
        self._border_c   = Color(0.3,  0.3,  0.3)
        self._border_w   = 1.0

        # Animated state: thumb position fraction 0.0 = left, 1.0 = right
        self._thumb_t: float = 1.0 if value else 0.0
        # Animated track colour
        self._cur_track: Color = self._c_on if value else self._c_off

        self._is_hovered: bool = False

    # ---------------------------------------------------------------------------
    # Build
    # ---------------------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:  # type: ignore[override]
        theme = self._manager.theme if self._manager else None

        def _ov(override, default):
            return override if override is not None else default

        if theme:
            self._c_on       = _ov(self._ov_color_on,       theme.secondary)
            self._c_off      = _ov(self._ov_color_off,      theme.bg_normal)
            self._c_disabled = _ov(self._ov_color_disabled, theme.bg_disabled)
            self._border_c   = _ov(self._ov_border_color,   theme.border_color)
            self._border_w   = _ov(self._ov_border_width,   theme.border_width)
        else:
            self._border_w = _ov(self._ov_border_width, 1.0)

        self._c_thumb = _ov(self._ov_color_thumb, Color(1.0, 1.0, 1.0))

        self._thumb_t   = 1.0 if self._value else 0.0
        self._cur_track = self._c_on if self._value else self._c_off

        if self._size.x == 0 or self._size.y == 0:
            self._size.set(52.0, 28.0)

        self._dirty = False

    # ---------------------------------------------------------------------------
    # Value property
    # ---------------------------------------------------------------------------

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, v: bool) -> None:
        v = bool(v)
        if v != self._value:
            self._value = v
            if self._on_change:
                self._on_change(v)

    def toggle(self) -> None:
        """Flip the boolean value."""
        self.value = not self._value

    # ---------------------------------------------------------------------------
    # Per-frame
    # ---------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        target_t = 1.0 if self._value else 0.0
        target_c = (self._c_on if self._value else self._c_off) if self.enabled else self._c_disabled

        if self.animated and self._manager:
            t = min(1.0, self._manager.theme.animation_speed * dt)
            self._thumb_t   = self._thumb_t   + (target_t - self._thumb_t)   * t
            self._cur_track = self._cur_track.lerp(target_c, t)
        else:
            self._thumb_t   = target_t
            self._cur_track = target_c

        super().update(dt)

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return

        sr = self._manager.shape_renderer
        rx, ry, rw, rh = self.get_screen_rect()
        alpha = self.opacity

        tc = self._cur_track
        bc = self._border_c

        # Track (pill-shaped rounded rectangle)
        sr.draw_rect(
            V2(rx, ry), V2(rw, rh),
            color=(tc.r, tc.g, tc.b, tc.a * alpha),
            corner_radius=rh * 0.5,
            border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
            border_width=self._border_w,
        )

        # Thumb (circle)
        pad     = 3.0
        thumb_r = (rh - pad * 2) * 0.5
        travel  = rw - 2 * (pad + thumb_r)
        thumb_x = rx + pad + thumb_r + self._thumb_t * travel
        thumb_y = ry + rh * 0.5

        oc = self._c_thumb
        sr.draw_circle(
            V2(thumb_x, thumb_y), thumb_r,
            color=(oc.r, oc.g, oc.b, oc.a * alpha),
        )

    # ---------------------------------------------------------------------------
    # Event hooks
    # ---------------------------------------------------------------------------

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False

    def on_mouse_press(self, mx: float, my: float) -> None:
        pass  # visual state is driven by value / animated thumb

    def on_mouse_release(self, mx: float, my: float) -> None:
        if self.enabled and self.contains_point(mx, my):
            self.toggle()

    def on_key_press(self, key: int) -> None:
        import glfw
        if key == glfw.KEY_SPACE and self.enabled:
            self.toggle()


# ---------------------------------------------------------------------------
# Checkbox — square with animated checkmark
# ---------------------------------------------------------------------------

class Checkbox(UIElement):
    """Square checkbox that renders a ✓ checkmark when checked.

    Constructor keyword arguments beyond the standard :class:`UIElement` ones:

    * ``value``           — initial boolean state (default ``False``)
    * ``on_change``       — ``callable(bool)`` called when the value changes
    * ``color_bg``        — background colour in unchecked state
    * ``color_checked``   — background colour in checked state (filled accent)
    * ``color_disabled``  — background colour when ``enabled=False``
    * ``checkmark_color`` — colour of the ✓ stroke
    * ``border_color``    — box border colour
    * ``border_width``    — box border width in pixels
    * ``corner_radius``   — rounded corner radius in pixels
    * ``animated``        — smooth checkmark fade-in (default: ``True``)
    """

    def __init__(
        self,
        value: bool = False,
        on_change: Callable[[bool], None] | None = None,
        *,
        color_bg:        Color | None = None,
        color_checked:   Color | None = None,
        color_disabled:  Color | None = None,
        checkmark_color: Color | None = None,
        border_color:    Color | None = None,
        border_width:    float | None = None,
        corner_radius:   float | None = None,
        animated: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._focusable = True

        self._value: bool = bool(value)
        self._on_change: Callable[[bool], None] | None = on_change
        self.animated: bool = animated

        # Style overrides
        self._ov_color_bg        = color_bg
        self._ov_color_checked   = color_checked
        self._ov_color_disabled  = color_disabled
        self._ov_checkmark_color = checkmark_color
        self._ov_border_color    = border_color
        self._ov_border_width    = border_width
        self._ov_corner_radius   = corner_radius

        # Resolved colours
        self._c_bg       = Color(0.15, 0.15, 0.15)
        self._c_checked  = Color(0.384, 0.0, 0.933)   # purple accent
        self._c_disabled = Color(0.10, 0.10, 0.10, 0.6)
        self._c_mark     = Color(1.0, 1.0, 1.0)
        self._border_c   = Color(0.40, 0.40, 0.40)
        self._border_w   = 1.5
        self._corner_r   = 3.0

        # Animation: 0.0 = unchecked, 1.0 = fully checked
        self._check_t: float = 1.0 if value else 0.0
        self._cur_bg: Color  = self._c_checked if value else self._c_bg

        self._is_hovered: bool = False

    # ---------------------------------------------------------------------------
    # Build
    # ---------------------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:  # type: ignore[override]
        theme = self._manager.theme if self._manager else None

        def _ov(override, default):
            return override if override is not None else default

        if theme:
            self._c_bg       = _ov(self._ov_color_bg,       theme.bg_normal)
            self._c_checked  = _ov(self._ov_color_checked,  theme.primary)
            self._c_disabled = _ov(self._ov_color_disabled, theme.bg_disabled)
            self._c_mark     = _ov(self._ov_checkmark_color, Color(1.0, 1.0, 1.0))
            self._border_c   = _ov(self._ov_border_color,   theme.border_color)
            self._border_w   = _ov(self._ov_border_width,   theme.border_width)
            self._corner_r   = _ov(self._ov_corner_radius,  theme.corner_radius * 0.5)
        else:
            self._border_w = _ov(self._ov_border_width, 1.5)
            self._corner_r = _ov(self._ov_corner_radius, 3.0)
            self._c_mark   = _ov(self._ov_checkmark_color, self._c_mark)

        self._check_t = 1.0 if self._value else 0.0
        self._cur_bg  = self._c_checked if self._value else self._c_bg

        if self._size.x == 0 or self._size.y == 0:
            self._size.set(24.0, 24.0)

        self._dirty = False

    # ---------------------------------------------------------------------------
    # Value property
    # ---------------------------------------------------------------------------

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, v: bool) -> None:
        v = bool(v)
        if v != self._value:
            self._value = v
            if self._on_change:
                self._on_change(v)

    def toggle(self) -> None:
        """Flip the boolean value."""
        self.value = not self._value

    # ---------------------------------------------------------------------------
    # Per-frame
    # ---------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        target_t  = 1.0 if self._value else 0.0
        target_bg = (self._c_checked if self._value else self._c_bg) if self.enabled else self._c_disabled

        if self.animated and self._manager:
            t = min(1.0, self._manager.theme.animation_speed * dt)
            self._check_t = self._check_t + (target_t - self._check_t) * t
            self._cur_bg  = self._cur_bg.lerp(target_bg, t)
        else:
            self._check_t = target_t
            self._cur_bg  = target_bg

        super().update(dt)

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return

        sr = self._manager.shape_renderer
        rx, ry, rw, rh = self.get_screen_rect()
        alpha = self.opacity

        bg = self._cur_bg
        bc = self._border_c

        # Box
        sr.draw_rect(
            V2(rx, ry), V2(rw, rh),
            color=(bg.r, bg.g, bg.b, bg.a * alpha),
            corner_radius=self._corner_r,
            border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
            border_width=self._border_w,
        )

        # Checkmark (✓) — two connected line segments, faded by check_t
        if self._check_t > 0.001:
            mc = self._c_mark
            mark_alpha = mc.a * alpha * self._check_t
            mark_c = (mc.r, mc.g, mc.b, mark_alpha)

            pad = rw * 0.22
            # Left stroke: outer-left to mid-bottom
            mid_x  = rx + rw * 0.38
            mid_y  = ry + rh * 0.68
            start1 = (rx + pad,       ry + rh * 0.52)
            end1   = (mid_x,          mid_y)
            # Right stroke: mid-bottom to upper-right
            start2 = end1
            end2   = (rx + rw - pad,  ry + rh * 0.28)

            stroke_w = max(1.5, rw * 0.10)
            sr.draw_line(start1, end1, width=stroke_w, color=mark_c)
            sr.draw_line(start2, end2, width=stroke_w, color=mark_c)

    # ---------------------------------------------------------------------------
    # Event hooks
    # ---------------------------------------------------------------------------

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False

    def on_mouse_press(self, mx: float, my: float) -> None:
        pass

    def on_mouse_release(self, mx: float, my: float) -> None:
        if self.enabled and self.contains_point(mx, my):
            self.toggle()

    def on_key_press(self, key: int) -> None:
        import glfw
        if key == glfw.KEY_SPACE and self.enabled:
            self.toggle()
