from abc import ABC
from itertools import chain
from typing import Iterable

import rx
from alleycat.reactive import RV
from alleycat.reactive import functions as rv
from rx import operators as ops

from alleycat.ui import Context, Label, Component, PropagatingEvent, Event, MouseInput, MouseButton, TextAlign


class Button(Component, ABC):
    hover: RV[bool] = rv.new_view()

    active: RV[bool] = rv.new_view()

    def __init__(self, context: Context, visible: bool = True) -> None:
        super().__init__(context, visible)

        # noinspection PyTypeChecker
        self.hover = rx.merge(
            self.on_mouse_over.pipe(ops.map(lambda _: True)),
            self.on_mouse_out.pipe(ops.map(lambda _: False))).pipe(ops.start_with(False))

        mouse = MouseInput.input(self)

        # noinspection PyTypeChecker
        self.active = self.on_mouse_down.pipe(
            ops.filter(lambda e: e.button == MouseButton.LEFT),
            ops.map(lambda _: rx.concat(rx.of(True), mouse.on_button_release(MouseButton.LEFT).pipe(
                ops.take(1),
                ops.map(lambda _: False)))),
            ops.exclusive(),
            ops.start_with(False))

    def dispatch_event(self, event: Event) -> None:
        if isinstance(event, PropagatingEvent):
            event.stop_propagation()

        super().dispatch_event(event)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Button"], super().style_fallback_prefixes)


class LabelButton(Label, Button):

    def __init__(
            self,
            context: Context,
            text: str = "",
            text_align: TextAlign = TextAlign.Center,
            text_vertical_align: TextAlign = TextAlign.Center,
            text_size: int = 10,
            visible: bool = True) -> None:
        super().__init__(context, text, text_align, text_vertical_align, text_size, visible)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["LabelButton"], filter(lambda v: v != "Label", super().style_fallback_prefixes))
