from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from alleycat.ui import StyleLookup, Component, Toolkit, ComponentUI

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
