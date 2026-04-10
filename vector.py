import math
from fractions import Fraction

class Vector:

    DISPLAY_PRECISION = 1000

    _name_map = {"x": 0, "y": 1, "z": 2, "w": 3,
                 "a": 0, "b": 1, "c": 2, "d": 3}
    
    def __init__(self, *args, mutable=False, **kwargs):

        self.components = []
        
        if args: # handles Vector([1, 2, 3]) and Vector(1, 2, 3)
            if len(args) == 1 and isinstance(args[0], list|float):
                self.components = list(args[0]) if mutable else tuple(args[0])
            else:
                self.components = list(args) if mutable else tuple(args)

        if kwargs: # handles Vector(x=1, y=2, z=3)
            for key, value in kwargs.items():
                if key in Vector._name_map:
                    idx = Vector._name_map[key]
                    while len(self.components) <= idx: # handles Vector(z=2) by creating self.components = [0,0,2]
                        self.components.append(0)
                    self.components[idx] = value
        
        # self.components = tuple(self.components)
        # TODO make the components of a vector immutable
    
    def _validate_vector(self, other, op_name):
        if not isinstance(other, Vector):
            return False
        
        if len(self.components) != len(other.components):
            raise ValueError(
                f"Cannot perform {op_name} on vectors of different lengths: {len(self.components)} and {len(other.components)}"
            )
        return True
    
    def _get_fractions(self):
        # return [Fraction(x).limit_denominator() for x in self.components]
        return [(f.numerator) if (f := Fraction(x).limit_denominator(Vector.DISPLAY_PRECISION)).denominator == 1 else (f) for x in self.components]

    # handles accessing vector components using index. vector_instance[0]
    def __getitem__(self, idx):
        # if the index is [0:2] (included, excluded) it return a sub vector of those sub components
        if isinstance(idx, slice):
            return Vector(self.components[idx])
        
        # returns the value at that index in the vectors components
        return self.components[idx]
    
    # handles dynamic access like v.x and v.y and v.z
    def __getattr__(self, name):
        if name in Vector._name_map:
            idx = Vector._name_map[name]
            try:
                return self.components[idx]
            except IndexError:
                pass
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
        # allows the vector to be used in sets or as dict keys
        return hash(tuple(self.components))

    # Binary Operators
    def __add__(self, other):
        if not self._validate_vector(other, "addition"):
            return NotImplemented
        return Vector([a + b for a, b in zip(self.components, other.components)])
    
    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        if not self._validate_vector(other, "addition"):
            return NotImplemented
        self.components = [a + b for a, b in zip(self.components, other.components)]
        return self

    def __sub__(self, other):
        if not self._validate_vector(other, "subtraction"):
            return NotImplemented
        return Vector([a - b for a, b in zip(self.components, other.components)])
    
    def __rsub__(self, other):
        return self - other
    
    def __isub__(self, other):
        if not self._validate_vector(other, "addition"):
            return NotImplemented
        self.components = [a - b for a, b in zip(self.components, other.components)]
        return self

    def __mul__(self, other):
        # handles multiplying by a scalar
        if isinstance(other, int|float):
            return Vector([x * other for x in self.components])
        
        # handles multiply by another vector and performs dot product not cross product
        if self._validate_vector(other, "addition"):
            return sum(a * b for a, b in zip(self.components, other.components))

        return NotImplemented
    
    # handles case where the scalar is on the right of the vector. 5 * vector
    def __rmul__(self, other):
        return self.__mul__(other)
    
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

    # Unary Operators
    def __pos__(self):
        return Vector(self.components[:])

    def __neg__(self):
        return Vector([-x for x in self.components])

    def __abs__(self):
        return self.magnitude()

    # Comparison Operators
    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.components == other.components
    
    def is_close(self, other, tol=1e-9):
        if not isinstance(other, Vector) or len(self) != len(other):
            return False
        
        # checks every single number for near-equality
        return all(math.isclose(a, b, abs_tol=tol) for a, b in zip(self.components, other.components))

    # returns False if all components of a vector are zero
    def __bool__(self):
        return any(self.components)

    # Vector Functions
    def magnitude(self):
        return math.sqrt(sum(x**2 for x in self.components))
    
    def cross(self, other):
        if len(self.components) != 3 or len(other.components) != 3:
            raise ValueError("Cross product is only defined for 3D vectors")
        
        new_x = self.y * other.z - self.z * other.y
        new_y = self.z * other.x - self.x * other.z
        new_z = self.x * other.y - self.y * other.x
        
        return Vector([new_x, new_y, new_z])
    
    def unit_vector(self):
        magnitude_value = self.magnitude()
        return Vector([x / magnitude_value for x in self.components])

    def project_onto_scalar_factor(self, other):
        if self._validate_vector(other, "projection onto another vector"):
            magnitude_other_squared = other * other # i.e. other dotted with itself

            if magnitude_other_squared == 0:
                raise ValueError("Cannot project onto a zero vector.")
            
            dot_product = self * other

            scalar_factor = dot_product / magnitude_other_squared

            return scalar_factor

    def project_onto_vector(self, other):            
            scalar_factor = self.project_onto_scalar_factor(other)

            return scalar_factor * other

    # method aliases
    mag = magnitude

# # --- Testing the flexibility ---
# if __name__ == "__main__":
#     # Works with a list (Unlimited items)
#     v1 = Vector([1, 2, 3, 4, 5, 6])
#     print(f"List init: {v1.x}, {v1[5]}") # 1, 6

#     # Works with keywords
#     v2 = Vector(x=10, z=30)
#     print(f"Keyword init: {v2.components}") # [10, 0, 30]

#     # Works with positional arguments
#     v3 = Vector(1, 2)
#     print(f"Positional: {v3.x}, {v3.y}") # 1, 2