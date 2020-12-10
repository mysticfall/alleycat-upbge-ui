from abc import ABC
from itertools import chain
from typing import Optional, Iterable

import rx
from alleycat.reactive import RP
from alleycat.reactive import functions as rv
from returns.maybe import Maybe
from rx import Observable
from rx import operators as ops

from alleycat.ui import Component, Context, Image, Insets, ComponentUI, Dimension


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

    def on_image_change(self, component: Canvas) -> Observable:
        return component.observe("image")

    def on_padding_change(self, component: Canvas) -> Observable:
        return component.observe("padding")

    def calculate_size(self, image: Maybe[Image], padding: Insets) -> Dimension:
        (w, h) = image.map(lambda i: i.size.tuple).value_or((0, 0))
        (top, right, bottom, left) = padding.tuple

        return Dimension(w + left + right, h + top + bottom)

    def preferred_size(self, component: Canvas) -> Observable:
        image = self.on_image_change(component)
        padding = self.on_padding_change(component)

        return rx.combine_latest(image, padding).pipe(
            ops.map(lambda v: self.calculate_size(v[0], v[1])),
            ops.distinct_until_changed())
