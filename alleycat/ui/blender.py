from __future__ import annotations

import sys
from functools import reduce
from pathlib import Path
from typing import cast, Optional, Sequence, Mapping, Final, Callable, Iterator

import bge
import bgl
import blf
import bpy
import gpu
import rx
from alleycat.reactive import ReactiveObject, RV
from alleycat.reactive import functions as rv
from bge.logic import mouse, KX_INPUT_ACTIVE, KX_INPUT_JUST_ACTIVATED
from bge.types import SCA_InputEvent
from bgl import GL_BLEND
from gpu_extras.batch import batch_for_shader
from returns.maybe import Maybe, Some, Nothing
from rx import operators as ops, Observable
from rx.disposable import Disposable
from rx.subject import Subject, BehaviorSubject

from alleycat.ui import Toolkit, Context, Graphics, Bounds, Input, MouseInput, Point, LookAndFeel, WindowManager, \
    Dimension, MouseButton, Font, FontRegistry
from alleycat.ui.context import ContextBuilder, ErrorHandler
from alleycat.ui.event import EventLoopAware


def get_window_size() -> Dimension:
    return Dimension(bge.render.getWindowWidth(), bge.render.getWindowHeight())


class BlenderContext(Context):
    window_size: RV[Dimension] = rv.new_view()

    def __init__(self,
                 toolkit: BlenderToolkit,
                 look_and_feel: Optional[LookAndFeel] = None,
                 window_manager: Optional[WindowManager] = None,
                 error_handler: Optional[ErrorHandler] = None) -> None:
        super().__init__(toolkit, look_and_feel, window_manager, error_handler)

        self._resolution = BehaviorSubject(get_window_size())

        # noinspection PyTypeChecker
        self.window_size = self._resolution.pipe(ops.distinct_until_changed())

    def translate(self, point: Point) -> Point:
        if point is None:
            raise ValueError("Argument 'point' is required.")

        return point.copy(y=self.window_size.height - point.y)

    def process_draw(self) -> None:
        # noinspection PyTypeChecker
        bgl.glEnable(GL_BLEND)

        self._resolution.on_next(get_window_size())

        super().process_draw()


class BlenderToolkit(Toolkit[BlenderContext]):

    def __init__(self, resource_path: Path = Path("//"), error_handler: Optional[ErrorHandler] = None) -> None:
        super().__init__(resource_path, error_handler)

        fonts_path = resource_path / "fonts"

        self._font_registry = BlenderFontRegistry(fonts_path, self.error_handler)

    @property
    def font_registry(self) -> FontRegistry:
        return self._font_registry

    def create_graphics(self, context: BlenderContext) -> Graphics:
        return BlenderGraphics(context)

    def create_inputs(self, context: BlenderContext) -> Sequence[Input]:
        return BlenderMouseInput(context),


class BlenderGraphics(Graphics[BlenderContext]):
    # noinspection PyUnresolvedReferences
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

    def __init__(self, context: BlenderContext) -> None:
        super().__init__(context)

    def fill_rect(self, bounds: Bounds) -> Graphics:
        if bounds is None:
            raise ValueError("Argument 'bounds' is required.")

        def draw(area: Bounds):
            points = area.move_by(self.offset).points

            bc = cast(BlenderContext, self.context)
            vertices = tuple(map(lambda p: p.tuple, map(bc.translate, points)))
            indices = ((0, 1, 3), (3, 1, 2))

            self.shader.bind()
            self.shader.uniform_float("color", self.color.tuple)

            batch = batch_for_shader(self.shader, "TRIS", {"pos": vertices}, indices=indices)
            batch.draw(self.shader)

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

        bc = cast(BlenderContext, self.context)

        font_id = cast(BlenderFont, self.font).font_id

        def draw() -> None:
            (x, y) = bc.translate((location + self.offset)).tuple
            (r, g, b, a) = self.color.tuple

            blf.size(font_id, int(size), BlenderFont.DPI)
            blf.position(font_id, x, y, 0)
            blf.color(font_id, r, g, b, a)

            blf.draw(font_id, text)

        if self.clip is Nothing:
            draw()
        else:
            clip = self.clip.unwrap().move_by(self.offset)
            points = list(map(bc.translate, clip.points))

            def get(getter: Callable[[Point], float], aggregator: Callable[[Iterator[float]], float]) -> float:
                return aggregator(map(getter, points))

            if clip.width > 0 and clip.height > 0:
                blf.clipping(
                    font_id,
                    get(lambda p: p.x, min),
                    get(lambda p: p.y, min),
                    get(lambda p: p.x, max),
                    get(lambda p: p.y, max))

                blf.enable(font_id, blf.CLIPPING)

                draw()

                blf.disable(font_id, blf.CLIPPING)

        return self


class UI(ContextBuilder[BlenderContext]):

    def __init__(self, toolkit: Optional[BlenderToolkit] = None) -> None:
        super().__init__(toolkit if toolkit is not None else BlenderToolkit())

    def create_context(self) -> Context:
        return BlenderContext(cast(BlenderToolkit, self.toolkit), **self.args)


class BlenderMouseInput(MouseInput, ReactiveObject, EventLoopAware):
    position: RV[Point] = rv.new_view()

    buttons: RV[int] = rv.new_view()

    def __init__(self, context: BlenderContext) -> None:
        super().__init__(context)

        self._position = Subject()
        self._activeInputs = Subject()

        # noinspection PyTypeChecker
        self.position = self._position.pipe(
            ops.distinct_until_changed(),
            ops.map(lambda v: tuple(p * s for p, s in zip(v, context.window_size.tuple))),
            ops.map(Point.from_tuple),
            ops.share())

        codes = {
            MouseButton.LEFT: bge.events.LEFTMOUSE,
            MouseButton.MIDDLE: bge.events.MIDDLEMOUSE,
            MouseButton.RIGHT: bge.events.RIGHTMOUSE
        }

        def pressed(e: SCA_InputEvent) -> bool:
            return KX_INPUT_ACTIVE in e.status or KX_INPUT_JUST_ACTIVATED in e.status

        def value_for(button: MouseButton) -> Observable:
            code = codes[button]

            return self._activeInputs.pipe(
                ops.start_with({}),
                ops.map(lambda i: code in i and pressed(i[code])),
                ops.map(lambda v: button if v else 0))

        # noinspection PyTypeChecker
        self.buttons = rx.combine_latest(*[value_for(b) for b in MouseButton]).pipe(
            ops.map(lambda v: reduce(lambda a, b: a | b, v)),
            ops.distinct_until_changed(),
            ops.share())

    def process(self) -> None:
        self._position.on_next(mouse.position)
        self._activeInputs.on_next(mouse.activeInputs)

    def dispose(self) -> None:
        super().dispose()

        self.execute_safely(self._position.dispose)
        self.execute_safely(self._activeInputs.dispose)


class BlenderFont(Font, Disposable):
    DPI: Final = 72  # Make DPI configurable.

    def __init__(self, font_id: int, family: str, path: Optional[Path] = None) -> None:
        if family is None:
            raise ValueError("Argument 'family' is required.")

        super().__init__()

        self._family = family
        self._font_id = font_id
        self._path = Maybe.from_value(path)

    @property
    def family(self) -> str:
        return self._family

    @property
    def font_id(self) -> int:
        return self._font_id

    def dispose(self) -> None:
        super().dispose()

        self._path.map(str).map(blf.unload)


class BlenderFontRegistry(FontRegistry[BlenderFont]):
    default_font_name: Final = "Bfont"

    def __init__(self, font_path: Path, error_handler: ErrorHandler) -> None:
        super().__init__(error_handler)

        self._font_path = font_path
        self._fallback_font = BlenderFont(0, self.default_font_name)
        self._fonts = {self.fallback_font.family: self.fallback_font}

        absolute_path = Path(bpy.path.abspath(str(font_path)))

        if absolute_path.exists():
            for file in absolute_path.glob("*.ttf"):
                family = file.stem
                font_id = blf.load(str(file))

                if font_id == -1:
                    e = IOError(f"Failed to load font file: '{file}'")
                    tb = sys.exc_info()[2]

                    self.error_handler(e.with_traceback(tb))
                else:
                    self._fonts[family] = BlenderFont(font_id, family)

    @property
    def font_path(self) -> Path:
        return self._font_path

    @property
    def fonts(self) -> Mapping[str, BlenderFont]:
        return self._fonts

    @property
    def fallback_font(self) -> BlenderFont:
        return self._fallback_font

    def resolve(self, family: str) -> Maybe[BlenderFont]:
        if family is None:
            raise ValueError("Argument 'family' is required.")

        return Some(self.fonts[family]) if family in self.fonts else Nothing

    def text_extent(self, text: str, font: BlenderFont, size: float) -> Dimension:
        if text is None:
            raise ValueError("Argument 'text' is required.")

        if font is None:
            raise ValueError("Argument 'font' is required.")

        if size <= 0:
            raise ValueError("Argument 'size' is must be a positive number.")

        blf.size(font.font_id, int(size), BlenderFont.DPI)

        return Dimension.from_tuple(blf.dimensions(font.font_id, text))

    def dispose(self) -> None:
        super().dispose()

        for font in self.fonts.values():
            self.execute_safely(font.dispose)

        self._fonts = dict()
