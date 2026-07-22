from __future__ import annotations
from .point import Point
from .vector import Vector
from .matrix import Matrix
import math

class Line:

    EPSILON = 1e-9

    def __init__(self, point:Point, direction:Vector):
        if len(point) != len(direction):
            raise ValueError("Both the initial point and direction must exist in the same dimension.")
        
        self.point = point
        self.direction = direction
        self.dimensions = len(point)
        # TODO think about immutability

    def __str__(self):
        return f"L(t) = {self.point} + t * {self.direction}"
    
    def __repr__(self):
        return f"Line(point = {self.point}, direction = {self.direction})"
    
    def __eq__(self, other: Line):
        """Checks if two lines occupy the exact same space."""
        # must be a line and in the same dimension
        if not isinstance(other, Line) or self.dimensions != other.dimensions:
            return False
        
        # must be parallel
        if not self.is_parallel_to(other):
            return False
        
        # the distance between them should be zero (or pretty much zero)
        return self.distance_to_point(other.point) < Line.EPSILON
    
    # if point in line
    def __contains__(self, target: Point):
        return self.distance_to_point(target) < Line.EPSILON

    @staticmethod
    def from_two_points(p1: Point, p2: Point) -> Line:
        return Line(p1, p2 - p1)

    def get_point_at(self, t: int|float) -> Vector:
        return self.point + t * self.direction
    
    def closest_point_to(self, point: Point) -> Point:
        
        w = point - self.point

        projection_vector = w.project_onto(self.direction)
        
        return self.point + projection_vector

    def distance_to_point(self, point: Point) -> float:

        # TODO think about using cross product when implementing collisions cross.mag / direction.mag

        if len(point) != self.dimensions:
            raise ValueError("Line and point must exist in the same dimensions.")
        
        # a laser beam vector that starts from the line's origin to the target point
        w = point - self.point

        # get the shadow casted by the laser bean vector onto the line's direction vector
        projected_vector = w.project_onto(self.direction)

        # gets the distance difference between the laser beam and its projection
        # which you can think of as the base of the triangle formed
        perpendicular_vector = w - projected_vector

        # the distance is the magnitude
        return perpendicular_vector.magnitude()
    
    def reflect_point(self, point: Point) -> Point:

        closest_point = self.closest_point_to(point)

        drop_vector = closest_point - point

        return closest_point + drop_vector

    def is_parallel_to(self, other: Line, tol=EPSILON) -> bool:
        return Vector.are_parallel(self.direction, other.direction, tol=tol)
    
    def intersect(self, other: Line) -> Point: # TODO better name
        """
        Finds the exact coordinate where two lines intersect.
        Returns a Vector if they hit, or None if they are skew (miss each other).
        """
        if self.dimensions != other.dimensions:
            raise ValueError("Lines must exist in the same dimension to intersect.")
        
        target_vector = other.point - self.point
        # TODO maybe import matrix here
        
        m = Matrix(
            [self.dimensions[i], -other.direction[i], target_vector[i]] for i in range(self.dimensions)
        )

        rref_m = m.reduced_row_echelon_form()

        for row in rref_m:
            # If the left side is all zeroes, but the right side is a real number
            if all(abs(val) < Line.EPSILON for val in row[:-1]) and abs(row[-1]) > Line.EPSILON:
                return None  # The lines are SKEW. They miss each other entirely.
            
        # intersection point    
        t = rref_m.data[0][-1]

        return self.get_point_at(t)

    # TODO think about out sourcing function to other parts of the module
    
    # def angle_between(self)

    # def intersect_plane(plane: Plane) -> Vector:
    #     pass