from typing import Iterable

import gpu
from alleycat.reactive import ReactiveObject, RV
from alleycat.reactive import functions as rv
from bge.logic import mouse
from gpu_extras.batch import batch_for_shader
from rx import operators as ops
from rx.subject import Subject

from alleycat.ui import Toolkit, Context, Graphics, Bounds, Input, MouseInput, Point
from alleycat.ui.context import ContextBuilder
from alleycat.ui.event import EventLoopAware


class UI(ContextBuilder):
    def __init__(self) -> None:
        super().__init__(BlenderToolkit())


class BlenderToolkit(Toolkit):

    def create_graphics(self, context: Context) -> Graphics:
        return BlenderGraphics()

    def create_inputs(self, context: Context) -> Iterable[Input]:
        return [BlenderMouseInput(context)]


class BlenderGraphics(Graphics):
    # noinspection PyUnresolvedReferences
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")

    def fill_rect(self, bounds: Bounds) -> Graphics:
        vertices = tuple(map(lambda p: p.tuple, bounds.points))
        indices = ((0, 1, 3), (3, 1, 2))

        self.shader.bind()
        self.shader.uniform_float("color", (0, 0.5, 0.5, 1.0))

        batch = batch_for_shader(self.shader, "TRIS", {"pos": vertices}, indices=indices)
        batch.draw(self.shader)

        return self

    def dispose(self) -> None:
        super().dispose()


class BlenderMouseInput(MouseInput, ReactiveObject, EventLoopAware):
    position: RV[Point] = rv.new_view()

    def __init__(self, context: Context) -> None:
        super().__init__(context)

        self._position = Subject()

        # noinspection PyTypeChecker
        self.position = self._position.pipe(ops.distinct_until_changed(), ops.map(Point.from_tuple))

    def process(self) -> None:
        self._position.on_next(mouse.position)

    def dispose(self) -> None:
        super().dispose()

        self._position.dispose()
