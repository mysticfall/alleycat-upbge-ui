from __future__ import annotations

from abc import ABC
from enum import Enum
from itertools import chain
from typing import Mapping, Set, cast

from alleycat.reactive import RV
from rx import Observable, operators as ops

from alleycat.ui import Context, Input, InputLookup


class KeyState(Enum):
    Released = 0
    Pressed = 1
    Hold = 2


class KeyInput(Input, ABC):
    ID: str = "key"

    pressed: RV[Set[int]]

    def __init__(self, context: Context):
        super().__init__(context)

        def to_state(previous: Set[int], current: Set[int]) -> Mapping[int, KeyState]:
            hold = map(lambda k: (k, KeyState.Hold), current.intersection(previous))
            pressed = map(lambda k: (k, KeyState.Pressed), current.difference(previous))
            released = map(lambda k: (k, KeyState.Released), previous.difference(current))

            return dict(chain(hold, pressed, released))

        self._states = self.observe("pressed").pipe(
            ops.start_with(set()),
            ops.pairwise(),
            ops.map(lambda s: to_state(s[0], s[1])),
            ops.share())

    @property
    def id(self) -> str:
        return self.ID

    @staticmethod
    def input(lookup: InputLookup) -> KeyInput:
        if lookup is None:
            raise ValueError("Argument 'lookup' is required.")

        try:
            return cast(KeyInput, lookup.inputs[KeyInput.ID])
        except KeyError:
            raise NotImplementedError("Keyboard input is not supported in this backend.")

    def on_key_state_change(self, key_code: int) -> Observable:
        return self._states.pipe(ops.filter(lambda s: key_code in s), ops.map(lambda s: s[key_code]))

    def on_key_press(self, key_code: int) -> Observable:
        return self.on_key_state_change(key_code).pipe(
            ops.filter(lambda s: s == KeyState.Pressed),
            ops.map(lambda _: key_code))

    def on_key_release(self, key_code: int) -> Observable:
        return self.on_key_state_change(key_code).pipe(
            ops.filter(lambda s: s == KeyState.Released),
            ops.map(lambda _: key_code))
