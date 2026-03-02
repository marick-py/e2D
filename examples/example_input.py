"""
Example demonstrating keyboard and mouse input in e2D.

Shows Keys class, MouseButtons class, KeyState (PRESSED / JUST_PRESSED /
JUST_RELEASED), and the new get_chars() typed-text API.
"""

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    Keyboard, Mouse, Keys, MouseButtons, KeyState,
    WHITE, RED, GREEN, BLUE, YELLOW, CYAN, TextStyle
)

class InputExample(DefEnv):
    """Example showing keyboard and mouse input handling"""
    
    def __init__(self, root: RootEnv):
        self.root = root
        self.frame = 0
        self.messages = []
        self.player_pos = V2(450, 300)
        self.speed = 200.0
        # Typed-text buffer (updated via get_chars each frame)
        self.typed_text: str = ""
        self._TYPED_MAXLEN = 60
        
    def update(self):
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
            self.player_pos.set(450, 300)  # Reset position
        
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
            self.speed = 400.0  # Run when holding shift
        else:
            self.speed = 200.0
        
        # Keep only last 8 messages
        self.messages = self.messages[-8:]
        
        # Quit with ESC
        if self.root.keyboard.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
            import glfw
            glfw.set_window_should_close(self.root.window, True)
        
        # --- Typed text via get_chars() -----------------------------------
        # get_chars() returns all Unicode characters typed this frame.
        # BACKSPACE is a control key (not a char), so handle it separately.
        for ch in self.root.keyboard.get_chars():
            self.typed_text += ch
        if self.root.keyboard.get_key(Keys.BACKSPACE, KeyState.JUST_PRESSED):
            self.typed_text = self.typed_text[:-1]
        if len(self.typed_text) > self._TYPED_MAXLEN:
            self.typed_text = self.typed_text[-self._TYPED_MAXLEN:]

        self.frame += 1
    
    def draw(self):
        # Draw player
        self.root.draw_circle(self.player_pos, 20, color=BLUE, border_color=WHITE, border_width=2.0)
        
        # Draw mouse cursor indicator
        mouse_pos = self.root.mouse.position
        self.root.draw_circle(mouse_pos, 8, color=YELLOW)
        
        # Mouse button feedback
        if self.root.mouse.get_button(MouseButtons.LEFT, KeyState.PRESSED):
            self.root.draw_circle(mouse_pos, 40, color=(1.0, 0.0, 0.0, 0.3))
        
        if self.root.mouse.get_button(MouseButtons.RIGHT, KeyState.PRESSED):
            self.root.draw_circle(mouse_pos, 40, color=(0.0, 1.0, 0.0, 0.3))
        
        if self.root.mouse.get_button(MouseButtons.MIDDLE, KeyState.PRESSED):
            self.root.draw_circle(mouse_pos, 40, color=(1.0, 1.0, 0.0, 0.3))
        
        # Instructions
        self.root.print("Input Handling Example", V2(10, 10), scale=1.5)
        
        instructions = [
            "",
            "Keyboard:",
            "  WASD / Arrow Keys - Move blue circle",
            "  SHIFT - Hold to run faster",
            "  SPACE - Reset position",
            "  ENTER - Trigger event",
            "  0-9 - Number keys",
            "  F1 - Function key",
            "  ESC - Exit",
            "",
            "Mouse:",
            "  Left/Right/Middle Click - Show colored circle",
            "",
            "Type text (right panel):",
            "  Any key - append character",
            "  BACKSPACE - delete last character",
            "",
            "Recent Events:"
        ]
        
        y = 40
        for line in instructions:
            self.root.print(line, V2(10, y), scale=0.9)
            y += 20
        
        # Draw event messages
        event_style = TextStyle(font_size=16, color=YELLOW)
        for msg in self.messages:
            self.root.print(f"  • {msg}", V2(10, y), scale=0.9, style=event_style)
            y += 18
        
        # Draw player status
        self.root.print("Player Status:", V2(10, 500), scale=1.1)
        self.root.print(
            f"Position: ({self.player_pos.x:.0f}, {self.player_pos.y:.0f})",
            V2(10, 525),
            scale=0.9
        )
        self.root.print(
            f"Speed: {self.speed:.0f} px/s",
            V2(10, 545),
            scale=0.9,
            style=TextStyle(font_size=16, color=GREEN if self.speed > 200 else WHITE)
        )
        
        # Draw mouse status
        self.root.print(
            f"Mouse: ({mouse_pos.x:.0f}, {mouse_pos.y:.0f})",
            V2(10, 570),
            scale=0.9
        )

        # ---- Typed text demo (get_chars) ---------------------------------
        self.root.print("Type anything:", V2(500, 40), scale=1.1, style=TextStyle(font_size=18, color=CYAN))
        # Box outline
        self.root.draw_rect(V2(500, 65), V2(380, 32),
                            color=(0.1, 0.1, 0.15, 1.0),
                            border_color=(0.4, 0.8, 1.0, 0.9),
                            border_width=1.5)
        display = self.typed_text if self.typed_text else "..."
        self.root.print(
            display,
            V2(508, 73),
            scale=0.9,
            style=TextStyle(font_size=16, color=WHITE)
        )
        self.root.print(
            "(BACKSPACE to delete)",
            V2(500, 104),
            scale=0.8,
            style=TextStyle(font_size=14, color=(0.6, 0.6, 0.6, 1.0))
        )

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
