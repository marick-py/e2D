from typing import Optional
from PIL import Image, ImageFont
from attr import dataclass
import numpy as np
import moderngl
from ._types import ColorType, VAOType, ContextType, ProgramType, BufferType, TextureType
from .colors import normalize_color
from .palette import WHITE, BLACK
from .ui.base import Pivot, resolve_pivot
from .utils import find_system_font

# Backward-compat alias — new code should use ``Pivot`` directly.
Pivots = Pivot

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
        self.font_cache = {}
        
        # Character set to render
        self.chars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        
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
                float alpha = texture(tex, v_uv).a;
                f_color = vec4(v_color.rgb, v_color.a * alpha);
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

    def _get_or_create_font_atlas(self, font_path: str, font_size: int) -> dict:
        """Get or create a cached font atlas for the given font and size.

        Each character entry now stores ``offset_x``, ``offset_y`` (from
        ``font.getbbox``) and ``advance`` (horizontal advance width) so that
        descenders (g j p q y …) and special characters are positioned
        correctly on the baseline.
        """
        cache_key = (font_path, font_size)

        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # Load font
        try:
            font = ImageFont.truetype(find_system_font(font_path), font_size)
        except IOError:
            print(f"Warning: Could not load font '{font_path}'. Using default.")
            font = ImageFont.load_default()

        ascent, descent = font.getmetrics()  # type: ignore[union-attr]
        line_height = ascent + descent

        # Generate atlas
        char_data: dict = {}
        atlas_w, atlas_h = 1024, 1024
        atlas_img = Image.new('RGBA', (atlas_w, atlas_h), (0, 0, 0, 0))

        ax, ay = 0, 0   # current position in the atlas
        row_h = 0

        for char in self.chars:
            bbox = font.getbbox(char)
            if bbox is None:
                continue
            bl, bt, br, bb = bbox
            advance = font.getlength(char)

            # Get the rendered glyph mask
            mask = font.getmask(char)
            mw, mh = mask.size

            if mw <= 0 or mh <= 0:
                # Zero-width character (e.g. space)
                char_data[char] = {
                    'x': 0, 'y': 0, 'w': 0, 'h': 0,
                    'offset_x': 0, 'offset_y': 0,
                    'advance': advance,
                    'uv': (0.0, 0.0, 0.0, 0.0),
                }
                continue

            # Wrap to next row if needed
            if ax + mw >= atlas_w:
                ax = 0
                ay += row_h + 2
                row_h = 0

            # Create white glyph + alpha mask and paste
            char_img = Image.new('RGBA', (mw, mh), (255, 255, 255, 255))
            mask_img = Image.new('L', (mw, mh))
            mask_img.im.paste(mask, (0, 0, mw, mh))
            atlas_img.paste(char_img, (ax, ay), mask_img)

            char_data[char] = {
                'x': ax, 'y': ay,
                'w': mw, 'h': mh,
                'offset_x': bl,       # horizontal bearing
                'offset_y': bt,       # vertical offset from pen origin
                'advance': advance,   # horizontal advance to next char
                'uv': (ax / atlas_w, ay / atlas_h, mw / atlas_w, mh / atlas_h),
            }

            ax += mw + 2
            row_h = max(row_h, mh)

        # Create GPU texture
        texture = self.ctx.texture(atlas_img.size, 4, atlas_img.tobytes())
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        # Cache the atlas together with font metrics
        font_atlas = {
            'font': font,
            'char_data': char_data,
            'texture': texture,
            'ascent': ascent,
            'descent': descent,
            'line_height': line_height,
        }
        self.font_cache[cache_key] = font_atlas
        return font_atlas

    def get_text_width(self, text: str, scale: float = 1.0, style: TextStyle = DEFAULT_16_TEXT_STYLE) -> float:
        """Calculate the width of the text (widest line if multi-line)."""
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
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
    
    def _get_text_bounds(self, text: str, scale: float = 1.0, style: TextStyle = DEFAULT_16_TEXT_STYLE) -> tuple[float, float]:
        """Calculate the bounding box (width, height) of the text,
        with multi-line and letter-spacing support."""
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
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

    def _generate_vertices(self, text: str, pos: tuple[float, float], scale: float = 1.0,
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

    def draw_text(self, text: str, pos: tuple[float, float], scale: float = 1.0, style: TextStyle = DEFAULT_16_TEXT_STYLE, pivot: Pivot = Pivot.TOP_LEFT) -> None:
        if not text:
            return

        pivot = resolve_pivot(pivot)

        # Get font atlas for this style
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
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
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
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