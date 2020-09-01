from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from rx.disposable import Disposable

from alleycat.ui import Bounds, RGBA, Context

T = TypeVar("T", bound=Context, contravariant=True)


class Graphics(Disposable, ABC, Generic[T]):

    def __init__(self, context: T) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context

        self.color = RGBA(0, 0, 0, 0)

    @property
    def context(self) -> Context:
        return self._context

    @abstractmethod
    def fill_rect(self, bounds: Bounds) -> Graphics:
        pass

    @abstractmethod
    def clear(self) -> Graphics:
        pass
