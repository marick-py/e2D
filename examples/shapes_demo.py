import numpy as np
import glfw
from e2D import DefEnv, RootEnv, KeyState
from e2D.text_renderer import TextStyle, Pivots

class ShapesDemo(DefEnv):
    def __init__(self) -> None:
        self.ctx = rootEnv.ctx
        w, h = rootEnv.window_size
        
        # Animation parameters
        self.time = 0.0
        self.rotation = 0.0
        
        # ===== CACHED SHAPES (Created once, drawn many times) =====
        
        # Cached circle
        self.cached_circle = rootEnv.create_circle(
            center=(100, 100),
            radius=40,
            color=(1.0, 0.3, 0.3, 1.0),
            border_color=(1.0, 1.0, 1.0, 1.0),
            border_width=3.0
        )
        
        # Cached rounded rectangle
        self.cached_rect = rootEnv.create_rect(
            position=(200, 50),
            size=(120, 80),
            color=(0.3, 0.7, 1.0, 1.0),
            corner_radius=15.0,
            border_color=(1.0, 1.0, 1.0, 1.0),
            border_width=2.0
        )
        
        # Cached polyline (sine wave)
        x = np.linspace(0, 400, 100)
        y = 300 + 50 * np.sin(x * 0.05)
        points = np.column_stack([x + 50, y])
        self.cached_sine = rootEnv.create_lines(
            points=points,
            width=3.0,
            color=(0.2, 1.0, 0.5, 1.0)
        )
        
        # ===== BATCHED SHAPES (Many shapes in one draw call) =====
        
        # Circle batch for drawing many particles (INSTANCED = high performance!)
        self.circle_batch = rootEnv.create_circle_batch(max_shapes=10000)
        
        # Rectangle batch for drawing a grid (INSTANCED!)
        self.rect_batch = rootEnv.create_rect_batch(max_shapes=120)
        
        # Line batch for drawing a network (INSTANCED!)
        self.line_batch = rootEnv.create_line_batch(max_shapes=1000)
        
        # Generate random particles
        self.num_particles = 5000
        self.particle_positions = np.random.rand(self.num_particles, 2) * [w, h]
        self.particle_velocities = (np.random.rand(self.num_particles, 2) - 0.5) * 100
        self.particle_colors = np.random.rand(self.num_particles, 4)
        self.particle_colors[:, 3] = 0.8  # Alpha
        self.particle_radii = np.random.rand(self.num_particles) * 8 + 4
    
    def update(self) -> None:
        dt = rootEnv.delta
        self.time += dt
        self.rotation += dt * 0.5
        
        # Update particles
        self.particle_positions += self.particle_velocities * dt
        
        # Bounce off walls
        w, h = rootEnv.window_size
        for i in range(self.num_particles):
            if self.particle_positions[i, 0] < 0 or self.particle_positions[i, 0] > w:
                self.particle_velocities[i, 0] *= -1
            if self.particle_positions[i, 1] < 0 or self.particle_positions[i, 1] > h:
                self.particle_velocities[i, 1] *= -1
        
        # Clamp positions
        self.particle_positions[:, 0] = np.clip(self.particle_positions[:, 0], 0, w)
        self.particle_positions[:, 1] = np.clip(self.particle_positions[:, 1], 0, h)
    
    def draw(self) -> None:
        w, h = rootEnv.window_size
        
        # ===== SECTION 1: Cached Shapes =====
        # These were pre-created in __init__, just draw them
        self.cached_circle.draw()
        self.cached_rect.draw()
        self.cached_sine.draw()
        
        # ===== SECTION 2: Immediate Mode Drawing =====
        # These are drawn directly, useful for dynamic shapes
        
        # Animated rotating square
        rootEnv.draw_rect(
            position=(500, 80),
            size=(80, 80),
            color=(1.0, 0.8, 0.2, 1.0),
            rotation=self.rotation,
            corner_radius=10.0,
            border_color=(1.0, 0.0, 0.0, 1.0),
            border_width=3.0
        )
        
        # Pulsing circle
        pulse_radius = 30 + 15 * np.sin(self.time * 3)
        rootEnv.draw_circle(
            center=(650, 120),
            radius=pulse_radius,
            color=(0.8, 0.2, 1.0, 0.7)
        )
        
        # Simple lines forming a cross
        rootEnv.draw_line(
            start=(750, 80),
            end=(850, 180),
            width=3.0,
            color=(1.0, 1.0, 0.0, 1.0)
        )
        rootEnv.draw_line(
            start=(850, 80),
            end=(750, 180),
            width=3.0,
            color=(1.0, 1.0, 0.0, 1.0)
        )
        
        # Animated polyline (spiral)
        t = np.linspace(0, self.time * 2, 50)
        spiral_x = 950 + (t * 20) * np.cos(t * 2)
        spiral_y = 130 + (t * 20) * np.sin(t * 2)
        spiral_points = np.column_stack([spiral_x, spiral_y])
        rootEnv.draw_lines(
            points=spiral_points,
            width=2.0,
            color=(0.0, 1.0, 1.0, 1.0)
        )
        
        # ===== SECTION 3: Batched Drawing =====
        # Draw many shapes in a single draw call (VERY efficient)
        
        # Clear batches from previous frame
        self.circle_batch.clear()
        self.rect_batch.clear()
        self.line_batch.clear()
        
        # Add particles to circle batch using VECTORIZED method (much faster!)
        self.circle_batch.add_circles_numpy(
            centers=self.particle_positions,
            radii=self.particle_radii,
            colors=self.particle_colors
        )
        
        # Draw all particles in one call!
        self.circle_batch.flush()
        
        # Add grid of rectangles to rect batch
        grid_start_x, grid_start_y = 50, 450
        grid_size = 20
        grid_spacing = 25
        for i in range(15):
            for j in range(8):
                x = grid_start_x + i * grid_spacing
                y = grid_start_y + j * grid_spacing
                hue = (i + j) * 0.05 + self.time * 0.5
                color = (
                    0.5 + 0.5 * np.sin(hue),
                    0.5 + 0.5 * np.sin(hue + 2.1),
                    0.5 + 0.5 * np.sin(hue + 4.2),
                    0.9
                )
                self.rect_batch.add_rect(
                    center=(x + grid_size/2, y + grid_size/2),
                    size=(grid_size/2, grid_size/2),
                    color=color,
                    corner_radius=3.0
                )
        
        # Draw all rectangles in one call!
        self.rect_batch.flush()
        
        # Add network lines connecting nearby particles
        connection_dist = 150
        connections = 0
        for i in range(min(100, self.num_particles)):  # Limit for performance
            for j in range(i + 1, min(100, self.num_particles)):
                dist = np.linalg.norm(self.particle_positions[i] - self.particle_positions[j])
                if dist < connection_dist:
                    alpha = (1.0 - dist / connection_dist) * 0.3
                    self.line_batch.add_line(
                        start=tuple(self.particle_positions[i]),
                        end=tuple(self.particle_positions[j]),
                        width=1.0,
                        color=(0.5, 0.5, 1.0, float(alpha))
                    )
                    connections += 1
        
        # Draw all lines in one call!
        self.line_batch.flush()
        
        # ===== UI Overlay =====
        fps = 1.0 / rootEnv.delta if rootEnv.delta > 0 else 0
        rootEnv.print(f"FPS: {fps:.1f}", (10, 10), scale=0.5, 
                     style=TextStyle(color=(0.0, 1.0, 0.0, 1.0)))
        rootEnv.print(f"Particles: {self.num_particles}", (10, 40), scale=0.4,
                     style=TextStyle(color=(1.0, 1.0, 1.0, 1.0)))
        rootEnv.print(f"Connections: {connections}", (10, 65), scale=0.4,
                     style=TextStyle(color=(1.0, 1.0, 1.0, 1.0)))
        
        # Legend
        legend_y = h - 150
        rootEnv.print("Shape Demo", (10, legend_y), scale=0.45,
                     style=TextStyle(color=(1.0, 1.0, 0.0, 1.0)))
        rootEnv.print("Top: Cached & Immediate shapes", (10, legend_y + 30), scale=0.35,
                     style=TextStyle(color=(0.8, 0.8, 0.8, 1.0)))
        rootEnv.print("Center: Batched particles", (10, legend_y + 55), scale=0.35,
                     style=TextStyle(color=(0.8, 0.8, 0.8, 1.0)))
        rootEnv.print("Bottom: Batched grid", (10, legend_y + 80), scale=0.35,
                     style=TextStyle(color=(0.8, 0.8, 0.8, 1.0)))
        rootEnv.print("Press X to exit", (10, legend_y + 105), scale=0.35,
                     style=TextStyle(color=(1.0, 0.5, 0.5, 1.0)))

# Initialize and run
rootEnv = RootEnv(
    window_size=(1920, 1080),
    target_fps=0,
    vsync=False,
    version=(4, 3)
)
rootEnv.init(ShapesDemo()).loop()

