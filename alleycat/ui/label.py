from alleycat.reactive import RP
from alleycat.reactive import functions as rv

from alleycat.ui import Component, Context


class Label(Component):
    text: RP[str] = rv.from_value("")

    size: RP[int] = rv.from_value(10)

    def __init__(self, context: Context) -> None:
        super().__init__(context)
