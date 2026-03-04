"""
example_widgets.py — Phase 2 UI widgets demo  (updated for Phase 4 containers).

Demonstrates every Phase 2 widget inside a Phase 4 VBox / HBox layout:
  - Button       (click to increment counter; enable/disable all others)
  - Switch       (pill toggle — toggles circle animation on the canvas)
  - Checkbox     (square checkbox — toggles whether score label is shown)
  - Slider       (horizontal, continuous — controls circle radius)
  - Slider       (horizontal, step=5 — controls a score value 0-100)
  - RangeSlider  (horizontal — defines a brightness range [lo, hi])
  - Slider       (vertical — controls number of drawn circles)

Left panel:  widgets laid out inside VBox / HBox containers (Phase 4)
Right panel: live value readout + a simple canvas visualisation

Controls:
  T     — cycle theme
  R     — reset all widgets to defaults
  F3    — toggle debug outlines
  ESC   — quit
"""

import math
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import glfw

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keys, KeyState, TextStyle,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA,
)
from e2D.colors import Color
from e2D.ui import VBox, HBox, SizeMode
from e2D.ui.theme import (
    MONOKAI_THEME, DARK_THEME, LIGHT_THEME,
    SOLARIZED_DARK, SOLARIZED_LIGHT,
    NORD_THEME, DRACULA_THEME,
    TOKYO_NIGHT_THEME, HIGH_CONTRAST,
)
from e2D._pivot import Pivot

_THEMES = [
    ("Monokai",         MONOKAI_THEME),
    ("Dark",            DARK_THEME),
    ("Light",           LIGHT_THEME),
    ("Solarized Dark",  SOLARIZED_DARK),
    ("Solarized Light", SOLARIZED_LIGHT),
    ("Nord",            NORD_THEME),
    ("Dracula",         DRACULA_THEME),
    ("Tokyo Night",     TOKYO_NIGHT_THEME),
    ("High Contrast",   HIGH_CONTRAST),
]


def sty(size: int, color=None) -> TextStyle:
    return TextStyle(font_size=size, color=color or WHITE)


WIN_W  = 900
WIN_H  = 600
SEP_X  = 420   # left panel / canvas boundary
LBL_W  = 100   # width of the row label
CTRL_W = 190   # slider / range-slider width

_GREY  = Color(0.5, 0.5, 0.5)
_LGREY = Color(0.4, 0.4, 0.4)


class WidgetsExample(DefEnv):
    def __init__(self, root: RootEnv) -> None:
        self.root       = root
        self._theme_idx = 0
        root.ui.theme   = _THEMES[0][1]

        ui = root.ui
        h  = WIN_H

        # ── Left panel VBox ──────────────────────────────────────────────────
        #  Covers the whole left side; children lay out top-to-bottom.
        left = ui.vbox(
            spacing=4,
            position=V2(0, 0),
            size=V2(SEP_X, h),
            bg_color=Color(0.07, 0.07, 0.11, 1.0),
            border_color=Color(0.20, 0.20, 0.35, 1.0),
            border_width=1.0,
            padding=10,
        )

        # ── Title ────────────────────────────────────────────────────────────
        lbl_title = ui.label("Phase 2 Widgets Demo", default_style=sty(22, WHITE))
        left.add_child(lbl_title)
        lbl_hints = ui.label(
            "T = theme   R = reset   F3 = debug   ESC = quit",
            default_style=sty(11, _GREY),
        )
        left.add_child(lbl_hints)

        self._click_count = 0
        self._all_enabled = True

        # ── helper: section header ─────────────────────────────────────────
        def _sec(text: str) -> None:
            lb = ui.label("", default_style=sty(10, _LGREY))
            lb.set_plain_text(text)
            left.add_child(lb)

        def _row(label_text: str, widget, value_lbl=None) -> None:
            """HBox row: [label | widget | optional value readout]."""
            row = HBox(
                spacing=6, align='center',
                size=V2(SEP_X - 24, 34),
                bg_color=Color(0, 0, 0, 0),
                padding=0,
            )
            if label_text:
                lb = ui.label("", default_style=sty(13, WHITE))
                lb.set_plain_text(label_text)
                lb.size      = V2(LBL_W, 28)
                lb.size_mode = SizeMode.FIXED
                row.add_child(lb)
            row.add_child(widget)
            if value_lbl is not None:
                row.add_child(value_lbl)
            left.add_child(row)

        # ── Button section ───────────────────────────────────────────────────
        _sec("BUTTON")
        self._btn_increment = ui.button(
            "Increment Counter",
            on_click=self._on_increment,
            size=V2(152, 32),
        )
        self._btn_toggle_enabled = ui.button(
            "Disable Widgets",
            on_click=self._on_toggle_enabled,
            size=V2(148, 32),
        )
        btn_row = HBox(spacing=6, align='center',
                       size=V2(SEP_X - 24, 36),
                       bg_color=Color(0, 0, 0, 0),
                       padding=0)
        btn_row.add_child(self._btn_increment)
        btn_row.add_child(self._btn_toggle_enabled)
        left.add_child(btn_row)

        self._lbl_count = ui.label("", default_style=sty(14, CYAN))
        self._lbl_count.set_plain_text("Clicks: 0")
        left.add_child(self._lbl_count)

        # ── Switch section ───────────────────────────────────────────────────
        _sec("SWITCH — toggles canvas animation")
        self._lbl_switch = ui.label("", default_style=sty(13, GREEN))
        self._lbl_switch.set_plain_text("ON")
        self._switch = ui.switch(value=True, on_change=self._on_switch)
        _row("Animated:", self._switch, self._lbl_switch)

        # ── Checkbox section ─────────────────────────────────────────────────
        _sec("CHECKBOX — show/hide score label")
        self._lbl_check = ui.label("", default_style=sty(13, GREEN))
        self._lbl_check.set_plain_text("visible")
        self._checkbox = ui.checkbox(value=True, on_change=self._on_checkbox)
        _row("Show score:", self._checkbox, self._lbl_check)

        # ── Horizontal Slider (continuous) ───────────────────────────────────
        _sec("SLIDER (continuous) — circle radius  10..120")
        self._lbl_radius = ui.label("", default_style=sty(13, YELLOW))
        self._lbl_radius.set_plain_text("60")
        self._slider_radius = ui.slider(
            10, 120, value=60,
            on_change=self._on_radius,
            size=V2(CTRL_W, 20),
        )
        _row("Radius:", self._slider_radius, self._lbl_radius)

        # ── Horizontal Slider (step=5) ───────────────────────────────────────
        _sec("SLIDER (step=5) — score  0..100")
        self._lbl_score_val = ui.label("", default_style=sty(13, YELLOW))
        self._lbl_score_val.set_plain_text("50")
        self._slider_score = ui.slider(
            0, 100, step=5, value=50,
            on_change=self._on_score,
            size=V2(CTRL_W, 20),
        )
        _row("Score:", self._slider_score, self._lbl_score_val)
        self._score      = 50
        self._show_score = True

        # ── RangeSlider ──────────────────────────────────────────────────────
        _sec("RANGE SLIDER — brightness range  0..255")
        self._lbl_range = ui.label("", default_style=sty(13, YELLOW))
        self._lbl_range.set_plain_text("[64, 192]")
        self._range_slider = ui.range_slider(
            0, 255, step=1,
            low_value=64, high_value=192,
            on_change=self._on_range,
            size=V2(CTRL_W, 20),
        )
        _row("Brightness:", self._range_slider, self._lbl_range)
        self._brightness_lo = 64
        self._brightness_hi = 192

        # ── Vertical Slider ──────────────────────────────────────────────────
        _sec("VERT. SLIDER — circle count  1..12  (↑↓ when focused)")
        self._lbl_count_val = ui.label("", default_style=sty(13, YELLOW))
        self._lbl_count_val.set_plain_text("6")
        self._slider_count = ui.slider(
            1, 12, step=1, value=6,
            orientation='vertical',
            on_change=self._on_count,
            size=V2(20, 90),
        )
        _row("Count:", self._slider_count, self._lbl_count_val)
        self._circle_count = 6

        # ── Canvas labels (right panel, absolute positions) ──────────────────
        self._canvas_cx = SEP_X + (WIN_W - SEP_X) / 2
        self._canvas_cy = WIN_H / 2

        ui.label(
            "Live Canvas",
            position=V2(self._canvas_cx, 14),
            pivot=Pivot.TOP_MIDDLE,
            default_style=sty(14, _GREY),
        )
        self._score_label = ui.label(
            "Score: 50",
            position=V2(self._canvas_cx, WIN_H - 14),
            pivot=Pivot.BOTTOM_MIDDLE,
            default_style=sty(20, YELLOW),
        )

        # Animation state
        self._angle      = 0.0
        self._animated   = True
        self._radius_val = 60.0

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_increment(self) -> None:
        self._click_count += 1
        self._lbl_count.set_plain_text(f"Clicks: {self._click_count}")

    def _on_count(self, v: float) -> None:
        self._circle_count = int(v)
        self._lbl_count_val.set_plain_text(f"{int(v)}")

    def _on_toggle_enabled(self) -> None:
        self._all_enabled = not self._all_enabled
        state = self._all_enabled
        for w in (self._switch, self._checkbox,
                  self._slider_radius, self._slider_score,
                  self._range_slider, self._slider_count):
            w.enabled = state
        label = "Disable Widgets" if state else "Enable Widgets"
        self._btn_toggle_enabled.text = label

    def _on_switch(self, v: bool) -> None:
        self._animated = v
        color = GREEN if v else _GREY
        self._lbl_switch.set_text(("ON" if v else "OFF", sty(13, color)))

    def _on_checkbox(self, v: bool) -> None:
        self._show_score = v
        color = GREEN if v else _GREY
        text  = "visible" if v else "hidden"
        self._lbl_check.set_text((text, sty(13, color)))
        self._score_label.visible = v

    def _on_radius(self, v: float) -> None:
        self._radius_val = v
        self._lbl_radius.set_plain_text(f"{int(v)}")

    def _on_score(self, v: float) -> None:
        self._score = int(v)
        self._lbl_score_val.set_plain_text(f"{int(v)}")
        self._score_label.set_plain_text(f"Score: {int(v)}")

    def _on_range(self, lo: float, hi: float) -> None:
        self._brightness_lo = int(lo)
        self._brightness_hi = int(hi)
        self._lbl_range.set_plain_text(f"[{int(lo)}, {int(hi)}]")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def update(self) -> None:
        kb = self.root.keyboard

        if kb.get_key(Keys.T, KeyState.JUST_PRESSED):
            self._theme_idx = (self._theme_idx + 1) % len(_THEMES)
            name, theme = _THEMES[self._theme_idx]
            self.root.ui.theme = theme
            print(f"Theme: {name}")

        if kb.get_key(Keys.R, KeyState.JUST_PRESSED):
            self._reset()

        if kb.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
            glfw.set_window_should_close(self.root.window, True)

        if self._animated:
            self._angle += self.root.delta * 1.2

    def _reset(self) -> None:
        """Reset all widgets to their default values."""
        self._click_count = 0
        self._lbl_count.set_plain_text("Clicks: 0")
        self._switch.value           = True
        self._checkbox.value         = True
        self._slider_radius.value    = 60
        self._slider_score.value     = 50
        self._range_slider.low_value  = 64
        self._range_slider.high_value = 192
        self._slider_count.value     = 6

    def draw(self) -> None:
        root  = self.root
        theme = root.ui.theme
        bg    = theme.bg_window
        sep_c = theme.border_color

        # Canvas background (right side)
        root.draw_rect(
            V2(SEP_X, 0), V2(WIN_W - SEP_X, WIN_H),
            color=(max(0.0, bg.r - 0.01),
                   max(0.0, bg.g - 0.01),
                   max(0.0, bg.b - 0.01), 1.0),
        )
        root.draw_line(V2(SEP_X, 0), V2(SEP_X, WIN_H),
                       color=(sep_c.r, sep_c.g, sep_c.b, sep_c.a), width=1.0)

        # ── Canvas: circles drawn in a ring ─────────────────────────────
        cx   = self._canvas_cx
        cy   = self._canvas_cy
        n    = int(self._circle_count)
        r    = self._radius_val
        cw   = WIN_W - SEP_X
        ring = max(10.0, min(cw, WIN_H) * 0.3)

        lo_t = self._brightness_lo / 255.0
        hi_t = self._brightness_hi / 255.0

        for i in range(n):
            frac   = i / max(1, n)
            bright = lo_t + (hi_t - lo_t) * frac
            base_a = math.tau * frac + (self._angle if self._animated else 0)

            px = cx + math.cos(base_a) * ring
            py = cy + math.sin(base_a) * ring

            hue = math.tau * frac
            cr  = 0.5 + 0.5 * math.cos(hue)
            cg  = 0.5 + 0.5 * math.cos(hue + 2.094)
            cb  = 0.5 + 0.5 * math.cos(hue + 4.189)

            root.draw_circle(V2(px, py), r,
                             color=(cr * bright, cg * bright, cb * bright, 0.85),
                             layer=1)

        root.draw_circle(V2(cx, cy), 5, color=(0.6, 0.6, 0.6, 0.8))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = WindowConfig(
        size=V2(WIN_W, WIN_H),
        title="e2D Phase 2 Widgets (Phase 4 layout)",
        target_fps=60,
        vsync=False,
    )
    root = RootEnv(config=config)
    root.init(env := WidgetsExample(root))
    root.loop()


if __name__ == "__main__":
    main()
