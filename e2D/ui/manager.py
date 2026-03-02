"""
UIManager — owns every UI element, handles focus, tab navigation,
z-ordered drawing, and input dispatch.
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from .base import Pivot, UIElement
from .theme import UITheme, DARK_THEME
from .label import Label

if TYPE_CHECKING:
    from .._types import ContextType
    from ..text import TextRenderer, TextStyle
    from ..input import Keyboard, Mouse
    from ..vectors import Vector2D


class UIManager:
    """Central hub for the UI layer.

    Created automatically by :class:`RootEnv` and stored as ``env.ui``.
    """

    def __init__(
        self,
        ctx: ContextType,
        text_renderer: TextRenderer,
        window_size: Vector2D,
        theme: UITheme | None = None,
    ) -> None:
        self.ctx: ContextType = ctx
        self.text_renderer: TextRenderer = text_renderer
        self._window_size: Vector2D = window_size
        self.theme: UITheme = theme or DARK_THEME

        self._elements: list[UIElement] = []
        self._focused: Optional[UIElement] = None
        self._hovered: Optional[UIElement] = None

        self._wants_keyboard: bool = False
        self._wants_mouse: bool = False

    # -- public queries ------------------------------------------------------

    @property
    def focused_element(self) -> Optional[UIElement]:
        """Currently focused UI element (or *None*)."""
        return self._focused

    @property
    def wants_keyboard(self) -> bool:
        """*True* when a focusable element has keyboard focus (e.g. text input).

        Game code should check this before processing keyboard input::

            if not env.ui.wants_keyboard:
                # process game keys
        """
        return self._wants_keyboard

    @property
    def wants_mouse(self) -> bool:
        """*True* when the mouse is over a UI element."""
        return self._wants_mouse

    # -- element management --------------------------------------------------

    def add(self, element: UIElement) -> UIElement:
        """Register an element (and its children) with this manager."""
        element._set_manager(self)
        self._elements.append(element)
        element._build(self.ctx, self.text_renderer)
        return element

    def remove(self, element: UIElement) -> None:
        """Unregister and release GPU resources."""
        if self._focused is element:
            self.focus(None)
        element.release()
        element._manager = None
        if element in self._elements:
            self._elements.remove(element)

    # -- factory shortcuts ---------------------------------------------------

    def label(self, *segments, **kwargs) -> Label:
        """Create a :class:`Label`, add it, and return it."""
        lbl = Label(*segments, **kwargs)
        self.add(lbl)
        return lbl

    # -- focus ---------------------------------------------------------------

    def focus(self, element: Optional[UIElement]) -> None:
        if self._focused is element:
            return
        if self._focused is not None:
            self._focused.on_blur()
        self._focused = element
        if element is not None:
            element.on_focus()
        self._wants_keyboard = element is not None and element._focusable

    def focus_next(self) -> None:
        """Tab → move focus to the next focusable element."""
        self._cycle_focus(reverse=False)

    def focus_prev(self) -> None:
        """Shift+Tab → move focus to the previous focusable element."""
        self._cycle_focus(reverse=True)

    def _cycle_focus(self, reverse: bool) -> None:
        focusable = self._collect_focusable()
        if not focusable:
            return
        focusable.sort(key=lambda e: e._tab_index)
        if reverse:
            focusable.reverse()

        if self._focused is None:
            self.focus(focusable[0])
            return

        try:
            idx = focusable.index(self._focused)
            nxt = focusable[(idx + 1) % len(focusable)]
            self.focus(nxt)
        except ValueError:
            self.focus(focusable[0])

    def _collect_focusable(self) -> list[UIElement]:
        out: list[UIElement] = []
        for elem in self._elements:
            self._walk_focusable(elem, out)
        return out

    @staticmethod
    def _walk_focusable(elem: UIElement, out: list[UIElement]) -> None:
        if elem._focusable and elem.visible and elem.enabled:
            out.append(elem)
        for child in elem._children:
            UIManager._walk_focusable(child, out)

    # -- per-frame -----------------------------------------------------------

    def process_input(self, mouse: Mouse, keyboard: Keyboard) -> None:
        """Dispatch mouse / keyboard events to UI elements.

        Called by :class:`RootEnv` each frame **before** ``env.update()``.
        """
        import glfw
        from ..input import KeyState, Keys

        mx, my = mouse.position.x, mouse.position.y

        # -- hover detection (top z_index first) --
        sorted_elems = sorted(
            self._all_visible_elements(),
            key=lambda e: e.z_index,
            reverse=True,
        )
        new_hovered: Optional[UIElement] = None
        for elem in sorted_elems:
            if elem.enabled and elem.contains_point(mx, my):
                new_hovered = elem
                break
        self._hovered = new_hovered
        self._wants_mouse = new_hovered is not None

        # -- click → focus / activate --
        if mouse.just_pressed:
            if new_hovered is not None and new_hovered._focusable:
                self.focus(new_hovered)
            elif new_hovered is None:
                self.focus(None)

        # -- tab navigation --
        if keyboard.get_key(Keys.TAB, KeyState.JUST_PRESSED):
            if keyboard.get_key(Keys.LEFT_SHIFT) or keyboard.get_key(Keys.RIGHT_SHIFT):
                self.focus_prev()
            else:
                self.focus_next()

        # -- mark keyboard consumed when a focusable element has focus --
        keyboard.is_consumed = self._wants_keyboard

    def _all_visible_elements(self) -> list[UIElement]:
        """Flatten the element tree, visible only."""
        out: list[UIElement] = []
        for elem in self._elements:
            self._walk_visible(elem, out)
        return out

    @staticmethod
    def _walk_visible(elem: UIElement, out: list[UIElement]) -> None:
        if not elem.visible:
            return
        out.append(elem)
        for child in elem._children:
            UIManager._walk_visible(child, out)

    def update(self, dt: float) -> None:
        for elem in self._elements:
            if elem.enabled:
                elem.update(dt)

    def draw(self) -> None:
        """Render all visible elements sorted by z-index (ascending)."""
        elements = self._all_visible_elements()
        elements.sort(key=lambda e: e.z_index)
        for elem in elements:
            elem.draw(self.ctx)

    # -- resize --------------------------------------------------------------

    def on_resize(self, width: float, height: float) -> None:
        """Re-layout all anchored elements after a window resize."""
        self._window_size.set(width, height)
        for elem in self._elements:
            elem.layout(0, 0, width, height)
