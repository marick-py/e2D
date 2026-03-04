"""
Example demonstrating keyboard and mouse input in e2D.

Shows Keys class, MouseButtons class, KeyState (PRESSED / JUST_PRESSED /
JUST_RELEASED), and the new get_chars() typed-text API.
Uses labels and containers from the UI system for all text.
"""

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keyboard, Mouse, Keys, MouseButtons, KeyState,
    WHITE, RED, GREEN, BLUE, YELLOW, CYAN, TextStyle,
    Label, VBox, HBox, FreeContainer, SizeMode,
)
from e2D.colors import Color

# -- style helpers -----------------------------------------------------------

_TITLE  = TextStyle(font_size=28, color=WHITE)
_HEAD   = TextStyle(font_size=18, color=WHITE)
_INST   = TextStyle(font_size=15, color=(0.85, 0.85, 0.85, 1.0))
_INST_B = TextStyle(font_size=15, color=CYAN)
_EVENT  = TextStyle(font_size=15, color=YELLOW)
_STATUS = TextStyle(font_size=16, color=WHITE)
_DIM    = TextStyle(font_size=14, color=(0.6, 0.6, 0.6, 1.0))
_TYPED  = TextStyle(font_size=16, color=WHITE)


class InputExample(DefEnv):
    """Example showing keyboard and mouse input handling"""

    def __init__(self, root: RootEnv) -> None:
        self.root = root
        self.frame = 0
        self.messages: list[str] = []
        self.player_pos = V2(450, 300)
        self.speed = 200.0
        self.typed_text: str = ""
        self._TYPED_MAXLEN = 60

        ui = root.ui

        # ── Main layout ─────────────────────────────────────────────────
        self._main = ui.free_container(
            position=V2(0, 0), size=V2(900, 600),
            anchor_min=(0.0, 0.0), anchor_max=(1.0, 1.0),
            bg_color=Color(0, 0, 0, 0),
        )

        # ── Left panel: instructions inside a VBox ──────────────────────
        left_box = VBox(
            spacing=2, align='left',
            size=V2(460, 460),
            bg_color=Color(0.04, 0.04, 0.08, 0.85),
            corner_radius=8.0,
            padding=12,
        )
        self._main.add_child(left_box)
        self._main._child_offsets[id(left_box)] = (8.0, 8.0)

        def _lbl(text: str, style=_INST) -> Label:
            lb = ui.label(text, default_style=style)
            left_box.add_child(lb)
            return lb

        _lbl("Input Handling Example", _TITLE)
        _lbl("")
        _lbl("Keyboard:", _INST_B)
        _lbl("  WASD / Arrow Keys - Move blue circle")
        _lbl("  SHIFT - Hold to run faster")
        _lbl("  SPACE - Reset position")
        _lbl("  ENTER - Trigger event")
        _lbl("  0-9 - Number keys")
        _lbl("  F1 - Function key")
        _lbl("")
        _lbl("Mouse:", _INST_B)
        _lbl("  Left/Right/Middle Click - Colored circle")
        _lbl("")
        _lbl("Type text (right panel):", _INST_B)
        _lbl("  Any key - append character")
        _lbl("  BACKSPACE - delete last character")
        _lbl("")
        _lbl("Recent Events:", _INST_B)

        # Event message labels (pre-allocated, updated dynamically)
        self._event_lbls: list[Label] = []
        for _ in range(8):
            lb = ui.label("", default_style=_EVENT)
            left_box.add_child(lb)
            self._event_lbls.append(lb)

        # ── Bottom-left: Player / Mouse status ──────────────────────────
        status_box = VBox(
            spacing=2, align='left',
            size=V2(460, 80),
            bg_color=Color(0.04, 0.04, 0.08, 0.85),
            corner_radius=6.0,
            padding=10,
        )
        self._main.add_child(status_box)
        self._main._child_offsets[id(status_box)] = (8.0, 480.0)

        self._lbl_status_title = ui.label("Player Status:", default_style=_HEAD)
        status_box.add_child(self._lbl_status_title)
        self._lbl_pos = ui.label("Position: (450, 300)", default_style=_STATUS)
        status_box.add_child(self._lbl_pos)
        self._lbl_speed = ui.label("Speed: 200 px/s", default_style=_STATUS)
        status_box.add_child(self._lbl_speed)
        self._lbl_mouse = ui.label("Mouse: (0, 0)", default_style=_STATUS)
        status_box.add_child(self._lbl_mouse)

        # ── Right panel: typed text demo ────────────────────────────────
        type_box = VBox(
            spacing=4, align='left',
            size=V2(390, 100),
            bg_color=Color(0.04, 0.04, 0.08, 0.85),
            corner_radius=8.0,
            padding=10,
        )
        self._main.add_child(type_box)
        self._main._child_offsets[id(type_box)] = (490.0, 8.0)

        type_box.add_child(ui.label("Type anything:", default_style=TextStyle(font_size=18, color=CYAN)))

        self._lbl_typed = ui.label("...", default_style=_TYPED)
        type_box.add_child(self._lbl_typed)
        type_box.add_child(ui.label("(BACKSPACE to delete)", default_style=_DIM))

        self._main._compute_layout()

    # ── update ───────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        # WASD Movement (PRESSED state - continuous)
        if self.root.keyboard.get_key(Keys.W):
            self.player_pos.y -= self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.S):
            self.player_pos.y += self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.A):
            self.player_pos.x -= self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.D):
            self.player_pos.x += self.speed * self.root.delta

        # Arrow keys also work
        if self.root.keyboard.get_key(Keys.UP):
            self.player_pos.y -= self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.DOWN):
            self.player_pos.y += self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.LEFT):
            self.player_pos.x -= self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.RIGHT):
            self.player_pos.x += self.speed * self.root.delta

        # JUST_PRESSED events (triggers once per press)
        if self.root.keyboard.get_key(Keys.SPACE, KeyState.JUST_PRESSED):
            self.messages.append("SPACE pressed!")
            self.player_pos.set(450, 300)

        if self.root.keyboard.get_key(Keys.ENTER, KeyState.JUST_PRESSED):
            self.messages.append("ENTER pressed!")

        # Number keys
        for i in range(10):
            key = getattr(Keys, f"NUM_{i}")
            if self.root.keyboard.get_key(key, KeyState.JUST_PRESSED):
                self.messages.append(f"Number {i} pressed!")

        # Function keys
        if self.root.keyboard.get_key(Keys.F1, KeyState.JUST_PRESSED):
            self.messages.append("F1 pressed!")

        # Modifiers
        if self.root.keyboard.get_key(Keys.LEFT_SHIFT):
            self.speed = 400.0
        else:
            self.speed = 200.0

        # Keep only last 8 messages
        self.messages = self.messages[-8:]

        # Quit with ESC
        if self.root.keyboard.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
            import glfw
            glfw.set_window_should_close(self.root.window, True)

        # --- Typed text via get_chars() -----------------------------------
        for ch in self.root.keyboard.get_chars():
            self.typed_text += ch
        if self.root.keyboard.get_key(Keys.BACKSPACE, KeyState.JUST_PRESSED):
            self.typed_text = self.typed_text[:-1]
        if len(self.typed_text) > self._TYPED_MAXLEN:
            self.typed_text = self.typed_text[-self._TYPED_MAXLEN:]

        # ── Update dynamic labels ────────────────────────────────────────
        # Event messages
        for i, lbl in enumerate(self._event_lbls):
            if i < len(self.messages):
                lbl.set_plain_text(f"  \u2022 {self.messages[i]}")
            else:
                lbl.set_plain_text("")

        # Status
        self._lbl_pos.set_plain_text(
            f"Position: ({self.player_pos.x:.0f}, {self.player_pos.y:.0f})")
        self._lbl_speed.set_plain_text(f"Speed: {self.speed:.0f} px/s")
        mp = self.root.mouse.position
        self._lbl_mouse.set_plain_text(f"Mouse: ({mp.x:.0f}, {mp.y:.0f})")

        # Speed colour feedback
        if self.speed > 200:
            self._lbl_speed.default_style = TextStyle(font_size=16, color=GREEN)
        else:
            self._lbl_speed.default_style = _STATUS

        # Typed text
        self._lbl_typed.set_plain_text(
            self.typed_text if self.typed_text else "...")

        self.frame += 1

    # ── draw ─────────────────────────────────────────────────────────────

    def draw(self) -> None:
        # Draw player circle
        self.root.draw_circle(self.player_pos, 20, color=BLUE,
                              border_color=WHITE, border_width=2.0)

        # Mouse cursor indicator
        mouse_pos = self.root.mouse.position
        self.root.draw_circle(mouse_pos, 8, color=YELLOW)

        # Mouse button feedback
        if self.root.mouse.get_button(MouseButtons.LEFT, KeyState.PRESSED):
            self.root.draw_circle(mouse_pos, 40, color=(1.0, 0.0, 0.0, 0.3))
        if self.root.mouse.get_button(MouseButtons.RIGHT, KeyState.PRESSED):
            self.root.draw_circle(mouse_pos, 40, color=(0.0, 1.0, 0.0, 0.3))
        if self.root.mouse.get_button(MouseButtons.MIDDLE, KeyState.PRESSED):
            self.root.draw_circle(mouse_pos, 40, color=(1.0, 1.0, 0.0, 0.3))


def main():
    """Run the input example"""
    config = WindowConfig(
        size=(900, 600),
        title="e2D Input Example",
        target_fps=60,
        vsync=False
    )
    root = RootEnv(config=config)
    env = InputExample(root)
    root.init(env)
    root.loop()

if __name__ == "__main__":
    main()
