from __future__ import annotations

from alleycat.ui import Bounds, Context, Container, Graphics


def _to_tuples(bounds: Bounds):
    return tuple(map(lambda v: v.tuple, bounds.points))


class Panel(Container):

    def __init__(self, context: Context) -> None:
        super().__init__(context)

        self.bounds = Bounds(30, 40, 400, 200)

    def draw(self, g: Graphics):
        super().draw(g)

        g.fill_rect(self.bounds)
