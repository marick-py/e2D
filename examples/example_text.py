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
        
    def update(self, dt: float) -> None:
        self.frame += 1
        
    def draw(self) -> None:
        # Section 1: Basic Text
        self.root.print(
            "Text Rendering Examples",
            V2(10, 10),
            style=TextStyle(font_size=28)
        )
        
        # Section 2: Pivot Points — all 9 pivots on a well-spaced grid
        self.root.print("Pivot Points:", V2(10, 60), style=TextStyle(font_size=18))
        
        pivots_data = [
            (Pivots.TOP_LEFT,      "TOP_LEFT",      V2(60,  120)),
            (Pivots.TOP_MIDDLE,    "TOP_MIDDLE",     V2(280, 120)),
            (Pivots.TOP_RIGHT,     "TOP_RIGHT",      V2(500, 120)),
            (Pivots.LEFT,          "LEFT",           V2(60,  175)),
            (Pivots.CENTER,        "CENTER",         V2(280, 175)),
            (Pivots.RIGHT,         "RIGHT",          V2(500, 175)),
            (Pivots.BOTTOM_LEFT,   "BOTTOM_LEFT",    V2(60,  230)),
            (Pivots.BOTTOM_MIDDLE, "BOTTOM_MIDDLE",  V2(280, 230)),
            (Pivots.BOTTOM_RIGHT,  "BOTTOM_RIGHT",   V2(500, 230)),
        ]
        
        for pivot, name, pos in pivots_data:
            # Draw crosshair at the anchor point
            arm = 14
            self.root.draw_line(V2(pos.x - arm, pos.y), V2(pos.x + arm, pos.y),
                                width=1.0, color=(1.0, 0.3, 0.3, 0.6))
            self.root.draw_line(V2(pos.x, pos.y - arm), V2(pos.x, pos.y + arm),
                                width=1.0, color=(1.0, 0.3, 0.3, 0.6))
            self.root.draw_circle(pos, 3, color=RED)
            # Render label using that pivot so the red dot sits at the pivot
            self.root.print(
                name, pos, pivot=pivot,
                style=TextStyle(
                    font_size=14,
                    color=WHITE,
                    bg_color=(0.08, 0.08, 0.15, 0.85),
                    bg_margin=4.0,
                    bg_border_radius=3.0,
                ),
            )
        
        # Section 3: Text Styles
        self.root.print("Text Styles:", V2(10, 280), style=TextStyle(font_size=18))
        
        self.root.print(
            "Default Style (Sans-Serif)",
            V2(10, 310),
            style=DEFAULT_16_TEXT_STYLE
        )
        
        self.root.print(
            "Monospace Style (Courier)",
            V2(10, 340),
            style=MONO_16_TEXT_STYLE
        )
        
        # Section 4: Custom Styles
        self.root.print("Custom Styles:", V2(10, 380), style=TextStyle(font_size=18))
        
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
            V2(10, 410),
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
            V2(10, 455),
            style=custom_style_2
        )
        
        # Section 5: Cached Labels (High Performance)
        self.root.print("Cached Labels:", V2(10, 510), style=TextStyle(font_size=18))
        
        if self.cached_label is None:
            self.cached_label = self.root.print(
                "This label is cached for maximum performance!",
                V2(10, 540),
                style=MONO_16_TEXT_STYLE,
                save_cache=True
            )
        
        # Draw cached label (very fast, reuses GPU texture)
        if self.cached_label:
            self.cached_label.draw()
        
        # Section 6: Dynamic Text & Animation
        self.root.print("Dynamic Text:", V2(500, 280), style=TextStyle(font_size=18))
        
        self.root.print(
            f"Frame: {self.frame}",
            V2(500, 310)
        )
        
        fps = 1.0 / self.root.delta if self.root.delta > 0 else 0
        self.root.print(
            f"FPS: {fps:.1f}",
            V2(500, 340)
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
            V2(500, 380),
            style=animated_style
        )
        
        # Section 7: Unicode & International Characters
        # Use segoeui.ttf (Segoe UI) — excellent coverage for accented,
        # Greek, Cyrillic, and many other Unicode blocks.
        self.root.print("Unicode & International:", V2(500, 440), style=TextStyle(font_size=18))
        self.root.print(
            "Accented:  \u00e9 \u00e8 \u00ea \u00eb \u00f1 \u00fc \u00e7 \u00e0 \u00f6 \u00e5 \u00e4 \u00df \u00f8 \u00e6",
            V2(500, 470),
            style=TextStyle(font="segoeui.ttf", font_size=14, color=CYAN),
        )
        self.root.print(
            "Symbols:  \u00a9 \u00ae \u2122 \u00b0 \u00b1 \u00d7 \u00f7 \u2014 \u2026 \u00ab \u00bb \u00bf \u00a1",
            V2(500, 490),
            style=TextStyle(font="segoeui.ttf", font_size=14, color=CYAN),
        )
        self.root.print(
            "Greek:  \u0391\u0392\u0393\u0394\u03a3\u03a9  \u03b1\u03b2\u03b3\u03b4\u03c3\u03c9\u03c0\u03bc",
            V2(500, 510),
            style=TextStyle(font="segoeui.ttf", font_size=14, color=GREEN),
        )
        self.root.print(
            "Cyrillic:  \u041f\u0440\u0438\u0432\u0435\u0442  \u041c\u0438\u0440",
            V2(500, 530),
            style=TextStyle(font="segoeui.ttf", font_size=14, color=GREEN),
        )

        # Section 8: Emoji
        # Use seguiemj.ttf (Segoe UI Emoji) — native colour emoji on Windows.
        self.root.print("Emoji:", V2(500, 560), style=TextStyle(font_size=18))
        self.root.print(
            "\U0001f600 \U0001f680 \U0001f30d \u2b50 \U0001f525 \u2764 \U0001f389 \U0001f4a1",
            V2(500, 590),
            style=TextStyle(font="seguiemj.ttf", font_size=24),
        )

def main():
    """Run the text example"""
    config = WindowConfig(
        size=(900, 650),
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
