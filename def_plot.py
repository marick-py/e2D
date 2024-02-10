from e2D.plots import *
from e2D.winrec import *

class Env:
    def __init__(self) -> None:
        size = rootEnv.screen_size * .8
        position = rootEnv.screen_size * .1

        # self.plot = Plot(rootEnv, position, size, V2(-PI*5, 2), V2(PI*5, -2), V2(1,1) * 1)
        self.plot = Plot(rootEnv, position, size, V2(-10, 10), V2(10, -10), V2(1,1) * .5)

        self.plot.settings.multiple_set({
            "show_grid" : False,
            "grid_step" : V2(DOUBLE_PI, 1),
            "show_cursor_coords" : True,
            "show_pointer" : False,
            "show_zoom_info" : False,
            "change_axes_colors_on_mouse_hover" : False,
            "show_corners_coords" : False,
            "show_axes" : True
            # "use_real_time_rendering" : False,
        })
        # self.recorder = WinRec(rootEnv, fps=60)
        
        self.plot.add_function(MathFunction(lambda x,y: x**y - y**x))
        self.plot.add_function(MathFunction(lambda x,y: x - y, color=(255,0,0)))
        self.plot.add_object(Point(V2(5, 5), color=(255,127,0)))
        self.plot.add_object(Line(V2(-5, 5), V2(5, -5), color=(255,127,0)))

        self.plot.render()

    def draw(self) -> None:
        self.plot.draw()
        # self.recorder.draw(True)

    def update(self) -> None:
        self.plot.focus()
        self.plot.update()
        # self.recorder.update()

# (rootEnv:=RootEnv(V2(2560, 1440), target_fps=0, show_fps=False)).init(env:=Env())
(rootEnv:=RootEnv(V2(720, 720), target_fps=0, show_fps=True)).init(env:=Env())

# Vector2D.round_values_on_print = 2
# V2.round_values_on_print = 2

while not rootEnv.quit:
    rootEnv.frame()
# env.recorder.quit()