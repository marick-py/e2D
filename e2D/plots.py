from __future__ import annotations
from .envs import *
import numpy as np

__LITERAL_PIVOT_POSITIONS__ = Literal["top_left", "top_center", "top_right", "center_left", "center_center", "center_right", "bottom_left", "bottom_center", "bottom_right"]
__PIVOT_POSITIONS_MULTIPLIER__ = dict(zip(("top_left", "top_center", "top_right", "center_left", "center_center", "center_right", "bottom_left", "bottom_center", "bottom_right"), (Vector2D(x,y) for y in [0, .5, 1] for x in [0, .5, 1])))

__LITERAL_SETTINGS_KEYS__ = Literal['distance_to_axis_for_scalar_zoom','zoom_on_center','warp_mouse','movable','zoomable','use_inter_pixel_correction','use_real_time_rendering','change_axes_colors_on_mouse_hover','mouse_hover_axes_color','show_axes','show_x_axis','show_y_axis','axes_default_color','x_axis_color','y_axis_color','axes_default_width','x_axis_width','y_axis_width','render_axes_on_top','show_grid','grid_step','grid_color','grid_width','show_pointer','pointer_radius','pointer_color','show_cursor_coords','render_bg','bg_color','draw_rect','rect_color','rect_width','show_corners_coords','show_zoom_info','top_left_info_position','info_interline_space','info_font','info_precision']

class Function:
    def __init__(self) -> None:
        self.plot : Plot
        self.id = int|str
        self.__layer_surface__ :pg.Surface= None #type: ignore
    
    def __post_load_init__(self, plot:Plot) -> None:
        self.plot = plot
        self.__layer_surface__ = pg.Surface(self.plot.size(), pg.SRCALPHA, 32).convert_alpha()
        self.update()
        self.plot.functions[self.id] = self
    
    def update(self) -> None: pass
    
    def __render__(self) -> None: pass
    
    def draw(self) -> None:
        self.plot.canvas.blit(self.__layer_surface__, (0,0))

class Object:
    def __init__(self) -> None:
        self.plot : Plot
        self.id : int|str
        self.__layer_surface__ :pg.Surface= None #type: ignore
        self.__controller__ = None
    
    def __post_load_init__(self, plot:Plot, controller:Plot|Object) -> None:
        self.plot = plot
        self.__layer_surface__ = pg.Surface(self.plot.size(), pg.SRCALPHA, 32).convert_alpha()
        self.__controller__ = controller
        self.plot.objects[self.id] = self
        if isinstance(self, Line):
            self.point_a.__post_load_init__(self.plot, self)
            self.point_b.__post_load_init__(self.plot, self)
    
    def update(self) -> None: pass
    
    def __render__(self) -> None: pass
    
    def draw(self) -> None:
        self.plot.canvas.blit(self.__layer_surface__, (0,0))

class Line(Object):
    def __init__(self, id:int|str, point_a:Vector2D|Point, point_b:Vector2D|Point, color:list[float]|tuple[float,float,float]=(255,255,255), width:float=1) -> None:
        super().__init__()
        self.id = id
        if isinstance(point_a, Point):
            self.point_a = point_a
        else:
            self.point_a = Point(point_a)
        if isinstance(point_b, Point):
            self.point_b = point_b
        else:
            self.point_b = Point(point_b)
        self.color = color
        self.width = width
    
    def update(self) -> None:
        self.__render__()

    def __render__(self) -> None:
        self.__layer_surface__.fill((0,0,0,0))
        if self.point_a.__controller__ == self: self.point_a.update()
        if self.point_b.__controller__ == self: self.point_b.update()
        pg.draw.line(self.__layer_surface__, self.color, self.point_a.center(), self.point_b.center(), self.width)

class Point(Object):
    def __init__(self,
                id : int|str,
                position : Vector2D,
                label : str = "",
                radius : float = 1,
                color : list[float]|tuple[float,float,float] = (255,255,255),
                label_color : tuple[float, float, float] = (255, 255, 255),
                label_position_offset : Vector2D = Vector2D.zero(),
                label_pivot_position : __LITERAL_PIVOT_POSITIONS__ = "top_left",
                label_font : pg.font.Font = FONT_ARIAL_32,
                label_bg_color : tuple[int,int,int]|list[int]|None = None,
                label_border_color : tuple[int,int,int]|list[int]|None = None,
                label_border_width : float = 0,
                label_border_radius : int|list[int]|tuple[int,int,int,int] = -1,
                label_margin : Vector2D = Vector2D.zero()
                ) -> None:
        super().__init__()
        self.id = id
        self.position = position
        self.radius = radius
        self.color = color
        self.label = label
        self.label_color = label_color
        self.label_position_offset = label_position_offset
        self.label_pivot_position = label_pivot_position
        self.label_font = label_font
        self.label_bg_color = label_bg_color
        self.label_border_color = label_border_color
        self.label_border_width = label_border_width
        self.label_border_radius = label_border_radius
        self.label_margin = label_margin

        self.rect :list[float]= [0, 0, 0, 0]
        self.center = Vector2D.new_zero()

    def update(self) -> None:
        radius = self.radius * self.plot.size / (self.plot.bottom_right_plot_coord - self.plot.top_left_plot_coord) * self.plot.__y_axis_multiplier__
        self.center = self.plot.__plot2real__(self.position)
        self.text_position = self.plot.__plot2real__(self.position + self.label_position_offset)
        position = self.center - radius * .5
        self.rect = position() + radius()
        self.__render__()

    def __render__(self) -> None:
        self.__layer_surface__.fill((0,0,0,0))
        pg.draw.ellipse(self.__layer_surface__, self.color, self.rect)
        self.plot.rootEnv.print(self.label, self.text_position, color=self.label_color, pivot_position=self.label_pivot_position, font=self.label_font, bg_color=self.label_bg_color, border_color=self.label_border_color, border_width=self.label_border_width, border_radius=self.label_border_radius, margin=self.label_margin, personalized_surface=self.__layer_surface__)

class MathFunction(Function):
    def __init__(self,
                 id:int|str,
                 function:Callable[[int|float, int|float], int|float],
                 domain:list[float]=[-np.inf, np.inf],
                 codomain:list[float]=[-np.inf, np.inf],
                 color:list[float]|tuple[float,float,float]=(255,255,255)) -> None:
        super().__init__()
        self.id = id
        self.color = color
        self.function = function
        self.domain = domain
        self.codomain = codomain[::-1]

    def get_points(self) -> list:
        signs_self = np.sign(self.function(*self.plot.meshgrid))
        # i create 4 different matrixes? with the signs of f(x,y) pixel, each matrix is shifted according to this list [(0,0), (-1,0), (0,-1), (-1,-1)] and i find the points where summing the matrix i obtain a float => [-4 < x < 4]
        # credits for the plotting idea:
        # https://www.youtube.com/watch?v=EvvWOaLgKVU
        # mattbatwings (https://www.youtube.com/@mattbatwings)
        domain = tuple(((domain - self.plot.top_left_plot_coord.x) * self.plot.size.x / (self.plot.bottom_right_plot_coord.x - self.plot.top_left_plot_coord.x)) for domain in self.domain)
        codomain = tuple(((codomain - self.plot.top_left_plot_coord.y) * self.plot.size.y / (self.plot.bottom_right_plot_coord.y - self.plot.top_left_plot_coord.y)) for codomain in self.codomain)
        
        signs_sum = signs_self + np.roll(signs_self, axis=1, shift=1) + np.roll(signs_self, axis=0, shift=-1) + np.roll(signs_self, axis=(1,0), shift=(1,-1))
        coords = np.column_stack(np.where(((-4 < signs_sum) & (signs_sum < 4))[:-1, 1:])[::-1]) / self.plot.scale()

        return coords[
            np.logical_and(
                np.logical_and(coords[:, 0] >= domain[0], coords[:, 0] <= domain[1]),
                np.logical_and(coords[:, 1] >= codomain[0], coords[:, 1] <= codomain[1]))]

    def update(self, new_function:None|Callable[[int|float, int|float], int|float]=None, render=True, domain:list[float]|None=None, codomain:list[float]|None=None) -> None:
        if new_function != None:
            self.function = new_function
        if domain != None: self.domain = domain
        if codomain != None: self.codomain = codomain
        if render:
            self.points = self.get_points()
            self.__render__()
    
    def get_derivative(self, delta:float=.01, color:None|list[float]|tuple[float,float,float]=None) -> MathFunction:
        return MathFunction(lambda x,y: (self.function(x + delta, y) - self.function(x,y))/delta - y, color if color != None else self.color) #type: ignore

    def __render__(self) -> None:
        self.__layer_surface__.fill((0,0,0,0))
        offset = self.plot.dragging - self.plot.start_dragging if (self.plot.dragging != None) and (not self.plot.settings.get("use_real_time_rendering")) else Vector2D.zero()
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
                self.__layer_surface__.set_at(point, self.color) #type: ignore

class TimeFunction(Function):
    def __init__(self, id:int|str, function, t_range:list[float]=[0,0, 1.0], t_step:float=.01, color:list[float]|tuple[float,float,float]=(255,255,255)) -> None:
        super().__init__()
        self.id = id
        self.color = color
        self.function = function
        self.t_range = t_range
        self.t_step = t_step
    def get_points(self) -> list:
        signs_self = np.sign(self.function(*self.plot.meshgrid))
        domain = [((domain - self.plot.top_left_plot_coord.x) * self.plot.size.x / (self.plot.bottom_right_plot_coord.x - self.plot.top_left_plot_coord.x)) for domain in self.domain]
        codomain = [((codomain - self.plot.top_left_plot_coord.y) * self.plot.size.y / (self.plot.bottom_right_plot_coord.y - self.plot.top_left_plot_coord.y)) for codomain in self.codomain]
        signs_sum = signs_self + np.roll(signs_self, axis=1, shift=1) + np.roll(signs_self, axis=0, shift=-1) + np.roll(signs_self, axis=(1,0), shift=(1,-1))
        coords = np.column_stack(np.where(((-4 < signs_sum) & (signs_sum < 4))[:-1, 1:])[::-1]) / self.plot.scale()
        return coords[
            np.logical_and(
                np.logical_and(coords[:, 0] >= domain[0], coords[:, 0] <= domain[1]),
                np.logical_and(coords[:, 1] >= codomain[0], coords[:, 1] <= codomain[1]))] #type: ignore
    def update(self, new_function=None, render=True, domain:list[float]|None=None, codomain:list[float]|None=None) -> None:
        if new_function != None:
            self.function = new_function
        if domain != None: self.domain = domain
        if codomain != None: self.codomain = codomain
        if render:
            self.points = self.get_points()
            self.__render__()
    def __render__(self) -> None:
        self.__layer_surface__.fill((0,0,0,0))
        offset = self.plot.dragging - self.plot.start_dragging if (self.plot.dragging != None) and (not self.plot.settings.get("use_real_time_rendering")) else Vector2D.zero()
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
                self.__layer_surface__.set_at(point, self.color) #type: ignore

class PointsFunction(Function):
    def __init__(self, id:int|str, points:list[Vector2D]=[], points_color:list[float]|tuple[float,float,float]=(255,0,0), color:list[float]|tuple[float,float,float]=(255,255,255)) -> None:
        super().__init__()
        self.id = id
        self.color = color
        self.points = points
        self.points_color = points_color

    def update(self, points:list[Vector2D]|None=None) -> None:
        if points != None: self.points = points
        self.plot_points = [self.plot.__plot2real__(point)() for point in self.points if \
                        self.plot.top_left_x < point.x < self.plot.bottom_right_x and \
                        self.plot.bottom_right_y < point.y < self.plot.top_left_y]
        self.__render__()

    def __render__(self) -> None:
        self.__layer_surface__.fill((0,0,0,0))
        if len(self.plot_points)>=2: pg.draw.lines(self.__layer_surface__, self.color, False, self.plot_points) #type: ignore
        # for point in self.points:
            # pg.draw.circle(self.__layer_surface__,
            #                self.points_color,
            #                self.plot.__plot2real__(point),
            #                5)

"""
def no_error_complex_function(function, args) -> Vector2D:
    res :complex= function(args)
    return Vector2D(res.real, res.imag)
sign = lambda value: -1 if value < 0 else (1 if value > 0 else 0)
class ComplexFunction:
    def __init__(self, function, plot:"Plot", starting_t:float=-10, ending_t:float=10, step=.01, color=(255,255,255), auto_connect_treshold=float("inf"), points_radius=2, points_color=None) -> None:
        self.auto_connect_treshold = auto_connect_treshold
        self.plot = plot
        self.starting_t = starting_t
        self.ending_t = ending_t
        self.color = color
        self.step = step
        self.points_color = points_color
        self.points_radius = points_radius
        self.update_function(function)
    
    def update_points(self) -> None:
        self.update_function(self.function)
    
    def update_function(self, new_function) -> None:
        self.function = new_function
        self.points :list[Vector2D]= [point for t in range(int(self.starting_t / self.step), int(self.ending_t / self.step)) if (self.plot.bottom_right_y < (point:=no_error_complex_function(new_function, t * self.step)).y < self.plot.top_left_y) and (self.plot.top_left_x < point.x < self.plot.bottom_right_x)]
        self.full_auto_connect = not any(point.distance_to(self.points[i]) > self.auto_connect_treshold for i,point in enumerate(self.points[1:]))

    def draw(self) -> None:
        if self.points_radius:
            for point in self.points:
                pg.draw.circle(self.plot.canvas, self.color if self.points_color == None else self.points_color, self.plot.__plot2real__(point)(), self.points_radius)

        if len(self.points) < 2: return
        if self.full_auto_connect:
            pg.draw.lines(self.plot.canvas, self.color, False, [self.plot.__plot2real__(point)() for point in self.points])
        else:
            real_points = [self.plot.__plot2real__(point)() for point in self.points]
            for i,(point, real_point) in enumerate(zip(self.points[1:], real_points[1:])):
                if point.distance_to(self.points[i]) < self.auto_connect_treshold:
                    pg.draw.line(self.plot.canvas, self.color, real_points[i], real_point) #type: ignore
"""

class __PlotSettings__:
    def __init__(self, plot:Plot) -> None:
        self.plot = plot
        self.settings :dict[__LITERAL_SETTINGS_KEYS__, int|float|bool|Vector2D|tuple|list|pg.font.Font]= {
            # axes
                "distance_to_axis_for_scalar_zoom" : 10,

            # cursor
                "zoom_on_center" : False,
                "warp_mouse" : True,
                "movable" : True,
                "zoomable" : True,

            # plot visual options
                # plot system
                    "use_inter_pixel_correction" : True,
                    "use_real_time_rendering" : True,
                
                # axes
                    "change_axes_colors_on_mouse_hover" : True,
                    "mouse_hover_axes_color" : rgb(200, 200, 200),
                    "show_axes" : True,
                    "show_x_axis" : True,
                    "show_y_axis" : True,
                    "axes_default_color" : rgb(100, 100, 100),
                    "x_axis_color" : None,
                    "y_axis_color" : None,
                    "axes_default_width" : 5,
                    "x_axis_width" : None,
                    "y_axis_width" : None,
                    "render_axes_on_top" : False,

                # grid
                    "show_grid" : True,
                    "grid_step" : Vector2D(PI, 1),
                    "grid_color" : rgb(17, 65, 68),
                    "grid_width" : 1,
            
                # pointer
                    "show_pointer" : True,
                    "pointer_radius" : 15,
                    "pointer_color" : rgb(255, 255, 255),
                
                # cursor
                    "show_cursor_coords" : False,

                # rect
                    "render_bg" : True,
                    "bg_color" : rgb(28, 29, 34),
                    "draw_rect" : True,
                    "rect_color" : rgb(255, 255, 255),
                    "rect_width" : 5,
                    "show_corners_coords" : True,

                # info options
                    "show_zoom_info": True,
                    "top_left_info_position" : self.plot.position + Vector2D(15, 75),
                    "info_interline_space" : Vector2D(0, 24),
                    "info_font" : NEW_FONT(24),
                    "info_precision" : 2,
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
    
    def toggle(self, key:__LITERAL_SETTINGS_KEYS__) -> None:
        self.set(key, not self.get(key))

    def set(self, key:__LITERAL_SETTINGS_KEYS__, new_value:int|float|bool|Vector2D|tuple|list|pg.font.Font) -> None:
        if not (key in self.settings): raise ValueError(f"The key [{key}] does not exist...")
        self.settings[key] = new_value

    def multiple_set(self, new_key_and_values_dict:dict[__LITERAL_SETTINGS_KEYS__, int|float|bool|Vector2D|tuple|list|pg.font.Font]) -> None:
        self.settings.update(new_key_and_values_dict)
    
    def get(self, key:__LITERAL_SETTINGS_KEYS__) -> int|float|bool|Vector2D|tuple|list|pg.font.Font:
        return self.settings[key]

    def multiple_get(self, keys:list[__LITERAL_SETTINGS_KEYS__]) -> list[int|float|bool|Vector2D|tuple|list|pg.font.Font]:
        return [self.get(key) for key in keys]

class Plot:
    __y_axis_multiplier__ = Vector2D(1, -1)
    def __init__(self, rootEnv:"RootEnv", plot_position:Vector2D, plot_size:Vector2D, top_left_plot_coord:Vector2D, bottom_right_plot_coord: Vector2D, scale:Vector2D=Vector2D.one()) -> None:
        self.rootEnv = rootEnv
        self.top_left_plot_coord = top_left_plot_coord
        self.bottom_right_plot_coord = bottom_right_plot_coord
        self.position = plot_position
        self.size = plot_size
        self.scale = scale
        self.settings = __PlotSettings__(self)
        self.functions :dict[int|str, Function]= {}
        self.objects :dict[int|str, Object]= {}
        self.canvas = pg.Surface(self.size(), pg.SRCALPHA, 32).convert_alpha()
        self.dragging = None
        self.start_dragging = Vector2D.new_zero()
        self.is_mouse_in_rect = False
        self.mouse_scalar = Vector2D.new_one()
        self.plot_mouse_position = Vector2D.new_zero()
        self.focus_using_corners(top_left_plot_coord, bottom_right_plot_coord)

    def set_borders_by_position_and_zoom(self) -> None:
        self.top_left_plot_coord = self.current_offset - 2**(self.current_zoom.mult(-.1)) * self.__y_axis_multiplier__
        self.bottom_right_plot_coord = self.current_offset + 2**(-.1*self.current_zoom) * self.__y_axis_multiplier__
        self.top_left_x, self.top_left_y = self.top_left_plot_coord
        self.bottom_right_x, self.bottom_right_y = self.bottom_right_plot_coord

    def update_grid(self, update_step_grid:bool=False) -> None:
        self.set_borders_by_position_and_zoom()
        if update_step_grid:
            self.step = (self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size / self.scale
            X, Y = np.arange(self.top_left_plot_coord.x, self.bottom_right_plot_coord.x, self.step.x), np.arange(self.top_left_plot_coord.y, self.bottom_right_plot_coord.y, self.step.y)
            self.meshgrid = np.meshgrid(X, Y)
            self.pixel_size = abs(self.size / (self.bottom_right_plot_coord - self.top_left_plot_coord) * (self.step * -1))
            if self.settings.get("use_inter_pixel_correction"): self.pixel_size.add(both=1)

    def add_functions(self, *functions:Function) -> None:
        for func in functions:
            func.__post_load_init__(self)
    def remove_function(self, *functions:int|str|Function) -> None:
        for fid in functions:
            if fid in self.functions:
                del self.functions[fid]
            elif isinstance(fid, Function):
                del self.functions[fid.id]
            else:
                raise Exception(f"Unknown util type: {fid}")
            
    def add_objects(self, *objects:Object) -> None:
        for obj in objects:
            obj.__post_load_init__(self, self)
    def remove_function(self, *objects:int|str|Object) -> None:
        for oid in objects:
            if oid in self.objects:
                del self.objects[oid]
            elif isinstance(oid, Object):
                del self.functions[oid.id]
            else:
                raise Exception(f"Unknown util type: {oid}")
    
    def add(self, *data:Object|Function) -> None:
        for d in data:
            if isinstance(d, Object):
                self.add_objects(d)
            elif isinstance(d, Function):
                self.add_functions(d)

    def __plot2real__(self, plot_position:Vector2D) -> Vector2D:
        return (plot_position + self.top_left_plot_coord * -1) * self.size / (self.bottom_right_plot_coord - self.top_left_plot_coord)

    def __real2plot__(self, real_position:Vector2D) -> Vector2D:
        return (real_position - self.position) * (self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size + self.top_left_plot_coord

    def render(self) -> None:
        # fill canvas with alpha zero color
        self.canvas.fill((0,0,0,0))

        # draw grid
        if self.settings.get("show_grid"):
            grid_step = self.settings.get("grid_step")
            grid_color = self.settings.get("grid_color")
            grid_width = self.settings.get("grid_width")
            clamped_top_left = grid_step * (self.top_left_plot_coord / grid_step).__ceil__()
            clamped_bottom_right = grid_step * (self.bottom_right_plot_coord / grid_step).__ceil__()
            for x_value in np.arange(clamped_top_left.x, clamped_bottom_right.x, grid_step.x): #type: ignore
                pg.draw.line(self.canvas, grid_color, self.__plot2real__((x_value, self.top_left_y))(), self.__plot2real__((x_value, self.bottom_right_y))(), grid_width) #type: ignore
            for y_value in np.arange(clamped_bottom_right.y, clamped_top_left.y, grid_step.y): #type: ignore
                pg.draw.line(self.canvas, grid_color, self.__plot2real__((self.top_left_x, y_value))(), self.__plot2real__((self.bottom_right_x, y_value))(), grid_width) #type: ignore

        # draw functions
        for function in self.functions.values(): function.draw()
        # draw objects
        for obj in self.objects.values(): obj.draw()

        # draw rect, pointer and corner coords
        if self.settings.get("draw_rect"):
            pg.draw.rect(self.canvas, self.settings.get("rect_color"), Vector2D.zero()() + self.size(), self.settings.get("rect_width")) #type: ignore

        if self.settings.get("show_pointer"):
            center = self.size * .5
            aimer_radius = self.settings.get("pointer_radius")
            pointer_color = self.settings.get("pointer_color")
            pg.draw.line(self.canvas, pointer_color, (center + aimer_radius)(), (center - aimer_radius)(), 1) #type: ignore
            pg.draw.line(self.canvas, pointer_color, (center + self.__y_axis_multiplier__ * aimer_radius)(), (center - self.__y_axis_multiplier__ * aimer_radius)(), 1) #type: ignore
            pg.draw.circle(self.canvas, pointer_color, (self.size * .5)(), 15, 1) #type: ignore

        if self.settings.get("show_corners_coords"):
            self.rootEnv.print(self.top_left_plot_coord.advanced_stringify(4, True), Vector2D.zero(), bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=Vector2D(10,10), personalized_surface=self.canvas)
            self.rootEnv.print(Vector2D(self.top_left_plot_coord.x, self.bottom_right_plot_coord.y).advanced_stringify(4, True), self.size * Vector2D(0, 1), pivot_position="bottom_left", bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=Vector2D(10,10), personalized_surface=self.canvas)
            self.rootEnv.print(self.bottom_right_plot_coord.advanced_stringify(4, True), self.size.copy, pivot_position="bottom_right", bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=Vector2D(10,10), personalized_surface=self.canvas)
            self.rootEnv.print(Vector2D(self.bottom_right_plot_coord.x, self.top_left_plot_coord.y).advanced_stringify(4, True), self.size * Vector2D(1, 0), pivot_position="top_right", bg_color=(0,0,0), border_color=(255,255,255), border_width=2, border_radius=15, margin=Vector2D(10,10), personalized_surface=self.canvas)
    
    def update(self) -> None:
        # update mouse and center positions
        self.plot_mouse_position = self.__real2plot__(self.rootEnv.mouse.position)
        self.plot_center_real_position = self.__plot2real__(Vector2D.zero()) + self.position

        self.is_mouse_in_rect = self.position.x < self.rootEnv.mouse.position.x < self.position.x + self.size.x and \
                                self.position.y < self.rootEnv.mouse.position.y < self.position.y + self.size.y

        # render the functions when i stop dragging (when i release the left mouse key)
        if self.rootEnv.mouse.get_key(0, "just_released") and self.dragging != None:
            self.dragging = None
            self.focus()

        if self.is_mouse_in_rect:
            if self.settings.get("zoomable"):
                # mouse scalar is needed for checking if the mouse is hovering an axis, in case it is the opposite one zoom value has to be multiplied by 0 so nullifying it.
                self.mouse_scalar = Vector2D(0 if abs(self.plot_center_real_position.x - self.rootEnv.mouse.position.x) < self.settings.get("distance_to_axis_for_scalar_zoom") else 1, 0 if abs(self.plot_center_real_position.y - self.rootEnv.mouse.position.y) < self.settings.get("distance_to_axis_for_scalar_zoom") else 1) #type: ignore
                if self.mouse_scalar.x == self.mouse_scalar.y == 0: self.mouse_scalar = Vector2D.one()
                for event in self.rootEnv.events:
                    if event.type == pg.MOUSEWHEEL:
                        if self.settings.get("zoom_on_center"):
                            # this will always zoom exactly in the middle of the canvas, according to the current plot offset
                            self.current_zoom += event.y * self.mouse_scalar
                        else:
                            # this will get the pre plot mouse position, calculate the zoom and with the "after" mouse position calculate the offset that i will add to the current plot offset
                            pre = self.__real2plot__(self.rootEnv.mouse.position)
                            self.current_zoom += event.y * self.mouse_scalar
                            # i have to update the corners of the plot here to use the real2plot function correctly (i cant use shortcuts)
                            self.update_grid(False)
                            self.current_offset += pre - self.__real2plot__(self.rootEnv.mouse.position)
                        self.focus()
            
            if self.settings.get("movable"):
                # start dragging whenever mouse left button is just pressed
                if self.rootEnv.mouse.get_key(0, "just_pressed") and self.dragging == None:
                    self.dragging = self.rootEnv.mouse.position.copy
                    self.start_dragging = self.dragging.copy
            
        # update the canvas if im dragging
        if self.dragging:
            moved = False
            if (not self.is_mouse_in_rect) and self.settings.get("warp_mouse"):
                if self.rootEnv.mouse.position.x < self.position.x:
                    self.rootEnv.mouse.position = Vector2D(self.position.x + self.size.x, self.rootEnv.mouse.position.y)
                    moved = True
                elif self.rootEnv.mouse.position.x > self.position.x + self.size.x:
                    self.rootEnv.mouse.position = Vector2D(self.position.x, self.rootEnv.mouse.position.y)
                    moved = True
                if self.rootEnv.mouse.position.y < self.position.y:
                    self.rootEnv.mouse.position = Vector2D(self.rootEnv.mouse.position.x, self.position.y + self.size.y)
                    moved = True
                elif self.rootEnv.mouse.position.y > self.position.y + self.size.y:
                    self.rootEnv.mouse.position = Vector2D(self.rootEnv.mouse.position.x, self.position.y)
                    moved = True
            if not moved:
                offset = (self.dragging - self.rootEnv.mouse.position)* Vector2D(1, -1) * (abs(self.bottom_right_plot_coord - self.top_left_plot_coord) / self.size)
                self.current_offset += offset
            self.dragging = self.rootEnv.mouse.position.copy

            # with real time rendering i update the function render each frame whnever im dragging the canvs around
            if self.settings.get("use_real_time_rendering"):
                self.focus()
            else:
                self.update_grid()
                self.render()
        
    def get_humanoid_zoom(self) -> Vector2D:
        return 2 ** (-.1*self.current_zoom)
        
    def focus(self, center:Vector2D|None=None, zoom:float|Vector2D|None=None) -> None:
        if center != None: self.current_offset = center.copy
        if zoom != None:
            if isinstance(zoom, Vector2D):
                self.current_zoom = Vector2D(-np.log2(zoom.x) * 10, -np.log2(zoom.y)*10)
            else:
                self.current_zoom = Vector2D(-10, -10) * np.log2(zoom)

        self.update_grid(True)
        for function in self.functions.values(): function.update()
        for obj in self.objects.values(): obj.update()
        self.render()
    
    def focus_using_corners(self, top_left_plot_coord:Vector2D|None=None, bottom_right_plot_coord: Vector2D|None=None) -> None:
        self.focus(
            (top_left_plot_coord + bottom_right_plot_coord).div(both=2),
            (bottom_right_plot_coord - top_left_plot_coord).div(both=2) * self.__y_axis_multiplier__
            )   

    def draw(self) -> None:
        # fill canvas with bg color
        if self.settings.get("render_bg"):
            self.rootEnv.screen.fill(self.settings.get("bg_color"), self.position() + self.size())
        
        # render functions before axes
        if render_axes_on_top:=self.settings.get("render_axes_on_top"): self.rootEnv.screen.blit(self.canvas, self.position())
        
        # render axes
        if self.top_left_x < 0 < self.bottom_right_x and (self.settings.get("show_x_axis") and self.settings.get("show_axes")):
            pg.draw.line(self.rootEnv.screen,
                         (self.settings.get("axes_default_color") if (x_color:=self.settings.get("x_axis_color"))==None else x_color) if (self.mouse_scalar.x or not self.settings.get("change_axes_colors_on_mouse_hover")) else (self.settings.get("mouse_hover_axes_color")), #type: ignore
                         (self.__plot2real__(Vector2D(0, self.top_left_y)) + self.position)(),
                         (self.__plot2real__(Vector2D(0, self.bottom_right_y)) + self.position)(),
                         self.settings.get("axes_default_width") if (x_width:=self.settings.get("x_axis_width"))==None else x_width) #type: ignore
        if self.bottom_right_y < 0 < self.top_left_y and (self.settings.get("show_y_axis") and self.settings.get("show_axes")):
            pg.draw.line(self.rootEnv.screen,
                         (self.settings.get("axes_default_color") if (y_color:=self.settings.get("y_axis_color"))==None else y_color) if (self.mouse_scalar.y or not self.settings.get("change_axes_colors_on_mouse_hover")) else (self.settings.get("mouse_hover_axes_color")), #type: ignore
                         (self.__plot2real__(Vector2D(self.top_left_x, 0)) + self.position)(),
                         (self.__plot2real__(Vector2D(self.bottom_right_x, 0)) + self.position)(),
                         self.settings.get("axes_default_width") if (y_width:=self.settings.get("y_axis_width"))==None else y_width) #type: ignore
        
        # render functions after axes
        if not render_axes_on_top: self.rootEnv.screen.blit(self.canvas, self.position())

        if self.is_mouse_in_rect and self.settings.get("show_cursor_coords"):
            self.rootEnv.print(self.plot_mouse_position.advanced_stringify(3, True), self.rootEnv.mouse.position, pivot_position="bottom_center") #type: ignore


        current_real_zoom = (.5**(.1*self.current_zoom))
        str_current_real_zoom = current_real_zoom.advanced_stringify(self.settings.get('info_precision'), True, True)
        data :list[tuple[str, __LITERAL_PIVOT_POSITIONS__, bool]]= [
            (f"ZOOM:", "top_left", self.settings.get("show_zoom_info")),
            (f"  x: {str_current_real_zoom[0]};", "top_left", self.settings.get("show_zoom_info")),
            (f"  y: {str_current_real_zoom[1]};", "top_left", self.settings.get("show_zoom_info")),
            (f"  ratio: {optimize_value_string(current_real_zoom.x / current_real_zoom.y, 4)};", "top_left", self.settings.get("show_zoom_info")),
        ]

        for i, (d, pivot_position, show) in enumerate(data):
            if show:
                self.rootEnv.print(d, self.settings.get("top_left_info_position") + self.settings.get("info_interline_space") * i, pivot_position=pivot_position, font=self.settings.get("info_font"))
