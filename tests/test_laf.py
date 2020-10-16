import unittest

from alleycat.ui import Panel, ComponentUI, Graphics, LayoutContainer, LookAndFeel, LabelButton, Button, Label
from alleycat.ui.component import T, Component
from alleycat.ui.glass import GlassPanelUI, GlassComponentUI, GlassLabelUI, GlassButtonUI, GlassLabelButtonUI
from tests.ui import UITestCase


# noinspection DuplicatedCode
class LookAndFeelTest(UITestCase):
    def test_register_ui(self):
        laf = self.context.look_and_feel

        class CustomPanelUI(ComponentUI[Panel]):
            def draw(self, g: Graphics, component: T) -> None:
                pass

        laf.register_ui(Panel, CustomPanelUI)

        panel_ui = laf.create_ui(Panel(self.context))
        container_ui = laf.create_ui(LayoutContainer(self.context))

        self.assertTrue(isinstance(panel_ui, CustomPanelUI))
        self.assertFalse(isinstance(container_ui, CustomPanelUI))

    def test_register_ui_order(self):
        class LookAndFeelFixture(LookAndFeel):
            @property
            def default_ui(self) -> ComponentUI[Component]:
                return GlassComponentUI()

        laf = LookAndFeelFixture(self.context.toolkit)

        laf.register_ui(LabelButton, GlassLabelButtonUI)
        laf.register_ui(Button, GlassButtonUI)
        laf.register_ui(Label, GlassLabelUI)

        self.assertTrue(isinstance(laf.create_ui(LabelButton(self.context)), GlassLabelButtonUI))
        self.assertTrue(isinstance(laf.create_ui(Button(self.context)), GlassButtonUI))
        self.assertTrue(isinstance(laf.create_ui(Label(self.context)), GlassLabelUI))

        laf = LookAndFeelFixture(self.context.toolkit)

        laf.register_ui(Button, GlassButtonUI)
        laf.register_ui(Label, GlassLabelUI)
        laf.register_ui(LabelButton, GlassLabelButtonUI)

        self.assertTrue(isinstance(laf.create_ui(LabelButton(self.context)), GlassLabelButtonUI))
        self.assertTrue(isinstance(laf.create_ui(Button(self.context)), GlassButtonUI))
        self.assertTrue(isinstance(laf.create_ui(Label(self.context)), GlassLabelUI))

    def test_deregister_ui(self):
        laf = self.context.look_and_feel

        def create_panel_ui():
            return laf.create_ui(Panel(self.context))

        def create_component_ui():
            return laf.create_ui(Component(self.context))

        self.assertTrue(isinstance(create_panel_ui(), GlassPanelUI))
        self.assertTrue(isinstance(create_component_ui(), GlassComponentUI))

        laf.deregister_ui(Panel)

        self.assertFalse(isinstance(create_panel_ui(), GlassPanelUI))
        self.assertTrue(isinstance(create_component_ui(), GlassComponentUI))


if __name__ == '__main__':
    unittest.main()
