from abc import ABC, abstractmethod
from typing import TypeVar

import cairocffi
from cairocffi import FontFace, SVGSurface, ToyFontFace
from returns.maybe import Maybe, Some

from alleycat.ui import Dimension, ErrorHandler, Registry

T = TypeVar("T", bound=FontFace)


class FontRegistry(Registry[T], ABC):

    def __init__(self, error_handler: ErrorHandler) -> None:
        super().__init__(error_handler)

    @property
    @abstractmethod
    def fallback_font(self) -> T:
        pass

    @abstractmethod
    def text_extent(self, text: str, font: T, size: float) -> Dimension:
        pass


class ToyFontRegistry(FontRegistry[ToyFontFace]):

    def __init__(self, error_handler: ErrorHandler) -> None:
        super().__init__(error_handler)

        self._fallback_font = ToyFontFace("Sans")
        self._fonts = {"Sans": self.fallback_font}

        self._surface = SVGSurface(None, 0, 0)
        self._context = cairocffi.Context(SVGSurface(None, 0, 0))

    @property
    def fallback_font(self) -> ToyFontFace:
        return self._fallback_font

    def create(self, name: str) -> Maybe[T]:
        return Some(ToyFontFace(name))

    def text_extent(self, text: str, font: ToyFontFace, size: float) -> Dimension:
        if text is None:
            raise ValueError("Argument 'text' is required.")

        if size <= 0:
            raise ValueError("Argument 'size' is must be a positive number.")

        self._context.set_font_size(size)
        self._context.set_font_face(font)

        (x_bearing, y_bearing, width, height, x_advance, y_advance) = self._context.text_extents(text)

        return Dimension(x_advance, height)

    def dispose(self) -> None:
        self._surface.finish()

        super().dispose()
