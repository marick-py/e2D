"""
Example demonstrating color system in e2D
Shows color creation, manipulation, pre-defined colors, and color operations
"""

from e2D import (
    RootEnv, DefEnv, V2, Color, WindowConfig,
    normalize_color, lerp_colors, gradient,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA,
    TextStyle
)
from e2D.color_defs import (
    MD_RED, MD_PINK, MD_PURPLE, MD_DEEP_PURPLE, MD_INDIGO,
    MD_BLUE, MD_LIGHT_BLUE, MD_CYAN, MD_TEAL, MD_GREEN,
    PASTEL_RED, PASTEL_ORANGE, PASTEL_YELLOW, PASTEL_GREEN,
    PASTEL_CYAN, PASTEL_BLUE, PASTEL_PURPLE, PASTEL_PINK,
    NEON_RED, NEON_GREEN, NEON_BLUE, NEON_PINK,
    UI_SUCCESS, UI_WARNING, UI_ERROR, UI_INFO
)

class ColorsExample(DefEnv):
    """Example showing color system features"""
    
    def __init__(self, root: RootEnv):
        self.root = root
        self.frame = 0
        
    def update(self):
        self.frame += 1
        
    def draw(self):
        # Title
        self.root.print("Color System Examples", V2(10, 10), scale=1.8)
        
        # Section 1: Basic Colors
        self.root.print("Basic Colors:", V2(10, 50), scale=1.2)
        
        basic_colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, BLACK]
        names = ["RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA", "WHITE", "BLACK"]
        
        for i, (color, name) in enumerate(zip(basic_colors, names)):
            x = 10 + i * 50
            self.root.draw_circle(V2(x + 20, 90), 15, color=color)
            self.root.print(name, V2(x, 115), scale=0.6)
        
        # Section 2: Material Design Colors
        self.root.print("Material Design Colors:", V2(10, 150), scale=1.2)
        
        md_colors = [
            MD_RED, MD_PINK, MD_PURPLE, MD_DEEP_PURPLE, MD_INDIGO,
            MD_BLUE, MD_LIGHT_BLUE, MD_CYAN, MD_TEAL, MD_GREEN
        ]
        
        for i, color in enumerate(md_colors):
            x = 10 + i * 40
            self.root.draw_circle(V2(x + 15, 190), 12, color=color)
        
        # Section 3: Pastel Colors
        self.root.print("Pastel Colors:", V2(10, 230), scale=1.2)
        
        pastel_colors = [
            PASTEL_RED, PASTEL_ORANGE, PASTEL_YELLOW, PASTEL_GREEN,
            PASTEL_CYAN, PASTEL_BLUE, PASTEL_PURPLE, PASTEL_PINK
        ]
        
        for i, color in enumerate(pastel_colors):
            x = 10 + i * 50
            self.root.draw_circle(V2(x + 20, 270), 15, color=color)
        
        # Section 4: Neon Colors
        self.root.print("Neon Colors:", V2(10, 310), scale=1.2)
        
        neon_colors = [NEON_RED, NEON_GREEN, NEON_BLUE, NEON_PINK]
        
        for i, color in enumerate(neon_colors):
            x = 10 + i * 60
            self.root.draw_circle(V2(x + 25, 350), 18, color=color)
        
        # Section 5: UI Colors
        self.root.print("UI Feedback Colors:", V2(10, 400), scale=1.2)
        
        ui_colors = [UI_SUCCESS, UI_WARNING, UI_ERROR, UI_INFO]
        ui_names = ["SUCCESS", "WARNING", "ERROR", "INFO"]
        
        for i, (color, name) in enumerate(zip(ui_colors, ui_names)):
            x = 10 + i * 90
            self.root.draw_rect(V2(x, 430), V2(70, 30), color=color, corner_radius=5.0)
            self.root.print(name, V2(x + 5, 435), scale=0.7)
        
        # Section 6: Color Operations
        self.root.print("Color Operations:", V2(500, 50), scale=1.2)
        
        base_color = Color.red()
        
        # Lightening
        self.root.print("Lighten:", V2(500, 90), scale=0.9)
        for i in range(5):
            lighter = base_color.lighten(i * 0.15)
            self.root.draw_circle(V2(500 + i * 30, 120), 12, color=lighter.to_rgba())
        
        # Darkening
        self.root.print("Darken:", V2(500, 150), scale=0.9)
        for i in range(5):
            darker = base_color.darken(i * 0.15)
            self.root.draw_circle(V2(500 + i * 30, 180), 12, color=darker.to_rgba())
        
        # Hue rotation
        self.root.print("Hue Rotation:", V2(500, 210), scale=0.9)
        for i in range(6):
            rotated = base_color.rotate_hue(i * 60)
            self.root.draw_circle(V2(500 + i * 30, 240), 12, color=rotated.to_rgba())
        
        # Section 7: Gradients
        self.root.print("Gradients:", V2(500, 280), scale=1.2)
        
        # Two-color gradient
        colors = gradient([RED, BLUE], 20)
        for i, color in enumerate(colors):
            self.root.draw_rect(V2(500 + i * 15, 310), V2(14, 30), color=color)
        
        # Multi-color gradient
        colors = gradient([RED, GREEN, BLUE], 20)
        for i, color in enumerate(colors):
            self.root.draw_rect(V2(500 + i * 15, 350), V2(14, 30), color=color)
        
        # Section 8: Animated Colors
        self.root.print("Animated:", V2(500, 400), scale=1.2)
        
        import math
        t = self.frame * 0.05
        
        # Rotating hue
        animated_color = Color.from_hsv(t % 1.0, 1.0, 1.0)
        self.root.draw_circle(V2(550, 440), 20, color=animated_color.to_rgba())
        
        # Pulsing brightness
        brightness = math.sin(t) * 0.3 + 0.7
        pulsing_color = Color.blue()
        self.root.draw_circle(V2(620, 440), 20, color=pulsing_color.to_rgba())
        
        # Fading alpha
        alpha = math.sin(t) * 0.5 + 0.5
        fading_color = Color.green().with_alpha(alpha)
        self.root.draw_circle(V2(690, 440), 20, color=fading_color.to_rgba())
        
        # Instructions
        self.root.print("ESC to exit", V2(10, 560), scale=0.9)

def main():
    """Run the colors example"""
    config = WindowConfig(
        size=(900, 600),
        title="e2D Colors Example",
        target_fps=60,
        vsync=False
    )
    root = RootEnv(config=config)
    env = ColorsExample(root)
    root.init(env)
    root.loop()

if __name__ == "__main__":
    main()
