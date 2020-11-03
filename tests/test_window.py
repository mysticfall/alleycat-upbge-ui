import unittest

from returns.maybe import Some

from alleycat.ui import Window, Bounds, Point, RGBA, Panel, MouseButton, Dimension
from alleycat.ui.glass import StyleKeys
from tests.ui import UITestCase


# noinspection DuplicatedCode
class WindowTest(UITestCase):

    def test_style_fallback(self):
        window = Window(self.context)

        prefixes = list(window.style_fallback_prefixes)
        keys = list(window.style_fallback_keys(StyleKeys.Background))

        self.assertEqual(["Window"], prefixes)
        self.assertEqual(["Window.background", "background"], keys)

    def test_draw(self):
        window1 = Window(self.context)

        window1.bounds = Bounds(10, 20, 80, 60)

        window2 = Window(self.context)

        window2.bounds = Bounds(50, 40, 50, 50)
        window2.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        self.context.process()

        self.assertImage("draw", self.context)

    def test_draw_children(self):
        window = Window(self.context)

        window.bounds = Bounds(10, 20, 80, 60)
        window.set_color(StyleKeys.Background, RGBA(0.5, 0.5, 0.5, 1))

        child1 = Panel(self.context)

        child1.bounds = Bounds(10, 10, 40, 40)
        child1.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        child2 = Panel(self.context)

        child2.bounds = Bounds(30, 30, 40, 40)
        child2.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

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
        window.resizable = True
        window.bounds = Bounds(10, 10, 50, 50)

        self.mouse.move_to(Point(30, 30))
        self.mouse.press(MouseButton.RIGHT)

        self.mouse.move_to(Point(40, 40))
        self.mouse.release(MouseButton.RIGHT)

        self.context.process()

        self.assertImage("drag_with_right_button", self.context)

        self.mouse.move_to(Point(20, 20))
        self.mouse.press(MouseButton.LEFT)

        self.mouse.move_to(Point(50, 50))
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
        bottom.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

        top = Window(self.context)
        top.draggable = True
        top.bounds = Bounds(20, 20, 50, 50)
        top.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))

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

    def test_resize(self):
        window = Window(self.context)
        window.draggable = True
        window.resizable = True

        def resize(name: str, drag_from: Point, drag_to: Point) -> None:
            window.bounds = Bounds(20, 20, 60, 60)

            self.mouse.move_to(drag_from)
            self.mouse.press(MouseButton.LEFT)
            self.mouse.move_to(drag_to)
            self.mouse.release(MouseButton.LEFT)

            self.context.process()

            self.assertImage(name, self.context)

        resize("resize_North", Point(40, 25), Point(40, 10))
        resize("resize_Northeast", Point(75, 25), Point(90, 10))
        resize("resize_East", Point(75, 40), Point(90, 40))
        resize("resize_Southeast", Point(75, 75), Point(90, 90))
        resize("resize_South", Point(40, 75), Point(40, 90))
        resize("resize_Southwest", Point(25, 75), Point(10, 90))
        resize("resize_West", Point(25, 40), Point(10, 40))
        resize("resize_Northwest", Point(25, 25), Point(10, 10))

        resize("resize_North_shrink", Point(40, 25), Point(40, 40))
        resize("resize_Northeast_shrink", Point(75, 25), Point(60, 40))
        resize("resize_East_shrink", Point(75, 40), Point(60, 40))
        resize("resize_Southeast_shrink", Point(75, 75), Point(60, 60))
        resize("resize_South_shrink", Point(40, 75), Point(40, 50))
        resize("resize_Southwest_shrink", Point(25, 75), Point(40, 60))
        resize("resize_West_shrink", Point(25, 40), Point(40, 40))
        resize("resize_Northwest_shrink", Point(25, 25), Point(40, 40))

        window.resizable = False

        resize("resize_non_resizable", Point(40, 25), Point(40, 10))

    def test_resize_to_collapse(self):
        window = Window(self.context)
        window.draggable = True
        window.resizable = True

        def resize(drag_from: Point, drag_to: Point, expected: Bounds) -> None:
            window.bounds = Bounds(20, 20, 60, 60)

            self.mouse.move_to(drag_from)
            self.mouse.press(MouseButton.LEFT)
            self.mouse.move_to(drag_to)
            self.mouse.release(MouseButton.LEFT)

            self.context.process()

            self.assertEqual(expected, window.bounds)

        resize(Point(40, 25), Point(40, 95), Bounds(20, 80, 60, 0))
        resize(Point(75, 25), Point(5, 95), Bounds(20, 80, 0, 0))
        resize(Point(75, 40), Point(5, 40), Bounds(20, 20, 0, 60))
        resize(Point(75, 75), Point(5, 5), Bounds(20, 20, 0, 0))
        resize(Point(40, 75), Point(40, 5), Bounds(20, 20, 60, 0))
        resize(Point(25, 75), Point(95, 5), Bounds(80, 20, 0, 0))
        resize(Point(25, 40), Point(95, 40), Bounds(80, 20, 0, 60))
        resize(Point(25, 25), Point(95, 95), Bounds(80, 80, 0, 0))

    def test_resize_with_min_size(self):
        window = Window(self.context)
        window.draggable = True
        window.resizable = True

        window.minimum_size_override = Some(Dimension(30, 30))

        def resize(drag_from: Point, drag_to: Point, expected: Bounds) -> None:
            window.bounds = Bounds(20, 20, 60, 60)

            self.mouse.move_to(drag_from)
            self.mouse.press(MouseButton.LEFT)
            self.mouse.move_to(drag_to)
            self.mouse.release(MouseButton.LEFT)

            self.context.process()

            self.assertEqual(expected, window.bounds)

        resize(Point(40, 25), Point(40, 95), Bounds(20, 50, 60, 30))
        resize(Point(75, 25), Point(5, 95), Bounds(20, 50, 30, 30))
        resize(Point(75, 40), Point(5, 40), Bounds(20, 20, 30, 60))
        resize(Point(75, 75), Point(5, 5), Bounds(20, 20, 30, 30))
        resize(Point(40, 75), Point(40, 5), Bounds(20, 20, 60, 30))
        resize(Point(25, 75), Point(95, 5), Bounds(50, 20, 30, 30))
        resize(Point(25, 40), Point(95, 40), Bounds(50, 20, 30, 60))
        resize(Point(25, 25), Point(95, 95), Bounds(50, 50, 30, 30))


if __name__ == '__main__':
    unittest.main()
