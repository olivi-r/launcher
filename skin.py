import tkinter

import numpy
from OpenGL.GL import *
from OpenGL.GLU import *
import PIL.Image
import pyopengltk


class Box:
    def __init__(
        self,
        pos_x: float,
        pos_y: float,
        pos_z: float,
        exp_x: float,
        exp_y: float,
        exp_z: float,
        pix_x: float,
        pix_y: float,
        pix_z: float,
        piv_x: float,
        piv_y: float,
        piv_z: float,
        rot_x: float,
        rot_y: float,
        rot_z: float,
        u: float,
        v: float,
        inc: float = 0,
    ) -> None:
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z

        self.exp_x = exp_x
        self.exp_y = exp_y
        self.exp_z = exp_z

        self.scl_x = pix_x + inc
        self.scl_y = pix_y + inc
        self.scl_z = pix_z + inc

        self.piv_x = piv_x
        self.piv_y = piv_y
        self.piv_z = piv_z

        self.rot_x = rot_x
        self.rot_y = rot_y
        self.rot_z = rot_z

        self.vertices = (
            numpy.array([-0.5, -0.5, 0.5, 1]),
            numpy.array([-0.5, 0.5, 0.5, 1]),
            numpy.array([0.5, 0.5, 0.5, 1]),
            numpy.array([0.5, -0.5, 0.5, 1]),
            numpy.array([0.5, -0.5, -0.5, 1]),
            numpy.array([0.5, 0.5, -0.5, 1]),
            numpy.array([-0.5, 0.5, -0.5, 1]),
            numpy.array([-0.5, -0.5, -0.5, 1]),
        )

        # for

        self.grid = []

        # grid lines wrapping x axis
        for x in range(pix_x + 1):
            # front
            self.grid.append(
                (
                    self.vertices[0] + numpy.array([x / pix_x, 0, 0, 0]),
                    self.vertices[1] + numpy.array([x / pix_x, 0, 0, 0]),
                )
            )
            # back
            self.grid.append(
                (
                    self.vertices[6] + numpy.array([x / pix_x, 0, 0, 0]),
                    self.vertices[7] + numpy.array([x / pix_x, 0, 0, 0]),
                )
            )
            # top
            self.grid.append(
                (
                    self.vertices[1] + numpy.array([x / pix_x, 0, 0, 0]),
                    self.vertices[6] + numpy.array([x / pix_x, 0, 0, 0]),
                )
            )
            # bottom
            self.grid.append(
                (
                    self.vertices[0] + numpy.array([x / pix_x, 0, 0, 0]),
                    self.vertices[7] + numpy.array([x / pix_x, 0, 0, 0]),
                )
            )

        # grid lines wrapping y axis
        for y in range(pix_y + 1):
            # front
            self.grid.append(
                (
                    self.vertices[0] + numpy.array([0, y / pix_y, 0, 0]),
                    self.vertices[3] + numpy.array([0, y / pix_y, 0, 0]),
                )
            )
            # back
            self.grid.append(
                (
                    self.vertices[4] + numpy.array([0, y / pix_y, 0, 0]),
                    self.vertices[7] + numpy.array([0, y / pix_y, 0, 0]),
                )
            )
            # right
            self.grid.append(
                (
                    self.vertices[0] + numpy.array([0, y / pix_y, 0, 0]),
                    self.vertices[7] + numpy.array([0, y / pix_y, 0, 0]),
                )
            )
            # left
            self.grid.append(
                (
                    self.vertices[3] + numpy.array([0, y / pix_y, 0, 0]),
                    self.vertices[4] + numpy.array([0, y / pix_y, 0, 0]),
                )
            )

        # grid lines wrapping z axis
        for z in range(pix_z + 1):
            # top
            self.grid.append(
                (
                    self.vertices[5] + numpy.array([0, 0, z / pix_z, 0]),
                    self.vertices[6] + numpy.array([0, 0, z / pix_z, 0]),
                )
            )
            # bottom
            self.grid.append(
                (
                    self.vertices[4] + numpy.array([0, 0, z / pix_z, 0]),
                    self.vertices[7] + numpy.array([0, 0, z / pix_z, 0]),
                )
            )
            # right
            self.grid.append(
                (
                    self.vertices[6] + numpy.array([0, 0, z / pix_z, 0]),
                    self.vertices[7] + numpy.array([0, 0, z / pix_z, 0]),
                )
            )
            # left
            self.grid.append(
                (
                    self.vertices[4] + numpy.array([0, 0, z / pix_z, 0]),
                    self.vertices[5] + numpy.array([0, 0, z / pix_z, 0]),
                )
            )

        self.quads = (
            (  # front
                0,
                1,
                2,
                3,
                u + pix_z / 64,
                v + (pix_y + pix_z) / 64,
                u + pix_z / 64,
                v + pix_z / 64,
                u + (pix_x + pix_z) / 64,
                v + pix_z / 64,
                u + (pix_x + pix_z) / 64,
                v + (pix_y + pix_z) / 64,
            ),
            (  # back
                4,
                5,
                6,
                7,
                u + (2 * pix_z + pix_x) / 64,
                v + (pix_y + pix_z) / 64,
                u + (2 * pix_z + pix_x) / 64,
                v + pix_z / 64,
                u + (2 * pix_z + 2 * pix_x) / 64,
                v + pix_z / 64,
                u + (2 * pix_z + 2 * pix_x) / 64,
                v + (pix_y + pix_z) / 64,
            ),
            (  # top
                1,
                6,
                5,
                2,
                u + pix_z / 64,
                v + pix_z / 64,
                u + pix_z / 64,
                v,
                u + (pix_x + pix_z) / 64,
                v,
                u + (pix_x + pix_z) / 64,
                v + pix_z / 64,
            ),
            (  # bottom
                0,
                7,
                4,
                3,
                u + (pix_x + pix_z) / 64,
                v + pix_z / 64,
                u + (pix_x + pix_z) / 64,
                v,
                u + (2 * pix_x + pix_z) / 64,
                v,
                u + (2 * pix_x + pix_z) / 64,
                v + pix_z / 64,
            ),
            (  # right
                7,
                6,
                1,
                0,
                u,
                v + (pix_y + pix_z) / 64,
                u,
                v + pix_z / 64,
                u + pix_z / 64,
                v + pix_z / 64,
                u + pix_z / 64,
                v + (pix_y + pix_z) / 64,
            ),
            (  # left
                3,
                2,
                5,
                4,
                u + (pix_x + pix_z) / 64,
                v + (pix_y + pix_z) / 64,
                u + (pix_x + pix_z) / 64,
                v + pix_z / 64,
                u + (pix_x + 2 * pix_z) / 64,
                v + pix_z / 64,
                u + (pix_x + 2 * pix_z) / 64,
                v + (pix_y + pix_z) / 64,
            ),
        )


class SkinView(pyopengltk.OpenGLFrame):
    def __init__(
        self,
        *args,
        slim: bool,
        skin_img: PIL.Image.Image,
        cape_img: PIL.Image.Image = None,
        exploded: bool = False,
        grid: bool = False,
        dragable: bool = True,
        drag_speed: float = 0.4,
        move_speed: float = 0.1,
        rot_x: float = 0,
        rot_y: float = 0,
        ortho: bool = False,
        show: dict = {},
        background_color: tuple = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.background_color = background_color
        self.ortho = ortho

        self.exploded = exploded
        self.grid = grid
        self.slim = slim

        self.show = {
            "hat": True,
            "jacket": True,
            "right-sleeve": True,
            "left-sleeve": True,
            "right-pants": True,
            "left-pants": True,
        }
        self.show.update(show)

        self.has_cape = cape_img is not None

        # layer visibility defaults
        self.show_cape = True
        self.show_hat = True
        self.show_jacket = True
        self.show_right_sleeve = True
        self.show_left_sleeve = True
        self.show_right_pants = True
        self.show_left_pants = True

        self.skin_overlays = {
            "hat": Box(0, 28, 0, 0, 33, 0, 8, 8, 8, 0, 24, 0, 0, 0, 0, 0.5, 0, 1),
            "jacket": Box(
                0, 18, 0, 0, 18, 0, 8, 12, 4, 0, 24, 0, 0, 0, 0, 0.25, 0.5, 0.5
            ),
            "right-pants": Box(
                -2, 6, 0, -4.5, 1, 0, 4, 12, 4, -1.9, 12, 0, 0, 0, 0, 0, 0.5, 0.5
            ),
            "left-pants": Box(
                2, 6, 0, 4.5, 1, 0, 4, 12, 4, 1.9, 12, 0, 0, 0, 0, 0, 0.75, 0.5
            ),
        }

        self.cape = Box(
            0, 16, -3.5, 0, 16, 1.5, 10, 16, 1, 0, 24, -3, -15, 180, 0, 0, 0
        )

        self.set_skin(skin_img)

        self.cape_img = cape_img
        if self.has_cape:
            try:
                self.cape_img = cape_img.size + (
                    numpy.array(list(cape_img.convert("RGBA").getdata()), numpy.uint8),
                )

            finally:
                cape_img.close()

        if dragable:
            self.bind("<Button-1>", self.set_pos)
            self.bind("<B1-Motion>", self.drag)
            self.bind("<MouseWheel>", self.scroll)
            self.bind("<Button-3>", self.set_pos)
            self.bind("<B3-Motion>", self.move)
            self.bind("<Motion>", self.set_pos)

        self.drag_speed = drag_speed
        self.move_speed = move_speed
        self.prev = [0, 0]

        self.drag_x = 0
        self.drag_y = 0
        self.x_rot = rot_x
        self.y_rot = rot_y

        self.zoom = 1

        self.move_x = 0
        self.move_y = 0
        self.x_off = 0
        self.y_off = 0

        self.walk_speed = 20

    def set_skin(self, skin_img: PIL.Image.Image) -> None:
        try:
            self.skin_img = skin_img.size + (
                numpy.array(list(skin_img.convert("RGBA").getdata()), numpy.uint8),
            )

        finally:
            skin_img.close()

    def set_pos(self, event: tkinter.Event) -> None:
        self.prev = [event.x, event.y]

    def drag(self, event: tkinter.Event) -> None:
        self.drag_x = event.x - self.prev[0]
        self.drag_y = event.y - self.prev[1]
        self.prev = [event.x, event.y]

    def scroll(self, event: tkinter.Event) -> None:
        self.zoom += event.delta / 800
        self.zoom = min(5, max(0.25, self.zoom))

    def move(self, event: tkinter.Event) -> None:
        self.move_x = event.x - self.prev[0]
        self.move_y = event.y - self.prev[1]
        self.prev = [event.x, event.y]

    def initgl(self) -> None:
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)

    def redraw(self) -> None:
        glViewport(0, 0, self.width, self.height)

        self.textures = glGenTextures(2)

        # skin texture
        glBindTexture(GL_TEXTURE_2D, self.textures[0])
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            *self.skin_img[:2],
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            self.skin_img[-1],
        )

        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        if self.cape_img is not None:
            # cape texture
            glBindTexture(GL_TEXTURE_2D, self.textures[1])

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                *self.cape_img[:2],
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                self.cape_img[-1],
            )

            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.skin = {
            "hat": Box(0, 28, 0, 0, 33, 0, 8, 8, 8, 0, 24, 0, 0, 0, 0, 0, 0),
            "jacket": Box(0, 18, 0, 0, 18, 0, 8, 12, 4, 0, 24, 0, 0, 0, 0, 0.25, 0.25),
            "right-pants": Box(
                -2, 6, 0, -4.5, 1, 0, 4, 12, 4, -1.9, 12, 0, 0, 0, 0, 0, 0.25
            ),
            "left-pants": Box(
                2, 6, 0, 4.5, 1, 0, 4, 12, 4, 1.9, 12, 0, 0, 0, 0, 0.25, 0.75
            ),
        }

        if self.slim:
            self.skin.update(
                {
                    "right-sleeve": Box(
                        -5.5,
                        18,
                        0,
                        -10.5,
                        18,
                        0,
                        3,
                        12,
                        4,
                        -5,
                        21.5,
                        0,
                        0,
                        0,
                        0,
                        0.625,
                        0.25,
                    ),
                    "left-sleeve": Box(
                        5.5,
                        18,
                        0,
                        10.5,
                        18,
                        0,
                        3,
                        12,
                        4,
                        5,
                        21.5,
                        0,
                        0,
                        0,
                        0,
                        0.5,
                        0.75,
                    ),
                }
            )

            self.skin_overlays.update(
                {
                    "right-sleeve": Box(
                        -5.5,
                        18,
                        0,
                        -10.5,
                        18,
                        0,
                        3,
                        12,
                        4,
                        -5,
                        21.5,
                        0,
                        0,
                        0,
                        0,
                        0.625,
                        0.5,
                        0.5,
                    ),
                    "left-sleeve": Box(
                        5.5,
                        18,
                        0,
                        10.5,
                        18,
                        0,
                        3,
                        12,
                        4,
                        5,
                        21.5,
                        0,
                        0,
                        0,
                        0,
                        0.75,
                        0.75,
                        0.5,
                    ),
                }
            )

        else:
            self.skin.update(
                {
                    # arms
                    "right-sleeve": Box(
                        -6, 18, 0, -11, 18, 0, 4, 12, 4, -5, 22, 0, 0, 0, 0, 0.625, 0.25
                    ),
                    "left-sleeve": Box(
                        6, 18, 0, 11, 18, 0, 4, 12, 4, 5, 22, 0, 0, 0, 0, 0.5, 0.75
                    ),
                }
            )

            self.skin_overlays.update(
                {
                    "right-sleeve": Box(
                        -6,
                        18,
                        0,
                        -11,
                        18,
                        0,
                        4,
                        12,
                        4,
                        -5,
                        22,
                        0,
                        0,
                        0,
                        0,
                        0.625,
                        0.5,
                        0.5,
                    ),
                    "left-sleeve": Box(
                        6,
                        18,
                        0,
                        11,
                        18,
                        0,
                        4,
                        12,
                        4,
                        5,
                        22,
                        0,
                        0,
                        0,
                        0,
                        0.75,
                        0.75,
                        0.5,
                    ),
                }
            )

        if self.background_color is None:
            glClearColor(1, 1, 1, 0)

        else:
            glClearColor(*self.background_color, 0)

        # setup projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.ortho:
            glOrtho(
                -self.width / 15,
                self.width / 15,
                -self.height / 15,
                self.height / 15,
                -100,
                250,
            )

        else:
            gluPerspective(60, self.width / self.height, 0.1, 250)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # move camera and apply controls
        self.y_rot += self.drag_x * self.drag_speed
        self.x_rot += self.drag_y * self.drag_speed
        self.x_rot = min(90, max(self.x_rot, -90))  # clamp x rotation
        self.drag_x = 0
        self.drag_y = 0

        self.y_off += self.move_x * self.move_speed
        self.x_off += self.move_y * self.move_speed
        self.move_x = 0
        self.move_y = 0

        glTranslatef(0, 0, -50)
        glTranslatef(self.y_off, -self.x_off, 0)
        glRotatef(self.x_rot, 1, 0, 0)
        glRotatef(self.y_rot, 0, 1, 0)
        glScalef(self.zoom, self.zoom, self.zoom)
        glTranslatef(0, -18, 0)

        # clear frame
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # get mouse vector
        proj = glGetFloatv(GL_PROJECTION_MATRIX)
        x = 2 * self.prev[0] / self.width - 1
        y = 1 - 2 * self.prev[1] / self.width
        ray_eye = numpy.linalg.inv(proj) @ numpy.array([x, y, -1, 1])
        ray_eye /= numpy.linalg.norm(ray_eye[:3])
        ray_eye[3] = 1
        view = glGetFloatv(GL_MODELVIEW_MATRIX)
        ray_world = (numpy.linalg.inv(view) @ ray_eye)[:3]
        ray_world /= numpy.linalg.norm(ray_world)

        # render cape
        if self.has_cape and self.show_cape:
            glBindTexture(GL_TEXTURE_2D, self.textures[1])
            glPushMatrix()
            glTranslatef(self.cape.piv_x, self.cape.piv_y, self.cape.piv_z)
            glRotatef(self.cape.rot_z, 0, 0, 1)
            glRotatef(self.cape.rot_y, 0, 1, 0)
            glRotatef(self.cape.rot_x, 1, 0, 0)
            glTranslatef(-self.cape.piv_x, -self.cape.piv_y, -self.cape.piv_z)
            if self.exploded:
                glTranslatef(self.cape.exp_x, self.cape.exp_y, self.cape.exp_z)

            else:
                glTranslatef(self.cape.pos_x, self.cape.pos_y, self.cape.pos_z)

            glScalef(self.cape.scl_x, self.cape.scl_y, self.cape.scl_z)
            glBegin(GL_QUADS)
            for face in self.cape.quads:
                for i in range(4):
                    glTexCoord2f(face[i * 2 + 4], face[i * 2 + 5] * 2)
                    glVertex4fv((self.cape.vertices[face[i]]))

            glEnd()
            glPopMatrix()

        glBindTexture(GL_TEXTURE_2D, self.textures[0])

        # render skin
        for overlay, box in self.skin.items():
            glPushMatrix()
            glTranslatef(box.piv_x, box.piv_y, box.piv_z)
            glRotatef(box.rot_z, 0, 0, 1)
            glRotatef(box.rot_y, 0, 1, 0)
            glRotatef(box.rot_x, 1, 0, 0)
            glTranslatef(-box.piv_x, -box.piv_y, -box.piv_z)
            if self.exploded:
                glTranslatef(box.exp_x, box.exp_y, box.exp_z)

            else:
                glTranslatef(box.pos_x, box.pos_y, box.pos_z)

            glScalef(box.scl_x, box.scl_y, box.scl_z)
            glBegin(GL_QUADS)
            for face in box.quads:
                for i in range(4):
                    glTexCoord2f(face[i * 2 + 4], face[i * 2 + 5])
                    glVertex4fv((box.vertices[face[i]]))

            glEnd()
            if self.grid and not self.show[overlay]:
                glScalef(1.001, 1.001, 1.001)
                glDisable(GL_TEXTURE_2D)
                glColor3f(1, 1, 1)
                glBegin(GL_LINES)
                for line in box.grid:
                    glVertex4fv(line[0])
                    glVertex4fv(line[1])

                glEnd()
                glEnable(GL_TEXTURE_2D)

            glPopMatrix()

        # render overlays
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glAlphaFunc(GL_NOTEQUAL, 0)
        glEnable(GL_ALPHA_TEST)
        for section, box in self.skin_overlays.items():
            if section in self.show and self.show[section]:
                glPushMatrix()
                glTranslatef(box.piv_x, box.piv_y, box.piv_z)
                glRotatef(box.rot_z, 0, 0, 1)
                glRotatef(box.rot_y, 0, 1, 0)
                glRotatef(box.rot_x, 1, 0, 0)
                glTranslatef(-box.piv_x, -box.piv_y, -box.piv_z)
                if self.exploded:
                    glTranslatef(box.exp_x, box.exp_y, box.exp_z)

                else:
                    glTranslatef(box.pos_x, box.pos_y, box.pos_z)

                glScalef(box.scl_x, box.scl_y, box.scl_z)
                glBegin(GL_QUADS)
                for face in box.quads:
                    for i in range(4):
                        glTexCoord2f(face[i * 2 + 4], face[i * 2 + 5])
                        glVertex4fv((box.vertices[face[i]]))

                glEnd()
                if self.grid:
                    glScalef(1.001, 1.001, 1.001)
                    glDisable(GL_TEXTURE_2D)
                    glColor3f(1, 1, 1)
                    glBegin(GL_LINES)
                    for line in box.grid:
                        glVertex4fv(line[0])
                        glVertex4fv(line[1])

                    glEnd()
                    glEnable(GL_TEXTURE_2D)

                glPopMatrix()

        glDisable(GL_ALPHA_TEST)
        glDisable(GL_BLEND)
