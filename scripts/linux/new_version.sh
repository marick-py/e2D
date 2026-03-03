#!/bin/bash
# e2D New Version Release Script

# Change to project root relative to script location
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo ""
echo "============================================"
echo "e2D New Version Release Workflow"
echo "============================================"
echo ""

# Step 1: Clean
echo "Step 1: Cleaning build artifacts..."
echo "============================================"
# Call sibling script; assumes execute permission or calls with sh
"$SCRIPT_DIR/clean.sh"
if [ $? -ne 0 ]; then
    echo "ERROR: Clean failed"
    exit 1
fi

# Step 2: Install dependencies
echo ""
echo "Step 2: Installing dependencies..."
echo "============================================"
py -3.13 -m pip install -e .[dev] --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Dependency installation failed"
    exit 1
fi
echo "Dependencies installed"

# Step 4: Run tests
echo ""
echo "Step 4: Running test suite..."
echo "============================================"
py -3.13 -m pytest tests/ -v
if [ $? -ne 0 ]; then
    echo ""
    echo "============================================"
    echo "ERROR: Tests failed!"
    echo "============================================"
    echo "Fix the failing tests before creating a new version"
    exit 1
fi

# Step 5: ReClean
echo ""
echo "Step 5: ReCleaning build artifacts..."
echo "============================================"
"$SCRIPT_DIR/clean.sh"
if [ $? -ne 0 ]; then
    echo "ERROR: Clean failed"
    exit 1
fi

echo ""
echo "============================================"
echo "All tests passed!"
echo "============================================"

# Step 6: Version bump
echo ""
echo "Step 6: Version bump..."
echo "============================================"
py -3.13 new_version.py
if [ $? -ne 0 ]; then
    echo "ERROR: Version update failed"
    exit 1
fi

echo ""
echo "============================================"
echo "Version update complete!"
echo "============================================"
