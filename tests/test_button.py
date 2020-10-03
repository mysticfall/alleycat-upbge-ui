import unittest

from alleycat.reactive import functions as rv
from alleycat.ui import Bounds, Window, RGBA, TextAlign, LabelButton, Point, MouseButton
from alleycat.ui.glass import ColorKeys
from tests.ui import UITestCase


# noinspection DuplicatedCode
class ButtonTest(UITestCase):

    def test_style_fallback(self):
        button = LabelButton(self.context)

        prefixes = list(button.style_fallback_prefixes)
        keys = list(button.style_fallback_keys(ColorKeys.Background))

        self.assertEqual(["LabelButton", "Button"], prefixes)
        self.assertEqual(["LabelButton.background", "Button.background", "background"], keys)

    def test_draw(self):
        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 100)

        button1 = LabelButton(self.context)

        button1.text = "Text"
        button1.bounds = Bounds(20, 10, 40, 20)

        button2 = LabelButton(self.context)

        button2.text = "AlleyCat"
        button2.text_size = 16
        button2.set_color(ColorKeys.Text, RGBA(1, 0, 0, 1))
        button2.bounds = Bounds(10, 50, 80, 30)

        window.add(button1)
        window.add(button2)

        self.context.process()

        self.assertImage("draw", self.context, tolerance=50)

    def test_align(self):
        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 100)

        button = LabelButton(self.context)

        button.text = "AlleyCat"
        button.text_size = 18
        button.bounds = Bounds(0, 0, 100, 100)

        window.add(button)

        self.context.process()
        self.assertImage("align_default", self.context)

        for align in TextAlign:
            for vertical_align in TextAlign:
                button.text_align = align
                button.text_vertical_align = vertical_align

                test_name = f"align_{align}_{vertical_align}".replace("TextAlign.", "")

                self.context.process()
                self.assertImage(test_name, self.context, tolerance=50)

    def test_hover(self):
        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 60)

        button = LabelButton(self.context)

        button.text = "AlleyCat"
        button.text_size = 18
        button.bounds = Bounds(10, 10, 80, 40)

        window.add(button)

        values = []

        rv.observe(button, "hover").subscribe(values.append)

        self.assertFalse(button.hover)
        self.assertEqual([False], values)

        self.mouse.move_to(Point(50, 30))
        self.context.process()

        self.assertTrue(button.hover)
        self.assertEqual([False, True], values)
        self.assertImage("hover_mouse_over", self.context, tolerance=50)

        self.mouse.move_to(Point(0, 0))
        self.context.process()

        self.assertFalse(button.hover)
        self.assertEqual([False, True, False], values)
        self.assertImage("hover_mouse_out", self.context, tolerance=50)

        self.mouse.move_to(Point(10, 10))
        self.context.process()

        self.assertTrue(button.hover)
        self.assertEqual([False, True, False, True], values)
        self.assertImage("hover_mouse_over2", self.context, tolerance=50)

    def test_active(self):
        window = Window(self.context)
        window.bounds = Bounds(0, 0, 100, 60)

        button = LabelButton(self.context)

        button.text = "AlleyCat"
        button.text_size = 18
        button.bounds = Bounds(10, 10, 80, 40)

        window.add(button)

        values = []

        rv.observe(button, "active").subscribe(values.append)

        self.assertFalse(button.active)
        self.assertEqual([False], values)

        self.mouse.move_to(Point(50, 30))
        self.mouse.press(MouseButton.LEFT)
        self.context.process()

        self.assertTrue(button.active)
        self.assertEqual([False, True], values)
        self.assertImage("active_mouse_down", self.context, tolerance=50)

        self.mouse.release(MouseButton.LEFT)
        self.context.process()

        self.assertFalse(button.active)
        self.assertEqual([False, True, False], values)
        self.assertImage("active_mouse_up", self.context, tolerance=50)

        self.mouse.press(MouseButton.LEFT)
        self.mouse.move_to(Point(0, 0))
        self.context.process()

        self.assertTrue(button.active)
        self.assertEqual([False, True, False, True], values)
        self.assertImage("active_mouse_drag_out", self.context, tolerance=50)

        self.mouse.release(MouseButton.LEFT)
        self.mouse.press(MouseButton.LEFT)
        self.mouse.move_to(Point(50, 30))
        self.context.process()

        self.assertFalse(button.active)
        self.assertEqual([False, True, False, True, False], values)
        self.assertImage("active_mouse_drag_in", self.context, tolerance=50)

        self.mouse.release(MouseButton.LEFT)
        self.mouse.press(MouseButton.RIGHT)
        self.context.process()

        self.assertFalse(button.active)
        self.assertEqual([False, True, False, True, False], values)
        self.assertImage("active_right_button", self.context, tolerance=50)


if __name__ == '__main__':
    unittest.main()
