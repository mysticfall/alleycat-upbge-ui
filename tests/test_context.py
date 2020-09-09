import unittest
from typing import Sequence

from cairo import ImageSurface, Format

from alleycat.ui import Context, Input, FakeMouseInput, MouseInput
from alleycat.ui.cairo import CairoToolkit, CairoContext


class ContextTest(unittest.TestCase):
    def test_inputs(self):
        class TestMouseInput(FakeMouseInput):
            pass

        class TestToolkit(CairoToolkit):

            def create_inputs(self, ctx: Context) -> Sequence[Input]:
                return TestMouseInput(ctx),

        toolkit = TestToolkit()
        context = CairoContext(toolkit, ImageSurface(Format.ARGB32, 10, 10))

        mouse_input = MouseInput.input(context)

        self.assertIsNotNone(mouse_input)
        self.assertIs(TestMouseInput, type(mouse_input))


if __name__ == '__main__':
    unittest.main()
