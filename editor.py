import tkinter.ttk

import color
import popups
import skin

import PIL.Image


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

    def popup(self) -> None:
        p = popups.NewSkinPopup(self)
        self.popups.append(p)
        p.show()

    def set_background_color(self, color: tuple) -> None:
        self.background_color = color

        popups.NewSkinPopup.background_color = color
        for popup in self.popups:
            popup.preview.background_color = color

        for view in self.views:
            view.background_color = self.background_color

    def create_tab(
        self,
        name: str,
        skin_img: PIL.Image.Image,
        slim: bool,
        cape_img: PIL.Image.Image = None,
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
            self.view.show[self.overlay_lookup[self.overlay_lookup.index(var) + 1]] = (
                var.get()
            )

    def ortho_cb(self) -> None:
        if self.view:
            self.view.ortho = self.ortho.get()

    def show_grid_cb(self) -> None:
        if self.view:
            self.view.grid = self.show_grid.get()
