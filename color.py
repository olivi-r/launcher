import colorsys
import re
import tkinter.ttk

import numpy as np
from PIL import Image, ImageDraw, ImageTk


class ColorPicker(tkinter.ttk.Frame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.hue = 0
        self.saturation = 0.5
        self.lightness = 0.5

        self.sub_frame = tkinter.ttk.Frame(self)
        self.sub_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5)

        self.square = tkinter.Canvas(
            self.sub_frame,
            width=200,
            height=150,
            bg="#000",
            borderwidth=0,
            highlightthickness=0,
        )
        self.square.pack(pady=5)
        self.square.bind("<Button-1>", self._ev_square)
        self.square.bind("<B1-Motion>", self._ev_square)

        self.hue_bar = tkinter.Canvas(
            self.sub_frame, width=200, height=30, borderwidth=0, highlightthickness=0
        )
        self.hue_bar.pack(pady=5)
        self.hue_bar.bind("<Button-1>", self._ev_hue)
        self.hue_bar.bind("<B1-Motion>", self._ev_hue)

        self.output = tkinter.ttk.Label(self.sub_frame)
        self.output.pack(pady=5)

        self.hex_value = tkinter.StringVar(self)
        self.hex_value.trace_add("write", lambda *_: self._hex_value_cb(self.hex_value))
        self.red_value = tkinter.StringVar(self)
        self.red_value.trace_add("write", lambda *_: self._red_value_cb(self.red_value))
        self.green_value = tkinter.StringVar(self)
        self.green_value.trace_add(
            "write", lambda *_: self._green_value_cb(self.green_value)
        )
        self.blue_value = tkinter.StringVar(self)
        self.blue_value.trace_add(
            "write", lambda *_: self._blue_value_cb(self.blue_value)
        )
        self.hsl_h_value = tkinter.StringVar(self)
        self.hsl_h_value.trace_add(
            "write", lambda *_: self._hue_value_cb(self.hsl_h_value)
        )
        self.hsl_s_value = tkinter.StringVar(self)
        self.hsl_s_value.trace_add(
            "write", lambda *_: self._hsl_s_value_cb(self.hsl_s_value)
        )
        self.hsl_l_value = tkinter.StringVar(self)
        self.hsl_l_value.trace_add(
            "write", lambda *_: self._hsl_l_value_cb(self.hsl_l_value)
        )
        self.hsv_h_value = tkinter.StringVar(self)
        self.hsv_h_value.trace_add(
            "write", lambda *_: self._hue_value_cb(self.hsv_h_value)
        )
        self.hsv_s_value = tkinter.StringVar(self)
        self.hsv_s_value.trace_add(
            "write", lambda *_: self._hsv_s_value_cb(self.hsv_s_value)
        )
        self.hsv_v_value = tkinter.StringVar(self)
        self.hsv_v_value.trace_add(
            "write", lambda *_: self._hsv_v_value_cb(self.hsv_v_value)
        )

        tkinter.ttk.Label(self, text="HEX:").grid(row=1, column=0, padx=5, pady=15)
        self.hex_entry = tkinter.ttk.Entry(self, width=8, textvariable=self.hex_value)
        self.hex_entry.grid(row=1, column=1, columnspan=3)

        tkinter.ttk.Label(self, text="RGB:").grid(row=2, column=0, pady=15)
        self.red_entry = tkinter.ttk.Entry(self, width=5, textvariable=self.red_value)
        self.red_entry.grid(row=2, column=1, padx=5)
        self.green_entry = tkinter.ttk.Entry(
            self, width=5, textvariable=self.green_value
        )
        self.green_entry.grid(row=2, column=2, padx=5)
        self.blue_entry = tkinter.ttk.Entry(self, width=5, textvariable=self.blue_value)
        self.blue_entry.grid(row=2, column=3, padx=5)

        tkinter.ttk.Label(self, text="HSL:").grid(row=3, column=0, pady=15)
        self.hsl_h_entry = tkinter.ttk.Entry(
            self, width=5, textvariable=self.hsl_h_value
        )
        self.hsl_h_entry.grid(row=3, column=1)
        self.hsl_s_entry = tkinter.ttk.Entry(
            self, width=5, textvariable=self.hsl_s_value
        )
        self.hsl_s_entry.grid(row=3, column=2)
        self.hsl_l_entry = tkinter.ttk.Entry(
            self, width=5, textvariable=self.hsl_l_value
        )
        self.hsl_l_entry.grid(row=3, column=3)

        tkinter.ttk.Label(self, text="HSV:").grid(row=4, column=0, pady=15)
        self.hsv_h_entry = tkinter.ttk.Entry(
            self, width=5, textvariable=self.hsv_h_value
        )
        self.hsv_h_entry.grid(row=4, column=1)
        self.hsv_s_entry = tkinter.ttk.Entry(
            self, width=5, textvariable=self.hsv_s_value
        )
        self.hsv_s_entry.grid(row=4, column=2)
        self.hsv_v_entry = tkinter.ttk.Entry(
            self, width=5, textvariable=self.hsv_v_value
        )
        self.hsv_v_entry.grid(row=4, column=3)

        for i in range(200):
            self.hue_bar.create_line(
                i,
                0,
                i,
                30,
                fill="#%02X%02X%02X"
                % tuple(
                    map(lambda x: round(x * 255), colorsys.hls_to_rgb(i / 200, 0.5, 1))
                ),
            )

        self.update()

    def _hex_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            value = var.get()
            m = re.match(r"#?(?P<value>([0-9a-fA-F]{6}|[0-9a-fA-F]{3}))?$", value)
            if m:
                if not value:
                    value = "000"

                else:
                    value = m.group("value")

                if len(value) == 3:
                    red = value[0] * 2
                    green = value[1] * 2
                    blue = value[2] * 2

                else:
                    red = value[:2]
                    green = value[2:4]
                    blue = value[4:]

                self.hue, self.lightness, self.saturation = colorsys.rgb_to_hls(
                    int(red, 16) / 255, int(green, 16) / 255, int(blue, 16) / 255
                )

                self.update()

    def _red_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            value = var.get()
            m = re.match(r"[0-9]*$", value)
            if m:
                if not value:
                    value = 0

                value = int(value)
                if value < 256:
                    self.hue, self.lightness, self.saturation = colorsys.rgb_to_hls(
                        value / 255,
                        *colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation)[
                            1:
                        ],
                    )

                    self.update()

    def _green_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            value = var.get()
            m = re.match(r"[0-9]*$", value)
            if m:
                if not value:
                    value = 0

                value = int(value)
                if value < 256:
                    r, _, b = colorsys.hls_to_rgb(
                        self.hue, self.lightness, self.saturation
                    )
                    self.hue, self.lightness, self.saturation = colorsys.rgb_to_hls(
                        r, value / 255, b
                    )

                    self.update()

    def _blue_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            value = var.get()
            m = re.match(r"[0-9]*$", value)
            if m:
                if not value:
                    value = 0

                value = int(value)
                if value < 256:
                    self.hue, self.lightness, self.saturation = colorsys.rgb_to_hls(
                        *colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation)[
                            :-1
                        ],
                        value / 255,
                    )

                    self.update()

    def _hue_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            m = re.match(r"(?P<value>[0-9]*)°?$", var.get())
            if m:
                value = m.group("value")
                if not value:
                    value = 0

                else:
                    value = int(value)

                if value < 361:
                    self.hue = value / 360
                    self.update()

    def _hsl_s_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            m = re.match(r"(?P<value>[0-9]*)%?$", var.get())
            if m:
                value = m.group("value")
                if not value:
                    value = 0

                else:
                    value = int(value)

                if value < 101:
                    self.saturation = value / 100
                    self.update()

    def _hsl_l_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            m = re.match(r"(?P<value>[0-9]*)%?$", var.get())
            if m:
                value = m.group("value")
                if not value:
                    value = 0

                else:
                    value = int(value)

                if value < 101:
                    self.lightness = value / 100
                    self.update()

    def _hsv_s_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            m = re.match(r"(?P<value>[0-9]*)%?$", var.get())
            if m:
                value = m.group("value")
                if not value:
                    value = 0

                else:
                    value = int(value)

                if value < 101:
                    h, _, v = colorsys.rgb_to_hsv(
                        *colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation)
                    )
                    self.hue, self.lightness, self.saturation = colorsys.rgb_to_hls(
                        *colorsys.hsv_to_rgb(h, value / 100, v)
                    )

                    self.update()

    def _hsv_v_value_cb(self, var: tkinter.StringVar) -> None:
        if not self.disable_cb:
            m = re.match(r"(?P<value>[0-9]*)%?$", var.get())
            if m:
                value = m.group("value")
                if not value:
                    value = 0

                else:
                    value = int(value)

                if value < 101:
                    h, s, _ = colorsys.rgb_to_hsv(
                        *colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation)
                    )
                    self.hue, self.lightness, self.saturation = colorsys.rgb_to_hls(
                        *colorsys.hsv_to_rgb(h, s, value / 100)
                    )

                    self.update()

    @property
    def color(self) -> str:
        c = "#%02X%02X%02X" % tuple(
            map(
                lambda x: round(x * 255),
                colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation),
            )
        )
        if all([c[2 * i + 1] == c[2 * i + 2] for i in range(3)]):
            c = c[::2]

        return c

    def update(self) -> None:
        self.disable_cb = True

        # update circle
        circle = Image.new("RGBA", (256, 256))
        draw = ImageDraw.Draw(circle)
        draw.ellipse((10, 10, 245, 245), fill=self.color, outline=self.color)
        circle = ImageTk.PhotoImage(circle.resize((40, 40)))
        self.output.config(image=circle)
        self.output.image = circle

        # update square
        self.slice = ImageTk.PhotoImage(
            Image.fromarray(
                np.array(
                    [
                        [
                            list(
                                map(
                                    lambda x: round(x * 255),
                                    colorsys.hsv_to_rgb(
                                        self.hue, x / 200, (150 - y) / 150
                                    ),
                                )
                            )
                            for x in range(200)
                        ]
                        for y in range(150)
                    ],
                    "uint8",
                ),
                mode="RGB",
            )
        )

        self.square.create_image(0, 0, anchor="nw", image=self.slice)

        hsv = colorsys.rgb_to_hsv(
            *colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation)
        )
        self.square.create_oval(
            hsv[1] * 200 - 3,
            150 - hsv[2] * 150 - 3,
            hsv[1] * 200 + 3,
            150 - hsv[2] * 150 + 3,
            fill="#fff",
            width=0,
        )

        # update hex
        self.hex_value.set(self.color)

        # update rgb
        rgb = colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation)
        self.red_value.set(round(rgb[0] * 255))
        self.green_value.set(round(rgb[1] * 255))
        self.blue_value.set(round(rgb[2] * 255))

        # update hsl
        self.hsl_h_value.set(f"{round(self.hue * 360)}°")
        self.hsl_s_value.set(f"{round(self.saturation * 100)}%")
        self.hsl_l_value.set(f"{round(self.lightness * 100)}%")

        # update hsv
        _, s, v = colorsys.rgb_to_hsv(*rgb)
        self.hsv_h_value.set(f"{round(self.hue * 360)}°")
        self.hsv_s_value.set(f"{round(s*100)}%")
        self.hsv_v_value.set(f"{round(v*100)}%")

        self.disable_cb = False

    def _ev_hue(self, event: tkinter.Event) -> None:
        self.hue = min(200, max(0, event.x)) / 200
        self.update()

    def _ev_square(self, event: tkinter.Event) -> None:
        saturation = min(200, max(0, event.x)) / 200
        value = min(150, max(0, 150 - event.y)) / 150
        _, self.lightness, self.saturation = colorsys.rgb_to_hls(
            *colorsys.hsv_to_rgb(self.hue, saturation, value)
        )
        self.update()
