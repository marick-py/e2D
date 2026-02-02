# GPU Plotting - Real-Time Mathematical Visualization

GPU-accelerated plotting with compute shaders for interactive mathematical visualizations.

## Features

- ✅ **GPU-computed** plots using compute shaders
- ✅ **Real-time** plotting of complex functions
- ✅ **Interactive** zoom and pan
- ✅ **Implicit functions** (f(x,y) = 0)
- ✅ **Parametric curves** support
- ✅ **Stream plots** for vector fields
- ✅ **Grid overlay** with axis labels

## Quick Start

### Basic Function Plot

```python
from e2D import RootEnv, Plot2D
import numpy as np

class PlotDemo(DefEnv):
    def __init__(self):
        # Create plot area
        self.plot = Plot2D(
            position=(100, 100),
            size=(800, 600),
            x_range=(-10, 10),
            y_range=(-10, 10)
        )
        
        # Plot y = sin(x)
        x = np.linspace(-10, 10, 1000)
        y = np.sin(x)
        self.plot.add_curve(x, y, color=(1.0, 0.0, 0.0, 1.0))
    
    def draw(self):
        self.plot.draw()
```

## Plot Types

### 1. Explicit Functions - y = f(x)

```python
class ExplicitPlot(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(1200, 800),
            x_range=(-5, 5),
            y_range=(-5, 5),
            show_grid=True,
            show_axes=True
        )
        
        # Multiple curves
        x = np.linspace(-5, 5, 1000)
        
        # y = x^2
        self.plot.add_curve(x, x**2, color=Color.RED.to_rgba(), label="x²")
        
        # y = sin(x)
        self.plot.add_curve(x, np.sin(x), color=Color.BLUE.to_rgba(), label="sin(x)")
        
        # y = e^(-x^2) (Gaussian)
        self.plot.add_curve(x, np.exp(-x**2), color=Color.GREEN.to_rgba(), label="e^(-x²)")
    
    def draw(self):
        self.plot.draw()
```

### 2. Parametric Curves

```python
class ParametricPlot(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(800, 800),
            x_range=(-2, 2),
            y_range=(-2, 2)
        )
        
        # Circle: x = cos(t), y = sin(t)
        t = np.linspace(0, 2*np.pi, 500)
        x = np.cos(t)
        y = np.sin(t)
        self.plot.add_parametric_curve(x, y, color=Color.CYAN.to_rgba())
        
        # Lissajous curve
        t = np.linspace(0, 2*np.pi, 1000)
        x = np.sin(3*t)
        y = np.sin(2*t)
        self.plot.add_parametric_curve(x, y, color=Color.MAGENTA.to_rgba())
    
    def draw(self):
        self.plot.draw()
```

### 3. Implicit Functions - f(x,y) = 0

GPU-computed implicit function plotting (runs on GPU via compute shader):

```python
class ImplicitPlot(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(800, 800),
            x_range=(-3, 3),
            y_range=(-3, 3)
        )
        
        # Circle: x^2 + y^2 - 1 = 0
        def circle(x, y):
            return x**2 + y**2 - 1.0
        
        self.plot.add_implicit_function(
            circle,
            resolution=512,  # GPU grid resolution
            color=Color.RED.to_rgba(),
            threshold=0.05   # Distance tolerance
        )
        
        # Heart curve: (x^2 + y^2 - 1)^3 - x^2*y^3 = 0
        def heart(x, y):
            return (x**2 + y**2 - 1)**3 - x**2 * y**3
        
        self.plot.add_implicit_function(
            heart,
            resolution=1024,
            color=Color.PINK.to_rgba()
        )
    
    def draw(self):
        self.plot.draw()
```

### 4. Vector Fields & Stream Plots

```python
class StreamPlot(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(800, 800),
            x_range=(-3, 3),
            y_range=(-3, 3)
        )
        
        # Define vector field: dx/dt = -y, dy/dt = x (rotation)
        def vector_field(x, y):
            return -y, x
        
        # Add stream plot
        self.plot.add_stream_plot(
            vector_field,
            resolution=50,  # Grid density
            color=Color.CYAN.to_rgba(),
            arrow_size=0.1
        )
    
    def draw(self):
        self.plot.draw()
```

## Interactive Features

### Zoom and Pan

```python
class InteractivePlot(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(1200, 800),
            x_range=(-10, 10),
            y_range=(-10, 10)
        )
        
        # Plot function
        x = np.linspace(-10, 10, 1000)
        y = np.sin(x) * np.exp(-x**2/20)
        self.plot.add_curve(x, y, color=Color.GREEN.to_rgba())
    
    def update(self):
        # Zoom with mouse wheel
        if rootEnv.mouse_scroll != 0:
            zoom_factor = 1.1 if rootEnv.mouse_scroll > 0 else 0.9
            self.plot.zoom(zoom_factor)
        
        # Pan with arrow keys
        pan_speed = 0.5
        if rootEnv.is_key_pressed(glfw.KEY_LEFT):
            self.plot.pan(-pan_speed, 0)
        if rootEnv.is_key_pressed(glfw.KEY_RIGHT):
            self.plot.pan(pan_speed, 0)
        if rootEnv.is_key_pressed(glfw.KEY_UP):
            self.plot.pan(0, pan_speed)
        if rootEnv.is_key_pressed(glfw.KEY_DOWN):
            self.plot.pan(0, -pan_speed)
    
    def draw(self):
        self.plot.draw()
```

### Animated Plots

```python
class AnimatedPlot(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(1200, 800),
            x_range=(0, 10),
            y_range=(-2, 2)
        )
        
        self.time = 0.0
        self.x = np.linspace(0, 10, 500)
    
    def update(self):
        self.time += rootEnv.delta
        
        # Clear previous curves
        self.plot.clear_curves()
        
        # Animate: y = sin(x - t)
        y = np.sin(self.x - self.time)
        self.plot.add_curve(self.x, y, color=Color.BLUE.to_rgba())
    
    def draw(self):
        self.plot.draw()
```

## Advanced Examples

### Phase Portrait

```python
class PhasePortrait(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(800, 800),
            x_range=(-3, 3),
            y_range=(-3, 3),
            show_grid=True
        )
        
        # Pendulum dynamics: dx/dt = y, dy/dt = -sin(x)
        def pendulum(x, y):
            return y, -np.sin(x)
        
        # Stream plot
        self.plot.add_stream_plot(
            pendulum,
            resolution=30,
            color=Color.CYAN.to_rgba()
        )
        
        # Add separatrix (unstable equilibrium)
        # Manually plot some trajectories
        for y0 in np.linspace(-2, 2, 10):
            t = np.linspace(0, 10, 500)
            # Solve ODE numerically (simplified)
            x = t  # Placeholder - use scipy.integrate.odeint in practice
            y = y0 * np.exp(-0.1*t)
            self.plot.add_parametric_curve(x, y, color=Color.YELLOW.to_rgba())
    
    def draw(self):
        self.plot.draw()
```

### Complex Function Visualization

```python
class ComplexPlot(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(800, 800),
            x_range=(-2, 2),
            y_range=(-2, 2)
        )
        
        # Plot |f(z)| = c for complex function f(z) = z^2
        for c in np.linspace(0.1, 2, 10):
            def level_curve(x, y):
                z = x + 1j*y
                return abs(z**2) - c
            
            hue = c / 2.0  # Color by level
            color = Color.from_hsv(hue, 1.0, 1.0).to_rgba()
            
            self.plot.add_implicit_function(
                level_curve,
                resolution=512,
                color=color,
                threshold=0.05
            )
    
    def draw(self):
        self.plot.draw()
```

### Real-Time Data Plotting

```python
class RealtimeDataPlot(DefEnv):
    def __init__(self):
        self.plot = Plot2D(
            position=(100, 100),
            size=(1200, 600),
            x_range=(0, 100),
            y_range=(-1, 1)
        )
        
        self.data_buffer = []
        self.max_points = 1000
    
    def update(self):
        # Simulate incoming data (e.g., from sensor)
        new_value = np.sin(rootEnv.time * 2.0) + np.random.normal(0, 0.1)
        self.data_buffer.append(new_value)
        
        # Keep buffer size limited
        if len(self.data_buffer) > self.max_points:
            self.data_buffer.pop(0)
        
        # Update plot
        self.plot.clear_curves()
        x = np.arange(len(self.data_buffer))
        y = np.array(self.data_buffer)
        self.plot.add_curve(x, y, color=Color.GREEN.to_rgba())
    
    def draw(self):
        self.plot.draw()
```

### Multi-Plot Dashboard

```python
class Dashboard(DefEnv):
    def __init__(self):
        # Create 4 plots in 2x2 grid
        self.plots = []
        
        for i in range(2):
            for j in range(2):
                plot = Plot2D(
                    position=(100 + j*620, 100 + i*420),
                    size=(600, 400),
                    x_range=(-5, 5),
                    y_range=(-2, 2),
                    show_grid=True
                )
                self.plots.append(plot)
        
        # Plot different functions
        x = np.linspace(-5, 5, 500)
        
        self.plots[0].add_curve(x, np.sin(x), color=Color.RED.to_rgba())
        self.plots[1].add_curve(x, np.cos(x), color=Color.BLUE.to_rgba())
        self.plots[2].add_curve(x, np.exp(-x**2), color=Color.GREEN.to_rgba())
        self.plots[3].add_curve(x, np.tanh(x), color=Color.YELLOW.to_rgba())
    
    def draw(self):
        for plot in self.plots:
            plot.draw()
```

## Plot2D API Reference

### Constructor

```python
plot = Plot2D(
    position: tuple[float, float],    # (x, y) in screen space
    size: tuple[float, float],        # (width, height) in pixels
    x_range: tuple[float, float] = (-10, 10),
    y_range: tuple[float, float] = (-10, 10),
    show_grid: bool = True,
    show_axes: bool = True,
    grid_color: tuple = (0.3, 0.3, 0.3, 1.0),
    axis_color: tuple = (1.0, 1.0, 1.0, 1.0),
    background_color: tuple = (0.1, 0.1, 0.1, 1.0)
)
```

### Methods

```python
# Add curves
plot.add_curve(x, y, color=(1,1,1,1), line_width=2.0, label=None)
plot.add_parametric_curve(x, y, color=(1,1,1,1), line_width=2.0)

# Add GPU-computed plots
plot.add_implicit_function(func, resolution=512, color=(1,1,1,1), threshold=0.05)
plot.add_stream_plot(vector_field, resolution=50, color=(1,1,1,1), arrow_size=0.1)

# Clear
plot.clear_curves()
plot.clear_all()  # Clear everything including implicit functions

# Transform
plot.zoom(factor: float)
plot.pan(dx: float, dy: float)  # In plot coordinates
plot.set_x_range(x_min: float, x_max: float)
plot.set_y_range(y_min: float, y_max: float)
plot.reset_view()

# Draw
plot.draw()

# Query
plot.screen_to_plot(screen_x, screen_y) -> (plot_x, plot_y)
plot.plot_to_screen(plot_x, plot_y) -> (screen_x, screen_y)
```

## Performance Tips

1. **Use GPU functions** - Implicit functions and stream plots run on GPU
2. **Reduce resolution** for faster updates (resolution parameter)
3. **Limit curve points** - 500-1000 points usually sufficient
4. **Cache static plots** - Don't regenerate unchanged curves
5. **Batch updates** - Update multiple curves before drawing

## GPU Compute Details

The implicit function and stream plot features use **compute shaders** for massive parallelization:

- **Implicit functions**: GPU evaluates f(x,y) at every pixel in parallel
- **Stream plots**: GPU integrates vector field using RK4 in parallel
- **Performance**: Can evaluate millions of points per frame at 60+ FPS

---

[← Back to README](../README.md)
