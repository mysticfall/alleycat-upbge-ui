from abc import ABC

from alleycat.reactive import functions as rv
from rx import operators as ops

from alleycat.ui import Bounds, Dimension, Point


class Bounded(ABC):
    bounds = rv.from_value(Bounds(0, 0, 0, 0))

    x = bounds.map(lambda b: b.x)

    y = bounds.map(lambda b: b.y)

    width = bounds.as_view().map(lambda b: b.width)

    height = bounds.as_view().map(lambda b: b.height)

    location = rv.combine_latest(x, y)(ops.map(lambda v: Point(v[0], v[1])))

    size = rv.combine_latest(width, height)(ops.map(lambda v: Dimension(v[0], v[1])))
