from abc import ABC
from itertools import chain
from typing import Iterable, Optional

from alleycat.reactive import RP, functions as rv
from returns.maybe import Maybe

from alleycat.ui import Component, ComponentUI, Context, Dimension, Image, Insets


class Canvas(Component):
    image: RP[Maybe[Image]] = rv.new_property()

    padding: RP[Insets] = rv.new_property()

    # noinspection PyTypeChecker
    def __init__(
            self,
            context: Context,
            image: Optional[Image] = None,
            padding: Insets = Insets(0, 0, 0, 0),
            visible: bool = True) -> None:
        self.image = Maybe.from_optional(image)
        self.padding = padding

        super().__init__(context, visible)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Canvas"], super().style_fallback_prefixes)


# noinspection PyMethodMayBeStatic
class CanvasUI(ComponentUI[Canvas], ABC):

    def __init__(self) -> None:
        super().__init__()

    def padding(self, component: Canvas) -> Insets:
        return component.padding

    def preferred_size(self, component: Canvas) -> Dimension:
        (width, height) = component.image.map(lambda i: i.size.tuple).value_or((0, 0))
        (top, right, bottom, left) = self.padding(component).tuple

        return Dimension(width + left + right, height + top + bottom)
