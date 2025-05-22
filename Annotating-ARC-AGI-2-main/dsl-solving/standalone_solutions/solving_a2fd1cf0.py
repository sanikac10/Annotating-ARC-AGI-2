# Standalone solution for ARC-AGI problem a2fd1cf0

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
TWO = 2
THREE = 3
EIGHT = 8

# DSL functions
def connect(
    a: IntegerTuple,
    b: IntegerTuple
) -> Indices:
    """ line between two points """
    ai, aj = a
    bi, bj = b
    si = min(ai, bi)
    ei = max(ai, bi) + 1
    sj = min(aj, bj)
    ej = max(aj, bj) + 1
    if ai == bi:
        return frozenset((ai, j) for j in range(sj, ej))
    elif aj == bj:
        return frozenset((i, aj) for i in range(si, ei))
    elif bi - ai == bj - aj:
        return frozenset((i, j) for i, j in zip(range(si, ei), range(sj, ej)))
    elif bi - ai == aj - bj:
        return frozenset((i, j) for i, j in zip(range(si, ei), range(ej - 1, sj - 1, -1)))
    return frozenset()


def combine(
    a: Container,
    b: Container
) -> Container:
    """ union """
    return type(a)((*a, *b))


def astuple(
    a: Integer,
    b: Integer
) -> IntegerTuple:
    """ constructs a tuple """
    return (a, b)


def minimum(
    container: IntegerSet
) -> Integer:
    """ minimum """
    return min(container, default=0)


def leftmost(
    patch: Patch
) -> Integer:
    """ column index of leftmost occupied cell """
    return min(j for i, j in toindices(patch))


def maximum(
    container: IntegerSet
) -> Integer:
    """ maximum """
    return max(container, default=0)


def underfill(
    grid: Grid,
    value: Integer,
    patch: Patch
) -> Grid:
    """ fill value at indices that are background """
    h, w = len(grid), len(grid[0])
    bg = mostcolor(grid)
    g = list(list(r) for r in grid)
    for i, j in toindices(patch):
        if 0 <= i < h and 0 <= j < w:
            if g[i][j] == bg:
                g[i][j] = value
    return tuple(tuple(r) for r in g)


def uppermost(
    patch: Patch
) -> Integer:
    """ row index of uppermost occupied cell """
    return min(i for i, j in toindices(patch))


def ofcolor(
    grid: Grid,
    value: Integer
) -> Indices:
    """ indices of all grid cells with value """
    return frozenset((i, j) for i, r in enumerate(grid) for j, v in enumerate(r) if v == value)


def toindices(
    patch: Patch
) -> Indices:
    """ indices of object cells """
    if len(patch) == 0:
        return frozenset()
    if isinstance(next(iter(patch))[1], tuple):
        return frozenset(index for value, index in patch)
    return patch


def mostcolor(
    element: Element
) -> Integer:
    """ most common color """
    values = [v for r in element for v in r] if isinstance(element, tuple) else [v for v, _ in element]
    return max(set(values), key=values.count)
    


# Solver function
def solve_a2fd1cf0(I):
    x1 = ofcolor(I, TWO)
    x2 = ofcolor(I, THREE)
    x3 = uppermost(x1)
    x4 = leftmost(x1)
    x5 = uppermost(x2)
    x6 = leftmost(x2)
    x7 = astuple(x3, x5)
    x8 = minimum(x7)
    x9 = maximum(x7)
    x10 = astuple(x8, x6)
    x11 = astuple(x9, x6)
    x12 = connect(x10, x11)
    x13 = astuple(x4, x6)
    x14 = minimum(x13)
    x15 = maximum(x13)
    x16 = astuple(x3, x14)
    x17 = astuple(x3, x15)
    x18 = connect(x16, x17)
    x19 = combine(x12, x18)
    O = underfill(I, EIGHT, x19)
    return O



# Example usage
if __name__ == '__main__':
    # Example input grid - replace with actual test data
    test_input = ((0, 0), (0, 0))
    result = solve_a2fd1cf0(test_input)
    print(f"Input: {test_input}")
    print(f"Output: {result}")