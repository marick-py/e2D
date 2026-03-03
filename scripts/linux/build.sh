#!/bin/bash
# e2D Site-Packages Install Script

# Change to project root relative to script location
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo ""
echo "============================================"
echo "e2D Installer"
echo "============================================"
echo ""

# Step 1: Clean previous build artifacts
echo "Step 1: Clean previous builds"
echo "============================================"
rm -rf build dist e2D.egg-info
rm -f e2D/*.c e2D/*.pyd e2D/*.so
echo "Cleaned build artifacts"

echo ""
echo "Step 2: Build Cython extensions in-place"
echo "============================================"
py -3.13 setup.py build_ext --inplace
if [ $? -ne 0 ]; then
    echo "ERROR: Cython build failed"
    exit 1
fi
echo "Built Cython extensions"

echo ""
echo "Step 3: Install e2D"
echo "============================================"
# Standard minimal install, respecting environment
py -3.13 -m pip install . --force-reinstall --no-deps
if [ $? -ne 0 ]; then
    echo "ERROR: pip install failed"
    exit 1
fi

echo ""
echo "============================================"
echo "Done!"
echo "============================================"
echo ""
echo "To verify: py -3.13 -c \"from e2D import Vector2D, Vector2Int, V2, V2I; print('OK')\""
