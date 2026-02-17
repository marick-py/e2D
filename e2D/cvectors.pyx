# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
# cython: cdivision=True
# cython: initializedcheck=False
# cython: overflowcheck=False

"""
Ultra-optimized Vector2D class for heavy simulations
Uses Cython with numpy backend for maximum performance
"""

import numpy as np
cimport numpy as cnp
cimport cython
from libc.math cimport sqrt, sin, cos, atan2, floor, ceil, fabs, fmod, pow as c_pow
from libc.stdlib cimport rand, RAND_MAX, srand

cnp.import_array()

cpdef void seed_rng(unsigned int seed):
    """Seed the C RNG used by Vector2D/Vector2Int random()"""
    srand(seed)

cdef class Vector2D:
    """
    High-performance 2D vector class optimized for heavy simulations.
    
    Uses contiguous numpy arrays and Cython for near-C performance.
    All operations are optimized with no bounds checking and inline C math.
    """
    
    def __cinit__(self, double x=0.0, double y=0.0):
        """Initialize vector with x, y components"""
        self.data = np.array([x, y], dtype=np.float64)
        self._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(self.data)
    
    # Property accessors with direct memory access
    @property
    def x(self):
        return self._data_ptr[0]
    
    @x.setter
    def x(self, double value):
        self._data_ptr[0] = value
    
    @property
    def y(self):
        return self._data_ptr[1]
    
    @y.setter
    def y(self, double value):
        self._data_ptr[1] = value
    
    # Fast inline operations
    @cython.cdivision(True)
    cdef inline double _length_squared(self) nogil:
        """Calculate squared length (no sqrt, faster)"""
        return self._data_ptr[0] * self._data_ptr[0] + self._data_ptr[1] * self._data_ptr[1]
    
    @cython.cdivision(True)
    cdef inline double _length(self) nogil:
        """Calculate length"""
        return sqrt(self._data_ptr[0] * self._data_ptr[0] + self._data_ptr[1] * self._data_ptr[1])
    
    @property
    def length(self):
        """Vector length (magnitude)"""
        return self._length()
    
    @property
    def length_sqrd(self):
        """Squared length (faster, avoids sqrt)"""
        return self._length_squared()
    
    cpdef Vector2D copy(self):
        """Fast copy"""
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = self.data.copy()
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        return result
    
    # In-place operations (fastest)
    cpdef void set(self, double x, double y):
        """Set both components"""
        self._data_ptr[0] = x
        self._data_ptr[1] = y
    
    cpdef void iadd(self, Vector2D other):
        """In-place addition"""
        self._data_ptr[0] += other._data_ptr[0]
        self._data_ptr[1] += other._data_ptr[1]
    
    cpdef void isub(self, Vector2D other):
        """In-place subtraction"""
        self._data_ptr[0] -= other._data_ptr[0]
        self._data_ptr[1] -= other._data_ptr[1]
    
    cpdef void imul(self, double scalar):
        """In-place scalar multiplication"""
        self._data_ptr[0] *= scalar
        self._data_ptr[1] *= scalar
    
    cpdef void idiv(self, double scalar):
        """In-place division"""
        cdef double inv = 1.0 / scalar
        self._data_ptr[0] *= inv
        self._data_ptr[1] *= inv
    
    cpdef void imul_vec(self, Vector2D other):
        """In-place component-wise multiplication"""
        self._data_ptr[0] *= other._data_ptr[0]
        self._data_ptr[1] *= other._data_ptr[1]
    
    cpdef void iadd_scalar(self, double scalar):
        """In-place scalar addition"""
        self._data_ptr[0] += scalar
        self._data_ptr[1] += scalar
    
    cpdef void isub_scalar(self, double scalar):
        """In-place scalar subtraction"""
        self._data_ptr[0] -= scalar
        self._data_ptr[1] -= scalar
    
    cpdef void normalize(self):
        """Normalize in-place"""
        cdef double length
        cdef double inv_length
        length = self._length()
        if length > 0.0:
            inv_length = 1.0 / length
            self._data_ptr[0] *= inv_length
            self._data_ptr[1] *= inv_length
    
    cpdef void clamp_inplace(self, Vector2D min_val, Vector2D max_val):
        """Clamp components in-place"""
        if self._data_ptr[0] < min_val._data_ptr[0]:
            self._data_ptr[0] = min_val._data_ptr[0]
        elif self._data_ptr[0] > max_val._data_ptr[0]:
            self._data_ptr[0] = max_val._data_ptr[0]
        
        if self._data_ptr[1] < min_val._data_ptr[1]:
            self._data_ptr[1] = min_val._data_ptr[1]
        elif self._data_ptr[1] > max_val._data_ptr[1]:
            self._data_ptr[1] = max_val._data_ptr[1]
    
    # New vector operations (return new instances)
    cpdef Vector2D add(self, Vector2D other):
        """Addition (returns new vector)"""
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] + other._data_ptr[0]
        result._data_ptr[1] = self._data_ptr[1] + other._data_ptr[1]
        return result
    
    cpdef Vector2D sub(self, Vector2D other):
        """Subtraction (returns new vector)"""
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] - other._data_ptr[0]
        result._data_ptr[1] = self._data_ptr[1] - other._data_ptr[1]
        return result
    
    cpdef Vector2D mul(self, double scalar):
        """Scalar multiplication (returns new vector)"""
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] * scalar
        result._data_ptr[1] = self._data_ptr[1] * scalar
        return result
    
    cpdef Vector2D mul_vec(self, Vector2D other):
        """Component-wise multiplication (returns new vector)"""
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] * other._data_ptr[0]
        result._data_ptr[1] = self._data_ptr[1] * other._data_ptr[1]
        return result
    
    cpdef Vector2D normalized(self):
        """Get normalized vector (returns new)"""
        cdef double length
        cdef double inv_length
        cdef Vector2D result
        
        length = self._length()
        result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        
        if length > 0.0:
            inv_length = 1.0 / length
            result._data_ptr[0] = self._data_ptr[0] * inv_length
            result._data_ptr[1] = self._data_ptr[1] * inv_length
        else:
            result._data_ptr[0] = 0.0
            result._data_ptr[1] = 0.0
        return result
    
    @cython.cdivision(True)
    cdef inline double _dot(self, Vector2D other) nogil:
        """Dot product (inline, no GIL)"""
        return self._data_ptr[0] * other._data_ptr[0] + self._data_ptr[1] * other._data_ptr[1]
    
    cpdef double dot_product(self, Vector2D other):
        """Dot product"""
        return self._dot(other)
    
    cpdef double distance_to(self, Vector2D other, bint rooted=True):
        """Distance to another vector"""
        cdef double dx
        cdef double dy
        cdef double dist_sq
        
        dx = self._data_ptr[0] - other._data_ptr[0]
        dy = self._data_ptr[1] - other._data_ptr[1]
        dist_sq = dx * dx + dy * dy
        if rooted:
            return sqrt(dist_sq)
        return dist_sq
    
    cpdef double angle_to(self, Vector2D other):
        """Angle to another vector"""
        cdef double dx
        cdef double dy
        
        dx = other._data_ptr[0] - self._data_ptr[0]
        dy = other._data_ptr[1] - self._data_ptr[1]
        return atan2(dy, dx)
    
    @property
    def angle(self):
        """Angle of this vector"""
        return atan2(self._data_ptr[1], self._data_ptr[0])
    
    @angle.setter
    def angle(self, double new_angle):
        """Set angle while maintaining magnitude"""
        cdef double mag
        
        mag = self._length()
        self._data_ptr[0] = mag * cos(new_angle)
        self._data_ptr[1] = mag * sin(new_angle)
    
    cpdef Vector2D rotate(self, double angle):
        """Rotate vector by angle (returns new)"""
        cdef double cos_a
        cdef double sin_a
        cdef Vector2D result
        
        cos_a = cos(angle)
        sin_a = sin(angle)
        result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] * cos_a - self._data_ptr[1] * sin_a
        result._data_ptr[1] = self._data_ptr[0] * sin_a + self._data_ptr[1] * cos_a
        return result
    
    cpdef void irotate(self, double angle):
        """Rotate in-place"""
        cdef double cos_a
        cdef double sin_a
        cdef double new_x
        cdef double new_y
        cos_a = cos(angle)
        sin_a = sin(angle)
        new_x = self._data_ptr[0] * cos_a - self._data_ptr[1] * sin_a
        new_y = self._data_ptr[0] * sin_a + self._data_ptr[1] * cos_a
        self._data_ptr[0] = new_x
        self._data_ptr[1] = new_y
    
    cpdef Vector2D lerp(self, Vector2D other, double t):
        """Linear interpolation"""
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] + (other._data_ptr[0] - self._data_ptr[0]) * t
        result._data_ptr[1] = self._data_ptr[1] + (other._data_ptr[1] - self._data_ptr[1]) * t
        return result
    
    cpdef Vector2D clamp(self, Vector2D min_val, Vector2D max_val):
        """Clamp (returns new)"""
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        
        result._data_ptr[0] = self._data_ptr[0]
        if result._data_ptr[0] < min_val._data_ptr[0]:
            result._data_ptr[0] = min_val._data_ptr[0]
        elif result._data_ptr[0] > max_val._data_ptr[0]:
            result._data_ptr[0] = max_val._data_ptr[0]
        
        result._data_ptr[1] = self._data_ptr[1]
        if result._data_ptr[1] < min_val._data_ptr[1]:
            result._data_ptr[1] = min_val._data_ptr[1]
        elif result._data_ptr[1] > max_val._data_ptr[1]:
            result._data_ptr[1] = max_val._data_ptr[1]
        
        return result
    
    cpdef Vector2D projection(self, Vector2D other):
        """Project this vector onto another"""
        cdef double dot
        cdef double other_len_sq
        cdef double scalar
        
        dot = self._dot(other)
        other_len_sq = other._length_squared()
        if other_len_sq > 0.0:
            scalar = dot / other_len_sq
            return other.mul(scalar)
        return Vector2D(0.0, 0.0)
    
    cpdef Vector2D reflection(self, Vector2D normal):
        """Reflect vector across normal"""
        cdef double dot
        cdef Vector2D result
        
        dot = self._dot(normal)
        result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] - 2.0 * dot * normal._data_ptr[0]
        result._data_ptr[1] = self._data_ptr[1] - 2.0 * dot * normal._data_ptr[1]
        return result
    
    # Python operator overloads
    def __add__(self, other):
        if isinstance(other, Vector2D):
            return self.add(other)
        elif isinstance(other, (int, float)):
            result = self.copy()
            result.iadd_scalar(other)
            return result
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Vector2D):
            return self.sub(other)
        elif isinstance(other, (int, float)):
            result = self.copy()
            result.isub_scalar(other)
            return result
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return self.mul(other)
        elif isinstance(other, Vector2D):
            return self.mul_vec(other)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other != 0.0:
                result = self.copy()
                result.idiv(other)
                return result
        elif isinstance(other, Vector2D):
            other_vec = <Vector2D>other
            x_val = self._data_ptr[0] / other_vec._data_ptr[0] if other_vec._data_ptr[0] != 0 else 0.0
            y_val = self._data_ptr[1] / other_vec._data_ptr[1] if other_vec._data_ptr[1] != 0 else 0.0
            return Vector2D(x_val, y_val)
        return NotImplemented
    
    def __iadd__(self, other):
        if isinstance(other, Vector2D):
            self.iadd(other)
        elif isinstance(other, (int, float)):
            self.iadd_scalar(other)
        return self
    
    def __isub__(self, other):
        if isinstance(other, Vector2D):
            self.isub(other)
        elif isinstance(other, (int, float)):
            self.isub_scalar(other)
        return self
    
    def __imul__(self, other):
        if isinstance(other, (int, float)):
            self.imul(other)
        elif isinstance(other, Vector2D):
            self.imul_vec(other)
        return self
    
    def __itruediv__(self, other):
        if isinstance(other, (int, float)) and other != 0.0:
            self.idiv(other)
        return self
    
    # Reverse operators (for 2 * vector, etc.)
    def __radd__(self, other):
        return self.__add__(other)
    
    def __rsub__(self, other):
        if isinstance(other, (int, float, np.integer, np.floating)):
            x_val = other - self._data_ptr[0]
            y_val = other - self._data_ptr[1]
            return Vector2D(x_val, y_val)
        return NotImplemented
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __rtruediv__(self, other):
        if isinstance(other, (int, float, np.integer, np.floating)):
            x_val = other / self._data_ptr[0] if self._data_ptr[0] != 0 else 0.0
            y_val = other / self._data_ptr[1] if self._data_ptr[1] != 0 else 0.0
            return Vector2D(x_val, y_val)
        return NotImplemented
    
    def __neg__(self):
        return self.mul(-1.0)
    
    def __abs__(self):
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = fabs(self._data_ptr[0])
        result._data_ptr[1] = fabs(self._data_ptr[1])
        return result
    
    def __call__(self):
        """Return vector as tuple when called: v() -> (x, y)"""
        return (self._data_ptr[0], self._data_ptr[1])
    
    def __getitem__(self, int idx):
        if idx == 0:
            return self._data_ptr[0]
        elif idx == 1:
            return self._data_ptr[1]
        raise IndexError("Index out of range")
    
    def __setitem__(self, int idx, double value):
        if idx == 0:
            self._data_ptr[0] = value
        elif idx == 1:
            self._data_ptr[1] = value
        else:
            raise IndexError("Index out of range")
    
    # Comparison operators
    def __eq__(self, other):
        if isinstance(other, Vector2D):
            return fabs(self._data_ptr[0] - (<Vector2D>other)._data_ptr[0]) < 1e-9 and \
                   fabs(self._data_ptr[1] - (<Vector2D>other)._data_ptr[1]) < 1e-9
        elif isinstance(other, Vector2Int):
            return fabs(self._data_ptr[0] - <double>(<Vector2Int>other)._data_ptr[0]) < 1e-9 and \
                   fabs(self._data_ptr[1] - <double>(<Vector2Int>other)._data_ptr[1]) < 1e-9
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        """Less than (compares length for consistency)"""
        if isinstance(other, Vector2D):
            return self._length_squared() < (<Vector2D>other)._length_squared()
        return NotImplemented
    
    def __le__(self, other):
        """Less than or equal"""
        if isinstance(other, Vector2D):
            return self._length_squared() <= (<Vector2D>other)._length_squared()
        return NotImplemented
    
    def __gt__(self, other):
        """Greater than"""
        if isinstance(other, Vector2D):
            return self._length_squared() > (<Vector2D>other)._length_squared()
        return NotImplemented
    
    def __ge__(self, other):
        """Greater than or equal"""
        if isinstance(other, Vector2D):
            return self._length_squared() >= (<Vector2D>other)._length_squared()
        return NotImplemented
    
    def __len__(self):
        """Always returns 2 (for x, y)"""
        return 2
    
    def __iter__(self):
        """Allow iteration: x, y = vector"""
        yield self._data_ptr[0]
        yield self._data_ptr[1]
    
    def __hash__(self):
        """Allow use in sets and as dict keys (rounded to avoid float issues)"""
        return hash((round(self._data_ptr[0], 9), round(self._data_ptr[1], 9)))
    
    def __bool__(self):
        """False if approximately (0, 0), True otherwise"""
        return fabs(self._data_ptr[0]) > 1e-9 or fabs(self._data_ptr[1]) > 1e-9
    
    def __str__(self):
        return f"Vector2D({self._data_ptr[0]:.6f}, {self._data_ptr[1]:.6f})"
    
    def __repr__(self):
        return f"Vector2D({self._data_ptr[0]}, {self._data_ptr[1]})"
    
    # Utility methods
    cpdef list to_list(self):
        """Convert to Python list"""
        return [self._data_ptr[0], self._data_ptr[1]]
    
    cpdef tuple to_tuple(self):
        """Convert to Python tuple"""
        return (self._data_ptr[0], self._data_ptr[1])
    
    cpdef Vector2Int to_int(self):
        """Convert to Vector2Int (truncates to integer)"""
        return Vector2Int(<int>self._data_ptr[0], <int>self._data_ptr[1])
    
    cpdef cnp.ndarray to_array(self):
        """Convert to numpy array"""
        return self.data
    
    # Class methods for common vectors
    @staticmethod
    def zero():
        return Vector2D(0.0, 0.0)
    
    @staticmethod
    def one():
        return Vector2D(1.0, 1.0)
    
    @staticmethod
    def up():
        return Vector2D(0.0, 1.0)
    
    @staticmethod
    def down():
        return Vector2D(0.0, -1.0)
    
    @staticmethod
    def left():
        return Vector2D(-1.0, 0.0)
    
    @staticmethod
    def right():
        return Vector2D(1.0, 0.0)
    
    @staticmethod
    def random(double min_val=0.0, double max_val=1.0):
        """Create random vector"""
        cdef double range_val
        cdef double rx
        cdef double ry
        
        range_val = max_val - min_val
        rx = (<double>rand() / <double>RAND_MAX) * range_val + min_val
        ry = (<double>rand() / <double>RAND_MAX) * range_val + min_val
        return Vector2D(rx, ry)


# Batch operations for processing many vectors at once
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void batch_add_inplace(list vectors, Vector2D displacement):
    """Add displacement to all vectors in-place (ultra-fast)"""
    cdef Vector2D vec
    cdef Py_ssize_t i
    cdef Py_ssize_t n = len(vectors)
    
    for i in range(n):
        vec = <Vector2D>vectors[i]
        vec._data_ptr[0] += displacement._data_ptr[0]
        vec._data_ptr[1] += displacement._data_ptr[1]


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void batch_scale_inplace(list vectors, double scalar):
    """Scale all vectors in-place"""
    cdef Vector2D vec
    cdef Py_ssize_t i
    cdef Py_ssize_t n = len(vectors)
    
    for i in range(n):
        vec = <Vector2D>vectors[i]
        vec._data_ptr[0] *= scalar
        vec._data_ptr[1] *= scalar


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void batch_normalize_inplace(list vectors):
    """Normalize all vectors in-place"""
    cdef Vector2D vec
    cdef Py_ssize_t i
    cdef Py_ssize_t n
    cdef double length
    cdef double inv_length
    
    n = len(vectors)
    
    for i in range(n):
        vec = <Vector2D>vectors[i]
        length = sqrt(vec._data_ptr[0] * vec._data_ptr[0] + vec._data_ptr[1] * vec._data_ptr[1])
        if length > 0.0:
            inv_length = 1.0 / length
            vec._data_ptr[0] *= inv_length
            vec._data_ptr[1] *= inv_length


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef cnp.ndarray[DTYPE_t, ndim=2] vectors_to_array(list vectors):
    """Convert list of vectors to numpy array (fast)"""
    cdef Py_ssize_t n
    cdef cnp.ndarray[DTYPE_t, ndim=2] result
    cdef Vector2D vec
    cdef Py_ssize_t i
    
    n = len(vectors)
    result = np.empty((n, 2), dtype=np.float64)
    
    for i in range(n):
        vec = <Vector2D>vectors[i]
        result[i, 0] = vec._data_ptr[0]
        result[i, 1] = vec._data_ptr[1]
    
    return result


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef list array_to_vectors(cnp.ndarray[DTYPE_t, ndim=2] arr):
    """Convert numpy array to list of vectors (fast)"""
    cdef Py_ssize_t n
    cdef list result
    cdef Vector2D vec
    cdef Py_ssize_t i
    
    n = arr.shape[0]
    result = []
    
    for i in range(n):
        vec = Vector2D(arr[i, 0], arr[i, 1])
        result.append(vec)
    
    return result


# ============================================================================
# Vector2Int - Integer Vector for Grid Systems and Precise Calculations
# ============================================================================

cdef class Vector2Int:
    """
    High-performance 2D integer vector class for grid systems and precise calculations.
    
    Perfect for:
    - Grid coordinates (tilemaps, cells)
    - Array indexing (no float precision errors)
    - Discrete math operations
    - Pathfinding (A*, BFS, DFS)
    
    Uses Cython with numpy int32 backend for maximum performance and precision.
    """
    
    def __cinit__(self, int x=0, int y=0):
        """Initialize vector with x, y integer components"""
        self.data = np.array([x, y], dtype=np.int32)
        self._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(self.data)
    
    # Property accessors with direct memory access
    @property
    def x(self):
        return self._data_ptr[0]
    
    @x.setter
    def x(self, int value):
        self._data_ptr[0] = value
    
    @property
    def y(self):
        return self._data_ptr[1]
    
    @y.setter
    def y(self, int value):
        self._data_ptr[1] = value
    
    # Fast inline operations
    @cython.cdivision(True)
    cdef inline long long _length_squared(self) nogil:
        """Calculate squared length (no sqrt, faster)"""
        return <long long>self._data_ptr[0] * <long long>self._data_ptr[0] + <long long>self._data_ptr[1] * <long long>self._data_ptr[1]
    
    @property
    def length_sqrd(self):
        """Squared length (faster, avoids sqrt)"""
        return self._length_squared()
    
    @property
    def length(self):
        """Vector length (magnitude) - returns float"""
        return sqrt(<double>self._length_squared())
    
    cpdef Vector2Int copy(self):
        """Fast copy"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = self.data.copy()
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        return result
    
    # In-place operations (fastest)
    cpdef void set(self, int x, int y):
        """Set both components"""
        self._data_ptr[0] = x
        self._data_ptr[1] = y
    
    cpdef void iadd(self, Vector2Int other):
        """In-place addition"""
        self._data_ptr[0] += other._data_ptr[0]
        self._data_ptr[1] += other._data_ptr[1]
    
    cpdef void isub(self, Vector2Int other):
        """In-place subtraction"""
        self._data_ptr[0] -= other._data_ptr[0]
        self._data_ptr[1] -= other._data_ptr[1]
    
    cpdef void imul(self, int scalar):
        """In-place scalar multiplication"""
        self._data_ptr[0] *= scalar
        self._data_ptr[1] *= scalar
    
    cpdef void ifloordiv(self, int scalar):
        """In-place integer floor division"""
        if scalar != 0:
            self._data_ptr[0] //= scalar
            self._data_ptr[1] //= scalar
    
    cpdef void imod(self, int scalar):
        """In-place modulo operation"""
        if scalar != 0:
            self._data_ptr[0] %= scalar
            self._data_ptr[1] %= scalar
    
    cpdef void imul_vec(self, Vector2Int other):
        """In-place component-wise multiplication"""
        self._data_ptr[0] *= other._data_ptr[0]
        self._data_ptr[1] *= other._data_ptr[1]
    
    cpdef void iadd_scalar(self, int scalar):
        """In-place scalar addition"""
        self._data_ptr[0] += scalar
        self._data_ptr[1] += scalar
    
    cpdef void isub_scalar(self, int scalar):
        """In-place scalar subtraction"""
        self._data_ptr[0] -= scalar
        self._data_ptr[1] -= scalar
    
    cpdef void iabs(self):
        """Take absolute value in-place"""
        if self._data_ptr[0] < 0:
            self._data_ptr[0] = -self._data_ptr[0]
        if self._data_ptr[1] < 0:
            self._data_ptr[1] = -self._data_ptr[1]
    
    cpdef void clamp_inplace(self, Vector2Int min_val, Vector2Int max_val):
        """Clamp components in-place"""
        if self._data_ptr[0] < min_val._data_ptr[0]:
            self._data_ptr[0] = min_val._data_ptr[0]
        elif self._data_ptr[0] > max_val._data_ptr[0]:
            self._data_ptr[0] = max_val._data_ptr[0]
        
        if self._data_ptr[1] < min_val._data_ptr[1]:
            self._data_ptr[1] = min_val._data_ptr[1]
        elif self._data_ptr[1] > max_val._data_ptr[1]:
            self._data_ptr[1] = max_val._data_ptr[1]
    
    # New vector operations (return new instances)
    cpdef Vector2Int add(self, Vector2Int other):
        """Addition (returns new vector)"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = np.empty(2, dtype=np.int32)
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] + other._data_ptr[0]
        result._data_ptr[1] = self._data_ptr[1] + other._data_ptr[1]
        return result
    
    cpdef Vector2Int sub(self, Vector2Int other):
        """Subtraction (returns new vector)"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = np.empty(2, dtype=np.int32)
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] - other._data_ptr[0]
        result._data_ptr[1] = self._data_ptr[1] - other._data_ptr[1]
        return result
    
    cpdef Vector2Int mul(self, int scalar):
        """Scalar multiplication (returns new vector)"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = np.empty(2, dtype=np.int32)
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] * scalar
        result._data_ptr[1] = self._data_ptr[1] * scalar
        return result
    
    cpdef Vector2Int floordiv(self, int scalar):
        """Floor division (returns new vector)"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = np.empty(2, dtype=np.int32)
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        if scalar != 0:
            result._data_ptr[0] = self._data_ptr[0] // scalar
            result._data_ptr[1] = self._data_ptr[1] // scalar
        else:
            result._data_ptr[0] = 0
            result._data_ptr[1] = 0
        return result
    
    cpdef Vector2Int mod(self, int scalar):
        """Modulo operation (returns new vector)"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = np.empty(2, dtype=np.int32)
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        if scalar != 0:
            result._data_ptr[0] = self._data_ptr[0] % scalar
            result._data_ptr[1] = self._data_ptr[1] % scalar
        else:
            result._data_ptr[0] = 0
            result._data_ptr[1] = 0
        return result
    
    cpdef Vector2Int mul_vec(self, Vector2Int other):
        """Component-wise multiplication (returns new vector)"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = np.empty(2, dtype=np.int32)
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] * other._data_ptr[0]
        result._data_ptr[1] = self._data_ptr[1] * other._data_ptr[1]
        return result
    
    cpdef Vector2Int abs_vec(self):
        """Absolute value (returns new vector)"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = np.empty(2, dtype=np.int32)
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = self._data_ptr[0] if self._data_ptr[0] >= 0 else -self._data_ptr[0]
        result._data_ptr[1] = self._data_ptr[1] if self._data_ptr[1] >= 0 else -self._data_ptr[1]
        return result
    
    @cython.cdivision(True)
    cdef inline int _dot(self, Vector2Int other) nogil:
        """Dot product (inline, no GIL)"""
        return self._data_ptr[0] * other._data_ptr[0] + self._data_ptr[1] * other._data_ptr[1]
    
    cpdef int dot_product(self, Vector2Int other):
        """Dot product"""
        return self._dot(other)
    
    cpdef long long distance_squared(self, Vector2Int other):
        """Squared distance to another vector (avoids sqrt)"""
        cdef int dx
        cdef int dy
        
        dx = self._data_ptr[0] - other._data_ptr[0]
        dy = self._data_ptr[1] - other._data_ptr[1]
        return <long long>dx * <long long>dx + <long long>dy * <long long>dy
    
    cpdef double distance_to(self, Vector2Int other):
        """Distance to another vector (float result)"""
        return sqrt(<double>self.distance_squared(other))
    
    cpdef int manhattan_distance(self, Vector2Int other):
        """Manhattan distance (grid distance)"""
        cdef int dx
        cdef int dy
        
        dx = self._data_ptr[0] - other._data_ptr[0]
        dy = self._data_ptr[1] - other._data_ptr[1]
        
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)
    
    cpdef int chebyshev_distance(self, Vector2Int other):
        """Chebyshev distance (max of abs differences)"""
        cdef int dx
        cdef int dy
        cdef int abs_dx
        cdef int abs_dy
        
        dx = self._data_ptr[0] - other._data_ptr[0]
        dy = self._data_ptr[1] - other._data_ptr[1]
        
        abs_dx = dx if dx >= 0 else -dx
        abs_dy = dy if dy >= 0 else -dy
        
        return abs_dx if abs_dx > abs_dy else abs_dy
    
    cpdef Vector2Int clamp(self, Vector2Int min_val, Vector2Int max_val):
        """Clamp (returns new)"""
        cdef Vector2Int result = Vector2Int.__new__(Vector2Int)
        result.data = np.empty(2, dtype=np.int32)
        result._data_ptr = <INT_DTYPE_t*> cnp.PyArray_DATA(result.data)
        
        result._data_ptr[0] = self._data_ptr[0]
        if result._data_ptr[0] < min_val._data_ptr[0]:
            result._data_ptr[0] = min_val._data_ptr[0]
        elif result._data_ptr[0] > max_val._data_ptr[0]:
            result._data_ptr[0] = max_val._data_ptr[0]
        
        result._data_ptr[1] = self._data_ptr[1]
        if result._data_ptr[1] < min_val._data_ptr[1]:
            result._data_ptr[1] = min_val._data_ptr[1]
        elif result._data_ptr[1] > max_val._data_ptr[1]:
            result._data_ptr[1] = max_val._data_ptr[1]
        
        return result
    
    # Conversion methods
    cpdef Vector2D to_float(self):
        """Convert to Vector2D (float)"""
        return Vector2D(<double>self._data_ptr[0], <double>self._data_ptr[1])
    
    cpdef tuple to_tuple(self):
        """Convert to Python tuple"""
        return (self._data_ptr[0], self._data_ptr[1])
    
    cpdef list to_list(self):
        """Convert to Python list"""
        return [self._data_ptr[0], self._data_ptr[1]]
    
    cpdef cnp.ndarray to_array(self):
        """Convert to numpy array"""
        return self.data
    
    # Python operator overloads
    def __add__(self, other):
        if isinstance(other, Vector2Int):
            return self.add(other)
        elif isinstance(other, (int, np.integer)):
            result = self.copy()
            result.iadd_scalar(other)
            return result
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Vector2Int):
            return self.sub(other)
        elif isinstance(other, (int, np.integer)):
            result = self.copy()
            result.isub_scalar(other)
            return result
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, (int, np.integer)):
            return self.mul(other)
        elif isinstance(other, Vector2Int):
            return self.mul_vec(other)
        return NotImplemented
    
    def __floordiv__(self, other):
        if isinstance(other, (int, np.integer)):
            return self.floordiv(other)
        elif isinstance(other, Vector2Int):
            other_vec = <Vector2Int>other
            x_val = self._data_ptr[0] // other_vec._data_ptr[0] if other_vec._data_ptr[0] != 0 else 0
            y_val = self._data_ptr[1] // other_vec._data_ptr[1] if other_vec._data_ptr[1] != 0 else 0
            return Vector2Int(x_val, y_val)
        return NotImplemented
    
    def __mod__(self, other):
        if isinstance(other, (int, np.integer)):
            return self.mod(other)
        elif isinstance(other, Vector2Int):
            other_vec = <Vector2Int>other
            x_val = self._data_ptr[0] % other_vec._data_ptr[0] if other_vec._data_ptr[0] != 0 else 0
            y_val = self._data_ptr[1] % other_vec._data_ptr[1] if other_vec._data_ptr[1] != 0 else 0
            return Vector2Int(x_val, y_val)
        return NotImplemented
    
    def __iadd__(self, other):
        if isinstance(other, Vector2Int):
            self.iadd(other)
        elif isinstance(other, (int, np.integer)):
            self.iadd_scalar(other)
        return self
    
    def __isub__(self, other):
        if isinstance(other, Vector2Int):
            self.isub(other)
        elif isinstance(other, (int, np.integer)):
            self.isub_scalar(other)
        return self
    
    def __imul__(self, other):
        if isinstance(other, (int, np.integer)):
            self.imul(other)
        elif isinstance(other, Vector2Int):
            self.imul_vec(other)
        return self
    
    def __ifloordiv__(self, other):
        if isinstance(other, (int, np.integer)) and other != 0:
            self.ifloordiv(other)
        return self
    
    def __imod__(self, other):
        if isinstance(other, (int, np.integer)) and other != 0:
            self.imod(other)
        return self
    
    # Reverse operators
    def __radd__(self, other):
        return self.__add__(other)
    
    def __rsub__(self, other):
        if isinstance(other, (int, np.integer)):
            x_val = other - self._data_ptr[0]
            y_val = other - self._data_ptr[1]
            return Vector2Int(x_val, y_val)
        return NotImplemented
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __rfloordiv__(self, other):
        if isinstance(other, (int, np.integer)):
            x_val = other // self._data_ptr[0] if self._data_ptr[0] != 0 else 0
            y_val = other // self._data_ptr[1] if self._data_ptr[1] != 0 else 0
            return Vector2Int(x_val, y_val)
        return NotImplemented
    
    def __neg__(self):
        return self.mul(-1)
    
    def __abs__(self):
        return self.abs_vec()
    
    def __pos__(self):
        return self.copy()
    
    # Comparison operators
    def __eq__(self, other):
        if isinstance(other, Vector2Int):
            return self._data_ptr[0] == (<Vector2Int>other)._data_ptr[0] and \
                   self._data_ptr[1] == (<Vector2Int>other)._data_ptr[1]
        elif isinstance(other, Vector2D):
            return <double>self._data_ptr[0] == (<Vector2D>other)._data_ptr[0] and \
                   <double>self._data_ptr[1] == (<Vector2D>other)._data_ptr[1]
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        """Less than (compares length squared for speed)"""
        if isinstance(other, Vector2Int):
            return self._length_squared() < (<Vector2Int>other)._length_squared()
        return NotImplemented
    
    def __le__(self, other):
        """Less than or equal"""
        if isinstance(other, Vector2Int):
            return self._length_squared() <= (<Vector2Int>other)._length_squared()
        return NotImplemented
    
    def __gt__(self, other):
        """Greater than"""
        if isinstance(other, Vector2Int):
            return self._length_squared() > (<Vector2Int>other)._length_squared()
        return NotImplemented
    
    def __ge__(self, other):
        """Greater than or equal"""
        if isinstance(other, Vector2Int):
            return self._length_squared() >= (<Vector2Int>other)._length_squared()
        return NotImplemented
    
    def __call__(self):
        """Return vector as tuple when called: v() -> (x, y)"""
        return (self._data_ptr[0], self._data_ptr[1])
    
    def __getitem__(self, int idx):
        if idx == 0:
            return self._data_ptr[0]
        elif idx == 1:
            return self._data_ptr[1]
        raise IndexError("Index out of range")
    
    def __setitem__(self, int idx, int value):
        if idx == 0:
            self._data_ptr[0] = value
        elif idx == 1:
            self._data_ptr[1] = value
        else:
            raise IndexError("Index out of range")
    
    def __len__(self):
        """Always returns 2 (for x, y)"""
        return 2
    
    def __iter__(self):
        """Allow iteration: x, y = vector"""
        yield self._data_ptr[0]
        yield self._data_ptr[1]
    
    def __hash__(self):
        """Allow use in sets and as dict keys"""
        return hash((self._data_ptr[0], self._data_ptr[1]))
    
    def __bool__(self):
        """False if (0, 0), True otherwise"""
        return self._data_ptr[0] != 0 or self._data_ptr[1] != 0
    
    def __str__(self):
        return f"Vector2Int({self._data_ptr[0]}, {self._data_ptr[1]})"
    
    def __repr__(self):
        return f"Vector2Int({self._data_ptr[0]}, {self._data_ptr[1]})"
    
    # Class methods for common vectors
    @staticmethod
    def zero():
        return Vector2Int(0, 0)
    
    @staticmethod
    def one():
        return Vector2Int(1, 1)
    
    @staticmethod
    def up():
        return Vector2Int(0, 1)
    
    @staticmethod
    def down():
        return Vector2Int(0, -1)
    
    @staticmethod
    def left():
        return Vector2Int(-1, 0)
    
    @staticmethod
    def right():
        return Vector2Int(1, 0)
    
    @staticmethod
    def random(int min_val=0, int max_val=1):
        """Create random integer vector"""
        cdef int range_val
        cdef int rx
        cdef int ry
        
        range_val = max_val - min_val + 1
        rx = (rand() % range_val) + min_val
        ry = (rand() % range_val) + min_val
        return Vector2Int(rx, ry)

