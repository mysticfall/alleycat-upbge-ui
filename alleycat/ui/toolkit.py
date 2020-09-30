from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Sequence, Optional

from rx.disposable import Disposable

from alleycat.ui import Graphics, Context, Input, FontRegistry, ErrorHandler
from alleycat.ui.error import default_error_handler

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
    def font_registry(self) -> FontRegistry:
        pass

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    @abstractmethod
    def create_graphics(self, context: T) -> Graphics:
        pass

    @abstractmethod
    def create_inputs(self, context: T) -> Sequence[Input]:
        pass
