from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from alleycat.ui import Graphics, StyleLookup, Component, Toolkit

T = TypeVar("T", bound=Component, contravariant=True)


class LookAndFeel(StyleLookup, ABC):

    def __init__(self, toolkit: Toolkit) -> None:
        if toolkit is None:
            raise ValueError("Argument 'toolkit' is required.")

        super().__init__()

        self._toolkit = toolkit

    @property
    def toolkit(self) -> Toolkit:
        return self._toolkit

    @abstractmethod
    def create_ui(self, component: T) -> ComponentUI[T]:
        pass


class ComponentUI(StyleLookup, Generic[T], ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def draw(self, g: Graphics, component: T) -> None:
        pass
