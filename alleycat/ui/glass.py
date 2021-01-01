from math import pi
from typing import Generic, TypeVar

import rx
from cairocffi import Context as Graphics, FontFace
from returns.maybe import Maybe, Nothing
from rx import Observable, operators as ops

from alleycat.ui import Bounds, Button, Canvas, CanvasUI, Component, ComponentUI, Container, ContainerUI, Dimension, \
    FontChangeEvent, Frame, FrameUI, Insets, InsetsChangeEvent, Label, LabelButton, LabelUI, \
    LookAndFeel, Panel, RGBA, TextAlign, Toolkit, Window, WindowUI

T = TypeVar("T", bound=Component, contravariant=True)


class GlassLookAndFeel(LookAndFeel):
    BorderThickness: float = 2

    def __init__(self, toolkit: Toolkit) -> None:
        super().__init__(toolkit)

        def with_prefix(key: str, prefix: str) -> str:
            return str.join(".", [prefix, key])

        active_color = RGBA(0.3, 0.7, 0.3, 1)
        highlight_color = RGBA(0.9, 0.8, 0.5, 1)

        self.set_font("text", toolkit.fonts.fallback_font)

        self.set_color(with_prefix(StyleKeys.Background, "Window"), RGBA(0, 0, 0, 0.8))
        self.set_color(with_prefix(StyleKeys.Border, "Window"), active_color)
        self.set_color(with_prefix(StyleKeys.Background, "Overlay"), RGBA(0, 0, 0, 0))
        self.set_color(with_prefix(StyleKeys.Border, "Overlay"), RGBA(0, 0, 0, 0))
        self.set_color(with_prefix(StyleKeys.Border, "Button"), active_color)
        self.set_color(with_prefix(StyleKeys.BorderHover, "Button"), highlight_color)
        self.set_color(with_prefix(StyleKeys.BackgroundActive, "Button"), active_color)
        self.set_color(with_prefix(StyleKeys.BorderActive, "Button"), active_color)

        self.set_color(StyleKeys.Text, RGBA(0.8, 0.8, 0.8, 1))
        self.set_color(with_prefix(StyleKeys.TextHover, "Button"), highlight_color)
        self.set_color(with_prefix(StyleKeys.TextActive, "Button"), RGBA(0, 0, 0, 1))

        self.set_insets(StyleKeys.Padding, Insets(10, 10, 10, 10))
        self.set_insets(with_prefix(StyleKeys.Padding, "Overlay"), Insets(0, 0, 0, 0))

        self.register_ui(Window, GlassWindowUI)
        self.register_ui(Frame, GlassFrameUI)
        self.register_ui(Panel, GlassPanelUI)
        self.register_ui(LabelButton, GlassLabelButtonUI)
        self.register_ui(Button, GlassButtonUI)
        self.register_ui(Label, GlassLabelUI)
        self.register_ui(Canvas, GlassCanvasUI)

    @property
    def default_ui(self) -> ComponentUI[Component]:
        return GlassComponentUI()


# noinspection PyMethodMayBeStatic
class GlassComponentUI(ComponentUI[T], Generic[T]):

    def __init__(self) -> None:
        super().__init__()

    def clip_bounds(self, component: T) -> Bounds:
        border = GlassLookAndFeel.BorderThickness * 0.5

        return super().clip_bounds(component) + Insets(border, border, border, border)

    def on_style_change(self, component: T) -> Observable:
        return rx.merge(component.on_style_change, component.context.look_and_feel.on_style_change)

    def draw(self, g: Graphics, component: T) -> None:
        assert g is not None
        assert component is not None

        self.background_color(component).map(lambda c: self.draw_background(g, component, c))
        self.draw_component(g, component)
        self.border_color(component).map(lambda c: self.draw_border(g, component, c))

    def draw_component(self, g: Graphics, component: T) -> None:
        pass

    def background_color(self, component: T) -> Maybe[RGBA]:
        return component.resolve_color(StyleKeys.Background)

    def border_color(self, component: T) -> Maybe[RGBA]:
        return component.resolve_color(StyleKeys.Border)

    def draw_rect(self, g: Graphics, area: Bounds, radius: float) -> None:
        (x, y, w, h) = area.tuple

        if w == 0 or h == 0:
            return

        degrees = pi / 180.0

        g.new_sub_path()

        g.arc(x + w - radius, y + radius, radius, -90 * degrees, 0)
        g.arc(x + w - radius, y + h - radius, radius, 0, 90 * degrees)
        g.arc(x + radius, y + h - radius, radius, 90 * degrees, 180 * degrees)
        g.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)

        g.close_path()

    def draw_background(self, g: Graphics, component: T, color: RGBA) -> None:
        area = component.bounds

        if area.width == 0 or area.height == 0:
            return

        g.set_source_rgba(color.r, color.g, color.b, color.a)

        self.draw_rect(g, area, 8)

        g.fill()

    def draw_border(
            self,
            g: Graphics,
            component: T,
            color: RGBA,
            thickness: float = GlassLookAndFeel.BorderThickness) -> None:
        area = component.bounds

        if area.width == 0 or area.height == 0:
            return

        g.set_source_rgba(color.r, color.g, color.b, color.a)
        g.set_line_width(thickness)

        self.draw_rect(g, area, 8)

        g.stroke()


C = TypeVar("C", bound=Container, contravariant=True)
W = TypeVar("W", bound=Window, contravariant=True)


class GlassContainerUI(GlassComponentUI[C], ContainerUI[C]):

    def __init__(self) -> None:
        super().__init__()

    def draw(self, g: Graphics, component: C) -> None:
        assert g is not None
        assert component is not None

        self.background_color(component).map(lambda c: self.draw_background(g, component, c))
        self.draw_component(g, component)

    def post_draw(self, g: Graphics, component: C) -> None:
        assert g is not None
        assert component is not None

        super().post_draw(g, component)

        self.border_color(component).map(lambda c: self.draw_border(g, component, c))


class GlassPanelUI(GlassContainerUI[Panel]):

    def __init__(self) -> None:
        super().__init__()


class GlassWindowUI(GlassContainerUI[W], WindowUI[W]):

    def __init__(self) -> None:
        super().__init__()


class GlassFrameUI(GlassWindowUI[Frame], FrameUI):

    def __init__(self) -> None:
        super().__init__()


# noinspection PyMethodMayBeStatic
class GlassLabelUI(GlassComponentUI[Label], LabelUI):
    _ratio_for_align = {TextAlign.Begin: 0., TextAlign.Center: 0.5, TextAlign.End: 1.}

    def __init__(self) -> None:
        super().__init__()

    def minimum_size(self, component: Label) -> Dimension:
        (width, height) = self.extents(component).tuple
        (top, right, bottom, left) = self.padding(component)

        return Dimension(width + left + right, height + top + bottom)

    def text_color(self, component: Label) -> Maybe[RGBA]:
        return component.resolve_color(StyleKeys.Text)

    def font(self, component: Label) -> FontFace:
        fonts = component.context.toolkit.fonts

        return component.resolve_font(StyleKeys.Text).value_or(fonts.fallback_font)

    def padding(self, component: Label) -> Insets:
        return component.resolve_insets(StyleKeys.Padding).value_or(Insets(0, 0, 0, 0))

    def on_invalidate(self, component: Label) -> Observable:
        text_changes = component.observe("text")
        size_changes = component.observe("text_size")

        style_changes = self.on_style_change(component)

        font_changes = style_changes.pipe(
            ops.filter(lambda e: isinstance(e, FontChangeEvent)),
            ops.filter(lambda e: e.key in component.style_fallback_keys(StyleKeys.Text)))

        padding_changes = style_changes.pipe(
            ops.filter(lambda e: isinstance(e, InsetsChangeEvent)),
            ops.filter(lambda e: e.key in component.style_fallback_keys(StyleKeys.Padding)))

        return rx.merge(
            super().on_invalidate(component),
            text_changes,
            size_changes,
            font_changes,
            padding_changes)

    def draw_component(self, g: Graphics, component: Label) -> None:
        super().draw_component(g, component)

        font = self.font(component)
        color = self.text_color(component)

        color.map(lambda c: self.draw_text(g, component, font, c))

    def draw_text(self, g: Graphics, component: Label, font: FontFace, color: RGBA) -> None:
        text = component.text
        size = component.text_size

        extents = component.context.toolkit.fonts.text_extent(text, font, size)
        padding = component.resolve_insets(StyleKeys.Padding).value_or(Insets(0, 0, 0, 0))

        (x, y, w, h) = component.bounds.tuple

        rh = self._ratio_for_align[component.text_align]
        rv = self._ratio_for_align[component.text_vertical_align]

        tx = (w - extents.width - padding.left - padding.right) * rh + x + padding.left
        ty = (h - extents.height - padding.top - padding.bottom) * rv + extents.height + y + padding.top

        g.set_font_face(font)
        g.set_font_size(size)

        # FIXME: Temporary workaround until we get a better way of handling text shadows.
        if component.shadow:
            g.move_to(tx + 1, ty + 1)

            g.set_source_rgba(0, 0, 0, 0.8)
            g.show_text(text)

        g.move_to(tx, ty)

        g.set_source_rgba(color.r, color.g, color.b, color.a)
        g.show_text(text)


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


# noinspection PyMethodMayBeStatic
class GlassCanvasUI(GlassComponentUI[Canvas], CanvasUI):

    def __init__(self) -> None:
        super().__init__()

    def padding(self, component: Canvas) -> Insets:
        return component.resolve_insets(StyleKeys.Padding).value_or(Insets(0, 0, 0, 0))

    def on_invalidate(self, component: Canvas) -> Observable:
        image_changes = component.observe("image")

        padding_changes = self.on_style_change(component).pipe(
            ops.filter(lambda e: isinstance(e, InsetsChangeEvent)),
            ops.filter(lambda e: e.key in component.style_fallback_keys(StyleKeys.Padding)))

        return rx.merge(
            super().on_invalidate(component),
            image_changes,
            padding_changes)

    def draw_component(self, g: Graphics, component: Canvas) -> None:
        super().draw_component(g, component)

        if component.image == Nothing:
            return

        image = component.image.unwrap()
        padding = component.resolve_insets(StyleKeys.Padding).value_or(Insets(0, 0, 0, 0)) + component.padding

        (x, y, w, h) = component.bounds.tuple

        bounds = Bounds(
            x + padding.left,
            y + padding.top,
            max(w - padding.left - padding.right, 0),
            max(h - padding.top - padding.bottom, 0))

        (iw, ih) = image.size.tuple
        (w, h) = bounds.size.tuple

        if iw == 0 or ih == 0 or w == 0 or h == 0:
            return

        (x, y) = bounds.location.tuple

        sw = w / iw
        sh = h / ih

        sx = x / sw
        sy = y / sh

        g.scale(sw, sh)
        g.set_source_surface(image.surface, sx, sy)
        g.paint()


class StyleKeys:
    Background: str = "background"
    BackgroundHover: str = "background:hover"
    BackgroundActive: str = "background:active"

    Border: str = "border"
    BorderHover: str = "border:hover"
    BorderActive: str = "border:active"

    Text: str = "text"
    TextHover: str = "text:hover"
    TextActive: str = "text:active"

    Padding: str = "padding"
