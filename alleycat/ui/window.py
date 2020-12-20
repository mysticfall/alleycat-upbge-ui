from __future__ import annotations

from abc import ABC
from itertools import chain
from typing import Optional, Iterator, Iterable, TypeVar, cast, NamedTuple, Sequence, Tuple

import rx
from alleycat.reactive import RP, RV, ReactiveObject
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Nothing, Some
from rx import operators as ops
from rx.subject import Subject

from alleycat.ui import Context, Graphics, Container, Layout, Drawable, Point, ErrorHandlerSupport, \
    ErrorHandler, MouseButton, Event, PropagatingEvent, ContainerUI, Bounds, MouseInput, Dimension, Direction


class Window(Container):
    draggable: RP[bool] = rv.from_value(False)

    resizable: RP[bool] = rv.from_value(False)

    def __init__(self, context: Context, layout: Optional[Layout] = None, visible: bool = True) -> None:
        super().__init__(context, layout, visible)

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
            ops.repeat(),
            ops.take_until(self.on_dispose))

        self._drag_listener = offset.subscribe(self.move_by, on_error=self.context.error_handler)

    def _initialize_resize(self, ui: WindowUI):
        mouse = MouseInput.input(self)

        bounds = self.on_drag_start.pipe(
            ops.filter(lambda e: self.resizable and e.button == MouseButton.LEFT),
            ops.map(lambda e: ui.resize_handle_at(self, e.position).map(
                lambda v: Window._ResizeState(v, e.position, self.bounds, self.minimum_size))),
            ops.map(lambda v: v.map(rx.of).value_or(rx.empty())),
            ops.switch_latest(),
            ops.map(lambda s: mouse.on_mouse_move.pipe(
                ops.map(lambda e: self._bounds_for_state(s, e.position)),
                ops.take_until(mouse.on_button_release(MouseButton.LEFT)))),
            ops.switch_latest(),
            ops.take_until(self.on_dispose))

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
        self.context.window_manager.remove(self)

        self.execute_safely(self._drag_listener.dispose)
        self.execute_safely(self._resize_listener.dispose)

        super().dispose()

    @staticmethod
    def _bounds_for_state(state: Window._ResizeState, location: Point) -> Bounds:
        (handle, anchor, init_bounds, min_size) = state
        (mw, mh) = min_size.tuple

        delta = location - anchor

        (x, y, w, h) = init_bounds.tuple

        if handle in (Direction.North, Direction.Northeast, Direction.Northwest):
            d = min(delta.y, max(h - mh, 0))
            y += d
            h -= d
        elif handle in (Direction.South, Direction.Southeast, Direction.Southwest):
            h += max(delta.y, min(-h + mh, 0))

        if handle in (Direction.East, Direction.Northeast, Direction.Southeast):
            w += max(delta.x, min(-w + mw, 0))
        elif handle in (Direction.West, Direction.Northwest, Direction.Southwest):
            d = min(delta.x, max(w - mw, 0))
            x += d
            w -= d

        return Bounds(x, y, w, h)

    class _ResizeState(NamedTuple):
        handle: Direction
        anchor: Point
        init_bounds: Bounds
        min_size: Dimension


class WindowManager(Drawable, ErrorHandlerSupport, ReactiveObject):
    windows: RV[Sequence[Window]] = rv.new_view()

    def __init__(self, error_handler: ErrorHandler) -> None:
        if error_handler is None:
            raise ValueError("Argument 'error_handler' is required.")

        super().__init__()

        self._error_handler = error_handler

        self._added_window = Subject()
        self._removed_window = Subject()

        changed_window = rx.merge(
            self._added_window.pipe(ops.map(lambda v: (v, True))),
            self._removed_window.pipe(ops.map(lambda v: (v, False))))

        def on_window_change(windows: Tuple[Window, ...], event: Tuple[Window, bool]):
            (window, added) = event

            if added and window not in windows:
                return windows + (window,)
            elif not added and window in windows:
                return tuple(c for c in windows if c is not window)

        # noinspection PyTypeChecker
        self.windows = changed_window.pipe(
            ops.scan(on_window_change, ()), ops.start_with(()), ops.distinct_until_changed())

    def add(self, window: Window) -> None:
        if window is None:
            raise ValueError("Argument 'window' is required.")

        self._added_window.on_next(window)

    def remove(self, window: Window) -> None:
        if window is None:
            raise ValueError("Argument 'window' is required.")

        self._removed_window.on_next(window)

    def window_at(self, location: Point) -> Maybe[Window]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        try:
            # noinspection PyTypeChecker
            children: Iterator[Window] = reversed(self.windows)

            return Some(next(c for c in children if c.bounds.contains(location)))
        except StopIteration:
            return Nothing

    def draw(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for window in self.windows:
            window.validate()
            window.draw(g)

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    def dispose(self) -> None:
        # noinspection PyTypeChecker
        for window in self.windows:
            self.execute_safely(window.dispose)

        super().dispose()


T = TypeVar("T", bound=Window, contravariant=True)


class WindowUI(ContainerUI[T], ABC):

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def allow_drag(self, component: T, location: Point) -> bool:
        return True

    @property
    def resize_handle_size(self) -> int:
        return 5

    def resize_handle_at(self, component: T, location: Point) -> Maybe[Direction]:
        (px, py) = (location - component.offset).tuple
        (x, y, w, h) = component.bounds.tuple

        handle: Optional[Direction] = None

        if y <= py <= y + self.resize_handle_size:
            handle = Direction.North
        elif y + h - self.resize_handle_size <= py <= y + h:
            handle = Direction.South

        if x + w - self.resize_handle_size <= px <= x + w:
            if handle is None:
                handle = Direction.East
            else:
                handle = Direction.Northeast if handle == Direction.North else Direction.Southeast
        elif x <= px <= x + self.resize_handle_size:
            if handle is None:
                handle = Direction.West
            else:
                handle = Direction.Northwest if handle == Direction.North else Direction.Southwest

        return Maybe.from_optional(handle)
