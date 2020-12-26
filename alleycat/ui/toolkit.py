from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Optional, Sequence, TypeVar

from cairocffi import FORMAT_ARGB32, ImageSurface, Surface
from rx.disposable import Disposable

from alleycat.ui import Context, Dimension, ErrorHandler, FontRegistry, Input
from alleycat.ui.error import default_error_handler
from alleycat.ui.image import ImageRegistry

T = TypeVar("T", bound=Context, contravariant=True)


class Toolkit(Disposable, Generic[T], ABC):

    def __init__(self, resource_path: Path = Path("."), error_handler: Optional[ErrorHandler] = None) -> None:
        if resource_path is None:
            raise ValueError("Argument 'resource_path' is required.")

        super().__init__()

        self._resource_path = resource_path
        self._error_handler = error_handler if error_handler is not None else default_error_handler

    @property
    def resource_path(self) -> Path:
        return self._resource_path

    @property
    @abstractmethod
    def fonts(self) -> FontRegistry:
        pass

    @property
    @abstractmethod
    def images(self) -> ImageRegistry:
        pass

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    # noinspection PyMethodMayBeStatic
    def create_surface(self, size: Dimension) -> Surface:
        if size is None:
            raise ValueError("Argument 'size' is required.")

        return ImageSurface(FORMAT_ARGB32, int(size.width), int(size.height))

    @abstractmethod
    def create_inputs(self, context: T) -> Sequence[Input]:
        pass
