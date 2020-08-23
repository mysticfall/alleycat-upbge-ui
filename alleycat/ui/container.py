from typing import List, Tuple

import rx
from alleycat.reactive import functions as rv
from rx import operators as ops
from rx.subject import Subject

from alleycat.ui import Component, Context


class Container(Component):
    children = rv.new_view()

    def __init__(self, context: Context) -> None:
        super().__init__(context)

        self._added_child = Subject()
        self._removed_child = Subject()

        changed_child = rx.merge(
            self._added_child.pipe(ops.map(lambda v: (v, True))),
            self._removed_child.pipe(ops.map(lambda v: (v, False))))

        def on_child_change(children: List[Component], event: Tuple[Component, bool]):
            (child, added) = event

            if added and child not in children:
                children.append(child)
            elif not added and child in children:
                children.remove(child)

            return children

        self.children = changed_child.pipe(ops.scan(on_child_change, []), ops.distinct_until_changed())

    def add(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._added_child.on_next(child)

    def remove(self, child: Component) -> None:
        if child is None:
            raise ValueError("Argument 'child' is required.")

        self._removed_child.on_next(child)
