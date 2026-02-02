import moderngl
import numpy as np
from .commons import get_pattr, get_pattr_value, set_pattr_value
from .types import VAOType, VectorType, ColorType, ContextType, ProgramType, BufferType
from .colors import normalize_color
from .color_defs import WHITE, BLACK, TRANSPARENT
from typing import Optional, Sequence
from enum import Enum


class FillMode(Enum):
    FILL = 0
    STROKE = 1
    FILL_STROKE = 2

class ShapeLabel:
    """A pre-rendered shape for efficient repeated drawing."""
    ctx: ContextType
    prog: ProgramType
    vbo: BufferType
    vao: VAOType
    vertex_count: int
    shape_type: str
    
    def __init__(self, ctx: ContextType, prog: ProgramType, 
                 vbo: BufferType, vertex_count: int, shape_type: str = 'line') -> None:
        self.ctx = ctx
        self.prog = prog
        self.vbo = vbo
        self.vertex_count = vertex_count
        self.shape_type = shape_type
        
        # Create VAO based on shape type
        if shape_type == 'circle':
            self.vao = self.ctx.vertex_array(self.prog, [
                (self.vbo, '2f 4f 1f 4f 1f 1f 2f', 'in_pos', 'in_color', 'in_radius',
                 'in_border_color', 'in_border_width', 'in_aa', 'in_center')
            ])
        elif shape_type == 'rect':
            self.vao = self.ctx.vertex_array(self.prog, [
                (self.vbo, '2f 4f 1f 4f 1f 1f 2f 2f', 'in_pos', 'in_color', 'in_radius',
                 'in_border_color', 'in_border_width', 'in_aa', 'in_size', 'in_local_pos')
            ])
        else:  # line
            self.vao = self.ctx.vertex_array(self.prog, [
                (self.vbo, '2f 4f', 'in_pos', 'in_color')
            ])
    
    def draw(self) -> None:
        """Draw the cached shape."""
        self.ctx.enable(moderngl.BLEND)
        set_pattr_value(self.prog, 'resolution', self.ctx.viewport[2:])
        self.vao.render(moderngl.TRIANGLES, vertices=self.vertex_count)


class InstancedShapeBatch:
    """High-performance instanced batch for drawing thousands of shapes with minimal CPU overhead."""
    ctx: ContextType
    prog: ProgramType
    shape_type: str
    max_instances: int
    instance_count: int
    floats_per_instance: int
    instance_buffer: BufferType
    quad_vbo: BufferType
    vao: VAOType
    instance_data: list[float]
    
    def __init__(self, ctx: ContextType, prog: ProgramType, shape_type: str = 'circle', max_instances: int = 100000) -> None:
        self.ctx = ctx
        self.prog = prog
        self.shape_type = shape_type
        self.max_instances = max_instances
        self.instance_count = 0
        
        # Per-instance data (stored once, reused for drawing)
        if shape_type == 'circle':
            # Per-instance: center(2f), color(4f), radius(1f), border_color(4f), border_width(1f), aa(1f) = 13 floats
            self.floats_per_instance = 13
            self.instance_buffer = self.ctx.buffer(reserve=max_instances * self.floats_per_instance * 4, dynamic=True)
            
            # Template quad (6 vertices for 2 triangles) - shared by all instances
            # These are the LOCAL positions that will be offset by instance data
            quad_verts = np.array([
                -1.0, -1.0,
                 1.0, -1.0,
                -1.0,  1.0,
                 1.0, -1.0,
                -1.0,  1.0,
                 1.0,  1.0
            ], dtype='f4')
            self.quad_vbo = self.ctx.buffer(quad_verts.tobytes())
            
            # Create VAO with per-vertex and per-instance attributes
            self.vao = self.ctx.vertex_array(
                self.prog,
                [
                    (self.quad_vbo, '2f', 'in_vertex'),  # Per-vertex (6 vertices)
                    (self.instance_buffer, '2f 4f 1f 4f 1f 1f/i', 'in_center', 'in_color', 'in_radius',
                     'in_border_color', 'in_border_width', 'in_aa')  # Per-instance (divisor = 1)
                ]
            )
        elif shape_type == 'rect':
            # Per-instance: center(2f), size(2f), color(4f), radius(1f), border_color(4f), border_width(1f), aa(1f), rotation(1f) = 16 floats
            self.floats_per_instance = 16
            self.instance_buffer = self.ctx.buffer(reserve=max_instances * self.floats_per_instance * 4, dynamic=True)
            
            quad_verts = np.array([
                -1.0, -1.0,
                 1.0, -1.0,
                -1.0,  1.0,
                 1.0, -1.0,
                -1.0,  1.0,
                 1.0,  1.0
            ], dtype='f4')
            self.quad_vbo = self.ctx.buffer(quad_verts.tobytes())
            
            self.vao = self.ctx.vertex_array(
                self.prog,
                [
                    (self.quad_vbo, '2f', 'in_vertex'),
                    (self.instance_buffer, '2f 2f 4f 1f 4f 1f 1f 1f/i', 'in_center', 'in_size', 'in_color', 
                     'in_radius', 'in_border_color', 'in_border_width', 'in_aa', 'in_rotation')
                ]
            )
        elif shape_type == 'line':
            # Per-instance: start(2f), end(2f), width(1f), color(4f) = 9 floats
            self.floats_per_instance = 9
            self.instance_buffer = self.ctx.buffer(reserve=max_instances * self.floats_per_instance * 4, dynamic=True)
            
            # Quad template for line segment
            quad_verts = np.array([
                -1.0, -1.0,
                 1.0, -1.0,
                -1.0,  1.0,
                 1.0, -1.0,
                -1.0,  1.0,
                 1.0,  1.0
            ], dtype='f4')
            self.quad_vbo = self.ctx.buffer(quad_verts.tobytes())
            
            self.vao = self.ctx.vertex_array(
                self.prog,
                [
                    (self.quad_vbo, '2f', 'in_quad_pos'),
                    (self.instance_buffer, '2f 2f 1f 4f/i', 'in_start', 'in_end', 'in_width', 'in_color')
                ]
            )
        
        self.instance_data = []
    
    def add_circle(self, center: VectorType, radius: float,
                   color: ColorType = WHITE,
                   border_color: ColorType = TRANSPARENT,
                   border_width: float = 0.0,
                   antialiasing: float = 1.0) -> None:
        """Add a circle instance to the batch."""
        self.instance_data.extend([*center, *color, radius, *border_color, border_width, antialiasing])
        self.instance_count += 1
    
    def add_circles_numpy(self, centers: np.ndarray, radii: np.ndarray, 
                          colors: np.ndarray,
                          border_colors: Optional[np.ndarray] = None,
                          border_widths: Optional[np.ndarray] = None,
                          antialiasing: float = 1.0) -> None:
        """Add multiple circles efficiently using numpy arrays (10-50x faster than loop).
        
        Args:
            centers: (N, 2) array of (x, y) positions
            radii: (N,) array of radii
            colors: (N, 4) array of (r, g, b, a) colors
            border_colors: (N, 4) array or None (defaults to transparent)
            border_widths: (N,) array or None (defaults to 0)
            antialiasing: Antialiasing width (scalar applied to all)
        """
        n = len(centers)
        if border_colors is None:
            border_colors = np.zeros((n, 4), dtype='f4')
        if border_widths is None:
            border_widths = np.zeros(n, dtype='f4')
        
        # Build interleaved data: [cx, cy, r, g, b, a, radius, br, bg, bb, ba, bw, aa] * N
        # Format: center(2), color(4), radius(1), border_color(4), border_width(1), aa(1) = 13 floats
        data = np.empty((n, 13), dtype='f4')
        data[:, 0:2] = centers
        data[:, 2:6] = colors
        data[:, 6] = radii
        data[:, 7:11] = border_colors
        data[:, 11] = border_widths
        data[:, 12] = antialiasing
        
        self.instance_data.extend(data.ravel())
        self.instance_count += n
    
    def add_rect(self, center: VectorType, size: VectorType,
                color: ColorType = WHITE,
                corner_radius: float = 0.0,
                border_color: ColorType = TRANSPARENT,
                border_width: float = 0.0,
                antialiasing: float = 1.0,
                rotation: float = 0.0) -> None:
        """Add a rectangle instance to the batch."""
        self.instance_data.extend([*center, *size, *color, corner_radius, *border_color, border_width, antialiasing, rotation])
        self.instance_count += 1
    
    def add_rects_numpy(self, centers: np.ndarray, sizes: np.ndarray,
                        colors: np.ndarray,
                        corner_radii: Optional[np.ndarray] = None,
                        border_colors: Optional[np.ndarray] = None,
                        border_widths: Optional[np.ndarray] = None,
                        antialiasing: float = 1.0,
                        rotations: Optional[np.ndarray] = None) -> None:
        """Add multiple rectangles efficiently using numpy arrays (10-50x faster than loop).
        
        Args:
            centers: (N, 2) array of (x, y) positions
            sizes: (N, 2) array of (width, height)
            colors: (N, 4) array of (r, g, b, a) colors
            corner_radii: (N,) array or None (defaults to 0)
            border_colors: (N, 4) array or None (defaults to transparent)
            border_widths: (N,) array or None (defaults to 0)
            antialiasing: Antialiasing width (scalar applied to all)
            rotations: (N,) array or None (defaults to 0)
        """
        n = len(centers)
        if corner_radii is None:
            corner_radii = np.zeros(n, dtype='f4')
        if border_colors is None:
            border_colors = np.zeros((n, 4), dtype='f4')
        if border_widths is None:
            border_widths = np.zeros(n, dtype='f4')
        if rotations is None:
            rotations = np.zeros(n, dtype='f4')
        
        # Format: center(2), size(2), color(4), radius(1), border_color(4), border_width(1), aa(1), rotation(1) = 16 floats
        data = np.empty((n, 16), dtype='f4')
        data[:, 0:2] = centers
        data[:, 2:4] = sizes
        data[:, 4:8] = colors
        data[:, 8] = corner_radii
        data[:, 9:13] = border_colors
        data[:, 13] = border_widths
        data[:, 14] = antialiasing
        data[:, 15] = rotations
        
        self.instance_data.extend(data.ravel())
        self.instance_count += n
    
    def add_line(self, start: VectorType, end: VectorType,
                width: float = 1.0,
                color: ColorType = WHITE) -> None:
        """Add a line instance to the batch."""
        self.instance_data.extend([*start, *end, width, *color])
        self.instance_count += 1
    
    def add_lines_numpy(self, starts: np.ndarray, ends: np.ndarray,
                        widths: np.ndarray, colors: np.ndarray) -> None:
        """Add multiple lines efficiently using numpy arrays (10-50x faster than loop).
        
        Args:
            starts: (N, 2) array of start (x, y) positions
            ends: (N, 2) array of end (x, y) positions
            widths: (N,) array of line widths
            colors: (N, 4) array of (r, g, b, a) colors
        """
        n = len(starts)
        
        # Format: start(2), end(2), width(1), color(4) = 9 floats
        data = np.empty((n, 9), dtype='f4')
        data[:, 0:2] = starts
        data[:, 2:4] = ends
        data[:, 4] = widths
        data[:, 5:9] = colors
        
        self.instance_data.extend(data.ravel())
        self.instance_count += n
    
    def flush(self) -> None:
        """Draw all instances in a single draw call."""
        if self.instance_count == 0:
            return
        
        # Upload instance data
        data = np.array(self.instance_data, dtype='f4')
        self.instance_buffer.write(data.tobytes())
        
        # Draw all instances with one call
        self.ctx.enable(moderngl.BLEND)
        set_pattr_value(self.prog, 'resolution', self.ctx.viewport[2:])
        self.vao.render(moderngl.TRIANGLES, vertices=6, instances=self.instance_count)
        
        self.instance_data.clear()
        self.instance_count = 0
    
    def clear(self) -> None:
        """Clear the batch without drawing."""
        self.instance_data.clear()
        self.instance_count = 0


class ShapeRenderer:
    """
    High-performance 2D shape renderer using SDF (Signed Distance Functions) and GPU shaders.
    Supports immediate mode, cached drawing, and batched rendering.
    """
    ctx: ContextType
    circle_instanced_prog: ProgramType
    rect_instanced_prog: ProgramType
    line_instanced_prog: ProgramType
    circle_prog: ProgramType
    rect_prog: ProgramType
    line_prog: ProgramType
    circle_vbo: BufferType
    rect_vbo: BufferType
    line_vbo: BufferType
    circle_vao: VAOType
    rect_vao: VAOType
    line_vao: VAOType
    
    def __init__(self, ctx: ContextType) -> None:
        self.ctx = ctx
        
        # ===== INSTANCED Circle Shader (for high-performance batching) =====
        self.circle_instanced_prog = self.ctx.program(
            vertex_shader="""
            #version 430
            uniform vec2 resolution;
            
            in vec2 in_vertex;  // Template quad vertex: (-1,-1) to (1,1)
            in vec2 in_center;  // Per-instance
            in vec4 in_color;   // Per-instance
            in float in_radius; // Per-instance
            in vec4 in_border_color;  // Per-instance
            in float in_border_width; // Per-instance
            in float in_aa;     // Per-instance
            
            out vec4 v_color;
            out vec2 v_local_pos;
            out float v_radius;
            out vec4 v_border_color;
            out float v_border_width;
            out float v_aa;
            
            void main() {
                // Expand vertex by radius + border + aa
                float expand = in_radius + in_border_width + in_aa * 2.0;
                vec2 world_pos = in_center + in_vertex * expand;
                
                vec2 ndc = (world_pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y;
                gl_Position = vec4(ndc, 0.0, 1.0);
                
                v_color = in_color;
                v_local_pos = in_vertex * expand;  // Local position for SDF
                v_radius = in_radius;
                v_border_color = in_border_color;
                v_border_width = in_border_width;
                v_aa = in_aa;
            }
            """,
            fragment_shader="""
            #version 430
            
            in vec4 v_color;
            in vec2 v_local_pos;
            in float v_radius;
            in vec4 v_border_color;
            in float v_border_width;
            in float v_aa;
            
            out vec4 f_color;
            
            void main() {
                float dist = length(v_local_pos) - v_radius;
                
                if (v_border_width > 0.0) {
                    float outer_dist = abs(dist);
                    float inner_dist = abs(dist + v_border_width);
                    float alpha_outer = 1.0 - smoothstep(0.0, v_aa, outer_dist);
                    float alpha_inner = 1.0 - smoothstep(0.0, v_aa, inner_dist);
                    float border_alpha = alpha_outer * (1.0 - alpha_inner);
                    float fill_alpha = 1.0 - smoothstep(-v_aa, v_aa, dist);
                    vec4 fill_color = vec4(v_color.rgb, v_color.a * fill_alpha);
                    vec4 border_col = vec4(v_border_color.rgb, v_border_color.a * border_alpha);
                    f_color = mix(fill_color, border_col, border_alpha / max(border_alpha + fill_alpha, 0.001));
                } else {
                    float alpha = 1.0 - smoothstep(-v_aa, v_aa, dist);
                    f_color = vec4(v_color.rgb, v_color.a * alpha);
                }
            }
            """
        )
        
        # ===== INSTANCED Rectangle Shader =====
        self.rect_instanced_prog = self.ctx.program(
            vertex_shader="""
            #version 430
            uniform vec2 resolution;
            
            in vec2 in_vertex;
            in vec2 in_center;
            in vec2 in_size;
            in vec4 in_color;
            in float in_radius;
            in vec4 in_border_color;
            in float in_border_width;
            in float in_aa;
            in float in_rotation;
            
            out vec4 v_color;
            out vec2 v_local_pos;
            out float v_radius;
            out vec4 v_border_color;
            out float v_border_width;
            out float v_aa;
            out vec2 v_size;
            
            void main() {
                float expand = in_border_width + in_aa * 2.0;
                vec2 expanded_size = in_size + expand;
                
                // Apply rotation
                float cos_a = cos(in_rotation);
                float sin_a = sin(in_rotation);
                vec2 rotated = vec2(
                    in_vertex.x * cos_a - in_vertex.y * sin_a,
                    in_vertex.x * sin_a + in_vertex.y * cos_a
                );
                
                vec2 world_pos = in_center + rotated * expanded_size;
                
                vec2 ndc = (world_pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y;
                gl_Position = vec4(ndc, 0.0, 1.0);
                
                v_color = in_color;
                v_local_pos = rotated * expanded_size;
                v_radius = in_radius;
                v_border_color = in_border_color;
                v_border_width = in_border_width;
                v_aa = in_aa;
                v_size = in_size;
            }
            """,
            fragment_shader="""
            #version 430
            
            in vec4 v_color;
            in vec2 v_local_pos;
            in float v_radius;
            in vec4 v_border_color;
            in float v_border_width;
            in float v_aa;
            in vec2 v_size;
            
            out vec4 f_color;
            
            float roundedBoxSDF(vec2 center, vec2 size, float radius) {
                vec2 q = abs(center) - size + radius;
                return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - radius;
            }
            
            void main() {
                float dist = roundedBoxSDF(v_local_pos, v_size, v_radius);
                
                if (v_border_width > 0.0) {
                    float outer_dist = abs(dist);
                    float inner_dist = abs(dist + v_border_width);
                    float alpha_outer = 1.0 - smoothstep(0.0, v_aa, outer_dist);
                    float alpha_inner = 1.0 - smoothstep(0.0, v_aa, inner_dist);
                    float border_alpha = alpha_outer * (1.0 - alpha_inner);
                    float fill_alpha = 1.0 - smoothstep(-v_aa, v_aa, dist);
                    vec4 fill_color = vec4(v_color.rgb, v_color.a * fill_alpha);
                    vec4 border_col = vec4(v_border_color.rgb, v_border_color.a * border_alpha);
                    f_color = mix(fill_color, border_col, border_alpha / max(border_alpha + fill_alpha, 0.001));
                } else {
                    float alpha = 1.0 - smoothstep(-v_aa, v_aa, dist);
                    f_color = vec4(v_color.rgb, v_color.a * alpha);
                }
            }
            """
        )

        self.line_instanced_prog = self.ctx.program(
            vertex_shader="""
            #version 430

            // Per-vertex attributes (quad corners: 4 vertices per instance)
            in vec2 in_quad_pos;  // (-1,-1), (1,-1), (1,1), (-1,1)

            // Per-instance attributes
            in vec2 in_start;
            in vec2 in_end;
            in float in_width;
            in vec4 in_color;

            out vec4 v_color;

            uniform vec2 resolution;

            void main() {
                // Calculate line direction and perpendicular
                vec2 line_vec = in_end - in_start;
                float line_length = length(line_vec);
                vec2 line_dir = line_vec / line_length;
                vec2 line_perp = vec2(-line_dir.y, line_dir.x);
                
                // Calculate half-width
                float half_width = in_width * 0.5;
                
                // Expand quad along line direction and perpendicular
                vec2 world_pos = in_start + 
                                line_dir * (in_quad_pos.x * line_length * 0.5 + line_length * 0.5) +
                                line_perp * (in_quad_pos.y * half_width);
                
                // Convert to NDC
                vec2 ndc = (world_pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y;
                
                gl_Position = vec4(ndc, 0.0, 1.0);
                v_color = in_color;
            }
            """,
            fragment_shader="""
            #version 430

            in vec4 v_color;
            out vec4 fragColor;

            uniform vec2 resolution;

            void main() {
                fragColor = v_color;
            }
            """
        )

        
        # ===== SDF Circle Shader =====
        self.circle_prog = self.ctx.program(
            vertex_shader="""
            #version 430
            uniform vec2 resolution;
            
            in vec2 in_pos;
            in vec4 in_color;
            in float in_radius;
            in vec4 in_border_color;
            in float in_border_width;
            in float in_aa;
            in vec2 in_center;
            
            out vec4 v_color;
            out vec2 v_local_pos;
            out float v_radius;
            out vec4 v_border_color;
            out float v_border_width;
            out float v_aa;
            
            void main() {
                vec2 ndc = (in_pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y;
                gl_Position = vec4(ndc, 0.0, 1.0);
                v_color = in_color;
                v_local_pos = in_pos - in_center;
                v_radius = in_radius;
                v_border_color = in_border_color;
                v_border_width = in_border_width;
                v_aa = in_aa;
            }
            """,
            fragment_shader="""
            #version 430
            
            in vec4 v_color;
            in vec2 v_local_pos;
            in float v_radius;
            in vec4 v_border_color;
            in float v_border_width;
            in float v_aa;
            
            out vec4 f_color;
            
            void main() {
                float dist = length(v_local_pos) - v_radius;
                
                if (v_border_width > 0.0) {
                    float outer_dist = abs(dist);
                    float inner_dist = abs(dist + v_border_width);
                    float alpha_outer = 1.0 - smoothstep(0.0, v_aa, outer_dist);
                    float alpha_inner = 1.0 - smoothstep(0.0, v_aa, inner_dist);
                    float border_alpha = alpha_outer * (1.0 - alpha_inner);
                    float fill_alpha = 1.0 - smoothstep(-v_aa, v_aa, dist);
                    vec4 fill_color = vec4(v_color.rgb, v_color.a * fill_alpha);
                    vec4 border_col = vec4(v_border_color.rgb, v_border_color.a * border_alpha);
                    f_color = mix(fill_color, border_col, border_alpha / max(border_alpha + fill_alpha, 0.001));
                } else {
                    float alpha = 1.0 - smoothstep(-v_aa, v_aa, dist);
                    f_color = vec4(v_color.rgb, v_color.a * alpha);
                }
            }
            """
        )
        
        # ===== SDF Rectangle Shader =====
        self.rect_prog = self.ctx.program(
            vertex_shader="""
            #version 430
            uniform vec2 resolution;
            
            in vec2 in_pos;
            in vec4 in_color;
            in float in_radius;
            in vec4 in_border_color;
            in float in_border_width;
            in float in_aa;
            in vec2 in_size;
            in vec2 in_local_pos;
            
            out vec4 v_color;
            out vec2 v_local_pos;
            out float v_radius;
            out vec4 v_border_color;
            out float v_border_width;
            out float v_aa;
            out vec2 v_size;
            
            void main() {
                vec2 ndc = (in_pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y;
                gl_Position = vec4(ndc, 0.0, 1.0);
                v_color = in_color;
                v_local_pos = in_local_pos;
                v_radius = in_radius;
                v_border_color = in_border_color;
                v_border_width = in_border_width;
                v_aa = in_aa;
                v_size = in_size;
            }
            """,
            fragment_shader="""
            #version 430
            
            in vec4 v_color;
            in vec2 v_local_pos;
            in float v_radius;
            in vec4 v_border_color;
            in float v_border_width;
            in float v_aa;
            in vec2 v_size;
            
            out vec4 f_color;
            
            float roundedBoxSDF(vec2 center, vec2 size, float radius) {
                vec2 q = abs(center) - size + radius;
                return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - radius;
            }
            
            void main() {
                float dist = roundedBoxSDF(v_local_pos, v_size, v_radius);
                
                if (v_border_width > 0.0) {
                    float outer_dist = abs(dist);
                    float inner_dist = abs(dist + v_border_width);
                    float alpha_outer = 1.0 - smoothstep(0.0, v_aa, outer_dist);
                    float alpha_inner = 1.0 - smoothstep(0.0, v_aa, inner_dist);
                    float border_alpha = alpha_outer * (1.0 - alpha_inner);
                    float fill_alpha = 1.0 - smoothstep(-v_aa, v_aa, dist);
                    vec4 fill_color = vec4(v_color.rgb, v_color.a * fill_alpha);
                    vec4 border_col = vec4(v_border_color.rgb, v_border_color.a * border_alpha);
                    f_color = mix(fill_color, border_col, border_alpha / max(border_alpha + fill_alpha, 0.001));
                } else {
                    float alpha = 1.0 - smoothstep(-v_aa, v_aa, dist);
                    f_color = vec4(v_color.rgb, v_color.a * alpha);
                }
            }
            """
        )
        
        # ===== Line Shader (immediate mode) =====
        self.line_prog = self.ctx.program(
            vertex_shader="""
            #version 430
            uniform vec2 resolution;
            
            in vec2 in_pos;
            in vec4 in_color;
            
            out vec4 v_color;
            
            void main() {
                vec2 ndc = (in_pos / resolution) * 2.0 - 1.0;
                ndc.y = -ndc.y;
                gl_Position = vec4(ndc, 0.0, 1.0);
                v_color = in_color;
            }
            """,
            fragment_shader="""
            #version 430
            
            in vec4 v_color;
            out vec4 f_color;
            
            void main() {
                f_color = v_color;
            }
            """
        )
        
        # Dynamic VBOs for immediate mode
        self.circle_vbo = self.ctx.buffer(reserve=65536)
        self.rect_vbo = self.ctx.buffer(reserve=65536)
        self.line_vbo = self.ctx.buffer(reserve=262144)  # Larger for polylines
        
        # VAOs for immediate mode
        # Circle format: pos(2f), color(4f), radius(1f), border_color(4f), border_width(1f), aa(1f), center(2f) = 15 floats
        self.circle_vao = self.ctx.vertex_array(self.circle_prog, [
            (self.circle_vbo, '2f 4f 1f 4f 1f 1f 2f', 'in_pos', 'in_color', 'in_radius',
             'in_border_color', 'in_border_width', 'in_aa', 'in_center')
        ])
        
        # Rect format: pos(2f), color(4f), radius(1f), border_color(4f), border_width(1f), aa(1f), size(2f), local_pos(2f) = 17 floats
        self.rect_vao = self.ctx.vertex_array(self.rect_prog, [
            (self.rect_vbo, '2f 4f 1f 4f 1f 1f 2f 2f', 'in_pos', 'in_color', 'in_radius',
             'in_border_color', 'in_border_width', 'in_aa', 'in_size', 'in_local_pos')
        ])
        
        self.line_vao = self.ctx.vertex_array(self.line_prog, [
            (self.line_vbo, '2f 4f', 'in_pos', 'in_color')
        ])
    
    # ========== CIRCLE ==========
    
    def _generate_circle_vertices(self, center: VectorType, radius: float, 
                                  color: ColorType = (1.0, 1.0, 1.0, 1.0),
                                  rotation: float = 0.0,
                                  border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                                  border_width: float = 0.0,
                                  antialiasing: float = 1.0) -> list[float]:
        """Generate vertices for a circle (as a quad).
        Format: pos(2f), color(4f), radius(1f), border_color(4f), border_width(1f), aa(1f), center(2f)
        """
        # Handle VectorType input - convert to tuple if needed
        cx, cy = center[0], center[1]
        
        # Expand for border and antialiasing
        expand = radius + border_width + antialiasing * 2
        
        # Quad vertices (2 triangles) in screen space
        quad_positions = [
            (cx - expand, cy - expand),
            (cx + expand, cy - expand),
            (cx - expand, cy + expand),
            (cx + expand, cy - expand),
            (cx - expand, cy + expand),
            (cx + expand, cy + expand)
        ]
        
        vertices = []
        for pos in quad_positions:
            vertices.extend([
                *pos,           # in_pos (screen position)
                *color,         # in_color
                radius,         # in_radius
                *border_color,  # in_border_color
                border_width,   # in_border_width
                antialiasing,   # in_aa
                cx, cy          # in_center (circle center)
            ])
        
        return vertices
    
    def draw_circle(self, center: VectorType, radius: float,
                   color: ColorType = (1.0, 1.0, 1.0, 1.0),
                   rotation: float = 0.0,
                   border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                   border_width: float = 0.0,
                   antialiasing: float = 1.0) -> None:
        """
        Draw a circle immediately.
        
        Args:
            center: (x, y) position in screen coordinates
            radius: Circle radius in pixels
            color: (r, g, b, a) fill color
            rotation: Rotation angle in radians (not used for circles, included for API consistency)
            border_color: (r, g, b, a) border color
            border_width: Border width in pixels (0 = no border)
            antialiasing: Antialiasing smoothness in pixels
        """
        vertices = self._generate_circle_vertices(center, radius, color, rotation, 
                                                  border_color, border_width, antialiasing)
        
        data = np.array(vertices, dtype='f4')
        self.circle_vbo.write(data.tobytes())
        
        self.ctx.enable(moderngl.BLEND)
        set_pattr_value(self.circle_prog, 'resolution', self.ctx.viewport[2:])
        self.circle_vao.render(moderngl.TRIANGLES, vertices=6)
    
    def create_circle(self, center: VectorType, radius: float,
                     color: ColorType = (1.0, 1.0, 1.0, 1.0),
                     rotation: float = 0.0,
                     border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                     border_width: float = 0.0,
                     antialiasing: float = 1.0) -> ShapeLabel:
        """Create a cached circle for repeated drawing."""
        vertices = self._generate_circle_vertices(center, radius, color, rotation,
                                                  border_color, border_width, antialiasing)
        
        data = np.array(vertices, dtype='f4')
        vbo = self.ctx.buffer(data.tobytes())
        
        return ShapeLabel(self.ctx, self.circle_prog, vbo, 6, 'circle')
    
    # ========== RECTANGLE ==========
    
    def _generate_rect_vertices(self, position: VectorType, size: VectorType,
                                color: ColorType = (1.0, 1.0, 1.0, 1.0),
                                rotation: float = 0.0,
                                corner_radius: float = 0.0,
                                border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                                border_width: float = 0.0,
                                antialiasing: float = 1.0) -> list[float]:
        """Generate vertices for a rectangle.
        Format: pos(2f), color(4f), radius(1f), border_color(4f), border_width(1f), aa(1f), size(2f), local_pos(2f)
        """
        # Handle VectorType input - convert to tuple if needed
        x, y = position[0], position[1]
        w, h = size
        
        # Center of rectangle
        cx, cy = x + w / 2, y + h / 2
        
        # Expand for border and antialiasing
        expand = border_width + antialiasing * 2
        
        # Rotation matrix
        cos_a = np.cos(rotation)
        sin_a = np.sin(rotation)
        
        # Half dimensions
        hw, hh = w / 2 + expand, h / 2 + expand
        half_size = (w / 2, h / 2)
        
        # Local corner positions
        local_corners = [
            (-hw, -hh), (hw, -hh), (-hw, hh),
            (hw, -hh), (-hw, hh), (hw, hh)
        ]
        
        vertices = []
        for lx, ly in local_corners:
            # Apply rotation and translate to screen space
            rx = lx * cos_a - ly * sin_a + cx
            ry = lx * sin_a + ly * cos_a + cy
            
            vertices.extend([
                rx, ry,         # in_pos (screen position)
                *color,         # in_color
                corner_radius,  # in_radius
                *border_color,  # in_border_color
                border_width,   # in_border_width
                antialiasing,   # in_aa
                *half_size,     # in_size (half-width, half-height for SDF)
                lx, ly          # in_local_pos (local position relative to center)
            ])
        
        return vertices
    
    def draw_rect(self, position: VectorType, size: VectorType,
                 color: ColorType = (1.0, 1.0, 1.0, 1.0),
                 rotation: float = 0.0,
                 corner_radius: float = 0.0,
                 border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                 border_width: float = 0.0,
                 antialiasing: float = 1.0) -> None:
        """
        Draw a rectangle immediately.
        
        Args:
            position: (x, y) top-left corner in screen coordinates
            size: (width, height) in pixels
            color: (r, g, b, a) fill color
            rotation: Rotation angle in radians around center
            corner_radius: Radius for rounded corners in pixels
            border_color: (r, g, b, a) border color
            border_width: Border width in pixels (0 = no border)
            antialiasing: Antialiasing smoothness in pixels
        """
        vertices = self._generate_rect_vertices(position, size, color, rotation,
                                               corner_radius, border_color, border_width, antialiasing)
        
        data = np.array(vertices, dtype='f4')
        self.rect_vbo.write(data.tobytes())
        
        self.ctx.enable(moderngl.BLEND)
        set_pattr_value(self.rect_prog, 'resolution', self.ctx.viewport[2:])
        self.rect_vao.render(moderngl.TRIANGLES, vertices=6)
    
    def create_rect(self, position: VectorType, size: VectorType,
                   color: ColorType = (1.0, 1.0, 1.0, 1.0),
                   rotation: float = 0.0,
                   corner_radius: float = 0.0,
                   border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                   border_width: float = 0.0,
                   antialiasing: float = 1.0) -> ShapeLabel:
        """Create a cached rectangle for repeated drawing."""
        vertices = self._generate_rect_vertices(position, size, color, rotation,
                                                corner_radius, border_color, border_width, antialiasing)
        
        data = np.array(vertices, dtype='f4')
        vbo = self.ctx.buffer(data.tobytes())
        
        return ShapeLabel(self.ctx, self.rect_prog, vbo, 6, 'rect')
    
    # ========== LINES ==========
    
    def _generate_line_segment_vertices(self, start: VectorType, end: VectorType,
                                        width: float, color: ColorType,
                                        antialias: float = 1.0) -> list[float]:
        """Generate vertices for a line segment as a quad."""
        # Handle VectorType input - convert to tuple if needed
        x1, y1 = start[0], start[1]
        x2, y2 = end[0], end[1]
        
        # Calculate perpendicular direction
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx * dx + dy * dy)
        
        if length < 0.001:
            return []
        
        # Normalized perpendicular
        px = -dy / length
        py = dx / length
        
        # Half width
        hw = width / 2 + antialias
        
        # Quad corners
        vertices = []
        quad = [
            (x1 + px * hw, y1 + py * hw),
            (x2 + px * hw, y2 + py * hw),
            (x1 - px * hw, y1 - py * hw),
            (x2 + px * hw, y2 + py * hw),
            (x1 - px * hw, y1 - py * hw),
            (x2 - px * hw, y2 - py * hw)
        ]
        
        for x, y in quad:
            vertices.extend([x, y, *color])
        
        return vertices
    
    def draw_line(self, start: VectorType, end: VectorType,
                 width: float = 1.0,
                 color: ColorType = (1.0, 1.0, 1.0, 1.0),
                 antialiasing: float = 1.0) -> None:
        """
        Draw a single line segment.
        
        Args:
            start: (x, y) start point in screen coordinates
            end: (x, y) end point in screen coordinates
            width: Line width in pixels
            color: (r, g, b, a) line color
            antialiasing: Antialiasing smoothness in pixels
        """
        vertices = self._generate_line_segment_vertices(start, end, width, color, antialiasing)
        
        if not vertices:
            return
        
        data = np.array(vertices, dtype='f4')
        self.line_vbo.write(data.tobytes())
        
        self.ctx.enable(moderngl.BLEND)
        set_pattr_value(self.line_prog, 'resolution', self.ctx.viewport[2:])
        self.line_vao.render(moderngl.TRIANGLES, vertices=6)
    
    def draw_lines(self, points: np.ndarray | Sequence[VectorType],
                  width: float = 1.0,
                  color: ColorType | np.ndarray = (1.0, 1.0, 1.0, 1.0),
                  antialiasing: float = 1.0,
                  closed: bool = False) -> None:
        """
        Draw a polyline (connected line segments).
        
        Args:
            points: Array of (x, y) points, shape (N, 2) or list of tuples
            width: Line width in pixels
            color: Single (r, g, b, a) color or array of colors per segment
            antialiasing: Antialiasing smoothness in pixels
            closed: If True, connect last point to first point
        """
        if isinstance(points, np.ndarray):
            points_array = points
        else:
            points_array = np.array(points, dtype='f4')
        
        if len(points_array) < 2:
            return
        
        # Handle color
        if isinstance(color, np.ndarray):
            colors = color
        else:
            colors = np.tile(color, (len(points_array) - 1, 1))
        
        vertices = []
        
        # Generate line segments
        for i in range(len(points_array) - 1):
            start = tuple(points_array[i])
            end = tuple(points_array[i + 1])
            seg_color = tuple(colors[i]) if len(colors) > 1 else tuple(colors[0])
            
            seg_verts = self._generate_line_segment_vertices(start, end, width, seg_color, antialiasing)
            vertices.extend(seg_verts)
        
        # Close the loop if requested
        if closed:
            start = tuple(points_array[-1])
            end = tuple(points_array[0])
            seg_color = tuple(colors[-1]) if len(colors) > 1 else tuple(colors[0])
            seg_verts = self._generate_line_segment_vertices(start, end, width, seg_color, antialiasing)
            vertices.extend(seg_verts)
        
        if not vertices:
            return
        
        data = np.array(vertices, dtype='f4')
        self.line_vbo.write(data.tobytes())
        
        self.ctx.enable(moderngl.BLEND)
        set_pattr_value(self.line_prog, 'resolution', self.ctx.viewport[2:])
        num_segments = (len(points_array) - 1) + (1 if closed else 0)
        self.line_vao.render(moderngl.TRIANGLES, vertices=num_segments * 6)
    
    def create_line(self, start: VectorType, end: VectorType,
                   width: float = 1.0,
                   color: ColorType = (1.0, 1.0, 1.0, 1.0),
                   antialiasing: float = 1.0) -> ShapeLabel:
        """Create a cached line for repeated drawing."""
        vertices = self._generate_line_segment_vertices(start, end, width, color, antialiasing)
        
        data = np.array(vertices, dtype='f4')
        vbo = self.ctx.buffer(data.tobytes())
        
        return ShapeLabel(self.ctx, self.line_prog, vbo, 6, 'line')
    
    def create_lines(self, points: np.ndarray | Sequence[VectorType],
                    width: float = 1.0,
                    color: ColorType | np.ndarray = (1.0, 1.0, 1.0, 1.0),
                    antialiasing: float = 1.0,
                    closed: bool = False) -> ShapeLabel:
        """Create a cached polyline for repeated drawing."""
        if isinstance(points, np.ndarray):
            points_array = points
        else:
            points_array = np.array(points, dtype='f4')
        
        if isinstance(color, np.ndarray):
            colors = color
        else:
            colors = np.tile(color, (len(points_array) - 1, 1))
        
        vertices = []
        
        for i in range(len(points_array) - 1):
            start = tuple(points_array[i])
            end = tuple(points_array[i + 1])
            seg_color = tuple(colors[i]) if len(colors) > 1 else tuple(colors[0])
            
            seg_verts = self._generate_line_segment_vertices(start, end, width, seg_color, antialiasing)
            vertices.extend(seg_verts)
        
        if closed:
            start = tuple(points_array[-1])
            end = tuple(points_array[0])
            seg_color = tuple(colors[-1]) if len(colors) > 1 else tuple(colors[0])
            seg_verts = self._generate_line_segment_vertices(start, end, width, seg_color, antialiasing)
            vertices.extend(seg_verts)
        
        data = np.array(vertices, dtype='f4')
        vbo = self.ctx.buffer(data.tobytes())
        
        num_segments = (len(points_array) - 1) + (1 if closed else 0)
        return ShapeLabel(self.ctx, self.line_prog, vbo, num_segments * 6, 'line')
    
    # ========== BATCHING ==========
    
    def create_circle_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple circles efficiently using GPU instancing.
        
        Args:
            max_shapes: Maximum number of shapes in the batch
        """
        return InstancedShapeBatch(self.ctx, self.circle_instanced_prog, 'circle', max_shapes)
    
    def create_rect_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple rectangles efficiently using GPU instancing.
        
        Args:
            max_shapes: Maximum number of shapes in the batch
        """
        return InstancedShapeBatch(self.ctx, self.rect_instanced_prog, 'rect', max_shapes)
    
    def create_line_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple lines efficiently using GPU instancing.
        
        Args:
            max_shapes: Maximum number of lines in the batch
        """
        return InstancedShapeBatch(self.ctx, self.line_instanced_prog, 'line', max_shapes)
