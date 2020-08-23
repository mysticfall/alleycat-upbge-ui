from abc import ABC, abstractmethod

from alleycat.ui import Graphics


class Drawable(ABC):

    @abstractmethod
    def draw(self, g: Graphics) -> None:
        pass
