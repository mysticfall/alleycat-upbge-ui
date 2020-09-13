from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import IntFlag
from typing import Final, Any, cast, Sequence

import rx
from alleycat.reactive import RV, RP
from alleycat.reactive import functions as rv
from rx import Observable
from rx import operators as ops

from alleycat.ui import Point, Context, Input, PositionalEvent, Event, InputLookup, \
    PropagatingEvent, Bounded, EventHandler


class MouseButton(IntFlag):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 4


class MouseEvent(PositionalEvent, ABC):
    pass


@dataclass(frozen=True)  # type:ignore
class MouseButtonEvent(MouseEvent, PropagatingEvent, ABC):
    button: MouseButton

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.button is None:
            raise ValueError("Argument 'button' is required.")


class MouseMoveEvent(MouseEvent, PropagatingEvent):

    def with_source(self, source: Any) -> Event:
        return MouseMoveEvent(source, self.position)


class MouseDownEvent(MouseButtonEvent):

    def with_source(self, source: Any) -> Event:
        return MouseDownEvent(source, self.position, self.button)


class MouseUpEvent(MouseButtonEvent):

    def with_source(self, source: Any) -> Event:
        return MouseUpEvent(source, self.position, self.button)


class MouseEventHandler(Bounded, EventHandler, ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    def on_mouse_move(self) -> Observable:
        return self.events.pipe(
            ops.filter(lambda e: isinstance(e, MouseMoveEvent)),
            ops.map(lambda e: e.with_source(self)))

    @property
    def on_mouse_down(self) -> Observable:
        return self.events.pipe(
            ops.filter(lambda e: isinstance(e, MouseDownEvent)),
            ops.map(lambda e: e.with_source(self)))

    @property
    def on_mouse_up(self) -> Observable:
        return self.events.pipe(
            ops.filter(lambda e: isinstance(e, MouseUpEvent)),
            ops.map(lambda e: e.with_source(self)))


class MouseInput(Input, ABC):
    ID: Final = "mouse"

    position: RV[Point]

    buttons: RV[int]

    def __init__(self, context: Context):
        super().__init__(context)

        def dispatch(event: PositionalEvent) -> None:
            self.context.dispatcher_at(event.position).map(lambda d: d.dispatch_event(event))

        self._dispatchers = rx.merge(*self.positional_events).subscribe(dispatch, on_error=self.error_handler)

    @property
    def id(self) -> str:
        return self.ID

    @staticmethod
    def input(lookup: InputLookup) -> MouseInput:
        if lookup is None:
            raise ValueError("Argument 'lookup' is required.")

        try:
            return cast(MouseInput, lookup.inputs[MouseInput.ID])
        except KeyError:
            raise NotImplemented("Mouse input is not supported in this backend.")

    @property
    def positional_events(self) -> Sequence[Observable]:
        return self.on_mouse_move, self.on_mouse_down, self.on_mouse_up

    @property
    def on_mouse_move(self) -> Observable:
        return rv.observe(self, "position").pipe(
            ops.distinct_until_changed(),
            ops.map(lambda p: MouseMoveEvent(self.context, p)))

    @property
    def on_mouse_down(self) -> Observable:
        def event_for(button: MouseButton) -> Observable:
            return self._button_down(button).pipe(
                ops.map(lambda _: rx.concat(
                    rx.of(self.position), rx.never().pipe(ops.take_until(self._next_button_up(button))))),
                ops.exclusive(),
                ops.map(lambda p: MouseDownEvent(self.context, p, button)))

        return rx.merge(*[event_for(button) for button in MouseButton])

    @property
    def on_mouse_up(self) -> Observable:
        def event_for(button: MouseButton) -> Observable:
            return self._button_up(button).pipe(
                ops.map(lambda _: rx.concat(
                    rx.of(self.position), rx.never().pipe(ops.take_until(self._button_down(button))))),
                ops.exclusive(),
                ops.map(lambda p: MouseUpEvent(self.context, p, button)))

        return rx.merge(*[event_for(button) for button in MouseButton])

    def _button_down(self, button: MouseButton) -> Observable:
        return rv.observe(self, "buttons").pipe(
            ops.filter(lambda b: b & button == button))

    def _button_up(self, button: MouseButton) -> Observable:
        return rv.observe(self, "buttons").pipe(
            ops.map(lambda b: b & button),
            ops.distinct_until_changed(),
            ops.pairwise(),
            ops.filter(lambda b: b[0] == button and b[1] != button))

    def _next_button_up(self, button: MouseButton) -> Observable:
        return rv.observe(self, "buttons").pipe(
            ops.map(lambda b: b & button),
            ops.filter(lambda b: b != button),
            ops.take(1))

    def dispose(self) -> None:
        super().dispose()

        self.execute_safely(self._dispatchers.dispose)


class FakeMouseInput(MouseInput):
    _position: RP[Point] = rv.from_value(Point(0, 0))

    _buttons: RP[int] = rv.from_value(0)

    position: RV[Point] = _position.as_view()

    buttons: RV[int] = _buttons.as_view()

    def __init__(self, context: Context):
        super().__init__(context)

    def pressed(self, button: MouseButton) -> bool:
        if button is None:
            raise ValueError("Argument 'button' is required.")

        return self._buttons & button == button

    def press(self, button: MouseButton) -> None:
        if button is None:
            raise ValueError("Argument 'button' is required.")

        self._buttons = self._buttons | button

    def release(self, button: MouseButton) -> None:
        if button is None:
            raise ValueError("Argument 'button' is required.")

        self._buttons = self._buttons ^ button

    def click(self, button: MouseButton) -> None:
        self.press(button)
        self.release(button)

    def move_to(self, location: Point) -> None:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        # noinspection PyTypeChecker
        self._position = location
