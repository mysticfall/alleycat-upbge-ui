import unittest

from alleycat.ui import Component, Panel, Bounds, Point
from alleycat.ui.cairo import UI


class ComponentTest(unittest.TestCase):

    def test_offset(self):
        context = UI().create_context()

        parent = Panel(context)
        parent.bounds = Bounds(10, 20, 80, 60)

        grand_parent = Panel(context)
        grand_parent.bounds = Bounds(20, 10, 40, 20)

        component = Component(context)
        component.bounds = Bounds(5, 5, 10, 10)

        self.assertEqual(Point(0, 0), component.offset)

        component.bounds = Bounds(10, 20, 10, 10)

        self.assertEqual(Point(0, 0), component.offset)

        parent.add(component)

        self.assertEqual(Point(10, 20), component.offset)

        parent.bounds = parent.bounds.copy(x=30, y=-10)

        self.assertEqual(Point(30, -10), component.offset)

        grand_parent.add(parent)

        self.assertEqual(Point(50, 0), component.offset)

        grand_parent.bounds = grand_parent.bounds.copy(x=-10, y=50)

        self.assertEqual(Point(20, 40), component.offset)


if __name__ == '__main__':
    unittest.main()
