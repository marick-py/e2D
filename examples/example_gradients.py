"""
example_gradients.py — Phase 5: Gradients, Opacity Cascade & Blur demo.

Panels:
  1 — Linear Gradients    draw_rect_gradient with various angles & stop counts
  2 — Radial Gradients    concentric and off-center radial fills
  3 — UI Gradients        UIContainer / VBox bg_gradient + opacity cascade
  4 — Blur                frosted-glass blur behind a container

Controls:
  1–4 / click sidebar    — switch panel
  T                      — cycle theme
  F3                     — debug outlines
"""

from __future__ import annotations
import sys as _sys, os as _os, math
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import glfw

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keys, KeyState, TextStyle,
    WHITE, CYAN, YELLOW, GREEN,
    LinearGradient, RadialGradient, PointGradient,
)
from e2D.colors import Color
from e2D.ui import (
    VBox, HBox, Label, Button, Slider, Switch,
    SizeMode, Anchor,
)
from e2D.ui.theme import (
    MONOKAI_THEME, DARK_THEME, LIGHT_THEME, NORD_THEME,
    TOKYO_NIGHT_THEME, DRACULA_THEME,
)

# ──────────────────────────────────────────────────────────────────────────────
WIN_W  = 1000
WIN_H  = 680
SIDE_W = 200
BODY_X = SIDE_W
BODY_W = WIN_W - SIDE_W
BODY_Y = 0
BODY_H = WIN_H

_THEMES = [
    MONOKAI_THEME, DARK_THEME, LIGHT_THEME,
    NORD_THEME, TOKYO_NIGHT_THEME, DRACULA_THEME,
]

NEON_GRAD = LinearGradient(
    stops=[(Color(0.05, 0.85, 0.95, 1.0), 0.0),
           (Color(0.55, 0.10, 0.90, 1.0), 1.0)],
    angle=0.0,
)
SUNSET_GRAD = LinearGradient(
    stops=[(Color(1.00, 0.35, 0.05, 1.0), 0.0),
           (Color(1.00, 0.75, 0.10, 1.0), 0.5),
           (Color(1.00, 0.35, 0.05, 1.0), 1.0)],
    angle=math.pi / 2,
)
FOREST_GRAD = LinearGradient(
    stops=[(Color(0.02, 0.18, 0.04, 1.0), 0.0),
           (Color(0.12, 0.70, 0.25, 1.0), 0.6),
           (Color(0.55, 0.95, 0.40, 1.0), 1.0)],
    angle=math.pi * 0.75,
)
PLASMA_GRAD = LinearGradient(
    stops=[(Color(0.60, 0.00, 0.80, 1.0), 0.0),
           (Color(0.05, 0.40, 0.95, 1.0), 0.33),
           (Color(0.00, 0.90, 0.70, 1.0), 0.66),
           (Color(0.90, 0.80, 0.00, 1.0), 1.0)],
    angle=math.pi * 1.25,
)

RADIAL_SUN = RadialGradient(
    stops=[(Color(1.00, 0.95, 0.30, 1.0), 0.0),
           (Color(1.00, 0.45, 0.00, 0.8), 0.55),
           (Color(0.60, 0.05, 0.00, 0.0), 1.0)],
    center=(0.5, 0.5),
    radius=1.0,
)
RADIAL_SPOTLIGHT = RadialGradient(
    stops=[(Color(1.00, 1.00, 1.00, 0.9), 0.0),
           (Color(0.20, 0.20, 0.50, 0.3), 0.5),
           (Color(0.00, 0.00, 0.10, 0.0), 1.0)],
    center=(0.30, 0.35),
    radius=0.85,
)
RADIAL_VIGNETTE = RadialGradient(
    stops=[(Color(0.85, 0.85, 0.85, 1.0), 0.0),
           (Color(0.10, 0.10, 0.10, 1.0), 1.0)],
    center=(0.5, 0.5),
    radius=1.0,
)


# ──────────────────────────────────────────────────────────────────────────────
# Panel builders
# ──────────────────────────────────────────────────────────────────────────────

def _panel_label(root: RootEnv, text: str) -> None:
    root.print(text, V2(BODY_X + 14, 14),
               style=TextStyle(font_size=16, color=WHITE))


def build_panel_linear(root: RootEnv, t: float) -> None:
    """Panel 1 — linear gradients."""
    _panel_label(root, "Linear Gradients")

    grads = [
        ("Neon  angle=0°",    NEON_GRAD),
        ("Sunset angle=90°",  SUNSET_GRAD),
        ("Forest angle=135°", FOREST_GRAD),
        ("Plasma (4 stops)",  PLASMA_GRAD),
    ]
    GW, GH = 180, 100
    PAD    = 20
    cols   = 4
    for idx, (label_text, g) in enumerate(grads):
        col = idx % cols
        row = idx // cols
        x = BODY_X + PAD + col * (GW + PAD)
        y = 55 + row * (GH + 40)
        root.draw_rect_gradient(V2(x, y), V2(GW, GH), gradient=g,
                                corner_radius=8.0)
        root.print(label_text, V2(x + 4, y + GH + 4),
                   style=TextStyle(font_size=10))

    # Animated spinning gradient
    anim_g = LinearGradient(
        stops=[(Color(0.00, 0.80, 1.00, 1.0), 0.0),
               (Color(0.90, 0.10, 0.50, 1.0), 1.0)],
        angle=t * 1.5,
    )
    row2_y = 55 + GH + 36          # below the first row + label + gap
    ax = BODY_X + PAD
    ay = row2_y
    anim_w = GW * 2 + PAD          # 380 px
    anim_h = GH + 30               # 130 px
    root.draw_rect_gradient(V2(ax, ay), V2(anim_w, anim_h),
                            gradient=anim_g,
                            corner_radius=12.0,
                            border_color=Color(1, 1, 1, 0.3),
                            border_width=1.5)
    root.print("Animated (angle rotates over time)", V2(ax + 6, ay + anim_h + 4),
               style=TextStyle(font_size=10))

    # Gradient with varying opacity (alpha fade overlay)
    fade_g = LinearGradient(
        stops=[(Color(0.20, 0.70, 1.00, 1.0), 0.0),
               (Color(0.20, 0.70, 1.00, 0.0), 1.0)],
        angle=0.0,
    )
    fx = ax + anim_w + PAD          # right of animated gradient
    fy = row2_y
    fade_w = BODY_W - (fx - BODY_X) - PAD
    fade_h = anim_h
    root.draw_rect(V2(fx, fy), V2(fade_w, fade_h),
                  color=Color(0.40, 0.10, 0.50, 1.0), corner_radius=6.0)
    root.draw_rect_gradient(V2(fx, fy), V2(fade_w, fade_h),
                            gradient=fade_g,
                            corner_radius=6.0)
    root.print("Alpha fade overlay", V2(fx + 4, fy + fade_h + 4),
               style=TextStyle(font_size=10))


def build_panel_radial(root: RootEnv, t: float) -> None:  # noqa: ARG001
    """Panel 2 — radial gradients."""
    _panel_label(root, "Radial Gradients")

    grads = [
        ("Sun glow",       RADIAL_SUN,       220, 140),
        ("Off-center spot",RADIAL_SPOTLIGHT, 220, 140),
        ("Vignette",       RADIAL_VIGNETTE,  220, 140),
    ]
    PAD = 20
    x   = BODY_X + PAD
    y   = 55
    for name, g, gw, gh in grads:
        root.draw_rect_gradient(V2(x, y), V2(gw, gh), gradient=g,
                                corner_radius=6.0)
        root.print(name, V2(x + 4, y + gh + 4),
                   style=TextStyle(font_size=10))
        x += gw + PAD

    # Animated pulsing radial
    pulse = 0.35 + 0.30 * abs(math.sin(t * 1.8))
    pulse_g = RadialGradient(
        stops=[(Color(0.20, 1.00, 0.60, 1.0), 0.0),
               (Color(0.00, 0.30, 0.10, 0.0), pulse)],
        center=(0.5, 0.5),
        radius=1.0,
    )
    px = BODY_X + PAD
    py = 55 + 140 + 36
    root.draw_rect_gradient(V2(px, py), V2(700, 160),
                            gradient=pulse_g,
                            corner_radius=10.0,
                            border_color=Color(0.20, 1.00, 0.60, 0.4),
                            border_width=1.5)
    root.print(f"Pulsing radial  (inner radius={pulse:.2f})", V2(px + 6, py + 164),
               style=TextStyle(font_size=10))

    # Multi-point IDW gradient
    shift = 0.08 * math.sin(t * 0.9)
    pt_grad = PointGradient(
        points=[
            ((0.10 + shift, 0.20), Color(1.00, 0.20, 0.30, 1.0)),  # red
            ((0.85 - shift, 0.15), Color(0.10, 0.50, 1.00, 1.0)),  # blue
            ((0.50, 0.85 + shift), Color(0.10, 0.95, 0.40, 1.0)),  # green
            ((0.20, 0.65),         Color(1.00, 0.85, 0.10, 1.0)),  # yellow
            ((0.80, 0.70),         Color(0.80, 0.20, 0.90, 1.0)),  # purple
        ],
        power=2.5,
    )
    ptx = BODY_X + PAD
    pty = py + 160 + 30
    root.draw_rect_gradient(V2(ptx, pty), V2(700, 160),
                            gradient=pt_grad,
                            corner_radius=10.0,
                            border_color=Color(0.80, 0.60, 1.00, 0.4),
                            border_width=1.5)
    root.print("Point gradient (IDW, 5 colour points, power=2.5)",
               V2(ptx + 6, pty + 164),
               style=TextStyle(font_size=10))


def build_panel_ui(ui, root: RootEnv, containers: dict) -> None:
    """Panel 3 — UIContainer bg_gradient + opacity cascade."""
    _panel_label(root, "UI Background Gradients & Opacity Cascade")
    for c in containers.values():
        c.visible = True


def hide_ui_containers(containers: dict) -> None:
    for c in containers.values():
        c.visible = False


def build_panel_blur(root: RootEnv, t: float) -> None:
    """Panel 4 — background blur (frosted glass)."""
    _panel_label(root, "Frosted Glass Blur")

    # Colourful scene behind the blur panels
    cols = [
        Color(0.90, 0.15, 0.30, 1.0),
        Color(0.10, 0.55, 0.95, 1.0),
        Color(0.15, 0.85, 0.45, 1.0),
        Color(0.95, 0.70, 0.05, 1.0),
        Color(0.75, 0.15, 0.90, 1.0),
    ]
    sw = BODY_W / len(cols)
    for i, c in enumerate(cols):
        x = BODY_X + i * sw
        root.draw_rect(V2(x, 0), V2(sw, WIN_H), color=c)

    # Swirling circles
    for k in range(6):
        angle = t * 0.8 + k * math.tau / 6
        cx = BODY_X + BODY_W / 2 + math.cos(angle) * 200
        cy = WIN_H / 2 + math.sin(angle * 1.3) * 130
        root.draw_circle(V2(cx, cy), 40 + 20 * math.sin(t + k),
                         color=Color(1, 1, 1, 0.25))

    root.shape_renderer.flush_queue()


# ──────────────────────────────────────────────────────────────────────────────
class GradientDemo(DefEnv):
    def __init__(self, root: RootEnv):
        self.root   = root
        self.ui     = root.ui
        self.t      = 0.0
        self.panel  = 1
        self._theme_idx = 0

        self._sidebar_btns: list = []
        self._ui_containers: dict = {}
        from e2D.ui import UIElement
        self._blur_container: UIElement | None = None

        self._build_sidebar()
        self._build_ui_panel()
        self._build_blur_panel()

    # ── sidebar ────────────────────────────────────────────────────────────
    def _build_sidebar(self) -> None:
        titles = [
            "1 – Linear Grad",
            "2 – Radial Grad",
            "3 – UI Gradients",
            "4 – Blur (F-Glass)",
        ]
        sidebar = self.ui.add(VBox(
            position=V2(0, 0), size=V2(SIDE_W, WIN_H),
            padding=(60, 8, 8, 8), spacing=6,
            bg_color=Color(0.07, 0.07, 0.10, 0.98),
        ))
        for i, title in enumerate(titles, 1):
            btn = self.ui.add(Button(
                title, size=V2(SIDE_W - 16, 34),
                on_click=lambda n=i: self._switch(n),
            ))
            sidebar.add_child(btn)
            self._sidebar_btns.append(btn)

        self.ui.add(Label(
            "T = cycle theme\nF3 = debug",
            position=V2(8, WIN_H - 42),
            default_style=TextStyle(font_size=10),
        ))

    # ── UI-panel containers ────────────────────────────────────────────────
    def _build_ui_panel(self) -> None:
        from e2D.ui import UIContainer, FreeContainer

        PAD = 14
        CW  = (BODY_W - PAD * 3) // 2
        CH  = 180

        # Parent container with linear gradient background
        parent_g = LinearGradient(
            stops=[(Color(0.08, 0.06, 0.18, 1.0), 0.0),
                   (Color(0.18, 0.08, 0.35, 1.0), 1.0)],
            angle=math.pi / 4,
        )
        outer = self.ui.add(UIContainer(
            position=V2(BODY_X + PAD, 55),
            size=V2(BODY_W - PAD * 2, CH),
            bg_gradient=parent_g,
            corner_radius=10.0,
            border_color=Color(0.55, 0.25, 0.90, 0.6),
            border_width=1.5,
            visible=False,
        ))
        outer.add_child(Label(
            "Parent container  (opacity=1.0, LinearGradient angle=45°)",
            position=V2(10, 10),
            default_style=TextStyle(font_size=11, color=WHITE),
        ))

        # Two child boxes demonstrating opacity cascade
        child_g1 = LinearGradient(
            stops=[(Color(0.05, 0.60, 0.95, 1.0), 0.0),
                   (Color(0.00, 0.90, 0.70, 1.0), 1.0)],
            angle=0.0,
        )
        child1 = UIContainer(
            position=V2(10, 36), size=V2(CW, 100),
            opacity=0.9,
            bg_gradient=child_g1,
            corner_radius=6.0,
        )
        child1.add_child(Label("opacity=0.9 (cascades from parent)",
                               position=V2(8, 8),
                               default_style=TextStyle(font_size=10, color=WHITE)))
        outer.add_child(child1)

        child_g2 = LinearGradient(
            stops=[(Color(0.95, 0.30, 0.10, 1.0), 0.0),
                   (Color(0.95, 0.80, 0.00, 1.0), 1.0)],
            angle=0.0,
        )
        child2 = UIContainer(
            position=V2(CW + PAD * 2 - 4, 36), size=V2(CW, 100),
            opacity=0.5,
            bg_gradient=child_g2,
            corner_radius=6.0,
        )
        child2.add_child(Label("opacity=0.5 (cascades from parent: effective ~0.5)",
                               position=V2(8, 8),
                               default_style=TextStyle(font_size=10, color=WHITE)))
        outer.add_child(child2)

        self._ui_containers["outer"] = outer

        # Second row — VBox with gradient
        vbox_g = LinearGradient(
            stops=[(Color(0.02, 0.14, 0.22, 1.0), 0.0),
                   (Color(0.04, 0.40, 0.55, 1.0), 1.0)],
            angle=math.pi / 2,
        )
        vbox = self.ui.add(VBox(
            position=V2(BODY_X + PAD, 55 + CH + PAD),
            size=V2((BODY_W - PAD * 3) // 2, 200),
            bg_gradient=vbox_g,
            padding=(8, 8, 8, 8), spacing=6,
            corner_radius=8.0,
            border_color=Color(0.05, 0.60, 0.85, 0.5),
            border_width=1.0,
            visible=False,
        ))
        vbox.add_child(Label("VBox with gradient background",
                             default_style=TextStyle(font_size=11, color=CYAN)))
        for i in range(4):
            vbox.add_child(Label(f"  row {i+1}  — opacity cascade test",
                                 default_style=TextStyle(font_size=10)))

        self._ui_containers["vbox"] = vbox

        # Third: nested opacity cascade visualisation
        cascade_g = RadialGradient(
            stops=[(Color(0.80, 0.10, 0.40, 1.0), 0.0),
                   (Color(0.10, 0.05, 0.20, 0.6), 1.0)],
        )
        cascade_outer = self.ui.add(UIContainer(
            position=V2(BODY_X + PAD * 2 + (BODY_W - PAD * 3) // 2, 55 + CH + PAD),
            size=V2((BODY_W - PAD * 3) // 2, 200),
            opacity=0.8,
            bg_gradient=cascade_g,
            corner_radius=8.0,
            border_color=Color(0.80, 0.10, 0.40, 0.6),
            border_width=1.0,
            visible=False,
        ))
        cascade_outer.add_child(Label("outer opacity=0.8, RadialGradient",
                                      position=V2(8, 6),
                                      default_style=TextStyle(font_size=10, color=WHITE)))
        for depth, op in enumerate([0.9, 0.7, 0.5], 1):
            ic = UIContainer(
                position=V2(12 + depth * 6, 28 + depth * 30),
                size=V2((BODY_W - PAD * 3) // 2 - 30 - depth * 12, 26),
                opacity=op,
                bg_color=Color(0.95, 0.80, 0.20, 1.0),
                corner_radius=4.0,
            )
            ic.add_child(Label(f"depth {depth}  opacity={op} → eff≈{0.8*op:.2f}",
                               position=V2(4, 4),
                               default_style=TextStyle(font_size=9, color=Color(0,0,0,1))))
            cascade_outer.add_child(ic)

        self._ui_containers["cascade"] = cascade_outer

    # ── blur panel container ───────────────────────────────────────────────
    def _build_blur_panel(self) -> None:
        from e2D.ui import UIContainer
        bc = self.ui.add(UIContainer(
            position=V2(BODY_X + 160, 160),
            size=V2(340, 240),
            blur=True,
            blur_radius=14.0,
            bg_color=Color(1.0, 1.0, 1.0, 0.12),
            corner_radius=14.0,
            border_color=Color(1.0, 1.0, 1.0, 0.45),
            border_width=1.5,
            visible=False,
        ))
        bc.add_child(Label(
            "Frosted glass\n(blur=True, blur_radius=14)",
            position=V2(16, 16),
            default_style=TextStyle(font_size=13, color=WHITE),
        ))
        bc.add_child(Label(
            "The scene behind this panel\nis Gaussian-blurred before\nthe semi-transparent bg is drawn.",
            position=V2(16, 60),
            default_style=TextStyle(font_size=10, color=Color(0.85, 0.95, 0.90, 1.0)),
        ))
        self._blur_container = bc

    # ── panel switching ────────────────────────────────────────────────────
    def _switch(self, n: int) -> None:
        self.panel = n
        hide_ui_containers(self._ui_containers)
        assert self._blur_container is not None
        self._blur_container.visible = False
        if n == 3:
            for c in self._ui_containers.values():
                c.visible = True
        elif n == 4:
            self._blur_container.visible = True

    # ── lifecycle ──────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        self.t += self.root.delta
        keys = self.root.keyboard

        if keys.get_key(Keys.T, KeyState.JUST_PRESSED):
            self._theme_idx = (self._theme_idx + 1) % len(_THEMES)
            self.ui.theme = _THEMES[self._theme_idx]

        for i in range(1, 5):
            k = getattr(Keys, f"NUM_{i}", None)
            if k and keys.get_key(k, KeyState.JUST_PRESSED):
                self._switch(i)

    def draw(self) -> None:
        # dark base
        self.root.draw_rect(V2(0, 0), V2(WIN_W, WIN_H),
                            color=Color(0.06, 0.06, 0.10, 1.0))
        # sidebar tint
        self.root.draw_rect(V2(0, 0), V2(SIDE_W, WIN_H),
                            color=Color(0.00, 0.00, 0.00, 0.35))

        if self.panel == 1:
            build_panel_linear(self.root, self.t)
        elif self.panel == 2:
            build_panel_radial(self.root, self.t)
        elif self.panel == 3:
            build_panel_ui(self.ui, self.root, self._ui_containers)
        elif self.panel == 4:
            build_panel_blur(self.root, self.t)

        self.root.shape_renderer.flush_queue()


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cfg = WindowConfig(title="e2D — Phase 5: Gradients & Blur",
                       size=(WIN_W, WIN_H))
    root = RootEnv(cfg)
    env  = GradientDemo(root)
    root.init(env)
    root.loop()
