import unittest

from alleycat.ui import Label, Bounds, Window, RGBA
from alleycat.ui.cairo import UI
from alleycat.ui.glass import ColorKeys
from tests.ui import UITestCase


class LabelTest(UITestCase):
    def test_draw(self):
        context = UI().create_context()

        window = Window(context)
        window.bounds = Bounds(0, 0, 100, 60)

        label = Label(context)

        label.text = "Label"
        label.bounds = Bounds(10, 20, 60, 30)

        label2 = Label(context)

        label2.text = "Test"
        label2.size = 20
        label2.set_color(ColorKeys.Text, RGBA(1, 0, 0, 1))
        label2.bounds = Bounds(0, 0, 80, 60)

        window.add(label)
        window.add(label2)

        context.process()

        self.assertImage("draw", context)


if __name__ == '__main__':
    unittest.main()
