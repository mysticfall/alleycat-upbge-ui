import rx
from alleycat.reactive import RP
from alleycat.reactive import functions as rv
from rx import Observable
from rx import operators as ops

from alleycat.ui import Bounds, Dimension, Insets
from .layout import Layout, LayoutContainer


class FillLayout(Layout):
    padding: RP[Insets] = rv.new_property()

    def __init__(self, padding: Insets = Insets(0, 0, 0, 0)) -> None:
        super().__init__()

        # noinspection PyTypeChecker
        self.padding = padding

    @property
    def on_constraints_change(self) -> Observable:
        return rx.merge(super().on_constraints_change, self.observe("padding"))

    def perform(self, component: LayoutContainer) -> None:
        p = self.padding

        bounds = Bounds(
            p.top,
            p.left,
            max(component.width - p.left - p.right, 0),
            max(component.height - p.top - p.bottom, 0))

        # noinspection PyTypeChecker
        for child in component.children:
            child.bounds = bounds

    def minimum_size(self, component: LayoutContainer) -> Observable:
        return self._calculate_size(component, "effective_minimum_size")

    def preferred_size(self, component: LayoutContainer) -> Observable:
        return self._calculate_size(component, "effective_preferred_size")

    def _calculate_size(self, component: LayoutContainer, size_attribute: str) -> Observable:
        children = component.observe("children")

        def max_size(s1: Dimension, s2: Dimension):
            return Dimension(max(s1.width, s2.width), max(s1.height, s2.height))

        return self.calculate_size(children, size_attribute, max_size).pipe(
            ops.combine_latest(self.observe("padding")),
            ops.map(lambda v: Dimension(v[0].width + v[1].left + v[1].right, v[0].height + v[1].top + v[1].bottom)))
