from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import chain
from typing import Any, Mapping, Sequence, Tuple

import rx
from alleycat.reactive import RP, RV, ReactiveObject, functions as rv
from rx import Observable

from alleycat.ui import Bounds, Component, Dimension


class Layout(ReactiveObject, ABC):
    _children: RP[Sequence[LayoutItem]] = rv.from_value(())

    children: RV[Sequence[LayoutItem]] = _children.as_view()

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def minimum_size(self) -> Dimension:
        pass

    @property
    @abstractmethod
    def preferred_size(self) -> Dimension:
        pass

    def add(self, child: Component, *args, **kwargs) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        existing = filter(lambda c: c.component != child, self._children)
        item = LayoutItem(child, args, kwargs)

        # noinspection PyTypeChecker
        self._children = tuple(chain(existing, (item,)))

    def remove(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        # noinspection PyTypeChecker
        self._children = tuple(filter(lambda c: c.component != child, self._children))

    @property
    def on_constraints_change(self) -> Observable:
        return rx.empty()

    @abstractmethod
    def perform(self, bounds: Bounds) -> None:
        pass


@dataclass(frozen=True)
class LayoutItem:
    component: Component

    args: Tuple[Any, ...]

    kwargs: Mapping[str, Any]
