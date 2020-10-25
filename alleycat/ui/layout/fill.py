from functools import reduce

import rx
from alleycat.reactive import RP, RV
from alleycat.reactive import functions as rv
from rx import Observable
from rx import operators as ops

from alleycat.ui import Bounds, Dimension, Insets
from .layout import Layout


class FillLayout(Layout):
    padding: RP[Insets] = rv.new_property()

    minimum_size: RV[Dimension] = rv.from_instance(
        lambda i: i.calculate_size("effective_minimum_size"), read_only=True)

    preferred_size: RV[Dimension] = rv.from_instance(
        lambda i: i.calculate_size("effective_preferred_size"), read_only=True)

    def __init__(self, padding: Insets = Insets(0, 0, 0, 0)) -> None:
        super().__init__()

        # noinspection PyTypeChecker
        self.padding = padding

    @property
    def on_constraints_change(self) -> Observable:
        return rx.merge(super().on_constraints_change, self.observe("padding"))

    def perform(self, bounds: Bounds) -> None:
        p = self.padding

        child_bounds = Bounds(
            p.top,
            p.left,
            max(bounds.width - p.left - p.right, 0),
            max(bounds.height - p.top - p.bottom, 0))

        # noinspection PyTypeChecker
        for child in self.children:
            child.bounds = child_bounds

    def calculate_size(self, size_attr: str) -> Observable:
        if size_attr is None:
            raise ValueError("Argument 'size_attribute' is required.")

        def max_size(s1: Dimension, s2: Dimension):
            return Dimension(max(s1.width, s2.width), max(s1.height, s2.height))

        return self.observe("children").pipe(
            ops.map(lambda v: map(lambda c: c.observe(size_attr), v)),
            ops.map(lambda b: rx.combine_latest(*b, rx.of(Dimension(0, 0)))),
            ops.switch_latest(),
            ops.map(lambda b: reduce(max_size, b)),
            ops.combine_latest(self.observe("padding")),
            ops.map(lambda v: Dimension(v[0].width + v[1].left + v[1].right, v[0].height + v[1].top + v[1].bottom)))
