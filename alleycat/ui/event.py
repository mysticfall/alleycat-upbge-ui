from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from queue import Queue
from typing import Any

from rx.disposable import Disposable

from alleycat.ui import Point


@dataclass
class Event(ABC):
    source: Any

    def __post_init__(self) -> None:
        if self.source is None:
            raise ValueError("Argument 'source' is missing.")


class EventLoopAware(ABC):

    @abstractmethod
    def process(self) -> None:
        pass


class EventDispatcher(ABC):

    @abstractmethod
    def dispatch_event(self, event: Event) -> None:
        pass


class EventQueue(ABC):

    def __init__(self) -> None:
        self._events = Queue()

    def queue_event(self, event: Event) -> None:
        if event is None:
            raise ValueError("Argument 'event' is required.")
        pass


class EventGenerator(Disposable, ABC):

    def __init__(self, queue: EventQueue) -> None:
        if queue is None:
            raise ValueError("Argument 'queue' is required.")

        super().__init__()

        self._queue = queue

    @property
    def queue(self) -> EventQueue:
        return self._queue


class MouseEvent(Event, ABC):
    position: Point


@dataclass
class MouseMoveEvent(MouseEvent):
    source: Any = field(repr=False)

    position: Point

    __slots__ = ["position"]

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.position is None:
            raise ValueError("Argument 'position' is missing.")
