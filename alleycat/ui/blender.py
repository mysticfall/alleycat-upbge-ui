from __future__ import annotations

from functools import reduce
from pathlib import Path
from typing import Iterable, Optional, Sequence, Set, cast

import bge
import bgl
import bpy
import gpu
import rx
from alleycat.reactive import RV, ReactiveObject, functions as rv
from bge.logic import KX_INPUT_ACTIVE, KX_INPUT_JUST_ACTIVATED, keyboard, mouse
from bge.types import SCA_InputEvent
from bgl import Buffer
from bpy.types import BlendDataImages, Image as BLImage, SpaceView3D
from cairocffi import Context as Graphics, FORMAT_ARGB32, FontOptions, ImageSurface, Matrix, Surface
from gpu.types import GPUBatch, GPUShader
from gpu_extras.batch import batch_for_shader
from returns.maybe import Maybe, Nothing, Some
from rx import Observable, operators as ops
from rx.subject import BehaviorSubject, Subject

from alleycat.ui import Bounds, Context, Dimension, FontRegistry, Image, ImageRegistry, Input, KeyInput, \
    LookAndFeel, MouseButton, MouseInput, Point, Toolkit, ToyFontRegistry, WindowManager
from alleycat.ui.context import ContextBuilder, ErrorHandler
from alleycat.ui.event import EventLoopAware

# noinspection PyUnresolvedReferences
use_viewport_render = bpy.context.scene.game_settings.use_viewport_render


class BlenderContext(Context):
    window_size: RV[Dimension] = rv.new_view()

    batch: RV[GPUBatch] = window_size.map(lambda c, s: c.create_batch(s))

    buffer: RV[GPUBatch] = window_size.map(lambda c, s: c.create_batch(s))

    def __init__(self,
                 toolkit: BlenderToolkit,
                 look_and_feel: Optional[LookAndFeel] = None,
                 font_options: Optional[FontOptions] = None,
                 window_manager: Optional[WindowManager] = None,
                 error_handler: Optional[ErrorHandler] = None) -> None:
        super().__init__(toolkit, look_and_feel, font_options, window_manager, error_handler)

        resolution = Dimension(bge.render.getWindowWidth(), bge.render.getWindowHeight())

        self._resolution = BehaviorSubject(resolution)

        # noinspection PyTypeChecker
        self.window_size = self._resolution.pipe(ops.distinct_until_changed())

        self._shader = cast(GPUShader, gpu.shader.from_builtin("2D_IMAGE"))

        if use_viewport_render:
            # noinspection PyArgumentList
            self._draw_handler = SpaceView3D.draw_handler_add(self.process, (), "WINDOW", "POST_PIXEL")
        else:
            self._draw_handler = None

            bge.logic.getCurrentScene().post_draw.append(self.process)

        # noinspection PyTypeChecker
        self._texture = Buffer(bgl.GL_INT, 1)

        bgl.glGenTextures(1, self.texture)

    @property
    def shader(self) -> GPUShader:
        return self._shader

    @property
    def texture(self) -> Buffer:
        return self._texture

    def create_batch(self, size: Dimension) -> GPUBatch:
        if size is None:
            raise ValueError("Argument 'size' is required.")

        points = Bounds(0, 0, size.width, size.height).points

        vertices = tuple(map(lambda p: p.tuple, map(self.translate, points)))
        coords = ((0, 0), (1, 0), (1, 1), (0, 1))

        indices = {"pos": vertices, "texCoord": coords}

        return batch_for_shader(self.shader, "TRI_FAN", indices)

    def translate(self, point: Point) -> Point:
        if point is None:
            raise ValueError("Argument 'point' is required.")

        return point.copy(y=self.window_size.height - point.y)

    # noinspection PyTypeChecker
    def process_draw(self) -> None:
        width = bge.render.getWindowWidth()
        height = bge.render.getWindowHeight()

        self._resolution.on_next(Dimension(width, height))

        super().process_draw()

        data = self.surface.get_data()

        source = bgl.Buffer(bgl.GL_BYTE, width * height * 4, data)

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glActiveTexture(bgl.GL_TEXTURE0)

        # noinspection PyUnresolvedReferences
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.texture[0])

        bgl.glTexImage2D(
            bgl.GL_TEXTURE_2D, 0, bgl.GL_SRGB_ALPHA, width, height, 0, bgl.GL_BGRA, bgl.GL_UNSIGNED_BYTE, source)

        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)

        self.shader.bind()
        self.shader.uniform_int("image", 0)

        self.batch.draw(self.shader)

        bgl.glDeleteBuffers(1, source)

    def dispose(self) -> None:
        if self._draw_handler:
            # noinspection PyArgumentList
            SpaceView3D.draw_handler_remove(self._draw_handler, "WINDOW")
        else:
            bge.logic.getCurrentScene().post_draw.remove(self.process)

        bgl.glDeleteTextures(1, self.texture)

        # noinspection PyTypeChecker
        bgl.glDeleteBuffers(1, self.texture)

        super().dispose()


class BlenderToolkit(Toolkit[BlenderContext]):

    def __init__(self, resource_path: Path = Path("//"), error_handler: Optional[ErrorHandler] = None) -> None:
        super().__init__(resource_path, error_handler)

        self._font_registry = ToyFontRegistry(self.error_handler)
        self._image_registry = BlenderImageRegistry(self.error_handler)

    @property
    def fonts(self) -> FontRegistry:
        return self._font_registry

    @property
    def images(self) -> ImageRegistry:
        return self._image_registry

    def create_inputs(self, context: BlenderContext) -> Sequence[Input]:
        return BlenderMouseInput(context), BlenderKeyInput(context)


class UI(ContextBuilder[BlenderContext]):

    def __init__(self, toolkit: Optional[BlenderToolkit] = None) -> None:
        super().__init__(toolkit if toolkit is not None else BlenderToolkit())

    def create_context(self) -> Context:
        return BlenderContext(**self.args)


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

    @property
    def on_mouse_wheel(self) -> Observable:
        def on_wheel(code: int) -> Observable:
            return self._activeInputs.pipe(
                ops.filter(lambda i: code in i),
                ops.map(lambda i: i[code].values[-1]),
                ops.filter(lambda v: v != 0))

        return rx.merge(on_wheel(bge.events.WHEELUPMOUSE), on_wheel(bge.events.WHEELDOWNMOUSE))

    def process(self) -> None:
        self._position.on_next(mouse.position)
        self._activeInputs.on_next(mouse.activeInputs)

    def dispose(self) -> None:
        super().dispose()

        self.execute_safely(self._position.dispose)
        self.execute_safely(self._activeInputs.dispose)


class BlenderKeyInput(KeyInput, ReactiveObject, EventLoopAware):
    pressed: RV[Set[int]] = rv.new_view()

    def __init__(self, context: BlenderContext) -> None:
        super().__init__(context)

        self._activeInputs = Subject()

        # noinspection PyTypeChecker
        self.pressed = self._activeInputs.pipe(
            ops.start_with({}),
            ops.map(lambda s: set(s.keys())))

    def process(self) -> None:
        self._activeInputs.on_next(keyboard.activeInputs)

    def dispose(self) -> None:
        super().dispose()

        self.execute_safely(self._activeInputs.dispose)


class BlenderImage(Image):

    def __init__(self, source: BLImage) -> None:
        if source is None:
            raise ValueError("Argument 'source' is required.")

        super().__init__()

        (width, height) = source.size

        self._size = Dimension(width, height)
        self._source = source

        pixels = source.pixels[:]

        channels = 4
        length = width * height

        def load_image() -> Iterable[int]:
            for i in range(0, length):
                offset = i * channels

                r = pixels[offset]
                g = pixels[offset + 1]
                b = pixels[offset + 2]
                a = pixels[offset + 3]

                yield int(b * 255)
                yield int(g * 255)
                yield int(r * 255)
                yield int(a * 255)

        data = bytearray(load_image())

        pattern = ImageSurface.create_for_data(data, FORMAT_ARGB32, width, height)

        self._surface = ImageSurface(FORMAT_ARGB32, width, height)

        ctx = Graphics(self._surface)

        m = Matrix()
        m.translate(0, height)
        m.scale(1, -1)

        ctx.set_matrix(m)
        ctx.set_source_surface(pattern)
        ctx.paint()

        self.surface.flush()

        pattern.finish()

    @property
    def source(self) -> BLImage:
        return self._source

    @property
    def surface(self) -> Surface:
        return self._surface

    @property
    def size(self) -> Dimension:
        return self._size

    def dispose(self) -> None:
        self.source.gl_free()

        super().dispose()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, BlenderImage):
            return False

        return o.source.name == self.source.name

    def __hash__(self) -> int:
        return self.source.name.__hash__()


class BlenderImageRegistry(ImageRegistry[BlenderImage]):

    def __init__(self, error_handler: ErrorHandler) -> None:
        super().__init__(error_handler)

    def create(self, key: str) -> Maybe[BlenderImage]:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        try:
            # noinspection PyTypeChecker
            return Some(BlenderImage(bpy.data.images[key]))
        except KeyError:
            if Path(bpy.path.abspath(key)).exists():
                images = cast(BlendDataImages, bpy.data.images)
                image = images.load(key, check_existing=False)

                return Some(BlenderImage(image))

        return Nothing
