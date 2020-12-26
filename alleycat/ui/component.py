from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, TYPE_CHECKING, TypeVar

import rx
from alleycat.reactive import RP, RV, ReactiveObject, functions as rv
from cairocffi import Context as Graphics
from returns.maybe import Maybe, Nothing
from rx import Observable, operators as ops

from alleycat.ui import Bounded, Bounds, Context, ContextAware, Dimension, Drawable, EventDispatcher, Input, \
    MouseEventHandler, Point, PositionalEvent, StyleResolver

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

    _minimum_size: RP[Dimension] = rv.from_value(Dimension(0, 0))

    _preferred_size: RP[Dimension] = rv.from_value(Dimension(0, 0))

    minimum_size_override: RP[Maybe[Dimension]] = rv.from_value(Nothing)

    minimum_size: RV[Dimension] = rv.combine_latest(_minimum_size, minimum_size_override)(
        ops.pipe(ops.map(lambda v: v[1].value_or(v[0])), ops.distinct_until_changed()))

    preferred_size_override: RP[Maybe[Dimension]] = rv.from_value(Nothing).pipe(lambda o: (
        ops.combine_latest(o.observe("minimum_size")),
        ops.map(lambda t: t[0].map(
            lambda v: t[1].copy(width=max(v.width, t[1].width), height=max(v.height, t[1].height)))),
        ops.distinct_until_changed()))

    preferred_size: RV[Dimension] = rv.combine_latest(_preferred_size, preferred_size_override, minimum_size)(
        ops.pipe(
            ops.map(lambda v: (v[1].value_or(v[0]), v[2])),
            ops.map(lambda v: v[0].copy(width=max(v[0].width, v[1].width), height=max(v[0].height, v[1].height))),
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
        self._valid = False
        self._ui = self.create_ui()

        assert self._ui is not None

        super().__init__()

        self.validate()

        self.ui \
            .on_invalidate(self) \
            .pipe(ops.take_until(self.on_dispose)) \
            .subscribe(lambda _: self.invalidate(), on_error=self.error_handler)

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

    @property
    def valid(self) -> bool:
        return self._valid

    # noinspection PyTypeChecker
    def validate(self, force: bool = False) -> None:
        if self.visible and (not self.valid or force):
            self._minimum_size = self.ui.minimum_size(self)
            self._preferred_size = self.ui.preferred_size(self)

            self._valid = True

            self.parent.map(lambda p: p.request_layout())

    def invalidate(self) -> None:
        self._valid = False

        self.parent.map(lambda p: p.invalidate())

    def draw(self, g: Graphics) -> None:
        if self.visible:
            g.save()

            (dx, dy) = self.parent.map(lambda p: p.location).value_or(Point(0, 0))
            (cx, cy, cw, ch) = self.ui.clip_bounds(self).tuple

            g.translate(dx, dy)
            g.rectangle(cx, cy, cw, ch)

            g.clip()

            try:
                self.draw_component(g)
            except BaseException as e:
                self.error_handler(e)

            g.restore()

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

    def minimum_size(self, component: T) -> Dimension:
        return Dimension(0, 0)

    def preferred_size(self, component: T) -> Dimension:
        return self.minimum_size(component)

    # noinspection PyMethodMayBeStatic
    def clip_bounds(self, component: T) -> Bounds:
        return component.bounds

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def on_invalidate(self, component: T) -> Observable:
        return component.observe("visible")

    @abstractmethod
    def draw(self, g: Graphics, component: T) -> None:
        pass
