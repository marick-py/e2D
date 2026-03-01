"""
e2D.ui — High-performance UI system for e2D.

Provides labels, buttons, sliders, input fields, toggles, containers,
theming, focus management, and a flexible anchor/layout system.

Phase 1: Pivot, UIElement, UITheme, Label, UIManager
"""

from .base import Pivot, UIElement
from .theme import UITheme
from .label import Label
from .manager import UIManager

__all__ = [
    'Pivot',
    'UIElement',
    'UITheme',
    'Label',
    'UIManager',
]
