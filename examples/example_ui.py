"""
example_ui.py — Phase 1 UI system demo.

Shows:
  - UIManager  (root.ui)
  - Label      (plain text and rich multi-segment text)
  - Pivot      (nine preset anchor positions)
  - UITheme    (9 built-in themes)
  - wants_keyboard / wants_mouse  (UI focus guards for game input)

For Phase 4 containers (VBox, HBox, Grid, ScrollContainer, FreeContainer)
see  example_containers.py.

Controls:
  T            - cycle through 9 themes
  P            - cycle through all 9 Pivot presets on the demo label
  ESC          - quit
"""

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import glfw

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keys, KeyState, TextStyle,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA,
)
from e2D.ui.theme import DARK_THEME, LIGHT_THEME, UITheme
from e2D._pivot import Pivot
from e2D.ui.label import Label


# ---------------------------------------------------------------------------
# helper — build a TextStyle quickly
# ---------------------------------------------------------------------------

def style(size: int, color) -> TextStyle:
    return TextStyle(font_size=size, color=color)


# All 9 Pivot presets in order (name, Pivot constant)
_PIVOTS = [
    ("TOP_LEFT",      Pivot.TOP_LEFT),
    ("TOP_MIDDLE",    Pivot.TOP_MIDDLE),
    ("TOP_RIGHT",     Pivot.TOP_RIGHT),
    ("LEFT",          Pivot.LEFT),
    ("CENTER",        Pivot.CENTER),
    ("RIGHT",         Pivot.RIGHT),
    ("BOTTOM_LEFT",   Pivot.BOTTOM_LEFT),
    ("BOTTOM_MIDDLE", Pivot.BOTTOM_MIDDLE),
    ("BOTTOM_RIGHT",  Pivot.BOTTOM_RIGHT),
]


class UIExample(DefEnv):
    """Demonstrates the e2D UI layer."""

    def __init__(self, root: RootEnv) -> None:
        self.root = root
        self._dark = True

        # ---- Static labels created once -----------------------------------

        # Title in the top-left
        self._title_lbl = root.ui.label(
            "e2D UI Example",
            position=V2(20, 20),
            pivot=Pivot.TOP_LEFT,
            default_style=style(28, WHITE),
        )

        # Subtitle
        self._sub_lbl = root.ui.label(
            "Press  ",
            ("T", style(18, YELLOW)),
            "  to toggle theme   |   ",
            ("P", style(18, CYAN)),
            "  to cycle pivot   |   ",
            ("ESC", style(18, RED)),
            "  to quit",
            position=V2(root.window_size.x / 2, 68),
            pivot=Pivot.TOP_MIDDLE,
            default_style=style(18, WHITE),
        )

        # Rich-text demo label — position will be updated live
        self._pivot_idx = 4   # start at CENTER
        self._demo_lbl = root.ui.label(
            "Pivot: ",
            (f"{_PIVOTS[self._pivot_idx][0]}", style(22, CYAN)),
            position=self._pivot_pos(),
            pivot=_PIVOTS[self._pivot_idx][1],
            default_style=style(22, WHITE),
        )

        # "wants_mouse" status label in the bottom-left
        self._mouse_lbl = root.ui.label(
            "wants_mouse: ",
            ("?", style(16, YELLOW)),
            position=V2(20, root.window_size.y - 20),
            pivot=Pivot.BOTTOM_LEFT,
            default_style=style(16, WHITE),
        )

        # "wants_keyboard" status label below that
        self._kb_lbl = root.ui.label(
            "wants_keyboard: ",
            ("?", style(16, YELLOW)),
            position=V2(20, root.window_size.y - 44),
            pivot=Pivot.BOTTOM_LEFT,
            default_style=style(16, WHITE),
        )

        # Theme indicator in bottom-right
        self._theme_lbl = root.ui.label(
            "DARK THEME",
            position=V2(root.window_size.x - 20, root.window_size.y - 20),
            pivot=Pivot.BOTTOM_RIGHT,
            default_style=style(18, CYAN),
        )

    # -- helpers -------------------------------------------------------------

    def _pivot_pos(self) -> V2:
        """Return the screen position for the current pivot demo."""
        cx, cy = self.root.window_size.x / 2, self.root.window_size.y / 2
        return V2(cx, cy)

    def _apply_theme(self, theme: UITheme) -> None:
        self.root.ui.theme = theme

    # -- lifecycle -----------------------------------------------------------

    def update(self) -> None:
        kb = self.root.keyboard

        # T — toggle dark / light theme
        if kb.get_key(Keys.T, KeyState.JUST_PRESSED):
            self._dark = not self._dark
            theme = DARK_THEME if self._dark else LIGHT_THEME
            self._apply_theme(theme)
            name = "DARK THEME" if self._dark else "LIGHT THEME"
            color = CYAN if self._dark else MAGENTA
            self._theme_lbl.set_text((name, style(18, color)))

        # P — cycle pivot
        if kb.get_key(Keys.P, KeyState.JUST_PRESSED):
            self._pivot_idx = (self._pivot_idx + 1) % len(_PIVOTS)
            pname, ppivot = _PIVOTS[self._pivot_idx]
            self._demo_lbl.pivot = ppivot
            self._demo_lbl.position = self._pivot_pos()
            self._demo_lbl.set_text(
                "Pivot: ",
                (pname, style(22, CYAN)),
            )

        # ESC — quit
        if kb.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
            glfw.set_window_should_close(self.root.window, True)

        # Update status labels
        wm = self.root.ui.wants_mouse
        wk = self.root.ui.wants_keyboard
        self._mouse_lbl.set_text(
            "wants_mouse: ",
            ("YES" if wm else "no", style(16, GREEN if wm else YELLOW)),
        )
        self._kb_lbl.set_text(
            "wants_keyboard: ",
            ("YES" if wk else "no", style(16, GREEN if wk else YELLOW)),
        )

    def draw(self) -> None:
        # Draw a subtle grid to show the window centre
        w, h = self.root.window_size.x, self.root.window_size.y
        cx, cy = w / 2, h / 2

        # Crosshair at window centre (the pivot anchor point)
        self.root.draw_line(V2(cx - 15, cy), V2(cx + 15, cy), color=(0.5, 0.5, 0.5, 0.8), width=1)
        self.root.draw_line(V2(cx, cy - 15), V2(cx, cy + 15), color=(0.5, 0.5, 0.5, 0.8), width=1)
        self.root.draw_circle(V2(cx, cy), 4, color=(1.0, 1.0, 0.0, 0.9))

        # Light border around the display area
        self.root.draw_rect(V2(10, 10), V2(w - 20, h - 20),
                            color=(0, 0, 0, 0),
                            border_color=(0.3, 0.3, 0.3, 1.0),
                            border_width=1.0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = WindowConfig(
        size=V2(900, 600),
        title="e2D Phase 1 — Labels & Pivots",
        target_fps=60,
        vsync=False,
    )
    root = RootEnv(config=config)
    root.init(env := UIExample(root))
    root.loop()


if __name__ == "__main__":
    main()
