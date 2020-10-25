import rx
from rx import Observable

from alleycat.ui import Dimension
from .layout import Layout, LayoutContainer


class AbsoluteLayout(Layout):

    def __init__(self) -> None:
        super().__init__()

    def perform(self, container: LayoutContainer) -> None:
        pass

    def minimum_size(self, container: LayoutContainer) -> Observable:
        return rx.of(Dimension(0, 0))

    def preferred_size(self, container: LayoutContainer) -> Observable:
        return container.observe("size")
