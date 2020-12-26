from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, Mapping, Optional, TYPE_CHECKING, TypeVar

from alleycat.reactive import RV, ReactiveObject, functions as rv
from cairocffi import ANTIALIAS_BEST, ANTIALIAS_SUBPIXEL, Context as Graphics, FontOptions, HINT_STYLE_FULL, \
    OPERATOR_CLEAR, Surface
from returns.maybe import Maybe
from rx import operators as ops

from alleycat.ui import Dimension, ErrorHandler, ErrorHandlerSupport, EventDispatcher, EventLoopAware, Input, \
    InputLookup, Point

if TYPE_CHECKING:
    from alleycat.ui import LookAndFeel, Toolkit, WindowManager


class Context(EventLoopAware, ReactiveObject, InputLookup, ErrorHandlerSupport, ABC):
    window_size: RV[Dimension]

    surface: RV[Surface] = rv.new_view()

    graphics: RV[Graphics] = surface.map(lambda c, s: c.create_graphics(s))

    def __init__(self,
                 toolkit: Toolkit,
                 look_and_feel: Optional[LookAndFeel] = None,
                 font_options: Optional[FontOptions] = None,
                 window_manager: Optional[WindowManager] = None,
                 error_handler: Optional[ErrorHandler] = None) -> None:
        if toolkit is None:
            raise ValueError("Argument 'toolkit' is required.")

        super().__init__()

        from alleycat.ui import WindowManager
        from alleycat.ui.glass import GlassLookAndFeel

        self._toolkit = toolkit

        self._look_and_feel = Maybe.from_optional(look_and_feel).or_else_call(lambda: GlassLookAndFeel(toolkit))
        self._font_options = Maybe.from_optional(font_options).or_else_call(
            lambda: FontOptions(antialias=ANTIALIAS_SUBPIXEL, hint_style=HINT_STYLE_FULL))

        self._error_handler = Maybe.from_optional(error_handler).value_or(toolkit.error_handler)

        self._window_manager = Maybe.from_optional(window_manager) \
            .or_else_call(lambda: WindowManager(self.error_handler))

        inputs = toolkit.create_inputs(self)

        assert inputs is not None

        self._inputs = {i.id: i for i in inputs}
        self._pollers = [i for i in inputs if isinstance(i, EventLoopAware)]

        # noinspection PyTypeChecker
        self.surface = self.observe("window_size").pipe(ops.map(self.toolkit.create_surface))

        old_surface = self.observe("surface").pipe(
            ops.pairwise(),
            ops.map(lambda s: s[0]),
            ops.take_until(self.on_dispose))

        old_surface.subscribe(Surface.finish, on_error=self.error_handler)

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
    def font_options(self) -> FontOptions:
        return self._font_options

    @property
    def window_manager(self) -> WindowManager:
        return self._window_manager

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    # noinspection PyMethodMayBeStatic
    def create_graphics(self, surface: Surface):
        if surface is None:
            raise ValueError("Argument 'surface' is required.")

        g = Graphics(surface)

        g.set_antialias(ANTIALIAS_BEST)
        g.set_font_options(self.font_options)

        return g

    def process(self) -> None:
        self.execute_safely(self.process_inputs)
        self.execute_safely(self.process_draw)

    def process_inputs(self) -> None:
        for poller in self._pollers:
            self.execute_safely(poller.process)

    def process_draw(self) -> None:
        (width, height) = self.window_size.tuple

        g: Graphics = self.graphics

        op = g.get_operator()

        g.rectangle(0, 0, width, height)
        g.set_source_rgba(0, 0, 0, 0)
        g.set_operator(OPERATOR_CLEAR)
        g.fill()

        g.set_operator(op)

        self.window_manager.draw(g)

        self.surface.flush()

    def dispatcher_at(self, location: Point) -> Maybe[EventDispatcher]:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        return self._window_manager.window_at(location).bind(lambda w: w.component_at(location))

    def dispose(self) -> None:
        super().dispose()

        self.execute_safely(self._window_manager.dispose)

        for i in self.inputs.values():
            self.execute_safely(i.dispose)


T = TypeVar("T", bound=Context, covariant=True)


class ContextBuilder(ABC, Generic[T]):

    def __init__(self, toolkit: Toolkit[T]) -> None:
        if toolkit is None:
            raise ValueError("Argument 'toolkit' is required.")

        self._args: Dict[str, Any] = dict({"toolkit": toolkit})

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

    def with_font_options(self, options: FontOptions) -> ContextBuilder:
        if options is None:
            raise ValueError("Argument 'options' is required.")

        self._args["font_options"] = options

        return self

    @abstractmethod
    def create_context(self) -> T:
        pass
