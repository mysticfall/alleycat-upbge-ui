from abc import ABC, abstractmethod
from typing import Dict, Generic, Iterator, Optional, TypeVar

from returns.maybe import Maybe
from rx.disposable import Disposable

from alleycat.ui import ErrorHandler, ErrorHandlerSupport

T = TypeVar("T")


class Registry(Generic[T], ErrorHandlerSupport, Disposable, ABC):

    def __init__(self, error_handler: ErrorHandler) -> None:
        if error_handler is None:
            raise ValueError("Argument 'error_handler' is required.")

        super().__init__()

        self._cache: Dict[str, T] = dict()
        self._error_handler = error_handler

    @abstractmethod
    def create(self, name: str) -> Maybe[T]:
        pass

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self) -> Iterator[str]:
        return iter(self._cache.keys())

    def __getitem__(self, key: str) -> Optional[T]:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        if key in self._cache:
            return self._cache[key]
        else:
            image = self.create(key).value_or(None)

            if image:
                self[key] = image

            return image

    def __setitem__(self, key: str, value: Optional[T]) -> None:
        if key is None:
            raise ValueError("Argument 'name' is required.")

        del self[key]

        if value:
            self._cache[key] = value

    def __delitem__(self, key: str) -> None:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        try:
            item = self._cache[key]

            if isinstance(item, Disposable):
                self.execute_safely(item.dispose)

            del self._cache[key]
        except KeyError:
            pass

    def __contains__(self, key: str) -> bool:
        if key is None:
            raise ValueError("Argument 'key' is required.")

        return key in self._cache

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    def dispose(self) -> None:
        for i in self._cache.values():
            if isinstance(i, Disposable):
                self.execute_safely(i.dispose)

        self._cache.clear()

        super().dispose()
