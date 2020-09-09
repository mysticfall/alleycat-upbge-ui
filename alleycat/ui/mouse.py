from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Final, Any, cast

from alleycat.reactive import RV, RP
from alleycat.reactive import functions as rv
from rx import Observable
from rx.disposable import Disposable
from rx.subject import Subject

from alleycat.ui import Point, Context, Input, PositionalEvent, Event, EventDispatcher, InputLookup


class MouseEvent(PositionalEvent, ABC):
    pass


@dataclass(frozen=True)
class MouseMoveEvent(MouseEvent):
    source: Any = field(repr=False)

    position: Point

    def with_source(self, source: Any) -> Event:
        return MouseMoveEvent(source, self.position)

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.position is None:
            raise ValueError("Argument 'position' is required.")


class MouseEventHandler(EventDispatcher, Disposable, ABC):

    def __init__(self):
        super().__init__()

        self._on_mouse_move = Subject()

    @property
    def on_mouse_move(self) -> Observable:
        return self._on_mouse_move

    def dispatch_event(self, event: Event) -> None:
        self._on_mouse_move.on_next(event.with_source(self))

        super().dispatch_event(event)

    def dispose(self) -> None:
        super().dispose()

        self._on_mouse_move.dispose()


class MouseInput(Input, ABC):
    ID: Final = "mouse"

    position: RV[Point]

    def __init__(self, context: Context):
        super().__init__(context)

        rv.observe(self, "position").subscribe(self.dispatch)

    @property
    def id(self) -> str:
        return self.ID

    @staticmethod
    def input(lookup: InputLookup) -> MouseInput:
        if lookup is None:
            raise ValueError("Argument 'look' is required.")

        try:
            return cast(MouseInput, lookup.inputs[MouseInput.ID])
        except KeyError:
            raise NotImplemented("Mouse input is not supported in this backend.")

    def dispatch(self, location: Point) -> None:
        window = self.context.window_manager.window_at(location)
        component = window.bind(lambda w: w.component_at(location))

        component.map(lambda c: c.dispatch_event(MouseMoveEvent(c, location)))


class FakeMouseInput(MouseInput):
    _position: RP[Point] = rv.new_property()

    position: RV[Point] = _position.as_view()

    def __init__(self, context: Context):
        super().__init__(context)

    def move_to(self, location: Point) -> None:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        # noinspection PyTypeChecker
        self._position = location
