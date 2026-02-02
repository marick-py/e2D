from enum import Enum
from typing import Optional
from PIL import Image, ImageFont
from attr import dataclass
import numpy as np
import moderngl
from .types import ColorType, VAOType, VectorType, ContextType, ProgramType, BufferType, TextureType
from .colors import normalize_color
from .color_defs import WHITE, BLACK

@dataclass
class TextStyle:
    font: str = "arial.ttf"
    font_size: int = 32
    color: ColorType = (1.0, 1.0, 1.0, 1.0)
    bg_color: ColorType = (0.0, 0.0, 0.0, 0.9)
    bg_margin: float | tuple[float, float, float, float] | tuple[float, float] | list[float] = 15.0
    bg_border_radius: float | tuple[float, float, float, float] | tuple[float, float] | list[float] = 15.0

class Pivots(Enum):
    TOP_LEFT = 0
    TOP_MIDDLE = 1
    TOP_RIGHT = 2
    LEFT = 3
    CENTER = 4
    RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_MIDDLE = 7
    BOTTOM_RIGHT = 8

DEFAULT_TEXT_STYLE = TextStyle()

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
            self.bg_vao.render(moderngl.TRIANGLES)
        
        # Draw text
        self.prog['resolution'] = self.ctx.viewport[2:]
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
            
            in vec2 in_pos;
            in vec4 in_color;
            in vec4 in_rect;  // x, y, width, height
            in vec4 in_radius; // top-left, top-right, bottom-right, bottom-left
            
            out vec4 v_color;
            out vec2 v_pos;
            out vec4 v_rect;
            out vec4 v_radius;
            
            void main() {
                vec2 ndc = (in_pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y;
                gl_Position = vec4(ndc, 0.0, 1.0);
                v_color = in_color;
                v_pos = in_pos;
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
            
            in vec2 in_pos;
            in vec2 in_uv;
            in vec4 in_color;
            
            out vec2 v_uv;
            out vec4 v_color;
            
            void main() {
                // Pixel to NDC
                vec2 ndc = (in_pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y; // Flip Y
                gl_Position = vec4(ndc, 0.0, 1.0);
                v_uv = in_uv;
                v_color = in_color;
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
        
        # Dynamic VBO for immediate mode
        self.vbo = self.ctx.buffer(reserve=65536) # 64KB
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '2f 2f 4f', 'in_pos', 'in_uv', 'in_color')
        ])

    def _get_or_create_font_atlas(self, font_path: str, font_size: int) -> dict:
        """Get or create a cached font atlas for the given font and size."""
        cache_key = (font_path, font_size)
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Load font
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Warning: Could not load font '{font_path}'. Using default.")
            font = ImageFont.load_default()
        
        # Generate Atlas
        char_data = {}
        atlas_w, atlas_h = 1024, 1024
        atlas_img = Image.new('RGBA', (atlas_w, atlas_h), (0, 0, 0, 0))
        
        x, y = 0, 0
        max_h = 0
        
        for char in self.chars:
            mask = font.getmask(char)
            w, h = mask.size
            
            if x + w >= atlas_w:
                x = 0
                y += max_h + 2
                max_h = 0
            
            # Create char image
            char_img = Image.new('RGBA', (w, h), (255, 255, 255, 255))
            mask_img = Image.new('L', (w, h))
            mask_img.im.paste(mask, (0, 0, w, h))
            atlas_img.paste(char_img, (x, y), mask_img)
            
            char_data[char] = {
                'x': x, 'y': y, 'w': w, 'h': h,
                'uv': (x/atlas_w, y/atlas_h, w/atlas_w, h/atlas_h)
            }
            
            x += w + 2
            max_h = max(max_h, h)
        
        # Create texture
        texture = self.ctx.texture(atlas_img.size, 4, atlas_img.tobytes())
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        
        # Cache it
        font_atlas = {
            'font': font,
            'char_data': char_data,
            'texture': texture
        }
        self.font_cache[cache_key] = font_atlas
        
        return font_atlas

    def get_text_width(self, text: str, scale: float = 1.0, style: TextStyle = DEFAULT_TEXT_STYLE) -> float:
        """Calculate the width of the text."""
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
        char_data = font_atlas['char_data']
        
        total_w = 0
        for char in text:
            if char in char_data:
                data = char_data[char]
                total_w += (data['w'] * scale) + (2 * scale)
        return total_w
    
    def _get_text_bounds(self, text: str, scale: float = 1.0, style: TextStyle = DEFAULT_TEXT_STYLE) -> tuple[float, float]:
        """Calculate the bounding box dimensions (width, height) of the text."""
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
        char_data = font_atlas['char_data']
        
        total_w = 0
        ref_char = 'M' if 'M' in char_data else self.chars[0]
        line_height = char_data[ref_char]['h'] * scale
        
        for char in text:
            if char in char_data:
                data = char_data[char]
                total_w += (data['w'] * scale) + (2 * scale)
        
        return total_w, line_height
    
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

    def _generate_vertices(self, text: str, pos: VectorType, scale: float = 1.0, 
            color: ColorType = WHITE, pivot: Pivots | int = Pivots.TOP_LEFT, char_data: dict = {} ) -> list[float]:

        if not char_data:
            raise ValueError("char_data is required for _generate_vertices")
        # Calculate text size first for pivoting
        total_w = 0
        max_h = 0
        
        # Determine max height for proper vertical alignment instead of per-glyph height
        # This fixes the "jittery" baseline issue by ensuring all chars use the same vertical metric
        # Use 'M' or 'H' or '|' as a reference for height if available, otherwise use max found
        ref_char = 'M' if 'M' in char_data else self.chars[0]
        line_height = char_data[ref_char]['h'] * scale
        
        for char in text:
            if char in char_data:
                data = char_data[char]
                total_w += (data['w'] * scale) + (2 * scale)
                max_h = max(max_h, data['h'] * scale)
        
        # Use consistent line height for vertical alignment
        max_h = line_height if line_height > 0 else max_h
        
        # Adjust start position based on pivot
        start_x, start_y = pos
        if pivot == Pivots.TOP_RIGHT:
            start_x -= total_w
        elif pivot == Pivots.BOTTOM_LEFT:
            start_y -= max_h
        elif pivot == Pivots.BOTTOM_RIGHT:
            start_x -= total_w
            start_y -= max_h
        elif pivot == Pivots.CENTER:
            start_x -= total_w / 2
            start_y -= max_h / 2
            
        vertices = []
        cursor_x = start_x
        cursor_y = start_y
        
        for char in text:
            if char not in char_data:
                continue
                
            data = char_data[char]
            w = data['w'] * scale
            h = data['h'] * scale
            
            # Align characters to bottom of line (baseline alignment)
            # Offset smaller characters down so they sit on the same baseline as taller ones
            y_offset = max_h - h
            
            # Quad vertices (x, y, u, v, r, g, b, a)
            # TL
            vertices.extend([cursor_x, cursor_y + y_offset, data['uv'][0], data['uv'][1], *color])
            
            # TR
            vertices.extend([cursor_x + w, cursor_y + y_offset, data['uv'][0] + data['uv'][2], data['uv'][1], *color])
            
            # BL
            vertices.extend([cursor_x, cursor_y + y_offset + h, data['uv'][0], data['uv'][1] + data['uv'][3], *color])
            
            # Triangle 2
            # TR
            vertices.extend([cursor_x + w, cursor_y + y_offset, data['uv'][0] + data['uv'][2], data['uv'][1], *color])
            # BL
            vertices.extend([cursor_x, cursor_y + y_offset + h, data['uv'][0], data['uv'][1] + data['uv'][3], *color])
            # BR
            vertices.extend([cursor_x + w, cursor_y + y_offset + h, data['uv'][0] + data['uv'][2], data['uv'][1] + data['uv'][3], *color])
            
            cursor_x += w + (2 * scale) # Spacing
            
        return vertices

    def draw_text(self, text: str, pos: VectorType, scale: float = 1.0, style: TextStyle = DEFAULT_TEXT_STYLE, pivot: Pivots | int = Pivots.TOP_LEFT) -> None:
        if not text:
            return
        
        # Get font atlas for this style
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
        char_data = font_atlas['char_data']
        texture = font_atlas['texture']
            
        # Get text dimensions for background
        text_width, text_height = self._get_text_bounds(text, scale, style)
        
        # Adjust position based on pivot for background calculation
        bg_x, bg_y = pos
        if pivot == Pivots.TOP_RIGHT:
            bg_x -= text_width
        elif pivot == Pivots.BOTTOM_LEFT:
            bg_y -= text_height
        elif pivot == Pivots.BOTTOM_RIGHT:
            bg_x -= text_width
            bg_y -= text_height
        elif pivot == Pivots.CENTER:
            bg_x -= text_width / 2
            bg_y -= text_height / 2
        
        # Draw background if specified
        if style.bg_color[3] > 0:  # Only draw if alpha > 0
            margin = self._normalize_margin(style.bg_margin)
            radius = self._normalize_radius(style.bg_border_radius)
            bg_vertices = self._generate_background_vertices(bg_x, bg_y, text_width, text_height,
                                                            style.bg_color, margin, radius)
            
            bg_data = np.array(bg_vertices, dtype='f4').tobytes()
            self.bg_vbo.write(bg_data)
            self.bg_prog['resolution'] = self.ctx.viewport[2:]
            self.ctx.enable(moderngl.BLEND)
            self.bg_vao.render(moderngl.TRIANGLES, vertices=len(bg_vertices)//14)
        
        # Draw text
        vertices = self._generate_vertices(text, pos, scale, style.color, pivot, char_data)
        if not vertices:
            return

        # Update VBO
        data_bytes = np.array(vertices, dtype='f4').tobytes()
        self.vbo.write(data_bytes)

        # Update Uniforms
        self.prog['resolution'] = self.ctx.viewport[2:]
        texture.use(0)

        # Draw
        self.ctx.enable(moderngl.BLEND)
        self.vao.render(moderngl.TRIANGLES, vertices=len(vertices)//8)

    def create_label(self, text: str, x: float, y: float, scale: float = 1.0, style: TextStyle = DEFAULT_TEXT_STYLE, pivot: Pivots | int = Pivots.TOP_LEFT) -> TextLabel:
        if not text:
            # Return empty label with default texture
            font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
            return TextLabel(self.ctx, self.prog, font_atlas['texture'], [])
        
        # Get font atlas for this style
        font_atlas = self._get_or_create_font_atlas(style.font, style.font_size)
        char_data = font_atlas['char_data']
        texture = font_atlas['texture']
        
        # Generate text vertices
        vertices = self._generate_vertices(text, (x, y), scale, style.color, pivot, char_data)
        
        # Generate background vertices if needed
        bg_vertices = None
        if style.bg_color[3] > 0:
            text_width, text_height = self._get_text_bounds(text, scale, style)
            
            # Adjust position based on pivot
            bg_x, bg_y = x, y
            if pivot == Pivots.TOP_RIGHT:
                bg_x -= text_width
            elif pivot == Pivots.BOTTOM_LEFT:
                bg_y -= text_height
            elif pivot == Pivots.BOTTOM_RIGHT:
                bg_x -= text_width
                bg_y -= text_height
            elif pivot == Pivots.CENTER:
                bg_x -= text_width / 2
                bg_y -= text_height / 2
            
            margin = self._normalize_margin(style.bg_margin)
            radius = self._normalize_radius(style.bg_border_radius)
            bg_vertices = self._generate_background_vertices(bg_x, bg_y, text_width, text_height,
                                                            style.bg_color, margin, radius)
        
        return TextLabel(self.ctx, self.prog, texture, vertices, self.bg_prog, bg_vertices)