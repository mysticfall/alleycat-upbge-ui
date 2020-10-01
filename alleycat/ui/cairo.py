from __future__ import annotations

from pathlib import Path
from typing import Optional, cast, Sequence, Mapping

import cairo
import rx
from alleycat.reactive import RV
from alleycat.reactive import functions as rv
from cairo import Surface, FontFace, Format, ImageSurface, ToyFontFace
from returns.maybe import Maybe, Some, Nothing

from alleycat.ui import Toolkit, Context, Graphics, Bounds, Input, Dimension, LookAndFeel, WindowManager, \
    FakeMouseInput, Font, Point, FontRegistry
from alleycat.ui.context import ContextBuilder, ErrorHandler
from alleycat.ui.font import T


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

    def __init__(self, resource_path: Path = Path("."), error_handler: Optional[ErrorHandler] = None) -> None:
        super().__init__(resource_path, error_handler)

        self._font_registry = CairoFontRegistry(self.error_handler)

    @property
    def font_registry(self) -> FontRegistry:
        return self._font_registry

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

        self._g = g

        super().__init__(context)

    @property
    def g(self) -> cairo.Context:
        return self._g

    def fill_rect(self, bounds: Bounds) -> Graphics:
        if bounds is None:
            raise ValueError("Argument 'bounds' is required.")

        def draw(area: Bounds):
            (x, y, w, h) = area.move_by(self.offset).tuple
            (r, g, b, a) = self.color

            self.g.set_source_rgba(r, g, b, a)
            self.g.rectangle(x, y, w, h)
            self.g.fill()

        clip = Some(bounds) if self.clip == Nothing else self.clip.bind(lambda c: bounds & c)
        clip.map(draw)

        return self

    def draw_text(self, text: str, size: float, location: Point, allow_wrap: bool = False) -> Graphics:
        if text is None:
            raise ValueError("Argument 'text' is required.")

        if size <= 0:
            raise ValueError("Argument 'size' should be a positive number.")

        if location is None:
            raise ValueError("Argument 'location' is required.")

        def draw() -> None:
            (x, y) = (location + self.offset).tuple
            (r, g, b, a) = self.color

            self.g.set_source_rgba(r, g, b, a)

            self.g.set_font_face(cast(CairoFont, self.font).font_face)
            self.g.set_font_size(size)

            self.g.move_to(x, y)

            self.g.show_text(text)

        if self.clip is Nothing:
            draw()
        else:
            (cx, cy, cw, ch) = self.clip.unwrap().move_by(self.offset)

            if cw > 0 and ch > 0:
                self.g.save()
                self.g.clip_extents()

                self.g.rectangle(cx, cy, cw, ch)
                self.g.clip()

                draw()

                self.g.restore()

        return self

    def reset(self) -> Graphics:
        super().reset()

        (w, h) = self.context.window_size.tuple

        op = self.g.get_operator()

        self.g.rectangle(0, 0, w, h)
        self.g.set_source_rgba(0, 0, 0, 0)
        self.g.set_operator(cairo.OPERATOR_CLEAR)
        self.g.fill()

        self.g.set_operator(op)

        return self


class UI(ContextBuilder[CairoContext]):

    def __init__(self, toolkit: Optional[CairoToolkit] = None) -> None:
        super().__init__(toolkit if toolkit is not None else CairoToolkit())

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


class CairoFont(Font):

    def __init__(self, family: str, font_face: FontFace) -> None:
        if family is None:
            raise ValueError("Argument 'family' is required.")

        if font_face is None:
            raise ValueError("Argument 'font_face' is required.")

        super().__init__()

        self._family = family
        self._font_face = font_face

    @property
    def family(self) -> str:
        return self._family

    @property
    def font_face(self) -> FontFace:
        return self._font_face


class CairoFontRegistry(FontRegistry[CairoFont]):

    def __init__(self, error_handler: ErrorHandler) -> None:
        super().__init__(error_handler)

        self._fallback_font = CairoFont("Sans", ToyFontFace("Sans"))
        self._fonts = {self.fallback_font.family: self.fallback_font}

    @property
    def fallback_font(self) -> CairoFont:
        return self._fallback_font

    @property
    def fonts(self) -> Mapping[str, CairoFont]:
        return self._fonts

    def resolve(self, family: str) -> Maybe[CairoFont]:
        if family is None:
            raise ValueError("Argument 'family' is required.")

        if family in self.fonts:
            return Some(self.fonts[family])

        font = CairoFont(family, ToyFontFace(family))

        self._fonts[family] = font

        return Some(font)

    def text_extent(self, text: str, font: T) -> Dimension:
        if text is None:
            raise ValueError("Argument 'text' is required.")

        extents = cairo.Context(cairo.SVGSurface(None, 0, 0)).text_extents(text)

        return Dimension(extents.width, extents.height)
