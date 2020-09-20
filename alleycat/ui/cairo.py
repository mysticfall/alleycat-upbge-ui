from __future__ import annotations

from typing import Optional, cast, Sequence

import cairo
import rx
from alleycat.reactive import RV
from alleycat.reactive import functions as rv
from cairo import Surface, Format, ImageSurface

from alleycat.ui import Toolkit, Context, Graphics, Bounds, Input, Dimension, LookAndFeel, WindowManager, FakeMouseInput
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

    def __init__(self) -> None:
        super().__init__()

    def create_graphics(self, context: CairoContext) -> Graphics:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        ctx = cairo.Context(context.surface)

        return CairoGraphics(ctx, context)

    def create_inputs(self, context: Context) -> Sequence[Input]:
        return FakeMouseInput(context),


class CairoGraphics(Graphics[CairoContext]):

    def __init__(self, g: cairo.Context, context: CairoContext) -> None:
        if g is None:
            raise ValueError("Argument 'g' is required.")

        super().__init__(context)

        self._g = g

    @property
    def g(self) -> cairo.Context:
        return self._g

    def fill_rect(self, bounds: Bounds) -> Graphics:
        if bounds is None:
            raise ValueError("Argument 'bounds' is required.")

        (x, y, w, h) = bounds.move_by(self.offset).tuple
        (r, g, b, a) = self.color

        self.g.set_source_rgba(r, g, b, a)
        self.g.rectangle(x, y, w, h)
        self.g.fill()

        return self

    def clear(self) -> Graphics:
        pass


class UI(ContextBuilder[CairoContext]):

    def __init__(self) -> None:
        super().__init__(CairoToolkit())

        self._surface: Optional[Surface] = None

    def with_surface(self, surface: Surface) -> UI:
        if surface is None:
            raise ValueError("Argument 'surface' is required.")

        self._surface = surface

        return self

    def with_image_surface(self, size: Dimension = Dimension(100, 100)) -> UI:
        if size is None:
            raise ValueError("Argument 'size' is required.")

        return self.with_surface(ImageSurface(Format.ARGB32, int(size.width), int(size.height)))

    def create_context(self) -> CairoContext:
        surface = self._surface if self._surface is not None else ImageSurface(Format.ARGB32, 100, 100)

        return CairoContext(cast(CairoToolkit, self.toolkit), surface, **self.args)
