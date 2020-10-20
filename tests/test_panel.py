import unittest

from alleycat.ui import Label, Bounds, Window, Panel, RGBA
from alleycat.ui.glass import StyleKeys
from tests.ui import UITestCase


class PanelTest(UITestCase):

    def test_style_fallback(self):
        label = Label(self.context)

        prefixes = list(label.style_fallback_prefixes)
        keys = list(label.style_fallback_keys(StyleKeys.Background))

        self.assertEqual(["Label"], prefixes)
        self.assertEqual(["Label.background", "background"], keys)

    def test_draw(self):
        self.context.look_and_feel.set_color("Panel.background", RGBA(0, 0, 1, 0.5))

        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 100)

        panel1 = Panel(self.context)
        panel1.bounds = Bounds(20, 20, 40, 60)

        panel2 = Panel(self.context)
        panel2.bounds = Bounds(50, 40, 40, 40)
        panel2.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        window.add(panel1)
        window.add(panel2)

        self.context.process()

        self.assertImage("draw", self.context)


if __name__ == '__main__':
    unittest.main()
