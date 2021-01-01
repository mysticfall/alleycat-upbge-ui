from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntFlag
from typing import Any, Sequence, cast

import rx
from alleycat.reactive import RP, RV, functions as rv
from rx import Observable, operators as ops
from rx.subject import Subject

from alleycat.ui import Bounded, Context, Event, EventHandler, Input, InputLookup, Point, PositionalEvent, \
    PropagatingEvent


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


class MouseOverEvent(MouseEvent):

    def with_source(self, source: Any) -> Event:
        return MouseOverEvent(source, self.position)


class MouseOutEvent(MouseEvent):

    def with_source(self, source: Any) -> Event:
        return MouseOutEvent(source, self.position)


class DragStartEvent(MouseButtonEvent):

    def with_source(self, source: Any) -> Event:
        return DragStartEvent(source, self.position, self.button)


class DragEvent(MouseButtonEvent):

    def with_source(self, source: Any) -> Event:
        return DragEvent(source, self.position, self.button)


class DragEndEvent(MouseButtonEvent):

    def with_source(self, source: Any) -> Event:
        return DragEndEvent(source, self.position, self.button)


class DragOverEvent(MouseButtonEvent):

    def with_source(self, source: Any) -> Event:
        return DragOverEvent(source, self.position, self.button)


class DragLeaveEvent(MouseButtonEvent):

    def with_source(self, source: Any) -> Event:
        return DragLeaveEvent(source, self.position, self.button)


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

    @property
    def on_mouse_over(self) -> Observable:
        position = MouseInput.input(self).observe("position")
        local_pos = position.pipe(ops.map(lambda p: p - self.offset))

        return self.on_mouse_move.pipe(
            ops.map(lambda e: e.position),
            ops.map(lambda p: rx.concat(rx.of(p), rx.never().pipe(
                ops.take_until(local_pos.pipe(ops.filter(lambda l: not self.bounds.contains(l))))))),
            ops.exclusive(),
            ops.map(lambda p: MouseOverEvent(self, p)))

    @property
    def on_mouse_out(self) -> Observable:
        position = MouseInput.input(self).observe("position")

        return self.on_mouse_over.pipe(
            ops.map(lambda e: position.pipe(
                ops.filter(lambda p: not self.bounds.contains(p - self.offset)),
                ops.take(1))),
            ops.exclusive(),
            ops.map(lambda p: MouseOutEvent(self, p)))

    @property
    def on_drag_start(self) -> Observable:
        mouse = MouseInput.input(self)
        position = mouse.observe("position")

        return self.on_mouse_down.pipe(
            ops.map(lambda e: position.pipe(
                ops.take(1),
                ops.map(lambda _: DragStartEvent(self, e.position, e.button)),
                ops.take_until(mouse.on_button_release(e.button)))),
            ops.exclusive())

    @property
    def on_drag(self) -> Observable:
        mouse = MouseInput.input(self)
        position = mouse.observe("position")

        return self.on_drag_start.pipe(
            ops.map(lambda e: position.pipe(
                ops.skip(1),
                ops.map(lambda p: DragEvent(self, p, e.button)),
                ops.take_until(mouse.on_button_release(e.button)))),
            ops.exclusive())

    @property
    def on_drag_over(self) -> Observable:
        mouse = MouseInput.input(self)

        return mouse.on_mouse_down.pipe(
            ops.filter(lambda e: not self.bounds.contains(e.position - self.offset)),
            ops.map(lambda e: self.on_mouse_over.pipe(
                ops.map(lambda o: (o.position, e.button)),
                ops.take_until(mouse.on_button_release(e.button)))),
            ops.exclusive(),
            ops.map(lambda e: DragOverEvent(self, e[0], e[1])))

    @property
    def on_drag_leave(self) -> Observable:
        mouse = MouseInput.input(self)
        position = mouse.observe("position")

        from_inside = self.on_mouse_down.pipe(
            ops.map(lambda e: position.pipe(
                ops.filter(lambda p: not self.bounds.contains(p - self.offset)),
                ops.take(1),
                ops.map(lambda p: (p, e.button)),
                ops.take_until(mouse.on_button_release(e.button)))),
            ops.exclusive())

        from_outside = self.on_drag_over.pipe(
            ops.map(lambda e: self.on_mouse_out.pipe(
                ops.take(1),
                ops.map(lambda o: (o.position, e.button)),
                ops.take_until(mouse.on_button_release(e.button)))),
            ops.exclusive())

        return rx.merge(from_inside, from_outside).pipe(
            ops.map(lambda e: DragLeaveEvent(self, e[0], e[1])))

    @property
    def on_drag_end(self) -> Observable:
        mouse = MouseInput.input(self)

        return self.on_drag_start.pipe(
            ops.map(lambda e: mouse.on_button_release(e.button).pipe(
                ops.take(1),
                ops.map(lambda _: (mouse.position, e.button)))),
            ops.exclusive(),
            ops.map(lambda e: DragEndEvent(self, e[0], e[1])))


class MouseInput(Input, ABC):
    ID: str = "mouse"

    position: RV[Point]

    buttons: RV[int]

    def __init__(self, context: Context):
        super().__init__(context)

        def dispatch(event: PositionalEvent) -> None:
            self.context.dispatcher_at(event.position).map(lambda d: d.dispatch_event(event))

        self._dispatchers = rx.merge(*self.positional_events) \
            .pipe(ops.take_until(self.on_dispose)) \
            .subscribe(dispatch, on_error=self.error_handler)

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
            raise NotImplementedError("Mouse input is not supported in this backend.")

    @property
    def positional_events(self) -> Sequence[Observable]:
        return self.on_mouse_move, self.on_mouse_down, self.on_mouse_up

    @property
    def on_mouse_move(self) -> Observable:
        return self.observe("position").pipe(
            ops.distinct_until_changed(),
            ops.map(lambda p: MouseMoveEvent(self.context, p)))

    @property
    def on_mouse_down(self) -> Observable:
        def event_for(button: MouseButton) -> Observable:
            return self.on_button_press(button).pipe(
                ops.map(lambda _: rx.concat(
                    rx.of(self.position), rx.never().pipe(
                        ops.take_until(self.on_button_release(button).pipe(ops.take(1)))))),
                ops.exclusive(),
                ops.map(lambda p: MouseDownEvent(self.context, p, button)))

        return rx.merge(*[event_for(button) for button in MouseButton])

    @property
    def on_mouse_up(self) -> Observable:
        def event_for(button: MouseButton) -> Observable:
            return self.on_button_release(button).pipe(
                ops.map(lambda _: rx.concat(
                    rx.of(self.position), rx.never().pipe(ops.take_until(self.on_button_press(button))))),
                ops.exclusive(),
                ops.map(lambda p: MouseUpEvent(self.context, p, button)))

        return rx.merge(*[event_for(button) for button in MouseButton])

    @property
    @abstractmethod
    def on_mouse_wheel(self) -> Observable:
        pass

    def on_button_press(self, button: MouseButton) -> Observable:
        return self.observe("buttons").pipe(ops.filter(lambda b: b & button == button))

    def on_button_release(self, button: MouseButton) -> Observable:
        return self.observe("buttons").pipe(
            ops.map(lambda b: b & button),
            ops.distinct_until_changed(),
            ops.pairwise(),
            ops.filter(lambda b: b[0] == button and b[1] != button))

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

        self._scroll = Subject()

    @property
    def on_mouse_wheel(self) -> Observable:
        return self._scroll

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

    def scroll(self, lines: int) -> None:
        self._scroll.on_next(lines)

    def dispose(self) -> None:
        self.execute_safely(self._scroll.dispose)

        super().dispose()
