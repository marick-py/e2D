from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from attr import dataclass
import numpy as np
import sys
import moderngl
from ._types import ColorType, VAOType, ContextType, ProgramType, BufferType, TextureType, FloatVec2
from .colors import normalize_color
from .palette import WHITE, BLACK
from .ui.base import Pivot, resolve_pivot
from .utils import find_system_font

# Backward-compat alias — new code should use ``Pivot`` directly.
Pivots = Pivot

# ---------------------------------------------------------------------------
#   Emoji / Unicode helpers
# ---------------------------------------------------------------------------

_EMOJI_FONTS: list[str] = (
    ["seguiemj.ttf"] if sys.platform == "win32"
    else ["Apple Color Emoji"] if sys.platform == "darwin"
    else ["NotoColorEmoji.ttf", "NotoColorEmoji-Regular.ttf"]
)

def _is_emoji(ch: str) -> bool:
    """Return *True* if *ch* falls in a known emoji / symbol Unicode range."""
    cp = ord(ch)
    return (
        0x1F000 <= cp <= 0x1FAFF
        or 0x2600 <= cp <= 0x27BF
        or 0x2300 <= cp <= 0x23FF
        or 0x2B00 <= cp <= 0x2BFF
        or 0xFE00 <= cp <= 0xFE0F
        or cp == 0x200D
        or cp == 0x20E3
        or 0xE0020 <= cp <= 0xE007F
        or 0x1F1E0 <= cp <= 0x1F1FF
    )

@dataclass
class TextStyle:
    font: str = "arial.ttf"
    font_size: int = 32
    color: ColorType = (1.0, 1.0, 1.0, 1.0)
    bg_color: ColorType = (0.0, 0.0, 0.0, 0.0)  # Transparent by default
    bg_margin: float | tuple[float, float, float, float] | tuple[float, float] | list[float] = 15.0
    bg_border_radius: float | tuple[float, float, float, float] | tuple[float, float] | list[float] = 15.0
    line_spacing: float = 1.2
    letter_spacing: float = 0.0

DEFAULT_12_TEXT_STYLE = TextStyle(font_size=12)
DEFAULT_16_TEXT_STYLE = TextStyle(font_size=16)
DEFAULT_32_TEXT_STYLE = TextStyle(font_size=32)
DEFAULT_64_TEXT_STYLE = TextStyle(font_size=64)

MONO_12_TEXT_STYLE = TextStyle(font="consola.ttf", font_size=12)
MONO_16_TEXT_STYLE = TextStyle(font="consola.ttf", font_size=16)
MONO_32_TEXT_STYLE = TextStyle(font="consola.ttf", font_size=32)
MONO_64_TEXT_STYLE = TextStyle(font="consola.ttf", font_size=64)

class TextLabel:
    ctx: ContextType
    prog: ProgramType
    texture: TextureType
    vertices: list[float]
    vbo: BufferType
    vao: VAOType
    bg_prog: Optional[ProgramType]
    bg_vertices: Optional[list[float]]
    bg_vbo: Optional[BufferType]
    bg_vao: Optional[VAOType]
    
    def __init__(self, ctx: ContextType, prog: ProgramType, texture: TextureType, vertices: list[float],
                 bg_prog: Optional[ProgramType] = None, bg_vertices: Optional[list[float]] = None) -> None:
        """
        A pre-rendered text label for efficient drawing.
        To generate select a option below:
            - use TextRenderer.create_label()
            - rootEnv.print(..., save_cache = True) will return a TextLabel.
        """
        self.ctx = ctx
        self.prog = prog
        self.texture = texture
        self.vertices = vertices
        self.vbo = self.ctx.buffer(np.array(vertices, dtype='f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '2f 2f 4f', 'in_pos', 'in_uv', 'in_color')
        ])
        
        # Background rendering
        self.bg_prog = bg_prog
        self.bg_vertices = bg_vertices
        if bg_prog and bg_vertices:
            self.bg_vbo = self.ctx.buffer(np.array(bg_vertices, dtype='f4').tobytes())
            self.bg_vao = self.ctx.vertex_array(self.bg_prog, [
                (self.bg_vbo, '2f 4f 4f 4f', 'in_pos', 'in_color', 'in_rect', 'in_radius')
            ])
        else:
            self.bg_vbo = None
            self.bg_vao = None
        
    def draw(self) -> None:
        self.ctx.enable(moderngl.BLEND)
        
        # Draw background first if exists
        if self.bg_vao and self.bg_prog:
            self.bg_prog['resolution'] = self.ctx.viewport[2:]
            self.bg_prog['u_pivot_local'] = (0.0, 0.0)
            self.bg_prog['u_screen_pos']  = (0.0, 0.0)
            self.bg_prog['u_rotation']    = 0.0
            self.bg_prog['u_opacity']     = 1.0
            self.bg_vao.render(moderngl.TRIANGLES)
        
        # Draw text
        self.prog['resolution'] = self.ctx.viewport[2:]
        self.prog['u_pivot_local'] = (0.0, 0.0)
        self.prog['u_screen_pos']  = (0.0, 0.0)
        self.prog['u_rotation']    = 0.0
        self.prog['u_opacity']     = 1.0
        self.texture.use(0)
        self.vao.render(moderngl.TRIANGLES)

class TextRenderer:
    """
    Renders text using a texture atlas generated from a TTF font via Pillow.
    Supports multiple fonts and sizes with caching for optimization.
    """
    ctx: ContextType
    font_cache: dict[tuple[str, int], dict]
    chars: str
    bg_prog: ProgramType
    prog: ProgramType
    
    def __init__(self, ctx: ContextType) -> None:
        self.ctx = ctx
        
        # Cache for font atlases: (font_path, font_size) -> {font, char_data, texture}
        self.font_cache: dict[tuple[str, int], dict] = {}
        
        # Base ASCII character set
        self._base_chars: str = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        
        # Emoji font cache
        self._emoji_font_cache: dict[int, ImageFont.FreeTypeFont | None] = {}
        
        # Background shader for rounded rectangles
        self.bg_prog = self.ctx.program(
            vertex_shader="""
            #version 430
            uniform vec2 resolution;
            uniform vec2 u_pivot_local;   // local pivot point (px)
            uniform vec2 u_screen_pos;    // screen position of pivot (px)
            uniform float u_rotation;     // radians
            uniform float u_opacity;      // 0-1

            in vec2 in_pos;
            in vec4 in_color;
            in vec4 in_rect;  // x, y, width, height
            in vec4 in_radius; // top-left, top-right, bottom-right, bottom-left
            
            out vec4 v_color;
            out vec2 v_pos;
            out vec4 v_rect;
            out vec4 v_radius;
            
            void main() {
                vec2 pos = in_pos;
                // rotate around local pivot then translate
                pos -= u_pivot_local;
                float c = cos(u_rotation);
                float s = sin(u_rotation);
                pos = vec2(pos.x*c - pos.y*s, pos.x*s + pos.y*c);
                pos += u_screen_pos;

                vec2 ndc = (pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y;
                gl_Position = vec4(ndc, 0.0, 1.0);
                v_color = vec4(in_color.rgb, in_color.a * u_opacity);
                v_pos = pos;
                v_rect = in_rect;
                v_radius = in_radius;
            }
            """,
            fragment_shader="""
            #version 430
            
            in vec4 v_color;
            in vec2 v_pos;
            in vec4 v_rect;
            in vec4 v_radius;
            out vec4 f_color;
            
            float roundedBoxSDF(vec2 center, vec2 size, vec4 radius) {
                vec2 q = abs(center) - size + vec2(radius.x);
                
                // Select the appropriate corner radius
                float r = radius.x;
                if (center.x > 0.0 && center.y > 0.0) r = radius.z; // bottom-right
                else if (center.x > 0.0 && center.y < 0.0) r = radius.y; // top-right
                else if (center.x < 0.0 && center.y > 0.0) r = radius.w; // bottom-left
                else r = radius.x; // top-left
                
                return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r;
            }
            
            void main() {
                vec2 rect_center = v_rect.xy + v_rect.zw * 0.5;
                vec2 rect_size = v_rect.zw * 0.5;
                vec2 pos_from_center = v_pos - rect_center;
                
                float dist = roundedBoxSDF(pos_from_center, rect_size, v_radius);
                float alpha = 1.0 - smoothstep(-1.0, 1.0, dist);
                
                f_color = vec4(v_color.rgb, v_color.a * alpha);
            }
            """
        )
        
        # Background VBO
        self.bg_vbo = self.ctx.buffer(reserve=4096)
        self.bg_vao = self.ctx.vertex_array(self.bg_prog, [
            (self.bg_vbo, '2f 4f 4f 4f', 'in_pos', 'in_color', 'in_rect', 'in_radius')
        ])
        
        # Shader
        self.prog = self.ctx.program(
            vertex_shader="""
            #version 430
            uniform vec2 resolution;
            uniform vec2 u_pivot_local;   // local pivot point (px)
            uniform vec2 u_screen_pos;    // screen position of pivot (px)
            uniform float u_rotation;     // radians
            uniform float u_opacity;      // 0-1

            in vec2 in_pos;
            in vec2 in_uv;
            in vec4 in_color;
            
            out vec2 v_uv;
            out vec4 v_color;
            
            void main() {
                vec2 pos = in_pos;
                // rotate around local pivot then translate
                pos -= u_pivot_local;
                float c = cos(u_rotation);
                float s = sin(u_rotation);
                pos = vec2(pos.x*c - pos.y*s, pos.x*s + pos.y*c);
                pos += u_screen_pos;

                // Pixel to NDC
                vec2 ndc = (pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y; // Flip Y
                gl_Position = vec4(ndc, 0.0, 1.0);
                v_uv = in_uv;
                v_color = vec4(in_color.rgb, in_color.a * u_opacity);
            }
            """,
            fragment_shader="""
            #version 430
            uniform sampler2D tex;
            
            in vec2 v_uv;
            in vec4 v_color;
            out vec4 f_color;
            
            void main() {
                vec4 texel = texture(tex, v_uv);
                float hi = max(max(texel.r, texel.g), texel.b);
                float lo = min(min(texel.r, texel.g), texel.b);
                float is_color = step(0.05, hi - lo);
                vec3 rgb = mix(v_color.rgb, texel.rgb, is_color);
                f_color = vec4(rgb, v_color.a * texel.a);
            }
            """
        )
        
        # Initialise new uniforms to safe defaults
        self.prog['u_pivot_local'] = (0.0, 0.0)
        self.prog['u_screen_pos']  = (0.0, 0.0)
        self.prog['u_rotation']    = 0.0
        self.prog['u_opacity']     = 1.0
        self.bg_prog['u_pivot_local'] = (0.0, 0.0)
        self.bg_prog['u_screen_pos']  = (0.0, 0.0)
        self.bg_prog['u_rotation']    = 0.0
        self.bg_prog['u_opacity']     = 1.0
        
        # Dynamic VBO for immediate mode
        self.vbo = self.ctx.buffer(reserve=65536) # 64KB
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '2f 2f 4f', 'in_pos', 'in_uv', 'in_color')
        ])

    def _get_emoji_font(self, font_size: int) -> ImageFont.FreeTypeFont | None:
        cached = self._emoji_font_cache.get(font_size)
        if cached is not None:
            return cached
        if font_size in self._emoji_font_cache:
            return None
        for name in _EMOJI_FONTS:
            try:
                font = ImageFont.truetype(find_system_font(name), font_size)
                self._emoji_font_cache[font_size] = font
                return font
            except (IOError, OSError):
                continue
        self._emoji_font_cache[font_size] = None  # type: ignore[assignment]
        return None

    @staticmethod
    def _render_glyph(char: str, font: ImageFont.FreeTypeFont,
                      embedded_color: bool = False) -> Image.Image | None:
        bbox = font.getbbox(char)
        if bbox is None:
            return None
        bl, bt, br, bb = bbox
        gw, gh = int(br - bl), int(bb - bt)
        if gw <= 0 or gh <= 0:
            return None
        img = Image.new('RGBA', (gw, gh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        try:
            if embedded_color:
                draw.text((-bl, -bt), char, font=font,  # type: ignore[arg-type]
                          fill=(255, 255, 255, 255), embedded_color=True)
            else:
                draw.text((-bl, -bt), char, font=font, fill=(255, 255, 255, 255))
        except Exception:
            draw.text((-bl, -bt), char, font=font, fill=(255, 255, 255, 255))
        return img

    @staticmethod
    def _grow_atlas(atlas_w: int, atlas_h: int,
                    atlas_img: Image.Image) -> tuple[int, int, Image.Image]:
        new_w = min(atlas_w * 2, 4096)
        new_h = min(atlas_h * 2, 4096)
        if new_w == atlas_w and new_h == atlas_h:
            return atlas_w, atlas_h, atlas_img
        new_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
        new_img.paste(atlas_img, (0, 0))
        return new_w, new_h, new_img

    def _get_or_create_font_atlas(self, font_path: str, font_size: int,
                                   text: str = "") -> dict:
        """Get or create a cached font atlas, dynamically expanding for *text*."""
        cache_key = (font_path, font_size)

        needed: set[str] = set()
        for ch in text:
            if ch not in '\n\r\t':
                needed.add(ch)

        if cache_key in self.font_cache:
            atlas = self.font_cache[cache_key]
            missing = needed - set(atlas['char_data'].keys())
            if not missing:
                return atlas
            self._expand_atlas(atlas, missing, font_size)
            return atlas

        all_chars: set[str] = set(self._base_chars) | needed
        return self._build_atlas(font_path, font_size, all_chars)

    def _build_atlas(self, font_path: str, font_size: int,
                     chars: set[str]) -> dict:
        cache_key = (font_path, font_size)
        try:
            font = ImageFont.truetype(find_system_font(font_path), font_size)
        except IOError:
            print(f"Warning: Could not load font '{font_path}'. Using default.")
            font = ImageFont.load_default()

        ascent, descent = font.getmetrics()  # type: ignore[union-attr]
        line_height: int = ascent + descent
        emoji_font = self._get_emoji_font(font_size)

        atlas_w, atlas_h = 1024, 1024
        atlas_img = Image.new('RGBA', (atlas_w, atlas_h), (0, 0, 0, 0))
        char_data: dict[str, dict] = {}
        ax, ay, row_h = 0, 0, 0

        for char in sorted(chars):
            is_emoji_char = _is_emoji(char)
            use_font = (emoji_font or font) if is_emoji_char else font
            bbox = use_font.getbbox(char)
            if bbox is None:
                continue
            bl, bt, br, bb = bbox
            advance = use_font.getlength(char)
            mw, mh = br - bl, bb - bt

            if mw <= 0 or mh <= 0:
                char_data[char] = {
                    'x': 0, 'y': 0, 'w': 0, 'h': 0,
                    'offset_x': 0, 'offset_y': 0,
                    'advance': advance,
                    'uv': (0.0, 0.0, 0.0, 0.0),
                }
                continue

            if ax + mw >= atlas_w:
                ax = 0
                ay += row_h + 2
                row_h = 0
            if ay + mh >= atlas_h:
                atlas_w, atlas_h, atlas_img = self._grow_atlas(atlas_w, atlas_h, atlas_img)

            glyph_img = self._render_glyph(char, use_font,  # type: ignore[arg-type]
                                           embedded_color=is_emoji_char and emoji_font is not None)
            if glyph_img is None:
                continue
            mw, mh = glyph_img.size
            if ax + mw >= atlas_w:
                ax = 0
                ay += row_h + 2
                row_h = 0
            if ay + mh >= atlas_h:
                atlas_w, atlas_h, atlas_img = self._grow_atlas(atlas_w, atlas_h, atlas_img)

            atlas_img.paste(glyph_img, (ax, ay))
            char_data[char] = {
                'x': ax, 'y': ay, 'w': mw, 'h': mh,
                'offset_x': bl, 'offset_y': bt,
                'advance': advance,
                'uv': (0.0, 0.0, 0.0, 0.0),  # computed below
            }
            ax += mw + 2
            row_h = max(row_h, mh)

        # Compute UVs with the final atlas dimensions (safe after any growth)
        for data in char_data.values():
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            if w > 0 and h > 0:
                data['uv'] = (x / atlas_w, y / atlas_h,
                              w / atlas_w, h / atlas_h)

        texture = self.ctx.texture(atlas_img.size, 4, atlas_img.tobytes())
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        font_atlas: dict = {
            'font': font, 'char_data': char_data, 'texture': texture,
            'ascent': ascent, 'descent': descent, 'line_height': line_height,
            '_atlas_img': atlas_img, '_atlas_w': atlas_w, '_atlas_h': atlas_h,
            '_cursor_x': ax, '_cursor_y': ay, '_row_h': row_h,
        }
        self.font_cache[cache_key] = font_atlas
        return font_atlas

    def _expand_atlas(self, atlas: dict, new_chars: set[str],
                      font_size: int) -> None:
        font = atlas['font']
        char_data = atlas['char_data']
        atlas_img = atlas['_atlas_img']
        ax, ay, row_h = atlas['_cursor_x'], atlas['_cursor_y'], atlas['_row_h']
        atlas_w, atlas_h = atlas['_atlas_w'], atlas['_atlas_h']
        emoji_font = (self._get_emoji_font(font_size)
                      if any(_is_emoji(c) for c in new_chars) else None)
        resized = False

        for char in sorted(new_chars):
            if char in char_data:
                continue
            is_emoji_char = _is_emoji(char)
            use_font = (emoji_font or font) if is_emoji_char else font
            bbox = use_font.getbbox(char)
            if bbox is None:
                continue
            bl, bt, br, bb = bbox
            advance = use_font.getlength(char)
            mw, mh = br - bl, bb - bt
            if mw <= 0 or mh <= 0:
                char_data[char] = {
                    'x': 0, 'y': 0, 'w': 0, 'h': 0,
                    'offset_x': 0, 'offset_y': 0,
                    'advance': advance,
                    'uv': (0.0, 0.0, 0.0, 0.0),
                }
                continue
            if ax + mw >= atlas_w:
                ax = 0; ay += row_h + 2; row_h = 0
            if ay + mh >= atlas_h:
                atlas_w, atlas_h, atlas_img = self._grow_atlas(atlas_w, atlas_h, atlas_img)
                resized = True
            glyph_img = self._render_glyph(char, use_font,  # type: ignore[arg-type]
                                           embedded_color=is_emoji_char and emoji_font is not None)
            if glyph_img is None:
                continue
            mw, mh = glyph_img.size
            if ax + mw >= atlas_w:
                ax = 0; ay += row_h + 2; row_h = 0
            if ay + mh >= atlas_h:
                atlas_w, atlas_h, atlas_img = self._grow_atlas(atlas_w, atlas_h, atlas_img)
                resized = True
            atlas_img.paste(glyph_img, (ax, ay))
            char_data[char] = {
                'x': ax, 'y': ay, 'w': mw, 'h': mh,
                'offset_x': bl, 'offset_y': bt,
                'advance': advance,
                'uv': (ax / atlas_w, ay / atlas_h, mw / atlas_w, mh / atlas_h),
            }
            ax += mw + 2
            row_h = max(row_h, mh)

        # If the atlas grew during expansion, recalculate ALL UVs
        if resized:
            for data in char_data.values():
                x, y, w, h = data['x'], data['y'], data['w'], data['h']
                if w > 0 and h > 0:
                    data['uv'] = (x / atlas_w, y / atlas_h,
                                  w / atlas_w, h / atlas_h)

        atlas['_cursor_x'] = ax; atlas['_cursor_y'] = ay; atlas['_row_h'] = row_h
        atlas['_atlas_w'] = atlas_w; atlas['_atlas_h'] = atlas_h; atlas['_atlas_img'] = atlas_img
        if resized:
            atlas['texture'].release()
            tex = self.ctx.texture((atlas_w, atlas_h), 4, atlas_img.tobytes())
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            atlas['texture'] = tex
        else:
            atlas['texture'].write(atlas_img.tobytes())

    def get_text_width(self, text: str, scale: float = 1.0, style: TextStyle = DEFAULT_16_TEXT_STYLE) -> float:
        """Calculate the width of the text (widest line if multi-line)."""
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size, text=text)
        char_data = font_atlas['char_data']
        ls = style.letter_spacing

        max_w = 0.0
        for line in text.split('\n'):
            w = 0.0
            for char in line:
                if char in char_data:
                    w += (char_data[char]['advance'] + ls) * scale
            if w > max_w:
                max_w = w
        return max_w
    
    def _get_text_bounds(self, text: str, scale: float = 1.0, style: TextStyle = DEFAULT_16_TEXT_STYLE) -> FloatVec2:
        """Calculate the bounding box (width, height) of the text,
        with multi-line and letter-spacing support."""
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size, text=text)
        char_data = font_atlas['char_data']
        line_h = font_atlas['line_height'] * scale
        ls = style.letter_spacing

        lines = text.split('\n')
        max_w = 0.0
        for line in lines:
            w = 0.0
            for char in line:
                if char in char_data:
                    w += (char_data[char]['advance'] + ls) * scale
            if w > max_w:
                max_w = w

        num = len(lines)
        total_h = line_h * (1.0 + (num - 1) * style.line_spacing) if num > 0 else 0.0
        return max_w, total_h
    
    def _normalize_margin(self, margin: float | tuple[float, float, float, float] | tuple[float, float] | list[float]) -> tuple[float, float, float, float]:
        """Normalize margin to (top, right, bottom, left)."""
        if isinstance(margin, (int, float)):
            return (margin, margin, margin, margin)
        elif isinstance(margin, (list, tuple)):
            if len(margin) == 2:
                return (margin[0], margin[1], margin[0], margin[1])
            elif len(margin) == 4:
                return (margin[0], margin[1], margin[2], margin[3])
        return margin[0], margin[1], margin[2], margin[3]
    
    def _normalize_radius(self, radius: float | tuple[float, float, float, float] | tuple[float, float] | list[float]) -> tuple[float, float, float, float]:
        """Normalize border radius to (top-left, top-right, bottom-right, bottom-left)."""
        if isinstance(radius, (int, float)):
            return (radius, radius, radius, radius)
        elif isinstance(radius, (list, tuple)):
            if len(radius) == 2:
                return (radius[0], radius[1], radius[0], radius[1])
            elif len(radius) == 4:
                return (radius[0], radius[1], radius[2], radius[3])
        return radius[0], radius[1], radius[2], radius[3]
    
    def _generate_background_vertices(self, x: float, y: float, width: float, height: float, 
                                     bg_color: ColorType, margin: tuple[float, float, float, float],
                                     radius: tuple[float, float, float, float]) -> list[float]:
        """Generate vertices for a rounded rectangle background."""
        # Apply margin
        bg_x = x - margin[3]  # left
        bg_y = y - margin[0]  # top
        bg_w = width + margin[1] + margin[3]  # right + left
        bg_h = height + margin[0] + margin[2]  # top + bottom
        
        vertices = []
        rect_data = [bg_x, bg_y, bg_w, bg_h]
        
        # Two triangles forming a quad
        # Each vertex: (x, y, r, g, b, a, rect_x, rect_y, rect_w, rect_h, radius_tl, radius_tr, radius_br, radius_bl)
        
        # Triangle 1
        vertices.extend([bg_x, bg_y, *bg_color, *rect_data, *radius])  # top-left
        vertices.extend([bg_x + bg_w, bg_y, *bg_color, *rect_data, *radius])  # top-right
        vertices.extend([bg_x, bg_y + bg_h, *bg_color, *rect_data, *radius])  # bottom-left
        
        # Triangle 2
        vertices.extend([bg_x + bg_w, bg_y, *bg_color, *rect_data, *radius])  # top-right
        vertices.extend([bg_x, bg_y + bg_h, *bg_color, *rect_data, *radius])  # bottom-left
        vertices.extend([bg_x + bg_w, bg_y + bg_h, *bg_color, *rect_data, *radius])  # bottom-right
        
        return vertices

    def _generate_vertices(self, text: str, pos: FloatVec2, scale: float = 1.0,
            color: ColorType = WHITE, pivot: Pivot = Pivot.TOP_LEFT, char_data: dict = {},
            line_height: float = 0.0, line_spacing: float = 1.0,
            letter_spacing: float = 0.0) -> list[float]:
        """Generate textured quads for *text* using the pre-built font atlas.

        Each glyph is positioned using ``offset_x`` / ``offset_y`` from
        ``font.getbbox`` so that descenders (g j p q y …) and special
        characters sit on the correct baseline.
        """

        if not char_data:
            raise ValueError("char_data is required for _generate_vertices")

        # --- text dimensions for pivot offset ---
        lines = text.split('\n')
        lh = line_height * scale if line_height > 0 else 0.0
        max_w = 0.0
        for line in lines:
            w = sum((char_data.get(c, {}).get('advance', 0) + letter_spacing) for c in line) * scale
            if w > max_w:
                max_w = w

        num = len(lines)
        total_h = lh * (1.0 + (num - 1) * line_spacing) if num > 0 else 0.0

        # Pivot produces the translation so the pivot point sits at *pos*
        ox, oy = pivot.offset(max_w, total_h)
        start_x = pos[0] + ox
        start_y = pos[1] + oy

        vertices: list[float] = []
        cursor_y = start_y

        for line in lines:
            cursor_x = start_x

            for char in line:
                if char not in char_data:
                    continue
                data = char_data[char]

                if data['w'] == 0:
                    cursor_x += (data['advance'] + letter_spacing) * scale
                    continue

                w = data['w'] * scale
                h = data['h'] * scale
                gx = cursor_x + data['offset_x'] * scale
                gy = cursor_y + data['offset_y'] * scale

                u0, v0, du, dv = data['uv']

                # Triangle 1: TL, TR, BL
                vertices.extend([gx,     gy,     u0,      v0,      *color])
                vertices.extend([gx + w, gy,     u0 + du, v0,      *color])
                vertices.extend([gx,     gy + h, u0,      v0 + dv, *color])
                # Triangle 2: TR, BL, BR
                vertices.extend([gx + w, gy,     u0 + du, v0,      *color])
                vertices.extend([gx,     gy + h, u0,      v0 + dv, *color])
                vertices.extend([gx + w, gy + h, u0 + du, v0 + dv, *color])

                cursor_x += (data['advance'] + letter_spacing) * scale

            cursor_y += lh * line_spacing

        return vertices

    def draw_text(self, text: str, pos: FloatVec2, scale: float = 1.0, style: TextStyle = DEFAULT_16_TEXT_STYLE, pivot: Pivot = Pivot.TOP_LEFT) -> None:
        if not text:
            return

        pivot = resolve_pivot(pivot)

        # Get font atlas for this style
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size, text=text)
        char_data = font_atlas['char_data']
        texture = font_atlas['texture']
            
        # Get text dimensions for background
        text_width, text_height = self._get_text_bounds(text, scale, style)
        
        # Adjust position based on pivot for background calculation
        bg_ox, bg_oy = pivot.offset(text_width, text_height)
        bg_x = pos[0] + bg_ox
        bg_y = pos[1] + bg_oy
        
        # Draw background if specified
        if style.bg_color[3] > 0:  # Only draw if alpha > 0
            margin = self._normalize_margin(style.bg_margin)
            radius = self._normalize_radius(style.bg_border_radius)
            bg_vertices = self._generate_background_vertices(bg_x, bg_y, text_width, text_height,
                                                            style.bg_color, margin, radius)
            
            bg_data = np.array(bg_vertices, dtype='f4').tobytes()
            self.bg_vbo.write(bg_data)
            self.bg_prog['resolution'] = self.ctx.viewport[2:]
            self.bg_prog['u_pivot_local'] = (0.0, 0.0)
            self.bg_prog['u_screen_pos']  = (0.0, 0.0)
            self.bg_prog['u_rotation']    = 0.0
            self.bg_prog['u_opacity']     = 1.0
            self.ctx.enable(moderngl.BLEND)
            self.bg_vao.render(moderngl.TRIANGLES, vertices=len(bg_vertices)//14)
        
        # Draw text
        vertices = self._generate_vertices(
            text, pos, scale, style.color, pivot, char_data,
            line_height=font_atlas['line_height'],
            line_spacing=style.line_spacing,
            letter_spacing=style.letter_spacing,
        )
        if not vertices:
            return

        # Update VBO
        data_bytes = np.array(vertices, dtype='f4').tobytes()
        self.vbo.write(data_bytes)

        # Reset uniforms for immediate-mode rendering (no transforms)
        self.prog['resolution'] = self.ctx.viewport[2:]
        self.prog['u_pivot_local'] = (0.0, 0.0)
        self.prog['u_screen_pos']  = (0.0, 0.0)
        self.prog['u_rotation']    = 0.0
        self.prog['u_opacity']     = 1.0
        texture.use(0)

        # Draw
        self.ctx.enable(moderngl.BLEND)
        self.vao.render(moderngl.TRIANGLES, vertices=len(vertices)//8)

    def create_label(self, text: str, x: float, y: float, scale: float = 1.0, style: TextStyle = DEFAULT_16_TEXT_STYLE, pivot: Pivot = Pivot.TOP_LEFT) -> TextLabel:
        if not text:
            # Return empty label with default texture
            font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
            return TextLabel(self.ctx, self.prog, font_atlas['texture'], [])

        pivot = resolve_pivot(pivot)

        # Get font atlas for this style
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size, text=text)
        char_data = font_atlas['char_data']
        texture = font_atlas['texture']
        
        # Generate text vertices
        vertices = self._generate_vertices(
            text, (x, y), scale, style.color, pivot, char_data,
            line_height=font_atlas['line_height'],
            line_spacing=style.line_spacing,
            letter_spacing=style.letter_spacing,
        )
        
        # Generate background vertices if needed
        bg_vertices = None
        if style.bg_color[3] > 0:
            text_width, text_height = self._get_text_bounds(text, scale, style)

            bg_ox, bg_oy = pivot.offset(text_width, text_height)
            bg_x = x + bg_ox
            bg_y = y + bg_oy

            margin = self._normalize_margin(style.bg_margin)
            radius = self._normalize_radius(style.bg_border_radius)
            bg_vertices = self._generate_background_vertices(bg_x, bg_y, text_width, text_height,
                                                            style.bg_color, margin, radius)
        
        return TextLabel(self.ctx, self.prog, texture, vertices, self.bg_prog, bg_vertices)