from __future__ import annotations

from abc import ABC
from typing import Tuple, Sequence, TYPE_CHECKING

import rx
from alleycat.reactive import ReactiveObject, RP, RV
from alleycat.reactive import functions as rv
from returns.maybe import Nothing, Maybe, Some
from rx import operators as ops
from rx.subject import Subject

from alleycat.ui import Bounded, Context, Drawable, Event, EventDispatcher, Graphics, StyleLookup, Point

if TYPE_CHECKING:
    from alleycat.ui import ComponentUI


class Component(ReactiveObject, Drawable, Bounded, EventDispatcher, StyleLookup):
    parent: RP[Maybe[Container]] = rv.from_value(Nothing)

    visible: RP[bool] = rv.from_value(True)

    def __init__(self, context: Context) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context
        self._ui = context.look_and_feel.create_ui(self)

        assert self._ui is not None

    @property
    def context(self) -> Context:
        return self._context

    @property
    def ui(self) -> ComponentUI:
        return self._ui

    def draw(self, g: Graphics) -> None:
        self.ui.draw(g, self)

    def dispatch_event(self, event: Event) -> None:
        pass

    @property
    def style_fallback(self) -> Maybe[StyleLookup]:
        return Some(self.context.look_and_feel)


class ComponentEvent(Event, ABC):
    def __init__(self, source: Component) -> None:
        super().__init__(source)


class Container(Component):
    children: RV[Sequence[Component]] = rv.new_view()

    def __init__(self, context: Context) -> None:
        super().__init__(context)

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

        child.parent = Some(self)

    def remove(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        child.parent = None

        self._removed_child.on_next(child)

    def component_at(self, location: Point) -> Maybe[Component]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        if self.bounds.contains(location):
            try:
                # noinspection PyTypeChecker
                child = next(c for c in self.children if c.bounds.contains(location - self.location))

                if isinstance(child, Container):
                    return child.component_at(location - self.location)
                else:
                    return Some(child)
            except StopIteration:
                return Some(self)

        return Nothing
