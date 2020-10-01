from abc import ABC

from alleycat.reactive import RV, RP
from alleycat.reactive import functions as rv

from alleycat.ui import Bounds, Dimension, Point


class Bounded(ABC):

    def __init__(self) -> None:
        super().__init__()

    bounds: RP[Bounds] = rv.from_value(Bounds(0, 0, 0, 0))

    x: RV[float] = bounds.as_view().map(lambda b: b.x)

    y: RV[float] = bounds.as_view().map(lambda b: b.y)

    width: RV[float] = bounds.as_view().map(lambda b: b.width)

    height: RV[float] = bounds.as_view().map(lambda b: b.height)

    location: RV[float] = bounds.as_view().map(lambda b: b.location)

    size: RV[Dimension] = bounds.as_view().map(lambda b: b.size)

    offset: RV[Point]

    def move_to(self, location: Point) -> None:
        self.bounds = self.bounds.move_to(location)

    def move_by(self, offset: Point) -> None:
        self.bounds = self.bounds.move_by(offset)
