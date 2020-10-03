import unittest

from returns.maybe import Some

from alleycat.ui import Window, Bounds, Point, RGBA, Panel, MouseButton
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

    def test_drag(self):
        window = Window(self.context)
        window.draggable = True
        window.bounds = Bounds(10, 10, 50, 50)

        self.mouse.move_to(Point(30, 30))
        self.mouse.press(MouseButton.RIGHT)

        self.mouse.move_to(Point(40, 40))
        self.mouse.release(MouseButton.RIGHT)

        self.context.process()

        self.assertImage("drag_with_right_button", self.context)

        self.mouse.move_to(Point(15, 15))
        self.mouse.press(MouseButton.LEFT)

        self.mouse.move_to(Point(40, 40))
        self.mouse.release(MouseButton.LEFT)

        self.context.process()

        self.assertImage("drag_with_left_button", self.context)

        self.mouse.press(MouseButton.LEFT)
        self.mouse.press(MouseButton.MIDDLE)

        self.mouse.move_to(Point(30, 50))

        self.mouse.release(MouseButton.MIDDLE)

        self.mouse.move_to(Point(20, 50))

        self.context.process()

        self.assertImage("drag_with_2_buttons", self.context)

        self.mouse.release(MouseButton.MIDDLE)

        window.draggable = False

        self.mouse.press(MouseButton.LEFT)
        self.mouse.move_to(Point(0, 0))
        self.mouse.release(MouseButton.LEFT)

        self.context.process()

        self.assertImage("drag_non_draggable", self.context)

    def test_drag_overlapping(self):
        bottom = Window(self.context)
        bottom.draggable = True
        bottom.bounds = Bounds(10, 10, 50, 50)
        bottom.set_color(ColorKeys.Background, RGBA(1, 0, 0, 1))

        top = Window(self.context)
        top.draggable = True
        top.bounds = Bounds(20, 20, 50, 50)
        top.set_color(ColorKeys.Background, RGBA(0, 0, 1, 1))

        self.mouse.move_to(Point(30, 30))
        self.mouse.press(MouseButton.LEFT)
        self.mouse.move_to(Point(50, 50))
        self.mouse.release(MouseButton.LEFT)

        self.context.process()

        self.assertImage("drag_overlapping_top", self.context)

        self.mouse.move_to(Point(20, 20))
        self.mouse.press(MouseButton.LEFT)
        self.mouse.move_to(Point(40, 40))
        self.mouse.release(MouseButton.LEFT)

        self.context.process()

        self.assertImage("drag_overlapping_bottom", self.context)


if __name__ == '__main__':
    unittest.main()
