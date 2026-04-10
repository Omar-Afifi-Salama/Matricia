import math
from vector import Vector

def is_parallel(obj_1, obj_2):
    # checking if two vectors are parallel
    if isinstance(obj_1, Vector) and isinstance(obj_2, Vector):
        if len(obj_1) != len(obj_2):
            return False
        
        dot_product = obj_1 * obj_2
        magnitudes_product = obj_1.magnitude() * obj_2.magnitude()

        # rel_tol is the 'relative tolerance'
        return math.isclose(dot_product, magnitudes_product, rel_tol=1e-9)

    return False

def angle_between(obj_1, obj_2, in_degrees = False):
    if isinstance(obj_1, Vector) and isinstance(obj_2, Vector):
        if len(obj_1) != len(obj_2):
            raise ValueError(
                f"Cannot calculate the angle between vectors of different lengths: {len(obj_1.components)} and {len(obj_2.components)}"
            )

        dot_product = obj_1 * obj_2
        magnitudes_product = obj_1.magnitude() * obj_2.magnitude()

        cos_angle = dot_product / magnitudes_product

        # creating a ceiling of 1 and -1 to deal with floating point imprecision
        cos_angle = max(-1.0, min(1.0, cos_angle))

        angle = math.acos(cos_angle)

        return math.degrees(angle) if in_degrees else angle
