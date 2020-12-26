from abc import ABC
from typing import Iterator, Optional, Sequence, TypeVar, cast

import rx
from alleycat.reactive import RV, functions as rv
from cairocffi import Context as Graphics
from returns.maybe import Maybe, Nothing, Some
from rx import Observable, operators as ops

from alleycat.ui import Bounds, Component, ComponentUI, Context, Dimension, Layout, Point


class Container(Component):
    children: RV[Sequence[Component]] = rv.new_view()

    def __init__(self, context: Context, layout: Optional[Layout] = None, visible: bool = True):
        from .layout import AbsoluteLayout

        self._layout = Maybe.from_optional(layout).or_else_call(AbsoluteLayout)
        self._layout_pending = True
        self._layout_running = False

        # noinspection PyTypeChecker
        self.children = self.layout.observe("children").pipe(
            ops.map(lambda children: tuple(map(lambda c: c.component, children))))

        super().__init__(context, visible)

        self.observe("size") \
            .pipe(ops.filter(lambda _: self.visible), ops.distinct_until_changed()) \
            .subscribe(lambda _: self.request_layout(), on_error=self.error_handler)

    @property
    def layout(self) -> Layout:
        return self._layout

    def validate(self, force: bool = False) -> None:
        if self.visible and (not self.valid or force):
            self.request_layout()

            # noinspection PyTypeChecker
            for child in self.children:
                child.validate(force)

        super().validate(force)

    def invalidate(self) -> None:
        if not self._layout_running:
            super().invalidate()

    @property
    def layout_pending(self) -> bool:
        return self._layout_pending or not self.valid

    def request_layout(self) -> None:
        self._layout_pending = True

    def perform_layout(self) -> None:
        self._layout_running = True

        try:
            self.layout.perform(self.bounds.copy(x=0, y=0))
        except BaseException as e:
            self.context.error_handler(e)

        self._layout_pending = False
        self._layout_running = False

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
        child.parent.map(lambda p: p.remove(child))

        self.layout.add(child, *args, **kwargs)

        child.parent = Some(self)

    def remove(self, child: Component) -> None:
        self.layout.remove(child)

        child.parent = Nothing

    def draw(self, g: Graphics) -> None:
        if self.layout_pending:
            self.perform_layout()

        super().draw(g)

    def draw_component(self, g: Graphics) -> None:
        super().draw_component(g)

        self.draw_children(g)

        cast(ContainerUI, self.ui).post_draw(g, self)

    def draw_children(self, g: Graphics) -> None:
        ui = cast(ContainerUI, self.ui)

        (cx, cy, cw, ch) = ui.content_bounds(self).tuple

        g.save()

        g.rectangle(cx, cy, cw, ch)
        g.clip()

        try:
            # noinspection PyTypeChecker
            for child in self.children:
                child.draw(g)
        except BaseException as e:
            self.error_handler(e)

        g.restore()

    def dispose(self) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            self.execute_safely(child.dispose)

        self.execute_safely(self.layout.dispose)

        super().dispose()


T = TypeVar("T", bound=Container, contravariant=True)


class ContainerUI(ComponentUI[T], ABC):

    def __init__(self) -> None:
        super().__init__()

    def minimum_size(self, component: T) -> Dimension:
        return component.layout.minimum_size

    def preferred_size(self, component: T) -> Dimension:
        return component.layout.preferred_size

    # noinspection PyMethodMayBeStatic
    def content_bounds(self, component: T) -> Bounds:
        return self.clip_bounds(component)

    def on_invalidate(self, component: T) -> Observable:
        other_changes = super().on_invalidate(component)
        children_changes = component.observe("children")

        def child_bounds_changes(child: Component):
            return rx.merge(
                child.observe("bounds"),
                child.observe("preferred_size"),
                child.observe("minimum_size"))

        children_bounds_changes = children_changes.pipe(
            ops.map(lambda children: map(child_bounds_changes, children)),
            ops.map(lambda b: rx.merge(*b)),
            ops.switch_latest(),
            ops.map(lambda _: None))

        return rx.merge(
            other_changes,
            children_changes,
            children_bounds_changes,
            component.layout.on_constraints_change)

    def post_draw(self, g: Graphics, component: T) -> None:
        pass
