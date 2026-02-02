"""
Type stubs for plots module
2D plotting with GPU-accelerated rendering
"""

from typing import Optional, Callable
from enum import Enum
import numpy as np
import numpy.typing as npt
from .types import BufferType, ColorType, ComputeShaderType, ContextType, ProgramType, VAOType, VectorType
from .color_defs import GRAY10, GRAY50, WHITE, RED, CYAN, TRANSPARENT

class ShaderManager:
    """Cache and manage shader files for the plots module."""
    _cache: dict[str, str]
    
    @staticmethod
    def load_shader(path: str) -> str:
        """Load a shader file with caching."""
        ...
    
    @staticmethod
    def create_program(ctx: ContextType, vertex_path: str, fragment_path: str) -> ProgramType:
        """Create a program from shader files."""
        ...
    
    @staticmethod
    def create_compute(ctx: ContextType, compute_path: str) -> ComputeShaderType:
        """Create a compute shader from file."""
        ...

class View2D:
    """
    Manages coordinate space (World <-> Clip) via UBO.
    """
    ctx: ContextType
    binding: int
    center: npt.NDArray[np.float32]
    zoom: float
    aspect: float
    resolution: npt.NDArray[np.float32]
    buffer: BufferType
    
    def __init__(self, ctx: ContextType, binding: int = 0) -> None: ...
    
    def update_win_size(self, width: int, height: int) -> None: ...
    def pan(self, dx: float, dy: float) -> None: ...
    def zoom_step(self, factor: float) -> None: ...
    def zoom_at(self, factor: float, ndc_x: float, ndc_y: float) -> None: ...
    def update_buffer(self) -> None: ...

class PlotSettings:
    bg_color: ColorType
    show_axis: bool
    axis_color: ColorType
    axis_width: float
    show_grid: bool
    grid_color: ColorType
    grid_spacing: float
    
    def __init__(
        self,
        bg_color: ColorType = (0.1, 0.1, 0.1, 1.0),
        show_axis: bool = True,
        axis_color: ColorType = (0.5, 0.5, 0.5, 1.0),
        axis_width: float = 2.0,
        show_grid: bool = True,
        grid_color: ColorType = (0.2, 0.2, 0.2, 1.0),
        grid_spacing: float = 1.0
    ) -> None: ...

class CurveSettings:
    color: ColorType
    width: float
    count: int
    
    def __init__(
        self,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        width: float = 2.0,
        count: int = 1024
    ) -> None:
        self.color = color
        self.width = width
        self.count = count

class ImplicitSettings:
    color: ColorType
    thickness: float
    
    def __init__(
        self,
        color: ColorType = (0.4, 0.6, 1.0, 1.0),
        thickness: float = 2.0
    ) -> None: ... 

class LineType(Enum):
    NONE: int
    DIRECT: int
    BEZIER_QUADRATIC: int
    BEZIER_CUBIC: int
    SMOOTH: int

class StreamSettings:
    point_color: ColorType
    point_radius: float
    show_points: bool
    round_points: bool
    line_type: LineType
    line_color: ColorType
    line_width: float
    curve_segments: int

    def __init__(
        self,
        point_color: ColorType = (1.0, 0.0, 0.0, 1.0),
        point_radius: float = 5.0,
        show_points: bool = True,
        round_points: bool = True,
        line_type: LineType|int = LineType.DIRECT,
        line_color: ColorType = (1.0, 0.0, 0.0, 1.0),
        line_width: float = 2.0,
        curve_segments: int = 10
    ) -> None: ...

class Plot2D:
    """A specific rectangular area on the screen for plotting."""
    ctx: ContextType
    top_left: VectorType
    bottom_right: VectorType
    settings: PlotSettings
    width: int
    height: int
    view: View2D
    viewport: tuple[int, int, int, int]
    grid_prog: ProgramType
    grid_quad: BufferType
    grid_vao: VAOType
    is_dragging: bool
    last_mouse_pos: VectorType
    
    def __init__(
        self, 
        ctx: ContextType,
        top_left: VectorType, 
        bottom_right: VectorType, 
        settings: Optional[PlotSettings] = None
    ) -> None: ...
    
    def set_rect(self, top_left: VectorType, bottom_right: VectorType) -> None: ...
    def update_window_size(self, win_width: int, win_height: int) -> None: ...
    def render(self, draw_callback: Callable[[], None]) -> None: ...
    def contains(self, x: float, y: float) -> bool: ...
    def on_mouse_drag(self, dx: float, dy: float) -> None: ...
    def on_scroll(self, yoffset: float, mouse_x: float, mouse_y: float) -> None: ...

class GpuStream:
    """Ring-buffer on GPU for high-performance point streaming."""
    ctx: ContextType
    capacity: int
    settings: StreamSettings
    head: int
    size: int
    buffer: BufferType
    prog: ProgramType
    vao: VAOType
    smooth_prog: ProgramType
    smooth_vao: VAOType
    
    def __init__(
        self, 
        ctx: ContextType, 
        capacity: int = 100000, 
        settings: Optional[StreamSettings] = None
    ) -> None: ...
    
    def push(self, points: npt.NDArray[np.float32]) -> None: ...
    def draw(self) -> None: ...
    def shift_points(self, offset: VectorType) -> None: ...

class ComputeCurve:
    """Parametric curve p(t) evaluated entirely on GPU."""
    ctx: ContextType
    count: int
    t_range: tuple[float, float]
    settings: CurveSettings
    vbo: BufferType
    compute_prog: ComputeShaderType
    render_prog: ProgramType
    vao: VAOType
    
    def __init__(
        self, 
        ctx: ContextType, 
        func_body: str, 
        t_range: tuple[float, float], 
        count: int = 1024, 
        settings: Optional[CurveSettings] = None
    ) -> None: ...
    
    def update(self) -> None: ...
    def draw(self) -> None: ...

class ImplicitPlot:
    """Rendering of f(x,y)=0 via Fragment Shader and SDF."""
    ctx: ContextType
    settings: ImplicitSettings
    quad: BufferType
    prog: ProgramType
    vao: VAOType
    
    def __init__(
        self, 
        ctx: ContextType, 
        func_body: str, 
        settings: Optional[ImplicitSettings] = None
    ) -> None: ...
    
    def draw(self) -> None: ...

class SegmentDisplay:
    """Simple 7-segment display renderer for numbers."""
    ctx: ContextType
    prog: ProgramType
    vbo: BufferType
    vao: VAOType
    digits: dict[str, list[int]]
    
    def __init__(self, ctx: ContextType) -> None: ...
    
    def draw_number(
        self, 
        text: str, 
        x: float, 
        y: float, 
        size: float = 20.0, 
        color: ColorType = (1.0, 1.0, 1.0, 1.0)
    ) -> None: ...
