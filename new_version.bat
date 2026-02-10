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

REM Step 2: Install dependencies
echo.
echo Step 2: Installing dependencies...
echo ============================================
py -3.13 -m pip install -e .[dev] --quiet
if errorlevel 1 (
    echo ERROR: Dependency installation failed
    pause
    exit /b 1
)
echo Dependencies installed

REM Step 4: Run tests
echo.
echo Step 4: Running test suite...
echo ============================================
py -3.13 -m pytest tests/ -v
if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: Tests failed!
    echo ============================================
    echo Fix the failing tests before creating a new version
    pause
    exit /b 1
)

REM Step 5=======================================
py -3.13 -m pytest tests/ -v
if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: Tests failed!
    echo ============================================
    echo Fix the failing tests before creating a new version
    pause
    exit /b 1
)

REM Step 5: ReClean
echo.
echo Step 5: ReCleaning build artifacts...
echo ============================================
call clean.bat
if errorlevel 1 (
    echo ERROR: Clean failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo All tests passed!
echo ============================================
6: Version bump
echo.
echo Step 6
echo Step 5: Version bump...
echo ============================================
py -3.13 new_version.py
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