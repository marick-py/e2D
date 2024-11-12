from __future__ import annotations

import math as _mt
import random as _rnd
from typing import Any, Generator

PI = _mt.pi
PI_HALF = PI / 2
PI_QUARTER = PI / 4
PI_float = PI * 2

sign = lambda val: -1 if val < 0 else (1 if val > 0 else 0)

cdef class Vector2D:
    cdef double _x, _y
    cdef double _round_values_on_print

    def __init__(self, double x=0.0, double y=0.0) -> None:
        self._x = x
        self._y = y
        self._round_values_on_print = 2

    # Property for x
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, double value):
        self._x = value
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, double value):
        self._y = value
    @property
    def round_values_on_print(self):
        return self._round_values_on_print
    @round_values_on_print.setter
    def round_values_on_print(self, double value):
        self._round_values_on_print = value

    def distance_to(self, Vector2D other, bint rooted=True) -> double:
        cdef double d = (self._x - other._x)**2 + (self._y - other._y)**2
        return d**0.5 if rooted else d

    def angle_to(self, Vector2D other) -> double:
        return _mt.atan2(other._y - self._y, other._x - self._x)

    def point_from_angle_and_radius(self, double rad, double radius) -> Vector2D:
        return Vector2D(radius * _mt.cos(rad) + self._x, radius * _mt.sin(rad) + self._y)

    @property
    def angle(self):
        return _mt.atan2(self._y, self._x)

    @angle.setter
    def angle(self, new_angle) -> None:
        self.rotate(new_angle - self.angle)

    @property
    def sign(self):
        return Vector2D(sign(self._x), sign(self._y))

    @property
    def length(self):
        return (self._x ** 2 + self._y ** 2) ** 0.5
    
    @property
    def length_sqrd(self):
        return self._x ** 2 + self._y ** 2

    def copy(self):
        return Vector2D(self._x, self._y)

    def normalize(self):
        cdef double mag = self.length
        if mag == 0: return self.copy
        return Vector2D(self._x / mag, self._y / mag)

    def floor(self, int n=1) -> Vector2D:
        return self.__floor__(n)

    def ceil(self, int n=1) -> Vector2D:
        return self.__ceil__(n)

    def round(self, int n=1) -> Vector2D:
        return self.__round__(n)

    @classmethod
    def randomize(cls, start, end) -> Vector2D:
        if not isinstance(start, Vector2D):
            if isinstance(start, (int, float)):
                start = Vector2D(start, start)
            else:
                raise TypeError(f"\nArg start must be in [Vector2D, int, float] not [{type(start)}]\n")
        if not isinstance(end, Vector2D):
            if isinstance(end, (int, float)):
                end = Vector2D(end, end)
            else:
                raise TypeError(f"\nArg end must be in [Vector2D, int, float] not [{type(end)}]\n")
        cdef d = end - start
        return Vector2D(start._x + _rnd.random() * d._x, start._y + _rnd.random() * d._y)

    def dot_product(self, Vector2D other) -> double:
        return self._x * other._x + self._y * other._y

    def projection(self, Vector2D other) -> Vector2D:
        cdef double dot_product = self.dot_product(other)
        cdef double magnitude_product = other.length_sqrd
        if magnitude_product == 0:
            raise ValueError("Cannot calculate projection for zero vectors.")
        return other * (dot_product / magnitude_product)

    def reflection(self, Vector2D normal) -> Vector2D:
        return self - self.projection(normal) * 2
    
    def cartesian_to_polar(self) -> tuple[float, float]:
        return self.length, _mt.atan2(self._y, self._x)

    @classmethod
    def polar_to_cartesian(cls, double r, double theta) -> Vector2D:
        return cls(r * _mt.cos(theta), r * _mt.sin(theta))

    def cartesian_to_complex(self) -> complex:
        return self._x + self._y * 1j

    @classmethod
    def complex_to_cartesian(cls, complex complex_n) -> Vector2D:
        return cls(complex_n.real, complex_n.imag)

    def lerp(self, Vector2D other, double t=.1) -> Vector2D:
        return Vector2D(self._x + (other._x - self._x) * t, self._y + (other._y - self._y) * t)

    def rotate(self, double angle, Vector2D center=None) -> None:
        if center == None: center = Vector2D.zero()
        cdef translated = self - center
        cdef cos_angle = _mt.cos(angle)
        cdef sin_angle = _mt.sin(angle)
        self._x = translated._x * cos_angle - translated._y * sin_angle + center._x
        self._y = translated._x * sin_angle + translated._y * cos_angle + center._y

    def no_zero_div_error(self, n, str error_mode="zero") -> Vector2D:
        cdef double result_x, result_y
        cdef bint n_is_zero
        cdef double nan_val = float('nan')
        if isinstance(n, (int, float)):
            if n == 0:
                result_x = 0 if error_mode == "zero" else (self._x if error_mode == "null" else nan_val)
                result_y = 0 if error_mode == "zero" else (self._y if error_mode == "null" else nan_val)
                return Vector2D(result_x, result_y)
            else:
                return self / n
        elif isinstance(n, Vector2D):
            n_is_zero = (n._x == 0) or (n._y == 0)
            result_x = 0 if (n._x == 0 and error_mode == "zero") else (self._x if error_mode == "null" else nan_val) if n._x == 0 else self._x / n._x
            result_y = 0 if (n._y == 0 and error_mode == "zero") else (self._y if error_mode == "null" else nan_val) if n._y == 0 else self._y / n._y
            return Vector2D(result_x, result_y)
        else:
            raise ValueError(f"Arg n must be in [Vector2D, int, float], not [{type(n)}]")
        
    def min(self, Vector2D other) -> Vector2D:
        return Vector2D(min(self._x, other._x), min(self._y, other._y))
    
    def max(self, Vector2D other) -> Vector2D:
        return Vector2D(max(self._x, other._x), max(self._y, other._y))

    def advanced_stringify(self, precision=None, bint use_scientific_notation=False, bint return_as_list=False) -> object:
        cdef int prec = self._round_values_on_print if precision is None else precision
        cdef double abs_x = abs(self._x)
        cdef double abs_y = abs(self._y)

        def optimize(double value, int prec) -> str:
            cdef double abs_value = abs(value)
            if abs_value < 1 / 10**prec and abs_value != 0:
                return "{:.{}e}".format(value, prec)
            elif abs_value < 10**prec:
                return "{:.{}f}".format(value, prec).rstrip('0').rstrip('.')
            else:
                return "{:.{}e}".format(value, prec)

        if return_as_list:
            if use_scientific_notation:
                return [optimize(self._x, prec), optimize(self._y, prec)]
            else:
                return ["{:.{}f}".format(self._x, prec), "{:.{}f}".format(self._y, prec)]
        
        if use_scientific_notation:
            return "{}, {}".format(optimize(self._x, prec), optimize(self._y, prec))
        else:
            return "{:.{}f}, {:.{}f}".format(self._x, prec, self._y, prec)

    def __str__(self) -> str:
        return "{:.{}f}, {:.{}f}".format(self._x, self._round_values_on_print, self._y, self._round_values_on_print)

    def __repr__(self) -> str:
        return "x:{:.{}f}\ty:{:.{}f}".format(self._x, self._round_values_on_print, self._y, self._round_values_on_print)
    
    def __call__(self) -> list:
        return [self._x, self._y]

    # fast operations     Vector2D.operation(both,x,y)
    def add(self, double both=0.0, double x=0.0, double y=0.0) -> Vector2D:
        return Vector2D(self._x + (x + both), self._y + (y + both))

    def sub(self, double both=0.0, double x=0.0, double y=0.0) -> Vector2D:
        return Vector2D(self._x - (x + both), self._y - (y + both))

    def mult(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        return Vector2D(self._x * (x + both), self._y * (y + both))

    def pow(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        return Vector2D(self._x ** (x + both), self._y ** (y + both))

    def mod(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        return Vector2D(self._x % (x + both), self._y % (y + both))

    def div(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        return Vector2D(self._x / (x + both), self._y / (y + both))
    
    def fdiv(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        return Vector2D(self._x // (x + both), self._y // (y + both))

    # fast inplace operations     Vector2D.ioperation(both,x,y)
    def set(self, double both=0.0, double x=0.0, double y=0.0) -> Vector2D:
        self._x = x + both
        self._y = y + both
        return self

    def iadd(self, double both=0.0, double x=0.0, double y=0.0) -> Vector2D:
        self._x += x + both
        self._y += y + both
        return self

    def isub(self, double both=0.0, double x=0.0, double y=0.0) -> Vector2D:
        self._x -= x + both
        self._y -= y + both
        return self

    def imult(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        self._x *= x + both
        self._y *= y + both
        return self

    def ipow(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        self._x **= x + both
        self._y **= y + both
        return self

    def imod(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        self._x %= x + both
        self._y %= y + both
        return self

    def idiv(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        self._x /= x + both
        self._y /= y + both
        return self

    def ifdiv(self, double both=1.0, double x=1.0, double y=1.0) -> Vector2D:
        self._x //= x + both
        self._y //= y + both
        return self

    # normal operations     Vector2D + a
    def __add__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D(self._x + o._x, self._y + o._y)

    def __sub__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D(self._x - o._x, self._y - o._y)

    def __mul__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D(self._x * o._x, self._y * o._y)

    def __mod__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D(self._x % o._x, self._y % o._y)

    def __pow__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D(self._x ** o._x, self._y ** o._y)

    def __truediv__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D(self._x / o._x, self._y / o._y)

    def __floordiv__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D(self._x // o._x, self._y // o._y)

    # in-place operations   Vector2D += a
    def __iadd__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        self._x += o._x
        self._y += o._y
        return self

    def __isub__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        self._x -= o._x
        self._y -= o._y
        return self

    def __imul__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        self._x *= o._x
        self._y *= o._y
        return self

    def __itruediv__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        self._x /= o._x
        self._y /= o._y
        return self

    def __imod__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        self._x %= o._x
        self._y %= o._y
        return self

    def __ipow__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        self._x **= o._x
        self._y **= o._y
        return self

    def __ifloordiv__(self, other):
        cdef Vector2D o = self.__normalize__(other)
        self._x //= o._x
        self._y //= o._y
        return self

    # comparasion
    def __eq__(self, other) -> bool:
        try:
            o = self.__normalize__(other)
        except TypeError:
            return False
        return self._x == o._x and self._y == o._y

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    # absolute value
    def __abs__(self) -> Vector2D:
        return Vector2D(abs(self._x), abs(self._y))

    # rounding operations
    def __round__(self, other=1) -> Vector2D:
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D(round(self._x / o._x) * o._x, round(self._y / o._y) * o._y)

    def __floor__(self, other=1) -> Vector2D:
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D((self._x // o._x) * o._x, (self._y // o._y) * o._y)

    def __ceil__(self, other=1) -> Vector2D:
        cdef Vector2D o = self.__normalize__(other)
        return Vector2D((-(-self._x // o._x)) * o._x, (-(-self._y // o._y)) * o._y)

    def __float__(self) -> Vector2D:
        return Vector2D(float(self._x), float(self._y))

    def __getitem__(self, n) -> float:
        if n == 0 or n == "x":
            return self._x
        elif n == 1 or n == "y":
            return self._y
        else:
            raise IndexError("Vector2D has only 'x' and 'y'.")

    def __iter__(self) -> Generator[float, Any, None]:
        yield self._x
        yield self._y

    cpdef Vector2D __normalize__(self, object other):
        if isinstance(other, Vector2D):
            return other
        elif isinstance(other, (int, float)):
            return Vector2D(float(other), float(other))
        elif isinstance(other, (list, tuple)):
            return Vector2D(float(other[0]), float(other[1]))
        else:
            try:
                return Vector2D(float(other.x), float(other.y))
            except AttributeError:
                raise TypeError(
                    f"The value {other} of type {type(other)} is not a compatible type: "
                    "[int, float, list, tuple, or Vector2D-compatible object]"
                )

    @classmethod
    def zero(cls) -> Vector2D: return V2zero
    @classmethod
    def one(cls) -> Vector2D: return V2one
    @classmethod
    def two(cls) -> Vector2D: return V2two
    @classmethod
    def pi(cls) -> Vector2D: return V2pi
    @classmethod
    def inf(cls) -> Vector2D: return V2inf
    @classmethod
    def neg_one(cls) -> Vector2D: return V2neg_one
    @classmethod
    def neg_two(cls) -> Vector2D: return V2neg_two
    @classmethod
    def neg_pi(cls) -> Vector2D: return V2neg_pi
    @classmethod
    def neg_inf(cls) -> Vector2D: return V2neg_inf
    @classmethod
    def up(cls) -> Vector2D: return V2up
    @classmethod
    def right(cls) -> Vector2D: return V2right
    @classmethod
    def down(cls) -> Vector2D: return V2down
    @classmethod
    def left(cls) -> Vector2D: return V2left
    @classmethod
    def up_right(cls) -> Vector2D: return V2up_right
    @classmethod
    def down_right(cls) -> Vector2D: return V2down_right
    @classmethod
    def up_left(cls) -> Vector2D: return V2up_left
    @classmethod
    def down_left(cls) -> Vector2D: return V2down_left
    @classmethod
    def up_right_norm(cls) -> Vector2D: return V2up_right_norm
    @classmethod
    def down_right_norm(cls) -> Vector2D: return V2down_right_norm
    @classmethod
    def up_left_norm(cls) -> Vector2D: return V2up_left_norm
    @classmethod
    def down_left_norm(cls) -> Vector2D: return V2down_left_norm

    @classmethod
    def new_zero(cls) -> Vector2D: return V2zero.copy()
    @classmethod
    def new_one(cls) -> Vector2D: return V2one.copy()
    @classmethod
    def new_two(cls) -> Vector2D: return V2two.copy()
    @classmethod
    def new_pi(cls) -> Vector2D: return V2pi.copy()
    @classmethod
    def new_inf(cls) -> Vector2D: return V2inf.copy()
    @classmethod
    def new_neg_one(cls) -> Vector2D: return V2neg_one.copy()
    @classmethod
    def new_neg_two(cls) -> Vector2D: return V2neg_two.copy()
    @classmethod
    def new_neg_pi(cls) -> Vector2D: return V2neg_pi.copy()
    @classmethod
    def new_neg_inf(cls) -> Vector2D: return V2neg_inf.copy()
    @classmethod
    def new_up(cls) -> Vector2D: return V2up.copy()
    @classmethod
    def new_right(cls) -> Vector2D: return V2right.copy()
    @classmethod
    def new_down(cls) -> Vector2D: return V2down.copy()
    @classmethod
    def new_left(cls) -> Vector2D: return V2left.copy()
    @classmethod
    def new_up_right(cls) -> Vector2D: return V2up_right.copy()
    @classmethod
    def new_down_right(cls) -> Vector2D: return V2down_right.copy()
    @classmethod
    def new_up_left(cls) -> Vector2D: return V2up_left.copy()
    @classmethod
    def new_down_left(cls) -> Vector2D: return V2down_left.copy()
    @classmethod
    def new_up_right_norm(cls) -> Vector2D: return V2up_right_norm.copy()
    @classmethod
    def new_down_right_norm(cls) -> Vector2D: return V2down_right_norm.copy()
    @classmethod
    def new_up_left_norm(cls) -> Vector2D: return V2up_left_norm.copy()
    @classmethod
    def new_down_left_norm(cls) -> Vector2D: return V2down_left_norm.copy()

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

V2up_right_norm = V2up_right.normalize()
V2down_right_norm = V2down_right.normalize()
V2up_left_norm = V2up_left.normalize()
V2down_left_norm = V2down_left.normalize()

VECTORS_4_DIRECTIONS = (V2right, V2down, V2left, V2up)
VECTORS_4_SEMIDIRECTIONS = (V2down_right, V2down_left, V2up_left, V2up_right)
VECTORS_4_SEMIDIRECTIONS_NORM = (V2down_right_norm, V2down_left_norm, V2up_left_norm, V2up_right_norm)
VECTORS_8_DIRECTIONS = (V2right, V2down_right, V2down, V2down_left, V2left, V2up_left, V2up, V2up_right)
VECTORS_8_DIRECTIONS_NORM = (V2right, V2down_right_norm, V2down, V2down_left_norm, V2left, V2up_left_norm, V2up, V2up_right_norm)