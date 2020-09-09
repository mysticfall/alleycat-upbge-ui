from __future__ import annotations

from typing import TYPE_CHECKING

import rx
from returns.functions import identity
from rx import operators as ops
from alleycat.reactive import ReactiveObject, RP, RV
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Some, Nothing

from alleycat.ui import Bounded, Context, Drawable, Event, EventDispatcher, Graphics, StyleLookup, Point

if TYPE_CHECKING:
    from alleycat.ui import ComponentUI, LayoutContainer


class Component(Bounded, Drawable, StyleLookup, EventDispatcher, ReactiveObject):
    visible: RP[bool] = rv.from_value(True)

    parent: RP[Maybe[LayoutContainer]] = rv.from_value(Nothing)

    _parent: RV[Maybe[LayoutContainer]] = parent.as_view()

    _p_location: RV[Point] = _parent \
        .map(lambda v: v.map(lambda p: rv.observe(p.location)).or_else_call(lambda: rx.of(Point(0, 0)))) \
        .pipe(ops.exclusive())

    _p_offset: RV[Point] = _parent \
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

    def dispatch_event(self, event: Event) -> None:
        pass

    @property
    def style_fallback(self) -> Maybe[StyleLookup]:
        return Some(self.context.look_and_feel)
