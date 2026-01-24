import moderngl
import numpy as np
from e2D import DefEnv, RootEnv
from e2D.text_renderer import Pivots, TextStyle

MAX_POINTS = 1_000_000

class Env(DefEnv):
    def __init__(self) -> None:
        self.MAX_POINTS = MAX_POINTS
        self.ctx = rootEnv.ctx
        
        # Load shaders from files
        self.prog1 = rootEnv.create_program_from_files(
            "shaders/point_vertex.glsl",
            "shaders/point_fragment.glsl",
            id="points"
        )
        self.compute = rootEnv.create_compute_shader_from_file(
            "shaders/particle_compute.glsl",
            id="point_update"
        )

        # Create initial points and velocities
        self.num_points = 1_000_000
        initial_points = np.random.rand(self.num_points, 2).astype("f4") * np.array(rootEnv.window_size, dtype="f4")
        initial_velocities = (np.random.rand(self.num_points, 2).astype("f4") - 0.5) * 100.0
        
        # Create compute buffers (SSBOs)
        self.points_buffer = rootEnv.create_buffer(initial_points, id="points", dynamic=True)
        self.velocities_buffer = rootEnv.create_buffer(initial_velocities, id="velocities", dynamic=True)
        
        # Create VAO for point rendering (no VBO needed, we use gl_VertexID to index SSBO)
        self.vao = self.ctx.vertex_array(self.prog1, [])
        
        # Set rendering uniforms
        rootEnv.get_uniform(self.prog1, "resolution").value = rootEnv.window_size_f
        rootEnv.get_uniform(self.prog1, "point_size").value = 3.0
        
        # Cache compute shader uniforms for cleaner access
        self.u_deltaTime = rootEnv.get_uniform(self.compute, "deltaTime")
        self.u_bounds = rootEnv.get_uniform(self.compute, "bounds")
        self.u_count = rootEnv.get_uniform(self.compute, "count")
        self.u_seed = rootEnv.get_uniform(self.compute, "seed")
        
        # Enable point size in shader
        self.ctx.enable(moderngl.PROGRAM_POINT_SIZE)
        self.ctx.enable(moderngl.BLEND)
        
        # Seed for random generation
        self.seed = np.random.randint(0, 2147483647, dtype=np.uint32)
    
    def draw(self) -> None:
        # Bind points buffer for vertex shader
        self.points_buffer.bind_to_storage_buffer(0)
        
        # Render points
        self.vao.render(moderngl.POINTS, vertices=self.num_points)
        
        # Draw FPS counter
        fps = 1.0 / rootEnv.delta if rootEnv.delta > 0 else 0
        rootEnv.print(f"FPS: {fps:.1f}", position=(20, 20), scale=0.5, pivot=Pivots.TOP_LEFT)
        rootEnv.print(f"Points: {self.num_points}", position=(20, 50), scale=0.5, pivot=Pivots.TOP_LEFT)

    def update(self) -> None:
        # Update seed
        self.seed = np.uint32((self.seed + 1) % 4294967295)
        
        # Clamp delta to reasonable values (prevent lag spikes when window is moved)
        dt = min(max(rootEnv.delta, 0.0001), 0.1)
        
        # Set compute shader uniforms using cached uniform objects
        self.u_deltaTime.value = float(dt)
        self.u_bounds.value = rootEnv.window_size_f
        self.u_count.value = self.num_points
        self.u_seed.value = int(self.seed)
        
        # Calculate work groups (256 threads per group)
        num_groups = (self.num_points + 255) // 256
        
        # Dispatch compute shader to update particle positions
        rootEnv.dispatch_compute(
            "point_update",
            groups_x=num_groups,
            buffers={
                0: "points",
                1: "velocities"
            }
        )

(rootEnv:=RootEnv(
    window_size=(1920, 1080),
    target_fps=0,
    vsync=False,
    version=(4,3)  # Compute shaders require OpenGL 4.3+
)).init(Env()).loop()
