from abc import ABC
from typing import Optional, Iterator, TypeVar, Sequence

import rx
from alleycat.reactive import RV
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Nothing, Some
from rx import Observable
from rx import operators as ops

from alleycat.ui import Component, Point, Graphics, Context, ComponentUI, Layout


class Container(Component):
    children: RV[Sequence[Component]] = rv.new_view()

    def __init__(self, context: Context, layout: Optional[Layout] = None, visible: bool = True):
        from .layout import AbsoluteLayout

        self._layout = Maybe.from_value(layout).or_else_call(AbsoluteLayout)
        self._layout_valid = True
        self._layout_in_progress = False

        # noinspection PyTypeChecker
        self.children = self.layout.observe("children").pipe(
            ops.map(lambda children: tuple(map(lambda c: c.component, children))))

        super().__init__(context, visible)

        on_size_change = self.observe("size")
        on_min_size_change = self.observe("effective_minimum_size")
        on_pre_size_change = self.observe("effective_preferred_size")
        on_children_change = self.observe("children")

        on_child_bounds_change = on_children_change.pipe(
            ops.map(lambda children: map(lambda c: c.observe("bounds"), children)),
            ops.map(lambda b: rx.merge(*b)),
            ops.switch_latest(),
            ops.map(lambda _: None))

        should_invalidate = rx.merge(
            on_size_change,
            on_min_size_change,
            on_pre_size_change,
            on_children_change,
            on_child_bounds_change,
            self.layout.on_constraints_change).pipe(
            ops.filter(lambda _: not self._layout_in_progress))

        self._layout_listener = should_invalidate.subscribe(
            lambda _: self.invalidate_layout(), self.context.error_handler)

    @property
    def layout(self) -> Layout:
        return self._layout

    def invalidate_layout(self) -> None:
        self._layout_valid = False

    def perform_layout(self) -> None:
        if not self._layout_valid and not self._layout_in_progress:
            self._layout_in_progress = True

            try:
                self.layout.perform(self.bounds)
            except BaseException as e:
                self.context.error_handler(e)

            self._layout_in_progress = False
            self._layout_valid = True

    def component_at(self, location: Point) -> Maybe[Component]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        if self.bounds.contains(location):
            try:
                # noinspection PyTypeChecker
                children: Iterator[Component] = reversed(self.children)

                child = next(c for c in children if c.bounds.contains(location - self.location))

                if isinstance(child, Container):
                    return child.component_at(location - self.location)
                else:
                    return Some(child)
            except StopIteration:
                return Some(self)

        return Nothing

    def add(self, child: Component, *args, **kwargs) -> None:
        self.layout.add(child, *args, **kwargs)

        child.parent.map(lambda p: p.remove(child))
        child.parent = Some(self)

    def remove(self, child: Component) -> None:
        self.layout.remove(child)

        child.parent = Nothing

    def draw(self, g: Graphics) -> None:
        self.perform_layout()

        super().draw(g)

    def draw_component(self, g: Graphics) -> None:
        super().draw_component(g)

        self.draw_children(g)

    def draw_children(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.draw(g)

    def dispose(self) -> None:
        self.execute_safely(self._layout_listener.dispose)
        self.execute_safely(self.layout.dispose)

        super().dispose()


T = TypeVar("T", bound=Container, contravariant=True)


class ContainerUI(ComponentUI[T], ABC):

    def __init__(self) -> None:
        super().__init__()

    def minimum_size(self, component: T) -> Observable:
        return component.layout.observe("minimum_size")

    def preferred_size(self, component: T) -> Observable:
        return component.layout.observe("preferred_size")
