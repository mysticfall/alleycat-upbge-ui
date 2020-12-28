import unittest
from typing import cast

from alleycat.reactive import functions as rv
from returns.maybe import Nothing, Some

from alleycat.ui import Bounds, Dimension, Insets, LabelButton, LabelUI, MouseButton, Point, RGBA, StyleLookup, \
    TextAlign, Window
from alleycat.ui.glass import StyleKeys
from ui import UITestCase


# noinspection DuplicatedCode
class ButtonTest(UITestCase):

    def test_style_fallback(self):
        button = LabelButton(self.context)

        prefixes = list(button.style_fallback_prefixes)
        keys = list(button.style_fallback_keys(StyleKeys.Background))

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
        button2.set_color(StyleKeys.Text, RGBA(1, 0, 0, 1))
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
        button.text_size = 16
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
        button.text_size = 14
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
        button.text_size = 14
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

    def test_validation(self):
        laf = self.context.look_and_feel
        fonts = self.context.toolkit.fonts

        button = LabelButton(self.context)
        button.validate()

        self.assertEqual(True, button.valid)

        button.text = "Button"

        self.assertEqual(False, button.valid)

        button.validate()
        button.text_size = 20

        self.assertEqual(False, button.valid)

        button.validate()
        button.text_align = TextAlign.End
        button.text_vertical_align = TextAlign.End

        self.assertEqual(True, button.valid)

        def test_style(lookup: StyleLookup):
            button.validate()

            lookup.set_font("NonExistentKey", fonts["Font1"])
            lookup.set_insets("NonExistentKey", Insets(10, 10, 10, 10))

            self.assertEqual(True, button.valid)

            lookup.set_font(StyleKeys.Text, fonts["Font1"])

            self.assertEqual(False, button.valid)

            button.validate()
            lookup.set_insets(StyleKeys.Padding, Insets(10, 10, 10, 10))

            self.assertEqual(False, button.valid)

        test_style(laf)
        test_style(button)

    def test_ui_extents(self):
        button = LabelButton(self.context)
        laf = self.context.look_and_feel
        ui = cast(LabelUI, button.ui)
        font_registry = self.context.toolkit.fonts

        tolerance = 0.1

        mono = font_registry["Mono"]

        self.assertEqual(Dimension(0, 0), ui.extents(button))

        button.text = "Test"
        button.validate()

        self.assertAlmostEqual(20.02, ui.extents(button).width, delta=tolerance)
        self.assertAlmostEqual(7.227, ui.extents(button).height, delta=tolerance)

        button.text_size = 15
        button.validate()

        self.assertAlmostEqual(30.03, ui.extents(button).width, delta=tolerance)
        self.assertAlmostEqual(10.840, ui.extents(button).height, delta=tolerance)

        laf.set_font("Button.text", mono)

        self.assertEqual(False, button.valid)

    def test_minimum_size(self):
        tolerance = 0.1

        def test_with_padding(padding: Insets):
            with LabelButton(self.context) as button:
                calculated = []

                button.set_insets(StyleKeys.Padding, padding)
                button.validate()

                pw = padding.left + padding.right
                ph = padding.top + padding.bottom

                rv.observe(button.minimum_size).subscribe(calculated.append)

                self.assertEqual(Nothing, button.minimum_size_override)
                self.assertEqual(Dimension(pw, ph), button.minimum_size)
                self.assertEqual([Dimension(pw, ph)], calculated)

                button.text = "Test"
                button.validate()

                self.assertEqual(2, len(calculated))

                self.assertEqual(Nothing, button.minimum_size_override)
                self.assertAlmostEqual(20.02 + pw, button.minimum_size.width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, button.minimum_size.height, delta=tolerance)
                self.assertAlmostEqual(20.02 + pw, calculated[1].width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, calculated[1].height, delta=tolerance)

                self.assertEqual(Bounds(0, 0, calculated[1].width, calculated[1].height), button.bounds)

                button.text_size = 15
                button.validate()

                self.assertEqual(3, len(calculated))

                self.assertEqual(Nothing, button.minimum_size_override)
                self.assertAlmostEqual(30.03 + pw, button.minimum_size.width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, button.minimum_size.height, delta=tolerance)
                self.assertAlmostEqual(30.03 + pw, calculated[2].width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, calculated[2].height, delta=tolerance)

                button.bounds = Bounds(10, 20, 60, 40)

                self.assertEqual(Bounds(10, 20, 60, 40), button.bounds)

                button.minimum_size_override = Some(Dimension(80, 50))
                button.validate()

                self.assertEqual(Some(Dimension(80, 50)), button.minimum_size_override)
                self.assertEqual(Dimension(80, 50), button.minimum_size)
                self.assertAlmostEqual(30.03 + pw, calculated[2].width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, calculated[2].height, delta=tolerance)

                self.assertEqual(Bounds(10, 20, 80, 50), button.bounds)

                button.bounds = Bounds(0, 0, 30, 40)

                self.assertEqual(Bounds(0, 0, 80, 50), button.bounds)

        for p in [Insets(0, 0, 0, 0), Insets(5, 5, 5, 5), Insets(10, 5, 0, 3)]:
            test_with_padding(p)

    def test_preferred_size(self):
        tolerance = 0.1

        def test_with_padding(padding: Insets):
            with LabelButton(self.context) as button:
                calculated = []

                button.set_insets(StyleKeys.Padding, padding)
                button.validate()

                pw = padding.left + padding.right
                ph = padding.top + padding.bottom

                rv.observe(button.preferred_size).subscribe(calculated.append)

                self.assertEqual(Nothing, button.preferred_size_override)
                self.assertEqual(Dimension(pw, ph), button.preferred_size)
                self.assertEqual([Dimension(pw, ph)], calculated)

                button.text = "Test"
                button.validate()

                self.assertEqual(2, len(calculated))

                self.assertEqual(Nothing, button.preferred_size_override)
                self.assertAlmostEqual(20.02 + pw, button.preferred_size.width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, button.preferred_size.height, delta=tolerance)
                self.assertEqual(2, len(calculated))
                self.assertAlmostEqual(20.02 + pw, calculated[1].width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, calculated[1].height, delta=tolerance)

                button.text_size = 15
                button.validate()

                self.assertEqual(3, len(calculated))

                self.assertEqual(Nothing, button.preferred_size_override)
                self.assertAlmostEqual(30.03 + pw, button.preferred_size.width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, button.preferred_size.height, delta=tolerance)
                self.assertEqual(3, len(calculated))
                self.assertAlmostEqual(30.03 + pw, calculated[2].width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, calculated[2].height, delta=tolerance)

                button.preferred_size_override = Some(Dimension(80, 50))
                button.validate()

                self.assertEqual(Some(Dimension(80, 50)), button.preferred_size_override)
                self.assertEqual(Dimension(80, 50), button.preferred_size)
                self.assertEqual(4, len(calculated))
                self.assertEqual(Dimension(80, 50), calculated[3])

                button.preferred_size_override = Some(Dimension(10, 10))
                button.validate()

                self.assertEqual(calculated[2], button.preferred_size)
                self.assertEqual(5, len(calculated))
                self.assertEqual(calculated[2], calculated[4])

                button.minimum_size_override = Some(Dimension(400, 360))
                button.validate()

                self.assertEqual(Dimension(400, 360), button.preferred_size)
                self.assertEqual(6, len(calculated))
                self.assertEqual(Dimension(400, 360), calculated[5])

        for p in [Insets(0, 0, 0, 0), Insets(5, 5, 5, 5), Insets(10, 5, 0, 3)]:
            test_with_padding(p)


if __name__ == '__main__':
    unittest.main()
