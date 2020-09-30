import unittest

from alleycat.ui import Label, Bounds, Window, Panel, RGBA
from alleycat.ui.cairo import UI
from alleycat.ui.glass import ColorKeys
from tests.ui import UITestCase


class PanelTest(UITestCase):

    def test_style_fallback(self):
        label = Label(self.context)

        prefixes = list(label.style_fallback_prefixes)
        keys = list(label.style_fallback_keys(ColorKeys.Background))

        self.assertEqual(["Label"], prefixes)
        self.assertEqual(["Label.background", "background"], keys)

    def test_draw(self):
        context = UI().create_context()
        context.look_and_feel.set_color("Panel.background", RGBA(0, 0, 1, 0.5))

        window = Window(context)
        window.bounds = Bounds(0, 0, 100, 100)

        panel1 = Panel(context)
        panel1.bounds = Bounds(20, 20, 40, 60)

        panel2 = Panel(context)
        panel2.bounds = Bounds(50, 40, 40, 40)
        panel2.set_color(ColorKeys.Background, RGBA(1, 0, 0, 1))

        window.add(panel1)
        window.add(panel2)

        context.process()

        self.assertImage("draw", context)


if __name__ == '__main__':
    unittest.main()
