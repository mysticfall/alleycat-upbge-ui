from __future__ import annotations

from itertools import chain
from typing import Optional, Iterable

from alleycat.ui import Context, Layout, Container


class Panel(Container):

    def __init__(self, context: Context, layout: Optional[Layout] = None, visible: bool = True) -> None:
        super().__init__(context, layout, visible)

    @property
    def style_fallback_prefixes(self) -> Iterable[str]:
        return chain(["Panel"], super().style_fallback_prefixes)
