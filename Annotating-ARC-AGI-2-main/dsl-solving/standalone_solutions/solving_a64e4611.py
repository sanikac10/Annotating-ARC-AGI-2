# Standalone solution for ARC-AGI problem a64e4611

# Complete arc_types.py content
'''
The following is the complete content of arc_types.py:
'''
from typing import (
    List,
    Union,
    Tuple,
    Any,
    Container,
    Callable,
    FrozenSet,
    Iterable
)

Boolean = bool
Integer = int
IntegerTuple = Tuple[Integer, Integer]
Numerical = Union[Integer, IntegerTuple]
IntegerSet = FrozenSet[Integer]
Grid = Tuple[Tuple[Integer]]
Cell = Tuple[Integer, IntegerTuple]
Object = FrozenSet[Cell]
Objects = FrozenSet[Object]
Indices = FrozenSet[IntegerTuple]
IndicesSet = FrozenSet[Indices]
Patch = Union[Object, Indices]
Element = Union[Object, Grid]
Piece = Union[Grid, Patch]
TupleTuple = Tuple[Tuple]
ContainerContainer = Container[Container]


# Constants
ZERO = 0
ONE = 1
TWO = 2
THREE = 3
SIX = 6
EIGHT = 8
TEN = 10

# DSL functions
def lbind(
    function: Callable,
    fixed: Any
) -> Callable:
    """ fix the leftmost argument """
    n = function.__code__.co_argcount
    if n == 2:
        return lambda y: function(fixed, y)
    elif n == 3:
        return lambda y, z: function(fixed, y, z)
    else:
        return lambda y, z, a: function(fixed, y, z, a)


def rbind(
    function: Callable,
    fixed: Any
) -> Callable:
    """ fix the rightmost argument """
    n = function.__code__.co_argcount
    if n == 2:
        return lambda x: function(x, fixed)
    elif n == 3:
        return lambda x, y: function(x, y, fixed)
    else:
        return lambda x, y, z: function(x, y, z, fixed)


def astuple(
    a: Integer,
    b: Integer
) -> IntegerTuple:
    """ constructs a tuple """
    return (a, b)


def fill(
    grid: Grid,
    value: Integer,
    patch: Patch
) -> Grid:
    """ fill value at indices """
    h, w = len(grid), len(grid[0])
    grid_filled = list(list(row) for row in grid)
    for i, j in toindices(patch):
        if 0 <= i < h and 0 <= j < w:
            grid_filled[i][j] = value
    return tuple(tuple(row) for row in grid_filled)


def multiply(
    a: Numerical,
    b: Numerical
) -> Numerical:
    """ multiplication """
    if isinstance(a, int) and isinstance(b, int):
        return a * b
    elif isinstance(a, tuple) and isinstance(b, tuple):
        return (a[0] * b[0], a[1] * b[1])
    elif isinstance(a, int) and isinstance(b, tuple):
        return (a * b[0], a * b[1])
    return (a[0] * b, a[1] * b)
    

def fork(
    outer: Callable,
    a: Callable,
    b: Callable
) -> Callable:
    """ creates a wrapper function """
    return lambda x: outer(a(x), b(x))


def matcher(
    function: Callable,
    target: Any
) -> Callable:
    """ construction of equality function """
    return lambda x: function(x) == target


def compose(
    outer: Callable,
    inner: Callable
) -> Callable:
    """ function composition """
    return lambda x: outer(inner(x))


def chain(
    h: Callable,
    g: Callable,
    f: Callable,
) -> Callable:
    """ function composition with three functions """
    return lambda x: h(g(f(x)))


def asindices(
    grid: Grid
) -> Indices:
    """ indices of all grid cells """
    return frozenset((i, j) for i in range(len(grid)) for j in range(len(grid[0])))


def ofcolor(
    grid: Grid,
    value: Integer
) -> Indices:
    """ indices of all grid cells with value """
    return frozenset((i, j) for i, r in enumerate(grid) for j, v in enumerate(r) if v == value)


def interval(
    start: Integer,
    stop: Integer,
    step: Integer
) -> Tuple:
    """ range """
    return tuple(range(start, stop, step))


def sfilter(
    container: Container,
    condition: Callable
) -> Container:
    """ keep elements in container that satisfy condition """
    return type(container)(e for e in container if condition(e))


def toindices(
    patch: Patch
) -> Indices:
    """ indices of object cells """
    if len(patch) == 0:
        return frozenset()
    if isinstance(next(iter(patch))[1], tuple):
        return frozenset(index for value, index in patch)
    return patch



# Solver function
def solve_a64e4611(I):
    x1 = asindices(I)
    x2 = fork(product, identity, identity)
    x3 = lbind(canvas, ZERO)
    x4 = compose(asobject, x3)
    x5 = fork(multiply, first, last)
    x6 = compose(positive, size)
    x7 = lbind(lbind, shift)
    x8 = rbind(fork, x5)
    x9 = lbind(x8, multiply)
    x10 = lbind(chain, x6)
    x11 = rbind(x10, x4)
    x12 = lbind(lbind, occurrences)
    x13 = chain(x9, x11, x12)
    x14 = compose(x2, first)
    x15 = compose(x13, last)
    x16 = fork(argmax, x14, x15)
    x17 = chain(x7, x4, x16)
    x18 = compose(x4, x16)
    x19 = fork(occurrences, last, x18)
    x20 = fork(mapply, x17, x19)
    x21 = multiply(TWO, SIX)
    x22 = interval(THREE, x21, ONE)
    x23 = astuple(x22, I)
    x24 = x20(x23)
    x25 = fill(I, THREE, x24)
    x26 = interval(THREE, TEN, ONE)
    x27 = astuple(x26, x25)
    x28 = x20(x27)
    x29 = fill(x25, THREE, x28)
    x30 = astuple(x26, x29)
    x31 = x20(x30)
    x32 = fill(x29, THREE, x31)
    x33 = rbind(toobject, x32)
    x34 = rbind(colorcount, THREE)
    x35 = chain(x34, x33, neighbors)
    x36 = matcher(x35, EIGHT)
    x37 = sfilter(x1, x36)
    x38 = fill(I, THREE, x37)
    x39 = ofcolor(x38, ZERO)
    x40 = rbind(bordering, x38)
    x41 = compose(x40, initset)
    x42 = lbind(contained, THREE)
    x43 = rbind(toobject, x38)
    x44 = chain(x42, palette, x43)
    x45 = compose(x44, dneighbors)
    x46 = fork(both, x45, x41)
    x47 = sfilter(x39, x46)
    O = fill(x38, THREE, x47)
    return O



# Example usage
if __name__ == '__main__':
    # Example input grid - replace with actual test data
    test_input = ((0, 0), (0, 0))
    result = solve_a64e4611(test_input)
    print(f"Input: {test_input}")
    print(f"Output: {result}")