from __future__ import annotations
from .envs import *
import numpy as np

def no_error_complex_function(function, args) -> V2|Vector2D:
    res :complex= function(args)
    return V2(res.real, res.imag)

sign = lambda value: -1 if value < 0 else (1 if value > 0 else 0)

class Function:
    def __init__(self, function, plot:"Plot", color) -> None:
        self.plot = plot
        self.color = color
        self.update_function(function)
    
    def update_points(self) -> None:
        self.update_function(self.function)

    def get_points(self) -> list:
        signs_self = np.sign(self.function(*self.plot.meshgrid))
        signs_sum = signs_self + np.roll(signs_self, axis=1, shift=1) + np.roll(signs_self, axis=0, shift=-1) + np.roll(signs_self, axis=(1,0), shift=(1,-1))
        return np.column_stack(np.where(((-4 < signs_sum) & (signs_sum < 4))[:-1, 1:])[::-1]) / self.plot.scale()
    
    def update_function(self, new_function) -> None:
        self.function = new_function
        self.points = self.get_points()
    
    def draw(self) -> None:
        # pg.draw.aalines(self.plot.canvas, self.color, False, self.points)
        for point in self.points:
            self.plot.canvas.set_at(list(map(int, point)), self.color)

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

class Plot:
    __top_left_multiplier__ = V2(1, -1)
    __bottop_right_multiplier__ = V2(1, -1)
    def __init__(self, rootEnv:"RootEnv", plot_position:V2|Vector2D, plot_size:V2|Vector2D, top_left_plot_coord:V2|Vector2D, bottom_right_plot_coord: V2|Vector2D, scale:V2|Vector2D=V2one) -> None:
        self.rootEnv = rootEnv

        self.top_left_plot_coord = top_left_plot_coord
        self.bottom_right_plot_coord = bottom_right_plot_coord

        self.position = plot_position
        self.size = plot_size
        self.scale = scale
        
        self.current_zoom = V2one * -np.log2(10)*10
        self.current_offset = V2(0,0)
        self.update_grid(True)

        self.functions :list[Function]= []

        self.canvas = pg.Surface(self.size())
        self.dragging = None
        self.is_mouse_in_rect = False

    def set_borders_by_position_and_zoom(self) -> None:
        self.top_left_plot_coord = self.current_offset - (.5**(.1*self.current_zoom)) * self.__top_left_multiplier__
        self.bottom_right_plot_coord = self.current_offset + (.5**(.1*self.current_zoom)) * self.__bottop_right_multiplier__
        self.top_left_x, self.top_left_y = self.top_left_plot_coord
        self.bottom_right_x, self.bottom_right_y = self.bottom_right_plot_coord

    def update_grid(self, update_step_grid=False) -> None:
        self.set_borders_by_position_and_zoom()
        if update_step_grid:
            self.step = (self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size / self.scale
            X, Y = np.arange(self.top_left_plot_coord.x, self.bottom_right_plot_coord.x, self.step.x), np.arange(self.top_left_plot_coord.y, self.bottom_right_plot_coord.y, self.step.y)
            self.meshgrid = np.meshgrid(X, Y)

    def load_function(self, function:Function) -> None:
        self.functions.append(function)

    def __plot2real__(self, plot_position:V2|Vector2D) -> V2|Vector2D:
        return (plot_position + self.top_left_plot_coord * -1) * self.size / (self.bottom_right_plot_coord - self.top_left_plot_coord)

    def __real2plot__(self, real_position:V2|Vector2D) -> V2|Vector2D:
        return (real_position - self.position) * (self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size + self.top_left_plot_coord

    def render(self) -> None:
        self.canvas.fill((0,0,0))
        if self.bottom_right_y < 0 < self.top_left_y: pg.draw.line(self.canvas, (100,100,100), self.__plot2real__(V2(self.top_left_x, 0))(), self.__plot2real__(V2(self.bottom_right_x, 0))())
        if self.top_left_x < 0 < self.bottom_right_x: pg.draw.line(self.canvas, (100,100,100), self.__plot2real__(V2(0, self.top_left_y))(), self.__plot2real__(V2(0, self.bottom_right_y))())
        
        for function in self.functions: function.draw()

        pg.draw.rect(self.canvas, (255,255,255), V2z() + self.size(), 5) #type: ignore
        self.rootEnv.print(str(self.top_left_plot_coord.__round__(.1)), V2z.copy(), bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=V2(10,10), personalized_surface=self.canvas)
        self.rootEnv.print(str(V2(self.top_left_plot_coord.x, self.bottom_right_plot_coord.y).__round__(.1)), self.size * V2(0, 1), fixed_sides=TEXT_FIXED_SIDES_BOTTOM_LEFT, bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=V2(10,10), personalized_surface=self.canvas)
        self.rootEnv.print(str(self.bottom_right_plot_coord.__round__(.1)), self.size.copy(), fixed_sides=TEXT_FIXED_SIDES_BOTTOM_RIGHT, bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=V2(10,10), personalized_surface=self.canvas)
        self.rootEnv.print(str(V2(self.bottom_right_plot_coord.x, self.top_left_plot_coord.y).__round__(.1)), self.size * V2(1, 0), fixed_sides=TEXT_FIXED_SIDES_TOP_RIGHT, bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=V2(10,10), personalized_surface=self.canvas)
    
    def update(self) -> None:
        self.is_mouse_in_rect = self.position.x < self.rootEnv.mouse.position.x < self.position.x + self.size.x and \
                                self.position.y < self.rootEnv.mouse.position.y < self.position.y + self.size.y

        if self.rootEnv.mouse.just_released[0] and self.dragging != None:
            self.dragging = None
            self.update_grid(True)
            for function in self.functions:
                function.update_points()
            self.render()

        if self.is_mouse_in_rect:
            for event in self.rootEnv.events:
                if event.type == pg.MOUSEWHEEL:
                    self.current_zoom += event.y
                    self.update_grid(True)
                    for function in self.functions:
                        function.update_points()
                    self.render()
            
            if self.rootEnv.mouse.just_pressed[0] and self.dragging == None:
                self.dragging = self.rootEnv.mouse.position.copy()
            
        if self.dragging:
            offset = (self.dragging - self.rootEnv.mouse.position)* V2(1, -1) * (abs(self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size)
            self.dragging = self.rootEnv.mouse.position.copy()
            self.current_offset += offset
            self.update_grid()
            self.render()

    def draw(self) -> None:
        self.rootEnv.screen.blit(self.canvas, self.position())
        if self.is_mouse_in_rect:
            self.rootEnv.print(str(round(self.__real2plot__(self.rootEnv.mouse.position), .1)), self.rootEnv.mouse.position, fixed_sides=TEXT_FIXED_SIDES_BOTTOM_MIDDLE)
