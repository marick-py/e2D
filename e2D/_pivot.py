"""
Pivot — normalised anchor/pivot point.

Lives at the e2D root (not inside ui/) so that text.py and ui/ can both
import it without creating a circular dependency.
"""

from __future__ import annotations
from typing import ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from .vectors import Vector2D


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


# Pre-defined pivots
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


__all__ = ['Pivot', 'resolve_pivot', '_PIVOTS_ENUM_MAP']
