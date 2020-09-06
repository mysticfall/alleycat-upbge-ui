from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Mapping, cast, TYPE_CHECKING, Final

from alleycat.reactive import RV, RP
from alleycat.reactive import functions as rv
from rx.disposable import Disposable

from alleycat.ui import Point, MouseMoveEvent

if TYPE_CHECKING:
    from alleycat.ui import Context


class Input(Disposable, ABC):

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


class InputLookup(ABC):

    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def inputs(self) -> Mapping[str, Input]:
        pass

    @property
    def mouse_input(self) -> MouseInput:
        try:
            return cast(MouseInput, self.inputs[MouseInput.ID])
        except KeyError:
            raise NotImplemented("Mouse input is not supported in this backend.")


class MouseInput(Input, ABC):
    ID: Final = "mouse"

    position: RV[Point]

    def __init__(self, context: Context):
        super().__init__(context)

        def dispatch_mouse_move(pos: Point):
            event = MouseMoveEvent(self.context, pos)
            self.context.dispatch_event(event)

        rv.observe(self, "position").subscribe(dispatch_mouse_move)

    def id(self) -> str:
        return self.ID

    def dispatch(self, location: Point) -> None:
        window = self.context.window_manager.window_at(location)
        component = window.bind(lambda w: w.component_at(location))

        event = component.map(lambda c: MouseMoveEvent(c, location))
        print(event)


class FakeMouseInput(MouseInput):
    _position: RP[Point] = rv.new_property()

    position: RV[Point] = _position.as_view()

    def __init__(self, context: Context):
        super().__init__(context)

    def move_to(self, location: Point) -> None:
        if location is None:
            raise ValueError("Argument 'location' is required.")

        # noinspection PyTypeChecker
        self._position = location
