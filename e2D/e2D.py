import numpy as _np
import math as _mt
import random as _rnd

PI = _mt.pi
HALF_PI = PI/2
QUARTER_PI = PI/4
DOUBLE_PI = PI*2

DEFAULT_MOUSE_BUTTON_MODE = 0
OVER_MOUSE_BUTTON_MODE = 1
CLICKED_MOUSE_BUTTON_MOVE = 2

KEY_MODE_PRESSED = 0
KEY_MODE_JUST_PRESSED = 1
KEY_MODE_JUST_RELEASED = 2

CALLBACK_MODE_ON_PRESSED = 0
CALLBACK_MODE_ON_RELEASED = 1

SCANCODES = {"":0,"backspace":8,"tab":9,"return":13,"escape":27,"space":32,"!":33,"\"":34,"#":35,"$":36,"%":37,"&":38,"'":39,"(":40,")":41,"*":42,"+":43,",":44,"-":45,".":46,"/":47,"0":48,"1":49,"2":50,"3":51,"4":52,"5":53,"6":54,"7":55,"8":56,"9":57,":":58,";":59,"<":60,"=":61,">":62,"?":63,"@":64,"[":91,"\\":92,"]":93,"^":94,"_":95,"`":96,"a":97,"b":98,"c":99,"d":100,"e":101,"f":102,"g":103,"h":104,"i":105,"j":106,"k":107,"l":108,"m":109,"n":110,"o":111,"p":112,"q":113,"r":114,"s":115,"t":116,"u":117,"v":118,"w":119,"x":120,"y":121,"z":122,"delete":127,"caps lock":1073741881,"f1":1073741882,"f2":1073741883,"f3":1073741884,"f4":1073741885,"f5":1073741886,"f6":1073741887,"f7":1073741888,"f8":1073741889,"f9":1073741890,"f10":1073741891,"f11":1073741892,"f12":1073741893,"print screen":1073741894,"scroll lock":1073741895,"break":1073741896,"insert":1073741897,"home":1073741898,"page up":1073741899,"end":1073741901,"page down":1073741902,"right":1073741903,"left":1073741904,"down":1073741905,"up":1073741906,"numlock":1073741907,"[/]":1073741908,"[*]":1073741909,"[-]":1073741910,"[+]":1073741911,"enter":1073741912,"[1]":1073741913,"[2]":1073741914,"[3]":1073741915,"[4]":1073741916,"[5]":1073741917,"[6]":1073741918,"[7]":1073741919,"[8]":1073741920,"[9]":1073741921,"[0]":1073741922,"[.]":1073741923,"power":1073741926,"equals":1073741927,"f13":1073741928,"f14":1073741929,"f15":1073741930,"help":1073741941,"menu":1073741942,"sys req":1073741978,"clear":1073741980,"euro":1073742004,"CurrencySubUnit":1073742005,"left ctrl":1073742048,"left shift":1073742049,"left alt":1073742050,"left meta":1073742051,"right ctrl":1073742052,"right shift":1073742053,"right alt":1073742054,"right meta":1073742055,"alt gr":1073742081,"AC Back":1073742094}
SCANCODES_NUMS = [i for i in SCANCODES.values()]

NUM_TYPE = int|float
ARRAY_TYPE = list|tuple

class Mouse:
    """
    # Need the pygame module to be imported as pg.
    """
    def __init__(self, parent) -> None:
        self.parent = parent
        self.pressed :list= [False, False, False]
        self.just_pressed :list= [False, False, False]
        self.just_released :list= [False, False, False]
    
    def update(self) -> None:
        self.position = V2(*pg.mouse.get_pos()) # type: ignore
        last_pressed = self.pressed.copy()
        self.pressed = list(pg.mouse.get_pressed()) # type: ignore
        self.just_pressed = [self.pressed[i] and not last_pressed[i] for i in range(3)]
        self.just_released = [not self.pressed[i] and last_pressed[i] for i in range(3)]
    
    def draw(self) -> None:
        pg.draw.circle(self.parent.screen, (110, 0, 0), self.position(), 10) # type: ignore

class Keyboard:
    """
    # Need the pygame module to be imported as pg.
    """
    def __init__(self, parent) -> None:
        self.parent = parent
        self.pressed :list= [False for _ in SCANCODES_NUMS]
        self.just_pressed :list= [False for _ in range(len(self.pressed))]
        self.just_released :list= [False for _ in range(len(self.pressed))]
    
    def update(self) -> None:
        last_pressed = self.pressed.copy()
        self.pressed :list= [pg.key.get_pressed()[i] for i in SCANCODES_NUMS] # type: ignore
        self.just_pressed = [self.pressed[i] and not last_pressed[i] for i in range(len(SCANCODES_NUMS))]
        self.just_released = [not self.pressed[i] and last_pressed[i] for i in range(len(SCANCODES_NUMS))]
    
    def get_key(self, scan_code, mode=KEY_MODE_PRESSED) -> bool:
        ll = self.pressed
        if mode == KEY_MODE_PRESSED:
            ll = self.pressed
        elif mode == KEY_MODE_JUST_PRESSED:
            ll = self.just_pressed
        elif mode == KEY_MODE_JUST_RELEASED:
            ll = self.just_released
        return ll[SCANCODES_NUMS.index(scan_code)]

class Vector2D:
    def __init__(self, x:NUM_TYPE=0, y:NUM_TYPE=0) -> None:
        self.x = x
        self.y = y

    def distance_to(self, object:"float|int|Vector2D|ARRAY_TYPE", squared:bool=True) -> NUM_TYPE:
        """
        # Calculate the distance between the current Vector2D object and another object.

        # Parameters:
            object (float or int or Vector2D or ARRAY_TYPE): The other object to which the distance is calculated.
            squared (bool, optional): If True, return the squared distance. If False, return the actual distance.
                                      Default is True.

        # Returns:
            NUM_TYPE: The squared distance between the current Vector2D object and the other object if `squared` is True,
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

    def angle_to(self, object:"float|int|Vector2D|ARRAY_TYPE") -> NUM_TYPE:
        """
        # Calculate the angle between the current Vector2D object and another object.

        # Parameters:
            object (float or int or Vector2D or ARRAY_TYPE): The other object to which the angle is calculated.

        # Returns:
            NUM_TYPE: The angle in radians between the current Vector2D object and the other object.

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

    def point_from_degs(self, rad:NUM_TYPE, radius:NUM_TYPE) -> "Vector2D":
        """
        # Calculate a new Vector2D point from the current point based on an angle in radians and a radius.

        # Parameters:
            rad (NUM_TYPE): The angle in radians.
            radius (NUM_TYPE): The distance from the current point.

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

    def copy(self) -> "Vector2D":
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

    def absolute_round(self, n=1) -> "Vector2D":
        """
        # Perform an "absolute round" operation on the Vector2D object.

        # Parameters:
            n (NUM_TYPE, optional): The numeric value to scale the "absolute rounded" vector. Default is 1.

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

    def floor(self, n:NUM_TYPE=1) -> "Vector2D":
        """
        # Round down the components of the Vector2D object to the nearest integer or the specified numeric value.

        # Parameters:
            n (NUM_TYPE, optional): The numeric value to round down the components. Default is 1.

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

    def ceil(self, n:NUM_TYPE=1) -> "Vector2D":
        """
        # Round up the components of the Vector2D object to the nearest integer or the specified numeric value.

        # Parameters:
            n (NUM_TYPE, optional): The numeric value to round up the components. Default is 1.

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

    def randomize(start:"NUM_TYPE|Vector2D|None"=None, end:"NUM_TYPE|Vector2D|None"=None) -> "Vector2D": #type: ignore
        """
        # Generate a random Vector2D point within the specified range.

        # Parameters:
            start (NUM_TYPE or Vector2D or None, optional): The starting point of the range.
                                                        Default is None, which corresponds to (0, 0).
                                                        If numeric, both x and y will have the same value.
            end (NUM_TYPE or Vector2D or None, optional): The ending point of the range.
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
        if not isinstance(start, Vector2D):
            if type(start) in NUM_TYPE: start = Vector2D(start, start) #type: ignore
            elif type(start) == None: start = Vector2D(0,0)
            else: raise Exception(f"\nArg start must be in [Vector2D, int, float, tuple, list] not a [{type(start)}]\n")
        if not isinstance(end, Vector2D):
            if type(end) in NUM_TYPE: end = Vector2D(end, end) #type: ignore
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
    def inter_points(self:"Vector2D", self_final_point:"Vector2D", lines:list[tuple["Vector2D", "Vector2D"]], sort:bool=False, return_empty:bool=False) -> list["Vector2D|None"]:
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
        def lineLineIntersect(P0, P1, Q0, Q1) -> tuple[NUM_TYPE, NUM_TYPE] | None:
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

    def normalize(self, max:NUM_TYPE=1, min:NUM_TYPE=0) -> "Vector2D":
        """
        # Normalize the Vector2D object to a new magnitude defined by max while preserving its direction.

        # Parameters:
            max (NUM_TYPE, optional): The new magnitude to which the Vector2D object will be scaled.
                                      Default is 1.
            min (NUM_TYPE, optional): The minimum magnitude. If provided, the Vector2D object will not be scaled
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

    def no_zero_div_error(self:"Vector2D", n:"NUM_TYPE|Vector2D", error_mode:str="zero") -> "Vector2D":
        """
        # Handle division between the Vector2D object and a numeric value or another Vector2D object.

        # Parameters:
            n (NUM_TYPE or Vector2D): The numeric value or Vector2D object for division.
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
        if isinstance(n, NUM_TYPE):
            if n == 0:
                return Vector2D(0 if error_mode == "zero" else (self.x if error_mode == "null" else _mt.nan), 0 if error_mode == "zero" else (self.y if error_mode == "null" else _mt.nan))
            else:
                return self / n
        elif isinstance(n, Vector2D):
            return Vector2D((0 if error_mode == "zero" else (self.x if error_mode == "null" else _mt.nan)) if n.x == 0 else self.x / n.x, (0 if error_mode == "zero" else (self.y if error_mode == "null" else _mt.nan)) if n.y == 0 else self.y / n.y)
        else:
            raise Exception(f"\nArg n must be in [Vector2D, int, float, tuple, list] not a [{type(n)}]\n")

    def __str__(self) -> str:
        return f"{self.x}, {self.y}"

    def __sub__(self, object:"float|int|Vector2D|ARRAY_TYPE") -> "Vector2D":
        object = self.__normalize__(object)
        return Vector2D(self.x - object.x, self.y - object.y)

    def __add__(self, object:"float|int|Vector2D|ARRAY_TYPE") -> "Vector2D":
        object = self.__normalize__(object)
        return Vector2D(self.x + object.x, self.y + object.y)

    def __mod__(self, object:"float|int|Vector2D|ARRAY_TYPE") -> "Vector2D":
        object = self.__normalize__(object)
        return Vector2D(self.x % object.x, self.y % object.y)

    def __radd__(self, object:"float|int|Vector2D|ARRAY_TYPE") -> "Vector2D":
        return self.__add__(object)

    def __repr__(self) -> str:
        return f"x:{self.x}\ty:{self.y}"

    def __call__(self, need_tuple=False) -> list|tuple:
        return (self.x, self.y) if need_tuple else [self.x, self.y]

    def __truediv__(self, object:"float|int|Vector2D|ARRAY_TYPE") -> "Vector2D":
        object = self.__normalize__(object)
        return Vector2D(self.x / object.x, self.y / object.y)

    def __floordiv__(self, object:"float|int|Vector2D|ARRAY_TYPE") -> "Vector2D":
        object = self.__normalize__(object)
        return Vector2D(self.x // object.x, self.y // object.y)
    
    def __abs__(self) -> "Vector2D":
        return Vector2D(abs(self.x), abs(self.y))

    def __round__(self, n:NUM_TYPE=1) -> "Vector2D":
        return Vector2D(round(self.x / n) * n, round(self.y / n) * n)

    def __floor__(self, n:NUM_TYPE=1) -> "Vector2D":
        return Vector2D(_mt.floor(self.x / n) * n, _mt.floor(self.y / n) * n)

    def __ceil__(self, n:NUM_TYPE=1) -> "Vector2D":
        return Vector2D(_mt.ceil(self.x / n) * n, _mt.ceil(self.y / n) * n)

    def __mul__(self, object:"float|int|Vector2D|ARRAY_TYPE") -> "Vector2D":
        object = self.__normalize__(object)
        return Vector2D(self.x * object.x, self.y * object.y)

    def __pow__(self, object:"float|int|Vector2D|ARRAY_TYPE") -> "Vector2D":
        object = self.__normalize__(object)
        return Vector2D(self.x ** object.x, self.y ** object.y)
    
    def __float__(self) -> "Vector2D":
        return Vector2D(float(self.x), float(self.y))

    def __getitem__(self, n) -> NUM_TYPE:
        if n in [0, "x"]:
            return self.x
        elif n in [1, "y"]:
            return self.y
        else:
            raise IndexError("V2 has only x,y...")
    
    def __normalize__(self, object) -> "Vector2D":
        if not isinstance(object, Vector2D):
            if isinstance(object, NUM_TYPE):
                return Vector2D(object, object)
            elif isinstance(object, ARRAY_TYPE):
                return Vector2D(*object[:2])
            else:
                raise TypeError(f"The value {object} is not a num type: [{NUM_TYPE}] nor an array type: [{ARRAY_TYPE}]")
        return object

class V2(Vector2D):
    def  __init__(self, x: NUM_TYPE = 0, y: NUM_TYPE = 0) -> None:
        super().__init__(x, y)

V2inf = Vector2D(float('inf'), float('inf'))
V2z = VectorZero = Vector2D()
V2one = Vector2D(1, 1)

def rgb(r:NUM_TYPE, g:NUM_TYPE, b:NUM_TYPE) -> tuple[NUM_TYPE, NUM_TYPE, NUM_TYPE]:
    return (r,g,b)

def color_fade(starting_c:ARRAY_TYPE, final_c:ARRAY_TYPE, index:NUM_TYPE, max_index:NUM_TYPE) -> tuple:
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

def angular_interpolation(starting_angle:NUM_TYPE, final_angle:NUM_TYPE, step:NUM_TYPE=.1) -> float:
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

def color_distance(starting_c:ARRAY_TYPE, final_c:ARRAY_TYPE, sqrd:bool=True) -> float:
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

def avg_position(*objects:"Vector2D") -> Vector2D:
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

def get_points(position:Vector2D, size:Vector2D, rotation:NUM_TYPE=0, pos_in_middle:bool=True, return_list:bool=False, clockwise_return:bool=False) -> tuple["Vector2D", "Vector2D", "Vector2D", "Vector2D"] | tuple[list[NUM_TYPE]|tuple[NUM_TYPE], list[NUM_TYPE]|tuple[NUM_TYPE], list[NUM_TYPE]|tuple[NUM_TYPE], list[NUM_TYPE]|tuple[NUM_TYPE]]:
    """
    # Generate points for a rectangle based on the given parameters.

    # Parameters:
        position (Vector2D): The center position of the rectangle.
        size (Vector2D): The size of the rectangle (width and height).
        rotation (NUM_TYPE, optional): The rotation angle in degrees. Default is 0.
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

def get_lines(position:Vector2D, size:Vector2D, rotation:NUM_TYPE=0, pos_in_middle:bool=True) -> list[list]:
    """
    # Generate lines representing the sides of a rectangle based on the given parameters.

    # Parameters:
        position (Vector2D): The center position of the rectangle.
        size (Vector2D): The size of the rectangle (width and height).
        rotation (NUM_TYPE, optional): The rotation angle in degrees. Default is 0.
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

def distance_line_point(line_point_a:Vector2D, line_point_b:Vector2D, point_c:Vector2D)  -> float:
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


#  default env
"""
import random as rnd
import numpy as np
from e2D import *

import pygame as pg

pg.init()
pg.font.init()
myfont = pg.font.SysFont("Arial", 32)

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1)
        self.clock = pg.time.Clock()
        self.keyboard = Keyboard(self)
        self.mouse = Mouse(self)
    
    def clear(self) -> None:
        self.screen.fill((0,0,0))
    
    def print(self, text, position, color=(255,255,255)) -> None:
        text_box = myfont.render(text, True, color)
        self.screen.blit(text_box, position())

    def draw(self) -> None:
        self.clock.tick(60)
        self.clear()
        self.print(str(self.clock.get_fps()), self.screen_size * .01)

        pg.display.update()
    
    def update(self) -> None:
        self.mouse.update()
        self.keyboard.update()

    def frame(self) -> None:
        self.update()
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_x):
                self.quit = True

env = Env()

while not env.quit:
    env.frame()
"""


#############################################################################################################################################################################################################################################################
# advanced env #TODO
"""
from e2D import *
import keyboard as key
import time as tm
import pygame as pg
import easygui
import uuid

pg.init()
pg.font.init()
myfont = pg.font.SysFont("Arial", 32)

class Button:
    def_side_border = .85
    def __init__(self,
                 parent,
                 text,
                 screen_ratio_position:V2,
                 screen_ratio_size:V2, 
                 text_color:tuple[num_type,num_type,num_type],
                 def_color:tuple[num_type,num_type,num_type],
                 over_color:tuple[num_type,num_type,num_type],
                 click_color:tuple[num_type,num_type,num_type],
                 callback,
                 border_color:tuple[num_type,num_type,num_type]=(255,255,255),
                 border_width:num_type=2,
                 corners:list[num_type]|num_type|None=10,
                 callback_mode=CALLBACK_MODE_ON_RELEASED,
                 font="Algerian",
                 font_downscale:float=1.0,
                 **callback_kwargs) -> None:
        self.parent :Env= parent
        self.text :str= text
        self.screen_ratio_size = screen_ratio_size  # ratio position is bot right
        self.screen_ratio_position = screen_ratio_position # ratio position is top left
        self.text_color = text_color
        self.callback = callback
        self.callback_kwargs = callback_kwargs
        self.def_color = def_color
        self.over_color = over_color
        self.click_color = click_color
        self.mouse_mode = DEFAULT_MOUSE_BUTTON_MODE
        self.font = font
        self.font_downscale = font_downscale
        self.callback_mode = callback_mode
        self.border_color = border_color
        self.border_width = border_width
        self.corners = corners
        self.update_screen_ratio_position()
    
    def update_screen_ratio_position(self) -> None:
        self.position = self.parent.screen_size * self.screen_ratio_position
        self.size = self.parent.screen_size * self.screen_ratio_size - self.parent.screen_size * self.screen_ratio_position
        self.set_box_and_text_size()
    
    def set_box_and_text_size(self) -> None:
        text_box = pg.font.SysFont(self.font, int(self.size.y)).render(self.text, True, self.text_color) #type: ignore
        text_box_size = V2(*text_box.get_rect()[2:])
        ratio = text_box_size.x / text_box_size.y
        self.font_size = min(self.size.x * self.def_side_border / ratio, self.size.y) * self.font_downscale
        self.text_box = pg.font.SysFont(self.font, int(self.font_size)).render(self.text, True, self.text_color) #type: ignore
        self.text_box_size = V2(*self.text_box.get_rect()[2:])

    def draw(self) -> None:
        color = self.def_color
        if self.mouse_mode == DEFAULT_MOUSE_BUTTON_MODE:
            color = self.def_color
        elif self.mouse_mode == OVER_MOUSE_BUTTON_MODE:
            color = self.over_color
        elif self.mouse_mode == CLICKED_MOUSE_BUTTON_MOVE:
            color = self.click_color
        
        if self.corners == None:
            pg.draw.rect(self.parent.screen, color, self.position() + self.size()) #type: ignore
        elif type(self.corners) in num_type:
            pg.draw.rect(self.parent.screen, color, self.position() + self.size(), border_radius=self.corners) #type: ignore
        elif type(self.corners) == list:
            pg.draw.rect(self.parent.screen, color, self.position() + self.size(), border_top_left_radius=self.corners[0], border_top_right_radius=self.corners[1], border_bottom_left_radius=self.corners[2], border_bottom_right_radius=self.corners[3]) #type: ignore
        if self.border_width:
            if self.corners == None:
                pg.draw.rect(self.parent.screen, self.border_color, self.position() + self.size(), self.border_width) #type: ignore
            elif type(self.corners) in num_type:
                pg.draw.rect(self.parent.screen, self.border_color, self.position() + self.size(), self.border_width, border_radius=self.corners) #type: ignore
            elif type(self.corners) == list:
                pg.draw.rect(self.parent.screen, self.border_color, self.position() + self.size(), self.border_width, border_top_left_radius=self.corners[0], border_top_right_radius=self.corners[1], border_bottom_left_radius=self.corners[2], border_bottom_right_radius=self.corners[3]) #type: ignore
        
        self.parent.screen.blit(self.text_box, (self.position + (self.size - self.text_box_size) / 2)())

    def update(self) -> None:
        if self.position.x < self.parent.mouse.position.x < self.position.x + self.size.x and self.position.y < self.parent.mouse.position.y < self.position.y + self.size.y:
            if self.parent.mouse.just_pressed[0] and CALLBACK_MODE_ON_PRESSED or self.parent.mouse.just_released[0] and CALLBACK_MODE_ON_RELEASED:
                self.mouse_mode = CLICKED_MOUSE_BUTTON_MOVE
                self.callback(**self.callback_kwargs)
            elif self.parent.mouse.pressed[0]:
                self.mouse_mode = CLICKED_MOUSE_BUTTON_MOVE
            else:
                self.mouse_mode = OVER_MOUSE_BUTTON_MODE
        else:
            self.mouse_mode = DEFAULT_MOUSE_BUTTON_MODE


class ButtonCallBacks:
    def __init__(self, parent) -> None:
        self.parent :Env= parent

    def on_load_image_callback(self, **kwargs) -> None:
        path = easygui.fileopenbox(filetypes=["*.png"])
        if not path: return
        image = pg.image.load(path) #type: ignore
        self.parent.reference_images.append({"path": path, "image":image, "id": uuid.uuid4()})

class Env:
    def __init__(self) -> None:
        self.quit = False
        self.screen_size = V2(1920, 1080)
        self.screen = pg.display.set_mode(self.screen_size(), vsync=1, flags=pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.keyboard = Keyboard(self)
        self.mouse = Mouse(self)
        self.buttons_callbacks = ButtonCallBacks(self)
        self.buttons = [
            Button(self,
                   text="add photo path",
                   screen_ratio_position=V2(.75, .1),
                   screen_ratio_size=V2(.99, .25),
                   text_color=rgb(255, 255, 255),
                   def_color=rgb(194, 87, 0),
                   over_color=rgb(107, 57, 15),
                   click_color=rgb(32, 20, 9),
                   callback=self.buttons_callbacks.on_load_image_callback,
                   font_downscale=.9)
                   ]
        self.reference_images = []
    
    def print(self, text, position, color=(255,255,255)) -> None:
        text_box = myfont.render(text, True, color)
        self.screen.blit(text_box, position())

    def clear(self) -> None:
        self.screen.fill((0,0,0))
    
    def draw(self) -> None:
        self.clock.tick(0)
        self.clear()
        self.print(str(self.clock.get_fps()), self.screen_size * .01)

        for button in self.buttons: button.draw()
        self.mouse.draw()

        pg.display.update()
    
    def update(self) -> None:
        last_screen_size = self.screen_size()
        self.screen_size = V2(*self.screen.get_rect()[2:])
        if last_screen_size != self.screen_size():
            for button in self.buttons: button.update_screen_ratio_position()
        
        self.keyboard.update()
        self.mouse.update()
        for button in self.buttons: button.update()
    
    def frame(self) -> None:
        self.update()
        self.draw()

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_x):
                self.quit = True

env = Env()

while not env.quit:
    env.frame()
"""

