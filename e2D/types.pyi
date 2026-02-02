"""
Type stubs for types module
Common type definitions for e2D library
"""

from typing import Union, Sequence
import numpy as np
import numpy.typing as npt
import moderngl
from .cvectors import Vector2D
from glfw import _GLFWwindow

# Type alias for vector-like objects - use this for ALL 2D vectors, positions, and sizes
# Accepts Vector2D instances, tuples (x, y), or lists [x, y]
VectorType = Union[Vector2D, tuple[int | float, int | float], Sequence[int | float]]

# Color type (RGBA values between 0.0 and 1.0)
ColorType = tuple[float, float, float, float]

# Numeric types
Number = int | float
IntVec2 = tuple[int, int]
FloatVec2 = tuple[float, float]
NumVec2 = tuple[Number, Number]

# Array-like types for numpy and buffers
pArray = list | tuple
ArrayLike = npt.NDArray[np.float32] | npt.NDArray[np.float64] | npt.NDArray[np.int32]

# Shader and GPU resource types
ContextType = moderngl.Context
ProgramType = moderngl.Program
ComputeShaderType = moderngl.ComputeShader
BufferType = moderngl.Buffer
VAOType = moderngl.VertexArray
TextureType = moderngl.Texture

ProgramAttrType = moderngl.Uniform | moderngl.UniformBlock | moderngl.Attribute | moderngl.Varying
UniformType = moderngl.Uniform
UniformBlockType = moderngl.UniformBlock

# Window type
WindowType = _GLFWwindow


__all__ = [
    'VectorType',
    'Vector2D',
    'ColorType',
    'Number',
    'IntVec2',
    'FloatVec2',
    'NumVec2',
    'ArrayLike',
    'ContextType',
    'ProgramType',
    'BufferType',
    'VAOType',
    'TextureType',
    'WindowType',
]