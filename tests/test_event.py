import unittest

from alleycat.ui import MouseMoveEvent, Point, Component
from tests.ui import UITestCase


class EventTest(UITestCase):

    def test_propagation(self):
        component = Component(self.context)

        event = MouseMoveEvent(component, Point(10, 10))

        self.assertFalse(event.propagation_stopped)

        event.stop_propagation()

        self.assertTrue(event.propagation_stopped)


if __name__ == '__main__':
    unittest.main()
