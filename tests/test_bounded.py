import unittest

from alleycat.ui import Bounded, Bounds, Point, Dimension
from alleycat.reactive import functions as rv


class BoundedTest(unittest.TestCase):
    class Fixture(Bounded):
        pass

    def setUp(self) -> None:
        self.fixture = self.Fixture()

    def test_bounds(self):
        bounds = []

        rv.observe(self.fixture.bounds).subscribe(bounds.append)

        self.assertEqual(Bounds(0, 0, 0, 0), self.fixture.bounds)
        self.assertEqual([Bounds(0, 0, 0, 0)], bounds)

        self.fixture.bounds = Bounds(-10, 30, 100, 200)

        self.assertEqual(Bounds(-10, 30, 100, 200), self.fixture.bounds)
        self.assertEqual([Bounds(0, 0, 0, 0), Bounds(-10, 30, 100, 200)], bounds)

    def test_location(self):
        locations = []

        rv.observe(self.fixture.location).subscribe(locations.append)

        self.assertEqual(Point(0, 0), self.fixture.location)
        self.assertEqual([Point(0, 0)], locations)

        self.fixture.bounds = Bounds(10, -30, 200, 100)

        self.assertEqual(Point(10, -30), self.fixture.location)
        self.assertEqual([Point(0, 0), Point(10, -30)], locations)

    def test_size(self):
        sizes = []

        rv.observe(self.fixture.size).subscribe(sizes.append)

        self.assertEqual(Dimension(0, 0), self.fixture.size)
        self.assertEqual([Dimension(0, 0)], sizes)

        self.fixture.bounds = Bounds(0, 0, 50, 150)

        self.assertEqual(Dimension(50, 150), self.fixture.size)
        self.assertEqual([Dimension(0, 0), Dimension(50, 150)], sizes)

    def test_x(self):
        points = []

        rv.observe(self.fixture.x).subscribe(points.append)

        self.assertEqual(0, self.fixture.x)
        self.assertEqual([0], points)

        self.fixture.bounds = Bounds(50, 10, 100, 100)

        self.assertEqual(50, self.fixture.x)
        self.assertEqual([0, 50], points)

    def test_y(self):
        points = []

        rv.observe(self.fixture.y).subscribe(points.append)

        self.assertEqual(0, self.fixture.y)
        self.assertEqual([0], points)

        self.fixture.bounds = Bounds(50, 10, 100, 100)

        self.assertEqual(10, self.fixture.y)
        self.assertEqual([0, 10], points)

    def test_width(self):
        widths = []

        rv.observe(self.fixture.width).subscribe(widths.append)

        self.assertEqual(0, self.fixture.width)
        self.assertEqual([0], widths)

        self.fixture.bounds = Bounds(50, 10, 100, 100)

        self.assertEqual(100, self.fixture.width)
        self.assertEqual([0, 100], widths)

    def test_height(self):
        heights = []

        rv.observe(self.fixture.height).subscribe(heights.append)

        self.assertEqual(0, self.fixture.height)
        self.assertEqual([0], heights)

        self.fixture.bounds = Bounds(50, 10, 100, 200)

        self.assertEqual(200, self.fixture.height)
        self.assertEqual([0, 200], heights)


if __name__ == '__main__':
    unittest.main()
