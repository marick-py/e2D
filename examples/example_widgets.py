"""
example_widgets.py — Phase 2 UI widgets demo.

Demonstrates every Phase 2 widget:
  - Button       (click to increment counter; enable/disable all others)
  - Switch       (pill toggle — toggles circle animation on the canvas)
  - Checkbox     (square checkbox — toggles whether score label is shown)
  - Slider       (horizontal, continuous — controls circle radius)
  - Slider       (horizontal, step=5 — controls a score value 0-100)
  - RangeSlider  (horizontal — defines a brightness range [lo, hi])
  - Slider       (vertical — controls number of drawn circles)

Left panel:  all widgets
Right panel: live value readout + a simple canvas visualisation

Controls:
  T     — toggle DARK / LIGHT theme
  R     — reset all widgets to defaults
  ESC   — quit
"""

import math
import glfw

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keys, KeyState, TextStyle,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA,
)
from e2D.colors import Color
from e2D.ui.theme import DARK_THEME, LIGHT_THEME
from e2D._pivot import Pivot


def style(size: int, color=None) -> TextStyle:
    c = color or WHITE
    return TextStyle(font_size=size, color=c)


SEP_X    = 420      # vertical separator between widget panel and canvas
LABEL_X  = 30       # left edge of widget labels
WIDGET_X = 210      # left edge of all widgets
W_W      = 190      # default horizontal slider / range slider width


class WidgetsExample(DefEnv):
    def __init__(self, root: RootEnv) -> None:
        self.root   = root
        self._dark  = True

        ui = root.ui

        # ---------------------------------------------------------------
        # Title + key hints
        # ---------------------------------------------------------------
        ui.label(
            "Phase 2 Widgets Demo",
            position=V2(10, 10),
            default_style=style(24, WHITE),
        )
        ui.label(
            "T = theme   |   R = reset   |   ESC = quit",
            position=V2(10, 42),
            default_style=style(13, Color(0.6, 0.6, 0.6)),
        )

        # ---------------------------------------------------------------
        # Section: Button
        # ---------------------------------------------------------------
        ui.label("BUTTON", position=V2(LABEL_X, 78),
                 default_style=style(11, Color(0.5, 0.5, 0.5)))

        self._click_count   = 0
        self._all_enabled   = True

        self._btn_increment = ui.button(
            "Increment Counter",
            on_click=self._on_increment,
            position=V2(WIDGET_X, 95),
            size=V2(150, 32),
        )
        self._btn_toggle_enabled = ui.button(
            "Disable Widgets",
            on_click=self._on_toggle_enabled,
            position=V2(WIDGET_X + 158, 95),
            size=V2(145, 32),
        )
        self._lbl_count = ui.label(
            "Clicks: 0",
            position=V2(LABEL_X, 107),
            default_style=style(14, CYAN),
        )

        # ---------------------------------------------------------------
        # Section: Switch
        # ---------------------------------------------------------------
        ui.label("SWITCH — animation on canvas circles",
                 position=V2(LABEL_X, 142),
                 default_style=style(11, Color(0.5, 0.5, 0.5)))
        ui.label("Animated:",
                 position=V2(LABEL_X, 163),
                 default_style=style(14, WHITE))
        self._switch = ui.switch(
            value=True,
            on_change=self._on_switch,
            position=V2(WIDGET_X, 160),
        )
        self._lbl_switch = ui.label(
            "ON",
            position=V2(WIDGET_X + 62, 163),
            default_style=style(14, GREEN),
        )

        # ---------------------------------------------------------------
        # Section: Checkbox
        # ---------------------------------------------------------------
        ui.label("CHECKBOX — show score label",
                 position=V2(LABEL_X, 204),
                 default_style=style(11, Color(0.5, 0.5, 0.5)))
        ui.label("Show score:",
                 position=V2(LABEL_X, 225),
                 default_style=style(14, WHITE))
        self._checkbox = ui.checkbox(
            value=True,
            on_change=self._on_checkbox,
            position=V2(WIDGET_X, 223),
        )
        self._lbl_check = ui.label(
            "visible",
            position=V2(WIDGET_X + 32, 225),
            default_style=style(14, GREEN),
        )

        # ---------------------------------------------------------------
        # Section: Horizontal Slider (continuous) — circle radius
        # ---------------------------------------------------------------
        ui.label("SLIDER (continuous) — circle radius",
                 position=V2(LABEL_X, 260),
                 default_style=style(11, Color(0.5, 0.5, 0.5)))
        ui.label("Radius:",
                 position=V2(LABEL_X, 281),
                 default_style=style(14, WHITE))
        self._slider_radius = ui.slider(
            10, 120, value=60,
            on_change=self._on_radius,
            position=V2(WIDGET_X, 278),
            size=V2(W_W, 20),
        )
        self._lbl_radius = ui.label(
            "60",
            position=V2(WIDGET_X + W_W + 8, 281),
            default_style=style(14, YELLOW),
        )

        # ---------------------------------------------------------------
        # Section: Horizontal Slider (step=5) — score
        # ---------------------------------------------------------------
        ui.label("SLIDER (step=5) — score 0..100",
                 position=V2(LABEL_X, 313),
                 default_style=style(11, Color(0.5, 0.5, 0.5)))
        ui.label("Score:",
                 position=V2(LABEL_X, 334),
                 default_style=style(14, WHITE))
        self._slider_score = ui.slider(
            0, 100, step=5, value=50,
            on_change=self._on_score,
            position=V2(WIDGET_X, 331),
            size=V2(W_W, 20),
        )
        self._lbl_score_val = ui.label(
            "50",
            position=V2(WIDGET_X + W_W + 8, 334),
            default_style=style(14, YELLOW),
        )
        self._score = 50
        self._show_score = True

        # ---------------------------------------------------------------
        # Section: RangeSlider — brightness range
        # ---------------------------------------------------------------
        ui.label("RANGE SLIDER — brightness range",
                 position=V2(LABEL_X, 366),
                 default_style=style(11, Color(0.5, 0.5, 0.5)))
        ui.label("Brightness:",
                 position=V2(LABEL_X, 387),
                 default_style=style(14, WHITE))
        self._range_slider = ui.range_slider(
            0, 255, step=1,
            low_value=64, high_value=192,
            on_change=self._on_range,
            position=V2(WIDGET_X, 384),
            size=V2(W_W, 20),
        )
        self._lbl_range = ui.label(
            "[64, 192]",
            position=V2(WIDGET_X + W_W + 8, 387),
            default_style=style(14, YELLOW),
        )
        self._brightness_lo = 64
        self._brightness_hi = 192

        # ---------------------------------------------------------------
        # Section: Vertical Slider — number of circles
        # ---------------------------------------------------------------
        ui.label("VERT. SLIDER — circle count",
                 position=V2(LABEL_X, 418),
                 default_style=style(11, Color(0.5, 0.5, 0.5)))
        ui.label("Count:",
                 position=V2(LABEL_X, 439),
                 default_style=style(14, WHITE))
        self._slider_count = ui.slider(
            1, 12, step=1, value=6,
            orientation='vertical',
            on_change=self._on_count,
            position=V2(WIDGET_X, 435),
            size=V2(20, 120),
        )
        self._lbl_count_val = ui.label(
            "6",
            position=V2(WIDGET_X + 28, 439),
            default_style=style(14, YELLOW),
        )
        self._circle_count = 6

        # ---------------------------------------------------------------
        # Separator label
        # ---------------------------------------------------------------
        ui.label(
            "↑↓ drag or use arrow keys when focused",
            position=V2(WIDGET_X + 28, 508),
            default_style=style(11, Color(0.4, 0.4, 0.4)),
        )

        # ---------------------------------------------------------------
        # Canvas labels (right panel)
        # ---------------------------------------------------------------
        self._canvas_x = SEP_X + 10
        self._canvas_w = root.window_size.x - SEP_X - 10
        self._canvas_cx = SEP_X + self._canvas_w / 2
        self._canvas_cy = root.window_size.y / 2

        ui.label(
            "Live Canvas",
            position=V2(self._canvas_cx, 14),
            pivot=Pivot.TOP_MIDDLE,
            default_style=style(14, Color(0.45, 0.45, 0.45)),
        )

        # Score display (bottom of canvas)
        self._score_label = ui.label(
            "Score: 50",
            position=V2(self._canvas_cx, root.window_size.y - 14),
            pivot=Pivot.BOTTOM_MIDDLE,
            default_style=style(20, YELLOW),
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
        color = GREEN if v else Color(0.5, 0.5, 0.5)
        self._lbl_switch.set_text(("ON" if v else "OFF", style(14, color)))

    def _on_checkbox(self, v: bool) -> None:
        self._show_score = v
        color = GREEN if v else Color(0.5, 0.5, 0.5)
        text  = "visible" if v else "hidden"
        self._lbl_check.set_text((text, style(14, color)))
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
            self._dark = not self._dark
            self.root.ui.theme = DARK_THEME if self._dark else LIGHT_THEME

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
        root = self.root
        w, h = root.window_size.x, root.window_size.y

        # Panel background (left)
        root.draw_rect(V2(0, 0), V2(SEP_X, h),
                       color=(0.06, 0.06, 0.08, 1.0))

        # Panel background (right / canvas)
        root.draw_rect(V2(SEP_X, 0), V2(w - SEP_X, h),
                       color=(0.04, 0.04, 0.06, 1.0))

        # Separator line
        root.draw_line(V2(SEP_X, 0), V2(SEP_X, h),
                       color=(0.2, 0.2, 0.2, 1.0), width=1.0)

        # ---- Canvas: circles drawn in a ring ---------------------------
        cx   = self._canvas_cx
        cy   = self._canvas_cy
        n    = int(self._circle_count)
        r    = self._radius_val
        ring = max(10.0, min(self._canvas_w, h) * 0.3)

        # Brightness range → colour tint
        lo_t = self._brightness_lo / 255.0
        hi_t = self._brightness_hi / 255.0

        for i in range(n):
            frac   = i / max(1, n)
            alpha  = frac           # 0 → 1 across the ring
            bright = lo_t + (hi_t - lo_t) * frac  # mapped to brightness range

            base_angle = math.tau * frac
            if self._animated:
                base_angle += self._angle

            px = cx + math.cos(base_angle) * ring
            py = cy + math.sin(base_angle) * ring

            # Cycle hue across ring
            hue = math.tau * frac
            cr  = 0.5 + 0.5 * math.cos(hue)
            cg  = 0.5 + 0.5 * math.cos(hue + 2.094)
            cb  = 0.5 + 0.5 * math.cos(hue + 4.189)

            root.draw_circle(
                V2(px, py), r,
                color=(cr * bright, cg * bright, cb * bright, 0.85),
            )

        # Centre dot
        root.draw_circle(V2(cx, cy), 5, color=(0.6, 0.6, 0.6, 0.8))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = WindowConfig(
        size=V2(900, 580),
        title="e2D Phase 2 Widgets",
        target_fps=60,
        vsync=False,
    )
    root = RootEnv(config=config)
    root.init(env := WidgetsExample(root))
    root.loop()


if __name__ == "__main__":
    main()
