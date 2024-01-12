import base64
from datetime import datetime
import io
import json
import pathlib
import tkinter.ttk
import uuid

from editor import Editor

from PIL import Image, ImageTk
import portablemc.standard
import requests
import sv_ttk


class Runner(portablemc.standard.StreamRunner):
    def process_stream_event(self, event):
        if isinstance(event, portablemc.standard.XmlStreamEvent):
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


class Watcher(portablemc.standard.Watcher):
    def __init__(self, output):
        super().__init__()
        self.output = output

    def handle(self, event) -> None:
        if isinstance(event, portablemc.standard.DownloadStartEvent):
            self.download_size = event.size

        elif isinstance(event, portablemc.standard.DownloadProgressEvent):
            complete = round(10 * (event.size / self.download_size))
            progress = (
                f"\x1b[32m"
                + "-" * complete
                + "\x1b[31m"
                + "-" * (10 - complete)
                + "\x1b[0m"
            )
            print(
                f"Download [{progress}] {event.size / 2 ** 20:.1f}M/{self.download_size / 2 ** 20:.1f}M {event.entry.name}",
                end="\r",
            )

        elif isinstance(event, portablemc.standard.DownloadCompleteEvent):
            print()

        else:
            print("event:", event)


class LauncherApp(tkinter.Tk):
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
        self.toolbar_frame = tkinter.ttk.Frame(self)
        self.toolbar_frame.pack(fill="x")

        # add light/dark mode button
        self.theme_button = tkinter.ttk.Button(
            self.toolbar_frame,
            text="",
            command=self.toggle_theme,
            style="Accent.TButton",
        )
        self.theme_button.pack(side="left", padx=5, pady=5)

        # tabbed page container
        self.content_frame = tkinter.ttk.Notebook(self)
        self.content_frame.pack(fill="both", expand=1)

        # add instances tab
        self.instances_tab = tkinter.ttk.Frame(self.content_frame)
        self.content_frame.add(self.instances_tab, text="Instances")

        # add skin editor tab
        self.editor = Editor(self.content_frame)
        self.content_frame.add(self.editor, text="Skin Editor")

        sv_ttk.set_theme("dark")
        self.theme_button.config(image=self.sun_image)

    def create_instance(self, name, version, loader=None, loader_version=None):
        instance_id = str(uuid.uuid4())
        root = pathlib.Path("instances") / instance_id
        root.mkdir(parents=True, exist_ok=True)

        file = pathlib.Path("config.json")
        if not file.exists():
            conf = {"instances": []}

        else:
            with file.open("r") as fp:
                conf = json.load(fp)

        loader_conf = {}
        if loader is not None:
            loader_conf["name"] = loader
            if loader_version is None:
                if loader == "forge":
                    loader_conf["version"] = "recommended"

        conf["instances"].append(
            {
                "name": name,
                "path": root.absolute(),
                "version": version,
                "loader": loader_conf,
                "jvm_args": self.default_jvm_args,
            }
        )

        with file.open("w+") as fp:
            json.dump(conf, fp)

    @staticmethod
    def get_skin(uuid: str):
        # fetch skin & cape from mojang api
        with requests.Session() as s:
            response = s.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
            )
            if response.ok:
                textures = json.loads(
                    base64.b64decode(
                        json.loads(response.content)["properties"][0]["value"]
                    )
                )["textures"]

                try:
                    response = s.get(textures["SKIN"]["url"])
                    if response.ok:
                        skin = Image.open(io.BytesIO(response.content))

                    else:
                        skin = None

                except KeyError:
                    skin = None

                try:
                    response = s.get(textures["CAPE"]["url"])
                    if response.ok:
                        cape = Image.open(io.BytesIO(response.content))

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
    LauncherApp().mainloop()
