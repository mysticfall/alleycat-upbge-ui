import unittest

from returns.maybe import Nothing

from alleycat.ui import StyleLookup, RGBA


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


if __name__ == '__main__':
    unittest.main()
