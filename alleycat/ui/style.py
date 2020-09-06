from __future__ import annotations

from abc import ABC
from typing import Dict, Mapping

from returns.maybe import Maybe, Some, Nothing
from returns.result import safe

from alleycat.ui import RGBA


class StyleLookup:

    def __init__(self) -> None:
        super().__init__()

        self._colors: Dict[ColorKey, RGBA] = dict()

    @property
    def style_fallback(self) -> Maybe[StyleLookup]:
        return Nothing

    @property
    def colors(self) -> Mapping[ColorKey, RGBA]:
        return self._colors

    def get_color(self, key: ColorKey) -> Maybe[RGBA]:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        color: Maybe[RGBA] = safe(lambda k: Some(self._colors[k]))(key).value_or(Nothing)

        def fallback() -> Maybe[RGBA]:
            return self.style_fallback.bind(lambda f: f.get_color(key))

        return color.map(lambda v: Some(v)).or_else_call(fallback)

    def set_color(self, key: ColorKey, value: RGBA) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        if value is None:
            raise ValueError("Argument 'value' is required.")

        self._colors[key] = value

    def clear_color(self, key: ColorKey) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        try:
            del self._colors[key]
        except KeyError:
            pass


class StyleKey(ABC):
    pass


class ColorKey(StyleKey):
    pass
