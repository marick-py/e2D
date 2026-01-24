# cython: language_level=3

"""
Cython header file for Vector2D class
Allows other Cython modules to use this without Python overhead
"""

cimport numpy as cnp

ctypedef cnp.float64_t DTYPE_t

cdef class Vector2D:
    cdef public cnp.ndarray data
    cdef DTYPE_t* _data_ptr
    
    # Fast inline methods (no Python overhead)
    cdef inline double _length_squared(self) nogil
    cdef inline double _length(self) nogil
    cdef inline double _dot(self, Vector2D other) nogil
    
    # cpdef methods (callable from Python and Cython)
    cpdef Vector2D copy(self)
    cpdef void set(self, double x, double y)
    cpdef void iadd(self, Vector2D other)
    cpdef void isub(self, Vector2D other)
    cpdef void imul(self, double scalar)
    cpdef void idiv(self, double scalar)
    cpdef void imul_vec(self, Vector2D other)
    cpdef void iadd_scalar(self, double scalar)
    cpdef void isub_scalar(self, double scalar)
    cpdef void normalize(self)
    cpdef void clamp_inplace(self, Vector2D min_val, Vector2D max_val)
    cpdef Vector2D add(self, Vector2D other)
    cpdef Vector2D sub(self, Vector2D other)
    cpdef Vector2D mul(self, double scalar)
    cpdef Vector2D mul_vec(self, Vector2D other)
    cpdef Vector2D normalized(self)
    cpdef double dot_product(self, Vector2D other)
    cpdef double distance_to(self, Vector2D other, bint rooted=*)
    cpdef double angle_to(self, Vector2D other)
    cpdef Vector2D rotate(self, double angle)
    cpdef void irotate(self, double angle)
    cpdef Vector2D lerp(self, Vector2D other, double t)
    cpdef Vector2D clamp(self, Vector2D min_val, Vector2D max_val)
    cpdef Vector2D projection(self, Vector2D other)
    cpdef Vector2D reflection(self, Vector2D normal)
    cpdef list to_list(self)
    cpdef tuple to_tuple(self)

# Batch operation functions
cpdef void batch_add_inplace(list vectors, Vector2D displacement)
cpdef void batch_scale_inplace(list vectors, double scalar)
cpdef void batch_normalize_inplace(list vectors)
cpdef cnp.ndarray vectors_to_array(list vectors)
cpdef list array_to_vectors(cnp.ndarray arr)

