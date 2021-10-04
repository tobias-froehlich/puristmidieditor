from const import OVERVIEW_LEFT_PANE_WIDTH
from const import OVERVIEW_LEFT_PANE_HEIGHT
from const import OVERVIEW_CENTER_PANE_WIDTH
from const import OVERVIEW_CENTER_PANE_HEIGHT
from const import OVERVIEW_NUMBER_OF_TRACKS
from const import OVERVIEW_TRACK_BOX_HEIGHT
from const import TRACK_RIGHT_EXTEND

import tkinter as tk
from Scrollcanvas import Scrollcanvas
from Toolbox import Toolbox
from TrackBox import TrackBox
from Track import Track

class OverviewWindow(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.__editMode = tk.StringVar()
        self.__toolbox = Toolbox(self, self.__editMode)
        self.__toolbox.grid(column=1, row=0)
        self.__leftPaneScrollcanvas = Scrollcanvas(
            self,
            OVERVIEW_LEFT_PANE_WIDTH,
            OVERVIEW_LEFT_PANE_HEIGHT,
            xscroll="none"
        )
        self.__leftPaneScrollcanvas.grid(column=0, row=1)
        self.__centerPaneScrollcanvas = Scrollcanvas(
            self,
            OVERVIEW_CENTER_PANE_WIDTH,
            OVERVIEW_CENTER_PANE_HEIGHT,
            xscroll="master",
            yscroll=self.__leftPaneScrollcanvas
        )
        self.__centerPaneScrollcanvas.grid(column=1, row=1)
        self.__createTrackBoxes()
        self.__createTracks()
        
    def __createTrackBoxes(self):
        self.__trackBoxBackgrounds = []
        for i in range(OVERVIEW_NUMBER_OF_TRACKS):
            self.__leftPaneScrollcanvas.createRectangle(
                0,
                i * OVERVIEW_TRACK_BOX_HEIGHT,
                OVERVIEW_LEFT_PANE_WIDTH,
                (i + 1) * OVERVIEW_TRACK_BOX_HEIGHT,
                fill="red",
                tag="scrollcanvas"
            )
        self.__leftPaneScrollcanvas.refresh()
        self.__trackBoxes = []
        for i in range(OVERVIEW_NUMBER_OF_TRACKS):
            self.__trackBoxes.append(TrackBox(
                self.__leftPaneScrollcanvas.canvas
            ))
            self.__leftPaneScrollcanvas.canvas.create_window(
                (0, i * OVERVIEW_TRACK_BOX_HEIGHT),
                window=self.__trackBoxes[-1],
                anchor="nw"
            )
        
    def __createTracks(self):
        self.__trackBackgrounds = []
        for i in range(OVERVIEW_NUMBER_OF_TRACKS):
            self.__centerPaneScrollcanvas.createRectangle(
                0,
                i * OVERVIEW_TRACK_BOX_HEIGHT,
                OVERVIEW_CENTER_PANE_WIDTH
                + TRACK_RIGHT_EXTEND,
                (i + 1) * OVERVIEW_TRACK_BOX_HEIGHT,
                fill="red",
                tag="scrollcanvas"
        )
        self.__centerPaneScrollcanvas.refresh()
        self.__tracks = []
        for i in range(OVERVIEW_NUMBER_OF_TRACKS):
            self.__tracks.append(Track(
                self.__centerPaneScrollcanvas.canvas,
                self.__editMode
            ))
            self.__centerPaneScrollcanvas.canvas.create_window(
                (0, i * OVERVIEW_TRACK_BOX_HEIGHT),
                window=self.__tracks[-1],
                anchor="nw"
            )
        
if __name__ == "__main__":
    root = tk.Tk()
    overviewWindow = OverviewWindow(root)
    overviewWindow.grid(row=0, column=1)

    root.mainloop()