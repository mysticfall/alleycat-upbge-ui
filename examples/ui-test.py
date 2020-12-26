import sys

from bge.logic import expandPath
from bpy.types import SpaceView3D

sys.path += [expandPath("//.."), expandPath("//../.venv/lib/python3.9/site-packages")]

import rx
from rx import operators as ops
from alleycat.ui import Bounds, Canvas, Insets, Panel, Label, LabelButton, RGBA, Frame
from alleycat.ui.blender import UI
from alleycat.ui.layout import Border, BorderLayout, HBoxLayout
from alleycat.ui.glass import StyleKeys

context = UI().create_context()
toolkit = context.toolkit

window = Frame(context, BorderLayout())
window.bounds = Bounds(160, 70, 280, 200)

panel = Panel(context, HBoxLayout())
panel.set_color(StyleKeys.Background, RGBA(0.3, 0.3, 0.3, 1))

window.add(panel, padding=Insets(10, 10, 10, 10))

icon = Canvas(context, toolkit.images["cat.png"])
icon.bounds = Bounds(0, 0, 64, 64)

panel.add(icon)

label = Label(context, text_size=18)
label.set_color(StyleKeys.Text, RGBA(1, 1, 1, 1))

panel.add(label)

button1 = LabelButton(context, text_size=16, text="Button 1")
button2 = LabelButton(context, text_size=16, text="Button 2")

buttons = Panel(context, HBoxLayout(spacing=10))

buttons.add(button1)
buttons.add(button2)

window.add(buttons, Border.Bottom, Insets(0, 10, 10, 10))


def handle_button(button: str):
    if len(button) > 0:
        label.text = f"{button} is pressed"
        panel.set_color(StyleKeys.Background, RGBA(1, 0, 0, 1))
    else:
        label.text = ""
        panel.set_color(StyleKeys.Background, RGBA(0.1, 0.1, 0.1, 1))


button1_active = button1.observe("active").pipe(ops.map(lambda v: "Button 1" if v else ""))
button2_active = button2.observe("active").pipe(ops.map(lambda v: "Button 2" if v else ""))

button_active = rx.combine_latest(button1_active, button2_active).pipe(ops.map(lambda v: v[0] + v[1]))

button_active.subscribe(handle_button, on_error=context.error_handler)

window.draggable = True
window.resizable = True


def register():
    #    bge.logic.getCurrentScene().post_draw.append(context.process)
    SpaceView3D.draw_handler_add(context.process, (), "WINDOW", "POST_PIXEL")
