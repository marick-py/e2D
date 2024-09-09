from __future__ import annotations

import math as _mt
import random as _rnd

PI = _mt.pi
HALF_PI = PI/2
QUARTER_PI = PI/4
DOUBLE_PI = PI*2

sign = lambda val: -1 if val < 0 else (1 if val > 0 else 0)

class Vector2D:
    round_values_on_print = 2
    def __init__(self, x=.0, y=.0) -> None:
        self.x = x
        self.y = y

    def distance_to(self, other, sqrd=True) -> int|float:
        d = (self.x - other.x)**2 + (self.y - other.y)**2
        return (d**(1/2) if sqrd else d)

    def angle_to(self, other) -> int|float:
        return _mt.atan2(other.y - self.y, other.x - self.x)

    def point_from_angle_and_radius(self, rad, radius) -> "Vector2D":
        return Vector2D(radius * _mt.cos(rad) + self.x, radius * _mt.sin(rad) + self.y)

    @property
    def angle(self) -> int|float:
        return _mt.atan2(self.y, self.x)

    @angle.setter
    def angle(self, argv) -> None:
        print(argv)

    @property
    def copy(self) -> "Vector2D":
        return Vector2D(self.x, self.y)

    @property
    def sign(self) -> "Vector2D":
        return Vector2D(sign(self.x), sign(self.y))
    
    @property
    def normalize(self) -> "Vector2D":
        if (mag:=self.length) == 0:
            return self.copy
        return Vector2D(self.x / mag, self.y / mag)
    
    @property
    def length(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** .5

    def floor(self, n=1) -> "Vector2D":
        return self.__floor__(n)

    def ceil(self, n=1) -> "Vector2D":
        return self.__ceil__(n)
    
    def round(self, n=1) -> "Vector2D":
        return self.__round__(n)

    @classmethod
    def randomize(cls, start, end) -> "Vector2D":
        if not isinstance(start, Vector2D):
            if isinstance(start, (int, float)):
                start = Vector2D(start, start)
            else:
                raise Exception(f"\nArg start must be in [Vector2D, int, float, tuple, list] not a [{type(start)}]\n")
        if not isinstance(end, Vector2D):
            if isinstance(end, (int, float)):
                end = Vector2D(end, end)
            else:
                raise Exception(f"\nArg end must be in [Vector2D, int, float, tuple, list] not a [{type(end)}]\n")
        return start + Vector2D(_rnd.random(), _rnd.random()) * (end - start)
    
    def dot_product(self, other) -> float:
        return self.x * other.x + self.y * other.y

    def projection(self, other) -> "Vector2D":
        dot_product = self.dot_product(other)
        magnitude_product = other.length ** 2
        if magnitude_product == 0:
            raise ValueError("Cannot calculate projection for zero vectors.")
        return other * (dot_product / magnitude_product)

    def reflection(self, normal) -> "Vector2D":
        return self - self.projection(normal) * 2

    def cartesian_to_polar(self) -> tuple:
        r = self.length
        theta = _mt.atan2(self.y, self.x)
        return r, theta

    @classmethod
    def polar_to_cartesian(cls, r, theta) -> "Vector2D":
        x = r * _mt.cos(theta)
        y = r * _mt.sin(theta)
        return cls(x, y)

    def cartesian_to_complex(self) -> complex:
        return self.x + self.y * 1j

    @classmethod
    def complex_to_cartesian(cls, complex_n) -> "Vector2D":
        return cls(complex_n.real, complex_n.imag)

    def lerp(self, other, t=.1) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        if not 0 <= t <= 1:
            raise ValueError("t must be between 0 and 1 for linear interpolation.")
        return Vector2D(self.x + (other.x - self.x) * t, self.y + (other.y - self.y) * t)

    def rotate(self, angle, center=None) -> "Vector2D":
        if center is None: center = Vector2D.zero()
        translated = self - center
        cos_angle = _mt.cos(angle)
        sin_angle = _mt.sin(angle)
        return Vector2D(translated.x * cos_angle - translated.y * sin_angle, translated.x * sin_angle + translated.y * cos_angle) + center

    def no_zero_div_error(self, n, error_mode="zero") -> "Vector2D":
        if isinstance(n, (int, float)):
            if n == 0:
                return Vector2D(0 if error_mode ==  "zero" else (self.x if error_mode == "null" else _mt.nan), 0 if error_mode == "zero" else (self.y if error_mode == "null" else _mt.nan))
            else:
                return self / n
        elif isinstance(n, Vector2D):
            return Vector2D((0 if error_mode == "zero" else (self.x if error_mode == "null" else _mt.nan)) if n.x == 0 else self.x / n.x, (0 if error_mode == "zero" else (self.y if error_mode == "null" else _mt.nan)) if n.y == 0 else self.y / n.y) #type: ignore
        else:
            raise Exception(f"\nArg n must be in [Vector2D, int, float, tuple, list] not a [{type(n)}]\n")

    def min(self, other) -> "Vector2D":
        return Vector2D(min(self.x, other.x), min(self.y, other.y))
    
    def max(self, other) -> "Vector2D":
        return Vector2D(max(self.x, other.x), max(self.y, other.y))

    def advanced_stringify(self, precision=None, use_scientific_notation=False, return_as_list=False) -> str|list[str]:
        precision = self.round_values_on_print if precision == None else precision
        def optimize(value) -> str:
            abs_value = abs(value)
            if abs_value < 1/10**precision and abs_value != 0:
                return f"{value:.{precision}e}"
            elif abs_value < 10**precision:
                return f"{value:.{precision}f}".rstrip('0').rstrip('.')
            else:
                return f"{value:.{precision}e}"
        if return_as_list:
            return [f"{optimize(self.x)}", f"{optimize(self.y)}"] if use_scientific_notation else [f"{self.x:.{precision}f}", f"{self.y:.{precision}f}"]
        return f"{optimize(self.x)}, {optimize(self.y)}" if use_scientific_notation else f"{self.x:.{precision}f}, {self.y:.{precision}f}"

    def __str__(self) -> str:
        return f"{self.x:.{self.round_values_on_print}f}, {self.y:.{self.round_values_on_print}f}"

    def __repr__(self) -> str:
        return f"x:{self.x:.{self.round_values_on_print}f}\ty:{self.y:.{self.round_values_on_print}f}"

    def __call__(self) -> list:
        return [self.x, self.y]
    
    # fast operations     Vector2D.operation(both,x,y)
    def add(self, both=.0, x=.0, y=.0) -> Vector2D:
        return Vector2D(self.x + (x + both), self.y + (y + both))
    
    def sub(self, both=.0, x=.0, y=.0) -> Vector2D:
        return Vector2D(self.x - (x + both), self.y - (y + both))
    
    def mult(self, both=.0, x=.0, y=.0) -> Vector2D:
        return Vector2D(self.x * (x + both), self.y * (y + both))
    
    def pow(self, both=.0, x=.0, y=.0) -> Vector2D:
        return Vector2D(self.x ** (x + both), self.y ** (y + both))
    
    def mod(self, both=.0, x=.0, y=.0) -> Vector2D:
        return Vector2D(self.x % (x + both), self.y % (y + both))
    
    def div(self, both=.0, x=.0, y=.0) -> Vector2D:
        return Vector2D(self.x / (x + both), self.y / (y + both))
    
    def fdiv(self, both=.0, x=.0, y=.0) -> Vector2D:
        return Vector2D(self.x // (x + both), self.y // (y + both))

    # fast inplace operations     Vector2D.ioperation(both,x,y)
    def set(self, both=.0, x=.0, y=.0) -> Vector2D:
        self.x = x + both
        self.y = y + both
        return self

    def iadd(self, both=.0, x=.0, y=.0) -> Vector2D:
        self.x += x + both
        self.y += y + both
        return self
    
    def isub(self, both=.0, x=.0, y=.0) -> Vector2D:
        self.x -= x + both
        self.y -= y + both
        return self
    
    def imult(self, both=.0, x=.0, y=.0) -> Vector2D:
        self.x *= x + both
        self.y *= y + both
        return self
    
    def ipow(self, both=.0, x=.0, y=.0) -> Vector2D:
        self.x **= x + both
        self.y **= y + both
        return self
    
    def imod(self, both=.0, x=.0, y=.0) -> Vector2D:
        self.x %= x + both
        self.y %= y + both
        return self
    
    def idiv(self, both=.0, x=.0, y=.0) -> Vector2D:
        self.x /= x + both
        self.y /= y + both
        return self
    
    def ifdiv(self, both=.0, x=.0, y=.0) -> Vector2D:
        self.x //= x + both
        self.y //= y + both
        return self

    # normal operations     Vector2D + a
    def __add__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(self.x * other.x, self.y * other.y)

    def __mod__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(self.x % other.x, self.y % other.y)
    
    def __pow__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(self.x ** other.x, self.y ** other.y)

    def __truediv__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(self.x / other.x, self.y / other.y)

    def __floordiv__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(self.x // other.x, self.y // other.y)
    
    # right operations      a + Vector2D
    def __radd__(self, other) -> "Vector2D":
        return self.__add__(other)
    
    def __rsub__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(other.x - self.x, other.y - self.y)
    
    def __rmul__(self, other) -> "Vector2D":
        return self.__mul__(other)

    def __rmod__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(other.x % self.x, other.y % self.y)
    
    def __rpow__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(other.x ** self.x, other.y ** self.y)

    def __rtruediv__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(other.x / self.x, other.y / self.y)

    def __rfloordiv__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        return Vector2D(other.x // self.x, other.y // self.y)
    
    # in-place operations   Vector2D += a
    def __iadd__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __imul__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        self.x *= other.x
        self.y *= other.y
        return self

    def __itruediv__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        self.x /= other.x
        self.y /= other.y
        return self
    
    def __imod__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        self.x %= other.x
        self.y %= other.y
        return self
    
    def __ipow__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        self.x **= other.x
        self.y **= other.y
        return self

    def __ifloordiv__(self, other) -> "Vector2D":
        other = Vector2D.__normalize__(other)
        self.x //= other.x
        self.y //= other.y
        return self

    # comparasion
    def __eq__(self, other) -> bool:
        try: other = Vector2D.__normalize__(other)
        except: return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __abs__(self) -> "Vector2D":
        return Vector2D(abs(self.x), abs(self.y))

    def __round__(self, n=1) -> "Vector2D":
        n = Vector2D.__normalize__(n)
        return Vector2D(round(self.x / n.x) * n.x, round(self.y / n.y) * n.y)

    def __floor__(self, n=1) -> "Vector2D":
        n = Vector2D.__normalize__(n)
        return Vector2D((self.x / n.x).__floor__() * n.x, (self.y / n.y).__floor__() * n.y)

    def __ceil__(self, n=1) -> "Vector2D":
        n = Vector2D.__normalize__(n)
        return Vector2D((self.x / n.x).__ceil__() * n.x, (self.y / n.y).__ceil__() * n.y)
    
    def __float__(self) -> "Vector2D":
        return Vector2D(float(self.x), float(self.y))

    def __getitem__(self, n) -> int|float:
        if n == 0 or n == "x":
            return self.x
        elif n == 1 or n == "y":
            return self.y
        else:
            raise IndexError("V2 has only x,y...")
    
    @classmethod
    def __normalize__(cls, other) -> "Vector2D":
        if isinstance(other, Vector2D):
            return other
        if isinstance(other, (int, float)):
            return cls(other, other)
        if isinstance(other, (list, tuple)):
            return cls(*other[:2])
        try:
            return cls(other.x, other.y)
        except:
            raise TypeError(f"The value {other} of type {type(other)} is not a num type: [{int|float}] nor an array type: [{list|tuple}]")
            
    @classmethod
    def zero(cls) -> "Vector2D": return V2zero
    @classmethod
    def one(cls) -> "Vector2D": return V2one
    @classmethod
    def two(cls) -> "Vector2D": return V2two
    @classmethod
    def pi(cls) -> "Vector2D": return V2pi
    @classmethod
    def inf(cls) -> "Vector2D": return V2inf
    @classmethod
    def neg_one(cls) -> "Vector2D": return V2neg_one
    @classmethod
    def neg_two(cls) -> "Vector2D": return V2neg_two
    @classmethod
    def neg_pi(cls) -> "Vector2D": return V2neg_pi
    @classmethod
    def neg_inf(cls) -> "Vector2D": return V2neg_inf
    @classmethod
    def up(cls) -> "Vector2D": return V2up
    @classmethod
    def right(cls) -> "Vector2D": return V2right
    @classmethod
    def down(cls) -> "Vector2D": return V2down
    @classmethod
    def left(cls) -> "Vector2D": return V2left
    @classmethod
    def up_right(cls) -> "Vector2D": return V2up_right
    @classmethod
    def down_right(cls) -> "Vector2D": return V2down_right
    @classmethod
    def up_left(cls) -> "Vector2D": return V2up_left
    @classmethod
    def down_left(cls) -> "Vector2D": return V2down_left
    @classmethod
    def up_right_norm(cls) -> "Vector2D": return V2up_right_norm
    @classmethod
    def down_right_norm(cls) -> "Vector2D": return V2down_right_norm
    @classmethod
    def up_left_norm(cls) -> "Vector2D": return V2up_left_norm
    @classmethod
    def down_left_norm(cls) -> "Vector2D": return V2down_left_norm

    @classmethod
    def new_zero(cls) -> "Vector2D": return V2zero.copy
    @classmethod
    def new_one(cls) -> "Vector2D": return V2one.copy
    @classmethod
    def new_two(cls) -> "Vector2D": return V2two.copy
    @classmethod
    def new_pi(cls) -> "Vector2D": return V2pi.copy
    @classmethod
    def new_inf(cls) -> "Vector2D": return V2inf.copy
    @classmethod
    def new_neg_one(cls) -> "Vector2D": return V2neg_one.copy
    @classmethod
    def new_neg_two(cls) -> "Vector2D": return V2neg_two.copy
    @classmethod
    def new_neg_pi(cls) -> "Vector2D": return V2neg_pi.copy
    @classmethod
    def new_neg_inf(cls) -> "Vector2D": return V2neg_inf.copy
    @classmethod
    def new_up(cls) -> "Vector2D": return V2up.copy
    @classmethod
    def new_right(cls) -> "Vector2D": return V2right.copy
    @classmethod
    def new_down(cls) -> "Vector2D": return V2down.copy
    @classmethod
    def new_left(cls) -> "Vector2D": return V2left.copy
    @classmethod
    def new_up_right(cls) -> "Vector2D": return V2up_right.copy
    @classmethod
    def new_down_right(cls) -> "Vector2D": return V2down_right.copy
    @classmethod
    def new_up_left(cls) -> "Vector2D": return V2up_left.copy
    @classmethod
    def new_down_left(cls) -> "Vector2D": return V2down_left.copy
    @classmethod
    def new_up_right_norm(cls) -> "Vector2D": return V2up_right_norm.copy
    @classmethod
    def new_down_right_norm(cls) -> "Vector2D": return V2down_right_norm.copy
    @classmethod
    def new_up_left_norm(cls) -> "Vector2D": return V2up_left_norm.copy
    @classmethod
    def new_down_left_norm(cls) -> "Vector2D": return V2down_left_norm.copy

from .cvb import *

V2 = Vector2D

V2zero = Vector2D(0, 0)

V2one = Vector2D(1.0, 1.0)
V2two = Vector2D(2.0, 2.0)
V2pi = Vector2D(PI, PI)
V2inf = Vector2D(float("inf"), float("inf"))

V2neg_one = Vector2D(1.0, 1.0)
V2neg_two = Vector2D(2.0, 2.0)
V2neg_pi = Vector2D(PI, PI)
V2neg_inf = Vector2D(float("inf"), float("inf"))

V2up = Vector2D(0, 1)
V2right = Vector2D(1, 0)
V2down = Vector2D(0, -1)
V2left = Vector2D(-1, 0)

V2up_right = Vector2D(1, 1)
V2down_right = Vector2D(1, -1)
V2up_left = Vector2D(-1, 1)
V2down_left = Vector2D(-1, -1)

V2up_right_norm = V2up_right.normalize
V2down_right_norm = V2down_right.normalize
V2up_left_norm = V2up_left.normalize
V2down_left_norm = V2down_left.normalize

VECTORS_4_DIRECTIONS = (V2right, V2down, V2left, V2up)
VECTORS_4_SEMIDIRECTIONS = (V2down_right, V2down_left, V2up_left, V2up_right)
VECTORS_4_SEMIDIRECTIONS_NORM = (V2down_right_norm, V2down_left_norm, V2up_left_norm, V2up_right_norm)
VECTORS_8_DIRECTIONS = (V2right, V2down_right, V2down, V2down_left, V2left, V2up_left, V2up, V2up_right)
VECTORS_8_DIRECTIONS_NORM = (V2right, V2down_right_norm, V2down, V2down_left_norm, V2left, V2up_left_norm, V2up, V2up_right_norm)


def rgb(r:float, g:float, b:float) -> tuple[float, float, float]:
    return (r,g,b)

# def color_lerp(current_c:list|tuple, final_c:list|tuple, step=.1) -> tuple[float, float, float]:
#     return tuple(c + (final_c[i] - c) * step for i,c in enumerate(current_c)) #type: ignore

# def color_fade(starting_c:list|tuple, final_c:list|tuple, index, max_index) -> tuple[float, float, float]:
#     return tuple((starting_c[i] - final_c[i]) / max_index * (max_index - index) + final_c[i] for i in range(3)) #type: ignore

# def weighted_color_fade(colors_dict:dict) -> tuple[float, float, float]:
#     colors = colors_dict.keys()
#     weights = colors_dict.values()

#     if float("inf") in weights: return list(colors)[list(weights).index(float("inf"))]
#     return tuple(sum(n[i]*w for n,w in zip(colors, weights)) / sum(weights) for i in range(3)) #type: ignore

# def color_distance(starting_c:list|tuple, final_c:list|tuple, sqrd) -> float:
#     distance = sum([(starting_c[i]-final_c[i])**2 for i in range(3)])
#     return (distance ** .5) if sqrd else distance

def lerp(starting, ending, step=.1) -> float:
    return starting + (ending - starting) * step

def angular_interpolation(starting_angle, final_angle, step=.1) -> float:
    # my way
    # delta = final_angle - starting_angle
    # return starting_angle + min((delta, delta - DOUBLE_PI, delta + DOUBLE_PI), key=abs) * step
    
    # math way
    shortest_angle = ((((final_angle - starting_angle) % DOUBLE_PI) + DOUBLE_PI * 1.5) % DOUBLE_PI) - PI
    return starting_angle + shortest_angle * step

def bezier_cubic_interpolation(t, p0, p1) -> float:
    return t*p0.y*3*(1 - t)**2 + p1.y*3*(1 - t) * t**2 + t**3

def bezier_quadratic_interpolation(t, p0) -> float:
    return 2*(1-t)*t*p0.y+t**2

def avg_position(*others) -> Vector2D:
    return sum(others) / len(others) #type: ignore

def inter_points(ray, lines, return_inter_lines=False, sort=False, return_empty=False) -> list[tuple[Vector2D | None, tuple[Vector2D, Vector2D]]] | list[Vector2D | None] | list[Vector2D]:
    def lineLineIntersect(P0, P1, Q0, Q1) -> "Vector2D | None":
        d = (P1.x-P0.x) * (Q1.y-Q0.y) + (P1.y-P0.y) * (Q0.x-Q1.x)
        if d == 0:
            return None
        t = ((Q0.x-P0.x) * (Q1.y-Q0.y) + (Q0.y-P0.y) * (Q0.x-Q1.x)) / d
        u = ((Q0.x-P0.x) * (P1.y-P0.y) + (Q0.y-P0.y) * (P0.x-P1.x)) / d
        if 0 <= t <= 1 and 0 <= u <= 1:
            return Vector2D(P1.x * t + P0.x * (1-t), P1.y * t + P0.y * (1-t))
        return None
    
    if return_inter_lines:
        collisions = [(ip, line) for line in lines if ((ip:=lineLineIntersect(line[1], line[0], ray[1], ray[0]))!=None or return_empty)]
        return sorted(collisions, key=lambda x: ray[0].distance_to(x[0], False) if x[0] != None else _mt.inf) if sort else collisions
    else:
        collisions = [ip for line in lines if ((ip:=lineLineIntersect(line[1], line[0], ray[1], ray[0]))!=None or return_empty)]
        return sorted(collisions, key=lambda x: ray[0].distance_to(x, False) if x != None else _mt.inf) if sort else collisions

def get_points(position, size, rotation=0, pos_in_middle=True, return_list=False, clockwise_return=False) -> tuple["Vector2D", "Vector2D", "Vector2D", "Vector2D"] | tuple[list[int|float]|tuple[int|float], list[int|float]|tuple[int|float], list[int|float]|tuple[int|float], list[int|float]|tuple[int|float]]:
    if pos_in_middle:
        d,a = size.length/2, size.angle
        d1, d2 = Vector2D.zero().point_from_angle_and_radius(rotation+a, d), Vector2D.zero().point_from_angle_and_radius(rotation-a, d)
        A, B, C, D = position+d1, position+d2, position-d2, position-d1
    else:
        A, B, C, D = position.copy,\
                     position.point_from_angle_and_radius(rotation + Vector2D.zero().angle_to(Vector2D(size.x, 0)), Vector2D.zero().distance_to(Vector2D(size.x, 0))),\
                     position.point_from_angle_and_radius(rotation + Vector2D.zero().angle_to(Vector2D(0, size.y)), Vector2D.zero().distance_to(Vector2D(0, size.y))),\
                     position.point_from_angle_and_radius(rotation + Vector2D.zero().angle_to(size),                Vector2D.zero().distance_to(size))
    points = (A, B, C, D) if not clockwise_return else (A, B, D, C)
    return points if not return_list else tuple(x() for x in points)

def get_lines(position, size, rotation=0, pos_in_middle=True) -> list[list]:
    A, B, C, D = get_points(position, size, rotation, pos_in_middle)
    return [[A, B], [A, C], [C, D], [D, B]]

def distance_line_point(line_point_a, line_point_b, point_c)  -> float:
    # numpy way
    # return float(_np.linalg.norm(_np.cross((line_point_b-line_point_a)(), (line_point_a-point_c)()))/_np.linalg.norm((line_point_b-line_point_a)())) #type: ignore

    # math way
    return abs((line_point_b.y - line_point_a.y) * point_c.x -\
               (line_point_b.x - line_point_a.x) * point_c.y +\
                line_point_b.x * line_point_a.y - line_point_b.y * line_point_a.x) /\
          ((line_point_b.y-line_point_a.y)**2 + (line_point_b.x-line_point_a.x)**2)**.5

def optimize_value_string(value, precision) -> str:
    abs_value = abs(value)
    if abs_value < 1/10**precision and abs_value != 0:
        return f"{value:.{precision}e}"
    elif abs_value < 10**precision:
        return f"{value:.{precision}f}".rstrip('0').rstrip('.')
    else:
        return f"{value:.{precision}e}"