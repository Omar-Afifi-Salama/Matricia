
import math
from vector import Vector

class Matrix:
    def __init__(self, *args, **kwargs):
        """
        Supports:
        1. Matrix([[1, 2], [3, 4]]) -> List of lists
        2. Matrix([1,2], [3,4])     -> Multiple Lists 
        3. Matrix(v1, v2)           -> Multiple Vector objects
        4. Matrix([1, 2, 3, 4], rows=2, cols=2) -> Flat list with shape
        """
        # TODO need to be able to handle a list of vectors
        # TODO add the ability to input generator expression with the code snippet below
        # if len(args) == 1 and hasattr(args[0], '__next__'):
        #     args = (list(args[0]),)
        # TODO add the square attribute because it used in a lot of functions so instead of doing a function call having it in the matrix is better.

        input_data = []

        # Case 1 & 4 (Single positional argument)
        if len(args) == 1:
            raw_data = args[0]
            
            # Check for Case 4: Flat list + dimensions in kwargs
            # We look for common aliases: r/m/rows and c/n/cols
            r = kwargs.get('rows') or kwargs.get('row') or kwargs.get('r') or kwargs.get('m')
            c = kwargs.get('cols') or kwargs.get('columns') or kwargs.get('c') or kwargs.get('n')

            if r is not None and c is not None:
                if (r * c) != len(raw_data):
                    raise ValueError(f"Cannot create a {r}x{c} matrix with {len(raw_data)} elements.")
                # Turn [1,2,3,4] into [[1,2], [3,4]]
                input_data = [raw_data[i * c : (i + 1) * c] for i in range(r)]
            
            # Case 1: Already a list of lists or list of Vectors
            elif isinstance(raw_data, (list, tuple)) and all(isinstance(item, (list, tuple, Vector)) for item in raw_data):
                input_data = raw_data
            else:
                # Fallback for a single row matrix: Matrix([1, 2, 3])
                input_data = [raw_data]

        # Case 2 & 3: Multiple arguments like Matrix([1,2], [3,4]) or Matrix(v1, v2)
        elif len(args) > 1:
            # We just verify every arg is a "row-like" thing
            if all(isinstance(arg, (list, tuple, Vector)) for arg in args):
                input_data = list(args)
        
        # Convert everything to Vectors
        self.data = [row if isinstance(row, Vector) else Vector(row) for row in input_data]

        # Validation
        if self.data:
            first_len = len(self.data[0])
            if not all(len(row) == first_len for row in self.data):
                raise ValueError("Inconsistent row lengths! A matrix must be rectangular.")
            
        self.row_num = len(self.data)
        self.col_num = len(self.data[0])

    def is_square(self):
        return self.row_num == self.col_num
    
    def same_dimensions_as(self, other):
        return self.row_num == other.row_num and self.col_num == other.col_num
    
    def _operations_possible(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented # TODO figure out how you are going to do error messages
        
        if self.row_num != other.row_num or self.col_num != other.col_num:
            return False
        
        return True
    
    def get_column(self, idx):
        if 0 <= idx <= self.col_num:
            return Vector([row[idx] for row in self.data])
        
        return NotImplemented

    def transpose(self):
        # return Matrix(self.get_column(i) for i in range(self.col_num))
        return Matrix([list(item) for item in zip(*self.data)])
    
    def _is_conformable_with(self, other):
        return self.col_num == other.row_num
    
    @property
    def _row_with_most_zeros(self):
        return max([(idx, sum(1 for x in v if x == 0)) for idx, v in enumerate(self.data)], key=lambda item: item[1])
    
    def is_diagonal(self): # TODO implement something for floating point zeros if abs(x) > 1e-9: return false If it's not "basically zero", 
        if not self.is_square():
            return False
        
        for vector_idx, vector in enumerate(self.data):
            for x_idx, x in enumerate(vector):
                if vector_idx != x_idx and x != 0:
                    return False
                
        return True

    def is_upper_triangle(self): # TODO implement something for floating point zeros if abs(x) > 1e-9: return false If it's not "basically zero", 
        if not self.is_square():
            return False
        
        for vector_idx, vector in enumerate(self.data):
            for x_idx, x in enumerate(vector):
                if vector_idx >= x_idx and x != 0:
                    return False
        
        return True

    def is_lower_triangle(self): # TODO implement something for floating point zeros if abs(x) > 1e-9: return false If it's not "basically zero",
        if not self.is_square():
            return False
        
        for vector_idx, vector in enumerate(self.data):
            for x_idx, x in enumerate(vector):
                if vector_idx >= x_idx: # skips the items below and of the diagonal
                    continue
                if x != 0:
                    return False
        
        return True

        # TODO a much faster implementation
        # for i in range(len(self.data)):

        # for j in range(i + 1, len(self.data)):
        #     if self.data[i][j] != 0:
        #         return False
        # return True
    
    def is_zero_matrix(self):
        return not any(x for v in self.data for x in v)

    def is_echelon(self):
        """
        a little bit difficult because you have to make sure that
        1. all zero rows are at the bottom
        2. the first non-zero entry (called pivot) of a row is further to the right than the pivot above it (creating a "staircase" shape)
        note doesn't require the values of the pivots to be zeros
        not doesn't require the matrix to be a square
        """
        pass

    def is_reduced_echelon(self):
        """
        a little bit difficult because you have to make sure that
        1. all zero rows are at the bottom
        2. the first non-zero entry (called pivot) of a row is further to the right than the pivot above it (creating a "staircase" shape)
        3. every pivot value is equal to 1
        4. the pivot is the only non-zero value in its column, i.e. the values above the pivot are equal to zero
        not doesn't require the matrix to be a square
        """
        pass

    def __getattr__(self, name):
        pass # TODO figure out if you will need this

    # TODO implement Fractions
    def __str__(self):
        # return "\n".join([f"| {' '.join(map(str, row.components))} |" for row in self.data])
        if not self.data: return "Matrix([])"
        
        # Find the longest string length of any component to pad the columns
        all_elements = [str(x) for row in self.data for x in row.components]
        max_len = max(len(s) for s in all_elements)
        
        # Build the rows with padding
        lines = []
        for row in self.data:
            formatted_row = " ".join(str(x).center(max_len) for x in row.components)
            lines.append(f"| {formatted_row} |")
            
        return "\n".join(lines)
    
    # TODO Implement Fractions
    def __repr__(self):
        return f"Matrix({[row.components for row in self.data]})"
    
    def __len__(self):
        return self.row_num * self.col_num
    
    def __iter__(self):
        return iter(self.data)
    
    # TODO figure out how the __hash__ works
    def __hash__(self):
        # allows the matrix to be used in sets or as dict keys
        return hash(tuple(self.data))
    
    # Binary Operators
    def __add__(self, other):
        # Adding two matrices together
        if self._operations_possible(other):
            return Matrix([v1 + v2 for v1, v2 in zip(self.data, other.data)])
        
        # Broadcasting i.e. updating the entire matrix by a value
        if isinstance(other, (int, float)):
            return Matrix([v + other for v in self.data])

        return NotImplemented # TODO as well

    def __radd__(self, other):
        return self.__add__(other)
    
    def __iadd__(self, other):
        # Adding two matrices together using the +=
        if self._operations_possible(other):
            self.data = [v1 + v2 for v1, v2 in zip(self.data, other.data)]
            return self
        
        # Broadcasting using the +=
        if isinstance(other, (int, float)):
            self.data = [v + other for v in self.data]
            return self
        
        return NotImplemented

    def __sub__(self, other):
        # subtracting two matrices together
        if self._operations_possible(other):
            return Matrix([v1 - v2 for v1, v2 in zip(self.data, other.data)])
        
        # Broadcasting i.e. updating the entire matrix by a value
        if isinstance(other, (int, float)):
            return Matrix([v - other for v in self.data])

        return NotImplemented # TODO as well

    def __rsub__(self, other):
        return self.__sub__(other)
    
    def __isub__(self, other):
        # Subtracting two matrices from each other using the -=
        if self._operations_possible(other):
            self.data = [v1 - v2 for v1, v2 in zip(self.data, other.data)]
            return self
        
        # Broadcasting using the +=
        if isinstance(other, (int, float)):
            self.data = [v - other for v in self.data]
            return self
        
        return NotImplemented
    
    def __mul__(self, other):
        if self._is_conformable_with(other):
            B_T = other.transpose()
            return Matrix([[v1 * v2 for v2 in B_T.data] for v1 in self.data])
        
        if isinstance(other, (int, float)):
            return Matrix([v * other for v in self.data])

        # Matrix * Vector (uses rows) (used in to rotate, scale, or shear a point in space)
        if isinstance(other, Vector):
            return Vector([v * other for v in self.data])
        
        return NotImplemented

    def __rmul__(self, other):
        # Vector * Matrix (uses columns) (used in adding weights to each column in the matrix, important in statistics )
        if isinstance(other, Vector):
            return Vector([col_vec * other for col_vec in self.transpose().data])
        # TODO implement vector *= Matrix
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        
        return NotImplemented

    def __imul__(self, other):
        if self._is_conformable_with(other):
            B_T = other.transpose()
            self.data = [[v1 * v2 for v2 in B_T.data] for v1 in self.data]
            return self
        
        if isinstance(other, (int, float)):
            self.data = [v * other for v in self.data]
            return self
        
        # TODO figure out what to do when it the *= causes a new datatype, by design it shouldn't and should raise and error
        if isinstance(other, Vector):
            raise TypeError

        return NotImplemented
    
    def __pos__(self):
        return Matrix(self.data[:])
    
    def __neg__(self):
        return Matrix([-v for v in self.data])
    
    def __abs__(self):
        pass # TODO Det

    # Comparison Operators
    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False
        
        if not self.same_dimensions_as(other):
            return False
        
        return self.data == other.data
    
    def is_close(self, other, tol=1e-9):
        if not isinstance(other, Matrix):
            return False
        
        if not self.same_dimensions_as(other):
            return False
        
        # checks every single vector for near-equality
        return all(v1.is_close(v2, tol) for v1, v2 in zip(self.data, other.data))
    
    def __bool__(self):
        return any(self.data)
    
    def has_determinant_of_zero(self): # TODO implement
        pass
    
    def determinant(self):
        if not self.is_square():
            raise ValueError("Cannot calculate the determinant of a non-square matrix.")
        
        if self.is_diagonal() or self.is_upper_triangle() or self.is_lower_triangle():
            return math.prod(x for v_idx, v in enumerate(self.data) for x_idx, x in enumerate(v) if v_idx == x_idx)
        
        # TODO create a function that finds if one of the three conditions that makes the det of a matrix 0 is found
        
        if self.row_num == 1:
            return self.data[0][0]
        
        if self.row_num == 2:
            a = self.data[0][0]
            b = self.data[0][1]
            c = self.data[1][0]
            d = self.data[1][1]

            return a * d - b * c
        
        zeros_along_rows = self._row_with_most_zeros
        B_T = self.transpose()
        zeros_along_cols = B_T._row_with_most_zeros

        if zeros_along_cols[1] > zeros_along_rows[1]:
            row_idx = zeros_along_cols[0]
            matrix = B_T
        else:
            row_idx = zeros_along_rows[0]
            matrix = self

        value = 0

        for pivot_idx, pivot in enumerate(matrix.data[row_idx]):
            if pivot == 0:
                value += 0
            else:
                sign = (-1) ** (row_idx + pivot_idx + 2)
                value += sign * pivot * Matrix([Vector([x for x_idx, x in enumerate(v) if x_idx != pivot_idx]) for v_idx, v in enumerate(matrix.data) if v_idx != row_idx]).determinant()
        
        return value
    
    # TODO Cramer's rule
    # TODO the inverse function using adjoint and the gj elim
    # TODO Gaussian elimination -> produces echelon form
    # TODO Gauss-Jordan Elimination -> produces row echelon form
    # TODO rank <- use gaussian elimination
    # TODO Vector spaces and subspaces if possible and useful
    # TODO Linear Combinations
    # TODO the augment method in the matrix and the de-augment method

if __name__ == "__main__":
    m = Matrix([1, 2, 3, 4, 5, 6, 7, 8, 9], m=3, n=3)
    # print(m)
    # print(repr(m))
    # print(len(m))
    # for v in m:
    #     for i in v:
    #         print(i, end=" ")
    # print()
    # m1 = Matrix([1,2,4], [3,9,9])
    # m2 = Matrix([0,1], [1,4], [5,8])
    # print(m1 * m2)
    # m1 = Matrix([[1, 5, -3], [1, 0, 2], [3, -1 , 2]])
    # print(m1.determinant())

    from datetime import datetime

    full_data = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 5, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 6, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 8, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 9, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 10]
    ] # det = 3.6-ish million

    # full_data = [[(i * 10 + j + 1) for j in range(10)] for i in range(10)] # det = 0
    # full_data[9][9] = 100

    for row in full_data:
        print(row)

    m10 = Matrix(full_data)
    print(f"Calculating determinant for 10x10...")
    start_time = datetime.now()
    print(f"Result: {m10.determinant()}")
    end_time = datetime.now()
    delta = end_time - start_time
    print(f"Time: {delta.total_seconds()} seconds")
    # print(m10.is_lower_triangle())