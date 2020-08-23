from abc import ABC

import rx
from alleycat.reactive import ReactiveObject
from alleycat.reactive import functions as rv

from alleycat.ui import Drawable, Dimension, Event, EventDispatcher, Graphics
from alleycat.ui.bounded import Bounded
from alleycat.ui.context import Context


class Component(ReactiveObject, Drawable, Bounded, EventDispatcher):
    visible = rv.from_value(True)

    min_size = rv.from_observable(rx.of(Dimension(0, 0)))

    max_size = rv.from_observable(rx.of(Dimension(0, 0)))

    preferred_size = rv.from_observable(rx.of(Dimension(0, 0)))

    def __init__(self, context: Context) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context

    @property
    def context(self) -> Context:
        return self._context

    def draw(self, g: Graphics) -> None:
        pass

    def dispatch_event(self, event: Event) -> None:
        pass


class ComponentEvent(Event, ABC):
    def __init__(self, source: Component) -> None:
        super().__init__(source)
