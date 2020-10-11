import unittest

from returns.maybe import Nothing

from alleycat.ui import Point, Dimension, Bounds, RGBA, Insets


class PrimitivesTest(unittest.TestCase):
    def test_point_init(self):
        point = Point(10.5, -20.2)

        self.assertEqual(10.5, point.x)
        self.assertEqual(-20.2, point.y)

    def test_point_unpack(self):
        (x, y) = Point(20.2, 15.3)

        self.assertEqual(20.2, x)
        self.assertEqual(15.3, y)

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

    def test_dimension_unpack(self):
        (width, height) = Dimension(20, 10)

        self.assertEqual(20, width)
        self.assertEqual(10, height)

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

    def test_bounds_unpack(self):
        (x, y, width, height) = Bounds(10, -30, 150, 200)

        self.assertEqual(10, x)
        self.assertEqual(-30, y)
        self.assertEqual(150, width)
        self.assertEqual(200, height)

    def test_bounds_to_tuple(self):
        self.assertEqual((30, 20, 100, 200), Bounds(30, 20, 100, 200).tuple)

    def test_bounds_from_tuple(self):
        self.assertEqual(Bounds(30, 0, 50, 40), Bounds.from_tuple((30, 0, 50, 40)))

    def test_bounds_move_to(self):
        self.assertEqual(Bounds(-10, 20, 100, 200), Bounds(20, 30, 100, 200).move_to(Point(-10, 20)))

    def test_bounds_move_by(self):
        self.assertEqual(Bounds(10, 50, 100, 200), Bounds(20, 30, 100, 200).move_by(Point(-10, 20)))

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

        self.assertEqual(Nothing, Bounds(10, 20, 100, 60) & Bounds(120, 20, 100, 60))
        self.assertEqual(Nothing, Bounds(10, 20, 100, 60) & Bounds(-120, 20, 100, 60))
        self.assertEqual(Nothing, Bounds(10, 20, 100, 60) & Bounds(10, 90, 100, 60))
        self.assertEqual(Nothing, Bounds(10, 20, 100, 60) & Bounds(10, -50, 100, 60))

        self.assertEqual(Bounds(10, 20, 30, 20), (Bounds(10, 20, 100, 60) & Bounds(-60, -20, 100, 60)).unwrap())
        self.assertEqual(Bounds(60, 20, 50, 20), (Bounds(10, 20, 100, 60) & Bounds(60, -20, 100, 60)).unwrap())
        self.assertEqual(Bounds(60, 40, 50, 40), (Bounds(10, 20, 100, 60) & Bounds(60, 40, 100, 60)).unwrap())
        self.assertEqual(Bounds(10, 40, 30, 40), (Bounds(10, 20, 100, 60) & Bounds(-60, 40, 100, 60)).unwrap())

        self.assertEqual(Bounds(40, 30, 70, 40), (Bounds(10, 20, 100, 60) & Bounds(40, 30, 100, 40)).unwrap())
        self.assertEqual(Bounds(10, 30, 70, 40), (Bounds(10, 20, 100, 60) & Bounds(-20, 30, 100, 40)).unwrap())
        self.assertEqual(Bounds(20, 20, 80, 20), (Bounds(10, 20, 100, 60) & Bounds(20, -20, 80, 60)).unwrap())
        self.assertEqual(Bounds(20, 40, 80, 40), (Bounds(10, 20, 100, 60) & Bounds(20, 40, 80, 60)).unwrap())

        self.assertEqual(Bounds(30, 40, 50, 20), (Bounds(10, 20, 100, 60) & Bounds(30, 40, 50, 20)).unwrap())

        self.assertEqual(Bounds(-10, 15, 130, 70), Bounds(10, 20, 100, 60) + Insets(5, 10, 5, 20))
        self.assertEqual(Bounds(15, 40, 85, 0), Bounds(10, 20, 100, 60) - Insets(20, 10, 50, 5))

    def test_bounds_location(self):
        self.assertEqual(Point(10, 20), Bounds(10, 20, 100, 200).location)

    def test_bounds_size(self):
        self.assertEqual(Dimension(100, 200), Bounds(10, 20, 100, 200).size)

    def test_bounds_points(self):
        points = (Point(-10, 20), Point(70, 20), Point(70, 60), Point(-10, 60))

        self.assertEqual(points, Bounds(-10, 20, 80, 40).points)

    def test_bounds_contains(self):
        self.assertTrue(Bounds(10, 20, 100, 50).contains(Point(60, 40)))
        self.assertFalse(Bounds(10, 20, 100, 50).contains(Point(0, 40)))
        self.assertTrue(Bounds(-50, -40, 100, 80).contains(Point(50, 0)))
        self.assertFalse(Bounds(-50, -40, 100, 80).contains(Point(51, 0)))

    def test_insets_init(self):
        self.assertEqual(5, Insets(5, 10, 120, 0).top)
        self.assertEqual(30, Insets(15, 30, 0, 30.5).right)
        self.assertEqual(120, Insets(5, 10, 120, 0).bottom)
        self.assertEqual(30.5, Insets(15, 30, 0, 30.5).left)

        with self.assertRaises(ValueError) as cm_top:
            Insets(-10, 0, 10, 30)

        self.assertEqual("Argument 'top' must be zero or a positive number.", cm_top.exception.args[0])

        with self.assertRaises(ValueError) as cm_right:
            Insets(20, -1, 10, 0)

        self.assertEqual("Argument 'right' must be zero or a positive number.", cm_right.exception.args[0])

        with self.assertRaises(ValueError) as cm_bottom:
            Insets(5, 0, -15, 30)

        self.assertEqual("Argument 'bottom' must be zero or a positive number.", cm_bottom.exception.args[0])

        with self.assertRaises(ValueError) as cm_left:
            Insets(0, 0, 40, -30)

        self.assertEqual("Argument 'left' must be zero or a positive number.", cm_left.exception.args[0])

    def test_insets_unpack(self):
        (top, right, bottom, left) = Insets(10, 30, 5, 20)

        self.assertEqual(10, top)
        self.assertEqual(30, right)
        self.assertEqual(5, bottom)
        self.assertEqual(20, left)

    def test_insets_to_tuple(self):
        self.assertEqual((30, 20, 15, 5), Insets(30, 20, 15, 5).tuple)

    def test_insets_from_tuple(self):
        self.assertEqual(Insets(30, 0, 50, 40), Insets.from_tuple((30, 0, 50, 40)))

    def test_insets_copy(self):
        self.assertEqual(Insets(15, 20, 0, 30), Insets(15, 10, 30, 30).copy(right=20, bottom=0))
        self.assertEqual(Insets(20, 10, 0, 30), Insets(10, 10, 0, 10).copy(top=20, left=30))
        self.assertEqual(Insets(5, 10, 0, 30), Insets(0, 0, 20, 40).copy(top=5, right=10, bottom=0, left=30))
        self.assertEqual(Insets(20, 10, 5, 30), Insets(20, 10, 5, 30).copy())

    def test_insets_operations(self):
        self.assertEqual(Insets(5, 10, 25, 30), Insets(0, 0, 10, 20) + Insets(5, 10, 15, 10))
        self.assertEqual(Insets(20, 15, 5, 10), Insets(15, 10, 0, 5) + 5)
        self.assertEqual(Insets(0, 0, 0, 10), Insets(0, 5, 10, 20) - Insets(5, 10, 15, 10))
        self.assertEqual(Insets(5, 0, 10, 0), Insets(15, 10, 20, 5) - 10)
        self.assertEqual(Insets(0, 20, 10, 60), Insets(0, 10, 5, 30) * 2)
        self.assertEqual(Insets(10, 0, 5, 2.5), Insets(20, 0, 10, 5) / 2)

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

    def test_rgba_unpack(self):
        (r, g, b, a) = RGBA(0.1, 0.2, 0.8, 1.0)

        self.assertEqual(0.1, r)
        self.assertEqual(0.2, g)
        self.assertEqual(0.8, b)
        self.assertEqual(1.0, a)

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
