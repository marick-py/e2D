"""
Type stubs for vectors module
High-level Python wrapper for Vector2D with additional utilities
"""

from typing import List, Tuple, Callable
from .cvectors import Vector2D, batch_add_inplace, batch_scale_inplace, batch_normalize_inplace, vectors_to_array, array_to_vectors

_COMPILED : bool
# Convenience aliases
V2 = Vector2D
Vec2 = Vector2D

# Pre-defined common vectors
class CommonVectors:
    """Pre-allocated common vectors (do not modify these!)"""
    ZERO: Vector2D
    ONE: Vector2D
    UP: Vector2D
    DOWN: Vector2D
    LEFT: Vector2D
    RIGHT: Vector2D
    
    @staticmethod
    def zero() -> Vector2D:
        """Create new zero vector"""
        ...
    
    @staticmethod
    def one() -> Vector2D:
        """Create new one vector"""
        ...
    
    @staticmethod
    def up() -> Vector2D:
        """Create new up vector"""
        ...
    
    @staticmethod
    def down() -> Vector2D:
        """Create new down vector"""
        ...
    
    @staticmethod
    def left() -> Vector2D:
        """Create new left vector"""
        ...
    
    @staticmethod
    def right() -> Vector2D:
        """Create new right vector"""
        ...

# Additional utility functions
def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values"""
    ...

def create_grid(width: int, height: int, spacing: float = 1.0) -> List[Vector2D]:
    """
    Create a grid of vectors
    
    Args:
        width: Number of columns
        height: Number of rows
        spacing: Distance between points
    
    Returns:
        List of Vector2D objects
    """
    ...

def create_circle(radius: float, num_points: int) -> List[Vector2D]:
    """
    Create vectors arranged in a circle
    
    Args:
        radius: Circle radius
        num_points: Number of points
    
    Returns:
        List of Vector2D objects
    """
    ...

def benchmark(num_iterations: int = 100000) -> None:
    """
    Run a simple benchmark to test vector performance
    """
    ...

__all__ = [
    'Vector2D',
    'V2',
    'Vec2',
    'CommonVectors',
    'batch_add_inplace',
    'batch_scale_inplace',
    'batch_normalize_inplace',
    'vectors_to_array',
    'array_to_vectors',
    'lerp',
    'create_grid',
    'create_circle',
    '_COMPILED',
]
