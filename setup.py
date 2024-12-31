from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        "e2D.Cmain",
        ["e2D\\Cmain.pyx"],
        # define_macros=[("CYTHON_LIMITED_API", "1")],
        # py_limited_api=True
    )

]

setup(
    ext_modules=cythonize(ext_modules),
)

# python setup.py build_ext --inplace