# Color System Guide

## Overview

e2D provides a comprehensive color system with 80+ pre-defined colors, color manipulation, and support for multiple color formats. All colors use RGBA float format (0.0-1.0) optimized for GPU rendering.

## Table of Contents

- [Color Formats](#color-formats)
- [Creating Colors](#creating-colors)
- [Pre-defined Colors](#pre-defined-colors)
- [Color Operations](#color-operations)
- [Color Conversion](#color-conversion)
- [Utility Functions](#utility-functions)

## Color Formats

e2D supports multiple color formats through the `ColorType`:

```python
from e2D import Color

# Tuple format (RGBA 0.0-1.0)
color = (1.0, 0.0, 0.0, 1.0)  # Red

# Color object
color = Color(1.0, 0.0, 0.0, 1.0)  # Red

# Pre-defined constants
from e2D import RED, BLUE, GREEN
color = RED  # (1.0, 0.0, 0.0, 1.0)
```

## Creating Colors

### From RGBA Float (0.0-1.0)

```python
from e2D import Color

# Standard format (GPU-friendly)
color = Color(1.0, 0.0, 0.0, 1.0)  # Red

# RGB only (alpha defaults to 1.0)
color = Color.from_rgb(1.0, 0.5, 0.0)  # Orange
```

### From RGB 255

```python
# From 0-255 values
color = Color.from_rgb255(255, 128, 0)  # Orange

# With alpha
color = Color.from_rgba255(255, 0, 0, 128)  # Semi-transparent red
```

### From Hex String

```python
# HTML/CSS hex format
color = Color.from_hex("#FF0000")  # Red
color = Color.from_hex("FF0000")   # Also works without #
color = Color.from_hex("#FF0000FF")  # With alpha

# Web colors
color = Color.from_hex("#1E90FF")  # Dodger Blue
```

### From HSV/HLS

```python
# HSV (Hue, Saturation, Value)
color = Color.from_hsv(0.0, 1.0, 1.0)  # Red
color = Color.from_hsv(0.5, 1.0, 1.0)  # Cyan
color = Color.from_hsv(0.33, 1.0, 1.0)  # Green

# HLS (Hue, Lightness, Saturation)
color = Color.from_hls(0.0, 0.5, 1.0)  # Red
```

### Grayscale

```python
# Create grayscale color
color = Color.from_gray(0.5)  # 50% gray
color = Color.from_gray(0.0)  # Black
color = Color.from_gray(1.0)  # White
```

### Quick Constructors

```python
# Pre-defined color factory methods
red = Color.red()
green = Color.green()
blue = Color.blue()
white = Color.white()
black = Color.black()
yellow = Color.yellow()
cyan = Color.cyan()
magenta = Color.magenta()
orange = Color.orange()
purple = Color.purple()
pink = Color.pink()
gray = Color.gray(0.5)  # With level parameter
```

## Pre-defined Colors

### Basic Colors

```python
from e2D import (
    TRANSPARENT, WHITE, BLACK,
    RED, GREEN, BLUE,
    CYAN, MAGENTA, YELLOW
)

# Usage
root.draw_circle(V2(100, 100), 30, color=RED)
root.draw_rect(V2(200, 100), V2(60, 60), color=BLUE)
```

### Extended Colors

```python
from e2D.color_defs import (
    ORANGE, PURPLE, PINK, BROWN,
    LIME, TEAL, NAVY, MAROON,
    OLIVE, SILVER, GOLD, INDIGO,
    VIOLET, TURQUOISE, CORAL
)
```

### Gray Shades

```python
from e2D.color_defs import (
    GRAY10, GRAY20, GRAY30, GRAY40, GRAY50,
    GRAY60, GRAY70, GRAY80, GRAY90
)

# 10 different gray levels
root.draw_circle(V2(100, 100), 30, color=GRAY50)
```

### Material Design Colors

```python
from e2D.color_defs import (
    MD_RED, MD_PINK, MD_PURPLE, MD_DEEP_PURPLE,
    MD_INDIGO, MD_BLUE, MD_LIGHT_BLUE, MD_CYAN,
    MD_TEAL, MD_GREEN, MD_LIGHT_GREEN, MD_LIME,
    MD_YELLOW, MD_AMBER, MD_ORANGE, MD_DEEP_ORANGE,
    MD_BROWN, MD_GREY, MD_BLUE_GREY
)
```

### Pastel Colors

```python
from e2D.color_defs import (
    PASTEL_RED, PASTEL_ORANGE, PASTEL_YELLOW,
    PASTEL_GREEN, PASTEL_CYAN, PASTEL_BLUE,
    PASTEL_PURPLE, PASTEL_PINK
)
```

### Neon Colors

```python
from e2D.color_defs import (
    NEON_RED, NEON_ORANGE, NEON_YELLOW,
    NEON_GREEN, NEON_CYAN, NEON_BLUE,
    NEON_PURPLE, NEON_PINK
)
```

### UI Colors

```python
from e2D.color_defs import (
    UI_SUCCESS,   # Green
    UI_WARNING,   # Amber
    UI_ERROR,     # Red
    UI_INFO,      # Blue
    UI_DISABLED   # Grey
)

# Usage for feedback
if error:
    color = UI_ERROR
elif warning:
    color = UI_WARNING
else:
    color = UI_SUCCESS
```

### Color Lookup

```python
from e2D import get_color, has_color

# Get color by name
red = get_color("red")
blue = get_color("blue")
material_blue = get_color("md_blue")

# Check if color exists
if has_color("custom_color"):
    color = get_color("custom_color")
```

## Color Operations

### Lightening and Darkening

```python
color = Color.red()

# Lighten by percentage
lighter = color.lighten(0.2)  # 20% lighter

# Darken by percentage
darker = color.darken(0.3)  # 30% darker

# Chain operations
color = Color.blue().lighten(0.1).darken(0.05)
```

### Interpolation (Lerp)

```python
red = Color.red()
blue = Color.blue()

# Interpolate between colors
purple = red.lerp(blue, 0.5)  # 50% blend

# Smooth transitions
for t in range(0, 101, 10):
    color = red.lerp(blue, t / 100.0)
    print(f"t={t}%: {color.to_hex()}")
```

### Saturation and Brightness

```python
color = Color.red()

# Adjust saturation
desaturated = color.with_saturation(0.5)
fully_saturated = color.with_saturation(1.0)

# Adjust brightness
brighter = color.with_brightness(0.8)
darker = color.with_brightness(0.3)
```

### Color Inversion

```python
color = Color(1.0, 0.0, 0.0, 1.0)  # Red

# Invert RGB (alpha unchanged)
inverted = color.invert()  # Cyan
print(inverted.to_hex())  # #00FFFF
```

### Hue Rotation

```python
color = Color.red()

# Rotate hue by degrees
rotated = color.rotate_hue(120)  # Red -> Green
rotated = color.rotate_hue(240)  # Red -> Blue

# Complementary color
complement = color.rotate_hue(180)
```

### Alpha Channel

```python
color = Color.red()

# Set opacity
semi_transparent = color.with_alpha(0.5)
fully_transparent = color.with_alpha(0.0)
fully_opaque = color.with_alpha(1.0)

# Adjust opacity
faded = color.fade(0.3)  # Multiply alpha by 0.3
```

## Color Conversion

### To Tuple

```python
color = Color.red()

# RGBA tuple (0.0-1.0)
rgba = color.to_rgba()  # (1.0, 0.0, 0.0, 1.0)

# RGB tuple (0.0-1.0)
rgb = color.to_rgb()  # (1.0, 0.0, 0.0)
```

### To 255 Format

```python
color = Color.red()

# RGB 255
rgb255 = color.to_rgb255()  # (255, 0, 0)

# RGBA 255
rgba255 = color.to_rgba255()  # (255, 0, 0, 255)
```

### To Hex

```python
color = Color.red()

# Without alpha
hex_color = color.to_hex()  # "#FF0000"

# With alpha
hex_color = color.to_hex(include_alpha=True)  # "#FF0000FF"
```

### To HSV/HLS

```python
color = Color.red()

# HSV tuple
hsv = color.to_hsv()  # (0.0, 1.0, 1.0)

# HLS tuple
hls = color.to_hls()  # (0.0, 0.5, 1.0)
```

## Utility Functions

### normalize_color

Convert any color format to RGBA tuple:

```python
from e2D import normalize_color, Color, RED

# From Color object
rgba = normalize_color(Color.red())  # (1.0, 0.0, 0.0, 1.0)

# From tuple
rgba = normalize_color((1.0, 0.0, 0.0, 1.0))  # (1.0, 0.0, 0.0, 1.0)

# From constant
rgba = normalize_color(RED)  # (1.0, 0.0, 0.0, 1.0)

# From hex string
rgba = normalize_color("#FF0000")  # (1.0, 0.0, 0.0, 1.0)

# From grayscale
rgba = normalize_color(0.5)  # (0.5, 0.5, 0.5, 1.0)
```

### lerp_colors

Interpolate between two colors:

```python
from e2D import lerp_colors, RED, BLUE

# Simple interpolation
purple = lerp_colors(RED, BLUE, 0.5)

# Smooth transitions
colors = [lerp_colors(RED, BLUE, t/10) for t in range(11)]
```

### gradient

Generate color gradients:

```python
from e2D import gradient, RED, GREEN, BLUE

# Two color gradient
colors = gradient([RED, BLUE], steps=10)

# Multi-color gradient
colors = gradient([RED, GREEN, BLUE], steps=20)

# Use for smooth color transitions
for i, color in enumerate(colors):
    root.draw_circle(V2(10 + i*15, 100), 5, color=color)
```

### batch_colors_to_array

Convert colors to numpy array for GPU:

```python
from e2D import batch_colors_to_array
import numpy as np

colors = [RED, GREEN, BLUE, YELLOW]

# Convert to GPU-ready array
color_array = batch_colors_to_array(colors)
# Returns: ndarray shape (4, 4) dtype float32

# Upload to GPU
vbo.write(color_array.tobytes())
```

## Examples

### Color Palette

```python
class ColorPalette:
    def __init__(self):
        self.colors = [
            Color.red(),
            Color.orange(),
            Color.yellow(),
            Color.green(),
            Color.cyan(),
            Color.blue(),
            Color.purple()
        ]
    
    def get_rainbow(self, index):
        return self.colors[index % len(self.colors)]
```

### Animated Color

```python
class AnimatedColor:
    def __init__(self, start_color, end_color, duration):
        self.start = start_color
        self.end = end_color
        self.duration = duration
        self.time = 0.0
    
    def update(self, dt):
        self.time += dt
        if self.time >= self.duration:
            self.time = 0.0
    
    def get_current_color(self):
        t = self.time / self.duration
        return self.start.lerp(self.end, t)
```

### Health Bar Colors

```python
def get_health_color(health, max_health):
    percentage = health / max_health
    
    if percentage > 0.6:
        return UI_SUCCESS  # Green
    elif percentage > 0.3:
        return UI_WARNING  # Orange
    else:
        return UI_ERROR  # Red

def draw_health_bar(root, pos, health, max_health):
    color = get_health_color(health, max_health)
    width = (health / max_health) * 100
    root.draw_rect(pos, V2(width, 10), color=color)
```

### Color Cycling

```python
class ColorCycler:
    def __init__(self, speed=1.0):
        self.hue = 0.0
        self.speed = speed
    
    def update(self, dt):
        self.hue += self.speed * dt
        if self.hue > 1.0:
            self.hue -= 1.0
    
    def get_color(self):
        return Color.from_hsv(self.hue, 1.0, 1.0)
```

### Theme System

```python
class Theme:
    def __init__(self, name, colors):
        self.name = name
        self.primary = colors['primary']
        self.secondary = colors['secondary']
        self.background = colors['background']
        self.text = colors['text']

# Create themes
dark_theme = Theme("dark", {
    'primary': MD_BLUE,
    'secondary': MD_PURPLE,
    'background': GRAY10,
    'text': WHITE
})

light_theme = Theme("light", {
    'primary': MD_LIGHT_BLUE,
    'secondary': MD_PINK,
    'background': GRAY90,
    'text': BLACK
})
```

## Performance Tips

1. **Use tuples for simple colors** - Direct tuple usage avoids object creation
2. **Cache Color objects** - Create once, reuse many times
3. **Use pre-defined constants** - Faster than creating new colors
4. **Batch color conversions** - Use `batch_colors_to_array` for GPU uploads

## See Also

- [API Reference](API_REFERENCE.md#color) - Complete API documentation
- [test_colors.py](../tests/test_colors.py) - Test suite
- [example_colors.py](../examples/example_colors.py) - Interactive examples
- [Shapes Guide](SHAPES.md) - Using colors with shapes
- [Text Guide](TEXT.md) - Using colors with text
