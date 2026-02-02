# e2D Project Structure

This document explains the organization and purpose of files in the e2D project.

## Directory Structure

```
e2D_2.0/
├── e2D/                    # Main package source code
│   ├── __init__.py         # Package initialization
│   ├── *.pyx               # Cython extension sources (cvectors, ccolors)
│   ├── *.pyi               # Type stubs for IDE support
│   ├── *.py                # Pure Python modules
│   └── shaders/            # GLSL shader files
│       ├── *.glsl          # Vertex, fragment, compute shaders
│
├── docs/                   # Feature documentation
│   ├── ENGINE.md           # RootEnv, DefEnv, main loop
│   ├── VECTORS.md          # Vector2D operations
│   ├── COLORS.md           # Color system
│   ├── SHAPES.md           # Shape rendering
│   ├── TEXT.md             # Text rendering
│   ├── PLOTS.md            # GPU plotting
│   ├── RECORDING.md        # Screen recording
│   └── PROJECT_STRUCTURE.md # This file
│
├── README.md               # Main project documentation
├── QUICKSTART.md           # Quick start guide
├── DEVELOPER_GUIDE.md      # Development workflow
├── BUILD_CHECKLIST.md      # Pre-release checklist
├── LICENSE                 # MIT license
│
├── pyproject.toml          # Modern Python build config (PEP 517/518)
├── setup.cfg               # Setup configuration
├── setup.py                # Build script (Cython compilation)
├── MANIFEST.in             # Source distribution file inclusion
│
├── new_version.py          # Version update automation script
├── .gitignore              # Git exclusions
│
└── e2D.egg-info/           # Package metadata (auto-generated)
```

## Core Package Files (`e2D/`)

### Python Modules
- **`__init__.py`** - Package entry point, exports public API
- **`vectors.py`** - Pure Python Vector2D fallback
- **`colors.py`** - Color class and operations
- **`color_defs.py`** - 80+ pre-defined color constants
- **`shapes.py`** - Shape rendering (circles, rectangles, lines)
- **`text_renderer.py`** - Text rendering with GPU caching
- **`plots.py`** - Mathematical plotting with GPU compute
- **`devices.py`** - RootEnv engine and DefEnv base class
- **`winrec.py`** - Screen recording (requires opencv-python)
- **`commons.py`** - Shared utilities
- **`types.py`** - Type definitions

### Cython Extensions (compiled for performance)
- **`cvectors.pyx`** - Cython-optimized Vector2D (10-500x faster)
- **`ccolors.pyx`** - Cython-optimized color operations
- **`cvectors.pxd`** - Cython declarations (C-level API)
- **`cvectors.c`** - Auto-generated C code (excluded from git)

### Type Stubs (`.pyi` files)
Provide IDE autocomplete and type checking for compiled extensions.

### GLSL Shaders (`shaders/`)
GPU programs for rendering:
- **`segment_vertex.glsl`** / **`segment_fragment.glsl`** - Line/segment rendering
- **`curve_vertex.glsl`** / **`curve_fragment.glsl`** - Curve plotting
- **`plot_grid_vertex.glsl`** / **`plot_grid_fragment.glsl`** - Plot grid overlay
- **`stream_vertex.glsl`** / **`stream_fragment.glsl`** - Vector field visualization
- **`stream_shift_compute.glsl`** - GPU compute for stream plots
- **`line_instanced_vertex.glsl`** - Instanced line rendering

## Configuration Files

### Build & Packaging
- **`pyproject.toml`** - Modern build system config (PEP 517)
  - Build dependencies (setuptools, Cython)
  - Package metadata
  - Optional extras: `[rec]`, `[dev]`, `[performance]`, `[all]`

- **`setup.cfg`** - Package configuration
  - Version, author, description
  - Dependencies
  - Python version requirements
  - Classifiers for PyPI

- **`setup.py`** - Build script
  - Cython extension compilation
  - Automatic fallback to pure Python
  - Configuration for both `.pyx` files

- **`MANIFEST.in`** - Source distribution inclusion rules
  - Includes: `.pyx`, `.pxd`, `.pyi`, `.glsl`, docs, LICENSE
  - Excludes: `.c` files (build artifacts), tests

### Git
- **`.gitignore`** - Git exclusions
  - Cython build artifacts: `*.c`, `*.pyd`, `*.so`, `*.html`
  - Python bytecode: `__pycache__/`, `*.pyc`
  - Distribution: `build/`, `dist/`, `*.egg-info/`
  - IDE: `.vscode/`, `.idea/`
  - **Sensitive files**: `SET_TOKEN.bat`, `new_version.bat`, `build_dev.bat`

## Documentation

### User Documentation
- **`README.md`** - Main project page (shown on GitHub and PyPI)
  - Features overview
  - Installation instructions
  - Quick start examples
  - Performance benchmarks
  - Links to detailed docs

- **`QUICKSTART.md`** - Getting started tutorial
- **`docs/*.md`** - Feature-specific documentation (see above)

### Developer Documentation
- **`DEVELOPER_GUIDE.md`** - Development workflow
  - Setting up development environment
  - Building from source
  - Running tests
  - Creating releases

- **`BUILD_CHECKLIST.md`** - Pre-release verification
  - Code quality checks
  - Testing requirements
  - Documentation updates
  - Version bumping steps

## Scripts & Automation

### Development Scripts (NOT in git - contain or reference tokens)
- **`SET_TOKEN.bat`** - Sets PyPI API token (CONTAINS SECRET - ignored by git)
- **`new_version.bat`** - Automated release workflow
- **`build_dev.bat`** - Local development build

### Python Automation (in git)
- **`new_version.py`** - Updates version numbers in:
  - `setup.cfg`
  - `e2D/__init__.py`
  - `README.md` (version history)

## Build Process

### Installation from PyPI
```
pip install e2D
  ↓
1. Download source distribution (.tar.gz)
2. setup.py runs:
   - Compiles cvectors.pyx → cvectors.c → cvectors.pyd (Windows) / .so (Linux)
   - Compiles ccolors.pyx → ccolors.c → ccolors.pyd (Windows) / .so (Linux)
3. If compilation fails:
   - Falls back to pure Python vectors.py
4. Installs package to site-packages
```

### Development Build
```
pip install -e .[dev]
  ↓
1. Installs package in editable mode
2. Compiles Cython extensions in-place
3. Changes to Python files take effect immediately
4. Changes to .pyx files require rebuild
```

### Release Process
```
1. Update version: python new_version.py patch
2. Clean: python -m build (removes old dist/)
3. Build: python -m build (creates .tar.gz and .whl)
4. Upload: python -m twine upload dist/*
```

## Optional Dependencies

### Core (always installed)
- **numpy** - Array operations, GPU data upload
- **moderngl** - OpenGL context and rendering
- **glfw** - Window management and input

### Optional Extras

#### `[rec]` - Screen Recording
```bash
pip install e2D[rec]
```
- **opencv-python** - Video encoding

#### `[dev]` - Development Tools
```bash
pip install e2D[dev]
```
- **pytest** - Testing framework
- **black** - Code formatter
- **mypy** - Type checker
- **build** - Build tool
- **twine** - PyPI upload

#### `[performance]` - Performance Monitoring
```bash
pip install e2D[performance]
```
- **cython** - Cython source for profiling

#### `[all]` - Everything
```bash
pip install e2D[all]
```
All optional dependencies.

## Version History

### v2.x (ModernGL-based - Current)
Complete rewrite with:
- ModernGL rendering (replaced pygame)
- Cython-optimized vectors (10-500x faster)
- GPU compute shaders for plotting
- Modern color system (80+ colors)
- Screen recording with async encoding
- Type hints throughout

### v1.x (Pygame-based - Legacy)
Original implementation:
- Pygame rendering
- Pure Python vectors
- Basic color system
- Install with: `pip install "e2D<2.0"`

## Security Notes

### Sensitive Files (excluded from git)
- **`SET_TOKEN.bat`** - Contains actual PyPI API token
- **`new_version.bat`** - References environment token
- **`build_dev.bat`** - May contain local paths

### Safe Files (included in git)
- **`new_version.py`** - Reads token from environment (safe)
- All `.py`, `.pyx`, `.pyi` files (source code)
- Documentation files
- Configuration files (no secrets)

### Before Publishing to GitHub
✅ Verified `.gitignore` excludes:
- Build artifacts (`*.c`, `*.pyd`, `*.so`)
- PyPI tokens (`SET_TOKEN.bat`)
- Local scripts (`*.bat`)

## Testing

### Run Tests
```bash
pytest
```

### Test Coverage
```bash
pytest --cov=e2D
```

### Type Checking
```bash
mypy e2D
```

## Contributing

See [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md) for:
- Development environment setup
- Coding standards
- Pull request process
- Release workflow

---

[← Back to README](../README.md)
