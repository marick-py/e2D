"""
Example demonstrating color system in e2D
Shows color creation, manipulation, pre-defined colors, and color operations.
Uses the UI system (Labels, HBox, VBox) for text layout.
"""

from e2D import (
    RootEnv, DefEnv, V2, Color, WindowConfig,
    normalize_color, lerp_colors, gradient,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA,
    TextStyle, Label, VBox, HBox, FreeContainer, SizeMode,
)
from e2D.palette import (
    MD_RED, MD_PINK, MD_PURPLE, MD_DEEP_PURPLE, MD_INDIGO,
    MD_BLUE, MD_LIGHT_BLUE, MD_CYAN, MD_TEAL, MD_GREEN,
    PASTEL_RED, PASTEL_ORANGE, PASTEL_YELLOW, PASTEL_GREEN,
    PASTEL_CYAN, PASTEL_BLUE, PASTEL_PURPLE, PASTEL_PINK,
    NEON_RED, NEON_GREEN, NEON_BLUE, NEON_PINK,
    UI_SUCCESS, UI_WARNING, UI_ERROR, UI_INFO
)


# -- helpers -----------------------------------------------------------------

_TITLE_STYLE = TextStyle(font_size=28, color=WHITE)
_SECTION     = TextStyle(font_size=18, color=WHITE)
_LABEL       = TextStyle(font_size=14, color=WHITE)
_SMALL_LABEL = TextStyle(font_size=13, color=WHITE)
_DIM_LABEL   = TextStyle(font_size=13, color=(0.75, 0.75, 0.75, 1.0))


class ColorsExample(DefEnv):
    """Example showing color system features"""

    def __init__(self, root: RootEnv) -> None:
        self.root = root
        self.frame = 0
        ui = root.ui

        # ── Main layout: FreeContainer covers the window ─────────────────
        self._main = ui.free_container(
            position=V2(0, 0),
            size=V2(900, 600),
            anchor_min=(0.0, 0.0), anchor_max=(1.0, 1.0),
            bg_color=Color(0.0, 0.0, 0.0, 0.0),
        )

        # ── Title ────────────────────────────────────────────────────────
        self._add(ui.label("Color System Examples", default_style=_TITLE_STYLE),
                  10, 10)

        # ── Section 1: Basic Colors ──────────────────────────────────────
        self._add(ui.label("Basic Colors:", default_style=_SECTION), 10, 50)
        # Names are rendered as centered labels below each circle (in draw)

        basic = ["RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA", "WHITE", "BLACK"]
        self._basic_name_lbls = []
        for i, name in enumerate(basic):
            x = 20 + i * 56
            lbl = ui.label(name, default_style=_SMALL_LABEL)
            self._add(lbl, x, 115)
            self._basic_name_lbls.append(lbl)

        # ── Section 2: Material Design Colors ────────────────────────────
        self._add(ui.label("Material Design:", default_style=_SECTION), 10, 145)

        # ── Section 3: Pastel Colors ─────────────────────────────────────
        self._add(ui.label("Pastel Colors:", default_style=_SECTION), 10, 225)

        # ── Section 4: Neon Colors ───────────────────────────────────────
        self._add(ui.label("Neon Colors:", default_style=_SECTION), 10, 305)

        # ── Section 5: UI Feedback Colors (HBox with buttons) ────────────
        self._add(ui.label("UI Feedback:", default_style=_SECTION), 10, 385)

        ui_data = [
            ("SUCCESS", UI_SUCCESS),
            ("WARNING", UI_WARNING),
            ("ERROR",   UI_ERROR),
            ("INFO",    UI_INFO),
        ]
        self._ui_fb_row = HBox(
            spacing=8, align='center',
            position=V2(0, 0), size=V2(480, 36),
            bg_color=Color(0, 0, 0, 0),
        )
        for name, color in ui_data:
            c = Color(color.r, color.g, color.b)  # type: ignore[union-attr]
            btn = ui.button(
                name,
                size=V2(110, 32),
                color_normal=c,
                color_hover=c.lighten(0.15),
                color_pressed=c.darken(0.15),
            )
            btn.enabled = False  # just display, no click
            self._ui_fb_row.add_child(btn)
        self._main.add_child(self._ui_fb_row)
        self._main._child_offsets[id(self._ui_fb_row)] = (10.0, 415.0)

        # ── Section 6: Color Operations (right side) ─────────────────────
        self._add(ui.label("Color Operations:", default_style=_SECTION), 500, 50)
        self._add(ui.label("Lighten:", default_style=_LABEL), 500, 85)
        self._add(ui.label("Darken:",  default_style=_LABEL), 500, 145)
        self._add(ui.label("Hue Rotation:", default_style=_LABEL), 500, 205)

        # ── Section 7: Gradients ─────────────────────────────────────────
        self._add(ui.label("Gradients:", default_style=_SECTION), 500, 275)

        # ── Section 8: Animated ──────────────────────────────────────────
        self._add(ui.label("Animated:", default_style=_SECTION), 500, 395)
        self._add(ui.label("Hue",       default_style=_DIM_LABEL), 530, 470)
        self._add(ui.label("Pulse",     default_style=_DIM_LABEL), 600, 470)
        self._add(ui.label("Fade",      default_style=_DIM_LABEL), 670, 470)

        self._main._compute_layout()

    # -- helper: add a child to _main at a local offset --------------------

    def _add(self, elem, x: float, y: float):
        self._main.add_child(elem)
        self._main._child_offsets[id(elem)] = (float(x), float(y))

    def update(self, dt: float) -> None:
        self.frame += 1

    def draw(self) -> None:
        # ── Basic Colors — circles ───────────────────────────────────────
        basic_colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, BLACK]
        for i, color in enumerate(basic_colors):
            x = 20 + i * 56
            self.root.draw_circle(V2(x + 15, 90), 15, color=color,
                                  border_color=(0.5, 0.5, 0.5, 0.4),
                                  border_width=1.0)

        # ── Material Design — circles ────────────────────────────────────
        md_colors = [
            MD_RED, MD_PINK, MD_PURPLE, MD_DEEP_PURPLE, MD_INDIGO,
            MD_BLUE, MD_LIGHT_BLUE, MD_CYAN, MD_TEAL, MD_GREEN
        ]
        for i, color in enumerate(md_colors):
            x = 10 + i * 44
            self.root.draw_circle(V2(x + 18, 185), 14, color=color)

        # ── Pastel Colors — circles ──────────────────────────────────────
        pastel_colors = [
            PASTEL_RED, PASTEL_ORANGE, PASTEL_YELLOW, PASTEL_GREEN,
            PASTEL_CYAN, PASTEL_BLUE, PASTEL_PURPLE, PASTEL_PINK
        ]
        for i, color in enumerate(pastel_colors):
            x = 10 + i * 56
            self.root.draw_circle(V2(x + 22, 265), 15, color=color)

        # ── Neon Colors — circles ────────────────────────────────────────
        neon_colors = [NEON_RED, NEON_GREEN, NEON_BLUE, NEON_PINK]
        for i, color in enumerate(neon_colors):
            x = 10 + i * 70
            self.root.draw_circle(V2(x + 30, 345), 18, color=color)

        # ── Color Operations — shapes ────────────────────────────────────
        base_color = Color.red()

        for i in range(5):
            lighter = base_color.lighten(i * 0.15)
            self.root.draw_circle(V2(500 + i * 32, 115), 12,
                                  color=lighter.to_rgba())
        for i in range(5):
            darker = base_color.darken(i * 0.15)
            self.root.draw_circle(V2(500 + i * 32, 175), 12,
                                  color=darker.to_rgba())
        for i in range(6):
            rotated = base_color.rotate_hue(i * 60)
            self.root.draw_circle(V2(500 + i * 32, 235), 12,
                                  color=rotated.to_rgba())

        # ── Gradients — rects ────────────────────────────────────────────
        colors2 = gradient([RED, BLUE], 20)
        for i, color in enumerate(colors2):
            self.root.draw_rect(V2(500 + i * 15, 305), V2(14, 30), color=color)

        colors3 = gradient([RED, GREEN, BLUE], 20)
        for i, color in enumerate(colors3):
            self.root.draw_rect(V2(500 + i * 15, 345), V2(14, 30), color=color)

        # ── Animated Colors ──────────────────────────────────────────────
        import math
        t = self.frame * 0.05

        animated_color = Color.from_hsv(t % 1.0, 1.0, 1.0)
        self.root.draw_circle(V2(545, 440), 22, color=animated_color.to_rgba())

        brightness = math.sin(t) * 0.3 + 0.7
        pulsing_color = Color.blue().lighten(brightness - 0.5)
        self.root.draw_circle(V2(615, 440), 22, color=pulsing_color.to_rgba())

        alpha = math.sin(t) * 0.5 + 0.5
        fading_color = Color.green().with_alpha(alpha)
        self.root.draw_circle(V2(685, 440), 22, color=fading_color.to_rgba())

def main() -> None:
    """Run the colors example"""
    config = WindowConfig(
        size=(900, 600),
        title="e2D Colors Example",
        target_fps=60,
        vsync=False
    )
    root = RootEnv(config=config)
    env = ColorsExample(root)
    root.init(env)
    root.loop()

if __name__ == "__main__":
    main()
