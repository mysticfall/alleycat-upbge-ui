from __future__ import annotations

from typing import Dict

from returns.maybe import Maybe, Some, Nothing

from alleycat.ui import RGBA, Font


class StyleLookup:

    def __init__(self) -> None:
        super().__init__()

        self._colors: Dict[str, RGBA] = dict()
        self._fonts: Dict[str, Font] = dict()

    def get_color(self, key: str) -> Maybe[RGBA]:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        return Some(self._colors[key]) if key in self._colors else Nothing

    def set_color(self, key: str, value: RGBA) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        if value is None:
            raise ValueError("Argument 'value' is required.")

        self._colors[key] = value

    def clear_color(self, key: str) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        try:
            del self._colors[key]
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

    def clear_font(self, key: str) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        try:
            del self._fonts[key]
        except KeyError:
            pass
