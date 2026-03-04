"""
e2D.ui.plot  —  Plot2D and GpuStream as first-class UI elements.

Classes
-------
UIPlot
    A :class:`UIElement` that hosts a :class:`~e2D.plot.Plot2D` inside a UI
    layout.  Supports mouse interaction (drag-to-pan, scroll-to-zoom) and
    exposes the full :class:`~e2D.plot.Plot2D` API via the ``.plot``
    attribute.  An optional gradient background sits behind the plot area.

UIStream
    A :class:`UIElement` that renders a live scrolling :class:`~e2D.plot.GpuStream`
    optimised for real-time metrics (FPS, latency, sensor data …).  Multiple
    named series can be added; each gets its own :class:`~e2D.plot.GpuStream`
    ring-buffer so all data stays on the GPU.

    Typical usage::

        # One-shot creation in __init__
        self.fps_graph = ui.add(UIStream(
            position=V2(10, 60), size=V2(400, 120),
            capacity=300,
            y_range=(0, 200),
        ))
        fps_series = self.fps_graph.add_series("fps",
            line_color=Color(0.15, 0.95, 0.50, 1.0))

        # Every frame
        fps_series.push_value(current_fps)
"""

from __future__ import annotations

import math
from typing import Optional, TYPE_CHECKING

import numpy as np

from .base import UIElement, MouseMode
from ..vectors import Vector2D, V2
from .._types import ColorType, ContextType, FloatVec2
from ..colors import Color, normalize_color
from ..gradient import LinearGradient, RadialGradient, PointGradient, GradientType

if TYPE_CHECKING:
    from .manager import UIManager
    from ..plot import Plot2D as _Plot2D, GpuStream as _GpuStream, View2D as _View2D


# ---------------------------------------------------------------------------
# _StreamSeries — one named data stream inside a UIStream widget
# ---------------------------------------------------------------------------

class _StreamSeries:
    """One GPU ring-buffer series inside a :class:`UIStream`.

    Do not construct directly — use :meth:`UIStream.add_series`.
    """

    def __init__(
        self,
        stream: '_GpuStream',
        name: str,
        *,
        capacity: int,
    ) -> None:
        self._stream  = stream
        self.name     = name
        self.capacity = capacity
        self._idx: int = 0   # monotonically increasing x counter

    # ------------------------------------------------------------------ push

    def push_value(self, y: float) -> None:
        """Append one scalar value to this series' ring-buffer."""
        pt = np.array([[float(self._idx), float(y)]], dtype='f4')
        self._stream.push(pt)
        self._idx += 1

    def push_values(self, ys) -> None:
        """Append multiple values at once (*ys*: list or 1-D numpy array)."""
        arr = np.asarray(ys, dtype='f4').ravel()
        n   = len(arr)
        xs  = np.arange(self._idx, self._idx + n, dtype='f4')
        pts = np.column_stack((xs, arr))
        self._stream.push(pts)
        self._idx += n

    def clear(self) -> None:
        """Erase all points from this series."""
        self._stream.clear_buffer()
        self._stream.head = 0
        self._stream.size = 0
        self._idx = 0

    @property
    def settings(self):
        """Direct access to the underlying :class:`~e2D.plot.StreamSettings`."""
        return self._stream.settings

    @property
    def size(self) -> int:
        return self._stream.size


# ---------------------------------------------------------------------------
# UIPlot — Plot2D as a UIElement
# ---------------------------------------------------------------------------

class UIPlot(UIElement):
    """A :class:`~e2D.plot.Plot2D` embedded in the UI layout system.

    The ``plot`` attribute gives full access to the underlying
    :class:`~e2D.plot.Plot2D` object (add curves, implicit plots, streams …).

    Parameters
    ----------
    position / size
        Screen position and pixel dimensions (same as every UIElement).
    plot_settings
        A :class:`~e2D.plot.PlotSettings` dataclass to configure grid colour,
        background, spacing, etc.
    gradient
        Optional :class:`~e2D.gradient.GradientType` drawn *behind* the plot
        quad (before the grid shader — gives the bg_color an extra flair).
    interactive
        When *True* (default), mouse drag pans the view and the scroll wheel
        zooms.
    corner_radius
        Rounded-corner clip applied to the plot area.
    border_color / border_width
        Border drawn around the plot frame.

    Example
    -------
    ::

        plot = ui.add(UIPlot(
            position=V2(20, 80), size=V2(600, 400),
            gradient=LinearGradient(
                stops=[(Color(0.02, 0.05, 0.12, 1.0), 0.0),
                       (Color(0.04, 0.12, 0.25, 1.0), 1.0)],
            ),
        ))
        plot.plot.view.zoom_step(2.0)
        curve = plot.plot_curve("x = sin(t)", func_body="x = t; y = sin(t);",
                                t_range=(-6, 6))
    """

    def __init__(
        self,
        position: Vector2D | tuple = (0.0, 0.0),
        size: Vector2D | tuple     = (400.0, 300.0),
        plot_settings = None,
        gradient: Optional[GradientType] = None,
        interactive: bool  = True,
        corner_radius: float = 6.0,
        border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
        border_width: float     = 0.0,
        **kwargs,
    ) -> None:
        super().__init__(
            position=position, size=size,
            mouse_mode=MouseMode.BLOCK,
            **kwargs,
        )
        self._plot_settings = plot_settings   # may be None — resolved in _build
        self._gradient      = gradient
        self._interactive   = interactive
        self.corner_radius  = corner_radius
        self.border_color   = border_color
        self.border_width   = border_width

        # Resolved in _build
        self.plot: Optional['_Plot2D'] = None
        self._is_hovered: bool = False
        self._dragging: bool   = False
        self._prev_mx: float   = 0.0
        self._prev_my: float   = 0.0

    # ----------------------------------------------------------------- build

    def _build(self, ctx: ContextType, text_renderer) -> None:
        from ..plot import Plot2D, PlotSettings
        rx, ry, rw, rh = self.get_screen_rect()

        # We need a RootEnv-compatible shim; Plot2D only uses ctx + window_size
        class _FakeRoot:
            def __init__(self, c, w, h):
                self.ctx = c
                self.window_size = V2(float(w), float(h))

        # Approximate window height from manager if available; default to 1080
        win_h = 1080.0
        if self._manager is not None:
            win_h = self._manager._window_size.y

        settings = self._plot_settings or PlotSettings()
        fake_root = _FakeRoot(ctx, rw + rx, win_h)

        self.plot = Plot2D(
            fake_root,  # type: ignore[arg-type]
            top_left     = (rx, ry),
            bottom_right = (rx + rw, ry + rh),
            settings     = settings,
        )
        self._dirty = False

    # ---------------------------------------------------------------- resize

    def _sync_plot_rect(self) -> None:
        """Called whenever position or size changes."""
        if self.plot is None:
            return
        rx, ry, rw, rh = self.get_screen_rect()
        self.plot.set_rect((rx, ry), (rx + rw, ry + rh))
        win_h = self._manager._window_size.y if self._manager else 1080.0
        self.plot.update_window_size(int(self._manager._window_size.x) if self._manager else 1920, int(win_h))

    # ------------------------------------------------------------------ draw

    def draw(self, ctx: ContextType) -> None:
        if not self.visible or self.plot is None:
            return

        assert self._manager is not None
        alpha = self._effective_opacity()
        rx, ry, rw, rh = self.get_screen_rect()

        # Sync viewport if size dirtied
        if self._dirty:
            self._sync_plot_rect()
            self._dirty = False

        sr = self._manager.shape_renderer

        # Optional gradient behind the plot
        if self._gradient is not None:
            sr.draw_rect_gradient(
                V2(rx, ry), V2(rw, rh),
                gradient=self._gradient,
                corner_radius=self.corner_radius,
                opacity=alpha,
            )
            sr.flush_queue()

        # Border / clipping frame (drawn on top after plot)
        def _draw_plot():
            pass   # plot renders itself inside render(); just a callback hook

        self.plot.render(_draw_plot)

        # Overlay border
        if self.border_width > 0:
            bc = normalize_color(self.border_color)
            sr.draw_rect(
                V2(rx, ry), V2(rw, rh),
                color=(0, 0, 0, 0),
                corner_radius=self.corner_radius,
                border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
                border_width=self.border_width,
                layer=500,
            )
            sr.flush_queue()

        # Children (labels, annotations, etc.)
        for child in self._children:
            if child.visible:
                child.draw(ctx)

    # --------------------------------------------------------- mouse events

    def on_hover_enter(self) -> None:
        self._is_hovered = True

    def on_hover_exit(self) -> None:
        self._is_hovered = False
        self._dragging  = False

    def on_mouse_press(self, mx: float, my: float) -> None:
        if self._interactive:
            self._dragging = True
            self._prev_mx  = mx
            self._prev_my  = my

    def on_mouse_release(self, mx: float, my: float) -> None:
        self._dragging = False

    def on_mouse_drag(self, mx: float, my: float, dx: float, dy: float) -> None:
        if self._interactive and self.plot is not None:
            self.plot.on_mouse_drag(dx, -dy)

    def on_scroll(self, dy: float) -> None:
        if self._interactive and self.plot is not None:
            rx, ry, rw, rh = self.get_screen_rect()
            # Use centre of plot as zoom target when there is no cursor pos
            cx, cy = rx + rw / 2, ry + rh / 2
            self.plot.on_scroll(dy, cx, cy)

    # --------------------------------------------------------- debug info

    def _debug_info(self):
        rows = super()._debug_info()
        if self.plot is not None:
            v = self.plot.view
            rows += [
                ("zoom_x", f"{v.zoom[0]:.3f}"),
                ("zoom_y", f"{v.zoom[1]:.3f}"),
                ("center", f"{v.center[0]:.3f}, {v.center[1]:.3f}"),
            ]
        return rows

    def release(self) -> None:
        if self.plot is not None:
            try:
                self.plot.grid_vao.release()
                self.plot.grid_quad.release()
                self.plot.grid_prog.release()
                self.plot.view.buffer.release()
            except Exception:
                pass
        super().release()

    # ------------------------------------------------- convenience helpers

    def add_stream(
        self,
        capacity: int = 100_000,
        settings=None,
    ) -> '_GpuStream':
        """Create and return a :class:`~e2D.plot.GpuStream` attached to this
        plot's context.  Call ``stream.draw()`` inside the render callback."""
        assert self.plot is not None
        from ..plot import GpuStream
        return GpuStream(self.plot.ctx, capacity=capacity, settings=settings)

    def plot_curve(
        self,
        func_body: str,
        t_range: tuple,
        count: int = 1024,
        settings=None,
    ):
        """Create a GPU compute curve and attach it to this plot."""
        assert self.plot is not None
        from ..plot import ComputeCurve
        return ComputeCurve(self.plot.ctx, func_body, t_range, count, settings)

    def plot_implicit(self, func_body: str, settings=None):
        """Create an implicit-surface plot and attach it to this plot."""
        assert self.plot is not None
        from ..plot import ImplicitPlot
        return ImplicitPlot(self.plot.ctx, func_body, settings)


# ---------------------------------------------------------------------------
# UIStream — live metrics stream as a standalone UI widget
# ---------------------------------------------------------------------------

class UIStream(UIElement):
    """Live-metrics streaming widget — multiple named GPU ring-buffer series.

    Each series is a :class:`_StreamSeries` backed by a :class:`~e2D.plot.GpuStream`.
    All series share one :class:`~e2D.plot.View2D` UBO so they render with a
    consistent coordinate space.

    The widget auto-scrolls on the x-axis so the newest data is always at the
    right edge, and auto-scales the y-axis when ``y_range`` is ``None``.

    Parameters
    ----------
    capacity
        Ring-buffer depth per series (number of samples).  300 ≈ 5 s at 60 fps.
    y_range
        ``(y_min, y_max)`` world-space y extents.  Pass ``None`` (default) for
        auto-scaling based on observed values.
    y_pad
        Extra headroom factor when auto-scaling (1.15 = 15 % above max).
    gradient
        Background gradient for the plot area.
    bg_color
        Fallback solid background colour (used when *gradient* is ``None``).
    show_labels
        When *True*, draws the series name and current value at the right edge.
    label_color
        Text colour for value labels.
    grid_lines
        Number of horizontal grid-lines drawn (0 = none).
    corner_radius / border_color / border_width
        Frame styling.

    Example
    -------
    ::

        graph = ui.add(UIStream(
            position=V2(10, 50), size=V2(500, 140),
            capacity=600,
            y_range=(0, 200),
            gradient=LinearGradient(
                stops=[(Color(0.02, 0.05, 0.12, 1.0), 0.0),
                       (Color(0.04, 0.10, 0.22, 1.0), 1.0)],
            ),
        ))
        fps_s  = graph.add_series("FPS",   line_color=Color(0.15, 0.95, 0.50))
        dt_s   = graph.add_series("dt ms", line_color=Color(0.90, 0.60, 0.10))

        # Every frame:
        fps_s.push_value(current_fps)
        dt_s.push_value(delta * 1000)
    """

    def __init__(
        self,
        position: Vector2D | tuple = (0.0, 0.0),
        size: Vector2D | tuple     = (300.0, 100.0),
        *,
        capacity: int   = 300,
        y_range: Optional[FloatVec2] = None,
        y_pad:   float  = 1.15,
        gradient: Optional[GradientType] = None,
        bg_color: ColorType = (0.02, 0.04, 0.02, 0.95),
        show_labels: bool   = True,
        label_color: ColorType = (0.85, 0.90, 0.85, 1.0),
        grid_lines:  int    = 4,
        corner_radius: float = 5.0,
        border_color: ColorType = (0.10, 0.45, 0.20, 0.55),
        border_width: float = 1.0,
        **kwargs,
    ) -> None:
        super().__init__(
            position=position, size=size,
            mouse_mode=MouseMode.PASS_THROUGH,
            **kwargs,
        )
        self._capacity   = capacity
        self._y_range    = y_range
        self._y_pad      = y_pad
        self._gradient   = gradient
        self._bg_color   = bg_color
        self._show_labels = show_labels
        self._label_color = label_color
        self._grid_lines  = grid_lines
        self.corner_radius = corner_radius
        self.border_color  = border_color
        self.border_width  = border_width

        self._series: list[_StreamSeries] = []
        self._view: Optional['_View2D']   = None

        # Auto-scale tracking
        self._y_obs_max: float = 1.0
        self._y_obs_min: float = 0.0

        # Label TextLabel cache per series
        self._label_cache: dict[str, object] = {}

    # ----------------------------------------------------------------- build

    def _build(self, ctx: ContextType, text_renderer) -> None:
        from ..plot import View2D
        self._view = View2D(ctx, binding=0)
        rx, ry, rw, rh = self.get_screen_rect()
        self._view.update_win_size(rw, rh)
        self._dirty = False

    # ---------------------------------------------------------------- series

    def add_series(
        self,
        name: str,
        *,
        line_color: ColorType = (1.0, 1.0, 1.0, 1.0),
        line_width: float    = 1.5,
        show_points: bool    = False,
        point_color: ColorType | None = None,
        point_radius: float  = 3.0,
        smooth: bool         = False,
        curve_segments: int  = 8,
        capacity: Optional[int] = None,
    ) -> _StreamSeries:
        """Add a named data series and return its :class:`_StreamSeries` handle.

        Parameters
        ----------
        name
            Display name (shown in label overlay when ``show_labels=True``).
        line_color
            RGBA line colour.
        line_width
            GPU line width in pixels.
        show_points
            Render each sample as a dot in addition to the line.
        point_color
            Point colour (defaults to *line_color*).
        point_radius
            Point dot radius when *show_points* is *True*.
        smooth
            Use Catmull-Rom interpolation between samples.
        curve_segments
            Subdivision count per segment when *smooth* is *True*.
        capacity
            Per-series override for ring-buffer depth (defaults to widget capacity).
        """
        view = self._view
        if view is None:
            raise RuntimeError("UIStream must be added to a UIManager before add_series()")
        from ..plot import GpuStream, StreamSettings, LineType
        cap    = capacity if capacity is not None else self._capacity
        pc     = point_color if point_color is not None else line_color
        ltype  = LineType.SMOOTH if smooth else LineType.DIRECT
        ss     = StreamSettings(
            line_color    = line_color,
            line_width    = line_width,
            line_type     = ltype,
            show_points   = show_points,
            point_color   = pc,
            point_radius  = point_radius,
            curve_segments = curve_segments,
        )
        stream = GpuStream(view.ctx, capacity=cap, settings=ss)
        series = _StreamSeries(stream, name, capacity=cap)
        self._series.append(series)
        return series

    def remove_series(self, name: str) -> None:
        """Remove and free a series by name."""
        for i, s in enumerate(self._series):
            if s.name == name:
                _safe_release_stream(s._stream)
                self._series.pop(i)
                self._label_cache.pop(name, None)
                return

    # ------------------------------------------------------------------ draw

    def draw(self, ctx: ContextType) -> None:
        if not self.visible or self._view is None:
            return

        assert self._manager is not None
        alpha  = self._effective_opacity()
        rx, ry, rw, rh = self.get_screen_rect()
        sr     = self._manager.shape_renderer

        # ── Background ────────────────────────────────────────────────────
        if self._gradient is not None:
            sr.draw_rect_gradient(
                V2(rx, ry), V2(rw, rh),
                gradient=self._gradient,
                corner_radius=self.corner_radius,
                opacity=alpha,
                layer=0,
            )
        else:
            bg = normalize_color(self._bg_color)
            sr.draw_rect(
                V2(rx, ry), V2(rw, rh),
                color=(bg.r, bg.g, bg.b, bg.a * alpha),
                corner_radius=self.corner_radius,
                layer=0,
            )

        # Border
        if self.border_width > 0:
            bc = normalize_color(self.border_color)
            sr.draw_rect(
                V2(rx, ry), V2(rw, rh),
                color=(0, 0, 0, 0),
                corner_radius=self.corner_radius,
                border_color=(bc.r, bc.g, bc.b, bc.a * alpha),
                border_width=self.border_width,
                layer=500,
            )

        sr.flush_queue()

        if not self._series:
            return

        # ── Compute y extents ──────────────────────────────────────────────
        if self._y_range is not None:
            y_min, y_max = self._y_range
        else:
            y_max = self._y_obs_max * self._y_pad
            y_min = self._y_obs_min
            if y_max <= y_min:
                y_max = y_min + 1.0

        # ── Horizontal grid lines (drawn as shape rects) ───────────────────
        if self._grid_lines > 0:
            for gi in range(self._grid_lines + 1):
                frac = gi / self._grid_lines
                gy   = ry + rh - frac * rh
                sr.draw_rect(
                    V2(rx + 1, gy), V2(rw - 2, 0.5),
                    color=(0.30, 0.45, 0.30, 0.25 * alpha),
                    layer=1,
                )
            sr.flush_queue()

        # ── Sub-viewport for stream rendering ─────────────────────────────
        PAD   = max(1, int(self.corner_radius * 0.5))
        gx    = int(rx + PAD)
        gw_px = int(rw - PAD * 2)
        gh_px = int(rh - PAD * 2)
        # OpenGL y-up: bottom of widget in GL coords
        win_h = self._manager._window_size.y
        gy_gl = int(win_h - (ry + rh - PAD))

        if gw_px <= 0 or gh_px <= 0:
            return

        last_vp = ctx.viewport
        last_sc = ctx.scissor

        self._view.update_win_size(gw_px, gh_px)

        # x window: show the last `capacity` samples from the series with most data
        max_idx = max((s._idx for s in self._series), default=0)
        cap     = max((s.capacity for s in self._series), default=self._capacity)
        x_max   = float(max_idx)
        x_min   = float(max_idx - cap)

        from ..plot import V2 as _V2  # just the same V2 — avoids circular re-import
        self._view.set_viewport(
            V2(x_min, y_max),
            V2(x_max, y_min),
        )

        ctx.viewport = (gx, gy_gl, gw_px, gh_px)
        ctx.scissor  = (gx, gy_gl, gw_px, gh_px)
        self._view.buffer.bind_to_uniform_block(0)

        # Notify auto-scale tracker per series
        for series in self._series:
            series._stream.draw()

        ctx.scissor  = last_sc
        ctx.viewport = last_vp

        # ── Value labels at right edge ─────────────────────────────────────
        if self._show_labels and self._manager is not None:
            self._draw_labels(ctx, rx, ry, rw, rh, y_min, y_max, alpha)

    def _draw_labels(
        self,
        ctx,
        rx: float, ry: float, rw: float, rh: float,
        y_min: float, y_max: float,
        alpha: float,
    ) -> None:
        """Draw series name + latest value at the right edge of the widget."""
        assert self._manager is not None
        from ..text import TextStyle
        tr = self._manager.text_renderer
        lc = normalize_color(self._label_color)
        style = TextStyle(font_size=9, color=Color(lc.r, lc.g, lc.b, lc.a * alpha))
        y_span = y_max - y_min if y_max != y_min else 1.0
        for series in self._series:
            if series.size < 1:
                continue
            # Peek at last y value: read last 2 floats from the ring-buffer
            # (4 bytes each = 8 bytes total, offset = (head-1) slot * 8 bytes)
            slot = (series._stream.head - 1) % series._stream.capacity
            try:
                raw  = series._stream.buffer.read(8, offset=slot * 8)
                import struct as _st
                _x, last_y = _st.unpack('2f', raw)
            except Exception:
                continue

            # Pin label to the y position of the last value
            frac      = (last_y - y_min) / y_span
            frac      = max(0.0, min(1.0, frac))
            label_y   = ry + rh - frac * rh - 6
            label_x   = rx + rw + 4

            sc        = series._stream.settings
            lc_s      = normalize_color(sc.line_color)
            dot_style = TextStyle(font_size=9, color=Color(lc_s.r, lc_s.g, lc_s.b, alpha))
            self._manager.text_renderer.draw_text(
                f"▶ {series.name} {last_y:.1f}",
                (label_x, label_y),
                style=dot_style,
            )

    # ---------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        """Track observed y-range for auto-scaling."""
        super().update(dt)
        if self._y_range is not None:
            return
        # Sample the latest value from each series to update auto-scale bounds
        for series in self._series:
            if series.size < 1:
                continue
            slot = (series._stream.head - 1) % series._stream.capacity
            try:
                raw  = series._stream.buffer.read(8, offset=slot * 8)
                import struct as _st
                _x, last_y = _st.unpack('2f', raw)
                self._y_obs_max = max(self._y_obs_max, last_y)
                self._y_obs_min = min(self._y_obs_min, last_y)
            except Exception:
                pass

    # --------------------------------------------------------------- release

    def release(self) -> None:
        for series in self._series:
            _safe_release_stream(series._stream)
        self._series.clear()
        if self._view is not None:
            try:
                self._view.buffer.release()
            except Exception:
                pass
        super().release()

    # ------------------------------------------------------------ debug info

    def _debug_info(self):
        rows = super()._debug_info()
        rows.append(("series", str(len(self._series))))
        rows.append(("capacity", str(self._capacity)))
        if self._y_range:
            rows.append(("y_range", f"{self._y_range[0]:.1f}–{self._y_range[1]:.1f}"))
        else:
            rows.append(("y_auto", f"{self._y_obs_min:.1f}–{self._y_obs_max:.1f}"))
        return rows


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _safe_release_stream(stream) -> None:
    for attr in ('buffer', 'prog', 'vao', 'smooth_prog', 'smooth_vao'):
        try:
            getattr(stream, attr).release()
        except Exception:
            pass
