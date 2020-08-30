from typing import TypeVar

from alleycat.ui import LookAndFeel, Component, ComponentUI, Panel, Graphics, Window

T = TypeVar("T", bound=Component, contravariant=True)


class GlassLookAndFeel(LookAndFeel):

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def create_ui(self, component: T) -> ComponentUI[T]:
        if isinstance(component, Panel):
            return GlassPanelUI()
        elif isinstance(component, Window):
            return GlassWindowUI()

        return super().create_ui(component)


class GlassPanelUI(ComponentUI[Panel]):
    def draw(self, g: Graphics, component: Panel) -> None:
        g.fill_rect(component.bounds)


class GlassWindowUI(ComponentUI[Window]):
    def draw(self, g: Graphics, component: Panel) -> None:
        g.fill_rect(component.bounds)
