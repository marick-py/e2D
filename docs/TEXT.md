# Text Rendering - Fast GPU Text

Hardware-accelerated text rendering with caching and styling.

## Features

- ✅ **GPU-accelerated** SDF (Signed Distance Field) text rendering
- ✅ **Text caching** with TextLabel for reuse
- ✅ **Custom fonts** support (TrueType/OpenType)
- ✅ **Color and styling** options
- ✅ **Automatic kerning** and spacing
- ✅ **Multi-line text** support

## Quick Start

### Immediate Mode

```python
from e2D import RootEnv

class MyApp(DefEnv):
    def draw(self):
        # Draw text immediately
        rootEnv.print("Hello World!", (100, 100))
        
        # With color and scale
        rootEnv.print(
            "Big Red Text",
            position=(100, 200),
            color=(1.0, 0.0, 0.0, 1.0),
            scale=1.5
        )
```

### Cached Mode (Recommended)

```python
class MyApp(DefEnv):
    def __init__(self):
        # Create text labels once
        self.title = rootEnv.create_text(
            "My Game Title",
            position=(960, 100),
            color=(1.0, 1.0, 1.0, 1.0),
            scale=2.0
        )
        
        self.fps_label = rootEnv.create_text(
            "",  # Will update each frame
            position=(10, 10),
            color=(0.0, 1.0, 0.0, 1.0),
            scale=0.5
        )
    
    def draw(self):
        # Draw cached labels (fast)
        self.title.draw()
        
        # Update and draw FPS
        self.fps_label.set_text(f"FPS: {rootEnv.fps:.1f}")
        self.fps_label.draw()
```

## Text Rendering Modes

### 1. Immediate Mode - `rootEnv.print()`
Best for: Quick debugging, one-time messages

```python
def draw(self):
    rootEnv.print("Quick Debug Info", (10, 10))
```

**Pros**: Simple, no setup
**Cons**: Slower, recreates text every frame

### 2. Cached Mode - `TextLabel`
Best for: Most use cases, reusable text

```python
def __init__(self):
    self.label = rootEnv.create_text("Score: 0", (10, 10))

def draw(self):
    self.label.set_text(f"Score: {self.score}")
    self.label.draw()
```

**Pros**: Fast, reusable, can update text
**Cons**: Small memory overhead per label

## API Reference

### Immediate Mode

```python
rootEnv.print(
    text: str,
    position: tuple[float, float],
    color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
    scale: float = 1.0,
    font: str = None  # Use default font if None
)
```

### Cached Mode

```python
# Create label
label = rootEnv.create_text(
    text: str,
    position: tuple[float, float],
    color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
    scale: float = 1.0,
    font: str = None
)

# Update label
label.set_text(new_text: str)
label.set_position(x: float, y: float)
label.set_color(r: float, g: float, b: float, a: float)
label.set_scale(scale: float)

# Draw label
label.draw()

# Get properties
text = label.get_text()
position = label.get_position()
color = label.get_color()
scale = label.get_scale()
```

## Custom Fonts

Load your own TrueType/OpenType fonts:

```python
class MyApp(DefEnv):
    def __init__(self):
        # Load custom font
        rootEnv.load_font("my_font", "path/to/font.ttf")
        
        # Create text with custom font
        self.custom_text = rootEnv.create_text(
            "Custom Font Text",
            position=(100, 100),
            font="my_font",
            scale=1.5
        )
    
    def draw(self):
        self.custom_text.draw()
```

## Examples

### FPS Counter

```python
class FPSCounter(DefEnv):
    def __init__(self):
        self.fps_label = rootEnv.create_text(
            "FPS: 0",
            position=(10, 10),
            color=(0.0, 1.0, 0.0, 1.0),
            scale=0.5
        )
    
    def draw(self):
        # Green if above 30, red if below
        fps = rootEnv.fps
        color = (0.0, 1.0, 0.0, 1.0) if fps > 30 else (1.0, 0.0, 0.0, 1.0)
        
        self.fps_label.set_text(f"FPS: {fps:.1f}")
        self.fps_label.set_color(*color)
        self.fps_label.draw()
```

### Score Display

```python
class ScoreUI(DefEnv):
    def __init__(self):
        self.score = 0
        self.label = rootEnv.create_text(
            "Score: 0",
            position=(1700, 50),
            color=(1.0, 1.0, 0.0, 1.0),
            scale=1.0
        )
    
    def add_points(self, points):
        self.score += points
        self.label.set_text(f"Score: {self.score}")
    
    def draw(self):
        self.label.draw()
```

### Multi-line Text

```python
class MultilineText(DefEnv):
    def __init__(self):
        lines = [
            "Welcome to e2D!",
            "Press SPACE to start",
            "Press ESC to quit"
        ]
        
        self.labels = []
        for i, line in enumerate(lines):
            label = rootEnv.create_text(
                line,
                position=(960, 400 + i * 40),
                color=(1.0, 1.0, 1.0, 1.0),
                scale=0.8
            )
            self.labels.append(label)
    
    def draw(self):
        for label in self.labels:
            label.draw()
```

### Animated Text

```python
class AnimatedText(DefEnv):
    def __init__(self):
        self.label = rootEnv.create_text(
            "Pulse Effect",
            position=(960, 540),
            color=(1.0, 0.5, 0.0, 1.0),
            scale=1.0
        )
        self.time = 0.0
    
    def update(self):
        self.time += rootEnv.delta
        
        # Pulse scale
        scale = 1.0 + 0.3 * math.sin(self.time * 3.0)
        self.label.set_scale(scale)
        
        # Rainbow color
        hue = (self.time * 0.5) % 1.0
        color = Color.from_hsv(hue, 1.0, 1.0).to_rgba()
        self.label.set_color(*color)
    
    def draw(self):
        self.label.draw()
```

### Debug Overlay

```python
class DebugOverlay(DefEnv):
    def __init__(self):
        self.labels = {
            "fps": rootEnv.create_text("", (10, 10), scale=0.4),
            "delta": rootEnv.create_text("", (10, 30), scale=0.4),
            "mouse": rootEnv.create_text("", (10, 50), scale=0.4),
        }
    
    def draw(self):
        # Update and draw debug info
        self.labels["fps"].set_text(f"FPS: {rootEnv.fps:.1f}")
        self.labels["delta"].set_text(f"Delta: {rootEnv.delta*1000:.2f}ms")
        self.labels["mouse"].set_text(f"Mouse: {rootEnv.mouse_pos}")
        
        for label in self.labels.values():
            label.draw()
```

### Typewriter Effect

```python
class TypewriterText(DefEnv):
    def __init__(self):
        self.full_text = "This text appears character by character..."
        self.visible_text = ""
        self.char_index = 0
        self.char_timer = 0.0
        self.char_delay = 0.1  # seconds per character
        
        self.label = rootEnv.create_text(
            "",
            position=(100, 540),
            color=(1.0, 1.0, 1.0, 1.0),
            scale=0.8
        )
    
    def update(self):
        if self.char_index < len(self.full_text):
            self.char_timer += rootEnv.delta
            
            if self.char_timer >= self.char_delay:
                self.char_timer = 0.0
                self.char_index += 1
                self.visible_text = self.full_text[:self.char_index]
                self.label.set_text(self.visible_text)
    
    def draw(self):
        self.label.draw()
```

## Performance Tips

1. **Use TextLabel** for text that appears multiple frames
2. **Update only when needed** - don't `set_text()` every frame if unchanged
3. **Cache labels** - create once, reuse many times
4. **Batch similar text** - draw all text at similar scales together
5. **Avoid excessive string formatting** - format strings only when they change

## Common Patterns

### Score with Shadow

```python
def __init__(self):
    # Shadow (black, slightly offset)
    self.shadow = rootEnv.create_text(
        "Score: 0",
        position=(102, 52),
        color=(0.0, 0.0, 0.0, 0.5),
        scale=1.0
    )
    
    # Main text (white)
    self.score_text = rootEnv.create_text(
        "Score: 0",
        position=(100, 50),
        color=(1.0, 1.0, 1.0, 1.0),
        scale=1.0
    )

def update_score(self, score):
    text = f"Score: {score}"
    self.shadow.set_text(text)
    self.score_text.set_text(text)

def draw(self):
    self.shadow.draw()      # Draw shadow first
    self.score_text.draw()  # Then main text
```

### Centered Text

```python
def create_centered_text(text, y_pos):
    # Note: Centering requires knowing text width
    # Approximate centering:
    estimated_width = len(text) * 20  # Rough estimate
    x_pos = (1920 - estimated_width) / 2
    
    return rootEnv.create_text(
        text,
        position=(x_pos, y_pos),
        scale=1.0
    )
```

### Conditional Display

```python
class ConditionalText(DefEnv):
    def __init__(self):
        self.warning = rootEnv.create_text(
            "WARNING!",
            position=(960, 100),
            color=(1.0, 0.0, 0.0, 1.0),
            scale=1.5
        )
        self.show_warning = False
    
    def draw(self):
        if self.show_warning:
            self.warning.draw()
```

## Text with Colors

```python
class ColoredText(DefEnv):
    def __init__(self):
        # Pre-defined colors from e2D
        self.texts = [
            rootEnv.create_text("Red", (100, 100), color=Color.RED.to_rgba()),
            rootEnv.create_text("Green", (100, 150), color=Color.GREEN.to_rgba()),
            rootEnv.create_text("Blue", (100, 200), color=Color.BLUE.to_rgba()),
            rootEnv.create_text("Yellow", (100, 250), color=Color.YELLOW.to_rgba()),
        ]
    
    def draw(self):
        for text in self.texts:
            text.draw()
```

---

[← Back to README](../README.md)
