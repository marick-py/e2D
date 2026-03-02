"""
WindowConfig — encapsulates all GLFW window creation and display settings.
"""

from __future__ import annotations
from typing import Optional
import glfw

from ..vectors import Vector2D, V2


class WindowConfig:
    """Complete window and monitor configuration settings.

    Example::

        config = WindowConfig(
            size=(1920, 1080),
            title="My Game",
            fullscreen=False,
            vsync=True,
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

    # MSAA
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
        # Window behaviour
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
        fixed_update_rate: int = 0,
        # OpenGL settings
        opengl_version: tuple[int, int] = (4, 3),
        opengl_profile: int = glfw.OPENGL_CORE_PROFILE,
        opengl_forward_compat: bool = True,
        # Anti-aliasing
        samples: int = 0,
        # Framebuffer bit depths
        red_bits: int = 8,
        green_bits: int = 8,
        blue_bits: int = 8,
        alpha_bits: int = 8,
        depth_bits: int = 24,
        stencil_bits: int = 8,
    ) -> None:
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
        self.monitor = None

        self.vsync = vsync
        self.target_fps = target_fps
        self.draw_fps = draw_fps
        self.fixed_update_rate = fixed_update_rate

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
        if not self.fullscreen:
            return None
        monitors = glfw.get_monitors()
        if self.monitor_index < len(monitors):
            return monitors[self.monitor_index]
        print(f"Warning: Monitor index {self.monitor_index} out of range, using primary monitor")
        return glfw.get_primary_monitor()

    def apply_hints(self) -> None:
        """Apply all window hints to GLFW before window creation."""
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, self.opengl_version[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, self.opengl_version[1])
        glfw.window_hint(glfw.OPENGL_PROFILE, self.opengl_profile)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, self.opengl_forward_compat)

        glfw.window_hint(glfw.RESIZABLE, self.resizable)
        glfw.window_hint(glfw.VISIBLE, self.visible)
        glfw.window_hint(glfw.DECORATED, self.decorated)
        glfw.window_hint(glfw.FOCUSED, self.focused)
        glfw.window_hint(glfw.AUTO_ICONIFY, self.auto_iconify)
        glfw.window_hint(glfw.FLOATING, self.floating)
        glfw.window_hint(glfw.MAXIMIZED, self.maximized)

        glfw.window_hint(glfw.RED_BITS, self.red_bits)
        glfw.window_hint(glfw.GREEN_BITS, self.green_bits)
        glfw.window_hint(glfw.BLUE_BITS, self.blue_bits)
        glfw.window_hint(glfw.ALPHA_BITS, self.alpha_bits)
        glfw.window_hint(glfw.DEPTH_BITS, self.depth_bits)
        glfw.window_hint(glfw.STENCIL_BITS, self.stencil_bits)

        if self.samples > 0:
            glfw.window_hint(glfw.SAMPLES, self.samples)


__all__ = ['WindowConfig']
