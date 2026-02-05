# Developer Guide - e2D Package

## 📁 Project Structure

```
e2D_2.0/
├── .github/
│   └── workflows/
│       ├── publish.yml           # Automated PyPI publishing
│       └── test.yml              # CI testing on multiple Python versions
├── docs/
│   └── API_REFERENCE.md          # Complete API documentation
├── e2D/                          # Main package
│   ├── __init__.py               # Package initialization & RootEnv
│   ├── __init__.pyi              # Type stubs
│   ├── cvectors.pyx              # Cython-optimized vector implementation
│   ├── cvectors.pxd              # Cython header
│   ├── cvectors.pyi              # Vector type stubs
│   ├── cvectors.c                # Compiled C extension
│   ├── ccolors.pyx               # Cython color operations (optional)
│   ├── ccolors.pyi               # Color type stubs
│   ├── ccolors.c                 # Compiled C extension
│   ├── vectors.py                # Python utilities and fallback
│   ├── vectors.pyi               # Vector type stubs
│   ├── colors.py                 # Color class and operations
│   ├── colors.pyi                # Color type stubs
│   ├── color_defs.py             # 80+ pre-defined colors
│   ├── commons.py                # Common utilities
│   ├── commons.pyi               # Type stubs
│   ├── devices.py                # Input handling (Keyboard/Mouse)
│   ├── devices.pyi               # Type stubs
│   ├── plots.py                  # Plotting utilities
│   ├── plots.pyi                 # Type stubs
│   ├── shapes.py                 # Shape rendering
│   ├── shapes.pyi                # Type stubs
│   ├── text_renderer.py          # Text rendering with PIL
│   ├── text_renderer.pyi         # Type stubs
│   ├── types.py                  # Type definitions
│   ├── types.pyi                 # Type stubs
│   ├── winrec.py                 # Screen recording
│   ├── winrec.pyi                # Type stubs
│   ├── test_colors.py            # Color system tests
│   └── shaders/                  # GLSL shader files
│       ├── curve_fragment.glsl
│       ├── curve_vertex.glsl
│       ├── line_instanced_vertex.glsl
│       ├── plot_grid_fragment.glsl
│       ├── plot_grid_vertex.glsl
│       ├── segment_fragment.glsl
│       ├── segment_vertex.glsl
│       ├── stream_fragment.glsl
│       ├── stream_shift_compute.glsl
│       └── stream_vertex.glsl
├── e2D.egg-info/                 # Package metadata (auto-generated)
├── dist/                         # Built distributions (auto-generated)
├── setup.py                      # Build configuration
├── setup.cfg                     # Package metadata
├── pyproject.toml                # Modern Python packaging (PEP 517)
├── MANIFEST.in                   # Distribution manifest
├── README.md                     # Main documentation & PyPI landing page
├── DEVELOPER_GUIDE.md            # This file
├── PUBLISHING.md                 # GitHub Actions publishing guide
├── LICENSE                       # MIT License
├── new_version.py                # Version updater helper script
├── new_version.bat               # Local version update script (optional)
├── build_dev.bat                 # Local development build script (optional)
└── SET_TOKEN.bat                 # Local PyPI token setup (optional, ignored by git)
```

**Note**: `.bat` files are optional local helpers. With GitHub Actions, you don't need them anymore!

## 🔧 Development Workflow

### 1. Initial Setup

```bash
# Clone or navigate to project
cd path/to/e2D-package

# Install in development mode
pip install -e .[dev]
```

This installs the package in "editable" mode, so changes are immediately reflected.

### 2. Making Changes

#### Modifying Python Code
- Edit files in `e2D/`
- Changes are immediately available (no reinstall needed)

#### Modifying Cython Code
If you modify `cvectors.pyx` or `cvectors.pxd`:

```bash
# Recompile the extension
python setup.py build_ext --inplace
```

### 3. Testing

```bash
# Test basic import
python -c "import e2D; print(e2D.__version__)"

# Run examples
python examples/example_usage.py
python examples/compare_performance.py

# Test installation from scratch
pip uninstall e2D
pip install .
```

### 4. Updating Version

```bash
# Run the version updater
python new_version.py
```

Or on Windows:
```cmd
new_version.bat
```

This updates:
- `setup.cfg` → `version`
- `e2D/__init__.py` → `__version__`

### 5. Building Distribution

```bash
# Clean previous builds
python clean.bat  # Windows
rm -rf build dist *.egg-info  # Linux/Mac

# Build source and wheel distributions
python -m build
```

This creates:
- `dist/e2D-x.x.x.tar.gz` (source distribution)
- `dist/e2D-x.x.x-*.whl` (wheel distribution)

### 6. Testing Distribution

```bash
# Test in a virtual environment
python -m venv test_env
test_env\Scripts\activate  # Windows
source test_env/bin/activate  # Linux/Mac

# Install from wheel
pip install dist/e2D-2.0.0-*.whl

# Test it works
python -c "from e2D import Vector2D; v = Vector2D(1, 2); print(v)"
```

### 7. Publishing to PyPI

#### Option A: Automated (Windows)
```cmd
new_version.bat
```

This script:
1. Updates version
2. Cleans build artifacts
3. Builds distributions
4. Uploads to PyPI

#### Option B: Manual
```bash
# Upload to PyPI
python -m twine upload dist/*

# Or upload to TestPyPI first
python -m twine upload --repository testpypi dist/*
```

## 📋 Pre-Release Checklist

Before publishing a new version:

- [ ] All tests pass
- [ ] Examples run without errors
- [ ] Version number updated in all files
- [ ] README.md is up to date
- [ ] CHANGELOG updated (if you have one)
- [ ] Cython extensions compile on Windows, Linux, Mac
- [ ] License file is included
- [ ] No sensitive data (API keys, tokens) in code

## 🔍 Troubleshooting

### Cython Won't Compile

**Problem**: `error: Microsoft Visual C++ 14.0 is required`

**Solution**: Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

**Alternative**: Package will use pure Python fallback (slower but functional)

### Import Errors

**Problem**: `ImportError: cannot import name 'Vector2D'`

**Solutions**:
```bash
# Ensure package is installed
pip list | grep e2D

# Reinstall in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Version Not Updating

**Problem**: Old version still shows after update

**Solutions**:
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
rm -rf build dist *.egg-info

# Reinstall
pip uninstall e2D
pip install -e .
```

### Build Fails

**Problem**: `error: command 'gcc' failed`

**Linux Solution**:
```bash
sudo apt-get install build-essential python3-dev
```

**Mac Solution**:
```bash
xcode-select --install
```

## 🚀 Performance Optimization

### Checking Compilation Status

```python
import e2D
print(f"Version: {e2D.__version__}")
```

### Benchmarking

```python
from e2D.vectors import benchmark
benchmark(iterations=100000)
```

### Profiling

```python
import cProfile
import pstats

cProfile.run('your_simulation_code()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## 📦 Distribution Best Practices

### Source Distribution
- Includes all source code
- Users compile on their machine
- Works on any platform
- Requires compiler

### Wheel Distribution
- Pre-compiled for specific platform
- Quick installation
- No compiler needed
- Platform-specific

### Building Wheels for Multiple Platforms

Use `cibuildwheel` for automated multi-platform builds:

```yaml
# .github/workflows/build.yml
name: Build wheels
on: [push, pull_request]
jobs:
  build_wheels:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - uses: actions/checkout@v2
      - uses: pypa/cibuildwheel@v2.11.0
```

## 🔐 Security

- **Never commit** your PyPI token
- Store token in environment variable or keyring
- Use API tokens instead of passwords
- Enable 2FA on PyPI account

## 📝 Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 2.0.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Examples:
- `2.0.0` → `2.0.1`: Bug fix
- `2.0.0` → `2.1.0`: New feature
- `2.0.0` → `3.0.0`: Breaking change

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/marick-py/e2D/issues)
- **Email**: riccardo.mariani@emptyhead.dev
- **Documentation**: README.md

---

Happy developing! 🚀


