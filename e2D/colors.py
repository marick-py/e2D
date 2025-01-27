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
        return __color_pygame__(*map(int, self.to_rgba().values))
    
    # fast operations     Vector2D.operation(both,x,y)
    def add(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        c_color = self.to_rgb()
        return Color(c_color.r + (r + all3), c_color.g + (g + all3), c_color.b + (b + all3)).to_mode(self.mode) # type: ignore
    
    def sub(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        c_color = self.to_rgb()
        return Color(c_color.r - (r + all3), c_color.g - (g + all3), c_color.b - (b + all3)).to_mode(self.mode) # type: ignore
    
    def mult(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        return Color(c_color.r * r * all3, c_color.g * g * all3, c_color.b * b * all3).to_mode(self.mode) # type: ignore
    
    def pow(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        return Color(c_color.r ** (r + all3), c_color.g ** (g + all3), c_color.b ** (b + all3)).to_mode(self.mode) # type: ignore
    
    def mod(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        return Color(c_color.r % (r + all3), c_color.g % (g + all3), c_color.b % (b + all3)).to_mode(self.mode) # type: ignore
    
    def div(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        return Color(c_color.r / r / all3, c_color.g / g / all3, c_color.b / b / all3).to_mode(self.mode) # type: ignore
    
    def fdiv(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        return Color(c_color.r // r // all3, c_color.g // g // all3, c_color.b // b // all3).to_mode(self.mode) # type: ignore

    # fast inplace operations     Vector2D.ioperation(both,x,y)
    def set(self, both=.0, x=.0, y=.0) -> "Color":
        self.x = x + both
        self.y = y + both
        return self

    def iadd(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        c_color = self.to_rgb()
        c_color.r += r + all3 # type: ignore
        c_color.g += g + all3 # type: ignore
        c_color.b += b + all3 # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def isub(self, all3=.0, r=.0, g=.0, b=.0) -> "Color":
        c_color = self.to_rgb()
        c_color.r -= r + all3 # type: ignore
        c_color.g -= g + all3 # type: ignore
        c_color.b -= b + all3 # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def imult(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        c_color.r *= r * all3 # type: ignore
        c_color.g *= g * all3 # type: ignore
        c_color.b *= b * all3 # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def ipow(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        c_color.r **= r + all3 # type: ignore
        c_color.g **= g + all3 # type: ignore
        c_color.b **= b + all3 # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def imod(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        c_color.r %= r + all3 # type: ignore
        c_color.g %= g + all3 # type: ignore
        c_color.b %= b + all3 # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def idiv(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        c_color.r /= r * all3 # type: ignore
        c_color.g /= g * all3 # type: ignore
        c_color.b /= b * all3 # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def ifdiv(self, all3=1.0, r=1.0, g=1.0, b=1.0) -> "Color":
        c_color = self.to_rgb()
        c_color.r //= r * all3 # type: ignore
        c_color.g //= g * all3 # type: ignore
        c_color.b //= b * all3 # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self

    # normal operations     Vector2D + a
    def __add__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(c_color.r + other.r, c_color.g + other.g, c_color.b + other.b).to_mode(self.mode) # type: ignore
    
    def __sub__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(c_color.r - other.r, c_color.g - other.g, c_color.b - other.b).to_mode(self.mode) # type: ignore
    
    def __mul__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(c_color.r * other.r, c_color.g * other.g, c_color.b * other.b).to_mode(self.mode) # type: ignore

    def __mod__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(c_color.r % other.r, c_color.g % other.g, c_color.b % other.b).to_mode(self.mode) # type: ignore
    
    def __pow__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(c_color.r ** other.r, c_color.g ** other.g, c_color.b ** other.b).to_mode(self.mode) # type: ignore

    def __truediv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(c_color.r / other.r, c_color.g / other.g, c_color.b / other.b).to_mode(self.mode) # type: ignore

    def __floordiv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(c_color.r // other.r, c_color.g // other.g, c_color.b // other.b).to_mode(self.mode) # type: ignore
    
    # right operations      a + Vector2D
    def __radd__(self, other) -> "Color":
        return self.__add__(other)
    
    def __rsub__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(other.r - c_color.r, other.g - c_color.g, other.b - c_color.b).to_mode(self.mode) # type: ignore
    
    def __rmul__(self, other) -> "Color":
        return self.__mul__(other)

    def __rmod__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(other.r % c_color.r, other.g % c_color.g, other.b % c_color.b).to_mode(self.mode) # type: ignore
    
    def __rpow__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(other.r ** c_color.r, other.g ** c_color.g, other.b ** c_color.b).to_mode(self.mode) # type: ignore

    def __rtruediv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(other.r / c_color.r, other.g / c_color.g, other.b / c_color.b).to_mode(self.mode) # type: ignore

    def __rfloordiv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        return Color(other.r // c_color.r, other.g // c_color.g, other.b // c_color.b).to_mode(self.mode) # type: ignore
    
    # in-place operations   Vector2D += a
    def __iadd__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        c_color.r += other.r # type: ignore
        c_color.g += other.g # type: ignore
        c_color.b += other.b # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self

    def __isub__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        c_color.r -= other.r # type: ignore
        c_color.g -= other.g # type: ignore
        c_color.b -= other.b # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def __imul__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        c_color.r *= other.r # type: ignore
        c_color.g *= other.g # type: ignore
        c_color.b *= other.b # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self

    def __itruediv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        c_color.r **= other.r # type: ignore
        c_color.g **= other.g # type: ignore
        c_color.b **= other.b # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def __imod__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        c_color.r %= other.r # type: ignore
        c_color.g %= other.g # type: ignore
        c_color.b %= other.b # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self
    
    def __ipow__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        c_color.r /= other.r # type: ignore
        c_color.g /= other.g # type: ignore
        c_color.b /= other.b # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self

    def __ifloordiv__(self, other) -> "Color":
        other = Color.__normalize__(other)
        c_color = self.to_rgb()
        c_color.r //= other.r # type: ignore
        c_color.g //= other.g # type: ignore
        c_color.b //= other.b # type: ignore
        self.__dict__ = c_color.to_mode(self.mode).__dict__
        return self

    # comparasion
    def __eq__(self, other) -> bool:
        try: other = Color.__normalize__(other)
        except: return False
        c_color = self.to_rgb()
        return c_color.r == other.r and c_color.g == other.g and c_color.b == other.b # type: ignore

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __abs__(self) -> "Color":
        c_color = self.to_rgb()
        return Color(abs(c_color.r), abs(c_color.g), abs(c_color.b)).to_mode(self.mode) # type: ignore

    def __round__(self, n=1) -> "Color":
        n = Color.__normalize__(n)
        c_color = self.to_rgb()
        return Color(round(c_color.r / n.r) * n.r, round(c_color.g / n.g) * n.g, round(c_color.b / n.b) * n.b).to_mode(self.mode) # type: ignore

    def __floor__(self, n=1) -> "Color":
        n = Color.__normalize__(n)
        c_color = self.to_rgb()
        return Color((c_color.r / n.r).__floor__() * n.r, (c_color.g / n.g).__floor__() * n.g, (c_color.b / n.b).__floor__() * n.b).to_mode(self.mode) # type: ignore

    def __ceil__(self, n=1) -> "Color":
        n = Color.__normalize__(n)
        c_color = self.to_rgb()
        return Color((c_color.r / n.r).__ceil__() * n.r, (c_color.g / n.g).__ceil__() * n.g, (c_color.b / n.b).__ceil__() * n.b).to_mode(self.mode) # type: ignore
    
    def __float__(self) -> "Color":
        c_color = self.to_rgb()
        return Color(float(c_color.r), float(c_color.g), float(c_color.b)).to_mode(self.mode) # type: ignore

    def __getitem__(self, n) -> int|float:
        return self.values[n] if isinstance(n, int) else self.values[self.keys.index(n)]
    
    def __iter__(self) -> Generator[float, Any, None]:
        for val in self.values:
            yield val
    
    @classmethod
    def __normalize__(cls, other) -> "Color":
        if isinstance(other, Color):
            return other
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

    @classmethod
    def randomize(cls) -> "Color":
        return Color(__randint__(0,255), __randint__(0,255), __randint__(0,255))

WHITE_COLOR_PYG = Color.white()()
BLACK_COLOR_PYG = Color.black()()
RED_COLOR_PYG = Color.red()()
GREEN_COLOR_PYG = Color.green()()
BLUE_COLOR_PYG = Color.blue()()
