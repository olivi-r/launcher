import base64
import datetime
import io
import json
import pathlib
import subprocess
import tkinter
import uuid

import editor

from lxml import etree
from PIL import Image, ImageTk
import portablemc.standard
import requests
import sv_ttk
import urllib3.exceptions


class Runner(portablemc.standard.StreamRunner):
    def process_stream_event(self, event: tkinter.Event) -> None:
        if isinstance(event, portablemc.standard.XmlStreamEvent):
            timestamp = datetime.datetime.fromtimestamp(event.time).strftime("%H:%M:%S")
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


class Launcher(tkinter.Tk):
    default_jvm_args = [
        "-Xmx2G",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M",
    ]

    def __init__(self, *args, **kwargs) -> None:
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

        # add bedrock instances tab
        self.bedrock_instances_tab = tkinter.ttk.Frame(self.content_frame)
        self.content_frame.add(self.bedrock_instances_tab, text="Bedrock Instances")

        # add java instances tab
        self.java_instances_tab = tkinter.ttk.Frame(self.content_frame)
        self.content_frame.add(self.java_instances_tab, text="Java Instances")

        # add skin editor tab
        self.editor = editor.Editor(self.content_frame)
        self.content_frame.add(self.editor, text="Skin Editor")

        sv_ttk.set_theme("dark")
        self.editor.set_background_color((0.15, 0.15, 0.15))
        self.theme_button.config(image=self.sun_image)

    def create_instance(
        self, name: str, version: str, loader: str = None, loader_version: str = None
    ) -> None:
        instance_id = str(uuid.uuid4())
        root = pathlib.Path("instances") / instance_id
        root.mkdir(parents=True, exist_ok=True)

        file = pathlib.Path("config.json")
        if not file.exists():
            conf = {"java-instances": []}

        else:
            with file.open("r") as fp:
                conf = json.load(fp)

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
            json.dump(conf, fp)

    @staticmethod
    def launch_dev_settings() -> None:
        subprocess.call(["start", "ms-settings:developers"])

    @staticmethod
    def download_appx(uuid: str, output_file: str) -> None:
        # configure namespaces
        soap = "{http://www.w3.org/2003/05/soap-envelope}"
        addressing = "{http://www.w3.org/2005/08/addressing}"
        secext = "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}"
        authorization = (
            "{http://schemas.microsoft.com/msus/2014/10/WindowsUpdateAuthorization}"
        )
        wssecurity = "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}"
        service = (
            "{http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService}"
        )

        time_created = datetime.datetime.now()
        time_expires = datetime.timedelta(minutes=5) + time_created

        # build request
        envelope = etree.Element(soap + "Envelope", {})
        header = etree.SubElement(envelope, soap + "Header")
        etree.SubElement(
            header, addressing + "Action", {soap + "mustUnderstand": "1"}
        ).text = "http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService/GetExtendedUpdateInfo2"
        etree.SubElement(
            header, addressing + "MessageID"
        ).text = "urn:uuid:af2aea53-49b2-4af5-b6df-80f78143023b"
        etree.SubElement(
            header, addressing + "To", {soap + "mustUnderstand": "1"}
        ).text = (
            "https://fe3.delivery.mp.microsoft.com/ClientWebService/client.asmx/secured"
        )
        security = etree.SubElement(
            header, secext + "Security", {soap + "mustUnderstand": "1"}
        )
        timestamp = etree.SubElement(
            security,
            wssecurity + "Timestamp",
        )
        etree.SubElement(timestamp, wssecurity + "Created").text = (
            time_created.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4] + "Z"
        )
        etree.SubElement(timestamp, wssecurity + "Expires").text = (
            time_expires.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4] + "Z"
        )
        windows_update_tickets_token = etree.SubElement(
            security,
            authorization + "WindowsUpdateTicketsToken",
            {wssecurity + "id": "ClientMSA"},
        )
        etree.SubElement(
            windows_update_tickets_token,
            "TicketType",
            {"Name": "AAD", "Version": "1.0", "Policy": "MBI_SSL"},
        ).text = ""
        body = etree.SubElement(envelope, soap + "Body")
        get_extended_update_info_2 = etree.SubElement(
            body, service + "GetExtendedUpdateInfo2"
        )
        update_ids = etree.SubElement(get_extended_update_info_2, service + "updateIDs")
        update_identity = etree.SubElement(update_ids, service + "UpdateIdentity")
        etree.SubElement(update_identity, service + "UpdateID").text = uuid
        etree.SubElement(update_identity, service + "RevisionNumber").text = "1"
        info_types = etree.SubElement(get_extended_update_info_2, service + "infoTypes")
        etree.SubElement(info_types, service + "XmlUpdateFragmentType").text = "FileUrl"
        etree.SubElement(
            info_types, service + "XmlUpdateFragmentType"
        ).text = "FileDecryption"
        etree.SubElement(
            info_types, service + "XmlUpdateFragmentType"
        ).text = "EsrpDecryptionInformation"
        etree.SubElement(
            info_types, service + "XmlUpdateFragmentType"
        ).text = "PiecesHashUrl"
        etree.SubElement(
            info_types, service + "XmlUpdateFragmentType"
        ).text = "BlockMapUrl"
        etree.SubElement(
            get_extended_update_info_2, service + "deviceAttributes"
        ).text = "E:BranchReadinessLevel=CBB&DchuNvidiaGrfxExists=1&ProcessorIdentifier=Intel64%20Family%206%20Model%2063%20Stepping%202&CurrentBranch=rs4_release&DataVer_RS5=1942&FlightRing=Retail&AttrDataVer=57&InstallLanguage=en-US&DchuAmdGrfxExists=1&OSUILocale=en-US&InstallationType=Client&FlightingBranchName=&Version_RS5=10&UpgEx_RS5=Green&GStatus_RS5=2&OSSkuId=48&App=WU&InstallDate=1529700913&ProcessorManufacturer=GenuineIntel&AppVer=10.0.17134.471&OSArchitecture=AMD64&UpdateManagementGroup=2&IsDeviceRetailDemo=0&HidOverGattReg=C%3A%5CWINDOWS%5CSystem32%5CDriverStore%5CFileRepository%5Chidbthle.inf_amd64_467f181075371c89%5CMicrosoft.Bluetooth.Profiles.HidOverGatt.dll&IsFlightingEnabled=0&DchuIntelGrfxExists=1&TelemetryLevel=1&DefaultUserRegion=244&DeferFeatureUpdatePeriodInDays=365&Bios=Unknown&WuClientVer=10.0.17134.471&PausedFeatureStatus=1&Steam=URL%3Asteam%20protocol&Free=8to16&OSVersion=10.0.17134.472&DeviceFamily=Windows.Desktop"

        payload = etree.tostring(envelope, pretty_print=1).decode()

        requests.packages.urllib3.disable_warnings(
            category=urllib3.exceptions.InsecureRequestWarning
        )
        with requests.Session() as s:
            response = s.post(
                "https://fe3.delivery.mp.microsoft.com/ClientWebService/client.asmx/secured",
                payload,
                verify=False,
                headers={
                    "Content-Type": "application/soap+xml; charset=utf-8",
                    "User-Agent": "Windows-Update-Agent/10.0.10011.16384 Client-Protocol/1.81",
                },
            )

            response.raise_for_status()
            new = etree.fromstring(response.content)
            url = new.xpath(
                "//ns:Url",
                namespaces={
                    "ns": "http://www.microsoft.com/SoftwareDistribution/Server/ClientWebService"
                },
            )[0].text

            response = s.get(url, stream=True)
            response.raise_for_status()
            with open(output_file, "wb+") as fp:
                for chunk in response.iter_content(chunk_size=8192):
                    fp.write(chunk)

    @staticmethod
    def start_bedrock() -> None:
        subprocess.call(
            [
                "explorer.exe",
                "shell:AppsFolder\\Microsoft.MinecraftUWP_8wekyb3d8bbwe!App",
            ]
        )

    @staticmethod
    def unregister_bedrock() -> None:
        subprocess.call(
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
    def register_bedrock(path: str) -> None:
        subprocess.call(
            [
                "powershell.exe",
                "Add-AppxPackage",
                "-Path",
                pathlib.Path(path) / "AppxManifest.xml",
                "-Register",
            ]
        )

    @staticmethod
    def get_skin(uuid: str) -> tuple:
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
    def get_face(skin: Image.Image) -> Image.Image:
        # get face of skin with overlays
        face = skin.crop((8, 8, 16, 16)).resize((64, 64), Image.Resampling.NEAREST)
        overlay = skin.crop((40, 8, 48, 16)).resize((72, 72), Image.Resampling.NEAREST)
        out = Image.new("RGBA", (72, 72))
        out.paste(face, (4, 4))
        out.paste(overlay, (0, 0), overlay)
        return out

    def toggle_theme(self) -> None:
        if self.tk.call("ttk::style", "theme", "use") == "sun-valley-dark":
            self.tk.call("set_theme", "light")
            self.editor.set_background_color((0.9, 0.9, 0.9))
            self.theme_button.config(image=self.moon_image)

        else:
            self.tk.call("set_theme", "dark")
            self.editor.set_background_color((0.15, 0.15, 0.15))
            self.theme_button.config(image=self.sun_image)


if __name__ == "__main__":
    Launcher.mainloop()
