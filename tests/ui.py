import unittest
from abc import ABC
from pathlib import Path
from typing import Optional, cast

from cairo import ImageSurface

from alleycat.ui import MouseInput, FakeMouseInput
from alleycat.ui.cairo import CairoContext, UI


class UITestCase(unittest.TestCase, ABC):
    def __init__(self, name: str, fixture_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        super().__init__(name)

        self.fixture_dir = fixture_dir if fixture_dir is not None else Path("fixtures", self.__module__)
        self.output_dir = output_dir if output_dir is not None else Path("output", self.__module__)

    def setUp(self) -> None:
        super().setUp()

        self.context = UI().create_context()
        self.mouse = cast(FakeMouseInput, MouseInput.input(self.context))

    def tearDown(self) -> None:
        super().tearDown()

        self.context.dispose()

    def assertImage(self, name: str, context: CairoContext, tolerance: int = 0):
        if name is None:
            raise ValueError("Argument 'name' is required.")

        if context is None:
            raise ValueError("Argument 'context' is required.")

        if tolerance < 0:
            raise ValueError("Argument 'tolerance' should be zero or a positive number.")

        surface = context.surface

        fixture_path = self.fixture_dir / (name + ".png")

        if not fixture_path.exists():
            fixture_path.parent.mkdir(parents=True, exist_ok=True)

            surface.write_to_png(fixture_path)

        fixture = ImageSurface.create_from_png(fixture_path).get_data()

        # noinspection PyTypeChecker
        target = surface.map_to_image(None).get_data()

        size = len(fixture)

        self.assertEqual(size, len(target))

        try:
            for f, t in iter(zip(fixture, target)):
                self.assertAlmostEqual(f, t, delta=tolerance)
        except AssertionError as e:
            output_path = self.output_dir / (name + ".png")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            surface.write_to_png(output_path)

            raise e
