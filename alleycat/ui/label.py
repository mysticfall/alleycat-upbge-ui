from enum import Enum
from itertools import chain
from typing import Iterable

from alleycat.reactive import RP
from alleycat.reactive import functions as rv

from alleycat.ui import Component, Context


class TextAlign(Enum):
    Begin = 0
    Center = 1
    End = 2


class Label(Component):
    text: RP[str] = rv.from_value("")

    text_align: RP[TextAlign] = rv.from_value(TextAlign.Center)

    text_vertical_align: RP[TextAlign] = rv.from_value(TextAlign.Center)

    size: RP[int] = rv.from_value(10)

    def __init__(self, context: Context) -> None:
        super().__init__(context)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Label"], super().style_fallback_prefixes)
