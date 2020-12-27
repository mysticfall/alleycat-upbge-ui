import unittest

from returns.maybe import Some

from alleycat.ui import Bounds, Dimension, Frame, Panel, RGBA
from alleycat.ui.glass import StyleKeys
from alleycat.ui.layout import AnchorLayout
from ui import UITestCase


# noinspection DuplicatedCode
class AnchorLayoutTest(UITestCase):

    def test_layout_anchor(self):
        container = Frame(self.context, AnchorLayout())
        container.bounds = Bounds(0, 0, 100, 100)

        child = Panel(self.context)
        child.preferred_size_override = Some(Dimension(20, 10))
        child.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        container.add(child)

        self.context.process()

        self.assertImage("anchor", self.context)


if __name__ == '__main__':
    unittest.main()
