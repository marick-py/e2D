"""Image rendering for e2D.

Provides GPU-accelerated image drawing with full layer-queue integration
(same deferred system as shapes / text).

Classes
-------
ScaleMode
    Enum controlling how an image is scaled into its target rect.
ImageLabel
    A cached GPU object (texture + VAO).  Created once, drawn many times at
    near-zero CPU cost.
ImageRenderer
    Singleton (one per Context) that owns the shader and drives draws.

Functions exposed on RootEnv (wired in __init__.py)
----------------------------------------------------
create_image(array)         -> ImageLabel
load_image(path)            -> ImageLabel
draw_image(label, ...)      — corners mode  (top-left + bottom-right)
draw_image_centered(...)    — center + scale mode
"""
from __future__ import annotations

import os
from enum import Enum
from typing import Optional, TYPE_CHECKING

import numpy as np
import moderngl

from ._types import ColorType, ContextType, ProgramType, BufferType, VAOType, TextureType, FloatVec2
from .utils import set_pattr_value_packed

if TYPE_CHECKING:
    from .vectors import Vector2D


# ---------------------------------------------------------------------------
#  ScaleMode
# ---------------------------------------------------------------------------

class ScaleMode(Enum):
    """How the image is scaled / cropped inside the destination rectangle.

    STRETCH        — fill the whole rect, ignoring aspect ratio.
    FIT            — scale uniformly so the *whole* image is visible (letterbox).
    FIT_WIDTH      — scale so image width fills the rect width; may crop vertically.
    FIT_HEIGHT     — scale so image height fills the rect height; may crop horizontally.
    FILL           — scale uniformly so the rect is *completely* covered (crop).
    PIXEL_PERFECT  — render at 1:1 pixel size, no scaling (position-only).
    """
    STRETCH      = 0
    FIT          = 1
    FIT_WIDTH    = 2
    FIT_HEIGHT   = 3
    FILL         = 4
    PIXEL_PERFECT= 5


# ---------------------------------------------------------------------------
#  ImageLabel
# ---------------------------------------------------------------------------

class ImageLabel:
    """A pre-uploaded GPU image object ready for repeated drawing.

    Create via :meth:`ImageRenderer.create_image` or
    :meth:`ImageRenderer.load_image` — do not instantiate directly.

    The label stores only immutable GPU objects (texture, cached quad VAO).
    All per-frame parameters (position, scale, rotation, tint …) are passed
    at draw time and handled via shader uniforms.
    """

    ctx: ContextType
    texture: TextureType
    _w: int   # original image pixel width
    _h: int   # original image pixel height
    _channels: int  # number of channels the texture was created with (3 or 4)

    def __init__(self, ctx: ContextType, texture: TextureType, width: int, height: int, channels: int = 4) -> None:
        self.ctx = ctx
        self.texture = texture
        self._w = width
        self._h = height
        self._channels = channels

    @property
    def size(self) -> tuple[int, int]:
        """Original pixel dimensions of the image."""
        return (self._w, self._h)

    @property
    def aspect(self) -> float:
        """Width / height aspect ratio."""
        return self._w / self._h if self._h else 1.0

    def draw(
        self,
        renderer: "ImageRenderer",
        # Position — corners variant
        top_left: Optional[FloatVec2] = None,
        bottom_right: Optional[FloatVec2] = None,
        # Position — center+scale variant
        center: Optional[FloatVec2] = None,
        display_width: Optional[float] = None,
        display_height: Optional[float] = None,
        # Common
        scale_mode: ScaleMode = ScaleMode.STRETCH,
        rotation: float = 0.0,
        tint: ColorType = (1.0, 1.0, 1.0, 1.0),
        opacity: float = 1.0,
        pivot_uv: FloatVec2 = (0.5, 0.5),
        corner_radius: float = 0.0,
        antialiasing: float = 1.0,
        flip_x: bool = False,
        flip_y: bool = False,
    ) -> None:
        """Execute the draw call immediately (called by ImageRenderer.flush)."""
        # Resolve destination rect (top-left + size)
        if top_left is not None and bottom_right is not None:
            x = float(top_left[0])
            y = float(top_left[1])
            w = float(bottom_right[0]) - x
            h = float(bottom_right[1]) - y
        elif center is not None:
            cw = float(display_width)  if display_width  is not None else float(self._w)
            ch = float(display_height) if display_height is not None else float(self._h)
            x = float(center[0]) - cw * 0.5
            y = float(center[1]) - ch * 0.5
            w, h = cw, ch
        else:
            raise ValueError("Either (top_left, bottom_right) or (center, display_width, display_height) must be provided.")

        if w <= 0 or h <= 0:
            return

        renderer._exec_draw(
            self,
            pos=(x, y),
            size=(w, h),
            scale_mode=scale_mode,
            rotation=rotation,
            tint=tint,
            opacity=opacity,
            pivot_uv=pivot_uv,
            corner_radius=corner_radius,
            aa=antialiasing,
            flip_x=flip_x,
            flip_y=flip_y,
        )


# ---------------------------------------------------------------------------
#  ImageRenderer
# ---------------------------------------------------------------------------

_IMAGE_VERT = """
#version 430

// resolution uniform — pixels
uniform vec2  u_resolution;
// destination rect in screen-pixels (y-down)
uniform vec2  u_pos;        // top-left
uniform vec2  u_size;       // width, height
// pivot point in 0..1 UV space (rotation centre)
uniform vec2  u_pivot_uv;
// rotation in radians
uniform float u_rotation;

in vec2 in_vertex;   // unit quad: -1..1

// Outputs to fragment shader
out vec2 v_local_px;   // pixel offset from rect centre
out vec2 v_local_uv;   // 0..1 UV within rect (before scale-mode remapping)

void main() {
    float hw = u_size.x * 0.5;
    float hh = u_size.y * 0.5;

    // pivot in local pixel space
    vec2 pivot_px = (u_pivot_uv - 0.5) * u_size;

    // v_local_uv: (0,0) at top-left of the screen rect.
    // in_vertex.y = -1 at the visual top (ndc.y is flipped later), so
    // direct mapping 0..1 gives UV.y=0 at top → correct for top-down image data.
    v_local_uv = in_vertex * 0.5 + 0.5;
    vec2 local = in_vertex * vec2(hw, hh);

    // Rotate around pivot
    vec2 offset = local - pivot_px;
    float c = cos(u_rotation);
    float s = sin(u_rotation);
    vec2 rot = vec2(offset.x * c - offset.y * s,
                    offset.x * s + offset.y * c);
    v_local_px = local;

    vec2 centre    = u_pos + u_size * 0.5;
    vec2 world_pos = centre + pivot_px + rot;
    vec2 ndc       = (world_pos / u_resolution) * 2.0 - 1.0;
    ndc.y          = -ndc.y;
    gl_Position    = vec4(ndc, 0.0, 1.0);
}
"""

_IMAGE_FRAG = """
#version 430

// Image texture
uniform sampler2D u_tex;

// Destination rect size (for SDF corner radius)
uniform vec2  u_size;
// Scale mode: 0=STRETCH, 1=FIT, 2=FIT_WIDTH, 3=FIT_HEIGHT, 4=FILL, 5=PIXEL_PERFECT
uniform int   u_scale_mode;
// Original image pixel size (for non-STRETCH modes)
uniform vec2  u_img_size;
// Tint colour (multiplied with texture)
uniform vec4  u_tint;
// Global opacity
uniform float u_opacity;
// Corner radius in pixels
uniform float u_corner_radius;
// Antialiasing edge softness
uniform float u_aa;
// UV flip
uniform vec2  u_flip;   // (flip_x, flip_y) — 0 or 1

in vec2 v_local_px;
in vec2 v_local_uv;

out vec4 f_color;

float roundedBoxSDF(vec2 center, vec2 half_size, float radius) {
    vec2 q = abs(center) - half_size + radius;
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - radius;
}

void main() {
    // ---- Compute UV based on scale mode ----
    vec2 uv = v_local_uv;   // 0..1 raw

    // Aspect ratios
    float img_ar  = u_img_size.x / max(u_img_size.y, 0.0001);
    float rect_ar = u_size.x     / max(u_size.y,     0.0001);

    if (u_scale_mode == 0) {
        // STRETCH — identity, no adjustment needed
        uv = v_local_uv;

    } else if (u_scale_mode == 1) {
        // FIT — letterbox: image fully visible, black bars on sides or top/bottom
        float scale;
        if (img_ar > rect_ar) {
            // image wider → fit width
            scale = rect_ar / img_ar;
            uv = vec2(v_local_uv.x,
                      (v_local_uv.y - 0.5) / scale + 0.5);
        } else {
            // image taller → fit height
            scale = img_ar / rect_ar;
            uv = vec2((v_local_uv.x - 0.5) / scale + 0.5,
                      v_local_uv.y);
        }
        // Transparent outside image bounds
        if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
            discard;
        }

    } else if (u_scale_mode == 2) {
        // FIT_WIDTH — image width fills rect, may crop top/bottom
        float scale = img_ar / rect_ar;
        uv = vec2(v_local_uv.x,
                  (v_local_uv.y - 0.5) * scale + 0.5);
        if (uv.y < 0.0 || uv.y > 1.0) discard;

    } else if (u_scale_mode == 3) {
        // FIT_HEIGHT — image height fills rect, may crop sides
        float scale = rect_ar / img_ar;
        uv = vec2((v_local_uv.x - 0.5) * scale + 0.5,
                  v_local_uv.y);
        if (uv.x < 0.0 || uv.x > 1.0) discard;

    } else if (u_scale_mode == 4) {
        // FILL — cover entire rect, crop to maintain aspect ratio
        if (img_ar > rect_ar) {
            float scale = rect_ar / img_ar;
            uv = vec2((v_local_uv.x - 0.5) / scale + 0.5,
                      v_local_uv.y);
        } else {
            float scale = img_ar / rect_ar;
            uv = vec2(v_local_uv.x,
                      (v_local_uv.y - 0.5) / scale + 0.5);
        }

    } else if (u_scale_mode == 5) {
        // PIXEL_PERFECT — 1 image pixel = 1 screen pixel, centred
        // v_local_px is in screen pixels relative to rect centre
        uv = vec2(
            (v_local_px.x + u_img_size.x * 0.5) / u_img_size.x,
            (v_local_px.y + u_img_size.y * 0.5) / u_img_size.y
        );
        if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) discard;
    }

    // ---- UV flipping ----
    if (u_flip.x > 0.5) uv.x = 1.0 - uv.x;
    if (u_flip.y > 0.5) uv.y = 1.0 - uv.y;

    // ---- Sample texture with bilinear filtering (default) ----
    vec4 texel = texture(u_tex, uv);

    // ---- Tint & opacity ----
    vec4 color = texel * u_tint;
    color.a   *= u_opacity;

    // ---- Rounded corner SDF clip ----
    if (u_corner_radius > 0.0) {
        float dist  = roundedBoxSDF(v_local_px, u_size * 0.5, u_corner_radius);
        float alpha = 1.0 - smoothstep(-u_aa, u_aa, dist);
        color.a    *= alpha;
    }

    if (color.a <= 0.0) discard;
    f_color = color;
}
"""


class ImageRenderer:
    """Renders ImageLabel objects using a textured quad shader.

    One instance lives inside :class:`~e2D.shapes.ShapeRenderer` so that
    image draws participate in the same layer-sorted deferred queue.

    All public draw methods simply enqueue a lambda into
    ``ShapeRenderer._queue`` under type character ``'i'``.
    """

    ctx: ContextType
    _prog: ProgramType
    _quad_vbo: BufferType
    _quad_vao: VAOType

    def __init__(self, ctx: ContextType) -> None:
        self.ctx = ctx

        self._prog = ctx.program(
            vertex_shader=_IMAGE_VERT,
            fragment_shader=_IMAGE_FRAG,
        )

        # Shared unit quad (-1..1) — 6 vertices, 2 triangles
        _qv = np.array([
            -1.0, -1.0,   1.0, -1.0,  -1.0,  1.0,
             1.0, -1.0,  -1.0,  1.0,   1.0,  1.0,
        ], dtype='f4')
        self._quad_vbo = ctx.buffer(_qv.tobytes())
        self._quad_vao = ctx.vertex_array(
            self._prog,
            [(self._quad_vbo, '2f', 'in_vertex')],
        )

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _prepare_array(array: np.ndarray, target_channels: int = 0) -> tuple:
        """Normalise *array* to a C-contiguous uint8 array ready for GPU upload.

        Args:
            array:           Input image. Supported dtypes: uint8, float32/64.
                             Supported shapes: (H,W), (H,W,1), (H,W,2), (H,W,3), (H,W,4).
            target_channels: If > 0, force this many channels in the output.
                             If 0, keep natural channel count.

        Returns:
            (arr, channels) — uint8 C-contiguous numpy array and its channel count.
        """
        arr = np.asarray(array)

        # Flatten single-channel dim
        if arr.ndim == 2:
            arr = arr[:, :, np.newaxis]  # (H,W,1)

        channels = arr.shape[2]

        # Convert to uint8
        if arr.dtype != np.uint8:
            arr = (np.clip(arr.astype(np.float32), 0.0, 1.0) * 255).astype(np.uint8)

        # Channel conversion when target_channels is specified
        if target_channels > 0 and channels != target_channels:
            if target_channels == 4 and channels == 3:
                alpha = np.full(arr.shape[:2] + (1,), 255, dtype=np.uint8)
                arr = np.concatenate([arr, alpha], axis=-1)
                channels = 4
            elif target_channels == 3 and channels == 4:
                arr = arr[:, :, :3]
                channels = 3
            elif target_channels == 1 and channels >= 3:
                # Luminance approximation
                arr = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]).astype(np.uint8)[:, :, np.newaxis]
                channels = 1
            # For other mismatches just keep as-is and let the caller handle it

        return np.ascontiguousarray(arr), channels

    def create_image(self, array: np.ndarray) -> ImageLabel:
        """Upload a numpy array as a GPU texture and return an ImageLabel.

        Args:
            array: Image data.  Supported shapes:
                   * ``(H, W, 4)`` — RGBA uint8 or float32
                   * ``(H, W, 3)`` — RGB  uint8 or float32
                   * ``(H, W)``    — Grayscale (single-channel)

        Returns:
            ImageLabel ready for drawing.
        """
        arr, channels = self._prepare_array(array)
        h, w = arr.shape[:2]

        texture = self.ctx.texture((w, h), channels, arr.tobytes())
        texture.filter = moderngl.LINEAR, moderngl.LINEAR
        texture.repeat_x = False
        texture.repeat_y = False

        return ImageLabel(self.ctx, texture, w, h, channels)

    def create_streaming_image(self, width: int, height: int, channels: int = 3) -> ImageLabel:
        """Pre-allocate a GPU texture for streaming / video-feed use.

        Allocates the texture once.  Call :meth:`update_image` every frame to
        push new pixel data without any GPU memory allocation overhead.

        Args:
            width:    Texture width in pixels.
            height:   Texture height in pixels.
            channels: 1 (R), 2 (RG), 3 (RGB) or 4 (RGBA).

        Returns:
            ImageLabel ready for drawing.  Pixel data is uninitialised until
            the first call to :meth:`update_image`.
        """
        texture = self.ctx.texture((width, height), channels)
        texture.filter = moderngl.LINEAR, moderngl.LINEAR
        texture.repeat_x = False
        texture.repeat_y = False
        return ImageLabel(self.ctx, texture, width, height, channels)

    def update_image(self, label: ImageLabel, array: np.ndarray) -> None:
        """Push new pixel data into an existing ImageLabel texture.

        Zero GPU allocation — uses ``texture.write()`` on the pre-allocated
        texture.  Intended for streaming / video-feed use cases where
        :meth:`create_streaming_image` was used to pre-allocate the texture.

        The array dimensions must match the texture dimensions that were used
        when the ``ImageLabel`` was created.

        Args:
            label: ImageLabel created via :meth:`create_streaming_image` (or
                   :meth:`create_image` — any ``ImageLabel`` works).
            array: New pixel data.  Must have the same spatial dimensions as
                   the texture.  Channels are coerced automatically.
        """
        arr, _ = self._prepare_array(array, target_channels=label._channels)
        label.texture.write(arr.tobytes())

    def load_image(self, path: str) -> ImageLabel:
        """Load an image from a file and return an ImageLabel.

        Requires Pillow.  All common formats (PNG, JPG, BMP, WEBP, …) are
        supported.

        Args:
            path: Absolute or relative path to the image file.

        Returns:
            ImageLabel ready for drawing.

        Raises:
            FileNotFoundError: If the file does not exist.
            ImportError: If Pillow is not installed.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Image file not found: {path}")

        try:
            from PIL import Image as PILImage
        except ImportError:
            raise ImportError("Pillow is required for load_image.  Install with: pip install pillow")

        img = PILImage.open(path).convert("RGBA")
        arr = np.array(img, dtype=np.uint8)
        return self.create_image(arr)

    # ------------------------------------------------------------------
    # Immediate draw (called from the deferred queue)
    # ------------------------------------------------------------------

    def _exec_draw(
        self,
        label: ImageLabel,
        pos: FloatVec2,
        size: FloatVec2,
        scale_mode: ScaleMode,
        rotation: float,
        tint: ColorType,
        opacity: float,
        pivot_uv: FloatVec2,
        corner_radius: float,
        aa: float,
        flip_x: bool,
        flip_y: bool,
    ) -> None:
        """Execute one image draw call immediately (no batching — each image
        is a separate GL call because the texture binding changes)."""
        prog = self._prog
        vp   = self.ctx.viewport

        prog['u_resolution']   = (float(vp[2]), float(vp[3]))
        prog['u_pos']          = (float(pos[0]), float(pos[1]))
        prog['u_size']         = (float(size[0]), float(size[1]))
        prog['u_pivot_uv']     = (float(pivot_uv[0]), float(pivot_uv[1]))
        prog['u_rotation']     = float(rotation)
        prog['u_scale_mode']   = int(scale_mode.value)
        prog['u_img_size']     = (float(label._w), float(label._h))
        prog['u_tint']         = (float(tint[0]), float(tint[1]), float(tint[2]), float(tint[3]))
        prog['u_opacity']      = float(opacity)
        prog['u_corner_radius']= float(corner_radius)
        prog['u_aa']           = float(aa)
        prog['u_flip']         = (1.0 if flip_x else 0.0, 1.0 if flip_y else 0.0)

        label.texture.use(0)
        prog['u_tex'] = 0

        self.ctx.enable(moderngl.BLEND)
        self._quad_vao.render(moderngl.TRIANGLES)

    # ------------------------------------------------------------------
    # Deferred (queue-based) draw entry points
    # ------------------------------------------------------------------

    def draw_image(
        self,
        queue: list,
        label: ImageLabel,
        top_left: FloatVec2,
        bottom_right: FloatVec2,
        scale_mode: ScaleMode = ScaleMode.STRETCH,
        rotation: float = 0.0,
        tint: ColorType = (1.0, 1.0, 1.0, 1.0),
        opacity: float = 1.0,
        pivot_uv: FloatVec2 = (0.5, 0.5),
        corner_radius: float = 0.0,
        antialiasing: float = 1.0,
        flip_x: bool = False,
        flip_y: bool = False,
        layer: int = 0,
    ) -> None:
        """Enqueue an image draw (corners mode) into the shape render queue."""
        x  = float(top_left[0])
        y  = float(top_left[1])
        w  = float(bottom_right[0]) - x
        h  = float(bottom_right[1]) - y

        _tint = (float(tint[0]), float(tint[1]), float(tint[2]), float(tint[3]))
        _piv  = (float(pivot_uv[0]), float(pivot_uv[1]))

        renderer = self

        queue.append((layer, 'i',
            lambda _r=renderer, _l=label, _pos=(x, y), _sz=(w, h): _r._exec_draw(
                _l, _pos, _sz, scale_mode, rotation, _tint, opacity, _piv,
                corner_radius, antialiasing, flip_x, flip_y,
            )
        ))

    def draw_image_centered(
        self,
        queue: list,
        label: ImageLabel,
        center: FloatVec2,
        display_width: Optional[float] = None,
        display_height: Optional[float] = None,
        scale: float = 1.0,
        scale_mode: ScaleMode = ScaleMode.STRETCH,
        rotation: float = 0.0,
        tint: ColorType = (1.0, 1.0, 1.0, 1.0),
        opacity: float = 1.0,
        pivot_uv: FloatVec2 = (0.5, 0.5),
        corner_radius: float = 0.0,
        antialiasing: float = 1.0,
        flip_x: bool = False,
        flip_y: bool = False,
        layer: int = 0,
    ) -> None:
        """Enqueue an image draw (center + scale mode) into the shape render queue.

        If display_width / display_height are not given, the image's natural
        pixel dimensions are used, then multiplied by ``scale``.
        """
        cw = float(display_width  if display_width  is not None else label._w) * scale
        ch = float(display_height if display_height is not None else label._h) * scale
        cx, cy = float(center[0]), float(center[1])
        top_left     = (cx - cw * 0.5, cy - ch * 0.5)
        bottom_right = (cx + cw * 0.5, cy + ch * 0.5)

        self.draw_image(
            queue, label,
            top_left=top_left, bottom_right=bottom_right,
            scale_mode=scale_mode, rotation=rotation, tint=tint, opacity=opacity,
            pivot_uv=pivot_uv, corner_radius=corner_radius, antialiasing=antialiasing,
            flip_x=flip_x, flip_y=flip_y, layer=layer,
        )
