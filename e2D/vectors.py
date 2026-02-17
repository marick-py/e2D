"""
High-level Python wrapper for Vector2D and Vector2Int with additional utilities
Provides compatibility layer and convenience functions
"""

# Import compiled Cython implementation (required)
from .cvectors import ( # type: ignore
    Vector2D,
    Vector2Int,
    batch_add_inplace,
    batch_scale_inplace,
    batch_normalize_inplace,
    vectors_to_array,
    array_to_vectors,
    seed_rng,
)


# Convenience aliases
V2 = Vector2D
Vec2 = Vector2D
V2I = Vector2Int
Vec2I = Vector2Int


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
    'seed_rng',
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
    vectors = [Vector2D(i, i+1) for i in range(1000)]
    displacement = Vector2D(1.0, 1.0)
    start = time.perf_counter()
    for i in range(num_iterations // 1000):
        batch_add_inplace(vectors, displacement)
    end = time.perf_counter()
    print(f"Batch add:     {(end - start) * 1000:.2f} ms")
    
    print("=" * 50)
    print("✓ Using compiled Cython extension")


if __name__ == "__main__":
    # Run benchmark when executed directly
    benchmark()

