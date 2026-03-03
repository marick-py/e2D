"""
Button — clickable button with animated visual state transitions.

Usage::

    # direct construction
    btn = Button("Start Game", on_click=start_game, position=V2(100, 200))
    env.ui.add(btn)

    # factory shortcut
    btn = env.ui.button("Start Game", on_click=start_game, position=V2(100, 200))

    # custom style
    btn = Button(
        "Custom",
        on_click=handler,
        color_normal=Color(0.2, 0.2, 0.5),
        corner_radius=12.0,
    )
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


class Button(UIElement):
    """Clickable button with configurable text and animated state colours.

    Beyond the standard :class:`UIElement` keyword arguments the constructor accepts:

    * ``text``           — label string (default ``"Button"``)
    * ``on_click``       — ``callable()`` invoked on activation (click or Space/Enter)
    * ``text_style``     — :class:`TextStyle` override; defaults are taken from the active theme
    * ``color_normal``   — :class:`Color` for the idle state background
    * ``color_hover``    — background when the cursor is over the button
    * ``color_pressed``  — background while held down
    * ``color_disabled`` — background when ``enabled=False``
    * ``color_focused``  — background when focused via Tab
    * ``border_color``   — stroke colour drawn around the button
    * ``border_width``   — stroke width in pixels (``None`` → theme default)
    * ``corner_radius``  — rounded-corner radius in pixels (``None`` → theme default)
    * ``animated``       — enable smooth colour transitions (default: ``True``)
    """

    def __init__(
        self,
        text: str = "Button",
        on_click: Callable[[], None] | None = None,
        *,
        text_style:     TextStyle | None = None,
        color_normal:   Color | None = None,
        color_hover:    Color | None = None,
        color_pressed:  Color | None = None,
        color_disabled: Color | None = None,
        color_focused:  Color | None = None,
        border_color:   Color | None = None,
        border_width:   float | None = None,
        corner_radius:  float | None = None,
        animated: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._focusable = True

        self._text: str = text
        self._on_click: Callable[[], None] | None = on_click
        self.animated: bool = animated

        # Style overrides (resolved against theme in _build)
        self._ov_text_style     = text_style
        self._ov_color_normal   = color_normal
        self._ov_color_hover    = color_hover
        self._ov_color_pressed  = color_pressed
        self._ov_color_disabled = color_disabled
        self._ov_color_focused  = color_focused
        self._ov_border_color   = border_color
        self._ov_border_width   = border_width
        self._ov_corner_radius  = corner_radius

        # Resolved colours (overwritten in _build when theme is available)
        self._c_normal   = Color(0.18, 0.18, 0.18)
        self._c_hover    = Color(0.26, 0.26, 0.26)
        self._c_pressed  = Color(0.12, 0.12, 0.12)
        self._c_disabled = Color(0.10, 0.10, 0.10, 0.6)
        self._c_focused  = Color(0.18, 0.18, 0.30)
        self._border_c   = Color(0.35, 0.35, 0.35)
        self._border_w   = 1.0
        self._corner_r   = 6.0

        # Current displayed colour (lerped toward target each frame)
        self._cur_color: Color = self._c_normal

        # Interaction flags
        self._is_hovered: bool = False
        self._is_pressed: bool = False

        # Internal text label — created in _build
        self._label: Optional[Label] = None

    # ---------------------------------------------------------------------------
    # Build (called once after UIManager.add())
    # ---------------------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:  # type: ignore[override]
        theme = self._manager.theme if self._manager else None

        def _ov(override, default):
            return override if override is not None else default

        if theme:
            self._c_normal   = _ov(self._ov_color_normal,   theme.bg_normal)
            self._c_hover    = _ov(self._ov_color_hover,    theme.bg_hover)
            self._c_pressed  = _ov(self._ov_color_pressed,  theme.bg_pressed)
            self._c_disabled = _ov(self._ov_color_disabled, theme.bg_disabled)
            self._c_focused  = _ov(self._ov_color_focused,  theme.bg_focused)
            self._border_c   = _ov(self._ov_border_color,   theme.border_color)
            self._border_w   = _ov(self._ov_border_width,   theme.border_width)
            self._corner_r   = _ov(self._ov_corner_radius,  theme.corner_radius)
            txt_style = self._ov_text_style or TextStyle(
                font=theme.font,
                font_size=theme.font_size,
                color=theme.text_color,
            )
        else:
            self._border_w = _ov(self._ov_border_width, 1.0)
            self._corner_r = _ov(self._ov_corner_radius, 6.0)
            txt_style = self._ov_text_style or DEFAULT_16_TEXT_STYLE

        self._cur_color = self._c_normal

        # Default size if caller didn't supply one
        if self._size.x == 0 or self._size.y == 0:
            self._size.set(120.0, 36.0)

        # Create internal label — pivot=CENTER keeps it centred in the button
        self._label = Label(self._text, default_style=txt_style, pivot=Pivot.CENTER)
        self._label._build(ctx, text_renderer)
        self._dirty = False

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _target_color(self) -> Color:
        if not self.enabled:
            return self._c_disabled
        if self._is_pressed:
            return self._c_pressed
        if self._focused:
            return self._c_focused
        if self._is_hovered:
            return self._c_hover
        return self._c_normal

    # ---------------------------------------------------------------------------
    # Per-frame
    # ---------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        target = self._target_color()
        if self.animated and self._manager:
            t = min(1.0, self._manager.theme.animation_speed * dt)
            self._cur_color = self._cur_color.lerp(target, t)
        else:
            self._cur_color = target

        # Keep label centred inside button bounds
        if self._label is not None:
            rx, ry, rw, rh = self.get_screen_rect()
            self._label._position.set(rx + rw * 0.5, ry + rh * 0.5)
            self._label.opacity = self.opacity

        super().update(dt)

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return

        sr = self._manager.shape_renderer
        rx, ry, rw, rh = self.get_screen_rect()
        alpha = self.opacity
        c  = self._cur_color
        bc = self._border_c

        sr.draw_rect(
            V2(rx, ry), V2(rw, rh),
            color=(c.r, c.g, c.b, c.a * alpha),
            corner_radius=self._corner_r,
            border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
            border_width=self._border_w,
        )

        if self._label is not None:
            self._label.draw(ctx or self._manager.ctx)

    # ---------------------------------------------------------------------------
    # Text property
    # ---------------------------------------------------------------------------

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        if self._label is not None:
            self._label.set_plain_text(value)

    # ---------------------------------------------------------------------------
    # Event hooks (called by UIManager)
    # ---------------------------------------------------------------------------

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False
        self._is_pressed = False   # cancel visual press if cursor leaves while held

    def on_mouse_press(self, mx: float, my: float) -> None:
        if self.enabled:
            self._is_pressed = True

    def on_mouse_release(self, mx: float, my: float) -> None:
        was_pressed = self._is_pressed
        self._is_pressed = False
        if was_pressed and self.enabled and self.contains_point(mx, my) and self._on_click:
            self._on_click()

    def on_key_press(self, key: int) -> None:
        import glfw
        if key in (glfw.KEY_SPACE, glfw.KEY_ENTER, glfw.KEY_KP_ENTER):
            if self.enabled and self._on_click:
                self._on_click()

    # ---------------------------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------------------------

    def release(self) -> None:
        if self._label is not None:
            self._label.release()
            self._label = None
        super().release()
