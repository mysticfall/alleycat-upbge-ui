import unittest
from typing import Iterable

from alleycat.reactive import functions as rv
from returns.maybe import Nothing, Some

from alleycat.ui import Bounds, Component, ComponentUI, Container, Dimension, Graphics, MouseMoveEvent, Panel, Point, \
    RGBA
from alleycat.ui.component import T
from tests.ui import UITestCase


# noinspection DuplicatedCode
class ComponentTest(UITestCase):

    def test_offset(self):
        parent = Panel(self.context)
        parent.bounds = Bounds(10, 20, 80, 60)

        grand_parent = Container(self.context)
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
        parent = Container(self.context)
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

    def test_validation(self):
        minimum_size = Dimension(10, 10)
        preferred_size = Dimension(20, 20)

        class FixtureComponent(Component):
            def create_ui(self) -> ComponentUI:
                return FixtureUI()

        class FixtureUI(ComponentUI):
            def minimum_size(self, component: T) -> Dimension:
                return minimum_size

            def preferred_size(self, component: T) -> Dimension:
                return preferred_size

            def draw(self, g: Graphics, component: T) -> None:
                pass

        fixture = FixtureComponent(self.context)

        self.assertEqual(True, fixture.valid)

        fixture.invalidate()

        self.assertEqual(False, fixture.valid)

        fixture.validate()

        self.assertEqual(True, fixture.valid)

        minimum_size = Dimension(30, 30)
        preferred_size = Dimension(40, 40)

        self.assertEqual(Dimension(10, 10), fixture.minimum_size)
        self.assertEqual(Dimension(20, 20), fixture.preferred_size)

        fixture.validate()

        self.assertEqual(Dimension(10, 10), fixture.minimum_size)
        self.assertEqual(Dimension(20, 20), fixture.preferred_size)

        fixture.validate(force=True)

        self.assertEqual(Dimension(30, 30), fixture.minimum_size)
        self.assertEqual(Dimension(40, 40), fixture.preferred_size)

    def test_minimum_size(self):
        minimum_size = Dimension(10, 10)

        class FixtureComponent(Component):
            def create_ui(self) -> ComponentUI:
                return FixtureUI()

        class FixtureUI(ComponentUI):
            def minimum_size(self, component: T) -> Dimension:
                return minimum_size

            def draw(self, g: Graphics, component: T) -> None:
                pass

        fixture = FixtureComponent(self.context)

        sizes = []
        effective_sizes = []

        rv.observe(fixture.minimum_size_override).subscribe(sizes.append)
        rv.observe(fixture.minimum_size).subscribe(effective_sizes.append)

        self.assertEqual(Nothing, fixture.minimum_size_override)
        self.assertEqual(Dimension(10, 10), fixture.minimum_size)
        self.assertEqual([Nothing], sizes)
        self.assertEqual([Dimension(10, 10)], effective_sizes)

        fixture.bounds = Bounds(10, 20, 100, 50)
        fixture.validate(force=True)

        self.assertEqual(Bounds(10, 20, 100, 50), fixture.bounds)

        fixture.minimum_size_override = Some(Dimension(200, 100))
        fixture.validate(force=True)

        self.assertEqual(Some(Dimension(200, 100)), fixture.minimum_size_override)
        self.assertEqual(Dimension(200, 100), fixture.minimum_size)
        self.assertEqual([Some(Dimension(200, 100))], sizes[1:])
        self.assertEqual([Dimension(200, 100)], effective_sizes[1:])
        self.assertEqual(Bounds(10, 20, 200, 100), fixture.bounds)

        minimum_size = Dimension(240, 260)
        fixture.validate(force=True)

        self.assertEqual(Some(Dimension(200, 100)), fixture.minimum_size_override)
        self.assertEqual(Dimension(200, 100), fixture.minimum_size)
        self.assertEqual(2, len(effective_sizes))
        self.assertEqual([Some(Dimension(200, 100))], sizes[1:])
        self.assertEqual([Dimension(200, 100)], effective_sizes[1:])
        self.assertEqual(Bounds(10, 20, 200, 100), fixture.bounds)

        fixture.bounds = Bounds(0, 0, 30, 40)
        fixture.validate(force=True)

        self.assertEqual(Bounds(0, 0, 200, 100), fixture.bounds)

        fixture.minimum_size_override = Nothing
        fixture.validate(force=True)

        self.assertEqual(Nothing, fixture.minimum_size_override)
        self.assertEqual(Dimension(240, 260), fixture.minimum_size)
        self.assertEqual(3, len(effective_sizes))
        self.assertEqual([Nothing], sizes[2:])
        self.assertEqual([Dimension(240, 260)], effective_sizes[2:])
        self.assertEqual(Bounds(0, 0, 240, 260), fixture.bounds)

    def test_preferred_size(self):
        preferred_size = Dimension(10, 10)

        class FixtureComponent(Component):
            pass

        class FixtureUI(ComponentUI):
            def preferred_size(self, component: T) -> Dimension:
                return preferred_size

            def draw(self, g: Graphics, component: T) -> None:
                pass

        self.context.look_and_feel.register_ui(FixtureComponent, FixtureUI)

        fixture = FixtureComponent(self.context)

        sizes = []
        effective_sizes = []

        rv.observe(fixture.preferred_size_override).subscribe(sizes.append)
        rv.observe(fixture.preferred_size).subscribe(effective_sizes.append)

        self.assertEqual(Nothing, fixture.preferred_size_override)
        self.assertEqual(Dimension(10, 10), fixture.preferred_size)
        self.assertEqual([Nothing], sizes)
        self.assertEqual([Dimension(10, 10)], effective_sizes)

        fixture.preferred_size_override = Some(Dimension(100, 80))
        fixture.validate(force=True)

        self.assertEqual(Some(Dimension(100, 80)), fixture.preferred_size_override)
        self.assertEqual(Dimension(100, 80), fixture.preferred_size)
        self.assertEqual([Some(Dimension(100, 80))], sizes[1:])
        self.assertEqual([Dimension(100, 80)], effective_sizes[1:])

        preferred_size = Dimension(240, 300)
        fixture.validate(force=True)

        self.assertEqual(Some(Dimension(100, 80)), fixture.preferred_size_override)
        self.assertEqual(Dimension(100, 80), fixture.preferred_size)
        self.assertEqual([Some(Dimension(100, 80))], sizes[1:])
        self.assertEqual([Dimension(100, 80)], effective_sizes[1:])

        fixture.preferred_size_override = Nothing
        fixture.validate(force=True)

        self.assertEqual(Nothing, fixture.preferred_size_override)
        self.assertEqual(Dimension(240, 300), fixture.preferred_size)
        self.assertEqual([Nothing], sizes[2:])
        self.assertEqual([Dimension(240, 300)], effective_sizes[2:])

        fixture.minimum_size_override = Some(Dimension(400, 360))
        fixture.validate(force=True)

        self.assertEqual(Dimension(400, 360), fixture.preferred_size)
        self.assertEqual([Dimension(400, 360)], effective_sizes[3:])

        fixture.preferred_size_override = Some(Dimension(300, 300))
        fixture.validate(force=True)

        self.assertEqual(Dimension(400, 360), fixture.preferred_size)
        self.assertEqual([Some(Dimension(400, 360))], sizes[3:])
        self.assertEqual([Dimension(400, 360)], effective_sizes[3:])


if __name__ == '__main__':
    unittest.main()
