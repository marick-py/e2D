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
from libc.stdlib cimport rand, RAND_MAX

cnp.import_array()

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
        cdef Vector2D result
        
        if isinstance(other, Vector2D):
            return self.add(other)
        elif isinstance(other, (int, float)):
            result = self.copy()
            result.iadd_scalar(other)
            return result
        return NotImplemented
    
    def __sub__(self, other):
        cdef Vector2D result
        
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
        cdef Vector2D result
        
        if isinstance(other, (int, float)):
            if other != 0.0:
                result = self.copy()
                result.idiv(other)
                return result
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
    
    def __neg__(self):
        return self.mul(-1.0)
    
    def __abs__(self):
        cdef Vector2D result = Vector2D.__new__(Vector2D)
        result.data = np.empty(2, dtype=np.float64)
        result._data_ptr = <DTYPE_t*> cnp.PyArray_DATA(result.data)
        result._data_ptr[0] = fabs(self._data_ptr[0])
        result._data_ptr[1] = fabs(self._data_ptr[1])
        return result
    
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

