"""
Type stubs for text_renderer module
Text rendering using texture atlases and TTF fonts
"""

from enum import Enum
from typing import Optional
from .types import ColorType, ContextType, ProgramType, TextureType, VAOType, VectorType, BufferType
from .color_defs import WHITE

class TextStyle:
    """Text styling options"""
    font: str
    font_size: int
    color: ColorType
    bg_color: ColorType
    bg_margin: float | tuple[float, float, float, float]
    bg_border_radius: float | tuple[float, float, float, float]
    
    def __init__(
        self,
        font: str = "arial.ttf",
        font_size: int = 32,
        color: ColorType = (1.0, 1.0, 1.0, 1.0),
        bg_color: ColorType = (0.0, 0.0, 0.0, 0.9),
        bg_margin: float | tuple[float, float, float, float] = 15.0,
        bg_border_radius: float | tuple[float, float, float, float] = 15.0
    ) -> None: ...

class Pivots(Enum):
    """Text anchor/pivot points"""
    TOP_LEFT: int
    TOP_MIDDLE: int
    TOP_RIGHT: int
    LEFT: int
    CENTER: int
    RIGHT: int
    BOTTOM_LEFT: int
    BOTTOM_MIDDLE: int
    BOTTOM_RIGHT: int

DEFAULT_TEXT_STYLE: TextStyle

class TextLabel:
    """A pre-rendered text label for efficient drawing."""
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
    
    def __init__(
        self, 
        ctx: ContextType, 
        prog: ProgramType, 
        texture: TextureType, 
        vertices: list[float],
        bg_prog: Optional[ProgramType] = None, 
        bg_vertices: Optional[list[float]] = None
    ) -> None: ...
    
    def draw(self) -> None:
        """Draw the text label"""
        ...

class TextRenderer:
    """
    Renders text using a texture atlas generated from a TTF font via Pillow.
    Supports multiple fonts and sizes with caching for optimization.
    """
    ctx: ContextType
    font_cache: dict[tuple[str, int], dict]
    chars: str
    bg_prog: ProgramType
    bg_vbo: BufferType
    bg_vao: VAOType
    prog: ProgramType
    vbo: BufferType
    vao: VAOType
    
    def __init__(self, ctx: ContextType) -> None: ...
    
    def get_text_width(
        self, 
        text: str, 
        scale: float = 1.0, 
        style: TextStyle = DEFAULT_TEXT_STYLE
    ) -> float:
        """Calculate the width of the text."""
        ...
    
    def draw_text(
        self,
        text: str,
        pos: VectorType,
        scale: float = 1.0,
        style: TextStyle = DEFAULT_TEXT_STYLE,
        pivot: Pivots | int = Pivots.TOP_LEFT
    ) -> None:
        """Draw text immediately."""
        ...
    
    def create_label(
        self,
        text: str,
        x: float,
        y: float,
        scale: float = 1.0,
        style: TextStyle = DEFAULT_TEXT_STYLE,
        pivot: Pivots | int = Pivots.TOP_LEFT
    ) -> TextLabel:
        """Create a cached text label for repeated drawing."""
        ...
