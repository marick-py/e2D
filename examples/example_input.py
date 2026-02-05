"""
Example demonstrating keyboard and mouse input in e2D
Shows Keys class, MouseButtons class, and input states (PRESSED, JUST_PRESSED, JUST_RELEASED)
"""

from e2D import (
    RootEnv, DefEnv, V2,
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

def main():
    """Run the input example"""
    root = RootEnv(window_size=V2(900, 600), target_fps=60, title="e2D Input Example")
    env = InputExample(root)
    root.init(env)
    root.loop()

if __name__ == "__main__":
    main()
