import unittest

from returns.maybe import Nothing, Maybe, Some

from alleycat.ui import StyleLookup, ColorKey, RGBA


class StyleLookupTest(unittest.TestCase):
    def test_lookup_color(self):
        lookup = StyleLookup()

        red = RGBA(1, 0, 0, 1)
        blue = RGBA(0, 0, 1, 1)

        red_key = ColorKey()
        blue_key = ColorKey()

        lookup.set_color(red_key, red)
        lookup.set_color(blue_key, blue)

        self.assertEqual(Nothing, lookup.get_color(ColorKey()))
        self.assertEqual(red, lookup.get_color(red_key).unwrap())
        self.assertEqual(blue, lookup.get_color(blue_key).unwrap())

    def test_fallback(self):
        parent = StyleLookup()

        class Child(StyleLookup):
            @property
            def style_fallback(self) -> Maybe[StyleLookup]:
                return Some(parent)

        child = Child()

        red = RGBA(1, 0, 0, 1)
        red_key = ColorKey()

        parent.set_color(red_key, red)

        self.assertEqual(red, child.get_color(red_key).unwrap())


if __name__ == '__main__':
    unittest.main()
