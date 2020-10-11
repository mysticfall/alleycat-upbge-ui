from abc import ABC, abstractmethod
from enum import Enum
from itertools import chain
from typing import Iterable

import rx
from alleycat.reactive import RP
from alleycat.reactive import functions as rv
from rx import Observable
from rx import operators as ops

from alleycat.ui import Component, Context, ComponentUI


class TextAlign(Enum):
    Begin = 0
    Center = 1
    End = 2


class Label(Component):
    text: RP[str] = rv.from_value("")

    text_align: RP[TextAlign] = rv.from_value(TextAlign.Center)

    text_vertical_align: RP[TextAlign] = rv.from_value(TextAlign.Center)

    text_size: RP[int] = rv.from_value(10)

    def __init__(self, context: Context) -> None:
        super().__init__(context)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Label"], super().style_fallback_prefixes)


class LabelUI(ComponentUI[Label], ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def on_font_change(self, component: Label) -> Observable:
        pass

    def on_extents_change(self, component: Label) -> Observable:
        text = component.observe("text")
        size = component.observe("text_size")
        font = self.on_font_change(component)

        registry = component.context.toolkit.font_registry

        return rx.combine_latest(text, font, size).pipe(
            ops.map(lambda v: registry.text_extent(v[0], v[1], v[2])))
