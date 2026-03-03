@echo off
REM ============================================
REM e2D Site-Packages Install Script
REM Builds and installs to Python 3.13 site-packages
REM Backs up existing install to e2D-old
REM ============================================

pushd "%~dp0..\.."

echo.
echo ============================================
echo e2D Site-Packages Installer
echo ============================================
echo.

REM Step 1: Clean previous build artifacts
echo Step 1: Clean previous builds
echo ============================================
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist e2D\*.c del /q e2D\*.c
if exist e2D\*.pyd del /q e2D\*.pyd
if exist e2D\*.so del /q e2D\*.so
echo Cleaned build artifacts

echo.
echo Step 2: Build Cython extensions in-place
echo ============================================
py -3.13 setup.py build_ext --inplace
if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: Cython build failed
    echo ============================================
    popd
    pause
    exit /b 1
)
echo Built Cython extensions

echo.
echo Step 3: Resolve Python 3.13 site-packages path
echo ============================================
REM Use the actual target pip will install to (user site-packages if system is not writable)
for /f "delims=" %%i in ('py -3.13 -c "import site, os; sp=site.getsitepackages()[0]; print(sp if os.access(sp, os.W_OK) else site.getusersitepackages())"') do set SITE_PACKAGES=%%i
if not defined SITE_PACKAGES (
    echo ERROR: Could not determine site-packages path
    popd
    pause
    exit /b 1
)
echo Site-packages: %SITE_PACKAGES%

echo.
echo Step 4: Backup existing e2D installation
echo ============================================
if exist "%SITE_PACKAGES%\e2D-old" (
    echo Removing previous backup ^(e2D-old^)...
    rmdir /s /q "%SITE_PACKAGES%\e2D-old"
)
if exist "%SITE_PACKAGES%\e2D" (
    echo Backing up e2D to e2D-old...
    xcopy "%SITE_PACKAGES%\e2D" "%SITE_PACKAGES%\e2D-old\" /e /i /q
    echo Backup saved to: %SITE_PACKAGES%\e2D-old
) else (
    echo No existing e2D installation found, skipping backup
)

echo.
echo Step 5: Install e2D to Python 3.13 site-packages
echo ============================================
py -3.13 -m pip install . --force-reinstall --no-deps
if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: pip install failed
    echo ============================================
    popd
    pause
    exit /b 1
)

echo.
echo ============================================
echo Done!
echo ============================================
echo.
echo Installed : %SITE_PACKAGES%\e2D
echo Backup    : %SITE_PACKAGES%\e2D-old
echo.
echo To verify: py -3.13 -c "from e2D import Vector2D, Vector2Int, V2, V2I; print('OK')"
echo.
popd
pause
