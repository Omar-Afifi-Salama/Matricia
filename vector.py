from __future__ import annotations
import math
from fractions import Fraction

class Vector:

    DISPLAY_PRECISION = 1000

    EPSILON = 1e-9

    _name_map = {"x": 0, "y": 1, "z": 2, "w": 3,
                 "a": 0, "b": 1, "c": 2, "d": 3}
    
    def __init__(self, *args, mutable=False, **kwargs):
        """Initializes a Vector instance.

        Supports multiple input formats:
            Vector(1, 2, 3)              -> Positional arguments
            Vector([1, 2, 3])            -> List/Tuple
            Vector(x=1, y=2)             -> Named coordinates
            Vector(n for n in range(3))  -> Generators

        Args:
            *args: Vector components.
            mutable (bool): If True, components are stored as a list. 
                            If False, stored as a tuple (default).
            **kwargs: Named components (x, y, z, w).
        """
        self.mutable = mutable
        temp_list = [] # initialized empty early in case of no args or kwargs to handle Vector()
        
        if args:
            if len(args) == 1:
                arg = args[0]
                # handles Vector([1, 2, 3]) or Vector(generator)
                if isinstance(arg, (list, tuple)) or hasattr(arg, "__iter__") and not isinstance(arg, str):
                    temp_list = [float(x) for x in arg]
                else:
                    # handles Vector(5)
                    temp_list = [float(arg)]
            else:
                # handles Vector(1, 2, 3)
                temp_list = [float(x) for x in args]

        if kwargs: # handles Vector(x=1, y=2, z=3)
            for key, value in kwargs.items():
                if key in Vector._name_map:
                    idx = Vector._name_map[key]
                    while len(temp_list) <= idx: # handles Vector(z=2) by creating temp_list = [0,0,2]
                        temp_list.append(0)
                    temp_list[idx] = float(value)

        self.components = temp_list if self.mutable else tuple(temp_list)
    
    def _validate_vector(self, other) -> bool:
        """Strict internal checker using to make sure
        that vector operations are possible.

        Args:
            other (Vector): It is the other vector on which
            we are checking if the operation is valid.

        Raises:
            ValueError: If both vector aren't of the same dimensions.

        Returns:
            bool : True if the other is a Vector and of
            the same dimensions else False
        """
        if not isinstance(other, Vector):
            return False
        
        if len(self.components) != len(other.components):
            raise ValueError(
                f"Cannot perform operation on vectors of of different lengths: {len(self.components)} and {len(other.components)}"
            )
        
        return True
    
    @staticmethod
    def same_dimensions(*vectors:Vector) -> bool:
        """Dimensions checker for multiple vectors.
        Should be used before doing any vector operation.

        Supports:
            same_dimensions(v1, v2, v3, ...)   -> Positional Arguments
            same_dimensions([v1, v2, v3, ...]) -> List/Tuple

        Args:
            *vectors(Vector): One or more Vector instances to compare.

        Raises:
            TypeError: If any of the arguments are not Vector instances.
        
        Returns:
            bool: True if all vector arguments are of the same dimensions,
            or if less than two vector argument are provided, else False.
        """
        if len(vectors) == 1 and isinstance(vectors[0], (list, tuple)):
            vectors = vectors[0]

        if len(vectors) < 2:
            return True # a vector to itself is of the same dimensions
        
        for i, v in enumerate(vectors):
            if not isinstance(v, Vector):
                raise TypeError(f"Argument at index {i} is {type(v).__name__}, not a Vector.")
        
        if not all(len(vectors[0]) == len(v) for v in vectors[1:]):
            return False
        
        return True

    def _get_fractions(self):
        """Internal method that returns the vector's components in pretty faction forms."""
        return [(f.numerator) if (f := Fraction(x).limit_denominator(Vector.DISPLAY_PRECISION)).denominator == 1 else (f) for x in self.components]

    # handles accessing vector components using index. vector_instance[0]
    def __getitem__(self, idx):
        # if the index is [0:2] (included, excluded) it returns a sub vector of those sub components
        if isinstance(idx, slice):
            return Vector(self.components[idx])
        
        # returns the value at that index in the vectors components
        return self.components[idx]
    
    def __setitem__(self, index, value):
        if not self.mutable:
            raise TypeError("This vector is immutable.")
        
        # expands the list if the index is outside the list so [1, 2, 3] and v[6] = 4 then [1, 2, 3, 0, 0, 0, 4]
        while len(self.components) <= index:
            self.components.append(0.0)
        
        self.components[index] = float(value)

    def __setattr__(self, name, value):

        if name in ('mutable', 'components'):
            super().__setattr__(name, value)
            return

        if not getattr(self, 'mutable', False):
            raise AttributeError("This vector is immutable. Use mutable=True to modify.")
        
        if name in Vector._name_map:
            idx = self._name_map[name]

            while len(self.components) <= idx:
                self.components.append(0.0)
            
            self.components[idx] = float(value)
        else:
            # treats the object like a generic python object
            super().__setattr__(name, value)

    # handles dynamic access like v.x and v.y and v.z
    def __getattr__(self, name):
        if name in Vector._name_map:
            idx = Vector._name_map[name]
            try:
                return self.components[idx]
            except IndexError:
                raise IndexError(f"The Vector doesn't have a value at the component '{name}'.")
        raise AttributeError(f"Vector object has no '{name}' attribute.")
    
    # handles trying to print(vector_instance)
    def __str__(self):
        fractions = self._get_fractions()
        return f"< {', '.join(map(str, fractions))} >"
    
    # useful for debugging as it shows how the object was created
    def __repr__(self):
        fractions = self._get_fractions()
        return f"Vector({fractions})"
    
    def __len__(self):
        return len(self.components)

    def __iter__(self):
        return iter(self.components)
    
    def __hash__(self):
        # each object in python has a unique hash like their fingerprint and python uses them in things like sets and dictionary as keys
        # in short, this allows the vector to be used in sets or as dict keys
        if self.mutable:
            # if an object is mutable it is very dangerous to depend on its hash because it can change later and this is defeats the purpose of depending on hashes in the first place
            raise TypeError("Mutable vectors cannot be hashed.")
        
        return hash(self.components)

    # Binary Operators
    def __add__(self, other):
        if self._validate_vector(other):
            return Vector([a + b for a, b in zip(self.components, other.components)], mutable=(self.mutable and other.mutable))
        
        # < 1, 2, 3 > + 5 = < 6, 7, 8 >
        if isinstance(other, (int, float)):
            return Vector([x + other for x in self.components], mutable=(self.mutable and other.mutable))
        
        return NotImplemented
    
    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        if self.mutable:
            if self._validate_vector(other):
                self.components = [a + b for a, b in zip(self.components, other.components)]
                return self
            elif isinstance(other, (int, float)):
                self.components = [x + other for x in self.components]
                return self
        else:
            # if the vector is immutable then return a new vector
            return self + other
        
        return NotImplemented

    def __sub__(self, other):
        if self._validate_vector(other):
            return Vector([a - b for a, b in zip(self.components, other.components)], mutable=(self.mutable and other.mutable))
        
        # < 1, 2, 3 > - 5 = < -4, -3, -2 >
        if isinstance(other, (int, float)):
            return Vector([x - other for x in self.components], mutable=(self.mutable and other.mutable))
        
        return NotImplemented
    
    def __rsub__(self, other):
        # -(self - other) = -self + other = other - self. we did this to be able to use the implementation in __sub__
        return -(self - other)
    
    def __isub__(self, other):
        if self.mutable:
            if self._validate_vector(other):
                self.components = [a - b for a, b in zip(self.components, other.components)]
                return self
            elif isinstance(other, (int, float)):
                self.components = [x - other for x in self.components]
                return self
        else:
            # if the vector is immutable then return a new vector
            return self - other
        
        return NotImplemented

    def __mul__(self, other):
        # handles multiplying by a scalar
        if isinstance(other, int|float):
            return Vector([x * other for x in self.components])
        
        # handles multiply by another vector and performs dot product not cross product
        if self._validate_vector(other):
            return sum(a * b for a, b in zip(self.components, other.components))

        # vector * matrix is defined in the matrix class

        return NotImplemented
    
    # handles case where the scalar is on the right of the vector. 5 * vector
    def __rmul__(self, other):
        return self * other
    
    def __imul__(self, other):
        # handles multiplying by a scalar
        if isinstance(other, int|float):
            # self.components = [x * other for x in self.components]
            # this is has a memory complexity of O(1) instead of O(n)
            for i in range(len(self.components)):
                self.components[i] *= other
            return self
        
        if isinstance(other, Vector):
            raise TypeError("Cannot use *= for dot products because the result is a scalar.")
        
        return NotImplemented
    
    def __truediv__(self, other):
        """Scalar Division: Vector / 2.0"""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Vector division by zero.")
            return Vector([x / other for x in self.components], mutable=self.mutable)
        return NotImplemented

    def __itruediv__(self, other):
        """In-place Scalar Division: v /= 2.0"""
        if self.mutable:
            if isinstance(other, (int, float)):
                if other == 0:
                    raise ZeroDivisionError("Vector division by zero.")
                for i in range(len(self)):
                    self.components[i] /= other
                return self
            return NotImplemented
        else:
            # Fallback for immutable: creates a new object
            return self / other

    def __floordiv__(self, other):
        """Scalar Floor Division: Vector // 2"""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Vector floor division by zero.")
            return Vector([x // other for x in self.components], mutable=self.mutable)
        return NotImplemented

    def __ifloordiv__(self, other):
        """In-place Floor Division: v //= 2"""
        if self.mutable:
            if isinstance(other, (int, float)):
                if other == 0:
                    raise ZeroDivisionError("Vector floor division by zero.")
                for i in range(len(self)):
                    self.components[i] //= other
                return self
            return NotImplemented
        else:
            return self // other

    # Unary Operators
    def __pos__(self):
        return Vector(self.components[:], mutable=self.mutable)

    def __neg__(self):
        return Vector([-x for x in self.components], mutable=self.mutable)

    def __abs__(self):
        return self.magnitude()

    # Comparison Operators
    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.is_close(other)
    
    def __ne__(self, other):
        return not self == other
    
    def is_close(self, other, tol=EPSILON):
        if not isinstance(other, Vector) or len(self) != len(other):
            return False
        
        # checks every single number for near-equality
        return all(math.isclose(a, b, abs_tol=tol) for a, b in zip(self.components, other.components))

    # returns False if all components of a vector are zero
    def __bool__(self):
        return any(abs(x) > self.EPSILON for x in self.components)
    
    def is_zero_vector(self):
        return not bool(self)

    def is_unit_vector(self):
        return math.isclose(self.magnitude(), 1.0, rel_tol=self.EPSILON)

    # Vector Functions
    def magnitude(self) -> float:
        """Returns the magnitude of the vector.
        Rule: sqrt(sum(each component squared))
        """
        return math.sqrt(sum(x**2 for x in self.components))
    
    def cross(self, other:Vector) -> Vector:
        """Calculates the cross product between two vectors.

        Args:
            other (Vector): The vector that gets crossed.
            Ex: a.cross(b) = a x b

        Raises:
            ValueError: If not both vectors are exactly 3D.

        Returns:
            Vector: a new vector that is perpendicular to both.
        """
        if len(self.components) != 3 or not isinstance(other, Vector) or len(other.components) != 3:
            raise ValueError("Cross product is only defined for 3D vectors")
        
        new_x = self.y * other.z - self.z * other.y
        new_y = self.z * other.x - self.x * other.z
        new_z = self.x * other.y - self.y * other.x
        
        return Vector([new_x, new_y, new_z], mutable=(self.mutable and other.mutable))
    
    def normalize(self) -> Vector:
        """Returns a unit vector pointing in the same direction as this vector.

        Raises:
            ValueError: If the vector is a zero vector, as its direction 
                        is undefined and normalization would involve division by zero.

        Returns:
            Vector: A new Vector instance with a magnitude of exactly 1.0.
        """
        if self.is_zero_vector():
            raise ValueError("Cannot normalize a zero vector. Direction is undefined.")

        magnitude_value = self.magnitude()
        return Vector([x / magnitude_value for x in self.components], mutable=self.mutable)

    def scalar_projection_onto(self, other:Vector) -> float:
        """Calculates the scalar factor that results from
        projecting the first vector on to the second.

        Args:
            other (Vector): The second vector on which projection happens.

        Raises:
            ValueError: If the second vector is the zero vector.

        Returns:
            float: The scalar factor.
        """
        if self._validate_vector(other):
            magnitude_other_squared = other * other # i.e. other dotted with itself

            if magnitude_other_squared <= self.EPSILON:
                raise ValueError("Cannot project onto a zero vector.")
            
            dot_product = self * other

            return dot_product / magnitude_other_squared

    def project_onto(self, other:Vector) -> Vector:
        """Calculates the Vector that results from
        projecting the first vector on to the second.

        Args:
            other (Vector): The second vector on which projection happens.

        Raises:
            ValueError: If the second vector is the zero vector.

        Returns:
            Vector: The Vector that results from projection.
        """      
        scalar_factor = self.scalar_projection_onto(other)
        return scalar_factor * other
    
    def linear_interpolation(self:Vector, other:Vector, t:float|int):
        """Rule: p_new = p1 + t * (p2 - p1) where 0 <= t <= 1"""
        if not 0 <= t <= 1:
            raise ValueError(
                "Interpolation is only valid for values between 0 and 1. For values greater than 1, try 'linear_extrapolation()'."
                )
        
        return self + t * (other - self)
    
    def linear_extrapolation(self:Vector, other:Vector, t:float|int):
        """Rule: p_new = p1 + t * (p2 - p1) where t > 1 or t < 0"""
        if not (t > 1 or t < 0):
            raise ValueError(
                "Extrapolation is only valid for values less than 0 and greater than 1. For values outside this domain, try 'linear_interpolation()'."
                )
        
        return self + t * (other - self)

    @staticmethod
    def are_parallel(v1:Vector, v2:Vector, allow_antiparallel:bool=True, tol:float=EPSILON) -> bool:
        
        if not Vector.same_dimensions(v1, v2):
            raise ValueError(f"Dimension mismatch: {len(v1)} and {len(v2)}")
        
        if v1.is_zero_vector() or v2.is_zero_vector():
            return False
        
        u1 = v1.normalize()
        u2 = v2.normalize()

        dot_product = u1 * u2

        if allow_antiparallel:
            return math.isclose(abs(dot_product), 1.0, abs_tol=tol)
        else:
            return math.isclose(dot_product, 1.0, abs_tol=tol)

    @staticmethod
    def are_antiparallel(v1:Vector, v2:Vector, tol:float=EPSILON) -> bool:
        if not Vector.same_dimensions(v1, v2):
            raise ValueError(f"Dimension mismatch: {len(v1)} and {len(v2)}")
        
        if v1.is_zero_vector() or v2.is_zero_vector():
            return False
        
        u1 = v1.normalize()
        u2 = v2.normalize()

        dot_product = u1 * u2

        return math.isclose(dot_product, -1.0, abs_tol=tol)

    @staticmethod
    def are_all_parallel(*vectors:Vector, allow_antiparallel:bool=True, tol:float=EPSILON) -> bool:
        if len(vectors) < 2:
            return True
        
        # idea is if a // b and a // c and a // d then for sure b // c // d
        anchor = vectors[0]

        for v in vectors[1:]:
            if not Vector.are_parallel(anchor, v, allow_antiparallel=allow_antiparallel, tol=tol):
                return False
            
        return True
    
    @staticmethod
    def angle_between(v1:Vector, v2:Vector, in_degrees:bool=False) -> float:
        if not Vector.same_dimensions(v1, v2):
            raise ValueError(f"Dimension mismatch: {len(v1)} and {len(v2)}")
        
        if v1.is_zero_vector() or v2.is_zero_vector():
            raise ValueError("Angle is undefined with a zero vector.")
        
        u1 = v1.normalize()
        u2 = v2.normalize()

        dot_product = max(-1.0, min(1.0, u1 * u2))

        angle = math.acos(dot_product)

        return math.degrees(angle) if in_degrees else angle
    
    @staticmethod
    def are_perpendicular(v1:Vector, v2:Vector, tol:float=EPSILON) -> bool:
        if not Vector.same_dimensions(v1, v2):
            raise ValueError(f"Dimension mismatch: {len(v1)} and {len(v2)}")
        
        dot_product = v1 * v2

        return math.isclose(dot_product, 0.0, abs_tol=tol)

    @staticmethod
    def mean(*vectors:Vector) -> Vector:
        
        if not vectors:
            return None
        
        if not Vector.same_dimensions(vectors):
            raise ValueError(f"Cannot calculate the mean vector. Vectors are not all of the same dimensions.")
        
        dimensions = len(vectors[0])
        total_components = [0.0] * dimensions

        for v in vectors:
            for i in range(dimensions):
                total_components[i] += v[i]

        mean_components = [x / len(vectors) for x in total_components]

        return Vector(mean_components, mutable=all(v.mutable for v in vectors))
    
    @staticmethod
    def angular_spread(*vectors:Vector, in_degrees:bool=False) -> float:
        if len(vectors) < 2:
            return 0.0
        
        mean_vector = Vector.mean(vectors)
        sum_of_angles = sum(Vector.angle_between(v, mean_vector, in_degrees=in_degrees) for v in vectors)

        return sum_of_angles / len(vectors)
    
    @staticmethod
    def max_angular_deviation(*vectors:Vector, in_degrees:bool=False) -> float:
        if len(vectors) < 2:
            return 0.0
        
        if not Vector.same_dimensions(vectors):
            raise ValueError(f"Cannot calculate the mean vector. Vectors are not all of the same dimensions.")
        
        max_angle = 0.0

        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                angle = Vector.angle_between(vectors[i], vectors[j])
                if angle > max_angle:
                    max_angle = angle

        return math.degrees(max_angle) if in_degrees else max_angle
    
    @staticmethod
    def cross_product(v1:Vector, v2:Vector) -> Vector:
        try:
            return v1.cross(v2)
        except AttributeError:
            raise TypeError("Both arguments must be Vector instances.")
    
    @staticmethod
    def parallelogram_area(v1:Vector, v2:Vector) -> float:
        return Vector.cross_product(v1, v2).magnitude()
    
    @staticmethod
    def triangle_area(v1:Vector, v2:Vector) -> float:
        return 0.5 * Vector.parallelogram_area(v1, v2)
    
    @staticmethod
    def scalar_triple_product(v1:Vector, v2:Vector, v3:Vector) -> float:
        try:
            return v1 * v2.cross(v3)
        except (AttributeError, TypeError):
            raise TypeError("All arguments must be Vector instances and 3D.")
    
    @staticmethod
    def volume_of_parallelepiped(v1:Vector, v2:Vector, v3:Vector) -> float:
        return abs(Vector.scalar_triple_product(v1, v2, v3))
    
    @staticmethod
    def are_coplanar(v1:Vector, v2:Vector, v3:Vector, tol:float=EPSILON) -> bool:
        triple_prod = Vector.scalar_triple_product(v1, v2, v3)
        return math.isclose(triple_prod, 0.0, abs_tol=tol)
    
    # method aliases
    mag = magnitude
    get_unit_vector = normalize
    norm = normalize
    are_orthogonal = are_perpendicular
    are_linearly_dependent = are_parallel
    is_zero = is_zero_vector
    is_unit = is_unit_vector
    get_mean_vector = mean

    # TODO Docstring for the methods
    # TODO Division by a scalar __truediv__ and __floordiv__ and __itruediv__ and __ifloordiv__