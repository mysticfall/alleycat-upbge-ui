from __future__ import annotations

from typing import Optional

from alleycat.reactive import functions as rv, RP
from returns.maybe import Maybe, Nothing

from alleycat.ui import Context, Graphics, Container, LayoutContainer, Layout, Drawable


class Window(LayoutContainer):
    parent: RP[Maybe[Container[Window]]] = rv.from_value(Nothing)

    def __init__(self, context: Context, layout: Optional[Layout] = None) -> None:
        super().__init__(context, layout)

        context.window_manager.add(self)


class WindowManager(Container[Window], Drawable):

    def add(self, child: Window) -> None:
        super().add(child)

        child.parent = self

    def remove(self, child: Window) -> None:
        super().remove(child)

        child.parent = Nothing

    def draw(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.draw(g)
