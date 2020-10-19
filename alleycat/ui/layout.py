from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from typing import Optional, Iterator, TypeVar

import rx
from alleycat.reactive import RP, ReactiveObject
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Nothing, Some
from rx import Observable
from rx import operators as ops

from alleycat.ui import Component, Container, Point, Graphics, Context, ComponentUI, Bounds, Dimension, Insets


class Layout(ReactiveObject, ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    def on_constraints_change(self) -> Observable:
        return rx.empty()

    @abstractmethod
    def perform(self, component: LayoutContainer) -> None:
        pass

    @abstractmethod
    def minimum_size(self, component: LayoutContainer) -> Observable:
        pass

    @abstractmethod
    def preferred_size(self, component: LayoutContainer) -> Observable:
        pass


class AbsoluteLayout(Layout):

    def __init__(self) -> None:
        super().__init__()

    def perform(self, component: LayoutContainer) -> None:
        pass

    def minimum_size(self, component: LayoutContainer) -> Observable:
        return rx.of(Dimension(0, 0))

    def preferred_size(self, component: LayoutContainer) -> Observable:
        return component.observe("size")


class FillLayout(Layout):
    padding: RP[Insets] = rv.new_property()

    def __init__(self, insets: Insets = Insets(0, 0, 0, 0)) -> None:
        super().__init__()

        # noinspection PyTypeChecker
        self.padding = insets

    @property
    def on_constraints_change(self) -> Observable:
        return rx.merge(super().on_constraints_change, self.observe("padding"))

    def perform(self, component: LayoutContainer) -> None:
        p = self.padding

        bounds = Bounds(
            p.top,
            p.left,
            max(component.width - p.left - p.right, 0),
            max(component.height - p.top - p.bottom, 0))

        # noinspection PyTypeChecker
        for child in component.children:
            child.bounds = bounds

    def minimum_size(self, component: LayoutContainer) -> Observable:
        return self._calculate_size(component, "effective_minimum_size").pipe(
            ops.combine_latest(self.observe("padding")),
            ops.map(lambda v: Dimension(v[0].width + v[1].left + v[1].right, v[0].height + v[1].top + v[1].bottom)))

    def preferred_size(self, component: LayoutContainer) -> Observable:
        return self._calculate_size(component, "effective_preferred_size").pipe(
            ops.combine_latest(self.observe("padding")),
            ops.map(lambda v: Dimension(v[0].width + v[1].left + v[1].right, v[0].height + v[1].top + v[1].bottom)))

    @staticmethod
    def _calculate_size(component: LayoutContainer, attribute: str) -> Observable:
        def max_size(s1: Dimension, s2: Dimension):
            return Dimension(max(s1.width, s2.width), max(s1.height, s2.height))

        return component.observe("children").pipe(
            ops.map(lambda children: map(lambda c: c.observe(attribute), children)),
            ops.map(lambda b: rx.combine_latest(*b, rx.of(Dimension(0, 0)))),
            ops.switch_latest(),
            ops.map(lambda b: reduce(max_size, b)))


class LayoutContainer(Component, Container[Component]):

    def __init__(self, context: Context, layout: Optional[Layout] = None):
        self._layout = Maybe.from_value(layout).or_else_call(AbsoluteLayout)

        super().__init__(context)

        self._layout_valid = True
        self._layout_in_progress = False

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
                self.layout.perform(self)
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

                if isinstance(child, LayoutContainer):
                    return child.component_at(location - self.location)
                else:
                    return Some(child)
            except StopIteration:
                return Some(self)

        return Nothing

    def add(self, child: Component) -> None:
        super().add(child)

        child.parent.map(lambda p: p.remove(child))
        child.parent = Some(self)

    def remove(self, child: Component) -> None:
        super().remove(child)

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

        # noinspection PyTypeChecker
        for child in self.children:
            self.execute_safely(child.dispose)

        super().dispose()


T = TypeVar("T", bound=LayoutContainer, contravariant=True)


class LayoutContainerUI(ComponentUI[T], ABC):

    def __init__(self) -> None:
        super().__init__()

    def minimum_size(self, component: T) -> Observable:
        return component.layout.minimum_size(component)

    def preferred_size(self, component: T) -> Observable:
        return component.layout.preferred_size(component)


class Anchor(Enum):
    North = 0
    Northeast = 1
    East = 2
    Southeast = 3
    South = 4
    Southwest = 5
    West = 6
    Northwest = 7
