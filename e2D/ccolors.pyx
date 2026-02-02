# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""
Cython-optimized color operations for e2D
High-performance batch conversions and color space transformations
"""

cimport cython
from libc.math cimport fmin, fmax, fmod, floor
import numpy as np
cimport numpy as cnp

cnp.import_array()


@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline float clamp(float val, float min_val, float max_val) nogil:
    """Clamp value between min and max"""
    return fmin(fmax(val, min_val), max_val)


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_lerp_colors(
    float[:, :] colors1,
    float[:, :] colors2,
    float t
) -> cnp.ndarray:
    """
    Batch linear interpolation between two color arrays
    colors1, colors2: shape (N, 4) RGBA float arrays
    t: interpolation factor (0.0-1.0)
    Returns: shape (N, 4) interpolated colors
    """
    cdef int n = colors1.shape[0]
    cdef int i, j
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            for j in range(4):
                result[i, j] = colors1[i, j] + (colors2[i, j] - colors1[i, j]) * t
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_multiply_colors(float[:, :] colors, float factor) -> cnp.ndarray:
    """
    Multiply RGB channels by factor (preserves alpha)
    colors: shape (N, 4) RGBA float array
    factor: multiplication factor
    Returns: shape (N, 4) multiplied colors
    """
    cdef int n = colors.shape[0]
    cdef int i
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            result[i, 0] = clamp(colors[i, 0] * factor, 0.0, 1.0)
            result[i, 1] = clamp(colors[i, 1] * factor, 0.0, 1.0)
            result[i, 2] = clamp(colors[i, 2] * factor, 0.0, 1.0)
            result[i, 3] = colors[i, 3]
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_add_colors(float[:, :] colors1, float[:, :] colors2) -> cnp.ndarray:
    """
    Add two color arrays (clamped to 1.0)
    colors1, colors2: shape (N, 4) RGBA float arrays
    Returns: shape (N, 4) added colors
    """
    cdef int n = colors1.shape[0]
    cdef int i, j
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            for j in range(4):
                result[i, j] = clamp(colors1[i, j] + colors2[i, j], 0.0, 1.0)
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_grayscale(float[:, :] colors) -> cnp.ndarray:
    """
    Convert colors to grayscale using luminance formula
    colors: shape (N, 4) RGBA float array
    Returns: shape (N, 4) grayscale colors (alpha preserved)
    """
    cdef int n = colors.shape[0]
    cdef int i
    cdef float gray
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            gray = 0.2989 * colors[i, 0] + 0.5870 * colors[i, 1] + 0.1140 * colors[i, 2]
            result[i, 0] = gray
            result[i, 1] = gray
            result[i, 2] = gray
            result[i, 3] = colors[i, 3]
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_invert(float[:, :] colors) -> cnp.ndarray:
    """
    Invert RGB channels (preserves alpha)
    colors: shape (N, 4) RGBA float array
    Returns: shape (N, 4) inverted colors
    """
    cdef int n = colors.shape[0]
    cdef int i
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            result[i, 0] = 1.0 - colors[i, 0]
            result[i, 1] = 1.0 - colors[i, 1]
            result[i, 2] = 1.0 - colors[i, 2]
            result[i, 3] = colors[i, 3]
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline void rgb_to_hsv_fast(float r, float g, float b, float* h, float* s, float* v) nogil:
    """Fast RGB to HSV conversion"""
    cdef float cmax = fmax(r, fmax(g, b))
    cdef float cmin = fmin(r, fmin(g, b))
    cdef float delta = cmax - cmin
    
    v[0] = cmax
    
    if cmax == 0.0:
        s[0] = 0.0
        h[0] = 0.0
        return
    
    s[0] = delta / cmax
    
    if delta == 0.0:
        h[0] = 0.0
        return
    
    if cmax == r:
        h[0] = fmod((g - b) / delta, 6.0)
    elif cmax == g:
        h[0] = (b - r) / delta + 2.0
    else:
        h[0] = (r - g) / delta + 4.0
    
    h[0] /= 6.0
    if h[0] < 0.0:
        h[0] += 1.0


@cython.boundscheck(False)
@cython.wraparound(False)
cdef inline void hsv_to_rgb_fast(float h, float s, float v, float* r, float* g, float* b) nogil:
    """Fast HSV to RGB conversion"""
    if s == 0.0:
        r[0] = v
        g[0] = v
        b[0] = v
        return
    
    cdef float h6 = h * 6.0
    cdef int i = <int>floor(h6)
    cdef float f = h6 - i
    cdef float p = v * (1.0 - s)
    cdef float q = v * (1.0 - s * f)
    cdef float t = v * (1.0 - s * (1.0 - f))
    
    if i == 0:
        r[0] = v
        g[0] = t
        b[0] = p
    elif i == 1:
        r[0] = q
        g[0] = v
        b[0] = p
    elif i == 2:
        r[0] = p
        g[0] = v
        b[0] = t
    elif i == 3:
        r[0] = p
        g[0] = q
        b[0] = v
    elif i == 4:
        r[0] = t
        g[0] = p
        b[0] = v
    else:
        r[0] = v
        g[0] = p
        b[0] = q


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_rgb_to_hsv(float[:, :] colors) -> cnp.ndarray:
    """
    Convert RGB colors to HSV
    colors: shape (N, 4) RGBA float array
    Returns: shape (N, 4) HSVA float array (alpha preserved)
    """
    cdef int n = colors.shape[0]
    cdef int i
    cdef float h, s, v
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            rgb_to_hsv_fast(colors[i, 0], colors[i, 1], colors[i, 2], &h, &s, &v)
            result[i, 0] = h
            result[i, 1] = s
            result[i, 2] = v
            result[i, 3] = colors[i, 3]
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_hsv_to_rgb(float[:, :] colors) -> cnp.ndarray:
    """
    Convert HSV colors to RGB
    colors: shape (N, 4) HSVA float array
    Returns: shape (N, 4) RGBA float array (alpha preserved)
    """
    cdef int n = colors.shape[0]
    cdef int i
    cdef float r, g, b
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            hsv_to_rgb_fast(colors[i, 0], colors[i, 1], colors[i, 2], &r, &g, &b)
            result[i, 0] = r
            result[i, 1] = g
            result[i, 2] = b
            result[i, 3] = colors[i, 3]
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_rotate_hue(float[:, :] colors, float degrees) -> cnp.ndarray:
    """
    Rotate hue of RGB colors by degrees
    colors: shape (N, 4) RGBA float array
    degrees: rotation amount (0-360)
    Returns: shape (N, 4) rotated colors
    """
    cdef int n = colors.shape[0]
    cdef int i
    cdef float h, s, v, r, g, b
    cdef float rotation = degrees / 360.0
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            rgb_to_hsv_fast(colors[i, 0], colors[i, 1], colors[i, 2], &h, &s, &v)
            h = fmod(h + rotation, 1.0)
            if h < 0.0:
                h += 1.0
            hsv_to_rgb_fast(h, s, v, &r, &g, &b)
            result[i, 0] = r
            result[i, 1] = g
            result[i, 2] = b
            result[i, 3] = colors[i, 3]
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
def batch_saturate(float[:, :] colors, float amount) -> cnp.ndarray:
    """
    Adjust saturation of RGB colors
    colors: shape (N, 4) RGBA float array
    amount: saturation change (-1.0 to 1.0)
    Returns: shape (N, 4) adjusted colors
    """
    cdef int n = colors.shape[0]
    cdef int i
    cdef float h, s, v, r, g, b
    cdef float[:, :] result = np.empty((n, 4), dtype=np.float32)
    
    with nogil:
        for i in range(n):
            rgb_to_hsv_fast(colors[i, 0], colors[i, 1], colors[i, 2], &h, &s, &v)
            s = clamp(s + amount, 0.0, 1.0)
            hsv_to_rgb_fast(h, s, v, &r, &g, &b)
            result[i, 0] = r
            result[i, 1] = g
            result[i, 2] = b
            result[i, 3] = colors[i, 3]
    
    return np.asarray(result)


@cython.boundscheck(False)
@cython.wraparound(False)
def generate_gradient(float[:, :] colors, int steps) -> cnp.ndarray:
    """
    Generate smooth gradient between multiple colors
    colors: shape (N, 4) RGBA float array (control points)
    steps: total number of gradient steps
    Returns: shape (steps, 4) gradient colors
    """
    cdef int n_colors = colors.shape[0]
    cdef int segments = n_colors - 1
    cdef int steps_per_segment = steps // segments
    cdef int i, j, k
    cdef float t
    cdef float[:, :] result = np.empty((steps, 4), dtype=np.float32)
    cdef int idx = 0
    
    with nogil:
        for i in range(segments):
            for j in range(steps_per_segment):
                t = <float>j / <float>steps_per_segment
                for k in range(4):
                    result[idx, k] = colors[i, k] + (colors[i + 1, k] - colors[i, k]) * t
                idx += 1
        
        # Add final color
        if idx < steps:
            for k in range(4):
                result[idx, k] = colors[n_colors - 1, k]
    
    return np.asarray(result)
