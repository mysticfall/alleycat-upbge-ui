from itertools import chain
from typing import Iterable, Optional

from rx import operators as ops

from alleycat.ui import Bounds, Context, Dimension, Layout, Window


class Overlay(Window):
    def __init__(self, context: Context, layout: Optional[Layout] = None):
        super().__init__(context, layout)

        def on_resolution_change(size: Dimension):
            self.bounds = Bounds(0, 0, size.width, size.height)

        context.observe("window_size") \
            .pipe(ops.take_until(self.on_dispose)) \
            .subscribe(on_resolution_change, on_error=self.error_handler)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Overlay"], super().style_fallback_prefixes)
