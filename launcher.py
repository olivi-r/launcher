from base64 import b64decode
from datetime import datetime
from io import BytesIO
from json import dump, load, loads
from pathlib import Path
from subprocess import call
from tkinter import Tk, ttk
from uuid import uuid4

from editor import Editor

from PIL import Image, ImageTk
from portablemc.standard import StreamRunner, XmlStreamEvent
from requests import Session
from sv_ttk import set_theme


class Runner(StreamRunner):
    def process_stream_event(self, event):
        if isinstance(event, XmlStreamEvent):
            timestamp = datetime.fromtimestamp(event.time).strftime("%H:%M:%S")
            message = f"[{timestamp}] [{event.thread}/{event.level}] {event.message}"

            match event.level:
                case "INFO":
                    print(message)

                case "WARN":
                    print(f"\x1b[33m{message}\x1b[0m")

                case "ERROR":
                    print(f"\x1b[31m{message}\x1b[0m")

                case _:
                    print(f"\x1b[34m{message}\x1b[0m")

        elif isinstance(event, str):
            print(event.strip())


class Launcher(Tk):
    default_jvm_args = [
        "-Xmx2G",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # load light/dark mode icons
        self.sun_image = ImageTk.PhotoImage(
            Image.open("assets/sun.png").resize((20, 20))
        )
        self.moon_image = ImageTk.PhotoImage(
            Image.open("assets/moon.png").resize((20, 20))
        )

        # add toolbar
        self.toolbar_frame = ttk.Frame(self)
        self.toolbar_frame.pack(fill="x")

        # add light/dark mode button
        self.theme_button = ttk.Button(
            self.toolbar_frame,
            text="",
            command=self.toggle_theme,
            style="Accent.TButton",
        )
        self.theme_button.pack(side="left", padx=5, pady=5)

        # tabbed page container
        self.content_frame = ttk.Notebook(self)
        self.content_frame.pack(fill="both", expand=1)

        # add instances tab
        self.instances_tab = ttk.Frame(self.content_frame)
        self.content_frame.add(self.instances_tab, text="Instances")

        # add skin editor tab
        self.editor = Editor(self.content_frame)
        self.content_frame.add(self.editor, text="Skin Editor")

        set_theme("dark")
        self.editor.set_background_color((0.15, 0.15, 0.15))
        self.theme_button.config(image=self.sun_image)

    def create_instance(self, name, version, loader=None, loader_version=None):
        instance_id = str(uuid4())
        root = Path("instances") / instance_id
        root.mkdir(parents=True, exist_ok=True)

        file = Path("config.json")
        if not file.exists():
            conf = {"java-instances": []}

        else:
            with file.open("r") as fp:
                conf = load(fp)

        loader_conf = {}
        if loader is not None:
            loader_conf["name"] = loader
            if loader_version is None:
                if loader == "forge":
                    loader_conf["version"] = "recommended"

        conf["java-instances"].append(
            {
                "name": name,
                "path": root.absolute(),
                "version": version,
                "loader": loader_conf,
                "jvm_args": self.default_jvm_args,
            }
        )

        with file.open("w+") as fp:
            dump(conf, fp)

    @staticmethod
    def start_bedrock():
        call(
            [
                "explorer.exe",
                "shell:AppsFolder\\Microsoft.MinecraftUWP_8wekyb3d8bbwe!App",
            ]
        )

    @staticmethod
    def unregister_bedrock():
        call(
            [
                "powershell.exe",
                "Get-AppxPackage",
                "Microsoft.MinecraftUWP",
                "|",
                "Remove-AppxPackage",
                "-PreserveApplicationData",
            ]
        )

    @staticmethod
    def register_bedrock(path):
        call(
            [
                "powershell.exe",
                "Add-AppxPackage",
                "-Path",
                Path(path) / "AppxManifest.xml",
                "-Register",
            ]
        )

    @staticmethod
    def get_skin(uuid: str):
        # fetch skin & cape from mojang api
        with Session() as s:
            response = s.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
            )
            if response.ok:
                textures = loads(
                    b64decode(loads(response.content)["properties"][0]["value"])
                )["textures"]

                try:
                    response = s.get(textures["SKIN"]["url"])
                    if response.ok:
                        skin = Image.open(BytesIO(response.content))

                    else:
                        skin = None

                except KeyError:
                    skin = None

                try:
                    response = s.get(textures["CAPE"]["url"])
                    if response.ok:
                        cape = Image.open(BytesIO(response.content))

                    else:
                        cape = None

                except KeyError:
                    cape = None

        return skin, cape

    @staticmethod
    def get_face(skin: Image) -> Image:
        # get face of skin with overlays
        face = skin.crop((8, 8, 16, 16)).resize((64, 64), Image.Resampling.NEAREST)
        overlay = skin.crop((40, 8, 48, 16)).resize((72, 72), Image.Resampling.NEAREST)
        out = Image.new("RGBA", (72, 72))
        out.paste(face, (4, 4))
        out.paste(overlay, (0, 0), overlay)
        return out

    def toggle_theme(self):
        if self.tk.call("ttk::style", "theme", "use") == "sun-valley-dark":
            self.tk.call("set_theme", "light")
            self.editor.set_background_color((0.9, 0.9, 0.9))
            self.theme_button.config(image=self.moon_image)

        else:
            self.tk.call("set_theme", "dark")
            self.editor.set_background_color((0.15, 0.15, 0.15))
            self.theme_button.config(image=self.sun_image)


if __name__ == "__main__":
    Launcher().mainloop()
