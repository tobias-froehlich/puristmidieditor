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
    
    def __init__(self, root, overviewWindow, position, editMode, openEditingWindowFunction):
        super().__init__(
            root,
            width=OVERVIEW_CENTER_PANE_WIDTH
            + TRACK_RIGHT_EXTEND,
            height=OVERVIEW_TRACK_BOX_HEIGHT,
            relief="raised",
            borderwidth=2
        )
        self.__overviewWindow = overviewWindow
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
        self.__sequenceImageObjects = []
        self.__sequenceImages = []
        self.__sequences = []
        
    def getLength(self):
        return self.__data.shape[0]
        
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
        possible =  sequence.addNote(
            midicode, velocity,
            startTimestep - offset,
            endTimestep - offset
        )
        if possible:
            imageObject = self.__sequenceImageObjects[iSequence]
            for x in range((startTimestep - offset) * OVERVIEW_TIME_STEP_WIDTH, (endTimestep + 1 - offset) * OVERVIEW_TIME_STEP_WIDTH - 1):
                imageObject.put("#ffffff", (x, 128 - midicode))
        return possible

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

    def deleteNote(self, startTimestep, endTimestep, midicode):
        for iSequence in range(len(self.__sequences)):
            sequence = self.__sequences[iSequence]
            if sequence.getStartTimestep() <= endTimestep \
                and sequence.getEndTimestep() >= startTimestep:
                sequence.deleteNote(startTimestep, endTimestep, midicode)
                offset = sequence.getStartTimestep()
                imageObject = self.__sequenceImageObjects[iSequence]
                for x in range((startTimestep - offset) * OVERVIEW_TIME_STEP_WIDTH, (endTimestep - offset + 1) * OVERVIEW_TIME_STEP_WIDTH - 1):
                    imageObject.transparency_set(x, 128 - midicode, True)
                                    
    def getForbiddenRegions(self, startTimestep, endTimestep):
        forbiddenRegions = []
        start = startTimestep
        for t in range(startTimestep, min(endTimestep, len(self.__data))):
            if self.__data[t] > 0:
                if start < t:
                    forbiddenRegions.append((start, t - 1))
                start = t + 1
        if self.__data[min(endTimestep, len(self.__data)) - 1] == 0:
            forbiddenRegions.append((start, endTimestep - 1))
        if endTimestep > len(self.__data):
            forbiddenRegions.append((len(self.__data), endTimestep))
        return forbiddenRegions
            
    
    def resetSize(self, length):
        self.config(width=length * OVERVIEW_TIME_STEP_WIDTH)
        self.__canvas.config(width=length * OVERVIEW_TIME_STEP_WIDTH)
    
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
                1,
                endTimestep * OVERVIEW_TIME_STEP_WIDTH,
                OVERVIEW_TRACK_BOX_HEIGHT - 4,
                fill="blue",
            )
        )
        self.__sequenceImageObjects.append(
            tk.PhotoImage(
                width=(endTimestep - startTimestep) * OVERVIEW_TIME_STEP_WIDTH,
                height=OVERVIEW_TRACK_BOX_HEIGHT - 5
            )
        )
        print(self.__sequenceImageObjects)
        self.__sequenceImageObjects[-1].put("#ffffff", (0, 0))
        self.__sequenceImages.append(
            self.__canvas.create_image(
                startTimestep * OVERVIEW_TIME_STEP_WIDTH,
                1,
                image=self.__sequenceImageObjects[-1],
                anchor="nw"
            )
        )

        self.__sequences.append(
            Sequence(startTimestep, endTimestep - startTimestep)
        )
        self.__fillWithZeros(endTimestep)
        self.__data[startTimestep:endTimestep] = len(self.__sequences)
        self.__overviewWindow.refresh()
        
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
            self.__canvas.delete(self.__sequenceImages[i])
            del self.__sequenceRectangles[i]
            del self.__sequenceImages[i]
            del self.__sequenceImageObjects[i]
            del self.__sequences[i]
        self.__deleteZerosAtEnd()
        self.__overviewWindow.refresh()
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
        rectangle = self.__sequenceRectangles[index]
        (x1, y1, x2, y2) = self.__canvas.coords(rectangle)
        self.__canvas.coords(
            rectangle,
            newStartTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y1,
            newEndTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y2
        )
        image = self.__sequenceImages[index]
        (x, y) = self.__canvas.coords(image)
        self.__canvas.coords(
            image,
            newStartTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y1
        )
        self.__sequences[index].setStartTimestep(newStartTimestep)
        self.__deleteZerosAtEnd()
        self.__overviewWindow.refresh()
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

        sequence = self.__sequences[index]
        newStartTimestep = min(newStartTimestep, sequence.getFirstNonemptyTimestep())
        if newStartTimestep >= endTimestepOfSequence:
            self.__data[startTimestepOfSequence:endTimestepOfSequence] = index + 1
            return       
        self.__data[newStartTimestep:endTimestepOfSequence] = index + 1
        rectangle = self.__sequenceRectangles[index]
        (x1, y1, x2, y2) = self.__canvas.coords(rectangle)
        self.__canvas.coords(
            rectangle,
            newStartTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y1,
            endTimestepOfSequence * OVERVIEW_TIME_STEP_WIDTH,
            y2
        )
        image = self.__sequenceImages[index]
        (x1, y1) = self.__canvas.coords(image)
        self.__canvas.coords(
            image,
            newStartTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y1
        )
        imageObject = self.__sequenceImageObjects[index]
        imageObject.config(width=(endTimestepOfSequence - newStartTimestep) * OVERVIEW_TIME_STEP_WIDTH)
        imageObject.blank()

        sequence.resizeLeft(newStartTimestep - startTimestepOfSequence)
        for note in sequence.getAllNotes():
            midicode = note[0]
            start = note[2]
            end = note[3]
            offset = sequence.getStartTimestep()
            for x in range((start - offset) * OVERVIEW_TIME_STEP_WIDTH, (end + 1 - offset) * OVERVIEW_TIME_STEP_WIDTH - 1):
                imageObject.put("#ffffff", (x, 128 - midicode))

        
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
        sequence = self.__sequences[index]
        newEndTimestep = max(newEndTimestep, sequence.getLastNonemptyTimestep() + 1)
        if startTimestepOfSequence >= newEndTimestep:
            self.__data[startTimestepOfSequence:endTimestepOfSequence] = index + 1
            return
        self.__data[startTimestepOfSequence:newEndTimestep] = index + 1
        rectangle = self.__sequenceRectangles[index]
        (x1, y1, x2, y2) = self.__canvas.coords(rectangle)
        self.__canvas.coords(
            rectangle,
            startTimestepOfSequence * OVERVIEW_TIME_STEP_WIDTH,
            y1,
            newEndTimestep * OVERVIEW_TIME_STEP_WIDTH,
            y2
        )

        sequence.resizeRight(newEndTimestep - endTimestepOfSequence)
        self.__sequenceImageObjects[index].config(width=(newEndTimestep - startTimestepOfSequence) * OVERVIEW_TIME_STEP_WIDTH)
        self.__deleteZerosAtEnd()
        self.__overviewWindow.refresh()
        print("total length: ", self.__data.shape[0])
        
                
        
    def __editMidi(self):
        if self.__startTimestep < self.__endTimestep:
            self.__openEditingWindowFunction(self.__startTimestep, self.__endTimestep, self.__position)
