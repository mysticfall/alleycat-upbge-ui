from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from alleycat.ui import ErrorHandler, ErrorHandlerSupport

if TYPE_CHECKING:
    from alleycat.ui import Context


class ContextAware(ErrorHandlerSupport, ABC):

    @property
    @abstractmethod
    def context(self) -> "Context":
        pass

    @property
    def error_handler(self) -> ErrorHandler:
        return self.context.error_handler
