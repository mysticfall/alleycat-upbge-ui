from __future__ import annotations

from alleycat.ui import Context, Container


class Panel(Container):

    def __init__(self, context: Context) -> None:
        super().__init__(context)
