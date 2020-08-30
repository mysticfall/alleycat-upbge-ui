from __future__ import annotations

from abc import ABC, abstractmethod

from rx.disposable import Disposable

from alleycat.ui import Bounds, RGBA


class Graphics(Disposable, ABC):

    def __init__(self) -> None:
        super().__init__()

        self.color = RGBA(0, 0, 0, 0)

    @abstractmethod
    def fill_rect(self, bounds: Bounds) -> Graphics:
        pass

    @abstractmethod
    def clear(self) -> Graphics:
        pass
