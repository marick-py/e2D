"""
Type stubs for cvectors module (Cython-compiled Vector2D)
Provides type hints for all Vector2D operations
"""

from typing import List, Tuple
from .types import Number
import numpy as np
import numpy.typing as npt

class Vector2D:
    """
    High-performance 2D vector class optimized for heavy simulations.
    
    Uses contiguous numpy arrays and Cython for near-C performance.
    All operations are optimized with no bounds checking and inline C math.
    """
    
    data: npt.NDArray[np.float64]
    
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        """Initialize vector with x, y components"""
        ...
    
    # Property accessors
    @property
    def x(self) -> float:
        """X component"""
        ...
    
    @x.setter
    def x(self, value: float) -> None: ...
    
    @property
    def y(self) -> float:
        """Y component"""
        ...
    
    @y.setter
    def y(self, value: float) -> None: ...
    
    @property
    def length(self) -> float:
        """Vector length (magnitude)"""
        ...
    
    @property
    def length_sqrd(self) -> float:
        """Squared length (faster, avoids sqrt)"""
        ...
    
    @property
    def angle(self) -> float:
        """Angle of this vector"""
        ...
    
    @angle.setter
    def angle(self, new_angle: float) -> None:
        """Set angle while maintaining magnitude"""
        ...
    
    # Methods
    def copy(self) -> Vector2D:
        """Fast copy"""
        ...
    
    def set(self, x: float, y: float) -> None:
        """Set both components"""
        ...
    
    def iadd(self, other: Vector2D) -> None:
        """In-place addition"""
        ...
    
    def isub(self, other: Vector2D) -> None:
        """In-place subtraction"""
        ...
    
    def imul(self, scalar: float) -> None:
        """In-place scalar multiplication"""
        ...
    
    def idiv(self, scalar: float) -> None:
        """In-place division"""
        ...
    
    def imul_vec(self, other: Vector2D) -> None:
        """In-place component-wise multiplication"""
        ...
    
    def iadd_scalar(self, scalar: float) -> None:
        """In-place scalar addition"""
        ...
    
    def isub_scalar(self, scalar: float) -> None:
        """In-place scalar subtraction"""
        ...
    
    def normalize(self) -> None:
        """Normalize in-place"""
        ...
    
    def clamp_inplace(self, min_val: Vector2D, max_val: Vector2D) -> None:
        """Clamp components in-place"""
        ...
    
    def add(self, other: Vector2D) -> Vector2D:
        """Addition (returns new vector)"""
        ...
    
    def sub(self, other: Vector2D) -> Vector2D:
        """Subtraction (returns new vector)"""
        ...
    
    def mul(self, scalar: float) -> Vector2D:
        """Scalar multiplication (returns new vector)"""
        ...
    
    def mul_vec(self, other: Vector2D) -> Vector2D:
        """Component-wise multiplication (returns new vector)"""
        ...
    
    def normalized(self) -> Vector2D:
        """Get normalized vector (returns new)"""
        ...
    
    def dot_product(self, other: Vector2D) -> float:
        """Dot product"""
        ...
    
    def distance_to(self, other: Vector2D, rooted: bool = True) -> float:
        """Distance to another vector"""
        ...
    
    def angle_to(self, other: Vector2D) -> float:
        """Angle to another vector"""
        ...
    
    def rotate(self, angle: float) -> Vector2D:
        """Rotate vector by angle (returns new)"""
        ...
    
    def irotate(self, angle: float) -> None:
        """Rotate in-place"""
        ...
    
    def lerp(self, other: Vector2D, t: float) -> Vector2D:
        """Linear interpolation"""
        ...
    
    def clamp(self, min_val: Vector2D, max_val: Vector2D) -> Vector2D:
        """Clamp (returns new)"""
        ...
    
    def projection(self, other: Vector2D) -> Vector2D:
        """Project this vector onto another"""
        ...
    
    def reflection(self, normal: Vector2D) -> Vector2D:
        """Reflect vector across normal"""
        ...
    
    # Python operator overloads
    def __add__(self, other: Vector2D | Number) -> Vector2D: ...
    def __sub__(self, other: Vector2D | Number) -> Vector2D: ...
    def __mul__(self, other: Vector2D | Number) -> Vector2D: ...
    def __truediv__(self, other: Number) -> Vector2D: ...
    def __iadd__(self, other: Vector2D | Number) -> Vector2D: ...
    def __isub__(self, other: Vector2D | Number) -> Vector2D: ...
    def __imul__(self, other: Vector2D | Number) -> Vector2D: ...
    def __itruediv__(self, other: Number) -> Vector2D: ...
    def __neg__(self) -> Vector2D: ...
    def __abs__(self) -> Vector2D: ...
    def __getitem__(self, idx: int) -> float: ...
    def __setitem__(self, idx: int, value: float) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    
    # Utility methods
    def to_list(self) -> List[float]:
        """Convert to Python list"""
        ...
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to Python tuple"""
        ...
    
    # Class methods for common vectors
    @staticmethod
    def zero() -> Vector2D:
        """Create zero vector (0, 0)"""
        ...
    
    @staticmethod
    def one() -> Vector2D:
        """Create one vector (1, 1)"""
        ...
    
    @staticmethod
    def up() -> Vector2D:
        """Create up vector (0, 1)"""
        ...
    
    @staticmethod
    def down() -> Vector2D:
        """Create down vector (0, -1)"""
        ...
    
    @staticmethod
    def left() -> Vector2D:
        """Create left vector (-1, 0)"""
        ...
    
    @staticmethod
    def right() -> Vector2D:
        """Create right vector (1, 0)"""
        ...
    
    @staticmethod
    def random(min_val: float = 0.0, max_val: float = 1.0) -> Vector2D:
        """Create random vector"""
        ...

# Batch operations for processing many vectors at once
def batch_add_inplace(vectors: List[Vector2D], displacement: Vector2D) -> None:
    """Add displacement to all vectors in-place (ultra-fast)"""
    ...

def batch_scale_inplace(vectors: List[Vector2D], scalar: float) -> None:
    """Scale all vectors in-place"""
    ...

def batch_normalize_inplace(vectors: List[Vector2D]) -> None:
    """Normalize all vectors in-place"""
    ...

def vectors_to_array(vectors: List[Vector2D]) -> npt.NDArray[np.float64]:
    """Convert list of vectors to numpy array (fast)"""
    ...

def array_to_vectors(arr: npt.NDArray[np.float64]) -> List[Vector2D]:
    """Convert numpy array to list of vectors (fast)"""
    ...
