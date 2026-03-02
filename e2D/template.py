from e2D import RootEnv, DefEnv, WindowConfig
from e2D.input import Keys, KeyState
from e2D.palette import WHITE, RED, GREEN, BLUE, get_color
from e2D.vectors import Vector2D, V2

class MyApp(DefEnv):
    
    def __init__(self) -> None:
        ...
    
    def update(self) -> None:
        ...
    
    def draw(self) -> None:
        ...


win_conf = WindowConfig(
    size=V2(1920, 1080),
    target_fps=60,
    title="My e2D App",
    vsync=True,
    resizable=False
)
rootEnv = RootEnv(config=win_conf)
rootEnv.init(env:=MyApp())

# Optional: Enable screen recording (need e2D[rec] installation)
# root.init_rec(fps=30, draw_on_screen=True, path='recording.mp4')
rootEnv.loop()
