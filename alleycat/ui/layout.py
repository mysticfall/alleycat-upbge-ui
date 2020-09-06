from abc import ABC
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

        child.parent = Some(self)

    def remove(self, child: Component) -> None:
        super().remove(child)

        child.parent = Nothing

    def draw(self, g: Graphics) -> None:
        super().draw(g)

        self.draw_children(g)

    def draw_children(self, g: Graphics) -> None:
        # noinspection PyTypeChecker
        for child in self.children:
            child.draw(g)
