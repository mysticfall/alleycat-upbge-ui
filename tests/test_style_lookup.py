import unittest

from cairo import ToyFontFace
from returns.maybe import Nothing, Some

from alleycat.ui import StyleLookup, RGBA, ColorChangeEvent, FontChangeEvent, Insets, InsetsChangeEvent
from alleycat.ui.cairo import CairoFont


class StyleLookupTest(unittest.TestCase):
    def test_lookup_color(self):
        lookup = StyleLookup()

        red = RGBA(1, 0, 0, 1)
        blue = RGBA(0, 0, 1, 1)

        red_key = "red"
        blue_key = "blue"

        lookup.set_color(red_key, red)
        lookup.set_color(blue_key, blue)

        self.assertEqual(Nothing, lookup.get_color("green"))
        self.assertEqual(red, lookup.get_color(red_key).unwrap())
        self.assertEqual(blue, lookup.get_color(blue_key).unwrap())

        lookup.clear_color(blue_key)

        self.assertEqual(Nothing, lookup.get_color(blue_key))

    def test_lookup_font(self):
        lookup = StyleLookup()

        sans = CairoFont("Sans", ToyFontFace("Sans"))
        serif = CairoFont("Serif", ToyFontFace("Serif"))

        label_key = "label"
        button_key = "button"

        lookup.set_font(label_key, sans)
        lookup.set_font(button_key, serif)

        self.assertEqual(Nothing, lookup.get_font("dialog"))
        self.assertEqual(sans, lookup.get_font(label_key).unwrap())
        self.assertEqual(serif, lookup.get_font(button_key).unwrap())

        lookup.clear_font(label_key)

        self.assertEqual(Nothing, lookup.get_font(label_key))

    def test_lookup_insets(self):
        lookup = StyleLookup()

        padding = Insets(5, 5, 5, 5)
        margin = Insets(10, 10, 10, 10)

        padding_key = "padding"
        margin_key = "margin"

        lookup.set_insets(padding_key, padding)
        lookup.set_insets(margin_key, margin)

        self.assertEqual(Nothing, lookup.get_insets("button_padding"))
        self.assertEqual(padding, lookup.get_insets(padding_key).unwrap())
        self.assertEqual(margin, lookup.get_insets(margin_key).unwrap())

        lookup.clear_insets(padding_key)

        self.assertEqual(Nothing, lookup.get_insets(padding_key))

    def test_on_style_change(self):
        lookup = StyleLookup()

        changes = []

        lookup.on_style_change.subscribe(changes.append)

        self.assertEqual([], changes)

        lookup.set_color("color1", RGBA(1, 0, 0, 1))
        lookup.set_color("color1", RGBA(1, 0, 0, 1))  # Should ignore duplicated requests.

        self.assertEqual([ColorChangeEvent(lookup, "color1", Some(RGBA(1, 0, 0, 1)))], changes)

        lookup.set_color("color2", RGBA(0, 1, 0, 1))

        self.assertEqual([ColorChangeEvent(lookup, "color2", Some(RGBA(0, 1, 0, 1)))], changes[1:])

        lookup.set_color("color2", RGBA(0, 1, 1, 1))

        self.assertEqual([ColorChangeEvent(lookup, "color2", Some(RGBA(0, 1, 1, 1)))], changes[2:])

        font = CairoFont("Sans", ToyFontFace("Sans"))

        lookup.set_font("font1", font)

        self.assertEqual([FontChangeEvent(lookup, "font1", Some(font))], changes[3:])

        lookup.clear_color("color1")
        lookup.clear_font("font1")

        self.assertEqual([ColorChangeEvent(lookup, "color1", Nothing)], changes[4:5])
        self.assertEqual([FontChangeEvent(lookup, "font1", Nothing)], changes[5:])

        padding = Insets(5, 5, 5, 5)

        lookup.set_insets("padding", padding)

        self.assertEqual([InsetsChangeEvent(lookup, "padding", Some(padding))], changes[6:])

        lookup.clear_insets("padding")

        self.assertEqual([InsetsChangeEvent(lookup, "padding", Nothing)], changes[7:])


if __name__ == '__main__':
    unittest.main()
