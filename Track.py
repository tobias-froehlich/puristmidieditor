# -*- coding: utf-8 -*-

from const import OVERVIEW_CENTER_PANE_WIDTH
from const import OVERVIEW_TRACK_BOX_HEIGHT
from const import TRACK_RIGHT_EXTEND
from const import OVERVIEW_TIME_STEP_WIDTH
from const import TRACK_COLORS

from Sequence import Sequence

import tkinter as tk
import numpy as np

class Track(tk.Frame):
    
    def __init__(self, root, position, editMode, openEditingWindowFunction):
        super().__init__(
            root,
            width=OVERVIEW_CENTER_PANE_WIDTH
            + TRACK_RIGHT_EXTEND,
            height=OVERVIEW_TRACK_BOX_HEIGHT,
            relief="raised",
            borderwidth=2
        )
        self.__position = position
        self.__openEditingWindowFunction = openEditingWindowFunction
        self.__data = np.zeros((0,), dtype='int')
        self.__editMode = editMode
        self.grid_propagate(0)
        self.__canvas = tk.Canvas(
            self,
            width=OVERVIEW_CENTER_PANE_WIDTH
            + TRACK_RIGHT_EXTEND - 4,
            height=OVERVIEW_TRACK_BOX_HEIGHT - 4,
            bg="red"
        )
        self.__canvas.grid(column=0, row=0)
        self.__canvas.bind("<Button-1>", self.__onClickLeft)
        self.__canvas.bind("<ButtonRelease-1>", self.__onReleaseLeft)
        self.__sequenceRectangles = []
        self.__sequences = []
        
    def getPosition(self):
        return self.__position
        
    def getColor(self):
        return TRACK_COLORS[self.__position]
        

    def setPosition(self, position):
        self.__position = position

    def addNote(self, midicode, velocity, startTimestep, endTimestep):
        if startTimestep < 0:
            return False
        if endTimestep >= self.__data.shape[0]:
            return False
        if self.__data[startTimestep] == 0:
            return False
        if self.__data[endTimestep] == 0:
            return False
        if self.__data[startTimestep] != self.__data[endTimestep]:
            return False
        iSequence = self.__data[startTimestep] - 1
        sequence = self.__sequences[iSequence]
        offset = sequence.getStartTimestep()
        return sequence.addNote(
            midicode, velocity,
            startTimestep - offset,
            endTimestep - offset
        )

    def getNotes(self, startTimestep, endTimestep):
        notes = []
        for sequence in self.__sequences:
            notes.extend(
                sequence.getNotes(
                    startTimestep,
                    endTimestep
                )
            )
        return notes
    
#    def deleteNotes(self, startTimestep, endTimestep, startMidicode, endMidicode):
#        for sequence in self.__sequences:
#            if sequence.getStartTimestep() <= endTimestep \
#                and sequence.getEndTimestep() >= startTimestep:
#                sequence.deleteNotes(startTimestep, endTimestep, startMidicode, endMidicode)
        
    def deleteNote(self, startTimestep, endTimestep, midicode):
        for sequence in self.__sequences:
            if sequence.getStartTimestep() <= endTimestep \
                and sequence.getEndTimestep() >= startTimestep:
                sequence.deleteNote(startTimestep, endTimestep, midicode)
 
    
    def __onClickLeft(self, event):
        timestep = event.x // OVERVIEW_TIME_STEP_WIDTH
        self.__startTimestep = timestep
        
    def __onReleaseLeft(self, event):
        print(self.__editMode.get())
        self.__endTimestep = event.x // OVERVIEW_TIME_STEP_WIDTH
        editMode = self.__editMode.get()
        if editMode == "create":
            self.__startTimestep = self.__nextFree(
                self.__startTimestep
            )
            self.__endTimestep = min(
                    self.__endTimestep,
                    self.__lastFreeAfter(self.__startTimestep)
            )
            if (self.__startTimestep < self.__endTimestep):
                self.__createSequence(self.__startTimestep, self.__endTimestep)
        elif editMode == "delete":
            self.__deleteSequence()
        elif editMode == "move":
            self.__move()
        elif editMode == "resize_left":
            self.__resizeLeft()
        elif editMode == "resize_right":
            self.__resizeRight()
        elif editMode == "edit_midi":
            self.__editMidi()
        self.__startTimestep = None
        self.__endTimestep = None
        
    def __nextFree(self, timestep):
        if (len(self.__data) <= timestep):
            result = timestep
        else:
            a = np.argwhere(self.__data[timestep:] == 0)
            if (len(a) == 0):
                result = len(self.__data)
            else:
                result = timestep + a[0][0]
        print("Next timestep: ", timestep, self.__data, result)
        return result
    
    def __previousFree(self, timestep):
        a = np.argwhere(self.__data[:timestep] == 0)
        if len(a) == 0:
            result = 0
        else:
              result = a[-1][0]
        return result
        
    def __lastFreeAfter(self, timestep):
        if self.__data.shape[0] <= timestep:
            return np.inf
        if self.__data[timestep] != 0:
            return np.inf
        i = timestep
        while (i < self.__data.shape[0]):
            if self.__data[i] != 0:
                return i - 1
            i += 1
        return np.inf
    
    def __firstFreeBefore(self, timestep):
        if self.__data[timestep] != 0:
            return -1
        i = timestep
        while (i >= 0):
            if self.__data[i] != 0:
                return i + 1
            i -= 1
        return -1
            
    
    def __createSequence(self, startTimestep, endTimestep):
        self.__sequenceRectangles.append(
            self.__canvas.create_rectangle(
                startTimestep * OVERVIEW_TIME_STEP_WIDTH,
                2,
                endTimestep * OVERVIEW_TIME_STEP_WIDTH,
                OVERVIEW_TRACK_BOX_HEIGHT - 2,
                fill="green"
            )
        )
        self.__sequences.append(
            Sequence(startTimestep, endTimestep - startTimestep)
        )
        self.__fillWithZeros(endTimestep)
        self.__data[startTimestep:endTimestep] = len(self.__sequences)
        
    def __fillWithZeros(self, endTimestep):
        if (self.__data.shape[0] < endTimestep):
            newZeros = np.zeros((endTimestep - self.__data.shape[0],), dtype='int')
            self.__data = np.concatenate([self.__data, newZeros], 0)

            
    def __deleteSequence(self):
        indexes = []
        for i in range(len(self.__sequences)):
            if self.__sequences[i].getStartTimestep() \
                <= self.__startTimestep \
                <= self.__sequences[i].getEndTimestep():
                indexes.append(i)
        print("delete: ", indexes)
        indexes.reverse()
        for i in indexes:
            self.__data[self.__sequences[i].getStartTimestep():self.__sequences[i].getEndTimestep()] = 0
            self.__data = np.where(self.__data > i, self.__data - 1, self.__data)
            self.__canvas.delete(self.__sequenceRectangles[i])
            del self.__sequenceRectangles[i]
            del self.__sequences[i]
        self.__deleteZerosAtEnd()
        print("length after createSequence: ", self.__data.shape[0])
        print("data after createSequence: ", self.__data)

    def __deleteZerosAtEnd(self):
        a = np.argwhere(self.__data > 0)
        if len(a) == 0:
            self.__data = np.zeros((0,), dtype='int')
        else:
            self.__data = self.__data[0:a[-1][0]+1]

    def __getMaximalCoveredIndex(self, startTimestep, endTimestep):
        return self.__data[startTimestep:endTimestep].max()

    def __move(self):
        print("move: startTimestep: ", self.__startTimestep)
        if (self.__startTimestep >= self.__data.shape[0]):
            return
        index = self.__data[self.__startTimestep] - 1
        if (index < 0):
            return
        print(self.__sequences)
        print(index)
        startTimestepOfSequence = self.__sequences[index].getStartTimestep()
        endTimestepOfSequence = self.__sequences[index].getEndTimestep()
        diff = self.__endTimestep - self.__startTimestep
        self.__data[startTimestepOfSequence:endTimestepOfSequence] = 0
        self.__fillWithZeros(self.__data.shape[0] + diff + endTimestepOfSequence - startTimestepOfSequence)
        possible = False
        i = 0
        while not possible:
            newStartTimestep = startTimestepOfSequence + diff - i
            newEndTimestep = endTimestepOfSequence + diff - i
            if (newStartTimestep >= 0):
                if self.__getMaximalCoveredIndex(newStartTimestep, newEndTimestep) == 0:
                    possible = True
                    break
            newStartTimestep = startTimestepOfSequence + diff + i
            newEndTimestep = endTimestepOfSequence + diff + i
            if (newStartTimestep >= 0):
                if self.__getMaximalCoveredIndex(newStartTimestep, newEndTimestep) == 0:
                    possible = True
            i += 1
        self.__data[newStartTimestep:newEndTimestep] = index + 1
        (x1, y1, x2, y2) = self.__canvas.coords(index + 1)
        self.__canvas.coords(
            index + 1,
            newStartTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y1,
            newEndTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y2
        )
        self.__sequences[index].setStartTimestep(newStartTimestep)
        self.__deleteZerosAtEnd()
        print("total length: ", self.__data.shape[0])

    def __resizeLeft(self):
        if (self.__startTimestep >= self.__data.shape[0]):
            return
        index = self.__data[self.__startTimestep] - 1
        if (index < 0):
            return
        startTimestepOfSequence = self.__sequences[index].getStartTimestep()
        endTimestepOfSequence = self.__sequences[index].getEndTimestep()
        diff = self.__endTimestep - self.__startTimestep
        self.__data[startTimestepOfSequence:endTimestepOfSequence] = 0
        newStartTimestep = startTimestepOfSequence + diff
        newStartTimestep = max(newStartTimestep, self.__firstFreeBefore(startTimestepOfSequence))
        newStartTimestep = max(newStartTimestep, 0)
        if newStartTimestep >= endTimestepOfSequence:
            self.__data[startTimestepOfSequence:endTimestepOfSequence] = index + 1
            return
        self.__data[newStartTimestep:endTimestepOfSequence] = index + 1
        (x1, y1, x2, y2) = self.__canvas.coords(index + 1)
        self.__canvas.coords(
            index + 1,
            newStartTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y1,
            endTimestepOfSequence * OVERVIEW_TIME_STEP_WIDTH,
            y2
        )
        self.__sequences[index].resizeLeft(newStartTimestep - startTimestepOfSequence)
        
    def __resizeRight(self):
        if (self.__startTimestep >= self.__data.shape[0]):
            return
        index = self.__data[self.__startTimestep] - 1
        if (index < 0):
            return
        startTimestepOfSequence = self.__sequences[index].getStartTimestep()
        endTimestepOfSequence = self.__sequences[index].getEndTimestep()
        diff = self.__endTimestep - self.__startTimestep
        self.__data[startTimestepOfSequence:endTimestepOfSequence] = 0
        newEndTimestep = endTimestepOfSequence + diff
        newEndTimestep = min(newEndTimestep, self.__lastFreeAfter(endTimestepOfSequence) + 1)
        self.__fillWithZeros(newEndTimestep)
        if startTimestepOfSequence >= newEndTimestep:
            self.__data[startTimestepOfSequence:endTimestepOfSequence] = index + 1
            return
        self.__data[startTimestepOfSequence:newEndTimestep] = index + 1
        (x1, y1, x2, y2) = self.__canvas.coords(index + 1)
        self.__canvas.coords(
            index + 1,
            startTimestepOfSequence * OVERVIEW_TIME_STEP_WIDTH,
            y1,
            newEndTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y2
        )
        self.__sequences[index].resizeRight(newEndTimestep - endTimestepOfSequence)        
        self.__deleteZerosAtEnd()
        print("total length: ", self.__data.shape[0])
        
                
        
    def __editMidi(self):
        if self.__startTimestep < self.__endTimestep:
            self.__openEditingWindowFunction(self.__startTimestep, self.__endTimestep, self.__position)
