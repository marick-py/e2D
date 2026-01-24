from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import numpy as np
import sys

# Compiler optimization flags
extra_compile_args = []
extra_link_args = []

if sys.platform == "win32":
    # MSVC compiler flags (Windows)
    extra_compile_args = [
        "/O2",           # Maximum optimization
        "/fp:fast",      # Fast floating-point model
        "/GL",           # Whole program optimization
    ]
    # Check for AVX2 support
    try:
        extra_compile_args.append("/arch:AVX2")
    except:
        pass
    extra_link_args = ["/LTCG"]  # Link-time code generation
else:
    # GCC/Clang flags (Linux/Mac)
    extra_compile_args = [
        "-O3",              # Maximum optimization
        "-ffast-math",      # Fast math operations
        "-march=native",    # Optimize for current CPU
        "-funroll-loops",   # Unroll loops
    ]

# Define extensions
extensions = [
    Extension(
        "e2D.cvectors",
        sources=["e2D/cvectors.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        define_macros=[
            ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
        ],
    )
]

ext_modules = cythonize(
    extensions,
    compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'nonecheck': False,
        'cdivision': True,
        'initializedcheck': False,
        'overflowcheck': False,
        'embedsignature': True,
        'annotation_typing': True,
    },
    annotate=False,
)

# Custom build_ext to handle compilation failures gracefully
class BuildExtWithFallback(build_ext):
    def run(self) -> None:
        try:
            super().run()
        except Exception as e:
            print(f"\n{'='*60}")
            print("WARNING: Cython extension compilation failed!")
            print(f"Error: {e}")
            print("\ne2D will still work but with reduced performance.")
            print("Vector2D will use pure Python fallback.")
            print(f"{'='*60}\n")
    
    def build_extension(self, ext) -> None:
        try:
            super().build_extension(ext)
        except Exception as e:
            print(f"\nFailed to build {ext.name}: {e}")
            print("Continuing with installation...")

# Read README for long description
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "High-performance 2D graphics and math library with ultra-optimized vector operations"

setup(
    # Use setup.cfg for most metadata
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExtWithFallback},
    zip_safe=False,
)
