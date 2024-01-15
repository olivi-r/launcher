import base64
import io
import json
import tkinter.ttk

import color
import skin

from PIL import Image


class NewPopup(tkinter.ttk.Frame):
    background_color = (0.15, 0.15, 0.15)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, borderwidth=1, relief="solid", **kwargs)

        content = tkinter.ttk.Frame(self)
        content.pack(padx=10, pady=10)

        # name
        tkinter.ttk.Label(content, text="Name:").grid(row=0, column=0)
        self.name = tkinter.ttk.Entry(content)
        self.name.grid(row=0, column=1, padx=10, columnspan=2, sticky="nesw")

        # slim
        self.slim = tkinter.IntVar(content, 0)
        tkinter.ttk.Checkbutton(
            content, text="Slim arms", variable=self.slim, command=self.update_preview
        ).grid(row=1, column=0, columnspan=2)

        # templates
        self.template = tkinter.IntVar(self, 0)
        tkinter.ttk.Radiobutton(
            content,
            text="Use a template",
            variable=self.template,
            value=0,
            command=self.update_preview,
        ).grid(row=1, column=2, sticky="w", padx=10, pady=10)
        tkinter.ttk.Radiobutton(
            content,
            text="Use a default skin",
            variable=self.template,
            value=1,
            command=self.update_preview,
        ).grid(row=2, column=2, sticky="w", padx=10)

        self.template_choice = tkinter.ttk.Combobox(
            content,
            values=[
                "Steve",
                "Alex",
                "Ari",
                "Kai",
                "Noor",
                "Sunny",
                "Zuri",
                "Efe",
                "Makena",
            ],
            state="disabled",
            width=8,
        )
        self.template_choice.current(0)
        self.template_choice.grid(row=2, column=3)
        self.template_choice.bind("<FocusIn>", lambda _: self.update_preview())

        self.preview = skin.SkinView(
            self,
            slim=False,
            skin_img=Editor.get_template_skin(False),
            background_color=self.background_color,
        )
        self.preview.animate = True
        self.preview.pack(fill="both", expand=1, padx=10)

        # buttons
        button_panel = tkinter.ttk.Frame(self)
        button_panel.pack(pady=10)
        tkinter.ttk.Button(button_panel, text="Cancel", command=self.close).pack(
            side="left", padx=20
        )
        tkinter.ttk.Button(
            button_panel, text="Create", command=self.create, style="Accent.TButton"
        ).pack(side="right", padx=20)

    def create(self) -> None:
        slim = self.slim.get()
        if self.template.get():
            skin = Editor.get_default_skin(self.template_choice.get(), slim)

        else:
            skin = Editor.get_template_skin(slim)

        name = self.name.get() or "Untitled"
        self.master.create_tab(name, skin, slim)
        self.close()

    def close(self) -> None:
        self.master.popups.pop(self.master.popups.index(self))
        self.destroy()

    def update_preview(self) -> None:
        self.template_choice.select_clear()
        self.preview.slim = self.slim.get()

        if self.template.get():
            self.template_choice.config(state="readonly")
            self.preview.set_skin(
                Editor.get_default_skin(self.template_choice.get(), self.slim.get())
            )

        else:
            self.template_choice.config(state="disabled")
            self.preview.set_skin(Editor.get_template_skin(self.slim.get()))

    def show(self) -> None:
        self.place(anchor="c", relx=0.5, rely=0.5, width=400, height=350)


class Editor(tkinter.ttk.Frame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.popups = []

        self.left_frame = tkinter.ttk.Frame(self)
        self.left_frame.pack(side="left", fill="y")

        self.color_picker = color.ColorPicker(self.left_frame)
        self.color_picker.pack()

        self.viewport = tkinter.ttk.Frame(self)
        self.viewport.pack(side="left", fill="both", expand=1)

        self.buttons = tkinter.ttk.Frame(self.viewport)
        self.buttons.pack(fill="x", pady=5)

        tkinter.ttk.Button(self.buttons, text="New Skin", command=self.popup).pack(
            side="left"
        )
        tkinter.ttk.Button(self.buttons, text="Load Skin").pack(side="left", padx=10)

        self.tabs = tkinter.ttk.Notebook(self.viewport, width=500, height=500)
        self.tabs.pack(side="bottom", fill="both", expand=1)

        self.tabs.bind("<<NotebookTabChanged>>", self.update_tabs)

        self.views = []

        self.view = None

        self.right_frame = tkinter.ttk.Frame(self)
        self.right_frame.pack(side="right", fill="both")

        # checkbox variables
        self.slim = tkinter.IntVar(self)
        self.exploded = tkinter.IntVar(self)
        self.overlay_hat = tkinter.IntVar(self)
        self.overlay_jacket = tkinter.IntVar(self)
        self.overlay_right_sleeve = tkinter.IntVar(self)
        self.overlay_left_sleeve = tkinter.IntVar(self)
        self.overlay_right_pants = tkinter.IntVar(self)
        self.overlay_left_pants = tkinter.IntVar(self)
        self.ortho = tkinter.IntVar(self)
        self.show_grid = tkinter.IntVar(self)

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
            text="Thin arms",
            variable=self.slim,
            command=self.slim_cb,
        ).pack(anchor="w")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Exploded View",
            variable=self.exploded,
            command=self.exploded_cb,
        ).pack(anchor="w")

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

        tkinter.ttk.Separator(self.right_frame).pack(fill="x")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Orthographic",
            variable=self.ortho,
            command=self.ortho_cb,
        ).pack(side="bottom", anchor="w")

        tkinter.ttk.Checkbutton(
            self.right_frame,
            text="Show Grid",
            variable=self.show_grid,
            command=self.show_grid_cb,
        ).pack(side="bottom", anchor="w")

        self.update_tabs()

    @staticmethod
    def get_template_skin(slim_arms: bool) -> Image.Image:
        arms = "slim" if slim_arms else "classic"
        with open("skins.json", "r") as fp:
            return Image.open(
                io.BytesIO(base64.b64decode(json.load(fp)["template"][arms]))
            )

    @staticmethod
    def get_default_skin(name: str, slim_arms: bool) -> Image.Image:
        arms = "slim" if slim_arms else "classic"
        with open("skins.json", "r") as fp:
            return Image.open(
                io.BytesIO(base64.b64decode(json.load(fp)["default"][name][arms]))
            )

    def popup(self) -> None:
        p = NewPopup(self)
        self.popups.append(p)
        p.show()

    def set_background_color(self, color: tuple) -> None:
        self.background_color = color

        NewPopup.background_color = color
        for popup in self.popups:
            popup.preview.background_color = color

        for view in self.views:
            view.background_color = self.background_color

    def create_tab(
        self, name: str, skin_img: Image.Image, slim: bool, cape_img: Image.Image = None
    ) -> None:
        view = skin.SkinView(
            self.tabs,
            slim=slim,
            skin_img=skin_img,
            cape_img=cape_img,
            rot_y=-45,
            rot_x=35.264,
            grid=True,
            width=550,
            height=500,
            background_color=self.background_color,
        )
        view.animate = True

        self.views.append(view)
        self.tabs.add(view, text=name, sticky="nesw")
        self.tabs.select(len(self.tabs.tabs()) - 1)

    def update_tabs(self, event: tkinter.Event = None) -> None:
        current = self.tabs.select()
        if current:
            index = self.tabs.tabs().index(current)
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
            self.show_grid.set(self.view.grid)

        else:
            # update checkbuttons
            self.slim.set(0)
            self.exploded.set(0)
            self.overlay_hat.set(True)
            self.overlay_jacket.set(True)
            self.overlay_right_sleeve.set(True)
            self.overlay_left_sleeve.set(True)
            self.overlay_right_pants.set(True)
            self.overlay_left_pants.set(True)
            self.ortho.set(False)
            self.show_grid.set(True)

    def slim_cb(self) -> None:
        if self.view:
            self.view.slim = self.slim.get()

    def exploded_cb(self) -> None:
        if self.view:
            self.view.exploded = self.exploded.get()

    def overlays_cb(self, var: tkinter.IntVar) -> None:
        if self.view:
            self.view.show[
                self.overlay_lookup[self.overlay_lookup.index(var) + 1]
            ] = var.get()

    def ortho_cb(self) -> None:
        if self.view:
            self.view.ortho = self.ortho.get()

    def show_grid_cb(self) -> None:
        if self.view:
            self.view.grid = self.show_grid.get()
