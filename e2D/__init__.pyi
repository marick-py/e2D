from __future__ import annotations
from typing import Callable, Literal

PI : float
HALF_PI : float
QUARTER_PI : float
DOUBLE_PI : float

# regular expression to remove comments:
# """([\s\S]*?)"""

# 

sign : Callable[[int|float], Literal[-1,0,1]]

class Vector2D:
    round_values_on_print : int|float
    def __init__(self:"Vector2D", x:int|float=.0, y:int|float=.0) -> None:
        """
        # Initialize a 2D vector with the specified x and y components.

        ## Parameters:
            x (int | float, optional): The x-component of the vector. Default is 0.
            y (int | float, optional): The y-component of the vector. Default is 0.

        ## Example:
            vector1 = Vector2D()        # Creates a vector with x=0 and y=0
            vector2 = Vector2D(3, -2.5) # Creates a vector with x=3 and y=-2.5

        ## Explanation:
            This constructor initializes a 2D vector with the specified x and y components.

            If no arguments are provided, the default values for x and y are both set to 0.

            The x and y components can be integers or floating-point numbers.

            Example usage is shown in the "Example" section above.
        """
        self.x : int|float
        self.y : int|float

    def distance_to(self:"Vector2D", other:"Vector2D", sqrd:bool=True) -> int|float:
        """
        # Calculate the distance between the current Vector2D other and another other.

        ## Parameters:
            other (float or int or Vector2D or list|tuple): The other other to which the distance is calculated.
            squared (bool, optional): If True, return the squared distance. If False, return the actual distance.
                                      Default is True.

        ## Returns:
            int|float: The squared distance between the current Vector2D other and the other other if `squared` is True,
                      otherwise the actual distance.

        ## Example:
            point1 = Vector2D(0, 0)

            point2 = Vector2D(3, 4)

            squared_distance = point1.distance_to(point2)

            print(f"Squared Distance: {squared_distance}")

            distance = point1.distance_to(point2, squared=False)

            print(f"Actual Distance: {distance}")

            This will calculate the squared and actual distances between the two points.

        ## Explanation:
            The function calculates the squared distance between the current Vector2D other (self) and another other
            (other) using the formula: (self.x - other.x)**2 + (self.y - other.y)**2.

            The result is returned as the squared distance if `squared` is True, or as the actual distance if `squared` is False.
        """
        ...

    def angle_to(self:"Vector2D", other:"Vector2D") -> int|float:
        """
        # Calculate the angle between the current Vector2D other and another other.

        ## Parameters:
            other (float or int or Vector2D or list|tuple): The other other to which the angle is calculated.

        ## Returns:
            int|float: The angle in radians between the current Vector2D other and the other other.

        ## Example:
            point1 = Vector2D(0, 0)

            point2 = Vector2D(1, 1)

            angle = point1.angle_to(point2)

            print(f"Angle in radians: {angle}")

            This will calculate the angle in radians between the two points.

        ## Explanation:
            The function calculates the angle in radians between the current Vector2D other (self) and another other
            (other) using the `atan2` function from the `math` module.

            The result is returned as the angle in radians.
        """
        ...

    def point_from_angle_and_radius(self:"Vector2D", rad: int|float, radius: int|float) -> "Vector2D":
        """
        # Calculate a new Vector2D point from the current point based on an angle in radians and a radius.

        ## Parameters:
            rad (int|float): The angle in radians.
            radius (int|float): The distance from the current point.

        ## Returns:
            Vector2D: A new Vector2D point calculated from the current point.

        ## Example:
            point1 = Vector2D(0, 0)

            angle = 45

            distance = 5

            new_point = point1.point_from_degs(_mt.radians(angle), distance)

            print(new_point.x, new_point.y)

            This will calculate a new point 5 units away from point1 at a 45-degree angle.

        ## Explanation:
            The function calculates a new Vector2D point based on an angle in radians (rad) and a distance (radius)
            from the current Vector2D point.

            It computes the new x and y coordinates of the point using the trigonometric functions `cos` and `sin`
            to determine the horizontal and vertical components of the new point.

            The result is returned as a new Vector2D point with the calculated coordinates.
        """
        ...

    @property
    def angle(self:"Vector2D") -> int|float: ...

    @angle.setter
    def angle(self:"Vector2D", argv) -> None: ...

    @property
    def copy(self:"Vector2D") -> "Vector2D":
        """
        # Create a copy of the current Vector2D other.

        ## Returns:
            Vector2D: A new Vector2D other with the same x and y coordinates as the current other.

        ## Example:
            point1 = Vector2D(1, 2)

            point2 = point1.copy()

            print(point2.x, point2.y)

            This will print the x and y coordinates of the copied Vector2D other (1, 2).

        ## Explanation:
            The function creates a new Vector2D other with the same x and y coordinates as the current other.

            The result is returned as a new Vector2D other, effectively making a copy of the original other.
        """
        ...

    @property
    def sign(self:"Vector2D") -> "Vector2D":
        """
        # Perform an "absolute round" operation on the Vector2D other.

        ## Parameters:
            n (int|float, optional): The numeric value to scale the "absolute rounded" vector. Default is 1.

        ## Returns:
            Vector2D: The "absolute rounded" Vector2D other scaled by the provided numeric value.

        ## Example:
            vector1 = Vector2D(3.3, -4.7)

            result1 = vector1.absolute_round(0.5)

            print(result1.x, result1.y)

            vector2 = Vector2D(-2.8, 1.1)

            result2 = vector2.absolute_round()

            print(result2.x, result2.y)

        ## Explanation:
            The function performs an "absolute round" operation on the Vector2D other.

            The "absolute round" operation involves taking the absolute values of both the x and y components of the Vector2D other,
            and then scaling the resulting vector by the provided numeric value (n).

            The default value of n is 1, which means the "absolute rounded" vector will have the same magnitude as the original vector.

            If the provided numeric value (n) is 0, the function returns a Vector2D other with zeros for both components.

            If the provided numeric value (n) is negative, the resulting "absolute rounded" vector will point in the opposite direction
            as the original vector but will have the same magnitude.

            Note: The "absolute round" operation does not perform standard mathematical rounding; instead, it ensures the resulting
            vector points in the same direction as the original vector but has non-negative components.
        """
        ...
    
    @property
    def normalize(self:"Vector2D") -> "Vector2D":
        """
        # Vector Normalization

        ## Returns:
            Vector2D: A new vector with the same direction as the current vector but with a magnitude of 1.

        ## Raises:
            ValueError: If the magnitude of the current vector is zero (zero vector).

        ## Example:
            v = Vector2D(3, 4)
            normalized_v = v.normalize()  # Normalize the vector (3, 4)
            print(normalized_v)  # Output: (0.6, 0.8)

        ## Explanation:
            This method calculates the normalized version of the current vector, which means a new vector with the same direction as the original but with a magnitude of 1.

            The method first calculates the magnitude of the current vector using the 'magnitude' method.

            If the magnitude is zero (zero vector), a ValueError is raised, as normalization is not defined for zero vectors.

            The normalized vector is obtained by dividing each component of the current vector by its magnitude.

            The resulting normalized vector is returned.

            Example usage is shown in the "Example" section above.
        """
        ...
    
    @property
    def length(self:"Vector2D") -> float:
        ...

    def floor(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        ...

    def ceil(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        ...
    
    def round(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        ...

    @classmethod
    def randomize(cls, start:"int|float|Vector2D", end:"int|float|Vector2D") -> "Vector2D":
        """
        # Generate a random Vector2D point within the specified range.

        ## Parameters:
            start (int|float or Vector2D or None, optional): The starting point of the range.
                                                        Default is None, which corresponds to (0, 0).
                                                        If numeric, both x and y will have the same value.
            end (int|float or Vector2D or None, optional): The ending point of the range.
                                                        Default is None, which corresponds to (1, 1).
                                                        If numeric, both x and y will have the same value.

        ## Returns:
            Vector2D: A new random Vector2D point within the specified range.

        ## Example:
            random_point = randomize(Vector2D(10, 20), Vector2D(50, 70))

            print(random_point.x, random_point.y)

            This will print a random point between (10, 20) and (50, 70).

        ## Explanation:
            The function generates a random Vector2D point within the specified range defined by `start` and `end`.

            If `start` and `end` are numeric values (int or float), both x and y coordinates will have the same value.

            If `start` and `end` are None, the default range is assumed to be (0, 0) to (1, 1).

            The function first checks if `start` and `end` are Vector2D others. If not, it creates new Vector2D others
            based on the numeric values provided or the default values.

            It then generates random x and y coordinates in the range [0, 1) using the `random()` function from the `random` module.
            These random values are then scaled by (end - start) and added to the start point to obtain the final random Vector2D point.
        """
        ...
    
    def dot_product(self:"Vector2D", other:"Vector2D") -> float:
        """
        # Calculate the dot product of the current vector with another vector.

        ## Parameters:
            other (Vector2D): The other vector for the dot product calculation.

        ## Returns:
            float: The dot product value.

        ## Example:
            v1 = Vector2D(2, 3)
            v2 = Vector2D(4, -1)
            result = v1.dot_product(v2)
            print(result)  # Output: 5

        ## Explanation:
            The dot product of two vectors (A and B) is given by the formula: dot_product = A.x * B.x + A.y * B.y

            The method takes another vector (other) as input and returns the dot product value.

            Example usage is shown in the "Example" section above.
        """
        ...

    def projection(self:"Vector2D", other:"Vector2D") -> "Vector2D":
        """
        # Vector Projection

        ## Parameters:
            other (float, int, Vector2D, V2, list, tuple): The vector onto which to project.

        ## Returns:
            Vector2D or V2: The projection of the current vector onto the 'other' vector.

        ## Raises:
            ValueError: If 'other' is a zero vector.

        ## Example:
            v1 = Vector2D(3, 4)
            v2 = Vector2D(1, 0)
            projection_v = v1.projection(v2)  # Calculate the projection of v1 onto v2
            print(projection_v)  # Output: (3.0, 0.0)

        ## Explanation:
            This method calculates the projection of the current vector onto the 'other' vector.
            The projection is a vector that represents the component of the current vector in the direction of the 'other' vector.

            If 'other' is not a Vector2D instance, it will be converted to one using the '__normalize__' method.
            The method first normalizes the 'other' vector using the '__normalize__' method of the vector.

            Next, it calculates the dot product of the current vector and the normalized 'other' vector using the 'dot_product' method.
            It also calculates the squared magnitude of the 'other' vector using the 'magnitude' method.

            If the magnitude of 'other' is zero (a zero vector), a ValueError is raised, as projection is not defined for zero vectors.

            The projection is then obtained by scaling the 'other' vector by the dot product divided by the squared magnitude.

            The resulting projection vector is returned.

            Example usage is shown in the "Example" section above.
        """
        ...

    def reflection(self:"Vector2D", normal:"Vector2D") -> "Vector2D":
        """
        # Vector Reflection

        ## Parameters:
            normal (float, int, Vector2D, V2, list, tuple): The normal vector representing the surface of reflection.

        ## Returns:
            Vector2D or V2: The reflected vector.

        ## Example:
            incident_vector = Vector2D(3, 4)
            normal_vector = Vector2D(1, 0)
            reflected_vector = incident_vector.reflection(normal_vector)  # Calculate the reflection of the incident vector over the given normal
            print(reflected_vector)  # Output: (-3.0, 4.0)

        ## Explanation:
            This method calculates the reflection of the current vector over the given normal vector.
            The normal vector represents the surface of reflection, and it should be normalized (unit vector).

            The method first normalizes the 'normal' vector using the '__normalize__' method of the vector.
            Next, it calculates the projection of the current vector onto the 'normal' vector using the 'projection' method.
            The reflected vector is obtained by subtracting twice the projection from the current vector.

            The resulting reflected vector is returned.

            Example usage is shown in the "Example" section above.
        """
        ...

    def cartesian_to_polar(self:"Vector2D") -> tuple:
        """
        # Convert Cartesian Coordinates to Polar Coordinates

        ## Returns:
            tuple: A tuple containing the radial distance (magnitude) 'r' and the angle 'theta' in radians.

        ## Example:
            v = Vector2D(3, 4)
            r, theta = v.cartesian_to_polar()  # Convert Cartesian coordinates (3, 4) to polar
            print(r, theta)  # Output: (5.0, 0.9272952180016122)

        ## Explanation:
            This method converts Cartesian coordinates (x, y) to polar coordinates (r, theta).
            'r' is the radial distance (magnitude) from the origin to the point, and 'theta' is the angle
            (in radians) measured from the positive x-axis to the point.

            The method calculates the radial distance 'r' using the 'magnitude' method of the vector.
            The angle 'theta' is calculated using the arctan2 function, which takes the y and x components of the vector.

            The resulting 'r' and 'theta' are returned as a tuple.

            Example usage is shown in the "Example" section above.
        """
        ...

    @classmethod
    def polar_to_cartesian(cls, r: int|float, theta: int|float) -> "Vector2D":
        """
        # Convert Polar Coordinates to Cartesian Coordinates

        ## Parameters:
            r (float or int): The radial distance (magnitude) from the origin to the point.
            theta (float or int): The angle (in radians or degrees) measured from the positive x-axis to the point.

        ## Returns:
            Vector2D or V2: A new vector representing the Cartesian coordinates (x, y) of the point.

        ## Example:
            cartesian_point = Vector2D.polar_to_cartesian(5, math.pi/4)  # Convert polar coordinates (r=5, theta=45 degrees) to Cartesian
            print(cartesian_point)  # Output: (3.5355339059327378, 3.5355339059327373)

        ## Explanation:
            This class method converts polar coordinates (r, theta) to Cartesian coordinates (x, y).
            'r' is the radial distance (magnitude) from the origin to the point, and 'theta' is the angle
            (in radians or degrees) measured from the positive x-axis to the point.

            The method calculates the x and y components using trigonometric functions (cosine and sine) based on 'r' and 'theta'.

            Example usage is shown in the "Example" section above.
        """
        ...

    def cartesian_to_complex(self:"Vector2D") -> complex: ...

    @classmethod
    def complex_to_cartesian(cls, complex_n: complex) -> "Vector2D": ...

    def lerp(self:"Vector2D", other:"int|float|Vector2D|list|tuple", t:float=.1) -> "Vector2D":
        """
        # Linear Interpolation (LERP)

        ## Parameters:
            other (float, int, Vector2D, V2, list, tuple): The vector to interpolate towards.
            t (float): The interpolation parameter. Must be between 0 and 1.

        ## Returns:
            Vector2D or V2: The result of the linear interpolation.

        ## Raises:
            ValueError: If t is not within the range [0, 1].

        ## Example:
            v1 = Vector2D(1, 2)
            v2 = Vector2D(5, 7)
            interpolated_v = v1.lerp(v2, 0.5)  # Linearly interpolate between v1 and v2 with t = 0.5
            print(interpolated_v)  # Output: (3.0, 4.5)

        ## Explanation:
            This method performs linear interpolation between the current vector and the 'other' vector.
            The 't' parameter represents the interpolation parameter, which controls how much the interpolation
            leans towards the 'other' vector. When 't' is 0, the result will be equal to the current vector (self).
            When 't' is 1, the result will be equal to the 'other' vector. For intermediate values of 't', the
            result will be a linear combination of the two vectors, smoothly transitioning between them.

            If 'other' is not a Vector2D instance, it will be converted to one using the '__normalize__' method.
            If 't' is not within the range [0, 1], a ValueError is raised.

            Example usage is shown in the "Example" section above.
        """
        ...

    def rotate(self:"Vector2D", angle: int|float, center:"Vector2D|None"=None) -> "Vector2D":
        """
        # Rotate the vector by a given angle around the origin or a specified center.

        ## Parameters:
            angle (int or float): The angle of rotation in radians or degrees, depending on the trigonometric functions used.
            center (float, int, Vector2D, V2, list, tuple, or None): The center of rotation.
                If None, the vector is rotated around the origin (0, 0).

        ## Returns:
            Vector2D or V2: The rotated vector.

        ## Example:
            v = Vector2D(3, 4)
            rotated_v = v.rotate(math.pi / 4)  # Rotate 45 degrees around the origin
            print(rotated_v)  # Output: (0.7071067811865476, 5.656854249492381)
            
            center = Vector2D(1, 1)
            rotated_v = v.rotate(math.pi / 4, center)  # Rotate 45 degrees around the center (1, 1)
            print(rotated_v)  # Output: (1.7071067811865475, 2.656854249492381)

        ## Explanation:
            This method rotates the vector by the specified angle around the given center.
            If no center is provided, the vector is rotated around the origin (0, 0).

            The method calculates the trigonometric functions (cosine and sine) of the angle to perform the rotation.
            The translated vector is obtained by subtracting the center from the current vector.
            The rotated vector is then obtained by applying the rotation transformation to the translated vector.
            The center is added back to the rotated vector to obtain the final result.

            Example usage is shown in the "Example" section above.
        """
        ...

    def no_zero_div_error(self:"Vector2D", n:"int|float|Vector2D", error_mode:Literal["zero", "null", "nan"]="zero") -> "Vector2D":
        """
        # Handle division between the Vector2D other and a numeric value or another Vector2D other.

        ## Parameters:
            n (int|float or Vector2D): The numeric value or Vector2D other for division.
            error_mode (str, optional): The mode to handle division by zero scenarios.
                                        - "zero" (default): Return a Vector2D other with zeros for both components.
                                        - "null": Return a Vector2D other with the original x or y component if available,
                                                   otherwise, return NaN (Not a Number) for the component.

        ## Returns:
            Vector2D: A new Vector2D other after division or handling division by zero scenarios.

        ## Example:
            vector1 = Vector2D(3, 4)

            result1 = vector1.no_zero_div_error(2)

            print(result1.x, result1.y)

            vector2 = Vector2D(5, 0)

            result2 = vector1.no_zero_div_error(vector2, error_mode="null")

            print(result2.x, result2.y)

        ## Explanation:
            The function handles division between the Vector2D other and a numeric value or another Vector2D other.

            If n is a numeric value (int or float):
                - If n is zero, the function returns a Vector2D other with zeros for both components if error_mode is "zero".
                - If error_mode is "null", the function returns a Vector2D other with the original x or y component if available,
                  otherwise, return NaN (Not a Number) for the component.

            If n is a Vector2D other:
                - If n's x or y component is zero, the function returns a Vector2D other with zeros for the corresponding component
                  if error_mode is "zero".
                - If error_mode is "null", the function returns a Vector2D other with the original x or y component if available,
                  otherwise, return NaN (Not a Number) for the component.

            If n is neither a numeric value nor a Vector2D other, the function raises an exception.
        """
        ...

    def min(self:"Vector2D", other:"Vector2D") -> "Vector2D": ...
    
    def max(self:"Vector2D", other:"Vector2D") -> "Vector2D": ...

    def advanced_stringify(self:"Vector2D", precision: float|None=None, use_scientific_notation:bool=False, return_as_list=False) -> str|list[str]:
        def optimize(value: int|float) -> str: ...
        ...

    def __str__(self:"Vector2D") -> str: ...

    def __repr__(self:"Vector2D") -> str: ...

    def __call__(self:"Vector2D") -> list: ...

    # fast operations     Vector2D.operation(both,x,y)
    def add(self, both:int|float=.0, x:int|float=.0, y:int|float=.0) -> Vector2D: ...
    
    def sub(self, both:int|float=.0, x:int|float=.0, y:int|float=.0) -> Vector2D: ...
    
    def mult(self, both:int|float=.0, x:int|float=.0, y:int|float=.0) -> Vector2D: ...
    
    def pow(self, both:int|float=.0, x:int|float=.0, y:int|float=.0) -> Vector2D: ...
    
    def mod(self, both:int|float=.0, x:int|float=.0, y:int|float=.0) -> Vector2D: ...
    
    def div(self, both:int|float=.0, x:int|float=.0, y:int|float=.0) -> Vector2D: ...
    
    def fdiv(self, both:int|float=.0, x:int|float=.0, y:int|float=.0) -> Vector2D: ...

    # fast inplace operations     Vector2D.ioperation(both,x,y)
    def set(self, both=int|float, x:int|float, y:int|float) -> Vector2D: ...

    def iadd(self, both:int|float, x:int|float, y=int|float) -> Vector2D: ...
    
    def isub(self, both:int|float, x:int|float, y=int|float) -> Vector2D: ...
    
    def imult(self, both:int|float, x:int|float, y=int|float) -> Vector2D: ...
    
    def ipow(self, both:int|float, x:int|float, y=int|float) -> Vector2D: ...
    
    def imod(self, both:int|float, x:int|float, y=int|float) -> Vector2D: ...
    
    def idiv(self, both:int|float, x:int|float, y=int|float) -> Vector2D: ...
    
    def ifdiv(self, both:int|float, x:int|float, y=int|float) -> Vector2D: ...

    # normal operations     Vector2D + a
    def __add__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __sub__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __mul__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __mod__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __pow__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __truediv__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __floordiv__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    # right operations      a + Vector2D
    def __radd__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __rsub__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __rmul__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __rmod__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __rpow__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __rtruediv__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __rfloordiv__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    # in-place operations   Vector2D += a
    def __iadd__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __isub__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __imul__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __itruediv__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __imod__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...
    
    def __ipow__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    def __ifloordiv__(self:"Vector2D", other:"int|float|Vector2D|list|tuple") -> "Vector2D": ...

    # comparasion
    def __eq__(self:"Vector2D", other) -> bool: ...

    def __ne__(self:"Vector2D", other) -> bool: ...

    def __abs__(self:"Vector2D") -> "Vector2D": ...

    def __round__(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D": ...

    def __floor__(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D": ...

    def __ceil__(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D": ...

    def __float__(self:"Vector2D") -> "Vector2D": ...

    def __getitem__(self:"Vector2D", n) -> int|float: ...
    
    @classmethod
    def __normalize__(cls, other:"Vector2D|int|float|tuple|list") -> "Vector2D": ...

    @classmethod
    def zero(cls) -> "Vector2D": ...
    @classmethod
    def one(cls) -> "Vector2D": ...
    @classmethod
    def two(cls) -> "Vector2D": ...
    @classmethod
    def pi(cls) -> "Vector2D": ...
    @classmethod
    def inf(cls) -> "Vector2D": ...
    @classmethod
    def neg_one(cls) -> "Vector2D": ...
    @classmethod
    def neg_two(cls) -> "Vector2D": ...
    @classmethod
    def neg_pi(cls) -> "Vector2D": ...
    @classmethod
    def neg_inf(cls) -> "Vector2D": ...
    @classmethod
    def up(cls) -> "Vector2D": ...
    @classmethod
    def right(cls) -> "Vector2D": ...
    @classmethod
    def down(cls) -> "Vector2D": ...
    @classmethod
    def left(cls) -> "Vector2D": ...
    @classmethod
    def up_right(cls) -> "Vector2D": ...
    @classmethod
    def down_right(cls) -> "Vector2D": ...
    @classmethod
    def up_left(cls) -> "Vector2D": ...
    @classmethod
    def down_left(cls) -> "Vector2D": ...
    @classmethod
    def up_right_norm(cls) -> "Vector2D": ...
    @classmethod
    def down_right_norm(cls) -> "Vector2D": ...
    @classmethod
    def up_left_norm(cls) -> "Vector2D": ...
    @classmethod
    def down_left_norm(cls) -> "Vector2D": ...
    
    @classmethod
    def new_zero(cls) -> "Vector2D": ...
    @classmethod
    def new_one(cls) -> "Vector2D": ...
    @classmethod
    def new_two(cls) -> "Vector2D": ...
    @classmethod
    def new_pi(cls) -> "Vector2D": ...
    @classmethod
    def new_inf(cls) -> "Vector2D": ...
    @classmethod
    def new_neg_one(cls) -> "Vector2D": ...
    @classmethod
    def new_neg_two(cls) -> "Vector2D": ...
    @classmethod
    def new_neg_pi(cls) -> "Vector2D": ...
    @classmethod
    def new_neg_inf(cls) -> "Vector2D": ...
    @classmethod
    def new_up(cls) -> "Vector2D": ...
    @classmethod
    def new_right(cls) -> "Vector2D": ...
    @classmethod
    def new_down(cls) -> "Vector2D": ...
    @classmethod
    def new_left(cls) -> "Vector2D": ...
    @classmethod
    def new_up_right(cls) -> "Vector2D": ...
    @classmethod
    def new_down_right(cls) -> "Vector2D": ...
    @classmethod
    def new_up_left(cls) -> "Vector2D": ...
    @classmethod
    def new_down_left(cls) -> "Vector2D": ...
    @classmethod
    def new_up_right_norm(cls) -> "Vector2D": ...
    @classmethod
    def new_down_right_norm(cls) -> "Vector2D": ...
    @classmethod
    def new_up_left_norm(cls) -> "Vector2D": ...
    @classmethod
    def new_down_left_norm(cls) -> "Vector2D": ...

V2 = Vector2D

V2zero : Vector2D

V2one : Vector2D
V2two : Vector2D
V2pi : Vector2D
V2inf : Vector2D

V2neg_one : Vector2D
V2neg_two : Vector2D
V2neg_pi : Vector2D
V2neg_inf : Vector2D

V2up : Vector2D
V2right : Vector2D
V2down : Vector2D
V2left : Vector2D

V2up_right : Vector2D
V2down_right : Vector2D
V2up_left : Vector2D
V2down_left : Vector2D

V2up_right_norm : Vector2D
V2down_right_norm : Vector2D
V2up_left_norm : Vector2D
V2down_left_norm : Vector2D

VECTORS_4_DIRECTIONS : tuple[Vector2D, Vector2D, Vector2D, Vector2D]
VECTORS_4_SEMIDIRECTIONS : tuple[Vector2D, Vector2D, Vector2D, Vector2D]
VECTORS_4_SEMIDIRECTIONS_NORM : tuple[Vector2D, Vector2D, Vector2D, Vector2D,]
VECTORS_8_DIRECTIONS : tuple[Vector2D, Vector2D, Vector2D, Vector2D, Vector2D, Vector2D, Vector2D, Vector2D]
VECTORS_8_DIRECTIONS_NORM : tuple[Vector2D, Vector2D, Vector2D, Vector2D, Vector2D, Vector2D, Vector2D, Vector2D]


def rgb(r:float, g:float, b:float) -> tuple[float, float, float]:
    return (r,g,b)

def lerp(starting: int|float, ending: int|float, step: int|float=.1) -> float: ...

# def color_lerp(current_c: list|tuple, final_c: list|tuple, step: int|float=.1) -> tuple[float, float, float]:
#     """
#     # Linearly interpolate between two colors.

#     ## Parameters:
#         current_c (tuple or list): The RGB values of the current color as a tuple or list.
#         final_c (tuple or list): The RGB values of the target color as a tuple or list.
#         step (int or float): The interpolation step, ranging from 0.0 (current color) to 1.0 (target color).

#     ## Returns:
#         tuple: The RGB values of the interpolated color as a tuple.

#     ## Example:
#         current_c = (255, 0, 0)

#         final_c = (0, 0, 255)

#         step = 0.5

#         interpolated_color = color_lerp(current_c, final_c, step)

#         print(f"At step {step}: RGB {interpolated_color}")
        
#     This will calculate the color at an interpolation step of 0.5 between (255, 0, 0) and (0, 0, 255).
#     """
#     return tuple(c + (final_c[i] - c) * step for i,c in enumerate(current_c)) #type: ignore

# def color_fade(starting_c: list|tuple, final_c: list|tuple, index: int|float, max_index: int|float) -> tuple[float, float, float]:
#     """
#     # Calculate the color at a specific index of a color fade between two given colors.

#     ## Parameters:
#         starting_c (tuple or list): The RGB values of the starting color as a tuple or list.
#         final_c (tuple or list): The RGB values of the final color as a tuple or list.
#         index (int or float): The current index of the color fade, representing a position
#                               between the starting and final colors.
#         max_index (int or float): The maximum index of the color fade, indicating the endpoint
#                                   position between the starting and final colors.

#     ## Returns:
#         tuple: The RGB values of the color at the specified index as a tuple.

#     ## Example:
#         starting_c = (255, 0, 0)

#         final_c = (0, 0, 255)

#         max_index = 100

#         for i in range(max_index + 1):
        
#             color_at_index = color_fade(starting_c, final_c, i, max_index)

#             print(f"At index {i}: RGB {color_at_index}")
            
#         This will print the colors transitioning from (255, 0, 0) to (0, 0, 255).
#     """
#     return tuple((starting_c[i] - final_c[i]) / max_index * (max_index - index) + final_c[i] for i in range(3)) #type: ignore

# def weighted_color_fade(colors_dict:dict) -> tuple[float, float, float]:
#     """
#     # Calculate the weighted color based on a dictionary of colors and their corresponding weights.

#     ## Parameters:
#         colors_dict (dict): A dictionary where keys represent RGB color values as tuples,
#                             and values represent the weights (floats) for each color.

#     ## Returns:
#         tuple: The RGB values of the calculated weighted color as a tuple.

#     ## Example:
#         colors_dict = {
        
#             (255, 255, 255): 0.1,

#             (0, 0, 0): 0.9,

#         }

#         weighted_color = weighted_color_fade(colors_dict)

#         print(f"Weighted color: RGB {weighted_color}")

#         This will print the weighted color based on the provided dictionary.
#     """
#     colors = colors_dict.keys()
#     weights = colors_dict.values()

#     if float("inf") in weights: return list(colors)[list(weights).index(float("inf"))]
#     return tuple(sum(n[i]*w for n,w in zip(colors, weights)) / sum(weights) for i in range(3)) #type: ignore

# def color_distance(starting_c: list|tuple, final_c: list|tuple, sqrd:bool=True) -> float:
#     """
#     # Calculate the distance between two colors in RGB space.

#     ## Parameters:
#         starting_c (list or tuple): The RGB values of the starting color.
#         final_c (list or tuple): The RGB values of the final color.
#         sqrd (bool, optional): If True, return the squared distance. If False, return
#                                the actual distance. Default is True.

#     ## Returns:
#         float: The squared distance between the two colors if `sqrd` is True, otherwise
#                the actual distance.

#     ## Example:
#         starting_c = [255, 0, 0]

#         final_c = [0, 255, 0]

#         squared_distance = color_distance(starting_c, final_c)

#         print(f"Squared Distance: {squared_distance}")

#         distance = color_distance(starting_c, final_c, sqrd=False)

#         print(f"Actual Distance: {distance}")

#         This will calculate the squared and actual distances between the colors.

#     ## Explanation:
#         The function first calculates the squared distance between the two colors in RGB
#         space. It does this by computing the sum of the squared differences of the RGB
#         components for each color. The squared distance is obtained by taking the square
#         root of this sum.

#         The `sqrd` parameter allows the user to choose between returning the squared
#         distance or the actual distance. If `sqrd` is True, the function returns the
#         squared distance, and if `sqrd` is False, it returns the actual distance.
#     """
#     distance = sum([(starting_c[i]-final_c[i])**2 for i in range(3)])
#     return (distance ** .5) if sqrd else distance

def angular_interpolation(starting_angle: int|float, final_angle: int|float, step: int|float=.1) -> float:
    """
    # Perform angular interpolation between two angles using the shortest distance.

    ## Parameters:
        starting_angle (int or float): The initial angle in radians.
        final_angle (int or float): The target angle in radians to interpolate towards.
        step (int or float, optional): The step size for interpolation in radians. Default is 0.1.

    ## Returns:
        float: The interpolated angle as a result of angular interpolation.

    ## Example:
        starting_angle = 1.0

        final_angle = 5.0

        interpolated_angle = angular_interpolation(starting_angle, final_angle)

        print(f"Interpolated angle: {interpolated_angle}")

        This will print the interpolated angle using angular interpolation.

    ## Explanation:
        The function calculates three distances between the `starting_angle` and the
        `final_angle`. These distances represent possible angular interpolations:
            1. The direct interpolation from `starting_angle` to `final_angle`.
            2. The interpolation by taking a full circle (2 * pi) and then proceeding from
               `starting_angle` to `final_angle`.
            3. The interpolation by taking a full circle (2 * pi) in the opposite direction
               and then proceeding from `starting_angle` to `final_angle`.

        The function then chooses the shortest distance from the three options and returns
        the interpolated angle obtained by multiplying the shortest distance by the `step`
        value.

        The `step` parameter controls the granularity of interpolation. Smaller `step` values
        provide more fine-grained interpolation but may require more iterations.
    """
    ...

def bezier_cubic_interpolation(t: float, p0:Vector2D, p1:Vector2D) -> float: ...

def bezier_quadratic_interpolation(t: float, p0:Vector2D) -> float: ...

def avg_position(*others:"Vector2D") -> Vector2D:
    """
    # Calculate the average position for a variable number of Vector2D others.

    ## Parameters:
        *others (Vector2D): Variable number of Vector2D others representing positions.

    ## Returns:
        Vector2D: The average position as a new Vector2D other.

    ## Example:
        position1 = Vector2D(10, 20)

        position2 = Vector2D(30, 40)

        position3 = Vector2D(50, 60)

        average_pos = avg_position(position1, position2, position3)

        print(average_pos)

        This will print the average position of the three Vector2D others.

    ## Explanation:
        The function takes a variable number of Vector2D others as input, representing positions.
        It calculates the sum of all the Vector2D others using the `sum` function and then divides
        it by the total number of others (length of `others`) to find the average position.

        The result is returned as a new Vector2D other representing the average position.
    """
    ...

def inter_points(ray: list["Vector2D"]|tuple["Vector2D", "Vector2D"], lines: list[tuple["Vector2D", "Vector2D"]], return_inter_lines:bool=False, sort:bool=False, return_empty:bool=False) -> list[tuple[Vector2D | None, tuple[Vector2D | V2, Vector2D | V2]]] | list[Vector2D | None] | list[Vector2D]:
    """
    # Find intersection points between a ray or line segment and multiple line segments.

    ## Parameters:
        ray (list[Vector2D] | tuple[Vector2D, Vector2D]): The ray or line segment represented by two endpoints
            (start and end points).
        lines (list[tuple[Vector2D, Vector2D]]): A list of line segments represented by tuples of their endpoints.
        return_inter_lines (bool, optional): If True, return a list of tuples containing the intersection points and the
            corresponding intersecting line segment. Default is False.
        sort (bool, optional): If True, sort the intersection points by their distance from the ray's start point.
            Default is False.
        return_empty (bool, optional): If True, include None for line segments with no intersection. Default is False.

    ## Returns:
        list[tuple[Vector2D | None, tuple[Vector2D | V2, Vector2D | V2]]] | list[Vector2D | None]:
        - If return_inter_lines is True, returns a list of tuples, each containing:
            - The intersection point (Vector2D) if it exists, or None otherwise.
            - The corresponding intersecting line segment (tuple[Vector2D | V2, Vector2D | V2]).
        - If return_inter_lines is False, returns a list of intersection points (Vector2D) if they exist, or None otherwise.

    # Example:
        ray = [Vector2D(1, 2), Vector2D(5, 3)]
        lines = [(Vector2D(2, 2), Vector2D(4, 4)), (Vector2D(3, 3), Vector2D(6, 2))]
        result = inter_points(ray, lines, return_inter_lines=True, sort=True)
        print(result)

    ## Explanation:
        The function finds the intersection points (if any) between the given ray (or line segment) and the provided list
        of line segments. The intersection points are returned in a list.

        If return_inter_lines is True, the function returns a list of tuples, where each tuple contains the intersection point
        (Vector2D) and the corresponding intersecting line segment (tuple[Vector2D | V2, Vector2D | V2]). If return_inter_lines
        is False, the function returns only a list of intersection points (Vector2D) without the corresponding line segments.

        If sort is True, the intersection points are sorted by their distance from the ray's start point. If sort is False,
        the intersection points are returned in the order they were found.

        If return_empty is True, the function includes None for line segments with no intersection. If return_empty is False,
        line segments with no intersection are omitted from the result.

        Example usage is shown in the "Example" section above.
    """
    def lineLineIntersect(P0:"Vector2D", P1:"Vector2D", Q0:"Vector2D", Q1:"Vector2D") -> "Vector2D | None": ...
    ...

def get_points(position:Vector2D, size:Vector2D, rotation: int|float=0, pos_in_middle:bool=True, return_list:bool=False, clockwise_return:bool=False) -> tuple["Vector2D", "Vector2D", "Vector2D", "Vector2D"] | tuple[list[int|float]|tuple[int|float], list[int|float]|tuple[int|float], list[int|float]|tuple[int|float], list[int|float]|tuple[int|float]]:
    """
    # Generate points for a rectangle based on the given parameters.

    ## Parameters:
        position (Vector2D): The center position of the rectangle.
        size (Vector2D): The size of the rectangle (width and height).
        rotation (int|float, optional): The rotation angle in degrees. Default is 0.
        pos_in_middle (bool, optional): If True, the points represent corners of the rectangle.
                                        If False, the points represent the rectangle's edges.
                                        Default is True.
        return_list (bool, optional): If True, return the points as lists instead of Vector2D others.
                                      Default is False.
        clockwise_return (bool, optional): If True, return the points in clockwise order (A, B, D, C).
                                           If False, return the points in counterclockwise order (A, B, C, D).
                                           Default is False.

    ## Returns:
        tuple: A tuple containing the four points of the rectangle.

    ## Example:
        position = Vector2D(100, 100)

        size = Vector2D(50, 30)

        rotation = 45

        points = get_points(position, size, rotation)

        print(points)

        This will print the four points of the rotated rectangle.

    ## Explanation:
        The function calculates the four points (A, B, C, D) of the rectangle based on the center position,
        size, rotation, and pos_in_middle parameters. The points represent the rectangle's corners if pos_in_middle
        is True, and the edges if pos_in_middle is False.

        The points are returned as Vector2D others unless the return_list parameter is set to True. In that case,
        the points will be returned as lists.

        The clockwise_return parameter determines the order of the points. If True, the points will be returned in
        clockwise order (A, B, D, C), otherwise, they will be returned in counterclockwise order (A, B, C, D).
    """
    ...

def get_lines(position:Vector2D, size:Vector2D, rotation:int|float=0, pos_in_middle:bool=True) -> list[list]:
    """
    # Generate lines representing the sides of a rectangle based on the given parameters.

    ## Parameters:
        position (Vector2D): The center position of the rectangle.
        size (Vector2D): The size of the rectangle (width and height).
        rotation (int|float, optional): The rotation angle in degrees. Default is 0.
        pos_in_middle (bool, optional): If True, the points represent corners of the rectangle.
                                        If False, the points represent the rectangle's edges.
                                        Default is True.

    ## Returns:
        list[list[Vector2D]]: A list of lists, where each sublist contains two Vector2D others
                              representing the start and end points of a line segment.

    ## Example:
        position = Vector2D(100, 100)

        size = Vector2D(50, 30)

        rotation = 45

        lines = get_lines(position, size, rotation)

        print(lines)

        This will print the four line segments representing the sides of the rotated rectangle.

    ## Explanation:
        The function calculates the four points (A, B, C, D) of the rectangle using the `get_points` function
        based on the center position, size, rotation, and pos_in_middle parameters.

        The function then returns a list of lists, where each sublist contains two Vector2D others representing
        the start and end points of a line segment forming the sides of the rectangle.
    """
    ...

def distance_line_point(line_point_a:Vector2D, line_point_b:Vector2D, point_c:Vector2D)  -> float:
    """
    # Calculate the distance between a line segment and a point.

    ## Parameters:
        line_point_a (Vector2D): The starting point of the line segment.
        line_point_b (Vector2D): The ending point of the line segment.
        point_c (Vector2D): The point to which the distance is calculated.

    ## Returns:
        float: The distance between the line segment and the point.

    ## Example:
        line_point_a = Vector2D(0, 0)
        
        line_point_b = Vector2D(10, 0)

        point_c = Vector2D(5, 5)

        distance = distance_line_point(line_point_a, line_point_b, point_c)

        print(distance)

        This will print the distance between the line segment and the point.

    ## Explanation:
        The function calculates the distance between a line segment defined by two points (line_point_a and line_point_b)
        and a third point (point_c).

        It does this by first computing the cross product of vectors (line_point_b - line_point_a) and (line_point_a - point_c).
        The magnitude of the resulting vector is divided by the magnitude of (line_point_b - line_point_a) to obtain the distance.

        The result is returned as a float representing the distance between the line segment and the point.
    """
    ...

def optimize_value_string(value: int|float, precision: int) -> str:
    ...