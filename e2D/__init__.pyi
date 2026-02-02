"""
Type stubs for e2D package
High-Performance 2D Graphics and Math Library
"""

import numpy as np
from typing import Optional, Any
from .types import BufferType, ComputeShaderType, ContextType, Number, ProgramAttrType, ProgramType, ProgramType, UniformType, VectorType, pArray
from .text_renderer import DEFAULT_TEXT_STYLE, Pivots, TextRenderer, TextLabel, TextStyle
from .shapes import ShapeRenderer, ShapeLabel, InstancedShapeBatch
from .devices import Keyboard, Mouse

__version__: str
__author__: str
__email__: str

_VECTOR_COMPILED: bool

class DefEnv:
    """Base environment class for user environments"""
    ctx: ContextType
    
    def __init__(self) -> None: ...
    def draw(self) -> None: ...
    def update(self) -> None: ...
    def on_resize(self, width: int, height: int) -> None: ...

class RootEnv:
    """Root environment managing the window, context, and main loop"""
    window: Any  # glfw._GLFWwindow
    window_size: tuple[int, int]
    target_fps: int
    ctx: ContextType
    programs: dict[str, ProgramType]
    compute_shaders: dict[str, ComputeShaderType]
    buffers: dict[str, BufferType]
    keyboard: Keyboard
    mouse: Mouse
    text_renderer: TextRenderer
    shape_renderer: ShapeRenderer
    delta: float
    last_frame_time: float
    start_time: float
    env: DefEnv
    
    def __init__(
        self,
        window_size: tuple[int, int] = (1920, 1080),
        target_fps: int = 60,
        vsync: bool = True,
        version: tuple[int, int] = (4, 3),
        monitor: Optional[int] = None
    ) -> None: ...
    
    @property
    def window_size_f(self) -> tuple[float, float]:
        """Get window size as floats for shader uniforms."""
        ...
    
    @property
    def runtime(self) -> float:
        """Get total elapsed time since program initialization in seconds."""
        ...
    
    def init(self, env: DefEnv) -> "RootEnv": ...
    
    def load_shader_file(self, path: str) -> str:
        """Load shader source code from a file."""
        ...
    
    def create_program(self, vertex_shader: str, fragment_shader: str, id: str) -> ProgramType: ...
    def create_program_from_files(self, vertex_path: str, fragment_path: str, id: str) -> ProgramType: ...
    def get_program(self, id: str) -> Optional[ProgramType]: ...
    
    def create_compute_shader(self, compute_shader: str, id: str) -> ComputeShaderType: ...
    def create_compute_shader_from_file(self, compute_path: str, id: str) -> ComputeShaderType: ...
    def get_compute_shader(self, id: str) -> Optional[ComputeShaderType]: ...
    
    def create_buffer(
        self, 
        data: Any = None, 
        reserve: int = 0, 
        id: Optional[str] = None, 
        dynamic: bool = True
    ) -> BufferType: ...
    
    def get_buffer(self, id: str) -> Optional[BufferType]: ...
    def bind_buffer_to_storage(self, buffer: BufferType | str, binding: int) -> None: ...
    
    def dispatch_compute(
        self,
        compute_id: str | ComputeShaderType,
        groups_x: int = 1,
        groups_y: int = 1,
        groups_z: int = 1,
        buffers: Optional[dict[int, BufferType | str]] = None,
        wait: bool = True
    ) -> None: ...
    
    def read_buffer(self, buffer: BufferType | str, dtype: str = 'f4') -> np.ndarray: ...
    def write_buffer(self, buffer: BufferType | str, data: Any, offset: int = 0) -> None: ...
    
    def get_pattr(
        self, 
        prog_id: str | ProgramType, 
        name: str
    ) -> ProgramAttrType: ...
    
    def get_uniform(
        self, 
        prog_id: str | ProgramType | ComputeShaderType, 
        name: str
    ) -> UniformType: ...
    
    def get_pattr_value(self, prog_id: str | ProgramType, name: str) -> Number | pArray: ...
    def set_pattr_value(self, prog_id: str | ProgramType, name: str, value: Any, *, force_write: bool = False) -> None: ...
    
    def loop(self) -> None:
        """Main rendering loop"""
        ...
    
    def print(
        self,
        text_or_label: str | TextLabel,
        position: VectorType,
        scale: float = 1.0,
        style: TextStyle = DEFAULT_TEXT_STYLE,
        pivot: Pivots|int = Pivots.TOP_LEFT,
        save_cache: bool = False
    ) -> Optional[TextLabel]: ...
    
    # Shape drawing methods
    def draw_circle(self, center: VectorType, radius: float, **kwargs: Any) -> None: ...
    def draw_rect(self, position: VectorType, size: VectorType, **kwargs: Any) -> None: ...
    def draw_line(self, start: VectorType, end: VectorType, **kwargs: Any) -> None: ...
    def draw_lines(self, points: Any, **kwargs: Any) -> None: ...
    
    def create_circle(self, center: VectorType, radius: float, **kwargs: Any) -> ShapeLabel: ...
    def create_rect(self, position: VectorType, size: VectorType, **kwargs: Any) -> ShapeLabel: ...
    def create_line(self, start: VectorType, end: VectorType, **kwargs: Any) -> ShapeLabel: ...
    def create_lines(self, points: Any, **kwargs: Any) -> ShapeLabel: ...
    
    def create_circle_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch: ...
    def create_rect_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch: ...
    def create_line_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch: ...
