@echo off
REM ============================================
REM e2D New Version Release Script
REM Cleans, builds, tests, and bumps version
REM ============================================

echo.
echo ============================================
echo e2D New Version Release Workflow
echo ============================================
echo.

REM Step 1: Clean
echo Step 1: Cleaning build artifacts...
echo ============================================
call clean.bat
if errorlevel 1 (
    echo ERROR: Clean failed
    pause
    exit /b 1
)

REM Step 2: Build
echo.
echo Step 2: Building Cython extensions...
echo ============================================
call build_dev.bat
if errorlevel 1 (
    echo ERROR: Build failed
    echo Cannot proceed with version bump without successful build
    pause
    exit /b 1
)

REM Step 3: Run tests
echo.
echo Step 3: Running test suite...
echo ============================================
python -m unittest discover -s tests -p "test_*.py" -v
if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: Tests failed!
    echo ============================================
    echo Fix the failing tests before creating a new version
    pause
    exit /b 1
)

echo.
echo ============================================
echo All tests passed!
echo ============================================

REM Step 4: Version bump
echo.
echo Step 4: Version bump...
echo ============================================
python new_version.py
if errorlevel 1 (
    echo ERROR: Version update failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo Version update complete!
echo ============================================
pause