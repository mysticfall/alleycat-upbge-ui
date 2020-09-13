from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import field, dataclass
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


class PropagatingEvent(Event, ABC):

    def stop_propagation(self) -> None:
        object.__setattr__(self, "_stop_propagation", True)

    @property
    def propagation_stopped(self) -> bool:
        return getattr(self, "_stop_propagation", False)


@dataclass(frozen=True)  # type:ignore
class PositionalEvent(Event, ABC):
    source: Any = field(repr=False)

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


class EventDispatcher(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def dispatch_event(self, event: Event) -> None:
        pass
