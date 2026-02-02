@echo off
REM Clean up build artifacts and temporary files

echo Cleaning e2D project...

REM Remove build directories
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "e2D.egg-info" rmdir /s /q "e2D.egg-info"

REM Remove Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

REM Remove compiled Python files
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
del /s /q *.pyd 2>nul

REM Remove Cython build files
del /s /q e2D\*.c 2>nul
del /s /q e2D\*.html 2>nul

echo.
echo ✓ Cleanup complete!
echo.
echo Kept:
echo   - Source code (.py, .pyx, .pxd)
echo   - Documentation (.md)
echo   - Configuration files
echo.
pause
