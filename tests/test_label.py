import unittest

from alleycat.ui import Label, Bounds, Window, RGBA, TextAlign
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

        label.text = "Text"
        label.bounds = Bounds(0, 30, 60, 30)

        label2 = Label(self.context)

        label2.text = "AlleyCat"
        label2.text_size = 18
        label2.set_color(ColorKeys.Text, RGBA(1, 0, 0, 1))
        label2.bounds = Bounds(20, 0, 80, 60)

        window.add(label)
        window.add(label2)

        self.context.process()

        self.assertImage("draw", self.context)

    def test_align(self):
        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 100)

        label = Label(self.context)

        label.text = "AlleyCat"
        label.text_size = 18
        label.bounds = Bounds(0, 0, 100, 100)

        window.add(label)

        self.context.process()
        self.assertImage("align_default", self.context)

        for align in TextAlign:
            for vertical_align in TextAlign:
                label.text_align = align
                label.text_vertical_align = vertical_align

                test_name = f"align_{align}_{vertical_align}".replace("TextAlign.", "")

                self.context.process()
                self.assertImage(test_name, self.context)


if __name__ == '__main__':
    unittest.main()
