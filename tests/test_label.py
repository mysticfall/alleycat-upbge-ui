import unittest

from alleycat.ui import Label, Bounds, Window, RGBA
from alleycat.ui.glass import ColorKeys
from tests.ui import UITestCase


class LabelTest(UITestCase):

    def test_style_fallback(self):
        label = Label(self.context)

        prefixes = list(label.style_fallback_prefixes)
        keys = list(label.style_fallback_keys(ColorKeys.Background))

        self.assertEqual(["Label"], prefixes)
        self.assertEqual(["Label.background", "background"], keys)

    def test_draw(self):
        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 60)

        label = Label(self.context)

        label.text = "Label"
        label.bounds = Bounds(10, 20, 60, 30)

        label2 = Label(self.context)

        label2.text = "Test"
        label2.size = 20
        label2.set_color(ColorKeys.Text, RGBA(1, 0, 0, 1))
        label2.bounds = Bounds(0, 0, 80, 60)

        window.add(label)
        window.add(label2)

        self.context.process()

        self.assertImage("draw", self.context)


if __name__ == '__main__':
    unittest.main()
