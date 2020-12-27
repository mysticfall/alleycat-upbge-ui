import unittest

from returns.maybe import Some

from alleycat.ui import Bounds, Dimension, Frame, Insets, Panel, RGBA
from alleycat.ui.glass import StyleKeys
from alleycat.ui.layout import StackLayout
from ui import UITestCase


# noinspection DuplicatedCode
class StackLayoutTest(UITestCase):

    def test_layout(self):
        container = Frame(self.context, StackLayout())
        container.bounds = Bounds(0, 0, 100, 100)

        child1 = Panel(self.context)
        child1.bounds = Bounds(10, 10, 20, 20)
        child1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        child2 = Panel(self.context)
        child2.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))
        child2.preferred_size_override = Some(Dimension(80, 60))

        child3 = Panel(self.context)
        child3.set_color(StyleKeys.Background, RGBA(0, 1, 0, 1))
        child3.preferred_size_override = Some(Dimension(60, 40))

        container.add(child1)
        container.add(child2, fill=False)
        container.add(child3, False)

        self.context.process()

        self.assertImage("stack", self.context)

        child4 = Panel(self.context)
        child4.set_color(StyleKeys.Background, RGBA(0, 1, 1, 1))

        container.add(child4, fill=True)

        self.context.process()

        self.assertImage("stack-fill", self.context)

        container.add(child3, True)

        self.context.process()

        self.assertImage("stack-fill2", self.context)

    def test_layout_with_insets(self):
        layout = StackLayout()
        container = Frame(self.context, layout)
        container.bounds = Bounds(0, 0, 100, 100)

        child1 = Panel(self.context)
        child1.bounds = Bounds(10, 10, 20, 20)
        child1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        child2 = Panel(self.context)
        child2.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))
        child2.preferred_size_override = Some(Dimension(80, 60))

        container.add(child1)
        container.add(child2, fill=False)

        def test(padding: Insets):
            layout.padding = padding

            self.assertEqual(True, container.layout_pending)
            self.context.process()
            self.assertEqual(False, container.layout_pending)

            name = f"stack-{padding.top},{padding.right},{padding.bottom},{padding.left}"

            self.assertImage(name, self.context)

        for p in [Insets(10, 10, 10, 10), Insets(15, 0, 15, 0), Insets(0, 10, 20, 0)]:
            test(p)


if __name__ == '__main__':
    unittest.main()
