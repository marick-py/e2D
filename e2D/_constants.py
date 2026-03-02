"""
Mathematical constants used throughout e2D.
"""

import numpy as np

PI: float = float(np.pi)
PI_HALF: float = float(np.pi / 2)
PI_QUARTER: float = float(np.pi / 4)
TAU: float = float(np.pi * 2)

__all__ = ['PI', 'PI_HALF', 'PI_QUARTER', 'TAU']
