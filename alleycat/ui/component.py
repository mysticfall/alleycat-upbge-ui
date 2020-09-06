from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from alleycat.reactive import ReactiveObject, RP
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Some, Nothing

from alleycat.ui import Bounded, Context, Drawable, Event, EventDispatcher, Graphics, StyleLookup

if TYPE_CHECKING:
    from alleycat.ui import ComponentUI, LayoutContainer


class Component(Bounded, Drawable, StyleLookup, EventDispatcher, ReactiveObject):
    visible: RP[bool] = rv.from_value(True)

    parent: RP[Maybe[LayoutContainer]] = rv.from_value(Nothing)

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
        self.draw_component(g)

    def draw_component(self, g: Graphics) -> None:
        self.ui.draw(g, self)

    def dispatch_event(self, event: Event) -> None:
        pass

    @property
    def style_fallback(self) -> Maybe[StyleLookup]:
        return Some(self.context.look_and_feel)


class ComponentEvent(Event, ABC):

    def __init__(self, source: Component) -> None:
        super().__init__(source)
