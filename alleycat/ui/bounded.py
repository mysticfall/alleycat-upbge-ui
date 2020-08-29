from abc import ABC

from alleycat.reactive import RV, RP
from alleycat.reactive import functions as rv
from rx import operators as ops

from alleycat.ui import Bounds, Dimension, Point


class Bounded(ABC):
    bounds: RP[Bounds] = rv.from_value(Bounds(0, 0, 0, 0))

    x: RV[float] = bounds.as_view().map(lambda b: b.x)

    y: RV[float] = bounds.as_view().map(lambda b: b.y)

    width: RV[float] = bounds.as_view().map(lambda b: b.width)

    height: RV[float] = bounds.as_view().map(lambda b: b.height)

    location: RV[float] = rv.combine_latest(x, y)(ops.map(lambda v: Point(v[0], v[1])))

    size: RV[Dimension] = rv.combine_latest(width, height)(ops.map(lambda v: Dimension(v[0], v[1])))
