"""
e2D - High-Performance 2D Graphics and Math Library
Combines ultra-optimized vector operations with moderngl rendering

Copyright (c) 2025 Riccardo Mariani
MIT License
"""

__version__ = "2.0.2"
__author__ = "Riccardo Mariani"
__email__ = "riccardo.mariani@emptyhead.dev"

import numpy as np
import moderngl
import glfw
import time
import os

# Import type definitions
from .types import (
    ComputeShaderType, ProgramAttrType, UniformType, VectorType, ColorType, Number,
    ContextType, ProgramType, BufferType, WindowType, pArray
)

# Import original e2D modules
from .text_renderer import DEFAULT_TEXT_STYLE, Pivots, TextRenderer, TextLabel, TextStyle
from .shapes import ShapeRenderer, ShapeLabel, InstancedShapeBatch, FillMode
from .devices import Keyboard, Mouse, KeyState
from .commons import get_pattr, get_pattr_value, set_pattr_value, get_uniform

from typing import Optional

# Import color utilities
from .colors import Color, normalize_color, lerp_colors, gradient, batch_colors_to_array
from .color_defs import (
    # Basic colors
    TRANSPARENT, WHITE, BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW,
    # Extended colors (most common)
    ORANGE, PURPLE, PINK, GRAY50,
    # Lookup functions
    COLOR_NAMES, get_color, has_color,
)

# Try to import Cython-optimized color operations (optional batch utilities)
try:
    from . import ccolors  # type: ignore[import-not-found]
    _COLOR_COMPILED = True
except ImportError:
    _COLOR_COMPILED = False

# Import Vector2D - vectors.py handles Cython/Python fallback internally
from .vectors import (
    Vector2D,
    V2,
    CommonVectors,
    batch_add_inplace,
    batch_scale_inplace,
    batch_normalize_inplace,
    vectors_to_array,
    array_to_vectors,
    lerp,
    create_grid,
    create_circle,
    _COMPILED as _VECTOR_COMPILED,
)


class DefEnv:
    ctx: ContextType
    def __init__(self) -> None: ...

    def draw(self) -> None: ...

    def update(self) -> None: ...

    def on_resize(self, width: int, height: int) -> None: ...

class RootEnv:
    window_size: VectorType
    target_fps: int
    window: WindowType
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
        ) -> None:

        if not glfw.init():
            raise RuntimeError("GLFW initialization failed")
            
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, version[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, version[1])
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.RESIZABLE, True)

        self.window_size = window_size
        self.target_fps = target_fps

        self.window = glfw.create_window(window_size[0], window_size[1], "e2D", monitor, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
            
        glfw.make_context_current(self.window)
        
        try:
            self.ctx = moderngl.create_context()
        except Exception as e:
            print(f"Error creating ModernGL context: {e}")
            glfw.terminate()
            raise
        
        # VSync control - must be set AFTER context creation
        if vsync:
            glfw.swap_interval(1)
        else:
            glfw.swap_interval(0)

        print(f"OpenGL Context: {self.ctx.version_code} / {self.ctx.info['GL_RENDERER']}")
        
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Set initial viewport
        fb_size = glfw.get_framebuffer_size(self.window)
        self.ctx.viewport = (0, 0, fb_size[0], fb_size[1])
        
        glfw.set_window_size_callback(self.window, self._on_resize)

        self.programs :dict[str, ProgramType]= {}
        self.compute_shaders = {}
        self.buffers :dict[str, BufferType]= {}
        
        self.keyboard = Keyboard()
        self.mouse = Mouse()
        self.text_renderer = TextRenderer(self.ctx)
        self.shape_renderer = ShapeRenderer(self.ctx)
        
        # Delta time tracking
        self.delta = 0.0
        self.last_frame_time = time.perf_counter()
        
        # Runtime tracking (elapsed time from initialization)
        self.start_time = time.perf_counter()
    
    @property
    def window_size_f(self) -> tuple[float, float]:
        """Get window size as floats for shader uniforms."""
        return (float(self.window_size[0]), float(self.window_size[1]))
    
    @property
    def runtime(self) -> float:
        """Get total elapsed time since program initialization in seconds."""
        return time.perf_counter() - self.start_time
    
    def _on_resize(self, window: WindowType, width: int, height: int) -> None:
        self.window_size = (width, height)
        fb_size = glfw.get_framebuffer_size(window)
        self.ctx.viewport = (0, 0, fb_size[0], fb_size[1])
        if hasattr(self, 'env') and hasattr(self.env, 'on_resize'):
            self.env.on_resize(fb_size[0], fb_size[1])

    def init(self, env: DefEnv) -> "RootEnv":
        self.env = env
        return self
    
    def init_rec(self, fps: int = 30, draw_on_screen: bool = True, path: str = 'output.mp4') -> 'RootEnv':
        """Initialize screen recording.
        
        Args:
            fps: Recording framerate (independent of application FPS)
            draw_on_screen: Show recording stats overlay
            path: Output video file path
        
        Returns:
            Self for method chaining
        
        Controls:
            F9: Pause/Resume recording
            F10: Restart recording (clear buffer)
            F12: Take screenshot
        """
        from .winrec import WinRec
        self.__winrecorder__ = WinRec(self, fps=fps, draw_on_screen=draw_on_screen, path=path)
        return self
    
    def load_shader_file(self, path: str) -> str:
        """Load shader source code from a file.
        
        Args:
            path: Path to shader file (relative to working directory or absolute)
        
        Returns:
            Shader source code as string
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Shader file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def create_program(self, vertex_shader: str, fragment_shader: str, id: str) -> ProgramType:
        new_program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        if id in self.programs:
            print(f"Warning: Program with id '{id}' already exists. Overwriting.")
        self.programs[id] = new_program
        return new_program
    
    def create_program_from_files(self, vertex_path: str, fragment_path: str, id: str) -> ProgramType:
        """Create a shader program from shader files.
        
        Args:
            vertex_path: Path to vertex shader file
            fragment_path: Path to fragment shader file
            id: Identifier for the program
        
        Returns:
            The created program
        """
        vertex_shader = self.load_shader_file(vertex_path)
        fragment_shader = self.load_shader_file(fragment_path)
        return self.create_program(vertex_shader, fragment_shader, id)

    def get_program(self, id:str) -> ProgramType | None:
        return self.programs.get(id, None)
    
    def __draw__(self) -> None:
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.env.draw()
        
        # Screen recording: capture frame before overlay, draw stats after
        if hasattr(self, '__winrecorder__'):
            self.__winrecorder__.update()  # Captures clean frame
            self.__winrecorder__.draw()     # Draws stats overlay (not recorded)
    
    def create_compute_shader(self, compute_shader:str, id:str) -> ComputeShaderType:
        """Create and store a compute shader program."""
        new_compute = self.ctx.compute_shader(compute_shader)
        if id in self.compute_shaders:
            print(f"Warning: Compute shader with id '{id}' already exists. Overwriting.")
        self.compute_shaders[id] = new_compute
        return new_compute
    
    def create_compute_shader_from_file(self, compute_path:str, id:str) -> ComputeShaderType:
        """Create a compute shader from a file.
        
        Args:
            compute_path: Path to compute shader file
            id: Identifier for the compute shader
        
        Returns:
            The created compute shader
        """
        compute_shader = self.load_shader_file(compute_path)
        return self.create_compute_shader(compute_shader, id)
    
    def get_compute_shader(self, id:str) -> ComputeShaderType | None:
        """Retrieve a compute shader by id."""
        return self.compute_shaders.get(id, None)
    
    def create_buffer(self, data=None, reserve:int=0, id:Optional[str]=None, dynamic:bool=True) -> BufferType:
        """Create and optionally store a buffer.
        
        Args:
            data: Initial data (numpy array, bytes, or None)
            reserve: Reserve size in bytes if data is None
            id: Optional identifier to store the buffer
            dynamic: If True, buffer is marked for frequent updates
        """
        if data is not None:
            if isinstance(data, np.ndarray):
                buffer = self.ctx.buffer(data.tobytes(), dynamic=dynamic)
            else:
                buffer = self.ctx.buffer(data, dynamic=dynamic)
        else:
            buffer = self.ctx.buffer(reserve=reserve, dynamic=dynamic)
        
        if id is not None:
            if id in self.buffers:
                print(f"Warning: Buffer with id '{id}' already exists. Overwriting.")
            self.buffers[id] = buffer
        
        return buffer
    
    def get_buffer(self, id:str) -> BufferType | None:
        """Retrieve a buffer by id."""
        return self.buffers.get(id, None)
    
    def bind_buffer_to_storage(self, buffer:BufferType|str, binding:int) -> None:
        """Bind a buffer to a shader storage binding point.
        
        Args:
            buffer: Buffer object or buffer id
            binding: SSBO binding point (0, 1, 2, ...)
        """
        if isinstance(buffer, str):
            loc_buffer = self.get_buffer(buffer)
            if loc_buffer is None:
                raise ValueError(f"Buffer with id '{buffer}' does not exist.")
            buffer = loc_buffer
        
        buffer.bind_to_storage_buffer(binding)
    
    def dispatch_compute(self, 
            compute_id:str|ComputeShaderType, 
            groups_x:int=1, groups_y:int=1, groups_z:int=1,
            buffers:Optional[dict[int, BufferType|str]]=None,
            wait:bool=True
        ) -> None:
        """Dispatch a compute shader with automatic buffer binding.
        
        Args:
            compute_id: Compute shader object or id
            groups_x, groups_y, groups_z: Number of work groups
            buffers: Optional dict mapping binding points to buffers {0: buffer, 1: 'buffer_id', ...}
            wait: If True, wait for compute to complete before returning
        """
        if isinstance(compute_id, str):
            compute = self.get_compute_shader(compute_id)
            if compute is None:
                raise ValueError(f"Compute shader with id '{compute_id}' does not exist.")
        else:
            compute = compute_id
        
        # Bind buffers if provided
        if buffers:
            for binding, buffer in buffers.items():
                self.bind_buffer_to_storage(buffer, binding)
        
        # Run compute shader
        compute.run(groups_x, groups_y, groups_z)
        
        # Memory barrier to ensure compute writes are visible
        if wait:
            self.ctx.memory_barrier()
    
    def read_buffer(self, buffer:BufferType|str, dtype='f4') -> np.ndarray:
        """Read data from a buffer into a numpy array.
        
        Args:
            buffer: Buffer object or buffer id
            dtype: numpy dtype for the output array
        """
        if isinstance(buffer, str):
            loc_buffer = self.get_buffer(buffer)
            if loc_buffer is None:
                raise ValueError(f"Buffer with id '{buffer}' does not exist.")
            buffer = loc_buffer
        
        data = np.frombuffer(buffer.read(), dtype=dtype)
        return data
    
    def write_buffer(self, buffer:BufferType|str, data, offset:int=0) -> None:
        """Write data to a buffer.
        
        Args:
            buffer: Buffer object or buffer id
            data: Data to write (numpy array or bytes)
            offset: Byte offset in the buffer
        """
        if isinstance(buffer, str):
            loc_buffer = self.get_buffer(buffer)
            if loc_buffer is None:
                raise ValueError(f"Buffer with id '{buffer}' does not exist.")
            buffer = loc_buffer
        
        if isinstance(data, np.ndarray):
            data = data.tobytes()
        
        buffer.write(data, offset=offset)
    
    def __update__(self) -> None:
        self.env.update()

    def get_pattr(self, prog_id:str|ProgramType, name:str) -> ProgramAttrType:
        return get_pattr(prog_id, name, programs=self.programs)
    
    def get_uniform(self, prog_id:str|ProgramType|ComputeShaderType, name:str) -> UniformType:
        return get_uniform(prog_id, name, compute_shaders=self.compute_shaders, programs=self.programs)

    def get_pattr_value(self, prog_id:str|ProgramType, name:str) -> Number|pArray:
        return get_pattr_value(prog_id, name, programs=self.programs)
    
    def set_pattr_value(self, prog_id:str|ProgramType, name: str, value, *, force_write: bool= False) -> None:
        return set_pattr_value(prog_id, name, value, force_write=force_write, programs=self.programs)

    def loop(self) -> None:
        # Register callbacks
        glfw.set_scroll_callback(self.window, self.mouse._on_scroll)
        glfw.set_cursor_pos_callback(self.window, self.mouse._on_cursor_pos)
        glfw.set_mouse_button_callback(self.window, self.mouse._on_mouse_button)
        glfw.set_key_callback(self.window, self.keyboard._on_key)

        target_frame_time = 1.0 / self.target_fps if (self.target_fps and self.target_fps > 0) else 0.0
            
        while not glfw.window_should_close(self.window):
            start_time = time.perf_counter()
            
            # Calculate delta time
            self.delta = start_time - self.last_frame_time
            self.last_frame_time = start_time
            
            self.keyboard.update()
            self.mouse.update()
            glfw.poll_events()
            
            if self.keyboard.get_key(glfw.KEY_X, KeyState.JUST_PRESSED):
                glfw.set_window_should_close(self.window, True)
            
            try:
                self.__update__()
                self.__draw__()
                glfw.swap_buffers(self.window)
            except Exception as e:
                print(f"Error in loop: {e}")
                import traceback
                traceback.print_exc()
                break
            
            # FPS Limiting
            if target_frame_time > 0:
                elapsed = time.perf_counter() - start_time
                wait = target_frame_time - elapsed
                if wait > 0:
                    time.sleep(wait)
        
        # Cleanup recording before terminating
        if hasattr(self, '__winrecorder__'):
            self.__winrecorder__.quit()
        
        glfw.terminate()

    def print(
        self,
        text_or_label: str|TextLabel,
        position: VectorType,
        scale: float = 1.0,
        style: TextStyle = DEFAULT_TEXT_STYLE,
        pivot: Pivots|int = Pivots.TOP_LEFT,
        save_cache: bool = False
    ) -> Optional[TextLabel]:

        if isinstance(text_or_label, TextLabel):
            text_or_label.draw()
        else:
            if save_cache:
                return self.text_renderer.create_label(str(text_or_label), position[0], position[1], scale, style, pivot)
            else:
                self.text_renderer.draw_text(str(text_or_label), position, scale, style, pivot)
    
    # ========== Shape Drawing Methods ==========
    
    def draw_circle(self, center: VectorType, radius: float, **kwargs) -> None:
        """Draw a circle. See ShapeRenderer.draw_circle for parameters."""
        self.shape_renderer.draw_circle(center, radius, **kwargs)
    
    def draw_rect(self, position: VectorType, size: VectorType, **kwargs) -> None:
        """Draw a rectangle. See ShapeRenderer.draw_rect for parameters."""
        self.shape_renderer.draw_rect(position, size, **kwargs)
    
    def draw_line(self, start: VectorType, end: VectorType, **kwargs) -> None:
        """Draw a line. See ShapeRenderer.draw_line for parameters."""
        self.shape_renderer.draw_line(start, end, **kwargs)
    
    def draw_lines(self, points, **kwargs) -> None:
        """Draw a polyline. See ShapeRenderer.draw_lines for parameters."""
        self.shape_renderer.draw_lines(points, **kwargs)
    
    def create_circle(self, center: VectorType, radius: float, **kwargs) -> ShapeLabel:
        """Create a cached circle. See ShapeRenderer.create_circle for parameters."""
        return self.shape_renderer.create_circle(center, radius, **kwargs)
    
    def create_rect(self, position: VectorType, size: VectorType, **kwargs) -> ShapeLabel:
        """Create a cached rectangle. See ShapeRenderer.create_rect for parameters."""
        return self.shape_renderer.create_rect(position, size, **kwargs)
    
    def create_line(self, start: VectorType, end: VectorType, **kwargs) -> ShapeLabel:
        """Create a cached line. See ShapeRenderer.create_line for parameters."""
        return self.shape_renderer.create_line(start, end, **kwargs)
    
    def create_lines(self, points, **kwargs) -> ShapeLabel:
        """Create a cached polyline. See ShapeRenderer.create_lines for parameters."""
        return self.shape_renderer.create_lines(points, **kwargs)
    
    def create_circle_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple circles using GPU instancing."""
        return self.shape_renderer.create_circle_batch(max_shapes)
    
    def create_rect_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple rectangles using GPU instancing."""
        return self.shape_renderer.create_rect_batch(max_shapes)
    
    def create_line_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple lines using GPU instancing."""
        return self.shape_renderer.create_line_batch(max_shapes)


# Export all public symbols for easy access
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',
    # Core classes
    'RootEnv',
    'DefEnv',
    # Vector classes and utilities
    'Vector2D',
    'V2',
    'CommonVectors',
    'batch_add_inplace',
    'batch_scale_inplace',
    'batch_normalize_inplace',
    'vectors_to_array',
    'array_to_vectors',
    'lerp',
    'create_grid',
    'create_circle',
    # Type aliases
    'VectorType',
    'ColorType',
    # Color utilities
    'Color',
    'normalize_color',
    'lerp_colors',
    'gradient',
    'batch_colors_to_array',
    # Pre-defined colors
    'TRANSPARENT',
    'WHITE',
    'BLACK',
    'RED',
    'GREEN',
    'BLUE',
    'CYAN',
    'MAGENTA',
    'YELLOW',
    'ORANGE',
    'PURPLE',
    'PINK',
    'GRAY50',
    'COLOR_NAMES',
    'get_color',
    'has_color',
    # Text rendering
    'TextRenderer',
    'TextLabel',
    'TextStyle',
    'Pivots',
    'DEFAULT_TEXT_STYLE',
    # Shape rendering
    'ShapeRenderer',
    'ShapeLabel',
    'InstancedShapeBatch',
    'FillMode',
    # Input devices
    'Keyboard',
    'Mouse',
    'KeyState',
    # ModernGL utilities
    'get_pattr',
    'get_pattr_value',
    'set_pattr_value',
    'get_uniform',
    # Compilation flags
    '_VECTOR_COMPILED',
    '_COLOR_COMPILED',
]