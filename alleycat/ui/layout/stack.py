from functools import reduce
from typing import Callable

import rx
from alleycat.reactive import RP, functions as rv
from rx import Observable

from alleycat.ui import Bounds, Dimension, Insets
from .layout import Layout, LayoutItem


# noinspection PyProtectedMember
class StackLayout(Layout):
    padding: RP[Insets] = rv.new_property()

    def __init__(self, padding: Insets = Insets(0, 0, 0, 0)) -> None:
        super().__init__()

        # noinspection PyTypeChecker
        self.padding = padding

    @property
    def minimum_size(self) -> Dimension:
        return self._calculate_size(lambda i: i.component.minimum_size)

    @property
    def preferred_size(self) -> Dimension:
        return self._calculate_size(lambda i: i.component.preferred_size)

    def _calculate_size(self, extractor: Callable[[LayoutItem], Dimension]) -> Dimension:
        children = filter(lambda c: c.component.visible, self.children)

        def merge(s1: Dimension, s2: Dimension):
            return Dimension(max(s1.width, s2.width), max(s1.height, s2.height))

        # noinspection PyTypeChecker
        (width, height) = reduce(merge, map(extractor, children), Dimension(0, 0)).tuple
        (top, right, bottom, left) = self.padding.tuple

        return Dimension(width + left + right, height + top + bottom)

    @property
    def on_constraints_change(self) -> Observable:
        return rx.merge(super().on_constraints_change, self.observe("padding"))

    def perform(self, bounds: Bounds) -> None:
        (top, right, bottom, left) = self.padding.tuple

        available = Dimension(max(bounds.width - left - right, 0), max(bounds.height - top - bottom, 0))

        # noinspection PyTypeChecker
        for child in self.children:
            fill = not ((len(child.args) > 0 and not child.args[0]) or
                        ("fill" in child.kwargs and not child.kwargs["fill"]))

            if fill:
                child.component.bounds = Bounds(left, top, available.width, available.height)
            else:
                preferred = child.component.preferred_size

                width = min(available.width, preferred.width)
                height = min(available.height, preferred.height)

                x = (bounds.width - width) / 2 + left - right
                y = (bounds.height - height) / 2 + top - bottom

                child.component.bounds = Bounds(x, y, width, height)
