"""
Example demonstrating text rendering in e2D
Shows basic text, styles, pivots, cached labels, and backgrounds
"""

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    TextRenderer, TextLabel, TextStyle, Pivots,
    DEFAULT_16_TEXT_STYLE, MONO_16_TEXT_STYLE,
    WHITE, BLACK, RED, BLUE, GREEN, YELLOW, CYAN
)

class TextExample(DefEnv):
    """Example showing various text rendering features"""
    
    def __init__(self, root: RootEnv):
        self.root = root
        self.frame = 0
        self.cached_label = None
        
    def update(self):
        self.frame += 1
        
    def draw(self):
        # Section 1: Basic Text
        self.root.print(
            "Text Rendering Examples",
            V2(10, 10),
            scale=2.0,
            style=DEFAULT_16_TEXT_STYLE
        )
        
        # Section 2: Different Pivots
        self.root.print("Pivot Points:", V2(10, 60), scale=1.2)
        
        # Draw a cross to show pivot position
        pivot_pos = V2(400, 120)
        self.root.draw_line(V2(380, 120), V2(420, 120), width=1.0, color=RED)
        self.root.draw_line(V2(400, 100), V2(400, 140), width=1.0, color=RED)
        
        pivots = [
            (Pivots.TOP_LEFT, "TOP_LEFT", V2(400, 90)),
            (Pivots.TOP_MIDDLE, "TOP_MIDDLE", V2(400, 120)),
            (Pivots.CENTER, "CENTER", V2(400, 150)),
        ]
        
        for pivot, name, pos in pivots:
            self.root.print(name, pos, scale=1.0, pivot=pivot)
        
        # Section 3: Text Styles
        self.root.print("Text Styles:", V2(10, 200), scale=1.2)
        
        self.root.print(
            "Default Style (Sans-Serif)",
            V2(10, 230),
            style=DEFAULT_16_TEXT_STYLE
        )
        
        self.root.print(
            "Monospace Style (Courier)",
            V2(10, 260),
            style=MONO_16_TEXT_STYLE
        )
        
        # Section 4: Custom Styles
        self.root.print("Custom Styles:", V2(10, 310), scale=1.2)
        
        custom_style_1 = TextStyle(
            font="arial.ttf",
            font_size=24,
            color=RED,
            bg_color=(0.0, 0.0, 0.0, 0.8),
            bg_margin=10.0,
            bg_border_radius=8.0
        )
        
        self.root.print(
            "Red Text with Dark Background",
            V2(10, 340),
            style=custom_style_1
        )
        
        custom_style_2 = TextStyle(
            font="arial.ttf",
            font_size=20,
            color=YELLOW,
            bg_color=(0.0, 0.5, 1.0, 0.7),
            bg_margin=15.0,
            bg_border_radius=12.0
        )
        
        self.root.print(
            "Yellow Text with Blue Background",
            V2(10, 380),
            style=custom_style_2
        )
        
        # Section 5: Cached Labels (High Performance)
        self.root.print("Cached Labels:", V2(10, 440), scale=1.2)
        
        if self.cached_label is None:
            self.cached_label = self.root.print(
                "This label is cached for maximum performance!",
                V2(10, 470),
                scale=1.0,
                style=MONO_16_TEXT_STYLE,
                save_cache=True
            )
        
        # Draw cached label (very fast, reuses GPU texture)
        if self.cached_label:
            self.cached_label.draw()
        
        # Section 6: Dynamic Text & Animation
        self.root.print("Dynamic Text:", V2(500, 200), scale=1.2)
        
        self.root.print(
            f"Frame: {self.frame}",
            V2(500, 230),
            scale=1.0
        )
        
        fps = 1.0 / self.root.delta if self.root.delta > 0 else 0
        self.root.print(
            f"FPS: {fps:.1f}",
            V2(500, 260),
            scale=1.0
        )
        
        # Animated color text
        import math
        t = self.frame * 0.05
        color_r = math.sin(t) * 0.5 + 0.5
        color_g = math.sin(t + 2) * 0.5 + 0.5
        color_b = math.sin(t + 4) * 0.5 + 0.5
        
        animated_style = TextStyle(
            font="arial.ttf",
            font_size=28,
            color=(color_r, color_g, color_b, 1.0)
        )
        
        self.root.print(
            "Animated Color!",
            V2(500, 300),
            style=animated_style
        )
        
        # Section 7: Unicode Support
        self.root.print("Unicode:", V2(500, 360), scale=1.2)
        self.root.print("Hello World! 你好世界! مرحبا بالعالم!", V2(500, 390), scale=0.8)
        self.root.print("Emoji: 🎮 🚀 ⭐ 💎", V2(500, 420), scale=1.0)
        
        # Instructions
        self.root.print("ESC to exit", V2(10, 560), scale=0.9)

def main():
    """Run the text example"""
    config = WindowConfig(
        size=(900, 600),
        title="e2D Text Example",
        target_fps=60,
        vsync=False
    )
    root = RootEnv(config=config)
    env = TextExample(root)
    root.init(env)
    root.loop()

if __name__ == "__main__":
    main()
