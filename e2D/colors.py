"""
Modern color utilities for e2D - GPU-optimized with RGBA float defaults
Designed for ModernGL and GLTF compatibility (0.0-1.0 range)
"""

from __future__ import annotations
from typing import Union, Sequence, overload, TYPE_CHECKING, TypeAlias
import numpy as np
from numpy.typing import NDArray
from colorsys import hsv_to_rgb, hls_to_rgb, rgb_to_hsv, rgb_to_hls

# Forward declaration for ColorType (defined after Color class)
if TYPE_CHECKING:
    ColorType: TypeAlias = Union['Color', tuple[float, float, float, float]]
else:
    ColorType = Union['Color', tuple[float, float, float, float]]

# Type aliases for flexibility
ColorInput: TypeAlias = Union[ColorType, int, float, str, Sequence[float]]


class Color:
    """
    Immutable RGBA color optimized for GPU rendering.
    Default: RGBA floats in range [0.0, 1.0]
    """
    __slots__ = ('_r', '_g', '_b', '_a')
    
    def __init__(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0) -> None:
        """Create color with RGBA float values (0.0-1.0)"""
        self._r = float(r)
        self._g = float(g)
        self._b = float(b)
        self._a = float(a)
    
    # Properties for immutability
    @property
    def r(self) -> float:
        return self._r
    
    @property
    def g(self) -> float:
        return self._g
    
    @property
    def b(self) -> float:
        return self._b
    
    @property
    def a(self) -> float:
        return self._a
    
    # Constructors for different color spaces
    @classmethod
    def from_rgba(cls, r: float, g: float, b: float, a: float = 1.0) -> 'Color':
        """Create from RGBA floats (0.0-1.0)"""
        return cls(r, g, b, a)
    
    @classmethod
    def from_rgb(cls, r: float, g: float, b: float) -> 'Color':
        """Create from RGB floats (0.0-1.0), alpha defaults to 1.0"""
        return cls(r, g, b, 1.0)
    
    @classmethod
    def from_rgba255(cls, r: int, g: int, b: int, a: int = 255) -> 'Color':
        """Create from RGBA integers (0-255)"""
        return cls(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
    
    @classmethod
    def from_rgb255(cls, r: int, g: int, b: int) -> 'Color':
        """Create from RGB integers (0-255)"""
        return cls(r / 255.0, g / 255.0, b / 255.0, 1.0)
    
    @classmethod
    def from_hex(cls, hex_str: str) -> 'Color':
        """Create from hex string: '#RRGGBB' or '#RRGGBBAA' or 'RRGGBB'"""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
            return cls.from_rgb255(r, g, b)
        elif len(hex_str) == 8:
            r, g, b, a = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), int(hex_str[6:8], 16)
            return cls.from_rgba255(r, g, b, a)
        raise ValueError(f"Invalid hex color: {hex_str}")
    
    @classmethod
    def from_hsv(cls, h: float, s: float, v: float, a: float = 1.0) -> 'Color':
        """Create from HSV (h: 0-1, s: 0-1, v: 0-1)"""
        r, g, b = hsv_to_rgb(h, s, v)
        return cls(r, g, b, a)
    
    @classmethod
    def from_hls(cls, h: float, l: float, s: float, a: float = 1.0) -> 'Color':
        """Create from HLS (h: 0-1, l: 0-1, s: 0-1)"""
        r, g, b = hls_to_rgb(h, l, s)
        return cls(r, g, b, a)
    
    @classmethod
    def from_gray(cls, gray: float, a: float = 1.0) -> 'Color':
        """Create grayscale color"""
        return cls(gray, gray, gray, a)
    
    # Conversion methods
    def to_rgba(self) -> tuple[float, float, float, float]:
        """Convert to RGBA tuple (0.0-1.0)"""
        return (self._r, self._g, self._b, self._a)
    
    def to_rgb(self) -> tuple[float, float, float]:
        """Convert to RGB tuple (0.0-1.0)"""
        return (self._r, self._g, self._b)
    
    def to_rgba255(self) -> tuple[int, int, int, int]:
        """Convert to RGBA integers (0-255)"""
        return (int(self._r * 255), int(self._g * 255), int(self._b * 255), int(self._a * 255))
    
    def to_rgb255(self) -> tuple[int, int, int]:
        """Convert to RGB integers (0-255)"""
        return (int(self._r * 255), int(self._g * 255), int(self._b * 255))
    
    def to_hex(self, include_alpha: bool = False) -> str:
        """Convert to hex string"""
        r, g, b, a = self.to_rgba255()
        if include_alpha:
            return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def to_hsv(self) -> tuple[float, float, float]:
        """Convert to HSV (0.0-1.0)"""
        return rgb_to_hsv(self._r, self._g, self._b)
    
    def to_hls(self) -> tuple[float, float, float]:
        """Convert to HLS (0.0-1.0)"""
        return rgb_to_hls(self._r, self._g, self._b)
    
    def to_array(self) -> NDArray[np.float32]:
        """Convert to numpy array for GPU"""
        return np.array([self._r, self._g, self._b, self._a], dtype=np.float32)
    
    # Color operations
    def with_alpha(self, a: float) -> 'Color':
        """Return new color with different alpha"""
        return Color(self._r, self._g, self._b, a)
    
    def lerp(self, other: 'Color', t: float) -> 'Color':
        """Linear interpolation between colors"""
        return Color(
            self._r + (other._r - self._r) * t,
            self._g + (other._g - self._g) * t,
            self._b + (other._b - self._b) * t,
            self._a + (other._a - self._a) * t
        )
    
    def multiply(self, factor: float) -> 'Color':
        """Multiply RGB by factor (preserves alpha)"""
        return Color(
            min(self._r * factor, 1.0),
            min(self._g * factor, 1.0),
            min(self._b * factor, 1.0),
            self._a
        )
    
    def lighten(self, amount: float = 0.1) -> 'Color':
        """Lighten color by amount"""
        return self.lerp(Color.white(), amount)
    
    def darken(self, amount: float = 0.1) -> 'Color':
        """Darken color by amount"""
        return self.lerp(Color.black(), amount)
    
    def saturate(self, amount: float = 0.1) -> 'Color':
        """Increase saturation"""
        h, l, s = self.to_hls()
        return Color.from_hls(h, l, min(s + amount, 1.0), self._a)
    
    def desaturate(self, amount: float = 0.1) -> 'Color':
        """Decrease saturation"""
        h, l, s = self.to_hls()
        return Color.from_hls(h, l, max(s - amount, 0.0), self._a)
    
    def rotate_hue(self, degrees: float) -> 'Color':
        """Rotate hue by degrees (0-360)"""
        h, s, v = self.to_hsv()
        h = (h + degrees / 360.0) % 1.0
        return Color.from_hsv(h, s, v, self._a)
    
    def invert(self) -> 'Color':
        """Invert RGB (preserves alpha)"""
        return Color(1.0 - self._r, 1.0 - self._g, 1.0 - self._b, self._a)
    
    def grayscale(self) -> 'Color':
        """Convert to grayscale using luminance"""
        gray = 0.2989 * self._r + 0.5870 * self._g + 0.1140 * self._b
        return Color(gray, gray, gray, self._a)
    
    # Operators
    def __add__(self, other: 'Color') -> 'Color':
        """Add colors (clamped to 1.0)"""
        return Color(
            min(self._r + other._r, 1.0),
            min(self._g + other._g, 1.0),
            min(self._b + other._b, 1.0),
            min(self._a + other._a, 1.0)
        )
    
    def __sub__(self, other: 'Color') -> 'Color':
        """Subtract colors (clamped to 0.0)"""
        return Color(
            max(self._r - other._r, 0.0),
            max(self._g - other._g, 0.0),
            max(self._b - other._b, 0.0),
            max(self._a - other._a, 0.0)
        )
    
    def __mul__(self, factor: float) -> 'Color':
        """Multiply by scalar"""
        return Color(
            min(self._r * factor, 1.0),
            min(self._g * factor, 1.0),
            min(self._b * factor, 1.0),
            self._a
        )
    
    def __rmul__(self, factor: float) -> 'Color':
        """Right multiply by scalar"""
        return self.__mul__(factor)
    
    def __truediv__(self, factor: float) -> 'Color':
        """Divide by scalar"""
        return Color(
            self._r / factor,
            self._g / factor,
            self._b / factor,
            self._a
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return False
        return (self._r == other._r and self._g == other._g and 
                self._b == other._b and self._a == other._a)
    
    def __hash__(self) -> int:
        return hash((self._r, self._g, self._b, self._a))
    
    def __repr__(self) -> str:
        return f"Color(r={self._r:.3f}, g={self._g:.3f}, b={self._b:.3f}, a={self._a:.3f})"
    
    def __str__(self) -> str:
        return self.to_hex(include_alpha=True)
    
    def __iter__(self):
        """Support tuple unpacking: r, g, b, a = color"""
        return iter((self._r, self._g, self._b, self._a))
    
    def __getitem__(self, idx: int) -> float:
        """Support indexing: color[0] -> r"""
        if idx == 0:
            return self._r
        elif idx == 1:
            return self._g
        elif idx == 2:
            return self._b
        elif idx == 3:
            return self._a
        raise IndexError("Color index out of range (0-3)")
    
    # Pre-defined colors as class methods
    @classmethod
    def transparent(cls) -> 'Color':
        return cls(0.0, 0.0, 0.0, 0.0)
    
    @classmethod
    def white(cls) -> 'Color':
        return cls(1.0, 1.0, 1.0, 1.0)
    
    @classmethod
    def black(cls) -> 'Color':
        return cls(0.0, 0.0, 0.0, 1.0)
    
    @classmethod
    def red(cls) -> 'Color':
        return cls(1.0, 0.0, 0.0, 1.0)
    
    @classmethod
    def green(cls) -> 'Color':
        return cls(0.0, 1.0, 0.0, 1.0)
    
    @classmethod
    def blue(cls) -> 'Color':
        return cls(0.0, 0.0, 1.0, 1.0)
    
    @classmethod
    def cyan(cls) -> 'Color':
        return cls(0.0, 1.0, 1.0, 1.0)
    
    @classmethod
    def magenta(cls) -> 'Color':
        return cls(1.0, 0.0, 1.0, 1.0)
    
    @classmethod
    def yellow(cls) -> 'Color':
        return cls(1.0, 1.0, 0.0, 1.0)
    
    @classmethod
    def orange(cls) -> 'Color':
        return cls(1.0, 0.647, 0.0, 1.0)
    
    @classmethod
    def purple(cls) -> 'Color':
        return cls(0.5, 0.0, 0.5, 1.0)
    
    @classmethod
    def pink(cls) -> 'Color':
        return cls(1.0, 0.753, 0.796, 1.0)
    
    @classmethod
    def gray(cls, level: float = 0.5) -> 'Color':
        return cls(level, level, level, 1.0)


# Utility functions for batch operations
def normalize_color(color: ColorInput) -> tuple[float, float, float, float]:
    """
    Normalize various color inputs to RGBA float tuple.
    Supports: Color objects, tuples, lists, hex strings, single floats
    Always returns a tuple for performance (avoids Color object creation).
    """
    if isinstance(color, Color):
        return color.to_rgba()
    elif isinstance(color, str):
        return Color.from_hex(color).to_rgba()
    elif isinstance(color, (int, float)):
        v = float(color)
        return (v, v, v, 1.0)
    elif isinstance(color, (tuple, list)):
        if len(color) == 3:
            return (float(color[0]), float(color[1]), float(color[2]), 1.0)
        elif len(color) == 4:
            return (float(color[0]), float(color[1]), float(color[2]), float(color[3]))
        raise ValueError(f"Color tuple must have 3 or 4 elements, got {len(color)}")
    raise TypeError(f"Cannot convert {type(color)} to color")


def lerp_colors(color1: ColorInput, color2: ColorInput, t: float) -> tuple[float, float, float, float]:
    """Interpolate between two colors"""
    c1 = normalize_color(color1)
    c2 = normalize_color(color2)
    return (
        c1[0] + (c2[0] - c1[0]) * t,
        c1[1] + (c2[1] - c1[1]) * t,
        c1[2] + (c2[2] - c1[2]) * t,
        c1[3] + (c2[3] - c1[3]) * t
    )


def gradient(colors: list[ColorInput], steps: int) -> list[tuple[float, float, float, float]]:
    """Generate gradient between multiple colors"""
    if len(colors) < 2:
        raise ValueError("Need at least 2 colors for gradient")
    
    normalized = [normalize_color(c) for c in colors]
    result: list[tuple[float, float, float, float]] = []
    
    segments = len(normalized) - 1
    steps_per_segment = steps // segments
    
    for i in range(segments):
        for j in range(steps_per_segment):
            t = j / steps_per_segment
            result.append(lerp_colors(normalized[i], normalized[i + 1], t))
    
    result.append(normalized[-1])
    return result


def batch_colors_to_array(colors: Sequence[ColorInput]) -> NDArray[np.float32]:
    """Convert list of colors to numpy array for GPU"""
    result = np.empty((len(colors), 4), dtype=np.float32)
    for i, color in enumerate(colors):
        result[i] = normalize_color(color)
    return result
