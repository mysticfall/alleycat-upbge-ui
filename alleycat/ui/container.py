from __future__ import annotations

from typing import Tuple, Sequence, TypeVar, Generic

import rx
from alleycat.reactive import RV, ReactiveObject
from alleycat.reactive import functions as rv
from rx import operators as ops
from rx.subject import Subject

T = TypeVar("T")


class Container(ReactiveObject, Generic[T]):
    children: RV[Sequence[T]] = rv.new_view()

    def __init__(self) -> None:
        super().__init__()

        self._added_child = Subject()
        self._removed_child = Subject()

        changed_child = rx.merge(
            self._added_child.pipe(ops.map(lambda v: (v, True))),
            self._removed_child.pipe(ops.map(lambda v: (v, False))))

        def on_child_change(children: Tuple[T, ...], event: Tuple[T, bool]):
            (child, added) = event

            if added and child not in children:
                return children + (child,)
            elif not added and child in children:
                return tuple(c for c in children if c is not child)

        # noinspection PyTypeChecker
        self.children = changed_child.pipe(
            ops.scan(on_child_change, ()), ops.start_with(()), ops.distinct_until_changed())

    def add(self, child: T) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._added_child.on_next(child)

    def remove(self, child: T) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._removed_child.on_next(child)
