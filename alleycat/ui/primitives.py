from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import Any, Tuple, Union, Optional, Iterable, Iterator


@dataclass(frozen=True)
class Point(Iterable):
    x: float

    y: float

    __slots__ = ["x", "y"]

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.x, self.y

    @staticmethod
    def from_tuple(value: Tuple[float, float]) -> Point:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        return Point(value[0], value[1])

    def copy(self, x: Optional[float] = None, y: Optional[float] = None) -> Point:
        return Point(x if x is not None else self.x, y if y is not None else self.y)

    def __add__(self, other: Point) -> Point:
        if other is None:
            raise ValueError("Cannot perform the operation on None.")

        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        if other is None:
            raise ValueError("Cannot perform the operation on None.")

        return self + (-other)

    def __mul__(self, number: float) -> Point:
        return Point(self.x * number, self.y * number)

    def __truediv__(self, number: float) -> Point:
        return Point(self.x / number, self.y / number)

    def __neg__(self) -> Point:
        return Point(-self.x, -self.y)

    def __iter__(self) -> Iterator[float]:
        return iter(self.tuple)


@dataclass(frozen=True)
class Dimension(Iterable):
    width: float

    height: float

    __slots__ = ["width", "height"]

    @property
    def tuple(self) -> Tuple[float, float]:
        return self.width, self.height

    @staticmethod
    def from_tuple(value: Tuple[float, float]) -> Dimension:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        return Dimension(value[0], value[1])

    def copy(self, width: Optional[float] = None, height: Optional[float] = None) -> Dimension:
        return Dimension(
            width if width is not None else self.width,
            height if height is not None else self.height)

    def __add__(self, other: Dimension) -> Dimension:
        if other is None:
            raise ValueError("Cannot perform the operation on None.")

        return Dimension(self.width + other.width, self.height + other.height)

    def __sub__(self, other: Dimension) -> Dimension:
        if other is None:
            raise ValueError("Cannot perform the operation on None.")

        return Dimension(max(self.width - other.width, 0), max(self.height - other.height, 0))

    def __mul__(self, number: float) -> Dimension:
        return Dimension(self.width * number, self.height * number)

    def __truediv__(self, number: float) -> Dimension:
        return Dimension(self.width / number, self.height / number)

    def __iter__(self) -> Iterator[float]:
        return iter(self.tuple)

    def __post_init__(self):
        _ensure_non_negative(self, "width")
        _ensure_non_negative(self, "height")


@dataclass(frozen=True)
class Bounds(Iterable):
    x: float

    y: float

    width: float

    height: float

    __slots__ = ["x", "y", "width", "height"]

    @property
    def tuple(self) -> Tuple[float, float, float, float]:
        return self.x, self.y, self.width, self.height

    @staticmethod
    def from_tuple(value: Tuple[float, float, float, float]) -> Bounds:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        return Bounds(value[0], value[1], value[2], value[3])

    def copy(self,
             x: Optional[float] = None,
             y: Optional[float] = None,
             width: Optional[float] = None,
             height: Optional[float] = None) -> Bounds:

        return Bounds(
            x if x is not None else self.x,
            y if y is not None else self.y,
            width if width is not None else self.width,
            height if height is not None else self.height)

    def __add__(self, other: Union[Point, Bounds]) -> Bounds:
        if other is None:
            raise ValueError("Cannot perform the operation on None.")

        if isinstance(other, Point):
            return Bounds(
                min(self.x, other.x),
                min(self.y, other.y),
                max(self.x + self.width, max(self.x + self.width - other.x, other.x - self.x)),
                max(self.y + self.height, max(self.y + self.height - other.y, other.y - self.y)))
        elif isinstance(other, Bounds):
            return reduce(lambda b, p: b + p, other.points, self)

        assert False

    def __mul__(self, number: float) -> Bounds:
        return Bounds(self.x, self.y, self.width * number, self.height * number)

    def __truediv__(self, number: float) -> Bounds:
        return Bounds(self.x, self.y, self.width / number, self.height / number)

    def __iter__(self) -> Iterator[float]:
        return iter(self.tuple)

    def __post_init__(self):
        _ensure_non_negative(self, "width")
        _ensure_non_negative(self, "height")

    @property
    def location(self) -> Point:
        return Point(self.x, self.y)

    @property
    def size(self) -> Dimension:
        return Dimension(self.width, self.height)

    @property
    def points(self) -> Tuple[Point, Point, Point, Point]:
        return (self.location,
                Point(self.x + self.width, self.y),
                Point(self.x + self.width, self.y + self.height),
                Point(self.x, self.y + self.height))


@dataclass(frozen=True)
class RGBA(Iterable):
    r: float

    g: float

    b: float

    a: float

    __slots__ = ["r", "g", "b", "a"]

    @property
    def tuple(self) -> Tuple[float, float, float, float]:
        return self.r, self.g, self.b, self.a

    @staticmethod
    def from_tuple(value: Tuple[float, float, float, float]) -> RGBA:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        return RGBA(value[0], value[1], value[2], value[3])

    def copy(self,
             r: Optional[float] = None,
             g: Optional[float] = None,
             b: Optional[float] = None,
             a: Optional[float] = None) -> RGBA:
        return RGBA(
            r if r is not None else self.r,
            g if g is not None else self.g,
            b if b is not None else self.b,
            a if a is not None else self.a)

    def __iter__(self) -> Iterator[float]:
        return iter(self.tuple)

    def __post_init__(self):
        _ensure_range(self, "r")
        _ensure_range(self, "g")
        _ensure_range(self, "b")
        _ensure_range(self, "a")


def _ensure_non_negative(obj: Any, attr: str) -> None:
    assert obj is not None
    assert attr is not None

    if getattr(obj, attr) < 0:
        raise ValueError(f"Argument '{attr}' must be zero or a positive number.")


def _ensure_range(obj: Any, attr: str, min_value: float = 0, max_value: float = 1) -> None:
    assert obj is not None
    assert attr is not None
    assert max_value > min_value

    value = getattr(obj, attr)

    if not (min_value <= value <= max_value):
        raise ValueError(f"Argument '{attr}' must be between {min_value} and {max_value}.")
