from abc import ABC, abstractmethod

from cairocffi import Context as Graphics


class Drawable(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def draw(self, g: Graphics) -> None:
        pass
