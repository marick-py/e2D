"""
e2D - High-Performance 2D Graphics and Math Library
Combines ultra-optimized vector operations with moderngl rendering

Copyright (c) 2025 Riccardo Mariani
MIT License
"""

__version__ = "2.1.1"
__author__ = "Riccardo Mariani"
__email__ = "riccardo.mariani@emptyhead.dev"

import numpy as np
import moderngl
import glfw
import time
import os

# Import type definitions
from .types import (
    ComputeShaderType, ProgramAttrType, UniformType, ColorType, Number,
    ContextType, ProgramType, BufferType, WindowType, pArray
)

# Import original e2D modules
from .text_renderer import DEFAULT_16_TEXT_STYLE, MONO_16_TEXT_STYLE, Pivots, TextRenderer, TextLabel, TextStyle
from .shapes import ShapeRenderer, ShapeLabel, InstancedShapeBatch, FillMode
from .devices import Keyboard, Mouse, KeyState, Keys, MouseButtons
from .commons import get_pattr, get_pattr_value, set_pattr_value, get_uniform, PI, PI_HALF, PI_QUARTER, TAU

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
    from . import ccolors # type: ignore
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
)


class DefEnv:
    ctx: ContextType
    def __init__(self) -> None: ...

    def draw(self) -> None: ...

    def update(self) -> None: ...

    def on_resize(self, width: int, height: int) -> None: ...


class WindowConfig:
    """Complete window and monitor configuration settings.
    
    This class encapsulates all GLFW window creation and display settings.
    Use this to configure your window before passing it to RootEnv.
    
    Example:
        config = WindowConfig(
            size=(1920, 1080),
            title="My Game",
            fullscreen=False,
            vsync=True
        )
        env = RootEnv(config=config)
    """
    
    # Window properties
    size: Vector2D
    title: str
    resizable: bool
    visible: bool
    decorated: bool
    focused: bool
    auto_iconify: bool
    floating: bool
    maximized: bool
    center_on_screen: bool
    
    # Display properties
    fullscreen: bool
    monitor_index: int
    monitor: Optional[glfw._GLFWmonitor]
    
    # Rendering properties
    vsync: bool
    target_fps: int
    draw_fps: bool
    
    # OpenGL properties
    opengl_version: tuple[int, int]
    opengl_profile: int
    opengl_forward_compat: bool
    
    # MSAA (Multi-Sample Anti-Aliasing)
    samples: int
    
    # Framebuffer properties
    red_bits: int
    green_bits: int
    blue_bits: int
    alpha_bits: int
    depth_bits: int
    stencil_bits: int
    
    def __init__(
        self,
        # Window size and title
        size: Vector2D | tuple[int | float, int | float] = (1920, 1080),
        title: str = "e2D",
        
        # Window behavior
        resizable: bool = True,
        visible: bool = True,
        decorated: bool = True,
        focused: bool = True,
        auto_iconify: bool = True,
        floating: bool = False,
        maximized: bool = False,
        center_on_screen: bool = True,
        
        # Display settings
        fullscreen: bool = False,
        monitor_index: int = 0,
        
        # Rendering settings
        vsync: bool = False,
        target_fps: int = 60,
        draw_fps: bool = False,
        
        # OpenGL settings
        opengl_version: tuple[int, int] = (4, 3),
        opengl_profile: int = glfw.OPENGL_CORE_PROFILE,
        opengl_forward_compat: bool = True,
        
        # Anti-aliasing
        samples: int = 0,  # 0 = disabled, 4 or 8 = enabled
        
        # Framebuffer bit depths (usually leave as default)
        red_bits: int = 8,
        green_bits: int = 8,
        blue_bits: int = 8,
        alpha_bits: int = 8,
        depth_bits: int = 24,
        stencil_bits: int = 8,
    ):
        """Initialize window configuration with all GLFW settings.
        
        Args:
            size: Window size as (width, height) or Vector2D
            title: Window title text
            resizable: Allow window resizing
            visible: Show window immediately
            decorated: Show window decorations (title bar, borders)
            focused: Focus window on creation
            auto_iconify: Auto-minimize fullscreen windows on focus loss
            floating: Keep window above others (always on top)
            maximized: Start window maximized
            center_on_screen: Center window on monitor (if not fullscreen)
            fullscreen: Run in fullscreen mode
            monitor_index: Which monitor to use (0 = primary)
            vsync: Enable vertical sync
            target_fps: Target frame rate (0 = unlimited)
            draw_fps: Display FPS counter
            opengl_version: OpenGL version as (major, minor)
            opengl_profile: GLFW OpenGL profile constant
            opengl_forward_compat: Use forward-compatible OpenGL context
            samples: MSAA samples (0, 4, or 8)
            red_bits, green_bits, blue_bits, alpha_bits: Color channel bit depths
            depth_bits: Depth buffer bit depth
            stencil_bits: Stencil buffer bit depth
        """
        # Convert size to Vector2D if needed
        if isinstance(size, tuple):
            self.size = V2(float(size[0]), float(size[1]))
        else:
            self.size = size
        
        self.title = title
        self.resizable = resizable
        self.visible = visible
        self.decorated = decorated
        self.focused = focused
        self.auto_iconify = auto_iconify
        self.floating = floating
        self.maximized = maximized
        self.center_on_screen = center_on_screen
        
        self.fullscreen = fullscreen
        self.monitor_index = monitor_index
        self.monitor = None  # Will be resolved during window creation
        
        self.vsync = vsync
        self.target_fps = target_fps
        self.draw_fps = draw_fps
        
        self.opengl_version = opengl_version
        self.opengl_profile = opengl_profile
        self.opengl_forward_compat = opengl_forward_compat
        
        self.samples = samples
        
        self.red_bits = red_bits
        self.green_bits = green_bits
        self.blue_bits = blue_bits
        self.alpha_bits = alpha_bits
        self.depth_bits = depth_bits
        self.stencil_bits = stencil_bits
    
    def get_monitor(self) -> Optional[glfw._GLFWmonitor]:
        """Get the monitor object for this configuration.
        
        Returns:
            Monitor object if fullscreen, None otherwise
        """
        if not self.fullscreen:
            return None
        
        monitors = glfw.get_monitors()
        if self.monitor_index < len(monitors):
            return monitors[self.monitor_index]
        else:
            print(f"Warning: Monitor index {self.monitor_index} out of range, using primary monitor")
            return glfw.get_primary_monitor()
    
    def apply_hints(self) -> None:
        """Apply all window hints to GLFW before window creation."""
        # OpenGL version and profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, self.opengl_version[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, self.opengl_version[1])
        glfw.window_hint(glfw.OPENGL_PROFILE, self.opengl_profile)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, self.opengl_forward_compat)
        
        # Window properties
        glfw.window_hint(glfw.RESIZABLE, self.resizable)
        glfw.window_hint(glfw.VISIBLE, self.visible)
        glfw.window_hint(glfw.DECORATED, self.decorated)
        glfw.window_hint(glfw.FOCUSED, self.focused)
        glfw.window_hint(glfw.AUTO_ICONIFY, self.auto_iconify)
        glfw.window_hint(glfw.FLOATING, self.floating)
        glfw.window_hint(glfw.MAXIMIZED, self.maximized)
        
        # Framebuffer properties
        glfw.window_hint(glfw.RED_BITS, self.red_bits)
        glfw.window_hint(glfw.GREEN_BITS, self.green_bits)
        glfw.window_hint(glfw.BLUE_BITS, self.blue_bits)
        glfw.window_hint(glfw.ALPHA_BITS, self.alpha_bits)
        glfw.window_hint(glfw.DEPTH_BITS, self.depth_bits)
        glfw.window_hint(glfw.STENCIL_BITS, self.stencil_bits)
        
        # MSAA
        if self.samples > 0:
            glfw.window_hint(glfw.SAMPLES, self.samples)


class RootEnv:
    window_size: Vector2D
    target_fps: int
    draw_fps: bool
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
    config: WindowConfig
    
    def __init__(self, config: Optional[WindowConfig] = None) -> None:
        """Initialize the rendering environment.
        
        Usage:
            # With custom config
            config = WindowConfig(
                size=(1920, 1080),
                title="My App",
                fullscreen=False,
                vsync=True,
                target_fps=60
            )
            env = RootEnv(config=config)
            
            # With default settings
            env = RootEnv()
        
        Args:
            config: WindowConfig object with all window settings.
                   If None, uses default WindowConfig settings.
        """
        if not glfw.init():
            raise RuntimeError("GLFW initialization failed")
        
        # Create default config if none provided
        if config is None:
            config = WindowConfig()
        
        self.config = config
        
        # Apply all GLFW window hints
        config.apply_hints()
        
        # Store commonly accessed values
        self.window_size = config.size
        self.target_fps = config.target_fps
        self.draw_fps = config.draw_fps
        self._resizable = config.resizable
        self._fullscreen = config.fullscreen
        self._vsync = config.vsync
        
        # Resolve monitor for fullscreen
        monitor_for_window = config.get_monitor()
        
        # Create window - pass monitor ONLY if fullscreen
        self.window = glfw.create_window(
            int(config.size[0]),
            int(config.size[1]),
            config.title,
            monitor_for_window,  # None for windowed, monitor object for fullscreen
            None
        )
        
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        
        # Center window on specified monitor if windowed and center_on_screen is True
        if not config.fullscreen and config.center_on_screen:
            # Get the target monitor (respects monitor_index for windowed mode)
            monitors = glfw.get_monitors()
            target_monitor = monitors[config.monitor_index] if config.monitor_index < len(monitors) else glfw.get_primary_monitor()
            
            video_mode = glfw.get_video_mode(target_monitor)
            monitor_x, monitor_y = glfw.get_monitor_pos(target_monitor)
            
            window_w, window_h = int(config.size[0]), int(config.size[1])
            screen_w, screen_h = video_mode.size.width, video_mode.size.height
            
            # Calculate centered position on the target monitor
            x = monitor_x + (screen_w - window_w) // 2
            y = monitor_y + (screen_h - window_h) // 2
            
            glfw.set_window_pos(self.window, x, y)
            
        glfw.make_context_current(self.window)
        
        try:
            self.ctx = moderngl.create_context()
        except Exception as e:
            print(f"Error creating ModernGL context: {e}")
            glfw.terminate()
            raise
        
        # VSync control - must be set AFTER context creation
        glfw.swap_interval(1 if config.vsync else 0)

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
    def window_position(self) -> Vector2D:
        """Get current window position."""
        pos = glfw.get_window_pos(self.window)
        return V2(float(pos[0]), float(pos[1]))
    
    @property
    def resizable(self) -> bool:
        """Get window resizable state."""
        return self._resizable
    
    @resizable.setter
    def resizable(self, value: bool) -> None:
        """Set window resizable state."""
        self._resizable = value
        glfw.set_window_attrib(self.window, glfw.RESIZABLE, glfw.TRUE if value else glfw.FALSE)
    
    @property
    def vsync(self) -> bool:
        """Get VSync state."""
        return self._vsync
    
    @vsync.setter
    def vsync(self, value: bool) -> None:
        """Set VSync state. Changes take effect immediately."""
        self._vsync = value
        glfw.swap_interval(1 if value else 0)
    
    @property
    def runtime(self) -> float:
        """Get total elapsed time since program initialization in seconds."""
        return time.perf_counter() - self.start_time
    
    def set_window_size(self, width: int | float, height: int | float) -> None:
        """Set window size. Use this instead of modifying window_size directly.
        
        Args:
            width: New window width
            height: New window height
        """
        width, height = int(width), int(height)
        glfw.set_window_size(self.window, width, height)
        self.window_size.set(width, height)
    
    def set_window_position(self, x: int | float, y: int | float) -> None:
        """Set window position on screen.
        
        Args:
            x: X position (left edge)
            y: Y position (top edge)
        """
        glfw.set_window_pos(self.window, int(x), int(y))
    
    def center_window(self) -> None:
        """Center the window on the primary monitor."""
        video_mode = glfw.get_video_mode(glfw.get_primary_monitor())
        window_w, window_h = int(self.window_size[0]), int(self.window_size[1])
        screen_w, screen_h = video_mode.size.width, video_mode.size.height
        self.set_window_position((screen_w - window_w) // 2, (screen_h - window_h) // 2)
    
    def set_window_title(self, title: str) -> None:
        """Set window title.
        
        Args:
            title: New window title
        """
        glfw.set_window_title(self.window, title)
    
    def maximize_window(self) -> None:
        """Maximize the window."""
        glfw.maximize_window(self.window)
    
    def minimize_window(self) -> None:
        """Minimize (iconify) the window."""
        glfw.iconify_window(self.window)
    
    def restore_window(self) -> None:
        """Restore the window from maximized or minimized state."""
        glfw.restore_window(self.window)
    
    def _on_resize(self, window: WindowType, width: int, height: int) -> None:
        self.window_size.set(width, height)
        fb_size = glfw.get_framebuffer_size(window)
        self.ctx.viewport = (0, 0, fb_size[0], fb_size[1])
        if hasattr(self, 'env') and hasattr(self.env, 'on_resize'):
            self.env.on_resize(fb_size[0], fb_size[1])

    def init(self, env: DefEnv) -> "RootEnv":
        self.env = env
        return self
    
    def init_rec(self, fps: int = 30, draw_on_screen: bool = True, path: str = 'output.mp4') -> None:
        from .winrec import WinRec
        self.__winrecorder__ = WinRec(self, fps=fps, draw_on_screen=draw_on_screen, path=path)
    
    def load_shader_file(self, path: str) -> str:
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

        if self.draw_fps:
            fps = 1.0 / self.delta if self.delta > 0 else 0.0
            self.print(f"FPS: {fps:.2f}", V2(10, 10), scale=1.0, style=MONO_16_TEXT_STYLE, pivot=Pivots.TOP_LEFT)
        
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
            
            if self.keyboard.get_key(Keys.X, KeyState.JUST_PRESSED):
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
        position: Vector2D,
        scale: float = 1.0,
        style: TextStyle = MONO_16_TEXT_STYLE,
        pivot: Pivots|int = Pivots.TOP_LEFT,
        save_cache: bool = False
    ) -> Optional[TextLabel]:

        if isinstance(text_or_label, TextLabel):
            text_or_label.draw()
        else:
            if save_cache:
                return self.text_renderer.create_label(str(text_or_label), position.x, position.y, scale, style, pivot)
            else:
                self.text_renderer.draw_text(str(text_or_label), (position.x, position.y), scale, style, pivot)
    
    # ========== Shape Drawing Methods ==========
    
    def draw_circle(self, center: Vector2D, radius: float,
                   color: ColorType = (1.0, 1.0, 1.0, 1.0),
                   rotation: float = 0.0,
                   border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                   border_width: float = 0.0,
                   antialiasing: float = 1.0) -> None:
        """Draw a circle. See ShapeRenderer.draw_circle for parameters."""
        self.shape_renderer.draw_circle(center, radius, color=color, rotation=rotation,
                                       border_color=border_color, border_width=border_width,
                                       antialiasing=antialiasing)
    
    def draw_rect(self, position: Vector2D, size: Vector2D,
                 color: ColorType = (1.0, 1.0, 1.0, 1.0),
                 rotation: float = 0.0,
                 corner_radius: float = 0.0,
                 border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                 border_width: float = 0.0,
                 antialiasing: float = 1.0) -> None:
        """Draw a rectangle. See ShapeRenderer.draw_rect for parameters."""
        self.shape_renderer.draw_rect(position, size, color=color, rotation=rotation,
                                     corner_radius=corner_radius, border_color=border_color,
                                     border_width=border_width, antialiasing=antialiasing)
    
    def draw_line(self, start: Vector2D, end: Vector2D,
                 width: float = 1.0,
                 color: ColorType = (1.0, 1.0, 1.0, 1.0),
                 antialiasing: float = 1.0) -> None:
        """Draw a line. See ShapeRenderer.draw_line for parameters."""
        self.shape_renderer.draw_line((start.x, start.y), (end.x, end.y), width=width, color=color,
                                     antialiasing=antialiasing)
    
    def draw_lines(self, points,
                  width: float = 1.0,
                  color: ColorType = (1.0, 1.0, 1.0, 1.0),
                  antialiasing: float = 1.0,
                  closed: bool = False) -> None:
        """Draw a polyline. See ShapeRenderer.draw_lines for parameters."""
        self.shape_renderer.draw_lines(points, width=width, color=color,
                                      antialiasing=antialiasing, closed=closed)
    
    def create_circle(self, center: Vector2D, radius: float,
                     color: ColorType = (1.0, 1.0, 1.0, 1.0),
                     rotation: float = 0.0,
                     border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                     border_width: float = 0.0,
                     antialiasing: float = 1.0) -> ShapeLabel:
        """Create a cached circle. See ShapeRenderer.create_circle for parameters."""
        return self.shape_renderer.create_circle(center, radius, color=color, rotation=rotation,
                                                border_color=border_color, border_width=border_width,
                                                antialiasing=antialiasing)
    
    def create_rect(self, position: Vector2D, size: Vector2D,
                   color: ColorType = (1.0, 1.0, 1.0, 1.0),
                   rotation: float = 0.0,
                   corner_radius: float = 0.0,
                   border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
                   border_width: float = 0.0,
                   antialiasing: float = 1.0) -> ShapeLabel:
        """Create a cached rectangle. See ShapeRenderer.create_rect for parameters."""
        return self.shape_renderer.create_rect(position, size, color=color, rotation=rotation, corner_radius=corner_radius, border_color=border_color, border_width=border_width, antialiasing=antialiasing)
    
    def create_line(self, start: Vector2D, end: Vector2D,
                   width: float = 1.0,
                   color: ColorType = (1.0, 1.0, 1.0, 1.0),
                   antialiasing: float = 1.0) -> ShapeLabel:
        """Create a cached line. See ShapeRenderer.create_line for parameters."""
        return self.shape_renderer.create_line(start, end, width=width, color=color,
                                              antialiasing=antialiasing)
    
    def create_lines(self, points,
                    width: float = 1.0,
                    color: ColorType = (1.0, 1.0, 1.0, 1.0),
                    antialiasing: float = 1.0,
                    closed: bool = False) -> ShapeLabel:
        """Create a cached polyline. See ShapeRenderer.create_lines for parameters."""
        return self.shape_renderer.create_lines(points, width=width, color=color,
                                               antialiasing=antialiasing, closed=closed)
    
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
    'WindowConfig',
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
    'Vector2D',
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
    'DEFAULT_16_TEXT_STYLE',
    'MONO_16_TEXT_STYLE',
    # Shape rendering
    'ShapeRenderer',
    'ShapeLabel',
    'InstancedShapeBatch',
    'FillMode',
    # Input devices
    'Keyboard',
    'Mouse',
    'KeyState',
    'Keys',
    'MouseButtons',
    # ModernGL utilities
    'get_pattr',
    'get_pattr_value',
    'set_pattr_value',
    'get_uniform',
    # Compilation flags
    '_COLOR_COMPILED',
    'PI',
    'PI_HALF',
    'PI_QUARTER',
    'TAU',
]