from __future__ import annotations

from typing import Optional, Iterator

from returns.maybe import Maybe, Nothing, Some

from alleycat.ui import Context, Graphics, Container, LayoutContainer, Layout, Drawable, Point


class Window(LayoutContainer):

    def __init__(self, context: Context, layout: Optional[Layout] = None) -> None:
        super().__init__(context, layout)

        context.window_manager.add(self)


class WindowManager(Drawable, Container[Window]):

    def __init__(self) -> None:
        super().__init__()

    def window_at(self, location: Point) -> Maybe[Window]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        try:
            # noinspection PyTypeChecker
            children: Iterator[Window] = reversed(self.children)

            return Some(next(c for c in children if c.bounds.contains(location)))
        except StopIteration:
            return Nothing

    def draw(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.draw(g)

    def dispose(self) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.dispose()

        super().dispose()
