import unittest
from typing import cast

from alleycat.reactive import functions as rv
from returns.maybe import Nothing, Some

from alleycat.ui import Bounds, Dimension, Frame, Insets, Label, LabelUI, RGBA, StyleLookup, TextAlign
from alleycat.ui.glass import StyleKeys
from ui import UITestCase


# noinspection DuplicatedCode
class LabelTest(UITestCase):

    def test_style_fallback(self):
        label = Label(self.context)

        prefixes = list(label.style_fallback_prefixes)
        keys = list(label.style_fallback_keys(StyleKeys.Background))

        self.assertEqual(["Label"], prefixes)
        self.assertEqual(["Label.background", "background"], keys)

    def test_draw(self):
        window = Frame(self.context)
        window.bounds = Bounds(0, 0, 100, 60)

        label = Label(self.context)

        label.text = "Text"
        label.bounds = Bounds(0, 30, 60, 30)

        label2 = Label(self.context)

        label2.text = "AlleyCat"
        label2.text_size = 18
        label2.set_color(StyleKeys.Text, RGBA(1, 0, 0, 1))
        label2.bounds = Bounds(20, 0, 80, 60)

        window.add(label)
        window.add(label2)

        self.context.process()

        self.assertImage("draw", self.context, tolerance=50)

    def test_align(self):
        window = Frame(self.context)
        window.bounds = Bounds(0, 0, 100, 100)

        label = Label(self.context)

        label.text = "AlleyCat"
        label.text_size = 18
        label.bounds = Bounds(0, 0, 100, 100)

        window.add(label)

        self.context.process()
        self.assertImage("align_default", self.context, tolerance=50)

        for align in TextAlign:
            for vertical_align in TextAlign:
                label.text_align = align
                label.text_vertical_align = vertical_align

                test_name = f"align_{align}_{vertical_align}".replace("TextAlign.", "")

                self.context.process()
                self.assertImage(test_name, self.context)

    def test_validation(self):
        laf = self.context.look_and_feel
        fonts = self.context.toolkit.fonts

        label = Label(self.context)
        label.validate()

        self.assertEqual(True, label.valid)

        label.text = "Label"

        self.assertEqual(False, label.valid)

        label.validate()
        label.text_size = 20

        self.assertEqual(False, label.valid)

        label.validate()
        label.text_align = TextAlign.End
        label.text_vertical_align = TextAlign.End

        self.assertEqual(True, label.valid)

        def test_style(lookup: StyleLookup):
            label.validate()

            lookup.set_font("NonExistentKey", fonts["Font1"])
            lookup.set_insets("NonExistentKey", Insets(10, 10, 10, 10))

            self.assertEqual(True, label.valid)

            lookup.set_font(StyleKeys.Text, fonts["Font1"])

            self.assertEqual(False, label.valid)

            label.validate()
            lookup.set_insets(StyleKeys.Padding, Insets(10, 10, 10, 10))

            self.assertEqual(False, label.valid)

        test_style(laf)
        test_style(label)

    def test_ui_extents(self):
        label = Label(self.context)
        laf = self.context.look_and_feel
        ui = cast(LabelUI, label.ui)
        font_registry = self.context.toolkit.fonts

        tolerance = 0.1

        mono = font_registry["Mono"]

        self.assertEqual(Dimension(0, 0), ui.extents(label))

        label.text = "Test"
        label.validate()

        self.assertAlmostEqual(18.476, ui.extents(label).width, delta=tolerance)
        self.assertAlmostEqual(7.227, ui.extents(label).height, delta=tolerance)

        label.text_size = 15
        label.validate()

        self.assertAlmostEqual(27.715, ui.extents(label).width, delta=tolerance)
        self.assertAlmostEqual(10.840, ui.extents(label).height, delta=tolerance)

        laf.set_font("Label.text", mono)

        self.assertEqual(False, label.valid)

    def test_minimum_size(self):
        tolerance = 0.1

        def test_with_padding(padding: Insets):
            with Label(self.context) as label:
                calculated = []

                label.set_insets(StyleKeys.Padding, padding)
                label.validate()

                pw = padding.left + padding.right
                ph = padding.top + padding.bottom

                rv.observe(label.minimum_size).subscribe(calculated.append)

                self.assertEqual(Nothing, label.minimum_size_override)
                self.assertEqual(Dimension(pw, ph), label.minimum_size)
                self.assertEqual([Dimension(pw, ph)], calculated)

                label.text = "Test"
                label.validate()

                self.assertEqual(2, len(calculated))

                self.assertEqual(Nothing, label.minimum_size_override)
                self.assertAlmostEqual(18.476 + pw, label.minimum_size.width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, label.minimum_size.height, delta=tolerance)
                self.assertAlmostEqual(18.476 + pw, calculated[1].width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, calculated[1].height, delta=tolerance)

                self.assertEqual(Bounds(0, 0, calculated[1].width, calculated[1].height), label.bounds)

                label.text_size = 15
                label.validate()

                self.assertEqual(3, len(calculated))

                self.assertEqual(Nothing, label.minimum_size_override)
                self.assertAlmostEqual(27.715 + pw, label.minimum_size.width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, label.minimum_size.height, delta=tolerance)
                self.assertAlmostEqual(27.715 + pw, calculated[2].width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, calculated[2].height, delta=tolerance)

                label.bounds = Bounds(10, 20, 60, 40)

                self.assertEqual(Bounds(10, 20, 60, 40), label.bounds)

                label.minimum_size_override = Some(Dimension(80, 50))
                label.validate()

                self.assertEqual(Some(Dimension(80, 50)), label.minimum_size_override)
                self.assertEqual(Dimension(80, 50), label.minimum_size)
                self.assertAlmostEqual(27.715 + pw, calculated[2].width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, calculated[2].height, delta=tolerance)

                self.assertEqual(Bounds(10, 20, 80, 50), label.bounds)

                label.bounds = Bounds(0, 0, 30, 40)

                self.assertEqual(Bounds(0, 0, 80, 50), label.bounds)

        for p in [Insets(0, 0, 0, 0), Insets(5, 5, 5, 5), Insets(10, 5, 0, 3)]:
            test_with_padding(p)

    def test_preferred_size(self):
        tolerance = 0.1

        def test_with_padding(padding: Insets):
            with Label(self.context) as label:
                calculated = []

                label.set_insets(StyleKeys.Padding, padding)
                label.validate()

                pw = padding.left + padding.right
                ph = padding.top + padding.bottom

                rv.observe(label.preferred_size).subscribe(calculated.append)

                self.assertEqual(Nothing, label.preferred_size_override)
                self.assertEqual(Dimension(pw, ph), label.preferred_size)
                self.assertEqual([Dimension(pw, ph)], calculated)

                label.text = "Test"
                label.validate()

                self.assertEqual(2, len(calculated))

                self.assertEqual(Nothing, label.preferred_size_override)
                self.assertAlmostEqual(18.476 + pw, label.preferred_size.width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, label.preferred_size.height, delta=tolerance)
                self.assertEqual(2, len(calculated))
                self.assertAlmostEqual(18.476 + pw, calculated[1].width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, calculated[1].height, delta=tolerance)

                label.text_size = 15
                label.validate()

                self.assertEqual(3, len(calculated))

                self.assertEqual(Nothing, label.preferred_size_override)
                self.assertAlmostEqual(27.715 + pw, label.preferred_size.width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, label.preferred_size.height, delta=tolerance)
                self.assertEqual(3, len(calculated))
                self.assertAlmostEqual(27.715 + pw, calculated[2].width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, calculated[2].height, delta=tolerance)

                label.preferred_size_override = Some(Dimension(80, 50))
                label.validate()

                self.assertEqual(Some(Dimension(80, 50)), label.preferred_size_override)
                self.assertEqual(Dimension(80, 50), label.preferred_size)
                self.assertEqual(4, len(calculated))
                self.assertEqual(Dimension(80, 50), calculated[3])

                label.preferred_size_override = Some(Dimension(10, 10))
                label.validate()

                self.assertEqual(calculated[2], label.preferred_size)
                self.assertEqual(5, len(calculated))
                self.assertEqual(calculated[2], calculated[4])

                label.minimum_size_override = Some(Dimension(400, 360))
                label.validate()

                self.assertEqual(Dimension(400, 360), label.preferred_size)
                self.assertEqual(6, len(calculated))
                self.assertEqual(Dimension(400, 360), calculated[5])

        for p in [Insets(0, 0, 0, 0), Insets(5, 5, 5, 5), Insets(10, 5, 0, 3)]:
            test_with_padding(p)


if __name__ == '__main__':
    unittest.main()
