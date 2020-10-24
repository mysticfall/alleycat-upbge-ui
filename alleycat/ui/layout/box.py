from abc import ABC, abstractmethod
from enum import Enum
from typing import Sequence

import rx
from alleycat.reactive import RP
from alleycat.reactive import functions as rv
from rx import Observable
from rx import operators as ops

from alleycat.ui import Dimension, Insets, Bounds, Component
from .layout import Layout, LayoutContainer


class BoxAlign(Enum):
    Begin = 0
    Center = 1
    End = 2
    Stretch = 3


class BoxLayout(Layout, ABC):
    spacing: RP[float] = rv.new_property()

    padding: RP[Insets] = rv.new_property()

    align: RP[BoxAlign] = rv.new_property()

    # noinspection PyTypeChecker
    def __init__(
            self,
            spacing: float = 0,
            padding: Insets = Insets(0, 0, 0, 0),
            align: BoxAlign = BoxAlign.Center) -> None:
        if spacing < 0:
            raise ValueError("Argument 'spacing' should be zero or a positive number.")

        super().__init__()

        self.spacing = spacing
        self.padding = padding
        self.align = align

    @property
    def on_constraints_change(self) -> Observable:
        return rx.merge(super().on_constraints_change, self.observe("spacing"), self.observe("padding"))

    def minimum_size(self, component: LayoutContainer) -> Observable:
        return self._calculate_size(component, "effective_minimum_size")

    def preferred_size(self, component: LayoutContainer) -> Observable:
        return self._calculate_size(component, "effective_preferred_size")

    @abstractmethod
    def _from_size(self, size: Dimension) -> float:
        pass

    @abstractmethod
    def _to_size(self, value: float) -> Dimension:
        pass

    @abstractmethod
    def _calculate_bounds(self, size: float, offset: float, preferred: Dimension, parent: Bounds) -> Bounds:
        pass

    def perform(self, component: LayoutContainer) -> None:
        s = self._from_size

        # noinspection PyTypeChecker
        children: Sequence[Component] = component.children

        area = component.bounds.copy(x=0, y=0) - self.padding
        spacing = self.spacing

        space_between = max(len(children) - 1, 0) * spacing
        space_available = s(area.size) - space_between
        space_needed = sum(map(lambda c: s(c.effective_preferred_size), children))
        space_to_reduce = max(space_needed - space_available, 0)

        reduced_size = dict.fromkeys(children, 0.)

        def calculate_sizes_to_reduce(comps: Sequence[Component], remaining: float = space_to_reduce):
            if remaining <= 0:
                return

            target = remaining / len(comps)
            next_comps = []
            next_remaining = remaining

            for c in comps:
                available = s(c.effective_preferred_size - c.effective_minimum_size)

                if available > target:
                    next_comps.append(c)

                reduced = min(target, available)
                reduced_size[c] += reduced

                next_remaining -= reduced

            if len(next_comps) > 0:
                calculate_sizes_to_reduce(next_comps, next_remaining)

        calculate_sizes_to_reduce(children)

        offset = 0

        for child in children:
            preferred = child.effective_preferred_size
            size = s(preferred) - reduced_size[child]

            child.bounds = self._calculate_bounds(size, offset, preferred, area)

            offset += size + spacing

    @abstractmethod
    def _reduce_size(self, s1: Dimension, s2: Dimension) -> Dimension:
        pass

    def _calculate_size(self, component: LayoutContainer, size_attribute: str) -> Observable:
        children = component.observe("children")

        padding = self.observe("padding").pipe(ops.map(lambda p: Dimension(p.left + p.right, p.top + p.bottom)))
        spacing = rx.combine_latest(children, self.observe("spacing")).pipe(
            ops.map(lambda v: self._to_size(max(len(v[0]) - 1, 0) * v[1])))

        return self.calculate_size(children, size_attribute, self._reduce_size).pipe(
            ops.combine_latest(padding, spacing),
            ops.map(lambda v: v[0] + v[1] + v[2]))


class HBoxLayout(BoxLayout):

    def __init__(
            self,
            spacing: float = 0,
            padding: Insets = Insets(0, 0, 0, 0),
            align: BoxAlign = BoxAlign.Center) -> None:
        super().__init__(spacing, padding, align)

    def _from_size(self, size: Dimension) -> float:
        return size.width

    def _to_size(self, value: float) -> Dimension:
        return Dimension(value, 0)

    def _reduce_size(self, s1: Dimension, s2: Dimension) -> Dimension:
        return Dimension(s1.width + s2.width, max(s1.height, s2.height))

    def _calculate_bounds(self, size: float, offset: float, preferred: Dimension, area: Bounds) -> Bounds:
        align = self.align

        if align == BoxAlign.Begin:
            return Bounds(area.x + offset, area.y, size, preferred.height)
        elif align == BoxAlign.End:
            return Bounds(area.x + offset, area.y + area.height - preferred.height, size, preferred.height)
        elif align == BoxAlign.Stretch:
            return Bounds(area.x + offset, area.y, size, area.height)

        return Bounds(area.x + offset, area.y + (area.height - preferred.height) / 2., size, preferred.height)


class VBoxLayout(BoxLayout):

    def __init__(
            self,
            spacing: float = 0,
            padding: Insets = Insets(0, 0, 0, 0),
            align: BoxAlign = BoxAlign.Center) -> None:
        super().__init__(spacing, padding, align)

    def _from_size(self, size: Dimension) -> float:
        return size.height

    def _to_size(self, value: float) -> Dimension:
        return Dimension(0, value)

    def _reduce_size(self, s1: Dimension, s2: Dimension) -> Dimension:
        return Dimension(max(s1.width, s2.width), s1.height + s2.height)

    def _calculate_bounds(self, size: float, offset: float, preferred: Dimension, area: Bounds) -> Bounds:
        align = self.align

        if align == BoxAlign.Begin:
            return Bounds(area.x, area.y + offset, preferred.width, size)
        elif align == BoxAlign.End:
            return Bounds(area.x + area.width - preferred.width, area.y + offset, preferred.width, size)
        elif align == BoxAlign.Stretch:
            return Bounds(area.x, area.y + offset, area.width, size)

        return Bounds(area.x + (area.width - preferred.width) / 2., area.y + offset, preferred.width, size)
