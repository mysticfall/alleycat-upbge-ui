from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from typing import Callable, Sequence

import rx
from alleycat.reactive import RP, functions as rv
from rx import Observable

from alleycat.ui import Bounds, Component, Dimension, Insets
from .layout import Layout, LayoutItem


class BoxAlign(Enum):
    Begin = 0
    Center = 1
    End = 2
    Stretch = 3


class BoxDirection(Enum):
    Forward = 0
    Reverse = 1


# noinspection PyProtectedMember
class BoxLayout(Layout, ABC):
    spacing: RP[float] = rv.new_property()

    padding: RP[Insets] = rv.new_property()

    align: RP[BoxAlign] = rv.new_property()

    direction: RP[BoxDirection] = rv.new_property()

    # noinspection PyTypeChecker
    def __init__(
            self,
            spacing: float = 0,
            padding: Insets = Insets(0, 0, 0, 0),
            align: BoxAlign = BoxAlign.Center,
            direction: BoxDirection = BoxDirection.Forward) -> None:
        if spacing < 0:
            raise ValueError("Argument 'spacing' should be zero or a positive number.")

        super().__init__()

        self.spacing = spacing
        self.padding = padding
        self.align = align
        self.direction = direction

    @property
    def minimum_size(self) -> Dimension:
        return self._calculate_size(lambda i: i.component.minimum_size)

    @property
    def preferred_size(self) -> Dimension:
        return self._calculate_size(lambda i: i.component.preferred_size)

    @property
    def on_constraints_change(self) -> Observable:
        return rx.merge(super().on_constraints_change, self.observe("spacing"), self.observe("padding"))

    @abstractmethod
    def _from_size(self, size: Dimension) -> float:
        pass

    @abstractmethod
    def _to_size(self, value: float) -> Dimension:
        pass

    @abstractmethod
    def _calculate_bounds(self, size: float, offset: float, preferred: Dimension, parent: Bounds) -> Bounds:
        pass

    def perform(self, bounds: Bounds) -> None:
        s = self._from_size

        # noinspection PyTypeChecker
        children: Sequence[Component] = tuple(filter(lambda c: c.visible, map(lambda c: c.component, self.children)))

        area = bounds.copy(x=0, y=0) - self.padding
        spacing = self.spacing

        space_between = max(len(children) - 1, 0) * spacing
        space_available = s(area.size) - space_between
        space_needed = sum(map(lambda c: s(c.preferred_size), children))
        space_to_reduce = max(space_needed - space_available, 0)

        reduced_size = dict.fromkeys(children, 0.)

        def calculate_sizes_to_reduce(comps: Sequence[Component], remaining: float = space_to_reduce):
            if remaining <= 0:
                return

            target = remaining / len(comps)
            next_comps = []
            next_remaining = remaining

            for c in comps:
                available = s(c.preferred_size - c.minimum_size)

                if available > target:
                    next_comps.append(c)

                reduced = min(target, available)
                reduced_size[c] += reduced

                next_remaining -= reduced

            if len(next_comps) > 0:
                calculate_sizes_to_reduce(next_comps, next_remaining)

        calculate_sizes_to_reduce(children)

        offset = 0 if self.direction == BoxDirection.Forward else s(area.size)

        for child in children:
            preferred = child.preferred_size
            size = max(s(preferred) - reduced_size[child], 0)

            if self.direction != BoxDirection.Forward:
                offset -= size

            child.bounds = self._calculate_bounds(size, offset, preferred, area)

            offset += size + spacing if self.direction == BoxDirection.Forward else -spacing

    @abstractmethod
    def _reduce_size(self, s1: Dimension, s2: Dimension) -> Dimension:
        pass

    def _calculate_size(self, extractor: Callable[[LayoutItem], Dimension]) -> Dimension:
        children = tuple(filter(lambda c: c.component.visible, self.children))

        # noinspection PyTypeChecker
        size = reduce(self._reduce_size, map(extractor, children), Dimension(0, 0))
        spacing = self._to_size(max(len(children) - 1, 0) * self.spacing)

        (top, right, bottom, left) = self.padding.tuple

        return size + Dimension(left + right, top + bottom) + spacing


class HBoxLayout(BoxLayout):

    def __init__(
            self,
            spacing: float = 0,
            padding: Insets = Insets(0, 0, 0, 0),
            align: BoxAlign = BoxAlign.Center,
            direction: BoxDirection = BoxDirection.Forward) -> None:
        super().__init__(spacing, padding, align, direction)

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
            align: BoxAlign = BoxAlign.Center,
            direction: BoxDirection = BoxDirection.Forward) -> None:
        super().__init__(spacing, padding, align, direction)

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
