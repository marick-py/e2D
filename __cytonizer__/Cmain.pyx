from libc.math cimport cos, sin, atan2, pi
from libc.stdlib cimport rand, RAND_MAX

cdef class Vector2D:
    #cdef int _storage_type

    cdef float _x
    cdef float _y

    def __init__(self, x=0, y=0):
        self.set(x, y)
    
    property x:
        def __get__(self):
            return self._x

        def __set__(self, value):
            self._x = <float>value
            #self._update_storage_type()

    property y:
        def __get__(self):
            return self._y

        def __set__(self, value):
            self._y = <float>value
            #self._update_storage_type()

    def set(self, x=0, y=0):
        self._x = <float>x
        self._y = <float>y
        #self._update_storage_type()

#    cdef void _update_storage_type(self):
#        if float(self._x) == self._x and float(self._y) == self._y:
#            self._storage_type = 0
#        else:
#            self._storage_type = 1

    def distance_to(self, other):
        d = (self._x - other.x)**2 + (self._y - other.y)**2
        return (d**(1/2))
    
    def angle_to(self, other):
        other = self.__normalize__(other)
        return atan2(other.y - self._y, other.x - self._x)

    def point_from_degs(self, degs, radius):
        cdef float rads = pi / 180 * degs
        cdef float x = radius * cos(rads) + self._x
        cdef float y = radius * sin(rads) + self._y
        return Vector2D(x, y)

    def point_from_rads(self, rad, radius):
        cdef float x = radius * cos(rad) + self._x
        cdef float y = radius * sin(rad) + self._y
        return Vector2D(x, y)

    def copy(self):
        return Vector2D(self._x, self._y)

    @property
    def sign(self):
        return self.no_zero_div_error(abs(self), "zero")

    def floor(self, n=1):
        return self.__floor__(n)

    def ceil(self, n=1):
        return self.__ceil__(n)

    def round(self, n=1):
        return self.__round__(n)

    @staticmethod
    def randomize(start=None, end=None):
        cdef Vector2D start_vector, end_vector
        if isinstance(start, Vector2D):
            start_vector = start
        elif isinstance(start, (int, float)):
            start_vector = Vector2D(start, start)
        elif start is None:
            start_vector = Vector2D(0, 0)
        else:
            raise Exception(f"\nArg start must be in [Vector2D, int, float, None] not a [{type(start)}]\n")
        if isinstance(end, Vector2D):
            end_vector = end
        elif isinstance(end, (int, float)):
            end_vector = Vector2D(end, end)
        elif end is None:
            end_vector = Vector2D(1, 1)
        else:
            raise Exception(f"\nArg end must be in [Vector2D, int, float, None] not a [{type(end)}]\n")
        cdef float rand_value = rand() / RAND_MAX
        cdef Vector2D random_vector = start_vector + Vector2D(rand_value, rand_value) * (end_vector - start_vector)
        return random_vector

    def dot_product(self, other):
        other = self.__normalize__(other)
        return self._x * other.x + self._y * other.y

    def normalize(self):
        mag = self.length()
        if mag == 0: return self
        return Vector2D(self._x / mag, self._y / mag)

    def projection(self, other):
        other = self.__normalize__(other)
        dot_product = self.dot_product(other)
        magnitude_product = other.length() ** 2
        if magnitude_product == 0: raise ValueError("Cannot calculate projection for zero vectors.")
        return other * (dot_product / magnitude_product)

    def reflection(self, normal):
        normal = self.__normalize__(normal)
        projection = self.projection(normal)
        return self - projection * 2

    def cartesian_to_polar(self):
        r = self.length()
        theta = atan2(self._y, self._x)
        return r, theta

    @staticmethod
    def polar_to_cartesian(r, theta):
        cdef float x = r * cos(theta)
        cdef float y = r * sin(theta)
        return Vector2D(x, y)

    def cartesian_to_complex(self):
        return self._x + self._y * 1j

    @staticmethod
    def complex_to_cartesian(complex_n):
        return Vector2D(complex_n.real, complex_n.imag)

    def length(self):
        return (self._x ** 2 + self._y ** 2) ** .5

    def lerp(self, other, t):
        other = self.__normalize__(other)
        if not 0 <= t <= 1:
            raise ValueError("t must be between 0 and 1 for linear interpolation.")
        return Vector2D(self._x + (other.x - self._x) * t, self._y + (other.y - self._y) * t)

    def rotate(self, angle, center=None):
        if center is None: center = Vector2D(0,0)
        else: center = self.__normalize__(center)
        translated = self - center
        cos_angle = cos(angle)
        sin_angle = sin(angle)
        return Vector2D(translated.x * cos_angle - translated.y * sin_angle, translated.x * sin_angle + translated.y * cos_angle) + center
    def no_zero_div_error(self, n, error_mode="zero"):
        cdef Vector2D result
        if isinstance(n, (int, float)):
            if n == 0:
                result = Vector2D(0 if error_mode == "zero" else (self._x if error_mode == "null" else float('nan')),
                                 0 if error_mode == "zero" else (self._y if error_mode == "null" else float('nan')))
            else: result = self / n
        elif isinstance(n, Vector2D):
            result = Vector2D(
                (0 if error_mode == "zero" else (self._x if error_mode == "null" else float('nan'))) if n._x == 0 else self._x / n._x,
                (0 if error_mode == "zero" else (self._y if error_mode == "null" else float('nan'))) if n._y == 0 else self._y / n._y)
        else: raise Exception(f"\nArg n must be in [Vector2D, int, float] not a [{type(n)}]\n")
        return result
    def min(self, other):
        other = self.__normalize__(other)
        return Vector2D(min(self._x, other.x), min(self._y, other.y))
    def max(self, other):
        other = self.__normalize__(other)
        return Vector2D(max(self._x, other.x), max(self._y, other.y))

    def advanced_stringify(self, precision=2, use_scientific_notation=False, return_as_list=False):
        def optimize(value):
            cdef abs_value = abs(value)
            if abs_value < 1/10**precision and abs_value != 0:
                return f"{value:.{precision}e}"
            elif abs_value < 10**precision:
                return f"{value:.{precision}f}".rstrip('0').rstrip('.')
            else:
                return f"{value:.{precision}e}"
        if return_as_list:
            return [optimize(self._x), optimize(self._y)] if use_scientific_notation else [f"{self._x:.{precision}f}", f"{self._y:.{precision}f}"]
        return f"{optimize(self._x)}, {optimize(self._y)}" if use_scientific_notation else f"{self._x:.{precision}f}, {self._y:.{precision}f}"

    def __str__(self):
        return f"{self._x}, {self._y}"

    def __repr__(self):
        return f"x:{self._x}\ty:{self._y}"

    def __call__(self, return_tuple=False):
        return (self._x, self._y) if return_tuple else [self._x, self._y]

    # normal operations     Vector2D + a
    def __add__(self, other):
        other = self.__normalize__(other)
        return Vector2D(self._x + other.x, self._y + other.y)
    def __sub__(self, other):
        other = self.__normalize__(other)
        return Vector2D(self._x - other.x, self._y - other.y)
    def __mul__(self, other):
        other = self.__normalize__(other)
        return Vector2D(self._x * other.x, self._y * other.y)
    def __mod__(self, other):
        other = self.__normalize__(other)
        return Vector2D(self._x % other.x, self._y % other.y)
    def __pow__(self, other):
        other = self.__normalize__(other)
        return Vector2D(self._x ** other.x, self._y ** other.y)
    def __truediv__(self, other):
        other = self.__normalize__(other)
        return Vector2D(self._x / other.x, self._y / other.y)
    def __floordiv__(self, other):
        other = self.__normalize__(other)
        return Vector2D(self._x // other.x, self._y // other.y)
    
    # right operations      a + Vector2D
    def __radd__(self, other):
        return self.__add__(other)
    def __rsub__(self, other):
        other = self.__normalize__(other)
        return Vector2D(other.x - self._x, other.y - self._y)
    def __rmul__(self, other):
        return self.__mul__(other)
    def __rmod__(self, other):
        other = self.__normalize__(other)
        return Vector2D(other.x % self._x, other.y % self._y)
    def __rpow__(self, other):
        other = self.__normalize__(other)
        return Vector2D(other.x ** self._x, other.y ** self._y)
    def __rtruediv__(self, other):
        other = self.__normalize__(other)
        return Vector2D(other.x / self._x, other.y / self._y)
    def __rfloordiv__(self, other):
        other = self.__normalize__(other)
        return Vector2D(other.x // self._x, other.y // self._y)
    
    # in-place operations   Vector2D += a
    def __iadd__(self, other):
        other = self.__normalize__(other)
        self._x += other.x
        self._y += other.y
        return self
    def __isub__(self, other):
        other = self.__normalize__(other)
        self._x -= other.x
        self._y -= other.y
        return self
    def __imul__(self, other):
        other = self.__normalize__(other)
        self._x *= other.x
        self._y *= other.y
        return self
    def __itruediv__(self, other):
        other = self.__normalize__(other)
        self._x /= other.x
        self._y /= other.y
        return self
    def __imod__(self, other):
        other = self.__normalize__(other)
        self._x %= other.x
        self._y %= other.y
        return self
    def __ipow__(self, other):
        other = self.__normalize__(other)
        self._x **= other.x
        self._y **= other.y
        return self
    def __ifloordiv__(self, other):
        other = self.__normalize__(other)
        self._x //= other.x
        self._y //= other.y
        return self

    # comparasion
    def __eq__(self, other):
        try: other = self.__normalize__(other)
        except: return False
        return self._x == other.x and self._y == other.y
    def __ne__(self, other):
        return not self.__eq__(other)

    def __abs__(self):
        return Vector2D(abs(self._x), abs(self._y))
    def __round__(self, n=1):
        n = self.__normalize__(n)
        return Vector2D(round(self._x / n.x) * n.x, round(self._y / n.y) * n.y)
    def __floor__(self, n=1):
        n = self.__normalize__(n)
        return Vector2D((self._x / n.x).__floor__() * n.x, (self._y / n.y).__floor__() * n.y)
    def __ceil__(self, n=1):
        n = self.__normalize__(n)
        return Vector2D((self._x / n.x).__ceil__() * n.x, (self._y / n.y).__ceil__() * n.y)
    def __float__(self):
        return Vector2D(float(self._x), float(self._y))
    def __getitem__(self, n):
        if n in [0, "x"]:
            return self._x
        elif n in [1, "y"]:
            return self._y
        else:
            raise IndexError("V2 has only x,y...")
    cdef __normalize__(self, other):
        if not isinstance(other, Vector2D):
            if any(isinstance(other, cls) for cls in (int, float)):
                return Vector2D(<float>other, <float>other)
            elif any(isinstance(other, cls) for cls in (list, tuple)):
                return Vector2D(<float>other[0], <float>other[1])
            else:
                try:
                    return Vector2D(<float>other.x, <float>other.y)
                except:
                    raise TypeError(f"The value {other} of type {type(other)} is not a num type: [int|float] nor an array type: [list|tuple]")
        return other