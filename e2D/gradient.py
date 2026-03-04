"""Gradient definitions for e2D shapes and UI elements.

:class:`LinearGradient`, :class:`RadialGradient`, and :class:`PointGradient`
can be used as:

* The ``bg_gradient`` parameter of any :class:`~e2D.ui.containers.UIContainer` subclass.
* The ``gradient`` parameter of :meth:`~e2D.shapes.ShapeRenderer.draw_rect_gradient`.
* The per-state gradient colours of :class:`~e2D.ui.button.Button`.

Linear / Radial gradient stops are a ``list[tuple[Color, float]]`` where the
``float`` is the stop position in **[0, 1]**.  Up to **8 stops** are supported.

:class:`PointGradient` takes a list of ``(point, Color)`` pairs instead and
uses **inverse-distance weighting (IDW)** to blend between them — every pixel
gets a colour proportional to the inverse of its distance to each control
point.  Up to **16 points** are supported.

Examples::

    from e2D import LinearGradient, RadialGradient, PointGradient, Color
    from e2D.vectors import V2

    # Simple two-stop left→right gradient
    grad = LinearGradient(
        stops=[(Color(0.2, 0.4, 0.9), 0.0), (Color(0.8, 0.2, 0.5), 1.0)],
        angle=0.0,   # 0 = left → right
    )

    # Radial vignette
    vignette = RadialGradient(
        stops=[(Color(1, 1, 1, 0), 0.0), (Color(0, 0, 0, 0.7), 1.0)],
        center=(0.5, 0.5),
        radius=1.0,
    )

    # Scattered colour points — normalised 0-1 UV space
    scatter = PointGradient(
        points=[
            (V2(0.25, 0.25), Color(1, 0, 0)),   # red near top-left
            (V2(0.75, 0.25), Color(0, 1, 0)),   # green near top-right
            (V2(0.50, 0.75), Color(0, 0, 1)),   # blue near bottom-centre
        ],
        power=2.0,       # IDW exponent (higher = sharper transitions)
    )

    # Same but in pixel coordinates (element is 400 × 300)
    scatter_px = PointGradient(
        points=[
            ((100, 80),  Color(1, 0, 0)),
            ((300, 80),  Color(0, 1, 0)),
            ((200, 220), Color(0, 0, 1)),
        ],
        normalized=False,   # treat point coords as pixels relative to element TL
        power=2.0,
    )
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from .colors import Color


# ---------------------------------------------------------------------------
# Gradient dataclasses
# ---------------------------------------------------------------------------

@dataclass
class LinearGradient:
    """A linear colour gradient.

    Args:
        stops:  ``[(Color, position), …]`` — list of (colour, 0..1) stop pairs.
                At most **8** stops are used; any excess are silently ignored.
        angle:  Direction in *radians*.  ``0`` = left → right.  ``math.pi/2``
                = top → bottom.  ``math.pi`` = right → left.
    """

    stops: list[tuple[Color, float]]
    angle: float = 0.0


@dataclass
class RadialGradient:
    """A radial colour gradient.

    Args:
        stops:   ``[(Color, position), …]`` — same format as
                 :class:`LinearGradient`.
        center:  Normalised centre within the element bbox:
                 ``(0, 0)`` = top-left, ``(1, 1)`` = bottom-right,
                 ``(0.5, 0.5)`` = centre (default).
        radius:  Gradient radius as a fraction of the element's *smaller*
                 dimension.  ``1.0`` reaches the nearest edge; values ``>1``
                 extend beyond.
    """

    stops: list[tuple[Color, float]]
    center: tuple[float, float] = (0.5, 0.5)
    radius: float = 1.0


@dataclass
class PointGradient:
    """Scattered colour points blended via **inverse-distance weighting (IDW)**.

    Each pixel's colour is a weighted average of all control-point colours,
    where the weight of point *i* is ``1 / distance(pixel, point_i) ** power``.
    A pixel that falls exactly on a control point gets that point's colour.

    Args:
        points:     ``[(point, Color), …]`` — up to **16** pairs.

                    *point* can be:

                    * A :class:`~e2D.vectors.Vector2D` or 2-tuple.
                    * In **normalised UV** space ``(0..1, 0..1)`` when
                      ``normalized=True`` (default) — ``(0,0)`` is top-left,
                      ``(1,1)`` is bottom-right of the element.
                    * In **pixel** space relative to the element's top-left
                      corner when ``normalized=False``.

        power:      IDW exponent.  ``2.0`` (default) gives smooth blending;
                    larger values sharpen the transitions so each region is
                    dominated by its nearest point.
        normalized: When *True* (default) points are in 0-1 UV space.
                    When *False* points are in pixel coordinates relative
                    to the element's top-left corner (converted to UV
                    internally using the element's pixel size).
    """

    points: list[tuple]   # list of (V2 | tuple[float,float], Color)
    power: float = 2.0
    normalized: bool = True


# Public type alias
GradientType = Union[LinearGradient, RadialGradient, PointGradient]
