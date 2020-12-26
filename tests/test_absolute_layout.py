import unittest

from returns.maybe import Some

from alleycat.ui import Bounds, Dimension, Frame, Panel
from alleycat.ui.layout import AbsoluteLayout
from ui import UITestCase


# noinspection DuplicatedCode
class AbsoluteLayoutTest(UITestCase):

    def test_layout(self):
        container = Frame(self.context, AbsoluteLayout())
        container.bounds = Bounds(30, 30, 200, 200)

        child1 = Panel(self.context)
        child1.bounds = Bounds(10, 10, 20, 20)

        child2 = Panel(self.context)
        child2.bounds = Bounds(50, 60, 20, 20)

        container.add(child1)
        container.add(child2)

        self.assertEqual(False, container.valid)
        self.context.process()
        self.assertEqual(True, container.valid)

        self.assertEqual(Bounds(10, 10, 20, 20), child1.bounds)
        self.assertEqual(Bounds(50, 60, 20, 20), child2.bounds)

        self.assertEqual(Dimension(0, 0), container.minimum_size)
        self.assertEqual(Dimension(0, 0), container.preferred_size)

        container.bounds = Bounds(20, 20, 100, 100)

        child1.minimum_size_override = Some(Dimension(400, 400))
        child2.bounds = Bounds(-30, -40, 50, 50)

        self.assertEqual(False, container.valid)
        self.context.process()
        self.assertEqual(True, container.valid)

        self.assertEqual(Bounds(10, 10, 400, 400), child1.bounds)
        self.assertEqual(Bounds(-30, -40, 50, 50), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.minimum_size)


if __name__ == '__main__':
    unittest.main()
