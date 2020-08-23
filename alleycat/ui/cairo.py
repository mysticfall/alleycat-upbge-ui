from typing import Iterable

from cairo import Surface, Format, ImageSurface

from alleycat.ui import Toolkit, Context, Graphics, Bounds, Input
from alleycat.ui.context import ContextBuilder


class UI(ContextBuilder):
    def __init__(self) -> None:
        super().__init__(CairoToolkit())


class CairoToolkit(Toolkit):

    def create_graphics(self, context: Context) -> Graphics:
        surface = ImageSurface(Format.ARGB32, 1024, 768)

        return CairoGraphics(surface)

    def create_inputs(self, context: Context) -> Iterable[Input]:
        return []


class CairoGraphics(Graphics):
    def __init__(self, surface: Surface):
        if surface is None:
            raise ValueError("Argument 'surface' is required.")

        super().__init__()

        self._surface = surface

    @property
    def surface(self) -> Surface:
        return self._surface

    def fill_rect(self, bounds: Bounds) -> Graphics:
        return self

    def dispose(self) -> None:
        super().dispose()

        self._surface.finish()
