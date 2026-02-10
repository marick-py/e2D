"""
Example demonstrating shape rendering in e2D
Shows circles, rectangles, lines, polylines, cached shapes, and instanced batching
"""

from e2D import (
    RootEnv, DefEnv, V2, WindowConfig,
    ShapeRenderer, ShapeLabel, InstancedShapeBatch,
    WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, TRANSPARENT
)

class ShapesExample(DefEnv):
    """Example showing various shape rendering techniques"""
    
    def __init__(self, root: RootEnv):
        self.root = root
        self.frame = 0
        
        # Cached shapes (create once, draw many times)
        self.cached_circle = None
        self.cached_rect = None
        
        # Instanced batches (draw thousands of shapes efficiently)
        self.circle_batch = None
        
    def update(self):
        self.frame += 1
        
    def draw(self):
        # Section 1: Basic Shapes
        self.root.print("Basic Shapes:", V2(10, 10), scale=1.2)
        
        # Circle with border
        self.root.draw_circle(
            V2(100, 80), 30,
            color=RED,
            border_color=WHITE,
            border_width=2.0
        )
        
        # Rectangle with rounded corners
        self.root.draw_rect(
            V2(250, 80), V2(60, 60),
            color=GREEN,
            corner_radius=10.0,
            border_color=WHITE,
            border_width=2.0
        )
        
        # Rectangle with anti-aliasing
        self.root.draw_rect(
            V2(400, 80), V2(60, 60),
            color=BLUE,
            corner_radius=5.0,
            antialiasing=True  # Smooth edges
        )
        
        # Section 2: Lines
        self.root.print("Lines & Polylines:", V2(10, 180), scale=1.2)
        
        # Simple line
        self.root.draw_line(
            V2(100, 250), V2(300, 250),
            width=5.0,
            color=YELLOW
        )
        
        # Polyline (connected lines)
        points = [
            V2(100, 320),
            V2(150, 370),
            V2(200, 320),
            V2(250, 370),
            V2(300, 320)
        ]
        self.root.draw_lines(points, width=3.0, color=CYAN)
        
        # Section 3: Cached Shapes (Performance Optimization)
        self.root.print("Cached Shapes (High Performance):", V2(10, 400), scale=1.2)
        
        # Create cached shapes once
        if self.cached_circle is None:
            self.cached_circle = self.root.create_circle(
                V2(100, 480), 25,
                color=MAGENTA,
                border_color=WHITE,
                border_width=2.0
            )
        
        if self.cached_rect is None:
            self.cached_rect = self.root.create_rect(
                V2(200, 480), V2(50, 50),
                color=CYAN,
                corner_radius=5.0
            )
        
        # Draw cached shapes (very fast, reuses GPU data)
        self.cached_circle.draw()
        self.cached_rect.draw()
        
        # Section 4: Instanced Batching (Draw THOUSANDS of shapes)
        self.root.print("Instanced Batching (100 circles):", V2(450, 10), scale=1.2)
        
        if self.circle_batch is None:
            self.circle_batch = self.root.create_circle_batch(max_shapes=100)
        
        # Clear and fill batch
        self.circle_batch.clear()
        
        # Add 100 circles with different colors
        for i in range(10):
            for j in range(10):
                self.circle_batch.add_circle(
                    V2(450 + i * 20, 60 + j * 20),
                    radius=8.0,
                    color=(i/10, j/10, 0.5, 1.0)
                )
        
        # Draw all at once (extremely fast!)
        self.circle_batch.flush()
        
        # Animation example
        self.root.print("Animated:", V2(450, 280), scale=1.2)
        
        import math
        t = self.frame * 0.05
        for i in range(8):
            angle = (i / 8) * 2 * math.pi + t
            x = 550 + math.cos(angle) * 50
            y = 380 + math.sin(angle) * 50
            self.root.draw_circle(
                V2(x, y), 10,
                color=(math.sin(t + i) * 0.5 + 0.5, 0.5, math.cos(t + i) * 0.5 + 0.5, 1.0)
            )
        
        # Instructions
        self.root.print("ESC to exit", V2(10, 560), scale=0.9)

def main():
    """Run the shapes example"""
    config = WindowConfig(
        size=(900, 600),
        title="e2D Shapes Example",
        target_fps=60,
        vsync=False
    )
    root = RootEnv(config=config)
    env = ShapesExample(root)
    root.init(env)
    root.loop()

if __name__ == "__main__":
    main()
