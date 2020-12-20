from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from typing import Any, Callable, Mapping, Sequence

from alleycat.reactive import ReactiveObject
from returns.maybe import Maybe, Nothing, Some
from returns.result import ResultE, safe

from alleycat.ui import Bounds, Component, Dimension, Insets
from .layout import Layout


class Border(Enum):
    Center = 0
    Top = 1
    Right = 2
    Bottom = 3
    Left = 4


# noinspection PyProtectedMember
class BorderLayout(Layout):

    def __init__(self) -> None:
        self._areas = {
            Border.Center: BorderItem(Border.Center),
            Border.Top: BorderItem(Border.Top),
            Border.Right: BorderItem(Border.Right),
            Border.Bottom: BorderItem(Border.Bottom),
            Border.Left: BorderItem(Border.Left)
        }

        self._column = BorderColumn(self.areas[Border.Left], self.areas[Border.Center], self.areas[Border.Right])
        self._row = BorderRow(self.areas[Border.Top], self.column, self.areas[Border.Bottom])

        super().__init__()

    @property
    def areas(self) -> Mapping[Border, BorderItem]:
        return self._areas

    @property
    def column(self) -> BorderColumn:
        return self._column

    @property
    def row(self) -> BorderRow:
        return self._row

    @property
    def minimum_size(self) -> Dimension:
        return self.row.minimum_size if self.row.visible else Dimension(0, 0)

    @property
    def preferred_size(self) -> Dimension:
        return self.row.preferred_size if self.row.visible else Dimension(0, 0)

    def add(self, child: Component, *args, **kwargs) -> None:
        @safe
        def parse(a, key) -> ResultE[Any]:
            return a[key]

        region: Border = parse(args, 0) \
            .lash(lambda _: parse(kwargs, "region")) \
            .value_or(Border.Center)  # type:ignore

        padding: Insets = parse(args, 1) \
            .lash(lambda _: parse(kwargs, "padding")) \
            .value_or(Insets(0, 0, 0, 0))  # type:ignore

        super().add(child, *args, **kwargs)

        area = self.areas[region]
        area.component = Some(child)
        area.padding = padding

    def remove(self, child: Component) -> None:
        super().remove(child)

        c = Some(child)

        for area in self.areas.values():
            if area.component == c:
                area.component = Nothing

    def perform(self, bounds: Bounds) -> None:
        if self.row != Nothing and self.row.visible:
            self.row.bounds = bounds

    def dispose(self) -> None:
        self.row.dispose()
        self.column.dispose()

        # noinspection PyTypeChecker
        for item in self.areas.values():
            item.dispose()

        super().dispose()


class BorderArea(ReactiveObject, ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def visible(self) -> bool:
        pass

    @property
    @abstractmethod
    def minimum_size(self) -> Dimension:
        pass

    @property
    @abstractmethod
    def preferred_size(self) -> Dimension:
        pass

    # FIXME: See mypy#4165
    @property  # type: ignore
    @abstractmethod
    def bounds(self) -> Bounds:
        pass

    # FIXME: See mypy#1362
    @bounds.setter  # type: ignore
    @abstractmethod
    def bounds(self, bounds: Bounds) -> None:
        pass


# noinspection PyProtectedMember
class BorderStrip(BorderArea, ABC):

    def __init__(self, begin: BorderArea, center: BorderArea, end: BorderArea) -> None:
        if begin is None:
            raise ValueError("Argument 'begin' is required.")

        if center is None:
            raise ValueError("Argument 'center' is required.")

        if end is None:
            raise ValueError("Argument 'end' is required.")

        self._begin = begin
        self._center = center
        self._end = end
        self._areas = (begin, center, end)

        super().__init__()

    @property
    def begin(self) -> BorderArea:
        return self._begin

    @property
    def center(self) -> BorderArea:
        return self._center

    @property
    def end(self) -> BorderArea:
        return self._end

    @property
    def areas(self) -> Sequence[BorderArea]:
        return self._areas

    @property
    def visible(self) -> bool:
        return any(map(lambda i: i.visible, self._areas))

    @property
    def minimum_size(self) -> Dimension:
        return self._calculate_size(lambda a: a.minimum_size)

    @property
    def preferred_size(self) -> Dimension:
        return self._calculate_size(lambda a: a.preferred_size)

    @property
    def bounds(self) -> Bounds:
        # noinspection PyTypeChecker
        return reduce(lambda b1, b2: b1 + b2, map(lambda i: i.bounds, self.areas)) if self.areas else Bounds(0, 0, 0, 0)

    # noinspection PyUnresolvedReferences
    @bounds.setter
    def bounds(self, bounds: Bounds) -> None:
        s = self._from_size

        # noinspection PyTypeChecker
        items: Sequence[BorderArea] = tuple(filter(lambda i: i.visible, self.areas))

        space_available = s(bounds.size)
        space_needed = sum(map(lambda i: s(i.preferred_size), items))

        space_to_reduce = max(space_needed - s(bounds.size), 0)

        reduced_size = dict.fromkeys(map(id, items), 0.)

        def calculate_sizes_to_reduce(targets: Sequence[BorderArea], size_to_reduce: float = space_to_reduce):
            if size_to_reduce <= 0:
                return

            target = size_to_reduce / len(targets)
            next_targets = []
            next_remaining = size_to_reduce

            for t in targets:
                available = s(t.preferred_size - t.minimum_size)

                if available > target:
                    next_targets.append(t)

                reduced = min(target, available)
                reduced_size[id(t)] += reduced

                next_remaining -= reduced

            if len(next_targets) > 0:
                calculate_sizes_to_reduce(next_targets, next_remaining)

        calculate_sizes_to_reduce(items)
        remaining = space_available

        def set_edge_bounds(item: BorderArea, setter: Callable[[BorderArea, float, Bounds], None]) -> float:
            preferred = item.preferred_size
            size = s(preferred) - reduced_size[id(item)]

            setter(item, size, bounds)

            return size

        offset = 0.

        remaining -= offset

        if self.begin.visible:
            # noinspection PyUnresolvedReferences
            offset = set_edge_bounds(self.begin, self._set_begin_bounds)
            remaining -= offset

        if self.end.visible:
            # noinspection PyUnresolvedReferences
            remaining -= set_edge_bounds(self.end, self._set_end_bounds)

        if self.center.visible:
            # noinspection PyUnresolvedReferences
            self._set_center_bounds(self.center, remaining, offset, bounds)

    def _calculate_size(self, extractor: Callable[[BorderArea], Dimension]) -> Dimension:
        items = filter(lambda i: i.visible, self.areas)

        # noinspection PyTypeChecker
        return reduce(self._reduce_size, map(extractor, items), Dimension(0, 0))

    @abstractmethod
    def _from_size(self, size: Dimension) -> float:
        pass

    @abstractmethod
    def _reduce_size(self, s1: Dimension, s2: Dimension) -> Dimension:
        pass

    @abstractmethod
    def _set_begin_bounds(self, item: BorderArea, size: float, area: Bounds) -> None:
        pass

    @abstractmethod
    def _set_center_bounds(self, item: BorderArea, size: float, offset: float, area: Bounds) -> None:
        pass

    @abstractmethod
    def _set_end_bounds(self, item: BorderArea, size: float, area: Bounds) -> None:
        pass


class BorderColumn(BorderStrip):
    def __init__(self, begin: BorderArea, center: BorderArea, end: BorderArea) -> None:
        super().__init__(begin, center, end)

    def _from_size(self, size: Dimension) -> float:
        return size.width

    def _reduce_size(self, s1: Dimension, s2: Dimension) -> Dimension:
        return Dimension(s1.width + s2.width, max(s1.height, s2.height))

    def _set_begin_bounds(self, item: BorderArea, size: float, area: Bounds) -> None:
        # noinspection PyTypeHints
        item.bounds = Bounds(area.x, area.y, size, area.height)  # type: ignore

    def _set_center_bounds(self, item: BorderArea, size: float, offset: float, area: Bounds) -> None:
        # noinspection PyTypeHints
        item.bounds = Bounds(area.x + offset, area.y, size, area.height)  # type: ignore

    def _set_end_bounds(self, item: BorderArea, size: float, area: Bounds) -> None:
        # noinspection PyTypeHints
        item.bounds = Bounds(area.x + area.width - size, area.y, size, area.height)  # type: ignore


class BorderRow(BorderStrip):
    def __init__(self, begin: BorderArea, center: BorderArea, end: BorderArea):
        super().__init__(begin, center, end)

    def _from_size(self, size: Dimension) -> float:
        return size.height

    def _reduce_size(self, s1: Dimension, s2: Dimension) -> Dimension:
        return Dimension(max(s1.width, s2.width), s1.height + s2.height)

    def _set_begin_bounds(self, item: BorderArea, size: float, area: Bounds) -> None:
        # noinspection PyTypeHints
        item.bounds = Bounds(area.x, area.y, area.width, size)  # type: ignore

    def _set_center_bounds(self, item: BorderArea, size: float, offset: float, area: Bounds) -> None:
        # noinspection PyTypeHints
        item.bounds = Bounds(area.x, area.y + offset, area.width, size)  # type: ignore

    def _set_end_bounds(self, item: BorderArea, size: float, area: Bounds) -> None:
        # noinspection PyTypeHints
        item.bounds = Bounds(area.x, area.y + area.height - size, area.width, size)  # type: ignore


# noinspection PyProtectedMember
class BorderItem(BorderArea):

    def __init__(self, border: Border) -> None:
        if border is None:
            raise ValueError("Argument 'border' is required.")

        self.component: Maybe[Component] = Nothing
        self.padding: Insets = Insets(0, 0, 0, 0)

        self._border = border

        super().__init__()

    @property
    def border(self) -> Border:
        return self._border

    @property
    def visible(self) -> bool:
        return self.component.map(lambda c: c.visible).value_or(False)

    @property
    def minimum_size(self) -> Dimension:
        return self._calculate_size(lambda c: c.minimum_size)

    @property
    def preferred_size(self) -> Dimension:
        return self._calculate_size(lambda c: c.preferred_size)

    @property
    def bounds(self) -> Bounds:
        if self.component == Nothing:
            return Bounds(0, 0, 0, 0)

        component = self.component.unwrap()
        bounds = component.bounds

        return (bounds + self.padding).copy(x=bounds.x, y=bounds.y)

    @bounds.setter
    def bounds(self, bounds: Bounds) -> None:
        if self.bounds != bounds:
            self.component.map(lambda c: setattr(c, "bounds", bounds - self.padding))

    def _calculate_size(self, extractor: Callable[[Component], Dimension]) -> Dimension:
        (top, right, bottom, left) = self.padding.tuple

        return self.component \
            .map(extractor) \
            .map(lambda s: s.copy(width=s.width + left + right, height=s.height + top + bottom)) \
            .value_or(Dimension(0, 0))

    def __eq__(self, other) -> bool:
        if not isinstance(other, BorderItem):
            return False

        return other.component == self.component and other.border == self.border and other.padding == self.padding

    def __hash__(self) -> int:
        return hash((self.border, id(self.component)))
