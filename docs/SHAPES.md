# Shape Rendering - GPU-Accelerated 2D Shapes

High-performance shape rendering using SDF (Signed Distance Functions) and GPU instancing.

## Features

- ✅ **GPU-accelerated** rendering with SDF shaders
- ✅ **Instanced drawing** - 10,000+ shapes in one draw call
- ✅ **Anti-aliased** edges for smooth graphics
- ✅ **Rounded corners** on rectangles
- ✅ **Borders and fills** with independent colors
- ✅ **Rotation support** for all shapes

## Rendering Modes

### 1. Immediate Mode
Draw shapes directly (simple, good for few shapes):

```python
from e2D import RootEnv

class MyApp(DefEnv):
    def draw(self):
        # Draw shapes immediately
        rootEnv.draw_circle(
            center=(100, 100),
            radius=50,
            color=(1.0, 0.0, 0.0, 1.0),
            border_color=(1.0, 1.0, 1.0, 1.0),
            border_width=3.0
        )
        
        rootEnv.draw_rect(
            position=(200, 100),
            size=(100, 80),
            color=(0.0, 1.0, 0.0, 1.0),
            rotation=0.785,  # 45° in radians
            corner_radius=10.0
        )
        
        rootEnv.draw_line(
            start=(300, 100),
            end=(400, 200),
            width=3.0,
            color=(0.0, 0.0, 1.0, 1.0)
        )
```

### 2. Cached Mode
Pre-create shapes for efficient reuse:

```python
class MyApp(DefEnv):
    def __init__(self):
        # Create shapes once
        self.circle = rootEnv.create_circle(
            center=(100, 100),
            radius=50,
            color=(1.0, 0.0, 0.0, 1.0)
        )
        
        self.rect = rootEnv.create_rect(
            position=(200, 100),
            size=(100, 80),
            color=(0.0, 1.0, 0.0, 1.0)
        )
    
    def draw(self):
        # Draw cached shapes (fast)
        self.circle.draw()
        self.rect.draw()
```

### 3. Batched Mode (Best Performance)
Draw thousands of shapes in one call:

```python
class MyApp(DefEnv):
    def __init__(self):
        # Create batches
        self.circle_batch = rootEnv.create_circle_batch(max_shapes=10000)
        self.rect_batch = rootEnv.create_rect_batch(max_shapes=1000)
    
    def draw(self):
        # Clear previous frame
        self.circle_batch.clear()
        
        # Add thousands of circles
        for i in range(10000):
            self.circle_batch.add_circle(
                center=(random.uniform(0, 1920), random.uniform(0, 1080)),
                radius=random.uniform(5, 20),
                color=(random.random(), random.random(), random.random(), 1.0)
            )
        
        # Draw ALL circles in ONE draw call!
        self.circle_batch.flush()
```

## Shapes Reference

### Circles

```python
# Immediate
rootEnv.draw_circle(
    center=(x, y),
    radius=50,
    color=(1.0, 0.0, 0.0, 1.0),      # Fill color
    border_color=(1.0, 1.0, 1.0, 1.0),  # Border color
    border_width=3.0,                # Border thickness
    antialiasing=1.0                 # Edge smoothness
)

# Cached
circle = rootEnv.create_circle(center, radius, color=...)
circle.draw()

# Batched
batch = rootEnv.create_circle_batch(max_shapes=10000)
batch.add_circle(center, radius, color=...)
batch.flush()

# Batch with numpy (10-50x faster for many circles)
centers = np.array([[x1, y1], [x2, y2], ...], dtype=np.float32)
radii = np.array([r1, r2, ...], dtype=np.float32)
colors = np.array([[r, g, b, a], ...], dtype=np.float32)
batch.add_circles_numpy(centers, radii, colors)
```

### Rectangles

```python
# Immediate
rootEnv.draw_rect(
    position=(x, y),     # Top-left corner
    size=(width, height),
    color=(0.0, 1.0, 0.0, 1.0),
    rotation=0.785,      # Radians
    corner_radius=10.0,  # Rounded corners
    border_color=(1.0, 1.0, 1.0, 1.0),
    border_width=2.0
)

# Cached
rect = rootEnv.create_rect(position, size, color=...)
rect.draw()

# Batched
batch = rootEnv.create_rect_batch(max_shapes=1000)
batch.add_rect(
    center=(cx, cy),  # Note: batch uses center, not position
    size=(w, h),
    color=...,
    corner_radius=10.0,
    rotation=0.785
)
batch.flush()

# Batch with numpy
centers = np.array([[cx1, cy1], [cx2, cy2], ...], dtype=np.float32)
sizes = np.array([[w1, h1], [w2, h2], ...], dtype=np.float32)
colors = np.array([[r, g, b, a], ...], dtype=np.float32)
batch.add_rects_numpy(centers, sizes, colors)
```

### Lines

```python
# Single line
rootEnv.draw_line(
    start=(x1, y1),
    end=(x2, y2),
    width=3.0,
    color=(1.0, 1.0, 0.0, 1.0)
)

# Polyline (connected segments)
points = [(x1, y1), (x2, y2), (x3, y3), ...]
rootEnv.draw_lines(
    points=points,
    width=2.0,
    color=(1.0, 0.0, 1.0, 1.0),
    closed=False  # True to connect last to first
)

# Cached polyline
line = rootEnv.create_lines(points, width=2.0, color=...)
line.draw()

# Batched lines
batch = rootEnv.create_line_batch(max_shapes=1000)
batch.add_line(start, end, width=3.0, color=...)
batch.flush()
```

## Advanced Examples

### Particle System

```python
class ParticleSystem(DefEnv):
    def __init__(self):
        self.batch = rootEnv.create_circle_batch(max_shapes=10000)
        self.positions = [Vector2D.random(0, 1920) for _ in range(10000)]
        self.velocities = [Vector2D.random(-100, 100) for _ in range(10000)]
        self.colors = [(random.random(), random.random(), 1.0, 0.8) 
                       for _ in range(10000)]
    
    def update(self):
        dt = rootEnv.delta
        for i in range(len(self.positions)):
            self.positions[i].iadd(self.velocities[i].mul(dt))
    
    def draw(self):
        self.batch.clear()
        
        # Vectorized addition (ultra-fast)
        centers = np.array([p.to_tuple() for p in self.positions], 
                          dtype=np.float32)
        radii = np.full(len(self.positions), 5.0, dtype=np.float32)
        colors = np.array(self.colors, dtype=np.float32)
        
        self.batch.add_circles_numpy(centers, radii, colors)
        self.batch.flush()  # 10,000 circles in one draw call!
```

### UI Elements

```python
class Button(DefEnv):
    def __init__(self):
        self.button_bg = rootEnv.create_rect(
            position=(100, 100),
            size=(200, 60),
            color=(0.2, 0.5, 0.8, 1.0),
            corner_radius=10.0,
            border_color=(1.0, 1.0, 1.0, 1.0),
            border_width=2.0
        )
    
    def draw(self):
        self.button_bg.draw()
        rootEnv.print("Click Me", (200, 130), scale=0.5)
```

### Grid Visualization

```python
class Grid(DefEnv):
    def __init__(self):
        self.batch = rootEnv.create_rect_batch(max_shapes=1000)
    
    def draw(self):
        self.batch.clear()
        
        # Draw 20x20 grid
        for i in range(20):
            for j in range(20):
                x = 50 + i * 30
                y = 50 + j * 30
                hue = (i + j) * 0.05
                color = Color.from_hsv(hue, 0.8, 1.0).to_rgba()
                
                self.batch.add_rect(
                    center=(x, y),
                    size=(25, 25),
                    color=color,
                    corner_radius=3.0
                )
        
        self.batch.flush()  # 400 rectangles in one draw call!
```

### Connection Graph

```python
class NetworkGraph(DefEnv):
    def __init__(self):
        self.node_batch = rootEnv.create_circle_batch(max_shapes=100)
        self.line_batch = rootEnv.create_line_batch(max_shapes=1000)
        self.nodes = [Vector2D.random(100, 1820) for _ in range(50)]
    
    def draw(self):
        # Draw connections
        self.line_batch.clear()
        for i, node1 in enumerate(self.nodes):
            for j, node2 in enumerate(self.nodes[i+1:], start=i+1):
                dist = node1.distance_to(node2)
                if dist < 200:
                    alpha = 1.0 - dist / 200.0
                    self.line_batch.add_line(
                        start=node1.to_tuple(),
                        end=node2.to_tuple(),
                        width=1.0,
                        color=(0.5, 0.8, 1.0, alpha)
                    )
        self.line_batch.flush()
        
        # Draw nodes
        self.node_batch.clear()
        for node in self.nodes:
            self.node_batch.add_circle(
                center=node.to_tuple(),
                radius=10,
                color=(1.0, 0.2, 0.2, 1.0),
                border_color=(1.0, 1.0, 1.0, 1.0),
                border_width=2.0
            )
        self.node_batch.flush()
```

## Performance Tips

1. **Use batches** for more than ~10 shapes
2. **Use numpy arrays** with `add_circles_numpy()` for best performance
3. **Reuse batches** - just `clear()` and refill each frame
4. **Pre-allocate** batch sizes appropriately
5. **Group by type** - separate batches for circles, rects, lines
6. **Minimize state changes** - draw all circles, then all rects

## API Reference

### Immediate Mode
- `rootEnv.draw_circle(center, radius, **kwargs)`
- `rootEnv.draw_rect(position, size, **kwargs)`
- `rootEnv.draw_line(start, end, **kwargs)`
- `rootEnv.draw_lines(points, **kwargs)`

### Cached Mode
- `rootEnv.create_circle(center, radius, **kwargs) -> ShapeLabel`
- `rootEnv.create_rect(position, size, **kwargs) -> ShapeLabel`
- `rootEnv.create_line(start, end, **kwargs) -> ShapeLabel`
- `rootEnv.create_lines(points, **kwargs) -> ShapeLabel`
- `shape.draw()` - Draw cached shape

### Batched Mode
- `rootEnv.create_circle_batch(max_shapes) -> InstancedShapeBatch`
- `rootEnv.create_rect_batch(max_shapes) -> InstancedShapeBatch`
- `rootEnv.create_line_batch(max_shapes) -> InstancedShapeBatch`
- `batch.add_circle(center, radius, **kwargs)`
- `batch.add_circles_numpy(centers, radii, colors, ...)`
- `batch.add_rect(center, size, **kwargs)`
- `batch.add_rects_numpy(centers, sizes, colors, ...)`
- `batch.add_line(start, end, width, color)`
- `batch.add_lines_numpy(starts, ends, widths, colors)`
- `batch.flush()` - Draw all shapes
- `batch.clear()` - Clear batch

---

[← Back to README](../README.md)
