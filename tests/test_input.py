import unittest
from typing import cast

from alleycat.ui import Bounds, Component, FakeMouseInput, Point, Window, MouseMoveEvent
from alleycat.ui.cairo import UI


class InputTest(unittest.TestCase):

    def test_mouse_move(self):
        context = UI().create_context()

        mouse_input = cast(FakeMouseInput, context.mouse_input)

        parent = Window(context)
        parent.bounds = Bounds(20, 20, 60, 60)

        component = Component(context)
        component.bounds = Bounds(10, 10, 20, 20)

        parent.add(component)

        events = []
        parent_events = []

        component.on_mouse_move.subscribe(events.append)
        parent.on_mouse_move.subscribe(parent_events.append)

        mouse_input.move_to(Point(10, 10))

        self.assertEqual([], events)
        self.assertEqual([], parent_events)

        mouse_input.move_to(Point(20, 20))

        self.assertEqual([], events)
        self.assertEqual([MouseMoveEvent(parent, Point(20, 20))], parent_events)

        mouse_input.move_to(Point(30, 30))

        self.assertEqual([MouseMoveEvent(component, Point(30, 30))], events)
        self.assertEqual([
            MouseMoveEvent(parent, Point(20, 20)),
            MouseMoveEvent(parent, Point(30, 30))], parent_events)


if __name__ == '__main__':
    unittest.main()
