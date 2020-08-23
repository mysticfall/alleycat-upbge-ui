from abc import ABC, abstractmethod
from typing import Iterable

from alleycat.ui import Graphics, Context, Input


class Toolkit(ABC):

    @abstractmethod
    def create_graphics(self, context: Context) -> Graphics:
        pass

    @abstractmethod
    def create_inputs(self, context: Context) -> Iterable[Input]:
        pass
