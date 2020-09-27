from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from returns.maybe import Maybe, Nothing, Some
from rx.disposable import Disposable

from alleycat.ui import Bounds, RGBA, Context, Point, Font

T = TypeVar("T", bound=Context, contravariant=True)


class Graphics(Disposable, ABC, Generic[T]):

    def __init__(self, context: T) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context

        self._offset = Point(0, 0)
        self._clip: Maybe[Bounds] = Nothing
        self._font = context.font_registry.fallback_font

        assert self._font is not None

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

        if value == Nothing:
            self._clip = value
        else:
            bounds = value.unwrap().move_by(self._offset)
            clip = Some(bounds) if self._clip is Nothing else self._clip.bind(lambda c: bounds & c)

            self._clip = self._clip.map(lambda b: b.copy(width=0, height=0)) if clip is Nothing else clip

    @abstractmethod
    def fill_rect(self, bounds: Bounds) -> Graphics:
        pass

    @abstractmethod
    def draw_text(self, text: str, size: float, location: Point, allow_wrap: bool = False) -> Graphics:
        pass

    @abstractmethod
    def clear(self) -> Graphics:
        pass
