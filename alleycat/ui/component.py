from __future__ import annotations

from abc import ABC
from typing import Tuple, List, Sequence

import rx
from alleycat.reactive import ReactiveObject, RP, RV
from alleycat.reactive import functions as rv
from returns.maybe import Nothing, Maybe, Some
from rx import operators as ops

from alleycat.ui import Drawable, Event, EventDispatcher, Graphics
from alleycat.ui.bounded import Bounded
from alleycat.ui.context import Context


class Component(ReactiveObject, Drawable, Bounded, EventDispatcher):
    parent: RP[Maybe[Container]] = rv.from_value(Nothing)

    visible: RP[bool] = rv.from_value(True)

    def __init__(self, context: Context) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context

    @property
    def context(self) -> Context:
        return self._context

    def draw(self, g: Graphics) -> None:
        pass

    def dispatch_event(self, event: Event) -> None:
        pass


class ComponentEvent(Event, ABC):
    def __init__(self, source: Component) -> None:
        super().__init__(source)


class Container(Component):
    children: RV[Sequence[Component]] = rv.new_view()

    def __init__(self, context: Context) -> None:
        super().__init__(context)

        from rx.subject import Subject
        self._added_child = Subject()
        self._removed_child = Subject()

        changed_child = rx.merge(
            self._added_child.pipe(ops.map(lambda v: (v, True))),
            self._removed_child.pipe(ops.map(lambda v: (v, False))))

        def on_child_change(children: List[Component], event: Tuple[Component, bool]):
            (child, added) = event

            if added and child not in children:
                children.append(child)
            elif not added and child in children:
                children.remove(child)

            return children

        # noinspection PyTypeChecker
        self.children = changed_child.pipe(ops.scan(on_child_change, []), ops.distinct_until_changed())

    def add(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._added_child.on_next(child)

        child.parent = Some(self)

    def remove(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        child.parent = None

        self._removed_child.on_next(child)
