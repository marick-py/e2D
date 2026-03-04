"""
example_containers.py — Phase 4 Containers & Layout demo.

Demonstrates every Phase 4 container type:

  Panel 1 ─ VBox       vertical stack, four align modes
  Panel 2 ─ HBox       horizontal stack, three align modes
  Panel 3 ─ Grid       rows×columns cell layout
  Panel 4 ─ ScrollContainer  scrollable list with 30 items
  Panel 5 ─ SizeMode   FIXED / PERCENT / AUTO comparison
  Panel 6 ─ FreeContainer    relative & anchor-based children
  Panel 7 ─ Widgets    buttons, sliders, toggle, inputs inside VBoxes

Controls:
  1–7 / click sidebar buttons  — switch panel
  T                            — cycle theme
  F3                           — toggle debug outlines
"""

from __future__ import annotations
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import glfw

from e2D import (
    Button, RootEnv, DefEnv, V2, UIManager, WindowConfig,
    Keys, KeyState, TextStyle,
    WHITE, YELLOW, CYAN, GREEN,
)
from e2D.colors import Color
from e2D.ui import (
    VBox, HBox, Grid, FreeContainer, ScrollContainer,
    SizeMode, Anchor,
)
from e2D.ui.theme import (
    MONOKAI_THEME, DARK_THEME, LIGHT_THEME,
    SOLARIZED_DARK, SOLARIZED_LIGHT,
    NORD_THEME, DRACULA_THEME,
    TOKYO_NIGHT_THEME, HIGH_CONTRAST,
)
from e2D._pivot import Pivot

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

WIN_W   = 1100
WIN_H   = 700
SIDE_W  = 220       # sidebar width
HEADER  = 50        # top bar height
PANEL_X = SIDE_W
PANEL_Y = HEADER
PANEL_W = WIN_W - SIDE_W
PANEL_H = WIN_H - HEADER

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

_GREY     = Color(0.45, 0.45, 0.45)
_DGREY    = Color(0.25, 0.25, 0.30)
_CELL_BG  = [
    Color(0.70, 0.25, 0.25, 0.85),
    Color(0.25, 0.60, 0.30, 0.85),
    Color(0.25, 0.35, 0.72, 0.85),
    Color(0.70, 0.55, 0.15, 0.85),
    Color(0.55, 0.25, 0.70, 0.85),
    Color(0.20, 0.60, 0.65, 0.85),
    Color(0.75, 0.40, 0.20, 0.85),
    Color(0.35, 0.65, 0.55, 0.85),
    Color(0.60, 0.30, 0.50, 0.85),
    Color(0.45, 0.55, 0.20, 0.85),
    Color(0.25, 0.45, 0.70, 0.85),
    Color(0.65, 0.25, 0.40, 0.85),
]


def sty(size: int, color=None) -> TextStyle:
    return TextStyle(font_size=size, color=color or WHITE)


def panel_bg() -> Color:
    return Color(0.06, 0.06, 0.10, 1.0)


def section_bg() -> Color:
    return Color(0.10, 0.10, 0.15, 1.0)


def header_bg() -> Color:
    return Color(0.13, 0.13, 0.22, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Example class
# ─────────────────────────────────────────────────────────────────────────────

class ContainersExample(DefEnv):
    """Phase 4 containers demo."""

    def __init__(self, root: RootEnv) -> None:
        self.root = root
        self._theme_idx = 0
        self._last_win_size = (WIN_W, WIN_H)
        root.ui.theme = _THEMES[0][1]

        ui = root.ui

        # ── build the UI ────────────────────────────────────────────────
        self._panels: list[FreeContainer] = []
        self._nav_btns: list[Button] = []
        self._cur_panel = 0

        self._build_top_bar(ui)
        self._build_sidebar(ui)

        # Create all panels (only panel 0 visible initially)
        self._panels.append(self._build_panel_vbox(ui))
        self._panels.append(self._build_panel_hbox(ui))
        self._panels.append(self._build_panel_grid(ui))
        self._panels.append(self._build_panel_scroll(ui))
        self._panels.append(self._build_panel_sizemode(ui))
        self._panels.append(self._build_panel_free(ui))
        self._panels.append(self._build_panel_widgets(ui))

        self._show_panel(0)

    # ── top bar ──────────────────────────────────────────────────────────

    def _build_top_bar(self, ui) -> None:
        bar = ui.hbox(
            spacing=0, align='center',
            position=V2(0, 0), size=V2(WIN_W, HEADER),
            anchor_min=(0.0, 0.0), anchor_max=(1.0, 0.0),
            margin=(0.0, 0.0, float(-HEADER), 0.0),
            bg_color=Color(0.04, 0.04, 0.08, 1.0),
            border_color=Color(0.18, 0.18, 0.30, 1.0),
            border_width=1.0,
            padding=10,
        )
        # Title fills left portion; hints fill right
        title = ui.label(
            "Phase 4 — Containers & Layout",
            position=V2(0, 0),
            default_style=sty(20, WHITE),
        )
        hints = ui.label(
            "  1–7 = panel   T = theme   F3 = debug",
            position=V2(0, 0),
            default_style=sty(12, _GREY),
        )
        bar.add_child(title)
        bar.add_child(hints)

    # ── sidebar ──────────────────────────────────────────────────────────

    _NAV_LABELS = [
        "1 · VBox",
        "2 · HBox",
        "3 · Grid",
        "4 · Scroll",
        "5 · SizeMode",
        "6 · FreeContainer",
        "7 · Widgets",
    ]

    def _build_sidebar(self, ui) -> None:
        sidebar = ui.vbox(
            spacing=4,
            position=V2(0, HEADER), size=V2(SIDE_W, WIN_H - HEADER),
            bg_color=Color(0.05, 0.05, 0.09, 1.0),
            border_color=Color(0.18, 0.18, 0.30, 1.0),
            border_width=1.0,
            padding=10,
        )
        self._sidebar = sidebar
        for i, label in enumerate(self._NAV_LABELS):
            idx = i
            btn = ui.button(
                label,
                on_click=lambda n=idx: self._show_panel(n),
                size=V2(196, 36),
            )
            sidebar.add_child(btn)
            self._nav_btns.append(btn)

        # Spacer label
        spacer = ui.label("", position=V2(0, 0), default_style=sty(8))
        sidebar.add_child(spacer)

        # Info text
        info_lines = [
            "Press F3 to toggle",
            "debug outlines on",
            "any panel.",
            "",
            "Hover an element",
            "to see its info",
            "in the debug panel.",
        ]
        for line in info_lines:
            lbl = ui.label(line, position=V2(0, 0), default_style=sty(11, _GREY))
            sidebar.add_child(lbl)

    # ── panel helpers ─────────────────────────────────────────────────────

    def _make_panel(self, ui) -> FreeContainer:
        p = ui.free_container(
            position=V2(PANEL_X, PANEL_Y),
            size=V2(PANEL_W, PANEL_H),
            anchor_min=(0.0, 0.0), anchor_max=(1.0, 1.0),
            margin=(float(HEADER), 0.0, 0.0, float(SIDE_W)),
            bg_color=panel_bg(),
            visible=False,
        )
        return p

    def _section_header(self, ui, panel: FreeContainer,
                         x: float, y: float, w: float,
                         text: str) -> None:
        hdr = ui.hbox(
            spacing=0, align='center',
            position=V2(x, y), size=V2(w, 28),
            bg_color=header_bg(),
            corner_radius=4.0,
            padding=0,
        )
        lbl = ui.label(text, position=V2(8, 0), default_style=sty(13, YELLOW))
        hdr.add_child(lbl)
        panel.add_child(hdr)

    # ── Panel 0: VBox ─────────────────────────────────────────────────────

    def _build_panel_vbox(self, ui) -> FreeContainer:
        p = self._make_panel(ui)

        title = ui.label("", default_style=sty(16, CYAN))
        title.set_plain_text("VBox — vertical stack with different align modes")
        p.add_child(title)
        p._child_offsets[id(title)] = (14.0, 10.0)
        p._compute_layout()

        align_modes = ['left', 'center', 'right', 'stretch']
        box_colors  = [
            Color(0.12, 0.12, 0.20, 0.9),
            Color(0.12, 0.20, 0.12, 0.9),
            Color(0.20, 0.12, 0.12, 0.9),
            Color(0.20, 0.15, 0.08, 0.9),
        ]
        btn_widths  = [80, 140, 100, 200]   # varying widths to see alignment
        btn_cols    = [YELLOW, GREEN, CYAN, Color(1.0, 0.5, 0.1)]

        col_w  = (PANEL_W - 48) // 4
        col_y  = 46

        for ci, align in enumerate(align_modes):
            col_x = 12 + ci * (col_w + 4)

            # Section label
            albl = ui.label("", default_style=sty(11, _GREY))
            albl.set_plain_text(f"align='{align}'")
            p.add_child(albl)
            p._child_offsets[id(albl)] = (float(col_x), float(col_y))

            vb = VBox(
                spacing=6, align=align,
                position=V2(0, 0),
                size=V2(col_w, 220),
                bg_color=box_colors[ci],
                border_color=Color(0.30, 0.30, 0.50, 0.7),
                border_width=1.0,
                corner_radius=5.0,
                padding=8,
            )
            for bi in range(4):
                w = btn_widths[bi % len(btn_widths)]
                btn = ui.button(f"Item {bi+1}", size=V2(w, 30))
                btn._ov_color_normal = box_colors[ci].darken(0.4)
                vb.add_child(btn)

            p.add_child(vb)
            p._child_offsets[id(vb)] = (float(col_x), float(col_y + 20))

        # re-layout after repositioning
        p._compute_layout()

        # Explanation labels below the boxes
        note_y = 280 + col_y + 20
        notes = [
            "VBox places children top-to-bottom.",
            "Use  spacing=N  for a pixel gap between items.",
            "align='stretch'  makes every child fill the container width.",
            "Set  size_mode = SizeMode.AUTO  on a VBox to auto-size its height.",
        ]
        for ni, n in enumerate(notes):
            nlbl = ui.label("", default_style=sty(12, _GREY))
            nlbl.set_plain_text(f"• {n}")
            p.add_child(nlbl)
            p._child_offsets[id(nlbl)] = (14.0, float(note_y + ni * 20))
        p._compute_layout()
        return p

    # ── Panel 1: HBox ─────────────────────────────────────────────────────

    def _build_panel_hbox(self, ui) -> FreeContainer:
        p = self._make_panel(ui)

        title = ui.label("", default_style=sty(16, CYAN))
        title.set_plain_text("HBox — horizontal stack with different align modes")
        p.add_child(title)
        p._child_offsets[id(title)] = (14.0, 10.0)

        align_modes = ['top', 'center', 'bottom', 'stretch']
        box_colors  = [
            Color(0.12, 0.16, 0.25, 0.9),
            Color(0.12, 0.22, 0.18, 0.9),
            Color(0.22, 0.12, 0.15, 0.9),
            Color(0.20, 0.18, 0.10, 0.9),
        ]
        btn_heights = [24, 44, 36, 28]

        row_h = (PANEL_H - 140) // 4
        row_x = 12

        for ri, align in enumerate(align_modes):
            row_y = 46 + ri * (row_h + 6)

            albl = ui.label("", default_style=sty(11, _GREY))
            albl.set_plain_text(f"align='{align}'")
            p.add_child(albl)
            p._child_offsets[id(albl)] = (float(row_x), float(row_y))

            hb = HBox(
                spacing=6, align=align,
                position=V2(0, 0),
                size=V2(PANEL_W - 28, row_h - 20),
                bg_color=box_colors[ri],
                border_color=Color(0.30, 0.30, 0.50, 0.7),
                border_width=1.0,
                corner_radius=5.0,
                padding=6,
            )
            for bi in range(5):
                h = btn_heights[bi % len(btn_heights)]
                btn = ui.button(f"Btn {bi+1}", size=V2(90, h))
                hb.add_child(btn)

            p.add_child(hb)
            p._child_offsets[id(hb)] = (float(row_x), float(row_y + 18))

        p._compute_layout()

        notes = [
            "HBox places children left-to-right.",
            "align='stretch'  makes every child fill the container height.",
        ]
        note_y = 46 + 4 * (row_h + 6) + 6
        for ni, n in enumerate(notes):
            nlbl = ui.label("", default_style=sty(12, _GREY))
            nlbl.set_plain_text(f"• {n}")
            p.add_child(nlbl)
            p._child_offsets[id(nlbl)] = (14.0, float(note_y + ni * 18))
        p._compute_layout()
        return p

    # ── Panel 2: Grid ─────────────────────────────────────────────────────

    def _build_panel_grid(self, ui) -> FreeContainer:
        p = self._make_panel(ui)

        title = ui.label("", default_style=sty(16, CYAN))
        title.set_plain_text("Grid — rows × columns cell layout")
        p.add_child(title)
        p._child_offsets[id(title)] = (14.0, 10.0)

        configs = [
            (3, "3 columns, equal cells, gap=(4,4)"),
            (4, "4 columns, equal cells, gap=(6,6)"),
            (2, "2 columns, equal cells, gap=(8,8)"),
        ]
        n_items = 12
        grid_y  = 40
        grid_h  = 148   # 3*(148+28) = 528 ≤ PANEL_H-100 → no overflow

        for gi, (cols, desc) in enumerate(configs):
            gx = 14
            gy = grid_y + gi * (grid_h + 28)

            desc_lbl = ui.label("", default_style=sty(11, _GREY))
            desc_lbl.set_plain_text(desc)
            p.add_child(desc_lbl)
            p._child_offsets[id(desc_lbl)] = (float(gx), float(gy))

            gap = float(4 + gi * 2)
            gd = Grid(
                columns=cols,
                cell_spacing=(gap, gap),
                position=V2(0, 0),
                size=V2(PANEL_W - 28, grid_h),
                bg_color=Color(0.10, 0.10, 0.18, 0.9),
                border_color=Color(0.25, 0.25, 0.45, 0.7),
                border_width=1.0,
                corner_radius=5.0,
                padding=8,
            )
            for ci in range(n_items):
                c = _CELL_BG[ci % len(_CELL_BG)]
                btn = ui.button(
                    f"#{ci+1}",
                    size=V2(60, 40),
                    color_normal=c,
                    color_hover=c.lighten(0.25),
                    color_pressed=c.darken(0.2),
                )
                gd.add_child(btn)

            p.add_child(gd)
            p._child_offsets[id(gd)] = (float(gx), float(gy + 18))

        p._compute_layout()

        notes_y = grid_y + 3 * (grid_h + 28) + 4
        notes   = [
            "Grid fills the container; each cell gets an equal share of space.",
            "Pass cell_size=(w,h) to use fixed-size cells instead.",
        ]
        for ni, n in enumerate(notes):
            nlbl = ui.label("", default_style=sty(12, _GREY))
            nlbl.set_plain_text(f"• {n}")
            p.add_child(nlbl)
            p._child_offsets[id(nlbl)] = (14.0, float(notes_y + ni * 18))
        p._compute_layout()
        return p

    # ── Panel 3: ScrollContainer ─────────────────────────────────────────

    def _build_panel_scroll(self, ui: UIManager) -> FreeContainer:
        p = self._make_panel(ui)

        title = ui.label("", default_style=sty(16, CYAN))
        title.set_plain_text("ScrollContainer — scrollable single-child wrapper")
        p.add_child(title)
        p._child_offsets[id(title)] = (14.0, 10.0)

        info = ui.label("", default_style=sty(12, _GREY))
        info.set_plain_text("Scroll with the mouse wheel or drag the thumb. "
                            "Click an item to see its name below.")
        p.add_child(info)
        p._child_offsets[id(info)] = (14.0, 34.0)

        # ScrollContainer on the left
        sc = ScrollContainer(
            scroll_vertical=True,
            show_scrollbar=True,
            scroll_speed=36,
            position=V2(0, 0),
            size=V2(380, PANEL_H - 110),
            bg_color=Color(0.08, 0.08, 0.14, 1.0),
            border_color=Color(0.25, 0.25, 0.45, 0.8),
            border_width=1.0,
            corner_radius=6.0,
            padding=6,
        )
        sc.size_mode = SizeMode.FIXED

        # Content VBox (AUTO height — adjusts to items)
        content = VBox(spacing=3, position=V2(0, 0), size=V2(354, 0))
        content.size_mode = SizeMode.AUTO

        self._scroll_clicked_lbl: object | None = None  # assigned below

        for i in range(30):
            fi = i
            c = _CELL_BG[i % len(_CELL_BG)]
            btn = ui.button(
                f"  Item {i+1:02d}  — click me",
                size=V2(350, 34),
                color_normal=c.darken(0.35),
                color_hover=c.lighten(0.15),
                on_click=lambda n=fi: self._on_scroll_item(n + 1),
            )
            content.add_child(btn)

        sc.add_child(content)
        p.add_child(sc)
        p._child_offsets[id(sc)] = (14.0, 56.0)

        # Right info panel
        info2 = ui.label("", default_style=sty(13, _GREY))
        info2.set_plain_text("Last clicked:")
        p.add_child(info2)
        p._child_offsets[id(info2)] = (420.0, 56.0)

        self._scroll_result_lbl = ui.label("", default_style=sty(18, YELLOW))
        self._scroll_result_lbl.set_plain_text("—")
        p.add_child(self._scroll_result_lbl)
        p._child_offsets[id(self._scroll_result_lbl)] = (420.0, 78.0)

        note_texts = [
            "• ScrollContainer wraps one child.",
            "• The child is usually a VBox/HBox with",
            "  size_mode = SizeMode.AUTO.",
            "• Scroll bubbles up from children,",
            "  so hovering any item scrolls the list.",
            "• Drag the scrollbar thumb to scroll.",
            "• Set scroll_speed to adjust sensitivity.",
        ]
        for ni, nt in enumerate(note_texts):
            nlbl = ui.label("", default_style=sty(12, _GREY))
            nlbl.set_plain_text(nt)
            p.add_child(nlbl)
            p._child_offsets[id(nlbl)] = (420.0, float(130 + ni * 20))

        p._compute_layout()
        return p

    def _on_scroll_item(self, n: int) -> None:
        self._scroll_result_lbl.set_plain_text(f"Item {n}")  # type: ignore[union-attr]

    # ── Panel 4: SizeMode ────────────────────────────────────────────────

    def _build_panel_sizemode(self, ui: UIManager) -> FreeContainer:
        p = self._make_panel(ui)

        title = ui.label("", default_style=sty(16, CYAN))
        title.set_plain_text("SizeMode — FIXED · PERCENT · AUTO")
        p.add_child(title)
        p._child_offsets[id(title)] = (14.0, 10.0)

        # ── FIXED ────────────────────────────────────────────
        def _sec(text: str, y: float) -> None:
            lb = ui.label("", default_style=sty(14, YELLOW))
            lb.set_plain_text(text)
            p.add_child(lb)
            p._child_offsets[id(lb)] = (14.0, y)

        def _note(text: str, y: float) -> None:
            lb = ui.label("", default_style=sty(11, _GREY))
            lb.set_plain_text(text)
            p.add_child(lb)
            p._child_offsets[id(lb)] = (14.0, y)

        _sec("SizeMode.FIXED  (default — size in pixels)", 44.0)
        _note("Each button has an explicit size=V2(w, h) and never changes.", 64.0)

        hb_fixed = HBox(
            spacing=8, align='center',
            position=V2(0, 0), size=V2(PANEL_W - 28, 50),
            bg_color=section_bg(),
            padding=8,
        )
        for lbl, w in [("Small 80px", 80), ("Medium 160px", 160), ("Large 240px", 240)]:
            btn = ui.button(lbl, size=V2(w, 34))
            hb_fixed.add_child(btn)
        p.add_child(hb_fixed)
        p._child_offsets[id(hb_fixed)] = (14.0, 82.0)

        # ── PERCENT ──────────────────────────────────────────
        _sec("SizeMode.PERCENT  (size as fraction 0–1 of parent inner width)", 148.0)
        _note("btn.size_mode = SizeMode.PERCENT; btn.size = V2(0.33, 1.0)  → 33% wide, 100% tall.", 168.0)

        hb_pct = HBox(
            spacing=4, align='stretch',
            position=V2(0, 0), size=V2(PANEL_W - 28, 50),
            bg_color=section_bg(),
            padding=8,
        )
        pct_labels = [("20%", 0.20), ("30%", 0.30), ("50%", 0.50)]
        for lbl, frac in pct_labels:
            btn = ui.button(lbl, size=V2(frac, 1.0))
            btn.size_mode = SizeMode.PERCENT
            hb_pct.add_child(btn)
        p.add_child(hb_pct)
        p._child_offsets[id(hb_pct)] = (14.0, 186.0)

        # ── AUTO ─────────────────────────────────────────────
        _sec("SizeMode.AUTO  (VBox/HBox sizes itself to fit content)", 252.0)
        _note("vbox.size_mode = SizeMode.AUTO  → its height = sum of children + spacing + padding.", 272.0)

        outer = HBox(
            spacing=12, align='top',
            position=V2(0, 0), size=V2(PANEL_W - 28, 260),
            bg_color=section_bg(),
            padding=10,
        )

        for n_items, label_color in [(2, YELLOW), (4, CYAN), (6, GREEN)]:
            vb = VBox(
                spacing=6, align='stretch',
                position=V2(0, 0),
                size=V2(220, 0),
                bg_color=Color(0.12, 0.12, 0.22, 0.9),
                border_color=Color(0.30, 0.30, 0.55, 0.7),
                border_width=1.0,
                corner_radius=4.0,
                padding=6,
            )
            vb.size_mode = SizeMode.AUTO
            cap = ui.label("", default_style=sty(11, label_color))
            cap.set_plain_text(f"AUTO · {n_items} items")
            vb.add_child(cap)
            for i in range(n_items):
                btn = ui.button(f"Item {i+1}", size=V2(200, 28))
                vb.add_child(btn)
            outer.add_child(vb)

        p.add_child(outer)
        p._child_offsets[id(outer)] = (14.0, 290.0)

        p._compute_layout()
        return p

    # ── Panel 5: FreeContainer ───────────────────────────────────────────

    def _build_panel_free(self, ui: UIManager) -> FreeContainer:
        p = self._make_panel(ui)

        title = ui.label("", default_style=sty(16, CYAN))
        title.set_plain_text("FreeContainer — relative & anchor-based child layout")
        p.add_child(title)
        p._child_offsets[id(title)] = (14.0, 10.0)

        # Left: relative positioning demo
        lsec = ui.label("", default_style=sty(14, YELLOW))
        lsec.set_plain_text("Relative positioning  (position = offset from panel top-left)")
        p.add_child(lsec)
        p._child_offsets[id(lsec)] = (14.0, 38.0)

        free1 = FreeContainer(
            position=V2(0, 0),
            size=V2(410, 240),
            bg_color=section_bg(),
            border_color=Color(0.25, 0.25, 0.45, 0.7),
            border_width=1.0,
            corner_radius=6.0,
            padding=0,
        )
        p.add_child(free1)
        p._child_offsets[id(free1)] = (14.0, 60.0)

        # Add children at relative positions inside free1
        positions_and_labels = [
            (V2(10,  10), "pos=(10, 10)",  YELLOW),
            (V2(200, 10), "pos=(200, 10)", CYAN),
            (V2(10, 140), "pos=(10, 140)", GREEN),
            (V2(200,140), "pos=(200,140)", Color(1.0, 0.5, 0.2)),
        ]
        for pos, text, col in positions_and_labels:
            btn = ui.button(text, size=V2(170, 32), position=pos)
            btn._ov_color_normal = col.darken(0.5)
            free1.add_child(btn)
        # Center label
        clbl = ui.label("", default_style=sty(11, _GREY), position=V2(100, 90))
        clbl.set_plain_text("Each button's position is relative")
        free1.add_child(clbl)
        clbl2 = ui.label("", default_style=sty(11, _GREY), position=V2(120, 110))
        clbl2.set_plain_text("to the FreeContainer's top-left.")
        free1.add_child(clbl2)

        p._compute_layout()

        # Right: Interactive anchor presets demo
        rsec = ui.label("", default_style=sty(14, YELLOW))
        rsec.set_plain_text("Anchor presets  (click a preset to apply it to the demo box)")
        p.add_child(rsec)
        p._child_offsets[id(rsec)] = (450.0, 38.0)

        free2 = FreeContainer(
            position=V2(0, 0),
            size=V2(416, 460),
            bg_color=section_bg(),
            border_color=Color(0.25, 0.25, 0.45, 0.7),
            border_width=1.0,
            corner_radius=6.0,
            padding=0,
        )
        p.add_child(free2)
        p._child_offsets[id(free2)] = (450.0, 60.0)

        # ── Preset buttons (left strip) ──
        _PRESETS = [
            ("FULL_RECT",    Anchor.FULL_RECT),
            ("CENTER",       Anchor.CENTER),
            ("TOP_LEFT",     Anchor.TOP_LEFT),
            ("TOP_RIGHT",    Anchor.TOP_RIGHT),
            ("BOTTOM_LEFT",  Anchor.BOTTOM_LEFT),
            ("BOTTOM_RIGHT", Anchor.BOTTOM_RIGHT),
            ("LEFT_WIDE",    Anchor.LEFT_WIDE),
            ("RIGHT_WIDE",   Anchor.RIGHT_WIDE),
            ("TOP_WIDE",     Anchor.TOP_WIDE),
            ("HCENTER_WIDE", Anchor.HCENTER_WIDE),
            ("BOTTOM_WIDE",  Anchor.BOTTOM_WIDE),
            ("VCENTER_WIDE", Anchor.VCENTER_WIDE),
        ]
        preset_vb = VBox(spacing=4, align='stretch',
                         size=V2(128, 0), size_mode=SizeMode.AUTO,
                         bg_color=Color(0, 0, 0, 0))
        free2.add_child(preset_vb)
        free2._child_offsets[id(preset_vb)] = (6.0, 6.0)

        # ── Demo area (right side) ──
        self._anchor_inner = FreeContainer(
            size=V2(268, 370),
            bg_color=Color(0.10, 0.10, 0.20, 0.9),
            border_color=Color(0.25, 0.25, 0.50, 0.8),
            border_width=1.0,
            padding=6,
        )
        free2.add_child(self._anchor_inner)
        free2._child_offsets[id(self._anchor_inner)] = (142.0, 6.0)

        # Demo button: auto-sized from text + padding — no hardcoded dimensions.
        # Its _size is updated automatically by Button.text.setter whenever the
        # preset callback changes the label, so natural_size() is always current.
        self._anchor_demo_btn = ui.button("FULL_RECT")
        self._anchor_demo_btn._ov_color_normal = Color(0.18, 0.14, 0.35, 0.8)
        self._anchor_demo_btn.anchor_min, self._anchor_demo_btn.anchor_max = Anchor.FULL_RECT
        self._anchor_inner.add_child(self._anchor_demo_btn)

        # Current anchor label under demo area
        self._anchor_lbl = ui.label("", default_style=sty(11, CYAN))
        self._anchor_lbl.set_plain_text("Current: FULL_RECT  (min=(0,0)  max=(1,1))")
        free2.add_child(self._anchor_lbl)
        free2._child_offsets[id(self._anchor_lbl)] = (142.0, 384.0)

        # ── Helper: compute margin tuple from natural button size ──
        # Point-anchor axes keep _size; a negative margin offsets the element
        # back so it visually aligns to the named edge / corner / center.
        def _margins_for(n: str, dw: float, dh: float) -> tuple:
            return {
                "FULL_RECT":    (0.0,     0.0, 0.0,    0.0),
                "CENTER":       (-dh/2,   0.0, 0.0, -dw/2),
                "TOP_LEFT":     (0.0,     0.0, 0.0,    0.0),
                "TOP_RIGHT":    (0.0,     0.0, 0.0,   -dw),
                "BOTTOM_LEFT":  (-dh,     0.0, 0.0,    0.0),
                "BOTTOM_RIGHT": (-dh,     0.0, 0.0,   -dw),
                "LEFT_WIDE":    (0.0,     0.0, 0.0,    0.0),
                "RIGHT_WIDE":   (0.0,     0.0, 0.0,   -dw),
                "TOP_WIDE":     (0.0,     0.0, 0.0,    0.0),
                "BOTTOM_WIDE":  (-dh,     0.0, 0.0,    0.0),
                "HCENTER_WIDE": (-dh/2,   0.0, 0.0,    0.0),
                "VCENTER_WIDE": (0.0,     0.0, 0.0, -dw/2),
            }[n]

        # Build preset buttons
        for name, preset in _PRESETS:
            _n, _p = name, preset
            def _make_cb(n=_n, pr=_p):
                def cb():
                    # Setting .text triggers auto-resize via Button.text.setter,
                    # so natural_size() returns the correct dims for the new text.
                    self._anchor_demo_btn.text = n
                    dw, dh = self._anchor_demo_btn.natural_size()
                    self._anchor_demo_btn.anchor_min, self._anchor_demo_btn.anchor_max = pr
                    self._anchor_demo_btn.margin = _margins_for(n, dw, dh)
                    amin, amax = pr
                    self._anchor_lbl.set_plain_text(
                        f"Current: {n}  (min={amin}  max={amax})"
                    )
                    self._anchor_inner._compute_layout()
                return cb
            btn_p = ui.button(name, size=V2(128, 30), on_click=_make_cb())
            preset_vb.add_child(btn_p)

        p._compute_layout()
        return p

    # ── Panel 6: Widgets inside containers ───────────────────────────────

    def _build_panel_widgets(self, ui: UIManager) -> FreeContainer:
        p = self._make_panel(ui)

        title = ui.label("Widgets inside containers — all Phase 2/3 widgets in VBoxes", default_style=sty(16, CYAN))
        p.add_child(title)
        p._child_offsets[id(title)] = (14.0, 10.0)

        info = ui.label("All interactions (click, drag, scroll, focus/tab) work normally inside containers.", default_style=sty(12, _GREY))
        p.add_child(info)
        p._child_offsets[id(info)] = (14.0, 32.0)

        col_w  = (PANEL_W - 28 - 12) // 3   # ~280px per column
        col_y  = 56.0

        # ── Column 0: Buttons + Switch + Checkbox ─────────────────────────
        vb0 = VBox(
            spacing=8, align='stretch',
            size=V2(col_w, 0),
            size_mode=SizeMode.AUTO,
            bg_color=section_bg(),
            border_color=Color(0.22, 0.22, 0.40, 0.7),
            border_width=1.0,
            corner_radius=6.0,
            padding=10,
        )
        lbl_title0 = ui.label("Buttons · Switch · Checkbox", default_style=sty(13, YELLOW))
        vb0.add_child(lbl_title0)
        self._click_count = 0
        self._click_lbl = ui.label("Clicks: 0", default_style=sty(12, YELLOW))
        btn_normal = ui.button("Normal Button", size=V2(col_w - 24, 34), on_click=self._on_btn_click)
        btn_disabled = ui.button("Disabled Button", size=V2(col_w - 24, 34), enabled=False)
        vb0.add_child(btn_normal)
        vb0.add_child(self._click_lbl)
        vb0.add_child(btn_disabled)

        sw_lbl = ui.label("Switch (toggle):", default_style=sty(12, _GREY))
        vb0.add_child(sw_lbl)
        self._widget_switch = ui.switch(value=True, size=V2(50, 26),
                                         max_width=50)
        vb0.add_child(self._widget_switch)

        cb_lbl = ui.label("Checkbox (check):", default_style=sty(12, _GREY))
        vb0.add_child(cb_lbl)
        self._widget_checkbox = ui.checkbox(value=False, size=V2(22, 22),
                                             max_width=22, max_height=22)
        vb0.add_child(self._widget_checkbox)

        p.add_child(vb0)
        p._child_offsets[id(vb0)] = (14.0, col_y)

        # ── Column 1: Sliders ─────────────────────────────────────────────
        vb1 = VBox(
            spacing=8, align='left',
            size=V2(col_w, 0),
            size_mode=SizeMode.AUTO,
            bg_color=section_bg(),
            border_color=Color(0.22, 0.22, 0.40, 0.7),
            border_width=1.0,
            corner_radius=6.0,
            padding=10,
        )
        lbl_title1 = ui.label("Sliders · RangeSlider", default_style=sty(13, YELLOW))
        vb1.add_child(lbl_title1)

        sl_lbl = ui.label("Horizontal slider (0–100):", default_style=sty(12, _GREY))
        vb1.add_child(sl_lbl)
        self._widget_slider = ui.slider(
            0, 100, step=1, value=50,
            on_change=self._on_widget_slider,
            size=V2(col_w - 20, 20),
        )
        vb1.add_child(self._widget_slider)

        self._widget_slider_val = ui.label("50", default_style=sty(12, YELLOW))
        vb1.add_child(self._widget_slider_val)

        rl_lbl = ui.label("Range slider (0–255):", default_style=sty(12, _GREY))
        vb1.add_child(rl_lbl)
        self._widget_range = ui.range_slider(
            0, 255, step=1,
            low_value=60, high_value=200,
            on_change=self._on_widget_range,
            size=V2(col_w - 20, 20),
        )
        vb1.add_child(self._widget_range)

        self._widget_range_val = ui.label("[60, 200]", default_style=sty(12, YELLOW))
        vb1.add_child(self._widget_range_val)

        vert_lbl = ui.label("Vertical slider (1–10):", default_style=sty(12, _GREY))
        vb1.add_child(vert_lbl)
        self._widget_vslider = ui.slider(
            1, 10, step=1, value=5,
            orientation='vertical',
            size=V2(20, 100),
        )
        vb1.add_child(self._widget_vslider)

        p.add_child(vb1)
        p._child_offsets[id(vb1)] = (14.0 + col_w + 6, col_y)

        # ── Column 2: Input fields ─────────────────────────────────────────
        vb2 = VBox(
            spacing=8, align='left',
            size=V2(col_w, 0),
            size_mode=SizeMode.AUTO,
            bg_color=section_bg(),
            border_color=Color(0.22, 0.22, 0.40, 0.7),
            border_width=1.0,
            corner_radius=6.0,
            padding=10,
        )
        lbl_title2 = ui.label("InputField · MultiLineInput", default_style=sty(13, YELLOW))
        vb2.add_child(lbl_title2)

        fld_lbl = ui.label("Single-line (Enter to submit):", default_style=sty(12, _GREY))
        vb2.add_child(fld_lbl)
        fld = ui.input_field(
            placeholder="Type here…",
            on_submit=self._on_widget_field,
            size=V2(col_w - 20, 32),
            tab_index=10,
        )
        vb2.add_child(fld)

        self._widget_field_val = ui.label("", default_style=sty(12, YELLOW))
        self._widget_field_val.set_plain_text("(not submitted)")
        vb2.add_child(self._widget_field_val)

        ml_lbl = ui.label("", default_style=sty(12, _GREY))
        ml_lbl.set_plain_text("Multi-line (Ctrl+Enter):")
        vb2.add_child(ml_lbl)
        ml = ui.multi_line_input(
            placeholder="Type here…",
            auto_expand=False,
            show_scrollbar=True,
            size=V2(col_w - 20, 90),
            tab_index=11,
        )
        vb2.add_child(ml)

        p.add_child(vb2)
        p._child_offsets[id(vb2)] = (14.0 + (col_w + 6) * 2, col_y)

        p._compute_layout()
        return p

    def _on_btn_click(self) -> None:
        self._click_count += 1
        self._click_lbl.set_plain_text(f"Clicks: {self._click_count}")

    def _on_widget_slider(self, v: float) -> None:
        self._widget_slider_val.set_plain_text(str(int(v)))

    def _on_widget_range(self, lo: float, hi: float) -> None:
        self._widget_range_val.set_plain_text(f"[{int(lo)}, {int(hi)}]")

    def _on_widget_field(self, v: str) -> None:
        self._widget_field_val.set_plain_text(v or "(empty)")

    # ── panel switching ───────────────────────────────────────────────────

    def _show_panel(self, idx: int) -> None:
        self._cur_panel = idx
        for i, panel in enumerate(self._panels):
            panel.visible = (i == idx)

    # ── lifecycle ─────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        # Detect window resize and update fixed-width sidebar height
        ws = self.root.ui._window_size
        new_size = (int(ws.x), int(ws.y))
        if new_size != self._last_win_size:
            self._last_win_size = new_size
            _, h = new_size
            self._sidebar.size = V2(SIDE_W, h - HEADER)

        kb = self.root.keyboard

        # Number keys 1–7 switch panels
        panel_keys = [
            Keys.NUM_1,   Keys.NUM_2,   Keys.NUM_3, Keys.NUM_4,
            Keys.NUM_5,  Keys.NUM_6,   Keys.NUM_7,
        ]
        for i, key in enumerate(panel_keys):
            if kb.get_key(key, KeyState.JUST_PRESSED):
                self._show_panel(i)

        if kb.get_key(Keys.T, KeyState.JUST_PRESSED):
            self._theme_idx = (self._theme_idx + 1) % len(_THEMES)
            name, theme = _THEMES[self._theme_idx]
            self.root.ui.theme = theme
            self._show_panel(self._cur_panel)   # refresh nav button colours
            print(f"Theme: {name}")

        if kb.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
            glfw.set_window_should_close(self.root.window, True)

    def draw(self) -> None:
        # VBox/FreeContainer panels cover the full window with their bg_color.
        # The black clear colour from RootEnv.__draw__ shows only in any gaps.
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    config = WindowConfig(
        size=V2(WIN_W, WIN_H),
        title="e2D Phase 4 — Containers & Layout",
        target_fps=60,
        vsync=False,
    )
    root = RootEnv(config=config)
    root.init(env := ContainersExample(root))
    root.loop()


if __name__ == "__main__":
    main()
