# Input Handling Guide

## Overview

e2D provides comprehensive input handling for keyboard and mouse through the `Keyboard`, `Mouse`, `Keys`, and `MouseButtons` classes with full autocompletion support.

## Table of Contents

- [Keyboard Input](#keyboard-input)
- [Keys Class](#keys-class)
- [Mouse Input](#mouse-input)
- [MouseButtons Class](#mousebuttons-class)
- [Key States](#key-states)
- [Examples](#examples)

## Keyboard Input

### Accessing the Keyboard

```python
from e2D import RootEnv, Keys, KeyState

class MyEnv(DefEnv):
    def update(self):
        # Access keyboard through root
        if self.root.keyboard.get_key(Keys.SPACE):
            print("Space is pressed!")
```

### Checking Key States

```python
# Check if key is currently pressed
if self.root.keyboard.get_key(Keys.W):
    self.player.move_forward()

# Check if key was just pressed this frame
if self.root.keyboard.get_key(Keys.SPACE, KeyState.JUST_PRESSED):
    self.player.jump()

# Check if key was just released this frame
if self.root.keyboard.get_key(Keys.CTRL, KeyState.JUST_RELEASED):
    self.player.stop_running()
```

## Keys Class

The `Keys` class provides clean, autocomplete-friendly access to all keyboard keys.

### Letter Keys

```python
from e2D import Keys

# Movement
if self.root.keyboard.get_key(Keys.W):
    move_up()
if self.root.keyboard.get_key(Keys.A):
    move_left()
if self.root.keyboard.get_key(Keys.S):
    move_down()
if self.root.keyboard.get_key(Keys.D):
    move_right()

# Actions
if self.root.keyboard.get_key(Keys.E, KeyState.JUST_PRESSED):
    interact()
if self.root.keyboard.get_key(Keys.Q, KeyState.JUST_PRESSED):
    use_ability()
```

### Number Keys

```python
# 0-9 keys
if self.root.keyboard.get_key(Keys.NUM_1, KeyState.JUST_PRESSED):
    select_slot(1)
if self.root.keyboard.get_key(Keys.NUM_2, KeyState.JUST_PRESSED):
    select_slot(2)

# Loop through number keys
for i in range(10):
    key = getattr(Keys, f"NUM_{i}")
    if self.root.keyboard.get_key(key, KeyState.JUST_PRESSED):
        select_weapon(i)
```

### Arrow Keys

```python
# Directional input
if self.root.keyboard.get_key(Keys.UP):
    move_up()
if self.root.keyboard.get_key(Keys.DOWN):
    move_down()
if self.root.keyboard.get_key(Keys.LEFT):
    move_left()
if self.root.keyboard.get_key(Keys.RIGHT):
    move_right()
```

### Function Keys

```python
# F1-F12 keys
if self.root.keyboard.get_key(Keys.F1, KeyState.JUST_PRESSED):
    show_help()
if self.root.keyboard.get_key(Keys.F11, KeyState.JUST_PRESSED):
    toggle_fullscreen()
if self.root.keyboard.get_key(Keys.F12, KeyState.JUST_PRESSED):
    take_screenshot()
```

### Special Keys

```python
# Common special keys
if self.root.keyboard.get_key(Keys.SPACE):
    jump()
if self.root.keyboard.get_key(Keys.ENTER, KeyState.JUST_PRESSED):
    confirm()
if self.root.keyboard.get_key(Keys.ESCAPE, KeyState.JUST_PRESSED):
    open_menu()
if self.root.keyboard.get_key(Keys.TAB, KeyState.JUST_PRESSED):
    toggle_inventory()
if self.root.keyboard.get_key(Keys.BACKSPACE):
    delete_character()
```

### Modifier Keys

```python
# Shift keys
if self.root.keyboard.get_key(Keys.LEFT_SHIFT):
    run()
if self.root.keyboard.get_key(Keys.RIGHT_SHIFT):
    run()

# Control keys
if self.root.keyboard.get_key(Keys.LEFT_CONTROL):
    crouch()

# Alt keys
if self.root.keyboard.get_key(Keys.LEFT_ALT):
    show_alternative_view()

# Super/Windows/Command keys
if self.root.keyboard.get_key(Keys.LEFT_SUPER):
    # Windows key (usually reserved by OS)
    pass
```

### Numpad Keys

```python
# Numpad numbers
if self.root.keyboard.get_key(Keys.KP_0):
    numpad_input(0)

# Numpad operators
if self.root.keyboard.get_key(Keys.KP_ADD):
    increase_value()
if self.root.keyboard.get_key(Keys.KP_SUBTRACT):
    decrease_value()
if self.root.keyboard.get_key(Keys.KP_MULTIPLY):
    multiply_value()
if self.root.keyboard.get_key(Keys.KP_DIVIDE):
    divide_value()
```

### Complete Keys List

```python
# Letters: Keys.A through Keys.Z
# Numbers: Keys.NUM_0 through Keys.NUM_9
# Function: Keys.F1 through Keys.F25
# Arrows: Keys.UP, Keys.DOWN, Keys.LEFT, Keys.RIGHT
# Special: Keys.SPACE, Keys.ENTER, Keys.TAB, Keys.BACKSPACE,
#          Keys.ESCAPE, Keys.DELETE, Keys.INSERT, etc.
# Modifiers: Keys.LEFT_SHIFT, Keys.RIGHT_SHIFT, Keys.LEFT_CONTROL,
#           Keys.RIGHT_CONTROL, Keys.LEFT_ALT, Keys.RIGHT_ALT
# Numpad: Keys.KP_0 through Keys.KP_9, Keys.KP_ADD, Keys.KP_ENTER, etc.
```

## Mouse Input

### Mouse Position

```python
# Get current mouse position
mouse_pos = self.root.mouse.position
print(f"Mouse at ({mouse_pos.x}, {mouse_pos.y})")

# Check if mouse is over area
if 100 <= mouse_pos.x <= 200 and 100 <= mouse_pos.y <= 150:
    print("Mouse over button!")
```

### Mouse Movement

```python
# Get mouse delta (movement since last frame)
delta = self.root.mouse.delta
print(f"Mouse moved by ({delta.x}, {delta.y})")

# Camera control with mouse
self.camera.rotate(delta.x * 0.1)

# Get last frame's position
last_pos = self.root.mouse.last_position
```

### Mouse Scroll

```python
# Get scroll wheel input
scroll = self.root.mouse.scroll
if scroll.y > 0:
    zoom_in()
elif scroll.y < 0:
    zoom_out()

# Horizontal scroll (if supported)
if scroll.x != 0:
    scroll_horizontally(scroll.x)
```

## MouseButtons Class

The `MouseButtons` class provides clean access to mouse button constants.

### Button Checking

```python
from e2D import MouseButtons, KeyState

# Left mouse button
if self.root.mouse.get_button(MouseButtons.LEFT, KeyState.PRESSED):
    print("Left button held")

if self.root.mouse.get_button(MouseButtons.LEFT, KeyState.JUST_PRESSED):
    print("Left button clicked")

# Right mouse button
if self.root.mouse.get_button(MouseButtons.RIGHT, KeyState.PRESSED):
    secondary_action()

# Middle mouse button
if self.root.mouse.get_button(MouseButtons.MIDDLE, KeyState.PRESSED):
    pan_camera()

# Additional buttons (for gaming mice)
if self.root.mouse.get_button(MouseButtons.BUTTON_4, KeyState.JUST_PRESSED):
    previous_weapon()
if self.root.mouse.get_button(MouseButtons.BUTTON_5, KeyState.JUST_PRESSED):
    next_weapon()
```

### Available Buttons

```python
MouseButtons.LEFT      # Primary button
MouseButtons.RIGHT     # Secondary button
MouseButtons.MIDDLE    # Scroll wheel click
MouseButtons.BUTTON_4  # Side button 1
MouseButtons.BUTTON_5  # Side button 2
MouseButtons.BUTTON_6  # Extra button 1
MouseButtons.BUTTON_7  # Extra button 2
MouseButtons.BUTTON_8  # Extra button 3
```

## Key States

Three key states are available for precise input handling:

### PRESSED

Continuous state - true every frame while key is held.

```python
# Hold to move
if self.root.keyboard.get_key(Keys.W, KeyState.PRESSED):
    self.player.move_forward(self.root.delta)

# Or use default (PRESSED is default)
if self.root.keyboard.get_key(Keys.W):
    self.player.move_forward(self.root.delta)
```

### JUST_PRESSED

Single-frame event - true only on the frame the key was pressed.

```python
# Single action on press
if self.root.keyboard.get_key(Keys.SPACE, KeyState.JUST_PRESSED):
    self.player.jump()

# Prevent key repeat
if self.root.keyboard.get_key(Keys.E, KeyState.JUST_PRESSED):
    self.player.interact()  # Won't repeat if held
```

### JUST_RELEASED

Single-frame event - true only on the frame the key was released.

```python
# Action on release
if self.root.keyboard.get_key(Keys.LEFT_SHIFT, KeyState.JUST_RELEASED):
    self.player.stop_running()

# Charge attacks
if self.root.mouse.get_button(MouseButtons.LEFT, KeyState.JUST_RELEASED):
    self.player.release_charged_attack(self.charge_time)
```

## Examples

### Movement System

```python
class Player:
    def __init__(self):
        self.position = V2(400, 300)
        self.velocity = V2(0, 0)
        self.speed = 200.0
    
    def update(self, keyboard, dt):
        # Reset velocity
        self.velocity.set(0, 0)
        
        # WASD movement
        if keyboard.get_key(Keys.W):
            self.velocity.y = -self.speed
        if keyboard.get_key(Keys.S):
            self.velocity.y = self.speed
        if keyboard.get_key(Keys.A):
            self.velocity.x = -self.speed
        if keyboard.get_key(Keys.D):
            self.velocity.x = self.speed
        
        # Normalize diagonal movement
        if self.velocity.length > 0:
            self.velocity.normalize()
            self.velocity.iscale(self.speed * dt)
            self.position.iadd(self.velocity)
```

### Combat System

```python
class CombatSystem:
    def update(self, keyboard, mouse):
        # Primary attack
        if mouse.get_button(MouseButtons.LEFT, KeyState.JUST_PRESSED):
            self.primary_attack(mouse.position)
        
        # Secondary attack
        if mouse.get_button(MouseButtons.RIGHT, KeyState.JUST_PRESSED):
            self.secondary_attack(mouse.position)
        
        # Abilities (number keys)
        for i in range(1, 5):
            key = getattr(Keys, f"NUM_{i}")
            if keyboard.get_key(key, KeyState.JUST_PRESSED):
                self.use_ability(i - 1)
        
        # Dodge
        if keyboard.get_key(Keys.SPACE, KeyState.JUST_PRESSED):
            self.dodge()
```

### Camera Control

```python
class Camera:
    def __init__(self):
        self.position = V2(0, 0)
        self.zoom = 1.0
        self.pan_speed = 300.0
    
    def update(self, keyboard, mouse, dt):
        # Arrow key panning
        if keyboard.get_key(Keys.LEFT):
            self.position.x -= self.pan_speed * dt
        if keyboard.get_key(Keys.RIGHT):
            self.position.x += self.pan_speed * dt
        if keyboard.get_key(Keys.UP):
            self.position.y -= self.pan_speed * dt
        if keyboard.get_key(Keys.DOWN):
            self.position.y += self.pan_speed * dt
        
        # Mouse drag panning
        if mouse.get_button(MouseButtons.MIDDLE, KeyState.PRESSED):
            self.position.isub(mouse.delta)
        
        # Scroll wheel zoom
        if mouse.scroll.y != 0:
            self.zoom *= 1.0 + (mouse.scroll.y * 0.1)
            self.zoom = max(0.1, min(10.0, self.zoom))
```

### UI System

```python
class Button:
    def __init__(self, pos, size, callback):
        self.pos = pos
        self.size = size
        self.callback = callback
        self.hovered = False
    
    def update(self, mouse):
        # Check if mouse is over button
        self.hovered = (
            self.pos.x <= mouse.position.x <= self.pos.x + self.size.x and
            self.pos.y <= mouse.position.y <= self.pos.y + self.size.y
        )
        
        # Handle click
        if self.hovered and mouse.get_button(MouseButtons.LEFT, KeyState.JUST_PRESSED):
            self.callback()
    
    def draw(self, root):
        color = BLUE if self.hovered else GRAY
        root.draw_rect(self.pos, self.size, color=color)
```

### Keyboard Shortcuts

```python
class ShortcutSystem:
    def update(self, keyboard):
        # Check for Ctrl key
        ctrl = keyboard.get_key(Keys.LEFT_CONTROL) or keyboard.get_key(Keys.RIGHT_CONTROL)
        
        if ctrl:
            # Ctrl+S: Save
            if keyboard.get_key(Keys.S, KeyState.JUST_PRESSED):
                self.save()
            
            # Ctrl+O: Open
            if keyboard.get_key(Keys.O, KeyState.JUST_PRESSED):
                self.open()
            
            # Ctrl+Z: Undo
            if keyboard.get_key(Keys.Z, KeyState.JUST_PRESSED):
                self.undo()
            
            # Ctrl+Y: Redo
            if keyboard.get_key(Keys.Y, KeyState.JUST_PRESSED):
                self.redo()
```

## See Also

- [API Reference](API_REFERENCE.md#input) - Complete API documentation
- [test_input.py](../tests/test_input.py) - Test suite
- [example_input.py](../examples/example_input.py) - Interactive demonstration
- [example_keys.py](../examples/example_keys.py) - Keys class showcase
