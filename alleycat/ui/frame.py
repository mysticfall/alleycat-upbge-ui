from __future__ import annotations

from abc import ABC
from enum import Enum
from itertools import chain
from typing import Iterable, NamedTuple, Optional, cast

import rx
from alleycat.reactive import RP, functions as rv
from returns.maybe import Maybe, Nothing
from rx import operators as ops

from alleycat.ui import Bounds, Context, Dimension, Layout, MouseButton, MouseInput, Point, \
    Window, WindowUI


class Direction(Enum):
    North = 0
    Northeast = 1
    East = 2
    Southeast = 3
    South = 4
    Southwest = 5
    West = 6
    Northwest = 7


class Frame(Window):
    draggable: RP[bool] = rv.from_value(False)

    resizable: RP[bool] = rv.from_value(False)

    def __init__(self, context: Context, layout: Optional[Layout] = None, visible: bool = True) -> None:
        super().__init__(context, layout, visible)

        ui = cast(FrameUI, self.ui)

        self._initialize_drag(ui)
        self._initialize_resize(ui)

    def _initialize_drag(self, ui: FrameUI):
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

    def _initialize_resize(self, ui: FrameUI):
        mouse = MouseInput.input(self)

        bounds = self.on_drag_start.pipe(
            ops.filter(lambda e: self.resizable and e.button == MouseButton.LEFT),
            ops.map(lambda e: ui.resize_handle_at(self, e.position).map(
                lambda v: Frame._ResizeState(v, e.position, self.bounds, self.minimum_size))),
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
        return chain(["Frame"], super().style_fallback_prefixes)

    def dispose(self) -> None:
        self.execute_safely(self._drag_listener.dispose)
        self.execute_safely(self._resize_listener.dispose)

        super().dispose()

    @staticmethod
    def _bounds_for_state(state: Frame._ResizeState, location: Point) -> Bounds:
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


class FrameUI(WindowUI[Frame], ABC):

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def allow_drag(self, component: Frame, location: Point) -> bool:
        return True

    @property
    def resize_handle_size(self) -> int:
        return 10

    def resize_handle_at(self, component: Frame, location: Point) -> Maybe[Direction]:
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
