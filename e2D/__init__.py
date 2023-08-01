import numpy as _np
import math as _mt
import random as _rnd

PI = _mt.pi
HALF_PI = PI/2
QUARTER_PI = PI/4
DOUBLE_PI = PI*2


class Vector2D:
    def __init__(self, x:int|float=0, y:int|float=0) -> None:
        self.x = x
        self.y = y

    def distance_to(self, object:"float|int|Vector2D|V2|list|tuple", squared:bool=True) -> int|float:
        """
        # Calculate the distance between the current Vector2D object and another object.

        # Parameters:
            object (float or int or Vector2D or list|tuple): The other object to which the distance is calculated.
            squared (bool, optional): If True, return the squared distance. If False, return the actual distance.
                                      Default is True.

        # Returns:
            int|float: The squared distance between the current Vector2D object and the other object if `squared` is True,
                      otherwise the actual distance.

        # Example:
            point1 = Vector2D(0, 0)

            point2 = Vector2D(3, 4)

            squared_distance = point1.distance_to(point2)

            print(f"Squared Distance: {squared_distance}")

            distance = point1.distance_to(point2, squared=False)

            print(f"Actual Distance: {distance}")

            This will calculate the squared and actual distances between the two points.

        # Explanation:
            The function calculates the squared distance between the current Vector2D object (self) and another object
            (object) using the formula: (self.x - object.x)**2 + (self.y - object.y)**2.

            The result is returned as the squared distance if `squared` is True, or as the actual distance if `squared` is False.
        """
        object = self.__normalize__(object)
        d = (self.x - object.x)**2 + (self.y - object.y)**2
        return (d**(1/2) if squared else d)

    def angle_to(self, object:"float|int|Vector2D|V2|list|tuple") -> int|float:
        """
        # Calculate the angle between the current Vector2D object and another object.

        # Parameters:
            object (float or int or Vector2D or list|tuple): The other object to which the angle is calculated.

        # Returns:
            int|float: The angle in radians between the current Vector2D object and the other object.

        # Example:
            point1 = Vector2D(0, 0)

            point2 = Vector2D(1, 1)

            angle = point1.angle_to(point2)

            print(f"Angle in radians: {angle}")

            This will calculate the angle in radians between the two points.

        # Explanation:
            The function calculates the angle in radians between the current Vector2D object (self) and another object
            (object) using the `atan2` function from the `math` module.

            The result is returned as the angle in radians.
        """
        object = self.__normalize__(object)
        return _mt.atan2(object.y - self.y, object.x - self.x)

    def point_from_degs(self, rad:int|float, radius:int|float) -> "Vector2D|V2":
        """
        # Calculate a new Vector2D point from the current point based on an angle in radians and a radius.

        # Parameters:
            rad (int|float): The angle in radians.
            radius (int|float): The distance from the current point.

        # Returns:
            Vector2D: A new Vector2D point calculated from the current point.

        # Example:
            point1 = Vector2D(0, 0)

            angle = 45

            distance = 5

            new_point = point1.point_from_degs(_mt.radians(angle), distance)

            print(new_point.x, new_point.y)

            This will calculate a new point 5 units away from point1 at a 45-degree angle.

        # Explanation:
            The function calculates a new Vector2D point based on an angle in radians (rad) and a distance (radius)
            from the current Vector2D point.

            It computes the new x and y coordinates of the point using the trigonometric functions `cos` and `sin`
            to determine the horizontal and vertical components of the new point.

            The result is returned as a new Vector2D point with the calculated coordinates.
        """
        x = radius * _mt.cos(rad) + self.x
        y = radius * _mt.sin(rad) + self.y
        return Vector2D(x, y)

    def copy(self) -> "Vector2D|V2":
        """
        # Create a copy of the current Vector2D object.

        # Returns:
            Vector2D: A new Vector2D object with the same x and y coordinates as the current object.

        # Example:
            point1 = Vector2D(1, 2)

            point2 = point1.copy()

            print(point2.x, point2.y)

            This will print the x and y coordinates of the copied Vector2D object (1, 2).

        # Explanation:
            The function creates a new Vector2D object with the same x and y coordinates as the current object.

            The result is returned as a new Vector2D object, effectively making a copy of the original object.
        """
        return Vector2D(self.x, self.y)

    def absolute_round(self, n=1) -> "Vector2D|V2":
        """
        # Perform an "absolute round" operation on the Vector2D object.

        # Parameters:
            n (int|float, optional): The numeric value to scale the "absolute rounded" vector. Default is 1.

        # Returns:
            Vector2D: The "absolute rounded" Vector2D object scaled by the provided numeric value.

        # Example:
            vector1 = Vector2D(3.3, -4.7)

            result1 = vector1.absolute_round(0.5)

            print(result1.x, result1.y)

            vector2 = Vector2D(-2.8, 1.1)

            result2 = vector2.absolute_round()

            print(result2.x, result2.y)

        # Explanation:
            The function performs an "absolute round" operation on the Vector2D object.

            The "absolute round" operation involves taking the absolute values of both the x and y components of the Vector2D object,
            and then scaling the resulting vector by the provided numeric value (n).

            The default value of n is 1, which means the "absolute rounded" vector will have the same magnitude as the original vector.

            If the provided numeric value (n) is 0, the function returns a Vector2D object with zeros for both components.

            If the provided numeric value (n) is negative, the resulting "absolute rounded" vector will point in the opposite direction
            as the original vector but will have the same magnitude.

            Note: The "absolute round" operation does not perform standard mathematical rounding; instead, it ensures the resulting
            vector points in the same direction as the original vector but has non-negative components.
        """
        s_abs = abs(self)
        return self.no_zero_div_error(s_abs, "zero") * n

    def floor(self, n:int|float=1) -> "Vector2D|V2":
        """
        # Round down the components of the Vector2D object to the nearest integer or the specified numeric value.

        # Parameters:
            n (int|float, optional): The numeric value to round down the components. Default is 1.

        # Returns:
            Vector2D: A new Vector2D object with the components rounded down to the nearest integer or the specified numeric value.

        # Example:
            vector1 = Vector2D(3.3, 4.7)

            result1 = vector1.floor()

            print(result1.x, result1.y)

            vector2 = Vector2D(-2.8, 1.1)

            result2 = vector2.floor(2)

            print(result2.x, result2.y)

        # Explanation:
            The function rounds down the components of the Vector2D object to the nearest integer or the specified numeric value.

            If the provided numeric value (n) is positive, the components of the resulting Vector2D object will be rounded down to
            the nearest multiple of the provided numeric value.

            If the provided numeric value (n) is negative, the function behaves the same as when n is positive.

            If the provided numeric value (n) is 0, the function returns a Vector2D object with zeros for both components.

            If the provided numeric value (n) is not an integer, it will be converted to an integer before performing the rounding.

            Note: The floor operation always moves the components toward negative infinity, regardless of whether the original
            components are positive or negative.
        """
        return self.__floor__(n)

    def ceil(self, n:int|float=1) -> "Vector2D|V2":
        """
        # Round up the components of the Vector2D object to the nearest integer or the specified numeric value.

        # Parameters:
            n (int|float, optional): The numeric value to round up the components. Default is 1.

        # Returns:
            Vector2D: A new Vector2D object with the components rounded up to the nearest integer or the specified numeric value.

        # Example:
            vector1 = Vector2D(3.3, 4.7)

            result1 = vector1.ceil()

            print(result1.x, result1.y)

            vector2 = Vector2D(-2.8, 1.1)

            result2 = vector2.ceil(2)

            print(result2.x, result2.y)

        # Explanation:
            The function rounds up the components of the Vector2D object to the nearest integer or the specified numeric value.

            If the provided numeric value (n) is positive, the components of the resulting Vector2D object will be rounded up to
            the nearest multiple of the provided numeric value.

            If the provided numeric value (n) is negative, the function behaves the same as when n is positive.

            If the provided numeric value (n) is 0, the function returns a Vector2D object with zeros for both components.

            If the provided numeric value (n) is not an integer, it will be converted to an integer before performing the rounding.

            Note: The ceil operation always moves the components toward positive infinity, regardless of whether the original
            components are positive or negative.
        """
        return self.__ceil__(n)

    def randomize(start:"int|float|Vector2D|V2|None"=None, end:"int|float|Vector2D|V2|None"=None) -> "Vector2D|V2": #type: ignore
        """
        # Generate a random Vector2D point within the specified range.

        # Parameters:
            start (int|float or Vector2D or None, optional): The starting point of the range.
                                                        Default is None, which corresponds to (0, 0).
                                                        If numeric, both x and y will have the same value.
            end (int|float or Vector2D or None, optional): The ending point of the range.
                                                        Default is None, which corresponds to (1, 1).
                                                        If numeric, both x and y will have the same value.

        # Returns:
            Vector2D: A new random Vector2D point within the specified range.

        # Example:
            random_point = randomize(Vector2D(10, 20), Vector2D(50, 70))

            print(random_point.x, random_point.y)

            This will print a random point between (10, 20) and (50, 70).

        # Explanation:
            The function generates a random Vector2D point within the specified range defined by `start` and `end`.

            If `start` and `end` are numeric values (int or float), both x and y coordinates will have the same value.

            If `start` and `end` are None, the default range is assumed to be (0, 0) to (1, 1).

            The function first checks if `start` and `end` are Vector2D objects. If not, it creates new Vector2D objects
            based on the numeric values provided or the default values.

            It then generates random x and y coordinates in the range [0, 1) using the `random()` function from the `random` module.
            These random values are then scaled by (end - start) and added to the start point to obtain the final random Vector2D point.
        """
        if not isinstance(start, Vector2D|V2):
            if type(start) in int|float: start = Vector2D(start, start) #type: ignore
            elif type(start) == None: start = Vector2D(0,0)
            else: raise Exception(f"\nArg start must be in [Vector2D, int, float, tuple, list] not a [{type(start)}]\n")
        if not isinstance(end, Vector2D|V2):
            if type(end) in int|float: end = Vector2D(end, end) #type: ignore
            elif type(end) == None: end = Vector2D(1,1)
            else: raise Exception(f"\nArg end must be in [Vector2D, int, float, tuple, list] not a [{type(end)}]\n")
        return start + Vector2D(_rnd.random(), _rnd.random()) * (end - start)

    def mid_point_to(self, *objects) -> float:
        """
        # Calculate the midpoint between the current Vector2D object and one or more other Vector2D objects.

        # Parameters:
            *objects (Vector2D): Variable number of Vector2D objects representing other points.

        # Returns:
            Vector2D: A new Vector2D object representing the midpoint.

        # Example:
            point1 = Vector2D(1, 2)

            point2 = Vector2D(3, 4)

            mid_point = point1.mid_point_to(point2)

            print(mid_point.x, mid_point.y)

            This will print the midpoint between point1 and point2.

        # Explanation:
            The function calculates the midpoint between the current Vector2D object (self)
            and one or more other Vector2D objects (provided as *objects).

            It first sums up all the Vector2D objects (including self) and then divides the sum by
            the total number of points (len(objects) + 1) to find the average point, which represents the midpoint.

            The result is returned as a new Vector2D object.
        """
        return sum(list(objects) + [self]) / (len(objects)+1)

    # Vector2D(x,y) | [(Vector2D(x1,y1), Vector2D(x2,y2)), (Vector2D(x3,y3), Vector2D(x4,y4))]
    def inter_points(self:"Vector2D|V2", self_final_point:"Vector2D|V2", lines:list[tuple["Vector2D|V2", "Vector2D|V2"]], sort:bool=False, return_empty:bool=False) -> list["Vector2D|V2|None"]:
        """
        # Calculate the intersection points between a ray and a list of line segments.

        # Parameters:
            self (Vector2D): The starting point of the ray.
            self_final_point (Vector2D): The ending point of the ray.
            lines (list[tuple[Vector2D, Vector2D]]): A list of line segments represented by tuples of two Vector2D points.
            sort (bool, optional): If True, sort the intersection points by their distance to the starting point (self).
                                Default is False.
            return_empty (bool, optional): If True, include None in the result for lines with no intersection points.
                                        Default is False.

        # Returns:
            list[Vector2D|None]: A list of intersection points as Vector2D objects.
                                If return_empty is True, the list may also include None for lines without intersections.

        # Example:
            point1 = Vector2D(1, 2)

            point2 = Vector2D(3, 4)

            lines = [(Vector2D(2, 1), Vector2D(2, 5)), (Vector2D(0, 3), Vector2D(5, 3))]

            intersections = point1.inter_points(point2, lines)

            print(intersections)

        # Explanation:
            The function calculates the intersection points between the ray defined by the starting point (self)
            and the ending point (self_final_point) and a list of line segments (lines).

            It uses the lineLineIntersect function to check for intersection between the ray and each line segment.

            If sort is True, the intersection points are sorted by their distance to the starting point (self).

            If return_empty is True, the function includes None in the result for lines without intersection points.

            The function returns a list of intersection points as Vector2D objects.
        """
        ray = self() + self_final_point() #type: ignore
        def lineLineIntersect(P0, P1, Q0, Q1) -> tuple[int|float, int|float] | None:
            d = (P1[0]-P0[0]) * (Q1[1]-Q0[1]) + (P1[1]-P0[1]) * (Q0[0]-Q1[0])
            if d == 0:
                return None
            t = ((Q0[0]-P0[0]) * (Q1[1]-Q0[1]) +
                 (Q0[1]-P0[1]) * (Q0[0]-Q1[0])) / d
            u = ((Q0[0]-P0[0]) * (P1[1]-P0[1]) +
                 (Q0[1]-P0[1]) * (P0[0]-P1[0])) / d
            if 0 <= t <= 1 and 0 <= u <= 1:
                return P1[0] * t + P0[0] * (1-t), P1[1] * t + P0[1] * (1-t)
            return None
        collisions = [Vector2D(*line) if line else None for line in [lineLineIntersect(line1[1](), line1[0](), ray[:2], ray[2:]) for line1 in lines] if line or return_empty]
        if sort:
            collisions.sort(key=lambda x: self.distance_to(x, False)) #type: ignore
        return collisions

    def normalize(self, max:int|float=1, min:int|float=0) -> "Vector2D|V2":
        """
        # Normalize the Vector2D object to a new magnitude defined by max while preserving its direction.

        # Parameters:
            max (int|float, optional): The new magnitude to which the Vector2D object will be scaled.
                                      Default is 1.
            min (int|float, optional): The minimum magnitude. If provided, the Vector2D object will not be scaled
                                      below this value. Default is 0.

        # Returns:
            Vector2D: A new Vector2D object with the scaled magnitude.

        # Example:
            vector = Vector2D(3, 4)

            normalized_vector = vector.normalize(5, 2)

            print(normalized_vector.x, normalized_vector.y)

        # Explanation:
            The function scales the Vector2D object to a new magnitude defined by max while preserving its direction.

            It first calculates the current magnitude of the Vector2D object using distance_to method.

            If the current magnitude is not zero, it creates a new Vector2D object with magnitude max using
            point_from_degs method and the angle_to method to preserve the direction.

            If the current magnitude is zero, it returns a new zero vector (VectorZero.copy()).
        """
        return Vector2D(min, min).point_from_degs(Vector2D(min, min).angle_to(self), max) if Vector2D(min, min).distance_to(self) != 0 else VectorZero.copy()

    def no_zero_div_error(self:"Vector2D|V2", n:"int|float|Vector2D|V2", error_mode:str="zero") -> "Vector2D|V2":
        """
        # Handle division between the Vector2D object and a numeric value or another Vector2D object.

        # Parameters:
            n (int|float or Vector2D): The numeric value or Vector2D object for division.
            error_mode (str, optional): The mode to handle division by zero scenarios.
                                        - "zero" (default): Return a Vector2D object with zeros for both components.
                                        - "null": Return a Vector2D object with the original x or y component if available,
                                                   otherwise, return NaN (Not a Number) for the component.

        # Returns:
            Vector2D: A new Vector2D object after division or handling division by zero scenarios.

        # Example:
            vector1 = Vector2D(3, 4)

            result1 = vector1.no_zero_div_error(2)

            print(result1.x, result1.y)

            vector2 = Vector2D(5, 0)

            result2 = vector1.no_zero_div_error(vector2, error_mode="null")

            print(result2.x, result2.y)

        # Explanation:
            The function handles division between the Vector2D object and a numeric value or another Vector2D object.

            If n is a numeric value (int or float):
                - If n is zero, the function returns a Vector2D object with zeros for both components if error_mode is "zero".
                - If error_mode is "null", the function returns a Vector2D object with the original x or y component if available,
                  otherwise, return NaN (Not a Number) for the component.

            If n is a Vector2D object:
                - If n's x or y component is zero, the function returns a Vector2D object with zeros for the corresponding component
                  if error_mode is "zero".
                - If error_mode is "null", the function returns a Vector2D object with the original x or y component if available,
                  otherwise, return NaN (Not a Number) for the component.

            If n is neither a numeric value nor a Vector2D object, the function raises an exception.
        """
        if isinstance(n, int|float):
            if n == 0:
                return Vector2D(0 if error_mode == "zero" else (self.x if error_mode == "null" else _mt.nan), 0 if error_mode == "zero" else (self.y if error_mode == "null" else _mt.nan))
            else:
                return self / n
        elif isinstance(n, Vector2D|V2):
            return Vector2D((0 if error_mode == "zero" else (self.x if error_mode == "null" else _mt.nan)) if n.x == 0 else self.x / n.x, (0 if error_mode == "zero" else (self.y if error_mode == "null" else _mt.nan)) if n.y == 0 else self.y / n.y)
        else:
            raise Exception(f"\nArg n must be in [Vector2D, int, float, tuple, list] not a [{type(n)}]\n")

    def __str__(self) -> str:
        return f"{self.x}, {self.y}"

    def __sub__(self, object:"float|int|Vector2D|V2|list|tuple") -> "Vector2D|V2":
        object = self.__normalize__(object)
        return Vector2D(self.x - object.x, self.y - object.y)

    def __add__(self, object:"float|int|Vector2D|V2|list|tuple") -> "Vector2D|V2":
        object = self.__normalize__(object)
        return Vector2D(self.x + object.x, self.y + object.y)

    def __mod__(self, object:"float|int|Vector2D|V2|list|tuple") -> "Vector2D|V2":
        object = self.__normalize__(object)
        return Vector2D(self.x % object.x, self.y % object.y)

    def __radd__(self, object:"float|int|Vector2D|V2|list|tuple") -> "Vector2D|V2":
        return self.__add__(object)

    def __repr__(self) -> str:
        return f"x:{self.x}\ty:{self.y}"

    def __call__(self, return_tuple=False) -> list|tuple:
        return (self.x, self.y) if return_tuple else [self.x, self.y]

    def __truediv__(self, object:"float|int|Vector2D|V2|list|tuple") -> "Vector2D|V2":
        object = self.__normalize__(object)
        return Vector2D(self.x / object.x, self.y / object.y)

    def __floordiv__(self, object:"float|int|Vector2D|V2|list|tuple") -> "Vector2D|V2":
        object = self.__normalize__(object)
        return Vector2D(self.x // object.x, self.y // object.y)
    
    def __abs__(self) -> "Vector2D|V2":
        return Vector2D(abs(self.x), abs(self.y))

    def __round__(self, n:int|float=1) -> "Vector2D|V2":
        return Vector2D(round(self.x / n) * n, round(self.y / n) * n)

    def __floor__(self, n:int|float=1) -> "Vector2D|V2":
        return Vector2D(_mt.floor(self.x / n) * n, _mt.floor(self.y / n) * n)

    def __ceil__(self, n:int|float=1) -> "Vector2D|V2":
        return Vector2D(_mt.ceil(self.x / n) * n, _mt.ceil(self.y / n) * n)

    def __mul__(self, object:"float|int|Vector2D|V2|list|tuple") -> "Vector2D|V2":
        object = self.__normalize__(object)
        return Vector2D(self.x * object.x, self.y * object.y)

    def __pow__(self, object:"float|int|Vector2D|V2|list|tuple") -> "Vector2D|V2":
        object = self.__normalize__(object)
        return Vector2D(self.x ** object.x, self.y ** object.y)
    
    def __float__(self) -> "Vector2D|V2":
        return Vector2D(float(self.x), float(self.y))

    def __getitem__(self, n) -> int|float:
        if n in [0, "x"]:
            return self.x
        elif n in [1, "y"]:
            return self.y
        else:
            raise IndexError("V2 has only x,y...")
    
    def __normalize__(self, object) -> "Vector2D|V2":
        if not isinstance(object, Vector2D):
            if isinstance(object, int|float):
                return Vector2D(object, object)
            elif isinstance(object, list|tuple):
                return Vector2D(*object[:2])
            else:
                raise TypeError(f"The value {object} is not a num type: [{int|float}] nor an array type: [{list|tuple}]")
        return object

class V2(Vector2D):
    def  __init__(self, x: int|float = 0, y: int|float = 0) -> None:
        super().__init__(x, y)

V2inf = Vector2D(float('inf'), float('inf'))
V2z = VectorZero = Vector2D()
V2one = Vector2D(1, 1)

def rgb(r:int|float, g:int|float, b:int|float) -> tuple[int|float, int|float, int|float]:
    return (r,g,b)

def color_fade(starting_c:list|tuple, final_c:list|tuple, index:int|float, max_index:int|float) -> tuple:
    """
    # Calculate the color at a specific index of a color fade between two given colors.

    # Parameters:
        starting_c (tuple or list): The RGB values of the starting color as a tuple or list.
        final_c (tuple or list): The RGB values of the final color as a tuple or list.
        index (int or float): The current index of the color fade, representing a position
                              between the starting and final colors.
        max_index (int or float): The maximum index of the color fade, indicating the endpoint
                                  position between the starting and final colors.

    # Returns:
        tuple: The RGB values of the color at the specified index as a tuple.

    # Example:
        starting_c = (255, 0, 0)

        final_c = (0, 0, 255)

        max_index = 100

        for i in range(max_index + 1):
        
            color_at_index = color_fade(starting_c, final_c, i, max_index)

            print(f"At index {i}: RGB {color_at_index}")
            
        This will print the colors transitioning from (255, 0, 0) to (0, 0, 255).
    """
    return tuple((starting_c[i] - final_c[i]) / max_index * (max_index - index) + final_c[i] for i in range(3))

def weighted_color_fade(colors_dict:dict) -> tuple:
    """
    # Calculate the weighted color based on a dictionary of colors and their corresponding weights.

    # Parameters:
        colors_dict (dict): A dictionary where keys represent RGB color values as tuples,
                            and values represent the weights (floats) for each color.

    # Returns:
        tuple: The RGB values of the calculated weighted color as a tuple.

    # Example:
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
    return tuple(sum(n[i]*w for n,w in zip(colors, weights)) / sum(weights) for i in range(3))

def angular_interpolation(starting_angle:int|float, final_angle:int|float, step:int|float=.1) -> float:
    """
    # Perform angular interpolation between two angles using the shortest distance.

    # Parameters:
        starting_angle (int or float): The initial angle in radians.
        final_angle (int or float): The target angle in radians to interpolate towards.
        step (int or float, optional): The step size for interpolation in radians. Default is 0.1.

    # Returns:
        float: The interpolated angle as a result of angular interpolation.

    # Example:
        starting_angle = 1.0

        final_angle = 5.0

        interpolated_angle = angular_interpolation(starting_angle, final_angle)

        print(f"Interpolated angle: {interpolated_angle}")

        This will print the interpolated angle using angular interpolation.

    # Explanation:
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

def color_distance(starting_c:list|tuple, final_c:list|tuple, sqrd:bool=True) -> float:
    """
    # Calculate the distance between two colors in RGB space.

    # Parameters:
        starting_c (list or tuple): The RGB values of the starting color.
        final_c (list or tuple): The RGB values of the final color.
        sqrd (bool, optional): If True, return the squared distance. If False, return
                               the actual distance. Default is True.

    # Returns:
        float: The squared distance between the two colors if `sqrd` is True, otherwise
               the actual distance.

    # Example:
        starting_c = [255, 0, 0]

        final_c = [0, 255, 0]

        squared_distance = color_distance(starting_c, final_c)

        print(f"Squared Distance: {squared_distance}")

        distance = color_distance(starting_c, final_c, sqrd=False)

        print(f"Actual Distance: {distance}")

        This will calculate the squared and actual distances between the colors.

    # Explanation:
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

def avg_position(*objects:"Vector2D|V2") -> Vector2D|V2:
    """
    # Calculate the average position for a variable number of Vector2D objects.

    # Parameters:
        *objects (Vector2D): Variable number of Vector2D objects representing positions.

    # Returns:
        Vector2D: The average position as a new Vector2D object.

    # Example:
        position1 = Vector2D(10, 20)

        position2 = Vector2D(30, 40)

        position3 = Vector2D(50, 60)

        average_pos = avg_position(position1, position2, position3)

        print(average_pos)

        This will print the average position of the three Vector2D objects.

    # Explanation:
        The function takes a variable number of Vector2D objects as input, representing positions.
        It calculates the sum of all the Vector2D objects using the `sum` function and then divides
        it by the total number of objects (length of `objects`) to find the average position.

        The result is returned as a new Vector2D object representing the average position.
    """
    return sum(list(objects)) / (len(objects)) # type: ignore

def get_points(position:Vector2D|V2, size:Vector2D|V2, rotation:int|float=0, pos_in_middle:bool=True, return_list:bool=False, clockwise_return:bool=False) -> tuple["Vector2D|V2", "Vector2D|V2", "Vector2D|V2", "Vector2D|V2"] | tuple[list[int|float]|tuple[int|float], list[int|float]|tuple[int|float], list[int|float]|tuple[int|float], list[int|float]|tuple[int|float]]:
    """
    # Generate points for a rectangle based on the given parameters.

    # Parameters:
        position (Vector2D): The center position of the rectangle.
        size (Vector2D): The size of the rectangle (width and height).
        rotation (int|float, optional): The rotation angle in degrees. Default is 0.
        pos_in_middle (bool, optional): If True, the points represent corners of the rectangle.
                                        If False, the points represent the rectangle's edges.
                                        Default is True.
        return_list (bool, optional): If True, return the points as lists instead of Vector2D objects.
                                      Default is False.
        clockwise_return (bool, optional): If True, return the points in clockwise order (A, B, D, C).
                                           If False, return the points in counterclockwise order (A, B, C, D).
                                           Default is False.

    # Returns:
        tuple: A tuple containing the four points of the rectangle.

    # Example:
        position = Vector2D(100, 100)

        size = Vector2D(50, 30)

        rotation = 45

        points = get_points(position, size, rotation)

        print(points)

        This will print the four points of the rotated rectangle.

    # Explanation:
        The function calculates the four points (A, B, C, D) of the rectangle based on the center position,
        size, rotation, and pos_in_middle parameters. The points represent the rectangle's corners if pos_in_middle
        is True, and the edges if pos_in_middle is False.

        The points are returned as Vector2D objects unless the return_list parameter is set to True. In that case,
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

def get_lines(position:Vector2D|V2, size:Vector2D|V2, rotation:int|float=0, pos_in_middle:bool=True) -> list[list]:
    """
    # Generate lines representing the sides of a rectangle based on the given parameters.

    # Parameters:
        position (Vector2D): The center position of the rectangle.
        size (Vector2D): The size of the rectangle (width and height).
        rotation (int|float, optional): The rotation angle in degrees. Default is 0.
        pos_in_middle (bool, optional): If True, the points represent corners of the rectangle.
                                        If False, the points represent the rectangle's edges.
                                        Default is True.

    # Returns:
        list[list[Vector2D]]: A list of lists, where each sublist contains two Vector2D objects
                              representing the start and end points of a line segment.

    # Example:
        position = Vector2D(100, 100)

        size = Vector2D(50, 30)

        rotation = 45

        lines = get_lines(position, size, rotation)

        print(lines)

        This will print the four line segments representing the sides of the rotated rectangle.

    # Explanation:
        The function calculates the four points (A, B, C, D) of the rectangle using the `get_points` function
        based on the center position, size, rotation, and pos_in_middle parameters.

        The function then returns a list of lists, where each sublist contains two Vector2D objects representing
        the start and end points of a line segment forming the sides of the rectangle.
    """
    A, B, C, D = get_points(position, size, rotation, pos_in_middle)
    return [[A, B], [A, C], [C, D], [D, B]]

def distance_line_point(line_point_a:Vector2D|V2, line_point_b:Vector2D|V2, point_c:Vector2D|V2)  -> float:
    """
    # Calculate the distance between a line segment and a point.

    # Parameters:
        line_point_a (Vector2D): The starting point of the line segment.
        line_point_b (Vector2D): The ending point of the line segment.
        point_c (Vector2D): The point to which the distance is calculated.

    # Returns:
        float: The distance between the line segment and the point.

    # Example:
        line_point_a = Vector2D(0, 0)
        
        line_point_b = Vector2D(10, 0)

        point_c = Vector2D(5, 5)

        distance = distance_line_point(line_point_a, line_point_b, point_c)

        print(distance)

        This will print the distance between the line segment and the point.

    # Explanation:
        The function calculates the distance between a line segment defined by two points (line_point_a and line_point_b)
        and a third point (point_c).

        It does this by first computing the cross product of vectors (line_point_b - line_point_a) and (line_point_a - point_c).
        The magnitude of the resulting vector is divided by the magnitude of (line_point_b - line_point_a) to obtain the distance.

        The result is returned as a float representing the distance between the line segment and the point.
    """
    return float(_np.linalg.norm(_np.cross((line_point_b-line_point_a)(), (line_point_a-point_c)()))/_np.linalg.norm((line_point_b-line_point_a)()))
