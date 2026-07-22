from __future__ import annotations
from .point import Point
from .vector import Vector
from .line import Line
import math

class Plane:

    EPSILON = 1e-9

    def __init__(self, point: Point, normal: Vector):
        if len(point) != 3 or len(normal) != 3:
            raise ValueError("Point and normal both must exist in the 3 dimensions to create regular plane. For higher dimensions try the Hyperplane class.")
        
        if normal.is_zero_vector():
            raise ValueError("Normal vector cannot be the zero vector.")
        
        self.point = point
        self.normal = normal
        self.dimensions = len(point)
    
    @staticmethod
    def from_three_points(p1: Point, p2: Point, p3: Point) -> Plane:
        """Builds a 3D plane from 3 points."""

        if len(p1) != 3 or len(p2) != 3 or len(p3) != 3:
            raise ValueError("Regular planes only exist in 3 dimensions.")
        
        v1 = p2 - p1
        v2 = p3 - p1

        normal = v1.cross(v2)

        if normal.is_zero_vector():
            raise ValueError("The 3 points resulted in a normal vector of magnitude zero. The normal vector of a plane cannot be the zero vector.")
        
        return Plane(point=p1, normal=normal)

    def contains_point(self, point: Point) -> bool:
        """Checks if a point rests on a plane"""

        return self.distance_to_point(point) < Plane.EPSILON
    
    def __contains__(self, item):
        
        if isinstance(item, Point):
            return self.contains_point(item)
        
        if isinstance(item, Line):
            return self.intersect_line(item) is None
    
    # TODO review
    def __eq__(self, other: "Plane") -> bool:
        """Checks if two planes occupy the exact same infinite space."""
        if not isinstance(other, Plane) or self.dimensions != other.dimensions:
            return False
            
        # 1. Are their normal vectors perfectly parallel?
        if not Vector.are_parallel(self.normal, other.normal):
            return False
            
        # 2. Is Plane B's starting point resting perfectly on Plane A's surface?
        return self.contains_point(other.point)

    def distance_to_point(self, point: Point) -> float:
        """Calculates the shortest distance from a point to the plane."""

        w = point - self.point

        return abs(w.scalar_projection_onto(self.normal))

    def is_parallel_to(self, other: Plane) -> bool:
        return Vector.are_parallel(self.normal, other.normal)
    
    def intersect_line(self, line: Line) -> Point:
        """Calculates the point where the line intersects the plane."""

        if self.dimensions != line.dimensions:
            raise ValueError("Plane and Line must exist in the same dimension.")
        
        denominator = self.normal * line.direction

        if abs(denominator) < Plane.EPSILON:
            return None # i.e. the line never intersects the plane, because it exists entirely in the plane.
        
        w = self.point - line.point
        numerator = w * self.normal

        t = numerator / denominator

        return line.get_point_at(t)

    def intersect_plane(self, other: Plane) -> Line: # TODO FIXME
        """Calculates the Line where two 3D planes intersect."""
        
        # direction vector
        direction = self.normal.cross(other.normal)

        # uses the square to avoid using the square root function
        magnitude_direction_squared = direction * direction

        if magnitude_direction_squared < Plane.EPSILON:
            return None
        
        # distance from origin
        d1 = (self.point * other.point)
        d2 = (other.point * self.point)

        # law for starting point (d1 * n2 - d2 * n1)
        part = (Point(other.normal.components) * d1) - (Point(self.normal.components) * d2)

        part = Vector(part.components)

        start_point = part.cross(direction) * (1.0 / magnitude_direction_squared)

        return Line(start_point, direction)
    
    def closest_point_to(self, point: Point) -> Point:
        """Returns the point on the plane that is closest to the target point."""

        w = point - self.point

        scalar_factor = w.scalar_projection_onto(self.normal)

        drop_vector = self.normal * scalar_factor

        return point - drop_vector
    
    def reflect_point(self, point:Point) -> Point:
        """Reflects a point perfectly across the plane."""
        w = point - self.point

        scalar_factor = w.scalar_projection_onto(self.normal)

        drop_vector = self.normal * scalar_factor

        return point - (drop_vector * 2)
    
    def reflect_vector(self, vector: Vector) -> Vector:

        scalar_factor = vector.scalar_projection_onto(self.normal)

        drop_vector = self.normal * scalar_factor

        return vector - (drop_vector * 2)
    
    def is_in_front(self, point: Point) -> bool:
        """Checks if a point is in front of the plane or not."""

        w = point - self.point

        # if dot product is positive then it is in front.
        return (w * self.normal) > 0
    
    def is_behind(self, point: Point) -> bool:

        return not self.is_in_front(point)

class Hyperplane: # no cross product
    pass