import math

class Point:
    
    _name_map = {"x": 0, "y": 1, "z": 2, "w": 3,
                 "a": 0, "b": 1, "c": 2, "d": 3}

    def __init__(self, *args, **kwargs):

        self.components = []
        
        if args: # handles Point([1, 2, 3]) and Point(1, 2, 3)
            if len(args) == 1 and isinstance(args[0], list|float):
                self.components = list(args[0])
            else:
                self.components = list(args)

        if kwargs: # handles Point(x=1, y=2, z=3)
            for key, value in kwargs.items():
                if key in Point._name_map:
                    idx = Point._name_map[key]
                    while len(self.components) <= idx: # handles Point(z=2) by creating self.components = [0,0,2]
                        self.components.append(0)
                    self.components[idx] = value
        
        # self.components = tuple(self.components)
        # TODO make the components of a point immutable

    def _validate_point(self, other, op_name):
        if not isinstance(other, Point):
            return False
        
        if len(self.components) != len(other.components):
            raise ValueError(
                f"Cannot perform {op_name} on points of different dimensions: {len(self.components)} and {len(other.components)}"
            )
        return True
    
    # handles accessing point components using index. point_instance[0]
    def __getitem__(self, idx):
        # if the index is [0:2] (included, excluded) it return a sub point of those sub components
        if isinstance(idx, slice):
            return Point(self.components[idx])
        
        # returns the value at that index in the points components
        return self.components[idx]

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
        return f"( {', '.join(map(str, self.components))} )"
    
    # useful for debugging as it shows how the object was created
    def __repr__(self):
        return f"Point({self.components})"
    
    def __len__(self):
        return len(self.components)

    def __iter__(self):
        return iter(self.components)
    
    def __hash__(self):
        # allows the point to be used in sets or as dict keys
        return hash(tuple(self.components))
    
    # Binary Operations
    def __sub__(self, other):
        """
        Rule: Point - Point = Vector
              Point - Vector = Point
        """
        from vector import Vector 

        if isinstance(other, Point):
            return Vector([a - b for a, b in zip(self.components, other.components)])
        
        if isinstance(other, Vector):
            return Point([a - b for a, b in zip(self.components, other.components)])
        
        return NotImplemented

    def __add__(self, other):
        """Rule: Point + Vector = Point"""
        from vector import Vector
        
        if isinstance(other, Vector):
            return Point([a + b for a, b in zip(self.components, other.components)])
        
        return NotImplemented
    
    def distance_to(self, other):
        if not isinstance(other, Point):
            raise TypeError("Distance can only be calculated between two Points.")
        return math.sqrt(sum((b - a)**2 for a, b in zip(self.components, other.components)))

    def is_origin(self):
        # return all(x == 0 for x in self.components)
        return all(math.isclose(x, 0, abs_tol=1e-9) for x in self.components)
        # TODO create a config file that let's you choose between strict and lenient origin points
    
    def coords(self):
        return tuple(self.components)
    
    def linear_interpolation(self, other, t):
        """Rule: p_new = p1 + t * (p2 - p1)"""
        if not 0 <= t <= 1:
            raise ValueError(
                "Interpolation is only valid for values between 0 and 1. For values greater than 1, try 'linear_extrapolation()'."
                )
        
        return self + t * (other - self)
    
    # method aliases
    lerp = linear_interpolation

# def midpoint(p1, p2):
#     return Point([(a + b) / 2 for a, b in zip(p1.components, p2.components)])
# TODO need to rethink how to deal with standalone functions that are not methods
# TODO create the are_collinear() method