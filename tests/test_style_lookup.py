import unittest

from cairo import ToyFontFace
from returns.maybe import Nothing

from alleycat.ui import StyleLookup, RGBA
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


if __name__ == '__main__':
    unittest.main()
