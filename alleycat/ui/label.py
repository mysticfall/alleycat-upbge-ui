from abc import ABC, abstractmethod
from enum import Enum
from itertools import chain
from typing import Iterable

from alleycat.reactive import RP, functions as rv
from cairocffi import FontFace

from alleycat.ui import Component, ComponentUI, Context, Dimension


class TextAlign(Enum):
    Begin = 0
    Center = 1
    End = 2


class Label(Component):
    text: RP[str] = rv.new_property()

    text_align: RP[TextAlign] = rv.new_property()

    text_vertical_align: RP[TextAlign] = rv.new_property()

    text_size: RP[int] = rv.new_property()

    shadow: RP[bool] = rv.new_property()

    # noinspection PyTypeChecker
    def __init__(
            self,
            context: Context,
            text: str = "",
            text_align: TextAlign = TextAlign.Center,
            text_vertical_align: TextAlign = TextAlign.Center,
            text_size: int = 10,
            shadow: bool = False,
            visible: bool = True) -> None:
        if text_size < 0:
            raise ValueError("Argument 'text_size' should be zero or a positive number.")

        self.text = text
        self.text_align = text_align
        self.text_vertical_align = text_vertical_align
        self.text_size = text_size
        self.shadow = shadow

        super().__init__(context, visible)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Label"], super().style_fallback_prefixes)


class LabelUI(ComponentUI[Label], ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def font(self, component: Label) -> FontFace:
        pass

    def extents(self, component: Label) -> Dimension:
        text = component.text
        size = component.text_size
        font = self.font(component)

        registry = component.context.toolkit.fonts

        return registry.text_extent(text, font, size)
