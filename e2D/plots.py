from .envs import *

def no_error_function(function, args) -> int|float:
    try:
        return function(args)
    except:
        return float("inf")

def no_error_complex_function(function, args) -> V2|Vector2D:
    res :complex= function(args)
    return V2(res.real, res.imag)

class Function:
    def __init__(self, function, plot:"Plot", color, use_y_as_primary=False, auto_connect_treshold=5, points_radius=2, points_color=None) -> None:
        self.auto_connect_treshold = auto_connect_treshold
        self.plot = plot
        self.color = color
        self.points_radius = points_radius
        self.points_color = points_color
        self.update_function(function, use_y_as_primary)
    
    def update_function(self, new_function, use_y_as_primary=False) -> None:
        self.function = new_function
        if not use_y_as_primary:
            self.points = [V2(x * self.plot.step, y) for x in range(int(self.plot.starting_x / self.plot.step), int(self.plot.ending_x / self.plot.step)) if self.plot.ending_y < (y:=no_error_function(new_function, x * self.plot.step)) < self.plot.starting_y]
        else:
            self.points = [V2(x, y * self.plot.step) for y in range(int(self.plot.starting_y / self.plot.step), int(self.plot.ending_y / self.plot.step)) if self.plot.starting_x < (x:=no_error_function(new_function, y * self.plot.step)) < self.plot.ending_x]
        self.full_auto_connect = not any(abs(point.y - self.points[i].y) > self.auto_connect_treshold for i,point in enumerate(self.points[1:]))

    def draw(self) -> None:
        if self.points_radius:
            for point in self.points:
                pg.draw.circle(self.plot.rootEnv.screen, self.color if self.points_color == None else self.points_color, self.plot.plot2real(point)(), self.points_radius)

        if self.full_auto_connect:
            pg.draw.lines(self.plot.rootEnv.screen, self.color, False, [self.plot.plot2real(point)() for point in self.points]) #type: ignore
        else:
            real_points = [self.plot.plot2real(point)() for point in self.points]
            for i,(point, real_point) in enumerate(zip(self.points[1:], real_points[1:])):
                if abs(point[1] - self.points[i][1]) < self.auto_connect_treshold:
                    pg.draw.line(self.plot.rootEnv.screen, self.color, real_points[i], real_point) #type: ignore

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
    
    def update_function(self, new_function) -> None:
        self.function = new_function
        self.points :list[V2|Vector2D]= [point for t in range(int(self.starting_t / self.step), int(self.ending_t / self.step)) if (self.plot.ending_y < (point:=no_error_complex_function(new_function, t * self.step)).y < self.plot.starting_y) and (self.plot.starting_x < point.x < self.plot.ending_x)]
        self.full_auto_connect = not any(point.distance_to(self.points[i]) > self.auto_connect_treshold for i,point in enumerate(self.points[1:]))

    def draw(self) -> None:
        if self.points_radius:
            for point in self.points:
                pg.draw.circle(self.plot.rootEnv.screen, self.color if self.points_color == None else self.points_color, self.plot.plot2real(point)(), self.points_radius)

        if self.full_auto_connect:
            pg.draw.lines(self.plot.rootEnv.screen, self.color, False, [self.plot.plot2real(point)() for point in self.points]) #type: ignore
        else:
            real_points = [self.plot.plot2real(point)() for point in self.points]
            for i,(point, real_point) in enumerate(zip(self.points[1:], real_points[1:])):
                if point.distance_to(self.points[i]) < self.auto_connect_treshold:
                    pg.draw.line(self.plot.rootEnv.screen, self.color, real_points[i], real_point) #type: ignore

class Plot:
    def __init__(self, rootEnv, top_left_coord:V2|Vector2D, bottom_right_coord: V2|Vector2D, draw_position:V2|Vector2D, draw_size:V2|Vector2D, step:float=.1) -> None:
        self.rootEnv = rootEnv
        self.top_left_coord = top_left_coord
        self.bottom_right_coord = bottom_right_coord
        self.starting_x, self.starting_y = self.top_left_coord
        self.ending_x, self.ending_y = self.bottom_right_coord

        self.position = draw_position
        self.size = draw_size
        self.step = step
        self.update_real()
        self.functions :list[Function|ComplexFunction]= []

    def load_function(self, function:Function|ComplexFunction) -> None:
        self.functions.append(function)

    def plot2real(self, plot_position:V2|Vector2D) -> V2|Vector2D:
        return self.position + (plot_position + self.top_left_coord * -1) * self.ratio
    
    def update_real(self) -> None:
        self.ratio = self.size / (self.bottom_right_coord - self.top_left_coord)

    def draw(self) -> None:
        if self.starting_x < 0 < self.ending_x: pg.draw.line(self.rootEnv.screen, (100,100,100), self.plot2real(V2(self.starting_x, 0))(), self.plot2real(V2(self.ending_x, 0))())
        if self.ending_y < 0 < self.starting_y: pg.draw.line(self.rootEnv.screen, (100,100,100), self.plot2real(V2(0, self.starting_y))(), self.plot2real(V2(0, self.ending_y))())
        
        for function in self.functions: function.draw()
        pg.draw.rect(self.rootEnv.screen, (255,255,255), self.position() + self.size(), 5) #type: ignore

        self.rootEnv.print(str(self.top_left_coord), self.position)
        self.rootEnv.print(str(V2(self.top_left_coord.x, self.bottom_right_coord.y)), self.position + self.size * V2(0, 1))
        self.rootEnv.print(str(self.bottom_right_coord), self.position + self.size)
        self.rootEnv.print(str(V2(self.bottom_right_coord.x, self.top_left_coord.y)), self.position + self.size * V2(1, 0))