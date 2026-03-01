"""
UITheme — centralised style defaults for every UI element.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from ..colors import Color


@dataclass
class UITheme:
    """Global theme applied to every UI element that doesn't override a style.

    Instantiate with your own colours/fonts and pass to
    :class:`UIManager`::

        dark = UITheme(
            primary=Color.from_hex('#6200EE'),
            bg_normal=Color(0.12, 0.12, 0.12, 1.0),
        )
        env.ui.theme = dark
    """

    # -- accent colours ------------------------------------------------------
    primary:   Color = field(default_factory=lambda: Color(0.384, 0.000, 0.933, 1.0))   # #6200EE
    secondary: Color = field(default_factory=lambda: Color(0.012, 0.831, 0.741, 1.0))   # #03DAC6
    accent:    Color = field(default_factory=lambda: Color(0.733, 0.337, 1.000, 1.0))   # #BB86FC

    # -- backgrounds ---------------------------------------------------------
    bg_normal:   Color = field(default_factory=lambda: Color(0.118, 0.118, 0.118, 1.0))   # dark surface
    bg_hover:    Color = field(default_factory=lambda: Color(0.180, 0.180, 0.180, 1.0))
    bg_pressed:  Color = field(default_factory=lambda: Color(0.220, 0.220, 0.220, 1.0))
    bg_focused:  Color = field(default_factory=lambda: Color(0.160, 0.160, 0.200, 1.0))
    bg_disabled: Color = field(default_factory=lambda: Color(0.100, 0.100, 0.100, 0.6))

    # -- text ----------------------------------------------------------------
    text_color:          Color = field(default_factory=lambda: Color(1.0, 1.0, 1.0, 1.0))
    text_color_disabled: Color = field(default_factory=lambda: Color(0.5, 0.5, 0.5, 1.0))
    text_color_placeholder: Color = field(default_factory=lambda: Color(0.45, 0.45, 0.45, 1.0))

    # -- fonts ---------------------------------------------------------------
    font:      str = "arial.ttf"
    font_mono: str = "consola.ttf"
    font_size: int = 16

    # -- borders / corners ---------------------------------------------------
    border_color:    Color = field(default_factory=lambda: Color(0.3, 0.3, 0.3, 1.0))
    border_width:    float = 1.0
    corner_radius:   float = 6.0

    # -- spacing defaults ----------------------------------------------------
    element_spacing: float = 8.0    # default gap between siblings in containers
    default_padding: float = 8.0
    default_margin:  float = 4.0

    # -- animations (Phase 2+) -----------------------------------------------
    animate_hover:   bool = True
    animate_focus:   bool = True
    animation_speed: float = 8.0    # lerp speed per second

    # -- misc ----------------------------------------------------------------
    cursor_blink_rate: float = 0.53   # seconds per blink half-cycle
    scroll_speed:      float = 40.0   # pixels per scroll tick


# Convenience pre-built themes
DARK_THEME  = UITheme()

LIGHT_THEME = UITheme(
    primary   = Color(0.384, 0.000, 0.933, 1.0),
    secondary = Color(0.012, 0.831, 0.741, 1.0),
    accent    = Color(0.733, 0.337, 1.000, 1.0),
    bg_normal   = Color(0.96, 0.96, 0.96, 1.0),
    bg_hover    = Color(0.92, 0.92, 0.92, 1.0),
    bg_pressed  = Color(0.88, 0.88, 0.88, 1.0),
    bg_focused  = Color(0.93, 0.93, 0.97, 1.0),
    bg_disabled = Color(0.90, 0.90, 0.90, 0.6),
    text_color          = Color(0.0, 0.0, 0.0, 1.0),
    text_color_disabled = Color(0.55, 0.55, 0.55, 1.0),
    text_color_placeholder = Color(0.60, 0.60, 0.60, 1.0),
    border_color = Color(0.75, 0.75, 0.75, 1.0),
)
