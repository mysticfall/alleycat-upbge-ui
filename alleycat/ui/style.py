from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Dict, TypeVar, Generic, Any

from returns.maybe import Maybe, Some, Nothing
from rx import Observable
from rx import operators as ops
from rx.disposable import Disposable
from rx.subject import Subject

from alleycat.ui import RGBA, Font, Event


class StyleLookup(Disposable):

    def __init__(self) -> None:
        self._colors: Dict[str, RGBA] = dict()
        self._fonts: Dict[str, Font] = dict()
        self._on_style_change = Subject()

        super().__init__()

    @property
    def on_style_change(self) -> Observable:
        return self._on_style_change.pipe(ops.distinct_until_changed())

    def get_color(self, key: str) -> Maybe[RGBA]:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        return Some(self._colors[key]) if key in self._colors else Nothing

    def set_color(self, key: str, color: RGBA) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        if color is None:
            raise ValueError("Argument 'color' is required.")

        self._colors[key] = color
        self._on_style_change.on_next(ColorChangeEvent(self, key, Some(color)))

    def clear_color(self, key: str) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        try:
            del self._colors[key]

            self._on_style_change.on_next(ColorChangeEvent(self, key, Nothing))
        except KeyError:
            pass

    def get_font(self, key: str) -> Maybe[Font]:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        return Some(self._fonts[key]) if key in self._fonts else Nothing

    def set_font(self, key: str, font: Font) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        if font is None:
            raise ValueError("Argument 'font' is required.")

        self._fonts[key] = font
        self._on_style_change.on_next(FontChangeEvent(self, key, Some(font)))

    def clear_font(self, key: str) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        try:
            del self._fonts[key]

            self._on_style_change.on_next(FontChangeEvent(self, key, Nothing))
        except KeyError:
            pass

    def dispose(self) -> None:
        super().dispose()

        self._on_style_change.dispose()


T = TypeVar("T")


@dataclass(frozen=True)  # type:ignore
class StyleChangeEvent(Event, Generic[T], ABC):
    key: str

    value: Maybe[T]


@dataclass(frozen=True)
class ColorChangeEvent(StyleChangeEvent[RGBA]):
    value: Maybe[RGBA]  # It's redundant, of course. But MyPy isn't smart enough to handle this.

    def with_source(self, source: Any) -> Event:
        return ColorChangeEvent(source, self.key, self.value)


@dataclass(frozen=True)
class FontChangeEvent(StyleChangeEvent[Font]):
    value: Maybe[Font]

    def with_source(self, source: Any) -> Event:
        return FontChangeEvent(source, self.key, self.value)
