import unittest
from typing import cast

from returns.maybe import Nothing, Some
from rx import operators as ops

from alleycat.ui import Label, Bounds, Window, RGBA, TextAlign, LabelUI, Dimension, Insets
from alleycat.ui.glass import StyleKeys
from alleycat.reactive import functions as rv
from tests.ui import UITestCase


# noinspection DuplicatedCode
class LabelTest(UITestCase):

    def test_style_fallback(self):
        label = Label(self.context)

        prefixes = list(label.style_fallback_prefixes)
        keys = list(label.style_fallback_keys(StyleKeys.Background))

        self.assertEqual(["Label"], prefixes)
        self.assertEqual(["Label.background", "background"], keys)

    def test_draw(self):
        window = Window(self.context)
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
        window = Window(self.context)
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

    def test_ui_on_font_change(self):
        label = Label(self.context)
        laf = self.context.look_and_feel
        ui = cast(LabelUI, label.ui)
        font_registry = self.context.toolkit.fonts

        font1 = font_registry.resolve("Font 1").unwrap()
        font2 = font_registry.resolve("Font 2").unwrap()
        default = font_registry.fallback_font

        changes = []

        ui.on_font_change(label).pipe(ops.map(lambda e: e.family)).subscribe(changes.append)

        self.assertEqual([default.family], changes)

        label.set_font("text", font1)
        label.set_font("tooltip", font1)

        self.assertEqual([font1.family], changes[1:])

        label.set_font("text", font2)
        label.set_font("text", font2)  # Should ignore duplicates.

        self.assertEqual([font2.family], changes[2:])

        label.clear_font("text")

        self.assertEqual([default.family], changes[3:])

        laf.set_font("text", font1)

        self.assertEqual([font1.family], changes[4:])

        laf.set_font("Label.text", font2)

        self.assertEqual([font2.family], changes[5:])

        laf.clear_font("text")

        self.assertEqual([], changes[6:])

        label.set_font("text", font1)

        self.assertEqual([font1.family], changes[6:])

    def test_ui_on_extents_change(self):
        label = Label(self.context)
        laf = self.context.look_and_feel
        ui = cast(LabelUI, label.ui)
        font_registry = self.context.toolkit.fonts

        tolerance = 0.1

        mono = font_registry.resolve("Mono").unwrap()

        changes = []

        ui.on_extents_change(label).subscribe(changes.append)

        self.assertEqual([Dimension(width=0.0, height=0.0)], changes)

        label.text = "Test"

        self.assertEqual(2, len(changes))

        self.assertAlmostEqual(18.476, changes[1].width, delta=tolerance)
        self.assertAlmostEqual(7.227, changes[1].height, delta=tolerance)

        label.text_size = 15

        self.assertEqual(3, len(changes))

        self.assertAlmostEqual(27.715, changes[2].width, delta=tolerance)
        self.assertAlmostEqual(10.840, changes[2].height, delta=tolerance)

        laf.set_font("Label.text", mono)

        self.assertEqual(4, len(changes))

    def test_minimum_size(self):
        tolerance = 0.1

        def test_with_padding(padding: Insets):
            with Label(self.context) as label:
                calculated = []

                label.set_insets(StyleKeys.Padding, padding)

                pw = padding.left + padding.right
                ph = padding.top + padding.bottom

                rv.observe(label.minimum_size).subscribe(calculated.append)

                self.assertEqual(Nothing, label.minimum_size_override)
                self.assertEqual(Dimension(pw, ph), label.minimum_size)
                self.assertEqual([Dimension(pw, ph)], calculated)

                label.text = "Test"

                self.assertEqual(2, len(calculated))

                self.assertEqual(Nothing, label.minimum_size_override)
                self.assertAlmostEqual(18.476 + pw, label.minimum_size.width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, label.minimum_size.height, delta=tolerance)
                self.assertAlmostEqual(18.476 + pw, calculated[1].width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, calculated[1].height, delta=tolerance)

                self.assertEqual(Bounds(0, 0, calculated[1].width, calculated[1].height), label.bounds)

                label.text_size = 15

                self.assertEqual(3, len(calculated))

                self.assertEqual(Nothing, label.minimum_size_override)
                self.assertAlmostEqual(27.715 + pw, label.minimum_size.width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, label.minimum_size.height, delta=tolerance)
                self.assertAlmostEqual(27.715 + pw, calculated[2].width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, calculated[2].height, delta=tolerance)

                label.bounds = Bounds(10, 20, 60, 40)

                self.assertEqual(Bounds(10, 20, 60, 40), label.bounds)

                label.minimum_size_override = Some(Dimension(80, 50))

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

                pw = padding.left + padding.right
                ph = padding.top + padding.bottom

                rv.observe(label.preferred_size).subscribe(calculated.append)

                self.assertEqual(Nothing, label.preferred_size_override)
                self.assertEqual(Dimension(pw, ph), label.preferred_size)
                self.assertEqual([Dimension(pw, ph)], calculated)

                label.text = "Test"

                self.assertEqual(2, len(calculated))

                self.assertEqual(Nothing, label.preferred_size_override)
                self.assertAlmostEqual(18.476 + pw, label.preferred_size.width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, label.preferred_size.height, delta=tolerance)
                self.assertEqual(2, len(calculated))
                self.assertAlmostEqual(18.476 + pw, calculated[1].width, delta=tolerance)
                self.assertAlmostEqual(7.227 + ph, calculated[1].height, delta=tolerance)

                label.text_size = 15

                self.assertEqual(3, len(calculated))

                self.assertEqual(Nothing, label.preferred_size_override)
                self.assertAlmostEqual(27.715 + pw, label.preferred_size.width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, label.preferred_size.height, delta=tolerance)
                self.assertEqual(3, len(calculated))
                self.assertAlmostEqual(27.715 + pw, calculated[2].width, delta=tolerance)
                self.assertAlmostEqual(10.840 + ph, calculated[2].height, delta=tolerance)

                label.preferred_size_override = Some(Dimension(80, 50))

                self.assertEqual(Some(Dimension(80, 50)), label.preferred_size_override)
                self.assertEqual(Dimension(80, 50), label.preferred_size)
                self.assertEqual(4, len(calculated))
                self.assertEqual(Dimension(80, 50), calculated[3])

                label.preferred_size_override = Some(Dimension(10, 10))

                self.assertEqual(calculated[2], label.preferred_size)
                self.assertEqual(5, len(calculated))
                self.assertEqual(calculated[2], calculated[4])

                label.minimum_size_override = Some(Dimension(400, 360))

                self.assertEqual(Dimension(400, 360), label.preferred_size)
                self.assertEqual(6, len(calculated))
                self.assertEqual(Dimension(400, 360), calculated[5])

        for p in [Insets(0, 0, 0, 0), Insets(5, 5, 5, 5), Insets(10, 5, 0, 3)]:
            test_with_padding(p)


if __name__ == '__main__':
    unittest.main()
