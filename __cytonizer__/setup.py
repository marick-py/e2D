from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("Cmain.pyx"),
)

# python setup.py build_ext --inplace