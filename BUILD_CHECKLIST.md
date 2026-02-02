# e2D Build & Release Checklist

## ✅ Completed Updates

### 1. Setup Files Updated
- ✓ `setup.py` - Added ccolors.pyx compilation
- ✓ `setup.cfg` - Added opencv-python dependency
- ✓ `pyproject.toml` - Added opencv-python dependency
- ✓ `MANIFEST.in` - Added .pyi stub files
- ✓ `README.md` - Updated with new features (color system, screen recording)

### 2. Version Management
- ✓ `new_version.py` - Now updates both setup.cfg AND e2D/__init__.py
- ✓ Version sync between files maintained

### 3. Build Scripts
- ✓ `build_dev.bat` - Build extensions locally without installing
- ✓ `build_extensions.py` - In-place compilation for site-packages testing
- ✓ `build_extensions.bat` - Windows batch script for site-packages

## 📋 Next Steps (DO MANUALLY)

### Step 1: Compile Extensions in Site-Packages (Current Location)
```cmd
cd C:\Users\User\AppData\Roaming\Python\Python313\site-packages\e2D
build_extensions.bat
```

This will compile:
- cvectors.pyx → cvectors.pyd
- ccolors.pyx → ccolors.pyd

### Step 2: Test Compilation
```cmd
py -3.13 -c "from e2D import Vector2D, Color, _VECTOR_COMPILED, _COLOR_COMPILED; print(f'Vectors: {_VECTOR_COMPILED}, Colors: {_COLOR_COMPILED}')"
```

Expected output: `Vectors: True, Colors: True`

### Step 3: Copy Files to Project Directory
Copy all updated files from site-packages to your project:

**From:** `C:\Users\User\AppData\Roaming\Python\Python313\site-packages\e2D\`
**To:** `C:\Users\User\OneDrive\MyDev\Python\MyModules\e2D_2.0\e2D\`

Files to copy:
- All `.py` files
- All `.pyi` files  
- All `.pyx` files
- All `.pxd` files
- `shaders/` directory
- `__init__.py` (with correct version)

### Step 4: Build Distribution in Project Directory
```cmd
cd C:\Users\User\OneDrive\MyDev\Python\MyModules\e2D_2.0
build_dev.bat
```

This compiles extensions in the project directory without installing.

### Step 5: Update Version
```cmd
cd C:\Users\User\OneDrive\MyDev\Python\MyModules\e2D_2.0
py -3.13 new_version.py
```

Enter new version (e.g., 2.1.0). This will update:
- setup.cfg
- e2D/__init__.py

### Step 6: Build Distribution
```cmd
cd C:\Users\User\OneDrive\MyDev\Python\MyModules\e2D_2.0

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist e2D.egg-info rmdir /s /q e2D.egg-info

REM Build
py -3.13 -m build
```

### Step 7: Test Distribution Locally
```cmd
REM Create test environment
py -3.13 -m venv test_env
test_env\Scripts\activate

REM Install from wheel
pip install dist\e2D-2.1.0-*.whl

REM Test
py -3.13 -c "from e2D import Vector2D, Color; print('SUCCESS')"

REM Cleanup
deactivate
rmdir /s /q test_env
```

### Step 8: Upload to PyPI (WHEN READY)
```cmd
cd C:\Users\User\OneDrive\MyDev\Python\MyModules\e2D_2.0
new_version.bat
```

This will:
1. Update version
2. Clean builds
3. Build distributions
4. Upload to PyPI (requires PYPI_TOKEN environment variable)

## 🔍 Verification Commands

### Check Compiled Status
```python
import e2D
print(f"Version: {e2D.__version__}")
print(f"Vectors compiled: {e2D._VECTOR_COMPILED}")
print(f"Colors compiled: {e2D._COLOR_COMPILED}")
```

### Check Available Functions
```python
from e2D import Vector2D, Color, batch_add_inplace
from e2D.cvectors import Vector2D as CVec
from e2D.ccolors import batch_lerp_colors
print("All imports successful!")
```

### Run Benchmark
```python
from e2D.vectors import benchmark
benchmark(100000)
```

## 📦 What Gets Published

When you run `py -3.13 -m build`, it creates:

1. **Source Distribution** (`e2D-2.x.x.tar.gz`)
   - Contains all source code
   - Users compile on their machine
   - Works on any platform

2. **Wheel** (`e2D-2.x.x-cp313-cp313-win_amd64.whl`)
   - Pre-compiled for Windows Python 3.13
   - Fast installation
   - No compiler needed

## ⚠️ Important Notes

1. **DO NOT** run `pip install e2D` while in site-packages - it will overwrite your changes
2. **DO NOT** run `new_version.bat` until you're ready to upload to PyPI
3. **ALWAYS** test in a virtual environment before publishing
4. **BACKUP** your site-packages e2D folder before copying to project
5. **VERIFY** version numbers match in setup.cfg and __init__.py

## 🎯 New Features in This Release

- ✅ Modern Color class with RGBA float (0.0-1.0) for ModernGL
- ✅ 80+ pre-defined colors (Material Design, Pastel, Neon, UI)
- ✅ Cython-optimized batch color operations
- ✅ Screen recording with WinRec (F9/F10/F12 controls)
- ✅ Async video encoding with OpenCV
- ✅ Type-safe with comprehensive .pyi stubs
- ✅ Backward compatible with existing code

## 📚 Documentation Updated

- README.md - Added color system and recording examples
- setup.cfg - Updated description with new features
- All setup files - Added opencv-python dependency
