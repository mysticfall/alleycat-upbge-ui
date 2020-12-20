import unittest
from typing import Sequence

from returns.maybe import Some

from alleycat.ui import Bounds, Dimension, Insets, Panel, RGBA, Window
from alleycat.ui.glass import StyleKeys
from alleycat.ui.layout import BoxAlign, HBoxLayout, \
    VBoxLayout
from tests.ui import UITestCase


# noinspection DuplicatedCode
class BoxLayoutTest(UITestCase):

    def test_hbox_layout(self):
        layout = HBoxLayout()

        container = Window(self.context, layout)
        container.bounds = Bounds(5, 5, 90, 90)

        child1 = Panel(self.context)
        child1.preferred_size_override = Some(Dimension(20, 50))
        child1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        container.add(child1)

        child2 = Panel(self.context)
        child2.preferred_size_override = Some(Dimension(15, 60))
        child2.minimum_size_override = Some(Dimension(15, 60))
        child2.set_color(StyleKeys.Background, RGBA(0, 1, 0, 1))

        container.add(child2)

        child3 = Panel(self.context)
        child3.preferred_size_override = Some(Dimension(30, 40))
        child3.minimum_size_override = Some(Dimension(10, 20))
        child3.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

        container.add(child3)

        def test(spacing: float, padding: Insets, align: BoxAlign):
            container.bounds = Bounds(5, 5, 90, 90)

            layout.spacing = spacing
            layout.padding = padding
            layout.align = align

            self.assertEqual(True, container.layout_pending)
            self.context.process()
            self.assertEqual(False, container.layout_pending)

            prefix = f"hbox-{spacing}-{padding.top},{padding.right},{padding.bottom},{padding.left}-{align.name}-"

            self.assertImage(prefix + "full-size", self.context)

            container.bounds = Bounds(5, 5, 45, 45)

            self.assertEqual(True, container.layout_pending)
            self.context.process()
            self.assertEqual(False, container.layout_pending)

            self.assertImage(prefix + "half-size", self.context)

        for s in [0, 10]:
            for p in [Insets(0, 0, 0, 0), Insets(15, 20, 10, 5)]:
                for a in BoxAlign:
                    test(s, p, a)

    def test_hbox_hide_child(self):
        container = Window(self.context, HBoxLayout())
        container.bounds = Bounds(0, 0, 100, 100)

        child1 = Panel(self.context)
        child1.preferred_size_override = Some(Dimension(20, 50))
        child1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        container.add(child1)

        child2 = Panel(self.context)
        child2.preferred_size_override = Some(Dimension(15, 60))
        child2.minimum_size_override = Some(Dimension(15, 60))
        child2.set_color(StyleKeys.Background, RGBA(0, 1, 0, 1))

        container.add(child2)

        child3 = Panel(self.context)
        child3.preferred_size_override = Some(Dimension(30, 40))
        child3.minimum_size_override = Some(Dimension(10, 20))
        child3.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

        container.add(child3)

        def test(visibility: Sequence[bool]):
            child1.visible = visibility[0]
            child2.visible = visibility[1]
            child3.visible = visibility[2]

            self.assertEqual(True, container.layout_pending)
            self.context.process()
            self.assertEqual(False, container.layout_pending)

            name = f"hbox-visibility-{'-'.join(map(str, visibility))}"

            self.assertImage(name, self.context)

        for v1 in [True, False]:
            for v2 in [True, False]:
                for v3 in [True, False]:
                    test((v1, v2, v3))

    def test_vbox_layout(self):
        layout = VBoxLayout()

        container = Window(self.context, layout)
        container.bounds = Bounds(5, 5, 90, 90)

        child1 = Panel(self.context)
        child1.preferred_size_override = Some(Dimension(50, 20))
        child1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        container.add(child1)

        child2 = Panel(self.context)
        child2.preferred_size_override = Some(Dimension(60, 15))
        child2.minimum_size_override = Some(Dimension(60, 15))
        child2.set_color(StyleKeys.Background, RGBA(0, 1, 0, 1))

        container.add(child2)

        child3 = Panel(self.context)
        child3.preferred_size_override = Some(Dimension(40, 30))
        child3.minimum_size_override = Some(Dimension(20, 10))
        child3.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

        container.add(child3)

        def test(spacing: float, padding: Insets, align: BoxAlign):
            container.bounds = Bounds(5, 5, 90, 90)

            layout.spacing = spacing
            layout.padding = padding
            layout.align = align

            self.assertEqual(True, container.layout_pending)
            self.context.process()
            self.assertEqual(False, container.layout_pending)

            prefix = f"vbox-{spacing}-{padding.top},{padding.right},{padding.bottom},{padding.left}-{align.name}-"

            self.assertImage(prefix + "full-size", self.context)

            container.bounds = Bounds(5, 5, 45, 45)

            self.assertEqual(True, container.layout_pending)
            self.context.process()
            self.assertEqual(False, container.layout_pending)

            self.assertImage(prefix + "half-size", self.context)

        for s in [0, 10]:
            for p in [Insets(0, 0, 0, 0), Insets(15, 20, 10, 5)]:
                for a in BoxAlign:
                    test(s, p, a)

    def test_vbox_hide_child(self):
        container = Window(self.context, VBoxLayout())
        container.bounds = Bounds(0, 0, 100, 100)

        child1 = Panel(self.context)
        child1.preferred_size_override = Some(Dimension(50, 20))
        child1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        container.add(child1)

        child2 = Panel(self.context)
        child2.preferred_size_override = Some(Dimension(60, 15))
        child2.minimum_size_override = Some(Dimension(60, 15))
        child2.set_color(StyleKeys.Background, RGBA(0, 1, 0, 1))

        container.add(child2)

        child3 = Panel(self.context)
        child3.preferred_size_override = Some(Dimension(40, 30))
        child3.minimum_size_override = Some(Dimension(20, 10))
        child3.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

        container.add(child3)

        def test(visibility: Sequence[bool]):
            child1.visible = visibility[0]
            child2.visible = visibility[1]
            child3.visible = visibility[2]

            self.assertEqual(True, container.layout_pending)
            self.context.process()
            self.assertEqual(False, container.layout_pending)

            name = f"vbox-visibility-{'-'.join(map(str, visibility))}"

            self.assertImage(name, self.context)

        for v1 in [True, False]:
            for v2 in [True, False]:
                for v3 in [True, False]:
                    test((v1, v2, v3))


if __name__ == '__main__':
    unittest.main()
