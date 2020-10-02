from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from returns.maybe import Maybe
from rx.disposable import Disposable

from alleycat.ui import Dimension, ErrorHandlerSupport, ErrorHandler


class Font(Disposable, ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def family(self) -> str:
        pass


T = TypeVar("T", bound=Font)


class FontRegistry(Generic[T], ErrorHandlerSupport, Disposable, ABC):

    def __init__(self, error_handler: ErrorHandler) -> None:
        if error_handler is None:
            raise ValueError("Argument 'error_handler' is required.")

        super().__init__()

        self._error_handler = error_handler

    @property
    @abstractmethod
    def fallback_font(self) -> T:
        pass

    @abstractmethod
    def resolve(self, family: str) -> Maybe[T]:
        pass

    @abstractmethod
    def text_extent(self, text: str, font: T, size: float) -> Dimension:
        pass

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler
