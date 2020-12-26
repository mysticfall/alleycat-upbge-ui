from abc import ABC, abstractmethod
from typing import TypeVar

from cairocffi import Surface
from rx.disposable import Disposable

from alleycat.ui import Dimension, ErrorHandler, Registry


class Image(Disposable, ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def size(self) -> Dimension:
        pass

    @property
    @abstractmethod
    def surface(self) -> Surface:
        pass

    def dispose(self) -> None:
        self.surface.finish()

        super().dispose()


T = TypeVar("T", bound=Image)


class ImageRegistry(Registry[T], ABC):

    def __init__(self, error_handler: ErrorHandler) -> None:
        super().__init__(error_handler)
