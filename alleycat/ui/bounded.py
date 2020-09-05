from abc import ABC

from alleycat.reactive import RV, RP
from alleycat.reactive import functions as rv

from alleycat.ui import Bounds, Dimension


class Bounded(ABC):
    bounds: RP[Bounds] = rv.from_value(Bounds(0, 0, 0, 0))

    x: RV[float] = bounds.as_view().map(lambda b: b.x)

    y: RV[float] = bounds.as_view().map(lambda b: b.y)

    width: RV[float] = bounds.as_view().map(lambda b: b.width)

    height: RV[float] = bounds.as_view().map(lambda b: b.height)

    location: RV[float] = bounds.as_view().map(lambda b: b.location)

    size: RV[Dimension] = bounds.as_view().map(lambda b: b.size)
