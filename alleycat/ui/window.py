from __future__ import annotations

from abc import ABC
from itertools import chain
from typing import Optional, Iterator, Iterable, TypeVar, cast, NamedTuple

import rx
from alleycat.reactive import RP
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Nothing, Some
from rx import operators as ops

from alleycat.ui import Context, Graphics, Container, LayoutContainer, Layout, Drawable, Point, ErrorHandlerSupport, \
    ErrorHandler, MouseButton, Event, PropagatingEvent, ComponentUI, Anchor, Bounds, MouseInput


class Window(LayoutContainer):
    draggable: RP[bool] = rv.from_value(False)

    resizable: RP[bool] = rv.from_value(False)

    def __init__(self, context: Context, layout: Optional[Layout] = None) -> None:
        super().__init__(context, layout)

        context.window_manager.add(self)

        ui = cast(WindowUI, self.ui)

        self._initialize_drag(ui)
        self._initialize_resize(ui)

    def _initialize_drag(self, ui: WindowUI):
        offset = rx.merge(self.on_drag_start, self.on_drag).pipe(
            ops.filter(lambda e: self.draggable and e.button == MouseButton.LEFT),
            ops.filter(lambda e: ui.allow_drag(self, self.position_of(e))),
            ops.filter(lambda e: not self.resizable or ui.resize_handle_at(self, e.position) == Nothing),
            ops.map(lambda e: e.position),
            ops.pairwise(),
            ops.map(lambda v: v[1] - v[0]),
            ops.take_until(self.on_drag_end.pipe(ops.filter(lambda e: e.button == MouseButton.LEFT))),
            ops.repeat())

        self._drag_listener = offset.subscribe(self.move_by, on_error=self.context.error_handler)

    def _initialize_resize(self, ui: WindowUI):
        mouse = MouseInput.input(self)

        bounds = self.on_drag_start.pipe(
            ops.filter(lambda e: self.resizable and e.button == MouseButton.LEFT),
            ops.map(lambda e: ui.resize_handle_at(self, e.position).map(
                lambda v: Window._ResizeState(v, e.position, self.bounds))),
            ops.map(lambda v: v.map(rx.of).value_or(rx.empty())),
            ops.exclusive(),
            ops.map(lambda s: mouse.on_mouse_move.pipe(
                ops.map(lambda e: self._bounds_for_state(s, e.position)),
                ops.take_until(mouse.on_button_release(MouseButton.LEFT)))),
            ops.exclusive())

        def set_bounds(b: Bounds) -> None:
            self.bounds = b

        self._resize_listener = bounds.subscribe(set_bounds, on_error=self.context.error_handler)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Window"], super().style_fallback_prefixes)

    def dispatch_event(self, event: Event) -> None:
        if isinstance(event, PropagatingEvent):
            event.stop_propagation()

        super().dispatch_event(event)

    def dispose(self) -> None:
        self.execute_safely(self._drag_listener.dispose)

        super().dispose()

    @staticmethod
    def _bounds_for_state(state: Window._ResizeState, location: Point) -> Bounds:
        (handle, anchor, init_bounds) = state

        delta = location - anchor

        (x, y, w, h) = init_bounds.tuple

        if handle in (Anchor.North, Anchor.Northeast, Anchor.Northwest):
            y += delta.y
            h -= delta.y
        elif handle in (Anchor.South, Anchor.Southeast, Anchor.Southwest):
            h += delta.y

        if handle in (Anchor.East, Anchor.Northeast, Anchor.Southeast):
            w += delta.x
        elif handle in (Anchor.West, Anchor.Northwest, Anchor.Southwest):
            x += delta.x
            w -= delta.x

        return Bounds(x, y, w, h)

    class _ResizeState(NamedTuple):
        handle: Anchor
        anchor: Point
        init_bounds: Bounds


class WindowManager(Drawable, ErrorHandlerSupport, Container[Window]):

    def __init__(self, error_handler: ErrorHandler) -> None:
        if error_handler is None:
            raise ValueError("Argument 'error_handler' is required.")

        super().__init__()

        self._error_handler = error_handler

    def window_at(self, location: Point) -> Maybe[Window]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        try:
            # noinspection PyTypeChecker
            children: Iterator[Window] = reversed(self.children)

            return Some(next(c for c in children if c.bounds.contains(location)))
        except StopIteration:
            return Nothing

    def draw(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.draw(g)

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    def dispose(self) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            self.execute_safely(child.dispose)

        super().dispose()


T = TypeVar("T", bound=Window, contravariant=True)


class WindowUI(ComponentUI[T], ABC):

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def allow_drag(self, component: T, location: Point) -> bool:
        return True

    @property
    def resize_handle_size(self) -> int:
        return 5

    def resize_handle_at(self, component: T, location: Point) -> Maybe[Anchor]:
        (px, py) = (location - component.offset).tuple
        (x, y, w, h) = component.bounds.tuple

        handle: Optional[Anchor] = None

        if y <= py <= y + self.resize_handle_size:
            handle = Anchor.North
        elif y + h - self.resize_handle_size <= py <= y + h:
            handle = Anchor.South

        if x + w - self.resize_handle_size <= px <= x + w:
            if handle is None:
                handle = Anchor.East
            else:
                handle = Anchor.Northeast if handle == Anchor.North else Anchor.Southeast
        elif x <= px <= x + self.resize_handle_size:
            if handle is None:
                handle = Anchor.West
            else:
                handle = Anchor.Northwest if handle == Anchor.North else Anchor.Southwest

        return Maybe.from_value(handle)
