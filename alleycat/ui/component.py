from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

import rx
from alleycat.reactive import ReactiveObject, RP, RV
from alleycat.reactive import functions as rv
from returns.functions import identity
from returns.maybe import Maybe, Some, Nothing
from rx import operators as ops

from alleycat.ui import Context, Drawable, EventDispatcher, Graphics, StyleLookup, Point, \
    PositionalEvent, MouseEventHandler, ErrorHandler, Input

if TYPE_CHECKING:
    from alleycat.ui import ComponentUI, LayoutContainer


class Component(Drawable, StyleLookup, MouseEventHandler, EventDispatcher, ReactiveObject):
    visible: RP[bool] = rv.from_value(True)

    parent: RP[Maybe[LayoutContainer]] = rv.from_value(Nothing)

    _p_location: RV[Point] = parent.as_view() \
        .map(lambda v: v.map(lambda p: rv.observe(p.location)).or_else_call(lambda: rx.of(Point(0, 0)))) \
        .pipe(ops.exclusive())

    _p_offset: RV[Point] = parent.as_view() \
        .map(lambda v: v.map(lambda p: rv.observe(p.offset)).or_else_call(lambda: rx.of(Point(0, 0)))) \
        .pipe(ops.exclusive())

    offset: RV[Point] = rv.combine_latest(_p_location, _p_offset)(identity).map(lambda v: v[0] + v[1])

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
        g.offset = self.offset

        self.draw_component(g)

    def draw_component(self, g: Graphics) -> None:
        self.ui.draw(g, self)

    def position_of(self, event: PositionalEvent) -> Point:
        if event is None:
            raise ValueError("Argument 'event' is required.")

        return event.position - self.offset

    @property
    def style_fallback(self) -> Maybe[StyleLookup]:
        return Some(self.context.look_and_feel)

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
