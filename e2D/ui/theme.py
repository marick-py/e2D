"""
UITheme — centralised style defaults for every UI element.

Built-in themes (importable from e2D.ui.theme):

    MONOKAI_THEME     — dark olive-charcoal, neon orange/green/cyan accents,
                        semi-transparent surfaces.  **Default.**
    DARK_THEME        — neutral near-black, purple/teal accents (Material-ish).
    LIGHT_THEME       — near-white surface, dark text, same accent set.
    SOLARIZED_DARK    — Solarized dark palette (Ethan Schoonover).
    SOLARIZED_LIGHT   — Solarized light palette.
    NORD_THEME        — Arctic/Nordic blue-grey palette.
    DRACULA_THEME     — dark purple-slate, pink/purple accents.
    TOKYO_NIGHT_THEME — deep blue-black, soft blue/violet accents.
    HIGH_CONTRAST     — pure black/white with yellow accents; accessibility.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from ..colors import Color


@dataclass
class UITheme:
    """Global theme applied to every UI element that doesn't override a style.

    Instantiate with your own colours/fonts and pass to
    :class:`UIManager`::

        from e2D.ui.theme import MONOKAI_THEME
        env.ui.theme = MONOKAI_THEME

    Or build a custom one::

        my_theme = UITheme(
            primary=Color.from_hex('#FF5722'),
            bg_normal=Color(0.10, 0.10, 0.12, 0.88),
        )
        env.ui.theme = my_theme
    """

    # -- accent colours ------------------------------------------------------
    primary:   Color = field(default_factory=lambda: Color(0.992, 0.592, 0.122, 1.0))   # Monokai orange
    secondary: Color = field(default_factory=lambda: Color(0.400, 0.851, 0.933, 1.0))   # Monokai cyan
    accent:    Color = field(default_factory=lambda: Color(0.651, 0.894, 0.180, 1.0))   # Monokai green

    # -- backgrounds ---------------------------------------------------------
    # bg_window  : clear colour behind everything (use as root.clear_color)
    # bg_normal  : idle widget surface
    # bg_hover   : widget surface when cursor is over it
    # bg_pressed : widget surface while held
    # bg_focused : widget surface when keyboard-focused
    # bg_disabled: widget surface when disabled
    bg_window:   Color = field(default_factory=lambda: Color(0.152, 0.157, 0.129, 1.0))   # #272822
    bg_normal:   Color = field(default_factory=lambda: Color(0.196, 0.204, 0.169, 0.90))  # slightly lighter, semi
    bg_hover:    Color = field(default_factory=lambda: Color(0.231, 0.243, 0.196, 0.92))
    bg_pressed:  Color = field(default_factory=lambda: Color(0.992, 0.592, 0.122, 0.20))  # orange tint press
    bg_focused:  Color = field(default_factory=lambda: Color(0.400, 0.851, 0.933, 0.14))  # cyan tint focus
    bg_disabled: Color = field(default_factory=lambda: Color(0.180, 0.184, 0.157, 0.55))

    # -- text ----------------------------------------------------------------
    text_color:             Color = field(default_factory=lambda: Color(0.973, 0.973, 0.949, 1.0))   # #F8F8F2
    text_color_disabled:    Color = field(default_factory=lambda: Color(0.475, 0.475, 0.427, 1.0))
    text_color_placeholder: Color = field(default_factory=lambda: Color(0.475, 0.475, 0.427, 0.80))

    # -- fonts ---------------------------------------------------------------
    font:      str = "arial.ttf"
    font_mono: str = "consola.ttf"
    font_size: int = 16

    # -- borders / corners ---------------------------------------------------
    border_color:  Color = field(default_factory=lambda: Color(0.992, 0.592, 0.122, 0.55))  # neon-orange border
    border_width:  float = 1.0
    border_color_focused: Color = field(default_factory=lambda: Color(0.400, 0.851, 0.933, 0.90))  # bright cyan on focus
    border_width_focused: float = 2.0
    corner_radius: float = 5.0

    # -- spacing defaults ----------------------------------------------------
    element_spacing: float = 8.0
    default_padding: float = 8.0
    default_margin:  float = 4.0

    # -- animations ----------------------------------------------------------
    animate_hover:   bool  = True
    animate_focus:   bool  = True
    animation_speed: float = 9.0

    # -- scrollbars -------------------------------------------------------------
    scrollbar_color: Color = field(default_factory=lambda: Color(0.20, 0.20, 0.25, 0.60))
    scrollbar_thumb: Color = field(default_factory=lambda: Color(0.50, 0.50, 0.60, 0.85))

    # -- plots / streams -----------------------------------------------------
    # Background colour / gradient behind plot frames and UIStream widgets.
    # Set plot_bg_gradient to a LinearGradient / RadialGradient to override
    # the flat plot_bg_color.
    plot_bg_color:    Color = field(default_factory=lambda: Color(0.04, 0.05, 0.04, 0.96))
    plot_bg_gradient: object = None   # LinearGradient | RadialGradient | None
    plot_grid_color:  Color = field(default_factory=lambda: Color(0.20, 0.22, 0.18, 0.70))
    plot_axis_color:  Color = field(default_factory=lambda: Color(0.55, 0.58, 0.45, 0.90))
    plot_line_color:  Color = field(default_factory=lambda: Color(0.15, 0.95, 0.50, 1.0))   # Monokai green
    plot_line_width:  float = 1.5
    plot_border_color:Color = field(default_factory=lambda: Color(0.10, 0.42, 0.18, 0.55))
    plot_border_width:float = 1.0

    # -- misc ----------------------------------------------------------------
    cursor_blink_rate: float = 0.53
    scroll_speed:      float = 40.0

    def copy(self) -> 'UITheme':
        return UITheme(
            primary=self.primary.copy(),
            secondary=self.secondary.copy(),
            accent=self.accent.copy(),
            bg_window=self.bg_window.copy(),
            bg_normal=self.bg_normal.copy(),
            bg_hover=self.bg_hover.copy(),
            bg_pressed=self.bg_pressed.copy(),
            bg_focused=self.bg_focused.copy(),
            bg_disabled=self.bg_disabled.copy(),
            text_color=self.text_color.copy(),
            text_color_disabled=self.text_color_disabled.copy(),
            text_color_placeholder=self.text_color_placeholder.copy(),
            font=self.font,
            font_mono=self.font_mono,
            font_size=self.font_size,
            border_color=self.border_color.copy(),
            border_width=self.border_width,
            border_color_focused=self.border_color_focused.copy(),
            border_width_focused=self.border_width_focused,
            corner_radius=self.corner_radius,
            element_spacing=self.element_spacing,
            default_padding=self.default_padding,
            default_margin=self.default_margin,
            animate_hover=self.animate_hover,
            animate_focus=self.animate_focus,
            animation_speed=self.animation_speed,
            scrollbar_color=self.scrollbar_color.copy(),
            scrollbar_thumb=self.scrollbar_thumb.copy(),
            cursor_blink_rate=self.cursor_blink_rate,
            scroll_speed=self.scroll_speed,
            plot_bg_color=self.plot_bg_color.copy(),
            plot_bg_gradient=self.plot_bg_gradient,
            plot_grid_color=self.plot_grid_color.copy(),
            plot_axis_color=self.plot_axis_color.copy(),
            plot_line_color=self.plot_line_color.copy(),
            plot_line_width=self.plot_line_width,
            plot_border_color=self.plot_border_color.copy(),
            plot_border_width=self.plot_border_width,
        )

# ---------------------------------------------------------------------------
# MONOKAI  (default — dark olive-charcoal, neon accents, semi-transparent)
# ---------------------------------------------------------------------------
MONOKAI_THEME = UITheme()   # all defaults above are already Monokai


# ---------------------------------------------------------------------------
# DARK  (neutral Material-style dark)
# ---------------------------------------------------------------------------
DARK_THEME = UITheme(
    primary   = Color(0.384, 0.000, 0.933, 1.0),   # #6200EE
    secondary = Color(0.012, 0.831, 0.741, 1.0),   # #03DAC6
    accent    = Color(0.733, 0.337, 1.000, 1.0),   # #BB86FC
    bg_window   = Color(0.050, 0.050, 0.070, 1.0),
    bg_normal   = Color(0.118, 0.118, 0.118, 1.0),
    bg_hover    = Color(0.180, 0.180, 0.180, 1.0),
    bg_pressed  = Color(0.220, 0.220, 0.220, 1.0),
    bg_focused  = Color(0.160, 0.160, 0.200, 1.0),
    bg_disabled = Color(0.100, 0.100, 0.100, 0.60),
    text_color             = Color(1.00, 1.00, 1.00, 1.0),
    text_color_disabled    = Color(0.50, 0.50, 0.50, 1.0),
    text_color_placeholder = Color(0.45, 0.45, 0.45, 1.0),
    border_color  = Color(0.30, 0.30, 0.30, 1.0),
    border_width  = 1.0,
    border_color_focused = Color(0.733, 0.337, 1.000, 0.90),
    border_width_focused = 2.0,
    corner_radius = 6.0,
    animation_speed = 8.0,
)


# ---------------------------------------------------------------------------
# LIGHT  (near-white surface, dark text)
# ---------------------------------------------------------------------------
LIGHT_THEME = UITheme(
    primary   = Color(0.384, 0.000, 0.933, 1.0),
    secondary = Color(0.012, 0.831, 0.741, 1.0),
    accent    = Color(0.733, 0.337, 1.000, 1.0),
    bg_window   = Color(0.930, 0.930, 0.950, 1.0),
    bg_normal   = Color(0.960, 0.960, 0.960, 1.0),
    bg_hover    = Color(0.920, 0.920, 0.920, 1.0),
    bg_pressed  = Color(0.880, 0.880, 0.880, 1.0),
    bg_focused  = Color(0.930, 0.930, 0.970, 1.0),
    bg_disabled = Color(0.900, 0.900, 0.900, 0.60),
    text_color             = Color(0.050, 0.050, 0.050, 1.0),
    text_color_disabled    = Color(0.550, 0.550, 0.550, 1.0),
    text_color_placeholder = Color(0.600, 0.600, 0.600, 1.0),
    border_color  = Color(0.750, 0.750, 0.750, 1.0),
    border_width  = 1.0,
    border_color_focused = Color(0.384, 0.000, 0.933, 0.85),
    border_width_focused = 2.0,
    corner_radius = 6.0,
    animation_speed = 8.0,
)


# ---------------------------------------------------------------------------
# SOLARIZED DARK  (Ethan Schoonover — https://ethanschoonover.com/solarized/)
# ---------------------------------------------------------------------------
# TODO THIS LOOKS LIKE SHIT IN #example_widgets.py

SOLARIZED_DARK = UITheme(
    primary   = Color(0.149, 0.545, 0.824, 1.0),   # blue   #268BD2
    secondary = Color(0.165, 0.631, 0.596, 1.0),   # cyan   #2AA198
    accent    = Color(0.847, 0.506, 0.024, 1.0),   # orange #D97A06
    bg_window   = Color(0.000, 0.169, 0.212, 1.0), # base03 #002B36
    bg_normal   = Color(0.027, 0.212, 0.259, 1.0), # base02 #073642
    bg_hover    = Color(0.059, 0.255, 0.306, 0.95),
    bg_pressed  = Color(0.149, 0.545, 0.824, 0.20),
    bg_focused  = Color(0.165, 0.631, 0.596, 0.18),
    bg_disabled = Color(0.027, 0.212, 0.259, 0.55),
    text_color             = Color(0.514, 0.580, 0.588, 1.0),  # base0  #839496
    text_color_disabled    = Color(0.345, 0.431, 0.459, 1.0),  # base01
    text_color_placeholder = Color(0.345, 0.431, 0.459, 0.80),
    border_color  = Color(0.059, 0.255, 0.306, 1.0),
    border_width  = 1.0,
    border_color_focused = Color(0.149, 0.545, 0.824, 0.90),
    border_width_focused = 2.0,
    corner_radius = 4.0,
    animation_speed = 7.0,
)


# ---------------------------------------------------------------------------
# SOLARIZED LIGHT
# ---------------------------------------------------------------------------
# TODO THIS LOOKS LIKE SHIT IN #example_widgets.py

SOLARIZED_LIGHT = UITheme(
    primary   = Color(0.149, 0.545, 0.824, 1.0),
    secondary = Color(0.165, 0.631, 0.596, 1.0),
    accent    = Color(0.847, 0.506, 0.024, 1.0),
    bg_window   = Color(0.992, 0.965, 0.890, 1.0),  # base3  #FDF6E3
    bg_normal   = Color(0.933, 0.910, 0.835, 1.0),  # base2  #EEE8D5
    bg_hover    = Color(0.894, 0.871, 0.796, 1.0),
    bg_pressed  = Color(0.149, 0.545, 0.824, 0.18),
    bg_focused  = Color(0.165, 0.631, 0.596, 0.16),
    bg_disabled = Color(0.933, 0.910, 0.835, 0.60),
    text_color             = Color(0.396, 0.482, 0.514, 1.0),  # base00 #657B83
    text_color_disabled    = Color(0.576, 0.631, 0.631, 1.0),
    text_color_placeholder = Color(0.576, 0.631, 0.631, 0.80),
    border_color  = Color(0.827, 0.800, 0.722, 1.0),
    border_width  = 1.0,
    border_color_focused = Color(0.149, 0.545, 0.824, 0.85),
    border_width_focused = 2.0,
    corner_radius = 4.0,
    animation_speed = 7.0,
)


# ---------------------------------------------------------------------------
# NORD  (Arctic Studio — https://www.nordtheme.com/)
# ---------------------------------------------------------------------------
NORD_THEME = UITheme(
    primary   = Color(0.533, 0.753, 0.816, 1.0),   # nord8  #88C0D0
    secondary = Color(0.506, 0.631, 0.757, 1.0),   # nord9  #81A1C1
    accent    = Color(0.361, 0.506, 0.675, 1.0),   # nord10 #5E81AC
    bg_window   = Color(0.180, 0.204, 0.251, 1.0), # nord0  #2E3440
    bg_normal   = Color(0.231, 0.259, 0.322, 1.0), # nord1  #3B4252
    bg_hover    = Color(0.263, 0.298, 0.369, 0.95),# nord2  #434C5E
    bg_pressed  = Color(0.533, 0.753, 0.816, 0.22),
    bg_focused  = Color(0.506, 0.631, 0.757, 0.20),
    bg_disabled = Color(0.231, 0.259, 0.322, 0.55),
    text_color             = Color(0.925, 0.937, 0.953, 1.0),  # nord6  #ECEFF4
    text_color_disabled    = Color(0.561, 0.616, 0.698, 1.0),  # nord4
    text_color_placeholder = Color(0.561, 0.616, 0.698, 0.75),
    border_color  = Color(0.298, 0.337, 0.416, 1.0),           # nord3
    border_width  = 1.0,
    border_color_focused = Color(0.533, 0.753, 0.816, 0.90),
    border_width_focused = 2.0,
    corner_radius = 6.0,
    animation_speed = 8.0,
)


# ---------------------------------------------------------------------------
# DRACULA  (Zeno Rocha — https://draculatheme.com/)
# ---------------------------------------------------------------------------
DRACULA_THEME = UITheme(
    primary   = Color(1.000, 0.475, 0.776, 1.0),   # pink   #FF79C6
    secondary = Color(0.741, 0.576, 0.976, 1.0),   # purple #BD93F9
    accent    = Color(0.314, 0.980, 0.482, 1.0),   # green  #50FA7B
    bg_window   = Color(0.157, 0.165, 0.212, 1.0), # #282A36
    bg_normal   = Color(0.267, 0.278, 0.353, 0.92),# #44475A semi
    bg_hover    = Color(0.310, 0.322, 0.408, 0.94),
    bg_pressed  = Color(1.000, 0.475, 0.776, 0.20),
    bg_focused  = Color(0.741, 0.576, 0.976, 0.18),
    bg_disabled = Color(0.267, 0.278, 0.353, 0.50),
    text_color             = Color(0.973, 0.973, 0.949, 1.0),  # #F8F8F2
    text_color_disabled    = Color(0.424, 0.443, 0.553, 1.0),  # comment grey
    text_color_placeholder = Color(0.424, 0.443, 0.553, 0.85),
    border_color  = Color(1.000, 0.475, 0.776, 0.45),          # pink border
    border_width  = 1.0,
    border_color_focused = Color(0.741, 0.576, 0.976, 0.90),
    border_width_focused = 2.0,
    corner_radius = 7.0,
    animation_speed = 9.0,
)


# ---------------------------------------------------------------------------
# TOKYO NIGHT  (enkia — https://github.com/enkia/tokyo-night-vscode-theme)
# ---------------------------------------------------------------------------
TOKYO_NIGHT_THEME = UITheme(
    primary   = Color(0.478, 0.635, 0.969, 1.0),   # #7AA2F7
    secondary = Color(0.733, 0.604, 0.969, 1.0),   # #BB9AF7
    accent    = Color(0.122, 0.859, 0.698, 1.0),   # #1FDB97 (aqua)
    bg_window   = Color(0.102, 0.106, 0.149, 1.0), # #1A1B26
    bg_normal   = Color(0.141, 0.157, 0.231, 0.90),# #24283B semi
    bg_hover    = Color(0.169, 0.188, 0.278, 0.93),
    bg_pressed  = Color(0.478, 0.635, 0.969, 0.18),
    bg_focused  = Color(0.733, 0.604, 0.969, 0.16),
    bg_disabled = Color(0.141, 0.157, 0.231, 0.50),
    text_color             = Color(0.753, 0.792, 0.961, 1.0),  # #C0CAF5
    text_color_disabled    = Color(0.341, 0.382, 0.553, 1.0),
    text_color_placeholder = Color(0.341, 0.382, 0.553, 0.80),
    border_color  = Color(0.169, 0.188, 0.278, 1.0),
    border_width  = 1.0,
    border_color_focused = Color(0.478, 0.635, 0.969, 0.90),
    border_width_focused = 2.0,
    corner_radius = 8.0,
    animation_speed = 9.0,
)


# ---------------------------------------------------------------------------
# HIGH CONTRAST  (accessibility — pure black/white, yellow accents)
# ---------------------------------------------------------------------------
HIGH_CONTRAST = UITheme(
    primary   = Color(1.000, 1.000, 0.000, 1.0),   # pure yellow
    secondary = Color(0.000, 1.000, 1.000, 1.0),   # pure cyan
    accent    = Color(1.000, 0.600, 0.000, 1.0),   # orange
    bg_window   = Color(0.000, 0.000, 0.000, 1.0),
    bg_normal   = Color(0.000, 0.000, 0.000, 1.0),
    bg_hover    = Color(0.200, 0.200, 0.200, 1.0),
    bg_pressed  = Color(1.000, 1.000, 0.000, 0.25),
    bg_focused  = Color(0.000, 1.000, 1.000, 0.20),
    bg_disabled = Color(0.120, 0.120, 0.120, 1.0),
    text_color             = Color(1.000, 1.000, 1.000, 1.0),
    text_color_disabled    = Color(0.600, 0.600, 0.600, 1.0),
    text_color_placeholder = Color(0.600, 0.600, 0.600, 1.0),
    border_color  = Color(1.000, 1.000, 1.000, 1.0),
    border_width  = 2.0,
    border_color_focused = Color(1.000, 1.000, 0.000, 1.0),
    border_width_focused = 3.0,
    corner_radius = 0.0,   # sharp corners for maximum clarity
    animation_speed = 99.0,  # instant — no lerp delay
)

