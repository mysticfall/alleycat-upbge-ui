from typing import TypeVar, Final, Generic

from alleycat.ui import Component, ComponentUI, Graphics, LookAndFeel, Panel, RGBA, Window, Label, Point, Toolkit, \
    TextAlign

T = TypeVar("T", bound=Component, contravariant=True)


class GlassLookAndFeel(LookAndFeel):

    def __init__(self, toolkit: Toolkit) -> None:
        super().__init__(toolkit)

        def with_prefix(key: str, prefix: str) -> str:
            return str.join(".", [prefix, key])

        self.set_font("text", toolkit.font_registry.fallback_font)

        self.set_color(ColorKeys.Background, RGBA(0, 0, 0, 0))
        self.set_color(with_prefix(ColorKeys.Background, "Window"), RGBA(0, 0, 0, 0.8))

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

        return GlassComponentUI()


class GlassComponentUI(ComponentUI[T], Generic[T]):

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: T) -> None:
        assert g is not None
        assert component is not None

        def draw_background(color: RGBA) -> None:
            g.color = color
            g.fill_rect(component.bounds)

        component.resolve_color(ColorKeys.Background).map(draw_background)


class GlassPanelUI(GlassComponentUI[Panel]):

    def __init__(self) -> None:
        super().__init__()


class GlassWindowUI(GlassComponentUI[Window]):

    def __init__(self) -> None:
        super().__init__()


class GlassLabelUI(GlassComponentUI[Label]):
    _ratio_for_align = {TextAlign.Begin: 0., TextAlign.Center: 0.5, TextAlign.End: 1.}

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: Label) -> None:
        super().draw(g, component)

        def draw_text(color: RGBA) -> None:
            font_registry = component.context.toolkit.font_registry
            font = component.resolve_font("text").value_or(font_registry.fallback_font)

            g.font = font
            g.color = color

            text = component.text
            size = component.size

            extents = component.context.toolkit.font_registry.text_extent(text, font, size)

            (x, y, w, h) = component.bounds.tuple

            rh = self._ratio_for_align[component.text_align]
            rv = self._ratio_for_align[component.text_vertical_align]

            tx = (w - extents.width) * rh + x
            ty = (h - extents.height) * rv + extents.height + y

            g.draw_text(text, size, Point(tx, ty))

        component.resolve_color(ColorKeys.Text).map(draw_text)


class ColorKeys:
    Background: Final = "background"
    Text: Final = "text"
