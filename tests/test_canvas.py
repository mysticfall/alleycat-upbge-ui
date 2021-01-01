import unittest
from pathlib import Path

from returns.maybe import Some

from alleycat.ui import Bounds, Canvas, Dimension, Frame, Insets, RGBA, StyleLookup
from alleycat.ui.glass import StyleKeys
from ui import UITestCase

Tolerance: float = 3

FixturePath: str = str(Path(__file__).parent.joinpath("fixtures/cat.png"))


# noinspection DuplicatedCode
class CanvasTest(UITestCase):

    def test_style_fallback(self):
        canvas = Canvas(self.context)

        prefixes = list(canvas.style_fallback_prefixes)
        keys = list(canvas.style_fallback_keys(StyleKeys.Background))

        self.assertEqual(["Canvas"], prefixes)
        self.assertEqual(["Canvas.background", "background"], keys)

    def test_validation(self):
        canvas = Canvas(self.context)
        canvas.validate()

        self.assertEqual(True, canvas.valid)

        image = self.context.toolkit.images[FixturePath]

        canvas.image = Some(image)

        self.assertEqual(False, canvas.valid)

        canvas.validate()

        self.assertEqual(True, canvas.valid)

        def test_style(lookup: StyleLookup):
            canvas.validate()

            lookup.set_insets("NonExistentKey", Insets(10, 10, 10, 10))

            self.assertEqual(True, canvas.valid)

            canvas.validate()
            lookup.set_insets(StyleKeys.Padding, Insets(10, 10, 10, 10))

            self.assertEqual(False, canvas.valid)

        test_style(self.context.look_and_feel)
        test_style(canvas)

    def test_draw(self):
        image = self.context.toolkit.images[FixturePath]

        window = Frame(self.context)
        window.bounds = Bounds(0, 0, 100, 100)

        canvas1 = Canvas(self.context)
        canvas1.bounds = Bounds(30, 40, 80, 30)
        canvas1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        canvas2 = Canvas(self.context, image)
        canvas2.bounds = Bounds(0, 10, 64, 64)

        canvas3 = Canvas(self.context, image)
        canvas3.bounds = Bounds(10, 70, 80, 20)
        canvas3.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

        window.add(canvas1)
        window.add(canvas2)
        window.add(canvas3)

        self.context.process()

        self.assertImage("draw", self.context, tolerance=Tolerance)

    def test_draw_with_padding(self):
        image = self.context.toolkit.images[FixturePath]

        window = Frame(self.context)
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

            self.assertImage(
                f"draw_with_padding-{top},{right},{bottom},{left}-{w}x{h}", self.context, tolerance=Tolerance)

        assert_padding(Dimension(100, 100), Insets(0, 0, 0, 0))
        assert_padding(Dimension(100, 100), Insets(10, 5, 3, 15))
        assert_padding(Dimension(64, 64), Insets(0, 0, 0, 0))
        assert_padding(Dimension(64, 64), Insets(10, 5, 3, 15))


if __name__ == '__main__':
    unittest.main()
