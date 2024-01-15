import ctypes
import glob
import tkinter


class Text:
    @staticmethod
    def install_fonts():
        for path in glob.glob("assets/fonts/*.otf"):
            assert (
                ctypes.WinDLL("gdi32").AddFontResourceW(path) != 0
            ), f"Failed to install: {path}"

    @staticmethod
    def render(formatted_text, *args, **kwargs):
        output = tkinter.Text(*args, **kwargs)
        output.tag_config("black", foreground="#000")
        output.tag_config("dark_blue", foreground="#00A")
        output.tag_config("dark_green", foreground="#0A0")
        output.tag_config("dark_aqua", foreground="#0AA")
        output.tag_config("dark_red", foreground="#A00")
        output.tag_config("dark_purple", foreground="#A0A")
        output.tag_config("gold", foreground="#FA0")
        output.tag_config("gray", foreground="#AAA")
        output.tag_config("dark_gray", foreground="#555")
        output.tag_config("blue", foreground="#55F")
        output.tag_config("green", foreground="#5F5")
        output.tag_config("aqua", foreground="#5FF")
        output.tag_config("red", foreground="#F55")
        output.tag_config("light_purple", foreground="#F5F")
        output.tag_config("yellow", foreground="#FF5")
        output.tag_config("white", foreground="#FFF")
        output.tag_config("minecoin_gold", foreground="#DDD605")
        output.tag_config("material_quartz", foreground="#E3D4D1")
        output.tag_config("material_iron", foreground="#CECACA")
        output.tag_config("material_netherite", foreground="#443A3B")
        output.tag_config("material_redstone", foreground="#971607")
        output.tag_config("material_copper", foreground="#B4684D")
        output.tag_config("material_gold", foreground="#DEB12D")
        output.tag_config("material_emerald", foreground="#47A036")
        output.tag_config("material_diamond", foreground="#2CBAA8")
        output.tag_config("material_lapis", foreground="#21497B")
        output.tag_config("material_amethyst", foreground="#9A5CC6")

        output.config(font=("Minecraft", 10))
        output.tag_config("bold", font=("Minecraft", 10, "bold"))
        output.tag_config("italic", font=("Minecraft", 10, "italic"))
        output.tag_config("bold italic", font=("Minecraft", 10, "bold italic"))

        for segment in formatted_text:
            output.insert(
                "end", segment[0].encode("unicode-escape").decode("utf-8"), segment[1]
            )

        return output

    @staticmethod
    def parse(text: str) -> tuple:
        emitted = ()
        color = ""
        bold = False
        italic = False
        current = ()
        segment = ""
        skip = 0
        for i, char in enumerate(text):
            if skip:
                skip -= 1
                continue

            if char == "§" and i < len(text) - 1:
                skip = 1
                if segment:
                    if bold and italic:
                        config = ("bold italic",)

                    elif bold:
                        config = ("bold",)

                    elif italic:
                        config = ("italic",)

                    else:
                        config = ("normal",)

                    if color:
                        emitted += ((segment, current + config + (color,)),)

                    else:
                        emitted += ((segment, current + config),)

                prev_segment = segment
                segment = ""
                match text[i + 1]:
                    case "0":
                        color = "black"

                    case "1":
                        color = "dark_blue"

                    case "2":
                        color = "dark_green"

                    case "3":
                        color = "dark_aqua"

                    case "4":
                        color = "dark_red"

                    case "5":
                        color = "dark_purple"

                    case "6":
                        color = "gold"

                    case "7":
                        color = "gray"

                    case "8":
                        color = "dark_gray"

                    case "9":
                        color = "blue"

                    case "a":
                        color = "green"

                    case "b":
                        color = "aqua"

                    case "c":
                        color = "red"

                    case "d":
                        color = "light_purple"

                    case "e":
                        color = "yellow"

                    case "f":
                        color = "white"

                    case "g":
                        color = "minecoin_gold"

                    case "h":
                        color = "material_quartz"

                    case "i":
                        color = "material_iron"

                    case "j":
                        color = "material_netherite"

                    case "k":
                        # currently unsupported
                        current += ("obfuscated",)

                    case "l":
                        bold = True

                    case "m":
                        color = "material_redstone"

                    case "n":
                        color = "material_copper"

                    case "o":
                        italic = True

                    case "p":
                        color = "material_gold"

                    case "q":
                        color = "material_emerald"

                    case "r":
                        current = ()
                        bold = False
                        italic = False
                        color = ""

                    case "s":
                        color = "material_diamond"

                    case "t":
                        color = "material_lapis"

                    case "u":
                        color = "material_amethyst"

                    case _:
                        segment = prev_segment + char
                        emitted = emitted[:-1]
                        skip = 0

            else:
                segment += char

        if segment:
            if bold and italic:
                config = ("bold italic",)

            elif bold:
                config = ("bold",)

            elif italic:
                config = ("italic",)

            else:
                config = ("normal",)

            if color:
                emitted += ((segment, current + config + (color,)),)

            else:
                emitted += ((segment, current + config),)

        return emitted
