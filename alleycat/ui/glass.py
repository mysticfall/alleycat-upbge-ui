from typing import TypeVar, Final

from alleycat.ui import Component, ComponentUI, Graphics, LookAndFeel, Panel, RGBA, Window, ColorKey, Label, Point

T = TypeVar("T", bound=Component, contravariant=True)


class GlassLookAndFeel(LookAndFeel):

    def __init__(self) -> None:
        super().__init__()

        self.set_color(ColorKeys.Background, RGBA(0, 0, 0, 0.8))
        self.set_color(ColorKeys.Text, RGBA(0.8, 0.8, 0.8, 1))

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def create_ui(self, component: T) -> ComponentUI[T]:
        assert component is not None

        if isinstance(component, Panel):
            return GlassPanelUI()
        elif isinstance(component, Window):
            return GlassWindowUI()
        elif isinstance(component, Label):
            return GlassLabelUI()

        return super().create_ui(component)


class GlassPanelUI(ComponentUI[Panel]):

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: Panel) -> None:
        assert g is not None
        assert component is not None

        g.color = component.get_color(ColorKeys.Background).or_else_call(lambda: RGBA(0, 0, 0, 1))
        g.fill_rect(component.bounds)


class GlassWindowUI(ComponentUI[Window]):

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: Window) -> None:
        assert g is not None
        assert component is not None

        g.color = component.get_color(ColorKeys.Background).or_else_call(lambda: RGBA(0, 0, 0, 1))
        g.fill_rect(component.bounds)


class GlassLabelUI(ComponentUI[Label]):

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: Label) -> None:
        assert g is not None
        assert component is not None

        g.color = component.get_color(ColorKeys.Text).or_else_call(lambda: RGBA(0.8, 0.8, 0.8, 1))

        text = component.text
        extents = component.context.font_registry.text_extent(text, g.font)

        (x, y, w, h) = component.bounds.tuple

        tx = (w - extents.width) / 2.0 + x
        ty = (h - extents.height) / 2.0 + extents.height + y

        g.draw_text(text, component.size, Point(tx, ty))


class ColorKeys:
    Background: Final = ColorKey()
    Text: Final = ColorKey()
