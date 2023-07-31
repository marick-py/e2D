<p align="center">
  <img src="e2D_logo.png" alt="e2D Logo" width="400" height="300">
</p>

# e2D
## Python Utility Library for 2D Game Development and Graphics

e2D is a Python utility library designed to simplify 2D game development and graphics tasks. With e2D, developers can focus on the creative aspects of their games while enjoying the convenience of ready-to-use tools and functions.

## Features

- Efficient handling of keyboard and mouse input for interactive gameplay.
- Powerful vector calculations for easy position manipulation, distance calculation, and angle manipulation.
- Flexible color manipulation functions for smooth transitions and visual effects.
- Convenient positioning and collision detection functions to handle game object interactions.
- Simple API for ease of use, suitable for both beginners and experienced developers.

## Installation

You can install e2D using pip:

```bash
pip install e2D
```
```bash
pip3 install e2D
```

## Getting Started

To get started with e2D, follow these steps:

1. Create a new Python project or navigate to your existing project directory.

2. Install e2D via pip as shown in the Installation section.

3. Import the classes and functions you need from e2D into your Python files and start using the library.

## Examples

Here are some examples to demonstrate how to use e2D:

```python
# Example 0: Easy To Understand and Fast Math Implementation
from e2D import *

v1 = V2(10, -50)

# able to operate a Vector2D and a int/float
v1 *= 10 + 10

# able to operate a Vector2D and a list/tuple
v1 += [PI, 4.35]

list_v1 = v1()
tuple_v1 = v1(return_tuple=True)

abs_v1 = abs(v1)
square_root_v1 = abs_v1 ** .5
rounded_v1 = round(square_root_v1)

# Example 1: Handling Keyboard And Mouse Input in Pygame
from e2D.utils import Keyboard, Mouse

keyboard = Keyboard()
if keyboard.get_key("space"):
    print("Space key is pressed!")

mouse = Mouse()
print(mouse.get_position())
# V2(x,y)
print(mouse.just_pressed)
# [bool, bool, bool]

# Example 2: Vector Calculations
from e2D import Vector2D

vector1 = Vector2D(3, 4)
vector2 = Vector2D(-2, 6)
result = vector1 + vector2
print("Result:", result)

# Example 3: Color Manipulation
from e2D import color_fade, rgb

starting_color = rgb(255, 0, 0)
final_color = rgb(0, 0, 255)
intermediate_color = color_fade(starting_color, final_color, 0.5)
print("Intermediate Color:", intermediate_color)

# Example 4: Use Default Pygame Env just like this:
from e2D.envs import *

class Env:
    def __init__(self) -> None:
        pass

    def draw(self) -> None:
        pg.draw.circle(rootEnv.screen, (255,127,0), rootEnv.mouse.position(), 10)

    def update(self) -> None:
        pass

rootEnv = RootEnv(Env())
while not rootEnv.quit:
    rootEnv.frame()
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions

Contributions are welcome! If you find any bugs or have suggestions for improvements, feel free to open an issue or submit a pull request.

## Credits

e2D is developed and maintained by [marick-py](https://github.com/marick-py).

## Contact

For inquiries, you can reach me at [ricomari2006@gmail.com](mailto:ricomari2006@gmail.com).

Happy coding with e2D! 🚀
