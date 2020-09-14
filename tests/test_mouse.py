import unittest
from typing import cast

from alleycat.ui import Bounds, Component, FakeMouseInput, Point, Window, MouseMoveEvent, MouseInput, MouseOverEvent, \
    MouseOutEvent
from alleycat.ui import MouseButton, MouseDownEvent, MouseUpEvent
from alleycat.ui.cairo import UI


# noinspection DuplicatedCode
class MouseTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.context = UI().create_context()

        self.mouse_input = cast(FakeMouseInput, MouseInput.input(self.context))

        self.parent = Window(self.context)
        self.parent.bounds = Bounds(20, 20, 60, 60)

        self.component = Component(self.context)
        self.component.bounds = Bounds(10, 10, 20, 20)

        self.parent.add(self.component)

        self.input = cast(FakeMouseInput, MouseInput.input(self.context))

    def tearDown(self) -> None:
        super().tearDown()

        self.context.dispose()

    def test_buttons(self):
        self.assertEqual(0, self.input.buttons)

        self.assertFalse(self.input.pressed(MouseButton.LEFT))
        self.assertFalse(self.input.pressed(MouseButton.MIDDLE))
        self.assertFalse(self.input.pressed(MouseButton.RIGHT))

        self.input.press(MouseButton.LEFT)

        self.assertTrue(self.input.pressed(MouseButton.LEFT))
        self.assertFalse(self.input.pressed(MouseButton.MIDDLE))
        self.assertFalse(self.input.pressed(MouseButton.RIGHT))

        self.input.press(MouseButton.RIGHT)

        self.assertTrue(self.input.pressed(MouseButton.LEFT))
        self.assertFalse(self.input.pressed(MouseButton.MIDDLE))
        self.assertTrue(self.input.pressed(MouseButton.RIGHT))

        self.input.release(MouseButton.RIGHT)

        self.assertTrue(self.input.pressed(MouseButton.LEFT))
        self.assertFalse(self.input.pressed(MouseButton.MIDDLE))
        self.assertFalse(self.input.pressed(MouseButton.RIGHT))

    def test_mouse_move(self):
        events = []
        parent_events = []

        self.component.on_mouse_move.subscribe(events.append)
        self.parent.on_mouse_move.subscribe(parent_events.append)

        self.input.move_to(Point(10, 10))

        self.assertEqual([], events)
        self.assertEqual([], parent_events)

        self.input.move_to(Point(20, 20))

        self.assertEqual([], events)
        self.assertEqual([MouseMoveEvent(self.parent, Point(20, 20))], parent_events)

        self.input.move_to(Point(30, 30))

        self.assertEqual([MouseMoveEvent(self.component, Point(30, 30))], events)
        self.assertEqual([
            MouseMoveEvent(self.parent, Point(20, 20)),
            MouseMoveEvent(self.parent, Point(30, 30))], parent_events)

    def test_mouse_down(self):
        events = []
        parent_events = []

        self.component.on_mouse_down.subscribe(events.append)
        self.parent.on_mouse_down.subscribe(parent_events.append)

        self.input.move_to(Point(10, 10))

        self.input.click(MouseButton.LEFT)

        self.assertEqual([], events)
        self.assertEqual([], parent_events)

        self.input.move_to(Point(20, 20))

        self.input.press(MouseButton.LEFT)
        self.input.click(MouseButton.RIGHT)

        self.assertEqual([], events)

        self.assertEqual([
            MouseDownEvent(self.parent, Point(20, 20), MouseButton.LEFT),
            MouseDownEvent(self.parent, Point(20, 20), MouseButton.RIGHT)
        ], parent_events)

        self.input.release(MouseButton.LEFT)

        self.input.move_to(Point(30, 30))

        self.input.click(MouseButton.MIDDLE)
        self.input.click(MouseButton.LEFT)

        self.assertEqual([
            MouseDownEvent(self.component, Point(30, 30), MouseButton.MIDDLE),
            MouseDownEvent(self.component, Point(30, 30), MouseButton.LEFT)
        ], events)

        self.assertEqual([
            MouseDownEvent(self.parent, Point(30, 30), MouseButton.MIDDLE),
            MouseDownEvent(self.parent, Point(30, 30), MouseButton.LEFT)
        ], parent_events[2:])

    def test_mouse_up(self):
        events = []
        parent_events = []

        self.component.on_mouse_up.subscribe(events.append)
        self.parent.on_mouse_up.subscribe(parent_events.append)

        self.input.move_to(Point(10, 10))

        self.input.click(MouseButton.LEFT)

        self.assertEqual([], events)
        self.assertEqual([], parent_events)

        self.input.move_to(Point(20, 20))

        self.input.press(MouseButton.LEFT)
        self.input.click(MouseButton.RIGHT)

        self.assertEqual([], events)
        self.assertEqual([MouseUpEvent(self.parent, Point(20, 20), MouseButton.RIGHT)], parent_events)

        self.input.move_to(Point(30, 30))

        self.input.release(MouseButton.LEFT)

        self.input.click(MouseButton.MIDDLE)
        self.input.click(MouseButton.LEFT)

        self.assertEqual([
            MouseUpEvent(self.component, Point(30, 30), MouseButton.LEFT),
            MouseUpEvent(self.component, Point(30, 30), MouseButton.MIDDLE),
            MouseUpEvent(self.component, Point(30, 30), MouseButton.LEFT)
        ], events)

        self.assertEqual([
            MouseUpEvent(self.parent, Point(30, 30), MouseButton.LEFT),
            MouseUpEvent(self.parent, Point(30, 30), MouseButton.MIDDLE),
            MouseUpEvent(self.parent, Point(30, 30), MouseButton.LEFT)
        ], parent_events[1:])

    def test_mouse_over(self):
        events = []
        parent_events = []

        self.component.on_mouse_over.subscribe(events.append)
        self.parent.on_mouse_over.subscribe(parent_events.append)

        self.input.move_to(Point(10, 10))

        self.assertEqual([], events)
        self.assertEqual([], parent_events)

        self.input.move_to(Point(20, 20))

        self.assertEqual([], events)
        self.assertEqual([MouseOverEvent(self.parent, Point(20, 20))], parent_events)

        self.input.move_to(Point(25, 25))

        self.assertEqual([], events)
        self.assertEqual([MouseOverEvent(self.parent, Point(20, 20))], parent_events)

        self.input.move_to(Point(30, 30))
        self.input.move_to(Point(40, 40))

        self.assertEqual([MouseOverEvent(self.component, Point(30, 30))], events)
        self.assertEqual([MouseOverEvent(self.parent, Point(20, 20))], parent_events)

        self.input.move_to(Point(20, 20))
        self.input.move_to(Point(40, 40))

        self.assertEqual([
            MouseOverEvent(self.component, Point(30, 30)),
            MouseOverEvent(self.component, Point(40, 40))
        ], events)

        self.assertEqual([MouseOverEvent(self.parent, Point(20, 20))], parent_events)

    def test_mouse_out(self):
        events = []
        parent_events = []

        self.component.on_mouse_out.subscribe(events.append)
        self.parent.on_mouse_out.subscribe(parent_events.append)

        self.input.move_to(Point(10, 10))

        self.assertEqual([], events)
        self.assertEqual([], parent_events)

        self.input.move_to(Point(20, 20))

        self.assertEqual([], events)
        self.assertEqual([], parent_events)

        self.input.move_to(Point(10, 10))

        self.assertEqual([], events)
        self.assertEqual([MouseOutEvent(self.parent, Point(10, 10))], parent_events)

        self.input.move_to(Point(30, 30))
        self.input.move_to(Point(20, 20))

        self.assertEqual([MouseOutEvent(self.component, Point(20, 20))], events)
        self.assertEqual([MouseOutEvent(self.parent, Point(10, 10))], parent_events)

        self.input.move_to(Point(0, 0))

        self.assertEqual([MouseOutEvent(self.component, Point(20, 20))], events)
        self.assertEqual([
            MouseOutEvent(self.parent, Point(10, 10)),
            MouseOutEvent(self.parent, Point(0, 0))
        ], parent_events)


if __name__ == '__main__':
    unittest.main()
