from dataclasses import dataclass
from enum import Enum
from functools import reduce
from typing import Callable, Sequence, Set, Tuple

from alleycat.reactive import RV
from rx import operators as ops

from alleycat.ui import Bounds, Component, Dimension
from .layout import Layout, LayoutItem


class Direction(Enum):
    Top = 0
    Right = 1
    Bottom = 2
    Left = 3


@dataclass(frozen=True)
class Anchor:
    direction: Direction

    distance: float = 0

    def __post_init__(self) -> None:
        if self.distance < 0:
            raise ValueError(f"Distance must be zero or a positive number.")


AnchorItem = Tuple[Component, Set[Anchor]]


# noinspection PyProtectedMember
class AnchorLayout(Layout):
    anchors: RV[Sequence[AnchorItem]] = Layout.children.pipe(lambda o: (
        ops.map(lambda items: tuple(map(lambda i: (i.component, AnchorLayout._create_anchors(i)), items))),))

    def __init__(self) -> None:
        super().__init__()

    @property
    def minimum_size(self) -> Dimension:
        return self._calculate_size(lambda c: c.minimum_size)

    @property
    def preferred_size(self) -> Dimension:
        return self._calculate_size(lambda c: c.preferred_size)

    def _calculate_size(self, extractor: Callable[[Component], Dimension]) -> Dimension:
        items = filter(lambda a: a[0].visible, self.anchors)

        def get_size(item: AnchorItem):
            (width, height) = extractor(item[0]).tuple

            for anchor in item[1]:
                if anchor.direction == Direction.Right or anchor.direction == Direction.Left:
                    width += anchor.distance
                else:
                    height += anchor.distance

            return Dimension(width, height)

        def merge(s1: Dimension, s2: Dimension):
            return Dimension(max(s1.width, s2.width), max(s1.height, s2.height))

        # noinspection PyTypeChecker
        return reduce(merge, map(get_size, items), Dimension(0, 0))

    def perform(self, bounds: Bounds) -> None:
        # noinspection PyTypeChecker
        for (component, anchors) in self.anchors:
            if not component.visible:
                continue

            distances = dict(map(lambda a: (a.direction, a.distance), anchors))

            (iw, ih) = component.preferred_size.tuple

            # noinspection DuplicatedCode
            if Direction.Left in distances:
                x = distances[Direction.Left]

                if Direction.Right in distances:
                    width = bounds.width - distances[Direction.Right] - x
                else:
                    width = min(bounds.width - x, iw)
            elif Direction.Right in distances:
                x2 = bounds.width - distances[Direction.Right]
                width = min(x2, iw)
                x = x2 - width
            else:
                width = min(bounds.width, iw)
                x = (bounds.width - width) / 2

            # noinspection DuplicatedCode
            if Direction.Top in distances:
                y = distances[Direction.Top]

                if Direction.Bottom in distances:
                    height = bounds.height - distances[Direction.Bottom] - y
                else:
                    height = min(bounds.height - y, ih)
            elif Direction.Bottom in distances:
                y2 = bounds.height - distances[Direction.Bottom]
                height = min(y2, ih)
                y = y2 - height
            else:
                height = min(bounds.height, ih)
                y = (bounds.height - height) / 2

            component.bounds = Bounds(x, y, width, height)

    @staticmethod
    def _create_anchors(item: LayoutItem) -> Set[Anchor]:
        assert item is not None

        anchors = set(filter(lambda a: isinstance(a, Anchor), item.args))

        if len(anchors) > 0:
            return anchors

        count = len(item.args)

        if count > 1 and isinstance(item.args[0], Direction):
            direction = item.args[0]
            distance = float(item.args[1]) if len(item.args) > 1 else 0.

            return {Anchor(direction, distance)}
        elif "direction" in item.kwargs:
            direction = item.kwargs["direction"]
            distance = item.kwargs["distance"] if "distance" in item.kwargs else 0.

            return {Anchor(direction, distance)}

        return set()
