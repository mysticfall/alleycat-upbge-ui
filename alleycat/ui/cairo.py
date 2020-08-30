from __future__ import annotations

from typing import Iterable, Optional, cast

import cairo
import rx
from alleycat.reactive import RV
from alleycat.reactive import functions as rv
from cairo import Surface, Format, ImageSurface

from alleycat.ui import Toolkit, Context, Graphics, Bounds, Input, Dimension, LookAndFeel, WindowManager
from alleycat.ui.context import ContextBuilder, ErrorHandler


class CairoContext(Context):
    window_size: RV[Dimension] = rv.new_view()

    def __init__(self,
                 toolkit: CairoToolkit,
                 surface: Surface,
                 look_and_feel: Optional[LookAndFeel] = None,
                 window_manager: Optional[WindowManager] = None,
                 error_handler: Optional[ErrorHandler] = None) -> None:
        if surface is None:
            raise ValueError("Argument 'surface' is required.")

        self._surface = surface

        super().__init__(toolkit, look_and_feel, window_manager, error_handler)

        ctx = cairo.Context(surface)

        (x1, y1, x2, y2) = ctx.clip_extents()

        # noinspection PyTypeChecker
        self.window_size = rx.of(Dimension(x2 - x1, y2 - y1))

    @property
    def surface(self) -> Surface:
        return self._surface

    def dispose(self) -> None:
        super().dispose()

        self.surface.finish()


class CairoToolkit(Toolkit[CairoContext]):

    def create_graphics(self, context: CairoContext) -> Graphics:
        ctx = cairo.Context(context.surface)

        return CairoGraphics(ctx)

    def create_inputs(self, context: Context) -> Iterable[Input]:
        return []


class CairoGraphics(Graphics):
    def __init__(self, context: cairo.Context) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context

    @property
    def context(self) -> cairo.Context:
        return self._context

    def fill_rect(self, bounds: Bounds) -> Graphics:
        return self


class UI(ContextBuilder[CairoContext]):

    def __init__(self) -> None:
        super().__init__(CairoToolkit())

        self._surface: Optional[Surface] = None

    def with_surface(self, surface: Surface) -> UI:
        if surface is None:
            raise ValueError("Argument 'surface' is required.")

        self._surface = surface

        return self

    def create_context(self) -> CairoContext:
        surface = self._surface if self._surface is not None else ImageSurface(Format.ARGB32, 640, 480)

        return CairoContext(cast(CairoToolkit, self.toolkit), surface, **self.args)
