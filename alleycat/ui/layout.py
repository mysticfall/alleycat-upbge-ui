from abc import ABC
from enum import Enum
from typing import Optional, Iterator

from returns.maybe import Maybe, Nothing, Some

from alleycat.ui import Component, Container, Point, Graphics, Context


class Layout(ABC):

    def __init__(self) -> None:
        super().__init__()


class AbsoluteLayout(Layout):

    def __init__(self) -> None:
        super().__init__()


class LayoutContainer(Component, Container[Component]):

    def __init__(self, context: Context, layout: Optional[Layout] = None):
        super().__init__(context)

        self._layout = Maybe.from_value(layout).or_else_call(AbsoluteLayout)

    @property
    def layout(self) -> Layout:
        return self._layout

    def component_at(self, location: Point) -> Maybe[Component]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        if self.bounds.contains(location):
            try:
                # noinspection PyTypeChecker
                children: Iterator[Component] = reversed(self.children)

                child = next(c for c in children if c.bounds.contains(location - self.location))

                if isinstance(child, LayoutContainer):
                    return child.component_at(location - self.location)
                else:
                    return Some(child)
            except StopIteration:
                return Some(self)

        return Nothing

    def add(self, child: Component) -> None:
        super().add(child)

        child.parent.map(lambda p: p.remove(child))
        child.parent = Some(self)

    def remove(self, child: Component) -> None:
        super().remove(child)

        child.parent = Nothing

    def draw_component(self, g: Graphics) -> None:
        super().draw_component(g)

        self.draw_children(g)

    def draw_children(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.draw(g)

    def dispose(self) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            self.execute_safely(child.dispose)

        super().dispose()


class Anchor(Enum):
    North = 0
    Northeast = 1
    East = 2
    Southeast = 3
    South = 4
    Southwest = 5
    West = 6
    Northwest = 7
