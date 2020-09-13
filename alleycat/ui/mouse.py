from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from enum import IntFlag
from typing import Final, Any, cast, Sequence

import rx
from alleycat.reactive import RV, RP
from alleycat.reactive import functions as rv
from rx import Observable
from rx import operators as ops
from rx.disposable import Disposable
from rx.subject import Subject

from alleycat.ui import Point, Context, Input, PositionalEvent, Event, EventDispatcher, InputLookup, ErrorHandlerSupport


class MouseEvent(PositionalEvent, ABC):
    pass


class MouseButton(IntFlag):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 4


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


@dataclass(frozen=True)
class MouseDownEvent(MouseEvent):
    source: Any = field(repr=False)

    position: Point

    button: MouseButton

    def with_source(self, source: Any) -> Event:
        return MouseDownEvent(source, self.position, self.button)

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.position is None:
            raise ValueError("Argument 'position' is required.")

        if self.button is None:
            raise ValueError("Argument 'button' is required.")


@dataclass(frozen=True)
class MouseUpEvent(MouseEvent):
    source: Any = field(repr=False)

    position: Point

    button: MouseButton

    def with_source(self, source: Any) -> Event:
        return MouseUpEvent(source, self.position, self.button)

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.position is None:
            raise ValueError("Argument 'position' is required.")

        if self.button is None:
            raise ValueError("Argument 'button' is required.")


class MouseEventHandler(EventDispatcher, ErrorHandlerSupport, Disposable, ABC):

    def __init__(self):
        super().__init__()

        self._mouse_events = dict([(key, Subject()) for key in ["move", "up", "down"]])

    @property
    def on_mouse_move(self) -> Observable:
        return self._mouse_events["move"]

    @property
    def on_mouse_down(self) -> Observable:
        return self._mouse_events["down"]

    @property
    def on_mouse_up(self) -> Observable:
        return self._mouse_events["up"]

    def dispatch_event(self, event: Event) -> None:
        if isinstance(event, MouseMoveEvent):
            self._mouse_events["move"].on_next(event.with_source(self))
        elif isinstance(event, MouseDownEvent):
            self._mouse_events["down"].on_next(event.with_source(self))
        elif isinstance(event, MouseUpEvent):
            self._mouse_events["up"].on_next(event.with_source(self))

        super().dispatch_event(event)

    def dispose(self) -> None:
        super().dispose()

        for subject in self._mouse_events.values():
            self.execute_safely(subject.dispose)


class MouseInput(Input, ABC):
    ID: Final = "mouse"

    position: RV[Point]

    buttons: RV[int]

    def __init__(self, context: Context):
        super().__init__(context)

        self._dispatchers = rx.merge(*self.events) \
            .subscribe(lambda e: e.source.dispatch_event(e), on_error=self.error_handler)

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

    @property
    def events(self) -> Sequence[Observable]:
        return self.on_mouse_move, self.on_mouse_down, self.on_mouse_up

    @property
    def on_mouse_move(self) -> Observable:
        position = rv.observe(self, "position")

        window = position.pipe(
            ops.map(lambda p: (self.context.window_manager.window_at(p), p)),
            ops.map(lambda v: v[0].map(lambda w: rx.of((w, v[1]))).value_or(rx.empty())),
            ops.exclusive(),
            ops.distinct_until_changed())

        component = window.pipe(
            ops.map(lambda v: (v[0].component_at(v[1]), v[1])),
            ops.map(lambda v: v[0].map(lambda w: rx.of((w, v[1]))).value_or(rx.empty())),
            ops.exclusive(),
            ops.distinct_until_changed())

        return component.pipe(ops.map(lambda v: MouseMoveEvent(v[0], v[1])))

    @property
    def on_mouse_down(self) -> Observable:
        def event_for(button: MouseButton) -> Observable:
            return self._button_down(button).pipe(
                ops.map(lambda _: rx.concat(
                    rx.of(self.position), rx.never().pipe(ops.take_until(self._next_button_up(button))))),
                ops.exclusive(),
                ops.map(lambda p: (self.context.window_manager.window_at(p).bind(lambda w: w.component_at(p)), p)),
                ops.map(lambda v: v[0].map(lambda w: rx.of((w, v[1]))).value_or(rx.empty())),
                ops.exclusive(),
                ops.map(lambda v: MouseDownEvent(v[0], v[1], button)))

        return rx.merge(*[event_for(button) for button in MouseButton])

    @property
    def on_mouse_up(self) -> Observable:
        def event_for(button: MouseButton) -> Observable:
            return self._button_up(button).pipe(
                ops.map(lambda _: rx.concat(
                    rx.of(self.position), rx.never().pipe(ops.take_until(self._button_down(button))))),
                ops.exclusive(),
                ops.map(lambda p: (self.context.window_manager.window_at(p).bind(lambda w: w.component_at(p)), p)),
                ops.map(lambda v: v[0].map(lambda w: rx.of((w, v[1]))).value_or(rx.empty())),
                ops.exclusive(),
                ops.map(lambda v: MouseUpEvent(v[0], v[1], button)))

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
