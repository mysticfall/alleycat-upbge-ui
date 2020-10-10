from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Mapping, TYPE_CHECKING

from alleycat.reactive import ReactiveObject
from rx.disposable import Disposable

from alleycat.ui import ErrorHandlerSupport, ErrorHandler

if TYPE_CHECKING:
    from alleycat.ui import Context


class Input(ErrorHandlerSupport, ReactiveObject, ABC):

    def __init__(self, context: Context) -> None:
        if context is None:
            raise ValueError("Argument 'context' is required.")

        super().__init__()

        self._context = context

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    def context(self) -> Context:
        return self._context

    @property
    def error_handler(self) -> ErrorHandler:
        return self.context.error_handler


class InputLookup(ErrorHandlerSupport, Disposable, ABC):

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def inputs(self) -> Mapping[str, Input]:
        pass
