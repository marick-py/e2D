# Text Rendering Guide

## Overview

e2D provides efficient text rendering using texture atlases generated from TTF fonts. Supports caching, custom styles, and backgrounds.

## Table of Contents

- [Basic Text Rendering](#basic-text-rendering)
- [Text Styles](#text-styles)
- [Pivot Points](#pivot-points)
- [Cached Labels](#cached-labels)
- [Background Styles](#background-styles)
- [Font Management](#font-management)
- [Performance Tips](#performance-tips)

## Basic Text Rendering

### Simple Text

```python
from e2D import RootEnv, V2

# In your draw() method:
root.print("Hello, World!", V2(10, 10))
```

### With Scale

```python
# Small text
root.print("Small text", V2(10, 10), scale=0.8)

# Large text
root.print("Large text", V2(10, 50), scale=2.0)

# Normal text
root.print("Normal text", V2(10, 100), scale=1.0)
```

## Text Styles

### Pre-defined Styles

```python
from e2D import DEFAULT_16_TEXT_STYLE, MONO_16_TEXT_STYLE

# Default style (Arial)
root.print(
    "Default style",
    V2(10, 10),
    style=DEFAULT_16_TEXT_STYLE
)

# Monospace style (Consolas)
root.print(
    "Monospace style",
    V2(10, 40),
    style=MONO_16_TEXT_STYLE
)
```

Available pre-defined styles:
- `DEFAULT_16_TEXT_STYLE` - Arial 16pt
- `DEFAULT_32_TEXT_STYLE` - Arial 32pt
- `DEFAULT_64_TEXT_STYLE` - Arial 64pt
- `MONO_16_TEXT_STYLE` - Consolas 16pt (monospace)
- `MONO_32_TEXT_STYLE` - Consolas 32pt
- `MONO_64_TEXT_STYLE` - Consolas 64pt

### Custom Styles

```python
from e2D import TextStyle, WHITE, BLACK

# Create custom style
my_style = TextStyle(
    font="arial.ttf",          # Font file
    font_size=24,              # Size in pixels
    color=WHITE,               # Text color
    bg_color=BLACK,            # Background color
    bg_margin=15.0,            # Background padding
    bg_border_radius=10.0      # Rounded background corners
)

root.print("Custom styled text", V2(10, 10), style=my_style)
```

### Style Properties

```python
TextStyle(
    font="arial.ttf",              # Font filename
    font_size=16,                  # Font size in pixels
    color=(1.0, 1.0, 1.0, 1.0),   # RGBA text color
    bg_color=(0.0, 0.0, 0.0, 0.9), # RGBA background color
    bg_margin=15.0,                # Padding (all sides)
    bg_border_radius=15.0          # Corner radius
)
```

## Pivot Points

Control text alignment with pivot points.

### Available Pivots

```python
from e2D import Pivots

# Horizontal alignments
root.print("Left aligned", V2(400, 100), pivot=Pivots.LEFT)
root.print("Centered", V2(400, 130), pivot=Pivots.CENTER)
root.print("Right aligned", V2(400, 160), pivot=Pivots.RIGHT)

# Vertical alignments
root.print("Top", V2(100, 300), pivot=Pivots.TOP_MIDDLE)
root.print("Middle", V2(100, 300), pivot=Pivots.CENTER)
root.print("Bottom", V2(100, 300), pivot=Pivots.BOTTOM_MIDDLE)

# Corners
root.print("Top Left", V2(400, 200), pivot=Pivots.TOP_LEFT)
root.print("Top Right", V2(400, 200), pivot=Pivots.TOP_RIGHT)
root.print("Bottom Left", V2(400, 300), pivot=Pivots.BOTTOM_LEFT)
root.print("Bottom Right", V2(400, 300), pivot=Pivots.BOTTOM_RIGHT)
```

### Pivot Enumeration

```python
Pivots.TOP_LEFT       # 0
Pivots.TOP_MIDDLE     # 1
Pivots.TOP_RIGHT      # 2
Pivots.LEFT           # 3
Pivots.CENTER         # 4
Pivots.RIGHT          # 5
Pivots.BOTTOM_LEFT    # 6
Pivots.BOTTOM_MIDDLE  # 7
Pivots.BOTTOM_RIGHT   # 8
```

## Cached Labels

For text that doesn't change, create cached labels for better performance.

### Creating Cached Labels

```python
class MyEnv(DefEnv):
    def __init__(self, root):
        self.root = root
        
        # Create cached label (once)
        self.title = root.print(
            "Game Title",
            V2(400, 50),
            scale=2.0,
            style=DEFAULT_32_TEXT_STYLE,
            save_cache=True  # Returns TextLabel object
        )
    
    def draw(self):
        # Draw many times efficiently
        self.title.draw()
```

### Benefits

```python
# ❌ Slower - regenerates texture atlas every frame
def draw(self):
    for i in range(100):
        root.print(f"Score: {self.score}", V2(10, 10))

# ✅ Faster - cached texture, single draw call
def __init__(self, root):
    self.score_label = None

def draw(self):
    if self.score_changed:
        self.score_label = root.print(
            f"Score: {self.score}",
            V2(10, 10),
            save_cache=True
        )
        self.score_changed = False
    
    if self.score_label:
        self.score_label.draw()
```

## Background Styles

Add backgrounds to text for better readability.

### Simple Background

```python
style = TextStyle(
    font_size=24,
    color=WHITE,
    bg_color=(0.0, 0.0, 0.0, 0.8)  # Semi-transparent black
)

root.print("Text with background", V2(100, 100), style=style)
```

### Custom Margins

```python
# Uniform margin
style = TextStyle(
    bg_margin=20.0  # 20px on all sides
)

# Per-side margins (top, right, bottom, left)
style = TextStyle(
    bg_margin=(10.0, 20.0, 10.0, 20.0)
)

# Horizontal/vertical margins
style = TextStyle(
    bg_margin=(10.0, 20.0)  # 10px vertical, 20px horizontal
)
```

### Rounded Backgrounds

```python
# Fully rounded
style = TextStyle(
    bg_border_radius=15.0  # All corners
)

# Per-corner radius (top-left, top-right, bottom-right, bottom-left)
style = TextStyle(
    bg_border_radius=(15.0, 5.0, 15.0, 5.0)
)
```

## Font Management

### Using System Fonts

```python
# On Windows
style = TextStyle(font="arial.ttf")
style = TextStyle(font="consola.ttf")  # Consolas
style = TextStyle(font="times.ttf")

# On Linux
style = TextStyle(font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
```

### Text Width Calculation

```python
# Calculate text width before rendering
text = "Hello, World!"
width = root.text_renderer.get_text_width(
    text,
    scale=1.0,
    style=DEFAULT_16_TEXT_STYLE
)

print(f"Text width: {width}px")

# Use for centering
x = (window_width - width) / 2
root.print(text, V2(x, 100))
```

## Performance Tips

### 1. Use Cached Labels for Static Text

```python
# ❌ Slow - rebuilds every frame
def draw(self):
    root.print("Static Text", V2(10, 10))

# ✅ Fast - cached label
def __init__(self, root):
    self.label = root.print("Static Text", V2(10, 10), save_cache=True)

def draw(self):
    self.label.draw()
```

### 2. Cache Dynamic Text When Possible

```python
class ScoreDisplay:
    def __init__(self, root):
        self.root = root
        self.score = 0
        self.last_score = -1
        self.label = None
    
    def update_score(self, new_score):
        if new_score != self.last_score:
            # Only regenerate when score changes
            self.label = self.root.print(
                f"Score: {new_score}",
                V2(10, 10),
                save_cache=True
            )
            self.last_score = new_score
    
    def draw(self):
        if self.label:
            self.label.draw()
```

### 3. Limit Font Sizes

```python
# ❌ Too many font sizes = more atlas generation
style1 = TextStyle(font_size=14)
style2 = TextStyle(font_size=15)
style3 = TextStyle(font_size=16)
# Each size creates a new atlas!

# ✅ Use fewer, consistent sizes
style_small = TextStyle(font_size=12)
style_normal = TextStyle(font_size=16)
style_large = TextStyle(font_size=24)
```

### 4. Avoid Text in Hot Loops

```python
# ❌ Very slow
def draw(self):
    for i in range(1000):
        root.print(f"Item {i}", V2(10, i*20))

# ✅ Batch or cache
def __init__(self, root):
    self.labels = [
        root.print(f"Item {i}", V2(10, i*20), save_cache=True)
        for i in range(1000)
    ]

def draw(self):
    for label in self.labels:
        label.draw()
```

### 5. Use Monospace for Numbers

```python
# Variable-width fonts cause jitter when numbers change
style = TextStyle(font="arial.ttf")
root.print(f"FPS: {fps:.1f}", V2(10, 10), style=style)  # Jitters

# Monospace fonts maintain width
style = TextStyle(font="consola.ttf")
root.print(f"FPS: {fps:.1f}", V2(10, 10), style=style)  # Stable
```

## Examples

### HUD Display

```python
class HUD:
    def __init__(self, root):
        self.root = root
        self.style = TextStyle(
            font="consola.ttf",
            font_size=16,
            color=WHITE,
            bg_color=(0.0, 0.0, 0.0, 0.7),
            bg_margin=10.0,
            bg_border_radius=5.0
        )
    
    def draw(self, health, score, fps):
        # Top-left stats
        root.print(f"Health: {health}", V2(10, 10), style=self.style)
        root.print(f"Score: {score}", V2(10, 35), style=self.style)
        
        # Top-right FPS
        root.print(
            f"FPS: {fps:.1f}",
            V2(790, 10),
            style=self.style,
            pivot=Pivots.TOP_RIGHT
        )
```

### Tooltip System

```python
class Tooltip:
    def __init__(self, root):
        self.root = root
        self.style = TextStyle(
            font_size=14,
            color=WHITE,
            bg_color=(0.1, 0.1, 0.1, 0.95),
            bg_margin=8.0,
            bg_border_radius=4.0
        )
    
    def draw(self, text, mouse_pos):
        # Draw tooltip near mouse
        pos = mouse_pos + V2(15, 15)
        root.print(text, pos, style=self.style, pivot=Pivots.TOP_LEFT)
```

### Title Screen

```python
class TitleScreen:
    def __init__(self, root):
        self.root = root
        
        # Create cached title
        self.title = root.print(
            "MY GAME",
            V2(400, 200),
            scale=3.0,
            style=TextStyle(
                font_size=32,
                color=(1.0, 0.8, 0.0, 1.0),  # Gold
                bg_color=(0.0, 0.0, 0.0, 0.8),
                bg_margin=20.0,
                bg_border_radius=10.0
            ),
            pivot=Pivots.CENTER,
            save_cache=True
        )
        
        self.subtitle = root.print(
            "Press SPACE to start",
            V2(400, 300),
            scale=1.2,
            pivot=Pivots.CENTER,
            save_cache=True
        )
    
    def draw(self):
        self.title.draw()
        self.subtitle.draw()
```

### Debug Console

```python
class DebugConsole:
    def __init__(self, root, max_lines=10):
        self.root = root
        self.max_lines = max_lines
        self.messages = []
        self.style = MONO_16_TEXT_STYLE
    
    def log(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)
    
    def draw(self):
        y = 10
        for msg in self.messages:
            root.print(msg, V2(10, y), scale=0.8, style=self.style)
            y += 18
```

## See Also

- [API Reference](API_REFERENCE.md#text) - Complete API documentation
- [example_text.py](../examples/example_text.py) - Interactive examples
- [Colors Guide](COLORS.md) - Color system for text colors
