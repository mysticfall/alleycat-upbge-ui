from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cmp_to_key
from typing import TypeVar, Type, Callable, List, Tuple

from alleycat.ui import StyleLookup, Component, Toolkit, ComponentUI

T = TypeVar("T", bound=Component, contravariant=True)


class LookAndFeel(StyleLookup, ABC):

    def __init__(self, toolkit: Toolkit) -> None:
        if toolkit is None:
            raise ValueError("Argument 'toolkit' is required.")

        super().__init__()

        self._toolkit = toolkit
        self._ui_factories: List[Tuple[Type, Callable[[], ComponentUI]]] = list()

    @property
    def toolkit(self) -> Toolkit:
        return self._toolkit

    def create_ui(self, component: T) -> ComponentUI[T]:
        if component is None:
            raise ValueError("Argument 'component' is required.")

        for factory in self._ui_factories:
            if isinstance(component, factory[0]):
                return factory[1]()

        return self.default_ui

    def register_ui(self, component_type: Type, factory: Callable[[], ComponentUI]) -> None:
        if factory is None:
            raise ValueError("Argument 'factory' is required.")

        self.deregister_ui(component_type)

        factories = self._ui_factories[:]
        factories.append((component_type, factory))

        def comparator(v1, v2) -> int:
            def compare_names() -> int:
                name1 = v1[0].__qualname__
                name2 = v2[0].__qualname__

                return 1 if name1 < name2 else -1 if name1 > name2 else 0

            return -1 if issubclass(v1[0], v2[0]) else 1 if issubclass(v2[0], v1[0]) else compare_names()

        self._ui_factories = sorted(factories, key=cmp_to_key(comparator))

    def deregister_ui(self, component_type: Type) -> None:
        if component_type is None:
            raise ValueError("Argument 'component_type' is required.")

        self._ui_factories = [i for i in self._ui_factories if i[0] != component_type]

    @property
    @abstractmethod
    def default_ui(self) -> ComponentUI[Component]:
        pass
