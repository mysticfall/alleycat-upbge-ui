from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from rx import Observable
from rx.disposable import Disposable
from rx.subject import Subject

from alleycat.ui import Point


class Event(ABC):
    source: Any

    def __post_init__(self) -> None:
        if self.source is None:
            raise ValueError("Argument 'source' is missing.")

    @abstractmethod
    def with_source(self, source: Any) -> Event:
        pass

    def stop_propagation(self) -> None:
        object.__setattr__(self, "_stop_propagation", True)

    @property
    def propagation_stopped(self) -> bool:
        return getattr(self, "_stop_propagation", False)


class PositionalEvent(Event, ABC):
    position: Point


class EventLoopAware(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def process(self) -> None:
        pass


class EventDispatcher(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def dispatch_event(self, event: Event) -> None:
        pass


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
