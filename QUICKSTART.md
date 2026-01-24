# Vector2D - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Build the Extension

**Windows:**
```bash
build.bat
```

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

### Step 2: Test It Works

```bash
python -m e2D.vectors
```

You should see benchmark results like:
```
Vector2D Benchmark (100000 iterations)
==================================================
Creation:      15.23 ms
Addition:      18.45 ms
In-place add:  12.67 ms
Normalize:     45.12 ms
Batch add:     2.34 ms
==================================================
✓ Using compiled Cython extension (optimal performance)
```

### Step 3: Use in Your Code

```python
from e2D.vectors import Vector2D, V2

# Create a vector
position = Vector2D(100.0, 200.0)
velocity = V2(5.0, -2.0)

# Update position
position += velocity * 0.016  # ~60 FPS

print(f"New position: {position}")
```

## 📚 Next Steps

- Check out [example_usage.py](example_usage.py) for more examples
- Integrate with your ModernGL/GLFW project

## ⚡ Performance Tips

1. **Use in-place operations** for maximum speed:
   ```python
   v.iadd(other)  # Faster than v += other
   v.imul(2.0)    # Faster than v *= 2.0
   ```

2. **Use batch operations** for many vectors:
   ```python
   from e2D.vectors import batch_add_inplace
   batch_add_inplace(vectors, displacement)  # MUCH faster
   ```

3. **Avoid Python loops** when possible:
   ```python
   # Slow
   for v in vectors:
       v.normalize()
   
   # Fast
   batch_normalize_inplace(vectors)
   ```

## 🔧 Troubleshooting

**"ImportError: No module named 'cvectors'"**
- Run the build script again: `build.bat` or `./build.sh`

**"ERROR: Microsoft Visual C++ 14.0 is required" (Windows)**
- Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

**Build errors on Linux/Mac**
- Install build tools:
  - Ubuntu/Debian: `sudo apt-get install build-essential python3-dev`
  - CentOS/RHEL: `sudo yum install gcc gcc-c++ python3-devel`
  - Mac: `xcode-select --install`

## 📦 For Distribution

To prepare for PyPI upload:

```bash
# Install build tools
pip install build twine

# Build distributions
python -m build

# Test upload (optional)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## 💡 Integration Example

```python
from e2D.vectors import Vector2D, vectors_to_array
import moderngl
import numpy as np

# Create particle system
positions = [Vector2D.random(-10, 10) for _ in range(10000)]
velocities = [Vector2D.random(-1, 1) for _ in range(10000)]

# Update loop (optimized)
def update(dt):
    for i in range(len(positions)):
        temp = velocities[i].mul(dt)
        positions[i].iadd(temp)

# Upload to GPU
def get_gpu_buffer():
    pos_array = vectors_to_array(positions).astype(np.float32)
    return pos_array

# Use with ModernGL
# vbo.write(get_gpu_buffer())
```

## 📈 Expected Performance

For a typical simulation with 100,000 vectors:

| Operation | Pure Python | Vector2D | Speedup |
|-----------|-------------|--------------|---------|
| Creation | ~500 ms | ~15 ms | **33x** |
| Addition | ~800 ms | ~20 ms | **40x** |
| Normalize | ~2000 ms | ~45 ms | **44x** |
| Batch ops | ~1000 ms | ~2 ms | **500x** |

## 🎯 Use Cases

Perfect for:
- Particle systems (10,000+ particles)
- Physics simulations
- Collision detection
- Path finding
- Procedural generation
- Game engines
- Scientific computing

## 📝 License

MIT License - Use freely in your projects!


