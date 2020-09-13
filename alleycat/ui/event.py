from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from returns.maybe import Maybe, Nothing
from rx import Observable
from rx.disposable import Disposable
from rx.subject import Subject

from alleycat.ui import Point, InputLookup


@dataclass(frozen=True)  # type:ignore
class Event(ABC):
    source: Any

    def __post_init__(self) -> None:
        if self.source is None:
            raise ValueError("Argument 'source' is missing.")

    @abstractmethod
    def with_source(self, source: Any) -> Event:
        pass


class PropagatingEvent(Event, ABC):

    def stop_propagation(self) -> None:
        object.__setattr__(self, "_stop_propagation", True)

    @property
    def propagation_stopped(self) -> bool:
        return getattr(self, "_stop_propagation", False)


@dataclass(frozen=True)  # type:ignore
class PositionalEvent(Event, ABC):
    position: Point

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.position is None:
            raise ValueError("Argument 'position' is required.")


class EventLoopAware(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def process(self) -> None:
        pass


class EventDispatcher(Disposable, ABC):

    def __init__(self) -> None:
        super().__init__()

        self._events = Subject()

    @property
    def events(self) -> Observable:
        return self._events

    @property
    def parent_dispatcher(self) -> Maybe[EventDispatcher]:
        return Nothing

    def dispatch_event(self, event: Event) -> None:
        assert event is not None

        self._events.on_next(event)

        if isinstance(event, PropagatingEvent) and not event.propagation_stopped:
            self.parent_dispatcher.map(lambda p: p.dispatch_event(event))

    def dispose(self) -> None:
        super().dispose()

        self._events.dispose()


class EventHandler(EventDispatcher, InputLookup, ABC):
    pass
