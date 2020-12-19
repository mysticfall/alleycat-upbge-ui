import unittest

from returns.maybe import Some

from alleycat.ui import Bounds, Dimension, Insets, Panel, RGBA, Window
from alleycat.ui.glass import StyleKeys
from alleycat.ui.layout import FillLayout
from tests.ui import UITestCase


# noinspection DuplicatedCode
class FillLayoutTest(UITestCase):

    def test_layout(self):
        container = Window(self.context, FillLayout())
        container.bounds = Bounds(30, 30, 200, 200)

        child1 = Panel(self.context)
        child1.bounds = Bounds(10, 10, 20, 20)

        child2 = Panel(self.context)
        child2.bounds = Bounds(50, 60, 20, 20)

        container.add(child1)
        container.add(child2)

        self.context.process()

        self.assertEqual(True, container.valid)
        self.assertEqual(False, container.layout_pending)

        self.assertEqual(Bounds(0, 0, 200, 200), child1.bounds)
        self.assertEqual(Bounds(0, 0, 200, 200), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.minimum_size)

        container.bounds = Bounds(20, 20, 100, 100)

        self.assertEqual(True, container.layout_pending)
        self.context.process()
        self.assertEqual(False, container.layout_pending)

        self.assertEqual(Bounds(0, 0, 100, 100), child1.bounds)
        self.assertEqual(Bounds(0, 0, 100, 100), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.minimum_size)

        child1.bounds = Bounds(10, 60, 300, 300)
        child2.bounds = Bounds(-30, -40, 50, 50)

        self.assertEqual(True, container.layout_pending)
        self.context.process()
        self.assertEqual(False, container.layout_pending)

        self.assertEqual(Bounds(0, 0, 100, 100), child1.bounds)
        self.assertEqual(Bounds(0, 0, 100, 100), child2.bounds)
        self.assertEqual(Dimension(0, 0), container.minimum_size)

        child1.minimum_size_override = Some(Dimension(200, 300))
        child2.minimum_size_override = Some(Dimension(500, 150))

        child1.preferred_size_override = Some(Dimension(300, 450))
        child2.preferred_size_override = Some(Dimension(640, 400))

        self.assertEqual(True, container.layout_pending)
        self.context.process()
        self.assertEqual(False, container.layout_pending)

        self.assertEqual(Bounds(0, 0, 500, 300), child1.bounds)
        self.assertEqual(Bounds(0, 0, 500, 300), child2.bounds)
        self.assertEqual(Bounds(20, 20, 500, 300), container.bounds)
        self.assertEqual(Dimension(500, 300), container.minimum_size)
        self.assertEqual(Dimension(640, 450), container.preferred_size)

        child1.visible = False

        self.assertEqual(True, container.layout_pending)
        self.context.process()
        self.assertEqual(False, container.layout_pending)

        self.assertEqual(Bounds(20, 20, 500, 150), container.bounds)
        self.assertEqual(Dimension(500, 150), container.minimum_size)
        self.assertEqual(Dimension(640, 400), container.preferred_size)

    def test_layout_with_insets(self):
        layout = FillLayout(Insets(30, 15, 20, 40))
        container = Window(self.context, layout)
        container.bounds = Bounds(0, 0, 100, 100)

        child = Panel(self.context)
        child.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        container.add(child)

        self.assertEqual(True, container.layout_pending)
        self.context.process()
        self.assertEqual(False, container.layout_pending)

        self.assertImage("fill-30,15,20,40", self.context)

        def test(padding: Insets):
            layout.padding = padding

            self.assertEqual(True, container.layout_pending)
            self.context.process()
            self.assertEqual(False, container.layout_pending)

            name = f"fill-{padding.top},{padding.right},{padding.bottom},{padding.left}"

            self.assertImage(name, self.context)

        for p in [Insets(5, 5, 5, 5), Insets(15, 20, 40, 5), Insets(0, 10, 50, 60)]:
            test(p)


if __name__ == '__main__':
    unittest.main()
