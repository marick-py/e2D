from __future__ import annotations
from .envs import *
import numpy as np

def no_error_complex_function(function, args) -> V2|Vector2D:
    res :complex= function(args)
    return V2(res.real, res.imag)

sign = lambda value: -1 if value < 0 else (1 if value > 0 else 0)

class Function:
    def __init__(self, function, color) -> None:
        self.plot : Plot
        self.color = color
        self.function = function
        self.__layer_surface__ :pg.Surface= None #type: ignore
    
    def update_points(self) -> None:
        self.update_function(self.function)

    def get_points(self) -> list:
        signs_self = np.sign(self.function(*self.plot.meshgrid))
        signs_sum = signs_self + np.roll(signs_self, axis=1, shift=1) + np.roll(signs_self, axis=0, shift=-1) + np.roll(signs_self, axis=(1,0), shift=(1,-1))
        return np.column_stack(np.where(((-4 < signs_sum) & (signs_sum < 4))[:-1, 1:])[::-1]) / self.plot.scale()
    
    def update_function(self, new_function) -> None:
        self.function = new_function
        self.points = self.get_points()
        self.render()
    
    def render(self) -> None:
        self.__layer_surface__.fill((0,0,0,0))
        # print(self.plot.dra)
        offset = self.plot.dragging - self.plot.start_dragging if (self.plot.dragging != None) and (not self.plot.settings.get("use_real_time_rendering")) else V2z
        if any(x < 1 for x in self.plot.scale):
            # draw rects
            for point in self.points:
                pg.draw.rect(self.__layer_surface__, self.color, (point.tolist() + offset)() + self.plot.pixel_size()) #type: ignore
        else:
            # draw points
            for point in self.points:
                point = point.astype(int).tolist()
                if self.plot.dragging != None:
                    point = round(point + offset)()
                self.__layer_surface__.set_at(point, self.color)
    
    def draw(self) -> None:
        self.plot.canvas.blit(self.__layer_surface__, (0,0))

# class ComplexFunction:
#     def __init__(self, function, plot:"Plot", starting_t:float=-10, ending_t:float=10, step=.01, color=(255,255,255), auto_connect_treshold=float("inf"), points_radius=2, points_color=None) -> None:
#         self.auto_connect_treshold = auto_connect_treshold
#         self.plot = plot
#         self.starting_t = starting_t
#         self.ending_t = ending_t
#         self.color = color
#         self.step = step
#         self.points_color = points_color
#         self.points_radius = points_radius
#         self.update_function(function)
    
#     def update_points(self) -> None:
#         self.update_function(self.function)
    
#     def update_function(self, new_function) -> None:
#         self.function = new_function
#         self.points :list[V2|Vector2D]= [point for t in range(int(self.starting_t / self.step), int(self.ending_t / self.step)) if (self.plot.bottom_right_y < (point:=no_error_complex_function(new_function, t * self.step)).y < self.plot.top_left_y) and (self.plot.top_left_x < point.x < self.plot.bottom_right_x)]
#         self.full_auto_connect = not any(point.distance_to(self.points[i]) > self.auto_connect_treshold for i,point in enumerate(self.points[1:]))

#     def draw(self) -> None:
#         if self.points_radius:
#             for point in self.points:
#                 pg.draw.circle(self.plot.canvas, self.color if self.points_color == None else self.points_color, self.plot.__plot2real__(point)(), self.points_radius)

#         if len(self.points) < 2: return
#         if self.full_auto_connect:
#             pg.draw.lines(self.plot.canvas, self.color, False, [self.plot.__plot2real__(point)() for point in self.points])
#         else:
#             real_points = [self.plot.__plot2real__(point)() for point in self.points]
#             for i,(point, real_point) in enumerate(zip(self.points[1:], real_points[1:])):
#                 if point.distance_to(self.points[i]) < self.auto_connect_treshold:
#                     pg.draw.line(self.plot.canvas, self.color, real_points[i], real_point) #type: ignore

class __PlotSettings__:
    def __init__(self, plot:Plot) -> None:
        self.plot = plot
        self.settings :dict= {
            "use_real_time_rendering" : True,
            "show_corners_coords" : True,

            "use_inter_pixel_correction" : True,

            "show_zoom_info": True,
            "top_left_info_position" : self.plot.position + V2(20, 100),
            "info_spacing" : V2(0, 32),
            "info_precision" : 2,

            "distance_to_axis_for_scalar_zoom" : 10,

            "show_x_axis" : True,
            "show_y_axis" : True,
            "bg_color" : (25, 25, 25),
            "axes_default_color" : (100, 100, 100),
            "x_axis_color" : None,
            "y_axis_color" : None,
            "change_axes_colors_on_mouse_hover" : True,
            "mouse_hover_axes_color" : (200, 200, 200),

            "axes_default_width" : 5,
            "x_axis_width" : None,
            "y_axis_width" : None,

            "show_cursor_coords" : False,

            "zoom_on_center" : False,
        }

    def print_current_settings(self) -> None:
        longest_key = max(map(len, self.settings))
        longest_type = max(map(lambda setting: len(str(type(setting)).split("'")[1]), self.settings.values()))
        split_string = "'"
        texts = [
            f"{setting}{' '*(longest_key-len(setting))} :{str(type(self.settings[setting])).split(split_string)[1]}{' '*(longest_type-len(str(type(self.settings[setting])).split(split_string)[1]))}=\t{self.settings[setting]}"
            for setting in self.settings
            ]
        longest_text = max(map(len , texts))
        print("=" * longest_text)
        for text in texts:
            print(text)
        print("=" * longest_text)
    
    def toggle(self, key:str) -> None:
        self.set(key, not self.get(key))

    def set(self, key:str, new_value) -> None:
        if not (key in self.settings): raise ValueError(f"The key [{key}] does not exist...")
        self.settings[key] = new_value

    def multiple_set(self, keys:list[str], new_values:list) -> None:
        for key, new_value in zip(keys, new_values):
            self.set(key, new_value)
    
    def get(self, key:str) -> bool|V2|Vector2D|int|float:
        return self.settings[key]

    def multiple_get(self, keys:list[str]) -> list[bool|V2|Vector2D|int|float]:
        return [self.get(key) for key in keys]

class Plot:
    __top_left_multiplier__ = V2(1, -1)
    __bottom_right_multiplier__ = V2(1, -1)
    def __init__(self, rootEnv:"RootEnv", plot_position:V2|Vector2D, plot_size:V2|Vector2D, top_left_plot_coord:V2|Vector2D, bottom_right_plot_coord: V2|Vector2D, scale:V2|Vector2D=V2one) -> None:
        self.rootEnv = rootEnv

        self.top_left_plot_coord = top_left_plot_coord
        self.bottom_right_plot_coord = bottom_right_plot_coord

        self.position = plot_position
        self.size = plot_size
        self.scale = scale

        self.settings = __PlotSettings__(self)

        self.current_zoom = V2one * -np.log2(10)*10
        self.current_offset = V2(0,0)
        self.update_grid(True)

        self.functions :list[Function]= []

        self.canvas = pg.Surface(self.size())
        self.dragging = None
        self.start_dragging = V2z
        self.is_mouse_in_rect = False
        self.mouse_scalar = V2one.copy()

    def set_borders_by_position_and_zoom(self) -> None:
        self.top_left_plot_coord = self.current_offset - (.5**(.1*self.current_zoom)) * self.__top_left_multiplier__
        self.bottom_right_plot_coord = self.current_offset + (.5**(.1*self.current_zoom)) * self.__bottom_right_multiplier__
        self.top_left_x, self.top_left_y = self.top_left_plot_coord
        self.bottom_right_x, self.bottom_right_y = self.bottom_right_plot_coord

    def update_grid(self, update_step_grid=False) -> None:
        self.set_borders_by_position_and_zoom()
        if update_step_grid:
            self.step = (self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size / self.scale
            X, Y = np.arange(self.top_left_plot_coord.x, self.bottom_right_plot_coord.x, self.step.x), np.arange(self.top_left_plot_coord.y, self.bottom_right_plot_coord.y, self.step.y)
            self.meshgrid = np.meshgrid(X, Y)
            self.pixel_size = abs(self.size / (self.bottom_right_plot_coord - self.top_left_plot_coord) * (self.step * -1))
            if self.settings.get("use_inter_pixel_correction"):
                self.pixel_size += V2one

    def load_function(self, function:Function) -> None:
        function.plot = self
        function.__layer_surface__ = pg.Surface(self.size(), pg.SRCALPHA, 32).convert_alpha()
        function.update_function(function.function)
        self.functions.append(function)

    def __plot2real__(self, plot_position:V2|Vector2D) -> V2|Vector2D:
        return (plot_position + self.top_left_plot_coord * -1) * self.size / (self.bottom_right_plot_coord - self.top_left_plot_coord)

    def __real2plot__(self, real_position:V2|Vector2D) -> V2|Vector2D:
        return (real_position - self.position) * (self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size + self.top_left_plot_coord

    def render(self) -> None:
        self.canvas.fill(self.settings.get("bg_color")) #type: ignore

        for function in self.functions: function.draw()

        pg.draw.rect(self.canvas, (255,255,255), V2z() + self.size(), 5) #type: ignore

        center = self.size * .5
        aimer_radius = 15
        pg.draw.line(self.canvas, (100,100,100), (center + aimer_radius)(), (center - aimer_radius)(), 1)
        pg.draw.line(self.canvas, (100,100,100), (center + self.__top_left_multiplier__ * aimer_radius)(), (center - self.__top_left_multiplier__ * aimer_radius)(), 1)
        pg.draw.circle(self.canvas, (100,100,100), (self.size * .5)(), 15, 1)

        if self.settings.get("show_corners_coords"):
            self.rootEnv.print(str(self.top_left_plot_coord), V2z.copy(), bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=V2(10,10), personalized_surface=self.canvas)
            self.rootEnv.print(str(V2(self.top_left_plot_coord.x, self.bottom_right_plot_coord.y)), self.size * V2(0, 1), fixed_sides=TEXT_FIXED_SIDES_BOTTOM_LEFT, bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=V2(10,10), personalized_surface=self.canvas)
            self.rootEnv.print(str(self.bottom_right_plot_coord), self.size.copy(), fixed_sides=TEXT_FIXED_SIDES_BOTTOM_RIGHT, bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=V2(10,10), personalized_surface=self.canvas)
            self.rootEnv.print(str(V2(self.bottom_right_plot_coord.x, self.top_left_plot_coord.y)), self.size * V2(1, 0), fixed_sides=TEXT_FIXED_SIDES_TOP_RIGHT, bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=V2(10,10), personalized_surface=self.canvas)
    
    def update(self) -> None:
        self.plot_mouse_position = self.__real2plot__(self.rootEnv.mouse.position)
        self.plot_center_real_position = self.__plot2real__(V2z) + self.position

        self.is_mouse_in_rect = self.position.x < self.rootEnv.mouse.position.x < self.position.x + self.size.x and \
                                self.position.y < self.rootEnv.mouse.position.y < self.position.y + self.size.y

        if self.rootEnv.mouse.just_released[0] and self.dragging != None:
            self.dragging = None
            self.update_grid(True)
            for function in self.functions:
                function.update_points()
            self.render()

        if self.is_mouse_in_rect:
            self.mouse_scalar = V2(0 if abs(self.plot_center_real_position.x - self.rootEnv.mouse.position.x) < self.settings.get("distance_to_axis_for_scalar_zoom") else 1, 0 if abs(self.plot_center_real_position.y - self.rootEnv.mouse.position.y) < self.settings.get("distance_to_axis_for_scalar_zoom") else 1) #type: ignore
            if self.mouse_scalar.x == self.mouse_scalar.y == 0: self.mouse_scalar = V2one
            for event in self.rootEnv.events:
                if event.type == pg.MOUSEWHEEL:
                    if self.settings.get("zoom_on_center"):
                        self.current_zoom += event.y * self.mouse_scalar
                    else:
                        pre = self.__real2plot__(self.rootEnv.mouse.position)
                        self.current_zoom += event.y * self.mouse_scalar
                        self.update_grid(False)
                        self.current_offset += pre - self.__real2plot__(self.rootEnv.mouse.position)
                    self.update_grid(True)
                    for function in self.functions:
                        function.update_points()
                    self.render()
            
            if self.rootEnv.mouse.just_pressed[0] and self.dragging == None:
                self.dragging = self.rootEnv.mouse.position.copy()
                self.start_dragging = self.dragging.copy()
            
        if self.dragging:
            offset = (self.dragging - self.rootEnv.mouse.position)* V2(1, -1) * (abs(self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size)
            self.dragging = self.rootEnv.mouse.position.copy()
            self.current_offset += offset

            if self.settings.get("use_real_time_rendering"):
                self.update_grid(True)
                for function in self.functions: function.update_points()
            else:
                self.update_grid()
            self.render()

    def draw(self) -> None:
        self.rootEnv.screen.blit(self.canvas, self.position())
        if self.top_left_x < 0 < self.bottom_right_x and self.settings.get("show_x_axis"):
            pg.draw.line(self.rootEnv.screen,
                         (self.settings.get("axes_default_color") if (x_color:=self.settings.get("x_axis_color"))==None else x_color) if self.mouse_scalar.x else (self.settings.get("mouse_hover_axes_color")),
                         (self.__plot2real__(V2(0, self.top_left_y)) + self.position)(),
                         (self.__plot2real__(V2(0, self.bottom_right_y)) + self.position)(),
                         self.settings.get("axes_default_width") if (x_width:=self.settings.get("x_axis_width"))==None else x_width) #type: ignore
        if self.bottom_right_y < 0 < self.top_left_y and self.settings.get("show_y_axis"):
            pg.draw.line(self.rootEnv.screen,
                         (self.settings.get("axes_default_color") if (y_color:=self.settings.get("y_axis_color"))==None else y_color) if self.mouse_scalar.y else (self.settings.get("mouse_hover_axes_color")),
                         (self.__plot2real__(V2(self.top_left_x, 0)) + self.position)(),
                         (self.__plot2real__(V2(self.bottom_right_x, 0)) + self.position)(),
                         self.settings.get("axes_default_width") if (y_width:=self.settings.get("y_axis_width"))==None else y_width) #type: ignore

        if self.is_mouse_in_rect and self.settings.get("show_cursor_coords"):
            self.rootEnv.print(str(round(self.plot_mouse_position, .1)), self.rootEnv.mouse.position, fixed_sides=TEXT_FIXED_SIDES_BOTTOM_MIDDLE) #type: ignore

        data = [
            [f"ZOOM:", TEXT_FIXED_SIDES_TOP_LEFT, self.settings.get("show_zoom_info")],
            [f"  x: {(.5**(.1*self.current_zoom.x)):.{self.settings.get('info_precision')}f};", TEXT_FIXED_SIDES_TOP_LEFT, self.settings.get("show_zoom_info")],
            [f"  y: {(.5**(.1*self.current_zoom.y)):.{self.settings.get('info_precision')}f};", TEXT_FIXED_SIDES_TOP_LEFT, self.settings.get("show_zoom_info")],
        ]

        for i, (d, fixed_side, show) in enumerate(data):
            if show:
                self.rootEnv.print(d, self.settings.get("top_left_info_position") + self.settings.get("info_spacing") * i, fixed_sides=fixed_side) #type: ignore
