@echo off
REM ============================================
REM e2D Package - Version Update & Upload Script
REM ============================================

echo.
echo ============================================
echo e2D Package Publisher
echo ============================================
echo.

REM Update version
echo Step 1: Update version number
echo ============================================
py -3.13 new_version.py
if errorlevel 1 (
    echo ERROR: Version update failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo Step 2: Clean previous builds
echo ============================================
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist e2D.egg-info rmdir /s /q e2D.egg-info
if exist e2D\*.c del /q e2D\*.c
if exist e2D\*.pyd del /q e2D\*.pyd
if exist e2D\*.so del /q e2D\*.so
echo ✓ Cleaned build artifacts

echo.
echo ============================================
echo Step 3: Build distribution packages
echo ============================================
py -3.13 -m build
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo ✓ Built source and wheel distributions

echo.
echo ============================================
echo Step 4: Upload to PyPI
echo ============================================

REM Check if PYPI_TOKEN is set
if "%PYPI_TOKEN%"=="" (
    echo.
    echo ERROR: PYPI_TOKEN environment variable is not set!
    echo.
    echo To set it temporarily for this session:
    echo   set PYPI_TOKEN=your-token-here
    echo.
    echo To set it permanently:
    echo   setx PYPI_TOKEN "your-token-here"
    echo.
    echo Or run SET_TOKEN.bat to configure it
    echo.
    pause
    exit /b 1
)

py -3.13 -m twine upload -u __token__ -p %PYPI_TOKEN% --skip-existing --repository pypi dist/*
if errorlevel 1 (
    echo ERROR: Upload failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo ✓ Package published successfully!
echo ============================================
echo.
echo You can now install it with:
echo   py -3.13 -m pip install e2D --upgrade
echo.
pause
