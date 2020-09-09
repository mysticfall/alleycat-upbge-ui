import unittest

from alleycat.ui import MouseMoveEvent, Point, Component
from alleycat.ui.cairo import UI


class EventTest(unittest.TestCase):

    def test_propagation(self):
        context = UI().create_context()
        component = Component(context)

        event = MouseMoveEvent(component, Point(10, 10))

        self.assertFalse(event.propagation_stopped)

        event.stop_propagation()

        self.assertTrue(event.propagation_stopped)


if __name__ == '__main__':
    unittest.main()
