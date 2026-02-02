"""
Pre-defined color palette for e2D
All colors are RGBA tuples (0.0-1.0) for GPU compatibility
Import individual colors as needed: from e2D.color_defs import RED, BLUE
"""

from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import ColorType
else:
    ColorType = tuple[float, float, float, float]

# ============================================================================
# Basic Colors
# ============================================================================
TRANSPARENT: Final[ColorType] = (0.0, 0.0, 0.0, 0.0)
WHITE: Final[ColorType] = (1.0, 1.0, 1.0, 1.0)
BLACK: Final[ColorType] = (0.0, 0.0, 0.0, 1.0)
RED: Final[ColorType] = (1.0, 0.0, 0.0, 1.0)
GREEN: Final[ColorType] = (0.0, 1.0, 0.0, 1.0)
BLUE: Final[ColorType] = (0.0, 0.0, 1.0, 1.0)
CYAN: Final[ColorType] = (0.0, 1.0, 1.0, 1.0)
MAGENTA: Final[ColorType] = (1.0, 0.0, 1.0, 1.0)
YELLOW: Final[ColorType] = (1.0, 1.0, 0.0, 1.0)

# ============================================================================
# Extended Colors
# ============================================================================
ORANGE: Final[ColorType] = (1.0, 0.647, 0.0, 1.0)
PURPLE: Final[ColorType] = (0.5, 0.0, 0.5, 1.0)
PINK: Final[ColorType] = (1.0, 0.753, 0.796, 1.0)
BROWN: Final[ColorType] = (0.647, 0.165, 0.165, 1.0)
LIME: Final[ColorType] = (0.5, 1.0, 0.0, 1.0)
TEAL: Final[ColorType] = (0.0, 0.5, 0.5, 1.0)
NAVY: Final[ColorType] = (0.0, 0.0, 0.5, 1.0)
MAROON: Final[ColorType] = (0.5, 0.0, 0.0, 1.0)
OLIVE: Final[ColorType] = (0.5, 0.5, 0.0, 1.0)
SILVER: Final[ColorType] = (0.753, 0.753, 0.753, 1.0)
GOLD: Final[ColorType] = (1.0, 0.843, 0.0, 1.0)
INDIGO: Final[ColorType] = (0.294, 0.0, 0.51, 1.0)
VIOLET: Final[ColorType] = (0.933, 0.51, 0.933, 1.0)
TURQUOISE: Final[ColorType] = (0.251, 0.878, 0.816, 1.0)
CORAL: Final[ColorType] = (1.0, 0.498, 0.314, 1.0)

# ============================================================================
# Grayscale
# ============================================================================
GRAY10: Final[ColorType] = (0.1, 0.1, 0.1, 1.0)
GRAY20: Final[ColorType] = (0.2, 0.2, 0.2, 1.0)
GRAY30: Final[ColorType] = (0.3, 0.3, 0.3, 1.0)
GRAY40: Final[ColorType] = (0.4, 0.4, 0.4, 1.0)
GRAY50: Final[ColorType] = (0.5, 0.5, 0.5, 1.0)
GRAY60: Final[ColorType] = (0.6, 0.6, 0.6, 1.0)
GRAY70: Final[ColorType] = (0.7, 0.7, 0.7, 1.0)
GRAY80: Final[ColorType] = (0.8, 0.8, 0.8, 1.0)
GRAY90: Final[ColorType] = (0.9, 0.9, 0.9, 1.0)

# ============================================================================
# Material Design Colors (Primary Palette)
# ============================================================================
MD_RED: Final[ColorType] = (0.957, 0.263, 0.212, 1.0)  # #F44336
MD_PINK: Final[ColorType] = (0.914, 0.118, 0.388, 1.0)  # #E91E63
MD_PURPLE: Final[ColorType] = (0.612, 0.153, 0.690, 1.0)  # #9C27B0
MD_DEEP_PURPLE: Final[ColorType] = (0.404, 0.227, 0.718, 1.0)  # #673AB7
MD_INDIGO: Final[ColorType] = (0.247, 0.318, 0.710, 1.0)  # #3F51B5
MD_BLUE: Final[ColorType] = (0.129, 0.588, 0.953, 1.0)  # #2196F3
MD_LIGHT_BLUE: Final[ColorType] = (0.012, 0.663, 0.957, 1.0)  # #03A9F4
MD_CYAN: Final[ColorType] = (0.0, 0.737, 0.831, 1.0)  # #00BCD4
MD_TEAL: Final[ColorType] = (0.0, 0.588, 0.533, 1.0)  # #009688
MD_GREEN: Final[ColorType] = (0.298, 0.686, 0.314, 1.0)  # #4CAF50
MD_LIGHT_GREEN: Final[ColorType] = (0.545, 0.765, 0.290, 1.0)  # #8BC34A
MD_LIME: Final[ColorType] = (0.804, 0.863, 0.224, 1.0)  # #CDDC39
MD_YELLOW: Final[ColorType] = (1.0, 0.922, 0.231, 1.0)  # #FFEB3B
MD_AMBER: Final[ColorType] = (1.0, 0.757, 0.027, 1.0)  # #FFC107
MD_ORANGE: Final[ColorType] = (1.0, 0.596, 0.0, 1.0)  # #FF9800
MD_DEEP_ORANGE: Final[ColorType] = (1.0, 0.341, 0.133, 1.0)  # #FF5722
MD_BROWN: Final[ColorType] = (0.475, 0.333, 0.282, 1.0)  # #795548
MD_GREY: Final[ColorType] = (0.620, 0.620, 0.620, 1.0)  # #9E9E9E
MD_BLUE_GREY: Final[ColorType] = (0.376, 0.490, 0.545, 1.0)  # #607D8B

# ============================================================================
# Pastel Colors
# ============================================================================
PASTEL_RED: Final[ColorType] = (1.0, 0.412, 0.380, 1.0)
PASTEL_ORANGE: Final[ColorType] = (1.0, 0.706, 0.510, 1.0)
PASTEL_YELLOW: Final[ColorType] = (1.0, 0.996, 0.635, 1.0)
PASTEL_GREEN: Final[ColorType] = (0.467, 0.867, 0.467, 1.0)
PASTEL_CYAN: Final[ColorType] = (0.467, 0.867, 0.867, 1.0)
PASTEL_BLUE: Final[ColorType] = (0.686, 0.933, 0.933, 1.0)
PASTEL_PURPLE: Final[ColorType] = (0.800, 0.600, 0.800, 1.0)
PASTEL_PINK: Final[ColorType] = (1.0, 0.820, 0.863, 1.0)

# ============================================================================
# Neon Colors
# ============================================================================
NEON_RED: Final[ColorType] = (1.0, 0.0, 0.0, 1.0)
NEON_ORANGE: Final[ColorType] = (1.0, 0.4, 0.0, 1.0)
NEON_YELLOW: Final[ColorType] = (1.0, 1.0, 0.0, 1.0)
NEON_GREEN: Final[ColorType] = (0.0, 1.0, 0.0, 1.0)
NEON_CYAN: Final[ColorType] = (0.0, 1.0, 1.0, 1.0)
NEON_BLUE: Final[ColorType] = (0.0, 0.4, 1.0, 1.0)
NEON_PURPLE: Final[ColorType] = (0.8, 0.0, 1.0, 1.0)
NEON_PINK: Final[ColorType] = (1.0, 0.0, 0.5, 1.0)

# ============================================================================
# UI Common Colors
# ============================================================================
UI_SUCCESS: Final[ColorType] = (0.298, 0.686, 0.314, 1.0)  # Green
UI_WARNING: Final[ColorType] = (1.0, 0.757, 0.027, 1.0)  # Amber
UI_ERROR: Final[ColorType] = (0.957, 0.263, 0.212, 1.0)  # Red
UI_INFO: Final[ColorType] = (0.129, 0.588, 0.953, 1.0)  # Blue
UI_DISABLED: Final[ColorType] = (0.62, 0.62, 0.62, 1.0)  # Grey

# ============================================================================
# Color Dictionary (for dynamic lookup)
# ============================================================================
COLOR_NAMES: dict[str, ColorType] = {
    # Basic
    'transparent': TRANSPARENT,
    'white': WHITE,
    'black': BLACK,
    'red': RED,
    'green': GREEN,
    'blue': BLUE,
    'cyan': CYAN,
    'magenta': MAGENTA,
    'yellow': YELLOW,
    # Extended
    'orange': ORANGE,
    'purple': PURPLE,
    'pink': PINK,
    'brown': BROWN,
    'lime': LIME,
    'teal': TEAL,
    'navy': NAVY,
    'maroon': MAROON,
    'olive': OLIVE,
    'silver': SILVER,
    'gold': GOLD,
    'indigo': INDIGO,
    'violet': VIOLET,
    'turquoise': TURQUOISE,
    'coral': CORAL,
    # Grayscale
    'gray10': GRAY10,
    'gray20': GRAY20,
    'gray30': GRAY30,
    'gray40': GRAY40,
    'gray50': GRAY50,
    'gray60': GRAY60,
    'gray70': GRAY70,
    'gray80': GRAY80,
    'gray90': GRAY90,
    # Material Design
    'md_red': MD_RED,
    'md_pink': MD_PINK,
    'md_purple': MD_PURPLE,
    'md_deep_purple': MD_DEEP_PURPLE,
    'md_indigo': MD_INDIGO,
    'md_blue': MD_BLUE,
    'md_light_blue': MD_LIGHT_BLUE,
    'md_cyan': MD_CYAN,
    'md_teal': MD_TEAL,
    'md_green': MD_GREEN,
    'md_light_green': MD_LIGHT_GREEN,
    'md_lime': MD_LIME,
    'md_yellow': MD_YELLOW,
    'md_amber': MD_AMBER,
    'md_orange': MD_ORANGE,
    'md_deep_orange': MD_DEEP_ORANGE,
    'md_brown': MD_BROWN,
    'md_grey': MD_GREY,
    'md_blue_grey': MD_BLUE_GREY,
    # Pastels
    'pastel_red': PASTEL_RED,
    'pastel_orange': PASTEL_ORANGE,
    'pastel_yellow': PASTEL_YELLOW,
    'pastel_green': PASTEL_GREEN,
    'pastel_cyan': PASTEL_CYAN,
    'pastel_blue': PASTEL_BLUE,
    'pastel_purple': PASTEL_PURPLE,
    'pastel_pink': PASTEL_PINK,
    # Neon
    'neon_red': NEON_RED,
    'neon_orange': NEON_ORANGE,
    'neon_yellow': NEON_YELLOW,
    'neon_green': NEON_GREEN,
    'neon_cyan': NEON_CYAN,
    'neon_blue': NEON_BLUE,
    'neon_purple': NEON_PURPLE,
    'neon_pink': NEON_PINK,
    # UI
    'ui_success': UI_SUCCESS,
    'ui_warning': UI_WARNING,
    'ui_error': UI_ERROR,
    'ui_info': UI_INFO,
    'ui_disabled': UI_DISABLED,
}


def get_color(name: str) -> ColorType:
    """Get color by name (case-insensitive)"""
    return COLOR_NAMES[name.lower()]


def has_color(name: str) -> bool:
    """Check if color name exists"""
    return name.lower() in COLOR_NAMES


__all__ = [
    # Basic
    'TRANSPARENT', 'WHITE', 'BLACK', 'RED', 'GREEN', 'BLUE',
    'CYAN', 'MAGENTA', 'YELLOW',
    # Extended
    'ORANGE', 'PURPLE', 'PINK', 'BROWN', 'LIME', 'TEAL',
    'NAVY', 'MAROON', 'OLIVE', 'SILVER', 'GOLD', 'INDIGO',
    'VIOLET', 'TURQUOISE', 'CORAL',
    # Grayscale
    'GRAY10', 'GRAY20', 'GRAY30', 'GRAY40', 'GRAY50',
    'GRAY60', 'GRAY70', 'GRAY80', 'GRAY90',
    # Material Design
    'MD_RED', 'MD_PINK', 'MD_PURPLE', 'MD_DEEP_PURPLE', 'MD_INDIGO',
    'MD_BLUE', 'MD_LIGHT_BLUE', 'MD_CYAN', 'MD_TEAL', 'MD_GREEN',
    'MD_LIGHT_GREEN', 'MD_LIME', 'MD_YELLOW', 'MD_AMBER', 'MD_ORANGE',
    'MD_DEEP_ORANGE', 'MD_BROWN', 'MD_GREY', 'MD_BLUE_GREY',
    # Pastels
    'PASTEL_RED', 'PASTEL_ORANGE', 'PASTEL_YELLOW', 'PASTEL_GREEN',
    'PASTEL_CYAN', 'PASTEL_BLUE', 'PASTEL_PURPLE', 'PASTEL_PINK',
    # Neon
    'NEON_RED', 'NEON_ORANGE', 'NEON_YELLOW', 'NEON_GREEN',
    'NEON_CYAN', 'NEON_BLUE', 'NEON_PURPLE', 'NEON_PINK',
    # UI
    'UI_SUCCESS', 'UI_WARNING', 'UI_ERROR', 'UI_INFO', 'UI_DISABLED',
    # Functions
    'COLOR_NAMES', 'get_color', 'has_color',
]
