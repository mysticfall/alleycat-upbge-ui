from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Mapping, TypeVar, Generic

import rx
from alleycat.reactive import ReactiveObject, RP, RV
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Some, Nothing
from rx import operators as ops, Observable

from alleycat.ui import Context, ContextAware, Drawable, EventDispatcher, Graphics, StyleResolver, Point, \
    PositionalEvent, MouseEventHandler, Input, Bounds, Dimension, Bounded

if TYPE_CHECKING:
    from alleycat.ui import Container, LookAndFeel


class Component(Drawable, StyleResolver, MouseEventHandler, EventDispatcher, ContextAware, ReactiveObject):
    visible: RP[bool] = rv.new_property()

    parent: RP[Maybe[Container]] = rv.from_value(Nothing)

    offset: RV[Point] = parent.as_view().map(
        lambda _, parent: parent.map(
            lambda p: rx.combine_latest(
                p.observe("offset"), p.observe("location")).pipe(ops.map(lambda v: v[0] + v[1]))
        ).or_else_call(lambda: rx.of(Point(0, 0)))
    ).pipe(lambda _: (ops.exclusive(),))

    preferred_size_override: RP[Maybe[Dimension]] = rv.from_value(Nothing).pipe(lambda o: (
        ops.combine_latest(o.observe("minimum_size")),
        ops.map(lambda t: t[0].map(
            lambda v: t[1].copy(width=max(v.width, t[1].width), height=max(v.height, t[1].height)))),
        ops.distinct_until_changed()))

    minimum_size_override: RP[Maybe[Dimension]] = rv.from_value(Nothing)

    preferred_size: RV[Dimension] = preferred_size_override.as_view().pipe(lambda c: (
        ops.combine_latest(c.ui.preferred_size(c)),
        ops.map(lambda v: v[0].value_or(v[1])),
        ops.combine_latest(c.observe("minimum_size")),
        ops.map(lambda v: v[0].copy(width=max(v[0].width, v[1].width), height=max(v[0].height, v[1].height))),
        ops.distinct_until_changed()))

    minimum_size: RV[Dimension] = minimum_size_override.as_view().pipe(lambda c: (
        ops.combine_latest(c.ui.minimum_size(c)),
        ops.map(lambda v: v[0].value_or(v[1])),
        ops.distinct_until_changed()))

    bounds: RP[Bounds] = Bounded.bounds.pipe(lambda o: (
        ops.combine_latest(o.observe("minimum_size")),
        ops.map(lambda v: v[0].copy(width=max(v[0].width, v[1].width), height=max(v[0].height, v[1].height))),
        ops.start_with(o.preferred_size)))

    def __init__(self, context: Context, visible: bool = True) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        # noinspection PyTypeChecker
        self.visible = visible

        self._context = context
        self._ui = self.create_ui()

        assert self._ui is not None

        super().__init__()

    @property
    def context(self) -> Context:
        return self._context

    @property
    def ui(self) -> ComponentUI:
        return self._ui

    @property
    def look_and_feel(self) -> LookAndFeel:
        return self.context.look_and_feel

    def create_ui(self) -> ComponentUI:
        return self.context.look_and_feel.create_ui(self)

    def show(self) -> None:
        # noinspection PyTypeChecker
        self.visible = True

    def hide(self) -> None:
        # noinspection PyTypeChecker
        self.visible = False

    def toggle_visibility(self) -> bool:
        # noinspection PyTypeChecker
        self.visible = not self.visible

        return self.visible

    def draw(self, g: Graphics) -> None:
        if self.visible:
            offset = g.offset
            clip = g.clip

            g.offset = self.offset

            def draw_clipped_area(bounds: Bounds) -> None:
                g.clip = Some(bounds)

                self.draw_component(g)

            new_clip = Some(self.bounds) if g.clip == Nothing else g.clip.bind(lambda c: self.bounds & c)
            new_clip.map(draw_clipped_area)

            g.offset = offset
            g.clip = clip

    def draw_component(self, g: Graphics) -> None:
        self.ui.draw(g, self)

    def position_of(self, event: PositionalEvent) -> Point:
        if event is None:
            raise ValueError("Argument 'event' is required.")

        return event.position - self.offset

    @property
    def inputs(self) -> Mapping[str, Input]:
        return self.context.inputs

    @property
    def parent_dispatcher(self) -> Maybe[EventDispatcher]:
        # noinspection PyTypeChecker
        return self.parent

    def __repr__(self) -> Any:
        return str({"id": id(self), "type": type(self).__name__})


T = TypeVar("T", bound=Component, contravariant=True)


class ComponentUI(Generic[T], ABC):

    def __init__(self) -> None:
        super().__init__()

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def minimum_size(self, component: T) -> Observable:
        return rx.of(Dimension(0, 0))

    def preferred_size(self, component: T) -> Observable:
        return self.minimum_size(component)

    @abstractmethod
    def draw(self, g: Graphics, component: T) -> None:
        pass
