from e2D.plots import Plot2D, PlotSettings, CurveSettings, ImplicitSettings, StreamSettings, LineType, GpuStream, ComputeCurve, ImplicitPlot
from e2D import DefEnv, RootEnv, KeyState
import numpy as np
import glfw

from e2D.text_renderer import TextStyle

class GraphEnv(DefEnv):
    def __init__(self) -> None:
        self.ctx = rootEnv.ctx
        w, h = rootEnv.window_size
        
        # FPS Display
        self.current_fps :float= 0.0

        # Main Plot: Takes up most of the screen (Top part)
        main_settings = PlotSettings(
            bg_color=(0.05, 0.05, 0.05, 1.0),
            show_grid=True,
            grid_color=(0.15, 0.15, 0.15, 1.0),
            grid_spacing=1.0,
            show_axis=True,
            axis_color=(0.3, 0.3, 0.3, 1.0)
        )
        self.plot_main = Plot2D(self.ctx, (100, 0), (w, h//2), settings=main_settings)
        
        # FPS Plot: Bottom strip
        fps_settings = PlotSettings(
            bg_color=(0.0, 0.0, 0.0, 1.0),
            show_grid=True,
            grid_color=(0.2, 0.2, 0.2, 1.0),
            grid_spacing=1.0,
            show_axis=True
        )
        self.plot_fps = Plot2D(self.ctx, (0, h//2), (w, h), settings=fps_settings)
    
        # Real-time Data Stream (FPS Tracker)
        stream_settings = StreamSettings(
            point_color=(1.0, 0.2, 0.2, 1.0),
            point_radius=5.0,
            show_points=True,
            line_type=LineType.SMOOTH,
            line_color=(1.0, 1.0, 0.0, 1.0),
            line_width=5.0
        )
        self.stream = GpuStream(self.ctx, capacity=10_000, settings=stream_settings)
        
        # Parametric Curve (Lissajous)
        curve_settings = CurveSettings(
            color=(0.2, 1.0, 0.5, 1.0),
            width=2.0
        )
        code_param = """
        x = sin(3.0 * t);
        y = cos(5.0 * t);
        """
        self.curve = ComputeCurve(self.ctx, code_param, t_range=(0, 2*np.pi), count=2048, settings=curve_settings)
        self.curve.update()
        
        # Implicit Function (Circle)
        implicit_settings = ImplicitSettings(
            color=(0.4, 0.6, 1.0, 1.0),
            thickness=2.0
        )
        code_implicit = """
        val = x*x + y*y - 0.25; // Radius 0.5 circle
        """
        self.implicit = ImplicitPlot(self.ctx, code_implicit, settings=implicit_settings)
        
        code_implicit = """
        val = x*x - y; // Radius 0.5 circle
        """
        self.implicit_sqr = ImplicitPlot(self.ctx, code_implicit, settings=implicit_settings)

        # Initial resize to ensure viewports are correct
        self.on_resize(w, h)
        
        self.last_time = glfw.get_time()
        self.frame_count = 0
        self.fps_update_time = self.last_time

    def on_resize(self, width: int, height: int) -> None:
        # Layout:
        # FPS Plot: Bottom self.fps_height px
        # Main Plot: Top (Height - self.fps_height px)

        main_height = height // 2
        if main_height < 100: main_height = 100 # Minimum height
        
        self.plot_main.set_rect((0, 0), (width, main_height))
        self.plot_main.update_window_size(width, height)
        
        self.plot_fps.set_rect((0, main_height), (width, height))
        self.plot_fps.update_window_size(width, height)
        
        # Set FPS plot view to show history
        # Center at (-10, 1.0), Zoom to fit width 20
        self.plot_fps.view.center = np.array([-10.0, 1.0], dtype='f4')
        self.plot_fps.view.zoom = 0.1 
        self.plot_fps.view.update_buffer()

    def update(self) -> None:
        # FPS Calculation
        current_time = glfw.get_time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        fps = 1.0 / dt if dt > 0 else 60.0
        self.current_fps = fps
        
        # Shift existing points to the left
        # Shift by -0.1 units per frame
        # self.stream.shift_points((-0.1, 0.0))
        
        new_points = np.array([[current_time * 100, fps]], dtype='f4')
        self.stream.push(new_points)

        # Input Handling
        mouse = rootEnv.mouse
        
        # Scroll
        if mouse.scroll != (0, 0):
            x, y = mouse.position
            if self.plot_fps.contains(x, y):
                self.plot_fps.on_scroll(mouse.scroll[1], x, y)
            elif self.plot_main.contains(x, y):
                self.plot_main.on_scroll(mouse.scroll[1], x, y)
        
        # Mouse Button (Dragging start/end)
        if mouse.get_button(glfw.MOUSE_BUTTON_LEFT, KeyState.JUST_PRESSED):
            x, y = mouse.position
            if self.plot_fps.contains(x, y):
                self.plot_fps.is_dragging = True
                self.plot_fps.last_mouse_pos = (x, y)
            elif self.plot_main.contains(x, y):
                self.plot_main.is_dragging = True
                self.plot_main.last_mouse_pos = (x, y)
        
        if mouse.get_button(glfw.MOUSE_BUTTON_LEFT, KeyState.JUST_RELEASED):
             self.plot_main.is_dragging = False
             self.plot_fps.is_dragging = False
             
        # Mouse Move (Dragging)
        if self.plot_main.is_dragging:
            dx, dy = mouse.delta
            self.plot_main.on_mouse_drag(dx, dy)
            
        if self.plot_fps.is_dragging:
            dx, dy = mouse.delta
            self.plot_fps.on_mouse_drag(dx, dy)

    def draw(self) -> None:
        # 1. Render Main Plot
        def draw_main() -> None:
            self.implicit.draw()
            self.implicit_sqr.draw()
            self.curve.draw()

        self.plot_main.render(draw_main)
        
        # 2. Render FPS Plot
        def draw_fps() -> None:
            self.stream.draw()
        self.plot_fps.render(draw_fps)
        
        # 3. Render FPS Overlay
        self.ctx.viewport = (0, 0, rootEnv.window_size[0], rootEnv.window_size[1])
        self.ctx.scissor = None
        rootEnv.print(f"FPS: {int(self.current_fps)}", (10, 10), scale=0.4, style=TextStyle(color=(0.0, 1.0, 0.0, 1.0)))

# Initialize RootEnv with OpenGL 4.3 for Compute Shaders
rootEnv = RootEnv(
    window_size=(1920, 1080),
    version=(4,3),
    target_fps=144,  # Limit to 144 FPS
    vsync=False
)

# Start App
rootEnv.init(GraphEnv()).loop()

