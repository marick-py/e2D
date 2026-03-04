"""
example_stats.py — Phase 6: Live Stats Overlay & FPS Graph demo.

The stats panel (F2) shows FPS, frame time, UPS, physics step and elapsed
time, topped by a scrolling FPS line graph backed by a GPU ring-buffer.

Scenes:
  1 — Idle          minimal draw load  → high, stable FPS
  2 — Shape stress  10 000+ draw calls → observe FPS drop in graph
  3 — Fixed update  physics loop at configurable rate (UPS row visible)

Controls:
  1 / 2 / 3     — switch scene
  F2            — toggle stats panel  (always works)
  +  /  -       — stress: increase / decrease shape count  (scene 2)
  U  /  D       — physics: faster / slower UPS             (scene 3)
"""

from __future__ import annotations
import sys as _sys, os as _os, math, random
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keys, KeyState, TextStyle,
    WHITE, CYAN, YELLOW, GREEN, RED,
    LinearGradient, RadialGradient,
)
from e2D.colors import Color

# ──────────────────────────────────────────────────────────────────────────────
WIN_W = 960
WIN_H = 640


class StatsDemo(DefEnv):
    def __init__(self, root: RootEnv):
        self.root     = root
        self.ui       = root.ui
        self.t        = 0.0
        self.scene    = 1
        self._phys_t  = 0.0     # simple physics counter for scene 3

        # scene-2 stress
        self._shape_count = 500
        self._shapes: list[tuple] = []   # [(x,y,r,color)]
        random.seed(42)
        self._regen_shapes(2000)

        # scene-3 physics counters
        self._phys_ticks  = 0
        self._ball_x      = WIN_W / 2
        self._ball_vx     = 180.0   # px per second of physics time
        self._ball_vy     = 140.0
        self._ball_y      = WIN_H / 2

        self._build_ui()

        # Open the stats panel immediately so the user sees it right away
        self.ui.show_stats = True

    # ── shape pool ─────────────────────────────────────────────────────────
    def _regen_shapes(self, n: int) -> None:
        self._shapes = [
            (
                random.uniform(0, WIN_W),
                random.uniform(0, WIN_H),
                random.uniform(4, 22),
                Color(random.random(), random.random(), random.random(), 0.65),
            )
            for _ in range(n)
        ]

    # ── UI ─────────────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        from e2D.ui import VBox, HBox, Button, Label, UIContainer

        hint_bg = LinearGradient(
            stops=[(Color(0.05, 0.12, 0.20, 0.92), 0.0),
                   (Color(0.02, 0.06, 0.14, 0.92), 1.0)],
            angle=0.0,
        )

        bar = self.ui.add(HBox(
            position=V2(0, 0), size=V2(WIN_W, 46),
            bg_gradient=hint_bg,
            padding=(6, 8, 6, 8), spacing=8,
        ))
        for i, title in enumerate(["1 Idle", "2 Stress", "3 Physics"], 1):
            bar.add_child(self.ui.add(Button(
                title, size=V2(110, 30),
                on_click=lambda n=i: self._switch(n),
            )))

        from e2D.ui import Label as _Label
        self._hint: _Label = self.ui.add(Label(  # type: ignore[assignment]
            self._hint_text(),
            position=V2(WIN_W - 310, 52),
            default_style=TextStyle(font_size=10, color=Color(0.70, 0.80, 0.70, 1.0)),
        ))

    def _hint_text(self) -> str:
        if self.scene == 2:
            return (f"Shapes: {self._shape_count}   (+/- to change)\n"
                    f"F2 — toggle stats panel")
        elif self.scene == 3:
            ups = int(round(1.0 / self.root._fixed_dt)) if self.root._fixed_dt > 0 else 0
            return (f"UPS: {ups}   (U/D to change)\n"
                    f"F2 — toggle stats panel")
        return "F2 — toggle stats panel"

    # ── scene switching ────────────────────────────────────────────────────
    def _switch(self, n: int) -> None:
        self.scene = n
        if n == 3:
            # enable fixed timestep at 60 UPS
            self.root._fixed_dt = 1.0 / 60.0
        else:
            self.root._fixed_dt = 0.0

    # ── lifecycle ──────────────────────────────────────────────────────────
    def fixed_update(self, dt: float) -> None:
        """Called by the fixed-rate loop (scene 3)."""
        if self.scene != 3:
            return
        self._ball_x += self._ball_vx * dt
        self._ball_y += self._ball_vy * dt
        r = 18.0
        if self._ball_x - r < 0:
            self._ball_x = r; self._ball_vx *= -1
        if self._ball_x + r > WIN_W:
            self._ball_x = WIN_W - r; self._ball_vx *= -1
        if self._ball_y - r < 0:
            self._ball_y = r; self._ball_vy *= -1
        if self._ball_y + r > WIN_H:
            self._ball_y = WIN_H - r; self._ball_vy *= -1
        self._phys_ticks += 1

    def update(self, dt: float) -> None:
        self.t += self.root.delta
        keys = self.root.keyboard

        for i in (1, 2, 3):
            k = getattr(Keys, f"NUM_{i}", None)
            if k and keys.get_key(k, KeyState.JUST_PRESSED):
                self._switch(i)

        if self.scene == 2:
            if (keys.get_key(Keys.EQUAL, KeyState.JUST_PRESSED)
                    or keys.get_key(Keys.KP_ADD, KeyState.JUST_PRESSED)):
                self._shape_count = min(self._shape_count + 500, 20000)
                self._regen_shapes(self._shape_count)
            if (keys.get_key(Keys.MINUS, KeyState.JUST_PRESSED)
                    or keys.get_key(Keys.KP_SUBTRACT, KeyState.JUST_PRESSED)):
                self._shape_count = max(self._shape_count - 500, 100)
                self._regen_shapes(self._shape_count)

        if self.scene == 3:
            if keys.get_key(Keys.U, KeyState.JUST_PRESSED):
                cur = int(round(1.0 / self.root._fixed_dt)) if self.root._fixed_dt > 0 else 60
                self.root._fixed_dt = 1.0 / min(cur + 20, 300)
            if keys.get_key(Keys.D, KeyState.JUST_PRESSED):
                cur = int(round(1.0 / self.root._fixed_dt)) if self.root._fixed_dt > 0 else 60
                self.root._fixed_dt = 1.0 / max(cur - 20, 10)

        self._hint.set_plain_text(self._hint_text())

    def draw(self) -> None:
        if self.scene == 1:
            self._draw_scene_idle()
        elif self.scene == 2:
            self._draw_scene_stress()
        elif self.scene == 3:
            self._draw_scene_physics()

    # ── scene 1 — idle ─────────────────────────────────────────────────────
    def _draw_scene_idle(self) -> None:
        # Gentle animated gradient background
        bg = LinearGradient(
            stops=[(Color(0.04, 0.06, 0.16, 1.0), 0.0),
                   (Color(0.10, 0.04, 0.22, 1.0), 1.0)],
            angle=self.t * 0.2,
        )
        self.root.draw_rect_gradient(V2(0, 0), V2(WIN_W, WIN_H), gradient=bg)

        # A few glowing rings
        for k in range(5):
            angle = self.t * 0.5 + k * math.tau / 5
            cx = WIN_W / 2 + math.cos(angle) * 180
            cy = WIN_H / 2 + math.sin(angle * 0.7) * 110
            for ring in range(3):
                self.root.draw_circle(
                    V2(cx, cy), 18 - ring * 5,
                    color=Color(0, 0, 0, 0),
                    border_color=Color(0.30 + ring * 0.25,
                                       0.70 - ring * 0.15,
                                       1.00, 0.55 - ring * 0.15),
                    border_width=1.5,
                )

        self.root.print(
            "Scene 1 — Idle\nF2 to open the stats panel\n"
            "Notice the FPS graph is smooth and flat.",
            V2(20, WIN_H // 2 - 30),
            style=TextStyle(font_size=13, color=WHITE),
        )

    # ── scene 2 — shape stress ─────────────────────────────────────────────
    def _draw_scene_stress(self) -> None:
        self.root.draw_rect(V2(0, 0), V2(WIN_W, WIN_H),
                            color=Color(0.04, 0.04, 0.06, 1.0))

        t = self.t
        for x, y, r, c in self._shapes[:self._shape_count]:
            ox = math.sin(t * 0.4 + x * 0.01) * 14
            oy = math.cos(t * 0.4 + y * 0.01) * 14
            self.root.draw_circle(V2(x + ox, y + oy), r, color=c)

        self.root.print(
            f"Scene 2 — Shape stress test\n"
            f"{self._shape_count} circles   (+/- to adjust)\n"
            f"Watch the FPS graph dip.",
            V2(20, WIN_H // 2 - 30),
            style=TextStyle(font_size=11, color=WHITE),
        )

    # ── scene 3 — fixed physics ────────────────────────────────────────────
    def _draw_scene_physics(self) -> None:
        fdt = self.root._fixed_dt if self.root._fixed_dt > 0 else 1.0 / 60.0
        ups = int(round(1.0 / fdt))

        bg = RadialGradient(
            stops=[(Color(0.05, 0.12, 0.22, 1.0), 0.0),
                   (Color(0.02, 0.04, 0.10, 1.0), 1.0)],
        )
        self.root.draw_rect_gradient(V2(0, 0), V2(WIN_W, WIN_H), gradient=bg)

        # Trail
        for i in range(12):
            alpha_trail = (i / 12) * 0.35
            offset = 12 - i
            self.root.draw_circle(
                V2(self._ball_x - self._ball_vx * fdt * offset,
                   self._ball_y - self._ball_vy * fdt * offset),
                18 * (i / 12),
                color=Color(0.20, 0.80, 1.00, alpha_trail),
            )

        self.root.draw_circle(
            V2(self._ball_x, self._ball_y), 18,
            color=Color(0.20, 0.80, 1.00, 1.0),
            border_color=WHITE, border_width=1.5,
        )

        self.root.print(
            f"Scene 3 — Fixed physics loop\n"
            f"UPS = {ups}   (U / D to change)\n"
            f"Notice UPS row in the stats panel.\n"
            f"Physics ticks: {self._phys_ticks}",
            V2(20, WIN_H // 2 - 40),
            style=TextStyle(font_size=11, color=WHITE),
        )


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cfg = WindowConfig(
        title="e2D — Phase 6: Stats Overlay & FPS Graph",
        size=(WIN_W, WIN_H),
        target_fps=0,
        vsync=False
    )
    root = RootEnv(cfg)
    env  = StatsDemo(root)
    root.init(env)
    root.loop()
