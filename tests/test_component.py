import unittest
from typing import Iterable

from returns.maybe import Nothing

from alleycat.ui import Component, Panel, Bounds, Point, MouseMoveEvent, LayoutContainer, RGBA
from tests.ui import UITestCase


class ComponentTest(UITestCase):

    def test_offset(self):
        parent = Panel(self.context)
        parent.bounds = Bounds(10, 20, 80, 60)

        grand_parent = LayoutContainer(self.context)
        grand_parent.bounds = Bounds(20, 10, 40, 20)

        component = Component(self.context)
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

    def test_position_of(self):
        parent = LayoutContainer(self.context)
        parent.bounds = Bounds(10, 20, 80, 60)

        component = Component(self.context)
        component.bounds = Bounds(5, 5, 10, 10)

        parent.add(component)

        event = MouseMoveEvent(component, Point(30, 40))

        self.assertEqual(Point(20, 20), component.position_of(event))

    def test_resolve_color(self):
        class Fixture(Component):
            @property
            def style_fallback_prefixes(self) -> Iterable[str]:
                yield "Type"
                yield "Parent"
                yield "GrandParent"

        fixture = Fixture(self.context)

        prefixes = list(fixture.style_fallback_prefixes)
        keys = list(fixture.style_fallback_keys("color"))

        laf = self.context.look_and_feel

        self.assertEqual(["Type", "Parent", "GrandParent"], prefixes)
        self.assertEqual(["Type.color", "Parent.color", "GrandParent.color", "color"], keys)

        self.assertEqual(Nothing, fixture.resolve_color("color"))

        laf.set_color("GrandParent.color", RGBA(1, 0, 0, 1))
        self.assertEqual(RGBA(1, 0, 0, 1), fixture.resolve_color("color").unwrap())

        laf.set_color("GreatGrandParent.color", RGBA(0, 0, 0, 1))
        self.assertEqual(RGBA(1, 0, 0, 1), fixture.resolve_color("color").unwrap())

        fixture.set_color("color", RGBA(0, 1, 0, 1))
        self.assertEqual(RGBA(0, 1, 0, 1), fixture.resolve_color("color").unwrap())

        laf.set_color("color", RGBA(1, 1, 1, 1))
        self.assertEqual(RGBA(0, 1, 0, 1), fixture.resolve_color("color").unwrap())


if __name__ == '__main__':
    unittest.main()
