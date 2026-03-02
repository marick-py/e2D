"""
Label — rich text UI element with multi-segment, multi-style support.

Usage::

    # simple
    label = Label("Hello World")

    # rich text  (plain strings fall back to *default_style*)
    label = Label(
        ("Score: ", MONO_16),
        ("42",      TextStyle(font="consola.ttf", font_size=24, color=RED)),
    )

    # positional
    label = Label("FPS: 60", position=V2(10, 10), pivot=Pivot.TOP_LEFT)

NOTE  Option B (mega-atlas) is documented here for future reference but
      not implemented.  Current implementation uses Option A (one draw call
      per unique font atlas).
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import numpy as np
import moderngl

from .base import Pivot, UIElement
from ..text import TextStyle, DEFAULT_16_TEXT_STYLE

if TYPE_CHECKING:
    from ..text import TextRenderer
    from .._types import ContextType


class Label(UIElement):
    """Styled text element supporting multiple font/colour segments.

    Positional ``*segments`` are any mix of:
    * ``str``  — rendered with *default_style*
    * ``(str, TextStyle)`` — rendered with the given style

    Position and rotation are applied via shader uniforms, so moving or
    rotating a label is extremely cheap (no vertex rebuild).
    """

    def __init__(
        self,
        *segments: str | tuple[str, TextStyle],
        default_style: TextStyle = DEFAULT_16_TEXT_STYLE,
        rotation: float = 0.0,
        line_spacing: float = 1.2,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.default_style: TextStyle = default_style
        self.rotation: float = rotation
        self.line_spacing: float = line_spacing

        self._segments: list[tuple[str, TextStyle]] = self._parse(segments)

        # GPU state  (populated by _build / _rebuild)
        self._render_groups: list[dict] = []   # [{texture, vbo, vao, vtx_count}]
        self._ctx: Optional[ContextType] = None
        self._text_renderer: Optional[TextRenderer] = None
        self._built: bool = False
        self._text_width: float = 0.0
        self._text_height: float = 0.0

    # -- public API ----------------------------------------------------------

    @property
    def text(self) -> str:
        """Plain concatenation of all segment texts."""
        return ''.join(t for t, _ in self._segments)

    def set_text(self, *segments: str | tuple[str, TextStyle]) -> None:
        """Replace all segments and schedule a rebuild."""
        self._segments = self._parse(segments)
        self._dirty = True

    def set_plain_text(self, text: str) -> None:
        """Replace text keeping the current default style."""
        self._segments = [(text, self.default_style)]
        self._dirty = True

    # -- segment parsing -----------------------------------------------------

    def _parse(self, segments) -> list[tuple[str, TextStyle]]:
        out: list[tuple[str, TextStyle]] = []
        for seg in segments:
            if isinstance(seg, str):
                out.append((seg, self.default_style))
            elif isinstance(seg, (tuple, list)) and len(seg) >= 2:
                out.append((str(seg[0]), seg[1]))
            else:
                out.append((str(seg), self.default_style))
        return out

    # -- GPU build -----------------------------------------------------------

    def _build(self, ctx, text_renderer) -> None:
        self._ctx = ctx
        self._text_renderer = text_renderer
        self._rebuild()

    def _rebuild(self) -> None:
        if self._ctx is None or self._text_renderer is None:
            return

        # Release old GPU resources
        self._release_groups()

        tr = self._text_renderer
        prog = tr.prog

        # ---- 1. group segments by atlas ------------------------------------
        # Each atlas key = (font, font_size)
        # Items: list of (text, style, cursor_x_start)
        atlas_groups: dict[tuple[str, int], dict] = {}
        cursor_x: float = 0.0
        cursor_y: float = 0.0
        max_line_h: float = 0.0
        max_total_w: float = 0.0

        for text, style in self._segments:
            atlas = tr._get_or_create_font_atlas(style.font, style.font_size)
            key = (style.font, style.font_size)
            if key not in atlas_groups:
                atlas_groups[key] = {'atlas': atlas, 'items': []}

            char_data = atlas['char_data']
            line_h = atlas['line_height']
            if line_h > max_line_h:
                max_line_h = line_h

            seg_start_x = cursor_x
            seg_start_y = cursor_y

            for ch in text:
                if ch == '\n':
                    if cursor_x > max_total_w:
                        max_total_w = cursor_x
                    cursor_x = 0.0
                    cursor_y += max_line_h * self.line_spacing
                    max_line_h = line_h
                    continue
                d = char_data.get(ch)
                if d:
                    cursor_x += d['advance'] + getattr(style, 'letter_spacing', 0.0)

            atlas_groups[key]['items'].append((text, style, seg_start_x, seg_start_y))

        if cursor_x > max_total_w:
            max_total_w = cursor_x
        self._text_width = max_total_w
        self._text_height = cursor_y + max_line_h if max_line_h > 0 else 0.0

        # Store computed size on the UIElement
        self._size.set(self._text_width, self._text_height)

        # ---- 2. generate vertices per atlas --------------------------------
        for key, grp in atlas_groups.items():
            atlas = grp['atlas']
            char_data = atlas['char_data']
            line_h = atlas['line_height']
            verts: list[float] = []

            for text, style, sx, sy in grp['items']:
                cx, cy = sx, sy
                color = style.color
                ls = getattr(style, 'letter_spacing', 0.0)

                for ch in text:
                    if ch == '\n':
                        cx = 0.0
                        cy += line_h * self.line_spacing
                        continue
                    d = char_data.get(ch)
                    if d is None:
                        continue
                    if d['w'] == 0:
                        cx += d['advance'] + ls
                        continue

                    w = d['w']
                    h = d['h']
                    gx = cx + d['offset_x']
                    gy = cy + d['offset_y']
                    u0, v0, du, dv = d['uv']

                    # tri 1: TL TR BL
                    verts.extend([gx,     gy,     u0,      v0,      *color])
                    verts.extend([gx + w, gy,     u0 + du, v0,      *color])
                    verts.extend([gx,     gy + h, u0,      v0 + dv, *color])
                    # tri 2: TR BL BR
                    verts.extend([gx + w, gy,     u0 + du, v0,      *color])
                    verts.extend([gx,     gy + h, u0,      v0 + dv, *color])
                    verts.extend([gx + w, gy + h, u0 + du, v0 + dv, *color])

                    cx += d['advance'] + ls

            if not verts:
                continue

            data = np.array(verts, dtype='f4')
            vbo = self._ctx.buffer(data.tobytes())
            vao = self._ctx.vertex_array(prog, [
                (vbo, '2f 2f 4f', 'in_pos', 'in_uv', 'in_color'),
            ])
            self._render_groups.append({
                'texture': atlas['texture'],
                'vbo': vbo,
                'vao': vao,
                'vtx_count': len(verts) // 8,
            })

        self._built = True
        self._dirty = False

    # -- draw ----------------------------------------------------------------

    def draw(self, ctx=None) -> None:
        if not self._built:
            return
        if self._dirty:
            self._rebuild()

        ctx = ctx or self._ctx
        if ctx is None or self._text_renderer is None:
            return
        ctx.enable(moderngl.BLEND)

        prog = self._text_renderer.prog

        # pivot offset (local coords)
        pox = self.pivot.x * self._text_width
        poy = self.pivot.y * self._text_height

        prog['resolution'] = ctx.viewport[2:]
        prog['u_pivot_local']  = (pox, poy)
        prog['u_screen_pos']   = (self._position.x, self._position.y)
        prog['u_rotation']     = self.rotation
        prog['u_opacity']      = self.opacity

        for grp in self._render_groups:
            grp['texture'].use(0)
            grp['vao'].render(moderngl.TRIANGLES, vertices=grp['vtx_count'])

        # Reset uniforms so other TextRenderer calls aren't affected
        prog['u_pivot_local'] = (0.0, 0.0)
        prog['u_screen_pos']  = (0.0, 0.0)
        prog['u_rotation']    = 0.0
        prog['u_opacity']     = 1.0

    # -- cleanup -------------------------------------------------------------

    def _release_groups(self) -> None:
        for grp in self._render_groups:
            try:
                grp['vbo'].release()
            except Exception:
                pass
            try:
                grp['vao'].release()
            except Exception:
                pass
        self._render_groups.clear()

    def release(self) -> None:
        self._release_groups()
        self._built = False
        super().release()
