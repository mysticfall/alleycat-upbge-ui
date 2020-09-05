import unittest

from returns.maybe import Some

from alleycat.ui import Window, Bounds, Point, WindowManager
from alleycat.ui.cairo import UI
from tests.ui import UITestCase


class WindowTest(UITestCase):

    def test_window_at(self):
        context = UI().create_context()

        manager = WindowManager()

        bottom = Window(context)
        bottom.bounds = Bounds(0, 0, 100, 100)

        middle = Window(context)
        middle.bounds = Bounds(100, 100, 100, 100)

        top = Window(context)
        top.bounds = Bounds(50, 50, 100, 100)

        manager.add(bottom)
        manager.add(middle)
        manager.add(top)

        self.assertEqual(Some(bottom), manager.window_at(Point(0, 0)))
        self.assertEqual(Some(bottom), manager.window_at(Point(100, 0)))
        self.assertEqual(Some(bottom), manager.window_at(Point(0, 100)))

        self.assertEqual(Some(middle), manager.window_at(Point(200, 100)))
        self.assertEqual(Some(middle), manager.window_at(Point(200, 200)))
        self.assertEqual(Some(middle), manager.window_at(Point(100, 200)))

        self.assertEqual(Some(top), manager.window_at(Point(100, 100)))
        self.assertEqual(Some(top), manager.window_at(Point(150, 150)))
        self.assertEqual(Some(top), manager.window_at(Point(150, 50)))
        self.assertEqual(Some(top), manager.window_at(Point(50, 150)))


if __name__ == '__main__':
    unittest.main()
