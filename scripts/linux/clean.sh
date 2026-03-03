#!/bin/bash
# Clean up build artifacts and temporary files

# Change to project root relative to script location
SCRIPT_DIR="$(dirname "$0")"
# Use absolute path for robustness
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo "Cleaning e2D project..."

# Remove build directories
rm -rf build dist e2D.egg-info

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove compiled Python files
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete

# Remove Cython build files
rm -f e2D/*.c

echo ""
echo "Cleanup complete!"
