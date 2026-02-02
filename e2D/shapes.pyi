"""
Type stubs for shapes module
High-performance 2D shape rendering using SDF and GPU shaders
"""

import moderngl
import numpy as np
import numpy.typing as npt
from typing import Optional, Sequence
from enum import Enum
from .types import ContextType, ProgramType, VAOType, VectorType, ColorType, BufferType
from .color_defs import WHITE, TRANSPARENT

class FillMode(Enum):
    """Shape fill mode"""
    FILL: int
    STROKE: int
    FILL_STROKE: int

class ShapeLabel:
    """A pre-rendered shape for efficient repeated drawing."""
    ctx: ContextType
    prog: ProgramType
    vbo: BufferType
    vertex_count: int
    shape_type: str
    vao: VAOType
    
    def __init__(
        self, 
        ctx: ContextType, 
        prog: ProgramType, 
        vbo: BufferType, 
        vertex_count: int, 
        shape_type: str = 'line'
    ) -> None: ...
    
    def draw(self) -> None:
        """Draw the cached shape."""
        ...

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
    
    def __init__(
        self, 
        ctx: ContextType, 
        prog: ProgramType, 
        shape_type: str = 'circle', 
        max_instances: int = 100000
    ) -> None: ...
    
    def add_circle(
        self, 
        center: VectorType, 
        radius: float,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
        border_width: float = 0.0,
        antialiasing: float = 1.0
    ) -> None:
        """Add a circle instance to the batch."""
        ...
    
    def add_circles_numpy(
        self, 
        centers: npt.NDArray[np.float32], 
        radii: npt.NDArray[np.float32], 
        colors: npt.NDArray[np.float32],
        border_colors: Optional[npt.NDArray[np.float32]] = None,
        border_widths: Optional[npt.NDArray[np.float32]] = None,
        antialiasing: float = 1.0
    ) -> None:
        """Add multiple circles efficiently using numpy arrays (10-50x faster than loop)."""
        ...
    
    def add_rect(
        self, 
        center: VectorType, 
        size: VectorType,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        corner_radius: float = 0.0,
        border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
        border_width: float = 0.0,
        antialiasing: float = 1.0,
        rotation: float = 0.0
    ) -> None:
        """Add a rectangle instance to the batch."""
        ...
    
    def add_rects_numpy(
        self, 
        centers: npt.NDArray[np.float32], 
        sizes: npt.NDArray[np.float32],
        colors: npt.NDArray[np.float32],
        corner_radii: Optional[npt.NDArray[np.float32]] = None,
        border_colors: Optional[npt.NDArray[np.float32]] = None,
        border_widths: Optional[npt.NDArray[np.float32]] = None,
        antialiasing: float = 1.0,
        rotations: Optional[npt.NDArray[np.float32]] = None
    ) -> None:
        """Add multiple rectangles efficiently using numpy arrays."""
        ...
    
    def add_line(
        self, 
        start: VectorType, 
        end: VectorType,
        width: float = 1.0,
        color: ColorType = (1.0, 1.0, 1.0, 1.0)
    ) -> None:
        """Add a line instance to the batch."""
        ...
    
    def add_lines_numpy(
        self, 
        starts: npt.NDArray[np.float32], 
        ends: npt.NDArray[np.float32],
        widths: npt.NDArray[np.float32], 
        colors: npt.NDArray[np.float32]
    ) -> None:
        """Add multiple lines efficiently using numpy arrays."""
        ...
    
    def flush(self) -> None:
        """Draw all instances in a single draw call."""
        ...
    
    def clear(self) -> None:
        """Clear the batch without drawing."""
        ...

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
    
    def __init__(self, ctx: ContextType) -> None: ...
    
    def draw_circle(
        self, 
        center: VectorType, 
        radius: float,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        rotation: float = 0.0,
        border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
        border_width: float = 0.0,
        antialiasing: float = 1.0
    ) -> None:
        """Draw a circle immediately."""
        ...
    
    def create_circle(
        self, 
        center: VectorType, 
        radius: float,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        rotation: float = 0.0,
        border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
        border_width: float = 0.0,
        antialiasing: float = 1.0
    ) -> ShapeLabel:
        """Create a cached circle for repeated drawing."""
        ...
    
    def draw_rect(
        self, 
        position: VectorType, 
        size: VectorType,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        rotation: float = 0.0,
        corner_radius: float = 0.0,
        border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
        border_width: float = 0.0,
        antialiasing: float = 1.0
    ) -> None:
        """Draw a rectangle immediately."""
        ...
    
    def create_rect(
        self, 
        position: VectorType, 
        size: VectorType,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        rotation: float = 0.0,
        corner_radius: float = 0.0,
        border_color: ColorType = (0.0, 0.0, 0.0, 0.0),
        border_width: float = 0.0,
        antialiasing: float = 1.0
    ) -> ShapeLabel:
        """Create a cached rectangle for repeated drawing."""
        ...
    
    def draw_line(
        self, 
        start: VectorType, 
        end: VectorType,
        width: float = 1.0,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        antialiasing: float = 1.0
    ) -> None:
        """Draw a single line segment."""
        ...
    
    def draw_lines(
        self, 
        points: npt.NDArray[np.float32] | Sequence[VectorType],
        width: float = 1.0,
        color: ColorType | npt.NDArray[np.float32] = (1.0, 1.0, 1.0, 1.0),
        antialiasing: float = 1.0,
        closed: bool = False
    ) -> None:
        """Draw a polyline (connected line segments)."""
        ...
    
    def create_line(
        self, 
        start: VectorType, 
        end: VectorType,
        width: float = 1.0,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        antialiasing: float = 1.0
    ) -> ShapeLabel:
        """Create a cached line for repeated drawing."""
        ...
    
    def create_lines(
        self, 
        points: npt.NDArray[np.float32] | Sequence[VectorType],
        width: float = 1.0,
        color: ColorType | npt.NDArray[np.float32] = (1.0, 1.0, 1.0, 1.0),
        antialiasing: float = 1.0,
        closed: bool = False
    ) -> ShapeLabel:
        """Create a cached polyline for repeated drawing."""
        ...
    
    def create_circle_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple circles efficiently using GPU instancing."""
        ...
    
    def create_rect_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple rectangles efficiently using GPU instancing."""
        ...
    
    def create_line_batch(self, max_shapes: int = 10000) -> InstancedShapeBatch:
        """Create a batch for drawing multiple lines efficiently using GPU instancing."""
        ...
