from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Mapping, Iterable, TypeVar, Generic

import rx
from alleycat.reactive import ReactiveObject, RP, RV
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Some, Nothing
from rx import operators as ops

from alleycat.ui import Context, Drawable, EventDispatcher, Graphics, StyleLookup, Point, \
    PositionalEvent, MouseEventHandler, ErrorHandler, Input, RGBA, Bounds, Font

if TYPE_CHECKING:
    from alleycat.ui import LayoutContainer


class Component(Drawable, StyleLookup, MouseEventHandler, EventDispatcher, ReactiveObject):
    visible: RP[bool] = rv.from_value(True)

    parent: RP[Maybe[LayoutContainer]] = rv.from_value(Nothing)

    offset: RV[Point] = parent.as_view().map(
        lambda _, parent: parent.map(
            lambda p: rx.combine_latest(
                p.observe("offset"), p.observe("location")).pipe(ops.map(lambda v: v[0] + v[1]))
        ).or_else_call(lambda: rx.of(Point(0, 0)))
    ).pipe(lambda _: (ops.exclusive(),))

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
    def style_fallback_prefixes(self) -> Iterable[str]:
        yield from ()

    def style_fallback_keys(self, key: str) -> Iterable[str]:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        for prefix in self.style_fallback_prefixes:
            yield str.join(".", [prefix, key])

        yield key

    def resolve_color(self, key: str) -> Maybe[RGBA]:
        color = self.get_color(key)

        if color is not Nothing:
            return color

        for k in self.style_fallback_keys(key):
            color = self.context.look_and_feel.get_color(k)

            if color is not Nothing:
                return color

        return Nothing

    def resolve_font(self, key: str) -> Maybe[Font]:
        font = self.get_font(key)

        if font is not Nothing:
            return font

        for k in self.style_fallback_keys(key):
            font = self.context.look_and_feel.get_font(k)

            if font is not Nothing:
                return font

        return Nothing

    @property
    def inputs(self) -> Mapping[str, Input]:
        return self.context.inputs

    @property
    def error_handler(self) -> ErrorHandler:
        return self.context.error_handler

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

    @abstractmethod
    def draw(self, g: Graphics, component: T) -> None:
        pass
