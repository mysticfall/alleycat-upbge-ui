import unittest

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


if __name__ == '__main__':
    unittest.main()