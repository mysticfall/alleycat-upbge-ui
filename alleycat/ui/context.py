from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Mapping, Optional, Any, Dict, TYPE_CHECKING, TypeVar, Generic

from alleycat.reactive import ReactiveObject, RV
from returns.maybe import Maybe, Some

from alleycat.ui import EventDispatcher, EventLoopAware, ErrorHandler, ErrorHandlerSupport, InputLookup, Input, \
    Dimension, Point, Bounds

if TYPE_CHECKING:
    from alleycat.ui import Graphics, LookAndFeel, Toolkit, WindowManager


class Context(EventLoopAware, InputLookup, ErrorHandlerSupport, ReactiveObject, ABC):
    window_size: RV[Dimension]

    def __init__(self,
                 toolkit: Toolkit,
                 look_and_feel: Optional[LookAndFeel] = None,
                 window_manager: Optional[WindowManager] = None,
                 error_handler: Optional[ErrorHandler] = None) -> None:
        if toolkit is None:
            raise ValueError("Argument 'toolkit' is required.")

        super().__init__()

        from alleycat.ui import WindowManager
        from alleycat.ui.glass import GlassLookAndFeel

        self._toolkit = toolkit

        self._look_and_feel = Maybe.from_value(look_and_feel).or_else_call(lambda: GlassLookAndFeel(toolkit))
        self._error_handler = Maybe.from_value(error_handler).value_or(toolkit.error_handler)

        self._window_manager = Maybe.from_value(window_manager) \
            .or_else_call(lambda: WindowManager(self.error_handler))

        inputs = toolkit.create_inputs(self)

        assert inputs is not None

        self._graphics: Optional[Graphics] = None
        self._inputs = {i.id: i for i in inputs}
        self._pollers = [i for i in inputs if isinstance(i, EventLoopAware)]

    @property
    def toolkit(self) -> Toolkit:
        return self._toolkit

    @property
    def inputs(self) -> Mapping[str, Input]:
        return self._inputs

    @property
    def look_and_feel(self) -> LookAndFeel:
        return self._look_and_feel

    @property
    def window_manager(self) -> WindowManager:
        return self._window_manager

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    def process(self) -> None:
        self.execute_safely(self.process_inputs)
        self.execute_safely(self.process_draw)

    def process_inputs(self) -> None:
        for poller in self._pollers:
            self.execute_safely(poller.process)

    def process_draw(self) -> None:
        if self._graphics is None:
            self._graphics = self.toolkit.create_graphics(self)

        assert self._graphics is not None

        (width, height) = self.window_size.tuple

        self._graphics.reset()
        self._graphics.clip = Some(Bounds(0, 0, width, height))

        self._window_manager.draw(self._graphics)

    def dispatcher_at(self, location: Point) -> Maybe[EventDispatcher]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        return self._window_manager.window_at(location).bind(lambda w: w.component_at(location))

    def dispose(self) -> None:
        super().dispose()

        if self._graphics is not None:
            self.execute_safely(self._graphics.dispose)

        self.execute_safely(self._window_manager.dispose)

        for i in self.inputs.values():
            self.execute_safely(i.dispose)


T = TypeVar("T", bound=Context, covariant=True)


class ContextBuilder(ABC, Generic[T]):

    def __init__(self, toolkit: Toolkit[T]) -> None:
        if toolkit is None:
            raise ValueError("Argument 'toolkit' is required.")

        self.toolkit = toolkit
        self._args: Dict[str, Any] = dict()

    @property
    def args(self) -> Dict[str, Any]:
        return self._args

    def with_resource_path(self, resource_path: Path) -> ContextBuilder:
        if resource_path is None:
            raise ValueError("Argument 'resource_path' is required.")

        self._args["resource_path"] = resource_path

        return self

    def with_window_manager(self, manager: WindowManager) -> ContextBuilder:
        if manager is None:
            raise ValueError("Argument 'manager' is required.")

        self._args["window_manager"] = manager

        return self

    def with_error_handler(self, handler: ErrorHandler) -> ContextBuilder:
        if handler is None:
            raise ValueError("Argument 'handler' is required.")

        self._args["error_handler"] = handler

        return self

    def with_look_and_feel(self, laf: LookAndFeel) -> ContextBuilder:
        if laf is None:
            raise ValueError("Argument 'laf' is required.")

        self._args["look_and_feel"] = laf

        return self

    @abstractmethod
    def create_context(self) -> T:
        pass
