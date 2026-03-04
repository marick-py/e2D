"""
Pivot system and UIElement base class for e2D UI.
"""

from __future__ import annotations
import inspect as _inspect
import os as _os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import UIManager

from ..vectors import Vector2D, V2
from .._pivot import Pivot, resolve_pivot, _PIVOTS_ENUM_MAP

# Absolute path of the e2D package directory.  Used to locate the first
# call-stack frame outside the library when capturing _debug_source.
_e2d_dir: str = _os.path.normcase(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
)


# ---------------------------------------------------------------------------
# MouseMode — controls how an element interacts with mouse hit-testing
# ---------------------------------------------------------------------------

class MouseMode:
    """Mouse interaction mode for a :class:`UIElement`.

    Assign to ``element.mouse_mode`` to control how the element participates
    in mouse hit-testing::

        btn.mouse_mode = MouseMode.BLOCK        # default for interactive widgets
        panel.mouse_mode = MouseMode.PASS_THROUGH  # layout containers
        overlay.mouse_mode = MouseMode.IGNORE   # completely invisible to mouse
        sc.mouse_mode = MouseMode.RELAY         # hovered + events bubble to parent

    Constants
    ---------
    ``BLOCK``
        Default for interactive elements (Button, Slider, etc.).
        The element is eligible to be hovered.  Children are tested first
        (deepest child wins); if none match, the element itself captures.

    ``RELAY``
        Like ``BLOCK`` — the element can be hovered — but after dispatching
        ``on_hover_enter``, ``on_mouse_press`` and ``on_mouse_release``, the
        event is also forwarded to the element's parent.  Useful for
        containers that want to react to interactions *inside* them even
        when a child handles the primary event.

    ``PASS_THROUGH``
        The element is *transparent* to mouse hit-testing: it is never
        selected as hovered.  Its children are still tested normally.
        Default for all layout containers (VBox, HBox, Grid, FreeContainer).

    ``IGNORE``
        Completely invisible to mouse.  Neither the element nor any of its
        children are tested or hovered.
    """

    BLOCK        = 'block'
    RELAY        = 'relay'
    PASS_THROUGH = 'pass_through'
    IGNORE       = 'ignore'


# ---------------------------------------------------------------------------
# UIElement — base class for every UI widget
# ---------------------------------------------------------------------------

class UIElement:
    """Abstract base class for all UI elements.

    Provides position, size, pivot, anchor-based layout, z-index,
    visibility, opacity, focus management, and a parent/child tree.
    """

    def __init__(
        self,
        position: Vector2D | tuple[float, float] = (0.0, 0.0),
        size: Vector2D | tuple[float, float] = (0.0, 0.0),
        pivot: Pivot = Pivot.TOP_LEFT,
        anchor_min: tuple[float, float] = (0.0, 0.0),
        anchor_max: tuple[float, float] = (0.0, 0.0),
        margin: float | tuple[float, ...] = 0.0,
        padding: float | tuple[float, ...] = 0.0,
        z_index: int = 0,
        tab_index: int = 0,
        visible: bool = True,
        enabled: bool = True,
        opacity: float = 1.0,
        size_mode: str = 'fixed',
        mouse_mode: str = MouseMode.BLOCK,
        max_width:  float | None = None,
        max_height: float | None = None,
        blur: bool = False,
        blur_radius: float = 10.0,
    ) -> None:
        self._position = (
            V2(float(position[0]), float(position[1]))
            if not isinstance(position, Vector2D) else position
        )
        self._size = (
            V2(float(size[0]), float(size[1]))
            if not isinstance(size, Vector2D) else size
        )
        self.pivot: Pivot = pivot
        self.anchor_min: tuple[float, float] = anchor_min
        self.anchor_max: tuple[float, float] = anchor_max
        self.margin: tuple[float, float, float, float] = _norm4(margin)
        self.padding: tuple[float, float, float, float] = _norm4(padding)
        self.z_index: int = z_index
        self.visible: bool = visible
        self.enabled: bool = enabled
        self.opacity: float = opacity

        # Focus / tab
        self._focused: bool = False
        self._focusable: bool = False
        self._tab_index: int = tab_index
        # Set True in subclasses that want to consume Tab (e.g. MultiLineInput)
        self._consumes_tab: bool = False

        # Dirty flag — subclasses set True when GPU rebuild is needed
        self._dirty: bool = True
        # Size mode — consulted by parent containers when computing layout.
        # 'fixed' = size in pixels (default), 'percent' = 0.0-1.0 fraction
        # of parent inner rect, 'auto' = fit content.
        self.size_mode: str = size_mode
        # Mouse interaction mode — see MouseMode constants.
        self.mouse_mode: str = mouse_mode
        # Optional size caps respected by VBox/HBox when align='stretch'.
        self.max_width:  float | None = max_width
        self.max_height: float | None = max_height

        # Blur / frosted-glass effect.
        # When True, UIManager renders a Gaussian-blurred copy of the scene
        # content that lies behind this element before drawing the element.
        # Only works when the element is a direct child of UIManager
        # (top-level registered element).
        self.blur: bool = blur
        # Gaussian blur radius in pixels (higher = more blur, heavier GPU cost).
        self.blur_radius: float = float(blur_radius)

        # Tree
        self._parent: Optional[UIElement] = None
        self._children: list[UIElement] = []
        self._manager: Optional[UIManager] = None

        # Debug — capture creation site: first stack frame outside e2D.
        self._debug_source: str = ""
        try:
            for _fi in _inspect.stack()[1:]:
                _fn = _os.path.normcase(_os.path.abspath(_fi.filename))
                if not _fn.startswith(_e2d_dir):
                    self._debug_source = (
                        f"{_os.path.basename(_fi.filename)}:{_fi.lineno}"
                    )
                    break
        except Exception:
            pass

    # -- properties ----------------------------------------------------------

    @property
    def position(self) -> Vector2D:
        return self._position

    @position.setter
    def position(self, value: Vector2D | tuple[float, float]) -> None:
        if isinstance(value, (tuple, list)):
            self._position.set(float(value[0]), float(value[1]))
        else:
            self._position = value
        # Position changes are handled by shader uniforms — no rebuild needed.
    
    @property
    def size(self) -> Vector2D:
        return self._size

    @size.setter
    def size(self, value: Vector2D | tuple[float, float]) -> None:
        if isinstance(value, (tuple, list)):
            self._size.set(float(value[0]), float(value[1]))
        else:
            self._size = value
        self._dirty = True

    @property
    def focused(self) -> bool:
        return self._focused

    def _effective_opacity(self) -> float:
        """Return the *cumulative* opacity for this element.

        The effective opacity is the product of this element's ``opacity``
        and all its ancestors' ``opacity`` values, clamped to ``[0, 1]``.
        This allows a semi-transparent parent container to dim all its children
        proportionally without each child needing explicit opacity overrides.

        Usage in custom widget draw() methods::

            alpha = self._effective_opacity()
            sr.draw_rect(..., color=(*bg_color.rgb, bg_color.a * alpha))
        """
        eff = self.opacity
        p = self._parent
        while p is not None:
            eff *= p.opacity
            p = p._parent
        return max(0.0, min(1.0, eff))

    # -- screen rect ---------------------------------------------------------

    def get_screen_rect(self) -> tuple[float, float, float, float]:
        """Return ``(x, y, width, height)`` in screen pixels."""
        ox, oy = self.pivot.offset(self._size.x, self._size.y)
        return (
            self._position.x + ox,
            self._position.y + oy,
            self._size.x,
            self._size.y,
        )

    def contains_point(self, x: float, y: float) -> bool:
        """Return *True* if *(x, y)* is inside this element."""
        rx, ry, rw, rh = self.get_screen_rect()
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    # -- tree ----------------------------------------------------------------

    def add_child(self, child: UIElement) -> None:
        child._parent = self
        self._children.append(child)
        if self._manager:
            child._set_manager(self._manager)

    def remove_child(self, child: UIElement) -> None:
        child._parent = None
        if child in self._children:
            self._children.remove(child)

    def _set_manager(self, manager: UIManager) -> None:
        """Recursively propagate the manager reference."""
        self._manager = manager
        for child in self._children:
            child._set_manager(manager)

    # -- focus ---------------------------------------------------------------

    def on_focus(self) -> None:
        """Called when this element gains focus."""
        self._focused = True

    def on_blur(self) -> None:
        """Called when this element loses focus."""
        self._focused = False

    # -- interaction event hooks (override in subclasses) -------------------

    def on_hover_enter(self) -> None:
        """Called once when the mouse cursor first enters this element."""
        pass

    def on_hover_exit(self) -> None:
        """Called once when the mouse cursor leaves this element."""
        pass

    def on_mouse_press(self, mx: float, my: float) -> None:
        """Called when mouse LEFT is pressed while over this element."""
        pass

    def on_mouse_release(self, mx: float, my: float) -> None:
        """Called when mouse LEFT is released (regardless of current position)
        if this element was the one pressed."""
        pass

    def on_mouse_drag(self, mx: float, my: float, dx: float, dy: float) -> None:
        """Called every frame while mouse LEFT is held and this element was
        the pressed target.  *dx/dy* are pixel deltas since last frame."""
        pass

    def on_char_input(self, chars: list[str]) -> None:
        """Called each frame with the characters typed since the last frame.

        Only called when this element has focus and ``chars`` is non-empty.
        Override in text-input subclasses.
        """
        pass

    def on_scroll(self, dy: float) -> None:
        """Called when the mouse wheel scrolls over this element.

        *dy* is positive for scroll-up, negative for scroll-down.
        """
        pass

    def on_key_press(self, key: int) -> None:
        """Called for every key in ``keyboard.just_pressed`` while this element
        has focus (Tab is consumed by UIManager unless ``_consumes_tab`` is True)."""
        pass

    # -- layout (Godot-style anchors) ----------------------------------------

    def layout(self, px: float, py: float, pw: float, ph: float) -> None:
        """Recompute position/size from anchors relative to parent rect.

        If both ``anchor_min`` and ``anchor_max`` are ``(0, 0)`` the element
        uses absolute positioning and this method is a no-op.

        **Per-axis behaviour** — each axis is handled independently:

        * When ``amax[i] != amin[i]`` the axis *stretches*: size is computed
          from the anchor fraction span minus the relevant margins, and
          position is set at ``amin[i] * parent_size + margin``.
        * When ``amax[i] == amin[i]`` the axis is a *point anchor*: the
          element keeps its current ``_size[i]`` (natural/fixed size) and
          is positioned at ``amin[i] * parent_size + margin``.  Use a
          negative margin to offset back by the element's own size (e.g.
          ``margin_left = -width`` to right-align against a right anchor).
        """
        amin = self.anchor_min
        amax = self.anchor_max
        if amin == (0.0, 0.0) and amax == (0.0, 0.0):
            return
        m = self.margin
        # X axis
        if amax[0] != amin[0]:
            new_x = px + amin[0] * pw + m[3]
            new_w = max(0.0, (amax[0] - amin[0]) * pw - m[1] - m[3])
        else:
            new_x = px + amin[0] * pw + m[3]
            new_w = self._size.x          # point anchor — keep natural size
        # Y axis
        if amax[1] != amin[1]:
            new_y = py + amin[1] * ph + m[0]
            new_h = max(0.0, (amax[1] - amin[1]) * ph - m[0] - m[2])
        else:
            new_y = py + amin[1] * ph + m[0]
            new_h = self._size.y          # point anchor — keep natural size
        self._position.set(new_x, new_y)
        self._size.set(new_w, new_h)
        self._dirty = True

    # -- lifecycle (override in subclasses) ----------------------------------

    def _build(self, ctx, text_renderer) -> None:
        """Create GPU resources.  Called by UIManager when the element is
        added or when the context becomes available."""
        pass

    def update(self, dt: float) -> None:
        """Per-frame logic.  Called by UIManager every frame."""
        for child in self._children:
            if child.enabled:
                child.update(dt)

    def draw(self, ctx) -> None:
        """Render this element.  Called by UIManager in z-order."""
        pass

    def _debug_info(self) -> list[tuple[str, str]]:
        """Return *(key, value)* pairs shown in the debug side panel.

        Override in widget subclasses to expose widget-specific state.
        The base implementation reports position, size, pivot, flags.
        """
        rx, ry, rw, rh = self.get_screen_rect()
        rows: list[tuple[str, str]] = [
            ("pos",     f"{rx:.0f}, {ry:.0f}"),
            ("size",    f"{rw:.0f} x {rh:.0f}"),
            ("pivot",   repr(self.pivot)),
            ("z-index", str(self.z_index)),
            ("visible", "yes" if self.visible else "no"),
            ("enabled", "yes" if self.enabled else "NO"),
            ("opacity", f"{self.opacity:.2f}"),
            ("focused", "yes" if self._focused else "no"),
        ]
        if hasattr(self, '_is_hovered'):
            rows.append(("hovered", "yes" if self._is_hovered else "no"))  # type: ignore[attr-defined]
        return rows

    def draw_debug_outline(self, color=(1.0, 0.0, 1.0, 0.5)) -> None:
        """Draw a debug outline around this element's screen rect."""
        if not self.visible or self._manager is None:
            return

        sr = self._manager.shape_renderer
        rx, ry, rw, rh = self.get_screen_rect()

        sr.draw_rect(
            V2(rx, ry), V2(rw, rh),
            color=color,
            border_width=1.0,
            layer=1000,
        )

    def release(self) -> None:
        """Free GPU resources.  Called when removed from UIManager."""
        for child in self._children:
            child.release()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _norm4(v: float | tuple | list) -> tuple[float, float, float, float]:
    """Normalise a spacing value to a 4-tuple (top, right, bottom, left)."""
    if isinstance(v, (int, float)):
        f = float(v)
        return (f, f, f, f)
    n = len(v)
    if n == 0:
        return (0.0, 0.0, 0.0, 0.0)
    if n == 1:
        f = float(v[0])  # type: ignore[index]
        return (f, f, f, f)
    if n == 2:
        return (float(v[0]), float(v[1]), float(v[0]), float(v[1]))  # type: ignore[index]
    return (float(v[0]), float(v[1]), float(v[2]), float(v[3]))  # type: ignore[index]
