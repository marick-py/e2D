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
- **Text rendering** with custom styles and TTF fonts
- **Screen recording** with async video encoding
- **Color system** with 80+ pre-defined colors
- **GLFW window management**

### 🎯 Game Development Tools
- **Keyboard and mouse input** handling
- **Collision detection**
- **Color manipulation**
- **Vector mathematics**

## 📦 Installation

### Basic Installation

```bash
pip install e2D
```

The package will automatically compile the Cython extensions during installation for optimal performance (like numpy). If compilation fails, it falls back to pure Python mode.

### Optional Features

Install with screen recording support:
```bash
pip install e2D[rec]
```

Install for development (includes testing tools):
```bash
pip install e2D[dev]
```

Install with performance monitoring (includes Cython source):
```bash
pip install e2D[performance]
```

Install everything:
```bash
pip install e2D[all]
```

### Legacy Version (1.x with Pygame)

If you need the old pygame-based version:
```bash
pip install "e2D<2.0"
```

### Requirements
- Python 3.9+
- NumPy (required)
- ModernGL (required)
- GLFW (required)
- Pillow (required - for text rendering)
- attrs (required - for data structures)
- OpenCV-Python (optional, for recording - install with `[rec]` extra)

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
from e2D import RootEnv, DefEnv

class MyApp(DefEnv):
    def __init__(self) -> None:
        pass
    
    def update(self) -> None:
        # Your game logic here
        pass
    
    def draw(self) -> None:
        # Your rendering code here
        pass

# Initialize and run
rootEnv = RootEnv(window_size=(1920, 1080), target_fps=60)
rootEnv.init(MyApp())

# Optional: Enable screen recording
rootEnv.init_rec(fps=30, draw_on_screen=True, path='output.mp4')

rootEnv.loop()
```

### Color System

```python
from e2D import Color, WHITE, RED, CYAN, normalize_color
from e2D.color_defs import MD_BLUE, PASTEL_PINK, NEON_GREEN

# Create colors
color1 = Color.from_hex("#FF5733")
color2 = Color.from_rgb255(100, 150, 200)
color3 = Color.from_hsv(0.5, 0.8, 1.0)

# Color operations
lighter = color1.lighten(0.2)
darker = color1.darken(0.2)
inverted = color1.invert()
rotated = color1.rotate_hue(120)

# Use pre-defined colors
from e2D import draw_circle
draw_circle((100, 100), 50, color=RED, fill_mode='fill')
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

### Getting Started
- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in minutes
- **[Developer Guide](DEVELOPER_GUIDE.md)** - In-depth development guide
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Understanding the codebase

### Core Features
- **[Engine Architecture](docs/ENGINE.md)** - RootEnv, DefEnv, main loop, input handling
- **[Vector Mathematics](docs/VECTORS.md)** - High-performance Vector2D operations, batch processing, GPU integration
- **[Shape Rendering](docs/SHAPES.md)** - GPU-accelerated circles, rectangles, lines with instancing
- **[Text Rendering](docs/TEXT.md)** - Fast GPU text with caching and custom fonts
- **[Color System](docs/COLORS.md)** - 80+ pre-defined colors, color operations, gradients
- **[GPU Plotting](docs/PLOTS.md)** - Real-time mathematical visualization with compute shaders
- **[Screen Recording](docs/RECORDING.md)** - Async video encoding (optional, requires opencv-python)

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

### Version 2.x (ModernGL-based - Current)
- **2.0.1** (Current) - Bug fixes and documentation improvements
- **2.0.0** - Complete rewrite with ModernGL rendering, Cython-optimized vectors, modern color system, screen recording, removed pygame dependency

### Version 1.x (Pygame-based - Legacy)
- **1.4.24** - Previous stable release with pure Python vectors and pygame
- Legacy versions available via: `pip install "e2D<2.0"`

---

**Made with ❤️ for high-performance 2D development**


