import rx
from alleycat.reactive import RV
from alleycat.reactive import functions as rv

from alleycat.ui import Dimension, Bounds
from .layout import Layout


class AbsoluteLayout(Layout):
    minimum_size: RV[Dimension] = rv.from_observable(rx.of(Dimension(0, 0)))

    preferred_size: RV[Dimension] = rv.from_observable(rx.of(Dimension(0, 0)))

    def __init__(self) -> None:
        super().__init__()

    def perform(self, bounds: Bounds) -> None:
        pass
