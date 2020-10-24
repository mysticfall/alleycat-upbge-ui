import unittest

from returns.maybe import Some

from alleycat.ui import Bounds, Dimension, Panel, Window, Insets
from alleycat.ui.layout import AbsoluteLayout, FillLayout
from tests.ui import UITestCase


# noinspection DuplicatedCode
class LayoutTest(UITestCase):

    def test_absolute_layout(self):
        container = Window(self.context, AbsoluteLayout())
        container.bounds = Bounds(30, 30, 200, 200)

        child1 = Panel(self.context)
        child1.bounds = Bounds(10, 10, 20, 20)

        child2 = Panel(self.context)
        child2.bounds = Bounds(50, 60, 20, 20)

        container.add(child1)
        container.add(child2)

        self.context.process()

        self.assertEqual(Bounds(10, 10, 20, 20), child1.bounds)
        self.assertEqual(Bounds(50, 60, 20, 20), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

        container.bounds = Bounds(20, 20, 100, 100)
        child1.minimum_size = Some(Dimension(400, 400))
        child2.bounds = Bounds(-30, -40, 50, 50)

        self.context.process()

        self.assertEqual(Bounds(10, 10, 400, 400), child1.bounds)
        self.assertEqual(Bounds(-30, -40, 50, 50), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

    def test_fill_layout(self):
        container = Window(self.context, FillLayout())
        container.bounds = Bounds(30, 30, 200, 200)

        child1 = Panel(self.context)
        child1.bounds = Bounds(10, 10, 20, 20)

        child2 = Panel(self.context)
        child2.bounds = Bounds(50, 60, 20, 20)

        container.add(child1)
        container.add(child2)

        self.context.process()

        self.assertEqual(Bounds(0, 0, 200, 200), child1.bounds)
        self.assertEqual(Bounds(0, 0, 200, 200), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

        container.bounds = Bounds(20, 20, 100, 100)

        self.context.process()

        self.assertEqual(Bounds(0, 0, 100, 100), child1.bounds)
        self.assertEqual(Bounds(0, 0, 100, 100), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

        child1.bounds = Bounds(10, 60, 300, 300)
        child2.bounds = Bounds(-30, -40, 50, 50)

        self.context.process()

        self.assertEqual(Bounds(0, 0, 100, 100), child1.bounds)
        self.assertEqual(Bounds(0, 0, 100, 100), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.effective_minimum_size)

        child1.minimum_size = Some(Dimension(200, 300))
        child2.minimum_size = Some(Dimension(500, 150))

        child1.preferred_size = Some(Dimension(300, 450))
        child2.preferred_size = Some(Dimension(640, 400))

        self.context.process()

        self.assertEqual(Bounds(0, 0, 500, 300), child1.bounds)
        self.assertEqual(Bounds(0, 0, 500, 300), child2.bounds)
        self.assertEqual(Bounds(20, 20, 500, 300), container.bounds)
        self.assertEqual(Dimension(500, 300), container.effective_minimum_size)
        self.assertEqual(Dimension(640, 450), container.effective_preferred_size)

    def test_fill_layout_insets(self):
        layout = FillLayout(Insets(10, 5, 3, 6))
        container = Window(self.context, layout)
        container.bounds = Bounds(30, 30, 200, 200)

        child = Panel(self.context)

        container.add(child)

        self.context.process()

        self.assertEqual(Bounds(10, 6, 189, 187), child.bounds)
        self.assertEqual(Dimension(11, 13), container.effective_minimum_size)
        self.assertEqual(Dimension(11, 13), container.effective_preferred_size)

        child.minimum_size = Some(Dimension(10, 10))

        self.context.process()

        self.assertEqual(Bounds(10, 6, 189, 187), child.bounds)
        self.assertEqual(Dimension(21, 23), container.effective_minimum_size)
        self.assertEqual(Dimension(21, 23), container.effective_preferred_size)

        layout.padding = Insets(5, 5, 5, 5)

        self.context.process()

        self.assertEqual(Bounds(5, 5, 190, 190), child.bounds)
        self.assertEqual(Dimension(20, 20), container.effective_minimum_size)
        self.assertEqual(Dimension(20, 20), container.effective_preferred_size)


if __name__ == '__main__':
    unittest.main()
