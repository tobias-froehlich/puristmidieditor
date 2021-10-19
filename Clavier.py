from const import GRID_PIXELS_PER_SEMINOTE
from const import GRID_WHITE_KEY_COLOR
from const import GRID_BLACK_KEY_COLOR
from const import GRID_MIDDLE_C_COLOR
from const import GRID_KEY_BORDER_COLOR
from const import GRID_PIXELS_PER_TIMESTEP

class Clavier:

    def __init__(self, scrollcanvas):
        self.__scrollcanvas = scrollcanvas
        self.__rectangles = []
        pps = GRID_PIXELS_PER_SEMINOTE
        white = GRID_WHITE_KEY_COLOR
        black = GRID_BLACK_KEY_COLOR
        middle_c = GRID_MIDDLE_C_COLOR
        for i in range(128):
            if i % 12 in [1, 3, 6, 8, 10]:
                color = black
            else:
                color = white
            if i == 60:
                color = middle_c
            obj = scrollcanvas.createRectangle(
                0, (127-i)*pps, 10, (128-i)*pps,
                width=1,
                outline=GRID_KEY_BORDER_COLOR,
                fill=color,
                tags=("scrollcanvas", "z-0")
            )
            self.__rectangles.append(obj)

    def refresh(self, num_of_timesteps):
        for i in range(128):
            coords = self.__scrollcanvas.coords(
                self.__rectangles[i]
            )
            coords[0] = 0
            coords[2] = num_of_timesteps \
                      * GRID_PIXELS_PER_TIMESTEP
            self.__scrollcanvas.coords(
                self.__rectangles[i],
                *coords
            )


