from colorsys import hsv_to_rgb as __hsv_to_rgb_def__, hls_to_rgb as __hls_to_rgb_def__, rgb_to_hls as __rgb_to_hls__, rgb_to_hsv as __rgb_to_hsv__
from typing import Any, Callable, Generator, Literal
from pygame.color import Color as __color_pygame__
from random import randint as __randint__

RGB_COLOR_MODE = "rgb"
RGBA_COLOR_MODE = "rgba"
BGR_COLOR_MODE = "bgr"
BGRA_COLOR_MODE = "bgra"
GRAY_COLOR_MODE = "g"
HSV_COLOR_MODE = "hsv"
HLS_COLOR_MODE = "hls"
# CMYK_COLOR_MODE = "cmyk"
# LAB_COLOR_MODE = "lab"

__LITERAL_COLOR_MODES__ = Literal["rgb","rgba","bgr","bgra","g","hsv","hls"] #,"cmyk","lab"]

def __hsv_to_rgb__(h:int|float, s:int|float, v:int|float) -> tuple[int|float, int|float, int|float]:
    r,g,b = __hsv_to_rgb_def__(h, s, v)
    return r*255, g*255, b*255

def __hls_to_rgb__(h:int|float, s:int|float, v:int|float) -> tuple[int|float, int|float, int|float]:
    r,g,b = __hls_to_rgb_def__(h, s, v)
    return r*255, g*255, b*255
    
__conversion_table__ :dict[__LITERAL_COLOR_MODES__, dict[__LITERAL_COLOR_MODES__, Callable]]= {
    "rgb": {
        "rgba": lambda r,g,b: (r, g, b, 255.0),
        "bgr": lambda r,g,b: (b, g, r),
        "bgra": lambda r,g,b: (b, g, r, 255.0),
        "g": lambda r,g,b: (.2989*r+.587*g+.114*b,),
        "hsv": lambda r,g,b: __rgb_to_hsv__(r/255.0, g/255.0, b/255.0),
        "hls": lambda r,g,b: __rgb_to_hls__(r/255.0, g/255.0, b/255.0),
        },
    "rgba": {
        "rgb": lambda r,g,b,a: (r, g, b),
        "bgr": lambda r,g,b,a: (b, g, r),
        "bgra": lambda r,g,b,a: (b, g, r, a),
        "g": lambda r,g,b,a: (.2989*r+.587*g+.114*b,),
        "hsv": lambda r,g,b,a: __rgb_to_hsv__(r/255.0, g/255.0, b/255.0),
        "hls": lambda r,g,b,a: __rgb_to_hls__(r/255.0, g/255.0, b/255.0),
        },
    "bgr": {
        "rgb": lambda b,g,r: (r, g, b),
        "rgba": lambda b,g,r: (r, g, b, 255.0),
        "bgra": lambda b,g,r: (b, g, r, 255.0),
        "g": lambda b,g,r: (.2989*r+.587*g+.114*b,),
        "hsv": lambda b,g,r: __rgb_to_hsv__(r/255.0, g/255.0, b/255.0),
        "hls": lambda b,g,r: __rgb_to_hls__(r/255.0, g/255.0, b/255.0),
        },
    "bgra": {
        "rgb": lambda b,g,r,a: (r, g, b),
        "rgba": lambda b,g,r,a: (b, g, r, a),
        "bgr": lambda b,g,r,a: (b, g, r),
        "g": lambda b,g,r,a: (.2989*r+.587*g+.114*b,),
        "hsv": lambda b,g,r,a: __rgb_to_hsv__(r/255.0, g/255.0, b/255.0),
        "hls": lambda b,g,r,a: __rgb_to_hls__(r/255.0, g/255.0, b/255.0),
        },
    "g": {
        "rgb": lambda g: (g, g, g),
        "rgba": lambda g: (g, g, g, 255.0),
        "bgr": lambda g: (g, g, g),
        "bgra": lambda g: (g, g, g, 255.0),
        "hsv": lambda g: __rgb_to_hsv__(g/255.0, g/255.0, g/255.0),
        "hls": lambda g: __rgb_to_hls__(g/255.0, g/255.0, g/255.0),
    },
    "hsv": {
        "rgb": lambda h,s,v: __hsv_to_rgb__(h,s,v),
        "rgba": lambda h,s,v: (*__hsv_to_rgb__(h,s,v), 255.0),
        "bgr": lambda h,s,v: __hsv_to_rgb__(h,s,v)[::-1],
        "bgra": lambda h,s,v: (*__hsv_to_rgb__(h,s,v)[::-1], 255.0),
        "g": lambda h,s,v: (sum(m*v for m,v in zip((.2989, .587, .114), __hsv_to_rgb__(h,s,v))),),
        "hls": lambda h,s,v: __rgb_to_hls__(*__hsv_to_rgb_def__(h,s,v)),
        },
    "hls": {
        "rgb": lambda h,l,s: __hls_to_rgb__(h,l,s),
        "rgba": lambda h,l,s: (*__hls_to_rgb__(h,l,s), 255.0),
        "bgr": lambda h,l,s: __hls_to_rgb__(h,l,s)[::-1],
        "bgra": lambda h,l,s: (*__hls_to_rgb__(h,l,s)[::-1], 255.0),
        "g": lambda h,l,s: (sum(m*v for m,v in zip((.2989, .587, .114), __hls_to_rgb__(h,l,s))),),
        "hsv": lambda h,l,s: __rgb_to_hsv__(*__hls_to_rgb_def__(h,l,s)),
        },
}

class Color:
    def __init__(self, *values, mode:__LITERAL_COLOR_MODES__=RGB_COLOR_MODE) -> None:
        self.__dict__ = dict(zip(mode, values))
        self.mode :__LITERAL_COLOR_MODES__= mode

    def lerp(self, other:"Color", step=.1) -> "Color":
        return (self + (other - self).mult(step))

    @staticmethod
    def weighted_lerp(colors_dict:dict["Color", float]) -> "Color":
        """Colors HAVE to be in the rgb format."""

        colors = colors_dict.keys()
        weights = colors_dict.values()
        if float("inf") in weights: return list(colors)[list(weights).index(float("inf"))]
        return sum(n.mult(w) for n,w in zip(colors, weights)).div(sum(weights))

    def distance_to(self, other:"Color", rooted=True) -> float:
        d = sum((self.to_rgb() - other.to_rgb()).pow(2))
        return (d ** .5) if rooted else d
    
    @classmethod
    def new_rgb(cls, r:int|float, g:int|float, b:int|float) -> "Color":
        return Color(r,g,b, mode=RGB_COLOR_MODE)
    @classmethod
    def new_rgba(cls, r:int|float, g:int|float, b:int|float, a:int|float) -> "Color":
        return Color(r,g,b,a, mode=RGBA_COLOR_MODE)
    @classmethod
    def new_bgr(cls, b:int|float, g:int|float, r:int|float) -> "Color":
        return Color(b,g,r, mode=BGR_COLOR_MODE)
    @classmethod
    def new_bgra(cls, b:int|float, g:int|float, r:int|float, a:int|float) -> "Color":
        return Color(b,g,r,a, mode=BGRA_COLOR_MODE)
    @classmethod
    def new_g(cls, g) -> "Color":
        return Color(g, mode=GRAY_COLOR_MODE)
    @classmethod
    def new_hsv(cls, h:int|float, s:int|float, v:int|float) -> "Color":
        return Color(h,s,v, mode=HSV_COLOR_MODE)
    @classmethod
    def new_hls(cls, h:int|float, l:int|float, s:int|float) -> "Color":
        return Color(h,l,s, mode=HLS_COLOR_MODE)
    # @classmethod
    # def new_cmyk(cls, c:int|float, m:int|float, y:int|float, k:int|float) -> Color:
    #     return Color(c,m,y,k, mode=CMYK_COLOR_MODE)
    # @classmethod
    # def new_lab(cls, l:int|float, a:int|float, b:int|float) -> Color:
    #     return Color(l,a,b, mode=LAB_COLOR_MODE)

    @property
    def values(self) -> tuple[int|float, ...]:
        return tuple(self.__dict__.values())[:-1]

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(self.__dict__.keys())[:-1]
    
    @property
    def items(self) -> tuple[tuple[str, int|float], ...]:
        return tuple(self.__dict__.items())[:-1]

    def copy(self) -> "Color":
        return Color(*self.values, mode=self.mode)

    def to_mode(self, mode:__LITERAL_COLOR_MODES__) -> "Color":
        if mode == self.mode: return self.copy()
        return Color(*__conversion_table__[self.mode][mode](*self.values), mode=mode)

    def to_rgb(self) -> "Color":
        if self.mode == RGB_COLOR_MODE: return self.copy()
        return Color(*__conversion_table__[self.mode][RGB_COLOR_MODE](*self.values), mode=RGB_COLOR_MODE)
    def to_rgba(self) -> "Color":
        if self.mode == RGBA_COLOR_MODE: return self.copy()
        return Color(*__conversion_table__[self.mode][RGBA_COLOR_MODE](*self.values), mode=RGBA_COLOR_MODE)
    def to_bgr(self) -> "Color":
        if self.mode == BGR_COLOR_MODE: return self.copy()
        return Color(*__conversion_table__[self.mode][BGR_COLOR_MODE](*self.values), mode=BGR_COLOR_MODE)
    def to_bgra(self) -> "Color":
        if self.mode == BGRA_COLOR_MODE: return self.copy()
        return Color(*__conversion_table__[self.mode][BGRA_COLOR_MODE](*self.values), mode=BGRA_COLOR_MODE)
    def to_g(self) -> "Color":
        if self.mode == GRAY_COLOR_MODE: return self.copy()
        return Color(*__conversion_table__[self.mode][GRAY_COLOR_MODE](*self.values), mode=GRAY_COLOR_MODE)
    def to_hsv(self) -> "Color":
        if self.mode == HSV_COLOR_MODE: return self.copy()
        return Color(*__conversion_table__[self.mode][HSV_COLOR_MODE](*self.values), mode=HSV_COLOR_MODE)
    def to_hls(self) -> "Color":
        if self.mode == HLS_COLOR_MODE: return self.copy()
        return Color(*__conversion_table__[self.mode][HLS_COLOR_MODE](*self.values), mode=HLS_COLOR_MODE)

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return "Color(" + ", ".join(f"{k}:{v}" for k, v in self.items) + ")"

    def __call__(self) -> __color_pygame__:
        return __color_pygame__(int(self.r), int(self.g), int(self.b))
    
    # fast operations     Vector2D.operation(both,x,y)
    def add(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        return Color(self.r + (r + all3), self.g + (g + all3), self.b + (b + all3))
    
    def sub(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        return Color(self.r - (r + all3), self.g - (g + all3), self.b - (b + all3))
    
    def mult(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        return Color(self.r * r * all3, self.g * g * all3, self.b * b * all3)
    
    def pow(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        return Color(self.r ** (r + all3), self.g ** (g + all3), self.b ** (b + all3))
    
    def mod(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        return Color(self.r % (r + all3), self.g % (g + all3), self.b % (b + all3))
    
    def div(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        return Color(self.r / r / all3, self.g / g / all3, self.b / b / all3)
    
    def fdiv(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        return Color(self.r // r // all3, self.g // g // all3, self.b // b // all3)

    # fast inplace operations     Vector2D.ioperation(both,x,y)
    def set(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        self.r = r + all3
        self.g = g + all3
        self.b = b + all3
        return self

    def iadd(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        self.r += r + all3
        self.g += g + all3
        self.b += b + all3
        return self
    
    def isub(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        self.r -= r + all3
        self.g -= g + all3
        self.b -= b + all3
        return self
    
    def imult(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        self.r *= r * all3
        self.g *= g * all3
        self.b *= b * all3
        return self
    
    def ipow(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        self.r **= r + all3
        self.g **= g + all3
        self.b **= b + all3
        return self
    
    def imod(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        self.r %= r + all3
        self.g %= g + all3
        self.b %= b + all3
        return self
    
    def idiv(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        self.r /= r * all3
        self.g /= g * all3
        self.b /= b * all3
        return self
    
    def ifdiv(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        self.r //= r * all3
        self.g //= g * all3
        self.b //= b * all3
        return self

    # normal operations     Vector2D + a
    def __add__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)
    
    def __sub__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(self.r - other.r, self.g - other.g, self.b - other.b)
    
    def __mul__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(self.r * other.r, self.g * other.g, self.b * other.b)

    def __mod__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(self.r % other.r, self.g % other.g, self.b % other.b)
    
    def __pow__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(self.r ** other.r, self.g ** other.g, self.b ** other.b)

    def __truediv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(self.r / other.r, self.g / other.g, self.b / other.b)

    def __floordiv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(self.r // other.r, self.g // other.g, self.b // other.b)
    
    # right operations      a + Vector2D
    def __radd__(self, other) -> "Color":
        return self.__add__(other)
    
    def __rsub__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(other.r - self.r, other.g - self.g, other.b - self.b)
    
    def __rmul__(self, other) -> "Color":
        return self.__mul__(other)

    def __rmod__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(other.r % self.r, other.g % self.g, other.b % self.b)
    
    def __rpow__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(other.r ** self.r, other.g ** self.g, other.b ** self.b)

    def __rtruediv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(other.r / self.r, other.g / self.g, other.b / self.b)

    def __rfloordiv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        return Color(other.r // self.r, other.g // self.g, other.b // self.b)
    
    # in-place operations   Vector2D += a
    def __iadd__(self, other) -> "Color":
        other = Color.__normalize__(other)
        self.r += other.r
        self.g += other.g
        self.b += other.b
        return self

    def __isub__(self, other) -> "Color":
        other = Color.__normalize__(other)
        self.r -= other.r
        self.g -= other.g
        self.b -= other.b
        return self
    
    def __imul__(self, other) -> "Color":
        other = Color.__normalize__(other)
        self.r *= other.r
        self.g *= other.g
        self.b *= other.b
        return self

    def __itruediv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        self.r **= other.r
        self.g **= other.g
        self.b **= other.b
        return self
    
    def __imod__(self, other) -> "Color":
        other = Color.__normalize__(other)
        self.r %= other.r
        self.g %= other.g
        self.b %= other.b
        return self
    
    def __ipow__(self, other) -> "Color":
        other = Color.__normalize__(other)
        self.r /= other.r
        self.g /= other.g
        self.b /= other.b
        return self

    def __ifloordiv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        self.r //= other.r
        self.g //= other.g
        self.b //= other.b
        return self

    # comparasion
    def __eq__(self, other) -> bool:
        try: other = Color.__normalize__(other)
        except: return False
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __abs__(self) -> "Color":
        self = self.to_rgb()
        return Color(abs(self.r), abs(self.g), abs(self.b))

    def __round__(self, n=1) -> "Color":
        n = Color.__normalize__(n)
        return Color(round(self.r / n.r) * n.r, round(self.g / n.g) * n.g, round(self.b / n.b) * n.b)

    def __floor__(self, n=1) -> "Color":
        n = Color.__normalize__(n)
        return Color((self.r / n.r).__floor__() * n.r, (self.g / n.g).__floor__() * n.g, (self.b / n.b).__floor__() * n.b)

    def __ceil__(self, n=1) -> "Color":
        n = Color.__normalize__(n)
        return Color((self.r / n.r).__ceil__() * n.r, (self.g / n.g).__ceil__() * n.g, (self.b / n.b).__ceil__() * n.b)
    
    def __float__(self) -> "Color":
        return Color(float(self.r), float(self.g), float(self.b))

    def __getitem__(self, n) -> int|float:
        return self.values[n] if isinstance(n, int) else self.values[self.keys.index(n)]
    
    def __iter__(self) -> Generator[float, Any, None]:
        for val in self.values:
            yield val
    
    @classmethod
    def __normalize__(cls, other) -> "Color":
        if isinstance(other, Color):
            return other
        if isinstance(other, __color_pygame__):
            return cls(*other[:], mode="rgba")
        if isinstance(other, (int, float)):
            return cls(other, other, other)
        if isinstance(other, (list, tuple)):
            return cls(*other[:3])
        try:
            return cls(*other.values, mode=other.mode)
        except:
            raise TypeError(f"The value {other} of type {type(other)} is not a num type: [{int|float}] nor an array type: [{list|tuple}]")
    
    @classmethod
    def white(cls) -> "Color": return Color(255,255,255)
    @classmethod
    def black(cls) -> "Color": return Color(0,0,0)
    @classmethod
    def red(cls) -> "Color": return Color(255,0,0)
    @classmethod
    def green(cls) -> "Color": return Color(0,255,0)
    @classmethod
    def blue(cls) -> "Color": return Color(0,0,255)
    
    # @classmethod
    # def (cls) -> "Color": return Color(0,0,255)

    @classmethod
    def randomize(cls) -> "Color":
        return Color(__randint__(0,255), __randint__(0,255), __randint__(0,255))


WHITE_COLOR = Color.white()
BLACK_COLOR = Color.black()
RED_COLOR = Color.red()
GREEN_COLOR = Color.green()
BLUE_COLOR = Color.blue()

WHITE_COLOR_PYG = WHITE_COLOR()
BLACK_COLOR_PYG = BLACK_COLOR()
RED_COLOR_PYG = RED_COLOR()
GREEN_COLOR_PYG = GREEN_COLOR()
BLUE_COLOR_PYG = BLUE_COLOR()
