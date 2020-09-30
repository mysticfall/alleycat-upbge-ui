import unittest

from returns.maybe import Some

from alleycat.ui import Window, Bounds, Point, RGBA, Panel
from alleycat.ui.glass import ColorKeys
from tests.ui import UITestCase


class WindowTest(UITestCase):

    def test_style_fallback(self):
        window = Window(self.context)

        prefixes = list(window.style_fallback_prefixes)
        keys = list(window.style_fallback_keys(ColorKeys.Background))

        self.assertEqual(["Window"], prefixes)
        self.assertEqual(["Window.background", "background"], keys)

    def test_draw(self):
        window1 = Window(self.context)

        window1.bounds = Bounds(10, 20, 80, 60)

        window2 = Window(self.context)

        window2.bounds = Bounds(50, 40, 50, 50)
        window2.set_color(ColorKeys.Background, RGBA(1, 0, 0, 1))

        self.context.process()

        self.assertImage("draw", self.context)

    def test_draw_children(self):
        window = Window(self.context)

        window.bounds = Bounds(10, 20, 80, 60)
        window.set_color(ColorKeys.Background, RGBA(0.5, 0.5, 0.5, 1))

        child1 = Panel(self.context)

        child1.bounds = Bounds(10, 10, 40, 40)
        child1.set_color(ColorKeys.Background, RGBA(1, 0, 0, 1))

        child2 = Panel(self.context)

        child2.bounds = Bounds(30, 30, 40, 40)
        child2.set_color(ColorKeys.Background, RGBA(0, 0, 1, 1))

        window.add(child1)
        window.add(child2)

        self.context.process()

        self.assertImage("draw_children", self.context)

    def test_window_at(self):
        manager = self.context.window_manager

        bottom = Window(self.context)
        bottom.bounds = Bounds(0, 0, 100, 100)

        middle = Window(self.context)
        middle.bounds = Bounds(100, 100, 100, 100)

        top = Window(self.context)
        top.bounds = Bounds(50, 50, 100, 100)

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
