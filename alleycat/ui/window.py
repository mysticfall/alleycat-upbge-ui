from __future__ import annotations

from abc import ABC
from itertools import chain
from typing import Iterable, Iterator, Optional, Sequence, Tuple, TypeVar

import rx
from alleycat.reactive import RV, ReactiveObject, functions as rv
from cairocffi import Context as Graphics
from returns.maybe import Maybe, Nothing, Some
from rx import operators as ops
from rx.subject import Subject

from alleycat.ui import Container, ContainerUI, Context, Drawable, ErrorHandler, ErrorHandlerSupport, Event, \
    Layout, Point, PropagatingEvent


class Window(Container, ABC):

    def __init__(self, context: Context, layout: Optional[Layout] = None, visible: bool = True) -> None:
        super().__init__(context, layout, visible)

        context.window_manager.add(self)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Window"], super().style_fallback_prefixes)

    def dispatch_event(self, event: Event) -> None:
        if isinstance(event, PropagatingEvent):
            event.stop_propagation()

        super().dispatch_event(event)

    def dispose(self) -> None:
        self.context.window_manager.remove(self)

        super().dispose()


T = TypeVar("T", bound=Window, contravariant=True)


class WindowUI(ContainerUI[T], ABC):
    def __init__(self) -> None:
        super().__init__()


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
