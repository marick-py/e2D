"""
Camera2D — 2D camera with pan, zoom, and coordinate transforms.
"""

from __future__ import annotations
import numpy as np

from ..vectors import Vector2D, V2
from .._types import FloatVec2


class Camera2D:
    """2D camera providing world <-> screen coordinate transforms with pan and zoom.

    All ``draw_*`` calls accept screen-space coordinates.  Use :class:`Camera2D`
    to maintain a world-space simulation and convert to screen-space before
    drawing.

    Example::

        cam = Camera2D(env.window_size)

        def update(self, dt: float) -> None:
            if env.keyboard.get_key(Keys.W): cam.pan(0, -5)
            if env.keyboard.get_key(Keys.S): cam.pan(0,  5)

        def draw(self) -> None:
            screen = cam.world_to_screen(player.pos)
            env.draw_circle(screen, cam.world_to_screen_scale(player.radius))

        def on_resize(self, w, h):
            cam.update_window_size(w, h)
    """

    def __init__(
        self,
        window_size: Vector2D | FloatVec2,
        position: Vector2D | FloatVec2 = (0.0, 0.0),
        zoom: float = 1.0,
    ) -> None:
        self.window_size: Vector2D = (
            V2(float(window_size[0]), float(window_size[1]))
            if not isinstance(window_size, Vector2D)
            else window_size
        )
        self.position: Vector2D = (
            V2(float(position[0]), float(position[1]))
            if not isinstance(position, Vector2D)
            else position
        )
        self.zoom: float = zoom

    # -- coordinate transforms -----------------------------------------------

    def world_to_screen(self, point: Vector2D | FloatVec2) -> Vector2D:
        cx = self.window_size[0] * 0.5
        cy = self.window_size[1] * 0.5
        sx = (point[0] - self.position[0]) * self.zoom + cx
        sy = (point[1] - self.position[1]) * self.zoom + cy
        return V2(sx, sy)

    def screen_to_world(self, point: Vector2D | FloatVec2) -> Vector2D:
        cx = self.window_size[0] * 0.5
        cy = self.window_size[1] * 0.5
        wx = (point[0] - cx) / self.zoom + self.position[0]
        wy = (point[1] - cy) / self.zoom + self.position[1]
        return V2(wx, wy)

    def world_to_screen_scale(self, length: float) -> float:
        return length * self.zoom

    def screen_to_world_scale(self, pixels: float) -> float:
        return pixels / self.zoom

    # -- navigation ----------------------------------------------------------

    def pan(self, dx: float, dy: float) -> None:
        self.position[0] += dx
        self.position[1] += dy

    def zoom_at(
        self,
        factor: float,
        screen_point: Vector2D | FloatVec2,
    ) -> None:
        world_anchor = self.screen_to_world(screen_point)
        self.zoom *= factor
        cx = self.window_size[0] * 0.5
        cy = self.window_size[1] * 0.5
        self.position[0] = world_anchor[0] - (screen_point[0] - cx) / self.zoom
        self.position[1] = world_anchor[1] - (screen_point[1] - cy) / self.zoom

    # -- housekeeping --------------------------------------------------------

    def update_window_size(self, width: float, height: float) -> None:
        self.window_size.set(width, height)

    def get_matrix(self) -> np.ndarray:
        """Return the 3x3 world->screen transform matrix (float32, row-major)."""
        cx = self.window_size[0] * 0.5
        cy = self.window_size[1] * 0.5
        z = self.zoom
        return np.array(
            [
                [z,   0.0, -self.position[0] * z + cx],
                [0.0, z,   -self.position[1] * z + cy],
                [0.0, 0.0, 1.0],
            ],
            dtype='f4',
        )


__all__ = ['Camera2D']
