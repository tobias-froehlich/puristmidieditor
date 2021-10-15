# -*- coding: utf-8 -*-

import tkinter as tk
from Scrollcanvas import Scrollcanvas
from Clavier import Clavier
from Palette import Palette
from const import EDITING_CENTER_PANE_WIDTH
from const import EDITING_CENTER_PANE_HEIGHT
from const import GRID_PIXELS_PER_SEMINOTE
from const import GRID_PIXELS_PER_TIMESTEP


class EditingWindow(tk.Frame):
    
    def __init__(self, root, tracks, startTimestep, endTimestep, position):
        super().__init__(root)
        self.__tracks = tracks
        self.__startTimestep = startTimestep
        self.__endTimestep = endTimestep
        self.__clickMidicode = None
        self.__clickStartTimestep = None
        self.__clickEndTimestep = None
        self.__position = position
        self.__palette = Palette(self, tracks)
        self.__palette.grid(column=0, row=0)
        self.__centerPaneScrollcanvas = Scrollcanvas(
            self,
            EDITING_CENTER_PANE_WIDTH,
            EDITING_CENTER_PANE_HEIGHT,
            xscroll="master",
            yscroll="master"
        )
        self.__centerPaneScrollcanvas.grid(column=1, row=0)
        self.__centerPaneScrollcanvas.bind("<Button-1>", self.__onClickLeft)
        self.__centerPaneScrollcanvas.bind("<ButtonRelease-1>", self.__onReleaseLeft)
        self.__clavier = Clavier(self.__centerPaneScrollcanvas)
        self.__clavier.refresh(self.__endTimestep - self.__startTimestep)
        self.__centerPaneScrollcanvas.refresh()
        self.__notes = []
        for iTrack in range(len(self.__tracks)):
            track = self.__tracks[iTrack]
            for note in track.getNotes(self.__startTimestep, self.__endTimestep):
                print(note)
                self.__drawNote(iTrack, note[0], note[1], note[2], note[3])

    def __onClickLeft(self, event):
        self.__clickMidicode = 127 - int(round(event.y / GRID_PIXELS_PER_SEMINOTE - 0.5))
        self.__clickStartTimestep = int(round(event.x / GRID_PIXELS_PER_TIMESTEP - 0.5)) + self.__startTimestep
        print("midicode: ", self.__clickMidicode)
        print("startTimstep: ", self.__clickStartTimestep)


    def __onReleaseLeft(self, event):
        self.__clickEndTimestep = int(round(event.x / GRID_PIXELS_PER_TIMESTEP - 0.5)) + self.__startTimestep
        print("endTimestep: ", self.__clickEndTimestep)
        self.__addNote(
            self.__palette.getPosition(),
            self.__clickMidicode,
            100,
            self.__clickStartTimestep,
            self.__clickEndTimestep
        )
        
    def __addNote(self, iTrack, midicode, velocity, startTimestep, endTimestep):
        if (endTimestep >= startTimestep):
            if (self.__tracks[iTrack].addNote(midicode, velocity, startTimestep, endTimestep)):
                self.__drawNote(iTrack, midicode, velocity, startTimestep, endTimestep)
                
    def __drawNote(self, iTrack, midicode, velocity, startTimestep, endTimestep):
        x1 = (startTimestep - self.__startTimestep) * GRID_PIXELS_PER_TIMESTEP
        x2 = (endTimestep + 1 - self.__startTimestep) * GRID_PIXELS_PER_TIMESTEP
        y1 = (127 - midicode) * GRID_PIXELS_PER_SEMINOTE
        y2 = (127 - midicode + 1) * GRID_PIXELS_PER_SEMINOTE
        self.__notes.append(
            self.__centerPaneScrollcanvas.createRectangle(
                x1, y1, x2, y2,
                fill=self.__tracks[iTrack].getColor()
            )
        )
    
if __name__ == "__main__":
    root = tk.Tk()
    editingWindow = EditingWindow(root)
    editingWindow.pack()
    root.mainloop()