"""
High-level Python wrapper for Vector2D with additional utilities
Provides compatibility layer and convenience functions
"""

from typing import Any, List, Literal, Protocol, runtime_checkable, TYPE_CHECKING, Sequence, cast
import numpy as np
from numpy.typing import NDArray

# Define a protocol that both implementations must follow
@runtime_checkable
class Vector2DProtocol(Protocol):
    """Protocol defining the Vector2D interface for type checking"""
    x: float
    y: float
    
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None: ...
    def copy(self) -> "Vector2DProtocol": ...
    def normalize(self) -> None: ...
    def __add__(self, other: Any) -> "Vector2DProtocol": ...
    def __sub__(self, other: Any) -> "Vector2DProtocol": ...
    def __mul__(self, other: Any) -> "Vector2DProtocol": ...
    def __getitem__(self, idx: int) -> float: ...
    def __setitem__(self, idx: int, value: float) -> None: ...
    def __len__(self) -> int: ...
    @property
    def length(self) -> float: ...
    @property
    def length_sqrd(self) -> float: ...

# For type checking - define stubs
if TYPE_CHECKING:
    # Constructor function for type checking
    def Vector2D(x: float = 0.0, y: float = 0.0) -> Vector2DProtocol: ...  # noqa: F811
    
    # Type stubs for batch operations
    def batch_add_inplace(vectors: Sequence[Vector2DProtocol], displacement: Vector2DProtocol) -> None: ...
    def batch_scale_inplace(vectors: Sequence[Vector2DProtocol], scalar: float) -> None: ...
    def batch_normalize_inplace(vectors: Sequence[Vector2DProtocol]) -> None: ...
    def vectors_to_array(vectors: Sequence[Vector2DProtocol]) -> NDArray[np.float64]: ...
    def array_to_vectors(arr: NDArray[np.float64]) -> list[Vector2DProtocol]: ...

# Try to import the optimized Cython version, fall back to pure Python
_COMPILED = False
if not TYPE_CHECKING:
    try:
        from .cvectors import (  # type: ignore[assignment]
            Vector2D,
            batch_add_inplace,
            batch_scale_inplace,
            batch_normalize_inplace,
            vectors_to_array,
            array_to_vectors,
        )
        _COMPILED = True
    except ImportError:
        print("WARNING: Compiled cvectors module not found. Please run: python setup.py build_ext --inplace")
        print("Falling back to pure Python implementation (slower)")
        _COMPILED = False
        
        # Fallback pure Python implementation
        class Vector2D:  # type: ignore[no-redef]
            """Pure Python fallback (much slower than compiled version)"""
            def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
                self.data = np.array([x, y], dtype=np.float64)
            
            @property
            def x(self) -> float:
                return self.data[0]
            
            @x.setter
            def x(self, value: float) -> None:
                self.data[0] = value
            
            @property
            def y(self) -> float:
                return self.data[1]
            
            @y.setter
            def y(self, value: float) -> None:
                self.data[1] = value
            
            @property
            def length(self) -> np.floating:
                return np.linalg.norm(self.data)
            
            @property
            def length_sqrd(self) -> float:
                return np.dot(self.data, self.data)
            
            def copy(self) -> "Vector2D":
                return Vector2D(self.x, self.y)
            
            def normalize(self) -> None:
                """Normalize this vector in place"""
                length = self.length
                if length > 0:
                    self.data /= length
            
            def __add__(self, other) -> "Vector2D":
                if isinstance(other, Vector2D):
                    return Vector2D(self.x + other.x, self.y + other.y)
                return Vector2D(self.x + other, self.y + other)
            
            def __sub__(self, other) -> "Vector2D":
                if isinstance(other, Vector2D):
                    return Vector2D(self.x - other.x, self.y - other.y)
                return Vector2D(self.x - other, self.y - other)
            
            def __mul__(self, other) -> "Vector2D":
                if isinstance(other, Vector2D):
                    return Vector2D(self.x * other.x, self.y * other.y)
                return Vector2D(self.x * other, self.y * other)
            
            def __getitem__(self, idx) -> float:
                """Support indexing like a tuple (v[0], v[1])"""
                if idx == 0:
                    return self.x
                elif idx == 1:
                    return self.y
                raise IndexError("Vector2D index out of range")
            
            def __setitem__(self, idx, value) -> None:
                """Support setting by index (v[0] = x)"""
                if idx == 0:
                    self.x = value
                elif idx == 1:
                    self.y = value
                else:
                    raise IndexError("Vector2D index out of range")
            
            def __len__(self) -> Literal[2]:
                """Support len(v) -> 2"""
                return 2
            
            def __repr__(self) -> str:
                return f"Vector2D({self.x}, {self.y})"
        
        # Fallback batch operations
        def batch_add_inplace(vectors: Sequence[Vector2D], displacement: Vector2D) -> None:  # type: ignore[misc]
            """Pure Python fallback for batch add"""
            for vec in vectors:
                vec.data += displacement.data  # type: ignore[attr-defined]
        
        def batch_scale_inplace(vectors: Sequence[Vector2D], scalar: float) -> None:  # type: ignore[misc]
            """Pure Python fallback for batch scale"""
            for vec in vectors:
                vec.data *= scalar  # type: ignore[attr-defined]
        
        def batch_normalize_inplace(vectors: Sequence[Vector2D]) -> None:  # type: ignore[misc]
            """Pure Python fallback for batch normalize"""
            for vec in vectors:
                length = vec.length
                if length > 0:
                    vec.data /= length  # type: ignore[attr-defined]
        
        def vectors_to_array(vectors: Sequence[Vector2D]) -> NDArray[np.float64]:  # type: ignore[misc]
            """Pure Python fallback for vectors to array"""
            return np.array([v.data for v in vectors], dtype=np.float64)  # type: ignore[attr-defined]
        
        def array_to_vectors(arr: NDArray[np.float64]) -> list[Vector2D]:  # type: ignore[misc]
            """Pure Python fallback for array to vectors"""
            return [Vector2D(row[0], row[1]) for row in arr]


# Convenience aliases
V2 = Vector2D
Vec2 = Vector2D


# Pre-defined common vectors (reusable instances for performance)
class CommonVectors:
    """Pre-allocated common vectors (do not modify these!)"""
    ZERO = Vector2D(0.0, 0.0)
    ONE = Vector2D(1.0, 1.0)
    UP = Vector2D(0.0, 1.0)
    DOWN = Vector2D(0.0, -1.0)
    LEFT = Vector2D(-1.0, 0.0)
    RIGHT = Vector2D(1.0, 0.0)
    
    @staticmethod
    def zero():
        """Create new zero vector"""
        return Vector2D(0.0, 0.0)
    
    @staticmethod
    def one():
        """Create new one vector"""
        return Vector2D(1.0, 1.0)
    
    @staticmethod
    def up():
        """Create new up vector"""
        return Vector2D(0.0, 1.0)
    
    @staticmethod
    def down():
        """Create new down vector"""
        return Vector2D(0.0, -1.0)
    
    @staticmethod
    def left():
        """Create new left vector"""
        return Vector2D(-1.0, 0.0)
    
    @staticmethod
    def right():
        """Create new right vector"""
        return Vector2D(1.0, 0.0)


# Export all public API
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
    '_COMPILED',
]


# Additional utility functions
def lerp(start, end, t):
    """Linear interpolation between two values"""
    return start + (end - start) * t


def create_grid(width, height, spacing=1.0):
    """
    Create a grid of vectors
    
    Args:
        width: Number of columns
        height: Number of rows
        spacing: Distance between points
    
    Returns:
        List of Vector2D objects
    """
    vectors = []
    for y in range(height):
        for x in range(width):
            vectors.append(Vector2D(x * spacing, y * spacing))
    return vectors


def create_circle(radius, num_points):
    """
    Create vectors arranged in a circle
    
    Args:
        radius: Circle radius
        num_points: Number of points
    
    Returns:
        List of Vector2D objects
    """
    import math
    vectors = []
    angle_step = 2 * math.pi / num_points
    for i in range(num_points):
        angle = i * angle_step
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        vectors.append(Vector2D(x, y))
    return vectors


# Performance benchmark function
def benchmark(num_iterations=100000):
    """
    Run a simple benchmark to test vector performance
    """
    import time
    
    print(f"Vector2D Benchmark ({num_iterations} iterations)")
    print("=" * 50)
    
    # Test 1: Vector creation
    start = time.perf_counter()
    for i in range(num_iterations):
        v = Vector2D(1.0, 2.0)
    end = time.perf_counter()
    print(f"Creation:      {(end - start) * 1000:.2f} ms")
    
    # Test 2: Addition
    v1 = Vector2D(1.0, 2.0)
    v2 = Vector2D(3.0, 4.0)
    start = time.perf_counter()
    for i in range(num_iterations):
        v3 = v1 + v2
    end = time.perf_counter()
    print(f"Addition:      {(end - start) * 1000:.2f} ms")
    
    # Test 3: In-place addition
    v1 = Vector2D(1.0, 2.0)
    v2 = Vector2D(3.0, 4.0)
    start = time.perf_counter()
    for i in range(num_iterations):
        v1 += v2
        v1 -= v2  # Keep value constant
    end = time.perf_counter()
    print(f"In-place add:  {(end - start) * 1000:.2f} ms")
    
    # Test 4: Normalization
    vectors = [Vector2D(i, i+1) for i in range(1000)]
    start = time.perf_counter()
    for i in range(num_iterations // 1000):
        for v in vectors:
            v.normalize()
    end = time.perf_counter()
    print(f"Normalize:     {(end - start) * 1000:.2f} ms")
    
    # Test 5: Batch operations
    if _COMPILED:
        vectors = [Vector2D(i, i+1) for i in range(1000)]
        displacement = Vector2D(1.0, 1.0)
        start = time.perf_counter()
        for i in range(num_iterations // 1000):
            batch_add_inplace(vectors, displacement)
        end = time.perf_counter()
        print(f"Batch add:     {(end - start) * 1000:.2f} ms")
    
    print("=" * 50)
    if _COMPILED:
        print("✓ Using compiled Cython extension (optimal performance)")
    else:
        print("⚠ Using pure Python fallback (compile for better performance)")


if __name__ == "__main__":
    # Run benchmark when executed directly
    benchmark()

