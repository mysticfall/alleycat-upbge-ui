import unittest

from alleycat.reactive import functions as rv
from returns.maybe import Some, Nothing

from alleycat.ui import Container, Component, Bounds, Point
from alleycat.ui.cairo import UI


class ContainerTest(unittest.TestCase):
    def test_children(self):
        context = UI().create_context()

        container = Container(context)

        children = []

        rv.observe(container, "children").subscribe(children.append)

        child1 = Component(context)
        child2 = Component(context)

        self.assertEqual([()], children)

        container.add(child1)

        self.assertEqual((child1,), container.children)
        self.assertEqual([(), (child1,)], children)

        container.add(child2)

        self.assertEqual((child1, child2), container.children)
        self.assertEqual([(), (child1,), (child1, child2)], children)

        container.remove(child1)

        self.assertEqual((child2,), container.children)

    def test_component_at(self):
        context = UI().create_context()

        parent = Container(context)
        parent.bounds = Bounds(0, 0, 200, 200)

        child = Container(context)
        child.bounds = Bounds(50, 50, 100, 100)

        grand_child = Container(context)
        grand_child.bounds = Bounds(25, 25, 50, 50)

        child.add(grand_child)
        parent.add(child)

        self.assertEqual(Nothing, parent.component_at(Point(-1, 0)))
        self.assertEqual(Nothing, parent.component_at(Point(201, 0)))
        self.assertEqual(Nothing, parent.component_at(Point(200, 201)))
        self.assertEqual(Nothing, parent.component_at(Point(-1, 200)))

        self.assertEqual(Some(parent), parent.component_at(Point(50, 49)))
        self.assertEqual(Some(parent), parent.component_at(Point(151, 50)))
        self.assertEqual(Some(parent), parent.component_at(Point(150, 151)))
        self.assertEqual(Some(parent), parent.component_at(Point(49, 150)))

        self.assertEqual(Some(child), parent.component_at(Point(50, 50)))
        self.assertEqual(Some(child), parent.component_at(Point(150, 50)))
        self.assertEqual(Some(child), parent.component_at(Point(150, 150)))
        self.assertEqual(Some(child), parent.component_at(Point(50, 150)))

        self.assertEqual(Some(grand_child), parent.component_at(Point(75, 75)))
        self.assertEqual(Some(grand_child), parent.component_at(Point(125, 75)))
        self.assertEqual(Some(grand_child), parent.component_at(Point(125, 125)))
        self.assertEqual(Some(grand_child), parent.component_at(Point(75, 125)))

        self.assertEqual(Some(child), parent.component_at(Point(74, 75)))
        self.assertEqual(Some(child), parent.component_at(Point(125, 74)))
        self.assertEqual(Some(child), parent.component_at(Point(126, 125)))
        self.assertEqual(Some(child), parent.component_at(Point(75, 126)))


if __name__ == '__main__':
    unittest.main()
