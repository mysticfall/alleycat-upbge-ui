from __future__ import annotations

from typing import cast, Optional, Sequence

import bge
import gpu
from alleycat.reactive import ReactiveObject, RV
from alleycat.reactive import functions as rv
from bge.logic import mouse
from gpu_extras.batch import batch_for_shader
from rx import operators as ops
from rx.subject import Subject, BehaviorSubject

from alleycat.ui import Toolkit, Context, Graphics, Bounds, Input, MouseInput, Point, LookAndFeel, WindowManager, \
    Dimension
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
        self._resolution.on_next(get_window_size())

        super().process_draw()


class BlenderToolkit(Toolkit[BlenderContext]):

    def create_graphics(self, context: BlenderContext) -> Graphics:
        return BlenderGraphics(context)

    def create_inputs(self, context: BlenderContext) -> Sequence[Input]:
        return BlenderMouseInput(context),


class BlenderGraphics(Graphics[BlenderContext]):
    # noinspection PyUnresolvedReferences
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

    def fill_rect(self, bounds: Bounds) -> Graphics:
        if bounds is None:
            raise ValueError("Argument 'bounds' is required.")

        bc = cast(BlenderContext, self.context)
        vertices = tuple(map(lambda p: p.tuple, map(bc.translate, bounds.points)))
        indices = ((0, 1, 3), (3, 1, 2))

        self.shader.bind()
        self.shader.uniform_float("color", self.color.tuple)

        batch = batch_for_shader(self.shader, "TRIS", {"pos": vertices}, indices=indices)
        batch.draw(self.shader)

        return self

    def clear(self) -> Graphics:
        return self

    def dispose(self) -> None:
        super().dispose()


class UI(ContextBuilder[BlenderContext]):

    def __init__(self) -> None:
        super().__init__(BlenderToolkit())

    def create_context(self) -> Context:
        return BlenderContext(cast(BlenderToolkit, self.toolkit), **self.args)


class BlenderMouseInput(MouseInput, ReactiveObject, EventLoopAware):
    position: RV[Point] = rv.new_view()

    def __init__(self, context: BlenderContext) -> None:
        super().__init__(context)

        self._position = Subject()

        # noinspection PyTypeChecker
        self.position = self._position.pipe(ops.distinct_until_changed(), ops.map(Point.from_tuple))

    def process(self) -> None:
        self._position.on_next(mouse.position)

    def dispose(self) -> None:
        super().dispose()

        self._position.dispose()
