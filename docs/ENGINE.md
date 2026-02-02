# Engine Architecture - RootEnv & DefEnv

Understanding the e2D engine architecture and window management.

## Core Concepts

e2D uses a **two-class architecture**:

1. **RootEnv** - Global singleton managing the window and OpenGL context
2. **DefEnv** - Base class for your application logic

```python
from e2D import RootEnv

# Your app inherits from DefEnv
class MyApp(DefEnv):
    def __init__(self):
        pass  # Initialize your state
    
    def update(self):
        pass  # Update logic (called every frame)
    
    def draw(self):
        pass  # Rendering (called every frame)

# Create window and run
rootEnv = RootEnv(
    title="My Game",
    width=1920,
    height=1080,
    fps=60
)
rootEnv.run(MyApp)
```

## RootEnv - The Engine Core

The `RootEnv` singleton manages:
- **Window creation** (GLFW + ModernGL)
- **Main loop** (update/draw cycle)
- **Input handling** (keyboard, mouse)
- **Frame timing** (delta time, FPS)
- **GPU context** (ModernGL context)

### Creating RootEnv

```python
rootEnv = RootEnv(
    title: str = "e2D Application",
    width: int = 1920,
    height: int = 1080,
    fps: int = 60,
    resizable: bool = False,
    vsync: bool = True,
    fullscreen: bool = False,
    msaa: int = 4  # Anti-aliasing samples
)
```

### Running Your App

```python
# Single application
rootEnv.run(MyApp)

# Multiple applications (switch between them)
rootEnv.run([MainMenu, GamePlay, GameOver])
```

## DefEnv - Application Base Class

Your application inherits from `DefEnv` and implements:

```python
class MyApp(DefEnv):
    def __init__(self):
        """
        Called once when application starts.
        Initialize your state here.
        """
        self.player_pos = Vector2D(960, 540)
        self.score = 0
    
    def update(self):
        """
        Called every frame before draw().
        Update game logic here.
        """
        if rootEnv.is_key_pressed(glfw.KEY_SPACE):
            self.score += 1
    
    def draw(self):
        """
        Called every frame after update().
        Render graphics here.
        """
        rootEnv.print(f"Score: {self.score}", (10, 10))
    
    def on_key_press(self, key, scancode, mods):
        """
        Optional: Handle key press events.
        """
        if key == glfw.KEY_ESCAPE:
            rootEnv.close()
    
    def on_mouse_click(self, x, y, button, mods):
        """
        Optional: Handle mouse click events.
        """
        print(f"Clicked at ({x}, {y})")
    
    def cleanup(self):
        """
        Optional: Clean up resources when app closes.
        """
        pass
```

## Main Loop

The main loop runs at the specified FPS:

```
┌─────────────────────────────────┐
│  Start Frame                    │
├─────────────────────────────────┤
│  1. Process Input Events        │
│     - Keyboard                  │
│     - Mouse                     │
│     - Window events             │
├─────────────────────────────────┤
│  2. Call update()               │
│     - Game logic                │
│     - Physics                   │
│     - AI                        │
├─────────────────────────────────┤
│  3. Call draw()                 │
│     - Clear screen              │
│     - Render graphics           │
│     - Swap buffers              │
├─────────────────────────────────┤
│  4. Frame Timing                │
│     - Calculate delta time      │
│     - Sleep to maintain FPS     │
└─────────────────────────────────┘
```

## Frame Timing

Access timing information via `rootEnv`:

```python
class TimingDemo(DefEnv):
    def update(self):
        # Delta time (seconds since last frame)
        dt = rootEnv.delta
        
        # Current FPS
        fps = rootEnv.fps
        
        # Total elapsed time
        time = rootEnv.time
        
        # Frame count
        frame = rootEnv.frame_count
    
    def draw(self):
        rootEnv.print(f"FPS: {rootEnv.fps:.1f}", (10, 10))
        rootEnv.print(f"Delta: {rootEnv.delta*1000:.2f}ms", (10, 30))
        rootEnv.print(f"Time: {rootEnv.time:.2f}s", (10, 50))
```

## Input Handling

### Keyboard

```python
class KeyboardDemo(DefEnv):
    def update(self):
        # Check if key is currently pressed
        if rootEnv.is_key_pressed(glfw.KEY_W):
            self.player_y += 5
        
        if rootEnv.is_key_pressed(glfw.KEY_S):
            self.player_y -= 5
        
        if rootEnv.is_key_pressed(glfw.KEY_A):
            self.player_x -= 5
        
        if rootEnv.is_key_pressed(glfw.KEY_D):
            self.player_x += 5
    
    def on_key_press(self, key, scancode, mods):
        # Single press event
        if key == glfw.KEY_SPACE:
            self.jump()
        
        if key == glfw.KEY_ESCAPE:
            rootEnv.close()
```

**Common GLFW Key Constants:**
- `glfw.KEY_SPACE`, `glfw.KEY_ENTER`, `glfw.KEY_ESCAPE`
- `glfw.KEY_LEFT`, `glfw.KEY_RIGHT`, `glfw.KEY_UP`, `glfw.KEY_DOWN`
- `glfw.KEY_A` through `glfw.KEY_Z`
- `glfw.KEY_0` through `glfw.KEY_9`
- `glfw.KEY_LEFT_SHIFT`, `glfw.KEY_LEFT_CONTROL`, `glfw.KEY_LEFT_ALT`

### Mouse

```python
class MouseDemo(DefEnv):
    def update(self):
        # Mouse position (x, y)
        mouse_pos = rootEnv.mouse_pos
        mx, my = mouse_pos
        
        # Mouse buttons (0=left, 1=right, 2=middle)
        if rootEnv.is_mouse_pressed(0):
            print("Left button held")
        
        # Mouse scroll
        scroll = rootEnv.mouse_scroll
        if scroll != 0:
            self.zoom += scroll * 0.1
    
    def on_mouse_click(self, x, y, button, mods):
        # Single click event
        if button == 0:  # Left click
            self.spawn_particle(x, y)
        
        if button == 1:  # Right click
            self.show_context_menu(x, y)
    
    def on_mouse_move(self, x, y):
        # Mouse move event
        self.cursor_pos = Vector2D(x, y)
```

## Window Management

```python
class WindowDemo(DefEnv):
    def update(self):
        # Get window size
        width, height = rootEnv.window_size
        
        # Close window
        if rootEnv.is_key_pressed(glfw.KEY_ESCAPE):
            rootEnv.close()
        
        # Toggle fullscreen (custom implementation)
        if rootEnv.is_key_pressed(glfw.KEY_F11):
            self.toggle_fullscreen()
```

## Multi-App Architecture

Switch between different application states:

```python
class MainMenu(DefEnv):
    def update(self):
        if rootEnv.is_key_pressed(glfw.KEY_SPACE):
            rootEnv.switch_app(GamePlay)  # Switch to game
    
    def draw(self):
        rootEnv.print("Main Menu", (960, 400))
        rootEnv.print("Press SPACE to start", (960, 500))

class GamePlay(DefEnv):
    def __init__(self):
        self.score = 0
    
    def update(self):
        # Game logic
        if self.game_over:
            rootEnv.switch_app(GameOver)
    
    def draw(self):
        rootEnv.print(f"Score: {self.score}", (10, 10))

class GameOver(DefEnv):
    def update(self):
        if rootEnv.is_key_pressed(glfw.KEY_SPACE):
            rootEnv.switch_app(MainMenu)  # Back to menu
    
    def draw(self):
        rootEnv.print("Game Over", (960, 400))
        rootEnv.print("Press SPACE to restart", (960, 500))

# Run with multiple apps
rootEnv = RootEnv(title="My Game")
rootEnv.run([MainMenu, GamePlay, GameOver])
```

## Background Color

```python
class ColorDemo(DefEnv):
    def __init__(self):
        # Set background color (r, g, b, a)
        rootEnv.set_background_color(0.1, 0.1, 0.2, 1.0)
        
        # Or use pre-defined colors
        rootEnv.set_background_color(*Color.BLACK.to_rgba())
```

## GPU Context Access

For advanced users, access the ModernGL context:

```python
class AdvancedDemo(DefEnv):
    def __init__(self):
        # Get ModernGL context
        ctx = rootEnv.ctx
        
        # Create custom shader program
        self.program = ctx.program(
            vertex_shader=vertex_source,
            fragment_shader=fragment_source
        )
        
        # Create custom buffer
        self.vbo = ctx.buffer(vertex_data)
```

## Complete Example

```python
from e2D import RootEnv, DefEnv, Vector2D, Color
import glfw
import math

class CompleteExample(DefEnv):
    def __init__(self):
        # State
        self.player_pos = Vector2D(960, 540)
        self.player_vel = Vector2D(0, 0)
        self.particles = []
        
        # UI
        self.fps_label = rootEnv.create_text("", (10, 10), scale=0.5)
        
        # Set background
        rootEnv.set_background_color(*Color.DARK_GRAY.to_rgba())
    
    def update(self):
        dt = rootEnv.delta
        
        # Player movement
        speed = 300  # pixels per second
        direction = Vector2D(0, 0)
        
        if rootEnv.is_key_pressed(glfw.KEY_W):
            direction.y += 1
        if rootEnv.is_key_pressed(glfw.KEY_S):
            direction.y -= 1
        if rootEnv.is_key_pressed(glfw.KEY_A):
            direction.x -= 1
        if rootEnv.is_key_pressed(glfw.KEY_D):
            direction.x += 1
        
        if direction.length() > 0:
            direction.normalize()
            self.player_vel = direction.mul(speed)
        else:
            self.player_vel = Vector2D(0, 0)
        
        self.player_pos.iadd(self.player_vel.mul(dt))
        
        # Update particles
        for p in self.particles:
            p['pos'].iadd(p['vel'].mul(dt))
            p['life'] -= dt
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # Update FPS
        self.fps_label.set_text(f"FPS: {rootEnv.fps:.1f}")
    
    def draw(self):
        # Draw player
        rootEnv.draw_circle(
            center=self.player_pos.to_tuple(),
            radius=20,
            color=Color.CYAN.to_rgba()
        )
        
        # Draw particles
        for p in self.particles:
            alpha = p['life'] / 2.0  # Fade out
            color = (*p['color'][:3], alpha)
            rootEnv.draw_circle(
                center=p['pos'].to_tuple(),
                radius=5,
                color=color
            )
        
        # Draw UI
        self.fps_label.draw()
        rootEnv.print(f"Particles: {len(self.particles)}", (10, 30), scale=0.5)
    
    def on_key_press(self, key, scancode, mods):
        if key == glfw.KEY_ESCAPE:
            rootEnv.close()
    
    def on_mouse_click(self, x, y, button, mods):
        if button == 0:  # Left click
            # Spawn particle burst
            for _ in range(20):
                self.particles.append({
                    'pos': Vector2D(x, y),
                    'vel': Vector2D.random(-200, 200),
                    'color': Color.random().to_rgba(),
                    'life': 2.0
                })

# Run the app
if __name__ == "__main__":
    rootEnv = RootEnv(
        title="Complete Example",
        width=1920,
        height=1080,
        fps=60
    )
    rootEnv.run(CompleteExample)
```

## RootEnv API Reference

### Properties (read-only)
- `rootEnv.delta` - Frame delta time (seconds)
- `rootEnv.fps` - Current frames per second
- `rootEnv.time` - Total elapsed time (seconds)
- `rootEnv.frame_count` - Total frames rendered
- `rootEnv.mouse_pos` - Mouse position (x, y)
- `rootEnv.mouse_scroll` - Mouse scroll amount
- `rootEnv.window_size` - Window dimensions (width, height)
- `rootEnv.ctx` - ModernGL context

### Methods
- `rootEnv.run(app_class or [app_classes])` - Start main loop
- `rootEnv.close()` - Close window
- `rootEnv.switch_app(app_class)` - Switch to different app
- `rootEnv.set_background_color(r, g, b, a)` - Set clear color
- `rootEnv.is_key_pressed(key)` - Check if key is pressed
- `rootEnv.is_mouse_pressed(button)` - Check if mouse button is pressed

### Drawing Methods
- `rootEnv.draw_circle(center, radius, **kwargs)`
- `rootEnv.draw_rect(position, size, **kwargs)`
- `rootEnv.draw_line(start, end, **kwargs)`
- `rootEnv.print(text, position, **kwargs)`
- `rootEnv.create_text(text, position, **kwargs)` - Create TextLabel
- `rootEnv.create_circle(**kwargs)` - Create cached shape
- `rootEnv.create_rect(**kwargs)` - Create cached shape

## DefEnv Lifecycle

```python
class AppLifecycle(DefEnv):
    def __init__(self):
        """Called once when app is created"""
        print("1. __init__ - Initialize state")
    
    def update(self):
        """Called every frame (before draw)"""
        print("2. update - Game logic")
    
    def draw(self):
        """Called every frame (after update)"""
        print("3. draw - Rendering")
    
    def on_key_press(self, key, scancode, mods):
        """Called when key is pressed"""
        print("4. on_key_press - Input event")
    
    def on_mouse_click(self, x, y, button, mods):
        """Called when mouse is clicked"""
        print("5. on_mouse_click - Input event")
    
    def cleanup(self):
        """Called once when app is closing"""
        print("6. cleanup - Free resources")
```

---

[← Back to README](../README.md)
