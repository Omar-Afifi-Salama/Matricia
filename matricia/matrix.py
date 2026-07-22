from __future__ import annotations
import math
from matricia.vector import Vector
from fractions import Fraction


class Matrix:
    EPSILON = 1e-9

    FRACTIONS = True

    DISPLAY_PRECISION = 1000

    def __init__(self, *args, mutable=False, **kwargs):
        """
        Supports:
        1. Matrix([[1, 2], [3, 4]]) -> List of lists
        2. Matrix([1,2], [3,4])     -> Multiple Lists
        3. Matrix(v1, v2)           -> Multiple Vector objects
        4. Matrix([v1, v2])           -> List of Vector objects
        5. Matrix([1, 2, 3, 4], rows=2, cols=2) -> Flat list with shape
        6. Matrix([n for n in range(5)]) -> Generator objects
        6. Matrix([n for n in range(5)] for _ in range(3)) -> Nested Generator objects or Map objects
        """
        self.mutable = mutable
        input_data = []

        args = list(args)

        # 2. Normalize Generators/Iterators
        if (
            len(args) == 1
            and hasattr(args[0], "__iter__")
            and not isinstance(args[0], (list, tuple, Vector, str))
        ):
            # "Drain" the generator into a list
            # args[0] becomes [item1, item2, ...]
            args[0] = list(args[0])

            # Now, check if the items INSIDE were also generators
            if (
                len(args[0]) > 0
                and hasattr(args[0][0], "__iter__")
                and not isinstance(args[0][0], (list, tuple, Vector, str))
            ):
                args[0] = [list(row) for row in args[0]]

        # Case 1 & 4 (Single positional argument)
        if len(args) == 1:
            raw_data = args[0]

            # Check for Case 4: Flat list + dimensions in kwargs
            # We look for common aliases: r/m/rows and c/n/cols
            r = (
                kwargs.get("rows")
                or kwargs.get("row")
                or kwargs.get("r")
                or kwargs.get("m")
            )
            c = (
                kwargs.get("cols")
                or kwargs.get("col")
                or kwargs.get("columns")
                or kwargs.get("c")
                or kwargs.get("n")
            )

            if r is not None and c is not None:
                if (r * c) != len(raw_data):
                    raise ValueError(
                        f"Cannot create a {r}x{c} matrix with {len(raw_data)} elements."
                    )
                # Turn [1,2,3,4] into [[1,2], [3,4]]
                input_data = [raw_data[i * c : (i + 1) * c] for i in range(r)]

            # Case 1: Already a list of lists or list of Vectors
            elif isinstance(raw_data, (list, tuple)) and all(
                isinstance(item, (list, tuple, Vector)) for item in raw_data
            ):
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
        self.data = [
            row
            if isinstance(row, Vector) and row.mutable == self.mutable
            else Vector(row, mutable=self.mutable)
            for row in input_data
        ]

        # Validation
        if self.data:
            first_len = len(self.data[0])
            if not all(len(row) == first_len for row in self.data):
                raise ValueError(
                    "Inconsistent row lengths! A matrix must be rectangular."
                )

    @property
    def is_square(self):
        return self.row_num == self.col_num

    @property
    def row_num(self):
        return len(self.data)

    @property
    def col_num(self):
        return len(self.data[0]) if self.data else 0

    def same_dimensions_as(self, other):
        if not isinstance(other, Matrix):
            return False

        return self.row_num == other.row_num and self.col_num == other.col_num

    # def _operations_possible(self, other):
    #     if not isinstance(other, Matrix):
    #         return NotImplemented

    #     if self.row_num != other.row_num or self.col_num != other.col_num:
    #         return False

    #     return True

    def _is_same_size(self, other):
        """Used for Addition and Subtraction."""
        if not isinstance(other, Matrix):
            return False
        return self.row_num == other.row_num and self.col_num == other.col_num

    def _can_multiply_with(self, other):
        """
        Used for Multiplication.
        Checks if (m x n) * (n x p) logic holds.
        """
        if isinstance(other, Matrix):
            # Columns of Left must match Rows of Right
            return self.col_num == other.row_num

        if isinstance(other, Vector):
            # Matrix * Vector: Columns of Matrix must match Vector length
            return self.col_num == len(other)

        return False

    def get_column(self, idx):
        if 0 <= idx <= self.col_num:
            return Vector([row[idx] for row in self.data])

        raise IndexError(
            f"Matrix column index {idx} out of range (0 to {self.col_num - 1})."
        )

    def transpose(self):
        # return Matrix(self.get_column(i) for i in range(self.col_num))
        return Matrix([list(item) for item in zip(*self.data)])

    def is_conformable_with(self, other):
        if not isinstance(other, Matrix):
            return False

        return self.col_num == other.row_num

    # TODO fix this
    @property
    def _row_with_most_zeros(self):
        return max(
            [(idx, sum(1 for x in v if math.isclose(x, 0, abs_tol=self.EPSILON))) for idx, v in enumerate(self.data)],
            key=lambda item: item[1],
        )

    def is_diagonal(self, tol=EPSILON):
        if not self.is_square:
            return False

        for vector_idx, vector in enumerate(self.data):
            for x_idx, x in enumerate(vector):
                if vector_idx != x_idx and not math.isclose(x, 0.0, abs_tol=tol):
                    return False

        return True

    # TODO FIXME
    def is_upper_triangle(self, tol=EPSILON):
        if not self.is_square:
            return False

        # for vector_idx, vector in enumerate(self.data):
        #     for x_idx, x in enumerate(vector):
        #         if vector_idx >= x_idx and math.isclose(x, 0.0, abs_tol=tol):
        #             return False

        for i in range(1, self.row_num):
            # Only look at columns 0 to i-1
            for j in range(i):
                if not math.isclose(self.data[i][j], 0.0, abs_tol=tol):
                    return False

        return True

    def is_lower_triangle(self, tol=EPSILON):
        if not self.is_square:
            return False

        # for vector_idx, vector in enumerate(self.data):
        #     for x_idx, x in enumerate(vector):
        #         if vector_idx >= x_idx: # skips the items below and of the diagonal
        #             continue
        #         if not math.isclose(x, 0.0, abs_tol=tol):
        #             return False

        for i, row in enumerate(self.data):
            for j, val in enumerate(row):
                # We only care about elements ABOVE the diagonal (i < j)
                if i < j:
                    # If it's NOT zero, it's not lower triangular
                    if not math.isclose(val, 0.0, abs_tol=tol):
                        return False

        return True

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

    def __getitem__(self, key):
        # Case: M[row, col] -> Returns a single float
        if isinstance(key, tuple):
            row_idx, col_idx = key
            return self.data[row_idx][col_idx]

        # Case: M[row] -> Returns a Vector (the row)
        # This also handles slicing naturally: M[0:2]
        return self.data[key]

    def __setitem__(self, key, value):
        if not self.mutable:
            raise AttributeError(
                "This Matrix is immutable. Set mutable=True to modify."
            )

        # Case: M[row, col] = 5.0
        if isinstance(key, tuple):
            row_idx, col_idx = key
            # This triggers the Vector's __setitem__, which has its own checks
            self.data[row_idx][col_idx] = float(value)

        # Case: M[row] = [1, 2, 3]
        else:
            new_row = Vector(value, mutable=self.mutable)
            if len(new_row) != self.col_num:
                raise ValueError(f"Length mismatch. Expected {self.col_num} elements.")
            self.data[key] = new_row

    def __setattr__(self, name, value):
        if name in ("data", "mutable"):
            super().__setattr__(name, value)
            return

        # Prevent adding new attributes if the matrix is immutable
        if not getattr(self, "mutable", False):
            raise AttributeError("Cannot add attributes to an immutable Matrix.")

        super().__setattr__(name, value)

    # TODO implement Fractions
    # def __str__(self):
    #     # return "\n".join([f"| {' '.join(map(str, row.components))} |" for row in self.data])
    #     if not self.data: return "Matrix([])"

    #     # Find the longest string length of any component to pad the columns
    #     all_elements = [str(x) for row in self.data for x in row.components]
    #     max_len = max(len(s) for s in all_elements)

    #     # Build the rows with padding
    #     lines = []
    #     for row in self.data:
    #         formatted_row = " ".join(str(x).center(max_len) for x in row.components)
    #         lines.append(f"| {formatted_row} |")

    #     return "\n".join(lines)

    def __str__(self):
        if not self.data:
            return "Matrix([])"

        def format_val(val):
            # MODE 1: Fractions
            if getattr(Matrix, "FRACTIONS", False):
                f = Fraction(
                    val
                ).limit_denominator(
                    getattr(Vector, "DISPLAY_PRECISION", 1000)
                )  # TODO think about if it should depend on the Matrix class attr or the Vector # i think we should use the lowest
                return str(f.numerator) if f.denominator == 1 else str(f)

            # MODE 2: Floats (Rounded)
            # Using :.4g is "smart"—it uses scientific notation only if the number is tiny
            return f"{float(val) if abs(val) > Matrix.EPSILON else 0:.4g}"  # TODO return zero if it is smaller than epsilon

        # 1. Create a 2D grid of strings using the chosen mode
        formatted_data = [[format_val(x) for x in row.components] for row in self.data]

        # 2. Calculate the max width for each column to keep things aligned
        col_widths = [
            max(len(formatted_data[r][c]) for r in range(self.row_num))
            for c in range(self.col_num)
        ]

        # 3. Build the final string
        lines = []
        for row_data in formatted_data:
            formatted_row = "  ".join(
                val.rjust(col_widths[i]) for i, val in enumerate(row_data)
            )
            lines.append(f"| {formatted_row} |")

        return "\n".join(lines)

    def __repr__(self):
        return f"Matrix({[list(row.components) for row in self.data]}, mutable={self.mutable})"

    def __len__(self):
        return self.row_num * self.col_num

    def __iter__(self):
        return iter(self.data)

    def __hash__(self):
        if self.mutable:
            raise TypeError("Mutable matrices cannot be hashed.")
        # allows the matrix to be used in sets or as dict keys
        return hash(tuple(self.data))

    # Binary Operators
    def __add__(self, other):
        # Adding two matrices together
        if self._is_same_size(other):
            return Matrix(
                [v1 + v2 for v1, v2 in zip(self.data, other.data)],
                mutable=(self.mutable and other.mutable),
            )

        # Broadcasting i.e. updating the entire matrix by a value
        if isinstance(other, (int, float)):
            return Matrix([v + other for v in self.data], mutable=self.mutable)

        return NotImplemented

    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        # Adding two matrices together using the +=
        if self._is_same_size(other):
            self.data = [v1 + v2 for v1, v2 in zip(self.data, other.data)]
            return self

        # Broadcasting using the +=
        if isinstance(other, (int, float)):
            self.data = [v + other for v in self.data]
            return self

        return NotImplemented

    def __sub__(self, other):
        # subtracting two matrices together
        if self._is_same_size(other):
            return Matrix(
                [v1 - v2 for v1, v2 in zip(self.data, other.data)],
                mutable=(self.mutable and other.mutable),
            )

        # Broadcasting i.e. updating the entire matrix by a value
        if isinstance(other, (int, float)):
            return Matrix([v - other for v in self.data], mutable=self.mutable)

        return NotImplemented

    def __rsub__(self, other):
        return -(self - other)

    def __isub__(self, other):
        # Subtracting two matrices from each other using the -=
        if self._is_same_size(other):
            self.data = [v1 - v2 for v1, v2 in zip(self.data, other.data)]
            return self

        # Broadcasting using the +=
        if isinstance(other, (int, float)):
            self.data = [v - other for v in self.data]
            return self

        return NotImplemented

    def __mul__(self, other):
        if self.is_conformable_with(other):
            B_T = other.transpose()
            return Matrix(
                [[v1 * v2 for v2 in B_T.data] for v1 in self.data],
                mutable=(self.mutable and other.mutable),
            )

        if isinstance(other, (int, float)):
            return Matrix([v * other for v in self.data], mutable=self.mutable)

        # Matrix * Vector (uses rows) (used in to rotate, scale, or shear a point in space)
        if isinstance(other, Vector):
            return Vector([v * other for v in self.data], mutable=self.mutable)

        return NotImplemented

    def __rmul__(self, other):
        # Vector * Matrix (uses columns) (used in adding weights to each column in the matrix, important in statistics )
        if isinstance(other, Vector):
            return Vector(
                [col_vec * other for col_vec in self.transpose().data],
                mutable=(self.mutable and other.mutable),
            )

        # TODO implement vector *= Matrix
        if isinstance(other, (int, float)):
            return self * other

        return NotImplemented

    def __imul__(self, other):
        if self.is_conformable_with(other):
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

    def __truediv__(self, other):
        """Scalar Division: Matrix / scalar"""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Matrix division by zero.")
            # Map the division across all Vector rows
            return Matrix([row / other for row in self.data], mutable=self.mutable)
        return NotImplemented

    def __itruediv__(self, other):
        """In-place Scalar Division: Matrix /= scalar"""
        if not self.mutable:
            return self.__truediv__(other)

        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Matrix division by zero.")
            for row in self.data:
                row /= other  # Vector handles its own in-place division
            return self
        return NotImplemented

    def __floordiv__(self, other):
        """Floor Division: Matrix // scalar"""
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Matrix division by zero.")
            return Matrix([row // other for row in self.data], mutable=self.mutable)
        return NotImplemented

    def __ifloordiv__(self, other):
        """In-place Floor Division: Matrix //= scalar"""
        if not self.mutable:
            return self.__floordiv__(other)

        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Matrix division by zero.")
            for row in self.data:
                row //= other
            return self
        return NotImplemented

    def __pow__(self, exponent):
        """Matrix Power: M ** n"""
        if not self.is_square:
            raise ValueError("Matrix power is only defined for square matrices.")

        if not isinstance(exponent, int):
            raise TypeError("Matrix exponent must be an integer.")

        # Case: M ** 0 -> Identity Matrix
        if exponent == 0:
            return Matrix.generate_identity_matrix(self.row_num, mutable=self.mutable)

        if exponent < 0:
            # Technically M^-n is (M.inverse()) ** n
            base_matrix = self.inverse()
            exponent = abs(exponent)
        else:
            base_matrix = self.copy()

        # Case: M ** 1 -> Copy of self
        if exponent == 1:
            return base_matrix

        # Case: M ** n -> Repeated Multiplication
        result = base_matrix

        for _ in range(exponent - 1):
            result = result * base_matrix

        return result

    def __ipow__(self, exponent):
        """In-place Matrix Power: M **= n"""
        # 1. Check if the matrix is square
        if not self.is_square:
            raise ValueError("Matrix power is only defined for square matrices.")

        # 2. If immutable, return a new object (standard Python)
        if not self.mutable:
            return self.__pow__(exponent)

        # 3. Use the existing __pow__ logic to get the result
        result = self.__pow__(exponent)

        # 4. SWAP: Point our internal data to the result's data
        self.data = result.data

        # 5. Return self to satisfy the 'm **= n' contract
        return self

    # Unary Operators
    def __pos__(self):
        return Matrix(self.data[:])

    def __neg__(self):
        return Matrix([-v for v in self.data])

    def __abs__(self):
        return Matrix([abs(vec) for vec in self.data], mutable=self.mutable)

    # Comparison Operators
    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False

        if not self.same_dimensions_as(other):
            return False

        return self.data == other.data

    def __ne__(self, other):
        return not self == other

    def is_close(self, other, tol=EPSILON):
        if not isinstance(other, Matrix):
            return False

        if not self.same_dimensions_as(other):
            return False

        # checks every single vector for near-equality
        return all(v1.is_close(v2, tol) for v1, v2 in zip(self.data, other.data))

    def __bool__(
        self,
    ):  # TODO implement the option to choose between strict and lenient zero
        return any(self.data)

    def is_zero_matrix(self, tol=EPSILON):
        # return not bool(self)
        return all(row.is_zero_vector(tol=tol) for row in self.data)

    def has_determinant_of_zero(self):  # TODO implement
        pass

    def copy(self, mutable=None):

        if mutable is None or not isinstance(mutable, bool):
            mutable = self.mutable

        return Matrix(
            [Vector(list(row.components), mutable=mutable) for row in self.data],
            mutable=mutable,
        )

    def row_echelon_form(self, tol=EPSILON) -> Matrix:

        m = self.copy(mutable=True)

        pivot_row = 0

        for col_num in range(m.col_num):
            target_row = pivot_row

            while target_row < m.row_num and math.isclose(
                m[target_row][col_num], 0.0, abs_tol=tol
            ):
                target_row += 1

            if target_row == m.row_num:
                continue

            if target_row != pivot_row:
                m.data[pivot_row], m.data[target_row] = (
                    m.data[target_row],
                    m.data[pivot_row],
                )

            for i in range(pivot_row + 1, m.row_num):
                factor = m[i][col_num] / m[pivot_row][col_num]
                m[i] -= factor * m[pivot_row]

            pivot_row += 1

            if pivot_row >= m.row_num:
                break

        return m.copy(mutable=self.mutable)

    def reduced_row_echelon_form(self) -> Matrix:

        m = self.copy(mutable=True)
        pivot_row = 0

        for col_num in range(m.col_num):
            target_row = pivot_row

            # Find the pivot
            while target_row < m.row_num and math.isclose(
                m[target_row][col_num], 0.0, abs_tol=1e-9
            ):
                target_row += 1

            if target_row == m.row_num:
                continue

            # Swap rows if necessary
            if target_row != pivot_row:
                m.data[pivot_row], m.data[target_row] = (
                    m.data[target_row],
                    m.data[pivot_row],
                )

            # --- RREF STEP 1: Normalize the Pivot ---
            # We divide the entire row by the pivot value to make the pivot exactly 1.
            pivot_val = m[pivot_row][col_num]
            m[pivot_row] = (1 / pivot_val) * m[pivot_row]

            # --- RREF STEP 2: Eliminate ABOVE and BELOW ---
            # We loop through EVERY row in the matrix, not just the ones below.
            for i in range(m.row_num):
                if i == pivot_row:
                    continue  # Do not subtract the pivot row from itself!

                # Since our pivot is exactly 1, the factor is simply the number we want to kill
                factor = m[i][col_num]
                m[i] -= factor * m[pivot_row]

            pivot_row += 1

            if pivot_row >= m.row_num:
                break

        return m.copy(mutable=self.mutable)

    def is_in_row_echelon_form(self) -> bool:
        # We track the column index of the previous row's pivot
        # We start at -1 because the first pivot can be at column 0
        prev_pivot_col = -1

        for row in self.data:
            # 1. Find the current row's pivot column index
            current_pivot_col = -1
            for idx, val in enumerate(row.components):
                if not math.isclose(val, 0.0, abs_tol=1e-9):
                    current_pivot_col = idx
                    break

            # 2. Check the Rules:
            if current_pivot_col == -1:
                # This is a zero row. From now on, every row must be a zero row.
                # We set the "prev_pivot_col" to a huge number so that any
                # non-zero row following this will fail the 'current > prev' check.
                prev_pivot_col = float("inf")
            else:
                # This is a non-zero row.
                # It MUST have a pivot further right than the last one.
                if current_pivot_col <= prev_pivot_col:
                    return False

                prev_pivot_col = current_pivot_col

        return True

    def is_in_reduced_row_echelon_form(self, tol=1e-9) -> bool:

        prev_pivot_col = -1

        for r_idx, row in enumerate(self.data):
            current_pivot_col = -1

            # 1. Find the pivot in the current row
            for c_idx, val in enumerate(row.components):
                if not math.isclose(val, 0.0, abs_tol=tol):
                    current_pivot_col = c_idx
                    break

            # If the row is all zeros
            if current_pivot_col == -1:
                prev_pivot_col = float("inf")
                continue

            # 2. Check the Staircase Rule (Ensures REF)
            # If this pivot is not strictly to the right of the last one, it fails.
            if current_pivot_col <= prev_pivot_col:
                return False

            # 3. Check the "Pivot is One" Rule
            # The pivot itself MUST be exactly 1.
            if not math.isclose(row.components[current_pivot_col], 1.0, abs_tol=tol):
                return False

            # 4. Check the "Zero Above" Rule
            # We loop from the top row down to the row right above our current one.
            for i in range(r_idx):
                if not math.isclose(self[i][current_pivot_col], 0.0, abs_tol=tol):
                    return False

            prev_pivot_col = current_pivot_col

        return True

    def determinant_using_laplace_expansion(self):
        if not self.is_square:
            raise ValueError("Cannot calculate the determinant of a non-square matrix.")

        if self.is_diagonal() or self.is_upper_triangle() or self.is_lower_triangle():
            return math.prod(
                x
                for v_idx, v in enumerate(self.data)
                for x_idx, x in enumerate(v)
                if v_idx == x_idx
            )

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
                value += (
                    sign
                    * pivot
                    * Matrix(
                        [
                            Vector(
                                [x for x_idx, x in enumerate(v) if x_idx != pivot_idx]
                            )
                            for v_idx, v in enumerate(matrix.data)
                            if v_idx != row_idx
                        ]
                    ).determinant()
                )

        return value

    def determinant(self) -> float:
        if not self.is_square:
            raise ValueError("Cannot calculate the determinant of a non-square matrix.")

        # 1. Work on a copy
        m = self.copy(mutable=True)
        swap_count = 0
        pivot_row = 0

        # 2. Run your exact REF logic
        for col_num in range(m.col_num):
            target_row = pivot_row
            while target_row < m.row_num and math.isclose(
                m[target_row][col_num], 0.0, abs_tol=1e-9
            ):
                target_row += 1

            if target_row == m.row_num:
                # If we skip a column on the diagonal, there's a zero on the main diagonal.
                # The product of the diagonal will be 0, so the determinant is 0!
                return 0.0

            # --- TRACK THE SWAP ---
            if target_row != pivot_row:
                m.data[pivot_row], m.data[target_row] = (
                    m.data[target_row],
                    m.data[pivot_row],
                )
                swap_count += 1
            # ----------------------

            # Standard elimination (does not change determinant)
            for i in range(pivot_row + 1, m.row_num):
                factor = m[i][col_num] / m[pivot_row][col_num]
                m[i] -= factor * m[pivot_row]

            pivot_row += 1

        # 3. Calculate the product of the main diagonal
        det = 1.0
        for i in range(m.row_num):
            det *= m[i][i]

        # 4. Apply the sign flip from the swaps
        if swap_count % 2 != 0:
            det *= -1

        return det

    @property
    def rank(self):
        if not self.is_in_row_echelon_form():
            m = self.row_echelon_form()
        else:
            m = self.copy()

        return sum([1 if v else 0 for v in m])

    @staticmethod
    def generate_identity_matrix(size, mutable=False):
        return Matrix(
            [[1 if i == j else 0 for j in range(size)] for i in range(size)],
            mutable=mutable,
        )

    @staticmethod
    def generate_zero_matrix(rows, cols, mutable=False):
        return Matrix([[0 for _ in range(cols)] for _ in range(rows)], mutable=mutable)

    def is_identity_matrix(self, tol=EPSILON):
        if not self.is_square:
            return False

        for i in range(self.row_num):
            for j in range(self.col_num):
                if i == j:
                    if not math.isclose(self[i][j], 1, abs_tol=tol):
                        return False
                else:
                    if not math.isclose(self[i][j], 0, abs_tol=tol):
                        return False

        return True

    def normalize(self):
        # The sum of the squares of the magnitudes of all row vectors
        return math.sqrt(sum(sum(x**2 for x in row) for row in self.data))

    def is_singular(self, tol=EPSILON):
        return math.isclose(self.determinant(), 0.0, abs_tol=tol)

    def is_non_singular(self, tol=EPSILON):
        return not self.is_singular(tol=tol)

    def inverse_using_adjoint(self):
        if not self.is_square:
            raise TypeError("There is no inverse for a non-square matrix.")

        det_A = self.determinant()

        if math.isclose(det_A, 0.0, abs_tol=self.EPSILON):
            raise ValueError("There is no inverse for a singular matrix.")

        return Matrix(
            [
                [
                    (1 / det_A)
                    * ((-1) ** (i + j))
                    * Matrix(
                        [
                            [self.data[r][c] for c in range(self.col_num) if c != i]
                            for r in range(self.row_num)
                            if r != j
                        ]
                    ).determinant()
                    for j in range(self.col_num)
                ]
                for i in range(self.row_num)
            ],
            mutable=self.mutable,
        )

    @staticmethod
    def are_inverses(m1: Matrix, m2: Matrix) -> bool:
        if not m1.is_square or not m2.is_square:
            return False

        if not m1.same_dimensions_as(m2):
            return False

        return (m1 * m2).is_identity_matrix()

    @staticmethod
    def generate_random_matrix(
        rows, cols, mutable=False, lower_limit=-100, upper_limit=100
    ):
        import random

        return Matrix(
            (
                [random.randint(lower_limit, upper_limit) for _ in range(cols)]
                for _ in range(rows)
            ),
            mutable=mutable,
        )

    # def augment(self, other) -> 'Matrix':
    #     """Glues another matrix to the right side of this one."""
    #     if self.row_num != other.row_num:
    #         raise ValueError("Matrices must have the same number of rows to augment.")

    #     # We grab the pure float/Fraction lists, add them together, and wrap in a new Vector
    #     new_data = [
    #         Vector(self.data[i].components + other.data[i].components)
    #         for i in range(self.row_num)
    #     ]

    #     return Matrix(new_data, mutable=self.mutable)

    def augment(self, other) -> "Matrix":
        """Glues another Matrix or a column Vector to the right side of this matrix."""

        if isinstance(other, Vector):
            if self.row_num != len(other.components):
                raise ValueError(
                    f"Vector length ({len(other.components)}) must match matrix rows ({self.row_num})."
                )

            new_data = [
                Vector(list(self.data[i].components) + [other.components[i]])
                for i in range(self.row_num)
            ]

        elif isinstance(other, Matrix):
            if self.row_num != other.row_num:
                raise ValueError(
                    "Matrices must have the same number of rows to augment."
                )

            new_data = [
                Vector(list(self.data[i].components) + list(other.data[i].components))
                for i in range(self.row_num)
            ]

        else:
            raise TypeError("Can only augment with a Matrix or a Vector.")

        return Matrix(new_data, mutable=self.mutable)

    def extract_left(self, split_index: int) -> "Matrix":
        """Extracts all columns from the start (included) of the matrix to the split_index (excluded)."""
        new_data = [Vector(row.components[:split_index]) for row in self.data]
        return Matrix(new_data, mutable=self.mutable)

    def extract_right(self, split_index: int) -> "Matrix":
        """Extracts all columns from split_index (included) to the end of the matrix (included)."""
        new_data = [Vector(row.components[split_index:]) for row in self.data]
        return Matrix(new_data, mutable=self.mutable)

    def inverse(self):
        if self.row_num != self.col_num:
            raise TypeError("There is no inverse for a non-square matrix.")

        if math.isclose(self.determinant(), 0.0, abs_tol=1e-9):
            raise ValueError("Matrix is singular (determinant is 0).")

        # 2. Create the Augmented Matrix [A | I]
        identity = Matrix.generate_identity_matrix(self.row_num)
        augmented_m = self.augment(identity)

        # 3. Let your flawless algorithm do the heavy lifting
        rref_m = augmented_m.reduced_row_echelon_form()

        # 4. Slice off the right half. The split index is just the width of the original matrix!
        return rref_m.extract_right(self.col_num)

    def has_no_solution(self, other) -> bool:
        """Checks if the system Ax = b has no solution."""
        augmented = self.augment(other)
        return self.rank != augmented.rank

    def has_unique_solution(self, other) -> bool:
        """Checks if the system Ax = b has exactly one unique solution."""
        augmented = self.augment(other)
        return (self.rank == augmented.rank) and (self.rank == self.col_num)

    def has_infinite_solutions(self, other) -> bool:
        """Checks if the system Ax = b has infinite solutions (free variables)."""
        augmented = self.augment(other)
        return (self.rank == augmented.rank) and (self.rank < self.col_num)

    def num_free_variables(self, other=None) -> int:
        """
        Calculates the number of free variables in the system.
        If an augmented vector/matrix 'other' is provided, it ensures the system is consistent.
        """
        # Safety Check: If they provided b
        if other is not None:
            if self.has_no_solution(other):
                raise ValueError(
                    "The system is inconsistent. Free variables are undefined for systems with no solution."
                )

        # The Rank-Nullity Formula
        # Number of Variables (Columns) - Number of Independent Equations (Rank)
        free_vars = self.col_num - self.rank

        # Return the result (will be 0 for unique solutions, >0 for infinite)
        return free_vars

    def solve(self, other: Vector | Matrix) -> Vector:
        """Rule: A * X = B
              A(self) * X(unknown) = B(other)

        If other is a matrix:
         self * unknown = other
         self.solve(other) -> solution for unknown

        If other is a vector:
         The result is the solution of a system of linear equations.
        """
        # safety checks
        if self.has_no_solution(other):
            raise ValueError("The system is inconsistent and has no solution.")

        if self.has_infinite_solutions(other):
            raise ValueError(
                "The system is linearly dependent and has infinite solutions."
            )

        rref_augmented_matrix = self.augment(other).reduced_row_echelon_form()

        solution_matrix = rref_augmented_matrix.extract_right(self.col_num)

        if isinstance(other, Vector):
            return Vector(
                [row.components[0] for row in solution_matrix.data],
                mutable=self.mutable,
            )

        return solution_matrix

    @classmethod
    def from_columns(cls, *vectors, mutable=False):
        """Creates a Matrix where each provided Vector becomes a column."""
        if not vectors:
            raise ValueError("Must provide at least one vector.")

        if len(vectors) == 1 and isinstance(vectors[0], (list, tuple)):
            vectors = vectors[0]

        # Ensure all vectors are the same height
        row_count = len(vectors[0].components)

        if any(len(v.components) != row_count for v in vectors):
            raise ValueError("All column vectors must have the same dimension.")

        # Build the rows by grabbing the i-th element from every vector
        new_data = [
            Vector([v.components[i] for v in vectors]) for i in range(row_count)
        ]

        return cls(new_data, mutable=mutable)

    def vectorize(self, by_column=False):
        if not by_column:
            # Row-Major Vectorization
            return Vector(
                [x for vec in self.data for x in vec.components], mutable=self.mutable
            )
        else:
            # Column-Major Vectorization
            return Vector(
                [
                    self.data[r][c]
                    for c in range(self.col_num)
                    for r in range(self.row_num)
                ],
                mutable=self.mutable,
            )

    @classmethod
    def from_vector(
        cls, vector, row_num: int, col_num: int, by_column=False, mutable=False
    ):
        """
        Reshapes a 1D Vector back into a 2D Matrix (Matricization).
        """
        if len(vector.components) != row_num * col_num:
            raise ValueError(
                f"Cannot reshape a vector of size {len(vector.components)} into a {row_num}x{col_num} matrix."
            )

        if not by_column:
            # Row-Major Matricization
            return cls(
                [
                    Vector(vector.components[i * col_num : (i + 1) * col_num])
                    for i in range(row_num)
                ],
                mutable=vector.mutable,
            )
        else:
            # Column-Major Matricization
            return cls(
                [
                    Vector([vector.components[r + c * row_num] for c in range(col_num)])
                    for r in range(row_num)
                ],
                mutable=vector.mutable,
            )

    # TODO Linear Combinations
    def get_linear_combination(self, *matrices: Matrix) -> Matrix:
        # M_vectorized = self.vectorize()
        # matrices_vectorized = [m.vectorize() for m in matrices]

        # solution = M_vectorized.get_linear_combination(matrices_vectorized)

        # return solution.matricization(self.row_num, self.col_num)
        M_vectorized = self.vectorize()
        matrices_vectorized = [m.vectorize() for m in matrices]

        # solution = M_vectorized.get_linear_combination(matrices_vectorized)

        A = Matrix.from_columns(*matrices_vectorized)

        if A.has_no_solution(M_vectorized):
            return None

        # return solution.matricization(self.row_num, self.col_num)
        return A.solve(M_vectorized)
    
    def is_symmetric(self):

        B_T = self.transpose()
        return self.data == B_T.data
    
    def is_skew_symmetric(self):

        B_T = - self.transpose()
        return self.data == B_T.data
    
    @property
    def trace(self):
        if not self.is_square:
            raise TypeError("There is no trace for a square matrix.")
        
        sum = 0
        
        for row_idx in range(self.row_num):
            for col_idx in range(self.col_num):
                if row_idx == col_idx:
                    sum += self[row_idx][col_idx]

        return sum
    
    def is_over_determined(self):
        return self.row_num > self.col_num
    
    def is_under_determined(self):
        return self.col_num > self.row_num
    
    def solve_using_cramers(self, idx_to_solve:int|list, vector:Vector):

        if not (isinstance(vector, Vector) and self.row_num == len(vector)):
            raise ValueError("The length of the vector must be equal to the matrix's row number")
        
        original_det = self.determinant()

        if original_det == 0:
            raise ZeroDivisionError("Cramer's rule cannot be used to solve matrices that have a determinant of zero.")

        solution_det = []

        # if it is a single value, turn it into a list so the main loop doesn't crash
        if isinstance(idx_to_solve, int):
            idx_to_solve = [idx_to_solve]

        for idx in idx_to_solve:
            m = Matrix(
                [
                    [col if col_idx != idx else vector[row_idx] for col_idx, col in enumerate(row)] for row_idx, row in enumerate(self.data)
                ]
            )

            solution_det.append(m.determinant())

        # if only value was wanted, then just return it
        if len(solution_det) == 1:
            return solution_det[0] / original_det
        
        # else return it as a vector # TODO maybe it would be better if it is a tuple or list
        return Vector([det / original_det for det in solution_det], mutable=self.mutable)
    
    def is_linearly_independent(self):

        if self.is_square:
            if self.determinant() == 0:
                return False
            else:
                return True
            
        rref_self = self.reduced_row_echelon_form()

        return rref_self.rank == self.row_num
    
    def is_linearly_dependent(self):

        return not self.is_linearly_independent()
    
    def get_basis():
        pass

    def null_space():
        pass

    def change_basis():
        pass

    norm = normalize
    identity = generate_identity_matrix

    # TODO augment with a matrix -> return augmented matrix

    # TODO Vector spaces, subspaces, spans, bases if possible and useful
    # TODO eigenvalues and eigenvectors
    # TODO clean up code base and do code review
    # TODO publish to PyPi
    # TODO README File
    # TODO Finite Shapes classes in space


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

    # print(m10.is_lower_triangle())

# TODO implement this code snippet across the library
# def MutableMatrix(*args, **kwargs):
#     return Matrix(*args, mutable=True, **kwargs)
