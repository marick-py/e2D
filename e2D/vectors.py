"""
High-level Python wrapper for Vector2D with additional utilities
Provides compatibility layer and convenience functions
"""

try:
    from .cvectors import (
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
    
    # Fallback implementation
    import numpy as np
    
    class Vector2D:
        """Pure Python fallback (much slower than compiled version)"""
        def __init__(self, x=0.0, y=0.0):
            self.data = np.array([x, y], dtype=np.float64)
        
        @property
        def x(self):
            return self.data[0]
        
        @x.setter
        def x(self, value):
            self.data[0] = value
        
        @property
        def y(self):
            return self.data[1]
        
        @y.setter
        def y(self, value):
            self.data[1] = value
        
        @property
        def length(self):
            return np.linalg.norm(self.data)
        
        @property
        def length_sqrd(self):
            return np.dot(self.data, self.data)
        
        def copy(self):
            return Vector2D(self.x, self.y)
        
        def __add__(self, other):
            if isinstance(other, Vector2D):
                return Vector2D(self.x + other.x, self.y + other.y)
            return Vector2D(self.x + other, self.y + other)
        
        def __sub__(self, other):
            if isinstance(other, Vector2D):
                return Vector2D(self.x - other.x, self.y - other.y)
            return Vector2D(self.x - other, self.y - other)
        
        def __mul__(self, other):
            if isinstance(other, Vector2D):
                return Vector2D(self.x * other.x, self.y * other.y)
            return Vector2D(self.x * other, self.y * other)
        
        def __repr__(self):
            return f"Vector2D({self.x}, {self.y})"


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

