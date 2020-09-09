from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

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
