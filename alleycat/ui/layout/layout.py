from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence, Tuple

import rx
from alleycat.reactive import ReactiveObject, RV
from alleycat.reactive import functions as rv
from rx import Observable
from rx import operators as ops
from rx.subject import Subject

from alleycat.ui import Component, Dimension, Bounds


class Layout(ReactiveObject, ABC):
    children: RV[Sequence[Component]] = rv.new_view()

    minimum_size: RV[Dimension]

    preferred_size: RV[Dimension]

    def __init__(self) -> None:
        super().__init__()

        self._added_child = Subject()
        self._removed_child = Subject()

        changed_child = rx.merge(
            self._added_child.pipe(ops.map(lambda v: (v, True))),
            self._removed_child.pipe(ops.map(lambda v: (v, False))))

        def on_child_change(children: Tuple[Component, ...], event: Tuple[Component, bool]):
            (child, added) = event

            if added and child not in children:
                return children + (child,)
            elif not added and child in children:
                return tuple(c for c in children if c is not child)

        # noinspection PyTypeChecker
        self.children = changed_child.pipe(
            ops.scan(on_child_change, ()), ops.start_with(()), ops.distinct_until_changed())

    def add(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._added_child.on_next(child)

    def remove(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._removed_child.on_next(child)

    @property
    def on_constraints_change(self) -> Observable:
        return rx.empty()

    @abstractmethod
    def perform(self, bounds: Bounds) -> None:
        pass

    def dispose(self) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.dispose()

        super().dispose()
