# Quick Reference - e2D API

Complete API reference based on type stubs.

## Installation

```bash
pip install e2D          # Basic
pip install e2D[rec]     # With recording
pip install e2D[all]     # Everything
```

## Basic Usage

```python
from e2D import RootEnv, DefEnv, Vector2D, Color, KeyState
from e2D.devices import Keys

class MyApp(DefEnv):
    def __init__(self):
        self.batch = rootEnv.create_circle_batch(max_shapes=1000)
    
    def update(self):
        if rootEnv.keyboard.get_key(Keys.SPACE, KeyState.JUST_PRESSED):
            print("Space!")
    
    def draw(self):
        rootEnv.draw_circle((100, 100), 50, color=(1,0,0,1))
        fps = 1.0 / rootEnv.delta if rootEnv.delta > 0 else 0
        rootEnv.print(f"FPS: {fps:.0f}", (10, 10), scale=0.5)

rootEnv = RootEnv(window_size=(1920, 1080), target_fps=60)
rootEnv.init(MyApp()).loop()
```

## RootEnv

### Constructor
```python
RootEnv(
    window_size=(1920, 1080),
    target_fps=60,
    vsync=True,
    version=(4, 3),
    monitor=None
)
```

### Properties
- `window_size` - (width, height)
- `window_size_f` - (width, height) as floats
- `delta` - Frame time in seconds
- `runtime` - Total elapsed time
- `ctx` - ModernGL context
- `window` - GLFW window
- `keyboard` - Keyboard handler
- `mouse` - Mouse handler

### Methods
- `init(env: DefEnv)` - Initialize
- `loop()` - Start main loop
- `init_rec(fps, draw_on_screen, path)` - Enable recording

### Drawing
```python
# Text
print(text, position, scale=1.0, style=DEFAULT_TEXT_STYLE, pivot=Pivots.TOP_LEFT, save_cache=False)

# Shapes (immediate)
draw_circle(center, radius, color=WHITE, border_color=TRANSPARENT, border_width=0, antialiasing=1.0)
draw_rect(position, size, color=WHITE, corner_radius=0, border_color=TRANSPARENT, border_width=0, antialiasing=1.0, rotation=0)
draw_line(start, end, width=1.0, color=WHITE)
draw_lines(points, width=1.0, color=WHITE, closed=False)

# Shapes (cached)
create_circle(center, radius, **kwargs) -> ShapeLabel
create_rect(position, size, **kwargs) -> ShapeLabel
create_line(start, end, **kwargs) -> ShapeLabel
create_lines(points, **kwargs) -> ShapeLabel

# Shapes (batched)
create_circle_batch(max_shapes=10000) -> InstancedShapeBatch
create_rect_batch(max_shapes=10000) -> InstancedShapeBatch
create_line_batch(max_shapes=10000) -> InstancedShapeBatch
```

## DefEnv

```python
class MyApp(DefEnv):
    def __init__(self):
        """Called once at start"""
        pass
    
    def update(self):
        """Called every frame before draw"""
        pass
    
    def draw(self):
        """Called every frame for rendering"""
        pass
    
    def on_resize(self, width, height):
        """Optional: called on window resize"""
        pass
```

## Input

### Keyboard
```python
from e2D import KeyState, Keys

# Check key state
rootEnv.keyboard.get_key(Keys.SPACE, KeyState.PRESSED)       # Held
rootEnv.keyboard.get_key(Keys.SPACE, KeyState.JUST_PRESSED)  # Clicked
rootEnv.keyboard.get_key(Keys.SPACE, KeyState.JUST_RELEASED) # Released
```

### Mouse
```python
# Position
x, y = rootEnv.mouse.position

# Buttons (0=left, 1=right, 2=middle)
rootEnv.mouse.get_button(0, KeyState.PRESSED)
rootEnv.mouse.get_button(0, KeyState.JUST_PRESSED)

# Scroll (tuple of x, y scroll)
sx, sy = rootEnv.mouse.scroll
```

## Vector2D

### Creation
```python
v = Vector2D(3.0, 4.0)
v = Vector2D.zero()
v = Vector2D.one()
v = Vector2D.up()       # (0, 1)
v = Vector2D.down()     # (0, -1)
v = Vector2D.left()     # (-1, 0)
v = Vector2D.right()    # (1, 0)
v = Vector2D.from_angle(1.57, length=5.0)
v = Vector2D.random(-10, 10)
```

### Properties
```python
v.x, v.y              # Components
v.length              # Magnitude
v.length_sqrd         # Squared magnitude (faster)
v.angle               # Angle in radians
```

### Methods (In-place - Fast!)
```python
v.iadd(other)         # v += other
v.isub(other)         # v -= other
v.imul(scalar)        # v *= scalar
v.idiv(scalar)        # v /= scalar
v.normalize()         # Normalize in-place
v.irotate(angle)      # Rotate in-place
v.clamp_inplace(min_vec, max_vec)
```

### Methods (Return New)
```python
v2 = v.add(other)
v2 = v.sub(other)
v2 = v.mul(scalar)
v2 = v.normalized()
v2 = v.rotate(angle)
v2 = v.lerp(other, t)
v2 = v.clamp(min_vec, max_vec)
v2 = v.projection(other)
v2 = v.reflection(normal)
```

### Math
```python
dot = v.dot_product(other)
dist = v.distance_to(other)
angle = v.angle_to(other)
```

### Operators
```python
v3 = v1 + v2
v3 = v1 - v2
v2 = v1 * 2.0
v2 = v1 / 2.0
v1 += v2
v1 -= v2
v1 *= 2.0
```

### Batch Operations (10-500x faster!)
```python
from e2D import batch_add_inplace, vectors_to_array, array_to_vectors

vectors = [Vector2D.random(-10, 10) for _ in range(10000)]
displacement = Vector2D(1.0, 0.5)

# Fast batch operations
batch_add_inplace(vectors, displacement)
batch_scale_inplace(vectors, 0.5)
batch_normalize_inplace(vectors)

# Convert to numpy
arr = vectors_to_array(vectors)  # -> np.ndarray shape (N, 2)

# Convert from numpy
vectors = array_to_vectors(arr)  # -> List[Vector2D]
```

## Color

### Creation
```python
c = Color(1.0, 0.0, 0.0, 1.0)
c = Color.from_rgb(1.0, 0.0, 0.0)
c = Color.from_rgb255(255, 0, 0)
c = Color.from_hex("#FF0000")
c = Color.from_hsv(0.0, 1.0, 1.0)
c = Color.from_gray(0.5)
```

### Pre-defined Colors
```python
from e2D import WHITE, BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW
from e2D import ORANGE, PURPLE, PINK, TRANSPARENT
from e2D.color_defs import MD_BLUE, PASTEL_PINK, NEON_GREEN  # 80+ more
```

### Properties
```python
c.r, c.g, c.b, c.a    # Components (0-1)
```

### Conversion
```python
c.to_rgba()           # (r, g, b, a) floats
c.to_rgb()            # (r, g, b) floats
c.to_rgba255()        # (r, g, b, a) ints 0-255
c.to_hex()            # "#RRGGBB"
c.to_hsv()            # (h, s, v)
c.to_array()          # np.ndarray
```

### Operations
```python
c2 = c.with_alpha(0.5)
c2 = c.lighten(0.2)
c2 = c.darken(0.2)
c2 = c.saturate(0.1)
c2 = c.desaturate(0.1)
c2 = c.rotate_hue(120)  # Degrees
c2 = c.invert()
c2 = c.grayscale()
c2 = c.lerp(other_color, 0.5)
```

## Shapes

### Immediate Mode
```python
rootEnv.draw_circle((100, 100), 50, color=(1,0,0,1))
rootEnv.draw_rect((200, 100), (80, 60), color=(0,1,0,1))
rootEnv.draw_line((300, 100), (400, 200), width=3, color=(0,0,1,1))
```

### Cached Mode
```python
circle = rootEnv.create_circle((100, 100), 50, color=(1,0,0,1))
circle.draw()
```

### Batched Mode (Best Performance)
```python
batch = rootEnv.create_circle_batch(max_shapes=10000)

# Add shapes
for i in range(1000):
    batch.add_circle(
        center=(random.random()*1920, random.random()*1080),
        radius=10,
        color=(random.random(), random.random(), random.random(), 1.0)
    )

# Draw all in one call
batch.flush()

# Clear for next frame
batch.clear()

# Numpy version (10-50x faster)
centers = np.random.rand(1000, 2) * [1920, 1080]
radii = np.full(1000, 10.0, dtype=np.float32)
colors = np.random.rand(1000, 4).astype(np.float32)
batch.add_circles_numpy(centers, radii, colors)
```

## Text

### Immediate
```python
rootEnv.print("Hello", (100, 100), scale=1.0)
```

### Styled
```python
from e2D.text_renderer import TextStyle

style = TextStyle(
    font="arial.ttf",
    font_size=32,
    color=(1, 1, 1, 1),
    bg_color=(0, 0, 0, 0.9),
    bg_margin=15.0,
    bg_border_radius=15.0
)
rootEnv.print("Styled Text", (100, 100), style=style)
```

### Cached
```python
label = rootEnv.print("Score: 0", (10, 10), save_cache=True)
# Later:
label.draw()
```

## Recording (Optional - requires pip install e2D[rec])

```python
rootEnv = RootEnv(window_size=(1920, 1080))
rootEnv.init_rec(fps=30, draw_on_screen=True, path='output.mp4')
rootEnv.init(MyApp()).loop()
```

**Controls:**
- `F9` - Pause/Resume
- `F10` - Restart (clear buffer)
- `F12` - Screenshot

---

For more details see [README.md](../README.md)
