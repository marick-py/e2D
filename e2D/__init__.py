from __future__ import annotations

import numpy as _np
import math as _mt
import random as _rnd

PI = _mt.pi
HALF_PI = PI/2
QUARTER_PI = PI/4
DOUBLE_PI = PI*2

# regular expression to remove comments:
# """([\s\S]*?)"""

# 

class Vector2D:
    round_values_on_print :int|float= 2
    def __init__(self:"Vector2D", x:int|float=0.0, y:int|float=0.0) -> None:
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
        self.x = x
        self.y = y
    
    def set(self:"Vector2D", x:int|float=0, y:int|float=0) -> None:
        """
        # Change the components of the Vector2D other without creating a new one.

        ## Parameters:
            x (int | float, optional): The new x-component to set. Default is 0.
            y (int | float, optional): The new y-component to set. Default is 0.

        ## Example:
            vector = Vector2D(1, 2)
            vector.set(3, -4)
            print(vector.x, vector.y)  # Output: 3, -4

        ## Explanation:
            The method updates the x and y components of the Vector2D other to the specified values.

            If no arguments are provided, the default values for x and y are both set to 0.

            The x and y components can be integers or floating-point numbers.

            The method does not return any value, but it modifies the Vector2D other in place.

            Example usage is shown in the "Example" section above.
        """
        self.x = x
        self.y = y

    def distance_to(self:"Vector2D", other:"float|int|Vector2D|list|tuple", sqrd:bool=True) -> int|float:
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
        other = self.__normalize__(other)
        d = (self.x - other.x)**2 + (self.y - other.y)**2
        return (d**(1/2) if sqrd else d)

    def angle(self:"Vector2D") -> int|float:
        return _mt.atan2(self.y, self.x)

    def angle_to(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> int|float:
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
        other = self.__normalize__(other)
        return _mt.atan2(other.y - self.y, other.x - self.x)

    def point_from_degs(self:"Vector2D", degs:int|float, radius:int|float) -> "Vector2D":
        """
        # Calculate a new Vector2D point from the current point based on an angle in degs and a radius.

        ## Parameters:
            rad (int|float): The angle in degs.
            radius (int|float): The distance from the current point.

        ## Returns:
            Vector2D: A new Vector2D point calculated from the current point.

        ## Example:
            point1 = Vector2D(0, 0)

            angle = 45

            distance = 5

            new_point = point1.point_from_degs(angle, distance)

            print(new_point.x, new_point.y)

            This will calculate a new point 5 units away from point1 at a 45-degree angle.

        ## Explanation:
            The function calculates a new Vector2D point based on an angle in degs (degs) and a distance (radius)
            from the current Vector2D point.

            It computes the new x and y coordinates of the point using the trigonometric functions `cos` and `sin`
            to determine the horizontal and vertical components of the new point.

            The result is returned as a new Vector2D point with the calculated coordinates.
        """
        x = radius * _mt.cos(_mt.radians(degs)) + self.x
        y = radius * _mt.sin(_mt.radians(degs)) + self.y
        return Vector2D(x, y)
    
    def point_from_rads(self:"Vector2D", rad:int|float, radius:int|float) -> "Vector2D":
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
        x = radius * _mt.cos(rad) + self.x
        y = radius * _mt.sin(rad) + self.y
        return Vector2D(x, y)

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
        return Vector2D(self.x, self.y)

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
        return self.no_zero_div_error(abs(self), "zero")

    def floor(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        return self.__floor__(n)

    def ceil(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        return self.__ceil__(n)
    
    def round(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        return self.__round__(n)

    def randomize(start:"int|float|Vector2D|None"=None, end:"int|float|Vector2D|None"=None) -> "Vector2D": #type: ignore
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
        if not any(isinstance(start, cls) for cls in {Vector2D, V2}):
            if type(start) in int|float: start = Vector2D(start, start) #type: ignore
            elif type(start) == None: start = Vector2D(0,0)
            else: raise Exception(f"\nArg start must be in [Vector2D, int, float, tuple, list] not a [{type(start)}]\n")
        if not any(isinstance(end, cls) for cls in {Vector2D, V2}):
            if type(end) in int|float: end = Vector2D(end, end) #type: ignore
            elif type(end) == None: end = Vector2D(1,1)
            else: raise Exception(f"\nArg end must be in [Vector2D, int, float, tuple, list] not a [{type(end)}]\n")
        return start + Vector2D(_rnd.random(), _rnd.random()) * (end - start) #type: ignore
    
    def dot_product(self, other:"float|int|Vector2D|list|tuple") -> float:
        other = self.__normalize__(other)
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
        return self.x * other.x + self.y * other.y

    def normalize(self) -> "Vector2D":
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
        mag = self.length()
        if mag == 0:
            return self
        return Vector2D(self.x / mag, self.y / mag)

    def projection(self, other:"float|int|Vector2D|list|tuple") -> "Vector2D":
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
        other = self.__normalize__(other)
        dot_product = self.dot_product(other)
        magnitude_product = other.length() ** 2
        if magnitude_product == 0:
            raise ValueError("Cannot calculate projection for zero vectors.")
        return other * (dot_product / magnitude_product)

    def reflection(self, normal:"float|int|Vector2D|list|tuple") -> "Vector2D":
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
        normal = self.__normalize__(normal)
        projection = self.projection(normal)
        return self - projection * 2

    def cartesian_to_polar(self) -> tuple:
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
        r = self.length()
        theta = _mt.atan2(self.y, self.x)
        return r, theta

    @classmethod
    def polar_to_cartesian(cls, r: float|int, theta: float|int) -> "Vector2D":
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
        x = r * _mt.cos(theta)
        y = r * _mt.sin(theta)
        return cls(x, y)

    def cartesian_to_complex(self) -> complex:
        return self.x + self.y * 1j

    @classmethod
    def complex_to_cartesian(cls, complex_n: complex) -> "Vector2D":
        return cls(complex_n.real, complex_n.imag)

    def length(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** .5

    def lerp(self, other:"float|int|Vector2D|list|tuple", t: float) -> "Vector2D":
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
        other = self.__normalize__(other)
        if not 0 <= t <= 1:
            raise ValueError("t must be between 0 and 1 for linear interpolation.")
        return Vector2D(self.x + (other.x - self.x) * t, self.y + (other.y - self.y) * t)

    def rotate(self, angle: int|float, center:"float|int|Vector2D|list|tuple|None"=None) -> "Vector2D":
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
        if center is None: center = V2z
        else: center = self.__normalize__(center)
        translated = self - center
        cos_angle = _mt.cos(angle)
        sin_angle = _mt.sin(angle)
        return Vector2D(translated.x * cos_angle - translated.y * sin_angle, translated.x * sin_angle + translated.y * cos_angle) + center

    def no_zero_div_error(self:"Vector2D", n:"int|float|Vector2D", error_mode:str="zero") -> "Vector2D":
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
        if any(isinstance(n, cls) for cls in {int, float}):
            if n == 0:
                return Vector2D(0 if error_mode == "zero" else (self.x if error_mode == "null" else _mt.nan), 0 if error_mode == "zero" else (self.y if error_mode == "null" else _mt.nan))
            else:
                return self / n
        elif any(isinstance(n, cls) for cls in {Vector2D, V2}):
            return Vector2D((0 if error_mode == "zero" else (self.x if error_mode == "null" else _mt.nan)) if n.x == 0 else self.x / n.x, (0 if error_mode == "zero" else (self.y if error_mode == "null" else _mt.nan)) if n.y == 0 else self.y / n.y) #type: ignore
        else:
            raise Exception(f"\nArg n must be in [Vector2D, int, float, tuple, list] not a [{type(n)}]\n")

    def min(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(min(self.x, other.x), min(self.y, other.y))
    
    def max(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(max(self.x, other.x), max(self.y, other.y))

    def advanced_stringify(self:"Vector2D", precision:float|None=None, use_scientific_notation:bool=False, return_as_list=False) -> str:
        precision = self.round_values_on_print if precision == None else precision
        def optimize(value) -> str:
            abs_value = abs(value)
            if abs_value < 1/10**precision and abs_value != 0:
                return f"{value:.{precision}e}"
            elif abs_value < 10**precision:
                return f"{value:.{precision}f}".rstrip('0').rstrip('.')
            else:
                return f"{value:.{precision}e}"
        if return_as_list:
            return [optimize(self.x), optimize(self.y)] if use_scientific_notation else [f"{self.x:.{precision}f}", f"{self.y:.{precision}f}"] #type: ignore
        return f"{optimize(self.x)}, {optimize(self.y)}" if use_scientific_notation else f"{self.x:.{precision}f}, {self.y:.{precision}f}"

    def __str__(self:"Vector2D") -> str:
        return f"{self.x:.{self.round_values_on_print}f}, {self.y:.{self.round_values_on_print}f}"

    def __repr__(self:"Vector2D") -> str:
        return f"x:{self.x:.{self.round_values_on_print}f}\ty:{self.y:.{self.round_values_on_print}f}"

    def __call__(self:"Vector2D", return_tuple=False) -> list|tuple:
        return (self.x, self.y) if return_tuple else [self.x, self.y]

    # normal operations     Vector2D + a
    def __add__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(self.x * other.x, self.y * other.y)

    def __mod__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(self.x % other.x, self.y % other.y)
    
    def __pow__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(self.x ** other.x, self.y ** other.y)

    def __truediv__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(self.x / other.x, self.y / other.y)

    def __floordiv__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(self.x // other.x, self.y // other.y)
    
    # right operations      a + Vector2D
    def __radd__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        return self.__add__(other)
    
    def __rsub__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(other.x - self.x, other.y - self.y)
    
    def __rmul__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        return self.__mul__(other)

    def __rmod__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(other.x % self.x, other.y % self.y)
    
    def __rpow__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(other.x ** self.x, other.y ** self.y)

    def __rtruediv__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(other.x / self.x, other.y / self.y)

    def __rfloordiv__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        return Vector2D(other.x // self.x, other.y // self.y)
    
    # in-place operations   Vector2D += a
    def __iadd__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __imul__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        self.x *= other.x
        self.y *= other.y
        return self

    def __itruediv__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        self.x /= other.x
        self.y /= other.y
        return self
    
    def __imod__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        self.x %= other.x
        self.y %= other.y
        return self
    
    def __ipow__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        self.x **= other.x
        self.y **= other.y
        return self

    def __ifloordiv__(self:"Vector2D", other:"float|int|Vector2D|list|tuple") -> "Vector2D":
        other = self.__normalize__(other)
        self.x //= other.x
        self.y //= other.y
        return self

    # comparasion
    def __eq__(self, other) -> bool:
        try: other = self.__normalize__(other)
        except: return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __abs__(self:"Vector2D") -> "Vector2D":
        return Vector2D(abs(self.x), abs(self.y))

    def __round__(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        n = self.__normalize__(n)
        return Vector2D(round(self.x / n.x) * n.x, round(self.y / n.y) * n.y)

    def __floor__(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        n = self.__normalize__(n)
        return Vector2D(_mt.floor(self.x / n.x) * n.x, _mt.floor(self.y / n.y) * n.y)

    def __ceil__(self:"Vector2D", n:"int|float|Vector2D"=1) -> "Vector2D":
        n = self.__normalize__(n)
        return Vector2D(_mt.ceil(self.x / n.x) * n.x, _mt.ceil(self.y / n.y) * n.y)
    
    def __float__(self:"Vector2D") -> "Vector2D":
        return Vector2D(float(self.x), float(self.y))

    def __getitem__(self:"Vector2D", n) -> int|float:
        if n in [0, "x"]:
            return self.x
        elif n in [1, "y"]:
            return self.y
        else:
            raise IndexError("V2 has only x,y...")
    
    def __normalize__(self:"Vector2D", other) -> "Vector2D":
        if not isinstance(other, Vector2D):
            if any(isinstance(other, cls) for cls in {int, float}):
                return Vector2D(other, other)
            elif any(isinstance(other, cls) for cls in {list, tuple}):
                return Vector2D(*other[:2])
            else:
                try:
                    return Vector2D(other.x, other.y)
                except:
                    raise TypeError(f"pThe value {other} of type {type(other)} is not a num type: [{int|float}] nor an array type: [{list|tuple}]")
        return other

from .cvb import *

V2 = Vector2D

V2inf = Vector2D(float('inf'), float('inf'))
V2z = VectorZero = Vector2D()
V2one = Vector2D(1.0, 1.0)

def rgb(r:float, g:float, b:float) -> tuple[float, float, float]:
    return (r,g,b)

def color_lerp(current_c:list|tuple, final_c:list|tuple, step:int|float=.1) -> tuple[float, float, float]:
    """
    # Linearly interpolate between two colors.

    ## Parameters:
        current_c (tuple or list): The RGB values of the current color as a tuple or list.
        final_c (tuple or list): The RGB values of the target color as a tuple or list.
        step (int or float): The interpolation step, ranging from 0.0 (current color) to 1.0 (target color).

    ## Returns:
        tuple: The RGB values of the interpolated color as a tuple.

    ## Example:
        current_c = (255, 0, 0)

        final_c = (0, 0, 255)

        step = 0.5

        interpolated_color = color_lerp(current_c, final_c, step)

        print(f"At step {step}: RGB {interpolated_color}")
        
    This will calculate the color at an interpolation step of 0.5 between (255, 0, 0) and (0, 0, 255).
    """
    return tuple(c + (final_c[i] - c) * step for i,c in enumerate(current_c)) #type: ignore

def color_fade(starting_c:list|tuple, final_c:list|tuple, index:int|float, max_index:int|float) -> tuple[float, float, float]:
    """
    # Calculate the color at a specific index of a color fade between two given colors.

    ## Parameters:
        starting_c (tuple or list): The RGB values of the starting color as a tuple or list.
        final_c (tuple or list): The RGB values of the final color as a tuple or list.
        index (int or float): The current index of the color fade, representing a position
                              between the starting and final colors.
        max_index (int or float): The maximum index of the color fade, indicating the endpoint
                                  position between the starting and final colors.

    ## Returns:
        tuple: The RGB values of the color at the specified index as a tuple.

    ## Example:
        starting_c = (255, 0, 0)

        final_c = (0, 0, 255)

        max_index = 100

        for i in range(max_index + 1):
        
            color_at_index = color_fade(starting_c, final_c, i, max_index)

            print(f"At index {i}: RGB {color_at_index}")
            
        This will print the colors transitioning from (255, 0, 0) to (0, 0, 255).
    """
    return tuple((starting_c[i] - final_c[i]) / max_index * (max_index - index) + final_c[i] for i in range(3)) #type: ignore

def weighted_color_fade(colors_dict:dict) -> tuple[float, float, float]:
    """
    # Calculate the weighted color based on a dictionary of colors and their corresponding weights.

    ## Parameters:
        colors_dict (dict): A dictionary where keys represent RGB color values as tuples,
                            and values represent the weights (floats) for each color.

    ## Returns:
        tuple: The RGB values of the calculated weighted color as a tuple.

    ## Example:
        colors_dict = {
        
            (255, 255, 255): 0.1,

            (0, 0, 0): 0.9,

        }

        weighted_color = weighted_color_fade(colors_dict)

        print(f"Weighted color: RGB {weighted_color}")

        This will print the weighted color based on the provided dictionary.
    """
    colors = colors_dict.keys()
    weights = colors_dict.values()

    if float("inf") in weights: return list(colors)[list(weights).index(float("inf"))]
    return tuple(sum(n[i]*w for n,w in zip(colors, weights)) / sum(weights) for i in range(3)) #type: ignore

def color_distance(starting_c:list|tuple, final_c:list|tuple, sqrd:bool=True) -> float:
    """
    # Calculate the distance between two colors in RGB space.

    ## Parameters:
        starting_c (list or tuple): The RGB values of the starting color.
        final_c (list or tuple): The RGB values of the final color.
        sqrd (bool, optional): If True, return the squared distance. If False, return
                               the actual distance. Default is True.

    ## Returns:
        float: The squared distance between the two colors if `sqrd` is True, otherwise
               the actual distance.

    ## Example:
        starting_c = [255, 0, 0]

        final_c = [0, 255, 0]

        squared_distance = color_distance(starting_c, final_c)

        print(f"Squared Distance: {squared_distance}")

        distance = color_distance(starting_c, final_c, sqrd=False)

        print(f"Actual Distance: {distance}")

        This will calculate the squared and actual distances between the colors.

    ## Explanation:
        The function first calculates the squared distance between the two colors in RGB
        space. It does this by computing the sum of the squared differences of the RGB
        components for each color. The squared distance is obtained by taking the square
        root of this sum.

        The `sqrd` parameter allows the user to choose between returning the squared
        distance or the actual distance. If `sqrd` is True, the function returns the
        squared distance, and if `sqrd` is False, it returns the actual distance.
    """
    distance = sum([(starting_c[i]-final_c[i])**2 for i in range(3)])
    return (distance ** .5) if sqrd else distance

def angular_interpolation(starting_angle:int|float, final_angle:int|float, step:int|float=.1) -> float:
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
    distances = (final_angle - starting_angle, final_angle - DOUBLE_PI - starting_angle, final_angle + DOUBLE_PI - starting_angle)
    return min(distances, key=abs) * step

def bezier_cubic_interpolation(t:float, p0:Vector2D, p1:Vector2D) -> float:
    return t*p0.y*3*(1 - t)**2 + p1.y*3*(1 - t) * t**2 + t**3

def bezier_quadratic_interpolation(t:float, p0:Vector2D) -> float:
    return 2*(1-t)*t*p0.y+t**2

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
    return sum(others) / len(others) #type: ignore

def inter_points(ray:list["Vector2D"]|tuple["Vector2D", "Vector2D"], lines:list[tuple["Vector2D", "Vector2D"]], return_inter_lines:bool=False, sort:bool=False, return_empty:bool=False) -> list[tuple[Vector2D | None, tuple[Vector2D | V2, Vector2D | V2]]] | list[Vector2D | None] | list[Vector2D]:
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
    def lineLineIntersect(P0:"Vector2D", P1:"Vector2D", Q0:"Vector2D", Q1:"Vector2D") -> "Vector2D | None":
        d = (P1.x-P0.x) * (Q1.y-Q0.y) + (P1.y-P0.y) * (Q0.x-Q1.x)
        if d == 0:
            return None
        t = ((Q0.x-P0.x) * (Q1.y-Q0.y) + (Q0.y-P0.y) * (Q0.x-Q1.x)) / d
        u = ((Q0.x-P0.x) * (P1.y-P0.y) + (Q0.y-P0.y) * (P0.x-P1.x)) / d
        if 0 <= t <= 1 and 0 <= u <= 1:
            return Vector2D(P1.x * t + P0.x * (1-t), P1.y * t + P0.y * (1-t))
        return None
    
    if return_inter_lines:
        collisions = [(ip, line) for line in lines if ((ip:=lineLineIntersect(line[1], line[0], ray[1], ray[0]))!=None or return_empty)]
        return sorted(collisions, key=lambda x: ray[0].distance_to(x[0], False) if x[0] != None else _mt.inf) if sort else collisions
    else:
        collisions = [ip for line in lines if ((ip:=lineLineIntersect(line[1], line[0], ray[1], ray[0]))!=None or return_empty)]
        return sorted(collisions, key=lambda x: ray[0].distance_to(x, False) if x != None else _mt.inf) if sort else collisions

def get_points(position:Vector2D, size:Vector2D, rotation:int|float=0, pos_in_middle:bool=True, return_list:bool=False, clockwise_return:bool=False) -> tuple["Vector2D", "Vector2D", "Vector2D", "Vector2D"] | tuple[list[int|float]|tuple[int|float], list[int|float]|tuple[int|float], list[int|float]|tuple[int|float], list[int|float]|tuple[int|float]]:
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
    if pos_in_middle:
        A, B, C, D = [position.point_from_degs(rotation + V2z.angle_to(size/-2),                 V2z.distance_to(size/-2)),
                      position.point_from_degs(rotation + V2z.angle_to(Vector2D(size.x, -1*size.y)/2), V2z.distance_to(Vector2D(size.x, -1*size.y)/2)),
                      position.point_from_degs(rotation + V2z.angle_to(Vector2D(-1*size.x, size.y)/2), V2z.distance_to(Vector2D(-1*size.x, size.y)/2)),
                      position.point_from_degs(rotation + V2z.angle_to(size/2),                  V2z.distance_to(size/2))]
    else:
        A, B, C, D = [position.copy(),
                      position.point_from_degs(rotation + V2z.angle_to(Vector2D(size.x, 0)), V2z.distance_to(Vector2D(size.x, 0))),
                      position.point_from_degs(rotation + V2z.angle_to(Vector2D(0, size.y)), V2z.distance_to(Vector2D(0, size.y))),
                      position.point_from_degs(rotation + V2z.angle_to(size),                V2z.distance_to(size))]
    points = (A, B, C, D) if not clockwise_return else (A, B, D, C)
    return points if not return_list else tuple(x() for x in points)

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
    A, B, C, D = get_points(position, size, rotation, pos_in_middle)
    return [[A, B], [A, C], [C, D], [D, B]]

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
    return float(_np.linalg.norm(_np.cross((line_point_b-line_point_a)(), (line_point_a-point_c)()))/_np.linalg.norm((line_point_b-line_point_a)())) #type: ignore

def optimize_value_string(value:int|float, precision:int) -> str:
    abs_value = abs(value)
    if abs_value < 1/10**precision and abs_value != 0:
        return f"{value:.{precision}e}"
    elif abs_value < 10**precision:
        return f"{value:.{precision}f}".rstrip('0').rstrip('.')
    else:
        return f"{value:.{precision}e}"