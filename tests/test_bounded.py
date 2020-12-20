import unittest

from alleycat.reactive import functions as rv

from alleycat.ui import Bounded, Bounds, Dimension, Point


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


if __name__ == '__main__':
    unittest.main()
