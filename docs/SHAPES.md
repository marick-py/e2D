# Shape Rendering Guide

## Overview

e2D provides high-performance shape rendering using ModernGL with GPU instancing support. This guide covers all shape drawing capabilities.

## Table of Contents

- [Basic Shapes](#basic-shapes)
- [Shape Parameters](#shape-parameters)
- [Cached Shapes](#cached-shapes)
- [Instanced Batching](#instanced-batching)
- [Lines and Polylines](#lines-and-polylines)
- [Performance Tips](#performance-tips)

## Basic Shapes

### Drawing a Circle

```python
from e2D import RootEnv, V2, RED, WHITE

# In your draw() method:
root.draw_circle(
    center=V2(100, 100),
    radius=50,
    color=RED,
    rotation=0.0,  # Optional rotation in radians
    border_color=WHITE,  # Optional border
    border_width=2.0,
    antialiasing=1.0  # Smooth edges
)
```

### Drawing a Rectangle

```python
root.draw_rect(
    position=V2(200, 100),  # Top-left corner
    size=V2(100, 80),       # Width, height
    color=GREEN,
    rotation=0.0,           # Optional rotation
    corner_radius=10.0,     # Rounded corners
    border_color=WHITE,
    border_width=2.0,
    antialiasing=1.0
)
```

## Shape Parameters

### Colors

All shapes accept colors in multiple formats:

```python
from e2D import Color, RED

# Tuple format
root.draw_circle(V2(100, 100), 30, color=(1.0, 0.0, 0.0, 1.0))

# Pre-defined constant
root.draw_circle(V2(100, 100), 30, color=RED)

# Color object
root.draw_circle(V2(100, 100), 30, color=Color.from_hex("#FF0000"))
```

### Borders

```python
# Circle with border
root.draw_circle(
    V2(100, 100), 50,
    color=BLUE,
    border_color=WHITE,
    border_width=3.0  # Border thickness
)

# Rectangle with border
root.draw_rect(
    V2(200, 100), V2(100, 80),
    color=GREEN,
    border_color=BLACK,
    border_width=2.0
)
```

### Corner Radius

```python
# Rounded rectangle
root.draw_rect(
    V2(100, 100), V2(100, 80),
    color=BLUE,
    corner_radius=15.0  # Pixel radius
)

# Fully rounded (pill shape)
root.draw_rect(
    V2(100, 100), V2(120, 40),
    color=RED,
    corner_radius=20.0  # Half of height
)
```

### Antialiasing

```python
# Smooth edges (default)
root.draw_circle(V2(100, 100), 50, antialiasing=1.0)

# Sharp edges (faster)
root.draw_circle(V2(100, 100), 50, antialiasing=0.0)

# Extra smooth (for large shapes)
root.draw_circle(V2(100, 100), 50, antialiasing=2.0)
```

## Cached Shapes

For shapes drawn repeatedly, create cached labels for better performance.

### Creating Cached Shapes

```python
class MyEnv(DefEnv):
    def __init__(self, root):
        self.root = root
        
        # Create once in __init__
        self.player = root.create_circle(
            V2(400, 300), 30,
            color=BLUE,
            border_color=WHITE,
            border_width=2.0
        )
        
        self.button = root.create_rect(
            V2(100, 100), V2(120, 40),
            color=GREEN,
            corner_radius=10.0
        )
    
    def draw(self):
        # Draw many times efficiently
        self.player.draw()
        self.button.draw()
```

### Benefits

```python
# ❌ Slower - rebuilds geometry every frame
def draw(self):
    for i in range(100):
        root.draw_circle(V2(i*10, 100), 20, color=RED)

# ✅ Faster - cached geometry
def __init__(self, root):
    self.circles = [
        root.create_circle(V2(i*10, 100), 20, color=RED)
        for i in range(100)
    ]

def draw(self):
    for circle in self.circles:
        circle.draw()
```

## Instanced Batching

For drawing thousands of shapes, use GPU instancing.

### Circle Batching

```python
class ParticleSystem(DefEnv):
    def __init__(self, root):
        self.root = root
        
        # Create batch (once)
        self.batch = root.create_circle_batch(max_shapes=10000)
    
    def draw(self):
        # Clear previous frame
        self.batch.clear()
        
        # Add all circles
        for particle in self.particles:
            self.batch.add_circle(
                center=particle.position,
                radius=particle.size,
                color=particle.color
            )
        
        # Draw all at once (single GPU call!)
        self.batch.flush()
```

### Rectangle Batching

```python
def draw(self):
    batch = root.create_rect_batch(max_shapes=1000)
    
    batch.clear()
    for tile in self.tiles:
        batch.add_rect(
            center=tile.position,
            size=tile.size,
            color=tile.color,
            corner_radius=5.0
        )
    batch.flush()
```

### Numpy Batch Operations

For maximum performance, use numpy arrays:

```python
import numpy as np

# Create batch
batch = root.create_circle_batch(max_shapes=10000)

# Prepare data as numpy arrays
centers = np.array([[i*10, j*10] for i in range(100) for j in range(100)], dtype='f4')
radii = np.full(10000, 5.0, dtype='f4')
colors = np.random.rand(10000, 4).astype('f4')

# Add all at once (10-50x faster than loop!)
batch.clear()
batch.add_circles_numpy(centers, radii, colors)
batch.flush()
```

## Lines and Polylines

### Single Line

```python
root.draw_line(
    start=V2(100, 100),
    end=V2(300, 200),
    width=5.0,
    color=WHITE,
    antialiasing=1.0
)
```

### Polyline (Connected Lines)

```python
# Define path
points = [
    V2(100, 100),
    V2(200, 150),
    V2(300, 100),
    V2(400, 200)
]

# Draw as connected line
root.draw_lines(
    points=points,
    width=3.0,
    color=CYAN,
    antialiasing=1.0,
    closed=False  # Set True to connect last to first
)
```

### Closed Shapes

```python
# Triangle
triangle = [
    V2(100, 100),
    V2(200, 100),
    V2(150, 200)
]

root.draw_lines(triangle, width=2.0, color=RED, closed=True)

# Hexagon
from e2D import create_circle
hexagon = create_circle(radius=50, segments=6)
root.draw_lines(hexagon, width=2.0, color=BLUE, closed=True)
```

### Cached Lines

```python
def __init__(self, root):
    # Create path once
    self.path = root.create_lines(
        points=[V2(i*10, np.sin(i*0.1)*50 + 200) for i in range(100)],
        width=2.0,
        color=GREEN
    )

def draw(self):
    self.path.draw()
```

## Performance Tips

### 1. Use Cached Shapes for Static Geometry

```python
# ❌ Slow - rebuilds every frame
def draw(self):
    root.draw_circle(V2(100, 100), 50, color=RED)

# ✅ Fast - cached geometry
def __init__(self, root):
    self.shape = root.create_circle(V2(100, 100), 50, color=RED)

def draw(self):
    self.shape.draw()
```

### 2. Use Instancing for Many Shapes

```python
# ❌ Slow - individual draw calls
def draw(self):
    for particle in self.particles:
        root.draw_circle(particle.pos, 5, color=WHITE)

# ✅ Fast - single instanced draw call
def draw(self):
    batch.clear()
    for particle in self.particles:
        batch.add_circle(particle.pos, 5, color=WHITE)
    batch.flush()
```

### 3. Use Numpy for Batch Data

```python
# ❌ Slower - Python loop
for particle in particles:
    batch.add_circle(particle.pos, particle.radius, particle.color)

# ✅ Faster - numpy arrays (10-50x faster!)
positions = vectors_to_array([p.pos for p in particles])
radii = np.array([p.radius for p in particles], dtype='f4')
colors = np.array([p.color for p in particles], dtype='f4')
batch.add_circles_numpy(positions, radii, colors)
```

### 4. Minimize Border Width

```python
# Borders add complexity
root.draw_circle(V2(100, 100), 50, border_width=10.0)  # Slower

# No border is faster
root.draw_circle(V2(100, 100), 50)  # Faster
```

### 5. Reduce Antialiasing for Small Shapes

```python
# Full antialiasing
root.draw_circle(V2(100, 100), 5, antialiasing=1.0)

# Disable for tiny shapes
root.draw_circle(V2(100, 100), 5, antialiasing=0.0)  # Faster
```

## Examples

### Button System

```python
class Button:
    def __init__(self, root, pos, size, text):
        self.pos = pos
        self.size = size
        self.shape = root.create_rect(
            pos, size,
            color=(0.2, 0.2, 0.8, 1.0),
            corner_radius=8.0,
            border_color=WHITE,
            border_width=2.0
        )
        self.label = root.print(text, pos, save_cache=True)
    
    def draw(self):
        self.shape.draw()
        self.label.draw()
```

### Particle Effect

```python
class ParticleEffect:
    def __init__(self, root, count=1000):
        self.batch = root.create_circle_batch(max_shapes=count)
        self.particles = [
            Particle(V2.random(0, 800), V2.random(-100, 100))
            for _ in range(count)
        ]
    
    def update(self, dt):
        for p in self.particles:
            p.position.iadd(p.velocity * dt)
    
    def draw(self):
        self.batch.clear()
        for p in self.particles:
            self.batch.add_circle(p.position, 3.0, color=p.color)
        self.batch.flush()
```

### Health Bar

```python
def draw_health_bar(root, pos, health, max_health):
    # Background
    root.draw_rect(
        pos, V2(100, 10),
        color=(0.2, 0.2, 0.2, 1.0),
        corner_radius=5.0
    )
    
    # Health fill
    width = (health / max_health) * 100
    root.draw_rect(
        pos, V2(width, 10),
        color=(0.0, 1.0, 0.0, 1.0),
        corner_radius=5.0
    )
    
    # Border
    root.draw_rect(
        pos, V2(100, 10),
        color=TRANSPARENT,
        corner_radius=5.0,
        border_color=WHITE,
        border_width=1.0
    )
```

## See Also

- [API Reference](API_REFERENCE.md#shapes) - Complete API documentation
- [example_shapes.py](../examples/example_shapes.py) - Interactive examples
- [Colors Guide](COLORS.md) - Color system documentation
