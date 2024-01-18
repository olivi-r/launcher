import base64
import io
import json
import tkinter.ttk

import skin

import PIL.Image


class NewSkinPopup(tkinter.ttk.Frame):
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
            skin_img=self.get_template_skin(False),
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
            skin = self.get_default_skin(self.template_choice.get(), slim)

        else:
            skin = self.get_template_skin(slim)

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
                self.get_default_skin(self.template_choice.get(), self.slim.get())
            )

        else:
            self.template_choice.config(state="disabled")
            self.preview.set_skin(self.get_template_skin(self.slim.get()))

    def show(self) -> None:
        self.place(anchor="c", relx=0.5, rely=0.5, width=400, height=350)

    @staticmethod
    def get_template_skin(slim_arms: bool) -> PIL.Image.Image:
        arms = "slim" if slim_arms else "classic"
        with open("skins.json", "r") as fp:
            return PIL.Image.open(
                io.BytesIO(base64.b64decode(json.load(fp)["template"][arms]))
            )

    @staticmethod
    def get_default_skin(name: str, slim_arms: bool) -> PIL.Image.Image:
        arms = "slim" if slim_arms else "classic"
        with open("skins.json", "r") as fp:
            return PIL.Image.open(
                io.BytesIO(base64.b64decode(json.load(fp)["default"][name][arms]))
            )
