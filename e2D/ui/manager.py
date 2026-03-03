"""
UIManager — owns every UI element, handles focus, tab navigation,
z-ordered drawing, and input dispatch.
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from .base import Pivot, UIElement
from .theme import UITheme, MONOKAI_THEME
from .label import Label

if TYPE_CHECKING:
    from .._types import ContextType
    from ..text import TextRenderer, TextStyle
    from ..input import Keyboard, Mouse
    from ..vectors import Vector2D
    from ..shapes import ShapeRenderer


class UIManager:
    """Central hub for the UI layer.

    Created automatically by :class:`RootEnv` and stored as ``env.ui``.
    """

    def __init__(
        self,
        ctx: ContextType,
        text_renderer: TextRenderer,
        shape_renderer: ShapeRenderer,
        window_size: Vector2D,
        theme: UITheme | None = None,
        window=None,
    ) -> None:
        self.ctx: ContextType = ctx
        self.text_renderer: TextRenderer = text_renderer
        self.shape_renderer: ShapeRenderer = shape_renderer
        self._window_size: Vector2D = window_size
        self._theme: UITheme = theme or MONOKAI_THEME

        self._elements: list[UIElement] = []
        self._focused: Optional[UIElement] = None
        self._hovered: Optional[UIElement] = None

        # Element that received the last mouse-down event (for drag/release)
        self._pressed_on: Optional[UIElement] = None
        # Stored each frame so interactive elements (e.g. Slider) can read them
        self._keyboard = None
        self._mouse    = None
        # Previous mouse position for computing drag deltas
        self._prev_mx: float = 0.0
        self._prev_my: float = 0.0

        self._wants_keyboard: bool = False
        self._wants_mouse: bool = False
        # GLFW window handle (needed for clipboard in InputField / MultiLineInput)
        self._window = window

    # -- public queries ------------------------------------------------------

    @property
    def theme(self) -> UITheme:
        return self._theme

    @theme.setter
    def theme(self, new_theme: UITheme) -> None:
        self._theme = new_theme
        # Rebuild every registered element so colours / fonts update immediately
        for elem in self._elements:
            elem._build(self.ctx, self.text_renderer)

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

    def button(self, text: str = '', on_click=None, **kwargs):
        """Create a :class:`Button`, add it, and return it."""
        from .button import Button
        btn = Button(text=text, on_click=on_click, **kwargs)
        self.add(btn)
        return btn

    def switch(self, value: bool = False, on_change=None, **kwargs):
        """Create a :class:`Switch` toggle, add it, and return it."""
        from .toggle import Switch
        sw = Switch(value=value, on_change=on_change, **kwargs)
        self.add(sw)
        return sw

    def checkbox(self, value: bool = False, on_change=None, **kwargs):
        """Create a :class:`Checkbox`, add it, and return it."""
        from .toggle import Checkbox
        cb = Checkbox(value=value, on_change=on_change, **kwargs)
        self.add(cb)
        return cb

    def slider(self, start: float = 0.0, end: float = 1.0, **kwargs):
        """Create a :class:`Slider`, add it, and return it."""
        from .slider import Slider
        sl = Slider(start=start, end=end, **kwargs)
        self.add(sl)
        return sl

    def range_slider(self, start: float = 0.0, end: float = 1.0, **kwargs):
        """Create a :class:`RangeSlider`, add it, and return it."""
        from .slider import RangeSlider
        rs = RangeSlider(start=start, end=end, **kwargs)
        self.add(rs)
        return rs

    def input_field(self, placeholder: str = '', value: str = '', **kwargs):
        """Create an :class:`InputField`, add it, and return it."""
        from .input_field import InputField
        f = InputField(placeholder=placeholder, value=value, **kwargs)
        self.add(f)
        return f

    def multi_line_input(self, placeholder: str = '', value: str = '', **kwargs):
        """Create a :class:`MultiLineInput`, add it, and return it."""
        from .input_field import MultiLineInput
        m = MultiLineInput(placeholder=placeholder, value=value, **kwargs)
        self.add(m)
        return m

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
        from ..input import KeyState, Keys, MouseButtons

        self._keyboard = keyboard
        self._mouse    = mouse
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

        # Dispatch hover enter / exit
        if new_hovered is not self._hovered:
            if self._hovered is not None:
                self._hovered.on_hover_exit()
            if new_hovered is not None:
                new_hovered.on_hover_enter()
        self._hovered = new_hovered
        self._wants_mouse = new_hovered is not None

        # -- mouse LEFT press --
        if MouseButtons.LEFT in mouse.just_pressed:
            if new_hovered is not None:
                self._pressed_on = new_hovered
                new_hovered.on_mouse_press(mx, my)
                if new_hovered._focusable:
                    self.focus(new_hovered)
            else:
                self.focus(None)

        # -- mouse LEFT drag (button still held, we have a pressed target) --
        if MouseButtons.LEFT in mouse.pressed and self._pressed_on is not None:
            dx = mx - self._prev_mx
            dy = my - self._prev_my
            if dx != 0 or dy != 0:
                self._pressed_on.on_mouse_drag(mx, my, dx, dy)

        # -- mouse LEFT release --
        if MouseButtons.LEFT in mouse.just_released:
            if self._pressed_on is not None:
                self._pressed_on.on_mouse_release(mx, my)
                self._pressed_on = None

        self._prev_mx = mx
        self._prev_my = my

        # -- tab navigation --
        if keyboard.get_key(Keys.TAB, KeyState.JUST_PRESSED):
            focused_consumes_tab = (
                self._focused is not None and self._focused._consumes_tab
            )
            is_ctrl_tab = (
                keyboard.get_key(Keys.LEFT_CONTROL)
                or keyboard.get_key(Keys.RIGHT_CONTROL)
            )
            if focused_consumes_tab and not is_ctrl_tab:
                # Let MultiLineInput (and similar) handle Tab itself
                self._focused.on_key_press(Keys.TAB)  # type: ignore[union-attr]
            else:
                # Normal Tab / Shift+Tab / Ctrl+Tab focus cycle
                if keyboard.get_key(Keys.LEFT_SHIFT) or keyboard.get_key(Keys.RIGHT_SHIFT):
                    self.focus_prev()
                else:
                    self.focus_next()

        # -- forward other keys to focused element --
        if self._focused is not None:
            for key in keyboard.just_pressed:
                if key != Keys.TAB:
                    self._focused.on_key_press(key)

        # -- forward char input to focused element --
        if self._focused is not None and keyboard.char_buffer:
            self._focused.on_char_input(list(keyboard.char_buffer))

        # -- mouse scroll (dispatch to hovered element) --
        if mouse.scroll.y != 0 and new_hovered is not None:
            new_hovered.on_scroll(mouse.scroll.y)

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
        # Flush any shape-renderer draw calls queued by UI elements
        self.shape_renderer.flush_queue()

    # -- resize --------------------------------------------------------------

    def on_resize(self, width: float, height: float) -> None:
        """Re-layout all anchored elements after a window resize."""
        self._window_size.set(width, height)
        for elem in self._elements:
            elem.layout(0, 0, width, height)
