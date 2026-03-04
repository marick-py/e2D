"""
Containers and Layout System — Phase 4 of e2D UI.

Provides hierarchical layout containers for organising UI elements:

* :class:`UIContainer` — abstract base with background, padding, and
  theming.  All concrete containers inherit from it.
* :class:`VBox` — vertical stack (`spacing`, cross-axis `align`)
* :class:`HBox` — horizontal stack (`spacing`, cross-axis `align`)
* :class:`Grid` — rows × columns cell grid
* :class:`FreeContainer` — absolute child positioning (no auto-layout)
* :class:`ScrollContainer` — scrollable single-child wrapper with
  optional scrollbar

Also provides:

* :class:`SizeMode` — ``FIXED``, ``PERCENT``, ``AUTO`` size mode
  constants; assign to ``element.size_mode``
* :class:`Anchor` — Godot-style anchor preset tuples for
  ``(anchor_min, anchor_max)``

Usage::

    # create a vertical stack and add to the manager
    side = env.ui.vbox(spacing=8, position=V2(20, 20), size=V2(240, 500),
                       bg_color=Color(0.1, 0.1, 0.15, 0.9))

    side.add_child(env.ui.button("Play"))
    side.add_child(env.ui.button("Settings"))
    side.add_child(env.ui.button("Quit"))

    # scrollable content panel
    scroll = env.ui.scroll_container(position=V2(300, 20), size=V2(400, 600))
    content = env.ui.vbox(spacing=4, size_mode=SizeMode.AUTO)
    for i in range(40):
        content.add_child(env.ui.label(f"Row {i}"))
    scroll.add_child(content)

    # PERCENT-sized children
    row = env.ui.hbox(spacing=0, size=V2(600, 40))
    left = Button("Left", size=V2(0.5, 1.0))
    left.size_mode = SizeMode.PERCENT
    row.add_child(left)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Optional

from .base import UIElement, MouseMode
from .label import Label
from ..colors import Color
from .._pivot import Pivot
from ..vectors import V2

if TYPE_CHECKING:
    from .._types import ContextType
    from ..text import TextRenderer, TextStyle
    from ..shapes import ShapeRenderer
    from ..gradient import GradientType, LinearGradient, RadialGradient


# ─────────────────────────────────────────────────────────────────────────────
# SizeMode
# ─────────────────────────────────────────────────────────────────────────────

class SizeMode:
    """Size mode constants for UIElement children inside containers.

    Assign to ``element.size_mode`` before adding to a container::

        btn = Button("OK")
        btn.size_mode = SizeMode.PERCENT
        btn._size.set(1.0, 1.0)   # 100% width, 100% height of parent inner rect
        hbox.add_child(btn)

    * ``FIXED``   — ``element.size`` is treated as pixels (default).
    * ``PERCENT`` — ``element.size`` values are 0.0–1.0 fractions of the
                    parent container's *inner* size.
    * ``AUTO``    — element sizes itself to fit its content.  Currently
                    meaningful for VBox / HBox (total stacked extent);
                    other elements fall back to ``FIXED``.
    """

    FIXED   = 'fixed'
    PERCENT = 'percent'
    AUTO    = 'auto'


# ─────────────────────────────────────────────────────────────────────────────
# Anchor — Godot-style convenience presets
# ─────────────────────────────────────────────────────────────────────────────

class Anchor:
    """Godot-style anchor convenience presets.

    Each preset is a two-tuple ``(anchor_min, anchor_max)`` that can be
    unpacked into the corresponding UIElement constructor kwargs or assigned
    directly::

        panel.anchor_min, panel.anchor_max = Anchor.FULL_RECT
        panel.layout(0, 0, win_w, win_h)
    """

    FULL_RECT    = ((0.0, 0.0), (1.0, 1.0))   # fills parent completely
    TOP_LEFT     = ((0.0, 0.0), (0.0, 0.0))   # absolute: top-left corner (default)
    TOP_RIGHT    = ((1.0, 0.0), (1.0, 0.0))   # top-right corner (use margin_left=-w)
    BOTTOM_LEFT  = ((0.0, 1.0), (0.0, 1.0))   # bottom-left corner (use margin_top=-h)
    BOTTOM_RIGHT = ((1.0, 1.0), (1.0, 1.0))   # bottom-right corner (use margin=-h,0,0,-w)
    CENTER       = ((0.5, 0.5), (0.5, 0.5))   # centred, fixed size (use margin=-h/2,0,0,-w/2)
    TOP_WIDE     = ((0.0, 0.0), (1.0, 0.0))   # full-width top strip   (fixed height)
    BOTTOM_WIDE  = ((0.0, 1.0), (1.0, 1.0))   # full-width bottom strip (use margin_top=-h)
    HCENTER_WIDE = ((0.0, 0.5), (1.0, 0.5))   # full-width centred strip (use margin_top=-h/2)
    LEFT_WIDE    = ((0.0, 0.0), (0.0, 1.0))   # full-height left strip  (fixed width)
    RIGHT_WIDE   = ((1.0, 0.0), (1.0, 1.0))   # full-height right strip (use margin_left=-w)
    VCENTER_WIDE = ((0.5, 0.0), (0.5, 1.0))   # full-height centred strip (use margin_left=-w/2)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ov(override, default):
    """Return *override* if not None, otherwise *default*."""
    return override if override is not None else default


# ─────────────────────────────────────────────────────────────────────────────
# UIContainer — abstract base
# ─────────────────────────────────────────────────────────────────────────────

class UIContainer(UIElement):
    """Abstract base container: background rendering, padding, and
    theming.  Concrete subclasses (VBox, HBox, …) override
    :meth:`_compute_layout`.

    Beyond the standard :class:`UIElement` kwargs:

    * ``bg_color``      — fill colour; ``None`` → transparent (no fill)
    * ``border_color``  — border stroke; ``None`` → theme default
    * ``border_width``  — border width in pixels; ``None`` → 0
    * ``corner_radius`` — rounded corners; ``None`` → theme default
    * ``clip_content``  — scissor-clip children to the container bounds
                          (default: ``False``)
    """

    def __init__(
        self,
        *,
        bg_color:      Color | None = None,
        bg_gradient:   'GradientType | None' = None,
        border_color:  Color | None = None,
        border_width:  float | None = None,
        corner_radius: float | None = None,
        clip_content:  bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        # Layout containers are transparent to mouse by default;
        # interactive child widgets stay hittable through them.
        if self.mouse_mode == MouseMode.BLOCK:
            self.mouse_mode = MouseMode.PASS_THROUGH
        self._ov_bg_color      = bg_color
        self._ov_bg_gradient   = bg_gradient    # LinearGradient / RadialGradient / None
        self._ov_border_color  = border_color
        self._ov_border_width  = border_width
        self._ov_corner_radius = corner_radius
        self.clip_content: bool = clip_content

        # Stores the *original* (sx, sy) fraction for PERCENT-mode children.
        # Without this, after the first layout pass the fraction is overwritten
        # with pixel values and the next pass multiplies again — exponential growth.
        self._percent_sizes: dict[int, tuple[float, float]] = {}

        # Stores the *original* (x, y) position of each child as a relative
        # offset from the container origin.  Used by the default
        # _compute_layout to translate children from local → screen coords.
        # Concrete subclasses (VBox, HBox, Grid) override _compute_layout and
        # compute absolute positions themselves, so the offsets are unused.
        self._child_offsets: dict[int, tuple[float, float]] = {}

        # Resolved drawing values (written in _build)
        self._bg_color    = Color(0.0, 0.0, 0.0, 0.0)
        self._bg_gradient = None          # resolved gradient or None
        self._border_c    = Color(0.0, 0.0, 0.0, 0.0)
        self._border_w    = 0.0
        self._corner_r    = 0.0

    # -- size property override -------------------------------------------
    # Override the parent setter so that changing container size
    # automatically re-runs the layout pass for children.

    @property
    def size(self):  # type: ignore[override]
        return self._size

    @size.setter
    def size(self, value) -> None:  # type: ignore[override]
        if isinstance(value, (tuple, list)):
            self._size.set(float(value[0]), float(value[1]))
        else:
            self._size = value
        self._dirty = True
        self._compute_layout()

    # -- build ------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:  # type: ignore[override]
        theme = self._manager.theme if self._manager else None
        if theme:
            # Default background: same hue as theme bg_normal but transparent.
            # Caller must pass bg_color explicitly to make it visible.
            t_bg = theme.bg_normal
            default_bg = Color(t_bg.r, t_bg.g, t_bg.b, 0.0)
            self._bg_color = _ov(self._ov_bg_color,      default_bg)
            self._border_c = _ov(self._ov_border_color,  theme.border_color)
            self._border_w = _ov(self._ov_border_width,  0.0)
            self._corner_r = _ov(self._ov_corner_radius, theme.corner_radius)
        else:
            self._bg_color = self._ov_bg_color      or Color(0.0, 0.0, 0.0, 0.0)
            self._border_c = self._ov_border_color  or Color(0.0, 0.0, 0.0, 0.0)
            self._border_w = self._ov_border_width  or 0.0
            self._corner_r = self._ov_corner_radius or 0.0

        # Gradient overrides solid bg_color when provided
        self._bg_gradient = self._ov_bg_gradient

        # Recursively build children
        for child in self._children:
            child._build(ctx, text_renderer)

        self._compute_layout()
        self._dirty = False

    # -- inner rect -------------------------------------------------------

    def _inner_rect(self) -> tuple[float, float, float, float]:
        """Return *(x, y, width, height)* of the padded content area."""
        rx, ry, rw, rh = self.get_screen_rect()
        p = self.padding  # (top, right, bottom, left)
        return (
            rx + p[3],
            ry + p[0],
            max(0.0, rw - p[1] - p[3]),
            max(0.0, rh - p[0] - p[2]),
        )

    # -- layout -----------------------------------------------------------

    def _compute_layout(self) -> None:
        """Position children relative to this container's padded origin.

        Each child's position is treated as a *local offset* from the
        container's top-left padding corner and translated to screen
        coordinates.  Concrete subclasses (VBox, HBox, Grid, …) override
        this to apply their own stacking/grid logic.
        """
        if not self._children:
            return

        rx, ry, rw, rh = self.get_screen_rect()
        p = self.padding
        origin_x = rx + p[3]   # left edge + left-padding
        origin_y = ry + p[0]   # top  edge + top-padding

        for child in self._children:
            am = child.anchor_min
            ax = child.anchor_max
            if am != (0.0, 0.0) or ax != (0.0, 0.0):
                # Anchor-based child — use standard Godot-style layout
                child.layout(rx, ry, rw, rh)
            else:
                # Relative positioning: use the saved offset if available,
                # fall back to the child's current position otherwise.
                rel_x, rel_y = self._child_offsets.get(
                    id(child), (child._position.x, child._position.y)
                )
                child._position.set(origin_x + rel_x, origin_y + rel_y)

            if hasattr(child, '_compute_layout'):
                child._compute_layout()  # type: ignore[union-attr]

    def layout(self, px: float, py: float, pw: float, ph: float) -> None:
        super().layout(px, py, pw, ph)
        self._compute_layout()

    # -- child management -------------------------------------------------

    def add_child(self, child: UIElement) -> None:  # type: ignore[override]
        # Save the child's initial position as its local offset *before*
        # _compute_layout converts it to absolute screen coordinates.
        self._child_offsets[id(child)] = (child._position.x, child._position.y)
        super().add_child(child)
        # Save the fraction immediately — _compute_layout would overwrite _size
        # with pixel values on the first pass, causing exponential growth.
        if getattr(child, 'size_mode', SizeMode.FIXED) == SizeMode.PERCENT:
            self._percent_sizes[id(child)] = (child._size.x, child._size.y)
        if self._manager:
            child._build(self._manager.ctx, self._manager.text_renderer)
        self._compute_layout()

    def remove_child(self, child: UIElement) -> None:  # type: ignore[override]
        self._percent_sizes.pop(id(child), None)
        self._child_offsets.pop(id(child), None)
        super().remove_child(child)
        self._compute_layout()

    # -- draw -------------------------------------------------------------

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return
        ctx   = ctx or self._manager.ctx
        sr    = self._manager.shape_renderer
        rx, ry, rw, rh = self.get_screen_rect()
        alpha = self._effective_opacity()
        c     = self._bg_color
        bc    = self._border_c

        if self._bg_gradient is not None:
            # Gradient overrides the solid fill colour
            sr.draw_rect_gradient(
                V2(rx, ry), V2(rw, rh),
                gradient=self._bg_gradient,
                corner_radius=self._corner_r,
                border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
                border_width=self._border_w,
                opacity=alpha,
            )
        elif c.a * alpha > 0.001 or self._border_w > 0:
            # Queue background only when it's visually non-trivial
            sr.draw_rect(
                V2(rx, ry), V2(rw, rh),
                color=(c.r, c.g, c.b, c.a * alpha),
                corner_radius=self._corner_r,
                border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
                border_width=self._border_w,
            )

        if self._children:
            # Flush background rect before drawing children so they appear on top
            sr.flush_queue()
            if self.clip_content:
                self._draw_clipped(ctx)
            else:
                self._draw_children(ctx)

    def _draw_children(self, ctx) -> None:
        """Draw all visible children (used by draw and subclass overrides)."""
        for child in self._children:
            if child.visible:
                child.draw(ctx)

    def _draw_clipped(self, ctx) -> None:
        """Draw children clipped to the container's inner rect."""
        if self._manager is None:
            return
        ix, iy, iw, ih = self._inner_rect()
        win_h = self._manager._window_size.y
        ctx.scissor = (int(ix), int(win_h - iy - ih), int(iw), int(ih))
        self._draw_children(ctx)
        self._manager.shape_renderer.flush_queue()
        ctx.scissor = None

    # -- debug ------------------------------------------------------------

    def _debug_info(self) -> list[tuple[str, str]]:
        rows = super()._debug_info()
        ix, iy, iw, ih = self._inner_rect()
        p = self.padding
        rows += [
            ("children",   str(len(self._children))),
            ("inner_size", f"{iw:.0f} x {ih:.0f}"),
            ("padding",    f"T{p[0]:.0f} R{p[1]:.0f} B{p[2]:.0f} L{p[3]:.0f}"),
            ("clip",       "yes" if self.clip_content else "no"),
            ("mouse_mode", self.mouse_mode),
            ("size_mode",  self.size_mode),
        ]
        return rows

    # -- child size helper ------------------------------------------------

    def _child_px_size(
        self,
        child: UIElement,
        avail_w: float,
        avail_h: float,
    ) -> tuple[float, float]:
        """Resolve *child*'s pixel dimensions given available space.

        Respects :attr:`size_mode` (``PERCENT`` multiplies against available
        space; everything else is taken as pixels).

        For PERCENT children the *original* fraction saved at :meth:`add_child`
        time is used — not the current ``_size`` value which may have been
        overwritten with pixels by a previous layout pass.
        """
        sm = getattr(child, 'size_mode', SizeMode.FIXED)
        if sm == SizeMode.PERCENT:
            sx, sy = self._percent_sizes.get(id(child), (child._size.x, child._size.y))
            return sx * avail_w, sy * avail_h
        return child._size.x, child._size.y

    # -- natural content size (override in layout containers) -------------

    def natural_size(self) -> tuple[float, float]:
        """Return the *natural* (unwrapped) content size in pixels.

        Used by parent containers when this container has
        ``size_mode = SizeMode.AUTO``.
        """
        return self._size.x, self._size.y


# ─────────────────────────────────────────────────────────────────────────────
# VBox — vertical stack
# ─────────────────────────────────────────────────────────────────────────────

class VBox(UIContainer):
    """Stacks children vertically, top-to-bottom.

    Constructor kwargs beyond :class:`UIContainer`:

    * ``spacing`` — pixel gap between children (default: ``0``)
    * ``align``   — horizontal alignment of children:
                    ``'left'`` (default), ``'center'``, ``'right'``,
                    ``'stretch'`` (children fill container width)
    """

    def __init__(
        self,
        spacing: float = 0.0,
        align:   str   = 'left',
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.spacing: float = spacing
        self.align:   str   = align

    def _compute_layout(self) -> None:
        if not self._children:
            if getattr(self, 'size_mode', SizeMode.FIXED) == SizeMode.AUTO:
                self._size.y = self.padding[0] + self.padding[2]
            return

        ix, iy, iw, ih = self._inner_rect()
        y = iy

        for child in self._children:
            if not child.visible:
                continue
            cw, ch = self._child_px_size(child, iw, ih)

            # Horizontal position based on align
            if self.align == 'stretch':
                cw = iw
                mw = getattr(child, 'max_width', None)
                if mw is not None:
                    cw = min(cw, mw)
                cx = ix
            elif self.align == 'center':
                cx = ix + (iw - cw) * 0.5
            elif self.align == 'right':
                cx = ix + iw - cw
            else:  # 'left'
                cx = ix

            child._position.set(cx, y)
            child._size.set(cw, ch)
            if hasattr(child, '_compute_layout'):
                child._compute_layout()  # type: ignore[union-attr]

            y += ch + self.spacing

        # AUTO height: shrink/grow to fit content
        if getattr(self, 'size_mode', SizeMode.FIXED) == SizeMode.AUTO:
            content_h = (y - iy) - self.spacing  # remove trailing gap
            self._size.y = max(
                0.0,
                content_h + self.padding[0] + self.padding[2],
            )

    def natural_size(self) -> tuple[float, float]:
        """Return total stacked height (width unchanged)."""
        p = self.padding
        total_h = p[0] + p[2]
        visible = [c for c in self._children if c.visible]
        if not visible:
            return self._size.x, total_h
        for c in visible:
            total_h += c._size.y
        total_h += self.spacing * max(0, len(visible) - 1)
        return self._size.x, total_h

    def _debug_info(self) -> list[tuple[str, str]]:
        rows = super()._debug_info()
        rows += [
            ("spacing", f"{self.spacing:.0f}px"),
            ("align",   self.align),
        ]
        return rows


# ─────────────────────────────────────────────────────────────────────────────
# HBox — horizontal stack
# ─────────────────────────────────────────────────────────────────────────────

class HBox(UIContainer):
    """Stacks children horizontally, left-to-right.

    Constructor kwargs beyond :class:`UIContainer`:

    * ``spacing`` — pixel gap between children (default: ``0``)
    * ``align``   — vertical alignment of children:
                    ``'top'`` (default), ``'center'``, ``'bottom'``,
                    ``'stretch'`` (children fill container height)
    """

    def __init__(
        self,
        spacing: float = 0.0,
        align:   str   = 'top',
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.spacing: float = spacing
        self.align:   str   = align

    def _compute_layout(self) -> None:
        if not self._children:
            if getattr(self, 'size_mode', SizeMode.FIXED) == SizeMode.AUTO:
                self._size.x = self.padding[1] + self.padding[3]
            return

        ix, iy, iw, ih = self._inner_rect()
        x = ix

        for child in self._children:
            if not child.visible:
                continue
            cw, ch = self._child_px_size(child, iw, ih)

            # Vertical position based on align
            if self.align == 'stretch':
                ch = ih
                mh = getattr(child, 'max_height', None)
                if mh is not None:
                    ch = min(ch, mh)
                cy = iy
            elif self.align == 'center':
                cy = iy + (ih - ch) * 0.5
            elif self.align == 'bottom':
                cy = iy + ih - ch
            else:  # 'top'
                cy = iy

            child._position.set(x, cy)
            child._size.set(cw, ch)
            if hasattr(child, '_compute_layout'):
                child._compute_layout()  # type: ignore[union-attr]

            x += cw + self.spacing

        # AUTO width: shrink/grow to fit content
        if getattr(self, 'size_mode', SizeMode.FIXED) == SizeMode.AUTO:
            content_w = (x - ix) - self.spacing
            self._size.x = max(
                0.0,
                content_w + self.padding[1] + self.padding[3],
            )

    def natural_size(self) -> tuple[float, float]:
        """Return total stacked width (height unchanged)."""
        p = self.padding
        total_w = p[1] + p[3]
        visible = [c for c in self._children if c.visible]
        if not visible:
            return total_w, self._size.y
        for c in visible:
            total_w += c._size.x
        total_w += self.spacing * max(0, len(visible) - 1)
        return total_w, self._size.y

    def _debug_info(self) -> list[tuple[str, str]]:
        rows = super()._debug_info()
        rows += [
            ("spacing", f"{self.spacing:.0f}px"),
            ("align",   self.align),
        ]
        return rows


# ─────────────────────────────────────────────────────────────────────────────
# Grid — rows × columns cell layout
# ─────────────────────────────────────────────────────────────────────────────

class Grid(UIContainer):
    """Arranges children in a rows × columns grid.

    Constructor kwargs beyond :class:`UIContainer`:

    * ``columns``      — number of columns (required; rows are computed
                         automatically from child count)
    * ``cell_spacing`` — ``(h_gap, v_gap)`` in pixels (default: ``(0, 0)``)
    * ``cell_size``    — if ``None`` all cells are equal (fill container);
                         if ``(w, h)`` each cell is this fixed size in
                         pixels regardless of container size
    """

    def __init__(
        self,
        columns:      int                              = 1,
        cell_spacing: tuple[float, float]              = (0.0, 0.0),
        cell_size:    tuple[float, float] | None       = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.columns:      int                         = max(1, columns)
        self.cell_spacing: tuple[float, float]         = cell_spacing
        self.cell_size:    tuple[float, float] | None  = cell_size

    def _compute_layout(self) -> None:
        if not self._children:
            return

        ix, iy, iw, ih = self._inner_rect()
        cols = self.columns
        hgap, vgap = self.cell_spacing

        visible = [c for c in self._children if c.visible]
        rows = math.ceil(len(visible) / cols)

        if self.cell_size is not None:
            cw, ch = self.cell_size
        else:
            # Equal cells filling inner rect
            cw = (iw - hgap * (cols - 1)) / cols if cols > 1 else iw
            ch = (ih - vgap * (rows - 1)) / rows if rows > 1 else ih
            cw = max(0.0, cw)
            ch = max(0.0, ch)

        for i, child in enumerate(visible):
            col = i % cols
            row = i // cols
            cx = ix + col * (cw + hgap)
            cy = iy + row * (ch + vgap)
            child._position.set(cx, cy)
            child._size.set(cw, ch)
            if hasattr(child, '_compute_layout'):
                child._compute_layout()  # type: ignore[union-attr]

    def _debug_info(self) -> list[tuple[str, str]]:
        rows_d = super()._debug_info()
        visible = sum(1 for c in self._children if c.visible)
        cols = self.columns
        actual_rows = math.ceil(visible / cols) if cols else 0
        rows_d += [
            ("columns", str(cols)),
            ("rows",    str(actual_rows)),
        ]
        return rows_d


# ─────────────────────────────────────────────────────────────────────────────
# FreeContainer — absolute positioning
# ─────────────────────────────────────────────────────────────────────────────

class FreeContainer(UIContainer):
    """Container with relative child positioning — each child's
    ``position`` is interpreted as an offset from the container's
    top-left corner (after padding).

    No automatic stacking is performed; children must be positioned
    manually.  Anchor-based children (those with non-zero
    ``anchor_min``/``anchor_max``) still use the Godot-style anchor
    layout.

    Constructor kwargs beyond :class:`UIContainer`:
        *(none beyond the standard UIContainer params)*

    Example::

        panel = FreeContainer(position=V2(200, 100), size=V2(400, 300),
                              bg_color=Color(0.1, 0.1, 0.1, 0.9))
        env.ui.add(panel)

        # position (10, 8) = 10 px from panel left, 8 px from panel top
        lbl = Label("Score: 0", position=V2(10, 8))
        panel.add_child(lbl)
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Maps id(child) → (rel_x, rel_y) — the offset saved at add_child time.
        self._child_offsets: dict[int, tuple[float, float]] = {}

    # -- child management -------------------------------------------------

    def add_child(self, child: UIElement) -> None:  # type: ignore[override]
        # Save the child's current position as its relative offset *before*
        # calling super() which triggers _compute_layout and may reset it.
        rel_x, rel_y = child._position.x, child._position.y
        super().add_child(child)
        self._child_offsets[id(child)] = (rel_x, rel_y)

    def remove_child(self, child: UIElement) -> None:  # type: ignore[override]
        self._child_offsets.pop(id(child), None)
        super().remove_child(child)

    # -- layout -----------------------------------------------------------

    def _compute_layout(self) -> None:
        rx, ry, rw, rh = self.get_screen_rect()
        p = self.padding
        origin_x = rx + p[3]  # left edge + left-padding
        origin_y = ry + p[0]  # top  edge + top-padding

        for child in self._children:
            am = child.anchor_min
            ax = child.anchor_max
            if am != (0.0, 0.0) or ax != (0.0, 0.0):
                # Anchor-based child — use standard layout()
                child.layout(rx, ry, rw, rh)
            else:
                # Relative child — the offset was saved at add_child time
                rel_x, rel_y = self._child_offsets.get(
                    id(child), (child._position.x, child._position.y)
                )
                child._position.set(origin_x + rel_x, origin_y + rel_y)
                if hasattr(child, '_compute_layout'):
                    child._compute_layout()  # type: ignore[union-attr]

    def _debug_info(self) -> list[tuple[str, str]]:
        rows = super()._debug_info()
        rows += [("type", "free")]
        return rows


# ─────────────────────────────────────────────────────────────────────────────
# ScrollContainer — scrollable single-child wrapper
# ─────────────────────────────────────────────────────────────────────────────

class ScrollContainer(UIContainer):
    """Wraps exactly one child and clips/scrolls it within the visible area.

    The child is typically a :class:`VBox` or :class:`HBox` with
    ``size_mode = SizeMode.AUTO`` so it sizes itself to fit its content.

    Constructor kwargs beyond :class:`UIContainer`:

    * ``scroll_vertical``   — enable vertical scrolling (default: ``True``)
    * ``scroll_horizontal`` — enable horizontal scrolling (default: ``False``)
    * ``show_scrollbar``    — show a scrollbar when content overflows
                              (default: ``True``)
    * ``scrollbar_width``   — scrollbar track width in pixels (default: ``8``)
    * ``scrollbar_color``   — scrollbar track colour
    * ``scrollbar_thumb``   — scrollbar thumb colour
    * ``scroll_speed``      — pixels scrolled per mouse-wheel notch
                              (default: ``40``)
    """

    _SB_MIN_THUMB = 16.0  # minimum scrollbar thumb height in pixels

    def __init__(
        self,
        *,
        scroll_vertical:   bool        = True,
        scroll_horizontal: bool        = False,
        show_scrollbar:    bool        = True,
        scrollbar_width:   float       = 8.0,
        scrollbar_color:   Color | None = None,
        scrollbar_thumb:   Color | None = None,
        scroll_speed:      float       = 40.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        # ScrollContainer needs to capture mouse for scrollbar drag and
        # hover effects — restore BLOCK even though UIContainer defaults to
        # PASS_THROUGH.  Callers may still override via mouse_mode= kwarg.
        if self.mouse_mode == MouseMode.PASS_THROUGH:
            self.mouse_mode = MouseMode.BLOCK
        self.scroll_vertical:   bool  = scroll_vertical
        self.scroll_horizontal: bool  = scroll_horizontal
        self.show_scrollbar:    bool  = show_scrollbar
        self._sb_width:         float = scrollbar_width
        self._ov_sb_color               = scrollbar_color
        self._ov_sb_thumb               = scrollbar_thumb
        self.scroll_speed:      float = scroll_speed

        # Resolved colours
        self._sb_color = Color(0.20, 0.20, 0.25, 0.60)
        self._sb_thumb_color = Color(0.50, 0.50, 0.60, 0.85)

        # Scroll state
        self._scroll_x: float = 0.0
        self._scroll_y: float = 0.0

        # Content size (measured from child after layout)
        self._content_w: float = 0.0
        self._content_h: float = 0.0

        # Scrollbar drag
        self._dragging_vbar: bool  = False
        self._dragging_hbar: bool  = False
        self._drag_start_y:  float = 0.0
        self._drag_start_x:  float = 0.0
        self._drag_scroll_y: float = 0.0
        self._drag_scroll_x: float = 0.0

        self._is_hovered: bool = False

    # -- build ------------------------------------------------------------

    def _build(self, ctx: ContextType, text_renderer: TextRenderer) -> None:  # type: ignore[override]
        theme = self._manager.theme if self._manager else None
        if theme:
            self._sb_color       = _ov(self._ov_sb_color, theme.scrollbar_color)
            self._sb_thumb_color = _ov(self._ov_sb_thumb, theme.scrollbar_thumb)
        else:
            self._sb_color       = self._ov_sb_color       or Color(0.20, 0.20, 0.25, 0.60)
            self._sb_thumb_color = self._ov_sb_thumb or Color(0.50, 0.50, 0.60, 0.85)
        super()._build(ctx, text_renderer)

    # -- scroll property --------------------------------------------------

    @property
    def scroll_y(self) -> float:
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: float) -> None:
        max_scroll = max(0.0, self._content_h - self._visible_h())
        self._scroll_y = max(0.0, min(float(value), max_scroll))
        self._compute_layout()

    @property
    def scroll_x(self) -> float:
        return self._scroll_x

    @scroll_x.setter
    def scroll_x(self, value: float) -> None:
        max_scroll = max(0.0, self._content_w - self._visible_w())
        self._scroll_x = max(0.0, min(float(value), max_scroll))
        self._compute_layout()

    # -- visible area helpers ---------------------------------------------

    def _visible_w(self) -> float:
        ix, iy, iw, ih = self._inner_rect()
        return iw - (self._sb_width if self._vbar_needed() else 0.0)

    def _visible_h(self) -> float:
        ix, iy, iw, ih = self._inner_rect()
        return ih - (self._sb_width if self._hbar_needed() else 0.0)

    def _vbar_needed(self) -> bool:
        if not self.scroll_vertical or not self.show_scrollbar:
            return False
        ix, iy, iw, ih = self._inner_rect()
        return self._content_h > ih

    def _hbar_needed(self) -> bool:
        if not self.scroll_horizontal or not self.show_scrollbar:
            return False
        ix, iy, iw, ih = self._inner_rect()
        return self._content_w > iw

    # -- layout -----------------------------------------------------------

    def add_child(self, child: UIElement) -> None:  # type: ignore[override]
        # Only one content child allowed; remove the existing one first.
        if self._children:
            self.remove_child(self._children[0])
        UIContainer.add_child(self, child)

    def _compute_layout(self) -> None:
        if not self._children:
            return
        child = self._children[0]

        ix, iy, iw, ih = self._inner_rect()
        vbar = self._vbar_needed()
        hbar = self._hbar_needed()
        vis_w = iw - (self._sb_width if vbar else 0.0)
        vis_h = ih - (self._sb_width if hbar else 0.0)

        # For AUTO-sized children: measure natural size first, then set width,
        # re-measure, because width affects VBox height (word wrap not supported
        # yet, but width must still be constrained).
        if hasattr(child, 'natural_size'):
            # Set content width to visible width so child auto-sizes correctly
            if self.scroll_vertical and not self.scroll_horizontal:
                child._size.set(vis_w, child._size.y)
            if hasattr(child, '_compute_layout'):
                child._compute_layout()  # type: ignore[union-attr]
            nw, nh = child.natural_size()  # type: ignore[union-attr]
        else:
            nw, nh = child._size.x, child._size.y

        self._content_w = nw
        self._content_h = nh

        # Clamp scroll so it doesn't exceed new content size
        max_sy = max(0.0, self._content_h - vis_h)
        max_sx = max(0.0, self._content_w - vis_w)
        self._scroll_y = min(self._scroll_y, max_sy)
        self._scroll_x = min(self._scroll_x, max_sx)

        # Position content child with scroll offset
        child._position.set(ix - self._scroll_x, iy - self._scroll_y)
        if hasattr(child, '_compute_layout'):
            child._compute_layout()  # type: ignore[union-attr]

    # -- scroll rect helpers (for hit-testing the scrollbars) -------------

    def _vbar_track_rect(self) -> tuple[float, float, float, float]:
        ix, iy, iw, ih = self._inner_rect()
        hbar = self._hbar_needed()
        bar_h = ih - (self._sb_width if hbar else 0.0)
        return (ix + iw - self._sb_width, iy, self._sb_width, bar_h)

    def _vbar_thumb_rect(self) -> tuple[float, float, float, float]:
        tx, ty, tw, th = self._vbar_track_rect()
        vis_h = self._visible_h()
        if self._content_h <= vis_h or self._content_h == 0:
            return (tx, ty, tw, th)
        ratio      = vis_h / self._content_h
        thumb_h    = max(self._SB_MIN_THUMB, th * ratio)
        scroll_frac = self._scroll_y / (self._content_h - vis_h)
        thumb_y    = ty + scroll_frac * (th - thumb_h)
        return (tx, thumb_y, tw, thumb_h)

    def _hbar_track_rect(self) -> tuple[float, float, float, float]:
        ix, iy, iw, ih = self._inner_rect()
        vbar = self._vbar_needed()
        bar_w = iw - (self._sb_width if vbar else 0.0)
        return (ix, iy + ih - self._sb_width, bar_w, self._sb_width)

    def _hbar_thumb_rect(self) -> tuple[float, float, float, float]:
        tx, ty, tw, th = self._hbar_track_rect()
        vis_w = self._visible_w()
        if self._content_w <= vis_w or self._content_w == 0:
            return (tx, ty, tw, th)
        ratio      = vis_w / self._content_w
        thumb_w    = max(self._SB_MIN_THUMB, tw * ratio)
        scroll_frac = self._scroll_x / (self._content_w - vis_w)
        thumb_x    = tx + scroll_frac * (tw - thumb_w)
        return (thumb_x, ty, thumb_w, th)

    # -- draw -------------------------------------------------------------

    def draw(self, ctx=None) -> None:
        if not self.visible or self._manager is None:
            return
        ctx = ctx or self._manager.ctx
        sr  = self._manager.shape_renderer
        rx, ry, rw, rh = self.get_screen_rect()
        alpha = self._effective_opacity()
        c  = self._bg_color
        bc = self._border_c

        # Background (gradient override if present)
        if self._bg_gradient is not None:
            sr.draw_rect_gradient(
                V2(rx, ry), V2(rw, rh),
                gradient=self._bg_gradient,
                corner_radius=self._corner_r,
                border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
                border_width=self._border_w,
                opacity=alpha,
            )
        elif c.a * alpha > 0.001 or self._border_w > 0:
            sr.draw_rect(
                V2(rx, ry), V2(rw, rh),
                color=(c.r, c.g, c.b, c.a * alpha),
                corner_radius=self._corner_r,
                border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
                border_width=self._border_w,
            )

        if self._children:
            sr.flush_queue()  # flush bg before clipping
            self._draw_scrolled(ctx)

        # Scrollbars (drawn on top — outside scissor)
        if self._vbar_needed():
            self._draw_vbar(sr, alpha)
        if self._hbar_needed():
            self._draw_hbar(sr, alpha)

    def _draw_scrolled(self, ctx) -> None:
        """Draw the content child with scissor clipping."""
        if self._manager is None:
            return
        ix, iy, iw, ih = self._inner_rect()
        vbar = self._vbar_needed()
        hbar = self._hbar_needed()
        clip_w = iw - (self._sb_width if vbar else 0.0)
        clip_h = ih - (self._sb_width if hbar else 0.0)

        win_h = self._manager._window_size.y
        ctx.scissor = (
            int(ix),
            int(win_h - iy - clip_h),
            max(1, int(clip_w)),
            max(1, int(clip_h)),
        )
        self._draw_children(ctx)
        self._manager.shape_renderer.flush_queue()
        ctx.scissor = None

    def _draw_vbar(self, sr: ShapeRenderer, alpha: float) -> None:
        tx, ty, tw, th = self._vbar_track_rect()
        sc = self._sb_color
        sth = self._sb_thumb_color
        sr.draw_rect(
            V2(tx, ty), V2(tw, th),
            color=(sc.r, sc.g, sc.b, sc.a * alpha),
            corner_radius=tw * 0.5,
        )
        thx, thy, thw, thh = self._vbar_thumb_rect()
        sr.draw_rect(
            V2(thx, thy), V2(thw, thh),
            color=(sth.r, sth.g, sth.b, sth.a * alpha),
            corner_radius=thw * 0.5,
        )

    def _draw_hbar(self, sr: ShapeRenderer, alpha: float) -> None:
        tx, ty, tw, th = self._hbar_track_rect()
        sc = self._sb_color
        sth = self._sb_thumb_color
        sr.draw_rect(
            V2(tx, ty), V2(tw, th),
            color=(sc.r, sc.g, sc.b, sc.a * alpha),
            corner_radius=th * 0.5,
        )
        thx, thy, thw, thh = self._hbar_thumb_rect()
        sr.draw_rect(
            V2(thx, thy), V2(thw, thh),
            color=(sth.r, sth.g, sth.b, sth.a * alpha),
            corner_radius=th * 0.5,
        )

    # -- input events -----------------------------------------------------

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False

    def on_scroll(self, dy: float) -> None:
        """Scroll vertically (or horizontally if only h-scroll enabled)."""
        if self.scroll_vertical:
            self.scroll_y = self._scroll_y - dy * self.scroll_speed
        elif self.scroll_horizontal:
            self.scroll_x = self._scroll_x - dy * self.scroll_speed

    def on_mouse_press(self, mx: float, my: float) -> None:
        """Start scrollbar thumb drag if click lands on a thumb."""
        if self._vbar_needed():
            thx, thy, thw, thh = self._vbar_thumb_rect()
            if thx <= mx <= thx + thw and thy <= my <= thy + thh:
                self._dragging_vbar = True
                self._drag_start_y  = my
                self._drag_scroll_y = self._scroll_y
                return
        if self._hbar_needed():
            thx, thy, thw, thh = self._hbar_thumb_rect()
            if thx <= mx <= thx + thw and thy <= my <= thy + thh:
                self._dragging_hbar = True
                self._drag_start_x  = mx
                self._drag_scroll_x = self._scroll_x

    def on_mouse_drag(self, mx: float, my: float, dx: float, dy: float) -> None:
        if self._dragging_vbar:
            tx, ty, tw, th = self._vbar_track_rect()
            vis_h = self._visible_h()
            if self._content_h <= vis_h or vis_h == 0:
                return
            ratio   = vis_h / self._content_h
            thumb_h = max(self._SB_MIN_THUMB, th * ratio)
            movable = th - thumb_h
            if movable > 0:
                delta = (my - self._drag_start_y) / movable
                max_s = self._content_h - vis_h
                self.scroll_y = self._drag_scroll_y + delta * max_s

        if self._dragging_hbar:
            tx, ty, tw, th = self._hbar_track_rect()
            vis_w = self._visible_w()
            if self._content_w <= vis_w or vis_w == 0:
                return
            ratio   = vis_w / self._content_w
            thumb_w = max(self._SB_MIN_THUMB, tw * ratio)
            movable = tw - thumb_w
            if movable > 0:
                delta = (mx - self._drag_start_x) / movable
                max_s = self._content_w - vis_w
                self.scroll_x = self._drag_scroll_x + delta * max_s

    def on_mouse_release(self, mx: float, my: float) -> None:
        self._dragging_vbar = False
        self._dragging_hbar = False

    # -- debug ------------------------------------------------------------

    def _debug_info(self) -> list[tuple[str, str]]:
        rows = super()._debug_info()
        rows += [
            ("scroll",     f"{self._scroll_x:.0f}, {self._scroll_y:.0f}"),
            ("content",    f"{self._content_w:.0f} x {self._content_h:.0f}"),
            ("vscroll",    "yes" if self.scroll_vertical   else "no"),
            ("hscroll",    "yes" if self.scroll_horizontal else "no"),
        ]
        return rows
