import unittest

from returns.maybe import Some

from alleycat.ui import Bounds, Component, Container, Dimension, Frame, Panel, RGBA
from alleycat.ui.glass import StyleKeys
from alleycat.ui.layout import Anchor, AnchorLayout, Direction
from ui import UITestCase


# noinspection DuplicatedCode
class AnchorLayoutTest(UITestCase):

    def setUp(self) -> None:
        super().setUp()

        self.container = Frame(self.context, AnchorLayout())
        self.container.bounds = Bounds(0, 0, 100, 100)

        self.child = Panel(self.context)
        self.child.preferred_size_override = Some(Dimension(40, 30))
        self.child.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))

    def test_no_anchor(self):
        self.context.process()
        self.assertImage("no-anchor", self.context)

        self.child.preferred_size_override = Some(Dimension(120, 130))

        self.context.process()
        self.assertImage("no-anchor-over-sized", self.context)

        self.child.minimum_size_override = Some(Dimension(60, 40))
        self.container.bounds = Bounds(0, 0, 50, 50)

        self.context.process()
        self.assertImage("no-anchor-min-size", self.context)

    def test_constraints(self):
        self.container.add(self.child, Anchor(Direction.Right, 15))

        self.context.process()
        self.assertImage("constraints", self.context)

        self.container.add(self.child, Direction.Right, 15)

        self.context.process()
        self.assertImage("constraints", self.context)

        self.container.add(self.child, direction=Direction.Right, distance=15)

        self.context.process()
        self.assertImage("constraints", self.context)

    def test_edges(self):
        for direction in Direction:
            for distance in [0, 10]:
                prefix = f"edge-{direction.name}-{distance}"

                self._perform_test(prefix, self.container, self.child, Anchor(direction, distance))

    def test_corners(self):
        corners = (
            (Anchor(Direction.Top), Anchor(Direction.Right)),
            (Anchor(Direction.Right), Anchor(Direction.Bottom)),
            (Anchor(Direction.Left), Anchor(Direction.Bottom)),
            (Anchor(Direction.Left), Anchor(Direction.Top)))

        for (c1, c2) in corners:
            for distance in [0, 10]:
                prefix = f"corner-{c1.direction.name}-{c2.direction.name}-{distance}"

                self._perform_test(
                    prefix, self.container, self.child, Anchor(c1.direction, distance), Anchor(c2.direction, distance))

    def test_stretch(self):
        stretches = ((True, False), (False, True), (True, True))

        for (horizontal, vertical) in stretches:
            for distance in [0, 10]:
                anchors = ()

                if horizontal:
                    name = "both" if vertical else "horizontal"
                    anchors += (Anchor(Direction.Left, distance), Anchor(Direction.Right, distance))
                else:
                    name = "vertical" if vertical else "none"

                if vertical:
                    anchors += (Anchor(Direction.Top, distance), Anchor(Direction.Bottom, distance))

                prefix = f"stretch-{name}-{distance}"

                self._perform_test(prefix, self.container, self.child, *anchors)

    def test_stretch_three_corners(self):
        for direction in Direction:
            for distance in [0, 10]:
                anchors = [Anchor(d, distance) for d in Direction if d != direction]

                prefix = f"stretch-except-{direction.name}-{distance}"

                self._perform_test(prefix, self.container, self.child, *anchors)

    def _perform_test(self, prefix: str, parent: Container, child: Component, *anchors: Anchor):
        child.preferred_size_override = Some(Dimension(60, 40))

        parent.add(child, *anchors)
        parent.bounds = Bounds(0, 0, 100, 100)

        self.context.process()
        self.assertImage(prefix, self.context)

        parent.bounds = Bounds(0, 0, 60, 60)

        self.context.process()
        self.assertImage(f"{prefix}-half-size", self.context)

        child.preferred_size_override = Some(Dimension(80, 60))
        child.minimum_size_override = Some(Dimension(60, 30))

        self.context.process()
        self.assertImage(f"{prefix}-min-size", self.context)

        parent.bounds = Bounds(0, 0, 100, 100)

        self.context.process()
        self.assertImage(f"{prefix}-pref-size", self.context)


if __name__ == '__main__':
    unittest.main()
