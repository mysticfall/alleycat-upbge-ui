from __future__ import annotations

from abc import ABC, abstractmethod

from rx.disposable import Disposable

from alleycat.ui import Bounds


class Graphics(Disposable, ABC):

    @abstractmethod
    def fill_rect(self, bounds: Bounds) -> Graphics:
        pass
