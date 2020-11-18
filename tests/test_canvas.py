import unittest
from pathlib import Path

from alleycat.ui import Bounds, Window, RGBA, Insets, \
    Canvas, Dimension
from alleycat.ui.glass import StyleKeys
from tests.ui import UITestCase


# noinspection DuplicatedCode
class CanvasTest(UITestCase):

    def test_style_fallback(self):
        canvas = Canvas(self.context)

        prefixes = list(canvas.style_fallback_prefixes)
        keys = list(canvas.style_fallback_keys(StyleKeys.Background))

        self.assertEqual(["Canvas"], prefixes)
        self.assertEqual(["Canvas.background", "background"], keys)

    def test_draw(self):
        image = self.context.toolkit.images.load(Path("fixtures/cat.png"))

        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 100)

        canvas1 = Canvas(self.context, image, Insets(5, 10, 0, 5))
        canvas1.bounds = Bounds(0, 10, 40, 20)
        canvas1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        canvas2 = Canvas(self.context, image)
        canvas2.bounds = Bounds(30, 40, 80, 30)

        canvas3 = Canvas(self.context)
        canvas3.bounds = Bounds(80, 10, 20, 20)
        canvas3.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

        window.add(canvas1)
        window.add(canvas2)
        window.add(canvas3)

        self.context.process()

        self.assertImage("draw", self.context, tolerance=50)

    def test_draw_with_padding(self):
        image = self.context.toolkit.images.load(Path("fixtures/cat.png"))

        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 100)

        canvas = Canvas(self.context, image)
        canvas.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        window.add(canvas)

        def assert_padding(size: Dimension, padding: Insets):
            (w, h) = size.tuple
            (top, right, bottom, left) = padding.tuple

            canvas.bounds = Bounds(0, 0, w, h)
            canvas.padding = padding

            self.context.process()

            self.assertImage(f"draw_with_padding-{top},{right},{bottom},{left}-{w}x{h}", self.context, tolerance=50)

        assert_padding(Dimension(100, 100), Insets(0, 0, 0, 0))
        assert_padding(Dimension(100, 100), Insets(10, 5, 3, 15))
        assert_padding(Dimension(64, 64), Insets(0, 0, 0, 0))
        assert_padding(Dimension(64, 64), Insets(10, 5, 3, 15))


if __name__ == '__main__':
    unittest.main()
