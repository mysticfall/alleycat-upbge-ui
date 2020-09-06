from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from alleycat.ui import Graphics, StyleLookup, Component

T = TypeVar("T", bound=Component, contravariant=True)


class LookAndFeel(StyleLookup, ABC):

    def __init__(self) -> None:
        super().__init__()

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def create_ui(self, component: T) -> ComponentUI[T]:
        return NoUI()


class ComponentUI(ABC, Generic[T]):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def draw(self, g: Graphics, component: T) -> None:
        pass


class NoUI(ComponentUI[Component]):

    def __init__(self) -> None:
        super().__init__()

    def draw(self, graphics: Graphics, component: Component) -> None:
        pass
