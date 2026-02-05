from e2D import RootEnv, DefEnv
from e2D import WHITE, RED, GREEN, BLUE, Keys, KeyState
from e2D.vectors import Vector2D, V2

class MyApp(DefEnv):
    
    def __init__(self) -> None:
        ...
    
    def update(self) -> None:
        ...
    
    def draw(self) -> None:
        ...


# Create the window and rendering environment
root = RootEnv(
    window_size=V2(1920, 1080),  # Window width and height
    target_fps=60,              # Target frame rate
    title="My e2D App",         # Window title
    vsync=True,                 # Enable vertical sync
    resizable=False             # Allow window resizing
)

# Initialize your application
app = MyApp()
root.init(app)

# Optional: Enable screen recording (need e2D[rec] installation)
# root.init_rec(fps=30, draw_on_screen=True, path='recording.mp4')

# Start the main loop
root.loop()