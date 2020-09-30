from __future__ import annotations

from typing import Dict, Mapping

from returns.maybe import Maybe, Some, Nothing

from alleycat.ui import RGBA


class StyleLookup:

    def __init__(self) -> None:
        super().__init__()

        self._colors: Dict[str, RGBA] = dict()

    @property
    def colors(self) -> Mapping[str, RGBA]:
        return self._colors

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
