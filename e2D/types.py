"""
Type definitions for e2D library
Provides common type aliases and type hints used throughout the library
"""

from __future__ import annotations

# Simple type aliases without imports to avoid circular dependencies
# These are used for type hints only

# Type alias for vector-like objects
# At runtime, accepts: Vector2D instances, tuples of 2 numbers, or sequences of 2 numbers
# Use this for ALL vector/position/size parameters for maximum flexibility
VectorType = object  # Union at type-check time via .pyi file

# Color type (RGBA values between 0.0 and 1.0)
ColorType = tuple[float, float, float, float]

# Numeric types
Number = int | float
IntVec2 = tuple[int, int]
FloatVec2 = tuple[float, float]
NumVec2 = tuple[Number, Number]

# Array-like types for numpy and buffers
pArray = object  # list | tuple at runtime
ArrayLike = object  # numpy array or similar at runtime

# Shader and GPU resource types (forward declarations at runtime)
ContextType = object  # moderngl.Context
ProgramType = object  # moderngl.Program
ComputeShaderType = object  # moderngl.ComputeShader
BufferType = object  # moderngl.Buffer
VAOType = object  # moderngl.VertexArray
TextureType = object  # moderngl.Texture

ProgramAttrType = object  # moderngl.Uniform | moderngl.UniformBlock | moderngl.Attribute | moderngl.Varying
UniformType = object  # moderngl.Uniform
UniformBlockType = object  # moderngl.UniformBlock

# Window and input types
WindowType = object  # glfw window

__all__ = [
    'VectorType',
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
