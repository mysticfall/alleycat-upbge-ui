from __future__ import annotations

from typing import Optional

from alleycat.ui import Context, Layout, LayoutContainer


class Panel(LayoutContainer):

    def __init__(self, context: Context, layout: Optional[Layout] = None) -> None:
        super().__init__(context, layout)
