import unittest
from typing import Set, cast

from returns.iterables import Fold
from returns.maybe import Nothing, Some

from alleycat.ui import Bounds, Component, Container, Dimension, Insets, Panel, RGBA, Window
from alleycat.ui.glass import StyleKeys
from alleycat.ui.layout import Border, BorderItem, BorderLayout
from tests.ui import UITestCase


# noinspection DuplicatedCode
class BorderLayoutTest(UITestCase):

    def create_container(self, areas: Set[Border]) -> Container:
        container = Window(self.context, BorderLayout())
        container.bounds = Bounds(5, 5, 90, 90)

        if Border.Top in areas:
            top = Panel(self.context)
            top.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))
            top.preferred_size_override = Some(Dimension(0, 20))

            container.add(top, Border.Top)

        if Border.Right in areas:
            right = Panel(self.context)
            right.set_color(StyleKeys.Background, RGBA(0, 1, 0, 1))
            right.preferred_size_override = Some(Dimension(15, 0))

            container.add(right, Border.Right)

        if Border.Bottom in areas:
            bottom = Panel(self.context)
            bottom.set_color(StyleKeys.Background, RGBA(0, 0, 1, 1))
            bottom.preferred_size_override = Some(Dimension(0, 20))

            container.add(bottom, Border.Bottom)

        if Border.Left in areas:
            left = Panel(self.context)
            left.set_color(StyleKeys.Background, RGBA(1, 1, 1, 1))
            left.preferred_size_override = Some(Dimension(5, 0))

            container.add(left, Border.Left)

        if Border.Center in areas:
            center = Panel(self.context)
            center.set_color(StyleKeys.Background, RGBA(0, 0, 0, 1))

            container.add(center, Border.Center)

        return container

    def test_layout(self):
        def test(areas: Set[Border]):
            with self.create_container(areas) as container:
                self.assertEqual(True, container.layout_pending)
                self.context.process()
                self.assertEqual(False, container.layout_pending)

                names = sorted(map(lambda a: a.name, areas))

                self.assertImage(f"border-{'-'.join(names)}", self.context)

        for area in Border:
            test({area})

        test({Border.Center, Border.Top})
        test({Border.Center, Border.Left, Border.Right})
        test({Border.Center, Border.Top, Border.Right})
        test({Border.Center, Border.Top, Border.Bottom})
        test({Border.Left, Border.Right})
        test({Border.Top, Border.Bottom})
        test({Border.Center, Border.Top, Border.Left, Border.Right})
        test({Border.Center, Border.Top, Border.Bottom, Border.Right})

        test(set(Border))

    def test_item_visibility(self):
        def test(areas: Set[Border]):
            with self.create_container(set(Border)) as container:
                layout = cast(BorderLayout, container.layout)

                for b in Border:
                    layout.areas[b].component.map(lambda c: setattr(c, "visible", b in areas))

                self.assertEqual(True, container.layout_pending)
                self.context.process()
                self.assertEqual(False, container.layout_pending)

                names = sorted(map(lambda a: a.name, areas))

                self.assertImage(f"border-{'-'.join(names)}", self.context)

        for area in Border:
            test({area})

        test({Border.Center, Border.Top})
        test({Border.Center, Border.Left, Border.Right})
        test({Border.Center, Border.Top, Border.Right})
        test({Border.Center, Border.Top, Border.Bottom})
        test({Border.Left, Border.Right})
        test({Border.Top, Border.Bottom})
        test({Border.Center, Border.Top, Border.Left, Border.Right})
        test({Border.Center, Border.Top, Border.Bottom, Border.Right})

        test(set(Border))

    def test_items(self):
        layout = BorderLayout()

        container = Window(self.context, layout)

        child1 = Panel(self.context)
        child2 = Panel(self.context)
        child3 = Panel(self.context)
        child4 = Panel(self.context)
        child5 = Panel(self.context)

        container.add(child1)
        container.add(child2, Border.Left)
        container.add(child3, Border.Top, Insets(2, 2, 2, 2))
        container.add(child4, Border.Right, padding=Insets(5, 5, 5, 5))
        container.add(child5, region=Border.Bottom, padding=Insets(10, 10, 10, 10))

        def assert_item(item: BorderItem, child: Component, border: Border, padding: Insets) -> None:
            self.assertEqual(child, item.component.unwrap())
            self.assertEqual(border, item.border)
            self.assertEqual(padding, item.padding)

        assert_item(layout.areas[Border.Center], child1, Border.Center, Insets(0, 0, 0, 0))
        assert_item(layout.areas[Border.Top], child3, Border.Top, Insets(2, 2, 2, 2))
        assert_item(layout.areas[Border.Right], child4, Border.Right, Insets(5, 5, 5, 5))
        assert_item(layout.areas[Border.Bottom], child5, Border.Bottom, Insets(10, 10, 10, 10))
        assert_item(layout.areas[Border.Left], child2, Border.Left, Insets(0, 0, 0, 0))

        container.add(child1, Border.Right)
        container.remove(child2)
        container.remove(child3)

        assert_item(layout.areas[Border.Right], child1, Border.Right, Insets(0, 0, 0, 0))

        # noinspection PyTypeChecker
        children = Fold.collect_all(map(lambda a: a.component, layout.areas.values()), Some(())).unwrap()

        self.assertEqual({child5, child1}, set(children))
        self.assertEqual(Nothing, layout.areas[Border.Top].component)
        self.assertEqual(Some(child1), layout.areas[Border.Right].component)
        self.assertEqual(Some(child5), layout.areas[Border.Bottom].component)
        self.assertEqual(Nothing, layout.areas[Border.Left].component)


if __name__ == '__main__':
    unittest.main()
