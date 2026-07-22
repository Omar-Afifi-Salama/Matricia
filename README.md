# Matricia

A simple, straight-forward library to perform mathematical computations in the domain of linear algebra using python.

## Features

- **5 New Data types in Python**: Vector, Matrix, Point, Line, Plane
- **Overloaded dunder methods** which allow for the use of normal python arithmetic, logical and comparison operators.
- **Straight-forward syntax** highly resembling Python's syntax.
- **Incredibly fast computations** most at O(n) time and space complexity.
- **Strong OOP Architecture** including things like static methods, class methods, duck
  typing, and polymorphism.

## Installation

Install via `pip`:

```bash
pip install matricia
```

## Quickstart

### Using Vectors

```python
from matricia import Vector

v = Vector(1, 2, 3) # < 1, 2, 3 >

u = Vector(x=3, z=5) # < 3, 0 ,5 >

dot_product = u * v # 18
```

### Using Matrices

```python
from matricia import Matrix

m = Matrix([[1, 2, 3],
            [4, 5, 6]])

n = Matrix([[15, -4, 0],
            [-12, 6, 1.3]])

k = m + n

# [[16, -2, 3],
 # [-8, 11, 7.3]]
```

# License

Distributed under the MIT License.
