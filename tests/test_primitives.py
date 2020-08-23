import unittest

from alleycat.ui import Point, Dimension, Bounds, RGBA


class PrimitivesTest(unittest.TestCase):
    def test_point_init(self):
        point = Point(10.5, -20.2)

        self.assertEqual(10.5, point.x)
        self.assertEqual(-20.2, point.y)

    def test_point_operations(self):
        self.assertEqual(Point(-5, 8), Point(-10, 6) + Point(5, 2))
        self.assertEqual(Point(4., -2.5), Point(6.3, 0) - Point(2.3, 2.5))
        self.assertEqual(Point(-6, -10), Point(3, 5) * -2)
        self.assertEqual(Point(5.2, -1.5), Point(10.4, -3) / 2)

        self.assertEqual(Point(-3, 6), -Point(3, -6))

    def test_point_to_tuple(self):
        self.assertEqual((3, 2), Point(3, 2).tuple)

    def test_point_from_tuple(self):
        self.assertEqual(Point(3, 2), Point.from_tuple((3, 2)))

    def test_point_copy(self):
        self.assertEqual(Point(3, 2), Point(1, 5).copy(x=3, y=2))
        self.assertEqual(Point(3, 5), Point(1, 5).copy(x=3))
        self.assertEqual(Point(1, 2), Point(1, 5).copy(y=2))
        self.assertEqual(Point(1, 5), Point(1, 5).copy())

    def test_dimension_init(self):
        self.assertEqual(120, Dimension(120, 0).width)
        self.assertEqual(30.5, Dimension(0, 30.5).height)

        with self.assertRaises(ValueError) as cm_width:
            Dimension(-10, 30)

        self.assertEqual("Argument 'width' must be zero or a positive number.", cm_width.exception.args[0])

        with self.assertRaises(ValueError) as cm_height:
            Dimension(30, -10)

        self.assertEqual("Argument 'height' must be zero or a positive number.", cm_height.exception.args[0])

    def test_dimension_to_tuple(self):
        self.assertEqual((30, 20), Dimension(30, 20).tuple)

    def test_dimension_from_tuple(self):
        self.assertEqual(Dimension(30, 0), Dimension.from_tuple((30, 0)))

    def test_dimension_copy(self):
        self.assertEqual(Dimension(30, 20), Dimension(10, 50).copy(width=30, height=20))
        self.assertEqual(Dimension(30, 50), Dimension(10, 50).copy(width=30))
        self.assertEqual(Dimension(10, 20), Dimension(10, 50).copy(height=20))
        self.assertEqual(Dimension(10, 50), Dimension(10, 50).copy())

    def test_dimension_operations(self):
        self.assertEqual(Dimension(15, 8), Dimension(10, 6) + Dimension(5, 2))
        self.assertEqual(Dimension(4, 2.5), Dimension(6.3, 5) - Dimension(2.3, 2.5))
        self.assertEqual(Dimension(0, 2.5), Dimension(2.3, 5) - Dimension(6.3, 2.5))
        self.assertEqual(Dimension(4, 0), Dimension(6.3, 2.5) - Dimension(2.3, 5))
        self.assertEqual(Dimension(6, 10), Dimension(3, 5) * 2)
        self.assertEqual(Dimension(5.2, 1.5), Dimension(10.4, 3) / 2)

    def test_bounds_init(self):
        self.assertEqual(-5, Bounds(-5, 10, 120, 0).x)
        self.assertEqual(-30, Bounds(15, -30, 0, 30.5).y)
        self.assertEqual(120, Bounds(-5, 10, 120, 0).width)
        self.assertEqual(30.5, Bounds(15, -30, 0, 30.5).height)

        with self.assertRaises(ValueError) as cm_width:
            Bounds(10, 0, -10, 30)

        self.assertEqual("Argument 'width' must be zero or a positive number.", cm_width.exception.args[0])

        with self.assertRaises(ValueError) as cm_height:
            Bounds(-20, 30, 30, -10)

        self.assertEqual("Argument 'height' must be zero or a positive number.", cm_height.exception.args[0])

    def test_bounds_to_tuple(self):
        self.assertEqual((30, 20, 100, 200), Bounds(30, 20, 100, 200).tuple)

    def test_bounds_from_tuple(self):
        self.assertEqual(Bounds(30, 0, 50, 40), Bounds.from_tuple((30, 0, 50, 40)))

    def test_bounds_copy(self):
        self.assertEqual(Bounds(-20, 20, 30, 30), Bounds(-20, 10, 80, 30).copy(y=20, width=30))
        self.assertEqual(Bounds(10, 10, 80, 100), Bounds(-20, 10, 80, 30).copy(x=10, height=100))
        self.assertEqual(Bounds(0, 0, 20, 40), Bounds(-20, 10, 80, 30).copy(x=0, y=0, width=20, height=40))
        self.assertEqual(Bounds(-20, 10, 80, 30), Bounds(-20, 10, 80, 30).copy())

    def test_bounds_operations(self):
        self.assertEqual(Bounds(0, 0, 100, 200), Bounds(0, 0, 100, 200) + Point(20, 30))
        self.assertEqual(Bounds(0, 0, 100, 230), Bounds(0, 0, 100, 200) + Point(80, 230))
        self.assertEqual(Bounds(0, 0, 120, 230), Bounds(0, 0, 100, 200) + Point(120, 230))
        self.assertEqual(Bounds(-20, 0, 120, 200), Bounds(0, 0, 100, 200) + Point(-20, 30))
        self.assertEqual(Bounds(-20, -30, 120, 230), Bounds(0, 0, 100, 200) + Point(-20, -30))

        self.assertEqual(Bounds(0, 0, 50, 40), Bounds(0, 0, 30, 30) + Bounds(20, 10, 30, 30))
        self.assertEqual(Bounds(-10, -20, 50, 30), Bounds(0, 0, 30, 30) + Bounds(-10, -20, 50, 30))
        self.assertEqual(Bounds(0, 0, 30, 30), Bounds(0, 0, 30, 30) + Bounds(10, 10, 20, 10))

        self.assertEqual(Bounds(20, 40, 200, 400), Bounds(20, 40, 100, 200) * 2)
        self.assertEqual(Bounds(20, 40, 100, 200), Bounds(20, 40, 200, 400) / 2)

    def test_bounds_location(self):
        self.assertEqual(Point(10, 20), Bounds(10, 20, 100, 200).location)

    def test_bounds_size(self):
        self.assertEqual(Dimension(100, 200), Bounds(10, 20, 100, 200).size)

    def test_bounds_points(self):
        points = (Point(-10, 20), Point(70, 20), Point(70, 60), Point(-10, 60))

        self.assertEqual(points, Bounds(-10, 20, 80, 40).points)

    def test_rgba_init(self):
        self.assertEqual(0.5, RGBA(0.5, 0.12, 0.2, 1).r)
        self.assertEqual(0.12, RGBA(0.5, 0.12, 0.2, 1).g)
        self.assertEqual(0.2, RGBA(0.5, 0.12, 0.2, 1).b)
        self.assertEqual(1, RGBA(0.5, 0.12, 0.2, 1).a)

        base = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 0.5}

        for attr in ["r", "g", "b", "a"]:
            for value in [-0.1, 1.1]:
                args = base.copy()
                args[attr] = value

                with self.assertRaises(ValueError) as cm:
                    RGBA(**args)

                self.assertEqual(f"Argument '{attr}' must be between 0 and 1.", cm.exception.args[0])

    def test_rgba_to_tuple(self):
        self.assertEqual((0.1, 0.2, 0.8, 1.0), RGBA(0.1, 0.2, 0.8, 1.0).tuple)

    def test_rgba_from_tuple(self):
        self.assertEqual(RGBA(0.1, 0.2, 0.8, 1.0), RGBA.from_tuple((0.1, 0.2, 0.8, 1.0)))

    def test_rgba_copy(self):
        self.assertEqual(RGBA(0.4, 0.2, 0.8, 0.3), RGBA(0.1, 0.2, 0.8, 1.0).copy(r=0.4, a=0.3))
        self.assertEqual(RGBA(0.1, 0.5, 0.1, 1.0), RGBA(0.1, 0.2, 0.8, 1.0).copy(g=0.5, b=0.1))
        self.assertEqual(RGBA(0.3, 0.1, 0.4, 0.4), RGBA(0.1, 0.2, 0.8, 1.0).copy(r=0.3, g=0.1, b=0.4, a=0.4))
        self.assertEqual(RGBA(0.1, 0.2, 0.8, 1.0), RGBA(0.1, 0.2, 0.8, 1.0).copy())


if __name__ == '__main__':
    unittest.main()
