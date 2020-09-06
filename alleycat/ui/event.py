from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from alleycat.ui import Point


@dataclass
class Event(ABC):
    source: Any

    def __init__(self, source: Any) -> None:
        if source is None:
            raise ValueError("Argument 'source' is required.")

        super().__init__()

        self.source = source

    def __post_init__(self) -> None:
        if self.source is None:
            raise ValueError("Argument 'source' is missing.")


class PositionalEvent(Event, ABC):
    position: Point

    def __init__(self, source: Any) -> None:
        super().__init__(source)


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

    def __init__(self, source: Any):
        super().__init__(source)


@dataclass
class MouseMoveEvent(MouseEvent):
    source: Any = field(repr=False)

    position: Point

    __slots__ = ["position"]

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.position is None:
            raise ValueError("Argument 'position' is missing.")
