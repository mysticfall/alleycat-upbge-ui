from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from alleycat.ui import Component, Graphics

T = TypeVar("T", bound=Component, contravariant=True)


class LookAndFeel(ABC):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def create_ui(self, component: T) -> ComponentUI[T]:
        return NoUI()


class ComponentUI(ABC, Generic[T]):
    @abstractmethod
    def draw(self, g: Graphics, component: T) -> None:
        pass


class NoUI(ComponentUI[Component]):
    def draw(self, graphics: Graphics, component: T) -> None:
        pass
