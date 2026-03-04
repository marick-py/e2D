"""
UIManager — owns every UI element, handles focus, tab navigation,
z-ordered drawing, and input dispatch.
"""

from __future__ import annotations

import moderngl
import numpy as np
from typing import Optional, TYPE_CHECKING

from .button import Button
from .toggle import Checkbox, Switch
from .slider import RangeSlider, Slider

from .containers import FreeContainer, HBox, ScrollContainer, VBox, Grid
from .input_field import InputField, MultiLineInput

from .base import Pivot, UIElement
from .theme import UITheme, MONOKAI_THEME
from .label import Label
from ..vectors import V2
from ..gradient import LinearGradient
from ..colors import Color

if TYPE_CHECKING:
    from .._types import ContextType
    from ..text import TextRenderer, TextStyle
    from ..input import Keyboard, Mouse
    from ..vectors import Vector2D
    from ..shapes import ShapeRenderer


class _UIDebugPanel:
    """Internal helper — renders a live debug info side panel for a hovered UIElement."""

    PANEL_W = 300
    PAD_X   = 10
    PAD_Y   = 8
    LINE_H  = 17
    TITLE_H = 24

    def __init__(self, mgr: 'UIManager') -> None:
        from ..text import TextStyle
        from ..colors import Color
        self._mgr  = mgr
        self._title_lbl: Optional[Label] = None
        self._kv_lbls:   list[Label]     = []
        self._src_lbl:   Optional[Label] = None
        self._s_title = TextStyle(font_size=14, color=Color(1.00, 0.92, 0.25))
        self._s_kv    = TextStyle(font_size=11, color=Color(0.87, 0.87, 0.90))
        self._s_src   = TextStyle(font_size=10, color=Color(0.35, 0.85, 0.45))
        # Cache last rendered strings — avoid GPU rebuild when text is unchanged
        self._last_title: str       = ""
        self._last_kv:    list[str] = []
        self._last_src:   str       = ""

    # -------------------------------------------------------------------------

    def _make(self, style) -> Label:
        lbl = Label("", default_style=style)
        lbl._manager = self._mgr
        lbl._build(self._mgr.ctx, self._mgr.text_renderer)
        return lbl

    def _ensure_kv(self, n: int) -> None:
        while len(self._kv_lbls) < n:
            self._kv_lbls.append(self._make(self._s_kv))

    # -------------------------------------------------------------------------

    def draw(self, elem: UIElement, win_w: float, win_h: float) -> None:
        info  = elem._debug_info()
        title = type(elem).__name__
        src   = getattr(elem, '_debug_source', '')
        kv    = [f"  {k:<13} {v}" for k, v in info]

        # Update labels only when content changes (spares GPU rebuilds)
        if self._title_lbl is None:
            self._title_lbl = self._make(self._s_title)
        if title != self._last_title:
            self._title_lbl.set_plain_text(title)
            self._last_title = title

        self._ensure_kv(len(kv))
        for i, line in enumerate(kv):
            if i >= len(self._last_kv) or self._last_kv[i] != line:
                self._kv_lbls[i].set_plain_text(line)
        self._last_kv = kv[:]

        if self._src_lbl is None:
            self._src_lbl = self._make(self._s_src)
        src_text = f"  @ {src}" if src else "  @ (source unknown)"
        if src_text != self._last_src:
            self._src_lbl.set_plain_text(src_text)
            self._last_src = src_text

        # ---- geometry ----
        n_kv    = len(kv)
        panel_h = (self.PAD_Y * 2
                   + self.TITLE_H + 6
                   + n_kv * self.LINE_H + 6
                   + self.LINE_H + self.PAD_Y)
        panel_x = win_w - self.PANEL_W - 8
        panel_y = 8.0
        sr  = self._mgr.shape_renderer
        ctx = self._mgr.ctx
        SEP = (0.27, 0.27, 0.48, 0.70)

        # Background — flush immediately so labels render on top
        sr.draw_rect(
            V2(panel_x, panel_y), V2(self.PANEL_W, panel_h),
            color=(0.04, 0.04, 0.09, 0.91),
            corner_radius=6.0,
            border_color=(0.27, 0.27, 0.48, 0.95),
            border_width=1.0,
            layer=9999,
        )
        sr.flush_queue()

        y = panel_y + self.PAD_Y

        self._title_lbl._position.set(panel_x + self.PAD_X, y)
        self._title_lbl.draw(ctx)
        y += self.TITLE_H + 2

        sr.draw_rect(V2(panel_x + self.PAD_X, y),
                     V2(self.PANEL_W - self.PAD_X * 2, 1),
                     color=SEP, layer=9999)
        sr.flush_queue()
        y += 6

        for i in range(n_kv):
            self._kv_lbls[i]._position.set(panel_x + self.PAD_X, y)
            self._kv_lbls[i].draw(ctx)
            y += self.LINE_H

        y += 4
        sr.draw_rect(V2(panel_x + self.PAD_X, y),
                     V2(self.PANEL_W - self.PAD_X * 2, 1),
                     color=SEP, layer=9999)
        sr.flush_queue()
        y += 5

        self._src_lbl._position.set(panel_x + self.PAD_X, y)
        self._src_lbl.draw(ctx)

    # -------------------------------------------------------------------------

    def release(self) -> None:
        if self._title_lbl is not None:
            self._title_lbl.release()
            self._title_lbl = None
        for lbl in self._kv_lbls:
            lbl.release()
        self._kv_lbls.clear()
        if self._src_lbl is not None:
            self._src_lbl.release()
            self._src_lbl = None
        self._last_title = ""
        self._last_kv    = []
        self._last_src   = ""


# ---------------------------------------------------------------------------
# _UIStatsPanel  —  live performance stats overlay
# ---------------------------------------------------------------------------

class _UIStatsPanel:
    """Internal stats HUD drawn when ``UIManager.show_stats`` is ``True``.

    Displays FPS, frame time, UPS (if a fixed update rate is set), and
    total elapsed time.  Toggled at runtime via **F2** or by setting
    ``ui.show_stats = True / False``.
    """

    PANEL_W        = 230
    PAD_X          = 10
    PAD_Y          = 8
    LINE_H         = 18
    GRAPH_H        = 64          # pixel height of the FPS strip
    GRAPH_CAPACITY = 300         # ring-buffer depth (~5 s at 60 fps)

    def __init__(self, mgr: 'UIManager') -> None:
        from ..text import TextStyle
        from ..colors import Color
        # Late import: plot.py imports from e2D root (circular at module level)
        from ..plot import GpuStream, View2D, StreamSettings, LineType as _LT
        self._mgr = mgr
        self._s_title = TextStyle(font_size=12, color=Color(0.15, 1.00, 0.60))
        self._s_val   = TextStyle(font_size=11, color=Color(0.87, 0.87, 0.90))
        self._labels:     list[Label] = []
        self._last_texts: list[str]   = []

        # ── FPS graph ──────────────────────────────────────────────────────
        _ss = StreamSettings(
            show_points  = False,
            line_type    = _LT.DIRECT,
            line_color   = Color(0.15, 0.95, 0.50, 1.0),
            line_width   = 1.5,
        )
        self._graph: GpuStream = GpuStream(
            mgr.ctx, capacity=self.GRAPH_CAPACITY, settings=_ss
        )
        self._graph_view: View2D = View2D(mgr.ctx, binding=0)
        self._graph_push_idx: int   = 0
        self._graph_y_max:    float = 120.0

        # ── Cached gradients ───────────────────────────────────────────────
        self._panel_grad = LinearGradient(
            stops=[
                (Color(0.02, 0.08, 0.04, 0.92), 0.0),
                (Color(0.06, 0.12, 0.08, 0.88), 0.55),
                (Color(0.04, 0.06, 0.03, 0.90), 1.0),
            ],
            angle=160.0,
        )
        self._graph_grad = LinearGradient(
            stops=[
                (Color(0.01, 0.06, 0.02, 0.97), 0.0),
                (Color(0.02, 0.10, 0.04, 0.93), 1.0),
            ],
            angle=90.0,
        )

    # -------------------------------------------------------------------------

    def _make(self, style) -> Label:
        lbl = Label("", default_style=style)
        lbl._manager = self._mgr
        lbl._build(self._mgr.ctx, self._mgr.text_renderer)
        return lbl

    def _ensure_labels(self, n: int) -> None:
        while len(self._labels) < n:
            self._labels.append(self._make(self._s_val))

    # -------------------------------------------------------------------------

    def push_fps(self, fps: float) -> None:
        """Append one FPS sample to the graph ring-buffer."""
        self._graph_y_max = max(self._graph_y_max, fps * 1.30, 30.0)
        pt = np.array([[float(self._graph_push_idx), float(fps)]], dtype='f4')
        self._graph.push(pt)
        self._graph_push_idx += 1

    # -------------------------------------------------------------------------

    def draw(self, lines: list[str], win_w: float, win_h: float) -> None:
        n = len(lines)
        self._ensure_labels(n)
        while len(self._last_texts) < n:
            self._last_texts.append("")

        for i, text in enumerate(lines):
            if self._last_texts[i] != text:
                self._labels[i].set_plain_text(text)
                self._last_texts[i] = text

        # Panel height: text rows + gap + graph strip + bottom pad
        panel_h = (self.PAD_Y * 2 + n * self.LINE_H
                   + self.PAD_Y + self.GRAPH_H + self.PAD_Y)
        # Position: top-left corner, small margin
        panel_x = 8.0
        panel_y = 8.0
        sr  = self._mgr.shape_renderer
        ctx = self._mgr.ctx

        # Outer panel background — flush immediately so labels appear on top
        sr.draw_rect_gradient(
            V2(panel_x, panel_y), V2(self.PANEL_W, panel_h),
            gradient=self._panel_grad,
            corner_radius=6.0,
            border_color=(0.10, 0.80, 0.40, 0.60),
            border_width=1.0,
            layer=9998,
        )
        sr.flush_queue()

        y = panel_y + self.PAD_Y
        for i in range(n):
            self._labels[i]._position.set(panel_x + self.PAD_X, y)
            self._labels[i].draw(ctx)
            y += self.LINE_H

        # ── FPS graph ──────────────────────────────────────────────────────
        # Graph rect in screen (y-down) coords
        graph_top_y  = panel_y + self.PAD_Y * 2 + n * self.LINE_H
        gw_f         = self.PANEL_W - self.PAD_X * 2

        # Graph background
        sr.draw_rect_gradient(
            V2(panel_x + self.PAD_X, graph_top_y),
            V2(gw_f, self.GRAPH_H),
            gradient=self._graph_grad,
            corner_radius=3.0,
            border_color=(0.08, 0.45, 0.20, 0.55),
            border_width=1.0,
            layer=9999,
        )
        sr.flush_queue()

        # Render the stream into a sub-viewport (inset 1 px from border)
        if self._graph.size > 1:
            gx     = int(panel_x + self.PAD_X + 1)
            # OpenGL y-up: bottom of graph in GL coords
            gy     = int(win_h - (graph_top_y + self.GRAPH_H - 1))
            gw_int = int(gw_f - 2)
            gh_int = self.GRAPH_H - 2

            last_vp = ctx.viewport
            last_sc = ctx.scissor

            self._graph_view.update_win_size(gw_int, gh_int)
            x_min = float(self._graph_push_idx - self._graph.capacity)
            x_max = float(self._graph_push_idx)
            # set_viewport(top_left_world, bottom_right_world)
            self._graph_view.set_viewport(
                V2(x_min, self._graph_y_max),
                V2(x_max, 0.0),
            )

            ctx.viewport = (gx, gy, gw_int, gh_int)
            ctx.scissor  = (gx, gy, gw_int, gh_int)
            self._graph_view.buffer.bind_to_uniform_block(0)
            self._graph.draw()

            ctx.scissor  = last_sc
            ctx.viewport = last_vp

    # -------------------------------------------------------------------------

    def release(self) -> None:
        for lbl in self._labels:
            lbl.release()
        self._labels.clear()
        self._last_texts.clear()
        # Free graph GPU resources
        for attr in ('buffer', 'prog', 'vao', 'smooth_prog', 'smooth_vao'):
            try:
                getattr(self._graph, attr).release()
            except Exception:
                pass
        try:
            self._graph_view.buffer.release()
        except Exception:
            pass


class UIManager:
    """Central hub for the UI layer.

    Created automatically by :class:`RootEnv` and stored as ``env.ui``.
    """

    def __init__(
        self,
        ctx: ContextType,
        text_renderer: TextRenderer,
        shape_renderer: ShapeRenderer,
        window_size: Vector2D,
        theme: UITheme | None = None,
        window=None,
    ) -> None:
        self.ctx: ContextType = ctx
        self.text_renderer: TextRenderer = text_renderer
        self.shape_renderer: ShapeRenderer = shape_renderer
        self._window_size: Vector2D = window_size
        self._theme: UITheme = theme or MONOKAI_THEME

        self._elements: list[UIElement] = []
        self._focused: Optional[UIElement] = None
        self._hovered: Optional[UIElement] = None

        # Element that received the last mouse-down event (for drag/release)
        self._pressed_on: Optional[UIElement] = None
        # Stored each frame so interactive elements (e.g. Slider) can read them
        self._keyboard = None
        self._mouse    = None
        # Previous mouse position for computing drag deltas
        self._prev_mx: float = 0.0
        self._prev_my: float = 0.0

        self._wants_keyboard: bool = False
        self._wants_mouse: bool = False
        # GLFW window handle (needed for clipboard in InputField / MultiLineInput)
        self._window = window

        self.debug_mode = False  # Set True to draw debug outlines and info
        self._debug_panel: Optional[_UIDebugPanel] = None
        # Separate hover for debug mode — includes PASS_THROUGH containers.
        self._debug_hovered: Optional[UIElement] = None

        # ── Stats overlay (F2 / show_stats) ──────────────────────────────────
        self._show_stats:   bool = False
        self._stats_panel:  Optional[_UIStatsPanel] = None
        # Cached stat values — updated each frame by RootEnv.loop()
        self._stat_fps:      float = 0.0
        self._stat_delta:    float = 0.0
        self._stat_ups:      float = 0.0
        self._stat_fixed_dt: float = 0.0
        self._stat_elapsed:  float = 0.0

        # ── Blur / frosted-glass FBOs ─────────────────────────────────────────
        # These are lazily created the first time a blurred element is drawn.
        # They track the window size and are recreated on resize.
        self._blur_fbo_size: tuple[int, int] = (0, 0)
        self._blur_capture_tex  = None   # Texture2D — copy of current screen
        self._blur_capture_fbo  = None   # Framebuffer wrapping capture tex
        self._blur_ping_tex     = None
        self._blur_ping_fbo     = None
        self._blur_pong_tex     = None
        self._blur_pong_fbo     = None
        self._blur_prog         = None   # Gaussian blur shader (both passes)
        self._blur_blit_prog    = None   # Screen-space blit (texture → element rect)
        self._blur_quad_vbo     = None   # Fullscreen -1..1 quad VBO
        self._blur_quad_vao     = None   # VAO for blur passes
        self._blur_blit_vao     = None   # VAO for blit pass

    # -- public queries ------------------------------------------------------

    @property
    def theme(self) -> UITheme:
        return self._theme

    @theme.setter
    def theme(self, new_theme: UITheme) -> None:
        self._theme = new_theme
        # Rebuild every registered element so colours / fonts update immediately
        for elem in self._elements:
            elem._build(self.ctx, self.text_renderer)

    @property
    def focused_element(self) -> Optional[UIElement]:
        """Currently focused UI element (or *None*)."""
        return self._focused

    @property
    def wants_keyboard(self) -> bool:
        """*True* when a focusable element has keyboard focus (e.g. text input).

        Game code should check this before processing keyboard input::

            if not env.ui.wants_keyboard:
                # process game keys
        """
        return self._wants_keyboard

    @property
    def wants_mouse(self) -> bool:
        """*True* when the mouse is over a UI element."""
        return self._wants_mouse

    @property
    def show_stats(self) -> bool:
        """Show / hide the live performance stats overlay (also toggled by F2)."""
        return self._show_stats

    @show_stats.setter
    def show_stats(self, value: bool) -> None:
        self._show_stats = bool(value)
        if not self._show_stats and self._stats_panel is not None:
            self._stats_panel.release()
            self._stats_panel = None

    def update_stats(
        self,
        fps:      float,
        delta:    float,
        ups:      float = 0.0,
        fixed_dt: float = 0.0,
        elapsed:  float = 0.0,
    ) -> None:
        """Update cached performance values displayed in the stats overlay.

        Should be called once per frame by :class:`RootEnv` (already wired up
        automatically — user code normally need not call this).

        Args:
            fps:      Rolling-average frames per second.
            delta:    Current frame delta time in seconds.
            ups:      Fixed-update ticks per second (0 if not used).
            fixed_dt: Fixed update time-step in seconds (0 if not used).
            elapsed:  Total elapsed time since program start in seconds.
        """
        self._stat_fps      = fps
        self._stat_delta    = delta
        self._stat_ups      = ups
        self._stat_fixed_dt = fixed_dt
        self._stat_elapsed  = elapsed
        # Push latest fps sample to the graph ring-buffer (if panel is live)
        if self._stats_panel is not None:
            self._stats_panel.push_fps(fps)

    # -- element management --------------------------------------------------

    def add(self, element: UIElement) -> UIElement:
        """Register an element (and its children) with this manager."""
        element._set_manager(self)
        self._elements.append(element)
        element._build(self.ctx, self.text_renderer)
        return element

    def remove(self, element: UIElement) -> None:
        """Unregister and release GPU resources."""
        if self._focused is element:
            self.focus(None)
        element.release()
        element._manager = None
        if element in self._elements:
            self._elements.remove(element)

    # -- factory shortcuts ---------------------------------------------------

    def label(self, *segments, **kwargs) -> Label:
        """Create a :class:`Label`, add it, and return it."""
        lbl = Label(*segments, **kwargs)
        self.add(lbl)
        return lbl

    def button(self, text: str = '', on_click=None, **kwargs) -> Button:
        """Create a :class:`Button`, add it, and return it."""
        btn = Button(text=text, on_click=on_click, **kwargs)
        self.add(btn)
        return btn

    def switch(self, value: bool = False, on_change=None, **kwargs) -> Switch:
        """Create a :class:`Switch` toggle, add it, and return it."""
        sw = Switch(value=value, on_change=on_change, **kwargs)
        self.add(sw)
        return sw

    def checkbox(self, value: bool = False, on_change=None, **kwargs) -> Checkbox:
        """Create a :class:`Checkbox`, add it, and return it."""
        cb = Checkbox(value=value, on_change=on_change, **kwargs)
        self.add(cb)
        return cb

    def slider(self, start: float = 0.0, end: float = 1.0, **kwargs) -> Slider:
        """Create a :class:`Slider`, add it, and return it."""
        sl = Slider(start=start, end=end, **kwargs)
        self.add(sl)
        return sl

    def range_slider(self, start: float = 0.0, end: float = 1.0, **kwargs) -> RangeSlider:
        """Create a :class:`RangeSlider`, add it, and return it."""
        rs = RangeSlider(start=start, end=end, **kwargs)
        self.add(rs)
        return rs

    def input_field(self, placeholder: str = '', value: str = '', **kwargs) -> InputField:
        """Create an :class:`InputField`, add it, and return it."""
        f = InputField(placeholder=placeholder, value=value, **kwargs)
        self.add(f)
        return f

    def multi_line_input(self, placeholder: str = '', value: str = '', **kwargs) -> MultiLineInput:
        """Create a :class:`MultiLineInput`, add it, and return it."""
        m = MultiLineInput(placeholder=placeholder, value=value, **kwargs)
        self.add(m)
        return m

    def vbox(self, spacing: float = 0.0, align: str = 'left', **kwargs) -> VBox:
        """Create a :class:`VBox` container, add it, and return it."""
        from .containers import VBox
        c = VBox(spacing=spacing, align=align, **kwargs)
        self.add(c)
        return c

    def hbox(self, spacing: float = 0.0, align: str = 'top', **kwargs) -> HBox:
        """Create an :class:`HBox` container, add it, and return it."""
        c = HBox(spacing=spacing, align=align, **kwargs)
        self.add(c)
        return c

    def grid(self, columns: int = 1, **kwargs) -> Grid:
        """Create a :class:`Grid` container, add it, and return it."""
        c = Grid(columns=columns, **kwargs)
        self.add(c)
        return c

    def free_container(self, **kwargs) -> FreeContainer:
        """Create a :class:`FreeContainer`, add it, and return it."""
        c = FreeContainer(**kwargs)
        self.add(c)
        return c

    def scroll_container(self, **kwargs) -> ScrollContainer:
        """Create a :class:`ScrollContainer`, add it, and return it."""
        c = ScrollContainer(**kwargs)
        self.add(c)
        return c

    # -- focus ---------------------------------------------------------------

    def focus(self, element: Optional[UIElement]) -> None:
        if self._focused is element:
            return
        if self._focused is not None:
            self._focused.on_blur()
        self._focused = element
        if element is not None:
            element.on_focus()
        self._wants_keyboard = element is not None and element._focusable

    def focus_next(self) -> None:
        """Tab → move focus to the next focusable element."""
        self._cycle_focus(reverse=False)

    def focus_prev(self) -> None:
        """Shift+Tab → move focus to the previous focusable element."""
        self._cycle_focus(reverse=True)

    def _cycle_focus(self, reverse: bool) -> None:
        focusable = self._collect_focusable()
        if not focusable:
            return
        focusable.sort(key=lambda e: e._tab_index)
        if reverse:
            focusable.reverse()

        if self._focused is None:
            self.focus(focusable[0])
            return

        try:
            idx = focusable.index(self._focused)
            nxt = focusable[(idx + 1) % len(focusable)]
            self.focus(nxt)
        except ValueError:
            self.focus(focusable[0])

    def _collect_focusable(self) -> list[UIElement]:
        out: list[UIElement] = []
        for elem in self._elements:
            if elem._parent is None:
                self._walk_focusable(elem, out)
        return out

    @staticmethod
    def _walk_focusable(elem: UIElement, out: list[UIElement]) -> None:
        if elem._focusable and elem.visible and elem.enabled:
            out.append(elem)
        for child in elem._children:
            UIManager._walk_focusable(child, out)

    # -- per-frame -----------------------------------------------------------

    def process_input(self, mouse: Mouse, keyboard: Keyboard) -> None:
        """Dispatch mouse / keyboard events to UI elements.

        Called by :class:`RootEnv` each frame **before** ``env.update()``.
        """
        from ..input import KeyState, Keys, MouseButtons

        self._keyboard = keyboard
        self._mouse    = mouse
        mx, my = mouse.position.x, mouse.position.y

        # -- hover detection --
        new_hovered = self._find_hovered_element(mx, my)

        # Dispatch hover enter / exit
        if new_hovered is not self._hovered:
            if self._hovered is not None:
                self._hovered.on_hover_exit()
            if new_hovered is not None:
                new_hovered.on_hover_enter()
                # RELAY: also notify ancestor chain
                from .base import MouseMode
                if getattr(new_hovered, 'mouse_mode', MouseMode.BLOCK) == MouseMode.RELAY:
                    p = new_hovered._parent
                    while p is not None:
                        p.on_hover_enter()
                        if getattr(p, 'mouse_mode', MouseMode.BLOCK) != MouseMode.RELAY:
                            break
                        p = p._parent
        self._hovered = new_hovered
        self._wants_mouse = new_hovered is not None

        # -- mouse LEFT press --
        if MouseButtons.LEFT in mouse.just_pressed:
            if new_hovered is not None:
                self._pressed_on = new_hovered
                new_hovered.on_mouse_press(mx, my)
                # RELAY: bubble press up the parent chain
                from .base import MouseMode as _MouseMode
                if getattr(new_hovered, 'mouse_mode', _MouseMode.BLOCK) == _MouseMode.RELAY:
                    p = new_hovered._parent
                    while p is not None:
                        p.on_mouse_press(mx, my)
                        if getattr(p, 'mouse_mode', _MouseMode.BLOCK) != _MouseMode.RELAY:
                            break
                        p = p._parent
                if new_hovered._focusable:
                    self.focus(new_hovered)
            else:
                self.focus(None)

        # -- mouse LEFT drag (button still held, we have a pressed target) --
        if MouseButtons.LEFT in mouse.pressed and self._pressed_on is not None:
            dx = mx - self._prev_mx
            dy = my - self._prev_my
            if dx != 0 or dy != 0:
                self._pressed_on.on_mouse_drag(mx, my, dx, dy)

        # -- mouse LEFT release --
        if MouseButtons.LEFT in mouse.just_released:
            if self._pressed_on is not None:
                self._pressed_on.on_mouse_release(mx, my)
                self._pressed_on = None

        self._prev_mx = mx
        self._prev_my = my

        # -- tab navigation --
        if keyboard.get_key(Keys.TAB, KeyState.JUST_PRESSED):
            focused_consumes_tab = (
                self._focused is not None and self._focused._consumes_tab
            )
            is_ctrl_tab = (
                keyboard.get_key(Keys.LEFT_CONTROL)
                or keyboard.get_key(Keys.RIGHT_CONTROL)
            )
            if focused_consumes_tab and not is_ctrl_tab:
                # Let MultiLineInput (and similar) handle Tab itself
                self._focused.on_key_press(Keys.TAB)  # type: ignore[union-attr]
            else:
                # Normal Tab / Shift+Tab / Ctrl+Tab focus cycle
                if keyboard.get_key(Keys.LEFT_SHIFT) or keyboard.get_key(Keys.RIGHT_SHIFT):
                    self.focus_prev()
                else:
                    self.focus_next()

        # -- forward other keys to focused element --
        if self._focused is not None:
            for key in keyboard.just_pressed:
                if key != Keys.TAB:
                    self._focused.on_key_press(key)

        # -- forward char input to focused element --
        if self._focused is not None and keyboard.char_buffer:
            self._focused.on_char_input(list(keyboard.char_buffer))

        # -- mouse scroll (dispatch to hovered element; bubble up parent chain) --
        # This lets a ScrollContainer receive scroll even when its content
        # child (e.g. a Label/Button inside it) is the topmost hovered element.
        if mouse.scroll.y != 0 and new_hovered is not None:
            target = new_hovered
            while target is not None:
                target.on_scroll(mouse.scroll.y)
                target = target._parent

        # -- mark keyboard consumed when a focusable element has focus --
        keyboard.is_consumed = self._wants_keyboard

        # -- F3 toggles debug mode (always active, regardless of focus) --
        if keyboard.get_key(Keys.F3, KeyState.JUST_PRESSED):
            self.debug_mode = not self.debug_mode

        # -- F2 toggles stats overlay (always active, regardless of focus) --
        if keyboard.get_key(Keys.F2, KeyState.JUST_PRESSED):
            self.show_stats = not self.show_stats

        # Update debug hover — includes PASS_THROUGH containers so they show
        # in the F3 panel even though they are transparent to click events.
        if self.debug_mode:
            self._debug_hovered = self._find_debug_hovered(mx, my)
        else:
            self._debug_hovered = None

    def _all_visible_elements(self) -> list[UIElement]:
        """Flatten the element tree (visible nodes only), visiting each node
        exactly once.  Only root elements (``_parent is None``) start a walk;
        children are reached via their parent's recursion."""
        out: list[UIElement] = []
        for elem in self._elements:
            if elem._parent is None:
                self._walk_visible(elem, out)
        return out

    @staticmethod
    def _walk_visible(elem: UIElement, out: list[UIElement]) -> None:
        if not elem.visible:
            return
        out.append(elem)
        for child in elem._children:
            UIManager._walk_visible(child, out)

    # -- recursive mouse hit-test ----------------------------------------

    @staticmethod
    def _hit_test(elem: UIElement, mx: float, my: float) -> Optional[UIElement]:
        """Depth-first search for the innermost hovered element.

        * Children are tested before the parent (deepest/last-rendered wins).
        * ``IGNORE``       — skip this element AND its children.
        * ``PASS_THROUGH`` — never selected, but children are tested.
        * ``BLOCK``        — normal: selectable if enabled & contains_point.
        * ``RELAY``        — same hit behaviour as BLOCK; the caller also
                             bubbles events to the parent chain.
        """
        from .base import MouseMode
        if not elem.visible:
            return None
        mm = getattr(elem, 'mouse_mode', MouseMode.BLOCK)
        if mm == MouseMode.IGNORE:
            return None

        # Search children last-first so the highest-rendered child wins.
        child_hit: Optional[UIElement] = None
        for child in sorted(elem._children, key=lambda c: c.z_index):
            hit = UIManager._hit_test(child, mx, my)
            if hit is not None:
                child_hit = hit
        if child_hit is not None:
            return child_hit

        # No child matched — test self.
        if mm == MouseMode.PASS_THROUGH:
            return None
        if elem.enabled and elem.contains_point(mx, my):
            return elem
        return None

    def _find_hovered_element(self, mx: float, my: float) -> Optional[UIElement]:
        """Find the single topmost interactive element under *(mx, my)*.

        Root elements are tested in ascending z_index order so the last /
        highest-z root wins when multiple roots overlap.
        """
        roots = sorted(
            (e for e in self._elements if e._parent is None and e.visible),
            key=lambda e: e.z_index,
        )
        result: Optional[UIElement] = None
        for root in roots:
            hit = self._hit_test(root, mx, my)
            if hit is not None:
                result = hit
        return result

    # -- debug hit-test (includes PASS_THROUGH containers) ---------------

    @staticmethod
    def _debug_hit_test(elem: UIElement, mx: float, my: float) -> Optional[UIElement]:
        """Like ``_hit_test`` but PASS_THROUGH elements can be selected.

        Only ``IGNORE`` blocks traversal.  Used in debug mode so that
        containers show their info in the F3 panel even though they are
        transparent to normal click events.
        """
        from .base import MouseMode
        if not elem.visible:
            return None
        if getattr(elem, 'mouse_mode', MouseMode.BLOCK) == MouseMode.IGNORE:
            return None
        # Children last-first so the topmost-rendered wins.
        child_hit: Optional[UIElement] = None
        for child in sorted(elem._children, key=lambda c: c.z_index):
            hit = UIManager._debug_hit_test(child, mx, my)
            if hit is not None:
                child_hit = hit
        if child_hit is not None:
            return child_hit
        if elem.contains_point(mx, my):
            return elem
        return None

    def _find_debug_hovered(self, mx: float, my: float) -> Optional[UIElement]:
        """Return the deepest visible element under cursor, including containers."""
        roots = sorted(
            (e for e in self._elements if e._parent is None and e.visible),
            key=lambda e: e.z_index,
        )
        result: Optional[UIElement] = None
        for root in roots:
            hit = self._debug_hit_test(root, mx, my)
            if hit is not None:
                result = hit
        return result

    def update(self, dt: float) -> None:
        for elem in self._elements:
            if elem._parent is None:
                elem.update(dt)

    def draw(self) -> None:
        """Render all visible elements sorted by z-index (ascending).

        Only top-level registered elements are iterated here; containers
        draw their own children recursively in their own ``draw()`` method.
        Walking into children at this level would cause double-rendering.
        """
        # ── Blur pre-pass ──────────────────────────────────────────────────
        # If any top-level visible element has blur=True, capture the current
        # screen content and run a two-pass Gaussian blur so each blurred
        # element can show a frosted-glass background when drawn.
        blurred_elems = [
            e for e in self._elements
            if e.visible and e._parent is None and getattr(e, 'blur', False)
        ]
        if blurred_elems:
            vp = self.ctx.viewport
            w, h = int(vp[2]), int(vp[3])
            if self._blur_fbo_size != (w, h) or self._blur_capture_fbo is None:
                self._setup_blur_fbos(w, h)
            # Use the maximum blur_radius across all blurred elements
            max_r = max(getattr(e, 'blur_radius', 10.0) for e in blurred_elems)
            self._capture_and_blur(max_r)

        # ── Main element draw loop ─────────────────────────────────────────
        elements = sorted(
            (e for e in self._elements if e.visible and e._parent is None),
            key=lambda e: e.z_index,
        )
        for elem in elements:
            if getattr(elem, 'blur', False) and blurred_elems:
                # Draw blurred scene background under this element first
                self._draw_blur_behind(elem)
                self.shape_renderer.flush_queue()
            elem.draw(self.ctx)

        if self.debug_mode:
            # Color-coded outlines: walk ALL visible elements (including
            # container children) so every hitbox gets an outline.
            # _debug_hovered (includes PASS_THROUGH) takes priority for the
            # cyan highlight so containers show up when hovered in debug mode.
            all_elems = self._all_visible_elements()
            all_elems.sort(key=lambda e: e.z_index)
            for elem in all_elems:
                if elem is self._debug_hovered or (self._debug_hovered is None and elem is self._hovered):
                    elem.draw_debug_outline((0.00, 1.00, 1.00, 0.50))
                elif elem is self._focused:
                    elem.draw_debug_outline((1.00, 1.00, 0.00, 0.45))
                else:
                    elem.draw_debug_outline((0.50, 0.50, 0.50, 0.18))

        # Flush all queued shapes (UI elements + debug outlines)
        self.shape_renderer.flush_queue()

        # ── Debug side-panel ───────────────────────────────────────────────
        if self.debug_mode:
            debug_target = self._debug_hovered if self._debug_hovered is not None else self._hovered
            if debug_target is not None:
                if self._debug_panel is None:
                    self._debug_panel = _UIDebugPanel(self)
                self._debug_panel.draw(
                    debug_target,
                    self._window_size.x,
                    self._window_size.y,
                )
        else:
            # Release panel resources when debug mode is turned off
            if self._debug_panel is not None:
                self._debug_panel.release()
                self._debug_panel = None

        # ── Stats overlay (F2) ─────────────────────────────────────────────
        if self._show_stats:
            if self._stats_panel is None:
                self._stats_panel = _UIStatsPanel(self)
            mins, secs = divmod(int(self._stat_elapsed), 60)
            hrs,  mins = divmod(mins, 60)
            elapsed_str = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs else f"{mins:02d}:{secs:02d}"
            lines: list[str] = [
                f"  FPS        {self._stat_fps:.1f}",
                f"  Frame time {self._stat_delta * 1000.0:.2f} ms",
            ]
            if self._stat_fixed_dt > 0.0:
                lines.append(f"  UPS        {self._stat_ups:.1f}")
                lines.append(f"  Phys step  {self._stat_fixed_dt * 1000.0:.2f} ms")
            lines.append(f"  Elapsed    {elapsed_str}")
            self._stats_panel.draw(lines, self._window_size.x, self._window_size.y)
        else:
            if self._stats_panel is not None:
                self._stats_panel.release()
                self._stats_panel = None

    # -- resize --------------------------------------------------------------

    def on_resize(self, width: float, height: float) -> None:
        """Re-layout all anchored elements after a window resize."""
        self._window_size.set(width, height)
        for elem in self._elements:
            if elem._parent is None:
                elem.layout(0, 0, width, height)
        # Invalidate blur FBOs so they are recreated at the new size.
        self._blur_fbo_size = (0, 0)

    # -- blur / frosted-glass helpers ----------------------------------------

    def _setup_blur_fbos(self, w: int, h: int) -> None:
        """(Re-)create the three ping-pong FBOs used for the blur effect.

        Called lazily the first time a blurred element is drawn, and again
        whenever the window is resized.  All existing FBO objects are
        released before creating new ones.
        """
        # Release old objects if they exist
        for attr in ('_blur_capture_fbo', '_blur_ping_fbo', '_blur_pong_fbo'):
            fbo = getattr(self, attr, None)
            if fbo is not None:
                fbo.release()
                setattr(self, attr, None)
        for attr in ('_blur_capture_tex', '_blur_ping_tex', '_blur_pong_tex'):
            tex = getattr(self, attr, None)
            if tex is not None:
                tex.release()
                setattr(self, attr, None)

        ctx = self.ctx
        self._blur_capture_tex = ctx.texture((w, h), 4)
        self._blur_ping_tex    = ctx.texture((w, h), 4)
        self._blur_pong_tex    = ctx.texture((w, h), 4)
        self._blur_capture_fbo = ctx.framebuffer(color_attachments=[self._blur_capture_tex])
        self._blur_ping_fbo    = ctx.framebuffer(color_attachments=[self._blur_ping_tex])
        self._blur_pong_fbo    = ctx.framebuffer(color_attachments=[self._blur_pong_tex])

        # Build shaders once (they're reused across all resizes)
        if self._blur_prog is None:
            self._blur_prog = ctx.program(
                vertex_shader="""
                #version 430
                in vec2 in_vertex;
                out vec2 v_uv;
                void main() {
                    v_uv = in_vertex * 0.5 + 0.5;
                    gl_Position = vec4(in_vertex, 0.0, 1.0);
                }
                """,
                fragment_shader="""
                #version 430
                uniform sampler2D u_tex;
                uniform vec2 u_resolution;
                uniform vec2 u_direction;
                uniform float u_radius;
                in vec2 v_uv;
                out vec4 f_color;
                void main() {
                    vec4  col    = vec4(0.0);
                    float sigma  = max(u_radius / 3.0, 0.001);
                    float total  = 0.0;
                    int   n      = int(min(ceil(u_radius * 2.0), 32.0));
                    for (int i = -n; i <= n; i++) {
                        float w   = exp(-float(i)*float(i) / (2.0*sigma*sigma));
                        vec2  uv  = v_uv + float(i) * u_direction / u_resolution;
                        col  += texture(u_tex, uv) * w;
                        total += w;
                    }
                    f_color = col / total;
                }
                """,
            )

        if self._blur_blit_prog is None:
            self._blur_blit_prog = ctx.program(
                vertex_shader="""
                #version 430
                uniform vec2 resolution;
                uniform vec2 u_pos;
                uniform vec2 u_size;
                in vec2 in_vertex;
                out vec2 v_screen_uv;
                out vec2 v_local_px;
                void main() {
                    vec2 screen_pos = u_pos + u_size * (in_vertex * 0.5 + 0.5);
                    v_screen_uv = vec2(screen_pos.x / resolution.x,
                                      1.0 - screen_pos.y / resolution.y);
                    // Local pixel offset from element centre (for SDF)
                    v_local_px = in_vertex * u_size * 0.5;
                    vec2 ndc = (screen_pos / resolution) * 2.0 - 1.0;
                    ndc.y = -ndc.y;
                    gl_Position = vec4(ndc, 0.0, 1.0);
                }
                """,
                fragment_shader="""
                #version 430
                uniform sampler2D u_tex;
                uniform vec2  u_size;
                uniform float u_corner_r;
                in vec2 v_screen_uv;
                in vec2 v_local_px;
                out vec4 f_color;

                float roundedBoxSDF(vec2 center, vec2 half_size, float radius) {
                    vec2 q = abs(center) - half_size + radius;
                    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - radius;
                }

                void main() {
                    float dist = roundedBoxSDF(v_local_px, u_size * 0.5, u_corner_r);
                    float alpha = 1.0 - smoothstep(-1.0, 1.0, dist);
                    if (alpha < 0.001) discard;
                    f_color = texture(u_tex, v_screen_uv) * vec4(1.0, 1.0, 1.0, alpha);
                }
                """,
            )

        # Build a shared unit quad VBO/VAO reused for all passes
        if self._blur_quad_vbo is None:
            _q = np.array([
                -1.0, -1.0,   1.0, -1.0,  -1.0,  1.0,
                 1.0, -1.0,  -1.0,  1.0,   1.0,  1.0,
            ], dtype='f4')
            self._blur_quad_vbo  = ctx.buffer(_q.tobytes())
            self._blur_quad_vao  = ctx.vertex_array(
                self._blur_prog, [(self._blur_quad_vbo, '2f', 'in_vertex')])
            self._blur_blit_vao  = ctx.vertex_array(
                self._blur_blit_prog, [(self._blur_quad_vbo, '2f', 'in_vertex')])

        self._blur_fbo_size = (w, h)

    def _capture_and_blur(self, blur_radius: float) -> None:
        """Capture the current screen into the capture FBO, then run a
        separable Gaussian blur (horizontal + vertical) into _blur_pong_fbo.

        The blurred texture can then be sampled via ``_blur_pong_tex``."""
        vp = self.ctx.viewport
        w, h = float(vp[2]), float(vp[3])

        # Copy screen → capture FBO (GPU-side blit)
        try:
            self.ctx.copy_framebuffer(
                dst=self._blur_capture_fbo,
                src=self.ctx.screen,
            )
        except Exception:
            # Fallback: CPU readback (slower ~1-3 ms but always works)
            data = self.ctx.screen.read(components=4)
            self._blur_capture_tex.write(data)

        # Horizontal pass:  capture → ping
        self._blur_ping_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self._blur_capture_tex.use(0)
        self._blur_prog['u_tex']        = 0
        self._blur_prog['u_resolution'] = (w, h)
        self._blur_prog['u_direction']  = (1.0, 0.0)
        self._blur_prog['u_radius']     = float(blur_radius)
        self._blur_quad_vao.render(moderngl.TRIANGLES)

        # Vertical pass:    ping → pong
        self._blur_pong_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self._blur_ping_tex.use(0)
        self._blur_prog['u_direction'] = (0.0, 1.0)
        self._blur_quad_vao.render(moderngl.TRIANGLES)

        # Return to the default screen FBO
        self.ctx.screen.use()

    def _draw_blur_behind(self, elem: UIElement) -> None:
        """Draw a textured quad covering *elem*'s screen rect, sampling from
        the pre-computed blurred texture (_blur_pong_tex).

        Call this immediately before ``elem.draw()`` when ``elem.blur`` is
        True.
        """
        vp      = self.ctx.viewport
        w, h    = float(vp[2]), float(vp[3])
        rx, ry, rw, rh = elem.get_screen_rect()
        ctx     = self.ctx
        ctx.enable(moderngl.BLEND)
        self._blur_pong_tex.use(0)
        self._blur_blit_prog['u_tex']        = 0
        self._blur_blit_prog['resolution']   = (w, h)
        self._blur_blit_prog['u_pos']        = (float(rx), float(ry))
        self._blur_blit_prog['u_size']       = (float(rw), float(rh))
        # Pass corner radius so the blurred quad clips to rounded corners
        corner_r = getattr(elem, '_corner_r', 0.0)
        self._blur_blit_prog['u_corner_r']   = float(corner_r)
        self._blur_blit_vao.render(moderngl.TRIANGLES)
