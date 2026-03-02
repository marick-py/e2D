"""
Type definitions for the e2D library.

Heavy imports are guarded by TYPE_CHECKING so they are skipped at runtime
(avoiding circular imports and startup cost) but fully visible to Pyright/mypy.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    import numpy.typing as npt
    import numpy as np
    import moderngl
    from glfw import _GLFWwindow
    from .colors import Color

# ----- colour ---------------------------------------------------------------
ColorType = Union['Color', 'tuple[float, float, float, float]']

# ----- numeric --------------------------------------------------------------
Number = int | float
IntVec2 = tuple[int, int]
FloatVec2 = tuple[float, float]
NumVec2 = tuple[Number, Number]

# ----- array-like -----------------------------------------------------------
pArray = list | tuple
ArrayLike = Union[
    'npt.NDArray[np.float32]',
    'npt.NDArray[np.float64]',
    'npt.NDArray[np.int32]',
]

# ----- GPU / moderngl -------------------------------------------------------
ContextType      = moderngl.Context
ProgramType      = moderngl.Program
ComputeShaderType= moderngl.ComputeShader
BufferType       = moderngl.Buffer
VAOType          = moderngl.VertexArray
TextureType      = moderngl.Texture

ProgramAttrType  = Union[
    'moderngl.Uniform', 'moderngl.UniformBlock',
    'moderngl.Attribute', 'moderngl.Varying',
]
UniformType      = moderngl.Uniform
UniformBlockType = moderngl.UniformBlock

# ----- window / input -------------------------------------------------------
WindowType = _GLFWwindow

__all__ = [
    'ColorType',
    'Number',
    'IntVec2',
    'FloatVec2',
    'NumVec2',
    'ArrayLike',
    'pArray',
    'ContextType',
    'ProgramType',
    'ComputeShaderType',
    'BufferType',
    'VAOType',
    'TextureType',
    'ProgramAttrType',
    'UniformType',
    'UniformBlockType',
    'WindowType',
]
