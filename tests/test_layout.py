import unittest

from returns.maybe import Some

from alleycat.ui import Bounds, Dimension, Frame, Panel, RGBA
from alleycat.ui.glass import StyleKeys
from alleycat.ui.layout import Border, BorderLayout, VBoxLayout
from ui import UITestCase


# noinspection DuplicatedCode
class LayoutTest(UITestCase):

    def test_nested_layout(self):
        box = Frame(self.context, VBoxLayout())
        box.bounds = Bounds(0, 0, 100, 100)

        child1 = Panel(self.context)
        child1.preferred_size_override = Some(Dimension(50, 20))
        child1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        box.add(child1)

        child2 = Panel(self.context, BorderLayout())

        top = Panel(self.context)
        top.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))
        top.preferred_size_override = Some(Dimension(0, 20))

        child2.add(top, Border.Top)

        right = Panel(self.context)
        right.set_color(StyleKeys.Background, RGBA(0, 1, 0, 1))
        right.preferred_size_override = Some(Dimension(15, 0))

        child2.add(right, Border.Right)

        bottom = Panel(self.context)
        bottom.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))
        bottom.preferred_size_override = Some(Dimension(0, 15))

        child2.add(bottom, Border.Bottom)

        left = Panel(self.context)
        left.set_color(StyleKeys.Background, RGBA(1, 1, 1, 1))
        left.preferred_size_override = Some(Dimension(5, 0))

        child2.add(left, Border.Left)

        center = Panel(self.context)
        center.set_color(StyleKeys.Background, RGBA(0, 0, 0, 1))
        center.preferred_size_override = Some(Dimension(60, 20))

        child2.add(center, Border.Center)

        box.add(child2)

        child3 = Panel(self.context)
        child3.preferred_size_override = Some(Dimension(40, 20))
        child3.minimum_size_override = Some(Dimension(20, 10))
        child3.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

        box.add(child3)

        self.assertEqual(True, box.layout_pending)
        self.context.process()
        self.assertEqual(False, box.layout_pending)

        self.assertImage("nested_layout", self.context)

        left.minimum_size_override = Some(Dimension(40, 0))
        top.preferred_size_override = Some(Dimension(0, 10))

        self.assertEqual(True, box.layout_pending)
        self.context.process()
        self.assertEqual(False, box.layout_pending)

        self.assertImage("nested_layout_resize_nested_child", self.context)

        bottom.visible = False

        self.assertEqual(True, box.layout_pending)
        self.context.process()
        self.assertEqual(False, box.layout_pending)

        self.assertImage("nested_layout_hide_nested_child", self.context)


if __name__ == '__main__':
    unittest.main()
