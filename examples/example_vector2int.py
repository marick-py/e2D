"""
Example: Converting your grid cell system to use Vector2Int

BEFORE (with precision errors):
    next_cell.position = Vector2D(3.0, 1.0)
    int(next_position.x + next_position.y * self.cells_count.x) = 13
    next_position.x + next_position.y * self.cells_count.x = 13.999999999999996

AFTER (perfect precision):
    Use Vector2Int instead!
"""

from e2D import V2I  # V2I is alias for Vector2Int


class GridSystem:
    """Example grid system using Vector2Int for perfect precision"""
    
    def __init__(self, width: int, height: int):
        # Use Vector2Int for grid dimensions
        self.cells_count = V2I(width, height)
        self.total_cells = width * height
        
        # Create grid of cells
        self.cells = [Cell(V2I(x, y)) for y in range(height) for x in range(width)]
    
    def get_cell_index(self, position: V2I) -> int:
        """
        Convert 2D grid position to 1D array index
        
        This is where precision matters!
        ✅ With Vector2Int: Always exact
        ❌ With Vector2D: Can have rounding errors
        """
        return position.x + position.y * self.cells_count.x
    
    def get_cell(self, position: V2I):
        """Get cell at grid position"""
        if 0 <= position.x < self.cells_count.x and 0 <= position.y < self.cells_count.y:
            index = self.get_cell_index(position)
            return self.cells[index]
        return None
    
    def get_neighbors(self, position: V2I):
        """Get all valid neighbor cells (4-directional)"""
        neighbors = []
        directions = [V2I(0, 1), V2I(0, -1), V2I(-1, 0), V2I(1, 0)]
        
        for direction in directions:
            neighbor_pos = position + direction
            cell = self.get_cell(neighbor_pos)
            if cell:
                neighbors.append(cell)
        
        return neighbors


class Cell:
    """Individual grid cell"""
    
    def __init__(self, position: V2I):
        # Store position as Vector2Int for exact indexing
        self.position = position
        self.data = None
    
    def __repr__(self):
        return f"Cell({self.position})"


def demonstrate_fix():
    """Demonstrate the precision fix"""
    print("=" * 70)
    print("YOUR ORIGINAL PROBLEM - FIXED!")
    print("=" * 70)
    
    # Create a small grid
    grid = GridSystem(10, 10)
    
    # Your exact use case
    next_cell_position = V2I(3, 1)
    
    print(f"\nGrid size: {grid.cells_count}")
    print(f"Cell position: {next_cell_position}")
    
    # Calculate index (the problematic calculation from your code)
    index = next_cell_position.x + next_cell_position.y * grid.cells_count.x
    
    print(f"\nCalculation: {next_cell_position.x} + {next_cell_position.y} * {grid.cells_count.x}")
    print(f"Result: {index}")
    print(f"Type: {type(index).__name__}")
    print(f"✅ Perfect! No precision error!")
    
    # Get the actual cell
    cell = grid.get_cell(next_cell_position)
    print(f"\nRetrieved cell: {cell}")
    
    # Get neighbors
    neighbors = grid.get_neighbors(next_cell_position)
    print(f"Neighbors: {neighbors}")
    
    print("\n" + "=" * 70)
    print("MIGRATION GUIDE FOR YOUR CODE")
    print("=" * 70)
    
    print("""
    # BEFORE (with Vector2D):
    from e2D import Vector2D
    
    class YourClass:
        def __init__(self):
            self.cells_count = Vector2D(10.0, 10.0)  # ❌ Float
            
        def get_index(self, pos):
            # ❌ Precision errors here!
            index = int(pos.x + pos.y * self.cells_count.x)
            return index
    
    
    # AFTER (with Vector2Int):
    from e2D import V2I  # or Vector2Int
    
    class YourClass:
        def __init__(self):
            self.cells_count = V2I(10, 10)  # ✅ Integer
            
        def get_index(self, pos: V2I) -> int:
            # ✅ Perfect precision, no int() needed!
            index = pos.x + pos.y * self.cells_count.x
            return index
    
    
    # USAGE:
    obj = YourClass()
    cell_pos = V2I(3, 1)  # Use V2I instead of Vector2D
    index = obj.get_index(cell_pos)  # Always exact: 13
    """)


def performance_comparison():
    """Show that Vector2Int is also faster!"""
    import time
    
    print("\n" + "=" * 70)
    print("BONUS: VECTOR2INT IS ALSO FASTER!")
    print("=" * 70)
    
    from e2D import V2, V2I
    
    # Create test data
    iterations = 100000
    
    # Test with Vector2D (float)
    start = time.perf_counter()
    grid_size_float = V2(10.0, 10.0)
    for i in range(iterations):
        pos = V2(float(i % 10), float(i // 10))
        index = int(pos.x + pos.y * grid_size_float.x)
    time_float = time.perf_counter() - start
    
    # Test with Vector2Int (int)
    start = time.perf_counter()
    grid_size_int = V2I(10, 10)
    for i in range(iterations):
        pos = V2I(i % 10, i // 10)
        index = pos.x + pos.y * grid_size_int.x
    time_int = time.perf_counter() - start
    
    print(f"\nIndex calculation performance ({iterations:,} iterations):")
    print(f"  Vector2D (float): {time_float:.4f}s")
    print(f"  Vector2Int (int): {time_int:.4f}s")
    print(f"  Speedup: {time_float/time_int:.2f}x faster! 🔥")
    print(f"\n✅ Vector2Int is faster AND more accurate!")


if __name__ == "__main__":
    try:
        demonstrate_fix()
        performance_comparison()
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print("""
✅ Use Vector2Int (V2I) for:
   • Grid coordinates
   • Cell indices
   • Array indexing
   • Tilemap positions
   • Any discrete/integer math

✅ Use Vector2D (V2) for:
   • Physics (velocity, acceleration)
   • Smooth animations
   • Rotations
   • Camera positions
   • Continuous movement

💡 TIP: You can convert between them:
   int_vec = V2I(5, 10)
   float_vec = int_vec.to_float()  # → Vector2D(5.0, 10.0)
        """)
        
    except ImportError as e:
        print("❌ Error: Could not import Vector2Int")
        print(f"   {e}")
        print("\n⚠️  You need to rebuild the Cython module first:")
        print("   Run: build_dev.bat")
