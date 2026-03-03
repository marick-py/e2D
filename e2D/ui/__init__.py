"""
e2D.ui — High-performance UI system for e2D.

Provides labels, buttons, sliders, input fields, toggles, containers,
theming, focus management, and a flexible anchor/layout system.

Phase 1: Pivot, UIElement, UITheme, Label, UIManager
"""

from .base import Pivot, UIElement
from .theme import (
    UITheme,
    MONOKAI_THEME, DARK_THEME, LIGHT_THEME,
    SOLARIZED_DARK, SOLARIZED_LIGHT,
    NORD_THEME, DRACULA_THEME,
    TOKYO_NIGHT_THEME, HIGH_CONTRAST,
)
from .label import Label
from .manager import UIManager
from .button import Button
from .toggle import Switch, Checkbox
from .slider import Slider, RangeSlider
from .input_field import InputField, MultiLineInput

__all__ = [
    'Pivot',
    'UIElement',
    'UITheme',
    'MONOKAI_THEME',
    'DARK_THEME',
    'LIGHT_THEME',
    'SOLARIZED_DARK',
    'SOLARIZED_LIGHT',
    'NORD_THEME',
    'DRACULA_THEME',
    'TOKYO_NIGHT_THEME',
    'HIGH_CONTRAST',
    'Label',
    'UIManager',
    'Button',
    'Switch',
    'Checkbox',
    'Slider',
    'RangeSlider',
    'InputField',
    'MultiLineInput',
]
