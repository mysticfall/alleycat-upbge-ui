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
    text: RP[str] = rv.new_property()

    text_align: RP[TextAlign] = rv.new_property()

    text_vertical_align: RP[TextAlign] = rv.new_property()

    text_size: RP[int] = rv.new_property()

    # noinspection PyTypeChecker
    def __init__(
            self,
            context: Context,
            text: str = "",
            text_align: TextAlign = TextAlign.Center,
            text_vertical_align: TextAlign = TextAlign.Center,
            text_size: int = 10,
            visible: bool = True) -> None:
        if text_size < 0:
            raise ValueError("Argument 'text_size' should be zero or a positive number.")

        self.text = text
        self.text_align = text_align
        self.text_vertical_align = text_vertical_align
        self.text_size = text_size

        super().__init__(context, visible)

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

    def minimum_size(self, component: Label) -> Observable:
        return self.on_extents_change(component)
