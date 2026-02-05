# e2D Examples

This folder contains interactive visual examples demonstrating various features of the e2D library.

## Available Examples

### Core Features

- **[example_vectors.py](example_vectors.py)** - Vector operations and particle systems
  - Vector2D creation and operations
  - Batch processing for performance
  - Particle system with 500+ particles
  - Vector visualization

- **[example_colors.py](example_colors.py)** - Color system and manipulation
  - Color creation methods (hex, RGB, HSV, etc.)
  - Pre-defined color palettes (Material Design, Pastel, Neon, UI)
  - Color operations (lighten, darken, hue rotation, gradients)
  - Animated colors

- **[example_shapes.py](example_shapes.py)** - Shape rendering
  - Basic shapes (circles, rectangles, lines)
  - Cached shapes for performance
  - Instanced batching (drawing 100+ shapes efficiently)
  - Shape animations

- **[example_text.py](example_text.py)** - Text rendering
  - Basic text rendering
  - Text styles and pivots
  - Custom text styles with backgrounds
  - Cached labels for performance
  - Unicode and emoji support

- **[example_input.py](example_input.py)** - Keyboard and mouse input
  - Keys class with autocompletion
  - MouseButtons class
  - Key states (PRESSED, JUST_PRESSED, JUST_RELEASED)
  - Interactive player movement

- **[example_keys.py](example_keys.py)** - Keys class demonstration
  - Clean autocompletion for key names
  - WASD movement example
  - Number key detection
  - Key state management

## Running Examples

Each example is a standalone Python file. Run them directly:

```bash
# From the examples directory
python example_vectors.py
python example_colors.py
python example_shapes.py
python example_text.py
python example_input.py
python example_keys.py
```

Or from anywhere:

```bash
python -m examples.example_vectors
python -m examples.example_colors
# etc...
```

## Requirements

All examples require:
- Python 3.10+
- e2D library installed (`pip install e2D`)
- A display (examples create windows)

## Getting Started Template

Want to start your own project? Use the default template:

```bash
# Copy the default template
cp e2D.default my_app.py

# Edit my_app.py with your code

# Run it
python my_app.py
```

Or start from scratch:

```python
from e2D import RootEnv, DefEnv, V2, Keys, KeyState

class MyApp(DefEnv):
    def __init__(self, root: RootEnv):
        self.root = root
    
    def update(self):
        # Your game logic here
        if self.root.keyboard.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
            import glfw
            glfw.set_window_should_close(self.root.window, True)
    
    def draw(self):
        # Your rendering here
        self.root.draw_circle(V2(400, 300), 50, color=(1, 0, 0, 1))

root = RootEnv(window_size=V2(800, 600), target_fps=60)
root.init(MyApp(root))
root.loop()
```

## Documentation

For detailed guides, see the [docs](../docs) folder:

- [Vector Operations Guide](../docs/VECTORS.md)
- [Color System Guide](../docs/COLORS.md)
- [Shape Rendering Guide](../docs/SHAPES.md)
- [Text Rendering Guide](../docs/TEXT.md)
- [Input Handling Guide](../docs/INPUT.md)
- [API Reference](../docs/API_REFERENCE.md)

## Contributing

Found a bug or have an idea for a new example? Contributions are welcome!

1. Fork the repository
2. Create your feature branch
3. Add your example with clear comments
4. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) for details
