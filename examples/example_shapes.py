"""
example_shapes.py — FULL e2D ShapeRenderer showcase  (1920 × 1080).

7 pages (1 per key / sidebar button):
  1 – Circles        draw_circle  + all params
  2 – Rectangles     draw_rect    + all params
  3 – Gradients      LinearGradient / RadialGradient / PointGradient
  4 – Lines          draw_line / draw_lines
  5 – Cached         ShapeLabel  (create_circle / create_rect / create_line / create_lines)
  6 – Batches        InstancedShapeBatch  (circle / rect / line)
  7 – Layers         draw-order control via layer=
"""

from __future__ import annotations

import math
import random
import numpy as np

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    UIManager, Button,
    ShapeLabel, InstancedShapeBatch,
    LinearGradient, RadialGradient, PointGradient,
    WHITE, BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW,
    ORANGE, PURPLE, PINK, GRAY50, TRANSPARENT,
    Color, TextStyle, Keys, KeyState,
)

# ── constants ─────────────────────────────────────────────────────────────────

WIN_W, WIN_H = 1920, 1080
SIDE_W       = 200          # sidebar
HDR_H        = 50           # top bar
CANVAS_X     = SIDE_W       # left edge of drawing area
CANVAS_Y     = HDR_H        # top edge of drawing area
CANVAS_W     = WIN_W - SIDE_W
CANVAS_H     = WIN_H - HDR_H

# ── tiny draw helpers ─────────────────────────────────────────────────────────

def _lab(root, text, x, y, size=12):
    root.print(text, V2(x, y), style=TextStyle(font_size=size, color=WHITE))


def _heading(root, text, x=CANVAS_X+14, y=CANVAS_Y+8, size=16):
    root.print(text, V2(x, y), style=TextStyle(font_size=size, color=YELLOW))


def _subhead(root, text, x, y):
    root.print(text, V2(x, y), style=TextStyle(font_size=13, color=CYAN))


def _sidebar_bg(root):
    """Dark sidebar background."""
    root.draw_rect(V2(0, 0), V2(SIDE_W, WIN_H),
                   color=Color(0.05, 0.05, 0.09), layer=-1)
    root.draw_rect(V2(0, 0), V2(WIN_W, HDR_H),
                   color=Color(0.04, 0.04, 0.08), layer=-1)


_NAV_LABELS = [
    "1  Circles",
    "2  Rectangles",
    "3  Gradients",
    "4  Lines",
    "5  Cached",
    "6  Batches",
    "7  Layers",
]


# ── main class ────────────────────────────────────────────────────────────────

class ShapesFullShowcase(DefEnv):

    # -- cached ShapeLabel objects (built once) --
    _cached_circle:       ShapeLabel | None = None
    _cached_rect:         ShapeLabel | None = None
    _cached_line:         ShapeLabel | None = None
    _cached_lines:        ShapeLabel | None = None
    _cached_lines_closed: ShapeLabel | None = None

    # -- InstancedShapeBatch objects (built once) --
    _batch_circle:    InstancedShapeBatch | None = None
    _batch_circle_np: InstancedShapeBatch | None = None
    _batch_rect:      InstancedShapeBatch | None = None
    _batch_rect_np:   InstancedShapeBatch | None = None
    _batch_line:      InstancedShapeBatch | None = None
    _batch_line_np:   InstancedShapeBatch | None = None

    def __init__(self, root: RootEnv) -> None:
        self.root  = root
        self.frame = 0
        self.page  = 0          # 0-indexed, maps to pages 1–7

        # Build real sidebar navigation buttons via the UI system
        ui = root.ui
        self._nav_btns: list[Button] = []
        sidebar = ui.vbox(
            spacing=4,
            position=V2(0, HDR_H), size=V2(SIDE_W, WIN_H - HDR_H),
            bg_color=Color(0.05, 0.05, 0.09, 1.0),
            border_color=Color(0.18, 0.18, 0.30, 1.0),
            border_width=1.0,
            padding=8,
        )
        for i, label in enumerate(_NAV_LABELS):
            btn = ui.button(
                label,
                on_click=lambda n=i: self._set_page(n),
                size=V2(SIDE_W - 16, 38),
            )
            sidebar.add_child(btn)
            self._nav_btns.append(btn)

    def _set_page(self, n: int) -> None:
        self.page = n

    def update(self, dt: float) -> None:
        self.frame += 1
        kb = self.root.keyboard
        keys = [Keys.NUM_1, Keys.NUM_2, Keys.NUM_3, Keys.NUM_4,
                Keys.NUM_5, Keys.NUM_6, Keys.NUM_7]
        for i, k in enumerate(keys):
            if kb.get_key(k, KeyState.JUST_PRESSED):
                self.page = i

    def draw(self) -> None:
        t = self.frame * 0.03
        _sidebar_bg(self.root)

        # Header
        page_names = [
            "draw_circle — all parameters",
            "draw_rect — all parameters",
            "draw_rect_gradient — Linear / Radial / Point",
            "draw_line / draw_lines",
            "ShapeLabel via create_* (cached GPU objects)",
            "InstancedShapeBatch — create_*_batch / add_* / flush",
            "Layer ordering — draw-order control via layer=",
        ]
        self.root.print(
            f"Page {self.page+1}/7  ·  {page_names[self.page]}",
            V2(CANVAS_X + 14, 14),
            style=TextStyle(font_size=14, color=WHITE),
        )

        [
            self._page_circles,
            self._page_rects,
            self._page_gradients,
            self._page_lines,
            self._page_cached,
            self._page_batches,
            self._page_layers,
        ][self.page](t)

    # =========================================================================
    # PAGE 1 — CIRCLES
    # 9 rows, each row = one variant, stacked vertically
    # =========================================================================
    def _page_circles(self, t: float) -> None:
        root = self.root
        CX  = CANVAS_X + 100    # circle center X
        SPC = 105               # row spacing
        R   = 38                # base radius
        LX  = CANVAS_X + 175   # label X

        _heading(root, "draw_circle — every parameter combination")

        rows = [
            ("plain",                            {}),
            ("color=RED",                        dict(color=RED)),
            ("color=TRANSPARENT + border_color=CYAN  border_width=5",
                dict(color=TRANSPARENT, border_color=CYAN, border_width=5.0)),
            ("color=(0.2,0.6,0.2)  border_color=WHITE  border_width=10",
                dict(color=(0.2, 0.6, 0.2, 1.0), border_color=WHITE, border_width=10.0)),
            ("antialiasing=0.0  (hard pixel edge)",
                dict(color=YELLOW, antialiasing=0.0)),
            ("antialiasing=8.0  (very soft / glow)",
                dict(color=MAGENTA, antialiasing=8.0)),
            ("all params: color, rotation, border_color, border_width, antialiasing, layer",
                dict(color=ORANGE, rotation=0.0, border_color=WHITE,
                     border_width=5.0, antialiasing=2.0, layer=3)),
            ("layer=10  (drawn on top of layer=0 shapes)",
                dict(color=BLUE, border_color=YELLOW, border_width=4.0, layer=10)),
            ("animated: radius + border_width + color oscillate each frame",
                None),   # handled separately below
        ]

        for i, (desc, kwargs) in enumerate(rows):
            cy = CANVAS_Y + 60 + i * SPC
            if kwargs is None:
                ar  = R - 6 + math.sin(t * 2) * 14
                abw = max(0.0, math.cos(t) * 8)
                root.draw_circle(
                    V2(CX, cy), ar,
                    color=(math.sin(t)*0.5+0.5, 0.3, math.cos(t)*0.5+0.5, 1.0),
                    border_color=WHITE, border_width=abw, antialiasing=2.0,
                )
            else:
                root.draw_circle(V2(CX, cy), R, **kwargs)
            _lab(root, desc, LX, cy - 8)

    # =========================================================================
    # PAGE 2 — RECTANGLES
    # =========================================================================
    def _page_rects(self, t: float) -> None:
        root = self.root
        RX   = CANVAS_X + 60
        RY0  = CANVAS_Y + 56
        SPC  = 100
        RW, RH = 110, 62
        LX   = CANVAS_X + 200

        _heading(root, "draw_rect — every parameter combination")

        rows = [
            ("plain",
             {}),
            ("color=RED  corner_radius=16",
             dict(color=RED, corner_radius=16.0)),
            ("color=TRANSPARENT  border_color=CYAN  border_width=4  (border only)",
             dict(color=TRANSPARENT, border_color=CYAN, border_width=4.0)),
            ("color=GREEN  rotation=π/6  (45° rotation)",
             dict(color=GREEN, rotation=math.pi/6)),
            ("rotation=π/4  corner_radius=12  border_color=YELLOW  border_width=4",
             dict(color=(0.2,0.2,0.8,1.0), rotation=math.pi/4,
                  corner_radius=12.0, border_color=YELLOW, border_width=4.0)),
            ("color=PURPLE  corner_radius=8  antialiasing=0.0  (hard edge)",
             dict(color=PURPLE, corner_radius=8.0, antialiasing=0.0)),
            ("color=PINK  corner_radius=8  antialiasing=7.0  (glow)",
             dict(color=PINK, corner_radius=8.0, antialiasing=7.0)),
            ("all params: color, rotation, corner_radius, border, aa, layer",
             dict(color=ORANGE, corner_radius=12.0,
                  border_color=WHITE, border_width=3.0,
                  antialiasing=2.0, layer=2)),
            ("animated: rotation + color  (all params combined)",
             None),
        ]

        for i, (desc, kwargs) in enumerate(rows):
            ry = RY0 + i * SPC
            if kwargs is None:
                root.draw_rect(
                    V2(RX, ry), V2(RW, RH),
                    color=(math.sin(t)*0.5+0.5, 0.4, math.cos(t)*0.5+0.5, 1.0),
                    rotation=t, corner_radius=14.0,
                    border_color=WHITE, border_width=3.0,
                    antialiasing=2.0, layer=0,
                )
            else:
                root.draw_rect(V2(RX, ry), V2(RW, RH), **kwargs)
            _lab(root, desc, LX, ry + 18)

    # =========================================================================
    # PAGE 3 — GRADIENTS
    # 3 sub-sections (Linear / Radial / Point), 4 columns each
    # =========================================================================
    def _page_gradients(self, t: float = 0.0) -> None:
        root = self.root
        GW, GH = 210, 110   # per-gradient rect size
        COL_SPC = 230       # horizontal stride
        SEC_H   = 200       # vertical band per section

        _heading(root, "draw_rect_gradient — LinearGradient / RadialGradient / PointGradient")

        # ── Linear ───────────────────────────────────────────────────────────
        SY = CANVAS_Y + 42
        _subhead(root, "LinearGradient(stops, angle)", CANVAS_X + 14, SY)
        lin_items = [
            ("2-stop  angle=0 (L→R)",
             LinearGradient([(Color(0.2,0.4,0.9),0.0),(Color(0.9,0.2,0.4),1.0)], angle=0.0)),
            ("3-stop  angle=π/2 (T→B)",
             LinearGradient([(Color(1,0,0),0),(Color(1,1,0),0.5),(Color(0,1,0),1)], angle=math.pi/2)),
            ("4-stop  angle=π/4  (diagonal)",
             LinearGradient([
                 (Color(0,0,0.5),0),(Color(0,0.5,1),0.33),
                 (Color(0.5,1,0.5),0.66),(Color(1,1,0),1)
             ], angle=math.pi/4)),
            ("8-stop rainbow  angle=0  (max stops)",
             LinearGradient([
                 (Color(1,0,0),0/7),(Color(1,.5,0),1/7),(Color(1,1,0),2/7),
                 (Color(0,1,0),3/7),(Color(0,1,1),4/7),(Color(0,0,1),5/7),
                 (Color(.5,0,1),6/7),(Color(1,0,1),7/7),
             ], angle=0.0)),
            ("angle=π (R→L)  corner_r=18  border",
             LinearGradient([(Color(0.1,0.9,0.4),0),(Color(0.9,0.1,0.8),1)], angle=math.pi)),
            ("rotation=π/8  opacity=0.65",
             LinearGradient([(Color(0.9,0.7,0.1),0),(Color(0.2,0.9,0.7),1)], angle=0.0)),
        ]
        lin_extra = [
            {},
            {},
            {},
            {},
            dict(corner_radius=18.0, border_color=WHITE, border_width=3.0),
            dict(rotation=math.pi/8, opacity=0.65),
        ]
        for ci, (desc, grad) in enumerate(lin_items):
            x = CANVAS_X + 14 + ci * COL_SPC
            root.draw_rect_gradient(V2(x, SY+22), V2(GW, GH), grad, **lin_extra[ci])
            _lab(root, desc, x, SY + 22 + GH + 4)

        # ── Radial ───────────────────────────────────────────────────────────
        SY2 = SY + SEC_H
        _subhead(root, "RadialGradient(stops, center, radius)", CANVAS_X + 14, SY2)
        rad_items = [
            ("default  center=(0.5,0.5)  r=1.0",
             RadialGradient([(Color(1,1,1),0),(Color(0.1,0.1,0.5),1)])),
            ("center=(0.2,0.2)  r=1.0",
             RadialGradient([(Color(1,0.8,0),0),(Color(0.5,0,0),1)], center=(0.2,0.2))),
            ("r=0.4  (sharp hot-spot)",
             RadialGradient([(Color(0,1,0.5),0),(Color(0,0,0.3),1)], radius=0.4)),
            ("r=1.8  (extends beyond rect)",
             RadialGradient([(Color(1,0.4,0.1),0),(Color(0.1,0,0.5),1)], radius=1.8)),
            ("center=(0.9,0.9)  r=1.2",
             RadialGradient([(Color(0,1,1),0),(Color(0.4,0,0.8),1)], center=(0.9,0.9), radius=1.2)),
            ("3-stop  corner_r=22  border  opacity=0.85",
             RadialGradient([
                 (Color(1,1,0.3),0),(Color(0.6,0.1,0.9),0.6),(Color(0,0,0),1)
             ], center=(0.5,0.5), radius=1.0)),
        ]
        rad_extra = [
            {},{},{},{},{},
            dict(corner_radius=22.0, border_color=WHITE, border_width=3.0, opacity=0.85),
        ]
        for ci, (desc, grad) in enumerate(rad_items):
            x = CANVAS_X + 14 + ci * COL_SPC
            root.draw_rect_gradient(V2(x, SY2+22), V2(GW, GH), grad, **rad_extra[ci])
            _lab(root, desc, x, SY2 + 22 + GH + 4)

        # ── Point ─────────────────────────────────────────────────────────────
        SY3 = SY2 + SEC_H
        _subhead(root, "PointGradient(points, power, normalized)", CANVAS_X + 14, SY3)
        rng = random.Random(42)
        pts16 = [(V2(rng.uniform(0.05,0.95), rng.uniform(0.05,0.95)),
                  Color(rng.random(), rng.random(), rng.random()))
                 for _ in range(16)]
        pt_items = [
            ("3-pts  UV  power=2.0  (smooth)",
             PointGradient([(V2(0.1,0.1),Color(1,0,0)),(V2(0.9,0.1),Color(0,1,0)),(V2(0.5,0.9),Color(0,0,1))], power=2.0, normalized=True)),
            ("3-pts  UV  power=8.0  (Voronoi)",
             PointGradient([(V2(0.1,0.1),Color(1,0,0)),(V2(0.9,0.1),Color(0,1,0)),(V2(0.5,0.9),Color(0,0,1))], power=8.0, normalized=True)),
            ("3-pts  px-coords  normalized=False",
             PointGradient([((20,20),Color(1,.5,0)),((190,20),Color(0,.8,1)),((105,90),Color(.8,0,.8))], power=2.0, normalized=False)),
            ("5-pts  power=0.5  (ultra-smooth)",
             PointGradient([(V2(.5,.5),Color(1,1,1)),(V2(0,0),Color(1,0,0)),(V2(1,0),Color(0,1,0)),(V2(1,1),Color(0,0,1)),(V2(0,1),Color(1,1,0))], power=0.5, normalized=True)),
            ("3-pts  corner_r=20  border  opacity=0.9",
             PointGradient([(V2(.25,.25),Color(0,1,1)),(V2(.75,.25),Color(1,0,1)),(V2(.5,.8),Color(1,1,0))], power=3.0)),
            ("16-pts (max IDW)  power=2.0",
             PointGradient(pts16, power=2.0, normalized=True)),
        ]
        pt_extra = [
            {},{},{},{},
            dict(corner_radius=20.0, border_color=WHITE, border_width=3.0, opacity=0.9),
            {},
        ]
        for ci, (desc, grad) in enumerate(pt_items):
            x = CANVAS_X + 14 + ci * COL_SPC
            root.draw_rect_gradient(V2(x, SY3+22), V2(GW, GH), grad, **pt_extra[ci])
            _lab(root, desc, x, SY3 + 22 + GH + 4)

        # note at bottom
        ny = SY3 + SEC_H
        _lab(root, "All gradient rects also support: rotation=, opacity=, corner_radius=, border_color=, border_width=, antialiasing=, layer=",
             CANVAS_X + 14, ny, size=11)

    # =========================================================================
    # PAGE 4 — LINES
    # =========================================================================
    def _page_lines(self, t: float = 0.0) -> None:
        root = self.root
        LX0 = CANVAS_X + 30
        SPC = 110

        _heading(root, "draw_line / draw_lines — every parameter combination")

        # Row 0: draw_line plain
        Y = CANVAS_Y + 50
        root.draw_line(V2(LX0, Y), V2(LX0+320, Y), width=2.0, color=WHITE)
        _lab(root, "draw_line  width=2  color=WHITE", LX0 + 330, Y - 6)

        # Row 1: width=6, color
        Y += SPC
        root.draw_line(V2(LX0, Y), V2(LX0+320, Y), width=6.0, color=YELLOW)
        _lab(root, "draw_line  width=6  color=YELLOW", LX0 + 330, Y - 6)

        # Row 2: width=14 + antialiasing
        Y += SPC
        root.draw_line(V2(LX0, Y), V2(LX0+320, Y), width=14.0, color=CYAN, antialiasing=3.0)
        _lab(root, "draw_line  width=14  antialiasing=3.0  (soft edge)", LX0 + 330, Y - 6)

        # Row 3: diagonal
        Y += SPC
        root.draw_line(V2(LX0, Y), V2(LX0+320, Y+90), width=6.0, color=ORANGE, layer=0)
        _lab(root, "draw_line  diagonal  width=6  layer=0", LX0 + 330, Y - 6)

        # Row 4: draw_lines open zigzag
        Y += SPC + 30
        zigzag = [V2(LX0 + i*64, Y + (60 if i%2 else 0)) for i in range(6)]
        root.draw_lines(zigzag, width=4.0, color=GREEN)
        _lab(root, "draw_lines  open zigzag  width=4  uniform color", LX0 + 400, Y + 20)

        # Row 5: draw_lines closed hexagon
        Y += SPC + 30
        hc = V2(LX0 + 160, Y + 40)
        hex_pts = [V2(hc.x + 55*math.cos(math.pi/3*i), hc.y + 55*math.sin(math.pi/3*i)) for i in range(6)]
        root.draw_lines(hex_pts, width=5.0, color=PINK, closed=True)
        _lab(root, "draw_lines  closed=True  hexagon  width=5", LX0 + 360, Y + 30)

        # draw_lines with per-segment numpy colors (open)
        seg_pts = np.array([[LX0+520, Y+10],[LX0+580, Y+90],[LX0+640, Y+10],[LX0+700, Y+90],[LX0+760, Y+10]], dtype='f4')
        seg_col = np.array([[1,0,0,1],[1,1,0,1],[0,1,0,1],[0,0.5,1,1]], dtype='f4')
        root.draw_lines(seg_pts, width=5.0, color=seg_col)
        _lab(root, "draw_lines  per-segment numpy colors  (open)", LX0+780, Y+30)

        # Row 6: draw_lines closed square + per-seg numpy colors
        Y += SPC + 60
        sq_pts = np.array([[LX0, Y],[LX0+200, Y],[LX0+200, Y+130],[LX0, Y+130]], dtype='f4')
        sq_col = np.array([[1,0,0,1],[0,1,0,1],[0,0,1,1],[1,1,0,1]], dtype='f4')
        root.draw_lines(sq_pts, width=7.0, color=sq_col, closed=True)
        _lab(root, "draw_lines  closed=True  per-segment numpy colors  square  width=7", LX0+220, Y+50)

        # spiral (many-point draw_lines)
        spiral = [V2(LX0+680 + (5+k*1.5)*math.cos(k*0.26), Y+70 + (5+k*1.5)*math.sin(k*0.26)) for k in range(60)]
        sc = np.array([[math.sin(k/60*math.pi*2)*0.5+0.5, math.cos(k/60*math.pi)*0.5+0.5, 0.8, 1.0] for k in range(59)], dtype='f4')
        root.draw_lines(spiral, width=3.5, color=sc)
        _lab(root, "draw_lines  spiral  60 pts  per-seg colors", LX0+780, Y+50)

    # =========================================================================
    # PAGE 5 — CACHED SHAPES (ShapeLabel)
    # =========================================================================
    def _page_cached(self, t: float = 0.0) -> None:
        root = self.root
        SPC = 200
        CX0 = CANVAS_X + 120
        CY  = CANVAS_Y + 200

        _heading(root, "ShapeLabel objects via create_*  (built once, drawn every frame from GPU cache)")

        # ── create_circle ─────────────────────────────────────────────────────
        if self._cached_circle is None:
            self._cached_circle = root.create_circle(
                V2(CX0, CY), 65,
                color=RED, border_color=WHITE,
                border_width=5.0, antialiasing=2.0,
            )
        self._cached_circle.draw()
        _lab(root, "create_circle\ncenter, radius, color,\nborder_color, border_width,\nantialiasing", CX0 - 80, CY + 75)

        # ── create_rect ───────────────────────────────────────────────────────
        if self._cached_rect is None:
            self._cached_rect = root.create_rect(
                V2(CX0 + SPC, CY - 40), V2(140, 90),
                color=GREEN, rotation=math.pi/8,
                corner_radius=14.0,
                border_color=YELLOW, border_width=4.0,
                antialiasing=2.0,
            )
        self._cached_rect.draw()
        _lab(root, "create_rect\npos, size, color, rotation,\ncorner_radius, border_color,\nborder_width, antialiasing", CX0 + SPC - 80, CY + 75)

        # ── create_line ───────────────────────────────────────────────────────
        if self._cached_line is None:
            self._cached_line = root.create_line(
                V2(CX0 + SPC*2 - 90, CY), V2(CX0 + SPC*2 + 90, CY),
                width=10.0, color=CYAN, antialiasing=2.5,
            )
        self._cached_line.draw()
        _lab(root, "create_line\nstart, end, width,\ncolor, antialiasing", CX0 + SPC*2 - 80, CY + 30)

        # ── create_lines open wave ────────────────────────────────────────────
        WX = CX0 + SPC * 3
        if self._cached_lines is None:
            wave = [V2(WX - 120 + i * 30, CY + math.sin(i * 0.9) * 50) for i in range(9)]
            self._cached_lines = root.create_lines(
                wave, width=6.0, color=ORANGE, antialiasing=2.0,
            )
        self._cached_lines.draw()
        _lab(root, "create_lines  open\npoints, width, color,\nantialiasing", WX - 80, CY + 75)

        # ── create_lines closed star ──────────────────────────────────────────
        SX = CX0 + SPC * 4
        if self._cached_lines_closed is None:
            star = []
            for i in range(10):
                r   = 65 if i % 2 == 0 else 28
                ang = math.pi/2 + 2*math.pi*i/10
                star.append(V2(SX + r*math.cos(ang), CY + r*math.sin(ang)))
            self._cached_lines_closed = root.create_lines(
                star, width=5.0, color=MAGENTA, closed=True,
            )
        self._cached_lines_closed.draw()
        _lab(root, "create_lines  closed=True\n5-point star\nwidth=5", SX - 80, CY + 75)

        # notes
        _lab(root,
             "ShapeLabel caches the shape into a GPU object once  →  0 CPU overhead each frame.\n"
             "Calling .draw() re-uses the cached buffer.",
             CANVAS_X + 14, WIN_H - 90)

    # =========================================================================
    # PAGE 6 — BATCHES
    # =========================================================================
    def _page_batches(self, t: float) -> None:
        root = self.root

        _heading(root, "InstancedShapeBatch — create_*_batch / add_* / add_*_numpy / flush")

        COL_W  = (CANVAS_W - 30) // 3
        COL_H  = (CANVAS_H - 70) // 2
        COLS   = [CANVAS_X + 10, CANVAS_X + 10 + COL_W, CANVAS_X + 10 + COL_W*2]
        ROWS   = [CANVAS_Y + 50, CANVAS_Y + 50 + COL_H]

        # helper to draw a labeled box around each demo
        def _box(col, row):
            root.draw_rect(V2(COLS[col], ROWS[row]), V2(COL_W-6, COL_H-10),
                           color=Color(0.08,0.08,0.14), corner_radius=8.0,
                           border_color=Color(0.2,0.2,0.35), border_width=1.0,
                           layer=-1)

        # ── 6A circle manual (5×6 grid) ──────────────────────────────────────
        _box(0, 0)
        _subhead(root, "circle_batch + add_circle  (5×6 manual)", COLS[0]+8, ROWS[0]+8)
        if self._batch_circle is None:
            self._batch_circle = root.create_circle_batch(max_shapes=300)
        self._batch_circle.clear()
        GX0, GY0 = COLS[0]+30, ROWS[0]+42
        COLS6, ROWS5 = 6, 5
        for r in range(ROWS5):
            for c in range(COLS6):
                self._batch_circle.add_circle(
                    V2(GX0 + c*38, GY0 + r*35),
                    radius=14.0,
                    color=(c/5, r/4, 0.8, 1.0),
                    border_color=(1,1,1,0.3), border_width=1.5,
                    antialiasing=1.2,
                )
        self._batch_circle.flush()

        # ── 6B circle numpy (6×6) ─────────────────────────────────────────────
        _box(1, 0)
        _subhead(root, "circle_batch + add_circles_numpy  (6×6)", COLS[1]+8, ROWS[1-1]+8)
        if self._batch_circle_np is None:
            self._batch_circle_np = root.create_circle_batch(max_shapes=500)
        self._batch_circle_np.clear()
        N  = 36
        gx, gy = np.meshgrid(np.linspace(COLS[1]+22, COLS[1]+COL_W-50, 6),
                              np.linspace(ROWS[0]+42,  ROWS[0]+COL_H-40,  6))
        cntrs = np.stack([gx.ravel(), gy.ravel()], axis=1).astype('f4')
        rads  = np.full(N, 14.0, dtype='f4')
        cols  = np.zeros((N,4), dtype='f4')
        cols[:,0] = np.linspace(0,1,N)
        cols[:,1] = np.linspace(1,0,N)
        cols[:,2] = 0.7
        cols[:,3] = 1.0
        self._batch_circle_np.add_circles_numpy(
            cntrs, rads, cols,
            border_colors=np.tile([1,1,1,0.4],(N,1)).astype('f4'),
            border_widths=np.full(N,1.5,dtype='f4'),
            antialiasing=1.2,
        )
        self._batch_circle_np.flush()

        # ── 6C rect manual (4×5) ──────────────────────────────────────────────
        _box(2, 0)
        _subhead(root, "rect_batch + add_rect  (4×5 varied rotation)", COLS[2]+8, ROWS[0]+8)
        if self._batch_rect is None:
            self._batch_rect = root.create_rect_batch(max_shapes=200)
        self._batch_rect.clear()
        for r in range(5):
            for c in range(4):
                self._batch_rect.add_rect(
                    V2(COLS[2]+40 + c*55, ROWS[0]+42 + r*38),
                    size=V2(38, 28),
                    color=(c/3, 0.4, r/4, 1.0),
                    corner_radius=5.0,
                    border_color=(1,1,1,0.25), border_width=1.2,
                    antialiasing=1.2,
                    rotation=c*0.4 + r*0.25,
                )
        self._batch_rect.flush()

        # ── 6D rect numpy (4×4) ───────────────────────────────────────────────
        _box(0, 1)
        _subhead(root, "rect_batch + add_rects_numpy  (4×4 rot 0→π)", COLS[0]+8, ROWS[1]+8)
        if self._batch_rect_np is None:
            self._batch_rect_np = root.create_rect_batch(max_shapes=500)
        self._batch_rect_np.clear()
        Nr   = 16
        rgx, rgy = np.meshgrid(np.linspace(COLS[0]+30, COLS[0]+COL_W-60, 4),
                                np.linspace(ROWS[1]+42, ROWS[1]+COL_H-40, 4))
        rc   = np.stack([rgx.ravel(), rgy.ravel()], axis=1).astype('f4')
        rs   = np.tile([34.0, 26.0], (Nr,1)).astype('f4')
        rcol = np.zeros((Nr,4), dtype='f4')
        rcol[:,0] = np.linspace(0.1,1.0,Nr)
        rcol[:,1] = 0.5
        rcol[:,2] = np.linspace(1.0,0.1,Nr)
        rcol[:,3] = 1.0
        self._batch_rect_np.add_rects_numpy(
            rc, rs, rcol,
            corner_radii=np.full(Nr, 6.0, dtype='f4'),
            border_colors=np.tile([1,1,1,0.3],(Nr,1)).astype('f4'),
            border_widths=np.full(Nr, 1.5, dtype='f4'),
            antialiasing=1.5,
            rotations=np.linspace(0, math.pi, Nr, dtype='f4'),
        )
        self._batch_rect_np.flush()

        # ── 6E line batch manual fan ──────────────────────────────────────────
        _box(1, 1)
        _subhead(root, "line_batch + add_line  (20-spoke fan)", COLS[1]+8, ROWS[1]+8)
        if self._batch_line is None:
            self._batch_line = root.create_line_batch(max_shapes=200)
        self._batch_line.clear()
        FCX = COLS[1] + COL_W//2 - 3
        FCY = ROWS[1] + COL_H//2
        for i in range(20):
            ang = math.pi * 2 * i / 20
            self._batch_line.add_line(
                V2(FCX, FCY),
                V2(FCX + 120*math.cos(ang), FCY + 120*math.sin(ang)),
                width=3.5,
                color=(math.sin(ang)*0.5+0.5, math.cos(ang)*0.5+0.5, 0.9, 1.0),
            )
        self._batch_line.flush()

        # ── 6F line batch numpy ───────────────────────────────────────────────
        _box(2, 1)
        _subhead(root, "line_batch + add_lines_numpy  (14 lines varied w+color)", COLS[2]+8, ROWS[1]+8)
        if self._batch_line_np is None:
            self._batch_line_np = root.create_line_batch(max_shapes=500)
        self._batch_line_np.clear()
        Nl   = 14
        ys   = np.linspace(ROWS[1]+45, ROWS[1]+COL_H-35, Nl, dtype='f4')
        x0   = np.full(Nl, COLS[2]+22.0, dtype='f4')
        x1   = np.full(Nl, COLS[2]+float(COL_W)-32, dtype='f4')
        stts = np.stack([x0, ys], axis=1)
        ends = np.stack([x1, ys], axis=1)
        wids = np.linspace(1.5, 14.0, Nl, dtype='f4')
        lc   = np.zeros((Nl,4), dtype='f4')
        lc[:,0] = np.linspace(1,0,Nl)
        lc[:,1] = np.linspace(0,1,Nl)
        lc[:,2] = 0.7
        lc[:,3] = 1.0
        self._batch_line_np.add_lines_numpy(stts, ends, wids, lc)
        self._batch_line_np.flush()

    # =========================================================================
    # PAGE 7 — LAYERS
    # =========================================================================
    def _page_layers(self, t: float = 0.0) -> None:
        root = self.root
        _heading(root, "layer= parameter — controls draw order regardless of call order")

        # Column layout: 4 demos side by side
        DEMO_W  = (CANVAS_W - 60) // 4
        DEMO_H  = int(CANVAS_H * 0.70)
        DEMO_Y  = CANVAS_Y + 52
        DEMO_XS = [CANVAS_X + 20 + i * (DEMO_W + 16) for i in range(4)]

        def _dbox(x, y, w, h):
            root.draw_rect(V2(x, y), V2(w, h),
                           color=Color(0.07,0.07,0.12), corner_radius=10.0,
                           border_color=Color(0.22,0.22,0.40), border_width=1.0,
                           layer=-1)

        # ── Demo 1: overlapping circles, issued out-of-order ─────────────────
        dx = DEMO_XS[0]
        _dbox(dx, DEMO_Y, DEMO_W, DEMO_H)
        _subhead(root, "Circles  (issued B→R→G)", dx+8, DEMO_Y+8)
        _lab(root,
             "Issued call order:\n"
             "  blue  (layer=2)  ← 1st call\n"
             "  red   (layer=0)  ← 2nd call\n"
             "  green (layer=1)  ← 3rd call\n\n"
             "Rendered order:\n"
             "  red(0) → green(1) → blue(2)",
             dx+12, DEMO_Y+36)
        cy = DEMO_Y + DEMO_H//2 + 30
        root.draw_circle(V2(dx+DEMO_W//2+35, cy), 55, color=BLUE,  layer=2)
        root.draw_circle(V2(dx+DEMO_W//2-35, cy), 55, color=RED,   layer=0)
        root.draw_circle(V2(dx+DEMO_W//2,    cy), 55, color=GREEN, layer=1)

        # ── Demo 2: overlapping rects ─────────────────────────────────────────
        dx = DEMO_XS[1]
        _dbox(dx, DEMO_Y, DEMO_W, DEMO_H)
        _subhead(root, "Rects  (issued Y→M→C)", dx+8, DEMO_Y+8)
        _lab(root,
             "Issued:\n"
             "  yellow  (layer=3)\n"
             "  magenta (layer=1)\n"
             "  cyan    (layer=2)\n\n"
             "Rendered:\n"
             "  magenta(1)→cyan(2)\n"
             "  →yellow(3)",
             dx+12, DEMO_Y+36)
        ry = DEMO_Y + DEMO_H//2 + 20
        root.draw_rect(V2(dx+DEMO_W//2+20, ry-35), V2(90,90), color=YELLOW,  layer=3)
        root.draw_rect(V2(dx+DEMO_W//2-50, ry-35), V2(90,90), color=MAGENTA, layer=1)
        root.draw_rect(V2(dx+DEMO_W//2-15, ry-35), V2(90,90), color=CYAN,    layer=2)

        # ── Demo 3: line sandwiched between circles ───────────────────────────
        dx = DEMO_XS[2]
        _dbox(dx, DEMO_Y, DEMO_W, DEMO_H)
        _subhead(root, "Line between 2 circles", dx+8, DEMO_Y+8)
        _lab(root,
             "orange circle  (layer=0)\n"
             "white line     (layer=1)\n"
             "purple circle  (layer=2)\n\n"
             "Line is visually between\n"
             "the two circles.",
             dx+12, DEMO_Y+36)
        ly  = DEMO_Y + DEMO_H//2 + 50
        lx0 = dx + DEMO_W//2 - 70
        root.draw_circle(V2(lx0,       ly), 44, color=ORANGE, layer=0)
        root.draw_line(  V2(lx0-20,    ly), V2(lx0+160, ly), width=10.0, color=WHITE, layer=1)
        root.draw_circle(V2(lx0+140,   ly), 44, color=PURPLE, layer=2)

        # ── Demo 4: mixed shapes, 5 layers ────────────────────────────────────
        dx = DEMO_XS[3]
        _dbox(dx, DEMO_Y, DEMO_W, DEMO_H)
        _subhead(root, "Mixed — 5 layers", dx+8, DEMO_Y+8)
        _lab(root,
             "blue rect     (layer=0)\n"
             "cyan line     (layer=1)\n"
             "yellow circle (layer=2)\n"
             "red rect      (layer=3)\n"
             "white circle  (layer=4)\n\n"
             "Also: gradient rect\n"
             "(layer=0) under\n"
             "a circle (layer=1).",
             dx+12, DEMO_Y+36)
        my  = DEMO_Y + DEMO_H//2 + 30
        mx  = dx + DEMO_W//2
        root.draw_rect(  V2(mx-55, my-50), V2(110,100), color=(0.2,0.2,0.9,1), layer=0)
        root.draw_line(  V2(mx-65, my),    V2(mx+65, my), width=8.0, color=CYAN, layer=1)
        root.draw_circle(V2(mx,    my),    40, color=(0.9,0.9,0.1,1), layer=2)
        root.draw_rect(  V2(mx-40, my-30), V2(80,60), color=(0.8,0.1,0.2,0.75),
                         corner_radius=8.0, layer=3)
        root.draw_circle(V2(mx,    my),    18, color=(1,1,1,0.95), layer=4)

        # Gradient + circle below
        gby = DEMO_Y + DEMO_H + 20
        root.draw_rect_gradient(
            V2(dx+8, gby), V2(DEMO_W-16, 68),
            LinearGradient([(Color(0.1,0.5,0.9),0),(Color(0.9,0.3,0.1),1)], angle=math.pi/3),
            layer=0,
        )
        root.draw_circle(V2(dx+DEMO_W//2, gby+34), 26, color=(0.2,1,0.5,0.85),
                         border_color=WHITE, border_width=3.0, layer=1)
        _lab(root, "gradient(l=0) under circle(l=1)", dx+8, gby+72)


# =============================================================================
# Entry point
# =============================================================================

def main() -> None:
    config = WindowConfig(
        size=(1920, 1080),
        title="e2D ShapeRenderer — Full Feature Showcase",
        target_fps=60,
        vsync=False,
    )
    root = RootEnv(config=config)
    env  = ShapesFullShowcase(root)
    root.init(env)
    root.loop()


if __name__ == "__main__":
    main()
