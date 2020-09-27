import unittest

from returns.maybe import Nothing, Some

from alleycat.ui import Bounds, RGBA, Point
from tests.ui import UITestCase


class GraphicsTest(UITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.g = self.context.toolkit.create_graphics(self.context)

    def tearDown(self) -> None:
        super().tearDown()

        self.g.dispose()

    def test_fill_rect(self):
        (width, height) = self.context.window_size

        self.g.color = RGBA(0, 0, 0, 1)
        self.g.fill_rect(Bounds(0, 0, width, height))

        self.g.color = RGBA(1, 0, 0, 1)
        self.g.fill_rect(Bounds(10, 20, 50, 30))

        self.g.color = RGBA(0, 1, 1, 0.3)
        self.g.fill_rect(Bounds(40, 30, 50, 40))

        self.assertImage("fill_rect", self.context)

    def test_offset(self):
        self.g.color = RGBA(1, 0, 0, 1)
        self.g.fill_rect(Bounds(0, 0, 20, 20))

        self.g.offset = Point(10, 10)
        self.g.color = RGBA(0, 1, 0, 1)
        self.g.fill_rect(Bounds(0, 0, 20, 20))

        self.g.offset = Point(20, 20)
        self.g.color = RGBA(0, 0, 1, 1)
        self.g.fill_rect(Bounds(0, 0, 20, 20))

        self.assertImage("offset", self.context)

    def test_clip(self):
        self.assertEqual(Nothing, self.g.clip)

        self.g.clip = Some(Bounds(10, 20, 100, 80))

        self.assertEqual(Bounds(10, 20, 100, 80), self.g.clip.unwrap())

        self.g.offset = Point(20, 10)
        self.assertEqual(Bounds(-10, 10, 100, 80), self.g.clip.unwrap())

        self.g.clip = Some(Bounds(10, 0, 100, 40))
        self.assertEqual(Bounds(10, 10, 80, 30), self.g.clip.unwrap())

        self.g.color = RGBA(1, 0, 0, 1)
        self.g.fill_rect(Bounds(0, 0, 100, 100))

        self.assertImage("clip", self.context)

        self.g.clip = Some(Bounds(100, 100, 100, 40))
        self.assertEqual(Bounds(10, 10, 0, 0), self.g.clip.unwrap())

        self.g.color = RGBA(0, 0, 1, 1)
        self.g.fill_rect(Bounds(0, 0, 100, 100))

        self.assertImage("clip_empty", self.context)

    def test_draw_text(self):
        self.g.offset = Point(10, 10)

        for i in range(10):
            self.g.color = RGBA(1, 0, 0, 0.1 * (i + 1))
            self.g.draw_text("Text", 10 + 2 * i, Point(5 * i, 10 * (i + 1)))

        self.assertImage("draw_text", self.context, tolerance=50)

    def test_draw_text_with_clip(self):
        self.g.clip = Some(Bounds(30, 30, 60, 60))

        for i in range(10):
            self.g.color = RGBA(1, 0, 0, 0.1 * (i + 1))
            self.g.draw_text("Text", 10 + 2 * i, Point(5 * i, 10 * (i + 1)))

        self.assertImage("draw_text_with_clip", self.context, tolerance=50)


if __name__ == '__main__':
    unittest.main()
