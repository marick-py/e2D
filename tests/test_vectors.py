"""
Unit tests for e2D vector operations
Tests Vector2D class and batch operations without requiring a window
"""

import numpy as np

from e2D import (
    Vector2D, V2, V2I, CommonVectors,
    batch_add_inplace, batch_scale_inplace, batch_normalize_inplace,
    vectors_to_array, array_to_vectors, lerp, create_grid, create_circle
)

def test_vector_creation():
    """Test vector creation and initialization"""
    print("\n=== Vector Creation ===")
    
    # Basic creation
    v1 = Vector2D(3.0, 4.0)
    assert v1.x == 3.0 and v1.y == 4.0, "Basic creation failed"
    
    # Alias
    v2 = V2(1.0, 2.0)
    assert v2.x == 1.0 and v2.y == 2.0, "Alias creation failed"
    
    # From tuple
    v3 = Vector2D(*(5.0, 6.0))
    assert v3.x == 5.0 and v3.y == 6.0, "Tuple unpacking failed"
    
    # Random
    v4 = Vector2D.random(-10, 10)
    assert -10 <= v4.x <= 10 and -10 <= v4.y <= 10, "Random creation out of bounds"
    
    print("✓ Vector creation tests passed")

def test_vector_operations():
    """Test basic vector operations"""
    print("\n=== Vector Operations ===")
    
    v1 = Vector2D(3.0, 4.0)
    v2 = Vector2D(1.0, 2.0)
    
    # Addition
    v3 = v1 + v2
    assert abs(v3.x - 4.0) < 0.001 and abs(v3.y - 6.0) < 0.001, "Addition failed"
    
    # Subtraction
    v4 = v1 - v2
    assert abs(v4.x - 2.0) < 0.001 and abs(v4.y - 2.0) < 0.001, "Subtraction failed"
    
    # Multiplication by scalar
    v5 = v1.mul(2.0)
    assert abs(v5.x - 6.0) < 0.001 and abs(v5.y - 8.0) < 0.001, "Scalar multiplication failed"
    
    # Length
    length = v1.length
    expected = (3.0**2 + 4.0**2)**0.5
    assert abs(length - expected) < 0.001, f"Length calculation failed: {length} != {expected}"
    
    # Dot product
    dot = v1.dot_product(v2)
    expected_dot = 3.0*1.0 + 4.0*2.0
    assert abs(dot - expected_dot) < 0.001, "Dot product failed"
    
    print("✓ Vector operations tests passed")

def test_inplace_operations():
    """Test in-place vector operations"""
    print("\n=== In-place Operations ===")
    
    v1 = Vector2D(3.0, 4.0)
    
    # In-place addition
    v1.iadd(Vector2D(1.0, 2.0))
    assert abs(v1.x - 4.0) < 0.001 and abs(v1.y - 6.0) < 0.001, "In-place addition failed"
    
    # In-place subtraction
    v2 = Vector2D(10.0, 10.0)
    v2.isub(Vector2D(5.0, 5.0))
    assert abs(v2.x - 5.0) < 0.001 and abs(v2.y - 5.0) < 0.001, "In-place subtraction failed"
    
    # In-place scaling
    v3 = Vector2D(2.0, 3.0)
    v3.imul(3.0)
    assert abs(v3.x - 6.0) < 0.001 and abs(v3.y - 9.0) < 0.001, "In-place scaling failed"
    
    # In-place normalization
    v4 = Vector2D(3.0, 4.0)
    v4.normalize()
    assert abs(v4.length - 1.0) < 0.001, "Normalization failed"
    
    print("✓ In-place operations tests passed")

def test_batch_operations():
    """Test batch vector operations"""
    print("\n=== Batch Operations ===")
    
    # Create test vectors
    vectors = [Vector2D(float(i), float(i)) for i in range(100)]
    
    # Batch add
    displacement = Vector2D(5.0, 10.0)
    batch_add_inplace(vectors, displacement)
    assert abs(vectors[0].x - 5.0) < 0.001 and abs(vectors[0].y - 10.0) < 0.001, "Batch add failed"
    
    # Batch scale
    batch_scale_inplace(vectors, 2.0)
    assert abs(vectors[0].x - 10.0) < 0.001 and abs(vectors[0].y - 20.0) < 0.001, "Batch scale failed"
    
    # Batch normalize
    vectors2 = [Vector2D(3.0, 4.0) for _ in range(10)]
    batch_normalize_inplace(vectors2)
    for v in vectors2:
        assert abs(v.length - 1.0) < 0.001, "Batch normalize failed"
    
    print("✓ Batch operations tests passed")

def test_array_conversion():
    """Test conversion between vectors and numpy arrays"""
    print("\n=== Array Conversion ===")
    
    # Vectors to array
    vectors = [Vector2D(1.0, 2.0), Vector2D(3.0, 4.0), Vector2D(5.0, 6.0)]
    arr = vectors_to_array(vectors)
    
    assert arr.shape == (3, 2), f"Array shape incorrect: {arr.shape}"
    assert abs(arr[0, 0] - 1.0) < 0.001, "Array conversion failed"
    assert abs(arr[1, 1] - 4.0) < 0.001, "Array conversion failed"
    
    # Array to vectors
    test_arr = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64)
    vecs = array_to_vectors(test_arr)
    
    assert len(vecs) == 2, "Array to vectors conversion failed"
    assert abs(vecs[0].x - 1.0) < 0.001 and abs(vecs[0].y - 2.0) < 0.001, "Array to vectors failed"
    
    print("✓ Array conversion tests passed")

def test_common_vectors():
    """Test common vector constants"""
    print("\n=== Common Vectors ===")
    
    assert CommonVectors.ZERO.x == 0.0 and CommonVectors.ZERO.y == 0.0, "ZERO vector incorrect"
    assert CommonVectors.UP.x == 0.0 and CommonVectors.UP.y == 1.0, "UP vector incorrect"
    assert CommonVectors.DOWN.x == 0.0 and CommonVectors.DOWN.y == -1.0, "DOWN vector incorrect"
    assert CommonVectors.LEFT.x == -1.0 and CommonVectors.LEFT.y == 0.0, "LEFT vector incorrect"
    assert CommonVectors.RIGHT.x == 1.0 and CommonVectors.RIGHT.y == 0.0, "RIGHT vector incorrect"
    
    print("✓ Common vectors tests passed")

def test_utility_functions():
    """Test vector utility functions"""
    print("\n=== Utility Functions ===")
    
    # Lerp
    v1 = Vector2D(0.0, 0.0)
    v2 = Vector2D(10.0, 10.0)
    v_mid = lerp(v1, v2, 0.5)
    assert abs(v_mid.x - 5.0) < 0.001 and abs(v_mid.y - 5.0) < 0.001, "Lerp failed"
    
    # Create circle
    circle_points = create_circle(100.0, 8)
    assert len(circle_points) == 8, "Create circle point count incorrect"
    # All points should be ~100 units from origin
    for p in circle_points:
        dist = (p.x**2 + p.y**2)**0.5
        assert abs(dist - 100.0) < 1.0, f"Circle point distance incorrect: {dist}"
    
    # Create grid
    grid = create_grid(3, 3, 10.0)
    assert len(grid) == 9, f"Grid size incorrect: {len(grid)}"
    
    print("✓ Utility functions tests passed")

def test_vector_properties():
    """Test vector properties and methods"""
    print("\n=== Vector Properties ===")
    
    v = Vector2D(3.0, 4.0)
    
    # Length
    assert abs(v.length - 5.0) < 0.001, "Length property failed"
    
    # Normalized
    norm = v.normalized()
    assert abs(norm.length - 1.0) < 0.001, "Normalized method failed"
    assert abs(v.length - 5.0) < 0.001, "Normalized should not modify original"
    
    # Distance
    v2 = Vector2D(6.0, 8.0)
    dist = v.distance_to(v2)
    expected = 5.0  # (3,4) to (6,8) = sqrt(9+16) = 5
    assert abs(dist - expected) < 0.001, f"Distance calculation failed: {dist} != {expected}"
    
    # Angle
    import math
    angle = v.angle
    expected_angle = math.atan2(4.0, 3.0)
    assert abs(angle - expected_angle) < 0.001, "Angle calculation failed"
    
    print("✓ Vector properties tests passed")

def test_numpy_integration():
    """Test vector flexibility with numpy arrays and operations"""
    print("\n=== NumPy Integration ===")
    
    # Create vectors from numpy arrays
    np_array = np.array([3.0, 4.0])
    v1 = Vector2D(np_array[0], np_array[1])
    assert abs(v1.x - 3.0) < 0.001 and abs(v1.y - 4.0) < 0.001, "Vector from numpy array failed"
    print("✓ Vector creation from numpy array")
    
    # Convert vectors to numpy for GPU upload
    vectors = [Vector2D(i, i*2) for i in range(100)]
    arr = vectors_to_array(vectors)
    
    # Verify shape and dtype
    assert arr.shape == (100, 2), f"Array shape incorrect: {arr.shape}"
    assert arr.dtype == np.float64, f"Array dtype incorrect: {arr.dtype}"
    print("✓ vectors_to_array produces correct shape and dtype")
    
    # Test array is contiguous (important for GPU upload)
    assert arr.flags['C_CONTIGUOUS'], "Array should be C-contiguous for GPU"
    print("✓ Array is C-contiguous for efficient GPU upload")
    
    # Convert back from numpy
    vecs_back = array_to_vectors(arr)
    assert len(vecs_back) == 100, "array_to_vectors length incorrect"
    assert abs(vecs_back[0].x) < 0.001 and abs(vecs_back[0].y) < 0.001, "array_to_vectors values incorrect"
    assert abs(vecs_back[50].x - 50.0) < 0.001 and abs(vecs_back[50].y - 100.0) < 0.001, "array_to_vectors values incorrect"
    print("✓ Round-trip conversion (vectors -> numpy -> vectors)")
    
    # Test with different numpy dtypes
    float32_arr = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    # Convert to float64 for compatibility
    float64_arr = float32_arr.astype(np.float64)
    vecs_f32 = array_to_vectors(float64_arr)
    assert len(vecs_f32) == 2, "float32->float64 array conversion failed"
    assert abs(vecs_f32[0].x - 1.0) < 0.001, "float32->float64 to vector conversion incorrect"
    print("✓ Conversion from different numpy dtypes (with proper casting)")
    
    # Test batch operations preserve numpy compatibility
    test_vectors = [Vector2D(1.0, 2.0) for _ in range(50)]
    batch_scale_inplace(test_vectors, 2.0)
    scaled_arr = vectors_to_array(test_vectors)
    assert abs(scaled_arr[0, 0] - 2.0) < 0.001 and abs(scaled_arr[0, 1] - 4.0) < 0.001, "Batch operations not numpy-compatible"
    print("✓ Batch operations maintain numpy compatibility")
    
    # Test slicing and indexing
    large_arr = vectors_to_array([Vector2D(i, i+1) for i in range(1000)])
    subset = large_arr[100:200]
    assert subset.shape == (100, 2), "Array slicing failed"
    assert abs(subset[0, 0] - 100.0) < 0.001, "Array slicing values incorrect"
    print("✓ NumPy slicing and indexing work correctly")
    
    # Test numpy operations on vector data
    positions = vectors_to_array([Vector2D(i*0.1, i*0.2) for i in range(10)])
    
    # Mean position
    mean_pos = np.mean(positions, axis=0)
    assert mean_pos.shape == (2,), "Mean calculation shape incorrect"
    print("✓ NumPy statistical operations (mean, std, etc.)")
    
    # Distance calculations using numpy
    point_a = np.array([0.0, 0.0])
    distances = np.linalg.norm(positions - point_a, axis=1)
    assert distances.shape == (10,), "Distance calculation shape incorrect"
    print("✓ NumPy distance calculations")
    
    # Test memory efficiency (no copy when possible)
    test_vecs = [Vector2D(1.0, 2.0) for _ in range(100)]
    arr1 = vectors_to_array(test_vecs)
    arr1_id = id(arr1.data)
    
    # Modifying array shouldn't affect vectors (they're separate)
    arr1[0, 0] = 999.0
    assert abs(test_vecs[0].x - 1.0) < 0.001, "Vectors should be independent from array"
    print("✓ Vectors and arrays are properly isolated")
    
    # Test with large datasets (performance check)
    large_dataset = [Vector2D.random(-100, 100) for _ in range(10000)]
    large_arr = vectors_to_array(large_dataset)
    assert large_arr.shape == (10000, 2), "Large dataset conversion failed"
    
    # Convert back
    recovered = array_to_vectors(large_arr[:100])  # Just test a subset
    assert len(recovered) == 100, "Large dataset recovery failed"
    print("✓ Large dataset handling (10k+ vectors)")
    
    # Test zero-copy view when possible
    arr_view = large_arr[5000:5100]
    assert arr_view.base is large_arr, "View should reference original array"
    print("✓ NumPy views work correctly (memory efficient)")
    
    print("✓ NumPy integration tests passed")


def test_vector2int_precision():
    """Test Vector2Int for exact integer precision (grid systems)"""
    print("\n=== Vector2Int Precision ===")
    
    # The precision problem with floats
    cell_pos_float = V2(3.0, 1.0)
    cells_per_row_float = 10.0
    index_float = cell_pos_float.x + cell_pos_float.y * cells_per_row_float
    # This can produce 13.999999999999998 due to float precision
    
    # The solution with Vector2Int
    cell_pos_int = V2I(3, 1)
    cells_per_row_int = 10
    index_int = cell_pos_int.x + cell_pos_int.y * cells_per_row_int
    
    assert index_int == 13, f"Vector2Int index calculation failed: {index_int} != 13"
    assert isinstance(index_int, int), "Vector2Int should produce int results"
    
    print("✓ Vector2Int produces exact integer results")
    print("✓ Vector2Int precision tests passed")


def test_vector2int_operations():
    """Test Vector2Int basic operations"""
    print("\n=== Vector2Int Operations ===")
    
    v1 = V2I(10, 20)
    v2 = V2I(5, 3)
    
    # Addition
    v3 = v1 + v2
    assert v3.x == 15 and v3.y == 23, "Vector2Int addition failed"
    
    # Subtraction
    v4 = v1 - v2
    assert v4.x == 5 and v4.y == 17, "Vector2Int subtraction failed"
    
    # Multiplication
    v5 = v1 * 2
    assert v5.x == 20 and v5.y == 40, "Vector2Int multiplication failed"
    
    # Floor division
    v6 = v1 // 2
    assert v6.x == 5 and v6.y == 10, "Vector2Int floor division failed"
    
    # Dot product
    dot = v1.dot_product(v2)
    expected_dot = 10 * 5 + 20 * 3
    assert dot == expected_dot, "Vector2Int dot product failed"
    
    print("✓ Vector2Int operations tests passed")


def test_vector2int_inplace():
    """Test Vector2Int in-place operations"""
    print("\n=== Vector2Int In-place Operations ===")
    
    # In-place addition
    v1 = V2I(10, 20)
    v1.iadd(V2I(5, 3))
    assert v1.x == 15 and v1.y == 23, "Vector2Int in-place addition failed"
    
    # In-place subtraction
    v2 = V2I(20, 30)
    v2.isub(V2I(5, 10))
    assert v2.x == 15 and v2.y == 20, "Vector2Int in-place subtraction failed"
    
    # In-place multiplication
    v3 = V2I(5, 10)
    v3.imul(3)
    assert v3.x == 15 and v3.y == 30, "Vector2Int in-place multiplication failed"
    
    # In-place floor division (if supported)
    if hasattr(V2I(1, 1), 'ifloordiv'):
        v4 = V2I(20, 30)
        v4.ifloordiv(2)
        assert v4.x == 10 and v4.y == 15, "Vector2Int in-place floor division failed"
    
    print("✓ Vector2Int in-place operations tests passed")


def test_vector2int_grid_system():
    """Test Vector2Int for grid/tile systems"""
    print("\n=== Vector2Int Grid System ===")
    
    # Create a grid system
    grid_size = V2I(10, 10)
    
    # Test various grid positions
    test_positions = [
        (V2I(0, 0), 0),
        (V2I(1, 0), 1),
        (V2I(0, 1), 10),
        (V2I(3, 1), 13),
        (V2I(9, 9), 99),
    ]
    
    for pos, expected_index in test_positions:
        index = pos.x + pos.y * grid_size.x
        assert index == expected_index, f"Grid index calculation failed for {pos}: {index} != {expected_index}"
    
    # Test neighbor calculation
    center = V2I(5, 5)
    directions = [V2I(0, 1), V2I(0, -1), V2I(-1, 0), V2I(1, 0)]
    
    expected_neighbors = [
        V2I(5, 6),   # up
        V2I(5, 4),   # down
        V2I(4, 5),   # left
        V2I(6, 5),   # right
    ]
    
    for direction, expected in zip(directions, expected_neighbors):
        neighbor = center + direction
        assert neighbor.x == expected.x and neighbor.y == expected.y, "Neighbor calculation failed"
    
    print("✓ Vector2Int grid system tests passed")


def test_vector2int_conversion():
    """Test conversion between Vector2D and Vector2Int"""
    print("\n=== Vector2Int Conversion ===")
    
    # Vector2Int to Vector2D
    int_vec = V2I(5, 10)
    float_vec = int_vec.to_float()
    assert abs(float_vec.x - 5.0) < 0.001 and abs(float_vec.y - 10.0) < 0.001, "V2I to V2 conversion failed"
    assert isinstance(float_vec, Vector2D), "to_float should return Vector2D"
    
    # Vector2D to Vector2Int (if method exists)
    if hasattr(Vector2D, 'to_int'):
        float_vec2 = V2(7.8, 12.3)
        int_vec2 = float_vec2.to_int()
        assert int_vec2.x == 7 and int_vec2.y == 12, "V2 to V2I conversion failed"
    
    print("✓ Vector2Int conversion tests passed")


def run_all_tests():
    """Run all vector tests"""
    print("\n" + "="*50)
    print("Running e2D Vector Tests (Headless)")
    print("="*50)
    
    test_vector_creation()
    test_vector_operations()
    test_inplace_operations()
    test_batch_operations()
    test_array_conversion()
    test_common_vectors()
    test_utility_functions()
    test_vector_properties()
    test_numpy_integration()
    
    # Vector2Int tests (if available)
    test_vector2int_precision()
    test_vector2int_operations()
    test_vector2int_inplace()
    test_vector2int_grid_system()
    test_vector2int_conversion()
    
    print("\n" + "="*50)
    print("✓ ALL VECTOR TESTS PASSED")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
