import unittest

from alleycat.reactive import functions as rv

from alleycat.ui import Container, Component
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


if __name__ == '__main__':
    unittest.main()
