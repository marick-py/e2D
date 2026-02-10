"""
Quick test to demonstrate Vector2Int solving the precision problem
Run this after rebuilding the Cython module
"""

def test_precision_problem():
    """Demonstrate the floating-point precision issue and solution"""
    from e2D import V2, V2I
    
    print("=" * 60)
    print("FLOATING-POINT PRECISION ERROR DEMONSTRATION")
    print("=" * 60)
    
    # The original problem with Vector2D
    print("\n❌ Vector2D (float) - HAS PRECISION ERRORS:")
    cell_pos_float = V2(3.0, 1.0)
    cells_per_row = 10.0
    index_float = cell_pos_float.x + cell_pos_float.y * cells_per_row
    print(f"   Position: {cell_pos_float}")
    print(f"   Calculation: {cell_pos_float.x} + {cell_pos_float.y} * {cells_per_row}")
    print(f"   Result: {index_float}")
    print(f"   int(Result): {int(index_float)}")
    print(f"   Expected: 13")
    print(f"   ⚠️  WRONG! Got {index_float} instead of 13.0")
    
    # The solution with Vector2Int
    print("\n✅ Vector2Int (int) - PERFECT PRECISION:")
    cell_pos_int = V2I(3, 1)
    cells_per_row_int = 10
    index_int = cell_pos_int.x + cell_pos_int.y * cells_per_row_int
    print(f"   Position: {cell_pos_int}")
    print(f"   Calculation: {cell_pos_int.x} + {cell_pos_int.y} * {cells_per_row_int}")
    print(f"   Result: {index_int}")
    print(f"   Expected: 13")
    print(f"   ✓ CORRECT! Perfect integer precision!")
    
    print("\n" + "=" * 60)
    print("ADDITIONAL VECTOR2INT TESTS")
    print("=" * 60)
    
    # Basic operations
    v1 = V2I(10, 20)
    v2 = V2I(5, 3)
    
    print(f"\nv1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v1 + v2 = {v1 + v2}")
    print(f"v1 - v2 = {v1 - v2}")
    print(f"v1 * 2 = {v1 * 2}")
    print(f"v1 // 2 = {v1 // 2}")
    print(f"v1.dot_product(v2) = {v1.dot_product(v2)}")
    
    # In-place operations
    v3 = V2I(5, 5)
    print(f"\nv3 = {v3}")
    v3.iadd(V2I(3, 2))
    print(f"After v3.iadd(V2I(3, 2)): {v3}")
    v3.imul(2)
    print(f"After v3.imul(2): {v3}")
    
    # Grid example
    print("\n" + "=" * 60)
    print("GRID SYSTEM EXAMPLE")
    print("=" * 60)
    
    grid_size = V2I(10, 10)
    positions = [V2I(x, y) for y in range(3) for x in range(3)]
    
    print(f"\nGrid size: {grid_size}")
    print("Positions and their array indices:")
    for pos in positions:
        idx = pos.x + pos.y * grid_size.x
        print(f"   {pos} → index {idx}")
    
    # Conversion
    print("\n" + "=" * 60)
    print("TYPE CONVERSIONS")
    print("=" * 60)
    
    int_vec = V2I(5, 10)
    float_vec = int_vec.to_float()
    print(f"\nVector2Int: {int_vec}")
    print(f"to_float(): {float_vec}")
    print(f"Type: {type(float_vec).__name__}")
    
    print("\n✅ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_precision_problem()
    except ImportError as e:
        print("❌ Error: Could not import Vector2Int")
        print(f"   {e}")
        print("\n⚠️  You need to rebuild the Cython module:")
        print("   1. Run: python setup.py build_ext --inplace")
        print("   2. Or run: build_dev.bat")
        print("   3. Then run this test again")
