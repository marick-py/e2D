"""
Example demonstrating the new Keys and MouseButtons classes for better autocompletion
"""

from e2D import RootEnv, DefEnv, V2, Keys, MouseButtons, KeyState, WHITE, RED, GREEN, BLUE, YELLOW

class KeysDemo(DefEnv):
    def __init__(self, root: RootEnv):
        self.root = root
        self.circle_pos = V2(400, 300)
        self.speed = 300.0
        self.message = "Use WASD to move, SPACE to reset, ESC to quit"
        
    def update(self):
        # Movement with WASD keys - notice the clean autocompletion!
        if self.root.keyboard.get_key(Keys.W):
            self.circle_pos.y -= self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.S):
            self.circle_pos.y += self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.A):
            self.circle_pos.x -= self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.D):
            self.circle_pos.x += self.speed * self.root.delta
        
        # Arrow keys also work
        if self.root.keyboard.get_key(Keys.UP):
            self.circle_pos.y -= self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.DOWN):
            self.circle_pos.y += self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.LEFT):
            self.circle_pos.x -= self.speed * self.root.delta
        if self.root.keyboard.get_key(Keys.RIGHT):
            self.circle_pos.x += self.speed * self.root.delta
        
        # Reset position with SPACE (JUST_PRESSED means it triggers once per press)
        if self.root.keyboard.get_key(Keys.SPACE, KeyState.JUST_PRESSED):
            self.circle_pos.set(400, 300)
            self.message = "Position reset!"
        
        # Quit with ESC
        if self.root.keyboard.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
            import glfw
            glfw.set_window_should_close(self.root.window, True)
        
        # Number keys change message
        if self.root.keyboard.get_key(Keys.NUM_1, KeyState.JUST_PRESSED):
            self.message = "You pressed 1!"
        if self.root.keyboard.get_key(Keys.NUM_2, KeyState.JUST_PRESSED):
            self.message = "You pressed 2!"
        if self.root.keyboard.get_key(Keys.NUM_3, KeyState.JUST_PRESSED):
            self.message = "You pressed 3!"
    
    def draw(self):
        # Draw moving circle
        self.root.draw_circle(self.circle_pos, 30, color=BLUE)
        
        # Show controls
        self.root.print(self.message, V2(10, 10), scale=1.2)
        self.root.print(f"Position: ({self.circle_pos.x:.0f}, {self.circle_pos.y:.0f})", V2(10, 40), scale=1.0)
        
        # Mouse button demo
        if self.root.mouse.get_button(MouseButtons.LEFT, KeyState.PRESSED):
            self.root.draw_circle(self.root.mouse.position, 20, color=RED)
            self.root.print("Left Click!", V2(10, 70), scale=1.0)
        
        if self.root.mouse.get_button(MouseButtons.RIGHT, KeyState.PRESSED):
            self.root.draw_circle(self.root.mouse.position, 20, color=GREEN)
            self.root.print("Right Click!", V2(10, 70), scale=1.0)
        
        if self.root.mouse.get_button(MouseButtons.MIDDLE, KeyState.PRESSED):
            self.root.draw_circle(self.root.mouse.position, 20, color=YELLOW)
            self.root.print("Middle Click!", V2(10, 70), scale=1.0)
        
        # Draw mouse cursor position indicator
        self.root.draw_circle(self.root.mouse.position, 5, color=WHITE)

if __name__ == "__main__":
    root = RootEnv(window_size=V2(800, 600), target_fps=60)
    env = KeysDemo(root)
    root.init(env)
    root.loop()
