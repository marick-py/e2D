@echo off
REM ============================================
REM e2D Development Build Script
REM Builds Cython extensions without installing
REM ============================================

echo.
echo ============================================
echo e2D Development Builder
echo ============================================
echo.

echo Step 1: Clean previous builds
echo ============================================
if exist build rmdir /s /q build
if exist e2D\*.c del /q e2D\*.c
if exist e2D\*.pyd del /q e2D\*.pyd
if exist e2D\*.so del /q e2D\*.so
echo ✓ Cleaned build artifacts

echo.
echo Step 2: Build Cython extensions in-place
echo ============================================
py -3.14 setup.py build_ext --inplace
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo ✓ Built extensions in-place

echo.
echo ============================================
echo ✓ Build complete!
echo ============================================
echo.
echo Extensions compiled to e2D/ directory
echo You can now test locally before publishing
echo.
echo To test: py -3.14 -c "from e2D import Vector2D, Color; print('OK')"
echo.
pause
