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
from EditingWindow import EditingWindow

class OverviewWindow(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.__addTrackButton = tk.Button(
            self,
            text="add Track",
            command=self.__addTrack
        )
        self.__addTrackButton.grid(column=0, row=0)
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
        self.__trackBoxBackgrounds = []
        self.__trackBoxWindows = []
        self.__trackBoxes = []
        self.__trackBackgrounds = []
        self.__trackWindows = []
        self.__tracks = []
        self.__forbiddenRegionRectangles = []

    def __addTrack(self):
        i = len(self.__trackBoxes)
        self.__trackBoxBackgrounds.append(
            self.__leftPaneScrollcanvas.createRectangle(
                0,
                i * OVERVIEW_TRACK_BOX_HEIGHT,
                OVERVIEW_LEFT_PANE_WIDTH,
                (i + 1) * OVERVIEW_TRACK_BOX_HEIGHT,
                fill="red",
                tag="scrollcanvas"
            )
        )
        self.__trackBoxes.append(TrackBox(
                self.__leftPaneScrollcanvas.canvas,
                i,
                self.__removeTrack,
                self.__flipTracks
        ))
        self.__trackBoxWindows.append(
                self.__leftPaneScrollcanvas.canvas.create_window(
                        (0, i * OVERVIEW_TRACK_BOX_HEIGHT),
                        window=self.__trackBoxes[-1],
                        anchor="nw"
                )
        )
        self.__leftPaneScrollcanvas.refresh()
        self.__trackBackgrounds.append(
            self.__centerPaneScrollcanvas.createRectangle(
                0,
                i * OVERVIEW_TRACK_BOX_HEIGHT,
                OVERVIEW_CENTER_PANE_WIDTH
                + TRACK_RIGHT_EXTEND,
                (i + 1) * OVERVIEW_TRACK_BOX_HEIGHT,
                fill="red",
                tag="scrollcanvas"
            )
        )
        self.__centerPaneScrollcanvas.refresh()
        self.__tracks.append(Track(
            self.__centerPaneScrollcanvas.canvas,
            i,
            self.__editMode,
            self.__openEditingWindow
        ))
        self.__trackWindows.append(
                self.__centerPaneScrollcanvas.canvas.create_window(
                        (0, i * OVERVIEW_TRACK_BOX_HEIGHT),
                        window=self.__tracks[-1],
                        anchor="nw"
                )
        )
        
    def __removeTrack(self, position):
        lastIndex = len(self.__tracks) - 1
        for i in range(position, lastIndex):
            self.__flipTracks(i, i+1)
        self.__leftPaneScrollcanvas.canvas.delete(self.__trackBoxBackgrounds[-1])
        del self.__trackBoxBackgrounds[-1]
        self.__leftPaneScrollcanvas.canvas.delete(self.__trackBoxWindows[-1])
        del self.__trackBoxWindows[-1]
        del self.__trackBoxes[-1]
        self.__centerPaneScrollcanvas.canvas.delete(self.__trackBackgrounds[-1])
        del self.__trackBackgrounds[-1]
        self.__centerPaneScrollcanvas.canvas.delete(self.__trackWindows[-1])
        del self.__trackWindows[-1]
        del self.__tracks[-1]
        self.__leftPaneScrollcanvas.refresh()
        self.__centerPaneScrollcanvas.refresh()

        
        
    def __flipTracks(self, position1, position2):
        if position1 < 0 or position2 < 0 \
            or position1 >= len(self.__tracks) \
            or position2 >= len(self.__tracks):
            return
        trackBox1 = self.__trackBoxes[position1]
        track1 = self.__tracks[position1]
        trackBox2 = self.__trackBoxes[position2]
        track2 = self.__tracks[position2]
        self.__leftPaneScrollcanvas.canvas.itemconfig(
                self.__trackBoxWindows[position1],
                window=trackBox2
        )
        self.__leftPaneScrollcanvas.canvas.itemconfig(
                self.__trackBoxWindows[position2],
                window=trackBox1
        )
        self.__centerPaneScrollcanvas.canvas.itemconfig(
                self.__trackWindows[position1],
                window=track2
        )
        self.__centerPaneScrollcanvas.canvas.itemconfig(
                self.__trackWindows[position2],
                window=track1
        )
        trackBox2.setPosition(position1)
        trackBox1.setPosition(position2)
        track2.setPosition(position1)
        track1.setPosition(position2)
        self.__trackBoxes[position1] = trackBox2
        self.__trackBoxes[position2] = trackBox1
        self.__tracks[position1] = track2
        self.__tracks[position2] = track1
        
        
    def __openEditingWindow(self, startTimestep, endTimestep, position):
        print("open editing window: ", startTimestep, endTimestep, position)
        root = tk.Toplevel(self)
        editingWindow = EditingWindow(
                root,
                self.__tracks,
                startTimestep,
                endTimestep,
                position
        )
        editingWindow.pack()
        editingWindow.grab_set()
    
if __name__ == "__main__":
    root = tk.Tk()
    overviewWindow = OverviewWindow(root)
    overviewWindow.grid(row=0, column=1)

    root.mainloop()