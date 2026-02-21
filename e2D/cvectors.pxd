# cython: language_level=3

"""
Cython header file for Vector2D and Vector2Int classes
Allows other Cython modules to use these without Python overhead
"""

cimport numpy as cnp

ctypedef cnp.float64_t DTYPE_t
ctypedef cnp.int32_t INT_DTYPE_t

cdef class Vector2Int:
    cdef public cnp.ndarray data
    cdef INT_DTYPE_t* _data_ptr
    
    # Fast inline methods
    cdef inline long long _length_squared(self) nogil
    cdef inline int _dot(self, Vector2Int other) nogil
    
    # cpdef methods
    cpdef Vector2Int copy(self)
    cpdef Vector2Int set(self, int x, int y)
    cpdef Vector2Int iadd(self, Vector2Int other)
    cpdef Vector2Int isub(self, Vector2Int other)
    cpdef Vector2Int imul(self, int scalar)
    cpdef Vector2Int ifloordiv(self, int scalar)
    cpdef Vector2Int imod(self, int scalar)
    cpdef Vector2Int imul_vec(self, Vector2Int other)
    cpdef Vector2Int iadd_scalar(self, int scalar)
    cpdef Vector2Int isub_scalar(self, int scalar)
    cpdef Vector2Int iabs(self)
    cpdef Vector2Int clamp_inplace(self, Vector2Int min_val, Vector2Int max_val)
    cpdef Vector2Int add(self, Vector2Int other)
    cpdef Vector2Int sub(self, Vector2Int other)
    cpdef Vector2Int mul(self, int scalar)
    cpdef Vector2Int floordiv(self, int scalar)
    cpdef Vector2Int mod(self, int scalar)
    cpdef Vector2Int mul_vec(self, Vector2Int other)
    cpdef Vector2Int abs_vec(self)
    cpdef int dot_product(self, Vector2Int other)
    cpdef long long distance_squared(self, Vector2Int other)
    cpdef double distance_to(self, Vector2Int other)
    cpdef int manhattan_distance(self, Vector2Int other)
    cpdef int chebyshev_distance(self, Vector2Int other)
    cpdef Vector2Int clamp(self, Vector2Int min_val, Vector2Int max_val)
    cpdef Vector2D to_float(self)
    cpdef tuple to_tuple(self)
    cpdef list to_list(self)
    cpdef cnp.ndarray to_array(self)

cdef class Vector2D:
    cdef public cnp.ndarray data
    cdef DTYPE_t* _data_ptr
    
    # Fast inline methods (no Python overhead)
    cdef inline double _length_squared(self) nogil
    cdef inline double _length(self) nogil
    cdef inline double _dot(self, Vector2D other) nogil
    
    # cpdef methods (callable from Python and Cython)
    cpdef Vector2D copy(self)
    cpdef Vector2D set(self, double x, double y)
    cpdef Vector2D iadd(self, Vector2D other)
    cpdef Vector2D isub(self, Vector2D other)
    cpdef Vector2D imul(self, double scalar)
    cpdef Vector2D idiv(self, double scalar)
    cpdef Vector2D imul_vec(self, Vector2D other)
    cpdef Vector2D iadd_scalar(self, double scalar)
    cpdef Vector2D isub_scalar(self, double scalar)
    cpdef Vector2D normalize(self)
    cpdef Vector2D clamp_inplace(self, Vector2D min_val, Vector2D max_val)
    cpdef Vector2D add(self, Vector2D other)
    cpdef Vector2D sub(self, Vector2D other)
    cpdef Vector2D mul(self, double scalar)
    cpdef Vector2D mul_vec(self, Vector2D other)
    cpdef Vector2D normalized(self)
    cpdef double dot_product(self, Vector2D other)
    cpdef double distance_to(self, Vector2D other, bint rooted=*)
    cpdef double angle_to(self, Vector2D other)
    cpdef Vector2D rotate(self, double angle)
    cpdef Vector2D irotate(self, double angle)
    cpdef Vector2D lerp(self, Vector2D other, double t)
    cpdef Vector2D clamp(self, Vector2D min_val, Vector2D max_val)
    cpdef Vector2D projection(self, Vector2D other)
    cpdef Vector2D reflection(self, Vector2D normal)
    cpdef list to_list(self)
    cpdef tuple to_tuple(self)
    cpdef Vector2Int to_int(self)
    cpdef cnp.ndarray to_array(self)

# Batch operation functions
cpdef void batch_add_inplace(list vectors, Vector2D displacement)
cpdef void batch_scale_inplace(list vectors, double scalar)
cpdef void batch_normalize_inplace(list vectors)
cpdef cnp.ndarray vectors_to_array(list vectors)
cpdef list array_to_vectors(cnp.ndarray arr)
cpdef void seed_rng(unsigned int seed)

