import math
from __future__ import annotations
from fractions import Fraction

class Point:

    DISPLAY_PRECISION = 1000

    EPSILON = 1e-9
    
    _name_map = {"x": 0, "y": 1, "z": 2, "w": 3,
                 "a": 0, "b": 1, "c": 2, "d": 3}

    def __init__(self, *args, mutable=False, **kwargs):
        """Initializes a Point instance.

        Supports multiple input formats:
            Point(1, 2, 3)              -> Positional arguments
            Point([1, 2, 3])            -> List/Tuple
            Point(x=1, y=2)             -> Named coordinates
            Point(n for n in range(3))  -> Generators

        Args:
            *args: Point components.
            mutable (bool): If True, components are stored as a list. 
                            If False, stored as a tuple (default).
            **kwargs: Named components (x, y, z, w).
        """
        self.mutable = mutable
        temp_list = [] # initialized empty early in case of no args or kwargs to handle Point()
        
        if args:
            if len(args) == 1:
                arg = args[0]
                # handles Point([1, 2, 3]) or Point(generator)
                if isinstance(arg, (list, tuple)) or hasattr(arg, "__iter__") and not isinstance(arg, str):
                    temp_list = [float(x) for x in arg]
                else:
                    # handles Point(5)
                    temp_list = [float(arg)]
            else:
                # handles Point(1, 2, 3)
                temp_list = [float(x) for x in args]

        if kwargs: # handles Point(x=1, y=2, z=3)
            for key, value in kwargs.items():
                if key in Point._name_map:
                    idx = Point._name_map[key]
                    while len(temp_list) <= idx: # handles Point(z=2) by creating temp_list = [0,0,2]
                        temp_list.append(0)
                    temp_list[idx] = float(value)

        self.components = temp_list if self.mutable else tuple(temp_list)

    def _validate_point(self, other):
        """Strict internal checker using to make sure
        that vector operations are possible.

        Args:
            other (Vector): It is the other vector on which
            we are checking if the operation is valid.

        Raises:
            ValueError: If both vector aren't of the same dimensions.

        Returns:
            bool : True if the other is a Vector and of
            the same dimensions else False"""
        if not isinstance(other, Point):
            return False
        
        if len(self.components) != len(other.components):
            raise ValueError(
                f"Cannot perform operation on points of different dimensions: {len(self.components)} and {len(other.components)}"
            )
        
        return True
    
    def _get_fractions(self):
        """Internal method that returns the point's components in pretty faction forms."""
        return [(f.numerator) if (f := Fraction(x).limit_denominator(Point.DISPLAY_PRECISION)).denominator == 1 else (f) for x in self.components]
    
    # handles accessing point components using index. point_instance[0]
    def __getitem__(self, idx):
        # if the index is [0:2] (included, excluded) it return a sub point of those sub components
        if isinstance(idx, slice):
            return Point(self.components[idx])
        
        # returns the value at that index in the points components
        return self.components[idx]

    def __setitem__(self, index, value):
        if not self.mutable:
            raise TypeError("This point is immutable.")
        
        # expands the list if the index is outside the list so [1, 2, 3] and p[6] = 4 then [1, 2, 3, 0, 0, 0, 4]
        while len(self.components) <= index:
            self.components.append(0.0)
        
        self.components[index] = float(value)

    def __setattr__(self, name, value):
        if not self.mutable:
            raise AttributeError("This point is immutable.")
        
        if name in Point._name_map:
            idx = self._name_map[name]
            self.components[idx] = value
        else:
            # treats the object like a generic python object
            super().__setattr__(name, value)

    # handles dynamic access like v.x and v.y and v.z
    def __getattr__(self, name):
        if name in Point._name_map:
            idx = Point._name_map[name]
            try:
                return self.components[idx]
            except IndexError:
                pass
        raise AttributeError(f"Point object has no '{name}' attribute.")
    
    def __str__(self):
        fractions = self._get_fractions()
        return f"( {', '.join(map(str, fractions))} )"
    
    # useful for debugging as it shows how the object was created
    def __repr__(self):
        fractions = self._get_fractions()
        return f"Point({fractions})"
    
    def __len__(self):
        return len(self.components)

    def __iter__(self):
        return iter(self.components)
    
    def __hash__(self):
        # allows the point to be used in sets or as dict keys
        if self.mutable:
            raise TypeError("Mutable points cannot be hashed.")
        
        return hash(tuple(self.components))
    
    # Binary Operations
    def __add__(self, other):
        """Rule: Point + Vector = Point
                 Point + Scalar = Point (Broadcasting)"""
        from vector import Vector
        
        if len(self) != len(other):
            raise ValueError("Dimensions must match.")
        
        if isinstance(other, Vector):    
            return Point([a + b for a, b in zip(self.components, other.components)], mutable=(self.mutable and other.mutable))
        
        if isinstance(other, (int, float)):
            return Point([x + other for x in self.components], mutable=self.mutable)
        
        return NotImplemented
    
    def __radd__(self, other):
        """Vector + Point = Point + Vector
           Scalar + Point = Point + Scalar """
        return self + other
    
    def __iadd__(self, other):
        """In-place addition: self += other"""
        if self.mutable:
            from vector import Vector

            if isinstance(other, Vector):
                if len(self) != len(other):
                    raise ValueError("Dimensions must match.")
                for i in range(len(self)):
                    self.components[i] += other.components[i]
                return self
            
            if isinstance(other, (int, float)):
                for i in range(len(self)):
                    self.components[i] += other
                return self
        else:
            return self + other
        
        return NotImplemented
    
    def __sub__(self, other):
        """
        Rule: Point - Point = Vector
              Point - Vector = Point
              Point - Scalar = Point (Broadcasting)
        """
        from vector import Vector 

        if isinstance(other, (int, float)):
            return Point([x - other for x in self.components], mutable=self.mutable)

        if len(self) != len(other):
            raise ValueError("Dimensions must match.")

        if isinstance(other, Point):
            return Vector([a - b for a, b in zip(self.components, other.components)], mutable=(self.mutable and other.mutable))
        
        if isinstance(other, Vector):
            return Point([a - b for a, b in zip(self.components, other.components)], mutable=(self.mutable and other.mutable))
        
        return NotImplemented
    
    def __rsub__(self, other):
        """Handles Scalar - Point"""
        if isinstance(other, (int, float)):
            return Point([other - x for x in self.components], mutable=self.mutable)
        
        return NotImplemented
    
    def __isub__(self, other):
        """In-place subtraction: self -= other"""
        if self.mutable:
            from vector import Vector

            if isinstance(other, (Point, Vector)):
                if len(self) != len(other):
                    raise ValueError("Dimensions must match.")
                for i in range(len(self)):
                    self.components[i] -= other.components[i]
                return self
            
            if isinstance(other, (int, float)):
                for i in range(len(self)):
                    self.components[i] -= other
                return self
        else:
            return self + other
        
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Point([x * other for x in self.components], mutable=self.mutable)
        
        # The Hadamard Product
        if isinstance(other, Point):
            
            if len(self) != len(other):
                    raise ValueError("Dimensions must match.")
            
            return Point([x * y for x, y in zip(self.components, other.components)])
        
        return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __imul__(self, other):
        if self.mutable:
            if isinstance(other, (int, float)):
                for i in range(len(self)):
                    self.components *= other
            # The Hadamard Product
            if isinstance(other, Point):
                if len(self) != len(other):
                    raise ValueError("Dimensions must match.")
                for i in range(len(self)):
                    self.components[i] *= other.components[i]
        else:
            return self * other
        
        return NotImplemented

    def __truediv__(self, other):
        """Scalar Division: Point / 2"""
        if isinstance(other, (int, float)):
            if other == 0:
                    raise ZeroDivisionError("Point division by zero.")
            return Point([x / other for x in self.components], mutable=self.mutable)
        
        return NotImplemented
    
    def __itruediv__(self, other):
        if self.mutable:
            if isinstance(other, (int, float)):
                if other == 0:
                    raise ZeroDivisionError("Point division by zero.")
                for i in range(len(self)):
                    self.components[i] /= other
                return self
        else:
            return self / other
        
        return NotImplemented

    def __floordiv__(self, other):
        """Scalar Floor Division: Point // 2"""
        if isinstance(other, (int, float)):
            if other == 0:
                    raise ZeroDivisionError("Point floor division by zero.")
            return Point([x // other for x in self.components], mutable=self.mutable)
        
        return NotImplemented
    
    def __ifloordiv__(self, other):
        if self.mutable:
            if isinstance(other, (int, float)):
                if other == 0:
                    raise ZeroDivisionError("Point floor division by zero.")
                for i in range(len(self)):
                    self.components[i] //= other
                return self
        else:
            return self // other
        
        return NotImplemented

    def distance_to(self, other):
        if not isinstance(other, Point):
            raise TypeError("Distance can only be calculated between two Points.")
        return math.sqrt(sum((b - a)**2 for a, b in zip(self.components, other.components)))
    
    def distance_squared_to(self, other):
        """Calculates the squared distance. Faster than distance_to() for comparisons."""
        if not isinstance(other, Point):
            raise TypeError("Must be a Point instance.")
        return sum((b - a)**2 for a, b in zip(self.components, other.components))
    
    def move(self, vector):
        """Translates the point by a given Vector."""
        return self + vector

    def is_origin(self, strict_origin=False, tol=EPSILON):
        if strict_origin:
            return all(x == 0 for x in self.components)
        
        return all(math.isclose(x, 0, abs_tol=tol) for x in self.components)
    
    def coords(self):
        return tuple(self.components)
    
    def linear_interpolation(self, other, t):
        """Rule: p_new = p1 + t * (p2 - p1) where 0 <= t <= 1"""
        if not 0 <= t <= 1:
            raise ValueError(
                "Interpolation is only valid for values between 0 and 1. For values greater than 1, try 'linear_extrapolation()'."
                )
        
        return self + t * (other - self)
    
    def linear_extrapolation(self, other, t):
        """Rule: p_new = p1 + t * (p2 - p1) where t > 1 or t < 0"""
        if not (t > 1 or t < 0):
            raise ValueError(
                "Extrapolation is only valid for values less than 0 and greater than 1. For values outside this domain, try 'linear_interpolation()'."
                )
        
        return self + t * (other - self)
    
    @staticmethod
    def midpoint(p1:Point, p2:Point) -> Point:
        return p1.linear_interpolation(p2, t=0.5)
    
    @staticmethod
    def centroid(*points):
        """Calculates the geometric center of a group of points."""
        # You can use your unpacking logic here similar to same_dimensions
        num_points = len(points)
        if num_points == 0: return None
        
        # Sum all components and divide by count
        return Point([sum(c) / num_points for c in zip(*(p.components for p in points))], mutable=all(p.mutable for p in points))
    
    @staticmethod
    def are_collinear(*points:Point, tol=EPSILON):
        """Checks if a sequence of points all lie on the same straight line."""
        from vector import Vector
        
        if len(points) == 1 and isinstance(points[0], (list, tuple)):
            points = points[0]

        if len(points) < 2:
            return True
        
        anchor_point = points[0]

        for i, p in enumerate(points):
            if not isinstance(p, Point):
                raise TypeError(f"Argument at index {i} is {type(p).__name__}, not a Point.")
            
            if not len(anchor_point) == len(p):
                raise TypeError(f"Argument at index {i} is of {len(p)} not {len(anchor_point)}")

        base_vector = points[1] - anchor_point

        if base_vector.is_zero_vector():
            # if the base vector is zero that means that both points are equal, which means that are on the same and thus on the same line. So we try again but by removing that point.
            return Point.are_collinear(points[1:], tol=tol)
        
        for i in range(2, len(points)):
            next_vec = points[i] - anchor_point
            if not next_vec.is_zero_vector():
                # again if the new vector is zero then both points are equal, and thus collinear.
                if not base_vector.is_parallel(next_vec, tol=tol):
                    return False
        
        return True

    # method aliases
    lerp = linear_interpolation

# TODO create the are_collinear() method