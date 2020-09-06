from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from rx.disposable import Disposable

from alleycat.ui import Bounds, RGBA, Context, Point

T = TypeVar("T", bound=Context, contravariant=True)


class Graphics(Disposable, ABC, Generic[T]):

    def __init__(self, context: T) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context

        self._color = RGBA(0, 0, 0, 0)
        self._offset = Point(0, 0)

    @property
    def context(self) -> Context:
        return self._context

    @property
    def color(self) -> RGBA:
        return self._color

    @color.setter
    def color(self, value: RGBA) -> None:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        self._color = value

    @property
    def offset(self) -> Point:
        return self._offset

    @offset.setter
    def offset(self, value: Point) -> None:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        self._offset = value

    @abstractmethod
    def fill_rect(self, bounds: Bounds) -> Graphics:
        pass

    @abstractmethod
    def clear(self) -> Graphics:
        pass
