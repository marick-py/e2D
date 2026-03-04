"""
e2D Application Template
========================

Copy this file to start a new project.  Uncomment the sections you need.

Sections:
  1. Imports & colours
  2. App class  (update / draw / fixed_update / events)
  3. UI setup   (optional — LiveStream, Labels, Buttons)
  4. Window configuration & run-loop

Press  F2   to toggle the built-in stats panel (FPS + FPS graph).
Press  ESC  to quit.
"""

from e2D import (
    RootEnv, DefEnv, WindowConfig,
    V2, Color,
    LinearGradient, RadialGradient, PointGradient,
    UIStream, Label, Button,
    MONOKAI_THEME,
)
from e2D.input import Keys, KeyState
from e2D.palette import WHITE, BLACK


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class MyApp(DefEnv):

    def __init__(self) -> None:
        # ── UI ──────────────────────────────────────────────────────────────
        # UIManager is available as  self.ui  inside DefEnv.
        # Show the built-in stats overlay automatically (toggle: F2).
        # self.ui.show_stats = True

        # ── Live FPS graph widget ────────────────────────────────────────────
        # self._fps_graph = self.ui.add(UIStream(
        #     position=V2(10, 10),
        #     size=V2(280, 100),
        #     capacity=300,
        #     y_range=(0, 200),
        #     gradient=LinearGradient(
        #         stops=[
        #             (Color(0.02, 0.05, 0.10, 0.95), 0.0),
        #             (Color(0.04, 0.10, 0.22, 0.90), 1.0),
        #         ],
        #         angle=90.0,
        #     ),
        # ))
        # self._fps_series = self._fps_graph.add_series(
        #     "FPS",
        #     line_color=Color(0.15, 0.95, 0.50, 1.0),
        # )

        # ── Example label ────────────────────────────────────────────────────
        # self._lbl = self.ui.add(Label(
        #     "Hello e2D!",
        #     position=V2(20, 120),
        # ))

        ...

    # ── Per-frame callbacks ─────────────────────────────────────────────────

    def update(self) -> None:
        """Called every frame (before :meth:`draw`).  ``self.dt`` = delta-time (s)."""
        # Push latest FPS to the live graph (if enabled):
        # self._fps_series.push_value(1.0 / self.dt if self.dt > 0 else 0.0)

        # Quit on ESC
        if self.keys.get(Keys.ESCAPE) == KeyState.PRESSED:
            self.root.close()

    def draw(self) -> None:
        """Called every frame after :meth:`update`.  Use shape_renderer here."""
        # self.shape_renderer.draw_circle(V2(960, 540), 80, WHITE)
        ...

    # ── Optional: fixed physics step ────────────────────────────────────────

    # def fixed_update(self, dt: float) -> None:
    #     """Called at a fixed rate (set in WindowConfig.ups)."""
    #     ...

    # ── Optional: window resize ─────────────────────────────────────────────

    # def on_resize(self, new_size: V2) -> None:
    #     ...


# ---------------------------------------------------------------------------
# Window configuration & entry point
# ---------------------------------------------------------------------------

win_conf = WindowConfig(
    size=V2(1920, 1080),
    target_fps=60,
    title="My e2D App",
    vsync=True,
    resizable=False,
    # ups=60,          # uncomment to enable fixed_update()
)

rootEnv = RootEnv(config=win_conf)
rootEnv.init(env := MyApp())

# Optional: enable screen recording  (requires  pip install e2D[rec])
# rootEnv.init_rec(fps=30, draw_on_screen=True, path='recording.mp4')

rootEnv.loop()
