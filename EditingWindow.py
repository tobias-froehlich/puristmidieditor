# -*- coding: utf-8 -*-

import tkinter as tk
from Scrollcanvas import Scrollcanvas
from Clavier import Clavier
from Palette import Palette
from const import EDITING_CENTER_PANE_WIDTH
from const import EDITING_CENTER_PANE_HEIGHT
from const import GRID_PIXELS_PER_SEMINOTE
from const import GRID_PIXELS_PER_TIMESTEP
from const import FORBIDDEN_REGION_COLOR


class EditingWindow(tk.Frame):
    
    def __init__(self, root, tracks, startTimestep, endTimestep, position):
        super().__init__(root)
        self.__tracks = tracks
        self.__startTimestep = startTimestep
        self.__endTimestep = endTimestep
        self.__clickStartMidicode = None
        self.__clickStartTimestep = None
        self.__clickEndTimestep = None
        self.__position = position       
        self.__centerPaneScrollcanvas = Scrollcanvas(
            self,
            EDITING_CENTER_PANE_WIDTH,
            EDITING_CENTER_PANE_HEIGHT,
            xscroll="master",
            yscroll="master"
        )
        self.__clavier = Clavier(self.__centerPaneScrollcanvas)
        self.__clavier.refresh(self.__endTimestep - self.__startTimestep)
        self.__centerPaneScrollcanvas.refresh()
        self.__initZLayers()
        self.__forbiddenRegionRectangles = []
        self.__palette = Palette(self, tracks)
        self.__palette.grid(column=0, row=0)  
        self.__centerPaneScrollcanvas.grid(column=1, row=0)
        self.__centerPaneScrollcanvas.bind("<Button-1>", self.__onClickLeft)
        self.__centerPaneScrollcanvas.bind("<ButtonRelease-1>", self.__onReleaseLeft)
        self.__centerPaneScrollcanvas.bind("<Button-3>", self.__onClickRight)
        self.__centerPaneScrollcanvas.bind("<ButtonRelease-3>", self.__onReleaseRight)

        self.__notes = []
        for iTrack in range(len(self.__tracks)):
            track = self.__tracks[iTrack]
            self.__notes.append([])
            for note in track.getNotes(self.__startTimestep, self.__endTimestep):
                print(note)
                self.__drawNote(iTrack, note[0], note[1], note[2], note[3])


    def initForbiddenRegions(self, iTrack):
        print("initForbiddenRegions: ", iTrack)
        while len(self.__forbiddenRegionRectangles) > 0:
            self.__centerPaneScrollcanvas.delete(self.__forbiddenRegionRectangles[-1])
            del self.__forbiddenRegionRectangles[-1]
        track = self.__tracks[iTrack]
        forbiddenRegions = track.getForbiddenRegions(self.__startTimestep, self.__endTimestep)
        for region in forbiddenRegions:
            start = region[0]
            end = region[1]
            x1 = (start - self.__startTimestep) * GRID_PIXELS_PER_TIMESTEP
            x2 = (end - self.__startTimestep + 1) * GRID_PIXELS_PER_TIMESTEP
            y1 = 0
            y2 = 128 * GRID_PIXELS_PER_SEMINOTE
            self.__forbiddenRegionRectangles.append(
                self.__centerPaneScrollcanvas.createRectangle(
                    x1, y1, x2, y2,
                    fill=FORBIDDEN_REGION_COLOR,
                    tags=("z-1",)
                )
            )
        self.__centerPaneScrollcanvas.canvas.tag_lower("z-1", "z-2")

    def __initZLayers(self):
        self.__dummyRectangleForZ0 = self.__centerPaneScrollcanvas.createRectangle(
                -10, -10, -5, -5,
                fill="yellow",
                tags=("z-0")
        )
        self.__dummyRectangleForZ1 = self.__centerPaneScrollcanvas.createRectangle(
                -10, -10, -5, -5,
                fill="yellow",
                tags=("z-1")
        )
        self.__dummyRectangleForZ2 = self.__centerPaneScrollcanvas.createRectangle(
                -10, -10, -5, -5,
                fill="yellow",
                tags=("z-2")
        )
        
    def __onClickLeft(self, event):
        self.__clickStartMidicode = 127 - int(round(event.y / GRID_PIXELS_PER_SEMINOTE - 0.5))
        self.__clickStartTimestep = int(round(event.x / GRID_PIXELS_PER_TIMESTEP - 0.5)) + self.__startTimestep
        print("midicode: ", self.__clickStartMidicode)
        print("startTimstep: ", self.__clickStartTimestep)

    def __onReleaseLeft(self, event):
        self.__clickEndTimestep = int(round(event.x / GRID_PIXELS_PER_TIMESTEP - 0.5)) + self.__startTimestep
        print("endTimestep: ", self.__clickEndTimestep)
        self.__addNote(
            self.__palette.getPosition(),
            self.__clickStartMidicode,
            100,
            self.__clickStartTimestep,
            self.__clickEndTimestep
        )
        
    def __onClickRight(self, event):
        self.__clickStartTimestep = int(round(event.x / GRID_PIXELS_PER_TIMESTEP - 0.5)) + self.__startTimestep
        self.__clickStartMidicode = 127 - int(round(event.y / GRID_PIXELS_PER_SEMINOTE - 0.5))

    def __onReleaseRight(self, event):
        self.__clickEndTimestep = int(round(event.x / GRID_PIXELS_PER_TIMESTEP - 0.5)) + self.__startTimestep
        self.__clickEndMidicode = 127 - int(round(event.y / GRID_PIXELS_PER_SEMINOTE - 0.5))
        self.__deleteNotes(
                self.__palette.getPosition(),
                self.__clickStartTimestep,
                self.__clickEndTimestep,
                self.__clickStartMidicode,
                self.__clickEndMidicode
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
        newNote = self.__centerPaneScrollcanvas.createRectangle(
                x1, y1, x2, y2,
                fill=self.__tracks[iTrack].getColor(),
                tags=("z-2",)
        )
        self.__notes[iTrack].append(newNote)
        
    def __deleteNotes(self, iTrack, startTimestep, endTimestep, startMidicode, endMidicode):
        print("deleteNotes: ", startTimestep, endTimestep, startMidicode, endMidicode)
#        self.__tracks[iTrack].__deleteNotes(startTimestep, endTimestep, startMidicode, endMidicode)
        xmin = (startTimestep - self.__startTimestep) * GRID_PIXELS_PER_TIMESTEP
        xmax = (endTimestep - self.__startTimestep) * GRID_PIXELS_PER_TIMESTEP
        ymax = (127 - startMidicode) * GRID_PIXELS_PER_SEMINOTE
        ymin = (127 - endMidicode) * GRID_PIXELS_PER_SEMINOTE
        iNote = 0
        while iNote < len(self.__notes[iTrack]):
            note = self.__notes[iTrack][iNote]
            (x1, y1, x2, y2) = self.__centerPaneScrollcanvas.coords(note)
            if (x1 <= xmax) and (x2 > xmin) and (y1 <= ymax) and (y2 > ymin):
                self.__centerPaneScrollcanvas.delete(note)
                del self.__notes[iTrack][iNote]
                noteMidicode = 127 - int(round(y1 / GRID_PIXELS_PER_SEMINOTE))
                noteStartTimestep = int(round(x1 / GRID_PIXELS_PER_TIMESTEP)) + self.__startTimestep
                noteEndTimestep = int(round(x2 / GRID_PIXELS_PER_TIMESTEP - 1)) + self.__startTimestep
                self.__tracks[iTrack].deleteNote(noteStartTimestep, noteEndTimestep, noteMidicode)
            else:
                iNote += 1
            

    
if __name__ == "__main__":
    root = tk.Tk()
    editingWindow = EditingWindow(root)
    editingWindow.pack()
    root.mainloop()