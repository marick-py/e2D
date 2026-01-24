# e2D - High-Performance 2D Graphics and Math Library

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-beta-orange.svg)

**e2D** combines ultra-optimized vector mathematics with modern OpenGL rendering for high-performance 2D applications. Perfect for games, simulations, and real-time graphics.

## ✨ Features

### 🚀 Optimized Vector Operations
- **Cython-compiled** Vector2D class (10-500x faster than pure Python)
- **Batch operations** for processing thousands of vectors efficiently
- **Direct memory access** with zero-copy operations
- **NumPy integration** for seamless GPU data upload

### 🎮 Modern Graphics
- **ModernGL** rendering pipeline
- **Shape rendering** with instancing support
- **Text rendering** with custom styles
- **GLFW window management**

### 🎯 Game Development Tools
- **Keyboard and mouse input** handling
- **Collision detection**
- **Color manipulation**
- **Vector mathematics**

## 📦 Installation

```bash
pip install e2D
```

The package will automatically compile the Cython extensions during installation for optimal performance (like numpy). If compilation fails, it falls back to pure Python mode.

### Requirements
- Python 3.9+
- NumPy
- ModernGL
- GLFW
- Pygame

## 🚀 Quick Start

### Optimized Vector Operations

```python
from e2D import Vector2D, batch_add_inplace, vectors_to_array

# Create vectors
v1 = Vector2D(3.0, 4.0)
v2 = Vector2D(1.0, 2.0)

# Basic operations
v3 = v1 + v2
length = v1.length
dot = v1.dot_product(v2)

# In-place operations (faster!)
v1.iadd(v2)
v1.normalize()
v1.irotate(0.1)

# Process thousands of vectors instantly
positions = [Vector2D.random(-10, 10) for _ in range(10000)]
displacement = Vector2D(1.0, 0.5)
batch_add_inplace(positions, displacement)  # 🚀 Lightning fast!

# Convert to numpy for GPU upload
pos_array = vectors_to_array(positions)
```

### Graphics Rendering

```python
from e2D import RootEnv

class MyApp(RootEnv):
    def __init__(self):
        super().__init__(
            window_size=(1920, 1080),
            target_fps=60,
            vsync=True
        )
    
    def update(self):
        # Your game logic here
        pass
    
    def draw(self):
        # Your rendering code here
        pass

app = MyApp()
app.run()
```

## 📊 Performance

Vector2D benchmark (100,000 operations):

| Operation | Time | vs Pure Python |
|-----------|------|----------------|
| Creation | 42 ms | 10x faster |
| Addition | 64 ms | 15x faster |
| In-place ops | 3.8 ms | **100x faster** |
| Normalization | 1.9 ms | **200x faster** |
| Batch operations | 0.17 ms | **500x+ faster** 🔥 |

Perfect for:
- Particle systems (10,000+ particles)
- Physics simulations
- Collision detection
- Path finding
- Real-time graphics

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in minutes
- **[API Reference](https://github.com/marick-py/e2D)** - Full API documentation
- **[Examples](examples/)** - Working code examples

## 🎯 Use Cases

### Particle System
```python
from e2D import Vector2D, batch_add_inplace, vectors_to_array

positions = [Vector2D.random(-10, 10) for _ in range(10000)]
velocities = [Vector2D.random(-1, 1) for _ in range(10000)]

def update(dt):
    # Update all particles in milliseconds
    for i in range(len(positions)):
        temp = velocities[i].mul(dt)
        positions[i].iadd(temp)

def render():
    # Upload to GPU
    pos_array = vectors_to_array(positions).astype(np.float32)
    vbo.write(pos_array)
```

### Physics Simulation
```python
from e2D import Vector2D

class RigidBody:
    def __init__(self, pos, vel):
        self.position = Vector2D(*pos)
        self.velocity = Vector2D(*vel)
        self.acceleration = Vector2D(0, -9.8)
    
    def update(self, dt):
        # Optimized in-place physics
        temp = self.acceleration.mul(dt)
        self.velocity.iadd(temp)
        
        temp = self.velocity.mul(dt)
        self.position.iadd(temp)
```

## 🔧 Development

### Building from Source

```bash
git clone https://github.com/marick-py/e2D.git
cd e2D
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Building Distribution

```bash
python -m build
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Riccardo Mariani**
- Email: ricomari2006@gmail.com
- GitHub: [@marick-py](https://github.com/marick-py)

## 🙏 Acknowledgments

- Built with [ModernGL](https://github.com/moderngl/moderngl)
- Optimized with [Cython](https://cython.org/)
- Inspired by the need for high-performance 2D mathematics in Python

## 📈 Version History

- **2.0.0** - Added ultra-optimized Vector2D with Cython compilation
- **1.4.24** - Previous stable release with pure Python vectors

---

**Made with ❤️ for high-performance 2D development**


