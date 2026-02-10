"""
Example demonstrating vector operations in e2D
Shows Vector2D creation, operations, batch processing, and performance
"""

from e2D import (
    RootEnv, DefEnv, V2, Vector2D, CommonVectors, WindowConfig,
    batch_add_inplace, batch_scale_inplace, batch_normalize_inplace,
    vectors_to_array, create_circle, lerp,
    WHITE, RED, GREEN, BLUE, YELLOW, CYAN
)
import math

class VectorsExample(DefEnv):
    """Example showing vector operations and batch processing"""
    
    def __init__(self, root: RootEnv):
        self.root = root
        self.frame = 0
        
        # Create particle system using vectors
        self.num_particles = 500
        self.positions = [Vector2D.random(100, 800) for _ in range(self.num_particles)]
        self.velocities = [Vector2D.random(-50, 50) for _ in range(self.num_particles)]
        
        # Arrow for vector visualization
        self.arrow_start = V2(100, 100)
        self.arrow_vector = V2(100, 50)
        
    def update(self):
        self.frame += 1
        
        # Update particle system using batch operations (VERY FAST!)
        dt = self.root.delta
        
        # Calculate displacements
        for i in range(self.num_particles):
            # Add velocity to position (in-place for performance)
            temp = self.velocities[i].mul(dt)
            self.positions[i].iadd(temp)
            
            # Bounce off walls
            if self.positions[i].x < 50 or self.positions[i].x > 850:
                self.velocities[i].x *= -1
            if self.positions[i].y < 50 or self.positions[i].y > 550:
                self.velocities[i].y *= -1
        
        # Animate arrow
        t = self.frame * 0.03
        self.arrow_vector.set(math.cos(t) * 100, math.sin(t) * 100)
        
    def draw(self):
        # Title
        self.root.print("Vector Operations Example", V2(10, 10), scale=1.5)
        
        # Section 1: Basic Vector Visualization
        self.root.print(f"Particle System ({self.num_particles} particles):", V2(10, 40), scale=1.0)
        
        # Draw particles
        for i, pos in enumerate(self.positions):
            # Color based on velocity
            speed = self.velocities[i].length
            color_t = min(speed / 100.0, 1.0)
            color = lerp(BLUE, RED, color_t)
            self.root.draw_circle(pos, 3, color=color)
        
        # Section 2: Vector Operations Visualization
        self.root.print("Vector Operations:", V2(450, 250), scale=1.2)
        
        # Draw arrow showing a vector
        arrow_end = V2(self.arrow_start.x + self.arrow_vector.x, 
                       self.arrow_start.y + self.arrow_vector.y)
        
        self.root.draw_line(self.arrow_start, arrow_end, width=3.0, color=YELLOW)
        self.root.draw_circle(self.arrow_start, 5, color=GREEN)
        self.root.draw_circle(arrow_end, 5, color=RED)
        
        # Show vector info
        length = self.arrow_vector.length
        angle = math.degrees(math.atan2(self.arrow_vector.y, self.arrow_vector.x))
        
        self.root.print(f"Vector: ({self.arrow_vector.x:.1f}, {self.arrow_vector.y:.1f})", 
                       V2(450, 290), scale=0.9)
        self.root.print(f"Length: {length:.1f}", V2(450, 310), scale=0.9)
        self.root.print(f"Angle: {angle:.1f}°", V2(450, 330), scale=0.9)
        
        # Section 3: Common Vectors
        self.root.print("Common Vectors:", V2(450, 370), scale=1.2)
        
        common_vecs = [
            (CommonVectors.ZERO, "ZERO", V2(450, 400)),
            (CommonVectors.UP, "UP", V2(550, 400)),
            (CommonVectors.DOWN, "DOWN", V2(650, 400)),
            (CommonVectors.LEFT, "LEFT", V2(450, 440)),
            (CommonVectors.RIGHT, "RIGHT", V2(550, 440)),
        ]
        
        for vec, name, pos in common_vecs:
            # Draw vector arrow
            end = V2(pos.x + vec.x * 20, pos.y + vec.y * 20)
            if vec.length > 0:
                self.root.draw_line(pos, end, width=2.0, color=CYAN)
            self.root.draw_circle(pos, 3, color=WHITE)
            self.root.print(name, V2(pos.x - 15, pos.y + 15), scale=0.7)
        
        # Section 4: Performance Info
        fps = 1.0 / self.root.delta if self.root.delta > 0 else 0
        self.root.print(f"FPS: {fps:.1f}", V2(10, 560), scale=1.0)
        self.root.print(f"Frame: {self.frame}", V2(150, 560), scale=1.0)
        
        # Instructions
        self.root.print("ESC to exit", V2(750, 560), scale=0.9)

def main():
    """Run the vectors example"""
    config = WindowConfig(
        size=(900, 600),
        title="e2D Vectors Example",
        target_fps=60,
        vsync=False
    )
    root = RootEnv(config=config)
    env = VectorsExample(root)
    root.init(env)
    root.loop()

if __name__ == "__main__":
    main()
