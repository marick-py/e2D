"""
Simple example demonstrating Vector2D usage
"""

from e2D.vectors import Vector2D, V2, batch_add_inplace, batch_normalize_inplace
import time

def example_basic_operations():
    """Basic vector operations"""
    print("=== Basic Operations ===")
    
    # Create vectors
    v1 = Vector2D(3.0, 4.0)
    v2 = V2(1.0, 2.0)
    
    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v1 length: {v1.length}")
    print(f"v1 + v2 = {v1 + v2}")
    print(f"v1 * 2 = {v1 * 2}")
    print(f"dot product: {v1.dot_product(v2)}")
    print(f"distance: {v1.distance_to(v2)}")
    print()


def example_performance():
    """Demonstrate performance with batch operations"""
    print("=== Performance Demo ===")
    
    # Create 100,000 vectors
    num_vectors = 100000
    print(f"Creating {num_vectors:,} vectors...")
    
    start = time.perf_counter()
    vectors = [Vector2D(i * 0.001, i * 0.002) for i in range(num_vectors)]
    end = time.perf_counter()
    print(f"Creation time: {(end - start) * 1000:.2f} ms")
    
    # Individual operations (slower)
    print("\nIndividual operations (Python loop):")
    displacement = Vector2D(1.0, 0.5)
    start = time.perf_counter()
    for v in vectors:
        v += displacement
    end = time.perf_counter()
    print(f"Time: {(end - start) * 1000:.2f} ms")
    
    # Batch operations (much faster)
    print("\nBatch operations (C loop):")
    displacement = Vector2D(-1.0, -0.5)  # Reverse the change
    start = time.perf_counter()
    batch_add_inplace(vectors, displacement)
    end = time.perf_counter()
    print(f"Time: {(end - start) * 1000:.2f} ms")
    print(f"Speedup: {((end - start) * 1000) / ((end - start) * 1000):.1f}x faster")
    print()


def example_particle_simulation():
    """Simple particle simulation"""
    print("=== Particle Simulation ===")
    
    class Particle:
        def __init__(self, x, y):
            self.position = Vector2D(x, y)
            self.velocity = Vector2D.random(-1.0, 1.0)
            self.acceleration = Vector2D(0.0, -0.98)  # Gravity
        
        def update(self, dt):
            # Physics integration (optimized in-place operations)
            temp = self.acceleration.mul(dt)
            self.velocity.iadd(temp)
            
            temp = self.velocity.mul(dt)
            self.position.iadd(temp)
            
            # Simple boundary bounce
            if self.position.y < 0:
                self.position.y = 0
                self.velocity.y = abs(self.velocity.y) * 0.8
    
    # Create particles
    num_particles = 1000
    particles = [Particle(i * 0.1, 10.0) for i in range(num_particles)]
    
    print(f"Simulating {num_particles} particles...")
    
    # Simulate for 100 steps
    start = time.perf_counter()
    dt = 0.016  # ~60 FPS
    for step in range(100):
        for particle in particles:
            particle.update(dt)
    end = time.perf_counter()
    
    print(f"100 simulation steps: {(end - start) * 1000:.2f} ms")
    print(f"Average per frame: {(end - start) * 10:.2f} ms")
    print(f"Theoretical FPS: {100 / (end - start):.0f}")
    print()


def example_vector_math():
    """Advanced vector mathematics"""
    print("=== Vector Math ===")
    
    v1 = Vector2D(1.0, 0.0)
    v2 = Vector2D(0.0, 1.0)
    
    # Rotation
    import math
    rotated = v1.rotate(math.pi / 4)  # 45 degrees
    print(f"Rotate (1,0) by 45°: {rotated}")
    
    # Projection
    v3 = Vector2D(3.0, 4.0)
    v4 = Vector2D(1.0, 0.0)
    proj = v3.projection(v4)
    print(f"Project (3,4) onto (1,0): {proj}")
    
    # Reflection
    incident = Vector2D(1.0, -1.0)
    normal = Vector2D(0.0, 1.0)
    reflected = incident.reflection(normal)
    print(f"Reflect (1,-1) across (0,1): {reflected}")
    
    # Interpolation
    start = Vector2D(0.0, 0.0)
    end = Vector2D(10.0, 10.0)
    mid = start.lerp(end, 0.5)
    print(f"Lerp from (0,0) to (10,10) at t=0.5: {mid}")
    print()


def example_moderngl_integration():
    """Example of using with ModernGL (pseudo-code)"""
    print("=== ModernGL Integration (Example) ===")
    
    from e2D.vectors import vectors_to_array
    import numpy as np
    
    # Create particle positions
    positions = [Vector2D.random(-10, 10) for _ in range(1000)]
    
    # Convert to numpy array for GPU upload
    buffer_data = vectors_to_array(positions).astype(np.float32)
    
    print(f"Buffer shape: {buffer_data.shape}")
    print(f"Buffer dtype: {buffer_data.dtype}")
    print(f"Buffer size: {buffer_data.nbytes} bytes")
    print("\nThis array can be directly uploaded to GPU via:")
    print("  vbo.write(buffer_data)")
    print()


if __name__ == "__main__":
    print("Vector2D Examples")
    print("=" * 50)
    print()
    
    example_basic_operations()
    example_vector_math()
    example_performance()
    example_particle_simulation()
    example_moderngl_integration()
    
    print("=" * 50)
    print("All examples completed!")

