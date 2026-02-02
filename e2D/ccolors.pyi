"""Type stubs for Cython color operations"""

import numpy as np
from numpy.typing import NDArray

def batch_lerp_colors(
    colors1: NDArray[np.float32],
    colors2: NDArray[np.float32],
    t: float
) -> NDArray[np.float32]: ...

def batch_multiply_colors(
    colors: NDArray[np.float32],
    factor: float
) -> NDArray[np.float32]: ...

def batch_add_colors(
    colors1: NDArray[np.float32],
    colors2: NDArray[np.float32]
) -> NDArray[np.float32]: ...

def batch_grayscale(
    colors: NDArray[np.float32]
) -> NDArray[np.float32]: ...

def batch_invert(
    colors: NDArray[np.float32]
) -> NDArray[np.float32]: ...

def batch_rgb_to_hsv(
    colors: NDArray[np.float32]
) -> NDArray[np.float32]: ...

def batch_hsv_to_rgb(
    colors: NDArray[np.float32]
) -> NDArray[np.float32]: ...

def batch_rotate_hue(
    colors: NDArray[np.float32],
    degrees: float
) -> NDArray[np.float32]: ...

def batch_saturate(
    colors: NDArray[np.float32],
    amount: float
) -> NDArray[np.float32]: ...

def generate_gradient(
    colors: NDArray[np.float32],
    steps: int
) -> NDArray[np.float32]: ...
