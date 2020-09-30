from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from returns.maybe import Maybe, Nothing, Some
from rx.disposable import Disposable

from alleycat.ui import Bounds, RGBA, Context, Point, Font

T = TypeVar("T", bound=Context, contravariant=True)


class Graphics(Disposable, ABC, Generic[T]):
    _offset: Point

    _clip: Maybe[Bounds]

    _color: RGBA

    _font: Font

    def __init__(self, context: T) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context

        self.reset()

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
    def font(self) -> Font:
        return self._font

    @font.setter
    def font(self, value: Font) -> None:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        self._font = value

    @property
    def offset(self) -> Point:
        return self._offset

    @offset.setter
    def offset(self, value: Point) -> None:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        self._offset = value

    @property
    def clip(self) -> Maybe[Bounds]:
        return self._clip.map(lambda c: c.move_by(-self._offset))

    @clip.setter
    def clip(self, value: Maybe[Bounds]) -> None:
        if value is None:
            raise ValueError("Argument 'value' is required.")

        self._clip = value.map(lambda v: v.move_by(self._offset))

    @abstractmethod
    def fill_rect(self, bounds: Bounds) -> Graphics:
        pass

    @abstractmethod
    def draw_text(self, text: str, size: float, location: Point, allow_wrap: bool = False) -> Graphics:
        pass

    @abstractmethod
    def clear(self) -> Graphics:
        pass

    def reset(self) -> Graphics:
        self._offset = Point(0, 0)
        self._clip: Maybe[Bounds] = Nothing
        self._color = RGBA(0, 0, 0, 1)
        self._font = self.context.font_registry.fallback_font

        assert self._font is not None

        return self

    def reset(self) -> Graphics:
        self._offset = Point(0, 0)
        self._clip: Maybe[Bounds] = Nothing
        self._color = RGBA(0, 0, 0, 1)
        self._font = self.context.font_registry.fallback_font

        assert self._font is not None

        return self
