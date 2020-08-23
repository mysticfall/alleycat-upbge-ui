from typing import List, Tuple

import rx
from alleycat.reactive import functions as rv
from rx import operators as ops
from rx.disposable import Disposable
from rx.subject import Subject

from alleycat.ui import Context, Container, Graphics


class Window(Container):

    def __init__(self, context: Context) -> None:
        super().__init__(context)

        context.window_manager.add(self)

    def draw(self, g: Graphics) -> None:
        super().draw(g)

        g.fill_rect(self.bounds)


class WindowManager(Disposable):
    windows = rv.new_view()

    def __init__(self) -> None:
        super().__init__()

        self._added_child = Subject()
        self._removed_child = Subject()

        changed_child = rx.merge(
            self._added_child.pipe(ops.map(lambda v: (v, True))),
            self._removed_child.pipe(ops.map(lambda v: (v, False))))

        def on_child_change(children: List[Window], event: Tuple[Window, bool]):
            (child, added) = event

            if added and child not in children:
                children.append(child)
            elif not added and child in children:
                children.remove(child)

            return children

        self.windows = changed_child.pipe(ops.scan(on_child_change, []), ops.distinct_until_changed())

    def add(self, child: Window) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._added_child.on_next(child)

    def remove(self, child: Window) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._removed_child.on_next(child)

    def draw(self, g: Graphics) -> None:
        for window in self.windows:
            window.draw(g)
