import unittest
from typing import Sequence

from alleycat.ui import Context, Dimension, FakeMouseInput, Input, MouseInput
from ui import TestContext, TestToolkit


class ContextTest(unittest.TestCase):
    def test_inputs(self):
        class TestMouseInput(FakeMouseInput):
            pass

        class ToolkitFixture(TestToolkit):

            def create_inputs(self, ctx: Context) -> Sequence[Input]:
                return TestMouseInput(ctx),

        toolkit = ToolkitFixture()
        context = TestContext(Dimension(10, 10), toolkit)

        mouse_input = MouseInput.input(context)

        self.assertIsNotNone(mouse_input)
        self.assertIs(TestMouseInput, type(mouse_input))


if __name__ == '__main__':
    unittest.main()
