from typing import TypeVar, Final, Generic

import rx
from returns.maybe import Maybe, Nothing
from rx import Observable
from rx import operators as ops

from alleycat.ui import Component, ComponentUI, Graphics, LookAndFeel, Panel, RGBA, Window, Label, Point, Toolkit, \
    TextAlign, Font, Button, LabelButton, WindowUI, LayoutContainerUI, FontChangeEvent, LabelUI, Insets, \
    InsetsChangeEvent, Dimension

T = TypeVar("T", bound=Component, contravariant=True)


class GlassLookAndFeel(LookAndFeel):
    BorderThickness: Final = 2

    def __init__(self, toolkit: Toolkit) -> None:
        super().__init__(toolkit)

        def with_prefix(key: str, prefix: str) -> str:
            return str.join(".", [prefix, key])

        active_color = RGBA(0.3, 0.7, 0.3, 1)
        highlight_color = RGBA(0.9, 0.8, 0.5, 1)

        self.set_font("text", toolkit.font_registry.fallback_font)

        self.set_color(with_prefix(StyleKeys.Background, "Window"), RGBA(0, 0, 0, 0.8))
        self.set_color(with_prefix(StyleKeys.Border, "Window"), active_color)
        self.set_color(with_prefix(StyleKeys.Border, "Button"), active_color)
        self.set_color(with_prefix(StyleKeys.BorderHover, "Button"), highlight_color)
        self.set_color(with_prefix(StyleKeys.BackgroundActive, "Button"), active_color)
        self.set_color(with_prefix(StyleKeys.BorderActive, "Button"), active_color)

        self.set_color(StyleKeys.Text, RGBA(0.8, 0.8, 0.8, 1))
        self.set_color(with_prefix(StyleKeys.TextHover, "Button"), highlight_color)
        self.set_color(with_prefix(StyleKeys.TextActive, "Button"), RGBA(0, 0, 0, 1))

        self.set_insets(StyleKeys.Padding, Insets(5, 10, 5, 10))

        self.register_ui(Window, GlassWindowUI)
        self.register_ui(Panel, GlassPanelUI)
        self.register_ui(LabelButton, GlassLabelButtonUI)
        self.register_ui(Button, GlassButtonUI)
        self.register_ui(Label, GlassLabelUI)

    @property
    def default_ui(self) -> ComponentUI[Component]:
        return GlassComponentUI()


# noinspection PyMethodMayBeStatic
class GlassComponentUI(ComponentUI[T], Generic[T]):

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: T) -> None:
        assert g is not None
        assert component is not None

        self.background_color(component).map(lambda c: self.draw_background(g, component, c))
        self.border_color(component).map(lambda c: self.draw_border(g, component, c))

    def background_color(self, component: T) -> Maybe[RGBA]:
        return component.resolve_color(StyleKeys.Background)

    def border_color(self, component: T) -> Maybe[RGBA]:
        return component.resolve_color(StyleKeys.Border)

    def draw_background(self, g: Graphics, component: T, color: RGBA) -> None:
        g.color = color
        g.fill_rect(component.bounds)

    def draw_border(
            self,
            g: Graphics,
            component: T,
            color: RGBA,
            thickness: float = GlassLookAndFeel.BorderThickness) -> None:
        g.color = color
        g.stroke = thickness
        g.draw_rect(component.bounds)


class GlassPanelUI(GlassComponentUI[Panel], LayoutContainerUI[Panel]):

    def __init__(self) -> None:
        super().__init__()


class GlassWindowUI(GlassComponentUI[Window], WindowUI[Window]):

    def __init__(self) -> None:
        super().__init__()


# noinspection PyMethodMayBeStatic
class GlassLabelUI(GlassComponentUI[Label], LabelUI):
    _ratio_for_align = {TextAlign.Begin: 0., TextAlign.Center: 0.5, TextAlign.End: 1.}

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: Label) -> None:
        super().draw(g, component)

        font = self.text_font(component)
        color = self.text_color(component)

        color.map(lambda c: self.draw_text(g, component, font, c))

    def minimum_size(self, component: Label) -> Observable:
        text_extents = super().minimum_size(component)

        return rx.combine_latest(text_extents, self.on_padding_change(component)).pipe(
            ops.map(lambda v: Dimension(v[0].width + v[1].left + v[1].right, v[0].height + v[1].top + v[1].bottom)))

    def draw_text(self, g: Graphics, component: Label, font: Font, color: RGBA) -> None:
        g.font = font
        g.color = color

        text = component.text
        size = component.text_size

        extents = component.context.toolkit.font_registry.text_extent(text, font, size)
        padding = component.resolve_insets(StyleKeys.Padding).value_or(Insets(0, 0, 0, 0))

        (x, y, w, h) = component.bounds.tuple

        rh = self._ratio_for_align[component.text_align]
        rv = self._ratio_for_align[component.text_vertical_align]

        tx = (w - extents.width - padding.left - padding.right) * rh + x + padding.left
        ty = (h - extents.height - padding.top - padding.bottom) * rv + extents.height + y + padding.top

        g.draw_text(text, size, Point(tx, ty))

    def text_color(self, component: Label) -> Maybe[RGBA]:
        return component.resolve_color(StyleKeys.Text)

    def text_font(self, component: Label) -> Font:
        font_registry = component.context.toolkit.font_registry

        return component.resolve_font(StyleKeys.Text).value_or(font_registry.fallback_font)

    def on_font_change(self, component: Label) -> Observable:
        keys = set(component.style_fallback_keys(StyleKeys.Text))
        fallback = component.context.toolkit.font_registry.fallback_font

        def effective_font() -> Font:
            return component.resolve_font(StyleKeys.Text).value_or(fallback)

        style_changes = rx.merge(component.on_style_change, component.context.look_and_feel.on_style_change)
        font_changes = style_changes.pipe(
            ops.filter(lambda e: isinstance(e, FontChangeEvent)),
            ops.filter(lambda e: e.key in keys),
            ops.map(lambda _: effective_font()),
            ops.start_with(effective_font()),
            ops.distinct_until_changed())

        return font_changes

    def on_padding_change(self, component: Label) -> Observable:
        keys = set(component.style_fallback_keys(StyleKeys.Padding))

        def effective_padding() -> Insets:
            return component.resolve_insets(StyleKeys.Padding).value_or(Insets(0, 0, 0, 0))

        style_changes = rx.merge(component.on_style_change, component.context.look_and_feel.on_style_change)
        padding_changes = style_changes.pipe(
            ops.filter(lambda e: isinstance(e, InsetsChangeEvent)),
            ops.filter(lambda e: e.key in keys),
            ops.map(lambda _: effective_padding()),
            ops.start_with(effective_padding()),
            ops.distinct_until_changed())

        return padding_changes


# noinspection PyMethodMayBeStatic
class GlassButtonUI(GlassComponentUI[Button]):

    def __init__(self) -> None:
        super().__init__()

    def background_color(self, component: T) -> Maybe[RGBA]:
        return self.resolve_color(component, StyleKeys.Background)

    def border_color(self, component: T) -> Maybe[RGBA]:
        return self.resolve_color(component, StyleKeys.Border)

    def resolve_color(self, component: LabelButton, key: str) -> Maybe[RGBA]:
        color: Maybe[RGBA] = Nothing

        if component.active:
            color = component.resolve_color(key + ":active")
        elif component.hover:
            color = component.resolve_color(key + ":hover")

        return component.resolve_color(key) if color == Nothing else color


class GlassLabelButtonUI(GlassButtonUI, GlassLabelUI):

    def __init__(self) -> None:
        super().__init__()

    def text_color(self, component: T) -> Maybe[RGBA]:
        return self.resolve_color(component, StyleKeys.Text)


class StyleKeys:
    Background: Final = "background"
    BackgroundHover: Final = "background:hover"
    BackgroundActive: Final = "background:active"

    Border: Final = "border"
    BorderHover: Final = "border:hover"
    BorderActive: Final = "border:active"

    Text: Final = "text"
    TextHover: Final = "text:hover"
    TextActive: Final = "text:active"

    Padding: Final = "padding"
