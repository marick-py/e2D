"""
Pivot system and UIElement base class for e2D UI.
"""

from __future__ import annotations
from typing import Optional, ClassVar, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .manager import UIManager

from ..vectors import Vector2D, V2


# ---------------------------------------------------------------------------
# Pivot
# ---------------------------------------------------------------------------

class Pivot:
    """Normalised anchor/pivot point.

    ``(0, 0)`` = top-left, ``(1, 1)`` = bottom-right.

    Pre-defined constants::

        Pivot.TOP_LEFT      Pivot.TOP_MIDDLE    Pivot.TOP_RIGHT
        Pivot.LEFT          Pivot.CENTER        Pivot.RIGHT
        Pivot.BOTTOM_LEFT   Pivot.BOTTOM_MIDDLE Pivot.BOTTOM_RIGHT

    Custom pivot::

        Pivot.custom(0.3, 0.7)
        Pivot.from_vector(V2(0.3, 0.7))
    """
    __slots__ = ('x', 'y', '_name')

    # Pre-defined constants (populated after class body)
    TOP_LEFT:      ClassVar[Pivot]
    TOP_MIDDLE:    ClassVar[Pivot]
    TOP_RIGHT:     ClassVar[Pivot]
    LEFT:          ClassVar[Pivot]
    CENTER:        ClassVar[Pivot]
    RIGHT:         ClassVar[Pivot]
    BOTTOM_LEFT:   ClassVar[Pivot]
    BOTTOM_MIDDLE: ClassVar[Pivot]
    BOTTOM_RIGHT:  ClassVar[Pivot]

    def __init__(self, x: float, y: float, name: str = '') -> None:
        self.x = float(x)
        self.y = float(y)
        self._name = name

    # -- factories -----------------------------------------------------------

    @classmethod
    def custom(cls, x: float, y: float) -> Pivot:
        """Create a custom pivot from normalised coordinates."""
        return cls(x, y, f'custom({x:.2f}, {y:.2f})')

    @classmethod
    def from_vector(cls, v: Vector2D) -> Pivot:
        """Create a custom pivot from a :class:`Vector2D`."""
        return cls(v.x, v.y, f'custom({v.x:.2f}, {v.y:.2f})')

    # -- helpers -------------------------------------------------------------

    def offset(self, width: float, height: float) -> tuple[float, float]:
        """Return ``(-width * x, -height * y)`` — the translation needed so
        that the pivot coincides with the element's position."""
        return (-width * self.x, -height * self.y)

    # -- dunder --------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Pivot):
            return self.x == other.x and self.y == other.y
        # Backward compat with the old ``Pivots`` enum if it leaks through
        val = getattr(other, 'value', None)
        if isinstance(val, int):
            compat = _PIVOTS_ENUM_MAP.get(val)
            if compat is not None:
                return self.x == compat.x and self.y == compat.y
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        if self._name:
            return f'Pivot.{self._name}'
        return f'Pivot({self.x}, {self.y})'


# Pre-defined pivots (set as class attributes after class body)
Pivot.TOP_LEFT      = Pivot(0.0, 0.0, 'TOP_LEFT')
Pivot.TOP_MIDDLE    = Pivot(0.5, 0.0, 'TOP_MIDDLE')
Pivot.TOP_RIGHT     = Pivot(1.0, 0.0, 'TOP_RIGHT')
Pivot.LEFT          = Pivot(0.0, 0.5, 'LEFT')
Pivot.CENTER        = Pivot(0.5, 0.5, 'CENTER')
Pivot.RIGHT         = Pivot(1.0, 0.5, 'RIGHT')
Pivot.BOTTOM_LEFT   = Pivot(0.0, 1.0, 'BOTTOM_LEFT')
Pivot.BOTTOM_MIDDLE = Pivot(0.5, 1.0, 'BOTTOM_MIDDLE')
Pivot.BOTTOM_RIGHT  = Pivot(1.0, 1.0, 'BOTTOM_RIGHT')

# Backward compat: map old Pivots(Enum) int values → Pivot instances
_PIVOTS_ENUM_MAP: dict[int, Pivot] = {
    0: Pivot.TOP_LEFT,
    1: Pivot.TOP_MIDDLE,
    2: Pivot.TOP_RIGHT,
    3: Pivot.LEFT,
    4: Pivot.CENTER,
    5: Pivot.RIGHT,
    6: Pivot.BOTTOM_LEFT,
    7: Pivot.BOTTOM_MIDDLE,
    8: Pivot.BOTTOM_RIGHT,
}


def resolve_pivot(pivot) -> Pivot:
    """Accept a :class:`Pivot`, old ``Pivots`` enum member, or int and
    return a :class:`Pivot` instance."""
    if isinstance(pivot, Pivot):
        return pivot
    val = getattr(pivot, 'value', pivot)
    if isinstance(val, int) and val in _PIVOTS_ENUM_MAP:
        return _PIVOTS_ENUM_MAP[val]
    return Pivot.TOP_LEFT


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
        visible: bool = True,
        enabled: bool = True,
        opacity: float = 1.0,
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
        self._tab_index: int = 0

        # Dirty flag — subclasses set True when GPU rebuild is needed
        self._dirty: bool = True

        # Tree
        self._parent: Optional[UIElement] = None
        self._children: list[UIElement] = []
        self._manager: Optional[UIManager] = None

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

    # -- layout (Godot-style anchors) ----------------------------------------

    def layout(self, px: float, py: float, pw: float, ph: float) -> None:
        """Recompute position/size from anchors relative to parent rect.

        If both ``anchor_min`` and ``anchor_max`` are ``(0, 0)`` the element
        uses absolute positioning and this method is a no-op.
        """
        amin = self.anchor_min
        amax = self.anchor_max
        if amin == (0.0, 0.0) and amax == (0.0, 0.0):
            return
        m = self.margin
        self._position.set(
            px + amin[0] * pw + m[3],
            py + amin[1] * ph + m[0],
        )
        self._size.set(
            (amax[0] - amin[0]) * pw - m[1] - m[3],
            (amax[1] - amin[1]) * ph - m[0] - m[2],
        )
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
