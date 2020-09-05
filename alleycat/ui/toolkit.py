from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence

from alleycat.ui import Graphics, Context, Input

T = TypeVar("T", bound=Context, contravariant=True)


class Toolkit(ABC, Generic[T]):

    @abstractmethod
    def create_graphics(self, context: T) -> Graphics:
        pass

    @abstractmethod
    def create_inputs(self, context: T) -> Sequence[Input]:
        pass
