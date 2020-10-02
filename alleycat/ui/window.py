from __future__ import annotations

from itertools import chain
from typing import Optional, Iterator, Iterable

import rx
from alleycat.reactive import RP
from alleycat.reactive import functions as rv
from returns.maybe import Maybe, Nothing, Some
from rx import operators as ops

from alleycat.ui import Context, Graphics, Container, LayoutContainer, Layout, Drawable, Point, ErrorHandlerSupport, \
    ErrorHandler, MouseButton


class Window(LayoutContainer):
    draggable: RP[bool] = rv.from_value(False)

    def __init__(self, context: Context, layout: Optional[Layout] = None) -> None:
        super().__init__(context, layout)

        context.window_manager.add(self)

        can_drag = ops.filter(lambda e: self.draggable and e.button == MouseButton.LEFT)

        offset = rx.merge(self.on_drag_start, self.on_drag).pipe(
            can_drag,
            ops.map(lambda e: e.position),
            ops.pairwise(),
            ops.map(lambda v: v[1] - v[0]),
            ops.take_until(self.on_drag_end.pipe(can_drag)),
            ops.repeat())

        self._drag_listener = offset.subscribe(self.move_by, on_error=context.error_handler)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Window"], super().style_fallback_prefixes)

    def dispose(self) -> None:
        self.execute_safely(self._drag_listener.dispose)

        super().dispose()


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
