# Color System - Modern GPU-Optimized Colors

Modern color class with 80+ pre-defined colors, optimized for ModernGL and GLTF (0.0-1.0 RGBA).

## Features

- ✅ **GPU-optimized** - RGBA floats (0.0-1.0) for direct GPU upload
- ✅ **80+ pre-defined colors** - Material Design, Pastels, Neon, UI colors
- ✅ **Color space conversions** - RGB, HSV, HLS, Hex
- ✅ **Color operations** - Lighten, darken, saturate, invert, rotate hue
- ✅ **Cython-optimized** batch operations
- ✅ **Type-safe** with full type hints
- ✅ **Immutable** - Thread-safe and predictable

## Quick Start

```python
from e2D import Color

# Create colors
red = Color.from_hex("#FF0000")
blue = Color.from_rgb255(0, 0, 255)
green = Color.from_hsv(0.33, 1.0, 1.0)

# Color operations
lighter = red.lighten(0.2)
darker = red.darken(0.2)
inverted = red.invert()
hue_shifted = red.rotate_hue(120)

# Convert to different formats
rgba_tuple = red.to_rgba()        # (1.0, 0.0, 0.0, 1.0)
rgb255 = red.to_rgb255()           # (255, 0, 0)
hex_str = red.to_hex()             # "#ff0000"
gpu_array = red.to_array()         # numpy array for GPU
```

## Pre-Defined Colors

```python
from e2D.color_defs import *

# Basic colors
WHITE, BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW

# Extended colors
ORANGE, PURPLE, PINK, BROWN, LIME, TEAL, NAVY, GOLD

# Grayscale (10-90% in 10% steps)
GRAY10, GRAY20, GRAY30, GRAY40, GRAY50, GRAY60, GRAY70, GRAY80, GRAY90

# Material Design colors
MD_RED, MD_PINK, MD_PURPLE, MD_INDIGO, MD_BLUE, MD_CYAN, MD_TEAL, 
MD_GREEN, MD_LIME, MD_YELLOW, MD_ORANGE, MD_BROWN, MD_GREY

# Pastel colors
PASTEL_RED, PASTEL_ORANGE, PASTEL_YELLOW, PASTEL_GREEN, 
PASTEL_CYAN, PASTEL_BLUE, PASTEL_PURPLE, PASTEL_PINK

# Neon colors
NEON_RED, NEON_ORANGE, NEON_YELLOW, NEON_GREEN, 
NEON_CYAN, NEON_BLUE, NEON_PURPLE, NEON_PINK

# UI colors
UI_SUCCESS, UI_WARNING, UI_ERROR, UI_INFO, UI_DISABLED
```

## Creating Colors

```python
from e2D import Color

# From RGBA floats (0.0-1.0) - GPU format
c1 = Color(1.0, 0.5, 0.0, 1.0)
c2 = Color.from_rgba(1.0, 0.5, 0.0, 1.0)

# From RGB floats
c3 = Color.from_rgb(1.0, 0.5, 0.0)  # Alpha defaults to 1.0

# From RGB/RGBA integers (0-255)
c4 = Color.from_rgb255(255, 128, 0)
c5 = Color.from_rgba255(255, 128, 0, 255)

# From hex string
c6 = Color.from_hex("#FF8000")
c7 = Color.from_hex("#FF8000FF")  # With alpha

# From HSV (Hue, Saturation, Value)
c8 = Color.from_hsv(0.1, 0.8, 1.0)

# From HLS (Hue, Lightness, Saturation)
c9 = Color.from_hls(0.1, 0.5, 0.8)

# Grayscale
c10 = Color.from_gray(0.5)  # 50% gray
```

## Color Operations

```python
color = Color.from_hex("#FF6B35")

# Lightening/Darkening
lighter = color.lighten(0.2)      # +20% lighter
darker = color.darken(0.2)        # +20% darker

# Saturation
saturated = color.saturate(0.3)   # More vibrant
desaturated = color.desaturate(0.3)  # More gray

# Hue rotation
rotated = color.rotate_hue(120)   # Rotate hue by 120°

# Inversion
inverted = color.invert()         # Invert RGB

# Grayscale
gray = color.grayscale()          # Convert to grayscale

# Alpha manipulation
transparent = color.with_alpha(0.5)  # 50% transparent

# Linear interpolation
color1 = Color.red()
color2 = Color.blue()
purple = color1.lerp(color2, 0.5)  # 50% blend

# Arithmetic
bright = color * 1.5              # Brighten
dim = color / 2.0                 # Dim
combined = color1 + color2        # Add colors
```

## Color Space Conversions

```python
color = Color.from_hex("#FF6B35")

# Get as different formats
rgba = color.to_rgba()        # (1.0, 0.42, 0.21, 1.0)
rgb = color.to_rgb()          # (1.0, 0.42, 0.21)
rgba255 = color.to_rgba255()  # (255, 107, 53, 255)
rgb255 = color.to_rgb255()    # (255, 107, 53)
hex_str = color.to_hex()      # "#ff6b35"
hex_alpha = color.to_hex(include_alpha=True)  # "#ff6b35ff"
hsv = color.to_hsv()          # (0.05, 0.79, 1.0)
hls = color.to_hls()          # (0.05, 0.61, 1.0)

# For GPU rendering
gpu_array = color.to_array()  # numpy float32 array [r, g, b, a]
```

## Batch Color Operations (Cython-Optimized)

For processing many colors efficiently:

```python
from e2D.ccolors import (
    batch_lerp_colors,
    batch_multiply_colors,
    batch_grayscale,
    batch_rotate_hue,
    generate_gradient
)
import numpy as np

# Create color arrays (N, 4) RGBA
colors1 = np.array([[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0]], dtype=np.float32)
colors2 = np.array([[0.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, 1.0]], dtype=np.float32)

# Batch operations (ultra-fast)
interpolated = batch_lerp_colors(colors1, colors2, 0.5)
brightened = batch_multiply_colors(colors1, 1.5)
grayscale = batch_grayscale(colors1)
hue_shifted = batch_rotate_hue(colors1, 60)  # Rotate 60°

# Generate gradient
control_colors = np.array([
    [1.0, 0.0, 0.0, 1.0],  # Red
    [0.0, 1.0, 0.0, 1.0],  # Green
    [0.0, 0.0, 1.0, 1.0],  # Blue
], dtype=np.float32)
gradient = generate_gradient(control_colors, steps=100)
```

## Gradients

```python
from e2D.colors import gradient
from e2D.color_defs import RED, YELLOW, GREEN

# Create smooth gradient
colors = gradient([RED, YELLOW, GREEN], steps=100)

# Use in rendering
for i, color in enumerate(colors):
    x = i * spacing
    draw_circle((x, y), radius, color=color)
```

## Usage with e2D Rendering

```python
from e2D import RootEnv, DefEnv
from e2D.color_defs import MD_BLUE, PASTEL_PINK

class MyApp(DefEnv):
    def draw(self):
        # Draw shapes with colors
        rootEnv.draw_circle(
            center=(100, 100),
            radius=50,
            color=MD_BLUE,
            border_color=PASTEL_PINK,
            border_width=3.0
        )
```

## Color Utilities

```python
from e2D.colors import normalize_color, lerp_colors
from e2D.color_defs import get_color, has_color

# Normalize various color inputs
c1 = normalize_color("#FF0000")           # Hex string
c2 = normalize_color((1.0, 0.0, 0.0))     # Tuple
c3 = normalize_color(Color.red())         # Color object

# Interpolate colors
purple = lerp_colors(RED, BLUE, 0.5)

# Get color by name
orange = get_color("orange")
md_blue = get_color("md_blue")

# Check if color exists
if has_color("neon_green"):
    color = get_color("neon_green")
```

## Best Practices

1. **Use pre-defined colors** when possible for consistency
2. **Use Color objects** for complex operations
3. **Use batch operations** for processing many colors
4. **Use RGBA floats (0.0-1.0)** for GPU compatibility
5. **Cache gradients** if used multiple times per frame

## API Reference

### Color Class
- **Construction**: `from_rgba()`, `from_rgb()`, `from_rgb255()`, `from_rgba255()`, `from_hex()`, `from_hsv()`, `from_hls()`, `from_gray()`
- **Conversion**: `to_rgba()`, `to_rgb()`, `to_rgb255()`, `to_rgba255()`, `to_hex()`, `to_hsv()`, `to_hls()`, `to_array()`
- **Operations**: `lighten()`, `darken()`, `saturate()`, `desaturate()`, `rotate_hue()`, `invert()`, `grayscale()`, `with_alpha()`, `lerp()`
- **Arithmetic**: `+`, `-`, `*`, `/`

### Batch Operations (ccolors module)
- `batch_lerp_colors()` - Interpolate color arrays
- `batch_multiply_colors()` - Scale brightness
- `batch_add_colors()` - Add colors
- `batch_grayscale()` - Convert to grayscale
- `batch_invert()` - Invert colors
- `batch_rgb_to_hsv()`, `batch_hsv_to_rgb()` - Color space conversion
- `batch_rotate_hue()` - Rotate hue
- `batch_saturate()` - Adjust saturation
- `generate_gradient()` - Create gradients

---

[← Back to README](../README.md)
