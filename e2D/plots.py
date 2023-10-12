from .envs import *

def no_error_function(function, args) -> int|float|None:
    try:
        return res if type(res:=function(args)) != complex else None
    except:
        return float("inf")

def no_error_complex_function(function, args) -> V2|Vector2D:
    res :complex= function(args)
    return V2(res.real, res.imag)

class Function:
    def __init__(self, function, plot:"Plot", color, use_y_as_primary=False, auto_connect_treshold:float=float("inf"), points_radius=2, points_color=None) -> None:
        self.auto_connect_treshold = auto_connect_treshold
        self.plot = plot
        self.color = color
        self.points_radius = points_radius
        self.use_y_as_primary = use_y_as_primary
        self.points_color = self.color if points_color == None else self.points_color
        self.update_function(function, self.use_y_as_primary)
    
    def update_points(self) -> None:
        self.update_function(self.function, self.use_y_as_primary)

    def update_function(self, new_function, use_y_as_primary=False) -> None:
        self.use_y_as_primary = use_y_as_primary
        self.function = new_function

        if not self.use_y_as_primary:
            real_step = abs(self.plot.ending_x - self.plot.starting_x) * self.plot.step
            self.points = [V2(self.plot.starting_x + x * real_step, y) for x in range(int(1 / self.plot.step)) if (y:=no_error_function(new_function, self.plot.starting_x + x * real_step)) != None and self.plot.ending_y < y < self.plot.starting_y]
        else:
            real_step = abs(self.plot.ending_y - self.plot.starting_y) * self.plot.step
            self.points = [V2(x, self.plot.starting_y + y * real_step) for y in range(int(1 / self.plot.step)) if (x:=no_error_function(new_function, self.plot.starting_y + y * real_step)) != None and self.plot.starting_x < x < self.plot.ending_x]
        self.full_auto_connect = not any(abs(point.y - self.points[i].y) > self.auto_connect_treshold for i,point in enumerate(self.points[1:]))
    
    def draw(self) -> None:
        if self.points_radius:
            for point in self.points:
                pg.draw.circle(self.plot.canvas, self.points_color, self.plot.plot2real(point)(), self.points_radius)

        if len(self.points) < 2: return
        self.draw_line = [self.plot.plot2real(point)() for point in self.points]
        if self.full_auto_connect:
            pg.draw.lines(self.plot.canvas, self.color, False, self.draw_line) #type: ignore
        else:
            for i,(point, real_point) in enumerate(zip(self.points[1:], self.draw_line[1:])):
                if abs(point[1] - self.points[i][1]) < self.auto_connect_treshold:
                    pg.draw.line(self.plot.canvas, self.color, self.draw_line[i], real_point) #type: ignore

class ComplexFunction:
    def __init__(self, function, plot:"Plot", starting_t:float=-10, ending_t:float=10, step=.01, color=(255,255,255), auto_connect_treshold=5, points_radius=2, points_color=None) -> None:
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
        self.points :list[V2|Vector2D]= [point for t in range(int(self.starting_t / self.step), int(self.ending_t / self.step)) if (self.plot.ending_y < (point:=no_error_complex_function(new_function, t * self.step)).y < self.plot.starting_y) and (self.plot.starting_x < point.x < self.plot.ending_x)]
        self.full_auto_connect = not any(point.distance_to(self.points[i]) > self.auto_connect_treshold for i,point in enumerate(self.points[1:]))

    def draw(self) -> None:
        if self.points_radius:
            for point in self.points:
                pg.draw.circle(self.plot.canvas, self.color if self.points_color == None else self.points_color, self.plot.plot2real(point)(), self.points_radius)

        if len(self.points) < 2: return
        if self.full_auto_connect:
            pg.draw.lines(self.plot.canvas, self.color, False, [self.plot.plot2real(point)() for point in self.points])
        else:
            real_points = [self.plot.plot2real(point)() for point in self.points]
            for i,(point, real_point) in enumerate(zip(self.points[1:], real_points[1:])):
                if point.distance_to(self.points[i]) < self.auto_connect_treshold:
                    pg.draw.line(self.plot.canvas, self.color, real_points[i], real_point) #type: ignore

class Plot:
    def __init__(self, rootEnv:"RootEnv", top_left_coord:V2|Vector2D, bottom_right_coord: V2|Vector2D, draw_position:V2|Vector2D, draw_size:V2|Vector2D, step:float=.01) -> None:
        self.rootEnv = rootEnv

        self.top_left_coord = top_left_coord
        self.bottom_right_coord = bottom_right_coord
        self.update_zoom(0)

        self.position = draw_position
        self.size = draw_size
        self.step = step
        self.functions :list[Function|ComplexFunction]= []

        self.canvas = pg.Surface(self.size())
        self.dragging = None

    def update_zoom(self, zoom_input:int|float) -> None:
        self.top_left_coord += V2(-1, 1) * -zoom_input
        self.bottom_right_coord += V2(1, -1) * -zoom_input
        self.starting_x, self.starting_y = self.top_left_coord
        self.ending_x, self.ending_y = self.bottom_right_coord

    def load_function(self, function:Function|ComplexFunction) -> None:
        self.functions.append(function)

    def plot2real(self, plot_position:V2|Vector2D) -> V2|Vector2D:
        return (plot_position + self.top_left_coord * -1) * self.size / (self.bottom_right_coord - self.top_left_coord)

    def update_canvas(self) -> None:
        self.canvas.fill((0,0,0))
        if self.starting_x < 0 < self.ending_x: pg.draw.line(self.canvas, (100,100,100), self.plot2real(V2(self.starting_x, 0))(), self.plot2real(V2(self.ending_x, 0))())
        if self.ending_y < 0 < self.starting_y: pg.draw.line(self.canvas, (100,100,100), self.plot2real(V2(0, self.starting_y))(), self.plot2real(V2(0, self.ending_y))())
        
        for function in self.functions: function.draw()
        pg.draw.rect(self.canvas, (255,255,255), V2z() + self.size(), 5) #type: ignore

        self.rootEnv.print(str(self.top_left_coord), V2z.copy(), bg_color=(0,0,0), personalized_surface=self.canvas)
        self.rootEnv.print(str(V2(self.top_left_coord.x, self.bottom_right_coord.y)), self.size * V2(0, 1), fixed_sides=TEXT_FIXED_SIDES_BOTTOM_LEFT, bg_color=(0,0,0), personalized_surface=self.canvas)
        self.rootEnv.print(str(self.bottom_right_coord), self.size.copy(), fixed_sides=TEXT_FIXED_SIDES_BOTTOM_RIGHT, bg_color=(0,0,0), personalized_surface=self.canvas)
        self.rootEnv.print(str(V2(self.bottom_right_coord.x, self.top_left_coord.y)), self.size * V2(1, 0), fixed_sides=TEXT_FIXED_SIDES_TOP_RIGHT, bg_color=(0,0,0), personalized_surface=self.canvas)
    
    def update(self) -> None:
        if self.rootEnv.mouse.just_released[0] and self.dragging != None:
            self.dragging = None
            for function in self.functions:
                function.update_points()
            self.update_canvas()

        if self.position.x < self.rootEnv.mouse.position.x < self.position.x + self.size.x and \
           self.position.y < self.rootEnv.mouse.position.y < self.position.y + self.size.y:
            for event in self.rootEnv.events:
                if event.type == pg.MOUSEWHEEL:
                    self.update_zoom(event.y)
                    for function in self.functions:
                        function.update_points()
                    self.update_canvas()
            
            if self.rootEnv.mouse.just_pressed[0] and self.dragging == None:
                self.dragging = self.rootEnv.mouse.position.copy()
            
            if self.dragging:
                offset = (self.dragging - self.rootEnv.mouse.position)* V2(1, -1) * (abs(self.bottom_right_coord - self.top_left_coord) / self.size)
                self.dragging = self.rootEnv.mouse.position.copy()
                self.top_left_coord += offset
                self.bottom_right_coord += offset
                self.top_left_coord = self.top_left_coord.__round__(.01)
                self.bottom_right_coord = self.bottom_right_coord.__round__(.01)
                self.update_zoom(0)
                self.update_canvas()

    def draw(self) -> None:
        self.rootEnv.screen.blit(self.canvas, self.position())