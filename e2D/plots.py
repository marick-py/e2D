from typing import Optional
import numpy as np
import moderngl
import struct
from dataclasses import dataclass
from enum import Enum
import os
from .commons import set_uniform_block_binding
from .types import ColorType, ComputeShaderType, Number, VAOType, ContextType, ProgramType, BufferType, ArrayLike
from .vectors import Vector2D
from .colors import normalize_color
from .color_defs import GRAY10, GRAY50, WHITE, RED, CYAN

class ShaderManager:
    """Cache and manage shader files for the plots module."""
    _cache = {}
    
    @staticmethod
    def load_shader(path: str) -> str:
        """Load a shader file with caching."""
        if path not in ShaderManager._cache:
            # Get the directory where this file is located
            module_dir = os.path.dirname(__file__)
            full_path = os.path.join(module_dir, path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Shader file not found: {full_path}")
            with open(full_path, 'r', encoding='utf-8') as f:
                ShaderManager._cache[path] = f.read()
        return ShaderManager._cache[path]
    
    @staticmethod
    def create_program(ctx: ContextType, vertex_path: str, fragment_path: str) -> ProgramType:
        """Create a program from shader files."""
        vertex_shader = ShaderManager.load_shader(vertex_path)
        fragment_shader = ShaderManager.load_shader(fragment_path)
        return ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    
    @staticmethod
    def create_compute(ctx: ContextType, compute_path: str) -> ComputeShaderType:
        """Create a compute shader from file."""
        compute_shader = ShaderManager.load_shader(compute_path)
        return ctx.compute_shader(compute_shader)

class View2D:
    """
    Manages coordinate space (World <-> Clip) via UBO.
    Binding point: 0
    Layout std140:
        vec2 resolution;  // 0
        vec2 center;      // 8
        vec2 scale;       // 16 (zoom_x, zoom_y)
        float aspect;     // 24
        float _pad;       // 28
    """
    ctx: ContextType
    binding: int
    center: ArrayLike
    zoom: float
    aspect: float
    resolution: ArrayLike
    buffer: BufferType
    
    def __init__(self, ctx: ContextType, binding: int = 0) -> None:
        self.ctx = ctx
        self.binding = binding
        self.center = np.array([0.0, 0.0], dtype='f4')
        self.zoom = 1.0
        self.aspect = 1.0
        self.resolution = np.array([1920.0, 1080.0], dtype='f4')
        
        self.buffer = self.ctx.buffer(reserve=32)
        self.buffer.bind_to_uniform_block(self.binding)
        self.update_buffer()

    def update_win_size(self, width: float, height: float) -> None:
        self.resolution = np.array([width, height], dtype='f4')
        self.aspect = width / height if height > 0 else 1.0
        self.update_buffer()

    def pan(self, dx: float, dy: float) -> None:
        world_scale = 1.0 / self.zoom
        self.center[0] -= dx * world_scale * self.aspect
        self.center[1] -= dy * world_scale
        self.update_buffer()

    def zoom_step(self, factor: float) -> None:
        self.zoom *= factor
        self.update_buffer()

    def zoom_at(self, factor: float, ndc_x: float, ndc_y: float) -> None:
        """Zooms by factor, keeping the point at (ndc_x, ndc_y) stationary."""
        prev_zoom = self.zoom
        self.zoom *= factor
        
        diff_scale = (1.0/prev_zoom - 1.0/self.zoom)
        self.center[0] += ndc_x * self.aspect * diff_scale
        self.center[1] += ndc_y * diff_scale
        
        self.update_buffer()

    def update_buffer(self) -> None:
        data = struct.pack(
            '2f2f2f1f1f',
            self.resolution[0], self.resolution[1],
            self.center[0], self.center[1],
            self.zoom, self.zoom,
            self.aspect,
            0.0
        )
        self.buffer.write(data)

@dataclass
class PlotSettings:
    bg_color: ColorType = GRAY10
    show_axis: bool = True
    axis_color: ColorType = GRAY50
    axis_width: float = 2.0
    show_grid: bool = True
    grid_color: ColorType = (0.2, 0.2, 0.2, 1.0)
    grid_spacing: float = 1.0

@dataclass
class CurveSettings:
    color: ColorType = WHITE
    width: float = 2.0
    count: int = 1024

@dataclass
class ImplicitSettings:
    color: ColorType = CYAN
    thickness: float = 2.0

class LineType(Enum):
    NONE = 0
    DIRECT = 1
    BEZIER_QUADRATIC = 2 
    BEZIER_CUBIC = 3
    SMOOTH = 4  # Catmull-Rom

@dataclass
class StreamSettings:
    point_color: ColorType = RED
    point_radius: float = 5.0
    show_points: bool = True
    round_points: bool = True
    line_type: LineType = LineType.DIRECT
    line_color: ColorType = RED
    line_width: float = 2.0
    curve_segments: int = 10

class Plot2D:
    """A specific rectangular area on the screen for plotting."""
    ctx: ContextType
    top_left: tuple[float, float] | Vector2D
    bottom_right: tuple[float, float] | Vector2D
    settings: PlotSettings
    width: Number
    height: Number
    view: View2D
    viewport: tuple[int, int, int, int]
    grid_prog: ProgramType
    grid_quad: BufferType
    grid_vao: VAOType
    is_dragging: bool
    last_mouse_pos: tuple[float, float]
    
    def __init__(self, ctx: ContextType, top_left: tuple[float, float] | Vector2D, bottom_right: tuple[float, float] | Vector2D, settings: Optional[PlotSettings] = None) -> None:
        self.ctx = ctx
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.settings = settings if settings else PlotSettings()
        
        self.width = bottom_right[0] - top_left[0]
        self.height = bottom_right[1] - top_left[1]
        
        self.view = View2D(ctx)
        self.view.update_win_size(self.width, self.height)
        
        self.viewport = (int(top_left[0]), 1080 - int(bottom_right[1]), int(self.width), int(self.height))
        self._init_grid_renderer()
        
        self.is_dragging = False
        self.last_mouse_pos = (0, 0)

    def _init_grid_renderer(self) -> None:
        self.grid_prog = ShaderManager.create_program(
            self.ctx,
            "shaders/plot_grid_vertex.glsl",
            "shaders/plot_grid_fragment.glsl"
        )
        try:
            set_uniform_block_binding(self.grid_prog, 'View', 0)
        except:
            pass
        self.grid_quad = self.ctx.buffer(np.array([-1,-1, 1,-1, -1,1, 1,1], dtype='f4'))
        self.grid_vao = self.ctx.simple_vertex_array(self.grid_prog, self.grid_quad, "in_vert")

    def set_rect(self, top_left: tuple[float, float] | Vector2D, bottom_right: tuple[float, float] | Vector2D) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.width = bottom_right[0] - top_left[0]
        self.height = bottom_right[1] - top_left[1]
        self.view.update_win_size(self.width, self.height)

    def update_window_size(self, win_width: int, win_height: int) -> None:
        x = self.top_left[0]
        w = self.width
        h = self.height
        y = win_height - self.bottom_right[1]
        self.viewport = (int(x), int(y), int(w), int(h))
        
    def render(self, draw_callback) -> None:
        self.ctx.viewport = self.viewport
        self.ctx.scissor = self.viewport
        self.ctx.clear(*normalize_color(self.settings.bg_color).to_array())
        
        self.view.buffer.bind_to_uniform_block(0)
        
        if self.settings.show_grid or self.settings.show_axis:
            self.grid_prog['grid_color'] = self.settings.grid_color
            self.grid_prog['axis_color'] = self.settings.axis_color
            self.grid_prog['spacing'] = self.settings.grid_spacing
            self.grid_prog['show_grid'] = self.settings.show_grid
            self.grid_prog['show_axis'] = self.settings.show_axis
            self.grid_vao.render(moderngl.TRIANGLE_STRIP)
        
        draw_callback()
        self.ctx.scissor = None

    def contains(self, x, y) -> bool:
        return (self.top_left[0] <= x <= self.bottom_right[0] and 
                self.top_left[1] <= y <= self.bottom_right[1])

    def on_mouse_drag(self, dx, dy) -> None:
        ndc_dx = (dx / self.width) * 2.0
        ndc_dy = (dy / self.height) * 2.0
        self.view.pan(ndc_dx, -ndc_dy)

    def on_scroll(self, yoffset, mouse_x, mouse_y) -> None:
        factor = 1.1 if yoffset > 0 else 0.9
        rel_x = mouse_x - self.top_left[0]
        rel_y = mouse_y - self.top_left[1]
        ndc_x = (rel_x / self.width) * 2.0 - 1.0
        ndc_y = 1.0 - (rel_y / self.height) * 2.0
        self.view.zoom_at(factor, ndc_x, ndc_y)

class GpuStream:
    """Ring-buffer on GPU for high-performance point streaming."""
    def __init__(self, ctx: ContextType, capacity: int = 100000, settings: Optional[StreamSettings] = None) -> None:
        self.ctx = ctx
        self.capacity = capacity
        self.settings = settings if settings else StreamSettings()
        self.head = 0
        self.size = 0
        
        # Initialize buffer with zeros to prevent garbage data
        self.buffer = self.ctx.buffer(data=np.zeros(capacity * 2, dtype='f4').tobytes())
        self.buffer.bind_to_storage_buffer(binding=1)
        
        self.prog = ShaderManager.create_program(
            ctx,
            "shaders/stream_vertex.glsl",
            "shaders/stream_fragment.glsl"
        )
        try:
            set_uniform_block_binding(self.prog, 'View', 0)
        except:
            pass
        self.vao = ctx.vertex_array(self.prog, [])

        # Smooth line shader (Catmull-Rom)
        self.smooth_prog = ctx.program(
            vertex_shader="""
            #version 430
            layout(std140, binding=0) uniform View {
                vec2 resolution;
                vec2 center;
                vec2 scale;
                float aspect;
            } view;
            
            layout(std430, binding=1) buffer PointBuffer {
                vec2 points[];
            };
            
            uniform int start_index;
            uniform int capacity;
            uniform int size;
            uniform int segments;
            uniform int type;
            
            vec2 get_point(int i) {
                int idx = clamp(i, 0, size - 1);
                int real_idx = (start_index + idx) % capacity;
                return points[real_idx];
            }
            
            void main() {
                int segment_id = gl_VertexID / segments;
                float t = float(gl_VertexID % segments) / float(segments);
                
                if (segment_id >= size - 1) {
                    gl_Position = vec4(2.0, 2.0, 0.0, 1.0);
                    return;
                }
                
                vec2 p0 = get_point(max(segment_id - 1, 0));
                vec2 p1 = get_point(segment_id);
                vec2 p2 = get_point(segment_id + 1);
                vec2 p3 = get_point(min(segment_id + 2, size - 1));
                
                vec2 pos;
                if (type == 4) {
                    float t2 = t * t;
                    float t3 = t2 * t;
                    pos = 0.5 * ((2.0 * p1) +
                                 (-p0 + p2) * t +
                                 (2.0*p0 - 5.0*p1 + 4.0*p2 - p3) * t2 +
                                 (-p0 + 3.0*p1 - 3.0*p2 + p3) * t3);
                } else {
                    pos = mix(p1, p2, t);
                }
                
                vec2 diff = pos - view.center;
                vec2 norm = diff * view.scale;
                norm.x /= view.aspect;
                gl_Position = vec4(norm, 0.0, 1.0);
            }
            """,
            fragment_shader="""
            #version 430
            uniform vec4 color;
            out vec4 f_color;
            void main() {
                f_color = color;
            }
            """
        )
        try:
            set_uniform_block_binding(self.smooth_prog, 'View', 0)
        except:
            pass
        self.smooth_vao = ctx.vertex_array(self.smooth_prog, [])

    def push(self, points: np.ndarray) -> None:
        if points.shape[0] == 0:
            return
            
        count = points.shape[0]
        if count > self.capacity:
            points = points[-self.capacity:]
            count = self.capacity
        
        offset = self.head * 8
        data = points.tobytes()
        
        if self.head + count <= self.capacity:
            self.buffer.write(data, offset=offset)
        else:
            first_part = self.capacity - self.head
            self.buffer.write(data[:first_part*8], offset=offset)
            self.buffer.write(data[first_part*8:], offset=0)
        
        self.head = (self.head + count) % self.capacity
        self.size = min(self.size + count, self.capacity)

    def draw(self) -> None:
        if self.size == 0:
            return
            
        start_index = (self.head - self.size + self.capacity) % self.capacity
        
        # Draw lines
        if self.settings.line_type != LineType.NONE and self.size >= 2:
            if self.settings.line_type == LineType.SMOOTH and self.size >= 2:
                self.smooth_prog['start_index'] = start_index
                self.smooth_prog['capacity'] = self.capacity
                self.smooth_prog['size'] = self.size
                self.smooth_prog['segments'] = self.settings.curve_segments
                self.smooth_prog['type'] = 4
                self.smooth_prog['color'] = self.settings.line_color
                self.ctx.line_width = self.settings.line_width
                
                num_vertices = (self.size - 1) * self.settings.curve_segments + 1
                self.smooth_vao.render(moderngl.LINE_STRIP, vertices=num_vertices)
            else:
                self.prog['start_index'] = start_index
                self.prog['capacity'] = self.capacity
                self.prog['color'] = self.settings.line_color
                self.ctx.line_width = self.settings.line_width
                self.vao.render(moderngl.LINE_STRIP, vertices=self.size)
            
        # Draw points
        if self.settings.show_points:
            self.prog['start_index'] = start_index
            self.prog['capacity'] = self.capacity
            self.prog['color'] = self.settings.point_color
            self.prog['point_size'] = self.settings.point_radius
            if 'round_points' in self.prog:
                self.prog['round_points'] = self.settings.round_points
            self.vao.render(moderngl.POINTS, vertices=self.size)

    def shift_points(self, offset: tuple[float, float] | Vector2D) -> None:
        """Shifts all existing points by the given offset using a Compute Shader."""
        if not hasattr(self, 'shift_prog'):
            self.shift_prog = ShaderManager.create_compute(
                self.ctx,
                "shaders/stream_shift_compute.glsl"
            )
        
        self.buffer.bind_to_storage_buffer(binding=1)
        self.shift_prog['offset'] = offset
        self.shift_prog['capacity'] = self.capacity
        
        group_size = 64
        num_groups = (self.capacity + group_size - 1) // group_size
        self.shift_prog.run(num_groups)

class ComputeCurve:
    """Parametric curve p(t) evaluated entirely on GPU."""
    def __init__(self, ctx: ContextType, func_body: str, t_range: tuple, count: int = 1024, settings: Optional[CurveSettings] = None):
        self.ctx = ctx
        self.count = count
        self.t_range = t_range
        self.settings = settings if settings else CurveSettings()
        
        self.vbo = self.ctx.buffer(reserve=count * 8)
        
        cs_src = f"""
        #version 430
        layout(local_size_x=64) in;
        
        layout(std430, binding=2) buffer Dest {{
            vec2 vertices[];
        }};
        
        uniform float t0;
        uniform float t1;
        uniform int count;
        
        void main() {{
            uint id = gl_GlobalInvocationID.x;
            if (id >= count) return;
            
            float t_norm = float(id) / float(count - 1);
            float t = t0 + t_norm * (t1 - t0);
            
            float x, y;
            {func_body}
            vertices[id] = vec2(x, y);
        }}
        """
        self.compute_prog = ctx.compute_shader(cs_src)
        
        self.render_prog = ShaderManager.create_program(
            ctx,
            "shaders/curve_vertex.glsl",
            "shaders/curve_fragment.glsl"
        )
        try:
            set_uniform_block_binding(self.render_prog, 'View', 0)
        except:
            pass
        self.vao = ctx.simple_vertex_array(self.render_prog, self.vbo, "in_pos")

    def update(self):
        self.vbo.bind_to_storage_buffer(binding=2)
        self.compute_prog['t0'] = self.t_range[0]
        self.compute_prog['t1'] = self.t_range[1]
        self.compute_prog['count'] = self.count
        
        group_size = 64
        num_groups = (self.count + group_size - 1) // group_size
        self.compute_prog.run(num_groups)

    def draw(self):
        self.render_prog['color'] = self.settings.color
        self.ctx.line_width = self.settings.width
        self.vao.render(moderngl.LINE_STRIP)

class ImplicitPlot:
    """Rendering of f(x,y)=0 via Fragment Shader and SDF."""
    def __init__(self, ctx: ContextType, func_body: str, settings: Optional[ImplicitSettings] = None):
        self.ctx = ctx
        self.settings = settings if settings else ImplicitSettings()
        
        self.quad = self.ctx.buffer(np.array([-1,-1, 1,-1, -1,1, 1,1], dtype='f4'))
        
        fs_src = f"""
        #version 430
        layout(std140, binding=0) uniform View {{
            vec2 resolution;
            vec2 center;
            vec2 scale;
            float aspect;
        }} view;
        
        uniform vec4 color;
        uniform float thickness;
        
        in vec2 uv;
        out vec4 f_color;
        
        void main() {{
            vec2 ndc = uv * 2.0 - 1.0;
            ndc.x *= view.aspect;
            vec2 p = (ndc / view.scale) + view.center;
            
            float x = p.x;
            float y = p.y;
            float val;
            
            {func_body}
            
            float dist = abs(val) / length(vec2(dFdx(val), dFdy(val)));
            float alpha = 1.0 - smoothstep(thickness - 1.0, thickness, dist);
            
            if (alpha <= 0.0) discard;
            f_color = vec4(color.rgb, color.a * alpha);
        }}
        """
        
        vs_src = """
        #version 430
        in vec2 in_vert;
        out vec2 uv;
        void main() {
            uv = in_vert * 0.5 + 0.5;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        """
        
        self.prog = ctx.program(vertex_shader=vs_src, fragment_shader=fs_src)
        try:
            set_uniform_block_binding(self.prog, 'View', 0)
        except:
            pass
        self.vao = ctx.simple_vertex_array(self.prog, self.quad, "in_vert")

    def draw(self):
        self.prog['color'] = self.settings.color
        self.prog['thickness'] = self.settings.thickness
        self.vao.render(moderngl.TRIANGLE_STRIP)

class SegmentDisplay:
    """Simple 7-segment display renderer for numbers."""
    def __init__(self, ctx: ContextType):
        self.ctx = ctx
        self.prog = ShaderManager.create_program(
            ctx,
            "shaders/segment_vertex.glsl",
            "shaders/segment_fragment.glsl"
        )
        self.vbo = ctx.buffer(reserve=4096)
        self.vao = ctx.simple_vertex_array(self.prog, self.vbo, 'in_pos')
        
        # 7-segment definitions (0-9)
        self.digits = {
            '0': [0, 1, 2, 4, 5, 6],
            '1': [2, 5],
            '2': [0, 2, 3, 4, 6],
            '3': [0, 2, 3, 5, 6],
            '4': [1, 2, 3, 5],
            '5': [0, 1, 3, 5, 6],
            '6': [0, 1, 3, 4, 5, 6],
            '7': [0, 2, 5],
            '8': [0, 1, 2, 3, 4, 5, 6],
            '9': [0, 1, 2, 3, 5, 6],
            '.': [7]
        }

    def draw_number(self, text: str, x: float, y: float, size: float = 20.0, color: ColorType = WHITE):
        vertices = []
        cursor_x = x
        w = size * 0.5
        h = size
        
        for char in str(text):
            if char not in self.digits:
                cursor_x += size * 0.5
                continue
                
            segs = self.digits[char]
            lines = []
            if 0 in segs: lines.extend([(0,0), (w,0)])
            if 1 in segs: lines.extend([(0,0), (0,h/2)])
            if 2 in segs: lines.extend([(w,0), (w,h/2)])
            if 3 in segs: lines.extend([(0,h/2), (w,h/2)])
            if 4 in segs: lines.extend([(0,h/2), (0,h)])
            if 5 in segs: lines.extend([(w,h/2), (w,h)])
            if 6 in segs: lines.extend([(0,h), (w,h)])
            if 7 in segs: lines.extend([(w/2, h-size*0.1), (w/2, h)])
            
            for lx, ly in lines:
                vertices.append(cursor_x + lx)
                vertices.append(y + ly)
            
            cursor_x += size * 0.8
            
        if not vertices:
            return

        data = np.array(vertices, dtype='f4')
        self.vbo.write(data.tobytes())
        
        fb_size = self.ctx.viewport[2:]
        self.prog['resolution'] = fb_size
        self.prog['color'] = color
        
        self.vao.render(moderngl.LINES, vertices=len(vertices)//2)
