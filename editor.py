import base64
import io
import json
import random
import tkinter.ttk

from color import ColorPicker
from skin import SkinView

from PIL import Image


class NewPopup(tkinter.ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, borderwidth=1, relief="solid", **kwargs)

        content = tkinter.ttk.Frame(self)
        content.pack(fill="both", expand=1, padx=10, pady=10)

        # name
        tkinter.ttk.Label(content, text="Name:").grid(row=0, column=0)
        name = tkinter.ttk.Entry(content)
        name.grid(row=0, column=1, padx=10, columnspan=3, sticky="nesw")

        # slim
        self.slim = tkinter.IntVar(content, 0)
        tkinter.ttk.Checkbutton(content, text="Slim arms", variable=self.slim).grid(
            row=1, column=0, columnspan=2
        )

        tkinter.ttk.Button(content, text="Use a template").grid(row=1, column=2)

    def show(self):
        self.place(anchor="c", relx=0.5, rely=0.5, width=400, height=350)


class Editor(tkinter.ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.left_frame = tkinter.ttk.Frame(self)
        self.left_frame.pack(side="left", fill="y")

        self.color_picker = ColorPicker(self.left_frame)
        self.color_picker.pack()

        self.viewport = tkinter.ttk.Frame(self)
        self.viewport.pack(side="left", fill="both", expand=1)

        self.buttons = tkinter.ttk.Frame(self.viewport)
        self.buttons.pack(fill="x", pady=5)

        tkinter.ttk.Button(self.buttons, text="New Skin", command=self.new_tab).pack(
            side="left", padx=5
        )
        tkinter.ttk.Button(self.buttons, text="Load Skin").pack(side="left", padx=5)

        self.tabs = tkinter.ttk.Notebook(self.viewport, width=500, height=500)
        self.tabs.pack(side="bottom", fill="both", expand=1)

        self.tabs.bind("<<NotebookTabChanged>>", self.update_tabs)

        self.views = []

        self.view = None

        self.right_frame = tkinter.ttk.Frame(self)
        self.right_frame.pack(side="right", fill="both")

        self.slim = tkinter.IntVar(self, 0)

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Thin arms",
            variable=self.slim,
            command=self.slim_cb,
        ).pack(anchor="w")

        self.exploded = tkinter.IntVar(self, 0)

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Exploded View",
            variable=self.exploded,
            command=self.exploded_cb,
        ).pack(anchor="w")

        self.overlay_hat = tkinter.IntVar(self, 1)
        self.overlay_jacket = tkinter.IntVar(self, 1)
        self.overlay_right_sleeve = tkinter.IntVar(self, 1)
        self.overlay_left_sleeve = tkinter.IntVar(self, 1)
        self.overlay_right_pants = tkinter.IntVar(self, 1)
        self.overlay_left_pants = tkinter.IntVar(self, 1)

        self.overlay_lookup = [
            self.overlay_hat,
            "hat",
            self.overlay_jacket,
            "jacket",
            self.overlay_right_sleeve,
            "right-sleeve",
            self.overlay_left_sleeve,
            "left-sleeve",
            self.overlay_right_pants,
            "right-pants",
            self.overlay_left_pants,
            "left-pants",
        ]

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Show Hat",
            variable=self.overlay_hat,
            command=lambda: self.overlays_cb(self.overlay_hat),
        ).pack(anchor="w")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Show Jacket",
            variable=self.overlay_jacket,
            command=lambda: self.overlays_cb(self.overlay_jacket),
        ).pack(anchor="w")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Show Right Sleeve",
            variable=self.overlay_right_sleeve,
            command=lambda: self.overlays_cb(self.overlay_right_sleeve),
        ).pack(anchor="w")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Show Left Sleeve",
            variable=self.overlay_left_sleeve,
            command=lambda: self.overlays_cb(self.overlay_left_sleeve),
        ).pack(anchor="w")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Show Right Pants",
            variable=self.overlay_right_pants,
            command=lambda: self.overlays_cb(self.overlay_right_pants),
        ).pack(anchor="w")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Show Left Pants",
            variable=self.overlay_left_pants,
            command=lambda: self.overlays_cb(self.overlay_left_pants),
        ).pack(anchor="w")

        self.ortho = tkinter.IntVar(self, 0)

        tkinter.ttk.Separator(self.right_frame).pack(fill="x")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Orthographic",
            variable=self.ortho,
            command=self.ortho_cb,
        ).pack(side="bottom", anchor="w")

    def set_background_color(self, color):
        self.background_color = color

        for view in self.views:
            view.background_color = self.background_color

    def new_tab(self):
        NewPopup(self).show()

        with open("skins.json", "r") as fp:
            default_skins = json.load(fp)["default"]
            slim = random.randint(0, 1)
            skin = Image.open(
                io.BytesIO(
                    base64.b64decode(
                        default_skins[random.choice(list(default_skins))][
                            ["classic", "slim"][slim]
                        ]
                    )
                )
            )
            self.create_tab(skin, slim)

    def create_tab(self, skin: Image, slim: bool, cape: Image = None):
        view = SkinView(
            self.tabs,
            slim=slim,
            skin_img=skin,
            cape_img=cape,
            rot_y=-45,
            rot_x=35.264,
            width=550,
            height=500,
            background_color=self.background_color,
        )
        view.animate = True

        self.views.append(view)
        self.tabs.add(view, text=f"Skin {len(self.views)}", sticky="nesw")
        self.tabs.select(len(self.tabs.tabs()) - 1)

    def update_tabs(self, event=None):
        index = self.tabs.tabs().index(self.tabs.select())
        self.view = self.views[index]

        # update checkbuttons
        self.slim.set(self.view.slim)
        self.exploded.set(self.view.exploded)
        self.overlay_hat.set(self.view.show["hat"])
        self.overlay_jacket.set(self.view.show["jacket"])
        self.overlay_right_sleeve.set(self.view.show["right-sleeve"])
        self.overlay_left_sleeve.set(self.view.show["left-sleeve"])
        self.overlay_right_pants.set(self.view.show["right-pants"])
        self.overlay_left_pants.set(self.view.show["left-pants"])
        self.ortho.set(self.view.ortho)

    def slim_cb(self):
        if self.view:
            self.view.slim = self.slim.get()

    def exploded_cb(self):
        if self.view:
            self.view.exploded = self.exploded.get()

    def overlays_cb(self, var):
        if self.view:
            self.view.show[
                self.overlay_lookup[self.overlay_lookup.index(var) + 1]
            ] = var.get()

    def ortho_cb(self):
        if self.view:
            self.view.ortho = self.ortho.get()
