from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar, Optional, Dict

from returns.maybe import Maybe, Some, Nothing
from rx.disposable import Disposable

from alleycat.ui import Dimension, ErrorHandlerSupport, ErrorHandler


class Image(Disposable, ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def size(self) -> Dimension:
        pass


T = TypeVar("T", bound=Image)


class ImageRegistry(Generic[T], ErrorHandlerSupport, Disposable, ABC):

    def __init__(self, error_handler: ErrorHandler) -> None:
        if error_handler is None:
            raise ValueError("Argument 'error_handler' is required.")

        super().__init__()

        self._cache: Dict[str, T] = dict()
        self._error_handler = error_handler

    def register(self, path: Path, name: Optional[str] = None) -> T:
        if path is None:
            raise ValueError("Argument 'path' is required.")

        image = self.load(path)

        key = Maybe.from_optional(name).value_or(path.name)

        if key in self._cache:
            Maybe.from_optional(self._cache[key]).map(lambda i: i.dispose())

            self._cache[key] = image

        return image

    @abstractmethod
    def load(self, path: Path) -> T:
        pass

    def resolve(self, name: str) -> Maybe[T]:
        if name is None:
            raise ValueError("Argument 'name' is required.")

        return Some(self._cache[name]) if name in self._cache else Nothing

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    def dispose(self) -> None:
        map(lambda i: self.execute_safely(i.dispose), self._cache.values())

        self._cache.clear()

        super().dispose()
